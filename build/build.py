#!/usr/bin/env python3
"""Sarathi static site generator.

Reads the public-domain gita/gita dataset and writes a fully static site:
home, 18 chapter pages, 701 verse pages, concept, word and situation pages,
search, reading plans, sources, sitemap. Every HTML/JSON file is written as
pure ASCII (non-ASCII becomes HTML entities or \\u escapes).
"""
import collections
import html
import json
import os
import re
import shutil
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import COMMENTATORS, CONCEPTS, SITUATIONS, THEMES, THEMES_SOURCE, THEME_WORDS, TRADITIONS, TRANSLATIONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src-data", "data")
OUT = os.path.join(ROOT, "site")
ASSETS = os.path.join(ROOT, "assets")
BASE_URL = os.environ.get("SARATHI_BASE_URL", "https://gita.dhirajmakam.com")
SITE = "Sārathi"

# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(s or "", quote=True)


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z]", "", s)


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(text.encode("ascii", "xmlcharrefreplace"))


def write_json(rel, obj):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii") as f:
        json.dump(obj, f, ensure_ascii=True, separators=(",", ":"))


def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return json.load(f)


MARKER = re.compile(r"[।|]{2}\s*[\d.\-\s]+\s*[।|]{2}")
LEAD = re.compile(r"^\s*(?:[।|]{2}\s*[\d.\-\s]+[।|]{2})?\s*(?:\d+\.\d+(?:[-–]\d+)?\.?)?\s*[-–—:]?\s*")


def clean_text(s):
    s = LEAD.sub("", s or "", count=1)
    s = MARKER.sub("", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    s = re.sub(r"^[\u0964|\s\xa0]+", "", s)
    s = re.sub(r"\u0964\u0964\s*$", "\u0964", s)
    return s.strip()


def trim(s, n):
    s = " ".join((s or "").split())
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(",;:.") + "…"


# ---------------------------------------------------------------- load data

verses_raw = load("verse.json")
chapters_raw = load("chapters.json")
translations_raw = load("translation.json")
commentary_raw = load("commentary.json")

CH = {}
for c in chapters_raw:
    n = int(c["chapter_number"])
    CH[n] = {
        "n": n,
        "name": c["name"],
        "tr": c["name_translation"],
        "translit": c["name_transliterated"],
        "meaning": c["name_meaning"],
        "summary": c["chapter_summary"].strip(),
        "count": int(c["verses_count"]),
    }

V = {}       # "2.47" -> verse dict
ORDER = []   # verse ids in reading order
by_internal = {}
for v in sorted(verses_raw, key=lambda x: x["verse_order"]):
    vid = "%d.%d" % (v["chapter_number"], v["verse_number"])
    lines = [l.strip() for l in v["text"].split("\n") if l.strip()]
    speaker = None
    if lines and lines[0].endswith("वाच") and len(lines[0]) < 30:
        speaker = lines.pop(0)
    lines = [MARKER.sub(" ॥", l).strip() for l in lines]
    # Some verses run both half-lines together ("...\u0964next"); split after a mid-line danda.
    split_lines = []
    for l in lines:
        split_lines.extend(x.strip() for x in re.split("(?<=\u0964)(?=\\s*[^\u0964\u0965\\s])", l) if x.strip())
    lines = split_lines
    tl = [l.strip() for l in v["transliteration"].split("\n") if l.strip()]
    t_speaker = None
    if speaker and tl and tl[0].endswith("uvācha"):
        t_speaker = tl.pop(0)
    words = []
    for part in v["word_meanings"].strip().split(";"):
        part = part.strip()
        if "—" not in part:
            if words and part:
                words[-1]["m"] += "; " + part
            continue
        sk, mean = part.split("—", 1)
        sk, mean = sk.strip(), mean.strip()
        keys = [k for k in (norm(p) for p in re.split(r"[-\s]+", sk)) if len(k) > 1]
        words.append({"w": sk, "m": mean, "k": keys})
    V[vid] = {
        "id": vid,
        "c": v["chapter_number"],
        "n": v["verse_number"],
        "order": v["verse_order"],
        "speaker": speaker,
        "t_speaker": t_speaker,
        "sa": lines,
        "tl": tl,
        "words": words,
        "tr": {},
        "cm": {},
    }
    ORDER.append(vid)
    by_internal[v["id"]] = vid

for t in translations_raw:
    vid = by_internal.get(t["verse_id"])
    if vid:
        V[vid]["tr"][t["authorName"]] = clean_text(t["description"])

for c in commentary_raw:
    vid = by_internal.get(c["verse_id"])
    if vid:
        V[vid]["cm"][c["authorName"]] = clean_text(c["description"])

assert len(V) == 701, len(V)

# audio
AUDIO_SRC = os.path.join(SRC, "verse_recitation")
for vid, v in V.items():
    p = os.path.join(AUDIO_SRC, str(v["c"]), "%d.mp3" % v["n"])
    v["audio"] = "/audio/%d/%d.mp3" % (v["c"], v["n"]) if os.path.exists(p) else None


def eng(v, author="Swami Sivananda"):
    return v["tr"].get(author) or next((x for a, l, _ in TRANSLATIONS if l == "english" for x in [v["tr"].get(a)] if x), "")


def card_text(v):
    p = v["tr"].get("Shri Purohit Swami", "")
    if p and len(p) <= 320:
        return p
    opts = [v["tr"].get(a, "") for a, l, _ in TRANSLATIONS if l == "english"]
    opts = [o for o in opts if o]
    return min(opts, key=len) if opts else ""


# ---------------------------------------------------------------- graph

WORD = {}
for vid in ORDER:
    for w in V[vid]["words"]:
        for k in w["k"]:
            e = WORD.setdefault(k, {"forms": collections.Counter(), "m": collections.Counter(), "v": []})
            e["forms"][w["w"].split()[0] if " " not in w["w"] else w["w"]] += 1
            e["m"][w["m"]] += 1
            if not e["v"] or e["v"][-1] != vid:
                e["v"].append(vid)

for vid in ORDER:
    V[vid]["concepts"] = []
CONCEPT_VERSES = {}
for cid, iast, deva, gloss, subs, exact in CONCEPTS:
    hits = []
    for vid in ORDER:
        keys = [k for w in V[vid]["words"] for k in w["k"]]
        if any(any(s in k for s in subs) or k in exact for k in keys):
            hits.append(vid)
            V[vid]["concepts"].append(cid)
    CONCEPT_VERSES[cid] = hits
CONCEPT = {c[0]: c for c in CONCEPTS}

THEME_OF = collections.defaultdict(list)
for tid, tname, vids in THEMES:
    for x in vids:
        assert x in V, x
        THEME_OF[x].append(tid)
THEME = {t[0]: t for t in THEMES}
CORE = []
for _, _, vids in THEMES:
    for x in vids:
        if x not in CORE:
            CORE.append(x)

SIT_OF = collections.defaultdict(list)
for sid, label, vids in SITUATIONS:
    for x in vids:
        assert x in V, x
        SIT_OF[x].append(sid)

WORD_PAGE_MIN = 3

import graph_build as GB  # noqa: E402
import graph_data as GD  # noqa: E402
import consult_data as CD  # noqa: E402

# ---------------------------------------------------------------- layout

FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600"
         "&family=Tiro+Devanagari+Sanskrit:ital@0;1&display=swap")


