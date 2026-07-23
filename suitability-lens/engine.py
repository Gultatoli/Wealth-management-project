"""Computation layer for the Suitability Lens.

Imports the existing analysis modules and turns them into per-client grids and
signals. Nothing here reimplements portfolio maths; it orchestrates the paper's
own functions so the tool and the paper can never disagree.
"""
import os
import sys

ANALYSIS = os.path.join(os.path.dirname(__file__), "..", "analysis")
if ANALYSIS not in sys.path:
    sys.path.insert(0, ANALYSIS)

import numpy as np
import analyse


def weights_for(axis_kind, step):
    if axis_kind == "equity":
        return analyse.graded(step)
    if axis_kind == "concentration":
        eq = 1 - step
        return {"SPY": round(0.60 * eq, 4), "EFA": round(0.30 * eq, 4),
                "EEM": round(0.10 * eq, 4), "SOXX": round(step, 4)}
    raise ValueError(f"unknown axis kind: {axis_kind}")


def market_risk(prices, weights):
    value = analyse.portfolio_value(prices, weights)
    underwater = analyse.longest_underwater_days(value)
    return {
        "vol_pct": round(analyse.annual_vol(value) * 100, 1),
        "max_drawdown_pct": round(analyse.max_drawdown(value) * 100, 1),
        "worst_year_pct": round(analyse.worst_rolling_year(value) * 100, 1),
        "underwater_years": round((underwater or 0) / 365.25, 1),
    }


def market_grid(prices, axis):
    return [market_risk(prices, weights_for(axis.kind, s)) for s in axis.steps]
