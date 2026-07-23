import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import analyse
import engine

PRICES = analyse.load_prices()


def test_as_of_is_iso_date():
    s = engine.as_of_date(PRICES)
    assert len(s) == 10 and s[4] == "-" and s[7] == "-"


def test_correlation_regime_shape():
    r = engine.correlation_regime(PRICES)
    assert -1.0 <= r["value"] <= 1.0
    assert r["status"] in ("elevated", "normal")
    assert len(r["as_of"]) == 10


def test_concentration_signal_shape():
    c = engine.concentration_signal(PRICES)
    assert isinstance(c["spread_pct"], float)
    assert c["status"] in ("elevated", "normal")
    assert len(c["as_of"]) == 10
