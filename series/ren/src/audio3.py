"""Soundtrack for REN Part 3 — cold night that warms up when the fire catches. Synced to scene3.py."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import Mix, SR, tt, sos, mtof, pulse, tri, pad, bell, pluck, kick, hat, click, noise, sub_boom
import scene3 as S
B = S.BEAT; D = S.DURATION
m = Mix(D)
n = int(D * SR); t_all = np.arange(n) / SR
# wind: band-passed noise with slow swells, quieter once the fire burns
wind = signal.sosfilt(sos("bandpass", [250, 1400]), noise(D, 5))
swell = 0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t_all) * np.sin(2 * np.pi * 0.06 * t_all + 1)
fl_curve = np.array([S.fire_level(x) for x in np.arange(0, D, 0.05)])
fl = np.interp(t_all, np.arange(0, D, 0.05), fl_curve)
m.add(0, wind * swell * (1 - 0.6 * fl), gain=0.16)
# cold pad (Am / Em) until ignition, warm pad (F / C) after
cold = [[45, 52, 57, 60], [40, 47, 52, 55]]
for k in range(int(S.T_IGNITE // (4 * B)) + 1):
    t0 = k * 4 * B
    if t0 >= S.T_IGNITE: break
    m.add(t0, pad([mtof(x) for x in cold[k % 2]], 4 * B + 0.5, a=0.6, r=0.6, lp=900, seed=k), gain=0.5, verb=0.5)
warm = [[41, 48, 53, 57, 60], [48, 55, 60, 64, 67], [43, 50, 55, 59, 62], [45, 52, 57, 60, 64]]
k = 0; t0 = S.T_IGNITE
while t0 < D:
    m.add(t0, pad([mtof(x) for x in warm[k % 4]], 4 * B + 0.6, a=0.5, r=0.8, lp=2000, seed=20 + k), gain=0.6, verb=0.5)
    t0 += 4 * B; k += 1
# chip arpeggio after ignition (warm), sparse bell before
t0 = S.T_IGNITE; k = 0
while t0 < D - 0.3:
    ch = warm[(k // 8) % 4]
    m.add(t0, pulse(mtof(ch[(k % 4) + 1] + 12), B / 2 * 0.7, duty=0.25), gain=0.05, pan=0.25)
    t0 += B / 2; k += 1
for k in range(int(S.T_IGNITE / (2 * B))):
    m.add(k * 2 * B, bell(mtof([69, 76, 72, 79][k % 4]), 2.0, 0.8), gain=0.06, verb=0.6)
# soft beat from the fire onwards
t0 = S.T_FIRE
while t0 < D - 0.3:
    m.add(t0, kick(0.3), gain=0.28); m.add(t0 + B / 2, hat(0.05), gain=0.07); t0 += B
# dialog type blips
for (t0, t1, text, tw) in S.DIALOG:
    if not tw: continue
    for c in range(0, len(text.replace("*", "")), 2):
        tc = t0 + c / S.CPS
        if tc < t1: m.add(tc, pulse(900 + 120 * (c % 3), 0.018, duty=0.5, rel=0.01), gain=0.04)
# shiver, items panel pops
for k in range(10): m.add(0.4 + k * 0.09, tri(mtof(84 - k), 0.07), gain=0.06)
for k, ti in enumerate([0.0, 0.5, 0.8]):
    m.add(S.T_ITEMS + 0.4 + ti, pulse(mtof([60, 76, 79][k]), 0.12, duty=0.5), gain=0.14)
# cardboard tearing
for j in range(len(S.CARD)):
    tj = S.T_TINDER + S.b(1) + j * S.b(3) / len(S.CARD)
    tear = signal.sosfilt(sos("bandpass", [1500, 6000]), noise(0.14, 60 + j)) * np.exp(-tt(0.14) / 0.04)
    m.add(tj, tear, gain=0.25, pan=-0.3 + 0.08 * j)
# battery contact: electric sizzle + spark pings
d = 1.4; z = noise(d, 9); env = (np.random.default_rng(3).random(int(d * SR)) > 0.6).astype(float)
env = signal.sosfilt(sos("lowpass", 400), env) * np.exp(-tt(d) / 0.6)
sizzle = signal.sosfilt(sos("highpass", 3000), z) * env
m.add(S.T_CONTACT, sizzle, gain=0.9)
for k in range(6): m.add(S.T_CONTACT + k * 0.07, click(4000 + 300 * k, 0.01), gain=0.15)
# ignition whoomp
d = 1.2; who = signal.sosfilt(sos("lowpass", 700), noise(d, 14)) * (np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2)
m.add(S.T_IGNITE - 0.2, who, gain=0.6); m.add(S.T_IGNITE, sub_boom(1.4, 46), gain=0.5)
# fire crackle following the flame size
rng = np.random.default_rng(8); t0 = S.T_IGNITE
while t0 < D - 0.2:
    lv = S.fire_level(t0)
    if rng.random() < 0.3 + 0.6 * lv:
        c = signal.sosfilt(sos("highpass", 1800), noise(0.02, int(t0 * 1000) % 997)) * np.exp(-tt(0.02) / 0.004)
        m.add(t0, c, gain=0.25 * lv * rng.uniform(0.4, 1.0), pan=rng.uniform(-0.3, 0.3))
    t0 += rng.uniform(0.03, 0.12)
roar = signal.sosfilt(sos("lowpass", 500), noise(D, 21)) * fl
m.add(0, roar, gain=0.12)
# tip warning beeps
for k in range(3):
    m.add(S.T_TIP + 0.5 + k * 0.4, pulse(mtof(76), 0.12, duty=0.5), gain=0.12); m.add(S.T_TIP + 0.7 + k * 0.4, pulse(mtof(72), 0.12, duty=0.5), gain=0.12)
# inventory slide + updates + end
m.add(S.T_INV, signal.sosfilt(sos("highpass", 1500), noise(0.35, 12)) * np.exp(-tt(0.35) / 0.12), gain=0.2)
for k, tu in enumerate(S.T_UPD):
    m.add(tu, pulse(mtof(83), 0.06, duty=0.5), gain=0.2); m.add(tu + 0.06, pulse(mtof(86 + k), 0.2, duty=0.5), gain=0.2)
t0 = S.T_END
while t0 < D - 0.2: m.add(t0, click(2400, 0.01), gain=0.08); t0 += B / 2
m.add(S.b(50.5), bell(mtof(79), 2.0, 0.8), gain=0.22, verb=0.5)
m.render("/home/claude/v014.wav", rt=2.0)
print("ok")
