"""Knowledge-graph pages for Sarathi: verse maps, state pages, the map explorer.

Imported by build.py, which passes in its data and helpers through init().
"""
import collections
import json

import graph_data as G

E = {}  # filled by init(): V, ORDER, CORE, THEMES, THEME, SITUATIONS, CONCEPT, page, esc, trim, eng, verse_url, sa_html, write_json

STATE = {s[0]: s for s in G.STATES}
CHEV = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
SIT = {}
# Relation phrases, forward (a -> b) and backward (seen from b).
REL = {
    "speaks": ("speaks to", "is addressed in"),
    "cultivates": ("cultivates", "is cultivated in"),
    "helps": ("helps when", "is helped by"),
    "teaches": ("teaches", "is taught in"),
    "antidote": ("is the antidote to", "is answered by"),
    "leads": ("leads to", "follows from"),
    "answers": ("answers", "is answered by"),
    "echoes": ("echoes", "is echoed in"),
    "parallel": ("parallels", "parallels"),
    "culminates": ("arrives at", "is reached from"),
    "theme": ("belongs to", "includes"),
}
WEIGHT = {"leads": 1, "answers": 1, "echoes": 1, "parallel": 1.2, "culminates": 1, "speaks": 1, "cultivates": 1,
          "antidote": 1, "helps": 1.5, "teaches": 2, "theme": 2.5}


def init(**kw):
    E.update(kw)
    for s in E["SITUATIONS"]:
        SIT[s[0]] = s


def core_order(vids):
    idx = {x: i for i, x in enumerate(E["CORE"])}
    return sorted(set(vids), key=lambda x: (idx.get(x, 9999), E["ORDER"].index(x)))


def verses_with_state(sid):
    return core_order([v for v, t in G.TAGS.items() if sid in t["s"]])


def chains_of(vid):
    return [c for c in G.CHAINS if any(v == vid for _, v in c[4])]


def state_chip(sid, extra=""):
    s = STATE[sid]
    return '<a class="vm-node st-%s" href="/state/%s/" data-why="%s"><span lang="sa">%s</span> %s%s</a>' % (
        "a" if s[3] == "afflictive" else "h", sid, E["esc"](s[4]), E["esc"](s[2]), E["esc"](s[1]), extra)


def _lc(x):
    return x[:1].lower() + x[1:] if x and not (len(x) > 1 and x[1].isupper()) else x


