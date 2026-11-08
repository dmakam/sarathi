"""Sarathi end-to-end checks. Run with:  bash run-tests.sh

Starts a throwaway web server on the built site, drives a real Chromium
browser through every feature, and prints PASS / FAIL for each check.
A plain-text copy of the results is written to tests/last-report.txt.
"""
import json
import os
import sys
import threading
import time
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
AXE = open(os.path.join(ROOT, "tests", "vendor", "axe.min.js"), encoding="utf-8").read()
PORT = 8099
BASE = "http://127.0.0.1:%d" % PORT
COACH = os.environ.get("SARATHI_COACH", "http://127.0.0.1:8080")

results = []


def check(name, ok, detail=""):
    results.append((bool(ok), name, detail))
    print(("PASS  " if ok else "FAIL  ") + name + ("   (" + detail + ")" if detail and not ok else ""))
    sys.stdout.flush()


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Quiet, directory=SITE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


PAGES = ["/", "/consult/", "/explore/", "/themes/", "/themes/habits/", "/chapters/", "/2/", "/2/47/", "/6/5/", "/facing/",
         "/map/", "/state/anger/", "/plans/", "/practice/", "/practice/2/47/", "/search/?q=karma",
         "/concept/karma/", "/sources/"]
SIZES = [("laptop", 1536, 864), ("200% zoom", 768, 432), ("phone", 390, 844)]

TYPED = [
    ("my son is stressed about his board exams", "exam-stress"),
    ("I got laid off today and I'm scared", "lost-job"),
    ("I didn't get promoted again", "passed-over"),
    ("the love of my life broke up with me and cheated on me", "cheated"),
    ("my wife wants a divorce", "marriage-ending"),
    ("my crush doesn't like me back", "not-loved-back"),
    ("kids at school keep making fun of me", "bullied"),
    ("I can't stop thinking about my ex", "cant-let-go"),
    ("money is so tight, I can't pay the rent", "money-worries"),
    ("I feel so ashamed of what I did", "ashamed"),
]
CRISIS = ["I want to die", "I don't want to live anymore", "thinking about suicide"]
UNSAFE = ["my husband hits me", "my dad beats me"]


# the redesigned phone screens, plus a few long-standing list pages
PHONE_PAGES = ["/", "/themes/", "/explore/", "/3/42/", "/2/47/", "/practice/3/42/", "/consult/", "/map/",
               "/chapters/", "/2/", "/search/", "/facing/anger/", "/concept/dharma/"]


