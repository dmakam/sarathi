"""Compute and cache the aligner's emissions for every chapter (the slow part)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import avv_align as A
src = sys.argv[1]
for n in list(range(1, 19)):
    p = os.path.join(src, "BGChapter%d.opus" % n)
    if os.path.exists(p + ".lp.npy"):
        continue
    lp = A.emissions(A.align.load_audio(p))
    np.save(p + ".lp.npy", lp.numpy().astype(np.float16))
    print("chapter", n, "cached", flush=True)
