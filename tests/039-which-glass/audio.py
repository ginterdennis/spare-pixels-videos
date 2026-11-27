"""039 audio (original): soft pad bed (A minor), pouring water = band-passed noise whose pitch rises as the
glass being filled gets fuller (the 'glug' rises), countdown ticks + boom at 2.8 s (hook_sfx), a dull thunk + two
low notes when the capped pipe is hit, a gulp when water reaches each pipe, a bright chord when glass 5 is full,
a soft whoosh down into the loop. No voice. 48 kHz."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import *
from hook import hook_sfx
import render as R

m = Mix(R.DUR)
BEAT = 0.5
CH = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 55]]
for b in range(int(R.DUR / (4 * BEAT)) + 1):
    t0 = b * 4 * BEAT
    if t0 >= R.DUR: break
    m.add(t0, pad([mtof(x) for x in CH[b % 4]], 4 * BEAT + 0.3, a=0.15, r=0.5, lp=1400, seed=b), gain=0.32, verb=0.35)
# light plucks on the beat after the reveal
for k in range(int((R.T5_FULL - R.REVEAL) / BEAT)):
    t = R.REVEAL + 0.4 + k * BEAT
    ch = CH[int(t / (4 * BEAT)) % 4]
    m.add(t, pluck(mtof(ch[k % 4] + 24), 0.4, 0.5), gain=0.07, pan=(-0.3 if k % 2 else 0.3))
hook_sfx(m, reveal=R.REVEAL, ticks=(0.0, 1.0, 2.0))


def pour(t0, t1, glass, f0, f1, gain=0.22):
    """Water pouring into a glass: noise through a resonant band whose centre rises with the level."""
    d = t1 - t0
    n = int(d * SR)
    x = noise(d, int(t0 * 10) + glass)
    out = np.zeros(n)
    blk = 2400
    for k in range(0, n, blk):
        u = k / max(1, n - 1)
        fc = f0 + (f1 - f0) * u
        sosb = signal.butter(2, [fc * 0.8, fc * 1.25], "bandpass", fs=SR, output="sos")
        seg = x[max(0, k - 600):k + blk]
        y = signal.sosfilt(sosb, seg)[-(min(blk, n - k)):]
        out[k:k + len(y)] = y
    env = np.minimum(1, tt(d) / 0.08) * np.clip((d - tt(d)) / 0.12, 0, 1)
    flutter = 0.75 + 0.25 * np.sin(2 * np.pi * 9 * tt(d)) ** 2
    m.add(t0, out * env * flutter * 3.0, gain=gain)


pour(0.0, R.T1_OUT, 1, 500, 800, gain=0.18)
pour(R.P12[1], R.T2_HIGH, 2, 420, 1000)
pour(R.P25[1], R.T5_FULL, 5, 600, 1500, gain=0.24)
# water reaches each pipe: a gulp
for t in (R.P12[0], R.P25[0]):
    m.add(t, sub_boom(0.25, 90), gain=0.3)
    m.add(t, pluck(mtof(64), 0.3, 0.3), gain=0.12)
# the capped pipe: thunk + two low notes
m.add(R.T2_CAP, kick(0.3), gain=0.45)
m.add(R.T2_CAP + 0.02, tri(mtof(52), 0.18), gain=0.25)
m.add(R.T2_CAP + 0.2, tri(mtof(46), 0.4), gain=0.25)
# glass 5 full
m.add(R.T5_FULL - 0.4, riser(0.4, 600, 2400), gain=0.2)
m.add(R.T5_FULL, sub_boom(1.0, 46), gain=0.6)
m.add(R.T5_FULL, snare(), gain=0.22)
for j, n in enumerate([81, 84, 88, 93]):
    m.add(R.T5_FULL + j * 0.04, bell(mtof(n), 1.4, 0.5), gain=0.11, verb=0.45)
# CTA + loop
m.add(R.CTA, click(2200, 0.012), gain=0.3)
m.add(R.CTA, bell(mtof(84), 0.6, 0.3), gain=0.08)
m.add(R.DRAIN0, whoosh(0.8, 3000, 300, seed=4), gain=0.22)
m.render("v039.wav", rt=1.4)
print("v039.wav")
