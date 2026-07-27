"""
The client. Pure data, no logic, so the case can be read and argued with
without reading any code.

Ruth is invented, but nothing about her is unusual. A client who sells a
business in her late fifties, wants an inflation-linked income from her mid
sixties, and scores "cautious" on a risk questionnaire while needing a return
that cautious will struggle to deliver, is the ordinary case in private-client
work rather than the exotic one. That tension is the whole point of her: the
paper argues that a risk label describes market risk and misses goal risk, and
Ruth is what that argument looks like when it belongs to a person.

Everything below is stated in 2004 money and uprated by INFLATION, so the
income requirement grows the way a real one does.
"""

NAME = "Ruth Alderman"
BORN = 1945
BIRTH_MONTH = 9   # she has a birthday in September, so her age through any
                  # given year is unambiguous rather than off by one

# The engagement begins in January 2004, the first full month of the paper's
# common data window.
START_MONTH = "2004-01"
END_MONTH = "2026-07"

POT = 450_000            # proceeds from selling her share of the business
INCOME = 22_000          # a year, in 2004 money, needed from age 65
INCOME_FROM = "2011-01"  # the month she stops working
INFLATION = 0.025        # the paper's Monte Carlo assumption, kept identical

# She wants the income to last to 95. History in this simulator runs out in
# July 2026, when she is 80, so the last 15 years are answered by the paper's
# block bootstrap rather than by history.
DIES_AT = 95
AGE_AT_END = 80

# An all-in annual charge: the discretionary fee, platform and underlying fund
# costs together. One percent is deliberately the same figure the paper uses,
# because the paper shows a 1% fee consuming about a quarter of the balanced
# portfolio's 23-year gain. Charging it here means the simulator has to earn it,
# and the debrief says plainly how much was taken.
FEE = 0.010

# What the risk questionnaire said, and what it missed. Both are needed, because
# the gap between them is the first decision the player has to make.
PROFILE = {
    "questionnaire": "Cautious",
    "tolerance": (
        "She sat through 2000 to 2003 in a workplace pension and remembers it "
        "badly. She says a fall of more than about 15% would stop her sleeping."
    ),
    "capacity": (
        "Moderate. Outside this portfolio she holds a £20,000 emergency fund, a "
        "small defined-benefit pension of £6,200 a year from 65, and the state "
        "pension. The house is hers, mortgage free. A permanent loss would not "
        "make her destitute, but it would cut the income this pot is meant to "
        "provide, and there is no way to replace the capital."
    ),
    "horizon": (
        "Thirty-seven years to 95, and she has a mother who reached 94. The "
        "money has to work for a long time after she stops."
    ),
    "requirement": (
        "£22,000 a year from 65, rising with inflation, on top of the DB and "
        "state pensions. On a £450,000 pot that is a demanding ask over a "
        "thirty-year retirement, and it is the number the questionnaire never "
        "asked about."
    ),
}

INTRO = (
    "January 2004. Ruth Alderman is 58. She has just sold her share of the "
    "family printing business and £450,000 has landed in an account that has "
    "never held more than five figures before. She wants to stop working at 65 "
    "and draw £22,000 a year from this money, rising with the cost of living, "
    "for as long as she lives. Her risk questionnaire says Cautious.\n\n"
    "You are her discretionary manager. From here to today you make the calls, "
    "and real market history happens to them."
)

# The suitability scoring needs to know what a defensible equity weight looks
# like at each stage of her life. These are wide bands on purpose: the argument
# is not that one number is correct, it is that some choices are outside any
# reasonable reading of her circumstances. Breaching a band is not automatically
# wrong, it is something the file has to justify.
SUITABILITY_BANDS = [
    # (from_month, to_month, min_equity, max_equity, why)
    ("2004-01", "2010-12", 0.35, 0.85,
     "Seven years from retirement with a thirty-plus year horizon and a "
     "demanding income requirement. Too little equity here is a goal-risk "
     "problem, not a safe choice."),
    ("2011-01", "2020-12", 0.30, 0.75,
     "Drawing an inflation-linked income with twenty-five years still to fund. "
     "She needs growth and she needs to survive a bad decade."),
    ("2021-01", "2026-07", 0.25, 0.65,
     "In her late seventies, still drawing, with fifteen years to fund. The "
     "pot no longer has time to recover from a very deep fall."),
]
