"""020 v2 score: v1's Am-F-G-E pad and ticking groove, re-timed, plus the hook kit's frame-0 hit,
3-2-1 clock ticks and the reveal boom at 3.0 s."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render_v2 as R

m = Mix(R.DUR)
B = 60 / 116
prog = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 56]]
t = 0.0; k = 0
while t < R.DUR:
    m.add(t, pad([mtof(x) for x in prog[k % 4]], 4 * B + 0.2, a=0.05, r=0.5, lp=1500, seed=k), gain=0.5, verb=0.3)
    t += 4 * B; k += 1
x = 0.0; n = 0
mel = [76, 72, 69, 72, 74, 71, 67, 71]
while x < R.DUR - 0.4:
    near = any(rv - 0.05 <= x < rv + 0.55 for rv in (R.REV, R.GONE, R.CTA))
    if not near and x >= 0.15:
        if n % 4 == 0: m.add(x, kick(), gain=0.38)
        m.add(x, click(3200 if n % 2 else 2400, 0.02), gain=0.06, pan=0.25 if n % 2 else -0.25)
        if n % 2 == 0: m.add(x, tri(mtof(mel[(n // 2) % 8]), 0.14), gain=0.06, pan=-0.2, verb=0.2)
    x += B / 2; n += 1
hook_sfx(m, reveal=R.REV, ticks=(0.0, 1.0, 2.0))
m.add(R.REV + 0.15, pluck(mtof(93), 0.4), gain=0.18, verb=0.3)            # lens pop
for tb in (R.R2, R.R3, R.CTA):
    m.add(tb - 0.3, whoosh(0.5, 400, 4200), gain=0.28)
m.add(R.RUN, pluck(mtof(79), 0.3), gain=0.2); m.add(R.RUN + 0.12, pluck(mtof(74), 0.3), gain=0.2)
d = R.BEND1 - R.BEND0
tt_ = tt(d); f = 520 * (1 - 0.35 * tt_ / d) * (1 + 0.04 * np.sin(2 * np.pi * 7 * tt_))
m.add(R.BEND0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt_ / d), gain=0.1, verb=0.4)
m.add(R.GONE - 0.4, riser(0.4, 400, 1700), gain=0.2); m.add(R.GONE, sub_boom(1.0, 48), gain=0.5)
for j, nn in enumerate([81, 84, 88, 93]):
    m.add(R.GONE + j * 0.045, bell(mtof(nn), 1.4, 0.5), gain=0.12, verb=0.5)
m.add(R.CTA + 0.1, pluck(mtof(81), 0.8), gain=0.3, verb=0.4); m.add(R.CTA + 0.22, pluck(mtof(88), 0.8), gain=0.3, verb=0.4)
m.render("v020v2.wav", rt=1.8)
print("ok")
