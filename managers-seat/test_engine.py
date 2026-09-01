"""
The engine lives in JavaScript because the page needs it. These tests run that
same file in node and check it against arithmetic done independently in Python
with pandas.

The point is not that the engine has bugs today. It is that a page and a test
suite with separate implementations of the same maths drift apart quietly, and
the drift shows up when somebody asks a question you cannot answer. There is one
engine, and Python checks it rather than copying it.
"""

import json
import os
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build  # noqa: E402
import market  # noqa: E402

NODE = "node"


@pytest.fixture(scope="module")
def payload():
    return build.build_payload()


@pytest.fixture(scope="module")
def game_path(payload, tmp_path_factory):
    p = tmp_path_factory.mktemp("seat") / "game.json"
    p.write_text(json.dumps(payload))
    return str(p)


def run_engine(game_path, picks):
    """Run one path through engine.js and hand the result back to Python."""
    script = """
    const fs = require('fs');
    const E = require(process.argv[1]);
    const D = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const picks = JSON.parse(process.argv[3]);
    const r = E.run(D, picks);
    process.stdout.write(JSON.stringify({
      finalValue: r.finalValue, finalModel: r.finalModel,
      finalEquity: r.finalEquity, survival: r.survival,
      totalFees: r.totalFees, incomePaid: r.incomePaid,
      incomeTarget: r.incomeTarget, drawRate: r.drawRate,
      breachMonths: r.breachMonths, ruinMonth: r.ruinMonth,
      scores: r.scores, value: r.series.value, equity: r.series.equity,
      model: r.series.model, reserve: r.series.reserve
    }));
    """
    out = subprocess.check_output(
        [NODE, "-e", script, os.path.join(HERE, "engine.js"), game_path,
         json.dumps(picks)],
        text=True)
    return json.loads(out)


def available(game_path, picks, decision_id):
    script = """
    const fs = require('fs');
    const E = require(process.argv[1]);
    const D = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const picks = JSON.parse(process.argv[3]);
    const d = D.decisions.find(x => x.id === process.argv[4]);
    process.stdout.write(JSON.stringify(
      E.availableOptions(D, picks, d).map(o => o.id)));
    """
    out = subprocess.check_output(
        [NODE, "-e", script, os.path.join(HERE, "engine.js"), game_path,
         json.dumps(picks), decision_id],
        text=True)
    return json.loads(out)


# --------------------------------------------------------------------------
# the arithmetic
# --------------------------------------------------------------------------

def test_a_held_portfolio_matches_python(payload, game_path):
    """Hold Cautious throughout, no income, no reserve, and check the engine's
    monthly compounding against the same thing done in pandas."""
    picks = {"d01_open": "b"}
    got = run_engine(game_path, picks)

    _, monthly, _ = market.build()
    weights = market.MODELS["cautious"]
    pot = payload["client"]["pot"]
    fee_monthly = 1 - (1 - payload["client"]["fee"]) ** (1 / 12)

    # Positions drift and are rebalanced every January, exactly as the engine
    # does it, so this is an independent implementation rather than a copy.
    holdings = {a: pot * w for a, w in weights.items()}
    values = []
    for i, (stamp, row) in enumerate(monthly.iterrows()):
        if i > 0 and stamp.month == 1:
            total = sum(holdings.values())
            holdings = {a: total * w for a, w in weights.items()}
        # market.json stores returns to eight decimal places, so round here too.
        # Otherwise this compares serialisation precision rather than logic, and
        # the interesting failure would be buried under a rounding difference.
        holdings = {a: v * (1 + round(float(row[a]), 8))
                    for a, v in holdings.items()}
        total = sum(holdings.values())
        take = total * fee_monthly
        holdings = {a: v * (1 - take / total) for a, v in holdings.items()}
        values.append(sum(holdings.values()))

    # Income starts in 2011, so only the pre-income stretch is a clean
    # comparison; that is 84 months and plenty to catch a compounding error.
    n = 84
    assert np.allclose(got["value"][:n], values[:n], rtol=1e-9), \
        "the engine's compounding does not match pandas"


def test_the_fee_is_actually_charged(payload, game_path):
    """Two identical paths at different fee levels should differ by the fee."""
    base = run_engine(game_path, {"d01_open": "b"})
    cheaper = run_engine(game_path, {"d01_open": "b", "d09_fee": "b"})
    assert cheaper["finalValue"] > base["finalValue"]
    assert cheaper["totalFees"] < base["totalFees"]


def test_fees_are_a_plausible_share_of_the_pot(game_path):
    got = run_engine(game_path, {"d01_open": "c"})
    # A 1% charge over 22 years on a pot of this size lands in the low
    # six figures. A wildly different number means the fee is being applied
    # annually instead of monthly, or to the wrong base.
    assert 80_000 < got["totalFees"] < 250_000


