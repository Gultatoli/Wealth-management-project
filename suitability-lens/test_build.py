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
    assert 68 <= m["goal"][m["axis"]["base_index"]] <= 82

    p = next(c for c in payload["clients"] if c["key"] == "priya")
    assert p["goal_metric"] == "concentration"
    # her second lens is a negative recent drawdown, deepening with concentration
    assert p["goal"][-1] < p["goal"][0] <= 0
