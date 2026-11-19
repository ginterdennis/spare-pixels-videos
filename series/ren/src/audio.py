"""Soundtrack for REN Part 1 — chip-style moody score + foley, all synthesized, synced to scene.py's beat grid."""
import math
import numpy as np
from scipy import signal
from scipy.io import wavfile
import scene as S

SR = 48000
DUR = S.DURATION
NS = int(DUR * SR) + SR
rng = np.random.default_rng(4)
B = S.BEAT
def bt(x): return x * B
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
def tt(d): return np.arange(int(d * SR)) / SR

mus = np.zeros((NS, 2)); sfx = np.zeros((NS, 2)); send = np.zeros((NS, 2))
def add(buf, t0, sig, pan=0.0, gain=1.0):
    i0 = int(round(t0 * SR))
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    if i0 >= NS: return
    n = min(len(sig), NS - i0)
    l = math.cos((pan + 1) * math.pi / 4) * 1.414; r = math.sin((pan + 1) * math.pi / 4) * 1.414
    if sig.ndim == 2:
        buf[i0:i0 + n] += sig[:n] * gain; return
    buf[i0:i0 + n, 0] += sig[:n] * gain * l; buf[i0:i0 + n, 1] += sig[:n] * gain * r

# ---------------- instruments ----------------
def pulse(f, d, duty=0.25, a=0.004, rel=0.08):
    t = tt(d); ph = (f * t) % 1
    s = np.where(ph < duty, 1.0, -1.0)
    s = signal.sosfilt(sos("lowpass", 3800), s)
    env = np.minimum(1, t / a) * np.clip((d - t) / rel, 0, 1)
    return s * env
def tri(f, d, rel=0.05):
    t = tt(d); ph = (f * t) % 1
    s = 4 * np.abs(ph - 0.5) - 1
    return s * np.clip((d - t) / rel, 0, 1) * np.minimum(1, t / 0.005)
def bell(f, d=2.0, tau=0.7):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.2)) * np.exp(-t / tau) * np.minimum(1, t / 0.003)
def noise(d): return rng.standard_normal(int(d * SR))
def kick():
    t = tt(0.4); f = 42 + 100 * np.exp(-t / 0.028)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15)
def snare():
    t = tt(0.3)
    n = signal.sosfilt(sos("bandpass", [1200, 6000]), noise(0.3)) * np.exp(-t / 0.07)
    return n + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
def hat(): t = tt(0.06); return signal.sosfilt(sos("highpass", 7000), noise(0.06)) * np.exp(-t / 0.015)
def click(f=2500, d=0.012):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / (d / 3))

# ---------------- harmony / timing ----------------
CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [48, 52, 55], "G": [55, 59, 62], "Em": [52, 55, 59]}
def chord_at(beat):
    if 13.5 <= beat < 18: return None
    if beat < 6: return "Am"
    if 18 <= beat < 22: return ["Am", "F"][int((beat - 18) / 2) % 2]
    if 22 <= beat < 28: return ["F", "C", "G"][min(2, int((beat - 22) / 2))]
    return ["Am", "F", "C", "G"][int((beat - 28) / 4) % 4]

# ---------------- pad + drone ----------------
pad = np.zeros((NS, 2))
blen = 2  # pad changes every 2 beats where the chord changes
beat = 0.0
segs = []
cur, start = chord_at(0), 0.0
for k in range(1, int(DUR / B * 4) + 2):
    bb = k / 4
    c = chord_at(bb) if bb < DUR / B else None
    if c != cur:
        segs.append((start, bb, cur)); cur, start = c, bb
for a, bb, c in segs:
    if not c: continue
    t0, t1 = bt(a), bt(bb)
    n = int((t1 - t0 + 0.6) * SR); t = np.arange(n) / SR
    env = np.minimum(1, t / 0.4) * np.clip((t1 - t0 + 0.6 - t) / 0.6, 0, 1)
    for m in [CH[c][0] - 12] + CH[c]:
        for ch, det in ((0, -0.09), (1, 0.09)):
            f = mtof(m) * 2 ** (det / 12)
            v = 2 * ((f * t + rng.uniform()) % 1) - 1
            i0 = int(t0 * SR); kk = min(n, NS - i0)
            pad[i0:i0 + kk, ch] += v[:kk] * env[:kk]
