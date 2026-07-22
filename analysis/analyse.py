"""
The analysis. Builds the risk-graded portfolios, measures their risk, and runs
the three tests described in the top-level README.

Everything here is deliberately explicit rather than clever, so that every
number can be traced back to a line of code and explained out loud.

Run (after fetch_data.py):
    python3 analyse.py

Outputs:
    - prints a results summary
    - writes results.md  (the numbers, ready to paste into the README)
    - writes ../figures/*.png  (the charts)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no screen in this environment; save charts to file
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
FIG_DIR = os.path.join(HERE, "..", "figures")
TRADING_DAYS = 252

# ---------------------------------------------------------------------------
# 1. Load the price series and line them up on the same trading days.
# ---------------------------------------------------------------------------
def load_prices():
    series = {}
    for ticker in ["SPY", "EFA", "EEM", "RSP", "AGG", "SOXX"]:
        df = pd.read_csv(os.path.join(DATA_DIR, f"{ticker}.csv"),
                         parse_dates=["date"], index_col="date")
        series[ticker] = df["adj_close"].rename(ticker)
    # inner join keeps only days present in every series
    prices = pd.concat(series.values(), axis=1, join="inner").dropna()
    return prices


# ---------------------------------------------------------------------------
# 2. Build a portfolio that is rebalanced to its target weights every year.
#    Between rebalances the weights drift with the market, exactly as a real
#    portfolio left alone for a year would.
# ---------------------------------------------------------------------------
def portfolio_value(prices, weights):
    """weights: dict like {'SPY': 0.6, 'AGG': 0.4}. Returns a value series."""
    value = pd.Series(index=prices.index, dtype=float)
    running = 1.0
    for year, block in prices.groupby(prices.index.year):
        start = block.iloc[0]
        # growth of each asset since the first trading day of the year
        growth = block[list(weights)] / start[list(weights)]
        # portfolio growth within the year = weighted sum of asset growth
        within = (growth * pd.Series(weights)).sum(axis=1)
        value.loc[block.index] = running * within
        running = value.loc[block.index].iloc[-1]  # carry year-end value forward
    return value


# ---------------------------------------------------------------------------
# 3. Risk and return measures.
# ---------------------------------------------------------------------------
def annual_vol(value):
    daily = value.pct_change().dropna()
    return daily.std() * np.sqrt(TRADING_DAYS)

def max_drawdown(value):
    return (value / value.cummax() - 1.0).min()

def worst_rolling_year(value):
    roll = value / value.shift(TRADING_DAYS) - 1.0
    return roll.min()

def cagr(value):
    years = (value.index[-1] - value.index[0]).days / 365.25
    return (value.iloc[-1] / value.iloc[0]) ** (1 / years) - 1

def calendar_year_return(value, year):
    block = value[value.index.year == year]
    if len(block) < 2:
        return np.nan
    return block.iloc[-1] / block.iloc[0] - 1

def drawdown_in_window(value, start, end):
    w = value[(value.index >= start) & (value.index <= end)]
    if len(w) < 2:
        return np.nan
    return (w / w.cummax() - 1.0).min()


# ---------------------------------------------------------------------------
# 4. Definitions: the risk-graded portfolios plus a semis-tilted sleeve.
#
# The equity portion is a GLOBAL blend, not just the US, because that is what a
# UK wealth manager's model portfolios actually hold. We split every unit of
# equity as 60% US (SPY), 30% developed-ex-US (EFA), 10% emerging (EEM), which
# is roughly global market-cap weight. The bond portion is a high-quality
# aggregate bond holding (AGG). So a "cautious" 40% equity portfolio is really
# 24% US + 12% developed + 4% emerging + 60% bonds.
# ---------------------------------------------------------------------------
def graded(equity):
    """Return the ticker weights for a portfolio with `equity` in global stocks."""
    return {
        "SPY": 0.60 * equity,
        "EFA": 0.30 * equity,
        "EEM": 0.10 * equity,
        "AGG": round(1 - equity, 4),
    }

PORTFOLIOS = {
    "Defensive (20/80)":   graded(0.20),
    "Cautious (40/60)":    graded(0.40),
    "Balanced (60/40)":    graded(0.60),
    "Growth (80/20)":      graded(0.80),
    "Adventurous (100/0)": graded(1.00),
    # An adventurous theme bet: 70% global equity, 30% semiconductors.
    "Semis-tilt (70/30)":  {"SPY": 0.42, "EFA": 0.21, "EEM": 0.07, "SOXX": 0.30},
}

STRESS = {
    "2008 financial crisis": ("2007-10-01", "2009-06-30"),
    "2020 COVID crash":      ("2020-02-01", "2020-04-30"),
    "2022 rate shock":       ("2022-01-01", "2022-12-31"),
}


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    prices = load_prices()
    start, end = prices.index[0].date(), prices.index[-1].date()

    values = {name: portfolio_value(prices, w) for name, w in PORTFOLIOS.items()}
    # standalone semiconductor series (100% SOXX) for the "extreme theme" point
    soxx = prices["SOXX"] / prices["SOXX"].iloc[0]
    values_all = dict(values)
    values_all["Semis only (100% SOXX)"] = soxx

    lines = []
    def out(s=""):
        print(s)
        lines.append(s)

    out(f"# Results\n")
    out(f"Window: {start} to {end}  ({(prices.index[-1]-prices.index[0]).days/365.25:.1f} years)")
    out(f"Equity is a global blend (60% US SPY, 30% developed-ex-US EFA, "
        f"10% emerging EEM). Bonds are AGG. RSP (equal-weight US) is used only "
        f"for the concentration test, SOXX (semiconductors) for the theme test. "
        f"All series are total-return (dividends reinvested).\n")

    # ---- full-period metrics table ----
    out("## Full-period risk and return (annual rebalancing)\n")
    out("| Portfolio | CAGR | Volatility | Max drawdown | Worst 12 months |")
    out("|-----------|------|-----------|--------------|-----------------|")
    for name, v in values_all.items():
        out(f"| {name} | {cagr(v)*100:.1f}% | {annual_vol(v)*100:.1f}% | "
            f"{max_drawdown(v)*100:.1f}% | {worst_rolling_year(v)*100:.1f}% |")
    out()

    # ---- calendar-year returns in key years ----
    key_years = [2008, 2020, 2022, 2023, 2024]
    out("## Calendar-year total return in key years\n")
    out("| Portfolio | " + " | ".join(str(y) for y in key_years) + " |")
    out("|" + "---|" * (len(key_years) + 1))
    for name, v in values_all.items():
        cells = " | ".join(f"{calendar_year_return(v, y)*100:+.1f}%" for y in key_years)
        out(f"| {name} | {cells} |")
    out()

    # ---- drawdown in each stress episode ----
    out("## Maximum drawdown within each stress episode\n")
    out("| Portfolio | " + " | ".join(STRESS) + " |")
    out("|" + "---|" * (len(STRESS) + 1))
    for name, v in values_all.items():
        cells = " | ".join(f"{drawdown_in_window(v, s, e)*100:.1f}%"
                            for s, e in STRESS.values())
        out(f"| {name} | {cells} |")
    out()

    # ---- TEST 1: did cautious behave like 'cautious' in 2022? ----
    caut_2022 = calendar_year_return(values["Cautious (40/60)"], 2022)
    bal_2022 = calendar_year_return(values["Balanced (60/40)"], 2022)
    adv_2022 = calendar_year_return(values["Adventurous (100/0)"], 2022)
    def_2022 = calendar_year_return(values["Defensive (20/80)"], 2022)
    out("## Test 1 - the cautious label in 2022\n")
    out(f"- Defensive (20% equity) 2022 return: {def_2022*100:+.1f}%")
    out(f"- Cautious (40% equity) 2022 return:  {caut_2022*100:+.1f}%")
    out(f"- Balanced (60% equity) 2022 return:  {bal_2022*100:+.1f}%")
    out(f"- Adventurous (100% equity) 2022 return: {adv_2022*100:+.1f}%")
    if adv_2022 != 0:
        out(f"- The cautious portfolio captured {caut_2022/adv_2022*100:.0f}% of the "
            f"all-equity loss despite holding only 40% equity.")
    out()

    # ---- TEST 2: concentration, cap-weight vs equal-weight ----
    spy = prices["SPY"] / prices["SPY"].iloc[0]
    rsp = prices["RSP"] / prices["RSP"].iloc[0]
    # relative strength of cap-weight over equal-weight
    rel = spy / rsp
    gap_2023 = (spy[spy.index.year == 2023].iloc[-1] / spy[spy.index.year == 2023].iloc[0]) - \
               (rsp[rsp.index.year == 2023].iloc[-1] / rsp[rsp.index.year == 2023].iloc[0])
    gap_2024 = (spy[spy.index.year == 2024].iloc[-1] / spy[spy.index.year == 2024].iloc[0]) - \
               (rsp[rsp.index.year == 2024].iloc[-1] / rsp[rsp.index.year == 2024].iloc[0])
    out("## Test 2 - concentration (cap-weight SPY vs equal-weight RSP)\n")
    out(f"- 2023 return gap (SPY minus RSP): {gap_2023*100:+.1f} pts")
    out(f"- 2024 return gap (SPY minus RSP): {gap_2024*100:+.1f} pts")
    out(f"- A positive gap means the cap-weighted index beat its equal-weighted twin "
        f"purely because a few mega-caps carried it: the concentration effect.")
    out()

    # ---- TEST 3: the theme and who could hold it ----
    soxx_2023 = calendar_year_return(soxx, 2023)
    soxx_2024 = calendar_year_return(soxx, 2024)
    soxx_2022 = calendar_year_return(soxx, 2022)
    soxx_2008 = calendar_year_return(soxx, 2008)
    out("## Test 3 - the AI/semis theme and the risk it demanded\n")
    out(f"- Semis (SOXX) 2023: {soxx_2023*100:+.1f}%   2024: {soxx_2024*100:+.1f}%")
    out(f"- Semis (SOXX) 2022: {soxx_2022*100:+.1f}%   2008: {soxx_2008*100:+.1f}%")
    out(f"- Semis full-period max drawdown: {max_drawdown(soxx)*100:.1f}%  "
        f"(volatility {annual_vol(soxx)*100:.1f}%)")
    out(f"- The reward was real, but only a client who could hold through a "
        f"{max_drawdown(soxx)*100:.0f}% drawdown could ever collect it.")
    out()

    # -----------------------------------------------------------------------
    # Charts
    # -----------------------------------------------------------------------
    # Chart A: growth of the risk-graded portfolios
    plt.figure(figsize=(10, 6))
    for name in ["Defensive (20/80)", "Cautious (40/60)", "Balanced (60/40)",
                 "Growth (80/20)", "Adventurous (100/0)"]:
        plt.plot(values[name].index, values[name], label=name)
    plt.title("Growth of £1: risk-graded portfolios (annual rebalancing)")
    plt.ylabel("Value of £1 invested")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, "risk_graded_growth.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # Chart B: concentration, SPY vs RSP relative
    plt.figure(figsize=(10, 6))
    plt.plot(rel.index, rel, color="darkred")
    plt.title("Concentration: cap-weighted (SPY) relative to equal-weighted (RSP)")
    plt.ylabel("SPY / RSP (rising = mega-caps pulling ahead)")
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, "concentration_spy_vs_rsp.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # Chart C: the theme's reward on top, its drawdown underneath, against a
    # broad global-equity portfolio for context. Two stacked panels.
    adv = values["Adventurous (100/0)"]
    adv_norm = adv / adv.iloc[0]
    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(10, 7.5), sharex=True,
        gridspec_kw={"height_ratios": [2, 1], "hspace": 0.08})
    top.plot(soxx.index, soxx, color="#1B7A6E", label="Semiconductors (SOXX)")
    top.plot(adv_norm.index, adv_norm, color="#7A7A7A", label="Adventurous (global equity)")
    top.set_yscale("log")
    top.set_ylabel("Growth of £1 (log scale)")
    top.set_title("The AI/semis theme: far more reward, far deeper holes")
    top.legend(loc="upper left")
    top.grid(alpha=0.3)
    dd_soxx = (soxx / soxx.cummax() - 1.0) * 100
    dd_adv = (adv / adv.cummax() - 1.0) * 100
    bot.fill_between(dd_soxx.index, dd_soxx, 0, color="#1B7A6E", alpha=0.25)
    bot.plot(dd_soxx.index, dd_soxx, color="#1B7A6E", linewidth=0.8, label="Semiconductors")
    bot.plot(dd_adv.index, dd_adv, color="#7A7A7A", linewidth=0.9, label="Global equity")
    bot.set_ylabel("Drawdown (%)")
    bot.set_xlabel("")
    bot.legend(loc="lower left", fontsize=8)
    bot.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, "semis_reward_vs_drawdown.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # Chart D (the headline): the bond cushion worked in 2008, failed in 2022.
    caut = values["Cautious (40/60)"]
    adv = values["Adventurous (100/0)"]
    caut_08, adv_08 = calendar_year_return(caut, 2008), calendar_year_return(adv, 2008)
    caut_22, adv_22 = calendar_year_return(caut, 2022), calendar_year_return(adv, 2022)
    fig, ax = plt.subplots(figsize=(9, 6.5))
    groups = ["2008\n(bonds cushioned)", "2022\n(bonds fell too)"]
    x = np.arange(len(groups))
    width = 0.35
    lo = min(caut_08, adv_08, caut_22, adv_22) * 100
    ax.set_ylim(lo - 6, 14)  # headroom above 0 for the annotations, below for labels
    ax.bar(x - width/2, [caut_08*100, caut_22*100], width,
           label="Cautious (40% equity)", color="#4C78A8")
    ax.bar(x + width/2, [adv_08*100, adv_22*100], width,
           label="Adventurous (100% equity)", color="#B0413E")
    for i, (c, a) in enumerate([(caut_08, adv_08), (caut_22, adv_22)]):
        ax.text(i - width/2, c*100 - 1.0, f"{c*100:.0f}%", ha="center", va="top", fontsize=10)
        ax.text(i + width/2, a*100 - 1.0, f"{a*100:.0f}%", ha="center", va="top", fontsize=10)
        share = c / a * 100
        ax.text(i, 9, f"cautious took {share:.0f}%\nof the equity loss",
                ha="center", va="center", fontsize=9, style="italic")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("Calendar-year total return (%)")
    ax.set_title("Does 'cautious' mean cautious? The bond cushion in 2008 vs 2022",
                 pad=14)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3, axis="y")
    plt.savefig(os.path.join(FIG_DIR, "bond_cushion_2008_vs_2022.png"), dpi=120, bbox_inches="tight")
    plt.close()

    with open(os.path.join(HERE, "results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\nWrote results.md and three charts to ../figures/")


if __name__ == "__main__":
    main()
