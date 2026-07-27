"""
The market layer: real history, turned into something the page can replay.

Everything the simulator does to a portfolio happens against actual monthly
returns from the CSVs in ../data/. No scenario is invented and no path is
pre-baked. The page ships the return series for every model portfolio it
offers, so whatever sequence of decisions a player makes, the outcome is
computed from the real returns that followed each decision.

Two design choices worth defending out loud:

1. Monthly, not daily. A 22-year replay at daily frequency would be a large
   payload for a page that has to work on a phone, and the decisions in this
   simulator are made at monthly-or-slower granularity. Where the narrative
   quotes a sharp intra-month fall (COVID, February to March 2020), that figure
   is measured from daily data in `context.py` and stated as such, so the story
   stays honest even though the engine runs monthly.

2. Asset-level returns, not model-level ones. It would be smaller and simpler
   to ship one return series per model portfolio, but that would quietly hold
   every model at its target weights forever, and a portfolio that cannot drift
   away from its target cannot demonstrate the thing the paper is about. So the
   page gets the underlying assets and the engine holds actual positions, lets
   them drift with markets, and rebalances annually in the way the paper's
   historical analysis does. The equity weight the suitability check sees is
   therefore the real drifted one, not the label.

Run:
    python3 market.py        # writes market.json and prints a summary
"""

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")

# The simulator starts at the first full month of 2004 and runs to the end of
# the data. 2003 is left out because the common window opens in October 2003
# and a part-year start would make the first annual review ragged.
START = "2004-01"

ETFS = ["SPY", "EFA", "EEM", "RSP", "AGG", "SHY"]

# The equity sleeve is the same global blend the paper uses everywhere: 60% US,
# 30% developed outside the US, 10% emerging, roughly global market-cap weight.
EQUITY = {"SPY": 0.60, "EFA": 0.30, "EEM": 0.10}

# The same blend with the US leg held equal-weighted instead of cap-weighted.
# This is the paper's concentration finding turned into something a manager can
# actually do: it keeps the equity weight identical and changes only how the US
# sleeve is spread across companies.
EQUITY_EW = {"RSP": 0.60, "EFA": 0.30, "EEM": 0.10}

# Anything in here counts as equity for the suitability scoring, so an
# equal-weighted sleeve is correctly treated as the same amount of equity risk.
EQUITY_ASSETS = {"SPY", "EFA", "EEM", "RSP"}


def _equity(weight, blend=None):
    blend = blend or EQUITY
    return {k: round(v * weight, 6) for k, v in blend.items()}


def _model(equity_weight, defensive_asset="AGG", blend=None):
    """A model portfolio: an equity sleeve plus one defensive asset."""
    w = _equity(equity_weight, blend)
    rest = round(1.0 - equity_weight, 6)
    if rest > 0:
        w[defensive_asset] = rest
    return w


# The menu a manager can choose from. The first five are the paper's
# risk-graded models. The two "short" variants hold 1-3 year Treasuries instead
# of aggregate bonds, which is how a manager actually cuts interest-rate risk
# without cutting equity: the lesson of 2022 was about duration, not about
# owning bonds at all. Cash is the panic button, and it is on the menu because
# clients ask for it.
MODELS = {
    "cash":            {"CASH": 1.0},
    "defensive":       _model(0.20),
    "cautious":        _model(0.40),
    "balanced":        _model(0.60),
    "growth":          _model(0.80),
    "adventurous":     _model(1.00),
    "cautious_short":  _model(0.40, "SHY"),
    "balanced_short":  _model(0.60, "SHY"),
    "cautious_ew":     _model(0.40, "AGG", EQUITY_EW),
    "balanced_ew":     _model(0.60, "AGG", EQUITY_EW),
}

MODEL_LABELS = {
    "cash":           "Cash",
    "defensive":      "Defensive (20% equity)",
    "cautious":       "Cautious (40% equity)",
    "balanced":       "Balanced (60% equity)",
    "growth":         "Growth (80% equity)",
    "adventurous":    "Adventurous (100% equity)",
    "cautious_short": "Cautious, short duration (40% equity)",
    "balanced_short": "Balanced, short duration (60% equity)",
    "cautious_ew":    "Cautious, equal-weighted US (40% equity)",
    "balanced_ew":    "Balanced, equal-weighted US (60% equity)",
}

