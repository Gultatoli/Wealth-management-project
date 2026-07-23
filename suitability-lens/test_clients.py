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
        assert all(b > a for a, b in zip(c.axis.steps, c.axis.steps[1:]))
        assert 0 <= c.axis.base_index < len(c.axis.steps)


def test_margaret_is_decumulation_retiree():
    m = next(c for c in clients.CLIENTS if c.key == "margaret")
    assert m.age == 66
    assert m.axis.kind == "equity"
    assert m.amounts["pot"] == 600_000
    assert m.amounts["withdraw_rate"] == 0.04
