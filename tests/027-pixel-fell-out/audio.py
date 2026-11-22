"""027 score, sound effects and narration (voice A: Kokoro am_michael, 1.1x, kit/voice.py).

Original chiptune theme in C (C - Am - F - G, 120 BPM, a 4-bar phrase on the absolute 2-second bar
grid, so the 24 s loop lands on a bar line). One sound per visual event, all times from anim.py.
The narrator says the on-screen words (or a shorter version), added LAST so narrate() ducks the
music and effects 9 dB under each line. The cat's "ah... ah... CHOO" is formant-synthesised.
"""
import sys, os
sys.path.insert(0, "/home/claude/kit")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal
from kit import *
from hook import hook_sfx
from voice import narrate
import anim

EV = anim.build()
DUR = anim.END
m = Mix(DUR)
B = 0.5                                     # one beat
RNG = np.random.default_rng(27)

# ------------------------------------------------------------------ voice cues (measured with voice.py)
CUES = [
    (0.00, "Find the missing pixel."),
    (EV["reveal"], "He fell out."),
    (EV["reveal"] + 0.93, "Now he wants back in."),
    (EV["try1"], "Try one."),
    (EV["nope"] + 0.02, "Nope."),
    (EV["try2"], "Try two."),
    (EV["splat"] + 0.03, "So close."),
    (EV["try3"], "Try three."),
    (EV["paw_pop"] + 0.27, "Wait... the cat?!"),
    (EV["click"] + 0.02, "Home."),
    (EV["eject"] + 0.14, "Again?!"),
    (EV["cta"] + 0.09, "Name him."),
    (EV["cta"] + 0.97, "Best name stars in part two."),
]


# ------------------------------------------------------------------ synth helpers
def sweep(f0, f1, d, duty=0.25, lp=5000, curve=1.0):
    """chip 'boing': pulse wave gliding f0 -> f1"""
    t = tt(d)
    f = f0 * (f1 / f0) ** ((t / d) ** curve)
    ph = np.cumsum(f) / SR % 1
    s = np.where(ph < duty, 1.0, -1.0)
    s = signal.sosfilt(sos("lowpass", lp), s)
    return s * np.minimum(1, t / 0.004) * np.clip((d - t) / 0.03, 0, 1)


def glide(f0, f1, d, vib=0.0, vr=7.0):
    """sine glide (slide whistle / squeak)"""
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d) * (1 + vib * np.sin(2 * np.pi * vr * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.01) * np.clip((d - t) / 0.04, 0, 1)


def thud(d=0.25, f=90):
    t = tt(d)
    return np.sin(2 * np.pi * f * t * (1 + 0.8 * np.exp(-t / 0.02))) * np.exp(-t / 0.06) \
        + signal.sosfilt(sos("lowpass", 900), noise(d, 4)) * np.exp(-t / 0.02) * 0.5


def vowel(f0a, f0b, formants, d, breath=0.15):
    """tiny formant voice: glottal saw with pitch glide -> resonators"""
    t = tt(d)
    f0 = f0a * (f0b / f0a) ** (t / d) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    src = 2 * (np.cumsum(f0) / SR % 1) - 1
    src = src + breath * noise(d, 8)
    out = np.zeros_like(t)
    for fc, bw, g in formants:
        out += g * signal.sosfilt(signal.butter(2, [fc - bw / 2, fc + bw / 2], "bandpass", fs=SR, output="sos"), src)
    env = np.minimum(1, t / 0.03) * np.clip((d - t) / 0.06, 0, 1)
    return out * env


AH = [(820, 160, 1.0), (1250, 200, 0.6), (2700, 300, 0.25)]
OO = [(380, 120, 1.0), (850, 160, 0.45), (2300, 300, 0.12)]


def ch(d=0.09):
    t = tt(d)
    return signal.sosfilt(sos("bandpass", [2600, 7500]), noise(d, 11)) * np.minimum(1, t / 0.005) * np.exp(-t / 0.05)


# ------------------------------------------------------------------ music
CHORDS = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]   # C Am F G
MEL = [(0, 72, .5), (.5, 76, .5), (1, 79, .5), (1.5, 76, .5), (2, 81, 1), (3, 79, .5), (3.5, 76, .5),
       (4, 72, .5), (4.5, 76, .5), (5, 69, 1), (6, 72, .5), (6.5, 74, .5), (7, 76, 1),
       (8, 77, .5), (8.5, 76, .5), (9, 74, .5), (9.5, 72, .5), (10, 69, 1), (11, 72, .5), (11.5, 74, .5),
       (12, 76, .5), (12.5, 74, .5), (13, 71, 1), (14, 74, .5), (14.5, 79, .5), (15, 67, 1)]


