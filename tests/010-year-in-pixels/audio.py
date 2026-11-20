import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
# ticking clock bed while the year fills
SC = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98]
last = -1
for k, t in enumerate(R.LT):
    t = max(0.0, t)
    if t - last < 0.045 and k != R.NT - 1: continue
    last = t
    mo = R.DAYS[k].month - 1
    m.add(t, click(2200 + mo * 120, 0.012), gain=0.18, pan=((k % R.COLS) / R.COLS - 0.5))
    if R.DAYS[k].day == 1:
        m.add(t, pluck(mtof(SC[mo] - 12), 0.9), gain=0.45, verb=0.4)
m.add(0, riser(R.T_TODAY, 180, 900), gain=0.18, verb=0.2)
m.add(0.0, pad([mtof(x) for x in [45, 52, 57, 60, 64]], R.T_TODAY + 0.3, a=0.8, r=0.3, lp=1400, seed=3), gain=0.5, verb=0.4)
# today hit
m.add(R.T_TODAY, sub_boom(1.6, 42), gain=0.8)
for n_ in [69, 76, 81, 88]:
    m.add(R.T_TODAY, bell(mtof(n_), 3.0, 1.1), gain=0.16, verb=0.6)
# heartbeat clock for the remaining 41
t = R.T_TODAY + 0.8
while t < R.DUR - 0.5:
    m.add(t, kick(0.3), gain=0.3); m.add(t + 0.25, kick(0.25), gain=0.18)
    t += 1.2
for k in range(R.LEFT):
    tt_ = R.T_LEFT + k * 0.03
    if k % 2 == 0: m.add(tt_, bell(mtof(84 + (k % 7)), 0.6, 0.2), gain=0.05, verb=0.5)
m.add(R.T_TODAY + 0.2, pad([mtof(x) for x in [41, 48, 53, 57, 60, 64]], R.DUR - R.T_TODAY, a=1.0, r=2.0, lp=1800, seed=8), gain=0.6, verb=0.5)
m.add(R.T_CTA, pluck(mtof(76), 0.8), gain=0.35, verb=0.4); m.add(R.T_CTA + 0.12, pluck(mtof(81), 0.8), gain=0.35, verb=0.4)
m.render("v010.wav", rt=2.4)
