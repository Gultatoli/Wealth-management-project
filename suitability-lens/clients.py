"""The three client cases. Pure data, no computation.

Each client showcases one of the paper's three drifts and ends in its own
discretionary decision. The `axis` describes the interactive lever: a set of
allocation steps the slider snaps to, with one marked as the client's current
(base) position.
"""
from dataclasses import dataclass


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
