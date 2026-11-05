"""Forced-alignment recitation scorer.

We already know the verse, so instead of transcribing (which turns Sanskrit
into Hindi-sounding guesses) we ask a multilingual CTC acoustic model how
well the audio supports each expected word, in order.

Score per word = goodness of pronunciation: the average log-probability of
the word's letters along the forced path, compared with the best the model
could do on those same frames unconstrained. A word that was said scores
near 0; a skipped or wrong word scores far below it.
"""
import re
import shutil
import subprocess

import numpy as np
import torch
import torchaudio

BUNDLE = torchaudio.pipelines.MMS_FA
_model = None
DICT = BUNDLE.get_dict()

# ---- Devanagari to plain roman letters the model knows (a-z) ----
VOW = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu", "ऋ": "ri",
       "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"}
SIGN = {"ा": "aa", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu", "ृ": "ri",
        "े": "e", "ै": "ai", "ो": "o", "ौ": "au"}
CONS = {"क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "c", "छ": "ch",
        "ज": "j", "झ": "jh", "ञ": "n", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh",
        "ण": "n", "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p",
        "फ": "ph", "ब": "b", "भ": "bh", "म": "m", "य": "y", "र": "r", "ल": "l",
        "व": "v", "श": "sh", "ष": "sh", "स": "s", "ह": "h"}
VIRAMA, ANUSVARA, CANDRA, VISARGA, AVAGRAHA = "्", "ं", "ँ", "ः", "ऽ"


def roman(word):
    out, i = [], 0
    w = re.sub(r"[़]", "", word)
    while i < len(w):
        c = w[i]
        if c in CONS:
            out.append(CONS[c])
            nxt = w[i + 1] if i + 1 < len(w) else ""
            if nxt == VIRAMA:
                i += 1
            elif nxt in SIGN:
                out.append(SIGN[nxt]); i += 1
            else:
                out.append("a")
        elif c in VOW:
            out.append(VOW[c])
        elif c in (ANUSVARA, CANDRA):
            out.append("m")
        elif c == VISARGA:
            out.append("h")
        i += 1
    return "".join(out)


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg  # bundled static ffmpeg for machines without one (local runs)
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_audio(path_or_bytes):
    args = [ffmpeg(), "-v", "quiet", "-i", "pipe:0" if isinstance(path_or_bytes, bytes) else path_or_bytes,
            "-f", "s16le", "-ac", "1", "-ar", str(BUNDLE.sample_rate), "-"]
    raw = subprocess.run(args, input=path_or_bytes if isinstance(path_or_bytes, bytes) else None, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def model():
    global _model
    if _model is None:
        _model = BUNDLE.get_model(with_star=False).eval()
    return _model


def viterbi(logp, tokens, blank=0):
    """CTC forced alignment. Returns, for each token index, the frames it covers."""
    T, S = logp.shape[0], 2 * len(tokens) + 1
    ext = [blank] * S
    for k, t in enumerate(tokens):
        ext[2 * k + 1] = t
    NEG = -1e30
    dp = np.full((T, S), NEG, dtype=np.float64)
    bp = np.zeros((T, S), dtype=np.int8)
    dp[0, 0] = logp[0, ext[0]]
    if S > 1:
        dp[0, 1] = logp[0, ext[1]]
    for t in range(1, T):
        prev = dp[t - 1]
        a = prev
        b = np.concatenate([[NEG], prev[:-1]])
        c = np.concatenate([[NEG, NEG], prev[:-2]])
        allow_skip = np.array([s % 2 == 1 and s >= 2 and ext[s] != ext[s - 2] for s in range(S)])
        c = np.where(allow_skip, c, NEG)
        stack = np.stack([a, b, c])
        choice = stack.argmax(0)
        dp[t] = stack.max(0) + logp[t, ext]
        bp[t] = choice
    s = S - 1 if S == 1 or dp[T - 1, S - 1] >= dp[T - 1, S - 2] else S - 2
    frames = [[] for _ in tokens]
    for t in range(T - 1, -1, -1):
        if s % 2 == 1:
            frames[s // 2].append(t)
        s -= int(bp[t, s])
    return frames


def score(words, audio):
    """words: Devanagari words in order. audio: float32 mono at 16 kHz."""
    wav = torch.from_numpy(audio).unsqueeze(0)
    with torch.inference_mode():
        emission, _ = model()(wav)
    logp = torch.log_softmax(emission[0], dim=-1).numpy()
    best = logp.max(1)
    romans = [roman(w) for w in words]
    tokens, owner = [], []
    for wi, r in enumerate(romans):
        for ch in r:
            if ch in DICT:
                tokens.append(DICT[ch]); owner.append(wi)
    frames = viterbi(logp, tokens)
    sec_per_frame = len(audio) / BUNDLE.sample_rate / logp.shape[0]
    per = [{"gop": [], "frames": []} for _ in words]
    for k, fr in enumerate(frames):
        if not fr:
            per[owner[k]]["gop"].append(-10.0)
            continue
        g = np.mean([logp[t, tokens[k]] - best[t] for t in fr])
        per[owner[k]]["gop"].append(float(g))
        per[owner[k]]["frames"].extend(fr)
    out = []
    for w, r, p in zip(words, romans, per):
        g = float(np.mean(p["gop"])) if p["gop"] else -10.0
        fr = p["frames"]
        out.append({"word": w, "roman": r, "gop": round(g, 2),
                    "start": round(min(fr) * sec_per_frame, 2) if fr else None,
                    "end": round((max(fr) + 1) * sec_per_frame, 2) if fr else None})
    return out