def verse_map_html(vid):
    """The verse's connections as a thread: the verse at the top, one line down through
    plain-worded stops. Tap a word and its "why" opens under that stop (app.js)."""
    t = G.TAGS.get(vid)
    if not t:
        return ""
    esc = E["esc"]
    C = E["CONCEPT"]

    def chip(kind, label, why, href, go):
        return ('<button type="button" class="vt-chip k-%s" aria-expanded="false" data-why="%s" data-href="%s" data-go="%s">'
                '<span class="vt-dot" aria-hidden="true"></span>%s</button>') % (kind, esc(why), href, esc(go), label)

    def stop(kind, title, inner, sid):
        return ('<div class="vt-stop k-%s"><span class="vt-node" aria-hidden="true"></span><h3>%s</h3>%s'
                '<p class="vt-why" data-stop="%s" aria-live="polite" hidden></p></div>') % (kind, title, inner, sid)

    stops = []
    feel = []
    for sid in t["s"]:
        st = STATE[sid]
        if st[3] == "afflictive":
            feel.append(chip("speaks", esc(st[1]), "It speaks to %s: %s." % (_lc(st[1]), _lc(st[4])), "/state/%s/" % sid, "See every verse on %s" % _lc(st[1])))
    for h in t["h"]:
        lab = SIT[h][1]
        feel.append(chip("helps", esc(lab), "Ask brings you here when you say: \u201c%s.\u201d" % lab.rstrip("."), "/facing/%s/" % h, "See verses for this"))
    if feel:
        stops.append(stop("speaks", "Reach for it when", '<div class="vt-chips">%s</div>' % "".join(feel), "feel"))
    grow = [chip("cultivates", esc(STATE[sid][1]), "It builds %s: %s." % (_lc(STATE[sid][1]), _lc(STATE[sid][4])), "/state/%s/" % sid, "See every verse on %s" % _lc(STATE[sid][1]))
            for sid in t["s"] if STATE[sid][3] == "healing"]
    if grow:
        stops.append(stop("cultivates", "What it grows in you", '<div class="vt-chips">%s</div>' % "".join(grow), "grow"))
    if t["c"]:
        ideas = [chip("idea", '<span lang="sa">%s</span> %s' % (esc(C[c][2]), esc(C[c][1])), "%s, %s." % (C[c][1], _lc(C[c][3])), "/concept/%s/" % c, "Every verse with %s" % C[c][1])
                 for c in t["c"]]
        stops.append(stop("idea", "Ideas inside it", '<div class="vt-chips">%s</div>' % "".join(ideas), "idea"))
    rel = []
    for a, typ, b, note in G.LINKS:
        if a == vid:
            rel.append((REL[typ][0], b, note))
        elif b == vid:
            rel.append((REL[typ][1], a, note))
    if rel:
        cards = "".join('<a class="vt-verse" href="%s"><span class="vt-vn">%s</span><span class="vt-vt"><span class="vt-rel">%s</span>%s</span>%s</a>'
                        % (E["verse_url"](o), o, esc(r[:1].upper() + r[1:]), esc(note), CHEV) for r, o, note in rel)
        stops.append(stop("verse", "Where it leads" if all(r in ("leads to", "arrives at") for r, _, _ in rel) else "Verses it talks to", cards, "rel"))
    for c in chains_of(vid):
        steps = []
        for i, (label, v) in enumerate(c[4]):
            steps.append('<a class="vt-step%s" href="%s">%s</a>' % (" here" if v == vid else "", E["verse_url"](v), esc(label)))
        last = c[4][-1][1]
        note = "Lit steps are this verse." + (" The last step is %s." % last if last != vid else "")
        stops.append(stop("chain", "Part of a chain",
                          '<div class="vt-chain"><span class="vt-ct">%s</span><span class="vt-cd">%s</span><div class="vt-steps">%s</div><span class="vt-cn">%s</span></div>'
                          % (esc(c[1]), esc(c[2]), '<span aria-hidden="true">&#8250;</span>'.join(steps), note), "chain"))
    return """<section class="v-sec vt" aria-labelledby="h-map" data-tab="links">
  <div class="vt-head"><span class="vt-hub" aria-hidden="true">{vid}</span><span><span class="vt-k">Verse map</span><span class="vt-h" id="h-map">Where this verse connects</span><span class="vt-s">Tap a word to see why.</span></span></div>
  <div class="vt-thread">{stops}</div>
  <a class="vt-all" href="/map/">See the whole map{chev}</a>
</section>""".format(vid=vid, stops="".join(stops), chev=CHEV)


def graph_json():
    nodes, edges = {}, []
    V = E["V"]
    for vid in G.TAGS:
        nodes[vid] = {"t": "verse", "l": vid, "u": E["verse_url"](vid), "d": E["trim"](E["eng"](V[vid]), 110)}
    for a, typ, b, note in G.LINKS:
        for x in (a, b):
            if x not in nodes:
                nodes[x] = {"t": "verse", "l": x, "u": E["verse_url"](x), "d": E["trim"](E["eng"](V[x]), 110)}
        edges.append([a, typ, b, note])
    for s in G.STATES:
        nodes["s:" + s[0]] = {"t": "state", "v": s[3], "l": s[1], "u": "/state/%s/" % s[0], "d": s[4]}
    for h in E["SITUATIONS"]:
        nodes["h:" + h[0]] = {"t": "situation", "l": h[1], "u": "/facing/%s/" % h[0]}
    C = E["CONCEPT"]
    for vid, t in G.TAGS.items():
        for s in t["s"]:
            edges.append([vid, "speaks" if STATE[s][3] == "afflictive" else "cultivates", "s:" + s, ""])
        for h in t["h"]:
            edges.append([vid, "helps", "h:" + h, ""])
        for c in t["c"]:
            nodes.setdefault("c:" + c, {"t": "idea", "l": C[c][1], "u": "/concept/%s/" % c, "d": C[c][3]})
            edges.append([vid, "teaches", "c:" + c, ""])
    for a, b, vv, note in G.ANTIDOTES:
        edges.append(["s:" + a, "antidote", "s:" + b, "%s (%s)" % (note, vv)])
    for i, (tid, name, vids) in enumerate(E["THEMES"], 1):
        nodes["t:" + tid] = {"t": "theme", "l": "Theme %d: %s" % (i, name), "u": "/themes/%s/" % tid}
        for vid in vids:
            edges.append([vid, "theme", "t:" + tid, ""])
    return {"nodes": nodes, "edges": edges, "rel": REL, "w": WEIGHT}


