"""
Monte Carlo simulation of the risk-graded portfolios, by historical block
bootstrap.

Why block bootstrap rather than the usual normal-distribution Monte Carlo?
A normal model assumes returns are independent and bell-shaped. They are not:
real markets have fat tails, and, as the main analysis shows, the correlation
between equities and bonds can flip. Standard planning-tool Monte Carlo would
miss exactly that. Instead we resample actual history in blocks of consecutive
months, which keeps real crashes, real fat tails, and the real joint behaviour
of the assets intact. The honest limitation: it still assumes the future looks
like the 2003 to 2026 sample, so it cannot invent a brand-new regime.

Two questions are answered:
  1. Accumulation: over 30 years, what is the range of outcomes for each risk
     level? (A label is a point; the outcome is a wide distribution.)
  2. Decumulation: for a retiree drawing an income, what is the probability the
     money lasts 30 years for each risk level?

Run (after fetch_data.py):
    python3 monte_carlo.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
FIG_DIR = os.path.join(HERE, "..", "figures")

# ---- assumptions (all stated so they can be challenged and changed) ----
ASSETS = ["SPY", "EFA", "EEM", "AGG"]
N_PATHS = 10_000
HORIZON_YEARS = 30
BLOCK_MONTHS = 6           # length of each resampled block
POT = 500_000             # starting pot for the decumulation test (GBP)
WITHDRAW_RATE = 0.04       # 4% of the initial pot, the classic starting point
INFLATION = 0.025          # withdrawals grow 2.5% a year
SEED = 42

def equity_split(equity):
    return {"SPY": 0.60 * equity, "EFA": 0.30 * equity,
            "EEM": 0.10 * equity, "AGG": round(1 - equity, 4)}

PORTFOLIOS = {
    "Defensive (20%)":   equity_split(0.20),
    "Cautious (40%)":    equity_split(0.40),
    "Balanced (60%)":    equity_split(0.60),
    "Growth (80%)":      equity_split(0.80),
    "Adventurous (100%)":equity_split(1.00),
}


def monthly_returns():
    """Monthly total returns for each asset, lined up on common months."""
    cols = {}
    for t in ASSETS:
        s = pd.read_csv(os.path.join(DATA_DIR, f"{t}.csv"),
                        parse_dates=["date"], index_col="date")["adj_close"]
        cols[t] = s.resample("ME").last().pct_change()
    df = pd.concat(cols, axis=1).dropna()
    return df[ASSETS]


def bootstrap_paths(returns, horizon_months, rng):
    """Return an array (N_PATHS, horizon_months, n_assets) of resampled returns,
    built from randomly placed blocks of consecutive real months."""
    R = returns.to_numpy()
    T = R.shape[0]
    n_blocks = int(np.ceil(horizon_months / BLOCK_MONTHS))
    starts = rng.integers(0, T - BLOCK_MONTHS + 1, size=(N_PATHS, n_blocks))
    offsets = np.arange(BLOCK_MONTHS)
    idx = (starts[:, :, None] + offsets[None, None, :])
    idx = idx.reshape(N_PATHS, n_blocks * BLOCK_MONTHS)[:, :horizon_months]
    return R[idx]  # (N_PATHS, horizon_months, n_assets)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    returns = monthly_returns()
    H = HORIZON_YEARS * 12
    sim = bootstrap_paths(returns, H, rng)  # shared paths for every portfolio

    lines = []
    def out(s=""):
        print(s); lines.append(s)

    out("# Monte Carlo results (historical block bootstrap)\n")
    out(f"{N_PATHS:,} paths, {HORIZON_YEARS}-year horizon, {BLOCK_MONTHS}-month "
        f"blocks, sampled from {returns.index[0].date()} to {returns.index[-1].date()}.")
    out("Monthly rebalancing; returns are nominal. The decumulation test uses a "
        f"GBP {POT:,} pot, a {WITHDRAW_RATE*100:.0f}% initial withdrawal growing "
        f"{INFLATION*100:.1f}% a year.\n")

    # portfolio monthly returns for every path: (N_PATHS, H) per portfolio
    port_returns = {}
    for name, w in PORTFOLIOS.items():
        weights = np.array([w[a] for a in ASSETS])
        port_returns[name] = sim @ weights

    # ---- Accumulation: distribution of a 1 pound investment after 30 years ----
    out("## Accumulation - value of £1 after 30 years (range of outcomes)\n")
    out("| Portfolio | 5th pct | 25th | Median | 75th | 95th |")
    out("|-----------|--------|------|--------|------|------|")
    fan = {}
    for name, pr in port_returns.items():
        wealth = np.cumprod(1 + pr, axis=1)          # (N_PATHS, H) growth of £1
        terminal = wealth[:, -1]
        fan[name] = wealth
        pcts = np.percentile(terminal, [5, 25, 50, 75, 95])
        out(f"| {name} | £{pcts[0]:.1f} | £{pcts[1]:.1f} | £{pcts[2]:.1f} | "
            f"£{pcts[3]:.1f} | £{pcts[4]:.1f} |")
    out()
    # how wide is the range within one label?
    bal = np.cumprod(1 + port_returns["Balanced (60%)"], axis=1)[:, -1]
    out(f"Even inside one label, the spread is large: a 'balanced' £1 lands "
        f"anywhere from about £{np.percentile(bal,5):.1f} to £{np.percentile(bal,95):.1f} "
        f"(5th to 95th percentile) after 30 years.\n")

    # ---- Decumulation: probability the pot lasts 30 years ----
    infl_m = (1 + INFLATION) ** (1 / 12)
    withdrawals = (POT * WITHDRAW_RATE / 12) * infl_m ** np.arange(H)
    out("## Decumulation - probability a £500k pot lasts 30 years (4% inflation-linked)\n")
    out("| Portfolio | Probability of lasting 30 years | Median years it lasted |")
    out("|-----------|--------------------------------|------------------------|")
    survival = {}
    for name, pr in port_returns.items():
        total = np.full(N_PATHS, float(POT))
        alive = np.ones(N_PATHS, dtype=bool)
        first_zero = np.full(N_PATHS, H)  # month it ran out, default = survived
        for m in range(H):
            total = total * (1 + pr[:, m]) - withdrawals[m]
            just_died = alive & (total <= 0)
            first_zero[just_died] = m
            alive &= total > 0
        prob = alive.mean()
        survival[name] = prob
        med_years = np.median(np.where(alive, H, first_zero)) / 12
        out(f"| {name} | {prob*100:.0f}% | {med_years:.0f}+ |")
    out()
    best = max(survival, key=survival.get)
    out(f"Highest survival probability: {best} at {survival[best]*100:.0f}%. "
        f"Note the most cautious portfolio is not automatically the safest for a "
        f"drawdown client: too little growth can lose to inflation and longevity "
        f"just as too much risk can lose to a bad early sequence.\n")

    # -------------------- charts --------------------
    # Chart: accumulation fan for the Balanced portfolio
    wealth = fan["Balanced (60%)"]
    months = np.arange(H) / 12
    lo, q25, med, q75, hi = [np.percentile(wealth, p, axis=0) for p in (5, 25, 50, 75, 95)]
    plt.figure(figsize=(10, 6))
    plt.fill_between(months, lo, hi, color="#4C78A8", alpha=0.15, label="5th–95th percentile")
    plt.fill_between(months, q25, q75, color="#4C78A8", alpha=0.30, label="25th–75th percentile")
    plt.plot(months, med, color="#1f4e79", linewidth=2, label="median")
    plt.title("Accumulation: range of outcomes for a 'balanced' £1 over 30 years")
    plt.xlabel("Years"); plt.ylabel("Value of £1 invested")
    plt.legend(loc="upper left"); plt.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, "mc_accumulation_fan.png"), dpi=120, bbox_inches="tight")
    plt.close()

    # Chart: decumulation survival probability by risk level
    names = list(survival)
    probs = [survival[n] * 100 for n in names]
    # highlight the lowest-survival portfolio (the "safe" one that was not safe)
    worst = int(np.argmin(probs))
    colors = ["#B0413E" if i == worst else "#4C78A8" for i in range(len(names))]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, probs, color=colors)
    for b, p in zip(bars, probs):
        plt.text(b.get_x() + b.get_width()/2, p + 1, f"{p:.0f}%", ha="center", fontsize=10)
    plt.ylim(0, 105)
    plt.title("Decumulation: probability a £500k pot lasts 30 years (4% inflation-linked)")
    plt.ylabel("Probability of success (%)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(alpha=0.3, axis="y")
    plt.savefig(os.path.join(FIG_DIR, "mc_decumulation_survival.png"), dpi=120, bbox_inches="tight")
    plt.close()

    with open(os.path.join(HERE, "monte_carlo_results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\nWrote monte_carlo_results.md and two charts to ../figures/")


if __name__ == "__main__":
    main()
