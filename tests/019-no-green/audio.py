import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R

m = Mix(R.DUR)
ROT = 12 * R.STEP / 30          # one full rotation = 1.6 s
# hypnotic drone during the stare
m.add(0.0, pad([mtof(x) for x in [41, 48, 53, 60]], R.T_STOP + 0.4, a=1.2, r=0.5, lp=900, seed=3), gain=0.9, verb=0.4)
m.add(0.0, pad([mtof(x) for x in [65, 72]], R.T_STOP + 0.4, a=3.0, r=0.5, lp=2400, seed=7), gain=0.25, verb=0.5)
# one soft tone per rotation, a slow 4-note cycle
cyc = [77, 72, 74, 69]
k = 0; t = 0.0
while t < R.T_STOP:
    m.add(t, bell(mtof(cyc[k % 4]), 1.6, 0.45), gain=0.07, pan=(-0.3 if k % 2 else 0.3), verb=0.5)
    k += 1; t += ROT
# hook: gentle chime
for j, n in enumerate([84, 89]):
    m.add(0.05 + j * 0.09, bell(mtof(n), 1.4, 0.5), gain=0.12, verb=0.5)
# stop: shimmer + low hit
m.add(R.T_STOP, sub_boom(1.4, 44), gain=0.6)
for j, n in enumerate([65, 72, 77, 81, 84]):
    m.add(R.T_STOP + j * 0.05, bell(mtof(n), 2.6, 1.0), gain=0.11, verb=0.6)
m.add(R.T_STOP, pad([mtof(x) for x in [53, 60, 65, 69, 72]], R.DUR - R.T_STOP, a=0.8, r=1.5, lp=2200, seed=5), gain=0.6, verb=0.5)
m.add(R.T_CTA, pluck(mtof(81), 0.8), gain=0.3, verb=0.4); m.add(R.T_CTA + 0.12, pluck(mtof(88), 0.8), gain=0.3, verb=0.4)
m.render("v019.wav", rt=2.4)
print("ok")