def page(rel, title, body, desc="", canonical=None, jsonld=None, body_class="", nav="read", scripts=""):
    canonical = canonical or "/" + rel.replace("index.html", "")
    full = title if title.startswith(SITE) else "%s | %s" % (title, SITE)
    ld = ('<script type="application/ld+json">%s</script>' % json.dumps(jsonld, ensure_ascii=True)) if jsonld else ""

    def nl(key, href, label):
        cur = ' aria-current="page"' if key == nav else ""
        return '<a href="%s"%s>%s</a>' % (href, cur, label)

    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{base}{canon}">
<meta name="theme-color" content="#0B3B40">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="/assets/app.css">
<script>try{{var z=JSON.parse(localStorage.getItem("sarathi.textsize")||"1");if(z>1)document.documentElement.style.setProperty("--zoom",z)}}catch(e){{}}</script>
{ld}
</head>
<body class="{bc}">
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <a class="brand" href="/"><img src="/assets/icon.svg" alt="" width="28" height="28"><span>{site}</span></a>
  <nav class="nav" aria-label="Main">
    {n0}{n1}{n2}{n3}{n4}{n5}
  </nav>
  <a class="nav-search" href="/search/" aria-label="Search the Gita"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></a>
  <button type="button" class="nav-size" aria-label="Text size: normal. Tap to make text larger."><span aria-hidden="true">A<small>A</small></span></button>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <p>{site} is a free reader for the Bhagavad Gita. Text, translations, commentaries and recitations come from the public-domain <a href="https://github.com/gita/gita">gita/gita</a> dataset. What you read and mark stays in your browser. Practice recordings are scored on our server and thrown away straight after.</p>
  <p><a href="/sources/">Sources and credits</a></p>
</footer>
{scripts}<script src="/assets/app.js" defer></script>
</body>
</html>
""".format(title=esc(full), desc=esc(desc or "Read the Bhagavad Gita word by word, with recitation, classical commentaries and verses for what you are facing."),
           base=BASE_URL, canon=esc(canonical), fonts=FONTS, ld=ld, bc=body_class, site=SITE, body=body,
           n1=nl("read", "/chapters/", "Read"), n2=nl("consult", "/consult/", "Ask S\u0101rathi"),
           n3=nl("map", "/map/", "Map"), n4=nl("plans", "/plans/", "Plans"),
           n5=nl("practice", "/practice/", "Practice"), n0=nl("themes", "/themes/", "Themes"), scripts=scripts)
    write(rel, doc)


def verse_url(vid):
    c, n = vid.split(".")
    return "/%s/%s/" % (c, n)


def sa_html(v, cls="sa"):
    out = '<p class="%s" lang="sa">%s</p>' % (cls, "<br>".join(esc(l) for l in v["sa"]))
    if cls == "vsa" and v.get("tl"):
        out += '<p class="vtl" lang="sa-Latn">%s</p>' % "<br>".join(esc(l) for l in v["tl"])
    return out


def verse_row(vid, extra=""):
    v = V[vid]
    return ('<li class="vrow"><a href="%s"><span class="vnum">%s</span>'
            '<span class="vsa" lang="sa">%s</span><span class="vtl" lang="sa-Latn">%s</span><span class="ven">%s</span>%s</a></li>') % (
        verse_url(vid), vid, esc(v["sa"][0] if v["sa"] else ""), esc(v["tl"][0] if v["tl"] else ""), esc(trim(eng(v), 170)), extra)


# ---------------------------------------------------------------- verse pages

TR_TABS = [(a, l, f) for a, l, f in TRANSLATIONS]
TRAD = {t[0]: t for t in TRADITIONS}


def build_verse(vid):
    v = V[vid]
    i = ORDER.index(vid)
    prev_id = ORDER[i - 1] if i > 0 else None
    next_id = ORDER[i + 1] if i < len(ORDER) - 1 else None
    ch = CH[v["c"]]

    words = []
    for w in v["words"]:
        keys = " ".join(w["k"])
        words.append('<button class="word" type="button" data-k="%s"><span class="w-sa">%s</span><span class="w-m">%s</span></button>'
                     % (esc(keys), esc(w["w"]), esc(w["m"])))

    tabs, panels = [], []
    for j, (author, lang, follows) in enumerate(TR_TABS):
        text = v["tr"].get(author)
        if not text:
            continue
        key = norm(author)
        sel = "true" if j == 0 else "false"
        tabs.append('<button role="tab" type="button" aria-selected="%s" aria-controls="tr-%s" id="tab-%s" data-tr="%s">%s%s</button>'
                    % (sel, key, key, key, esc(author.replace("Swami ", "").replace("Shri ", "").replace("Dr. ", "")),
                       ' <span class="lang">%s</span>' % ("Hindi" if lang == "hindi" else "") if lang == "hindi" else ""))
        foll = '<p class="follows">Follows the commentary of %s.</p>' % esc(follows) if follows else ""
        panels.append('<div role="tabpanel" id="tr-%s" aria-labelledby="tab-%s"%s><p class="tr-text" lang="%s">%s</p><p class="by">%s</p>%s</div>'
                      % (key, key, "" if j == 0 else " hidden", "hi" if lang == "hindi" else "en",
                         esc(text).replace("\n", "<br>"), esc(author), foll))

    groups = collections.OrderedDict((t[0], []) for t in TRADITIONS)
    for author in list(COMMENTATORS) + [a for a in v["cm"] if a not in COMMENTATORS]:
        if author in v["cm"]:
            groups[COMMENTATORS.get(author, "modern")].append(author)
    cm_html = []
    for tid, authors in groups.items():
        if not authors:
            continue
        _, tname, tdesc = TRAD[tid]
        btns = "".join('<button type="button" class="cm-btn" data-author="%s">%s</button>'
                       % (esc(a), esc(a.replace("Sri ", "").replace("Swami ", ""))) for a in authors)
        cm_html.append('<div class="trad"><h3>%s</h3><p>%s</p><div class="cm-list">%s</div></div>' % (esc(tname), esc(tdesc), btns))

    concepts = "".join('<a class="chip" href="/concept/%s/"><span lang="sa">%s</span> %s</a>'
                       % (c, esc(CONCEPT[c][2]), esc(CONCEPT[c][1])) for c in v["concepts"])
    sits = "".join('<a class="chip soft" href="/facing/%s/">%s</a>' % (s, esc(next(x[1] for x in SITUATIONS if x[0] == s)))
                   for s in SIT_OF.get(vid, []))
    themes = "".join('<a class="chip theme" href="/themes/%s/">Theme %d: %s</a>' % (t, [x[0] for x in THEMES].index(t) + 1, esc(THEME[t][1]))
                     for t in THEME_OF.get(vid, []))

    audio = ""
    if v["audio"]:
        audio = """<div class="player" data-src="{src}">
  <button type="button" class="play" aria-label="Play recitation"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path class="i-play" d="M8 5v14l11-7z" fill="currentColor"/><path class="i-pause" d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg></button>
  <div class="p-track"><div class="p-bar"></div></div>
  <label class="p-opt"><input type="checkbox" class="repeat"> Repeat after me</label>
  <select class="p-speed" aria-label="Playback speed"><option value="0.75">0.75x</option><option value="1" selected>1x</option><option value="1.25">1.25x</option></select>
