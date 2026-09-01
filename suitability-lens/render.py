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
    _write_artifact_body(html)
    return html


def _write_artifact_body(html):
    """Emit a body-only version for hosts that supply their own html/head/body
    skeleton (the claude.ai Artifact wrapper). Keeps the <style> and the body
    contents, drops the outer document tags so nothing is double-wrapped."""
    style = html[html.index("<style>"):html.index("</style>") + len("</style>")]
    body_inner = html[html.index("<body>") + len("<body>"):html.index("</body>")]
    with open(os.path.join(HERE, "artifact_body.html"), "w") as f:
        f.write(style + "\n" + body_inner.strip() + "\n")
