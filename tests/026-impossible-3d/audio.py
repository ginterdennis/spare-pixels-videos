"""026 score: 120 BPM (cuts at 7.0 / 14.5 / 21.5 s and the 24.0 s loop all land on beats),
Am-F-C-G pad + pluck arpeggio, groove ducked around every reveal, one sound per visual event."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render as R

m = Mix(R.DUR)
B = 0.5
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]   # Am F C G
arp = [[69, 72, 76, 72], [69, 72, 77, 72], [67, 72, 76, 72], [67, 71, 74, 71]]
QUIET = [(R.REV - 0.5, R.REV + 0.6), (R.SNAP - 0.2, R.SNAP + 0.5), (R.GREW - 0.1, R.GREW + 0.6),
         (R.TURN1 - 0.1, R.TURN1 + 0.6), (R.CUT4 - 0.05, R.CUT4 + 0.4)]


def quiet(x):
    return any(a <= x < b for a, b in QUIET)


t = 0.0; k = 0
while t < R.DUR - 0.01:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 4 * B + 0.25, a=0.08, r=0.5, lp=1600, seed=k), gain=0.42, verb=0.35)
    m.add(t, tri(mtof(prog[k % 4][0] - 12), 4 * B - 0.05, rel=0.2), gain=0.10)
    t += 4 * B; k += 1
x = 0.0; n = 0
while x < R.DUR - 0.2:
    bar = int(x // (4 * B))
    if x >= 0.2 and not quiet(x):
        if n % 4 == 0: m.add(x, kick(), gain=0.34)
        if n % 4 == 2: m.add(x, snare(), gain=0.07)
        m.add(x + B / 2, hat(), gain=0.05, pan=0.3)
        m.add(x, pluck(mtof(arp[bar % 4][n % 4]), 0.35, 0.5), gain=0.07, pan=-0.25 if n % 2 else 0.25, verb=0.25)
    x += B; n += 1

# 1. triangle
hook_sfx(m, reveal=R.REV, ticks=(0.0, 1.0, 2.0))
m.add(2.45, whoosh(0.85, 250, 3800), gain=0.30)
m.add(R.REV + 0.45, pluck(mtof(88), 0.4), gain=0.16, verb=0.3); m.add(R.REV + 0.57, pluck(mtof(84), 0.4), gain=0.14, verb=0.3)
m.add(R.BACK, whoosh(0.8, 3800, 300), gain=0.28)
m.add(R.SNAP, click(1500, 0.04), gain=0.55); m.add(R.SNAP, kick(0.3), gain=0.5)
for j, nn in enumerate([69, 76, 81, 88]):
    m.add(R.SNAP + j * 0.03, bell(mtof(nn), 1.3, 0.5), gain=0.11, verb=0.5)
# 2. Ames room
for c in R.CUTS:
    m.add(c - 0.28, whoosh(0.4, 500, 4500), gain=0.26)
    m.add(c, sub_boom(0.5, 55), gain=0.25)
d = R.ROLL1 - R.ROLL0
tr = tt(d)
rumble = signal.sosfilt(sos("lowpass", 260), noise(d, seed=7)) * (0.6 + 0.4 * np.sin(2 * np.pi * (2 + 4 * tr / d) * tr))
rumble *= np.minimum(1, tr / 0.25) * np.minimum(1, (d - tr) / 0.3) * (0.5 + tr / d)
m.add(R.ROLL0, rumble, gain=0.9)
f = 220 * 2 ** (1.6 * tr / d)                                           # rising "grow" tone
m.add(R.ROLL0, np.sin(2 * np.pi * np.cumsum(f) / SR) * (tr / d) ** 1.5 * 0.5, gain=0.12, verb=0.3)
m.add(R.GREW, kick(0.4), gain=0.55); m.add(R.GREW, sub_boom(1.0, 44), gain=0.6)
for j, nn in enumerate([76, 79, 84, 88]):
    m.add(R.GREW + j * 0.04, bell(mtof(nn), 1.1, 0.45), gain=0.10, verb=0.4)
m.add(R.LID, pluck(mtof(91), 0.25, 0.9), gain=0.25); m.add(R.LID, whoosh(2.0, 200, 3200), gain=0.24)
m.add(R.SAME + 0.1, bell(mtof(81), 1.6, 0.6), gain=0.18, verb=0.5); m.add(R.SAME + 0.22, bell(mtof(88), 1.6, 0.6), gain=0.16, verb=0.5)
# 3. ambiguous cylinder
d = R.TURN1 - R.TURN0
m.add(R.TURN0, riser(d, 300, 1400), gain=0.16); m.add(R.TURN0, whoosh(d, 300, 2500), gain=0.18)
m.add(R.TURN1 + 0.05, sub_boom(1.1, 46), gain=0.6); m.add(R.TURN1 + 0.05, snare(), gain=0.2)
for j, nn in enumerate([81, 84, 88, 93]):
    m.add(R.TURN1 + 0.05 + j * 0.04, bell(mtof(nn), 1.2, 0.45), gain=0.10, verb=0.4)
m.add(R.ORBIT, whoosh(1.2, 300, 2800), gain=0.24)
m.add(R.ORBIT + 0.3, pluck(mtof(76), 0.5), gain=0.2, verb=0.3); m.add(R.ORBIT + 0.42, pluck(mtof(72), 0.5), gain=0.2, verb=0.3)
# 4. CTA
for j, nn in enumerate([81, 88, 93]):
    m.add(R.CUT4 + 0.35 + j * 0.12, pluck(mtof(nn), 0.8), gain=0.24, verb=0.4)
m.render("v026.wav", rt=1.8)
print("ok")
