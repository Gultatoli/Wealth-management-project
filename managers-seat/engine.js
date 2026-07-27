/*
 * The replay engine.
 *
 * One implementation, used by both the page and the tests. The page runs it in
 * the browser as the player makes choices; test_engine.py runs this same file
 * in node and checks it against figures computed independently in Python.
 * Writing it twice, once for the page and once for the tests, would eventually
 * produce two engines that disagree, and the disagreement would surface in an
 * interview rather than in a test.
 *
 * The engine does no forecasting. It holds real positions in real assets,
 * applies the monthly returns those assets actually delivered, charges the fee,
 * pays the income, and reports what is left. Between rebalances the positions
 * drift exactly as a real portfolio's would, which is the point: the paper is
 * about the gap between the label on a portfolio and what is inside it, and an
 * engine that silently held every model at its target weights could never show
 * that gap.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Engine = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var OPENING_MODEL = "cautious";

  function monthsBetween(a, b) {
    var pa = a.split("-").map(Number), pb = b.split("-").map(Number);
    return (pb[0] - pa[0]) * 12 + (pb[1] - pa[1]);
  }

  /* An annual rate as its monthly equivalent, compounding. Same convention as
     analysis/costs.py, which turns an annual fee into a daily one this way. */
  function monthlyRate(annual) {
    return 1 - Math.pow(1 - annual, 1 / 12);
  }

  function sum(obj) {
    var t = 0;
    for (var k in obj) if (obj.hasOwnProperty(k)) t += obj[k];
    return t;
  }

  function bandFor(bands, month) {
    for (var i = 0; i < bands.length; i++) {
      if (month >= bands[i].from && month <= bands[i].to) return bands[i];
    }
    return null;
  }

  /* Probability her income survives to 95, given the pot and the allocation she
     is left holding. Interpolates linearly between the grid's withdrawal rates
     and between its equity levels. */
  function survival(surv, equity, rate) {
    if (!isFinite(rate) || rate <= 0) return 1;
    var rates = surv.rates, levels = surv.equity_levels;
    if (rate >= rates[rates.length - 1]) return 0;

    function rowAt(eq) {
      var row = surv.grid[eq.toFixed(1)];
      var j = 0;
      while (j < rates.length - 2 && rates[j + 1] < rate) j++;
      var t = (rate - rates[j]) / (rates[j + 1] - rates[j]);
      return row[j] + t * (row[j + 1] - row[j]);
    }

    var lo = levels[0], hi = levels[levels.length - 1];
    if (equity <= lo) return rowAt(lo);
    if (equity >= hi) return rowAt(hi);
    var k = 0;
    while (k < levels.length - 2 && levels[k + 1] < equity) k++;
    var w = (equity - levels[k]) / (levels[k + 1] - levels[k]);
    return rowAt(levels[k]) * (1 - w) + rowAt(levels[k + 1]) * w;
  }

  /*
   * picks: { decisionId: optionId }
   * Returns the full monthly history plus the three scores.
   */
  function run(D, picks) {
    var M = D.market, C = D.client, months = M.months;
    var n = months.length;
    var equityAssets = M.equity_assets;

    var byMonth = {};
    D.decisions.forEach(function (d) { byMonth[d.month] = d; });

    var model = OPENING_MODEL;
    var holdings = {};          // asset -> value, drifting between rebalances
    var reserve = 0;            // the ring-fenced cash sleeve
    var reserveYears = 0;
    var withdrawal = "fixed";
    var incomeSource = "auto";  // "auto" spends the reserve first, "invested" sells
    var fee = C.fee;
    var suspendUntil = -1;

    function setModel(name, total) {
      var w = M.models[name];
      holdings = {};
      for (var a in w) if (w.hasOwnProperty(a)) holdings[a] = total * w[a];
    }
    setModel(model, C.pot);

    function scale(factor) {
      for (var a in holdings) if (holdings.hasOwnProperty(a)) holdings[a] *= factor;
    }

    function equityWeight() {
      var total = sum(holdings);
      if (total <= 0) return 0;
      var eq = 0;
      for (var i = 0; i < equityAssets.length; i++) {
        eq += holdings[equityAssets[i]] || 0;
      }
      return eq / total;
    }

    var feeMonthly = monthlyRate(fee);
    var incomeStart = monthsBetween(C.start_month, C.income_from);

    var suitability = 0, conduct = 0, maxSuitability = 0, maxConduct = 0;
    var fileNotes = [], chosen = [];
    var series = { value: [], invested: [], reserve: [], income: [],
                   model: [], equity: [] };
    var totalFees = 0, totalIncome = 0, totalTarget = 0;
    var ruinMonth = null, breachMonths = 0;
    var variableAnnual = null;

    D.decisions.forEach(function (d) {
      var bs = -99, bc = -99;
      d.options.forEach(function (o) {
        bs = Math.max(bs, o.suitability || 0);
        bc = Math.max(bc, o.conduct || 0);
      });
      maxSuitability += bs;
      maxConduct += bc;
    });

    for (var m = 0; m < n; m++) {
      var month = months[m];
      var targetIncome = C.income * Math.pow(1 + C.inflation, m / 12);
      var invested = sum(holdings);

      /* ---- decisions take effect at the start of their month ---- */
      var d = byMonth[month];
      if (d) {
        var pick = picks[d.id], opt = null;
        for (var i = 0; i < d.options.length; i++) {
          if (d.options[i].id === pick) opt = d.options[i];
        }
        if (opt) {
          chosen.push({ decision: d.id, option: opt.id, label: opt.label,
                        month: month, title: d.title });
          if (opt.file) fileNotes.push({ month: month, text: opt.file });
          suitability += opt.suitability || 0;
          conduct += opt.conduct || 0;

          if (opt.one_off) {
            invested = Math.max(0, invested + opt.one_off);
            var before = sum(holdings);
            if (before > 0) scale(invested / before);
          }
          if (opt.model) {
            model = opt.model;
            setModel(model, invested);       // switching model means rebalancing
          } else if (opt.rebalance) {
            setModel(model, invested);
          }
          if (opt.fee !== undefined && opt.fee !== null) {
            fee = opt.fee;
            feeMonthly = monthlyRate(fee);
          }
          if (opt.withdrawal) withdrawal = opt.withdrawal;
          if (opt.income_source) incomeSource = opt.income_source;
          if (opt.suspend_months) suspendUntil = m + opt.suspend_months;
          if (opt.reserve_years !== undefined && opt.reserve_years !== null) {
            reserveYears = opt.reserve_years;
          }
        }
      }

      /* ---- the annual rebalance, and the annual top-up of the cash sleeve ----
         Annual rebalancing in January is the convention the paper's historical
         analysis uses. Between these dates the positions drift. */
      var isJanuary = month.slice(5) === "01";
      if (isJanuary && m > 0) {
        invested = sum(holdings);
        if (reserveYears > 0) {
          var want = reserveYears * targetIncome;
          if (reserve < want) {
            var take = Math.min(want - reserve, invested * 0.5);
            invested -= take;
            reserve += take;
          }
        }
        setModel(model, invested);
        if (withdrawal === "variable") {
          var raw = 0.04 * (invested + reserve);
          variableAnnual = Math.max(0.75 * targetIncome,
                                    Math.min(1.25 * targetIncome, raw));
        }
      }

      /* ---- markets: every position moves on its own return ---- */
      for (var a in holdings) {
        if (holdings.hasOwnProperty(a)) holdings[a] *= (1 + M.assets[a][m]);
      }
      reserve *= (1 + M.assets.CASH[m]);

      /* ---- the fee, charged on everything, every month ---- */
      invested = sum(holdings);
      var feeTaken = (invested + reserve) * feeMonthly;
      if (invested + reserve > 0) {
        var share = invested / (invested + reserve);
        if (invested > 0) scale(1 - (feeTaken * share) / invested);
        reserve -= feeTaken * (1 - share);
      }
      totalFees += feeTaken;

      /* ---- her income ---- */
      var paid = 0;
      if (m >= incomeStart) {
        totalTarget += targetIncome / 12;
        if (m >= suspendUntil) {
          var wantMonthly = (withdrawal === "variable" && variableAnnual !== null)
            ? variableAnnual / 12
            : targetIncome / 12;
          var need = wantMonthly;
          if (incomeSource !== "invested" && reserve > 0) {
            var fromReserve = Math.min(reserve, need);
            reserve -= fromReserve;
            need -= fromReserve;
          }
          invested = sum(holdings);
          var fromInvested = Math.min(Math.max(invested, 0), need);
          if (invested > 0 && fromInvested > 0) scale(1 - fromInvested / invested);
          need -= fromInvested;
          paid = wantMonthly - need;
          totalIncome += paid;
          if (need > 1 && ruinMonth === null) ruinMonth = m;
        }
      }

      if (reserve < 0) reserve = 0;
      invested = sum(holdings);

      /* ---- was this month's actual allocation defensible for her? ----
         Note this reads the drifted equity weight, not the model's label. */
      var band = bandFor(C.bands, month);
      var eqW = equityWeight();
      if (band && (eqW < band.min || eqW > band.max)) breachMonths++;

      series.value.push(invested + reserve);
      series.invested.push(invested);
      series.reserve.push(reserve);
      series.income.push(paid);
      series.model.push(model);
      series.equity.push(eqW);
    }

    /* ---- what happens after the data runs out ---- */
    var finalInvested = sum(holdings);
    var finalValue = finalInvested + reserve;
    // The reserve is cash, so it dilutes the equity weight she actually holds.
    var finalEquity = finalValue > 0
      ? equityWeight() * (finalInvested / finalValue) : 0;
    var finalIncome = C.income * Math.pow(1 + C.inflation, (n - 1) / 12);
    var drawRate = finalValue > 0 ? finalIncome / finalValue : Infinity;
    var lasts = survival(D.survival, finalEquity, drawRate);

    /* A band breach is not automatically wrong, so it costs less than an
       outright bad decision: one point per full year spent outside any
       defensible range, capped so it cannot swamp the choices themselves. */
    var breachPenalty = Math.min(6, Math.floor(breachMonths / 12));

    return {
      months: months,
      series: series,
      chosen: chosen,
      fileNotes: fileNotes,
      finalValue: finalValue,
      finalModel: model,
      finalEquity: finalEquity,
      finalIncome: finalIncome,
      drawRate: drawRate,
      survival: lasts,
      totalFees: totalFees,
      incomePaid: totalIncome,
      incomeTarget: totalTarget,
      incomeShortfall: totalTarget > 0 ? 1 - totalIncome / totalTarget : 0,
      ruinMonth: ruinMonth,
      breachMonths: breachMonths,
      scores: {
        suitability: suitability - breachPenalty,
        suitabilityMax: maxSuitability,
        conduct: conduct,
        conductMax: maxConduct,
        breachPenalty: breachPenalty
      }
    };
  }

  /* Which options can be offered from the state a player has actually reached.
     Re-runs the path up to that decision, so the menu never offers something
     incoherent, like drawing from a cash reserve that was never built. */
  function availableOptions(D, picks, decision) {
    var upto = {};
    for (var k = 0; k < D.decisions.length; k++) {
      var d = D.decisions[k];
      if (d.id === decision.id) break;
      if (picks[d.id]) upto[d.id] = picks[d.id];
    }
    var state = run(D, upto);
    var idx = D.market.months.indexOf(decision.month);
    var modelNow = idx > 0 ? state.series.model[idx - 1] : OPENING_MODEL;
    var reserveNow = idx > 0 ? state.series.reserve[idx - 1] : 0;
    var incomeNow = D.client.income *
      Math.pow(1 + D.client.inflation, Math.max(idx, 0) / 12);

    return decision.options.filter(function (o) {
      if (!o.requires) return true;
      if (o.requires.model_in &&
          o.requires.model_in.indexOf(modelNow) === -1) return false;
      if (o.requires.reserve_min !== undefined &&
          reserveNow < o.requires.reserve_min * incomeNow) return false;
      return true;
    });
  }

  return { run: run, availableOptions: availableOptions, survival: survival,
           monthsBetween: monthsBetween, OPENING_MODEL: OPENING_MODEL };
});
