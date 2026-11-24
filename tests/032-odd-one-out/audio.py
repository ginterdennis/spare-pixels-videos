"""032 audio: original. Pad + soft arpeggio, a clock tick under each 3-2-1 ring, hook hit at 0.00 s,
riser + boom on each payoff, whooshes on the round changes, CTA chime. No voice (people look). 48 kHz."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render as R

BPM = 120; BEAT = 60 / BPM
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
def chord(t): return CH[int((t % 8) // 2)]

m = Mix(R.DUR)
for b in range(int(R.DUR // 2) + 1):
    t0 = b * 2.0
    if t0 >= R.DUR: break
    m.add(t0, pad([mtof(x - 12) for x in chord(t0)], 2.3, a=0.3, r=0.5, lp=1500, seed=b), gain=0.42, verb=0.3)

hook_sfx(m, reveal=3.0, ticks=(0.0, 1.0, 2.0))

# arpeggio + pulse inside each search window (quiet during payoffs and the CTA)
windows = [(0.0, 2.9), (3.9, 9.9), (10.9, 17.4), (20.5, R.DUR)]
for (a, b) in windows:
    t = np.ceil(a / (BEAT / 2)) * (BEAT / 2)
    k = 0
    while t < b - 0.05:
        c = chord(t); n = c[k % 3] + 12 * (1 + (k // 3) % 2)
        m.add(t, pluck(mtof(n), 0.5), gain=0.22, pan=-0.3 + 0.2 * (k % 4), verb=0.3)
        if k % 2 == 0:
            m.add(t, kick(), gain=0.35 + 0.25 * (t - a) / (b - a))
        k += 1
        t += BEAT / 2
# clock ticks under the rings of rounds 2 and 3
for Rr in R.ROUNDS[1:]:
    c0, c1 = Rr["cd"]
    for j in range(3):
        m.add(c0 + j, click(2600 if j % 2 else 2200, 0.025), gain=0.32)
        m.add(c0 + j, tri(mtof(84 + (j == 2) * 5), 0.09), gain=0.10)
    T = Rr["end"]
    m.add(T - 1.4, riser(1.4, 250, 2000), gain=0.3, verb=0.2)
    m.add(T, sub_boom(1.3, 46), gain=0.75)
    m.add(T, snare(), gain=0.28)
    for j, n in enumerate([72, 76, 79, 84, 88]):
        m.add(T + j * 0.05, bell(mtof(n), 1.6, 0.6), pan=-0.4 + 0.2 * j, gain=0.13, verb=0.5)
for tw in (3.55, 10.55, 20.5):
    m.add(tw, whoosh(0.45, 400, 3500), gain=0.22)
for j, n in enumerate([76, 79, 84]):
    m.add(18.4 + j * 0.12, bell(mtof(n), 1.4, 0.5), gain=0.12, verb=0.5)
m.render("v032.wav", rt=2.0)
print("ok")
