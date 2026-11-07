"""Generate the phone-first Sarathi prototype artboards (one .dc.html per screen)."""
import json
import os
import re
import sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
WHEEL = open(os.path.join(HERE, "wheel.txt"), encoding="utf-8").read().strip()

PAPER, INK, MUTED, LINE, TEAL, SAFF, SAFFD = "#F2F6F7", "#1E2B3A", "#5D6B70", "#DDE6E8", "#0F5257", "#E9A845", "#B9781C"

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&amp;family=Newsreader:wght@400;500&amp;family=Tiro+Devanagari+Sanskrit&amp;display=swap">'
STYLE = """<style>
body{margin:0}
a{color:#0F5257}a:hover{color:#0B3F43}
@keyframes lampPulse{0%,100%{box-shadow:inset 0 0 0 1.5px #E9A845,0 0 0 0 rgba(233,168,69,.55)}50%{box-shadow:inset 0 0 0 1.5px #E9A845,0 0 0 9px rgba(233,168,69,0)}}
.lamp-next{animation:lampPulse 2.6s ease-in-out infinite}
@keyframes sheen{0%{background-position:200% 0}100%{background-position:-200% 0}}
.edge{background:linear-gradient(100deg,rgba(233,168,69,0) 30%,rgba(255,226,170,.9) 50%,rgba(233,168,69,0) 70%);background-size:200% 100%;animation:sheen 6s linear infinite}
@keyframes ring{0%{transform:scale(1);opacity:.55}100%{transform:scale(1.9);opacity:0}}
.ring{animation:ring 1.6s ease-out infinite}
.ring2{animation:ring 1.6s ease-out .8s infinite}
main>*{flex-shrink:0}
</style>"""


def lamp(lit, w=26):
    h = round(w * 46 / 40)
    if lit:
        return ('<svg width="%d" height="%d" viewBox="0 0 40 46" aria-hidden="true"><circle cx="20" cy="15" r="13" fill="#FFC86B" opacity="0.35"></circle>'
                '<path d="M20 4 C25 11 25 17 20 21 C15 17 15 11 20 4 Z" fill="#F5A623"></path><path d="M20 10 C22.5 13.5 22.5 16.5 20 19 C17.5 16.5 17.5 13.5 20 10 Z" fill="#FFE7A3"></path>'
                '<path d="M4 24 C4 34 12 40 20 40 C28 40 36 34 36 24 Z" fill="#B5653E"></path><path d="M3 24 H37" stroke="#8C4A2B" stroke-width="2.4" stroke-linecap="round"></path><path d="M14 40 H26 L24 44 H16 Z" fill="#8C4A2B"></path></svg>') % (w, h)
    return ('<svg width="%d" height="%d" viewBox="0 0 40 46" aria-hidden="true"><path d="M20 19 V15" stroke="#A9A299" stroke-width="1.6" stroke-linecap="round"></path>'
            '<path d="M4 24 C4 34 12 40 20 40 C28 40 36 34 36 24 Z" fill="#CFC7BB"></path><path d="M3 24 H37" stroke="#B8AFA2" stroke-width="2.4" stroke-linecap="round"></path><path d="M14 40 H26 L24 44 H16 Z" fill="#B8AFA2"></path></svg>') % (w, h)


def lamp_next(w=22, box=34):
    return ('<span class="lamp-next" style="display: grid; place-items: center; width: %dpx; height: %dpx; border-radius: 999px; background: rgba(233,168,69,0.14); flex: none;">%s</span>' % (box, box, lamp(False, w)))


ICON = {
    "ask": '<path d="M4 5h16v11H9l-5 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path>',
    "learn": '<path d="M12 3c2.6 3.3 2.6 6.2 0 8.4-2.6-2.2-2.6-5.1 0-8.4z" fill="currentColor"></path><path d="M4 13h16c0 4.4-3.6 7-8 7s-8-2.6-8-7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path>',
    "explore": '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="M15.5 8.5l-2 5-5 2 2-5z" fill="currentColor"></path>',
}
ARROW = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"></path></svg>'
CHEV_L = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"></path></svg>'
CHEV_R = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"></path></svg>'
PLAY = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M7 4.5v15l13-7.5z"></path></svg>'
MIC = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3"></rect><path d="M5 11a7 7 0 0 0 14 0M12 18v3"></path></svg>'
SEARCH = '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-4-4"></path></svg>'
LOGO = '<svg width="24" height="24" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3c5 6 8 11 8 16a8 8 0 0 1-16 0c0-5 3-10 8-16z" fill="#1F7A72"></path><circle cx="16" cy="19" r="4.2" fill="#C9A227"></circle><circle cx="16" cy="19" r="2" fill="#24306E"></circle></svg>'


def tabbar(active, dark=False):
    items = [("ask", "Ask", "PHome.dc.html"), ("learn", "Learn", "PLearn.dc.html"), ("explore", "Explore", "PExplore.dc.html")]
    cells = []
    for k, label, href in items:
        on = k == active
        col = TEAL if on else MUTED
        pill = 'background: #E3EFEC;' if on else ''
        cells.append('<a href="%s" aria-label="%s"%s style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; min-height: 52px; text-decoration: none; color: %s; font-size: 12.5px; font-weight: %s;">'
                     '<span style="display: grid; place-items: center; width: 56px; height: 30px; border-radius: 999px; %s"><svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">%s</svg></span>%s</a>'
                     % (href, label, ' aria-current="page"' if on else '', col, '700' if on else '600', pill, ICON[k], label))
    # colour switch: dark is the default; this cell takes you to the same screen in the other colours
    cells.append('<a href="@@THREF@@" data-toggle="theme" aria-label="Switch to @@TLABEL@@ colours" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; min-height: 52px; text-decoration: none; color: %s; font-size: 12.5px; font-weight: 600;">'
                 '<span style="display: grid; place-items: center; width: 56px; height: 30px; border-radius: 999px;"><svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">@@TICON@@</svg></span>@@TLABEL@@</a>' % MUTED)
    return ('<nav aria-label="Main" style="position: absolute; left: 0; right: 0; bottom: 0; height: 84px; box-sizing: border-box; padding: 6px 12px 22px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); background: rgba(255,255,255,0.96); border-top: 1px solid %s; z-index: 5;">%s</nav>' % (LINE, "".join(cells)))


def page(title, body, props=None, script_body="renderVals() { return {}; }", w=390, h=844):
    p = {"$preview": {"width": w, "height": h}}
    if props:
        p.update(props)
    src = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>%s</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
