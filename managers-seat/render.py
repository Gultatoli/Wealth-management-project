"""
Turn template.html plus the data into a page that works with no network.

Two files come out:

    index.html          a complete document, openable from disk
    artifact_body.html  the same thing without the document wrapper, for a host
                        that supplies its own <head> and <body>

Nothing is fetched at runtime. The market data, the survival grid and the engine
are all inlined, so the page opens on a plane, on a phone, or on an interviewer's
laptop with the wifi password nobody can remember.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

TITLE = "The Manager's Seat"
DESCRIPTION = ("Run a private client's portfolio through twenty-two years of "
               "real market history and see what your decisions did to her.")

DOC = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def build_body():
    with open(os.path.join(HERE, "template.html")) as f:
        template = f.read()
    with open(os.path.join(HERE, "engine.js")) as f:
        engine = f.read()
    with open(os.path.join(HERE, "game.json")) as f:
        data = f.read()

    start = "/*__GAME_DATA__*/"
    end = "/*__END_GAME_DATA__*/"
    a = template.index(start)
    b = template.index(end) + len(end)
    body = template[:a] + data + template[b:]

    body = body.replace("/*__ENGINE__*/", engine)

    # A closing script tag inside a JSON string would end the block early. The
    # data is generated from our own files so this cannot currently happen, but
    # it costs nothing to make it impossible rather than unlikely.
    assert "</script>" not in data, "data contains a closing script tag"
    return body


def main():
    body = build_body()

    with open(os.path.join(HERE, "artifact_body.html"), "w") as f:
        f.write(body)

    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(DOC.format(title=TITLE, description=DESCRIPTION, body=body))

    size = os.path.getsize(os.path.join(HERE, "index.html")) / 1024
    print(f"index.html and artifact_body.html written ({size:.0f} KB, "
          f"self-contained)")


if __name__ == "__main__":
    main()