# Equity weight per model, used by the suitability scoring.
MODEL_EQUITY = {name: round(sum(v for k, v in w.items()
                                if k in EQUITY_ASSETS), 4)
                for name, w in MODELS.items()}


def load_monthly_returns():
    """Monthly total returns for every asset the models can hold, including a
    cash series built from the Treasury bill rate."""
    cols = {}
    for ticker in ETFS:
        path = os.path.join(DATA_DIR, f"{ticker}.csv")
        s = pd.read_csv(path, parse_dates=["date"], index_col="date")["adj_close"]
        cols[ticker] = s.resample("ME").last().pct_change()

    cols["CASH"] = cash_monthly_returns()

    df = pd.concat(cols, axis=1).dropna()
    return df.loc[START:]


def cash_monthly_returns():
    """Turn the 13-week Treasury bill yield into a monthly return series.

    ^IRX is quoted as an annualised discount rate in percent. Bills accrue on an
    actual/360 basis, so a day at a 5% quoted rate earns roughly 0.05/360. We
    accrue day by day at whatever rate prevailed, which means the cash leg earns
    5% in 2007 and close to nothing from 2010 to 2021, exactly as a real client
    sitting in cash would have.

    This is a simplification in the client's favour: a retail client would earn
    less than the bill rate after a platform's interest margin. Cash therefore
    looks slightly better here than it really was, which biases the simulator
    against the argument it ends up making, and that is the safe direction for
    a bias to run.
    """
    path = os.path.join(DATA_DIR, "IRX.csv")
    y = pd.read_csv(path, parse_dates=["date"], index_col="date")["yield_pct"]
    y = y.sort_index()
    # Calendar days between quotes, so weekends and holidays still accrue.
    days = y.index.to_series().diff().dt.days.fillna(1).clip(lower=0, upper=10)
    daily = (y.shift(1).fillna(y.iloc[0]) / 100.0) * days / 360.0
    index = (1 + daily).cumprod()
    return index.resample("ME").last().pct_change()


def model_returns(monthly):
    """Monthly return series for each model portfolio, rebalanced monthly."""
    out = {}
    for name, weights in MODELS.items():
        r = sum(monthly[asset] * w for asset, w in weights.items())
        out[name] = r
    return pd.DataFrame(out)


def build():
    monthly = load_monthly_returns()
    models = model_returns(monthly)
    months = [d.strftime("%Y-%m") for d in monthly.index]
    payload = {
        "months": months,
        "start": months[0],
        "end": months[-1],
        # Per-asset monthly total returns. The engine holds positions in these
        # and lets them drift, so the page can show a portfolio moving away
        # from its target between rebalances.
        "assets": {a: [round(float(x), 8) for x in monthly[a]]
                   for a in monthly.columns},
        "models": MODELS,
        "labels": MODEL_LABELS,
        "equity": MODEL_EQUITY,
        "equity_assets": sorted(EQUITY_ASSETS),
    }
    return payload, monthly, models


def main():
    payload, monthly, models = build()
    path = os.path.join(HERE, "market.json")
    with open(path, "w") as f:
        json.dump(payload, f, separators=(",", ":"))

    n = len(payload["months"])
    size = os.path.getsize(path) / 1024
    print(f"market.json: {n} months, {payload['start']} to {payload['end']}, "
          f"{size:.0f} KB")
    print()
    print(f"{'model':<28} {'CAGR':>7} {'vol':>7} {'worst month':>12}")
    years = n / 12
    for name in MODELS:
        r = models[name]
        total = float((1 + r).prod())
        cagr = total ** (1 / years) - 1
        vol = float(r.std() * np.sqrt(12))
        print(f"{MODEL_LABELS[name]:<28} {cagr*100:6.1f}% {vol*100:6.1f}% "
              f"{r.min()*100:11.1f}%")


if __name__ == "__main__":
    main()
