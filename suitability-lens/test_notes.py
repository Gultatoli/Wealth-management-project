import notes
from clients import CLIENTS

BANNED = ("leverage", "robust", "seamless", "unlock", "delve", "landscape",
          "synergy", "elevate", "empower", "streamline")


def test_margaret_note_is_plain_and_specific():
    m = next(c for c in CLIENTS if c.key == "margaret")
    text = notes.review_note(
        m,
        base_market={"vol_pct": 5.5, "max_drawdown_pct": -18.0, "recent_dd_pct": -18.0},
        base_goal=75,
        target_market={"vol_pct": 11.2, "max_drawdown_pct": -36.0, "recent_dd_pct": -22.0},
        target_goal=92,
        conditions={"value": 0.42, "status": "elevated", "as_of": "2026-07-21"},
    )
    assert "—" not in text                     # no em dashes
    assert "75" in text and "92" in text
    assert 200 < len(text) < 1200
    for banned in BANNED:
        assert banned not in text.lower()


def test_all_three_notes_render_without_em_dashes():
    dummy_market = {"vol_pct": 20.0, "max_drawdown_pct": -58.0, "recent_dd_pct": -39.0}
    dummy_target = {"vol_pct": 19.0, "max_drawdown_pct": -58.0, "recent_dd_pct": -26.0}
    cond = {"value": 0.42, "status": "elevated", "as_of": "2026-07-21",
            "spread_pct": 2.5}
    for c in CLIENTS:
        text = notes.review_note(c, dummy_market, 60, dummy_target, 90, cond)
        assert text.startswith("Dear")
        assert "—" not in text
        for banned in BANNED:
            assert banned not in text.lower()