</div>""".format(src=v["audio"])

    speaker = '<p class="speaker"><span lang="sa">%s</span> %s</p>' % (esc(v["speaker"]), esc(v["t_speaker"] or "")) if v["speaker"] else ""
    nav = '<nav class="vnav" aria-label="Verses">%s<a href="/%d/">Chapter %d</a>%s</nav>' % (
        '<a rel="prev" href="%s">Previous %s</a>' % (verse_url(prev_id), prev_id) if prev_id else "<span></span>",
        v["c"], v["c"],
        '<a rel="next" href="%s">Next %s</a>' % (verse_url(next_id), next_id) if next_id else "<span></span>")

    body = """<article class="verse" data-vid="{vid}" data-card="{card}">
<div class="v-head">
  <p class="crumb"><a href="/{c}/">Chapter {c}: {chname}</a>, verse {n}</p>
  {speaker}
  {sa}
  <p class="tl" lang="sa-Latn"><span class="tl-k">Say it</span>{tl}</p>
  {audio}
  <div class="v-actions">
    <button type="button" class="btn ghost mark" data-vid="{vid}">Mark as read</button>
    <button type="button" class="btn ghost share">Make a share card</button>
    <a class="btn ghost" href="/practice/{c}/{n}/">Practice reciting</a>
  </div>
</div>
<section class="v-sec" aria-labelledby="h-words">
  <h2 id="h-words">Word by word</h2>
  <p class="hint">Tap a word to see every verse that uses it.</p>
  <div class="words">{words}</div>
  <div class="word-pop" hidden></div>
</section>
<section class="v-sec" aria-labelledby="h-tr">
  <h2 id="h-tr">Translation</h2>
  <div class="tabs" role="tablist" aria-label="Translators">{tabs}</div>
  {panels}
</section>
<section class="v-sec" aria-labelledby="h-cm">
  <h2 id="h-cm">Classical commentaries</h2>
  <p class="hint">The great teachers read this verse differently. Open one to compare. Most are in the original Sanskrit.</p>
  {cm}
  <div class="cm-out" hidden></div>
