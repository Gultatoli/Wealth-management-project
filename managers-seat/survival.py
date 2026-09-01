"""
The endgame: does her money last to 95?

History in this simulator stops in July 2026, when Ruth is 81. She wants the
income to run to 95, which leaves fifteen years that have not happened yet. The
simulator answers those fifteen years with the paper's own Monte Carlo rather
than with a new one, so the number at the end of a playthrough is the same kind
of number the paper reports, produced by the same code.

Concretely, this imports `analysis/monte_carlo.py` and uses its block bootstrap
and its survival function. Nothing about the method is reimplemented here. What
this file adds is only a grid: because the player's decisions determine both the
pot and the allocation she ends up with, the answer has to be available for any
combination of the two, and a page that has to work offline on a phone cannot
run ten thousand paths in the browser.

So the grid is computed once, here, and the page looks the answer up and
interpolates between rates.

Run:
    python3 survival.py      # writes survival.json
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))

import monte_carlo as MC  # noqa: E402  (path set above)

# Fifteen years from the end of the data to her ninety-fifth birthday.
HORIZON_YEARS = 15

# The equity weights the grid is computed for. Any allocation the player can
# reach maps onto one of these, and the page interpolates between them.
EQUITY_LEVELS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Withdrawal expressed as a fraction of the pot she has in July 2026. A player
# who ends with a large pot lands at the low end and a player who has burned
# through it lands at the high end, which is exactly the discrimination the
# score needs.
RATES = [round(x, 4) for x in np.arange(0.0, 0.2001, 0.005)]


def build():
    rng = np.random.default_rng(MC.SEED)
    returns = MC.monthly_returns()
    months = HORIZON_YEARS * 12
    sim = MC.bootstrap_paths(returns, months, rng)

    grid = {}
    for eq in EQUITY_LEVELS:
        weights = MC.equity_split(eq)
        w = np.array([weights.get(a, 0.0) for a in MC.ASSETS])
        port = sim @ w
        row = []
        for rate in RATES:
            if rate <= 0:
                row.append(1.0)
                continue
            p = MC.survival_prob(port, 1.0, rate, MC.INFLATION, months)
            row.append(round(float(p), 4))
        grid[f"{eq:.1f}"] = row

    return {
        "horizon_years": HORIZON_YEARS,
        "inflation": MC.INFLATION,
        "paths": MC.N_PATHS,
        "block_months": MC.BLOCK_MONTHS,
        "seed": MC.SEED,
        "equity_levels": EQUITY_LEVELS,
        "rates": RATES,
        "grid": grid,
        "source": ("analysis/monte_carlo.py block bootstrap, "
                   f"{MC.N_PATHS:,} paths, {MC.BLOCK_MONTHS}-month blocks"),
    }


def main():
    payload = build()
    path = os.path.join(HERE, "survival.json")
    with open(path, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"survival.json written: {len(EQUITY_LEVELS)} allocations x "
          f"{len(RATES)} withdrawal rates, {HORIZON_YEARS}-year horizon")
    print()
    print("Sanity check, probability the income lasts 15 years:")
    print(f"{'draw rate':>10}" + "".join(f"{e*100:8.0f}%" for e in EQUITY_LEVELS))
    for rate in [0.02, 0.04, 0.06, 0.08, 0.10]:
        i = payload["rates"].index(rate)
        cells = "".join(f"{payload['grid'][f'{e:.1f}'][i]*100:8.0f}%"
                        for e in EQUITY_LEVELS)
        print(f"{rate*100:9.1f}%" + cells)


if __name__ == "__main__":
    main()
