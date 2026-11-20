import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R

m = Mix(R.DUR)
B = 60 / 120
prog = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]  # C Am F G
t = 0.0; k = 0
while t < R.DUR:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 4 * B + 0.2, a=0.15, r=0.5, lp=1500, seed=k), gain=0.48, verb=0.3)
    t += 4 * B; k += 1
x = 0.0; n = 0
mel = [72, 76, 79, 76, 74, 77, 81, 77]
rev = (R.NUM, R.PCT, R.WF + 0.3)
while x < R.DUR - 0.4:
    if not any(rv - 0.05 <= x < rv + 0.55 for rv in rev):
        if n % 4 == 0: m.add(x, kick(), gain=0.38)
        if n % 4 == 2: m.add(x, snare(), gain=0.12)
        m.add(x + B / 4, hat(), gain=0.07, pan=0.3)
        if n % 2 == 0: m.add(x, tri(mtof(mel[(n // 2) % 8]), 0.14), gain=0.06, pan=-0.2, verb=0.2)
    x += B / 2; n += 1


def riffle(d=0.5, seed=0):
    """card riffle: a burst of tiny filtered clicks that speeds up."""
    rg = np.random.default_rng(seed)
    out = np.zeros(int((d + 0.05) * SR))
    tt_ = 0.0
    while tt_ < d:
        c = signal.sosfilt(sos("bandpass", [1800, 7000]), rg.standard_normal(int(0.008 * SR))) * np.exp(-np.arange(int(0.008 * SR)) / (0.0015 * SR))
        i = int(tt_ * SR); out[i:i + len(c)] += c * (0.6 + 0.4 * rg.random())
        tt_ += 0.012 + 0.02 * (1 - tt_ / d) * rg.random()
    return out


from scipy import signal
for j, (ts, a, b) in enumerate(R.SHUF):
    m.add(ts, riffle(0.55, j), gain=0.35, pan=0.1)
# 52! typing: fast ticks
for c in range(0, R.NUM_CHARS, 3):
    tc = R.NUM + 0.1 + 0.9 * (1 - (1 - c / R.NUM_CHARS) ** 0.5)
    m.add(tc, click(3000 + 400 * (c % 2), 0.012), gain=0.12)
# counter: rising tone
d = 2.4; tt_ = tt(d); f = 220 * (8 ** (1 - (1 - tt_ / d) ** 3))
m.add(R.CNT + 0.2, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt_ / 0.05) * np.clip((d - tt_) / 0.2, 0, 1), gain=0.08, verb=0.3)
for rv in rev:
    m.add(rv - 0.5, riser(0.5, 400, 1700), gain=0.2)
    m.add(rv, sub_boom(1.0, 48), gain=0.6)
    for j, nn in enumerate([84, 88, 91, 96]):
        m.add(rv + j * 0.045, bell(mtof(nn), 1.4, 0.5), gain=0.12, verb=0.5)
for tb in (R.CNT, R.CTA):
    m.add(tb - 0.35, whoosh(0.6, 400, 4200), gain=0.28)
m.add(R.CTA + 0.1, pluck(mtof(84), 0.8), gain=0.3, verb=0.4); m.add(R.CTA + 0.22, pluck(mtof(91), 0.8), gain=0.3, verb=0.4)
m.render("v021.wav", rt=1.8)
print("ok")
