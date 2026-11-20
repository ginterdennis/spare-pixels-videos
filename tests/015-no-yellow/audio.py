"""Original score + sound design for 015 'Your phone has zero yellow lights', synced to src/timing.json.
Uses the spare.pixels audio kit (kit.Mix and synth voices). 120 BPM, Am - F - C - G."""
import json, math, sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *  # Mix, pad, pluck, bell, pulse, tri, kick, snare, hat, click, whoosh, riser, sub_boom, mtof, tt, sos, noise, SR
from scipy import signal

T = json.load(open("src/timing.json"))
DUR = T["end"]
BT = 0.5            # one beat at 120 BPM
m = Mix(DUR)

# ------------------------------------------------------------ helpers
def bez(x1, y1, x2, y2):
    """CSS cubic-bezier easing, same as Remotion's Easing.bezier."""
    def f(p):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            s = (lo + hi) / 2
            x = 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
            if x < p: lo = s
            else: hi = s
        s = (lo + hi) / 2
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    return f

zin, zout = bez(0.62, 0, 0.18, 1), bez(0.55, 0, 0.25, 1)
LNZ = math.log(450)

def chirp(f0, f1, d, wave="tri"):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d)
    ph = np.cumsum(f) / SR
    s = 4 * np.abs(ph % 1 - 0.5) - 1 if wave == "tri" else np.sin(2 * np.pi * ph)
    return s * np.minimum(1, t / 0.004) * np.clip((d - t) / 0.03, 0, 1)

def crash(d=2.2):
    t = tt(d); n = noise(d, 11)
    return signal.sosfilt(sos("highpass", 4500), n) * np.exp(-t / 0.55) * 0.6

def shimmer(f, d):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.01 * t)
    return s * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2

def reverse_swell(d=0.9):
    return crash(d)[::-1] * 0.8