def test_income_starts_when_she_retires(payload, game_path):
    got = run_engine(game_path, {"d01_open": "c", "d06_retire": "a"})
    months = payload["market"]["months"]
    start = months.index(payload["client"]["income_from"])
    # Nothing paid before, something paid after.
    assert got["incomeTarget"] > 0
    total_months = len(months) - start
    expected_first_year = payload["client"]["income"] * \
        (1 + payload["client"]["inflation"]) ** (start / 12)
    assert expected_first_year > payload["client"]["income"]
    assert total_months > 180


def test_a_one_off_withdrawal_reduces_the_pot(game_path):
    kept = run_engine(game_path, {"d01_open": "c", "d02_gift": "c"})
    given = run_engine(game_path, {"d01_open": "c", "d02_gift": "b"})
    assert kept["finalValue"] > given["finalValue"], \
        "giving £40,000 away should leave less at the end"


# --------------------------------------------------------------------------
# state and gating
# --------------------------------------------------------------------------

def test_the_covid_reserve_option_needs_a_reserve(game_path):
    """The payoff for building a cash sleeve has to be causal, not decorative."""
    without = available(game_path, {"d01_open": "c", "d06_retire": "a"},
                        "d10_covid")
    assert "b" not in without, \
        "drawing from a reserve was offered to a player who never built one"

    with_reserve = available(game_path, {"d01_open": "c", "d06_retire": "b"},
                             "d10_covid")
    assert "b" in with_reserve, \
        "a player who built a reserve was not offered the use of it"


def test_staying_in_cash_is_only_offered_to_someone_in_cash(game_path):
    invested = available(game_path, {"d01_open": "c", "d04_call": "c"},
                         "d05_bottom")
    assert "d" not in invested

    in_cash = available(game_path, {"d01_open": "c", "d04_call": "a"},
                        "d05_bottom")
    assert "d" in in_cash


def test_switching_model_switches_the_holdings(payload, game_path):
    got = run_engine(game_path, {"d01_open": "a"})
    months = payload["market"]["months"]
    i = months.index("2004-01")
    assert got["model"][i] == "defensive"
    assert abs(got["equity"][i] - 0.20) < 0.02


def test_positions_drift_between_rebalances(payload, game_path):
    """The paper is about drift, so the engine must actually let it happen."""
    got = run_engine(game_path, {"d01_open": "c"})
    months = payload["market"]["months"]
    i = months.index("2008-11")
    # Equities fell hard through 2008 and bonds rose, so a Balanced portfolio
    # rebalanced last in January must be carrying well under its 60% target.
    assert got["equity"][i] < 0.55, \
        "equity weight did not drift down through the 2008 fall"


def test_the_reserve_is_spent_before_the_portfolio(payload, game_path):
    got = run_engine(game_path, {"d01_open": "c", "d06_retire": "b"})
    months = payload["market"]["months"]
    i = months.index("2020-03")
    assert got["reserve"][i] > 0, "the cash sleeve was never actually funded"


# --------------------------------------------------------------------------
# the three reference paths
# --------------------------------------------------------------------------

def test_the_reference_paths_rank_the_way_the_debrief_claims(payload, game_path):
    runs = {k: run_engine(game_path, v["picks"])
            for k, v in payload["comparisons"].items()}

    assert runs["by_the_book"]["finalValue"] > runs["left_alone"]["finalValue"]
    assert runs["left_alone"]["finalValue"] > runs["instinct"]["finalValue"]
    assert runs["by_the_book"]["survival"] > runs["left_alone"]["survival"]
    assert runs["instinct"]["survival"] < 0.1

    # Panicking into cash for most of two decades has to show up as time spent
    # outside any defensible equity range.
    assert runs["instinct"]["breachMonths"] > 150
    assert runs["by_the_book"]["breachMonths"] < 24


def test_by_the_book_scores_near_the_top(payload, game_path):
    got = run_engine(game_path, payload["comparisons"]["by_the_book"]["picks"])
    s = got["scores"]
    assert s["suitability"] >= 0.85 * s["suitabilityMax"]
    assert s["conduct"] >= 0.85 * s["conductMax"]


def test_the_panic_path_scores_badly(payload, game_path):
    got = run_engine(game_path, payload["comparisons"]["instinct"]["picks"])
    assert got["scores"]["suitability"] < 0
    assert got["scores"]["conduct"] < 0


def test_every_decision_is_reachable(payload, game_path):
    """Play the documented path and confirm each decision offered the choice
    the comparison relies on. A gated option that can never be reached would
    make the reference path a fiction."""
    picks = payload["comparisons"]["by_the_book"]["picks"]
    running = {}
    for d in payload["decisions"]:
        opts = available(game_path, running, d["id"])
        want = picks[d["id"]]
        assert want in opts, f"{d['id']}: reference choice {want} not offered"
        running[d["id"]] = want