pad = signal.sosfilt(sos("lowpass", 850), pad, axis=0) * 0.016
padlvl = np.ones(NS)
tv = np.arange(NS) / SR
padlvl *= 0.85 + 0.15 * np.clip((tv - bt(5)) / bt(1), 0, 1)              # swell into the storm
padlvl *= 1 - 0.7 * np.clip((tv - bt(13)) / 0.4, 0, 1) * (1 - np.clip((tv - bt(18)) / bt(2), 0, 1))
mus += pad * padlvl[:, None]; send += pad * 0.6

# low drone (A1) with breathing filter
t = np.arange(NS) / SR
dr = signal.sosfilt(sos("lowpass", 180), (2 * ((55 * t) % 1) - 1) + 0.6 * np.sin(2 * np.pi * 55.3 * t))
dr *= 0.05 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t)) * (0.6 + 0.6 * np.clip((t - bt(6)) / bt(4), 0, 1) * (1 - np.clip((t - bt(22)) / bt(4), 0, 1)))
mus[:, 0] += dr; mus[:, 1] += dr

# wind: two noise bands with slow movement, stronger after the blackout and in winter
wn = noise(NS / SR)
w1 = signal.sosfilt(sos("bandpass", [250, 900]), wn); w2 = signal.sosfilt(sos("bandpass", [900, 2600]), noise(NS / SR))
wl = 0.035 + 0.05 * np.clip((t - bt(13.5)) / bt(2), 0, 1) + 0.05 * np.clip((t - bt(18)) / bt(2), 0, 1) * (1 - 0.6 * np.clip((t - bt(28)) / bt(2), 0, 1))
lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t + 1) * np.sin(2 * np.pi * 0.07 * t)
sfx[:, 0] += (w1 * 0.8 + w2 * 0.35) * wl * lfo
sfx[:, 1] += (np.roll(w1, 9000) * 0.8 + np.roll(w2, 7000) * 0.35) * wl * (1.2 - lfo * 0.4)

# ---------------- arpeggio (pulse wave, 8ths) ----------------
def arp_on(beat):
    if beat < 13.5: return 0.8
    if beat < 22: return 0.0
    return 1.0 if beat < 59 else 0.0
k = 0
while bt(k / 2) < DUR - 0.2:
    bb = k / 2
    c = chord_at(bb); lv = arp_on(bb)
    if c and lv:
        tones = CH[c] + [CH[c][0] + 12]
        m = tones[[0, 1, 2, 3, 2, 1, 2, 3][k % 8]] + 12
        p = pulse(mtof(m), B / 2 * 0.9, duty=0.25 if (k // 8) % 2 == 0 else 0.125, rel=0.12)
        add(mus, bt(bb), p, -0.25 if k % 2 else 0.25, 0.05 * lv); add(send, bt(bb), p, 0, 0.03 * lv)
    k += 1

# ---------------- drums + bass ----------------
K, SN = kick(), snare()
for i in range(int(DUR / B) + 1):
    bb = i
    tb = bt(bb)
    if 22 <= bb < 28:                      # heartbeat under "This is Ren"
        add(sfx, tb, kick(), 0, 0.30); add(sfx, tb + 0.17, kick(), 0, 0.18)
    if 28 <= bb < 52:
        add(mus, tb, K, 0, 0.45)
        if bb % 2 == 1: add(mus, tb, SN, 0.05, 0.16)
        add(mus, tb + B / 2, hat(), 0.3, 0.07); add(mus, tb, hat(), -0.3, 0.04)
    if 52 <= bb < 60:
        if bb % 2 == 0: add(mus, tb, K, 0, 0.32)
        add(mus, tb + B / 2, hat(), 0.3, 0.04)
    c = chord_at(bb)
    if c and 28 <= bb < 60:
        root = CH[c][0] - 24
        for h_ in range(2):
            add(mus, tb + h_ * B / 2, tri(mtof(root), B / 2 * 0.85), 0, 0.16)

# ---------------- opening hit on the hook ----------------
add(sfx, 0.0, kick(), 0, 0.45)
t_ = tt(2.5); add(sfx, 0.0, np.sin(2 * np.pi * np.cumsum(32 + 50 * np.exp(-t_ / 0.1)) / SR) * np.exp(-t_ / 0.7), 0, 0.35)
for i, m in enumerate([57, 64, 69, 72]):
    add(mus, 0.01 + i * 0.03, bell(mtof(m), 3.0, 1.2), -0.3 + 0.2 * i, 0.05); add(send, 0.01 + i * 0.03, bell(mtof(m), 3.0, 1.2), 0, 0.07)

# ---------------- storm, blackout ----------------
d = bt(1.6); t_ = tt(d)
sw = signal.sosfilt(sos("bandpass", [2000, 9000]), noise(d)) * (t_ / d) ** 2
add(sfx, S.T_STORM - d, sw, 0, 0.10)
d = bt(8); t_ = tt(d)
shimmer = signal.sosfilt(sos("bandpass", [3000, 9000]), noise(d)) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t_)) * np.minimum(1, t_ / 0.5) * np.clip((d - t_) / 1.5, 0, 1)
add(sfx, S.T_STORM, shimmer, 0.2, 0.035); add(send, S.T_STORM, shimmer, 0, 0.03)
for i in range(14):                         # aurora chimes
    tc = S.T_STORM + rng.uniform(0, bt(7)); m = rng.choice([81, 84, 88, 91, 93])
    add(sfx, tc, bell(mtof(m), 2.5, 0.9), rng.uniform(-0.7, 0.7), 0.025); add(send, tc, bell(mtof(m), 2.5, 0.9), 0, 0.03)
