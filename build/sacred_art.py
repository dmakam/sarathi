"""Original artwork for Sarathi: the chariot wheel (rath chakra), the peacock
feather mark and the diya. Colours come from CSS classes so one drawing serves
every time of day."""
import math


def wheel(cx, cy, R):
    g = ['<circle class="wd" cx="%g" cy="%g" r="%g"/>' % (cx, cy, R * 0.9)]
    for k in range(16):
        a = 2 * math.pi * k / 16 + math.pi / 16
        big = k % 2 == 0
        r1, r2 = R * 0.2, R * 0.84
        w1, w2 = (R * 0.05, R * 0.022) if big else (R * 0.022, R * 0.01)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        pts = [(cx + ca * r1 + nx * w1, cy + sa * r1 + ny * w1), (cx + ca * r2 + nx * w2, cy + sa * r2 + ny * w2),
               (cx + ca * r2 - nx * w2, cy + sa * r2 - ny * w2), (cx + ca * r1 - nx * w1, cy + sa * r1 - ny * w1)]
        g.append('<path class="wk" d="M%s Z"/>' % " L".join("%.1f %.1f" % q for q in pts))
        g.append('<circle class="wk" cx="%.1f" cy="%.1f" r="%.1f"/>' % (cx + ca * R * 0.86, cy + sa * R * 0.86, R * (0.03 if big else 0.018)))
    for k in range(32):
        a = 2 * math.pi * k / 32
        g.append('<circle class="wk" cx="%.1f" cy="%.1f" r="%.1f"/>' % (cx + math.cos(a) * R, cy + math.sin(a) * R, R * 0.022))
    g.append('<circle class="wr" cx="%g" cy="%g" r="%g" stroke-width="%g"/>' % (cx, cy, R * 0.94, R * 0.07))
    g.append('<circle class="wr" cx="%g" cy="%g" r="%g" stroke-width="%g"/>' % (cx, cy, R * 0.875, R * 0.012))
    for k in range(12):
        g.append('<ellipse class="ws" cx="%g" cy="%g" rx="%g" ry="%g" transform="rotate(%g %g %g)"/>' % (cx, cy - R * 0.15, R * 0.035, R * 0.075, 30 * k, cx, cy))
    g.append('<circle class="wk" cx="%g" cy="%g" r="%g"/><circle class="ws" cx="%g" cy="%g" r="%g"/>' % (cx, cy, R * 0.11, cx, cy, R * 0.05))
    return ('<g class="wheel"><circle class="wg wg1" cx="%g" cy="%g" r="%g"/><circle class="wg wg2" cx="%g" cy="%g" r="%g"/>'
            '<g class="wspin" style="transform-origin:%gpx %gpx">%s</g></g>') % (cx, cy, R * 1.55, cx, cy, R * 1.22, cx, cy, "".join(g))


FEATHER = ('<svg class="feather" width="18" height="28" viewBox="0 0 26 40" aria-hidden="true">'
           '<path d="M13 39 C13 30 13 22 13 14" stroke="#8A6A1E" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
           '<path d="M13 1 C22 6 24 18 13 27 C2 18 4 6 13 1 Z" fill="#1F7A72"/>'
           '<ellipse cx="13" cy="13" rx="5.6" ry="7" fill="#C9A227"/><ellipse cx="13" cy="13.5" rx="3.2" ry="4.2" fill="#24306E"/></svg>')
