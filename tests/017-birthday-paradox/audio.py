import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R

m = Mix(R.DUR)
B = 0.5  # 120 bpm
prog = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]  # C Am F G
t = 0.0; k = 0
while t < R.DUR:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 2.2, a=0.3, r=0.6, lp=1600, seed=k), gain=0.5, verb=0.35)
    t += 2.0; k += 1
x = 0.5
while x < R.DUR - 0.6:
    quiet = (R.T_WHY - 0.1 <= x < R.T_LINES1 + 0.6)
    if not quiet:
        m.add(x, kick(), gain=0.45)
    m.add(x + B / 2, hat(), gain=0.10 if not quiet else 0.05, pan=0.3)
    x += B

PENTA = [72, 74, 76, 79, 81, 84, 86, 88]
rng = np.random.default_rng(4)
for k, a in enumerate(R.ARR):
    n = PENTA[int(rng.integers(0, len(PENTA)))]
    g = 0.26 if k < 23 else 0.14
    m.add(a + R.FALL * 0.8, pluck(mtof(n), 0.5, 0.55), gain=g, pan=float(rng.uniform(-0.5, 0.5)), verb=0.25)

# matches
for idx, (k, p) in enumerate(sorted(R.MATCH_AT.items())):
    tm = R.ARR[k] + R.FALL
    first = (k == R.FIRST)
    for j, n in enumerate([84, 88, 91, 96] if first else [88, 93]):
        m.add(tm + j * 0.05, bell(mtof(n), 1.8, 0.6), gain=0.16 if first else 0.09, verb=0.5)
    if first:
        m.add(tm, sub_boom(1.2, 48), gain=0.6)
# reaching 23
m.add(R.ARR[22] + R.FALL, bell(mtof(79), 1.2, 0.4), gain=0.1, verb=0.4)

# pairs: whoosh in, ticks while lines draw, riser, pink line
m.add(R.T_WHY - 0.2, whoosh(1.0, 2500, 300), gain=0.3)
for j in range(0, 253, 8):
    u = j / 253
    tl = R.T_LINES0 + (R.T_LINES1 - R.T_LINES0) * (np.arccos(1 - 2 * u) / np.pi)  # inverse of smoothstep approx
    m.add(float(tl), click(1600 + 8 * j, 0.015), gain=0.18, pan=float(np.sin(j)))
m.add(R.T_LINES0, riser(R.T_LINES1 - R.T_LINES0, 200, 1500), gain=0.3)
for n in [76, 83, 88]:
    m.add(R.T_LINES1 + 0.2, bell(mtof(n), 1.6, 0.6), gain=0.13, verb=0.5)
m.add(R.T_BACK - 0.3, whoosh(0.9, 300, 2500), gain=0.25)

# 70 people reached
m.add(R.T_P70 + R.FALL, sub_boom(1.6, 40), gain=0.75)
for n in [60, 67, 72, 76, 79, 84]:
    m.add(R.T_P70 + R.FALL, bell(mtof(n), 2.6, 1.0), gain=0.11, verb=0.7)
m.add(R.T_CTA, pluck(mtof(84), 0.8), gain=0.3, verb=0.4)
m.add(R.T_CTA + 0.12, pluck(mtof(91), 0.8), gain=0.3, verb=0.4)
m.render("v017.wav", rt=2.0)
print("ok")
