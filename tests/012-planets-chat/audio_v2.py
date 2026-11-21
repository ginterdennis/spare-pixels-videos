"""012 v2 score: the cold open replays v1's score around the removal (boom + sad trombone),
a hook-kit hit on frame 0, a tape-rewind sweep, then v1's score from v1-time 3.0 onwards."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy.io import wavfile
from kit import *
import render_v2 as R

sr, v1 = wavfile.read("v012.wav")          # run audio.py (v1) first
assert sr == SR
v1 = v1.astype(np.float64) / 32767
m = Mix(R.DUR)
seg = v1[int(R.COLD0 * SR): int((R.COLD0 + R.RW0) * SR)].copy()
seg[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))[:, None]
m.add(0.0, seg, gain=1.0)
m.add(0.0, sub_boom(0.6, 55), gain=0.35); m.add(0.0, click(1800, 0.03), gain=0.3)
# rewind: fast descending warble
d = R.RW1 - R.RW0 + 0.1; t_ = tt(d)
f = 1800 * (0.15 ** (t_ / d)) * (1 + 0.15 * np.sin(2 * np.pi * 23 * t_))
m.add(R.RW0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t_ / d), gain=0.22)
m.add(R.RW0, whoosh(d, 4000, 300), gain=0.3)
main = v1[int(R.V1START * SR):].copy()
main[: int(0.08 * SR)] *= np.linspace(0, 1, int(0.08 * SR))[:, None]
m.add(R.RW1, main, gain=1.0)
m.render("v012v2.wav", rt=1.2)
print("ok")