def section(t0, t1, mel=0.0, bass=0.0, drums=0.0, bells=0.0, padg=0.0, arp=0.0):
    """play the band on the absolute beat grid between t0 and t1"""
    for k in range(int(DUR / B) + 1):
        x = k * B
        if not (t0 <= x < t1):
            continue
        bar = int(x // (4 * B)) % 4
        ch_ = CHORDS[bar]
        beat = k % 4
        if bass:
            m.add(x, tri(mtof(ch_[0] - 12 + (7 if beat == 2 else 0)), B * 0.9), gain=0.20 * bass)
            m.add(x + B / 2, tri(mtof(ch_[0]), B * 0.4), gain=0.07 * bass)
        if drums:
            if beat in (0, 2):
                m.add(x, kick(0.3), gain=0.30 * drums)
            if beat in (1, 3):
                m.add(x, snare(), gain=0.07 * drums)
            m.add(x + B / 2, hat(), gain=0.045 * drums, pan=0.3)
            m.add(x, hat(0.03, 6), gain=0.025 * drums, pan=-0.3)
        if padg and beat == 0:
            m.add(x, pad([mtof(n) for n in ch_[1:]], 4 * B + 0.3, a=0.25, r=0.6, lp=1500, seed=k), gain=0.48 * padg,
                  verb=0.4)
        if arp:
            for j in range(4):
                n = ch_[1:][j % 3] + 12 * (j // 3) + 12
                m.add(x + j * B / 4, pulse(mtof(n), 0.09, duty=0.125, lp=3800), gain=0.026 * arp,
                      pan=0.3 if j % 2 else -0.3)
    for (b0, n, d) in MEL * 1:
        for rep in range(4):
            x = rep * 8.0 + b0 * B
            if t0 <= x < t1 and (mel or bells):
                if mel:
                    m.add(x, pulse(mtof(n), d * B * 0.85, duty=0.25, lp=3600), gain=0.06 * mel, verb=0.15)
                if bells:
                    m.add(x, bell(mtof(n + 12), 0.9, 0.35), gain=0.085 * bells, verb=0.35)


E = EV
section(0.0, E["reveal"], arp=0.8)                                     # hook: quiet searching arp
section(E["reveal"], E["try1"], bass=0.7, arp=0.6, mel=0.6)
section(E["try1"], E["splat"], bass=1.0, drums=1.0, mel=1.0)
section(E["try3"], E["click"], padg=1.0, bells=0.7)
section(E["click"] + 0.3, E["squeeze"], padg=0.7, bells=1.0, bass=0.5)
section(E["cta"], DUR, bass=0.9, drums=0.8, mel=0.8, arp=0.4)

# ------------------------------------------------------------------ hook
hook_sfx(m, reveal=E["reveal"], ticks=(0.0, 1.0, 2.0))
for k, x in enumerate((0.55, 1.10, 1.65)):                            # the cat's eyes dart
    m.add(x, pulse(mtof(91 - 3 * k), 0.05, duty=0.5), gain=0.06, pan=(-0.4, 0.4, 0.0)[k])
m.add(anim.WHIP0, whoosh(0.8, 3500, 250), gain=0.30)                    # whip down the screen
for k in range(1, 6):                                                   # heartbeat under the countdown
    m.add(k * B, kick(0.22), gain=0.16 + 0.03 * k)
    m.add(k * B + 0.16, kick(0.18), gain=0.07 + 0.015 * k)
m.add(1.2, riser(E["reveal"] - 1.2, 220, 1600), gain=0.13)

# ------------------------------------------------------------------ the hero
def jump(tk, big=False, pitch=1.0):
    if big:
        m.add(tk - 0.20, riser(0.2, 300, 900), gain=0.10)
        m.add(tk, sweep(220 * pitch, 1100 * pitch, 0.32, curve=0.7), gain=0.11)
    else:
        m.add(tk, sweep(330 * pitch, 880 * pitch, 0.13), gain=0.09)


def land(tl, g=1.0):
    m.add(tl, thud(0.22, 110), gain=0.22 * g)
    m.add(tl, click(1400, 0.02), gain=0.12 * g)


jump(E["reveal"] + 0.06 + 0.0, pitch=1.4)                               # tiny "hi" hop
land(E["reveal"] + 0.06 + 0.18, 0.5)
m.add(E["turned"] - 0.24, sweep(600, 760, 0.08, duty=0.5), gain=0.04)
jump(E["j1_takeoff"], big=True)
land(E["j1_land"], 1.2)
land(E["j1_land"] + 0.22, 0.5)
m.add(E["j1_land"] + 0.42, glide(900, 700, 0.6, vib=0.08, vr=9), gain=0.05)   # dizzy
for k, nm in enumerate(("p1", "p2", "p3")):
    jump(E[nm + "_takeoff"], pitch=1.0 + 0.19 * k)
    land(E[nm + "_land"], 0.8)
m.add(E["teeter"], glide(700, 760, 0.45, vib=0.06, vr=8), gain=0.04)          # wobble on the rim
jump(E["leap"], big=True, pitch=1.2)
# splat: music already stopped at the splat
m.add(E["splat"], thud(0.35, 70), gain=0.5)
m.add(E["splat"], signal.sosfilt(sos("lowpass", 1800), noise(0.25, 21)) * np.exp(-tt(0.25) / 0.05), gain=0.35)
m.add(E["splat"], sweep(260, 90, 0.35, duty=0.5, lp=1500), gain=0.10)
for j in range(6):                                                    # the tiles round him rattle
    m.add(E["splat"] + 0.02 + 0.035 * j, click(1700 + 180 * j, 0.012), gain=0.07, pan=RNG.uniform(-0.6, 0.6))
m.add(E["splat"] + 0.32, glide(1150, 620, 0.45, vib=0.03, vr=11), gain=0.05)   # squeak down the glass
land(E["flop"], 1.0)
for j, n in enumerate((67, 66, 65)):                                  # sad little wah-wah
    m.add(E["flop"] + 0.08 + j * 0.2, pulse(mtof(n - 12), 0.19, duty=0.5, lp=1400), gain=0.06)

# ------------------------------------------------------------------ the paw
pent = [60, 62, 64, 67, 69, 72, 74, 76, 79]
for k in range(9):
    tk = E["paw_pop"] + 0.035 * k
    m.add(tk, click(2600, 0.012), gain=0.10, pan=(k % 3 - 1) * 0.4)
    m.add(tk, pulse(mtof(pent[k] + 12), 0.06, duty=0.25), gain=0.035)
m.add(E["paw_out"], whoosh(E["paw_land"] - E["paw_out"], 600, 2600), gain=0.22)
m.add(E["paw_land"], thud(0.3, 75), gain=0.35)
m.add(E["paw_land"], bell(mtof(84), 0.8, 0.3), gain=0.05)
jump(E["onpaw_takeoff"], pitch=1.1)
land(E["onpaw_land"], 0.6)
d = E["lift_end"] - E["lift"]                                         # rising arpeggio on the lift
for j in range(16):
    m.add(E["lift"] + j * d / 16, pulse(mtof(60 + [0, 4, 7, 12][j % 4] + 12 * (j // 8)), 0.08, duty=0.25),
          gain=0.05 + 0.003 * j)
m.add(E["lift"], riser(d, 250, 1400), gain=0.15)
span = E["hopin"] - E["onpaw_land"]                                    # snare roll that speeds up into the click
x, step = E["onpaw_land"], 0.25
while x < E["hopin"]:
    u = (x - E["onpaw_land"]) / span
    m.add(x, snare(), gain=0.05 + 0.12 * u, pan=0.15 * (-1) ** int(x * 20))
    x += step; step = max(0.06, step * 0.86)
section(E["onpaw_land"], E["click"], bass=0.8)
m.add(E["wink"], bell(mtof(96), 0.6, 0.2), gain=0.07)
m.add(E["hopin"], sweep(500, 1300, 0.2), gain=0.08)
m.add(E["click"], click(1200, 0.03), gain=0.45); m.add(E["click"], kick(0.25), gain=0.35)
for j, n in enumerate((72, 76, 79, 84, 88)):
    m.add(E["click"] + 0.02 + j * 0.05, bell(mtof(n), 1.6, 0.6), gain=0.09, verb=0.5)
m.add(E["eyes_off"], sweep(900, 500, 0.1, duty=0.5), gain=0.03)
m.add(E["happy"], bell(mtof(91), 1.0, 0.4), gain=0.06, verb=0.4)

# ------------------------------------------------------------------ the sneeze
s0 = E["squeeze"] + 0.05
m.add(s0, vowel(520, 600, AH, 0.24), gain=0.20, verb=0.2)              # "ah..."
m.add(s0 + 0.32, vowel(600, 720, AH, 0.26), gain=0.24, verb=0.2)       # "ah..."
m.add(E["squeeze"], riser(E["achoo"] - E["squeeze"], 300, 1800), gain=0.08)
m.add(E["achoo"], ch(0.10), gain=0.55)                                 # "CH
m.add(E["achoo"] + 0.06, vowel(760, 420, OO, 0.30), gain=0.30, verb=0.3)  #   OO!"
m.add(E["achoo"], sub_boom(0.9, 48), gain=0.55)
for j in range(40):                                                    # the wave rattles every tile
    dd = RNG.uniform(0, 16)
    m.add(E["achoo"] + dd / anim.WAVE_V, click(RNG.uniform(1600, 3400), 0.01), gain=0.05 * np.exp(-dd / 12),
          pan=RNG.uniform(-0.8, 0.8))
m.add(E["eject"], sweep(300, 1500, 0.22, curve=0.6), gain=0.11)        # boing
m.add(E["eject"] + 0.05, whoosh(0.5, 800, 3000), gain=0.18)
m.add(E["eject"] + 0.25, glide(1500, 420, E["eject_land"] - E["eject"] - 0.25), gain=0.05)  # falling whistle
land(E["eject_land"], 0.5)

# ------------------------------------------------------------------ narration (LAST: ducks the rest)
spans = narrate(m, CUES)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
m.render("v027.wav", rt=1.6)
print("ok")
