import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
# quirky pizzicato bed (stops at the removal for drama)
BT = 60 / 112
prog = [[48, 55, 64], [45, 52, 60], [41, 48, 57], [43, 50, 59]]
t = 0.0; k = 0
while t < R.T_REMOVE - 0.1:
    ch = prog[(k // 8) % 4]
    m.add(t, pluck(mtof(ch[0]), 0.4, bright=0.4), gain=0.32)
    if k % 2 == 1: m.add(t, pluck(mtof(ch[1 + (k // 2) % 2] + 12), 0.3, bright=0.5), gain=0.14, pan=0.3)
    if k % 4 == 2: m.add(t, hat(0.05), gain=0.08)
    t += BT / 2; k += 1
# after removal: slow sad pad
m.add(R.T_REMOVE + 0.2, pad([mtof(x) for x in [45, 52, 57, 60]], R.DUR - R.T_REMOVE, a=1.0, r=2.0, lp=1200, seed=4), gain=0.6, verb=0.5)
def pop_in():
    t_ = tt(0.09); f = 600 + 900 * np.exp(-t_ / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ / 0.03)
def pop_out():
    t_ = tt(0.12); f = 900 + 700 * (t_ / 0.12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ / 0.04)
for it in R.items:
    if it["kind"] == "msg":
        if it["t"] > 0.1: m.add(it["t"], pop_out() if it["me"] else pop_in(), gain=0.45 if it["me"] else 0.5, verb=0.15)
        if it["t_typing"] > 0 and it["t"] - it["t_typing"] > 0.1:
            for j in range(int((it["t"] - it["t_typing"]) / 0.12)):
                m.add(it["t_typing"] + j * 0.12, click(3000, 0.006), gain=0.05)
    elif it["kind"] == "sys":
        if it["text"].startswith("IAU removed"):
            m.add(it["t"], sub_boom(1.8, 40), gain=0.9)
            # sad trombone-ish descending (original, generic)
            for j, n_ in enumerate([62, 61, 60, 59]):
                m.add(it["t"] + 0.15 + j * 0.32, pulse(mtof(n_ - 12), 0.34 if j < 3 else 1.0, duty=0.4, lp=1500), gain=0.25, verb=0.3)
        else:
            m.add(it["t"], bell(mtof(57), 1.5, 0.6), gain=0.2, verb=0.5)
m.add(R.T_CTA, bell(mtof(76), 2.0, 0.8), gain=0.25, verb=0.6); m.add(R.T_CTA + 0.1, bell(mtof(81), 2.0, 0.8), gain=0.2, verb=0.6)
m.render("v012.wav", rt=2.0)
