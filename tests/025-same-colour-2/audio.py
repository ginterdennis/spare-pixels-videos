"""025 score: 018's Dm-Bb-C-A pad and light groove (the sound that went with the best video),
plus the hook kit's frame-0 hit, a sting on each reveal and whooshes between rounds."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render as R

m = Mix(R.DUR)
B = 60 / 112
prog = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 61]]  # Dm Bb C A
t = 0.0; k = 0
while t < R.DUR:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 4 * B + 0.2, a=0.05, r=0.5, lp=1400, seed=k), gain=0.5, verb=0.3)
    t += 4 * B; k += 1
x = 0.0; n = 0
mel = [74, 77, 81, 77, 76, 74, 72, 69]
while x < R.DUR - 0.5:
    near = any(rv - 0.05 <= x < rv + 0.6 for rv in (R.REV1, R.REV2, R.REV3, R.RC))
    if not near and x >= 0.15:
        if n % 2 == 0: m.add(x, kick(), gain=0.4)
        m.add(x + B / 2, hat(), gain=0.09, pan=0.3)
        m.add(x, tri(mtof(mel[n % 8]), 0.16), gain=0.07, pan=-0.2, verb=0.2)
    x += B; n += 1
hook_sfx(m, reveal=R.REV1)                       # hit at 0.00 s, riser + boom at the first payoff
for tb in (R.R2, R.R3):
    m.add(tb - 0.35, whoosh(0.6, 400, 4000), gain=0.3)
for rv in (R.REV2, R.REV3):
    m.add(rv - 0.5, riser(0.5, 400, 1600), gain=0.2)
    m.add(rv, sub_boom(1.0, 50), gain=0.6)
    for j, nn in enumerate([81, 86, 89, 93]):
        m.add(rv + j * 0.045, bell(mtof(nn), 1.4, 0.5), gain=0.12, verb=0.5)
m.add(R.BACK1, whoosh(0.5, 3000, 600), gain=0.2)                # stripes slide back
m.add(R.REV2 - 0.6, whoosh(0.5, 300, 1500), gain=0.18)           # thumb slides up
m.add(R.RC, pluck(mtof(81), 0.8), gain=0.3, verb=0.4); m.add(R.RC + 0.12, pluck(mtof(86), 0.8), gain=0.3, verb=0.4)
m.render("v025.wav", rt=1.8)
print("ok")
