"""Peacock feather bookmark, redrawn by hand-tuned code from Dhiraj's own photo of a feather (IMG_4283).
Writes assets/feather.svg (used by the site) and, next to this file, mock.html for reviewing it.
Run:  python3 design/feather/gen.py"""
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
rnd = random.Random(4283)

# colours sampled from the photo, then evened out
BARB = ["#AEA68C", "#8E836A", "#C5B599", "#9C9478"]
LIME, GREEN, COPPER, COPPER_L, TURQ, TURQ_L, BLUE, BLUE_D = "#CFE070", "#4FA85A", "#8E6A2E", "#C9A04C", "#2EC4C2", "#79ECDB", "#2F63B5", "#1B2D6E"

W, H = 40, 84          # drawing units; the quill runs off the top edge, the eye hangs near the bottom
CX, EY = 20, 60        # eye centre


def half_width(y):
    # slim along the shaft, swelling like a leaf to its widest around the eye
    t = max(0.0, min(1.0, y / 74))
    return 2.2 + 15.5 * math.sin(t * math.pi * 0.78) ** 1.6


def barbs(dark):
    out = []
    y = -4.0
    while y < 70:
        hw = half_width(max(0, y + 8))
        for side in (-1, 1):
            reach = hw + rnd.uniform(-1.5, 2.5)
            drop = 7 + (y / 70) * 7 + rnd.uniform(-1.5, 2)
            ex, ey = CX + side * reach, y + drop
            c1x, c1y = CX + side * reach * 0.35, y + 0.6
            c2x, c2y = CX + side * reach * 0.85, y + drop * 0.35 + rnd.uniform(-0.6, 0.6)
            col = rnd.choice(BARB)
            out.append('<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                       % (CX, y, c1x, c1y, c2x, c2y, ex, ey, col, rnd.uniform(0.5, 0.95), rnd.uniform(0.26, 0.4)))
        y += rnd.uniform(1.0, 1.5)
    # loose wisps that flow past and below the eye
    for k in range(34):
        a = math.pi * (0.08 + 0.84 * k / 33)
        r1, r2 = 11, 11 + rnd.uniform(5, 12)
        bend = rnd.uniform(-2, 2)
        x1, y1 = CX + math.cos(a) * r1 * 0.9, EY + math.sin(a) * r1
        x2, y2 = CX + math.cos(a) * r2 * 0.95 + bend, EY + math.sin(a) * r2 + 2
        out.append('<path d="M%.2f %.2f Q%.2f %.2f %.2f %.2f" stroke="%s" stroke-opacity="%.2f" stroke-width=".3"/>'
                   % (x1, y1, (x1 + x2) / 2 + bend, (y1 + y2) / 2, x2, y2, rnd.choice(BARB), rnd.uniform(0.35, 0.8)))
    return '<g fill="none" stroke-linecap="round">' + "".join(out) + "</g>"


def heart(cx, cy, s):
    # the notched blue heart at the centre of the eye (notch on the right, as in the photo)
    return ('<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f '
            'C%.2f %.2f %.2f %.2f %.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f Z"' % (
                cx + 2.4 * s, cy - 0.2 * s,
                cx + 2.6 * s, cy - 3.6 * s, cx - 1.4 * s, cy - 5 * s, cx - 2.9 * s, cy - 2.2 * s,
                cx - 4.4 * s, cy + 0.6 * s, cx - 2.6 * s, cy + 5.2 * s, cx + 0.4 * s, cy + 4.4 * s,
                cx + 2.6 * s, cy + 3.8 * s, cx + 3.4 * s, cy + 2.2 * s, cx + 1.4 * s, cy + 1.2 * s,
                cx + 0.6 * s, cy + 0.6 * s, cx + 1.2 * s, cy - 0.4 * s, cx + 2.4 * s, cy - 0.2 * s))


def eye(uid):
    return ('<defs><radialGradient id="cu%s" cx=".45" cy=".5" r=".55"><stop offset=".55" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
            '<radialGradient id="bl%s" cx=".4" cy=".45" r=".6"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient></defs>'
            '<ellipse cx="%d" cy="%d" rx="11.6" ry="13.4" fill="%s" opacity=".9"/>'
            '<ellipse cx="%d" cy="%d" rx="11" ry="12.8" fill="%s"/>'
            '<ellipse cx="%d" cy="%.1f" rx="10.2" ry="12" fill="url(#cu%s)"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="6.6" ry="7.4" fill="%s"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="5.6" ry="6.4" fill="%s"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="4.4" ry="5.2" fill="%s" opacity=".85"/>'
            '%s fill="url(#bl%s)"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="1.1" ry="1.6" fill="#fff" opacity=".45"/>') % (
        uid, COPPER_L, COPPER, uid, BLUE, BLUE_D,
        CX, EY, LIME, CX, EY, GREEN, CX, EY + 0.3, uid,
        CX + 0.6, EY + 0.6, GREEN, CX + 0.6, EY + 0.6, TURQ, CX + 0.6, EY + 0.6, TURQ_L,
        heart(CX + 0.4, EY + 0.6, 0.95), uid, CX - 1.4, EY - 1.6)


def feather(dark, uid):
    quill = '<path d="M%d -6 L%d %d" stroke="%s" stroke-width=".9" stroke-linecap="round"/>' % (CX, CX, EY - 10, "#D8CBA2")
    return barbs(dark) + quill + eye(uid)


def svg(dark, uid, w, h, cls=""):
    return ('<svg class="%s" width="%s" height="%s" viewBox="0 0 %d %d" aria-hidden="true">%s</svg>'
            % (cls, w, h, W, H, feather(dark, uid)))


def outline(w, h, col):
    # not kept: the same feather, faded to a quiet grey
    return ('<svg width="%s" height="%s" viewBox="0 0 %d %d" aria-hidden="true" style="filter:grayscale(1);opacity:.45">%s</svg>'
            % (w, h, W, H, feather(True, "o%s" % w)))


ASSET = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "feather.svg")
rnd.seed(4283)
open(ASSET, "w", encoding="ascii").write(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">%s</svg>' % (W, H, feather(True, "f")))

SA = "&#2325;&#2352;&#2381;&#2350;&#2339;&#2381;&#2351;&#2375;&#2357;&#2366;&#2343;&#2367;&#2325;&#2366;&#2352;&#2360;&#2381;&#2340;&#2375; &#2350;&#2366; &#2347;&#2354;&#2375;&#2359;&#2369; &#2325;&#2342;&#2366;&#2330;&#2344;&#160;&#2404;"
n = [0]


def uid():
    n[0] += 1
    return str(n[0])


def panel(dark):
    th = "dark" if dark else "light"
    mute = "#5E7C7A" if dark else "#9AA3A6"
    return ('<div class="panel %s"><div class="head"><span class="rb">%s</span><p class="lab">Bhagavad Gita 2.47 &middot; kept</p><p class="sa">%s</p></div>'
            '<div class="head"><span class="rb">%s</span><p class="lab">Bhagavad Gita 2.48 &middot; not kept</p><p class="sa">%s</p></div>'
            '<div class="card"><span class="m">%s</span><b>Verse 2.47</b><span class="cs">%s</span><small>Karma Yoga</small></div>'
            '<div class="tag">%s</div></div>') % (
        th, svg(dark, uid(), 26, 55), SA, outline(26, 55, mute), SA, svg(dark, uid(), 16, 34), SA.split(" ")[0], "Dark (default)" if dark else "Light")


html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Peacock feather bookmark</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=Tiro+Devanagari+Sanskrit&display=swap">
<style>
body{margin:0;background:#1a1a1a;font-family:Figtree,system-ui,sans-serif;color:#ddd;padding:24px}
h1{font-size:22px;margin:0 0 4px;color:#fff}.sub{margin:0 0 18px;color:#aaa;font-size:15px}
.row{display:flex;gap:24px;align-items:flex-start;margin-bottom:24px}
.photo{width:420px;border-radius:14px}
.big{background:#071E22;border-radius:14px;padding:14px 26px;display:flex;gap:26px;align-items:flex-end}
.big .z{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:13px;color:#9DB6B3}
.big.l{background:#F4F7F6}.big.l .z{color:#5D6B70}
.grid{display:grid;grid-template-columns:repeat(2,390px);gap:24px}
.panel{position:relative;width:390px;border-radius:18px;overflow:hidden}
.dark{background:#071E22;color:#E4EFEC}.light{background:#F4F7F6;color:#1E2B3A}
.head{position:relative;padding:22px 18px 14px;border-bottom:1px solid rgba(128,128,128,.15)}
.lab{font:700 13px Figtree;letter-spacing:.14em;text-transform:uppercase;opacity:.7;margin:0 0 8px}
.sa{font-family:'Tiro Devanagari Sanskrit',serif;font-size:22px;line-height:1.6;margin:0;padding-right:30px}
.rb{position:absolute;top:-6px;right:14px}
.card{position:relative;margin:16px 18px 14px;width:180px;padding:14px 16px;border-radius:16px;box-sizing:border-box}
.dark .card{background:#0C2A2F;border:1px solid #1D4247}.light .card{background:#fff;border:1px solid #DDE6E8}
.card .m{position:absolute;top:-4px;left:12px}
.card b{display:block;margin-top:22px;font-size:17px}
.card .cs{display:block;font-family:'Tiro Devanagari Sanskrit',serif;font-size:16px}
.card small{font-size:14px;opacity:.7}
.tag{font-size:13px;opacity:.6;padding:0 18px 14px}
</style></head><body>
<h1>Your feather, as the bookmark</h1>
<p class="sub">Left: your photo. Right: the vector redrawn from it, at 3x and 6x. Below: on a verse at real size (kept and not kept) and on the Explore card.</p>
<div class="row">
<div><div class="big"><div class="z">%s3x</div><div class="z">%s6x</div></div>
<div class="big l" style="margin-top:12px"><div class="z">%s3x</div><div class="z">%s6x</div></div></div></div>
<div class="grid">%s%s</div>
</body></html>""" % (svg(True, uid(), 60, 126), svg(True, uid(), 120, 252), svg(False, uid(), 60, 126), svg(False, uid(), 120, 252), panel(True), panel(False))
if "--mock" in __import__("sys").argv:
    open(os.path.join(HERE, "mock.html"), "w").write(html)
print("ok", os.path.getsize(ASSET), "bytes")
