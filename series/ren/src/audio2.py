"""Soundtrack for REN Part 2 — chip-style daytime score + foley, synced to scene2.py."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import Mix, SR, tt, sos, mtof, pulse, tri, pad, bell, pluck, kick, hat, click, noise, sub_boom
import scene2 as S
B = S.BEAT
m = Mix(S.DURATION)
CH = [[48, 52, 55], [43, 47, 50], [45, 48, 52], [41, 45, 48]]   # C G Am F
nb = int(S.DURATION / B) + 1
for k in range(nb):
    t = k * B
    ch = CH[(k // 4) % 4]
    if k % 4 == 0:
        m.add(t, pad([mtof(x) for x in ch], 4 * B + 0.4, a=0.3, r=0.5, lp=1500, seed=k), gain=0.45, verb=0.3)
    m.add(t, tri(mtof(ch[0] - 12), B * 0.85), gain=0.32)
    for j in range(2):
        n_ = ch[(k * 2 + j) % 3] + 24
        m.add(t + j * B / 2, pulse(mtof(n_), B / 2 * 0.8, duty=0.25), gain=0.06, pan=0.25)
    in_inv = t >= S.T_INV
    if t >= S.T_EAT and not (S.T_HEAT <= t < S.T_BAG):
        m.add(t, kick(0.3), gain=0.32)
        m.add(t + B / 2, hat(0.05), gain=0.08)
# dialog type blips
for (t0, t1, text, tw) in S.DIALOG:
    if not tw: continue
    n = len(text.replace("*", ""))
    for c in range(0, n, 2):
        tc = t0 + c / S.CPS
        if tc < t1: m.add(tc, pulse(900 + 120 * (c % 3), 0.018, duty=0.5, rel=0.01), gain=0.04)
# hook sting
m.add(0.05, bell(mtof(84), 1.6, 0.6), gain=0.2, verb=0.5)
# shiver (body heat)
for k in range(10):
    m.add(S.T_HEAT + 0.6 + k * 0.09, tri(mtof(84 - k), 0.07), gain=0.07)
# snow scoops
for j in range(6):
    tj = S.T_BAG + 0.3 + j * (S.b(4) / 6)
    crunch = signal.sosfilt(sos("bandpass", [900, 5000]), noise(0.18, 40 + j)) * np.exp(-tt(0.18) / 0.05)
    m.add(tj, crunch, gain=0.35, pan=-0.2 + 0.08 * j)
# melt drips
rng = np.random.default_rng(3)
t = S.T_MELT + 0.6
while t < S.T_RATIO - 0.3:
    f0 = rng.uniform(1100, 1700)
    d = tt(0.08); f = f0 * (1 - 0.35 * d / 0.08)
    drip = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.02)
    m.add(t, drip, gain=0.18, pan=rng.uniform(-0.4, 0.4), verb=0.3)
    t += rng.uniform(0.18, 0.42)
# ratio: 10 snow pops, then the water chime
SC = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93]
for i in range(10):
    m.add(S.T_RATIO + 0.15 + i * 0.12, pulse(mtof(SC[i]), 0.06, duty=0.5), gain=0.12)
m.add(S.T_RATIO + 1.9, bell(mtof(72), 2.0, 0.8), gain=0.3, verb=0.5); m.add(S.T_RATIO + 1.9, sub_boom(1.0, 50), gain=0.4)
# pour into bottle
d = tt(1.6)
pour = signal.sosfilt(sos("bandpass", [600, 2400]), noise(1.6, 77)) * np.sin(np.pi * np.clip(d / 1.6, 0, 1)) ** 0.5
m.add(S.T_FILL + 0.3, pour, gain=0.22)
for k, n_ in enumerate([67, 72, 76, 79]):
    m.add(S.T_FILL + 0.3 + k * 0.4, pulse(mtof(n_), 0.12, duty=0.25), gain=0.12)
# inventory slide + updates
m.add(S.T_INV, signal.sosfilt(sos("highpass", 1500), noise(0.35, 12)) * np.exp(-tt(0.35) / 0.12), gain=0.2)
for k, tu in enumerate(S.T_UPD):
    m.add(tu, pulse(mtof(83), 0.06, duty=0.5), gain=0.2); m.add(tu + 0.06, pulse(mtof(88 + k), 0.2, duty=0.5), gain=0.2)
# end cursor ticks
t = S.T_END
while t < S.DURATION - 0.2:
    m.add(t, click(2400, 0.01), gain=0.08); t += B / 2
m.add(S.b(51.5), bell(mtof(79), 2.0, 0.8), gain=0.22, verb=0.5)
m.render("/home/claude/v013.wav", rt=1.6)
print("ok")