%s
%s
</helmet>
%s
</x-dc>
<script type="text/x-dc" data-dc-script data-props='%s'>
class Component extends DCLogic {
  %s
}
</script>
</body>
</html>
""" % (title, FONTS, STYLE, body, json.dumps(p), script_body)
    return src


def ent(s):
    # keep markup ASCII: every non-ASCII character outside the script becomes an entity
    head, sep, tail = s.partition('<script type="text/x-dc"')
    head = "".join(c if ord(c) < 128 else "&#%d;" % ord(c) for c in head)
    return head + sep + tail


MOON = '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path>'
SUN = '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>'


def save(name, src):
    # light files point their colour switch at the dark twin (D...), which dark.py flips back
    src = src.replace("@@THREF@@", "D" + name[1:]).replace("@@TLABEL@@", "Dark").replace("@@TICON@@", MOON)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(ent(src))


FRAME = 'position: relative; width: 390px; height: 844px; overflow: hidden; background: %s; color: %s; font-family: Figtree, system-ui, sans-serif;'

# ---------------------------------------------------------------- 1. Home
wheel = '<g transform="translate(195 392) scale(0.66) translate(-1150 -640)">' + WHEEL + '</g>'
home = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <section style="position: relative; height: 452px; background: linear-gradient(180deg, #0A1230 0%, #16275A 58%, #23396E 100%); color: #FFFFFF;">
    <svg width="390" height="452" viewBox="0 0 390 452" aria-hidden="true" style="position: absolute; left: 0; top: 0;">
      <circle cx="40" cy="70" r="1.2" fill="#fff" opacity="0.8"></circle><circle cx="120" cy="40" r="1" fill="#fff" opacity="0.6"></circle><circle cx="300" cy="64" r="1.4" fill="#fff" opacity="0.85"></circle><circle cx="352" cy="120" r="1" fill="#fff" opacity="0.5"></circle><circle cx="70" cy="190" r="1.1" fill="#fff" opacity="0.6"></circle><circle cx="330" cy="210" r="1.2" fill="#fff" opacity="0.6"></circle><circle cx="210" cy="30" r="1" fill="#fff" opacity="0.5"></circle>
      <circle cx="195" cy="392" r="230" fill="#F5C46B" opacity="0.07"></circle><circle cx="195" cy="392" r="180" fill="#F5C46B" opacity="0.07"></circle>
      ''' + wheel + '''
      <path d="M0 380 C 80 360, 150 372, 210 376 S 330 356, 390 366 L 390 452 L 0 452 Z" fill="#1A3A5C"></path>
      <path d="M0 412 C 100 394, 190 404, 260 408 S 350 396, 390 402 L 390 452 L 0 452 Z" fill="#12304D"></path>
    </svg>
    <header style="position: relative; height: 56px; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; justify-content: space-between;">
      <span style="display: flex; align-items: center; gap: 8px; font-size: 21px; font-weight: 700; color: #F1F4FB;">''' + LOGO + '''Sārathi</span>
      <a href="PExplore.dc.html" aria-label="Search" style="width: 44px; height: 44px; display: grid; place-items: center; color: #F1F4FB;">''' + SEARCH + '''</a>
    </header>
    <div style="position: relative; padding: 18px 20px 0; display: flex; flex-direction: column; gap: 12px; text-align: center;">
      <p style="margin: 0; font-size: 15px; font-weight: 600; color: #C7D1EA;">Namaste. Good evening.</p>
      <h1 style="margin: 0; font-size: 36px; line-height: 1.06; font-weight: 800; letter-spacing: -0.03em;">What’s on your mind?</h1>
      <a href="PAsk.dc.html" style="margin-top: 6px; display: flex; align-items: center; gap: 8px; height: 56px; box-sizing: border-box; padding: 0 6px 0 18px; background: #FFFFFF; border-radius: 18px; text-decoration: none; box-shadow: 0 18px 40px -18px rgba(5,10,30,0.7);"><span style="flex-grow: 1; text-align: left; font-size: 17px; color: #7A8790;">Tell me what happened…</span><span style="width: 44px; height: 44px; border-radius: 13px; background: #0F5257; color: #FFFFFF; display: grid; place-items: center;">''' + ARROW + '''</span></a>
    </div>
  </section>
  <div style="position: relative; margin-top: -34px; padding: 0 16px; display: flex; flex-direction: column; gap: 12px;">
    <a href="PVerse.dc.html" aria-label="Light your first lamp: verse 3.42" style="position: relative; overflow: hidden; display: flex; align-items: center; gap: 14px; padding: 18px 16px 18px 18px; border-radius: 22px; background: linear-gradient(135deg, #12383D 0%, #0F2E33 100%); border: 1px solid rgba(233,168,69,0.55); box-shadow: 0 18px 40px -20px rgba(15,46,51,0.8); text-decoration: none; color: #F4F1E6;">
      <span class="edge" aria-hidden="true" style="position: absolute; left: 0; right: 0; top: 0; height: 2px;"></span>
      <div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px;">
        <span style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;"><span style="color: #E9C77A;">Your journey</span><span style="color: #9FB7B4;">0 of 6 lit</span></span>
        <span style="font-size: 22px; font-weight: 800; letter-spacing: -0.01em;">Light your first lamp</span>
        <span style="font-size: 14.5px; color: #5D6B70;">Theme 1 · Exploring inner potential</span>
        <span style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">''' + lamp_next() + lamp(False, 24) * 5 + '''</span>
      </div>
      <span style="flex: none; width: 50px; height: 50px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(180deg, #F6C46A, #E39A35); color: #1C1204; box-shadow: 0 10px 22px -8px rgba(227,154,53,0.8);">''' + ARROW + '''</span>
    </a>
    <a href="PVerse.dc.html" style="display: flex; flex-direction: column; gap: 6px; padding: 14px 18px; border-radius: 20px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;">
      <span style="display: flex; align-items: center; justify-content: space-between;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Today’s verse · 2.47</span><span style="display: inline-flex; align-items: center; gap: 4px; font-size: 14px; font-weight: 700; color: #0F5257;">Read''' + CHEV_R + '''</span></span>
      <span style="font-family: Newsreader, Georgia, serif; font-size: 18px; line-height: 1.4;">“Your right is to the work alone, never to its fruits.”</span>
    </a>
  </div>
''' + tabbar("ask") + '\n</div>'
save("PHome.dc.html", page("Home", home))

# ---------------------------------------------------------------- 2. Ask (one artboard, four steps)
def opt_list(listname, handler):
    return ('<sc-for list="{{%s}}" as="o" hint-placeholder-count="5"><button type="button" onClick="{{o.go}}" style="display: flex; align-items: center; justify-content: space-between; width: 100%%; min-height: 58px; padding: 0 18px; border-radius: 16px; border: 1px solid #DDE6E8; background: #FFFFFF; font: 600 18px Figtree, sans-serif; color: #1E2B3A; text-align: left;"><span>{{o.label}}</span><span style="color: #9AA3A6;">%s</span></button></sc-for>' % (listname, CHEV_R))

ask = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <header style="height: 56px; box-sizing: border-box; padding: 0 8px; display: flex; align-items: center; gap: 4px;">
    <sc-if value="{{atStart}}" hint-placeholder-val="{{true}}"><a href="PHome.dc.html" aria-label="Back to home" style="width: 44px; height: 44px; display: grid; place-items: center; color: #1E2B3A;">''' + CHEV_L + '''</a></sc-if>
    <sc-if value="{{notStart}}" hint-placeholder-val="{{false}}"><button type="button" onClick="{{back}}" aria-label="Back" style="width: 44px; height: 44px; border: 0; background: none; display: grid; place-items: center; color: #1E2B3A;">''' + CHEV_L + '''</button></sc-if>
    <span style="flex-grow: 1; font-size: 15px; font-weight: 700; color: #5D6B70;">{{stepLabel}}</span>
    <span style="display: flex; gap: 6px; padding-right: 12px;"><span style="width: 22px; height: 5px; border-radius: 9px; background: {{d1}};"></span><span style="width: 22px; height: 5px; border-radius: 9px; background: {{d2}};"></span><span style="width: 22px; height: 5px; border-radius: 9px; background: {{d3}};"></span></span>
  </header>
  <main style="position: absolute; left: 0; right: 0; top: 56px; bottom: 84px; overflow-y: auto; padding: 8px 16px 20px; box-sizing: border-box;">
    <sc-if value="{{isWho}}" hint-placeholder-val="{{true}}"><div style="display: flex; flex-direction: column; gap: 10px;">
      <h1 style="margin: 4px 0 6px; font-size: 30px; line-height: 1.1; font-weight: 800; letter-spacing: -0.02em;">Where is this happening?</h1>
      ''' + opt_list("who", "go") + '''
    </div></sc-if>
    <sc-if value="{{isFeel}}" hint-placeholder-val="{{false}}"><div style="display: flex; flex-direction: column; gap: 10px;">
      <h1 style="margin: 4px 0 6px; font-size: 30px; line-height: 1.1; font-weight: 800; letter-spacing: -0.02em;">How are you feeling?</h1>
      <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px;"><sc-for list="{{feel}}" as="o" hint-placeholder-count="6"><button type="button" onClick="{{o.go}}" style="min-height: 76px; border-radius: 18px; border: 1px solid #DDE6E8; background: #FFFFFF; font: 700 19px Figtree, sans-serif; color: #1E2B3A;">{{o.label}}</button></sc-for></div>
    </div></sc-if>
    <sc-if value="{{isSit}}" hint-placeholder-val="{{false}}"><div style="display: flex; flex-direction: column; gap: 10px;">
      <h1 style="margin: 4px 0 6px; font-size: 30px; line-height: 1.1; font-weight: 800; letter-spacing: -0.02em;">Which is closest?</h1>
      ''' + opt_list("sit", "go") + '''
    </div></sc-if>
    <sc-if value="{{isAns}}" hint-placeholder-val="{{false}}"><div style="display: flex; flex-direction: column; gap: 14px;">
      <p style="margin: 0; font-size: 15px; color: #5D6B70;">I argued with a coworker</p>
      <article style="padding: 20px 18px; border-radius: 22px; background: linear-gradient(180deg, #0F2E33, #0B2428); color: #F4F1E6; display: flex; flex-direction: column; gap: 12px;">
        <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #E9C77A;">Krishna says · 2.63</span>
        <p lang="sa" style="margin: 0; font-family: 'Tiro Devanagari Sanskrit', serif; font-size: 21px; line-height: 1.6;">क्रोधाद्भवति संमोहः संमोहात्स्मृतिविभ्रमः\u00a0।</p>
        <p style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 19px; line-height: 1.45; text-wrap: pretty;">“Anger leads to delusion, delusion to loss of memory, and from that, good judgement is lost.”</p>
        <p style="margin: 0; font-size: 15.5px; line-height: 1.5; color: #C9D8D5;">Replaying the fight keeps it burning. Let the anger cool before you decide anything.</p>
        <div style="display: flex; gap: 10px;"><button type="button" style="display: inline-flex; align-items: center; gap: 8px; height: 44px; padding: 0 16px; border-radius: 999px; border: 0; background: #F4F1E6; color: #0B2428; font: 700 15px Figtree, sans-serif;">''' + PLAY + '''Listen</button><a href="PVerse.dc.html" style="display: inline-flex; align-items: center; height: 44px; padding: 0 16px; border-radius: 999px; border: 1px solid rgba(244,241,230,0.35); color: #F4F1E6; text-decoration: none; font-size: 15px; font-weight: 700;">Read in full</a></div>
      </article>
      <div style="padding: 16px 18px; border-radius: 18px; background: #E3F1EE; border: 1px solid #BFDDD7; display: flex; flex-direction: column; gap: 6px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Try today</span><span style="font-size: 17px; line-height: 1.45; font-weight: 600;">Write the reply you want to send. Sleep on it before you send it.</span></div>
      <div style="padding: 16px 18px; border-radius: 18px; background: #FFFFFF; border: 1px solid #DDE6E8; display: flex; flex-direction: column; gap: 6px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Ask yourself</span><span style="font-family: Newsreader, Georgia, serif; font-size: 18px; line-height: 1.45;">What do I actually need from this person?</span></div>
      <button type="button" onClick="{{restart}}" style="align-self: center; margin-top: 4px; height: 44px; padding: 0 18px; border: 0; background: none; color: #0F5257; font: 700 15px Figtree, sans-serif; text-decoration: underline;">Ask about something else</button>
    </div></sc-if>
  </main>
''' + tabbar("ask") + '\n</div>'
ask_js = """renderVals() {
    const s = this.state.step || 'who';
    const go = (n) => () => this.setState({ step: n });
    const order = ['who', 'feel', 'sit', 'ans'];
    const i = order.indexOf(s);
    const on = '#0F5257', off = '#CBD6D9';
    return {
      isWho: s === 'who', isFeel: s === 'feel', isSit: s === 'sit', isAns: s === 'ans',
      atStart: s === 'who', notStart: s !== 'who',
      stepLabel: s === 'ans' ? 'Krishna’s answer' : 'Step ' + (i + 1) + ' of 3',
      d1: i >= 0 ? on : off, d2: i >= 1 ? on : off, d3: i >= 2 ? on : off,
      who: ['Studies', 'At work', 'Family', 'Relationships', 'Just me'].map((l) => ({ label: l, go: go('feel') })),
      feel: ['Angry', 'Anxious', 'Low', 'Hurt', 'Stuck', 'Afraid'].map((l) => ({ label: l, go: go('sit') })),
      sit: ['I argued with a coworker', 'Someone took credit for my work', 'My boss criticised me', 'I feel stuck in my job'].map((l) => ({ label: l, go: go('ans') })),
      back: () => this.setState({ step: order[Math.max(0, i - 1)] }),
      restart: () => this.setState({ step: 'who' })
    };
  }"""
save("PAsk.dc.html", page("Ask", ask, script_body=ask_js))

# ---------------------------------------------------------------- 3. Learn
themes = ["Exploring inner potential", "Mastering your faculties", "Habit formation", "The three gunas", "From demoniac to divine", "Self mastery", "Regulation of mind", "Joyful actions"]
COUNTS = [6, 6, 6, 6, 6, 7, 6, 6]  # verses per theme, from the site data (theme 6 has 7; theme 12 has 5)
rows = []
for i, t in enumerate(themes):
    href = ' href="PVerse.dc.html"' if i == 0 else ' href="#"'
    rows.append('<a%s style="display: flex; align-items: center; gap: 14px; min-height: 64px; padding: 0 14px; border-radius: 16px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;">'
                '<span style="flex: none; width: 34px; height: 34px; border-radius: 999px; display: grid; place-items: center; background: %s; color: %s; font-size: 15px; font-weight: 800;">%d</span>'
                '<span style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;"><span style="font-size: 17px; font-weight: 700;">%s</span><span style="font-size: 13.5px; color: #67777C;">%s</span></span>'
                '<span style="color: #9AA3A6;">%s</span></a>' % (href, "#FBE9C6" if i == 0 else "#E6EEF0", "#8A5A12" if i == 0 else "#5D6B70", i + 1, t, "Start here · 6 verses" if i == 0 else "0 of %d lit" % COUNTS[i], CHEV_R))
learn = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <main style="position: absolute; left: 0; right: 0; top: 0; bottom: 84px; overflow-y: auto; padding: 20px 16px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">
    <div style="display: flex; flex-direction: column; gap: 6px; padding-top: 12px;"><h1 style="margin: 0; font-size: 32px; line-height: 1.08; font-weight: 800; letter-spacing: -0.02em;">Learn by heart</h1><p style="margin: 0; font-size: 16.5px; line-height: 1.45; color: #5D6B70;">20 themes, a few verses each. A lamp lights for every verse you can recite.</p></div>
    <a href="PVerse.dc.html" style="position: relative; overflow: hidden; display: flex; align-items: center; gap: 14px; padding: 18px; border-radius: 22px; background: linear-gradient(135deg, #0F2E33, #154045); color: #F4F1E6; text-decoration: none; box-shadow: 0 18px 40px -22px rgba(15,82,87,0.8);">
      <span class="edge" aria-hidden="true" style="position: absolute; left: 0; right: 0; top: 0; height: 2px;"></span>
      <div style="flex-grow: 1; display: flex; flex-direction: column; gap: 6px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #E9C77A;">Next up · verse 3.42</span><span style="font-size: 21px; font-weight: 800;">Exploring inner potential</span><span style="display: flex; align-items: center; gap: 6px;">''' + lamp_next() + lamp(False, 24) * 5 + '''</span></div>
      <span style="flex: none; width: 50px; height: 50px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(180deg, #F6C46A, #E39A35); color: #1C1204;">''' + ARROW + '''</span>
    </a>
    <h2 style="margin: 8px 0 0; font-size: 13px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #67777C;">All themes</h2>
    <div style="display: flex; flex-direction: column; gap: 8px;">''' + "".join(rows) + '''</div>
  </main>
''' + tabbar("learn") + '\n</div>'
save("PLearn.dc.html", page("Learn", learn))

# The verse's connections (live data for 3.42 from build/graph_data.py), drawn as a thread:
# the verse at the top, one line down through plain-worded stops. Tap a word, its "why" opens under it.
# kind -> (dot, label and line colour, chip tint); dark.py lightens these colours.
KIND = {"speaks": ("#B4533A", "rgba(180,83,58,0.10)"), "cultivates": ("#1F7A7A", "rgba(31,122,122,0.10)"),
        "helps": ("#A8801A", "rgba(201,162,39,0.14)"), "verse": ("#0F5257", "rgba(15,82,87,0.08)"),
        "chain": ("#A8801A", "rgba(201,162,39,0.12)"), "idea": ("#4B5AA8", "rgba(75,90,168,0.10)")}
SA = '<span lang="sa" style="font-family: \'Tiro Devanagari Sanskrit\', serif; font-weight: 400; font-size: 17px;">%s</span> '
VMAP = [  # id, stop, kind, name (html), why (JS string, ASCII escapes)
    ("rest", "feel", "speaks", "Restlessness", "It speaks to restlessness: a mind that will not settle."),
    ("mind", "feel", "helps", "My mind won&#8217;t settle", "Ask brings you here when your mind won\\u2019t settle."),
    ("ctrl", "grow", "cultivates", "Self-control", "It builds self-control: the senses guided, not driving."),
    ("clar", "grow", "cultivates", "Clarity", "It builds clarity: seeing things as they are."),
    ("manas", "idea", "idea", SA % "मनस्" + "manas", "manas, the mind. Higher than the senses, lower than the intellect."),
    ("buddhi", "idea", "idea", SA % "बुद्धि" + "buddhi", "buddhi, the intellect that discerns and decides for the mind."),
    ("atman", "idea", "idea", SA % "आत्मन्" + "ātman", "\\u0101tman, the Self, beyond the intellect and beyond desire\\u2019s reach."),
]
STOPS = [("feel", "speaks", "Reach for it when"), ("grow", "cultivates", "What it grows in you"), ("idea", "idea", "Ideas inside it")]
LADDER = [("Body", "3.42"), ("Senses", "3.42"), ("Mind", "3.42"), ("Intellect", "3.42"), ("The Self", "3.42"), ("Master desire", "3.43")]


def _stop(kind, title, inner, last=False):
    col = KIND[kind][0]
    seg = '' if last else '<span aria-hidden="true" style="position: absolute; left: 17px; top: 10px; bottom: -10px; width: 2px; background: %s; opacity: 0.6;"></span>' % col
    return ('<div style="position: relative; padding: 0 0 %dpx 44px;">' + seg +
            '<span aria-hidden="true" style="position: absolute; left: 11px; top: 3px; width: 14px; height: 14px; border-radius: 999px; background: %s; box-shadow: 0 0 0 4px rgba(233,168,69,0.12), 0 0 0 1px rgba(255,255,255,0.5);"></span>'
            '<h3 style="margin: 0 0 10px; font-size: 16px; font-weight: 800; color: #1E2B3A;">%s</h3>%s</div>') % (4 if last else 22, col, title, inner)


def verse_map():
    stops = []
    for sid, kind, title in STOPS:
        chips = []
        for nid, st, k, name, _ in VMAP:
            if st != sid:
                continue
            col, tint = KIND[k]
            chips.append('<button type="button" onClick="{{p_%s}}" aria-pressed="{{a_%s}}" style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 14px; border-radius: 999px; border: 1.5px solid %s; background: #FFFFFF; background-image: linear-gradient(%s, %s); box-shadow: {{r_%s}}; font: 700 16px Figtree, sans-serif; color: #1E2B3A;">'
                         '<span aria-hidden="true" style="width: 8px; height: 8px; border-radius: 999px; background: %s; flex: none;"></span>%s</button>' % (nid, nid, col, tint, tint, nid, col, name))
        inner = ('<div style="display: flex; flex-wrap: wrap; gap: 8px;">' + "".join(chips) + '</div>'
                 '<sc-if value="{{s_%s}}" hint-placeholder-val="{{false}}"><p aria-live="polite" style="margin: 10px 0 0; padding: 10px 14px; border-radius: 14px; border-left: 3px solid #E9A845; background: rgba(233,168,69,0.10); font-family: Newsreader, Georgia, serif; font-size: 17px; line-height: 1.4; color: #2F3C42; text-wrap: pretty;">{{y_%s}}</p></sc-if>' % (sid, sid))
        stops.append(_stop(kind, title, inner))
    nxt = ('<a href="PVerse.dc.html" style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 16px; background: #FFFFFF; border: 1.5px solid #0F5257; text-decoration: none; color: #1E2B3A;">'
           '<span style="flex: none; font-size: 20px; font-weight: 800; color: #0F5257;">3.43</span>'
           '<span style="flex-grow: 1; font-family: Newsreader, Georgia, serif; font-size: 17px; line-height: 1.35;">Knowing the Self above the intellect, master desire.</span>' + CHEV_R + '</a>')
    stops.append(_stop("verse", "Where it leads", nxt))
    steps = []
    for i, (n, v) in enumerate(LADDER):
        here = v == "3.42"
        steps.append('<span style="display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 10px; font-size: 15px; font-weight: 700; %s">%s</span>'
                     % ("background: rgba(201,162,39,0.16); color: #1E2B3A;" if here else "border: 1.5px dashed #A8801A; color: #A8801A;", n))
        if i < len(LADDER) - 1:
            steps.append('<span aria-hidden="true" style="color: #A8801A; font-weight: 800;">&#8250;</span>')
    chain = ('<div style="display: flex; flex-direction: column; gap: 10px; padding: 14px; border-radius: 16px; background: #FFFFFF; border: 1px dashed #A8801A;">'
             '<span style="display: flex; flex-direction: column; gap: 2px;"><span style="font-size: 17px; font-weight: 800;">The ladder of faculties</span><span style="font-size: 14.5px; color: #67777C;">What rules what, from body to Self.</span></span>'
             '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">' + "".join(steps) + '</div>'
             '<span style="font-size: 14px; color: #67777C;">Lit steps are this verse. The last step is 3.43.</span></div>')
    stops.append(_stop("chain", "Part of a chain", chain, last=True))
    return ('<section aria-label="Verse map: how 3.42 connects" style="display: flex; flex-direction: column; gap: 18px;">\n'
            '      <div style="display: flex; align-items: center; gap: 14px;">'
            '<span aria-hidden="true" style="flex: none; width: 64px; height: 64px; border-radius: 999px; background: radial-gradient(circle at 35% 30%, #1A4D52, #0B2A2E); box-shadow: 0 0 0 5px rgba(233,168,69,0.25), 0 0 24px 4px rgba(233,168,69,0.25); display: grid; place-items: center; font-size: 19px; font-weight: 800; color: #F6C46A;">3.42</span>'
            '<span style="display: flex; flex-direction: column; gap: 2px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Verse map</span>'
            '<span style="font-size: 20px; font-weight: 800; line-height: 1.2;">Where this verse connects</span><span style="font-size: 14.5px; color: #67777C;">Tap a word to see why.</span></span></div>\n'
            '      <div style="position: relative;">'
            '<span aria-hidden="true" style="position: absolute; left: 17px; top: -24px; height: 28px; width: 2px; background: #E9A845; opacity: 0.6;"></span>'
            + "".join(stops) + '</div>\n'
            '      <a href="PMap.dc.html" style="display: flex; align-items: center; justify-content: space-between; min-height: 52px; padding: 0 16px; border-radius: 14px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;"><span style="font-size: 16px; font-weight: 700;">See the whole map</span>' + CHEV_R + '</a>\n'
            '    </section>')


# ---------------------------------------------------------------- 4. Verse 3.42
words = [("indriyāṇi", "the senses"), ("parāṇi", "higher"), ("āhuḥ", "they say"), ("indriyebhyaḥ", "than the senses"), ("param", "higher"), ("manaḥ", "the mind"),
         ("manasaḥ", "than the mind"), ("tu", "but"), ("parā", "higher"), ("buddhiḥ", "the intellect"), ("yaḥ", "who"), ("buddheḥ", "than the intellect"), ("parataḥ", "beyond"), ("saḥ", "He, the Self")]
wchips = "".join('<span style="display: inline-flex; flex-direction: column; padding: 8px 12px; border-radius: 12px; background: #FFFFFF; border: 1px solid #DDE6E8;"><span style="font-size: 15.5px; font-weight: 700; color: #0F5257;">%s</span><span style="font-size: 13.5px; color: #5D6B70;">%s</span></span>' % w for w in words)
ladder = [("Body", "gross, outer", "#DDE6E8"), ("Senses", "finer than the body", "#E0D7C4"), ("Mind", "directs the senses", "#D3C7AE"), ("Intellect", "decides for the mind", "#EBC27A"), ("The Self", "beyond them all", "#E9A845")]
lad = "".join('<div style="display: flex; align-items: center; gap: 12px; margin-left: %dpx; padding: 10px 14px; border-radius: 14px; background: %s;"><span style="font-size: 16px; font-weight: 800; color: #1E2B3A; width: 84px;">%s</span><span style="font-size: 14px; color: #3D4A50;">%s</span></div>' % (i * 12, c, n, d) for i, (n, d, c) in enumerate(ladder))
lamps_strip = '<span style="display: flex; align-items: center; gap: 4px;">' + lamp_next(18, 28) + lamp(False, 18) * 5 + '</span>'
THEME_ROW = '\n    <section aria-label="Verses in Theme 1" style="display: flex; flex-direction: column; gap: 10px; padding: 16px; border-radius: 20px; background: #FFFFFF; border: 1px solid #DDE6E8;">\n      <div style="display: flex; align-items: baseline; justify-content: space-between;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">In Theme 1 · 6 verses</span><a href="PLearn.dc.html" style="font-size: 14px; font-weight: 700;">See theme</a></div>\n      <div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px;"><a href="PVerse.dc.html" aria-label="Verse 3.42" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #1E2B3A; font-size: 13px; font-weight: 700; background: #E3F1EE; box-shadow: inset 0 0 0 1.5px #0F5257;">{LAMP}3.42</a><a href="PVerse.dc.html" aria-label="Verse 3.43" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #67777C; font-size: 13px; font-weight: 700; ">{LAMP}3.43</a><a href="PVerse.dc.html" aria-label="Verse 7.4" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #67777C; font-size: 13px; font-weight: 700; ">{LAMP}7.4</a><a href="PVerse.dc.html" aria-label="Verse 7.5" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #67777C; font-size: 13px; font-weight: 700; ">{LAMP}7.5</a><a href="PVerse.dc.html" aria-label="Verse 13.5" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #67777C; font-size: 13px; font-weight: 700; ">{LAMP}13.5</a><a href="PVerse.dc.html" aria-label="Verse 13.6" style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 6px 0; border-radius: 12px; text-decoration: none; color: #67777C; font-size: 13px; font-weight: 700; ">{LAMP}13.6</a></div>\n      <a href="PLearn.dc.html" style="display: flex; align-items: center; justify-content: space-between; min-height: 48px; padding: 0 14px; border-radius: 14px; background: #F2F6F7; text-decoration: none; color: #1E2B3A;"><span style="font-size: 15px;"><span style="color: #67777C;">Also in</span> <b>Theme 2 · Mastering your faculties</b></span>CHEVR</a>\n    </section>'.replace('{LAMP}', lamp(False, 20)).replace('CHEVR', CHEV_R)
verse = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <header style="position: absolute; left: 0; right: 0; top: 0; z-index: 4; height: 56px; box-sizing: border-box; padding: 0 12px 0 4px; display: flex; align-items: center; gap: 4px; background: rgba(242,246,247,0.96); border-bottom: 1px solid #DDE6E8;">
    <a href="PLearn.dc.html" aria-label="Back to Learn" style="width: 44px; height: 44px; display: grid; place-items: center; color: #1E2B3A;">''' + CHEV_L + '''</a>
    <span style="flex-grow: 1; display: flex; flex-direction: column;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #9A6313;">Theme 1 · 1 of 6</span><span style="font-size: 15px; font-weight: 700;">Exploring inner potential</span></span>
    ''' + lamps_strip + '''
  </header>
  <main style="position: absolute; left: 0; right: 0; top: 56px; bottom: 156px; overflow-y: auto; padding: 18px 18px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px;">
    <span style="font-size: 13px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #67777C;">Bhagavad Gita 3.42</span>
    <p lang="sa" style="margin: 0; font-family: 'Tiro Devanagari Sanskrit', serif; font-size: 25px; line-height: 1.6; color: #1E2B3A; text-wrap: balance;">इन्द्रियाणि पराण्याहुरिन्द्रियेभ्यः परं मनः\u00a0।<br>मनसस्तु परा बुद्धिर्यो बुद्धेः परतस्तु सः\u00a0॥</p>
    <div style="display: flex; align-items: center; gap: 10px;">
      <button type="button" aria-label="Play the chant" style="width: 48px; height: 48px; flex: none; border-radius: 999px; border: 0; background: #0F5257; color: #FFFFFF; display: grid; place-items: center;">''' + PLAY + '''</button>
      <span style="flex-grow: 1; height: 4px; border-radius: 9px; background: #DDE6E8;"></span>
      <span style="font-size: 14px; font-weight: 700; color: #5D6B70;">Chant · 0:34</span>
    </div>
    <div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Say it</span>
      <p style="margin: 0; font-size: 18px; line-height: 1.55; color: #2F3C42; text-wrap: balance;">indriyāṇi parāṇy āhur indriyebhyaḥ paraṁ manaḥ<br>manasas tu parā buddhir yo buddheḥ paratas tu saḥ</p></div>
    <div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #0F5257;">Meaning</span>
      <p style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 21px; line-height: 1.45; text-wrap: pretty;">The senses are higher than the body, the mind is higher than the senses, the intellect is higher than the mind, and the Self is higher still.</p></div>
THEMEROW
    <div role="tablist" aria-label="Go deeper" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); padding: 4px; border-radius: 999px; background: #E6EEF0; margin-top: 4px;">
      <sc-for list="{{tabs}}" as="t" hint-placeholder-count="3"><button type="button" role="tab" aria-selected="{{t.sel}}" onClick="{{t.pick}}" style="height: 40px; border: 0; border-radius: 999px; background: {{t.bg}}; color: {{t.fg}}; font: 700 15px Figtree, sans-serif; box-shadow: {{t.sh}};">{{t.label}}</button></sc-for>
    </div>
    <sc-if value="{{showWords}}" hint-placeholder-val="{{true}}"><div style="display: flex; flex-wrap: wrap; gap: 8px;">''' + wchips + '''</div></sc-if>
    <sc-if value="{{showExplain}}" hint-placeholder-val="{{false}}"><div style="display: flex; flex-direction: column; gap: 8px;"><p style="margin: 0 0 4px; font-size: 16.5px; line-height: 1.5; color: #2F3C42;">Krishna names a ladder inside us. Each step is finer and steers the one below. Desire can rule the senses, mind and intellect, but it can’t reach the Self at the top.</p>''' + lad + '''<span style="font-size: 13.5px; color: #67777C;">From Swami Sivananda’s commentary</span></div></sc-if>
    <sc-if value="{{showLinks}}" hint-placeholder-val="{{false}}">''' + verse_map() + '''</sc-if>
  </main>
  <div style="position: absolute; left: 0; right: 0; bottom: 84px; z-index: 4; padding: 12px 16px; box-sizing: border-box; height: 72px; display: flex; gap: 10px; background: linear-gradient(180deg, rgba(242,246,247,0), #F2F6F7 30%);">
    <a href="PPractice.dc.html" style="flex-grow: 1; display: flex; align-items: center; justify-content: center; gap: 10px; border-radius: 999px; background: linear-gradient(180deg, #F6C46A, #E39A35); color: #1C1204; text-decoration: none; font-size: 17px; font-weight: 800; box-shadow: 0 12px 26px -10px rgba(227,154,53,0.8);">''' + MIC.format(s=20) + '''Learn it by heart</a>
    <a href="PVerse.dc.html" aria-label="Next verse in this theme, 3.43" style="flex: none; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 16px; border-radius: 999px; background: #FFFFFF; border: 1px solid #DDE6E8; color: #1E2B3A; text-decoration: none; line-height: 1.1;"><span style="font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #5D6B70;">Next</span><span style="font-size: 15px; font-weight: 800;">3.43 ›</span></a>
  </div>
''' + tabbar("learn") + '\n</div>'
verse_js = """renderVals() {
    const tab = this.state.tab || 'words';
    const sel = this.state.sel || '';
    const WHY = WHYJSON;
    const STOP = STOPJSON;
    const node = {};
    Object.keys(WHY).forEach((k) => {
      const on = sel === k;
      node['p_' + k] = () => this.setState({ sel: on ? '' : k });
      node['a_' + k] = on ? 'true' : 'false';
      node['r_' + k] = on ? '0 0 0 3px rgba(233,168,69,0.6)' : 'none';
    });
    ['feel', 'grow', 'idea'].forEach((st) => {
      node['s_' + st] = !!sel && STOP[sel] === st;
      node['y_' + st] = sel ? WHY[sel] : '';
    });
    const mk = (id, label) => ({ label, sel: tab === id ? 'true' : 'false', bg: tab === id ? '#FFFFFF' : 'transparent', fg: tab === id ? '#1E2B3A' : '#5D6B70', sh: tab === id ? '0 2px 6px rgba(30,43,58,0.12)' : 'none', pick: () => this.setState({ tab: id }) });
    return {
      tabs: [mk('words', 'Words'), mk('explain', 'Explained'), mk('links', 'Connected')],
      showWords: tab === 'words', showExplain: tab === 'explain', showLinks: tab === 'links',
      ...node
    };
  }"""
verse = verse.replace('THEMEROW', THEME_ROW)
verse_js = verse_js.replace('WHYJSON', '{ ' + ', '.join("%s: '%s'" % (v[0], v[4]) for v in VMAP) + ' }').replace('STOPJSON', '{ ' + ', '.join("%s: '%s'" % (v[0], v[1]) for v in VMAP) + ' }')
save("PVerse.dc.html", page("Verse 3.42", verse, script_body=verse_js))

# ---------------------------------------------------------------- 5. Practice (focus mode)
sa_words = ["इन्द्रियाणि", "पराण्याहुरिन्द्रियेभ्यः", "परं", "मनः\u00a0।",
            "मनसस्तु", "परा", "बुद्धिर्यो", "बुद्धेः", "परतस्तु", "सः\u00a0॥"]
close_idx = {6}
word_items = json.dumps([{"w": w, "close": i in close_idx} for i, w in enumerate(sa_words)])
practice = '<div style="' + FRAME % ("#0B2226", "#F4F1E6") + '">' + '''
  <header style="height: 60px; box-sizing: border-box; padding: 0 12px 0 4px; display: flex; align-items: center; gap: 6px;">
    <a href="PVerse.dc.html" aria-label="Close" style="width: 44px; height: 44px; display: grid; place-items: center; color: #F4F1E6;"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"></path></svg></a>
    <span style="flex-grow: 1; font-size: 16px; font-weight: 700;">Recite 3.42</span>
    <span style="display: flex; align-items: center; gap: 3px;"><sc-if value="{{lit}}" hint-placeholder-val="{{false}}">''' + lamp(True, 18) + '''</sc-if><sc-if value="{{unlit}}" hint-placeholder-val="{{true}}">''' + lamp_next(16, 26) + '''</sc-if>''' + lamp(False, 16) * 5 + '''</span>
  </header>
  <main style="position: absolute; left: 0; right: 0; top: 60px; bottom: 236px; overflow-y: auto; padding: 22px 20px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; gap: 18px;">
    <p lang="sa" style="margin: 0; font-family: 'Tiro Devanagari Sanskrit', serif; font-size: 28px; line-height: 1.75; text-align: center; text-wrap: balance;"><sc-for list="{{words}}" as="w" hint-placeholder-count="10"><span style="padding: 0 3px; border-radius: 6px; {{w.style}}">{{w.w}}</span> </sc-for></p>
    <sc-if value="{{showSay}}" hint-placeholder-val="{{true}}"><p style="margin: 0; font-size: 17px; line-height: 1.55; text-align: center; color: #B9CBC8; text-wrap: balance;">indriyāṇi parāṇy āhur indriyebhyaḥ paraṁ manaḥ<br>manasas tu parā buddhir yo buddheḥ paratas tu saḥ</p></sc-if>
    <button type="button" onClick="{{toggleSay}}" style="align-self: center; height: 40px; padding: 0 16px; border-radius: 999px; border: 1px solid rgba(244,241,230,0.25); background: none; color: #F4F1E6; font: 600 14.5px Figtree, sans-serif;">{{sayLabel}}</button>
  </main>
  <section style="position: absolute; left: 0; right: 0; bottom: 0; height: 236px; box-sizing: border-box; padding: 16px 20px 30px; border-radius: 26px 26px 0 0; background: #FFFFFF; color: #1E2B3A; display: flex; flex-direction: column; align-items: center; gap: 12px;">
    <sc-if value="{{isIdle}}" hint-placeholder-val="{{true}}"><p style="margin: 0; font-size: 16px; font-weight: 600; color: #5D6B70; text-align: center;">Listen once, then say the whole verse from memory.</p></sc-if>
    <sc-if value="{{isListening}}" hint-placeholder-val="{{false}}"><p style="margin: 0; font-size: 16px; font-weight: 700; color: #0F5257; text-align: center;">Listening… tap again when you finish</p></sc-if>
    <sc-if value="{{isResult}}" hint-placeholder-val="{{false}}"><div style="display: flex; align-items: center; gap: 10px; padding: 8px 14px; border-radius: 999px; background: #E3F1EE; border: 1px solid #BFDDD7;">''' + lamp(True, 20) + '''<span style="font-size: 15.5px; font-weight: 800; color: #0B3F43;">Lamp lit · 9 of 10 words clear</span></div></sc-if>
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; width: 100%; gap: 12px;">
      <button type="button" style="justify-self: start; display: flex; flex-direction: column; align-items: center; gap: 4px; border: 0; background: none; color: #1E2B3A; font: 700 13.5px Figtree, sans-serif;"><span style="width: 56px; height: 56px; border-radius: 999px; display: grid; place-items: center; background: #FFFFFF; border: 1px solid #DDE6E8;">''' + PLAY + '''</span>Listen</button>
      <button type="button" onClick="{{tapMic}}" aria-label="{{micLabel}}" style="position: relative; width: 96px; height: 96px; border-radius: 999px; border: 0; background: {{micBg}}; color: #FFFFFF; display: grid; place-items: center; box-shadow: 0 14px 30px -10px rgba(15,82,87,0.7);">
        <sc-if value="{{isListening}}" hint-placeholder-val="{{false}}"><span class="ring" aria-hidden="true" style="position: absolute; inset: 0; border-radius: 999px; border: 3px solid #1F7A72;"></span><span class="ring2" aria-hidden="true" style="position: absolute; inset: 0; border-radius: 999px; border: 3px solid #1F7A72;"></span></sc-if>
        ''' + MIC.format(s=34) + '''
      </button>
      <sc-if value="{{isResult}}" hint-placeholder-val="{{false}}"><a href="PVerse.dc.html" style="justify-self: end; display: flex; flex-direction: column; align-items: center; gap: 4px; text-decoration: none; color: #1E2B3A; font-size: 13.5px; font-weight: 700;"><span style="width: 56px; height: 56px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(180deg, #F6C46A, #E39A35); color: #1C1204;">''' + ARROW + '''</span>Next: 3.43</a></sc-if>
      <sc-if value="{{notResult}}" hint-placeholder-val="{{true}}"><button type="button" style="justify-self: end; display: flex; flex-direction: column; align-items: center; gap: 4px; border: 0; background: none; color: #5D6B70; font: 700 13.5px Figtree, sans-serif;"><span style="width: 56px; height: 56px; border-radius: 999px; display: grid; place-items: center; background: #FFFFFF; border: 1px solid #DDE6E8;"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"></path><circle cx="16" cy="7" r="2"></circle><circle cx="10" cy="17" r="2"></circle></svg></span>Options</button></sc-if>
    </div>
    <span style="font-size: 14px; font-weight: 700; color: #0F5257;">{{micText}}</span>
  </section>
</div>'''
practice_js = """renderVals() {
    const m = this.state.mode || 'idle';
    const say = this.state.say !== false;
    const words = %s.map((x) => ({ w: x.w, style: m === 'result' ? (x.close ? 'background: rgba(233,168,69,0.35); color: #FFE6B0;' : 'background: rgba(31,122,114,0.45); color: #FFFFFF;') : '' }));
    return {
      words,
      isIdle: m === 'idle', isListening: m === 'listening', isResult: m === 'result', notResult: m !== 'result',
      lit: m === 'result', unlit: m !== 'result',
      micBg: m === 'listening' ? '#B04A3A' : '#0F5257',
      micLabel: m === 'listening' ? 'Stop' : 'Recite',
      micText: m === 'idle' ? 'Tap to recite' : (m === 'listening' ? 'Tap to stop' : 'Recite again'),
      showSay: say, sayLabel: say ? 'Hide how to say it' : 'Show how to say it',
      toggleSay: () => this.setState({ say: !say }),
      tapMic: () => this.setState({ mode: m === 'idle' ? 'listening' : (m === 'listening' ? 'result' : 'listening') })
    };
  }""" % word_items
save("PPractice.dc.html", page("Practice 3.42", practice, script_body=practice_js))

# ---------------------------------------------------------------- 6. Explore
def tile(title, sub, chips, bg, fg, href):
    ch = "".join('<span style="padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,0.55); font-size: 13.5px; font-weight: 600;">%s</span>' % c for c in chips)
    return ('<a href="%s" style="display: flex; flex-direction: column; gap: 8px; padding: 18px; border-radius: 22px; background: %s; color: %s; text-decoration: none;">'
            '<span style="display: flex; align-items: center; justify-content: space-between;"><span style="font-size: 22px; font-weight: 800;">%s</span>%s</span>'
            '<span style="font-size: 15px; line-height: 1.4; opacity: 0.85;">%s</span><span style="display: flex; flex-wrap: wrap; gap: 6px;">%s</span></a>' % (href, bg, fg, title, CHEV_R, sub, ch))
MAP_ART = ('<svg width="92" height="84" viewBox="0 0 92 84" aria-hidden="true" style="flex: none;">'
           '<g fill="none" stroke-width="1.3" opacity="0.7"><path d="M46 42 Q30 20 14 16" stroke="#E59A84"></path><path d="M46 42 Q64 18 80 14" stroke="#E9C77A"></path>'
           '<path d="M46 42 Q24 44 10 52" stroke="#7FCFC4"></path><path d="M46 42 Q70 46 84 50" stroke="#86CDC2"></path><path d="M46 42 Q40 62 26 74" stroke="#AEB8F0"></path>'
           '<path d="M46 42 Q56 64 66 74" stroke="#AEB8F0"></path><path d="M14 16 Q12 34 10 52" stroke="#9DB6B3" stroke-dasharray="3 3"></path></g>'
           '<circle cx="14" cy="16" r="4.5" fill="#E59A84"></circle><circle cx="80" cy="14" r="4.5" fill="#E9C77A"></circle><circle cx="10" cy="52" r="4" fill="#7FCFC4"></circle>'
           '<circle cx="84" cy="50" r="4" fill="#86CDC2"></circle><circle cx="26" cy="74" r="3.5" fill="#AEB8F0"></circle><circle cx="66" cy="74" r="3.5" fill="#AEB8F0"></circle>'
           '<circle cx="46" cy="42" r="15" fill="rgba(233,168,69,0.18)"></circle><circle cx="46" cy="42" r="9" fill="#F6C46A"></circle></svg>')
MAP_CARD = ('<a href="PMap.dc.html" style="display: flex; align-items: center; gap: 14px; padding: 16px 16px 16px 14px; border-radius: 22px; background: linear-gradient(135deg, #123F44, #0A2B30); border: 1px solid rgba(233,168,69,0.35); color: #FFFFFF; text-decoration: none;">'
            + MAP_ART + '<span style="flex-grow: 1; display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 22px; font-weight: 800;">See the map</span>'
            '<span style="font-size: 15px; line-height: 1.4; color: #C9D8D5;">How feelings, verses and ideas connect. Find a path from one to another.</span></span>'
            '<span style="color: #F6C46A; display: grid;">' + CHEV_R + '</span></a>')
explore = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <main style="position: absolute; left: 0; right: 0; top: 0; bottom: 84px; overflow-y: auto; padding: 32px 16px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">
    <h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.02em;">Explore</h1>
    <label for="xs" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);">Search the Gita</label>
    <div style="display: flex; align-items: center; gap: 10px; height: 52px; padding: 0 16px; border-radius: 16px; background: #FFFFFF; border: 1px solid #DDE6E8; color: #5D6B70;">''' + SEARCH + '''<input id="xs" placeholder="Search a word, a verse, a feeling" style="flex-grow: 1; min-width: 0; border: 0; outline: none; background: transparent; font: 400 16.5px Figtree, sans-serif; color: #1E2B3A;"></div>
    ''' + MAP_CARD + '''
    ''' + tile("18 chapters", "Read the Gita in order, verse by verse.", ["1 Arjuna’s grief", "2 Knowledge", "3 Action", "+15"], "#DDEFEC", "#0B3F43", "PVerse.dc.html") + '''
    ''' + tile("Big ideas", "Words like dharma and karma, and every verse they appear in.", ["dharma", "karma", "ātman", "yoga", "+20"], "#E6EEFB", "#1F3A6E", "PVerse.dc.html") + '''
    ''' + tile("Feelings", "What the Gita says when you feel angry, afraid or low.", ["Anger", "Fear", "Grief", "Doubt", "+6"], "#EEE7F6", "#3E2C63", "PAsk.dc.html") + '''
  </main>
''' + tabbar("explore") + '\n</div>'
save("PExplore.dc.html", page("Explore", explore))

# ---------------------------------------------------------------- 7. The Gita map (opened from Explore and the verse map)
# Real data from build/graph_data.py: journey() per feeling and shortest paths from the live path finder.
JOURNEYS = {
    "restlessness": {"label": "Restlessness", "understand": ["2.60", "2.66", "3.42"], "practise": ["6.26", "6.5", "3.8", "13.8"],
                     "cures": [["Steadiness", "6.26", "Bring the wandering mind back, again and again"], ["Self-control", "2.61", "Restrain the senses and the mind grows steady"]]},
    "anger": {"label": "Anger", "understand": ["2.62", "2.63", "16.4"], "practise": ["16.3", "13.8", "16.2", "11.42"],
              "cures": [["Forgiveness", "16.3", "Forgiveness and freedom from malice are divine"]]},
    "fear": {"label": "Fear", "understand": ["2.56", "10.34", "12.15"], "practise": ["16.1", "12.16", "9.22", "13.5"],
             "cures": [["Fearlessness", "16.1", "Fearlessness heads the list of divine qualities"], ["Faith", "9.22", "The Lord carries what His devotee lacks"]]},
    "anxiety": {"label": "Anxiety", "understand": ["2.47", "2.48", "3.30"], "practise": ["15.5", "5.18", "2.56", "12.13"],
                "cures": [["Equanimity", "2.48", "Act, staying even in success and failure"], ["Non-attachment", "2.47", "The right is to the action, never to its fruits"]]},
    "craving": {"label": "Craving", "understand": ["2.62", "2.60", "3.43"], "practise": ["4.21", "17.8", "5.24", "12.14"],
                "cures": [["Contentment", "4.21", "Wanting nothing, one acts without being bound"], ["Inner joy", "5.21", "The joy within needs no outer objects"]]},
    "grief": {"label": "Grief", "understand": ["16.5", "2.56", "6.17"], "practise": ["13.5", "4.39", "15.4", "15.6"],
              "cures": [["Faith", "16.5", "Do not grieve: your nature is divine"]]},
    "doubt": {"label": "Doubt", "understand": ["4.39", "6.5", "16.5"], "practise": ["13.5", "15.4", "15.6", "18.56"],
              "cures": [["Faith", "4.39", "Faith, effort and self-control lead to knowledge"]]},
}
PATHS = {  # from the live path finder's weights; each step: from, relation, to, note
    "rp": ["Restlessness", "Peace", [["Restlessness", "is addressed in", "17.16", ""], ["17.16", "cultivates", "Peace", ""]]],
    "af": ["Anger", "Forgiveness", [["Anger", "is answered by", "Forgiveness", "Forgiveness and freedom from malice are divine (16.3)"]]],
    "ff": ["Fear", "Faith", [["Fear", "is answered by", "Faith", "The Lord carries what His devotee lacks (9.22)"]]],
    "vv": ["2.47", "18.56", [["2.47", "arrives at", "18.56", "Selfless action ends in grace"]]],
}
CHAINS = [("The ladder of fall", "How a passing thought becomes ruin.", ["Dwelling on objects", "Attachment", "Desire", "Anger", "Delusion", "Loss of memory", "Loss of reason", "Ruin"], "2.62&#8211;63", "#B4533A"),
          ("From senses to serenity", "Taming the senses step by step.", ["Senses pull the mind", "Restrain them", "Wisdom grows steady", "No like or dislike", "Serenity"], "2.60&#8211;64", "#1F7A7A"),
          ("The ladder of faculties", "What rules what, from body to Self.", ["Body", "Senses", "Mind", "Intellect", "The Self", "Master desire"], "3.42&#8211;43", "#A8801A")]
VPILL = '<a href="PVerse.dc.html" style="display: inline-flex; align-items: center; min-height: 40px; padding: 0 14px; border-radius: 12px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #0F5257; font-size: 16px; font-weight: 800;">{{v.n}}</a>'


def mstop(n, col, title, inner, last=False):
    seg = '' if last else '<span aria-hidden="true" style="position: absolute; left: 13px; top: 28px; bottom: -4px; width: 2px; background: %s; opacity: 0.5;"></span>' % col
    return ('<div style="position: relative; padding: 0 0 %dpx 42px;">%s'
            '<span aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 28px; height: 28px; border-radius: 999px; background: %s; color: #FFFFFF; display: grid; place-items: center; font-size: 14px; font-weight: 800;">%d</span>'
            '<h3 style="margin: 2px 0 10px; font-size: 17px; font-weight: 800;">%s</h3>%s</div>') % (4 if last else 20, seg, col, n, title, inner)


chain_cards = "".join(
    '<div style="display: flex; flex-direction: column; gap: 8px; padding: 14px 16px; border-radius: 18px; background: #FFFFFF; border: 1px solid #DDE6E8;">'
    '<span style="display: flex; align-items: baseline; justify-content: space-between; gap: 8px;"><span style="font-size: 17px; font-weight: 800;">%s</span><span style="flex: none; font-size: 14px; font-weight: 700; color: #0F5257;">%s</span></span>'
    '<span style="font-size: 14.5px; color: #67777C;">%s</span>'
    '<span style="display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px; font-size: 15px; font-weight: 600; line-height: 1.5;">%s</span></div>'
    % (t, v, d, ('<span aria-hidden="true" style="color: %s; font-weight: 800;">&#8250;</span>' % col).join('<span style="border-bottom: 2px solid %s;">%s</span>' % (col, st) for st in steps))
    for t, d, steps, v, col in CHAINS)

mapb = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <header style="position: absolute; left: 0; right: 0; top: 0; z-index: 4; height: 56px; box-sizing: border-box; padding: 0 12px 0 4px; display: flex; align-items: center; gap: 4px; background: rgba(242,246,247,0.96); border-bottom: 1px solid #DDE6E8;">
    <a href="PExplore.dc.html" aria-label="Back to Explore" style="width: 44px; height: 44px; display: grid; place-items: center; color: #1E2B3A;">''' + CHEV_L + '''</a>
    <span style="font-size: 17px; font-weight: 800;">The Gita map</span>
  </header>
  <main style="position: absolute; left: 0; right: 0; top: 56px; bottom: 84px; overflow-y: auto; padding: 20px 18px 28px; box-sizing: border-box; display: flex; flex-direction: column; gap: 16px;">
    <div style="display: flex; flex-direction: column; gap: 6px;">
      <h1 style="margin: 0; font-size: 30px; line-height: 1.1; font-weight: 800; letter-spacing: -0.02em;">Where are you right now?</h1>
      <p style="margin: 0; font-size: 16.5px; line-height: 1.45; color: #5D6B70;">Pick a feeling. The map draws your path through the Gita.</p>
    </div>
    <div role="group" aria-label="Feelings" style="display: flex; flex-wrap: wrap; gap: 8px;">
      <sc-for list="{{feels}}" as="f" hint-placeholder-count="7"><button type="button" onClick="{{f.pick}}" aria-pressed="{{f.sel}}" style="min-height: 44px; padding: 0 16px; border-radius: 999px; border: 1.5px solid {{f.bd}}; background: {{f.bg}}; color: {{f.fg}}; font: 700 16px Figtree, sans-serif;">{{f.label}}</button></sc-for>
    </div>
    <section aria-live="polite" style="display: flex; flex-direction: column; padding: 18px 16px 14px; border-radius: 22px; background: #FFFFFF; border: 1px solid #DDE6E8;">
      <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B4533A; margin-bottom: 14px;">Your path from {{feelName}}</span>
      ''' + mstop(1, "#B4533A", "See how it works", '<div style="display: flex; flex-wrap: wrap; gap: 8px;"><sc-for list="{{understand}}" as="v" hint-placeholder-count="3">' + VPILL + '</sc-for></div>') + '''
      ''' + mstop(2, "#1F7A7A", "What answers it", '<div style="display: flex; flex-direction: column; gap: 8px;"><sc-for list="{{cures}}" as="c" hint-placeholder-count="2"><a href="PVerse.dc.html" style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 16px; background: #E3F1EE; text-decoration: none; color: #1E2B3A;"><span style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px;"><span style="font-size: 17px; font-weight: 800; color: #0F5257;">{{c.name}} <span style="font-size: 14px; font-weight: 700; color: #67777C;">&#183; {{c.v}}</span></span><span style="font-family: Newsreader, Georgia, serif; font-size: 16.5px; line-height: 1.35;">{{c.note}}</span></span>' + CHEV_R + '</a></sc-for></div>') + '''
      ''' + mstop(3, "#A8801A", "Verses to practise", '<div style="display: flex; flex-wrap: wrap; gap: 8px;"><sc-for list="{{practise}}" as="v" hint-placeholder-count="4">' + VPILL + '</sc-for></div>', last=True) + '''
    </section>
    <h2 style="margin: 12px 0 0; font-size: 22px; font-weight: 800;">Chains of cause and effect</h2>
    <p style="margin: -8px 0 0; font-size: 15.5px; color: #5D6B70;">The Gita often teaches in steps.</p>
    ''' + chain_cards + '''
    <h2 style="margin: 12px 0 0; font-size: 22px; font-weight: 800;">Find a path</h2>
    <p style="margin: -8px 0 0; font-size: 15.5px; color: #5D6B70;">Pick two points and see how the Gita links them.</p>
    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
      <sc-for list="{{tries}}" as="t" hint-placeholder-count="4"><button type="button" onClick="{{t.pick}}" aria-pressed="{{t.sel}}" style="min-height: 44px; padding: 0 14px; border-radius: 999px; border: 1.5px solid {{t.bd}}; background: {{t.bg}}; color: #1E2B3A; font: 700 15px Figtree, sans-serif;">{{t.label}}</button></sc-for>
    </div>
    <ol aria-live="polite" style="margin: 0; padding: 16px; list-style: none; border-radius: 20px; background: #FFFFFF; border: 1px solid #DDE6E8; display: flex; flex-direction: column;">
      <li style="display: flex; align-items: center; gap: 10px;"><span aria-hidden="true" style="width: 14px; height: 14px; border-radius: 999px; background: #B4533A; flex: none;"></span><span style="font-size: 18px; font-weight: 800;">{{pFrom}}</span></li>
      <sc-for list="{{steps}}" as="s" hint-placeholder-count="2"><li style="display: flex; flex-direction: column;"><span style="margin-left: 6px; padding: 8px 0 8px 18px; border-left: 2px dashed #CBD6D9; font-size: 14.5px; color: #67777C;">{{s.rel}}<span style="display: block; font-family: Newsreader, Georgia, serif; font-size: 16px; color: #2F3C42;">{{s.note}}</span></span><span style="display: flex; align-items: center; gap: 10px;"><span aria-hidden="true" style="width: 14px; height: 14px; border-radius: 999px; background: {{s.dot}}; flex: none;"></span><span style="font-size: 18px; font-weight: 800;">{{s.to}}</span></span></li></sc-for>
    </ol>
    <p style="margin: 4px 0 0; font-size: 13.5px; line-height: 1.45; color: #67777C;">The map links the core shlokas of the twenty themes. Its links are drafts waiting for review.</p>
  </main>
''' + tabbar("explore") + '\n</div>'
map_js = """renderVals() {
    const J = JJSON;
    const P = PJSON;
    const f = this.state.feel || 'restlessness';
    const p = this.state.path || 'rp';
    const j = J[f];
    const v = (n) => ({ n });
    const path = P[p];
    return {
      feels: Object.keys(J).map((k) => ({ label: J[k].label, sel: k === f ? 'true' : 'false', bd: k === f ? '#B4533A' : '#DDE6E8', bg: k === f ? '#B4533A' : '#FFFFFF', fg: k === f ? '#FFFFFF' : '#1E2B3A', pick: () => this.setState({ feel: k }) })),
      feelName: j.label.toLowerCase(),
      understand: j.understand.map(v), practise: j.practise.map(v),
      cures: j.cures.map((c) => ({ name: c[0], v: c[1], note: c[2] })),
      tries: Object.keys(P).map((k) => ({ label: P[k][0] + ' to ' + P[k][1], sel: k === p ? 'true' : 'false', bd: k === p ? '#E9A845' : '#DDE6E8', bg: k === p ? 'rgba(233,168,69,0.16)' : '#FFFFFF', pick: () => this.setState({ path: k }) })),
      pFrom: path[0],
      steps: path[2].map((s, i) => ({ rel: s[1], note: s[3], to: s[2], dot: i === path[2].length - 1 ? '#1F7A7A' : '#0F5257' }))
    };
  }"""
map_js = map_js.replace("JJSON", json.dumps(JOURNEYS)).replace("PJSON", json.dumps(PATHS))
save("PMap.dc.html", page("The Gita map", mapb, script_body=map_js))
print("ok")