for i in range(60):                         # electric crackle
    tc = S.T_STORM + rng.uniform(0, bt(7.5))
    c_ = signal.sosfilt(sos("highpass", 2500), noise(0.01)) * np.exp(-tt(0.01) / 0.002)
    add(sfx, tc, c_, rng.uniform(-0.8, 0.8), 0.05)
for (tf, fx, fy) in S.FLASHES:              # transformer blowouts
    zd = 0.35; t_ = tt(zd)
    f = 200 + 1800 * np.exp(-t_ / 0.06)
    zap = (2 * ((np.cumsum(f) / SR) % 1) - 1) * np.exp(-t_ / 0.1)
    zap += signal.sosfilt(sos("bandpass", [800, 7000]), noise(zd)) * np.exp(-t_ / 0.05) * 0.8
    pan = (fx / 270) * 1.4 - 0.7
    add(sfx, tf, zap, pan, 0.12); add(send, tf, zap, 0, 0.06)
    add(sfx, tf, kick(), 0, 0.35)
for wd in S.WINDOWS[::40]:                  # relay clicks as blocks go dark
    if wd[4] < S.T_POWERDOWN:
        add(sfx, wd[4], click(rng.uniform(1500, 3000), 0.01), (wd[0] / 270) * 1.4 - 0.7, 0.05)
d = 1.8; t_ = tt(d)                          # generator spinning down
f = 25 + 120 * np.exp(-t_ / 0.55)
spin = signal.sosfilt(sos("lowpass", 1200), 2 * ((np.cumsum(f) / SR) % 1) - 1) * np.exp(-t_ / 0.7)
add(sfx, S.T_POWERDOWN, spin, 0, 0.22); add(send, S.T_POWERDOWN, spin, 0, 0.1)
t_ = tt(2.0); boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t_ / 0.08)) / SR) * np.exp(-t_ / 0.6)
add(sfx, S.T_POWERDOWN, boom, 0, 0.5)

# ---------------- no help / winter / meet ----------------
for k_, m in enumerate([76, 72]):            # lonely notes in the silence
    add(sfx, S.T_NOHELP + bt(1 + 2 * k_), bell(mtof(m), 3.0, 1.1), -0.3 + 0.6 * k_, 0.05)
    add(send, S.T_NOHELP + bt(1 + 2 * k_), bell(mtof(m), 3.0, 1.1), 0, 0.07)