</section>
{vmap}
{related}
{nav}
</article>
<dialog class="card-dlg"><div class="card-wrap"><canvas width="1080" height="1350"></canvas></div>
<div class="card-act"><button type="button" class="btn dl">Download image</button><button type="button" class="btn ghost sh" hidden>Share</button><button type="button" class="btn ghost close">Close</button></div></dialog>
""".format(vid=vid, card=esc(json.dumps({"sa": v["sa"], "tl": v["tl"], "en": card_text(v), "id": vid}, ensure_ascii=False)),
           c=v["c"], chname=esc(ch["tr"]), n=v["n"], speaker=speaker, sa=sa_html(v), tl="<br>".join(esc(l) for l in v["tl"]),
           audio=audio, words="".join(words), tabs="".join(tabs), panels="".join(panels), cm="".join(cm_html),
           related=('<section class="v-sec"><h2>In this verse</h2><div class="chips">%s%s%s</div></section>' % (themes, concepts, sits)) if (themes or concepts or sits) else "",
           nav=nav, vmap=GB.verse_map_html(vid))

    en = eng(v)
    jsonld = {
        "@context": "https://schema.org", "@type": "Quotation",
        "name": "Bhagavad Gita %s" % vid,
        "text": " ".join(v["sa"]),
        "inLanguage": "sa",
        "isPartOf": {"@type": "Book", "name": "Bhagavad Gita", "url": BASE_URL + "/"},
        "position": vid,
        "url": BASE_URL + verse_url(vid),
        "description": trim(en, 300),
    }
    page("%d/%d/index.html" % (v["c"], v["n"]), "Bhagavad Gita %s: %s" % (vid, trim(en, 60)), body,
         desc=trim("Bhagavad Gita chapter %d verse %d: %s" % (v["c"], v["n"], en), 155), jsonld=jsonld, body_class="pg-verse",
         scripts='<script src="/assets/map.js" defer></script>' if vid in GD.TAGS else "")

    write_json("data/c/%s.json" % vid, v["cm"])


# ---------------------------------------------------------------- other pages

def build_chapter(n):
    ch = CH[n]
    vids = [x for x in ORDER if V[x]["c"] == n]
    paras = "".join("<p>%s</p>" % esc(p) for p in ch["summary"].split("\n") if p.strip())
    nav = '<nav class="vnav">%s<a href="/chapters/">All chapters</a>%s</nav>' % (
        '<a rel="prev" href="/%d/">Chapter %d</a>' % (n - 1, n - 1) if n > 1 else "<span></span>",
        '<a rel="next" href="/%d/">Chapter %d</a>' % (n + 1, n + 1) if n < 18 else "<span></span>")
    body = """<section class="ch-head">
  <p class="crumb">Chapter {n} of 18</p>
  <h1><span lang="sa">{name}</span> {tr}</h1>
  <p class="lede">{meaning}. {count} verses.</p>
  <div class="v-actions"><a class="btn" href="/{n}/1/">Start reading</a><button type="button" class="btn ghost resume" data-ch="{n}" hidden>Resume</button></div>
</section>
<details class="summary"><summary>About this chapter</summary>{paras}</details>
<ol class="vlist">{rows}</ol>
{nav}""".format(n=n, name=esc(ch["name"]), tr=esc(ch["tr"]), meaning=esc(ch["meaning"]), count=ch["count"],
                paras=paras, rows="".join(verse_row(x) for x in vids), nav=nav)
    page("%d/index.html" % n, "Chapter %d: %s (%s)" % (n, ch["tr"], ch["meaning"]), body,
         desc=trim("Bhagavad Gita chapter %d, %s: %s" % (n, ch["tr"], ch["summary"]), 155), body_class="pg-list")


def chapter_rows():
    out = []
    for n in range(1, 19):
        ch = CH[n]
        out.append('<li class="crow" data-ch="%d"><a href="/%d/"><span class="cnum">%d</span><span class="cname"><span lang="sa">%s</span><span>%s</span></span><span class="cmeta">%s<span class="cprog"></span></span></a></li>'
                   % (n, n, n, esc(ch["name"]), esc(ch["tr"]), esc("%s, %d verses" % (ch["meaning"], ch["count"]))))
    return "".join(out)


def build_chapters():
    body = '<section class="ch-head"><h1>The eighteen chapters</h1><p class="lede">701 verses, a conversation on a battlefield between Arjuna and Krishna.</p></section><ol class="clist">%s</ol>' % chapter_rows()
    page("chapters/index.html", "All 18 chapters of the Bhagavad Gita", body, nav="read", body_class="pg-list")


def sit_cards():
    return "".join('<a class="sit" href="/facing/%s/">%s</a>' % (sid, esc(label)) for sid, label, _ in SITUATIONS)


def build_facing():
    body = '<section class="ch-head"><h1>What are you facing?</h1><p class="lede">Start from your life, not from chapter one. Each path opens five verses that speak to it.</p></section><div class="sits big">%s</div>' % sit_cards()
    page("facing/index.html", "Bhagavad Gita verses for what you are facing", body, nav="facing", body_class="pg-list")
    for sid, label, vids in SITUATIONS:
        items = []
        for x in vids:
            v = V[x]
            items.append('<li class="fcard"><a href="%s"><span class="vnum">%s</span>%s<span class="ven">%s</span></a></li>'
                         % (verse_url(x), x, sa_html(v, "vsa"), esc(trim(eng(v), 320))))
        others = "".join('<a class="sit" href="/facing/%s/">%s</a>' % (s, esc(l)) for s, l, _ in SITUATIONS if s != sid)
        body = """<section class="ch-head"><p class="crumb"><a href="/facing/">What you're facing</a></p><h1>{label}</h1>
<p class="lede">Five verses to read slowly, in this order.</p></section>
<ol class="flist">{items}</ol>
<section class="v-sec"><h2>Something else?</h2><div class="sits">{others}</div></section>""".format(label=esc(label), items="".join(items), others=others)
        page("facing/%s/index.html" % sid, "%s: Bhagavad Gita verses" % label, body, nav="facing", body_class="pg-list",
             desc=trim("%s? Five Bhagavad Gita verses that speak to it, with translation and recitation." % label.rstrip("."), 155))


def build_concepts():
    cards = []
    for cid, iast, deva, gloss, _, _ in CONCEPTS:
        cards.append('<a class="ccard" href="/concept/%s/"><span class="c-deva" lang="sa">%s</span><span class="c-iast">%s</span><span class="c-gloss">%s</span><span class="c-count">%d verses</span></a>'
                     % (cid, esc(deva), esc(iast), esc(gloss), len(CONCEPT_VERSES[cid])))
    body = '<section class="ch-head"><h1>Concepts</h1><p class="lede">The ideas the Gita returns to, found by where the Sanskrit word itself appears in a verse.</p></section><div class="cgrid">%s</div>' % "".join(cards)
    page("concepts/index.html", "Key concepts of the Bhagavad Gita", body, nav="concepts", body_class="pg-list")
    for cid, iast, deva, gloss, _, _ in CONCEPTS:
        vids = CONCEPT_VERSES[cid]
        per_ch = collections.Counter(V[x]["c"] for x in vids)
        mx = max(per_ch.values()) if per_ch else 1
        bars = "".join('<a class="bar" href="/%d/" style="--h:%.2f" title="Chapter %d: %d verses"><span>%d</span></a>'
                       % (n, per_ch.get(n, 0) / mx, n, per_ch.get(n, 0), n) for n in range(1, 19))
        co = collections.Counter(c for x in vids for c in V[x]["concepts"] if c != cid).most_common(6)
        rel = "".join('<a class="chip" href="/concept/%s/"><span lang="sa">%s</span> %s</a>' % (c, esc(CONCEPT[c][2]), esc(CONCEPT[c][1])) for c, _ in co)
        body = """<section class="ch-head"><p class="crumb"><a href="/concepts/">Concepts</a></p>
