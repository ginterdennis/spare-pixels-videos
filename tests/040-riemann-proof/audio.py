"""040 score + sound design + narrator (voice A+), synced to timing.py -> v040.wav"""
import sys, os
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
from voice import narrate, place
from timing import T, TEXT, LINES

HERE = os.path.dirname(os.path.abspath(__file__))
END = T["end"]
CUT0, CUT1 = T["cut"] + 0.95, T["cut"] + 1.65
m = Mix(END)
rng = np.random.default_rng(40)

# ---------------------------------------------------------------- bed: D minor, 100 bpm
BEAT = 0.6
CHORDS = [(50, 53, 57, 62), (46, 50, 53, 58), (53, 57, 60, 65), (48, 52, 55, 60)]   # Dm Bb F C
t = 0.0
k = 0
while t < END:
    d = min(4 * BEAT * 1.0, END - t)
    ch = CHORDS[k % 4]
    quiet = T["big"] - 0.3 <= t < T["big"] + 0.6
    m.add(t, pad([mtof(n) for n in ch], d + 0.6, a=0.4, r=0.6, lp=1500, seed=k), gain=0.30 if not quiet else 0.12)
    m.add(t, tri(mtof(ch[0] - 12), d * 0.9, rel=0.3), gain=0.10)
    t += 4 * BEAT
    k += 1

# arpeggio plucks (calm parts only)
def arps(t0, t1, gain=0.06):
    t = t0
    j = 0
    while t < t1:
        ch = CHORDS[int(t / (4 * BEAT)) % 4]
        n = ch[j % 4] + 12 + (12 if j % 8 >= 4 else 0)
        m.add(t, pluck(mtof(n), 0.5, 0.5), gain=gain, pan=0.3 if j % 2 else -0.3, verb=0.3)
        t += BEAT / 2
        j += 1

arps(T["primes"] - 0.2, T["lean"])
arps(T["tidy"], T["share"] + 1.5, gain=0.05)

# soft pulse
for b in np.arange(T["primes"], T["lean"], BEAT * 2):
    m.add(b, kick(0.3), gain=0.12)

# ---------------------------------------------------------------- A: hook (hit at 0, riser + boom on WITH AN AI.)
hook_sfx(m, reveal=T["stamp_ai"], gain=0.9)

# ---------------------------------------------------------------- B: primes light up at the centre
PR = [n for n in range(2, 40) if all(n % p for p in range(2, int(n ** 0.5) + 1))]
t0 = T["primes"] - 0.15
for i, n in enumerate(PR):
    tn = t0 + (n - 1.4) / 3.3
    if T["primes"] - 0.1 < tn < T["line"] - 0.1:
        m.add(tn, bell(mtof(81 + [0, 3, 5, 7, 10, 12, 15][i % 7]), 0.9, 0.3), gain=0.08, verb=0.4)

# ---------------------------------------------------------------- C: zeros snap onto the line
for j in range(14):
    tj = T["line"] + 0.4 + j * 0.065
    m.add(tj, click(2400 + 90 * j, 0.02), gain=0.12, pan=-0.4 + 0.06 * j)
m.add(T["line"] + 0.35, whoosh(0.6, 400, 2600, seed=4), gain=0.12)

# ---------------------------------------------------------------- D: 1859 -> 2026, NO PROOF.
for j in range(16):
    m.add(T["years"] + j * 0.06, click(1800 + 40 * j, 0.015), gain=0.10)
m.add(T["years"] + 1.8, sub_boom(0.7, 48), gain=0.5)
m.add(T["years"] + 1.8, snare(), gain=0.2)
m.add(T["years"] + 1.85, tri(mtof(50), 0.5, rel=0.3), gain=0.12)

# ---------------------------------------------------------------- E: typing that turns into a roar, 17 MILLION
t = T["lean"]
while t < T["big"] - 0.05:
    u = (t - T["lean"]) / (T["big"] - T["lean"])
    rate = 5 + 40 * u ** 2
    m.add(t, click(2000 + rng.uniform(-300, 600), 0.012), gain=0.05 + 0.06 * u, pan=rng.uniform(-0.5, 0.5))
    t += 1.0 / rate
for b in np.arange(T["howlong"], T["big"] - 0.1, BEAT / 2):
    m.add(b, hat(0.05), gain=0.08)
m.add(T["howlong"] + 0.2, riser(T["big"] - T["howlong"] - 0.2, 220, 2400), gain=0.22)
m.add(T["big"], sub_boom(1.4, 44), gain=0.8)
m.add(T["big"], snare(), gain=0.3)
for j, nn in enumerate([74, 77, 81, 86]):
    m.add(T["big"] + j * 0.03, bell(mtof(nn), 1.6, 0.6), gain=0.10, verb=0.5)
m.add(T["big"] + 0.3, kick(0.4), gain=0.3)

# ---------------------------------------------------------------- F: checkers pass, CORRECT.
for i in range(4):
    m.add(T["check"] + 0.15 + i * 0.12, click(1400, 0.02), gain=0.12)
    tp = T["check"] + 1.55 + i * 0.28
    m.add(tp, bell(mtof(79 + [0, 2, 4, 7][i]), 0.8, 0.3), gain=0.12, verb=0.35)
tc = T["check"] + 2.75
m.add(tc, sub_boom(0.9, 50), gain=0.55)
for j, nn in enumerate([62, 69, 74, 78, 81]):
    m.add(tc + j * 0.025, bell(mtof(nn), 1.8, 0.7), gain=0.09, verb=0.5)

# ---------------------------------------------------------------- G: the cut (17.4 million -> 76,000)
m.add(CUT0 - 0.05, whoosh(CUT1 - CUT0 + 0.2, 4200, 160, seed=7), gain=0.35)
d = CUT1 - CUT0
x = tt(d)
f = 1400 * (90 / 1400) ** (x / d)
m.add(CUT0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip((d - x) / 0.08, 0, 1) * 0.5, gain=0.18)
m.add(CUT1, sub_boom(0.6, 56), gain=0.45)
m.add(CUT1, click(3000, 0.02), gain=0.25)
m.add(CUT1 + 0.35, snare(), gain=0.18)
m.add(CUT1 + 0.35, bell(mtof(86), 1.0, 0.4), gain=0.10, verb=0.4)

# ---------------------------------------------------------------- H/I: band draws, theorems turn TRUE
m.add(T["tidy"] + 0.1, whoosh(1.6, 300, 1800, seed=9), gain=0.10)
for i in range(3):
    m.add(T["thm"] + 0.1 + i * 0.15, click(1600, 0.02), gain=0.10)
    tt_i = T["thm"] + 2.05 + i * 0.22
    m.add(tt_i, kick(0.25), gain=0.25)
    m.add(tt_i, bell(mtof(81 + 4 * i), 0.9, 0.35), gain=0.11, verb=0.4)

# ---------------------------------------------------------------- J: share card, resolve, hand back to frame 0
for j, nn in enumerate([50, 57, 62, 65, 69]):
    m.add(T["share"] + j * 0.04, bell(mtof(nn + 12), 2.2, 0.9), gain=0.07, verb=0.6)
m.add(END - 0.55, whoosh(0.55, 300, 3000, seed=11), gain=0.12)

# ---------------------------------------------------------------- narrator (last: ducks everything above)
cues = place([(T[k], TEXT[k]) for k, _, _ in LINES], end=END, max_late=0.08)
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
out = os.path.join(HERE, "v040.wav")
m.render(out, rt=1.4)
print(out)