def run():
    if not os.path.exists(os.path.join(SITE, "index.html")):
        print("The site isn't built yet. Run  bash run-local.sh  once, then try again.")
        sys.exit(2)
    serve()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # 1. every page, three screen sizes: loads, no script errors, no sideways scrolling
        for label, w, h in SIZES:
            page = browser.new_page(viewport={"width": w, "height": h})
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            for u in PAGES:
                del errs[:]
                r = page.goto(BASE + u, wait_until="load")
                page.wait_for_timeout(500)
                over = page.evaluate("document.documentElement.scrollWidth - innerWidth")
                check("%s on %s: opens cleanly" % (u, label), r.ok and not errs and over <= 1,
                      "status %s, errors %s, sideways scroll %spx" % (r.status, errs[:1], over))
            page.close()

        # 1b. legible for young and old eyes, on a phone, in dark and light:
        #     reading text >= 16px, any other text >= 13px, tap targets >= 44x44px (tests/legibility.js),
        #     plus axe's WCAG 2.1 AA scan (contrast and more) at phone size in both colour themes
        LEGIB = open(os.path.join(ROOT, "tests", "legibility.js"), encoding="utf-8").read()
        for theme in ("dark", "light"):
            ctx = browser.new_context(viewport={"width": 390, "height": 844})
            ctx.add_init_script("try{localStorage.setItem('sarathi.theme','%s')}catch(e){}" % theme)
            page = ctx.new_page()
            for u in PHONE_PAGES:
                page.goto(BASE + u)
                page.wait_for_timeout(700)
                views = [""]
                if page.locator(".v-tabs [data-tab]").count():
                    views = [b.get_attribute("data-tab") for b in page.locator(".v-tabs [data-tab]").all()]
                bad, axe_bad = [], []
                for t in views:
                    if t:
                        page.evaluate("document.querySelector('.v-tabs [data-tab=%s]').click()" % t)
                    if theme == "dark":
                        bad += ["%s %s %s '%s'" % (x["kind"], x["sel"], x["fs"], x["txt"]) for x in page.evaluate(LEGIB)]
                    if not page.evaluate("typeof axe !== 'undefined'"):
                        page.add_script_tag(content=AXE)
                    axe_bad += page.evaluate("""async () => (await axe.run(document, {runOnly: ['wcag2a','wcag2aa','wcag21aa']}))
                        .violations.map(v => v.id + ' x' + v.nodes.length)""")
                if theme == "dark":
                    check("%s on a phone: text size and tap targets" % u, not bad, "; ".join(bad[:4]))
                check("%s on a phone, %s: accessibility scan" % (u, theme), not axe_bad, ", ".join(sorted(set(axe_bad))))
            ctx.close()

        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # 2. accessibility scan (WCAG 2.1 AA rules axe can test automatically)
        for u in PAGES:
            page.goto(BASE + u)
            page.wait_for_timeout(800)
            page.add_script_tag(content=AXE)
            v = page.evaluate("""async () => (await axe.run(document, {runOnly: ['wcag2a','wcag2aa','wcag21aa']}))
                .violations.map(v => v.id + ' x' + v.nodes.length)""")
            check("%s: accessibility scan" % u, not v, ", ".join(v))

        # 3. Ask Sarathi: every topic and feeling shows only its own situations
        data = json.load(open(os.path.join(SITE, "data", "consult.json")))
        sits = {s["id"]: s for s in data["sit"]}
        by_title = {s["t"]: s for s in data["sit"]}
        for a in data["aud"]:
            for f in data["feel"]:
                page.goto(BASE + "/consult/")
                page.wait_for_selector(".cx-tile")
                page.click('[data-act=aud][data-id="%s"]' % a[0])
                page.wait_for_timeout(450)
                page.click('[data-act=feel][data-id="%s"]' % f[0])
                page.wait_for_timeout(450)
                titles = page.eval_on_selector_all(".cx-sits .cx-sit span", "els => els.map(e => e.textContent)")
                wrong = [t for t in titles if t in by_title and (a[0] not in by_title[t]["a"] or f[0] not in by_title[t]["f"])]
                check("Ask: %s + %s shows its own options" % (a[1], f[1]), len(titles) >= 2 and not wrong,
                      "%d options, off-topic: %s" % (len(titles), wrong))

        # 4. typed stories land on the right situation
        def typed(text):
            page.goto(BASE + "/consult/")
            page.wait_for_selector("#cx-text")
            page.fill("#cx-text", text)
            page.press("#cx-text", "Enter")
            page.wait_for_timeout(500)
            return page.inner_text(".cx-h"), page.eval_on_selector_all(".cx-sits .cx-sit", "els => els.map(e => e.dataset.id)")

        for text, want in TYPED:
            h, ids = typed(text)
            check('Ask: "%s" suggests %s first' % (text, sits[want]["t"]), ids[:1] == [want], "got %s" % ids[:3])
        for text in CRISIS:
            h, _ = typed(text)
            check('Ask: "%s" shows crisis help first' % text, "talk to someone" in h.lower(), h)
        for text in UNSAFE:
            h, _ = typed(text)
            check('Ask: "%s" shows the safety card' % text, "safety" in h.lower(), h)

        # 5. an answer card: verse, romanised line, notes, buttons, save
        page.goto(BASE + "/consult/#cheated")
        page.wait_for_selector(".cx-card")
        page.wait_for_timeout(600)
        check("Ask: answer shows shloka, romanised line and three notes",
              page.locator(".cx-sa").count() == 1 and (page.locator(".cx-tl").text_content() or "").strip() != "" and page.locator(".cx-notes > div").count() == 3)
        page.click("[data-act=next]")
        page.wait_for_timeout(400)
        check("Ask: Another verse switches the shloka", "2.56" in page.inner_text(".cx-ref"))
        page.click("[data-act=save]")
        page.wait_for_timeout(300)
        check("Ask: Save adds it to Saved for you", page.locator(".cx-savelist li").count() >= 1)
        page.click('[data-act=fb][data-v="no"]')
        page.wait_for_timeout(300)
        check('Ask: "Not quite" offers a box to say more', page.locator(".cx-fb .cx-write").count() == 1)

        # 6. keyboard only: Tab to a tile, Enter moves to the next question
        page.goto(BASE + "/consult/")
        page.wait_for_selector(".cx-tile")
        reached = False
        for _ in range(20):
            page.keyboard.press("Tab")
            if page.evaluate("document.activeElement.classList.contains('cx-tile')"):
                reached = True
                break
        if reached:
            page.keyboard.press("Enter")
            page.wait_for_timeout(500)
        check("Keyboard: Tab reaches the tiles and Enter goes to the next step", reached and "feel" in page.inner_text(".cx-h").lower())

        # 7. verse page: translation tabs and word meanings
        page.goto(BASE + "/2/47/")
        tabs = page.locator('.tabs [role="tab"]')
        n = tabs.count()
        if n > 1:
            tabs.nth(1).click()
            page.wait_for_timeout(200)
        check("Verse 2.47: translation tabs switch", n > 1 and tabs.nth(1).get_attribute("aria-selected") == "true", "%d tabs" % n)
        check("Verse 2.47: romanised Sanskrit is shown", page.locator('.tl[lang="sa-Latn"]').count() >= 1)
        check("Verse 2.47: verse map is drawn", page.locator(".vt-hub").count() >= 1 and page.locator(".vt-chip").count() >= 1)

        # 8. map: feeling journey and path finder
        page.goto(BASE + "/map/")
        page.wait_for_timeout(600)
        page.locator(".feel").first.click()
        page.wait_for_timeout(500)
        check("Map: picking a feeling draws its journey", page.locator(".jflow").count() == 1)
        page.click(".pf-go")
        page.wait_for_timeout(400)
        check("Map: path finder links Anger to Forgiveness", page.locator(".pf-out li").count() >= 2)

        # 9. practice: no-microphone check mark, text size control
        page.goto(BASE + "/practice/2/47/")
        page.evaluate("localStorage.removeItem('sarathi.recite')")
        page.reload()
        page.wait_for_selector(".self")
        page.click(".self")
        page.wait_for_timeout(300)
        check("Practice: 'I recited it from memory' adds a check mark", page.locator(".ticks .tick.ok").count() == 1)
        page.click(".nav-size")
        z = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--zoom').trim()")
        check("Text size button makes text larger", z == "1.15", "zoom " + z)
        page.click(".nav-size")
        page.click(".nav-size")

        # 10. the recitation coach (only if run-local.sh is running)
        try:
            urllib.request.urlopen(COACH + "/api/health", timeout=3)
            mp3 = os.path.join(SITE, "audio", "2", "47.mp3")
            req = urllib.request.Request(COACH + "/api/score?v=2.47", data=open(mp3, "rb").read(), method="POST",
                                         headers={"Content-Type": "audio/mpeg"})
            t0 = time.time()
            res = json.load(urllib.request.urlopen(req, timeout=120))
            clear = sum(1 for w in res.get("words", []) if w.get("mark") == "clear")
            check("Coach: scores the reference reading of 2.47 (%d of %d words clear, %.0fs)" % (clear, len(res.get("words", [])), time.time() - t0),
                  clear >= len(res.get("words", [])) - 2)
        except Exception as e:
            print("SKIP  Coach scoring: start  bash run-local.sh  in another window to include it (%s)" % type(e).__name__)

        browser.close()

    bad = [r for r in results if not r[0]]
    summary = "\n%d checks, %d passed, %d failed" % (len(results), len(results) - len(bad), len(bad))
    print(summary)
    with open(os.path.join(ROOT, "tests", "last-report.txt"), "w", encoding="ascii", errors="replace") as f:
        for ok, name, detail in results:
            f.write(("PASS  " if ok else "FAIL  ") + name + ("   (" + detail + ")" if detail and not ok else "") + "\n")
        f.write(summary + "\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    run()