gd = bt(3); t_ = tt(gd)
gust = signal.sosfilt(sos("bandpass", [400, 1800]), noise(gd)) * np.sin(np.pi * t_ / gd) ** 2
add(sfx, S.T_WINTER - bt(0.5), gust, -0.4, 0.12)
for i, m in enumerate([88, 93, 95, 100]):
    add(sfx, S.T_WINTER + i * 0.09, bell(mtof(m), 2.5, 0.8), 0.4, 0.03); add(send, S.T_WINTER + i * 0.09, bell(mtof(m), 2.5, 0.8), 0, 0.05)
cd = 0.5; t_ = tt(cd)
cut = signal.sosfilt(sos("bandpass", [600, 5000]), noise(cd)) * (t_ / cd) ** 3
add(sfx, S.T_MEET - cd, cut, 0, 0.08); add(sfx, S.T_MEET, kick(), 0, 0.25)

# ---------------- inventory ----------------
zd = 0.45; n = 26                            # backpack zipper
for i in range(n):
    tz = S.T_INV - 0.05 + zd * (i / n) ** 0.8
    add(sfx, tz, signal.sosfilt(sos("bandpass", [1800, 6500]), noise(0.012)) * np.exp(-tt(0.012) / 0.004), 0.1, 0.09)
PENTA = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96]
for i, ti in enumerate(S.ITEM_T):
    m = PENTA[i]
    blip = np.concatenate([pulse(mtof(m), 0.055, 0.5, rel=0.01), pulse(mtof(m + 12), 0.09, 0.5, rel=0.05)])
    add(sfx, ti, blip, -0.3 + 0.3 * (i % 3), 0.07); add(send, ti, blip, 0, 0.03)
    add(sfx, ti, kick(), 0, 0.12)
for i, m in enumerate([76, 79, 81, 84, 88]):  # meters fill
    add(sfx, S.T_MATTER - bt(0.5) + i * bt(0.4), pulse(mtof(m), 0.07, 0.5, rel=0.03), 0, 0.05)
k = 0                                        # selector cursor ticks
while S.T_END + k * B / 2 < DUR - 0.3:
    add(sfx, S.T_END + k * B / 2, click(3200, 0.008), 0.2, 0.035); k += 1
for i, m in enumerate([57, 64, 69, 72, 76]):  # closing chord on "Day 2 next"
    add(mus, bt(57) + i * 0.05, bell(mtof(m), 4.0, 1.4), -0.4 + 0.2 * i, 0.05); add(send, bt(57) + i * 0.05, bell(mtof(m), 4.0, 1.4), 0, 0.07)

# typewriter ticks
for (t0, t1, text, tw) in S.DIALOG:
    if not tw: continue
    s_ = text.replace("*", "")
    for j, ch in enumerate(s_):
        if ch == " " or j % 2: continue
        tc = t0 + j / S.CPS
        if tc >= min(t1, DUR): break
        add(sfx, tc, pulse(rng.uniform(1300, 1500), 0.018, 0.5, a=0.001, rel=0.008), 0, 0.022)

# ---------------- reverb + master ----------------
irn = int(2.6 * SR); ti_ = np.arange(irn) / SR
ir = rng.standard_normal((irn, 2)) * np.exp(-ti_ / 0.5)[:, None]
ir = signal.sosfilt(sos("lowpass", 5500, 1), ir, axis=0); ir[: int(0.025 * SR)] = 0
ir /= np.sqrt((ir ** 2).sum(axis=0))
wet = np.stack([signal.fftconvolve(send[:, c], ir[:, c])[:NS] for c in range(2)], axis=1)
mix = (mus + sfx + wet * 0.9)[: int(DUR * SR)]
tv = np.arange(len(mix)) / SR
mix *= (np.clip((DUR - tv) / 1.2, 0, 1) ** 1.2)[:, None]
mix *= np.minimum(1, tv / 0.015)[:, None]
import pyloudnorm as pyln
meter = pyln.Meter(SR)
mix *= 10 ** ((-13.5 - meter.integrated_loudness(mix)) / 20)
mix = np.tanh(mix * 1.15) / 1.15
mix *= min(1.0, 0.89 / np.abs(mix).max())
print("loudness", round(meter.integrated_loudness(mix), 1), "LUFS  peak", round(20 * np.log10(np.abs(mix).max()), 1), "dBFS")
wavfile.write("audio.wav", SR, (mix * 32767).astype(np.int16))
