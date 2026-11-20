import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
BPM = 120; BT = 0.5; BAR = 2.0
prog = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [53, 57, 60]), (43, [55, 59, 62])]
t = 0.0; b = 0
while t < R.DUR - 0.3:
    root, ch = prog[b % 4]
    for k in range(4):
        m.add(t + k * BT, tri(mtof(root), BT * 0.9), gain=0.30)
        m.add(t + k * BT + BT / 2, tri(mtof(root + 12), BT * 0.4), gain=0.18)
    for k in range(8):
        n_ = ch[k % 3] + 12
        m.add(t + k * BT / 2, pulse(mtof(n_), 0.12, duty=0.125), gain=0.05, pan=0.3)
    for k in range(4):
        m.add(t + k * BT, kick(0.25), gain=0.32)
        if k % 2 == 1: m.add(t + k * BT, hat(0.1, seed=k), gain=0.12)
    t += BAR; b += 1
# loading bar blips
for s in range(20):
    tt_ = 0.15 + (R.T_LOAD1 - 0.4) * (1 - (1 - (s + 1) / 20) ** 0.5)
    m.add(tt_, pulse(mtof(60 + s), 0.05, duty=0.5), gain=0.12)
m.add(R.T_LOAD1, pulse(mtof(84), 0.08, duty=0.5), gain=0.2); m.add(R.T_LOAD1 + 0.08, pulse(mtof(91), 0.15, duty=0.5), gain=0.2)
# items
for kind, txt, col, t0, t1, hh in R.items:
    if kind == "tag":
        m.add(t0, pulse(mtof(83), 0.07, duty=0.5), gain=0.22); m.add(t0 + 0.07, pulse(mtof(88), 0.22, duty=0.5), gain=0.22)
    elif kind == "line":
        n = sum(len(x) for x in txt)
        for c in range(0, n, 2):
            m.add(t0 + c / R.CPS, pulse(1100 + 300 * ((c * 7) % 5) / 5, 0.022, duty=0.5, rel=0.01), gain=0.06)
    elif kind == "done":
        for k, n_ in enumerate([72, 76, 79, 84, 88]):
            m.add(t0 + k * 0.09, pulse(mtof(n_), 0.16, duty=0.25), gain=0.25)
        m.add(t0 + 0.6, pulse(mtof(91), 0.4, duty=0.25), gain=0.2)
m.render("v011.wav", rt=1.2)
