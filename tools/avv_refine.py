"""Second pass for verses whose clip doesn't open with the verse's first words.

Each pada is chanted twice (leader, then group), so we align the first pada twice in a
row, starting just after the previous verse's last matched letter. The earlier copy is
the leader's, and the clip starts in the pause before it. The previous clip's end moves
to the same pause.

    python3 tools/avv_refine.py <dir with .opus and .lp.npy> <times.json> <verse,verse,...>
"""
import json
import os
import sys

import numpy as np
import torch
import torchaudio

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import avv_align as A  # noqa: E402

FPS = A.FPS


def first_letter(lp, c0):
    """Where the leader's copy of the first pada really begins. The aligner may park the
    first letter or two on a stray frame well before the rest; skip letters that sit
    more than 0.3 s before the next one."""
    star = A.DICT["*"]
    seq = [star] + c0 + [star] + c0 + [star]
    ali, sc = torchaudio.functional.forced_align(lp.unsqueeze(0), torch.tensor([seq], dtype=torch.int32), blank=0)
    sp = torchaudio.functional.merge_tokens(ali[0], sc[0].exp())
    sp = sp[1:1 + len(c0)]
    i = 0
    while i < min(4, len(sp) - 1) and sp[i + 1].start - sp[i].end > 15:
        i += 1
    return sp[i].start


def main():
    src, times, which = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    T = json.load(open(times))
    data = json.load(open(os.path.join(HERE, "..", "src-data", "data", "verse.json"), encoding="utf-8"))
    by = {"%d.%d" % (v["chapter_number"], v["verse_number"]): v for v in data}
    order = sorted(T, key=lambda k: tuple(map(int, k.split("."))))
    cache = {}
    for vid in which:
        ch = int(vid.split(".")[0])
        if ch not in cache:
            path = os.path.join(src, "BGChapter%d.opus" % ch)
            lp = torch.from_numpy(np.load(path + ".lp.npy").astype(np.float32))
            audio = A.align.load_audio(path)
            n = lp.shape[0]
            fr = audio[: n * A.SR // FPS].reshape(n, -1)
            en = np.convolve(np.log10((fr ** 2).mean(1) + 1e-8), np.ones(5) / 5, "same")
            cache = {ch: (lp, en)}
        lp, en = cache[ch]
        k = order.index(vid)
        prev = order[k - 1] if k and order[k - 1].split(".")[0] == str(ch) else None
        lo = max(int((T[prev]["lead_end"] if prev else 0) * FPS) + 5, int(T[vid]["start"] * FPS) - 25)
        hi = min(lp.shape[0], int(T[vid]["start"] * FPS) + 15 * FPS)
        c0 = A.lines(by[vid]["text"])[0]
        st = first_letter(lp[lo:hi], c0)
        if st is None:
            print(vid, "no match")
            continue
        s = lo + st
        sc = 0
        a = A.silence_snap(en, s - 8, s - 20, s - 1)
        old = T[vid]["start"]
        T[vid]["start"] = round(a / FPS, 2)
        if prev:
            T[prev]["end"] = T[vid]["start"]
        print(vid, "start", old, "->", T[vid]["start"], "score", round(sc, 3))
    json.dump(T, open(times, "w"), indent=0)


if __name__ == "__main__":
    main()
