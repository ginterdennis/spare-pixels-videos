import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R

m = Mix(R.DUR)
BPM = 120; B = 60 / BPM
# chords (Am F C G), 2 bars of 2 beats each... one chord per 2 s
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
t = 0.0; k = 0
while t < R.DUR:
    ch = prog[k % 4]
    m.add(t, pad([mtof(x) for x in ch], 2.2, a=0.3, r=0.6, lp=1500, seed=k), gain=0.55, verb=0.35)
    # arpeggio plucks on 8ths
    for j in range(4):
        n = ch[[0, 2, 1, 3][j]] + 12
        m.add(t + j * B / 2 * 2, pluck(mtof(n), 0.6, 0.5), gain=0.10, pan=(-0.4 if j % 2 else 0.4), verb=0.3)
    t += 2.0; k += 1

# drums from the grid onwards, drop out for reveals
def drum_ok(x):
    return x >= R.T_GRID and not (R.T_BR <= x < R.T_BR + 0.9) and not (R.T_TR <= x < R.T_TR + 1.2) and x < R.DUR - 0.6
x = 0.0
while x < R.DUR:
    if drum_ok(x):
        m.add(x, kick(), gain=0.55)
        m.add(x + B / 2, hat(), gain=0.12, pan=0.3)
    x += B

# hook: coin chime
for j, n in enumerate([88, 93, 96]):
    m.add(0.05 + j * 0.07, bell(mtof(n), 1.6, 0.5), gain=0.14, verb=0.5)

# million: tick per cell
prev = 0
for i in range(int(R.T_M0 * 600), int(R.T_Z0 * 600)):
    tt_ = i / 600; c = int(R.cells_filled(tt_))
    if c > prev:
        m.add(tt_, click(2200 + 90 * c, 0.02), gain=0.35, verb=0.2); prev = c
m.add(R.T_M1, sub_boom(1.0, 55), gain=0.45)
for n in [81, 85, 88]:
    m.add(R.T_M1, bell(mtof(n), 1.6, 0.6), gain=0.12, verb=0.5)

# billion: whoosh, year ticks, riser
m.add(R.T_Z0 - 0.1, whoosh(1.6, 200, 3000), gain=0.35)
prev = 0
for i in range(int(R.T_Z0 * 600), int(R.T_B1 * 600)):
    tt_ = i / 600; y = int(R.cells_filled(tt_) / 365.25)
    if y > prev:
        m.add(tt_, click(1800 + 40 * y, 0.02), gain=0.22, pan=(-0.3 if y % 2 else 0.3)); prev = y
m.add(R.T_B1 - 2.4, riser(2.4, 220, 1800), gain=0.35)
m.add(R.T_BR, sub_boom(1.6, 42), gain=0.75)
for n in [69, 76, 81, 85, 88]:
    m.add(R.T_BR, bell(mtof(n), 2.4, 0.9), gain=0.12, verb=0.6)

# trillion: shrink whoosh, tile ticks per row, riser, big reveal
m.add(R.T_S0, whoosh(1.4, 3000, 250), gain=0.35)
prev = 0
for i in range(int(R.T_S1 * 600), int(R.T_T1 * 600)):
    tt_ = i / 600; r = int(R.tiles_filled(tt_) // 32)
    if r > prev:
        m.add(tt_, click(1500 + 60 * r, 0.02), gain=0.25, pan=(-0.3 if r % 2 else 0.3)); prev = r
m.add(R.T_T1 - 3.0, riser(3.0, 180, 2400), gain=0.4)
m.add(R.T_TR, sub_boom(2.0, 38), gain=0.9)
for n in [57, 64, 69, 73, 76, 81]:
    m.add(R.T_TR, bell(mtof(n), 3.0, 1.2), gain=0.12, verb=0.7)

# CTA
m.add(R.T_CTA, pluck(mtof(81), 0.8), gain=0.3, verb=0.4)
m.add(R.T_CTA + 0.12, pluck(mtof(88), 0.8), gain=0.3, verb=0.4)
m.render("v016.wav", rt=2.0)
print("ok")
