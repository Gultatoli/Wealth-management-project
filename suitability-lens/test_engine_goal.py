import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import engine
from clients import CLIENTS

RET, SIM = engine.simulate_paths(30)


def test_margaret_survival_matches_paper():
    m = next(c for c in CLIENTS if c.key == "margaret")
    grid = engine.goal_grid(SIM, m)  # percentages aligned to axis steps
    cautious = grid[m.axis.base_index]
    growth = grid[-1]
    # Paper: cautious ~74%, balanced/growth ~92% over 30y at 4%
    assert 60 <= cautious <= 85
    assert growth > cautious
    assert growth >= 85


def test_tom_accumulation_probability_in_range():
    t = next(c for c in CLIENTS if c.key == "tom")
    grid = engine.goal_grid(SIM, t)
    assert all(0 <= p <= 100 for p in grid)
    assert grid[-1] >= grid[0] - 5


def test_priya_recent_drawdown_deepens_with_concentration():
    p = next(c for c in CLIENTS if c.key == "priya")
    grid = engine.goal_grid(SIM, p)  # recent (since 2021) drawdown %, negative
    # index 0 = diversified, index 6 = most concentrated
    assert all(v <= 0 for v in grid)          # drawdowns are negative
    assert grid[0] > grid[6]                  # diversified fell less (less negative)
    assert grid[6] < -33                      # concentrated fell meaningfully deeper
