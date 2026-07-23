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


RECENT_START = "2021-01-01"   # window where concentration risk actually shows


def market_risk(prices, weights):
    value = analyse.portfolio_value(prices, weights)
    underwater = analyse.longest_underwater_days(value)
    recent_dd = analyse.drawdown_in_window(value, RECENT_START, value.index[-1])
    return {
        "vol_pct": round(analyse.annual_vol(value) * 100, 1),
        "max_drawdown_pct": round(analyse.max_drawdown(value) * 100, 1),
        "recent_dd_pct": round(recent_dd * 100, 1),
        "worst_year_pct": round(analyse.worst_rolling_year(value) * 100, 1),
        "underwater_years": round((underwater or 0) / 365.25, 1),
    }


def market_grid(prices, axis):
    return [market_risk(prices, weights_for(axis.kind, s)) for s in axis.steps]


# ---- goal-risk lens ----
import monte_carlo as mc  # noqa: E402  (analysis dir already on sys.path)
import pandas as pd  # noqa: E402


def _returns_with_soxx():
    """Monthly returns for SPY, EFA, EEM, AGG, SOXX on common months.
    Mirrors mc.monthly_returns but keeps SOXX for the concentration client."""
    assets = ["SPY", "EFA", "EEM", "AGG", "SOXX"]
    cols = {}
    for t in assets:
        s = pd.read_csv(os.path.join(ANALYSIS, "..", "data", f"{t}.csv"),
                        parse_dates=["date"], index_col="date")["adj_close"]
        cols[t] = s.resample("ME").last().pct_change()
    df = pd.concat(cols, axis=1).dropna()
    df.columns = assets
    return df[assets]


# Module-level caches so the expensive bootstrap runs once.
_RET_CORE = None
_SIM_CORE = None
_RET_SOXX = None
_SIM_SOXX = None
_PRICES = None


def _prices():
    """Lazily load and cache the historical prices (same CSVs the paper uses)."""
    global _PRICES
    if _PRICES is None:
        _PRICES = analyse.load_prices()
    return _PRICES


def simulate_paths(max_horizon_years):
    """Build both the core (mc.ASSETS) and SOXX-inclusive path arrays once."""
    global _RET_CORE, _SIM_CORE, _RET_SOXX, _SIM_SOXX
    months = max_horizon_years * 12
    rng = np.random.default_rng(mc.SEED)
    _RET_CORE = mc.monthly_returns()
    _SIM_CORE = mc.bootstrap_paths(_RET_CORE, months, rng)
    rng2 = np.random.default_rng(mc.SEED)  # same seed, independent draw for 5-asset set
    _RET_SOXX = _returns_with_soxx()
    _SIM_SOXX = mc.bootstrap_paths(_RET_SOXX, months, rng2)
    return _RET_CORE, _SIM_CORE


def _port_returns(sim, returns_cols, weights):
    """Monthly portfolio returns per path: (N_PATHS, months)."""
    w = np.array([weights.get(a, 0.0) for a in returns_cols])
    return sim @ w


def _max_drawdown_paths(cum):
    """Worst peak-to-trough per path from a cumulative-wealth array (N, months)."""
    peak = np.maximum.accumulate(cum, axis=1)
    dd = cum / peak - 1.0
    return dd.min(axis=1)


def goal_grid(sim_core, client):
    months = client.horizon_years * 12
    out = []
    for step in client.axis.steps:
        weights = weights_for(client.axis.kind, step)
        if client.key == "margaret":
            pr = _port_returns(_SIM_CORE[:, :months, :], list(_RET_CORE.columns), weights)
            p = mc.survival_prob(pr, client.amounts["pot"],
                                 client.amounts["withdraw_rate"],
                                 client.amounts["inflation"], months)
            out.append(round(p * 100, 0))
        elif client.key == "tom":
            pr = _port_returns(_SIM_CORE[:, :months, :], list(_RET_CORE.columns), weights)
            pot = np.full(pr.shape[0], float(client.amounts["initial"]))
            for m in range(months):
                pot = pot * (1 + pr[:, m]) + client.amounts["monthly"]
            p = (pot >= client.amounts["target"]).mean()
            out.append(round(p * 100, 0))
        elif client.key == "priya":
            # Her second lens is the hidden concentration risk: the worst fall
            # since 2021, where a semis tilt bites and the 2008-dominated
            # full-history max drawdown does not. A historical figure, not a
            # simulation, because concentration is about what she actually holds.
            value = analyse.portfolio_value(_prices(), weights)
            recent_dd = analyse.drawdown_in_window(value, RECENT_START,
                                                   value.index[-1])
            out.append(round(recent_dd * 100, 1))   # negative %
        else:
            raise ValueError(client.key)
    return out
