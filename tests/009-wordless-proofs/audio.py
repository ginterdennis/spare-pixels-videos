import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R
m = Mix(R.DUR)
BPM = 100; BT = 60 / BPM
# pads per segment
for (t0, t1), ch in [(R.P1, [48, 55, 60, 64]), (R.P2, [41, 53, 57, 60]), (R.P3, [45, 52, 57, 60]), (R.PE, [43, 50, 55, 59])]:
    m.add(t0, pad([mtof(x) for x in ch], t1 - t0 + 0.6, a=0.5, r=0.8, lp=1500, seed=int(t0)), gain=0.55, verb=0.4)
# groove
t = 0.0
while t < R.PE[1] - 0.5:
    b = round(t / BT)
    if b % 2 == 0: m.add(t, kick(0.35), gain=0.35)
    m.add(t, hat(), gain=0.09, pan=0.3); m.add(t + BT / 2, hat(), gain=0.06, pan=-0.3)
    t += BT
last = [-1.0]
def note(t, midi, g=0.32, pan=0.0):
    if t - last[0] < 0.035: return
    last[0] = t; m.add(t, pluck(mtof(midi), 0.7), gain=g, pan=pan, verb=0.35)
SC = [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]
# proof 1 cells
T = [-0.3] + [0.9 + k * 1.35 for k in range(4)]
for k in range(5):
    cells = 2 * k + 1
    for mm in range(cells):
        tt_ = R.P1[0] + max(0.0, T[k] + mm * 0.06)
        note(tt_, SC[min(10, k + mm // 2)], pan=(mm / max(1, cells - 1) - 0.5))
m.add(R.P1[0] + T[-1] + 1.6, bell(mtof(84), 2.0, 0.8), gain=0.25, verb=0.6)
# proof 2
for i in range(6):
    for k in range(i + 1):
        note(R.P2[0] + 0.4 + i * 0.42 + k * 0.05, SC[min(10, k + i)] - 7, pan=(i / 5 - 0.5))
m.add(R.P2[0] + 3.9, whoosh(1.7, 300, 3000), gain=0.35)
m.add(R.P2[0] + 5.6, kick(0.5), gain=0.7); m.add(R.P2[0] + 5.6, bell(mtof(72), 1.5, 0.6), gain=0.2, verb=0.5)
m.add(R.P2[0] + 8.2, bell(mtof(81), 2.0, 0.8), gain=0.25, verb=0.6)
# proof 3
m.add(R.P3[0] + 0.05, bell(mtof(69), 2.0, 0.8), gain=0.22, verb=0.6)
for key, (a_, b_) in R.MOVES.items():
    m.add(R.P3[0] + a_, whoosh(b_ - a_, 250, 2500, seed=hash(key) % 100), gain=0.3)
    m.add(R.P3[0] + b_, kick(0.4), gain=0.6); m.add(R.P3[0] + b_, click(1800, 0.02), gain=0.25)
for i in range(4):
    for j in range(4):
        if (i < 3 and j < 3) or True:
            note(R.P3[0] + 6.7 + (i + j) * 0.04, SC[min(10, i + j + 2)], g=0.22)
for n_ in [57, 64, 69, 72, 76]:
    m.add(R.P3[0] + 7.0, bell(mtof(n_ + 12), 3.0, 1.2), gain=0.13, verb=0.6)
m.add(R.P3[0] + 7.0, sub_boom(1.2, 45), gain=0.5)
# end badges
for k in range(3):
    m.add(R.PE[0] + 0.4 + k * 0.12, pluck(mtof([72, 76, 79][k]), 0.9), gain=0.4, verb=0.4)
m.render("v009.wav", rt=2.2)
