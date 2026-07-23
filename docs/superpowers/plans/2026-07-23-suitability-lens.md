# The Suitability Lens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained, mobile-first web tool ("The Suitability Lens") that presents three client cases showing market risk versus goal risk, the drift that bites each client, present-day condition signals, and a client-facing review note, all driven by the existing analysis engine and data.

**Architecture:** A Python builder (`suitability-lens/build_cases.py`) imports the existing `analysis/analyse.py` and `analysis/monte_carlo.py` modules, computes a per-client allocation grid (market-risk stats from 23 years of history, goal-risk from the block-bootstrap Monte Carlo) plus current-conditions signals, and emits a single `cases.json`. A static HTML template embeds that JSON and renders everything client-side with hand-rolled inline SVG. No server, no external calls.

**Tech Stack:** Python 3 (pandas, numpy), reused analysis modules, plain HTML/CSS/JS with inline SVG, Chromium headless for verification, pytest for tests.

## Global Constraints

- Reuse the existing analysis modules; do not reimplement portfolio construction, risk metrics, or the Monte Carlo. Import them.
- Monte Carlo determinism: seed the RNG with `SEED = 42` (matching `analysis/monte_carlo.py`) so `cases.json` is reproducible.
- Data assets are SPY, EFA, EEM, AGG (core) plus RSP, SOXX (concentration). Do not add new tickers.
- The page must be fully self-contained: no external scripts, stylesheets, fonts, or images. Charts are inline SVG. No `http://` or `https://` references in `index.html` except inside visible prose.
- Theme-aware (light and dark via `prefers-color-scheme`) and mobile-first (single column, no horizontal scroll).
- Honesty guardrails on the page: every figure labelled illustrative, USD, and as-of a stated date; "Nothing here is investment advice" present; risk bands labelled illustrative; goal-risk figures labelled as sensitivity-dependent simulation output.
- All client-facing prose (review notes, condition readouts) obeys the-humanizer rules: no em dashes, no buzzwords, plain English, specific numbers, varied sentence length.
- Prose style: no em dashes anywhere in committed prose.
- Tests use pytest. Install once with `pip install pytest` if the import fails.

---

### Task 1: Scaffold and client definitions

**Files:**
- Create: `suitability-lens/clients.py`
- Test: `suitability-lens/test_clients.py`

**Interfaces:**
- Produces: `CLIENTS: list[Client]` where `Client` is a dataclass with fields
  `key: str`, `name: str`, `age: int`, `label: str`, `story: str`, `goal: str`,
  `horizon_years: int`, `amounts: dict`, `drift: str`, `decision: str`,
  `axis: AllocationAxis`. `AllocationAxis` is a dataclass with
  `kind: str` (one of `"equity"`, `"concentration"`), `steps: list[float]`,
  `base_index: int`, `label_lo: str`, `label_hi: str`.
- For `kind == "equity"`, each step is an equity fraction in [0,1] passed to
  `analyse.graded`. For `kind == "concentration"`, each step is a semis fraction
  in [0,1] blended into the equity sleeve (0 = fully diversified, up to 0.30
  semis-tilt), matching `analyse.PORTFOLIOS["Semis-tilt (70/30)"]` at 0.30.

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_clients.py
import clients

def test_three_clients_with_required_fields():
    assert len(clients.CLIENTS) == 3
    keys = {c.key for c in clients.CLIENTS}
    assert keys == {"margaret", "tom", "priya"}
    for c in clients.CLIENTS:
        assert c.name and c.story and c.goal and c.decision
        assert c.horizon_years > 0
        assert c.axis.kind in ("equity", "concentration")
        assert len(c.axis.steps) >= 7
        # steps strictly increasing
        assert all(b > a for a, b in zip(c.axis.steps, c.axis.steps[1:]))
        assert 0 <= c.axis.base_index < len(c.axis.steps)

def test_margaret_is_decumulation_retiree():
    m = next(c for c in clients.CLIENTS if c.key == "margaret")
    assert m.age == 66
    assert m.axis.kind == "equity"
    assert m.amounts["pot"] == 600_000
    assert m.amounts["withdraw_rate"] == 0.04
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_clients.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'clients'`

- [ ] **Step 3: Write minimal implementation**

```python
# suitability-lens/clients.py
"""The three client cases. Pure data, no computation.

Each client showcases one of the paper's three drifts and ends in its own
discretionary decision. The `axis` describes the interactive lever: a set of
allocation steps the slider snaps to, with one marked as the client's current
(base) position.
"""
from dataclasses import dataclass, field


@dataclass
class AllocationAxis:
    kind: str                 # "equity" or "concentration"
    steps: list               # increasing floats
    base_index: int           # which step is the client's current position
    label_lo: str
    label_hi: str


