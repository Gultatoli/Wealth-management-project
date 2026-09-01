"""Build cases.json (and index.html) for the Suitability Lens.

Usage:
    python3 build_cases.py            # use committed data
    python3 build_cases.py --fetch    # refresh data to the latest close first
"""
import argparse
import json
import os
import sys

ANALYSIS = os.path.join(os.path.dirname(__file__), "..", "analysis")
if ANALYSIS not in sys.path:
    sys.path.insert(0, ANALYSIS)

import analyse
import engine
import notes
from clients import CLIENTS

HERE = os.path.dirname(__file__)
GOAL_METRIC = {"margaret": "survival", "tom": "accumulation", "priya": "concentration"}
# The discretionary recommendation: which axis step the note argues toward.
TARGET_INDEX = {"margaret": 4, "tom": 2, "priya": 0}  # 0.60, 0.40, diversified


def build(fetch=False):
    if fetch:
        import fetch_data
        fetch_data.main()

    prices = analyse.load_prices()
    engine.simulate_paths(max(c.horizon_years for c in CLIENTS))
    corr = engine.correlation_regime(prices)
    conc = engine.concentration_signal(prices)

    clients_out = []
    for c in CLIENTS:
        market = engine.market_grid(prices, c.axis)
        goal = engine.goal_grid(engine._SIM_CORE, c)
        conditions = conc if c.key == "priya" else corr
        base = c.axis.base_index
        target = TARGET_INDEX[c.key]
        note = notes.review_note(c, market[base], goal[base],
                                 market[target], goal[target], conditions)
        clients_out.append({
            "key": c.key, "name": c.name, "age": c.age, "label": c.label,
            "story": c.story, "goal": c.goal, "horizon_years": c.horizon_years,
            "amounts": c.amounts, "drift": c.drift, "decision": c.decision,
            "axis": {"kind": c.axis.kind, "steps": c.axis.steps,
                     "base_index": c.axis.base_index,
                     "label_lo": c.axis.label_lo, "label_hi": c.axis.label_hi},
            "market": market, "goal_values": goal,
            "goal_metric": GOAL_METRIC[c.key],
            "conditions": conditions, "note": note,
        })

    return {"as_of": engine.as_of_date(prices), "clients": clients_out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true",
                    help="refresh data to the latest close before building")
    args = ap.parse_args()
    payload = build(fetch=args.fetch)
    with open(os.path.join(HERE, "cases.json"), "w") as f:
        json.dump(payload, f, indent=2)
    from render import render_page          # Task 7
    render_page(payload)
    print(f"Built cases.json and index.html (data as of {payload['as_of']})")


if __name__ == "__main__":
    main()