<h1><span lang="sa">{deva}</span> {iast}</h1><p class="lede">{gloss}. Appears in {cnt} verses.</p></section>
<section class="v-sec"><h2>Where it appears</h2><div class="bars" aria-label="Verses per chapter">{bars}</div></section>
<section class="v-sec"><h2>Often found with</h2><div class="chips">{rel}</div></section>
<section class="v-sec"><h2>Verses</h2><ol class="vlist">{rows}</ol></section>""".format(
            deva=esc(deva), iast=esc(iast), gloss=esc(gloss), cnt=len(vids), bars=bars, rel=rel,
            rows="".join(verse_row(x) for x in vids))
        page("concept/%s/index.html" % cid, "%s (%s) in the Bhagavad Gita" % (iast, gloss), body, nav="concepts", body_class="pg-list",
             desc=trim("Every Bhagavad Gita verse that uses %s, %s, with word meanings and translations." % (iast, gloss.lower()), 155))


def build_words():
    index = {}
    pages = 0
    for k, e in WORD.items():
        form = e["forms"].most_common(1)[0][0]
        meaning = e["m"].most_common(1)[0][0]
        index[k] = [form, meaning, e["v"]]
        if len(e["v"]) >= WORD_PAGE_MIN:
            pages += 1
            rows = []
            for x in e["v"]:
                m = next((w["m"] for w in V[x]["words"] if k in w["k"]), "")
                rows.append(verse_row(x, '<span class="wmean">Here: %s</span>' % esc(m)))
            meanings = "".join("<li>%s <span>(%d)</span></li>" % (esc(m), c) for m, c in e["m"].most_common(8))
            body = """<section class="ch-head"><p class="crumb">Word</p><h1>{form}</h1>
<p class="lede">Used in {n} verses of the Bhagavad Gita.</p></section>
<section class="v-sec"><h2>How it is translated</h2><ul class="means">{meanings}</ul></section>
<section class="v-sec"><h2>Every verse</h2><ol class="vlist">{rows}</ol></section>""".format(
                form=esc(form), n=len(e["v"]), meanings=meanings, rows="".join(rows))
            page("word/%s/index.html" % k, "%s: meaning in the Bhagavad Gita" % form, body, body_class="pg-list",
                 desc=trim("What %s means in the Bhagavad Gita, and all %d verses that use it." % (form, len(e["v"])), 155))
    write_json("data/words.json", index)
    write_json("data/wordpages.json", sorted(k for k, e in WORD.items() if len(e["v"]) >= WORD_PAGE_MIN))
    return pages


def build_search():
    idx = []
    for x in ORDER:
        v = V[x]
        idx.append([x, " ".join(v["tl"]), trim(eng(v), 400),
                    " ".join(filter(None, [v["tr"].get("Shri Purohit Swami", ""), v["tr"].get("Swami Gambirananda", "")]))[:900],
                    " ".join(w["m"] for w in v["words"]), " ".join(v["sa"])])
    write_json("data/search.json", idx)
    body = """<section class="ch-head"><h1>Search</h1>
<form class="sform" role="search" onsubmit="return false"><label for="q" class="vh">Search verses</label>
<input id="q" type="search" placeholder="Try: anger, karma yoga, 2.47, the mind is restless" autocomplete="off" autofocus></form>
<p class="hint s-status">Searches the transliteration, word meanings and five English translations.</p></section>
<ol class="vlist s-results"></ol>"""
    page("search/index.html", "Search the Bhagavad Gita", body, nav="", body_class="pg-list pg-search")


def build_plans():
    ess = ["2.7", "2.11", "2.13", "2.20", "2.22", "2.47", "2.48", "2.62", "2.63", "2.70", "3.19", "3.35", "4.7", "4.8",
           "5.18", "6.5", "6.34", "6.35", "7.7", "9.22", "9.26", "10.20", "11.32", "12.13", "12.15", "13.28",
           "15.7", "16.21", "18.65", "18.66"]
    for x in ess:
        assert x in V, x
    global ESSENTIALS
    ESSENTIALS = ess
    plans = {
        "themes": {"name": "Twenty themes", "desc": "One theme a week, about six shlokas each. The core path through the Gita.",
                   "days": [list(t[2]) for t in THEMES], "unit": "week", "labels": [t[1] for t in THEMES]},
        "eighteen": {"name": "Eighteen days", "desc": "One chapter a day, the way the battle lasted eighteen days.",
                     "days": [[x for x in ORDER if V[x]["c"] == n] for n in range(1, 19)]},
        "weekly": {"name": "A chapter a week", "desc": "Eighteen weeks, unhurried. Good for study circles.",
                   "days": [[x for x in ORDER if V[x]["c"] == n] for n in range(1, 19)], "unit": "week"},
        "essentials": {"name": "Thirty essential verses", "desc": "One verse a day for a month, the ones most often quoted.",
                       "days": [[x] for x in ess]},
        "daily": {"name": "A verse a day", "desc": "All 701 verses, one each day, for close reading or memorising.",
                  "days": [[x] for x in ORDER]},
    }
    write_json("data/plans.json", plans)
    cards = "".join("""<div class="plan" data-plan="{k}"><h2>{name}</h2><p>{desc}</p><p class="plan-len">{n} {unit}s</p>