# chords per 2-second bar (Am - F - C - G)
CH = {"Am": [45, 52, 57, 60, 64], "F": [41, 53, 57, 60, 65], "C": [48, 55, 60, 64, 67], "G": [43, 55, 59, 62, 67]}
PROG = ["Am", "F", "C", "G"]
chord_at = lambda t: PROG[int(t // 2) % 4]

# ------------------------------------------------------------ pads (filter opens during the zoom)
for b in range(int(DUR // 2) + 1):
    t0 = b * 2.0
    if t0 >= DUR: break
    lp = 1100
    if T["zoomStart"] - 0.5 <= t0 < T["zoomEnd"]: lp = 1100 + 2200 * (t0 - 2) / 6
    if t0 >= T["eyeStart"] - 0.6 and t0 < T["cardsHead"] - 0.5: lp = 900
    if t0 >= T["outStart"] - 0.1: lp = 1600
    g = 0.55 if t0 < T["zoomEnd"] else 0.4
    m.add(t0, pad([mtof(x) for x in CH[chord_at(t0)]], 2.6, a=0.35, r=0.7, lp=lp, seed=b), gain=g, verb=0.45)

# ------------------------------------------------------------ arpeggio bed (keeps energy up in the quiet stretches)
def arp(t0, t1, gain, rate=BT / 2, rate2=None, desc=False, ramp=None):
    t, i = t0, 0
    while t < t1 - 0.01:
        ch = CH[chord_at(t)]
        notes = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12]
        if desc: notes = notes[::-1]
        g = gain * (ramp(t) if ramp else 1)
        m.add(t, pluck(mtof(notes[i % len(notes)]), 0.35, 0.5), gain=g, pan=0.35 * math.sin(i * 0.9), verb=0.3)
        r = rate2(t) if rate2 else rate
        t += r; i += 1
arp(0.45, T["zoomEnd"], 0.24, rate2=lambda t: BT / 2 if t < 5.5 else BT / 4, ramp=lambda t: 0.8 + 0.4 * (t / 8))
arp(T["eyeStart"], T["same"], 0.2)
arp(T["same"], T["eyeEnd"], 0.15)
arp(T["outStart"] + 0.25, T["outEnd"], 0.2, rate=BT / 4, desc=True)
for t in np.arange(T["zoomStart"], T["zoomEnd"] - 0.01, BT):       # heartbeat kick under the zoom
    m.add(t, kick(0.3), gain=0.16 + 0.22 * (t - T["zoomStart"]) / (T["zoomEnd"] - T["zoomStart"]))
for t in np.arange(T["eyeStart"], T["same"] - 0.01, 2 * BT):
    m.add(t, kick(0.3), gain=0.18)
for t in np.arange(T["outStart"] + 2 * BT, T["outEnd"] - 0.01, 2 * BT):
    m.add(t, kick(0.3), gain=0.18)

# ------------------------------------------------------------ hook
m.add(0.0, sub_boom(1.2, 48), gain=0.45)
for i, n_ in enumerate([69, 72, 76, 81]):
    m.add(0.0 + i * 0.012, pluck(mtof(n_), 1.4, 0.7), gain=0.30, pan=-0.4 + i * 0.27, verb=0.4)
m.add(0.12, whoosh(0.9, 2500, 9000, seed=4), gain=0.20)          # sheen across the screen
m.add(T["reticle"], click(3200, 0.02), gain=0.35)                 # target lock
m.add(T["reticle"] + 0.09, bell(mtof(88), 1.2, 0.35), gain=0.13, verb=0.5)
m.add(T["reticle"] + 0.18, bell(mtof(93), 1.2, 0.35), gain=0.10, verb=0.5)

# ------------------------------------------------------------ zoom in: riser, sweep, ticks that follow the zoom counter
zd = T["zoomEnd"] - T["zoomStart"]
m.add(T["zoomStart"], riser(zd, 160, 1500), gain=0.42, verb=0.2)
m.add(T["zoomStart"] + zd * 0.35, whoosh(zd * 0.65, 250, 7000, seed=6), gain=0.32)
STEPS = 26
prev = 0
for i in range(1, int(zd * SR / 200)):
    t = T["zoomStart"] + i * 200 / SR
    lz = LNZ * zin(min(1, (t - T["zoomStart"]) / zd))
    k = int(lz / (LNZ / STEPS))
    if k > prev:
        prev = k
        m.add(t, click(1400 + 110 * k, 0.012), gain=0.16, pan=(k % 2) * 0.4 - 0.2)
        m.add(t, pluck(mtof(64 + [0, 3, 5, 7, 10, 12][k % 6] + 12 * (k // 13)), 0.25, 0.4), gain=0.07)
for b in range(int((T["zoomEnd"] - 4.0) / (BT / 2))):           # hats creep in
    t = 4.0 + b * BT / 2
    m.add(t, hat(0.05, seed=b), gain=0.02 + 0.06 * (t - 4.0) / 4.0, pan=0.3 if b % 2 else -0.3)

# arrival on the single pixel
A = T["zoomEnd"]
m.add(A, kick(0.6), gain=0.6); m.add(A, sub_boom(1.6, 42), gain=0.4); m.add(A, crash(2.4), gain=0.28)
for n_ in [57, 64, 69, 72, 76]:
    m.add(A, bell(mtof(n_ + 12), 2.6, 1.0), gain=0.10, verb=0.6)

# ------------------------------------------------------------ RED / GREEN on, BLUE off
m.add(T["lblR"], click(2600, 0.02), gain=0.4); m.add(T["lblR"], pluck(mtof(69), 0.9, 0.7), gain=0.38, pan=-0.45, verb=0.3)
m.add(T["lblG"], click(2900, 0.02), gain=0.4); m.add(T["lblG"], pluck(mtof(72), 0.9, 0.7), gain=0.38, pan=0.0, verb=0.3)
m.add(T["lblB"], chirp(520, 110, 0.32), gain=0.20, pan=0.45)    # power-down
m.add(T["lblB"] + 0.02, pulse(mtof(40), 0.22, 0.5, lp=900), gain=0.18, pan=0.45)
m.add(T["rgHeadline"] - 0.15, whoosh(0.35, 600, 5000, seed=8), gain=0.16)
for i, n_ in enumerate([76, 70]):                                  # "nuh-uh" on YELLOW LIGHTS FOUND: 0
    m.add(T["hudFlash"] + i * 0.14, pulse(mtof(n_), 0.12, 0.5, lp=3000), gain=0.16, pan=0.35)

# groove 8.0 .. world out
def groove(t0, t1, kick_g=0.42, clap_g=0.16, hat_g=0.06, sixteenth=False, bass=True):
    t = t0
    while t < t1 - 0.01:
        beat = round(t / BT)
        m.add(t, kick(0.35), gain=kick_g)
        if beat % 2 == 1: m.add(t, snare(), gain=clap_g, verb=0.25)
        m.add(t + BT / 2, hat(0.05, seed=beat), gain=hat_g, pan=0.25)
        if sixteenth:
            m.add(t + BT / 4, hat(0.03, seed=beat + 50), gain=hat_g * 0.5, pan=-0.25)
            m.add(t + 3 * BT / 4, hat(0.03, seed=beat + 80), gain=hat_g * 0.5, pan=-0.25)
        if bass:
            root = CH[chord_at(t)][0] - 12 if CH[chord_at(t)][0] >= 45 else CH[chord_at(t)][0]
            m.add(t + BT / 2, pulse(mtof(root + 12), 0.22, 0.4, lp=700), gain=0.20)
            m.add(t, pulse(mtof(root), 0.3, 0.5, lp=500), gain=0.24)
        t += BT
groove(A + BT, T["worldOut"], kick_g=0.34, clap_g=0.12, hat_g=0.05)

# ------------------------------------------------------------ eye scene: half-time, quieter
m.add(T["worldOut"], whoosh(0.5, 4000, 300, seed=12), gain=0.25)
for t in np.arange(T["eyeStart"], T["same"] - 0.01, BT):
    m.add(t + BT / 2, hat(0.04, seed=int(t * 10)), gain=0.04, pan=0.2)
for at, fill, two in [(T["p1In"], T["p1Fill"], False), (T["p2In"], T["p2Fill"], True)]:
    m.add(at - 0.05, whoosh(0.45, 400, 5000, seed=int(at)), gain=0.20)
    if two:
        m.add(at + 0.2, shimmer(mtof(84), 1.0), gain=0.05, pan=-0.3)
        m.add(at + 0.2, shimmer(mtof(91), 1.0), gain=0.05, pan=0.3)
    else:
        m.add(at + 0.2, shimmer(mtof(88), 1.0), gain=0.07)
    for i, n_ in enumerate([69, 72, 76]):                          # identical notes for both panels: same signal
        m.add(fill + i * 0.1, pluck(mtof(n_), 0.8, 0.6), gain=0.30, pan=-0.3 + 0.3 * i, verb=0.35)
S = T["same"]
m.add(S - 0.9, reverse_swell(0.9), gain=0.35)
m.add(S, kick(0.6), gain=0.55); m.add(S, sub_boom(1.4, 44), gain=0.38); m.add(S, snare(), gain=0.25, verb=0.4)
for n_ in [60, 64, 67, 72]:
    m.add(S, bell(mtof(n_ + 12), 2.2, 0.9), gain=0.11, verb=0.6)
m.add(T["eyeHead2"] - 0.1, whoosh(0.3, 700, 4000, seed=21), gain=0.12)
m.add(T["brainSub"], bell(mtof(84), 1.8, 0.7), gain=0.10, verb=0.6)
groove(S + BT, T["eyeEnd"], kick_g=0.26, clap_g=0.09, hat_g=0.05, bass=False)

# ------------------------------------------------------------ colour cards: full groove
m.add(T["cardsHead"] - 0.35, reverse_swell(0.35), gain=0.25)
groove(T["cardsHead"], T["cardsEnd"], kick_g=0.44, clap_g=0.16, hat_g=0.06, sixteenth=True)
CARD_SOUND = [
    ("white", [72, 76, 79, 84], [100, 100, 100]),
    ("black", [45], [0, 0, 0]),
    ("brown", [65, 69, 72, 76], [55, 27, 0]),
    ("magenta", [84, 88, 91, 96], [100, 0, 100]),
]
for st, (name, notes, rgb) in zip(T["cards"], CARD_SOUND):
    m.add(st - 0.18, whoosh(0.3, 500, 6000, seed=int(st * 3)), gain=0.18)
    if name == "black":
        m.add(st, chirp(300, 60, 0.4, "sin"), gain=0.3)
        m.add(st, sub_boom(0.8, 40), gain=0.35)
    else:
        for i, n_ in enumerate(notes):
            v = bell(mtof(n_), 1.4, 0.6) if name == "magenta" else pluck(mtof(n_), 1.0, 0.65)
            m.add(st + i * 0.03, v, gain=0.20, pan=-0.3 + 0.2 * i, verb=0.35)
    for k in range(3):
        if rgb[k] > 0:
            m.add(st + 0.18 + k * 0.08, click(2200 + 400 * k, 0.015), gain=0.18 * rgb[k] / 100, pan=-0.4 + 0.4 * k)

# ------------------------------------------------------------ zoom out over the sunset, payoff, CTA
m.add(T["worldIn"] - 0.6, reverse_swell(0.6), gain=0.4)
O = T["outStart"]
m.add(O, kick(0.6), gain=0.55); m.add(O, crash(2.0), gain=0.22)
od = T["outEnd"] - O
m.add(O, whoosh(od, 7000, 200, seed=31), gain=0.30)
prev = STEPS
for i in range(1, int(od * SR / 200)):
    t = O + i * 200 / SR
    lz = LNZ * (1 - zout(min(1, (t - O) / od)))
    k = int(math.ceil(lz / (LNZ / STEPS)))
    if k < prev:
        prev = k
        m.add(t, click(1400 + 110 * k, 0.012), gain=0.13, pan=(k % 2) * 0.4 - 0.2)
P = T["outEnd"]
m.add(P - 0.05, sub_boom(2.0, 48), gain=0.36)
for n_ in [48, 55, 60, 64, 67, 72, 74, 79]:                        # the sunset chord (C add9)
    m.add(P, bell(mtof(n_ + 12), 3.0, 1.3), gain=0.08, verb=0.7)
m.add(P, pad([mtof(x) for x in [48, 55, 62, 64, 67]], 2.6, a=0.05, r=1.0, lp=2600, seed=77), gain=0.3, verb=0.5)
CTA = T["cta"]
for i, n_ in enumerate([72, 74, 76, 79, 81, 84]):                  # swatches pop
    m.add(CTA + 0.25 + i * 0.07, pluck(mtof(n_), 0.8, 0.7), gain=0.24, pan=-0.5 + 0.2 * i, verb=0.4)
groove(CTA + 0.5, T["loop"] - 0.2, kick_g=0.22, clap_g=0.08, hat_g=0.045, bass=True)
m.add(T["loop"] - 0.05, whoosh(0.5, 3000, 600, seed=41), gain=0.15)

m.render("out/score_raw.wav", rt=2.0)

# gentle master compression so the booms don't dwarf the bed (loudnorm happens at mux)
from scipy.io import wavfile
sr, x = wavfile.read("out/score_raw.wav"); x = x.astype(np.float64) / 32768
env = np.sqrt(signal.sosfiltfilt(sos("lowpass", 8), (x ** 2).mean(1)) + 1e-12)
thr, ratio = 10 ** (-24 / 20), 3.0
gain = np.where(env > thr, (env / thr) ** (1 / ratio - 1), 1.0)
y = x * gain[:, None]
y = np.tanh(1.2 * y / np.abs(y).max()) / np.tanh(1.2) * 0.89
wavfile.write("out/score.wav", sr, (y * 32767).astype(np.int16))
print("wrote out/score.wav", DUR, "s")
