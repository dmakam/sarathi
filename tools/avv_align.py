"""Find where each verse starts and ends in the Aarsha Vidya Varshini chapter recordings.

The recordings are in teach-and-repeat style: the leader chants a line and a group
repeats it. We force-align the known verse text against the audio with the same MMS
aligner the recitation coach uses, verse by verse, with a "*" (star) token between
lines so the repeats, the chapter opening and the closing line are absorbed rather
than forced onto verse letters.

    python3 tools/avv_align.py <dir with BGChapterN.opus> <out.json> [chapters]

Output: {"12.1": {"start": s, "end": s, "score": x, "lead": s}, ...} in seconds.
"""
import json
import os
import re
import sys

import numpy as np
import torch
import torchaudio

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "server"))
import align  # noqa: E402

B = torchaudio.pipelines.MMS_FA
DICT = B.get_dict(star="*")
FPS = 50  # emission frames per second (20 ms)
SR = B.sample_rate
_m = None


def model():
    global _m
    if _m is None:
        torch.set_num_threads(os.cpu_count() or 2)
        _m = B.get_model(with_star=True).eval()
    return _m


def emissions(audio, chunk=30, ctx=1):
    """Log-probs for the whole file, computed in 30 s pieces with 1 s of context each side."""
    out, n, step = [], len(audio), chunk * SR
    for s in range(0, n, step):
        a, b = max(0, s - ctx * SR), min(n, s + step + ctx * SR)
        with torch.inference_mode():
            em, _ = model()(torch.from_numpy(audio[a:b]).unsqueeze(0))
        lp = torch.log_softmax(em[0], -1)
        lo = (s - a) * FPS // SR
        hi = lo + (min(n, s + step) - s) * FPS // SR
        out.append(lp[lo:hi])
    return torch.cat(out)


def _syl(r):
    return len(re.findall(r"[aeiou]+", r))


def lines(text):
    """Split a verse into the pieces the leader chants before the group repeats:
    the speaker line ("arjuna uvaca"), then each quarter-verse (pada)."""
    t = re.sub(r"[0-9.\u0966-\u096f]+", " ", text)
    t = t.replace("\u0909\u0935\u093e\u091a", "\u0909\u0935\u093e\u091a\u0964")
    out = []
    for p in [p.strip() for p in re.split(r"[\u0964\u0965|\n]+", t) if p.strip()]:
        ws = [w for w in (align.roman(x) for x in p.split()) if w]
        if not ws:
            continue
        parts = [ws]
        if not ws[-1].endswith("uvaaca") and len(ws) > 1:
            tot, acc, best = sum(_syl(w) for w in ws), 0, None
            for i, w in enumerate(ws[:-1]):
                acc += _syl(w)
                d = abs(acc - tot / 2)
                if best is None or d < best[0]:
                    best = (d, i + 1)
            if tot >= 12:
                parts = [ws[:best[1]], ws[best[1]:]]
        for q in parts:
            toks = [DICT[c] for c in "".join(q) if c in DICT]
            if toks:
                out.append(toks)
    return out


def align_verse(lp, chunks):
    star = DICT["*"]
    seq, owner = [star], [-1]
    for k, ch in enumerate(chunks):
        seq += ch + [star]
        owner += [k] * len(ch) + [-1]
    tgt = torch.tensor([seq], dtype=torch.int32)
    ali, sc = torchaudio.functional.forced_align(lp.unsqueeze(0), tgt, blank=0)
    spans = torchaudio.functional.merge_tokens(ali[0], sc[0].exp())
    assert len(spans) == len(seq), (len(spans), len(seq))
    first, last, good, csc = {}, {}, [], {}
    for p, sp in enumerate(spans):
        k = owner[p]
        if k < 0:
            continue
        first.setdefault(k, sp.start)
        last[k] = sp.end
        good.append(float(sp.score))
        csc.setdefault(k, []).append(float(sp.score))
    csc = {k: float(np.mean(v)) for k, v in csc.items()}
    return first, last, (float(np.mean(good)) if good else -99.0), csc


def silence_snap(energy, t, lo, hi):
    """Quietest 20 ms frame in [lo, hi] (frames), nearest to t on ties."""
    lo, hi = max(0, lo), min(len(energy) - 1, hi)
    if hi <= lo:
        return t
    seg = energy[lo:hi + 1]
    m = seg.min()
    cand = np.where(seg <= m + 0.02 * (seg.max() - m + 1e-9))[0] + lo
    return int(cand[np.argmin(abs(cand - t))])


