"""
The decision script has to stay true to the data underneath it.

Two kinds of check. The structural ones make sure every decision is playable:
real month, sane scores, options that reference models that exist. The factual
ones are the important half. Every market figure quoted anywhere in the
narrative is recomputed here from the CSVs, and the test fails if the number in
the prose is not the number in the data.

That matters more than it sounds. The whole point of the project is that a
person can be asked "where does 82% come from?" in an interview and answer it.
A figure that quietly goes stale when the data is refreshed would be worse than
no figure at all.
"""

import os
import sys

import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))

import analyse as A  # noqa: E402
import client  # noqa: E402
import decisions as DEC  # noqa: E402
import market  # noqa: E402


@pytest.fixture(scope="module")
def prices():
    return A.load_prices()


@pytest.fixture(scope="module")
def months():
    return market.build()[0]["months"]


@pytest.fixture(scope="module")
def prose():
    """Every word of narrative in the script, as one string."""
    parts = []
    for d in DEC.DECISIONS:
        parts.extend(d["context"])
        parts.append(d.get("client") or "")
        parts.append(d["question"])
        for o in d["options"]:
            parts.extend([o["label"], o.get("detail", ""), o.get("file", ""),
                          o["after"]])
    return " ".join(parts)


# --------------------------------------------------------------------------
# structure
# --------------------------------------------------------------------------

def test_every_decision_lands_on_a_real_month(months):
    for d in DEC.DECISIONS:
        assert d["month"] in months, f"{d['id']} is not a month in the data"


def test_decisions_are_in_order():
    got = [d["month"] for d in DEC.DECISIONS]
    assert got == sorted(got)


def test_decisions_start_after_the_data_does(months):
    assert DEC.DECISIONS[0]["month"] == months[0]


def test_options_are_well_formed():
    for d in DEC.DECISIONS:
        ids = [o["id"] for o in d["options"]]
        assert len(ids) == len(set(ids)), f"{d['id']} has duplicate option ids"
        assert 2 <= len(ids) <= 4
        for o in d["options"]:
            assert o["label"] and o["after"], f"{d['id']}/{o['id']} is missing text"
            assert -2 <= o["suitability"] <= 2
            assert -2 <= o["conduct"] <= 2
            if o.get("model"):
                assert o["model"] in market.MODELS, \
                    f"{d['id']}/{o['id']} names a model that does not exist"


def test_every_decision_has_at_least_one_ungated_option():
    """A player must never reach a decision with nothing to choose."""
    for d in DEC.DECISIONS:
        ungated = [o for o in d["options"] if not o.get("requires")]
        assert len(ungated) >= 2, f"{d['id']} could leave a player stuck"


def test_ages_match_her_birthday():
    for d in DEC.DECISIONS:
        year, month = int(d["month"][:4]), int(d["month"][5:])
        expected = year - client.BORN - (1 if month < client.BIRTH_MONTH else 0)
        assert d["age"] == expected, \
            f"{d['id']} says she is {d['age']}, the dates say {expected}"


def test_suitability_bands_cover_the_whole_period(months):
    covered = []
    for start, end, lo, hi, _why in client.SUITABILITY_BANDS:
        assert lo < hi
        covered.append((start, end))
    assert covered[0][0] == months[0]
    assert covered[-1][1] == months[-1]
    for (_, end), (start, _) in zip(covered, covered[1:]):
        assert end < start, "bands must not overlap"


# --------------------------------------------------------------------------
# the numbers in the prose
# --------------------------------------------------------------------------

def _pct(x, dp=1):
    return f"{abs(x) * 100:.{dp}f}%"


