import json
import re

import build_cases
import render


def test_render_is_self_contained():
    payload = build_cases.build(fetch=False)
    html = render.render_page(payload)

    # embedded JSON parses out of the data script tag
    m = re.search(
        r'<script id="cases-data" type="application/json">(.*?)</script>',
        html, re.S)
    assert m
    parsed = json.loads(m.group(1))
    assert len(parsed["clients"]) == 3

    # no external resource loads
    assert 'src="http' not in html
    assert 'href="http' not in html
    assert "cdn" not in html.lower()
    assert "<link" not in html.lower()

    for name in ("Margaret", "Tom", "Priya"):
        assert name in html
    assert "investment advice" in html.lower()
    assert payload["as_of"] in html
