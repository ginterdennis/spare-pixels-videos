import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
import render as R

BEAT = 0.5; S16 = BEAT / 4
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
def chord(t): return CH[int(t // 2) % 4]
def tones(t):
    c = chord(t); out = []
    for o in (12, 24):
        out += [m + o for m in c]
    return out  # 6 tones, low->high
m = Mix(R.DUR)
# pad
for b in range(int(R.T_FULL // 2) + 1):
    t0 = b * 2.0
    if t0 >= R.T_FULL: break
    m.add(t0, pad([mtof(x - 12) for x in chord(t0)], 2.3, a=0.4, r=0.5, lp=1400, seed=b), gain=0.5, verb=0.3)
# hits -> notes
balls_at = lambda t: sum(1 for x in R.BORN if x <= t)
last_step = -1
for (ht, hx, hy, bi) in R.HITS:
    if ht > R.T_SWEEP: break
    tn = tones(ht)
    idx = int(np.clip(hx / R.BOX * len(tn), 0, len(tn) - 1))
    if balls_at(ht) <= 3:
        t_play = ht
    else:
        step = int(np.ceil(ht / S16))
        if step == last_step: continue
        last_step = step; t_play = step * S16
    g = 0.55 if balls_at(ht) <= 3 else 0.38
    m.add(t_play, pluck(mtof(tn[idx]), 0.8), pan=(hx / R.BOX - 0.5) * 1.2, gain=g, verb=0.35)
# drums build
t_kick = next((b for b in sorted(R.BORN) if balls_at(b) >= 5), 99)
t_kick = np.ceil(t_kick / BEAT) * BEAT
t_hat = next(t / 10 for t in range(0, 300) if R.coverage(t / 10) >= 0.40)
t_snare = next(t / 10 for t in range(0, 300) if R.coverage(t / 10) >= 0.72)
t = t_kick
while t < R.T_SWEEP - 0.01:
    m.add(t, kick(), gain=0.7)
    if t >= t_snare and (round(t / BEAT) % 2 == 1): m.add(t, snare(), gain=0.32, verb=0.2)
    t += BEAT
t = np.ceil(t_hat / (BEAT / 2)) * (BEAT / 2)
while t < R.T_SWEEP - 0.01:
    m.add(t, hat(), gain=0.18, pan=0.3); t += BEAT / 2
# reveal ticks (rate-limited)
times = np.sort(R.REV[R.REV <= R.T_SWEEP].ravel())
lastt = -1
for tr in times:
    if tr - lastt > 0.045:
        m.add(tr, click(3200 + 400 * np.random.rand(), 0.01), pan=np.random.uniform(-0.5, 0.5), gain=0.05); lastt = tr
# riser into sweep
m.add(R.T_SWEEP - 1.8, riser(2.0, 250, 1800), gain=0.35, verb=0.2)
# sweep arpeggio (C major up)
sweep_notes = [72, 76, 79, 84, 88, 91, 96]
ts = np.linspace(R.T_SWEEP + 0.15, R.T_FULL, len(sweep_notes))
for k, (tq, n) in enumerate(zip(ts, sweep_notes)):
    m.add(tq, bell(mtof(n), 1.5, 0.5), pan=-0.4 + 0.8 * k / 6, gain=0.28, verb=0.5)
# reveal hit
T_HIT = R.T_FULL + 0.6
m.add(T_HIT, sub_boom(1.6), gain=0.8)
for n in [60, 64, 67, 72, 76]:
    m.add(T_HIT, bell(mtof(n), 3.5, 1.4), gain=0.16, verb=0.6)
m.add(T_HIT, pad([mtof(x) for x in [48, 55, 60, 64]], R.DUR - T_HIT, a=0.3, r=2.0, lp=2200, seed=9), gain=0.55, verb=0.4)
m.render("v004.wav", rt=2.2)
print("kick", t_kick, "hat", t_hat, "snare", t_snare)
