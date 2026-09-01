import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import analyse
import engine

PRICES = analyse.load_prices()


def test_weights_sum_to_one():
    for step in (0.2, 0.6, 1.0):
        w = engine.weights_for("equity", step)
        assert abs(sum(w.values()) - 1.0) < 1e-9
    for step in (0.0, 0.30):
        w = engine.weights_for("concentration", step)
        assert abs(sum(w.values()) - 1.0) < 1e-9


def test_market_risk_rises_with_equity():
    cautious = engine.market_risk(PRICES, engine.weights_for("equity", 0.40))
    growth = engine.market_risk(PRICES, engine.weights_for("equity", 0.80))
    assert growth["vol_pct"] > cautious["vol_pct"]
    assert growth["max_drawdown_pct"] < cautious["max_drawdown_pct"]  # deeper


def test_market_grid_length_matches_axis():
    from clients import CLIENTS
    m = next(c for c in CLIENTS if c.key == "margaret")
    grid = engine.market_grid(PRICES, m.axis)
    assert len(grid) == len(m.axis.steps)
    assert all("vol_pct" in row for row in grid)
