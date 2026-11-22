"""029 audio: original. Plucked notes on every wall hit (quantised to 16ths once it gets busy), a pad,
drums that build inside each round, hook hit at 0.00 s with 3 clock ticks, riser + boom on each
payoff, whooshes on the cover wipes. No voice (guessing game: people look). 48 kHz."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render as R

BPM = 120; BEAT = 60 / BPM; S16 = BEAT / 4
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
def chord(t): return CH[int((t % 8) // 2)]
def tones(t):
    c = chord(t); return [m + o for o in (12, 24) for m in c]

m = Mix(R.DUR)
# pad all the way through (loops: 21.5 s is not a bar multiple, so it fades into the frame-0 hit)
for b in range(int(R.DUR // 2) + 1):
    t0 = b * 2.0
    if t0 >= R.DUR: break
    m.add(t0, pad([mtof(x - 12) for x in chord(t0)], 2.3, a=0.3, r=0.5, lp=1500, seed=b), gain=0.45, verb=0.3)

hook_sfx(m, reveal=3.0, ticks=(0.0, 1.0, 2.0))

def round_music(Rd, t_from, t_to):
    """notes on wall hits + building drums for one round, in video time [t_from, t_to)."""
    last = -1
    nballs = lambda s: sum(1 for x in Rd["BORN"] if x <= s)
    for (ht, hx, hy, bi) in Rd["HITS"]:
        tv = ht + Rd["t0"]
        if tv < t_from or tv >= t_to: continue
        tn = tones(tv); idx = int(np.clip(hx / R.BOX * len(tn), 0, len(tn) - 1))
        if nballs(ht) <= 3: tp = tv
        else:
            st = int(np.ceil(tv / S16))
            if st == last: continue
            last = st; tp = st * S16
        m.add(tp, pluck(mtof(tn[idx]), 0.7), pan=(hx / R.BOX - 0.5) * 1.2, gain=0.5 if nballs(ht) <= 3 else 0.34, verb=0.35)
    t = np.ceil(max(t_from, 0) / BEAT) * BEAT
    span = t_to - t_from
    while t < t_to - 0.05:
        prog = (t - t_from) / span
        m.add(t, kick(), gain=0.62)
        if prog > 0.35:
            m.add(t + BEAT / 2, hat(), gain=0.16, pan=0.3)
        if prog > 0.6 and round(t / BEAT) % 2 == 1:
            m.add(t, snare(), gain=0.3, verb=0.2)
        t += BEAT

R1, R2, R3 = R.ROUNDS
round_music(R1, 0.0, R1["end"] - 0.3)
round_music(R2, R2["t0"], R2["end"] - 0.3)
round_music(R3, R3["t0"], R3["end"] - 0.3)
round_music(R1, 20.5, R.DUR)                          # loop lead-in (the kiwi again)

for Rd in (R2, R3):                                   # payoffs 10.0 and 17.5 (3.0 is in hook_sfx)
    T = Rd["end"]
    m.add(T - 1.6, riser(1.6, 250, 2000), gain=0.3, verb=0.2)
    m.add(T, sub_boom(1.3, 46), gain=0.75)
    m.add(T, snare(), gain=0.28)
    for j, n in enumerate([72, 76, 79, 84, 88]):
        m.add(T + j * 0.05, bell(mtof(n), 1.6, 0.6), pan=-0.4 + 0.2 * j, gain=0.13, verb=0.5)
# sweep sparkle on each reveal
for Rd in R.ROUNDS:
    ts = Rd["end"] - R.SWEEP
    for j, n in enumerate([84, 88, 91, 96]):
        m.add(ts + j * 0.07, bell(mtof(n), 0.9, 0.3), gain=0.07, verb=0.4)
# cover wipes
for tw in (3.55, 10.55, 20.5):
    m.add(tw, whoosh(0.45, 400, 3500), gain=0.22)
# CTA chime
for j, n in enumerate([76, 79, 84]):
    m.add(18.4 + j * 0.12, bell(mtof(n), 1.4, 0.5), gain=0.12, verb=0.5)
m.render("v029.wav", rt=2.0)
print("ok")