def journey(sid):
    """A practical reading path for a state: understand it, then what heals it."""
    s = STATE[sid]
    if s[3] == "afflictive":
        cures = [(a, vv, note) for a, b, vv, note in G.ANTIDOTES if b == sid]
        first = []
        for c in G.CHAINS:
            for _, vv in c[4]:
                if sid in G.TAGS.get(vv, {}).get("s", []) and vv not in first:
                    first.append(vv)
        speak = (first + [v for v in verses_with_state(sid) if v not in first])[:3]
        cure_verses = []
        for a, vv, _ in cures:
            for v in [vv] + verses_with_state(a):
                if v not in cure_verses and v not in speak:
                    cure_verses.append(v)
        return {"kind": "afflictive", "understand": speak, "cures": [c[0] for c in cures], "practise": cure_verses[:4]}
    heals = [b for a, b, _, _ in G.ANTIDOTES if a == sid]
    return {"kind": "healing", "understand": [], "cures": heals, "practise": verses_with_state(sid)[:5]}


def verse_card(vid, note=""):
    V = E["V"]
    v = V[vid]
    return ('<li class="jcard"><a href="%s"><span class="vnum">%s</span>%s<span class="ven">%s</span>%s</a></li>'
            % (E["verse_url"](vid), vid, E["sa_html"](v, "vsa"), E["esc"](E["trim"](E["eng"](v), 200)),
               ('<span class="wmean">%s</span>' % E["esc"](note)) if note else ""))


def build_state_pages():
    esc = E["esc"]
    for s in G.STATES:
        sid, name, deva, val, gloss = s
        j = journey(sid)
        if val == "afflictive":
            cures = "".join(state_chip(c) for c in j["cures"])
            body_j = """<section class="v-sec"><h2>1. See how it works</h2><ol class="jlist">{u}</ol></section>
<section class="v-sec"><h2>2. What answers it</h2><div class="chips">{c}</div></section>
<section class="v-sec"><h2>3. Verses to practise</h2><ol class="jlist">{p}</ol></section>""".format(
                u="".join(verse_card(v) for v in j["understand"]) or '<li class="hint">No verse among the core shlokas names it directly yet.</li>',
                c=cures or '<span class="hint">No remedy linked yet.</span>',
                p="".join(verse_card(v) for v in j["practise"]))
        else:
            heals = "".join(state_chip(c) for c in j["cures"])
            body_j = """<section class="v-sec"><h2>Verses that cultivate it</h2><ol class="jlist">{p}</ol></section>
{h}""".format(p="".join(verse_card(v) for v in j["practise"]),
              h=('<section class="v-sec"><h2>It answers</h2><div class="chips">%s</div></section>' % heals) if heals else "")
        allv = verses_with_state(sid)
        chs = [c for c in G.CHAINS if any(sid in G.TAGS.get(v, {}).get("s", []) for _, v in c[4])]
        body = """<section class="ch-head"><p class="crumb"><a href="/map/">Gita map</a>, {kind}</p>
<h1><span lang="sa">{deva}</span> {name}</h1><p class="lede">{gloss}. Linked to {n} of the core shlokas.</p></section>
{j}
{chains}
<section class="v-sec"><h2>Every linked verse</h2><div class="chips">{all}</div></section>""".format(
            kind="what troubles us" if val == "afflictive" else "what the Gita cultivates", deva=esc(deva), name=esc(name),
            gloss=esc(gloss), n=len(allv), j=body_j,
            chains=('<section class="v-sec"><h2>Chains it appears in</h2><div class="chips">%s</div></section>' % "".join(
                '<a class="chip" href="/map/#chain-%s">%s</a>' % (c[0], esc(c[1])) for c in chs)) if chs else "",
            all="".join('<a class="chip" href="%s">%s</a>' % (E["verse_url"](v), v) for v in allv))
        E["page"]("state/%s/index.html" % sid, "%s in the Bhagavad Gita" % name, body, nav="map", body_class="pg-list",
                  desc=E["trim"]("%s (%s) in the Bhagavad Gita: the verses that speak to it and what answers it." % (name, gloss.lower()), 155))


