import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
# low hypnotic drone during the stare
m.add(0.0, pad([mtof(x) for x in [38, 45, 50, 57]], R.T_SWITCH + 0.3, a=1.5, r=0.4, lp=900, seed=2), gain=0.9, verb=0.4)
# soft ticks each second, slightly louder in the last 3
def wood(f=1300):
    t = tt(0.08); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.018) + 0.3 * np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t / 0.008)
for s in range(1, int(R.T_SWITCH)):
    g = 0.22 if s < R.T_SWITCH - 3 else 0.38
    m.add(float(s), wood(1300 if s < R.T_SWITCH - 3 else 1700), gain=g, verb=0.2)
# switch: gentle shimmer (not startling)
for k, n in enumerate([74, 78, 81, 86]):
    m.add(R.T_SWITCH + k * 0.06, bell(mtof(n), 3.0, 1.0), gain=0.12, verb=0.7)
m.add(R.T_SWITCH, pad([mtof(x) for x in [50, 57, 62, 66, 69]], R.DUR - R.T_SWITCH, a=1.0, r=2.0, lp=2200, seed=5), gain=0.7, verb=0.5)
# reveal sting
m.add(R.T_TXT2, sub_boom(1.6, 42), gain=0.7)
for n in [62, 69, 74, 78]:
    m.add(R.T_TXT2, bell(mtof(n), 3.0, 1.2), gain=0.16, verb=0.6)
m.add(25.5, pluck(mtof(74), 0.8), gain=0.3, verb=0.4); m.add(25.62, pluck(mtof(81), 0.8), gain=0.3, verb=0.4)
m.render("v006.wav", rt=2.4)