<div class="plan-state"></div><button type="button" class="btn start">Start this plan</button></div>""".format(
        k=k, name=esc(p["name"]), desc=esc(p["desc"]), n=len(p["days"]), unit=p.get("unit", "day")) for k, p in plans.items())
    body = """<section class="ch-head"><h1>Reading plans</h1><p class="lede">Pick a pace. Your progress is kept in this browser only.</p></section>
<div class="today" hidden></div>
<div class="plans">{cards}</div>""".format(cards=cards)
    page("plans/index.html", "Bhagavad Gita reading plans", body, nav="plans", body_class="pg-list pg-plans")


def practice_words(v):
    out = []
    for line in v["sa"]:
        for tok in line.split():
            if re.sub(r"[\u0964\u0965\s]", "", tok):
                out.append(tok)
    return out


def build_practice(vid):
    v = V[vid]
    words = practice_words(v)
    spans, i = [], 0
    lines = []
    for line in v["sa"]:
        parts = []
        for tok in line.split():
            if re.sub(r"[\u0964\u0965\s]", "", tok):
                parts.append('<span class="pw" data-i="%d">%s</span>' % (i, esc(tok)))
                i += 1
            else:
                parts.append('<span class="pd">%s</span>' % esc(tok))
        lines.append(" ".join(parts))
    player = ('<div class="player" data-src="%s"><button type="button" class="play" aria-label="Play recitation"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path class="i-play" d="M8 5v14l11-7z" fill="currentColor"/><path class="i-pause" d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg></button>'
              '<div class="p-track"><div class="p-bar"></div></div><label class="p-opt"><input type="checkbox" class="repeat"> Repeat after me</label>'
              '<select class="p-speed" aria-label="Playback speed"><option value="0.75">0.75x</option><option value="1" selected>1x</option><option value="1.25">1.25x</option></select></div>' % v["audio"]) if v["audio"] else ""
    i = ORDER.index(vid)
    nxt = ORDER[i + 1] if i < len(ORDER) - 1 else None
    body = """<article class="practice" data-vid="{vid}">
<div class="p-head">
  <p class="crumb"><a href="/practice/">Practice</a>, <a href="{vurl}">read verse {vid}</a></p>
  <h1>Recite {vid}</h1>
  <p class="pv" lang="sa">{lines}</p>
  <p class="tl" lang="sa-Latn"><span class="tl-k">Say it</span>{tl}</p>
</div>
<div class="psteps">
  <section class="pstep"><h2>Listen</h2><p class="hint">Hear it first. This recording reads the verse slowly, word by word, with the joins between words opened up. Turn on Repeat after me to say it back in the pauses.</p>{player}</section>
  <section class="pstep rec"><h2>Recite</h2><p class="hint">Say the whole verse at your own pace. Recording stops by itself a few seconds after you finish.</p>
    <button type="button" class="mic" aria-pressed="false" aria-label="Start reciting"><svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg></button>
    <p class="mic-label">Tap and recite</p>
    <p class="live" aria-live="polite"></p>
  </section>
</div>
<div class="result" hidden aria-live="polite"></div>
<section class="pstep pprog"><h2>Your progress</h2><div class="progress"></div>
  <p class="hint">A Good earns a check mark. Two Goods on different days mark the verse learned, then reviews come back after 1, 3, 7 and 21 days.</p>
  {next}
</section>
</article>
<dialog class="consent card-dlg">
  <h2>Before you record</h2>
  <p>Your recording is sent to the S\u0101rathi coach, scored against the verse, and thrown away straight after. Nothing is stored on the server. Your score is kept in this browser, and your take stays on this device for playback until you leave the page.</p>
  <div class="card-act"><button type="button" class="btn ok">Start recording</button><button type="button" class="btn ghost cancel">Not now</button></div>
</dialog>""".format(vid=vid, words=esc(json.dumps(words, ensure_ascii=False)), vurl=verse_url(vid), lines="<br>".join(lines),
                    tl="<br>".join(esc(l) for l in v["tl"]), player=player,
                    next=('<p><a class="btn ghost" href="/practice/%s/%s/">Next verse, %s</a></p>' % (nxt.split(".")[0], nxt.split(".")[1], nxt)) if nxt else "")
    page("practice/%d/%d/index.html" % (v["c"], v["n"]), "Recite Bhagavad Gita %s" % vid, body, canonical=verse_url(vid),
         desc=trim("Practise reciting Bhagavad Gita %s: listen, recite, and see which words came through clearly." % vid, 155),
         body_class="pg-verse pg-practice", nav="practice", scripts='<script src="/assets/recite.js" defer></script>')


def build_practice_index():
    body = """<section class="ch-head"><h1>Practice reciting</h1>
<p class="lede">Learn verses by heart. Listen, recite, and get a check mark when every word comes through.</p></section>
<div class="practice-board vlist-wrap" data-essentials='{ess}' data-themes='{themes}'><p class="hint" style="max-width:880px;margin:24px auto;padding:0 16px">Loading your verses...</p></div>""".format(ess=json.dumps(CORE), themes=esc(json.dumps([[t[1], t[2]] for t in THEMES])))
    page("practice/index.html", "Practice reciting the Bhagavad Gita", body, nav="practice", body_class="pg-list",
         scripts='<script src="/assets/recite.js" defer></script>')


def theme_cards():
    out = []
    for i, (tid, name, vids) in enumerate(THEMES, 1):
        dev, rom = THEME_WORDS[tid]
        out.append('<a class="tc2 h%d" href="/themes/%s/" data-v="%s" style="--i:%d">'
                   '<span class="tc2-n">%02d</span><span class="tc2-sa" lang="sa">%s</span><span class="tc2-tl" lang="sa-Latn">%s</span>'
                   '<span class="tc2-name">%s</span><span class="tc2-bar" aria-hidden="true"><i></i></span></a>'
                   % ((i - 1) % 5, tid, ",".join(vids), i - 1, i, esc(dev), esc(rom), esc(name)))
    return '<div class="tc2-grid">%s</div>' % "".join(out)


def build_themes():
    body = """<section class="th-stage">
