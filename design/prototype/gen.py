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
    <sc-if value="{{showLinks}}" hint-placeholder-val="{{false}}"><div style="display: flex; flex-direction: column; gap: 8px;">
      <a href="PExplore.dc.html" style="display: flex; align-items: center; justify-content: space-between; min-height: 56px; padding: 0 16px; border-radius: 14px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;"><span><span lang="sa" style="font-family: 'Tiro Devanagari Sanskrit', serif; font-size: 18px;">बुद्धि</span> <b style="font-size: 16px;">buddhi</b> <span style="color: #5D6B70; font-size: 14.5px;">· the intellect</span></span>''' + CHEV_R + '''</a>
      <a href="PExplore.dc.html" style="display: flex; align-items: center; justify-content: space-between; min-height: 56px; padding: 0 16px; border-radius: 14px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;"><span><span lang="sa" style="font-family: 'Tiro Devanagari Sanskrit', serif; font-size: 18px;">मनस्</span> <b style="font-size: 16px;">manas</b> <span style="color: #5D6B70; font-size: 14.5px;">· the mind</span></span>''' + CHEV_R + '''</a>
      <a href="PLearn.dc.html" style="display: flex; align-items: center; justify-content: space-between; min-height: 56px; padding: 0 16px; border-radius: 14px; background: #FFFFFF; border: 1px solid #DDE6E8; text-decoration: none; color: #1E2B3A;"><span style="font-size: 16px; font-weight: 700;">Theme 2: Mastering your faculties</span>''' + CHEV_R + '''</a>
    </div></sc-if>
  </main>
  <div style="position: absolute; left: 0; right: 0; bottom: 84px; z-index: 4; padding: 12px 16px; box-sizing: border-box; height: 72px; display: flex; gap: 10px; background: linear-gradient(180deg, rgba(242,246,247,0), #F2F6F7 30%);">
    <a href="PPractice.dc.html" style="flex-grow: 1; display: flex; align-items: center; justify-content: center; gap: 10px; border-radius: 999px; background: linear-gradient(180deg, #F6C46A, #E39A35); color: #1C1204; text-decoration: none; font-size: 17px; font-weight: 800; box-shadow: 0 12px 26px -10px rgba(227,154,53,0.8);">''' + MIC.format(s=20) + '''Learn it by heart</a>
    <a href="PVerse.dc.html" aria-label="Next verse in this theme, 3.43" style="flex: none; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 16px; border-radius: 999px; background: #FFFFFF; border: 1px solid #DDE6E8; color: #1E2B3A; text-decoration: none; line-height: 1.1;"><span style="font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #5D6B70;">Next</span><span style="font-size: 15px; font-weight: 800;">3.43 ›</span></a>
  </div>
''' + tabbar("learn") + '\n</div>'
verse_js = """renderVals() {
    const tab = this.state.tab || 'words';
    const mk = (id, label) => ({ label, sel: tab === id ? 'true' : 'false', bg: tab === id ? '#FFFFFF' : 'transparent', fg: tab === id ? '#1E2B3A' : '#5D6B70', sh: tab === id ? '0 2px 6px rgba(30,43,58,0.12)' : 'none', pick: () => this.setState({ tab: id }) });
    return {
      tabs: [mk('words', 'Words'), mk('explain', 'Explained'), mk('links', 'Connected')],
      showWords: tab === 'words', showExplain: tab === 'explain', showLinks: tab === 'links'
    };
  }"""
verse = verse.replace('THEMEROW', THEME_ROW)
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
explore = '<div style="' + FRAME % (PAPER, INK) + '">' + '''
  <main style="position: absolute; left: 0; right: 0; top: 0; bottom: 84px; overflow-y: auto; padding: 32px 16px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">
    <h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.02em;">Explore</h1>
    <label for="xs" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);">Search the Gita</label>
    <div style="display: flex; align-items: center; gap: 10px; height: 52px; padding: 0 16px; border-radius: 16px; background: #FFFFFF; border: 1px solid #DDE6E8; color: #5D6B70;">''' + SEARCH + '''<input id="xs" placeholder="Search a word, a verse, a feeling" style="flex-grow: 1; min-width: 0; border: 0; outline: none; background: transparent; font: 400 16.5px Figtree, sans-serif; color: #1E2B3A;"></div>
    ''' + tile("18 chapters", "Read the Gita in order, verse by verse.", ["1 Arjuna’s grief", "2 Knowledge", "3 Action", "+15"], "#DDEFEC", "#0B3F43", "PVerse.dc.html") + '''
    ''' + tile("Big ideas", "Words like dharma and karma, and every verse they appear in.", ["dharma", "karma", "ātman", "yoga", "+20"], "#E6EEFB", "#1F3A6E", "PVerse.dc.html") + '''
    ''' + tile("Feelings", "What the Gita says when you feel angry, afraid or low.", ["Anger", "Fear", "Grief", "Doubt", "+6"], "#EEE7F6", "#3E2C63", "PAsk.dc.html") + '''
  </main>
''' + tabbar("explore") + '\n</div>'
save("PExplore.dc.html", page("Explore", explore))
print("ok")