@dataclass
class Client:
    key: str
    name: str
    age: int
    label: str                # their risk label
    story: str
    goal: str
    horizon_years: int
    amounts: dict
    drift: str                # short name of the drift showcased
    decision: str             # the discretionary call
    axis: AllocationAxis


CLIENTS = [
    Client(
        key="margaret",
        name="Margaret",
        age=66,
        label="Cautious",
        story="Just retired. She was profiled cautious, which feels right for "
              "someone who cannot go back to work.",
        goal="Draw about £24,000 a year, rising with inflation, for a 30-year "
             "retirement without running out of money.",
        horizon_years=30,
        amounts={"pot": 600_000, "income": 24_000, "withdraw_rate": 0.04,
                 "inflation": 0.025},
        drift="objective drift",
        decision="Take more market risk, not less, to cut the risk of the pot "
                 "running dry.",
        axis=AllocationAxis(
            kind="equity",
            steps=[0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80],
            base_index=2,     # 0.40 == cautious
            label_lo="More cautious",
            label_hi="More growth",
        ),
    ),
    Client(
        key="tom",
        name="Tom",
        age=28,
        label="Balanced",
        story="Saving hard for a first house. Profiled balanced, which sounds "
              "safe for a six-year plan.",
        goal="Turn £40,000 plus £500 a month into a house deposit in about six "
             "years.",
        horizon_years=6,
        amounts={"initial": 40_000, "monthly": 500, "target": 75_000},
        drift="diversification drift",
        decision="Do not lean on the bond cushion the way the label assumes, and "
                 "de-risk toward the goal as the date nears.",
        axis=AllocationAxis(
            kind="equity",
            steps=[0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80],
            base_index=4,     # 0.60 == balanced
            label_lo="More cautious",
            label_hi="More growth",
        ),
    ),
    Client(
        key="priya",
        name="Priya",
        age=45,
        label="Adventurous",
        story="Long horizon, high tolerance, profiled adventurous. Her equity "
              "sleeve has quietly drifted into a semiconductor-heavy bet.",
        goal="Grow wealth over the long run without carrying risk she did not "
             "choose and does not know about.",
        horizon_years=10,
        amounts={"initial": 250_000},
        drift="concentration drift",
        decision="Trim the concentration she did not know she was carrying back "
                 "toward a diversified adventurous portfolio.",
        axis=AllocationAxis(
            kind="concentration",
            steps=[0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
            base_index=6,     # 0.30 == full semis-tilt (her current drift)
            label_lo="Diversified",
            label_hi="Semis-tilt",
        ),
    ),
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_clients.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/clients.py suitability-lens/test_clients.py
git commit -m "Add Suitability Lens client definitions"
```

---

### Task 2: Weight helpers and the market-risk lens

**Files:**
- Create: `suitability-lens/engine.py`
- Test: `suitability-lens/test_engine_market.py`

**Interfaces:**
- Consumes: `analyse.load_prices`, `analyse.graded`, `analyse.portfolio_value`,
  `analyse.annual_vol`, `analyse.max_drawdown`, `analyse.worst_rolling_year`,
  `analyse.longest_underwater_days`; `clients.AllocationAxis`.
- Produces:
  - `weights_for(axis_kind: str, step: float) -> dict` — ticker weights for one
    step. `"equity"` returns `analyse.graded(step)`. `"concentration"` returns a
    100%-equity sleeve with `step` in SOXX: `{"SPY":0.60*(1-step), "EFA":0.30*(1-step), "EEM":0.10*(1-step), "SOXX": round(step,4)}`.
  - `market_risk(prices, weights) -> dict` with keys `vol_pct` (float, annualised
    %), `max_drawdown_pct` (float, negative %), `worst_year_pct` (float, %),
    `underwater_years` (float).
  - `market_grid(prices, axis) -> list[dict]` — one `market_risk` dict per step.

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_engine_market.py
import os, sys
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_engine_market.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine'`

- [ ] **Step 3: Write minimal implementation**

```python
# suitability-lens/engine.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_engine_market.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/engine.py suitability-lens/test_engine_market.py
git commit -m "Add market-risk lens to Suitability Lens engine"
```

---

### Task 3: The goal-risk lens

**Files:**
- Modify: `suitability-lens/engine.py`
- Test: `suitability-lens/test_engine_goal.py`

**Interfaces:**
- Consumes: `analysis/monte_carlo.py` as `mc` (`mc.monthly_returns`,
  `mc.bootstrap_paths`, `mc.survival_prob`, `mc.ASSETS`, `mc.N_PATHS`,
  `mc.BLOCK_MONTHS`, `mc.SEED`).
- Produces:
  - `simulate_paths(max_horizon_years) -> tuple(returns_df, sim_array)` — builds
    the block-bootstrap once with the fixed seed. `sim_array` shape is
    `(N_PATHS, max_horizon_years*12, len(ASSETS))`.
  - `goal_grid(sim_array, client) -> list[float]` — one goal-risk probability per
    axis step, as a percentage 0–100. Semantics per client:
    - margaret: `survival_prob` of the pot over `horizon_years` at her withdraw
      rate and inflation. Concentration/equity axis uses `weights_for`. SOXX is
      not in `mc.ASSETS`, so for margaret (equity axis) this is fine.
    - tom: probability that £initial plus £monthly contributions reaches
      `target` by `horizon_years` (accumulation success), computed from the same
      path returns.
    - priya: probability of avoiding a peak-to-trough drawdown worse than -30%
      over `horizon_years` (a "can she hold it" risk). Priya's axis is
      concentration and includes SOXX, which is NOT in `mc.ASSETS`; see Step 3
      for how her paths are built from a SOXX-inclusive return set.

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_engine_goal.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import engine
from clients import CLIENTS

RET, SIM = engine.simulate_paths(30)

def test_margaret_survival_matches_paper():
    m = next(c for c in CLIENTS if c.key == "margaret")
    grid = engine.goal_grid(SIM, m)  # percentages aligned to axis steps
    # cautious (0.40) is axis index 2; growth (0.80) is index 6
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
    # more growth should not reduce the chance of hitting a nominal target
    assert grid[-1] >= grid[0] - 5

def test_priya_hold_probability_decreases_with_concentration():
    p = next(c for c in CLIENTS if c.key == "priya")
    grid = engine.goal_grid(SIM, p)
    # index 0 = diversified, index 6 = full semis-tilt
    assert grid[0] > grid[6]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_engine_goal.py -v`
Expected: FAIL with `AttributeError: module 'engine' has no attribute 'simulate_paths'`

- [ ] **Step 3: Write minimal implementation (append to engine.py)**

```python
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
            pr = _port_returns(_SIM_SOXX[:, :months, :], list(_RET_SOXX.columns), weights)
            cum = np.cumprod(1 + pr, axis=1)
            worst = _max_drawdown_paths(cum)
            p = (worst > -0.30).mean()   # avoided a >30% drawdown
            out.append(round(p * 100, 0))
        else:
            raise ValueError(client.key)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_engine_goal.py -v`
Expected: PASS (3 tests). If margaret's survival is outside 60–85, re-check that
`_SIM_CORE` columns line up with `mc.ASSETS` order.

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/engine.py suitability-lens/test_engine_goal.py
git commit -m "Add goal-risk lens (survival, accumulation, drawdown) to engine"
```

---

### Task 4: Current-conditions signals

**Files:**
- Modify: `suitability-lens/engine.py`
- Test: `suitability-lens/test_engine_conditions.py`

**Interfaces:**
- Consumes: `analyse.load_prices`, `analyse.portfolio_value`, `analyse.graded`,
  `analyse.TRADING_DAYS`.
- Produces:
  - `as_of_date(prices) -> str` — ISO date of the latest common close.
  - `correlation_regime(prices) -> dict` with `value` (float, latest rolling
    252-day stock-bond correlation), `status` (`"elevated"` if value > 0 else
    `"normal"`), `as_of` (str).
  - `concentration_signal(prices) -> dict` with `spread_pct` (float, trailing
    1-year SPY return minus RSP return, in %), `status` (`"elevated"` if
    spread_pct > 5 else `"normal"`), `as_of` (str).

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_engine_conditions.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import analyse, engine

PRICES = analyse.load_prices()

def test_as_of_is_iso_date():
    s = engine.as_of_date(PRICES)
    assert len(s) == 10 and s[4] == "-" and s[7] == "-"

def test_correlation_regime_shape():
    r = engine.correlation_regime(PRICES)
    assert -1.0 <= r["value"] <= 1.0
    assert r["status"] in ("elevated", "normal")

def test_concentration_signal_shape():
    c = engine.concentration_signal(PRICES)
    assert isinstance(c["spread_pct"], float)
    assert c["status"] in ("elevated", "normal")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_engine_conditions.py -v`
Expected: FAIL with `AttributeError: module 'engine' has no attribute 'as_of_date'`

- [ ] **Step 3: Write minimal implementation (append to engine.py)**

```python
# ---- current-conditions signals ----
def as_of_date(prices):
    return str(prices.index[-1].date())


def correlation_regime(prices):
    eq = analyse.portfolio_value(prices, analyse.graded(1.00)).pct_change()
    bond = prices["AGG"].pct_change()
    roll = eq.rolling(analyse.TRADING_DAYS).corr(bond).dropna()
    value = round(float(roll.iloc[-1]), 2)
    return {"value": value,
            "status": "elevated" if value > 0 else "normal",
            "as_of": as_of_date(prices)}


def concentration_signal(prices):
    window = analyse.TRADING_DAYS
    spy = prices["SPY"]
    rsp = prices["RSP"]
    spy_ret = spy.iloc[-1] / spy.iloc[-window] - 1.0
    rsp_ret = rsp.iloc[-1] / rsp.iloc[-window] - 1.0
    spread = round(float((spy_ret - rsp_ret) * 100), 1)
    return {"spread_pct": spread,
            "status": "elevated" if spread > 5 else "normal",
            "as_of": as_of_date(prices)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_engine_conditions.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/engine.py suitability-lens/test_engine_conditions.py
git commit -m "Add current-conditions signals (correlation, concentration)"
```

---

### Task 5: Review-note generation

**Files:**
- Create: `suitability-lens/notes.py`
- Test: `suitability-lens/test_notes.py`

**Interfaces:**
- Consumes: `clients.Client`, the computed `market_grid`/`goal_grid` values and
  the conditions dicts (passed in, not recomputed).
- Produces: `review_note(client, base_market, base_goal, target_market,
  target_goal, conditions) -> str` — a short plain-English client letter. Takes
  the client's current (base) market/goal figures and the recommended (target)
  figures, plus the relevant condition dict, and returns 4–6 sentences.

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_notes.py
import notes
from clients import CLIENTS

def test_note_is_plain_and_specific():
    m = next(c for c in CLIENTS if c.key == "margaret")
    text = notes.review_note(
        m,
        base_market={"vol_pct": 7.0, "max_drawdown_pct": -20.0},
        base_goal=74,
        target_market={"vol_pct": 11.0, "max_drawdown_pct": -34.0},
        target_goal=90,
        conditions={"value": 0.2, "status": "elevated", "as_of": "2026-07-23"},
    )
    assert "—" not in text            # no em dashes
    assert "74" in text and "90" in text
    assert 200 < len(text) < 1200
    for banned in ("leverage", "robust", "seamless", "unlock", "delve"):
        assert banned not in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_notes.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'notes'`

- [ ] **Step 3: Write minimal implementation**

```python
# suitability-lens/notes.py
"""Client-facing review notes. Plain English, specific numbers, no jargon.

These are generated from the computed figures so they always match the tool.
They obey the-humanizer rules: no em dashes, no buzzwords, varied sentences.
"""


def review_note(client, base_market, base_goal, target_market, target_goal,
                conditions):
    if client.key == "margaret":
        return (
            f"Dear Margaret,\n\n"
            f"Your portfolio is profiled cautious, and on the measure most people "
            f"mean by risk it is: it moves around less and falls less far than a "
            f"bolder mix. But the risk that matters most to you is a different one, "
            f"whether the money lasts. On our simulations the cautious mix funds "
            f"your full 30 years about {int(base_goal)}% of the time. A more "
            f"growth-tilted mix raises that to roughly {int(target_goal)}%.\n\n"
            f"The trade is real. You would see bigger swings along the way, with a "
            f"worst historical fall nearer {abs(target_market['max_drawdown_pct']):.0f}% "
            f"than {abs(base_market['max_drawdown_pct']):.0f}%. In exchange you cut "
            f"the chance of running short later in retirement. For a 30-year plan "
            f"drawing 4%, that is a trade I would recommend making."
        )
    if client.key == "tom":
        return (
            f"Dear Tom,\n\n"
            f"Balanced sounds safe for a six-year plan, and the label is not wrong "
            f"about the long run. The catch is the bond half. It is meant to steady "
            f"the portfolio when shares fall, but in 2022 bonds and shares fell "
            f"together, and right now they are still moving in step "
            f"(correlation {conditions['value']:+.2f}). Over your short horizon that "
            f"matters more than it would for someone investing for decades.\n\n"
            f"My advice is not to rely on the bond cushion doing what the label "
            f"implies, and to step down the risk as your purchase date nears so a "
            f"bad final year cannot undo the plan."
        )
    if client.key == "priya":
        return (
            f"Dear Priya,\n\n"
            f"You are happy with a bold portfolio, and that is fine. The issue is "
            f"not how much risk you are taking but what kind. Your equity has drifted "
            f"into a heavy semiconductor position. Two adventurous investors can look "
            f"identical on a risk label and hold very different real risk: this "
            f"concentrated version has weathered falls near "
            f"{abs(base_market['max_drawdown_pct']):.0f}%, far deeper than a "
            f"diversified adventurous mix.\n\n"
            f"I am not suggesting you play it safe. I am suggesting you take the risk "
            f"you actually chose, spread across the market, rather than a single "
            f"theme you drifted into. My recommendation is to trim the concentration "
            f"back toward a diversified holding."
        )
    raise ValueError(client.key)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_notes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/notes.py suitability-lens/test_notes.py
git commit -m "Add client-facing review notes"
```

---

### Task 6: The builder — assemble cases.json

**Files:**
- Create: `suitability-lens/build_cases.py`
- Test: `suitability-lens/test_build.py`

**Interfaces:**
- Consumes: everything above.
- Produces:
  - `build(fetch: bool = False) -> dict` — the full cases payload. When
    `fetch=True`, first runs `fetch_data.main()` to refresh CSVs; otherwise uses
    committed data. Returns a dict:
    ```
    {
      "as_of": "YYYY-MM-DD",
      "clients": [
        {"key","name","age","label","story","goal","horizon_years","amounts",
         "drift","decision","axis": {"kind","steps","base_index","label_lo","label_hi"},
         "market": [ {vol_pct,...}, ... ],   # per step
         "goal": [ 74, 80, ... ],            # per step, %
         "goal_metric": "survival|accumulation|hold",
         "conditions": {...},                # the relevant signal
         "note": "Dear ..." }
      ]
    }
    ```
  - `main()` — build with `fetch` controlled by `--fetch` CLI flag, write
    `cases.json`, then call `render_page` (Task 7).

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_build.py
import build_cases

def test_build_payload_shape():
    payload = build_cases.build(fetch=False)
    assert payload["as_of"]
    assert len(payload["clients"]) == 3
    for c in payload["clients"]:
        n = len(c["axis"]["steps"])
        assert len(c["market"]) == n
        assert len(c["goal"]) == n
        assert c["note"].startswith("Dear")
        assert "conditions" in c
    m = next(c for c in payload["clients"] if c["key"] == "margaret")
    assert m["goal_metric"] == "survival"
    assert 60 <= m["goal"][m["axis"]["base_index"]] <= 85
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_build.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'build_cases'`

- [ ] **Step 3: Write minimal implementation**

```python
# suitability-lens/build_cases.py
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
GOAL_METRIC = {"margaret": "survival", "tom": "accumulation", "priya": "hold"}


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
        # recommended target index: for margaret/tom move toward the sensible
        # end; for priya move to diversified (index 0).
        target = {"margaret": len(c.axis.steps) - 3, "tom": 2, "priya": 0}[c.key]
        note = notes.review_note(c, market[base], goal[base],
                                 market[target], goal[target], conditions)
        clients_out.append({
            "key": c.key, "name": c.name, "age": c.age, "label": c.label,
            "story": c.story, "goal": c.goal, "horizon_years": c.horizon_years,
            "amounts": c.amounts, "drift": c.drift, "decision": c.decision,
            "axis": {"kind": c.axis.kind, "steps": c.axis.steps,
                     "base_index": c.axis.base_index,
                     "label_lo": c.axis.label_lo, "label_hi": c.axis.label_hi},
            "market": market, "goal": goal,
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_build.py -v`
Expected: PASS. Note: this test calls `build()` which imports `render` only in
`main()`, so it passes before Task 7 exists.

- [ ] **Step 5: Commit**

```bash
git add suitability-lens/build_cases.py suitability-lens/test_build.py
git commit -m "Add builder that assembles cases.json from the engine"
```

---

### Task 7: The page — template and render

**Files:**
- Create: `suitability-lens/template.html`
- Create: `suitability-lens/render.py`
- Test: `suitability-lens/test_render.py`

**Interfaces:**
- Consumes: the `build()` payload; `template.html`.
- Produces: `render_page(payload) -> str` (writes `index.html`, returns the HTML).
  Injects `json.dumps(payload)` at the `/*__CASES_JSON__*/` marker and the as-of
  date at `__AS_OF__`.

- [ ] **Step 1: Write the failing test**

```python
# suitability-lens/test_render.py
import os, re, json
import build_cases, render

def test_render_is_self_contained():
    payload = build_cases.build(fetch=False)
    html = render.render_page(payload)
    # embedded JSON parses
    m = re.search(r"const CASES = (\{.*?\});", html, re.S)
    assert m and json.loads(m.group(1))["clients"]
    # no external resource loads (allow visible prose to mention urls, but no
    # src=/href= to external hosts and no CDN script/link tags)
    assert "src=\"http" not in html and "href=\"http" not in html
    assert "cdn" not in html.lower()
    for name in ("Margaret", "Tom", "Priya"):
        assert name in html
    # honesty guardrails present
    assert "not investment advice" in html.lower()
    assert payload["as_of"] in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd suitability-lens && python3 -m pytest test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'render'`

- [ ] **Step 3: Write the template and render module**

Create `suitability-lens/template.html` with this structure (complete, self-contained; fill the JS bodies exactly as shown):

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Suitability Lens</title>
<style>
:root { --bg:#ffffff; --fg:#1a1a1a; --muted:#666; --line:#e2e2e2;
        --market:#c86b2b; --goal:#1a4d80; --warn:#b3402f; --card:#f7f7f5; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#141414; --fg:#ececec; --muted:#a0a0a0; --line:#2c2c2c;
          --market:#e0894f; --goal:#5aa0d6; --warn:#e0705c; --card:#1e1e1e; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.55 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:760px; margin:0 auto; padding:20px 16px 64px; }
h1 { font-size:1.5rem; margin:0 0 4px; }
.sub { color:var(--muted); margin:0 0 20px; }
.tabs { display:flex; gap:8px; margin:0 0 20px; flex-wrap:wrap; }
.tab { flex:1 1 auto; padding:10px 8px; border:1px solid var(--line);
  border-radius:10px; background:var(--card); color:var(--fg); cursor:pointer;
  font-size:0.95rem; }
.tab.active { border-color:var(--goal); color:var(--goal); font-weight:600; }
.lenses { display:flex; gap:12px; margin:16px 0; }
.lens { flex:1; border:1px solid var(--line); border-radius:12px; padding:14px;
  background:var(--card); }
.lens h3 { margin:0 0 8px; font-size:0.8rem; text-transform:uppercase;
  letter-spacing:0.04em; color:var(--muted); }
.big { font-size:1.8rem; font-weight:700; }
.market .big { color:var(--market); } .goal .big { color:var(--goal); }
.row { display:flex; justify-content:space-between; font-size:0.85rem;
  color:var(--muted); padding:2px 0; }
.flag { border-left:3px solid var(--warn); padding:8px 12px; margin:16px 0;
  background:var(--card); border-radius:0 8px 8px 0; }
.cond { border:1px dashed var(--line); border-radius:10px; padding:12px;
  margin:16px 0; font-size:0.9rem; }
.cond .badge { font-weight:700; }
.cond .elevated { color:var(--warn); } .cond .normal { color:var(--goal); }
input[type=range] { width:100%; }
.slabels { display:flex; justify-content:space-between; font-size:0.8rem;
  color:var(--muted); }
.note { white-space:pre-wrap; border:1px solid var(--line); border-radius:12px;
  padding:16px; margin:20px 0; background:var(--card); }
.decision { font-weight:600; margin:8px 0 0; }
.disc { color:var(--muted); font-size:0.8rem; margin-top:32px;
  border-top:1px solid var(--line); padding-top:12px; }
svg { width:100%; height:auto; display:block; }
</style>
</head>
<body>
<div class="wrap">
  <h1>The Suitability Lens</h1>
  <p class="sub">A risk label ranks market risk. It does not describe the risk a
  client actually faces. Pick a client and see the gap. Data as of __AS_OF__, in
  US dollars, illustrative and not investment advice.</p>
  <div class="tabs" id="tabs"></div>
  <div id="panel"></div>
  <p class="disc" id="disc"></p>
</div>
<script>
const CASES = /*__CASES_JSON__*/{};
// --- render logic ---
const panel = document.getElementById('panel');
const tabsEl = document.getElementById('tabs');
let current = 0, step = {};

function fmtPct(x){ return (x>0?'+':'') + x.toFixed(0) + '%'; }

function gauge(marketVol, goalPct){
  // simple two-bar SVG: market vol (0-25%) and goal prob (0-100%)
  const w=320,h=90;
  const mv = Math.min(marketVol,25)/25, gp=goalPct/100;
  return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="risk gauge">
    <text x="0" y="14" fill="var(--muted)" font-size="11">Market risk (volatility)</text>
    <rect x="0" y="20" width="${w}" height="10" rx="5" fill="var(--line)"/>
    <rect x="0" y="20" width="${(w*mv).toFixed(0)}" height="10" rx="5" fill="var(--market)"/>
    <text x="0" y="58" fill="var(--muted)" font-size="11">Goal risk (chance of meeting the goal)</text>
    <rect x="0" y="64" width="${w}" height="10" rx="5" fill="var(--line)"/>
    <rect x="0" y="64" width="${(w*gp).toFixed(0)}" height="10" rx="5" fill="var(--goal)"/>
  </svg>`;
}

function condBlock(c){
  const cond = c.conditions;
  if (c.key === 'priya'){
    return `<div class="cond">Current conditions
      <span class="badge ${cond.status}">${cond.status.toUpperCase()}</span><br>
      Over the last year the cap-weighted market (SPY) beat the equal-weighted
      version (RSP) by ${cond.spread_pct.toFixed(1)} points. A wide gap means the
      market is unusually concentrated in its largest companies right now, so the
      drift below is a live concern, not just history. As of ${cond.as_of}.</div>`;
  }
  return `<div class="cond">Current conditions
    <span class="badge ${cond.status}">${cond.status.toUpperCase()}</span><br>
    The rolling stock-bond correlation is ${cond.value>=0?'+':''}${cond.value.toFixed(2)}.
    When it is positive, the bond cushion this label relies on is compromised
    today, not just in 2022. As of ${cond.as_of}.</div>`;
}

function draw(){
  const c = CASES.clients[current];
  const i = step[c.key];
  const mk = c.market[i], goal = c.goal[i];
  panel.innerHTML = `
    <p><strong>${c.name}, ${c.age}.</strong> ${c.story}</p>
    <p><em>Goal:</em> ${c.goal}<br><em>Label:</em> ${c.label}</p>
    <div class="lenses">
      <div class="lens market"><h3>Market risk</h3>
        <div class="big">${mk.vol_pct.toFixed(1)}%</div>
        <div class="row"><span>Worst fall</span><span>${mk.max_drawdown_pct.toFixed(0)}%</span></div>
        <div class="row"><span>Worst year</span><span>${mk.worst_year_pct.toFixed(0)}%</span></div>
      </div>
      <div class="lens goal"><h3>${c.goal_metric==='survival'?'Chance money lasts':c.goal_metric==='accumulation'?'Chance goal is met':'Chance she can hold it'}</h3>
        <div class="big">${goal.toFixed(0)}%</div>
      </div>
    </div>
    ${gauge(mk.vol_pct, goal)}
    <div class="flag"><strong>${c.drift}.</strong> Move the slider and watch the two
      numbers pull apart. The label stays the same the whole way.</div>
    <label class="slabels"><span>${c.axis.label_lo}</span><span>${c.axis.label_hi}</span></label>
    <input type="range" min="0" max="${c.axis.steps.length-1}" value="${i}" id="slider">
    ${condBlock(c)}
    <p class="decision">Discretionary call: ${c.decision}</p>
    <div class="note">${c.note}</div>`;
  document.getElementById('slider').addEventListener('input', e=>{
    step[c.key] = +e.target.value; draw();
  });
}

CASES.clients.forEach((c,idx)=>{ step[c.key]=c.axis.base_index;
  const b=document.createElement('button'); b.className='tab'+(idx===0?' active':'');
  b.textContent=c.name; b.onclick=()=>{ current=idx;
    [...tabsEl.children].forEach((t,j)=>t.classList.toggle('active',j===idx)); draw(); };
  tabsEl.appendChild(b);
});
document.getElementById('disc').textContent =
  'Built from free Yahoo Finance total-return data for simplified index proxies '+
  '(SPY, EFA, EEM, AGG, RSP, SOXX), priced in US dollars. Risk bands and goal '+
  'probabilities are illustrative simulation output and depend on assumptions. '+
  'Nothing here is investment advice.';
draw();
</script>
</body>
</html>
```

Then create `suitability-lens/render.py`:

```python
# suitability-lens/render.py
import json
import os

HERE = os.path.dirname(__file__)


def render_page(payload):
    with open(os.path.join(HERE, "template.html")) as f:
        tpl = f.read()
    html = tpl.replace("/*__CASES_JSON__*/{}", "/*__CASES_JSON__*/" +
                       json.dumps(payload))
    html = html.replace("__AS_OF__", payload["as_of"])
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(html)
    return html
```

Note: the template stores `const CASES = /*__CASES_JSON__*/{};`. The replace swaps
the empty `{}` for the real JSON, so `const CASES = /*...*/{...real...};`. Adjust
the test's regex if needed: `const CASES = /\*__CASES_JSON__\*/(\{.*?\});`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd suitability-lens && python3 -m pytest test_render.py -v`
Expected: PASS. If the JSON regex fails, confirm the marker survived replacement
and update the regex to match `const CASES = /*__CASES_JSON__*/{...};`.

- [ ] **Step 5: Build for real and eyeball it in Chromium**

```bash
cd suitability-lens && python3 build_cases.py
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox \
  --disable-gpu --screenshot=/tmp/lens.png --window-size=390,1600 \
  "file://$(pwd)/index.html"
```
Expected: `index.html` and `cases.json` written; `/tmp/lens.png` shows the tool
with tabs, two lenses, a gauge, a slider, conditions, and a note. View the
screenshot to confirm layout on a narrow (mobile) width.

- [ ] **Step 6: Commit**

```bash
git add suitability-lens/template.html suitability-lens/render.py \
        suitability-lens/test_render.py suitability-lens/index.html \
        suitability-lens/cases.json
git commit -m "Add self-contained page template and render step"
```

---

### Task 8: Repo integration — README companion section and rebuild docs

**Files:**
- Modify: `README.md` (root)
- Create: `suitability-lens/README.md`

**Interfaces:**
- No code interface. Documentation and cross-linking only.

- [ ] **Step 1: Add the companion section to the root README**

Insert after the "Headline result" section (before "Method"):

```markdown
## Companion tool: the Suitability Lens

The analysis diagnoses the problem. The [Suitability Lens](suitability-lens/) is a
small interactive tool that acts on it. It takes three private clients, a retiree,
a house saver, and a concentrated investor, and shows each one's market risk and
goal risk side by side, the drift that bites them, a present-day read on whether
that drift is a live concern, and the plain-English note a discretionary manager
would send. Built from the same data and engine as this analysis. Live link: __ARTIFACT_URL__.
```

- [ ] **Step 2: Write the folder README**

```markdown
# The Suitability Lens

An interactive companion to the "Does cautious mean cautious?" analysis. Three
client cases showing market risk versus goal risk, the drift that bites each, a
current-conditions signal, and a client-facing review note.

## Rebuild

```bash
pip install -r ../requirements.txt pytest
cd suitability-lens
python3 build_cases.py            # uses the committed data snapshot
python3 build_cases.py --fetch    # refreshes data to the latest close first
python3 -m pytest -q              # run the checks
```

`build_cases.py` writes `cases.json` and the self-contained `index.html`. Open
`index.html` in any browser. Everything is embedded; there are no external calls.
```

- [ ] **Step 3: Run the full test suite**

Run: `cd suitability-lens && python3 -m pytest -q`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add README.md suitability-lens/README.md
git commit -m "Link the Suitability Lens from the main README"
```

---

### Task 9: Publish, wire the link, refresh the PDF, push

**Files:**
- Modify: `README.md` (root) — replace `__ARTIFACT_URL__` with the real URL.

- [ ] **Step 1: Publish `suitability-lens/index.html` as an Artifact**

Use the Artifact tool with `file_path` pointing at the built `index.html`, a
`title` of "The Suitability Lens", a one-sentence `description`, and a `favicon`.
Capture the returned URL.

- [ ] **Step 2: Wire the URL into the README and rebuild the PDF**

Replace `__ARTIFACT_URL__` in `README.md` with the artifact URL. Rebuild the
README PDF with the scratchpad `build_pdf.py` helper so the mobile copy is current.

- [ ] **Step 3: Commit and push**

```bash
git add README.md
git commit -m "Add live Suitability Lens link to the README"
git push -u origin claude/building-session-dtbmbc
```

- [ ] **Step 4: Send the PDF and the artifact link to the user.**

---

## Self-Review

**Spec coverage:**
- Three client cases with distinct drifts and decisions → Task 1 (definitions),
  Tasks 2–3 (their numbers), Task 5 (their notes). Covered.
- Two risk lenses (market + goal) → Tasks 2 and 3. Covered.
- Current-conditions layer, both meanings (refresh + live regime) → Task 4
  (signals), Task 6 `build(fetch=...)` (refresh). Covered.
- Client review notes, humanizer-clean → Task 5, with a banned-word test. Covered.
- Self-contained, theme-aware, mobile-first page with inline SVG → Task 7, with a
  no-external-resources test and a mobile screenshot. Covered.
- Delivery: folder, artifact, README companion section → Tasks 8–9. Covered.
- Honesty guardrails on the page → Task 7 template + test assertion. Covered.
- Reuse existing engine, deterministic seed → Global Constraints, Tasks 2–3.
  Covered.

**Placeholder scan:** `__ARTIFACT_URL__` is an intentional marker filled in Task 9,
not a plan placeholder. No "TBD"/"TODO"/"handle edge cases" left.

**Type consistency:** `weights_for(kind, step)`, `market_risk`/`market_grid`,
`simulate_paths`/`goal_grid`, `correlation_regime`/`concentration_signal`,
`review_note(...)`, `build(fetch=...)`, `render_page(payload)` are used with the
same signatures wherever referenced. `engine._SIM_CORE` is set by
`simulate_paths` before `goal_grid` reads it (Task 6 calls `simulate_paths` first).

**One risk to watch during execution:** Task 3 relies on `mc.monthly_returns()`
column order matching `mc.ASSETS`. If margaret's survival test lands outside
60–85%, check that `_port_returns` maps weights by the returns DataFrame's own
column order (it does, via `list(_RET_CORE.columns)`), not a hard-coded order.