<div class="th-head"><div><h1>The Gita in twenty themes</h1>
<p class="lede">One theme a week. Read, understand, learn by heart.</p></div>
<div class="v-actions"><a class="btn" href="/themes/{first}/">Begin with theme 1</a><a class="btn ghost on-dark" href="/plans/">Weekly plan</a></div></div>
{cards}
<p class="credit">Themes and shloka selection follow the <a href="{src}">{srcname}</a>.</p></section>""".format(
        first=THEMES[0][0], cards=theme_cards(), src=THEMES_SOURCE[1], srcname=esc(THEMES_SOURCE[0]))
    page("themes/index.html", "Twenty themes of the Bhagavad Gita", body, nav="themes", body_class="pg-themes",
         desc="The Bhagavad Gita in 20 themes and %d shlokas, from inner potential to equanimity, with recitation and practice." % len(CORE))
    for i, (tid, name, vids) in enumerate(THEMES, 1):
        items = []
        for x in vids:
            v = V[x]
            items.append('<li class="fcard"><a href="%s"><span class="vnum">%s</span>%s<span class="ven">%s</span></a>'
                         '<div class="v-actions"><a class="btn ghost sm" href="/practice/%s/%s/">Practice reciting</a></div></li>'
                         % (verse_url(x), x, sa_html(v, "vsa"), esc(trim(eng(v), 320)), v["c"], v["n"]))
        prev_t = THEMES[i - 2] if i > 1 else None
        next_t = THEMES[i] if i < len(THEMES) else None
        nav = '<nav class="vnav">%s<a href="/themes/">All themes</a>%s</nav>' % (
            '<a rel="prev" href="/themes/%s/">Theme %d: %s</a>' % (prev_t[0], i - 1, esc(prev_t[1])) if prev_t else "<span></span>",
            '<a rel="next" href="/themes/%s/">Theme %d: %s</a>' % (next_t[0], i + 1, esc(next_t[1])) if next_t else "<span></span>")
        body = """<section class="ch-head"><p class="crumb"><a href="/themes/">Themes</a>, {i} of 20</p><h1>{name}</h1>
<p class="lede">{n} shlokas. Read them in this order, then practise reciting each one.</p>
<div class="v-actions"><a class="btn" href="/practice/{pc}/{pn}/">Start practising</a></div></section>
<ol class="flist">{items}</ol>
{nav}""".format(i=i, name=esc(name), n=len(vids), pc=V[vids[0]]["c"], pn=V[vids[0]]["n"], items="".join(items), nav=nav)
        page("themes/%s/index.html" % tid, "%s: Bhagavad Gita theme %d" % (name, i), body, nav="themes", body_class="pg-list",
             desc=trim("%s: %d Bhagavad Gita shlokas (%s) with word meanings, translation and recitation practice." % (name, len(vids), ", ".join(vids)), 155))


def build_consult():
    data = {"aud": [[a, l, w] for a, l, w in CD.AUDIENCES], "feel": [[a, l, w] for a, l, w in CD.FEELINGS],
            "crisis": CD.CRISIS, "unsafe": CD.UNSAFE, "hints": CD.HINTS, "sit": [], "v": {}}
    for sid, aud, feels, title, words, vs, todo, ask in CD.SITUATIONS:
        data["sit"].append({"id": sid, "a": aud, "f": feels, "t": title, "w": words,
                            "v": [[x, why] for x, why in vs], "do": todo, "ask": ask})
        for x, _ in vs:
            assert x in V, x
            v = V[x]
            data["v"][x] = {"sa": v["sa"], "tl": v["tl"], "en": eng(v), "url": verse_url(x), "audio": v["audio"],
                            "pr": "/practice/%d/%d/" % (v["c"], v["n"])}
    write_json("data/consult.json", data)
    body = """<section class="cx" data-src="/data/consult.json">
  <div class="cx-stage" aria-live="polite">
    <div class="cx-step is-on">
      <p class="cx-kicker">Ask S&#257;rathi</p>
      <h1 class="cx-h">What&rsquo;s on your mind?</h1>
      <p class="cx-q">Loading&hellip;</p>
    </div>
  </div>
  <noscript><p class="cx-q">This guide needs JavaScript. You can still browse <a href="/facing/">verses for what you&rsquo;re facing</a>.</p></noscript>
</section>
<section class="cx-saved" hidden>
  <h2>Saved for you</h2>
  <ul class="cx-savelist"></ul>
</section>"""
    page("consult/index.html", "Ask S\u0101rathi", body, nav="consult", body_class="pg-consult",
         desc="Say what you're going through and get one shloka from the Gita, what it means for you, and one thing to try today.",
         scripts='<script src="/assets/consult.js" defer></script>\n')


def build_sources():
    tr = "".join("<li>%s (%s)%s</li>" % (esc(a), l.title(), ", following %s" % esc(f) if f else "") for a, l, f in TRANSLATIONS)
    cm = "".join("<li><strong>%s:</strong> %s</li>" % (esc(TRAD[t][1]), esc(", ".join(a for a, tt in COMMENTATORS.items() if tt == t))) for t in TRAD)
    body = """<section class="ch-head"><h1>Sources and credits</h1></section>
