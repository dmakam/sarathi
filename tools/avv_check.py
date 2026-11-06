"""Check every cut verse: does the clip open with this verse's first words, and stop
before the next verse begins? Uses the cached emissions from avv_align.py.

    python3 tools/avv_check.py <dir with .opus and .lp.npy> <times.json> <report.csv>
"""
import csv
import difflib
import json
import os
import sys

import numpy as np
import torchaudio

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import avv_align as A  # noqa: E402

LAB = torchaudio.pipelines.MMS_FA.get_labels(star="*")
INV = {i: c for i, c in enumerate(LAB)}


def greedy(lp, a, b):
    ids = lp[max(0, a):b, :len(LAB) - 1].argmax(1)
    out, prev = [], -1
    for i in ids:
        if i != prev and i != 0 and INV.get(int(i), "*") not in "*-|":
            out.append(INV[int(i)])
        prev = i
    return "".join(out)


def expect(text):
    ch = A.lines(text)
    inv = {v: k for k, v in A.DICT.items()}
    return ["".join(inv[t] for t in c) for c in ch]


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def main():
    src, times, rep = sys.argv[1:4]
    T = json.load(open(times))
    data = json.load(open(os.path.join(HERE, "..", "src-data", "data", "verse.json"), encoding="utf-8"))
    by = {"%d.%d" % (v["chapter_number"], v["verse_number"]): v for v in data}
    rows, cache = [], {}
    for vid in sorted(T, key=lambda k: tuple(map(int, k.split(".")))):
        ch = int(vid.split(".")[0])
        if ch not in cache:
            cache = {ch: np.load(os.path.join(src, "BGChapter%d.opus.lp.npy" % ch)).astype(np.float32)}
        lp = cache[ch]
        t = T[vid]
        a, b = int(t["start"] * 50), int(t["end"] * 50)
        lines = expect(by[vid]["text"])
        head = greedy(lp, a, a + 200)
        first = lines[0][: max(8, len(head))]
        s_open = sim(head[: len(lines[0])], lines[0][: len(head)]) if head else 0
        nv = "%d.%d" % (ch, by[vid]["verse_number"] + 1)
        tail = greedy(lp, b - 150, b)
        s_next = 0.0
        if nv in by:
            nl = expect(by[nv]["text"])[0]
            s_next = sim(tail[-len(nl):], nl[: len(tail)]) if tail else 0
        dur = t["end"] - t["start"]
        letters = sum(len(x) for x in lines)
        rows.append({"verse": vid, "start": t["start"], "end": t["end"], "seconds": round(dur, 1),
                     "sec_per_letter": round(dur / max(1, letters), 3), "align_score": t["score"],
                     "opens_like_verse": round(s_open, 2), "tail_like_next": round(s_next, 2),
                     "heard_at_start": head[:40], "expected_start": first[:40]})
    # flags: outliers in pace or weak opening or bleeding into the next verse
    pace = np.array([r["sec_per_letter"] for r in rows])
    med = float(np.median(pace))
    for r in rows:
        f = []
        if r["sec_per_letter"] > med * 1.6 or r["sec_per_letter"] < med * 0.55:
            f.append("length")
        if r["opens_like_verse"] < 0.45:
            f.append("opening")
        if r["tail_like_next"] > 0.6:
            f.append("runs into next")
        if r["align_score"] < 0.2:
            f.append("weak match")
        r["flag"] = ", ".join(f)
    with open(rep, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    bad = [r for r in rows if r["flag"]]
    print(len(rows), "clips,", len(bad), "flagged")
    for r in bad:
        print(r["verse"], r["flag"], "|", r["heard_at_start"], "|", r["expected_start"])


if __name__ == "__main__":
    main()
