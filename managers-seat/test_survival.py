"""
The endgame number has to be the paper's number.

The whole credibility of the simulator rests on the last figure it shows: the
chance her income lasts to 95. If that came from a different simulation than the
one in the paper, the two would eventually disagree and there would be no honest
answer to "which of these is right?".

These tests check that the grid really is the paper's block bootstrap, that the
paper's own headline decumulation figures still reproduce, and that the grid
behaves sensibly where a person would expect it to.
"""

import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))

import monte_carlo as MC  # noqa: E402
import survival  # noqa: E402


@pytest.fixture(scope="module")
def grid():
    return survival.build()


def test_the_grid_is_reproducible(grid):
    """Same seed, same numbers. If this fails the figure on screen is not one
    anybody could check."""
    again = survival.build()
    assert grid["grid"] == again["grid"]


def test_a_cell_matches_the_paper_s_own_code(grid):
    """Recompute one cell straight from monte_carlo.py and compare."""
    rng = np.random.default_rng(MC.SEED)
    returns = MC.monthly_returns()
    months = survival.HORIZON_YEARS * 12
    sim = MC.bootstrap_paths(returns, months, rng)

    weights = MC.equity_split(0.6)
    w = np.array([weights.get(a, 0.0) for a in MC.ASSETS])
    port = sim @ w
    rate = 0.06
    expected = MC.survival_prob(port, 1.0, rate, MC.INFLATION, months)

    i = grid["rates"].index(rate)
    assert abs(grid["grid"]["0.6"][i] - expected) < 1e-9


def test_the_paper_s_headline_figures_still_hold():
    """The README quotes 74% for Defensive and 92% for Balanced over thirty
    years at a 4% draw. The simulator repeats those numbers in its narrative,
    so they have to stay true."""
    rng = np.random.default_rng(MC.SEED)
    returns = MC.monthly_returns()
    months = 30 * 12
    sim = MC.bootstrap_paths(returns, max(MC.SENS_HORIZONS) * 12, rng)

    def prob(equity):
        weights = MC.equity_split(equity)
        w = np.array([weights.get(a, 0.0) for a in MC.ASSETS])
        return MC.survival_prob(sim @ w, MC.POT, 0.04, MC.INFLATION, months)

    assert round(prob(0.2) * 100) in (74, 75)
    assert round(prob(0.6) * 100) == 92


def test_survival_falls_as_the_draw_rises(grid):
    for eq in grid["equity_levels"]:
        row = grid["grid"][f"{eq:.1f}"]
        assert all(row[i] >= row[i + 1] - 1e-9 for i in range(len(row) - 1)), \
            f"survival is not monotonic in the withdrawal rate at {eq}"


def test_a_zero_draw_always_survives(grid):
    for eq in grid["equity_levels"]:
        assert grid["grid"][f"{eq:.1f}"][0] == 1.0


def test_the_cautious_trap_shows_up_at_high_draws(grid):
    """The paper's objective-drift finding: at a demanding withdrawal rate the
    least risky allocation is the least likely to last. If this ever stopped
    being true in the data, the simulator's whole argument would need redoing."""
    i = grid["rates"].index(0.08)
    no_equity = grid["grid"]["0.0"][i]
    balanced = grid["grid"]["0.6"][i]
    assert balanced > no_equity


def test_the_shipped_grid_matches_a_fresh_build(grid):
    """Guard against a stale survival.json sitting in the repo."""
    path = os.path.join(HERE, "survival.json")
    if not os.path.exists(path):
        pytest.skip("survival.json has not been built")
    with open(path) as f:
        shipped = json.load(f)
    assert shipped["grid"] == grid["grid"], \
        "survival.json is stale, re-run build.py"