<div class="prose">
<p>The Sanskrit text, transliteration, word meanings, translations, commentaries and recitations come from the <a href="https://github.com/gita/gita">gita/gita</a> open dataset, released into the public domain under the Unlicense. Thank you to everyone who built it.</p>
<h2>Themes</h2><p>The twenty themes and their shloka selection follow the <a href="{tsrc}">{tname}</a>.</p>
<h2>Translations</h2><ul>{tr}</ul>
<h2>Commentaries, by tradition</h2><ul>{cm}</ul>
<h2>How concepts are found</h2><p>A verse is linked to a concept when the Sanskrit word for it, or a form of it, appears in the verse's word-by-word breakdown. This is literal, not interpretive: a verse about desire that never says <em>k&#257;ma</em> will not appear under it.</p>
<h2>Privacy</h2><p>There are no accounts, no tracking scripts and no ads. Plan progress and preferences are stored in your own browser.</p>
</div>""".format(tr=tr, cm=cm, tsrc=THEMES_SOURCE[1], tname=esc(THEMES_SOURCE[0]))
    page("sources/index.html", "Sources and credits", body, nav="", body_class="pg-list")


def build_home():
    hero_v = V["2.47"]
    hwords = "".join('<span class="hw" tabindex="0" data-m="%s">%s</span> ' % (esc(w["w"] + ": " + w["m"]), esc(w["w"])) for w in hero_v["words"])
    vod = json.dumps([x for x in ORDER], ensure_ascii=True)
    body = """<section class="hero">
  <div class="hero-copy">
    <h1>The Gita, word by word.</h1>
    <p class="lede">All 701 verses with recitation, every Sanskrit word explained, and sixteen classical commentaries side by side.</p>
    <div class="v-actions"><a class="btn" href="/consult/">Ask S&#257;rathi about your day</a><a class="btn ghost" href="/themes/">Start with the 20 themes</a></div>
  </div>
  <figure class="hero-verse" data-src="{audio}">
    <p class="hv-sa" lang="sa">{sa}</p>
    <p class="hv-tl" lang="sa-Latn">{htl}</p>
    <p class="hv-words">{hwords}</p>
    <p class="hv-meaning" aria-live="polite">&nbsp;</p>
    <figcaption><a href="/2/47/">Chapter 2, verse 47</a><button type="button" class="hv-play" aria-label="Play verse 2.47"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path class="i-play" d="M8 5v14l11-7z" fill="currentColor"/><path class="i-pause" d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg><span>Listen</span></button></figcaption>
  </figure>
</section>
<section class="band">
  <h2>The Gita in twenty themes</h2>
  <p class="band-lede">Start here. The core of the Gita, one theme a week.</p>
  {themes}
</section>
<section class="band">
  <h2>What are you facing?</h2>
  <div class="sits">{sits}</div>
</section>
<section class="band vod" data-order='{vod}'>
  <h2>Today's verse</h2>
  <div class="vod-body"></div>
</section>
<section class="band">
  <h2>Read in order</h2>
  <ol class="clist">{chapters}</ol>
</section>
<section class="band">
  <h2>Ideas that run through it</h2>
  <div class="chips">{concepts}</div>
</section>""".format(ncore=len(CORE), themes=theme_cards(), audio=hero_v["audio"] or "", sa="<br>".join(esc(l) for l in hero_v["sa"]), htl="<br>".join(esc(l) for l in hero_v["tl"]), hwords=hwords, sits=sit_cards(),
                     vod=vod, chapters=chapter_rows(),
                     concepts="".join('<a class="chip" href="/concept/%s/"><span lang="sa">%s</span> %s</a>' % (c[0], esc(c[2]), esc(c[1])) for c in CONCEPTS))
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL + "/",
              "potentialAction": {"@type": "SearchAction", "target": BASE_URL + "/search/?q={q}", "query-input": "required name=q"}}
    page("index.html", "%s: the Bhagavad Gita, word by word" % SITE, body, jsonld=jsonld, body_class="pg-home", nav="")


def build_misc(word_pages):
    urls = ["/", "/consult/", "/themes/", "/chapters/", "/facing/", "/concepts/", "/plans/", "/practice/", "/search/", "/sources/"]
    urls += ["/themes/%s/" % t[0] for t in THEMES] + ["/map/"] + ["/state/%s/" % st[0] for st in GD.STATES]
    urls += ["/%d/" % n for n in range(1, 19)] + [verse_url(x) for x in ORDER]
    urls += ["/facing/%s/" % s[0] for s in SITUATIONS] + ["/concept/%s/" % c[0] for c in CONCEPTS]
    urls += ["/word/%s/" % k for k, e in WORD.items() if len(e["v"]) >= WORD_PAGE_MIN]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n'
          % "\n".join("<url><loc>%s%s</loc></url>" % (BASE_URL, u) for u in urls))
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE_URL)
    page("404.html", "Page not found", '<section class="ch-head"><h1>That page isn\'t here.</h1><p class="lede">Every verse lives at its chapter and number, like <a href="/2/47/">/2/47/</a>. Or <a href="/search/">search</a> for it.</p></section>', canonical="/404.html", body_class="pg-list")
    return len(urls)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))
    if "--no-audio" not in sys.argv:
        shutil.copytree(AUDIO_SRC, os.path.join(OUT, "audio"))
    GB.init(V=V, ORDER=ORDER, CORE=CORE, THEMES=THEMES, SITUATIONS=SITUATIONS, CONCEPT=CONCEPT, page=page, esc=esc,
            trim=trim, eng=eng, verse_url=verse_url, sa_html=sa_html, write_json=write_json)
    for x in ORDER:
        build_verse(x)
    for n in range(1, 19):
        build_chapter(n)
    build_chapters()
    build_facing()
    build_concepts()
    wp = build_words()
    build_search()
    build_themes()
    GB.build_state_pages()
    GB.build_map_page()
    build_plans()
    for x in ORDER:
        build_practice(x)
    build_practice_index()
    with open(os.path.join(ROOT, "server", "practice-words.json"), "w", encoding="ascii") as f:
        json.dump({x: practice_words(V[x]) for x in ORDER}, f, ensure_ascii=True)
    build_consult()
    build_sources()
    build_home()
    n = build_misc(wp)
    print("verses=%d chapters=18 concepts=%d situations=%d words=%d word_pages=%d sitemap_urls=%d"
          % (len(ORDER), len(CONCEPTS), len(SITUATIONS), len(WORD), wp, n))
    for cid, *_ in CONCEPTS:
        print("  concept %-10s %d" % (cid, len(CONCEPT_VERSES[cid])))


if __name__ == "__main__":
    main()
