"""021 v2 score: v1's C-Am-F-G groove and card riffles, re-timed; hook kit hit on frame 0,
riffle already running at 0.0 s, stamp boom at NEVER."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import *
from hook import hook_sfx
import render_v2 as R
import audio_parts as AP

m = Mix(R.DUR)
B = 60 / 120
prog = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]
t = 0.0; k = 0
while t < R.DUR:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 4 * B + 0.2, a=0.05, r=0.5, lp=1500, seed=k), gain=0.48, verb=0.3)
    t += 4 * B; k += 1
x = 0.0; n = 0
mel = [72, 76, 79, 76, 74, 77, 81, 77]
rev = (R.NEVER, R.PCT, R.WF + 0.45)
while x < R.DUR - 0.4:
    if not any(rv - 0.05 <= x < rv + 0.55 for rv in rev) and x >= 0.2:
        if n % 4 == 0: m.add(x, kick(), gain=0.38)
        if n % 4 == 2: m.add(x, snare(), gain=0.12)
        m.add(x + B / 4, hat(), gain=0.07, pan=0.3)
        if n % 2 == 0: m.add(x, tri(mtof(mel[(n // 2) % 8]), 0.14), gain=0.06, pan=-0.2, verb=0.2)
    x += B / 2; n += 1
hook_sfx(m, reveal=R.NEVER)
for j, (ts, a, b) in enumerate(R.V1.SHUF):
    r = AP.riffle(0.55, j)
    if ts < 0: r = r[int(-ts * SR):]; ts = 0.0
    m.add(ts, r, gain=0.38, pan=0.1)
for c in range(0, R.V1.NUM_CHARS, 3):
    tc = R.NUM + 0.1 + 0.9 * (1 - (1 - c / R.V1.NUM_CHARS) ** 0.5)
    m.add(tc, click(3000 + 400 * (c % 2), 0.012), gain=0.12)
d = 2.2; tt_ = tt(d); f = 220 * (8 ** (1 - (1 - tt_ / d) ** 3))
m.add(R.CNT + 0.2, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt_ / 0.05) * np.clip((d - tt_) / 0.2, 0, 1), gain=0.08, verb=0.3)
for rv in rev[1:]:
    m.add(rv - 0.5, riser(0.5, 400, 1700), gain=0.2)
    m.add(rv, sub_boom(1.0, 48), gain=0.6)
    for j, nn in enumerate([84, 88, 91, 96]):
        m.add(rv + j * 0.045, bell(mtof(nn), 1.4, 0.5), gain=0.12, verb=0.5)
for tb in (R.NUM, R.CNT, R.CTA):
    m.add(tb - 0.3, whoosh(0.5, 400, 4200), gain=0.28)
m.add(R.CTA + 0.1, pluck(mtof(84), 0.8), gain=0.3, verb=0.4); m.add(R.CTA + 0.22, pluck(mtof(91), 0.8), gain=0.3, verb=0.4)
m.render("v021v2.wav", rt=1.8)
print("ok")
