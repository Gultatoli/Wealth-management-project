"""
Drive the page in a real browser, check it, and photograph it.

Two jobs. First, catch the things that only appear once the page is running: a
console error, a layout that scrolls sideways on a phone, an option that never
renders. Second, produce screenshots at phone width, because the page itself
cannot be opened from a repository on a mobile browser and the pictures are how
the work gets reviewed.

The Chromium CLI's own --screenshot flag ignores the mobile viewport and
produces a misleading clipped image, so this drives Playwright with an explicit
viewport instead.

Run:
    python3 shots.py
"""

import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOT_DIR = os.path.join(HERE, "screenshots")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
WIDTH = 390  # the narrow end of what a modern phone reports


def shrink(path):
    """Cut the screenshots to a sane size for a repository.

    The debrief runs to about eleven thousand pixels, which at twice the device
    scale is well over a megabyte of PNG. The design is flat colour with no
    photographs, so reducing to a 256-colour palette is invisible and takes
    roughly three quarters off. Retina scale is kept because these images are
    how the work gets reviewed on a phone.
    """
    from PIL import Image
    with Image.open(path) as im:
        im.convert("RGB").quantize(colors=256, method=Image.MEDIANCUT).save(
            path, optimize=True)


def main():
    os.makedirs(SHOT_DIR, exist_ok=True)
    errors = []
    problems = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": WIDTH, "height": 900},
                                device_scale_factor=2)
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto("file://" + os.path.join(HERE, "index.html"))
        page.wait_for_timeout(300)

        def check_overflow(where):
            over = page.evaluate(
                "() => document.documentElement.scrollWidth - "
                "document.documentElement.clientWidth")
            if over > 0:
                problems.append(f"{where}: page scrolls {over}px sideways")

        def shot(name, full=False):
            path = os.path.join(SHOT_DIR, name)
            page.screenshot(path=path, full_page=full)
            shrink(path)

        check_overflow("brief")
        shot("1-brief.png", full=True)

        page.click("#start")
        page.wait_for_timeout(200)
        check_overflow("first decision")
        shot("2-first-decision.png", full=True)

        # Play a full round, taking the documented choice each time, and check
        # that every decision renders options and a consequence.
        book = None
        for key in ("by_the_book",):
            book = page.evaluate(f"() => window.GAME.comparisons['{key}'].picks")

        n = page.evaluate("() => window.GAME.decisions.length")
        for i in range(n):
            did = page.evaluate(f"() => window.GAME.decisions[{i}].id")
            want = book.get(did)
            btn = page.query_selector(f'.option[data-opt="{want}"]')
            if btn is None:
                avail = page.eval_on_selector_all(
                    ".option", "els => els.map(e => e.dataset.opt)")
                problems.append(
                    f"{did}: documented choice {want} not offered, saw {avail}")
                btn = page.query_selector(".option")
            btn.click()
            page.wait_for_timeout(120)

            if i == 3:  # the 2008 phone call, the pivotal one
                check_overflow("2008 call")
                shot("3-the-call.png", full=True)

            nxt = page.query_selector("#next")
            if nxt is None:
                problems.append(f"{did}: no next button after choosing")
                break
            nxt.click()
            page.wait_for_timeout(120)

        page.wait_for_timeout(400)
        check_overflow("debrief")
        shot("4-debrief.png", full=True)

        # A quick look at the dark theme, since both are meant to work.
        page.emulate_media(color_scheme="dark")
        page.wait_for_timeout(200)
        shot("5-debrief-dark.png", full=True)

        final = page.evaluate(
            "() => { const r = Engine.run(window.GAME, window.GAME."
            "comparisons.by_the_book.picks); return {v: r.finalValue, "
            "s: r.survival}; }")

        browser.close()

    print(f"screenshots written to {os.path.relpath(SHOT_DIR, HERE)}/")
    print(f"by-the-book run: £{final['v']:,.0f}, {final['s']*100:.0f}% to 95")

    if errors:
        print("\nconsole errors:")
        for e in errors[:10]:
            print(" ", e)
    if problems:
        print("\nproblems:")
        for p in problems:
            print(" ", p)
    if errors or problems:
        sys.exit(1)
    print("\nno console errors, no horizontal overflow at "
          f"{WIDTH}px, all {n} decisions playable")


if __name__ == "__main__":
    main()