def build_map_page():
    esc = E["esc"]
    aff = [s for s in G.STATES if s[3] == "afflictive"]
    heal = [s for s in G.STATES if s[3] == "healing"]
    journeys = {s[0]: journey(s[0]) for s in G.STATES}
    pick = "".join('<button type="button" class="feel st-a" data-s="%s"><span lang="sa">%s</span> %s</button>' % (s[0], esc(s[2]), esc(s[1])) for s in aff)
    pick_h = "".join('<button type="button" class="feel st-h" data-s="%s"><span lang="sa">%s</span> %s</button>' % (s[0], esc(s[2]), esc(s[1])) for s in heal)
    chains = []
    for c in G.CHAINS:
        steps = "".join('<li class="cstep"><a href="%s"><span class="cname">%s</span><span class="cref">%s</span></a></li>' % (E["verse_url"](v), esc(n), v)
                        for n, v in c[4])
        chains.append('<div class="chainbox ch-%s" id="chain-%s"><h3>%s</h3><p class="hint">%s</p><ol class="csteps">%s</ol></div>'
                      % (c[3], c[0], esc(c[1]), esc(c[2]), steps))
    V = E["V"]
    rows = []
    for label, a, b, c in G.GUNA_MATRIX:
        cells = "".join('<td><a href="%s"><span class="vnum">%s</span><span>%s</span></a></td>' % (E["verse_url"](x), x, esc(E["trim"](E["eng"](V[x]), 95)))
                        for x in (a, b, c))
        rows.append("<tr><th scope=\"row\">%s</th>%s</tr>" % (esc(label), cells))
    data = {"j": journeys, "states": {s[0]: [s[1], s[2], s[3], s[4]] for s in G.STATES},
            "verses": {v: [E["trim"](E["eng"](V[v]), 150), " ".join(V[v]["sa"][:1])] for v in G.TAGS}}
    E["write_json"]("data/map.json", data)
    E["write_json"]("data/graph.json", graph_json())
    body = """<header class="mtop"><a class="vtop-back" href="/explore/" aria-label="Back to Explore"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg></a><span>The Gita map</span></header>
<section class="map-hero">
  <div class="mh-copy">
    <h1>Where are you right now?</h1>
    <p class="lede">Pick a feeling. The map draws your path through the Gita: how it works, what answers it, and the verses to practise.</p>
  </div>
  <div class="feelings">
    <div class="feel-row"><span class="feel-label">What troubles you</span>{pick}</div>
    <div class="feel-row"><span class="feel-label">What you want to grow</span>{pick_h}</div>
  </div>
  <div class="journey" aria-live="polite" hidden></div>
</section>
<section class="band" id="chains"><h2>Chains of cause and effect</h2><p class="band-lede">The Gita often teaches in steps. Each step links to its verse.</p>{chains}</section>
<section class="band" id="gunas"><h2>The three gunas, four ways</h2><p class="band-lede">The same three qualities, applied to nature, signs, food and joy.</p>
<div class="gtable-wrap"><table class="gtable"><thead><tr><th></th><th scope="col"><span lang="sa">&#2360;&#2340;&#2381;&#2340;&#2381;&#2357;</span> Sattva</th><th scope="col"><span lang="sa">&#2352;&#2332;&#2360;&#2381;</span> Rajas</th><th scope="col"><span lang="sa">&#2340;&#2350;&#2360;&#2381;</span> Tamas</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="band" id="path"><h2>Find a path</h2><p class="band-lede">Pick any two points, a feeling, a verse, a situation or an idea, and see the shortest chain of links between them.</p>
<form class="pathform" onsubmit="return false">
  <label>From <input list="pf-nodes" class="pf-from" value="Anger" autocomplete="off"></label>
  <label>To <input list="pf-nodes" class="pf-to" value="Forgiveness" autocomplete="off"></label>
  <button type="submit" class="btn pf-go">Show the path</button>
  <datalist id="pf-nodes"></datalist>
</form>
<div class="pf-try">Try: <button type="button" class="chip" data-p="Craving|Inner joy">Craving to inner joy</button><button type="button" class="chip" data-p="Fear|Faith">Fear to faith</button><button type="button" class="chip" data-p="2.47|18.56">2.47 to 18.56</button><button type="button" class="chip" data-p="I feel alone|Devotion">Feeling alone to devotion</button></div>
<ol class="pf-out" aria-live="polite"></ol></section>
<p class="credit">The map links the {n} core shlokas of the twenty themes. Its links are drafts made from the text and translations, waiting for review.</p>""".format(
        pick=pick, pick_h=pick_h, chains="".join(chains), rows="".join(rows), n=len(G.TAGS))
    E["page"]("map/index.html", "The Gita map: from what troubles you to what heals it", body, nav="map", body_class="pg-map ph-bare",
              desc="Pick a feeling and follow a path through the Bhagavad Gita: the verses that explain it, what answers it, and verses to practise.",
              scripts='<script src="/assets/map.js" defer></script>')
