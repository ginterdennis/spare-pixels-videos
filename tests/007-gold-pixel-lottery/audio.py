import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
# hook ding
for n_ in [84, 91]:
    m.add(0.12, bell(mtof(n_), 2.5, 0.9), gain=0.3, verb=0.5)
m.add(0.0, pad([mtof(x) for x in [45, 52, 57, 60, 64]], R.C_END + 0.5, a=0.8, r=1.0, lp=1300, seed=1), gain=0.6, verb=0.4)
m.add(R.C_END - 0.2, pad([mtof(x) for x in [41, 48, 53, 57, 60]], R.D_END - R.C_END + 0.6, a=0.8, r=0.8, lp=1500, seed=2), gain=0.6, verb=0.4)
m.add(R.D_END + 0.3, pad([mtof(x) for x in [36, 43, 48, 52, 55, 62]], R.DUR - R.D_END, a=0.4, r=3.0, lp=2400, seed=3), gain=0.7, verb=0.5)
# zoom whooshes / risers
m.add(R.A_END, riser(R.B_END - R.A_END, 120, 900), gain=0.32, verb=0.3)
m.add(R.A_END, whoosh(R.B_END - R.A_END, 200, 3000, seed=4), gain=0.25)
m.add(R.C_END, riser(R.D_END - R.C_END, 150, 1200), gain=0.3, verb=0.3)
m.add(R.C_END, whoosh(R.D_END - R.C_END, 250, 4000, seed=5), gain=0.25)
# heartbeat pulse during zooms
t = R.A_END
while t < R.D_END:
    if not (R.B_END + 0.3 < t < R.C_END):
        m.add(t, kick(0.35), gain=0.45); m.add(t + 0.22, kick(0.3), gain=0.25)
    t += 1.0
# powers of ten -> ascending notes
notes = [60, 62, 64, 67, 69, 72, 74, 76, 79]
ts = np.arange(0, R.DUR, 1 / 120)
cnt = np.array([R.count_at(x) for x in ts])
for p in range(2, 9):
    hit = np.where(cnt >= 10 ** p)[0]
    if len(hit):
        tp = ts[hit[0]]
        m.add(tp, pluck(mtof(notes[p - 1] + 12), 1.0), gain=0.45, verb=0.4)
        m.add(tp, bell(mtof(notes[p - 1] + 24), 1.2, 0.4), gain=0.12, verb=0.5)
# lock at one screen
m.add(R.B_END, kick(0.6), gain=0.9); m.add(R.B_END, sub_boom(1.2, 45), gain=0.6)
m.add(R.B_END, bell(mtof(79), 2.0, 0.8), gain=0.22, verb=0.6)
# final reveal
T = R.D_END + 0.5
m.add(T, sub_boom(2.0, 38), gain=0.9)
for n_ in [60, 67, 72, 76, 79, 84]:
    m.add(T + (n_ - 60) * 0.01, bell(mtof(n_), 3.5, 1.4), gain=0.16, verb=0.7)
m.add(R.D_END + 3.0, pluck(mtof(72), 0.8), gain=0.3, verb=0.4)
m.render("v007.wav", rt=2.4)
