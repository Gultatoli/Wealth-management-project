"""Render the self-contained index.html from template.html + the built payload."""
import json
import os

HERE = os.path.dirname(__file__)


def render_page(payload):
    with open(os.path.join(HERE, "template.html")) as f:
        tpl = f.read()
    data = json.dumps(payload)
    html = tpl.replace("__CASES_JSON__", data).replace("__AS_OF__", payload["as_of"])
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(html)
    return html
