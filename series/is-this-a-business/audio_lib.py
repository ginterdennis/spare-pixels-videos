"""Shared score + sound effects for the "Is this a business?" series (spare.pixels audio kit, all synthesized).
Bouncy 120 BPM bed in F major (F - C - Dm - Bb), marimba-ish plucks, walking bass."""
import math, sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import Mix, pluck, bell, pulse, tri, kick, hat, click, whoosh, riser, sub_boom, noise, mtof, tt, sos, SR
from scipy import signal

BT = 0.5  # one beat at 120 BPM
CH = {  # bass root, chord tones (midi)
    "F": (41, [65, 69, 72]),
    "C": (36, [64, 67, 72]),
    "Dm": (38, [65, 69, 74]),
    "Bb": (34, [65, 70, 74]),
}
PROG = ["F", "C", "Dm", "Bb"]
# 2-bar melody (16 eighth notes), None = rest; repeats over the progression
MEL = [72, None, 74, 76, None, 72, None, 69, 70, None, 72, 74, None, 69, None, None,
       69, None, 72, 74, None, 76, None, 79, 77, None, 76, 74, None, 72, None, None]


def chord_at(t):
    return PROG[int(t // (4 * BT)) % 4]


def marimba(f, d=0.5):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.03)
    return s * np.minimum(1, t / 0.0015)


def bed(m, t0, t1, gain=1.0, melody=True, quiet=()):
    """Music between t0 and t1. `quiet` = list of (a, b) windows where the bed drops to 45 %."""
    def g(t):
        for a, b in quiet:
            if a <= t < b:
                return 0.45 * gain
        return gain
    t = t0
    i = 0
    while t < t1 - 1e-6:
        ch = chord_at(t)
        root, tones = CH[ch]
        beat = i % 8  # eighth-note index within the bar's first half... (8 eighths per 2 s bar)
        # walking bass on quarters: root, fifth, octave, fifth
        if i % 2 == 0:
            q = (i // 2) % 4
            n = [root, root + 7, root + 12, root + 7][q]
            m.add(t, tri(mtof(n), 0.42, 0.08), gain=0.32 * g(t), pan=0.0)
            m.add(t, kick(0.25), gain=(0.22 if q in (0, 2) else 0.0) * g(t))
        else:
            # off-beat marimba chord stab
            for k, n in enumerate(tones):
                m.add(t + k * 0.004, marimba(mtof(n), 0.35), gain=0.075 * g(t), pan=-0.35 + 0.35 * k)
            m.add(t, hat(0.05, seed=i), gain=0.05 * g(t), pan=0.3)
        if melody:
            mn = MEL[i % len(MEL)]
            if mn is not None:
                m.add(t, marimba(mtof(mn), 0.6), gain=0.17 * g(t), pan=0.15, verb=0.25)
        t += BT / 2
        i += 1


# ------------------------------------------------------------------ effects
def steps(m, t0, t1, up=False, gain=0.42, rate=0.085):
    """Quick footsteps on stairs; pitch walks down (or up) with the descent."""
    n = int((t1 - t0) / rate)
    for k in range(n):
        t = t0 + k * rate
        p = k / max(1, n - 1)
        f = (900 + 900 * p) if up else (1800 - 900 * p)
        m.add(t, click(f, 0.02), gain=gain, pan=-0.25 if k % 2 else 0.25)
        m.add(t, signal.sosfilt(sos("lowpass", 700), noise(0.04, k)) * np.exp(-tt(0.04) / 0.012), gain=gain * 0.8)


def zoom_in(m, t, d=0.4):
    m.add(t - 0.05, whoosh(d + 0.1, 400, 5000, seed=int(t * 10)), gain=0.32)


def zoom_out(m, t, d=0.35):
    m.add(t, whoosh(d, 5000, 400, seed=int(t * 10) + 1), gain=0.26)


def thunk(m, t):
    m.add(t, kick(0.3), gain=0.35)


def pop(m, t, n=84):
    m.add(t, click(2200, 0.012), gain=0.3)
    m.add(t, marimba(mtof(n), 0.25), gain=0.2, pan=0.2)


def hum(m, t0, t1, gain=0.55):
    d = t1 - t0
    if d <= 0:
        return
    t = tt(d)
    rum = signal.sosfilt(sos("lowpass", 180), noise(d, 31)) * (0.7 + 0.3 * np.sin(2 * np.pi * 6.2 * t))
    slosh = signal.sosfilt(sos("bandpass", [300, 900]), noise(d, 32)) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t)) ** 2 * 0.35
    env = np.minimum(1, t / 0.15) * np.clip((d - t) / 0.15, 0, 1)
    m.add(t0, (rum * 3 + slosh) * env, gain=gain)


def beeps(m, t, n=3, f=1760):
    for k in range(n):
        m.add(t + k * 0.16, pulse(f, 0.11, 0.5, 0.02, 5000), gain=0.22, pan=0.3)


def ticks(m, t0, t1, rate=0.06):
    k = 0
    t = t0
    while t < t1:
        m.add(t, click(3000 if k % 2 else 2400, 0.01), gain=0.3, pan=0.4)
        t += rate
        k += 1


def flop(m, t, seed=0):
    d = 0.12
    m.add(t, signal.sosfilt(sos("lowpass", 500), noise(d, seed)) * np.exp(-tt(d) / 0.03), gain=0.6)


def wahwah(m, t):
    """Comedic sad trombone: three short falls and one long one."""
    for k, (n, d) in enumerate([(67, 0.28), (66, 0.28), (65, 0.28), (64, 0.9)]):
        tt_ = tt(d)
        f = mtof(n) * (1 - 0.03 * tt_ / d) * (1 + (0.012 * np.sin(2 * np.pi * 6 * tt_) if k == 3 else 0))
        ph = np.cumsum(f) / SR
        s = signal.sosfilt(sos("lowpass", 1400), 2 * (ph % 1) - 1) * np.minimum(1, tt_ / 0.02) * np.clip((d - tt_) / 0.06, 0, 1)
        m.add(t + k * 0.3, s, gain=0.32, verb=0.2)


def slap(m, t):
    d = 0.18
    m.add(t, signal.sosfilt(sos("bandpass", [800, 5000]), noise(d, 77)) * np.exp(-tt(d) / 0.025), gain=0.4)
    m.add(t, kick(0.2), gain=0.2)


def ding_chord(m, t, notes=(72, 77, 81, 84)):
    for k, n in enumerate(notes):
        m.add(t + k * 0.03, bell(mtof(n), 1.6, 0.6), gain=0.09, pan=-0.3 + 0.2 * k, verb=0.45)
    m.add(t, sub_boom(0.9, 46), gain=0.3)


def notify(m, t):
    """Phone notification: two quick bright notes."""
    m.add(t, marimba(mtof(88), 0.3), gain=0.25, pan=0.2)
    m.add(t + 0.11, marimba(mtof(93), 0.4), gain=0.25, pan=0.2, verb=0.3)


def card(m, t):
    m.add(t - 0.3, riser(0.4, 300, 1500), gain=0.2)
    m.add(t, whoosh(0.5, 300, 3000, seed=5), gain=0.25)