def test_the_2008_fall_figures(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    peak = eq[(eq.index >= "2007-01-01") & (eq.index <= "2008-01-01")].max()

    at_oct_2008 = eq[eq.index <= "2008-10-01"].iloc[-1]
    assert _pct(at_oct_2008 / peak - 1) in prose, "the October 2008 fall is wrong"

    trough = eq[(eq.index >= "2008-06-01") & (eq.index <= "2009-12-31")].min()
    assert _pct(trough / peak - 1) in prose, "the peak-to-trough fall is wrong"


def test_the_2009_recovery(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    w = eq[(eq.index >= "2009-03-09") & (eq.index <= "2009-12-31")]
    assert _pct(w.iloc[-1] / w.iloc[0] - 1) in prose


def test_the_covid_fall_and_rebound(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    bal = A.portfolio_value(prices, A.graded(0.60))
    for series in (eq, bal):
        w = series[(series.index >= "2020-02-19") & (series.index <= "2020-03-23")]
        assert _pct(w.iloc[-1] / w.iloc[0] - 1) in prose

    w = eq[(eq.index >= "2020-03-23") & (eq.index <= "2020-12-31")]
    assert _pct(w.iloc[-1] / w.iloc[0] - 1) in prose


def test_the_2022_figures(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    cau = A.portfolio_value(prices, A.graded(0.40))
    agg = prices["AGG"] / prices["AGG"].iloc[0]

    for series in (eq, cau, agg):
        assert _pct(A.calendar_year_return(series, 2022)) in prose

    ratio = A.calendar_year_return(cau, 2022) / A.calendar_year_return(eq, 2022)
    assert f"{ratio * 100:.0f}%" in prose, "the 82% comparison is wrong"

    ratio_2008 = (A.calendar_year_return(cau, 2008) /
                  A.calendar_year_return(eq, 2008))
    assert f"{ratio_2008 * 100:.0f}%" in prose, "the 2008 comparison is wrong"


def test_the_concentration_gap(prices, prose):
    for ticker in ("SPY", "RSP"):
        s = prices[ticker] / prices[ticker].iloc[0]
        for year in (2023, 2024):
            assert _pct(A.calendar_year_return(s, year)) in prose

    spy = prices["SPY"] / prices["SPY"].iloc[0]
    rsp = prices["RSP"] / prices["RSP"].iloc[0]
    gap = (A.calendar_year_return(spy, 2023) -
           A.calendar_year_return(rsp, 2023)) * 100
    assert f"{gap:.1f} points" in prose


def test_the_bond_years(prices, prose):
    agg = prices["AGG"] / prices["AGG"].iloc[0]
    shy = pd.read_csv(os.path.join(HERE, "..", "data", "SHY.csv"),
                      parse_dates=["date"], index_col="date")["adj_close"]
    shy = shy.reindex(prices.index).ffill()
    shy = shy / shy.iloc[0]

    for year in (2008, 2013, 2018, 2020, 2021, 2022):
        assert _pct(A.calendar_year_return(agg, year)) in prose, \
            f"the {year} bond return is wrong"

    for year in (2013, 2022):
        assert _pct(A.calendar_year_return(shy, year)) in prose, \
            f"the {year} short-bond return is wrong"

    assert f"{A.cagr(shy) * 100:.1f}%" in prose
    assert f"{A.cagr(agg) * 100:.1f}%" in prose


def test_the_equity_years(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    for year in (2004, 2005, 2006, 2007, 2013, 2018):
        assert _pct(A.calendar_year_return(eq, year)) in prose, \
            f"the {year} equity return is wrong"


def test_the_cash_return(prose):
    cash = market.cash_monthly_returns().loc[market.START:]
    years = len(cash) / 12
    cagr = float((1 + cash).prod()) ** (1 / years) - 1
    assert f"{cagr * 100:.1f}%" in prose, "the cash return is wrong"


def test_the_growth_portfolio_drawdown(prices, prose):
    growth = A.portfolio_value(prices, A.graded(0.80))
    assert _pct(A.max_drawdown(growth)) in prose


def test_the_peak_date_is_right(prices, prose):
    eq = A.portfolio_value(prices, A.graded(1.0))
    peak = eq[(eq.index >= "2007-01-01") & (eq.index <= "2008-01-01")].idxmax()
    assert peak.strftime("%-d %B %Y") in prose
    trough = eq[(eq.index >= "2008-06-01") & (eq.index <= "2009-12-31")].idxmin()
    assert trough.strftime("%-d %B %Y") in prose