def run_chapter(path, ch, verses):
    audio = align.load_audio(path)
    cache = path + ".lp.npy"
    if os.path.exists(cache):
        lp = torch.from_numpy(np.load(cache).astype(np.float32))
    else:
        lp = emissions(audio)
        try:
            np.save(cache, lp.numpy().astype(np.float16))
        except OSError:
            pass
    T = lp.shape[0]
    frames = audio[: T * SR // FPS].reshape(T, -1)
    energy = np.log10((frames ** 2).mean(1) + 1e-8)
    energy = np.convolve(energy, np.ones(5) / 5, "same")
    n = len(verses)
    letters = sum(sum(len(c) for c in lines(v["text"])) for v in verses)
    pace = (T - 40 * FPS) / letters  # frames per letter, leader plus repeat
    cur, res, prev_e = 0, [], 0
    for i, v in enumerate(verses):
        chunks = lines(v["text"])
        need = sum(len(c) for c in chunks)
        # window: about 1.7x this verse's expected length at the chapter's pace, so a
        # refrain that recurs in later verses ("sa me priyah") can't pull the match ahead
        hi = min(T, cur + int(max(need * pace * 1.7, 20 * FPS)))
        first, last, score, csc = align_verse(lp[cur:hi], chunks)
        if not first:
            res.append(None)
            continue
        k0 = min(first)
        s = cur + first[k0]
        e = cur + last[max(last)]
        # The leader chants each line before the group repeats it. If the first line was
        # matched to the repeat, the leader's copy sits just before it: look back for it.
        d0 = last[k0] - first[k0]
        lo = max(prev_e + 5, s - int(2.5 * d0) - 100)
        if s - lo > len(chunks[k0]) + 20:
            f2, l2, sc2, _ = align_verse(lp[lo:s], [chunks[k0]])
            if f2 and sc2 >= 0.6 * csc[k0] and (l2[0] - f2[0]) > 0.5 * d0:
                s = lo + f2[0]
        prev_e = e
        if os.environ.get("AVV_DEBUG"): print(v["verse_number"], round(s / FPS, 1), round(e / FPS, 1), [len(c) for c in chunks], flush=True)
        res.append({"v": "%d.%d" % (ch, v["verse_number"]), "s": s, "e": e, "score": score,
                    "d_last": last[max(last)] - first[max(last)]})
        cur = e + 5
    # clip boundaries: from a pause just before this verse to a pause just before the next
    out = {}
    for i, r in enumerate(res):
        if r is None:
            continue
        a = silence_snap(energy, r["s"] - 8, r["s"] - 20, r["s"] - 1)
        if i + 1 < len(res) and res[i + 1]:
            nxt = res[i + 1]["s"]
            b = silence_snap(energy, nxt - 8, max(r["e"] + 5, nxt - 20), nxt - 1)
        else:
            # last verse: the group repeats the final line, then the closing line begins
            # last verse: the group repeats the final line, then "om tat sat ..." closes
            # the chapter. Find the closing line and cut in the pause before it.
            om = [DICT[c] for c in "omtatsat"]
            hi2 = min(T, r["e"] + 25 * FPS)
            f2, _, sc2, _ = align_verse(lp[r["e"]:hi2], [om])
            if f2 and sc2 > 0.15:
                nxt = r["e"] + f2[0]
                b = silence_snap(energy, nxt - 8, nxt - 20, nxt - 1)
            else:
                b = min(T - 1, r["e"] + r["d_last"] + 25)
                b = silence_snap(energy, b, b - 40, b + 40)
        out[r["v"]] = {"start": round(a / FPS, 2), "end": round(b / FPS, 2),
                       "lead_end": round(r["e"] / FPS, 2), "score": round(r["score"], 3)}
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    chs = [int(c) for c in sys.argv[3].split(",")] if len(sys.argv) > 3 else range(1, 19)
    data = json.load(open(os.path.join(HERE, "..", "src-data", "data", "verse.json"), encoding="utf-8"))
    res = json.load(open(dst)) if os.path.exists(dst) else {}
    for ch in chs:
        vs = sorted([v for v in data if v["chapter_number"] == ch], key=lambda v: v["verse_number"])
        res.update(run_chapter(os.path.join(src, "BGChapter%d.opus" % ch), ch, vs))
        json.dump(res, open(dst, "w"), indent=0)
        print("chapter", ch, "done", flush=True)


if __name__ == "__main__":
    main()
