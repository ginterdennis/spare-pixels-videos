"""042 score + sound design + narrator (voice A+ via vo.py: tight takes, 10 % faster) -> v042.wav.
One soundtrack for both looks. Bars tile the video exactly so the loop is seamless (041 playbook, point 8)."""
import sys, os, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import vo  # noqa: F401  (patches voice.say / voice._words before narrate/place use them)
from kit import *
from hook import hook_sfx
from voice import narrate, place
from timing import T, TEXT, LINES, A, END

HERE = os.path.dirname(os.path.abspath(__file__))
m = Mix(END)
rng = np.random.default_rng(42)

# ---------------------------------------------------------------- bed: F#m D A E (bright, forward), bars tile END
NBAR = 4 * max(1, round(END / 9.6))
BAR = END / NBAR
BEAT = BAR / 4
CH = [(54, 57, 61, 66), (50, 54, 57, 62), (57, 61, 64, 69), (52, 56, 59, 64)]   # F#m D A E
for k in range(NBAR):
    t = k * BAR
    ch = CH[k % 4]
    g = 0.18 if t < A["flip"] else 0.26
    m.add(t, pad([mtof(n) for n in ch], BAR + 0.5, a=0.3, r=0.5, lp=1700, seed=k), gain=g)
    m.add(t, tri(mtof(ch[0] - 12), BAR * 0.9, rel=0.3), gain=0.10)
for b in np.arange(0, END - 1e-6, BEAT):
    if b >= A["flip"]:
        m.add(b, kick(0.3), gain=0.12)
for b in np.arange(0, END - 1e-6, BEAT / 2):
    if A["short"] <= b < A["catch"]:
        m.add(b, hat(0.04), gain=0.045, pan=0.3 if int(b / (BEAT / 2)) % 2 else -0.3)


def arps(t0, t1, gain=0.045):
    t, j = math.ceil(t0 / (BEAT / 2)) * BEAT / 2, 0
    while t < t1:
        ch = CH[int(t / BAR) % 4]
        n = ch[j % 4] + 12 + (12 if j % 8 >= 4 else 0)
        m.add(t, pluck(mtof(n), 0.5, 0.5), gain=gain, pan=0.3 if j % 2 else -0.3, verb=0.3)
        t += BEAT / 2
        j += 1


arps(A["plane"], A["catch"])
arps(A["better"], END, 0.04)

# ---------------------------------------------------------------- hook: hit at 0 (the loop lands here), 1 in 4 flips electric
hook_sfx(m, reveal=A["flip"], gain=0.9)
zap = np.sin(2 * np.pi * np.cumsum(2400 * (300 / 2400) ** (tt(0.25) / 0.25)) / SR) * np.exp(-tt(0.25) / 0.08)
for j in range(8):
    m.add(A["flip"] + j * 0.03, zap, gain=0.10, pan=-0.6 + 0.17 * j)
m.add(A["flip"], signal.sosfilt(sos("highpass", 3000), noise(0.3, 6)) * np.exp(-tt(0.3) / 0.06), gain=0.2)

# ---------------------------------------------------------------- 500 km ruler, Munich -> Vienna
for j in range(6):
    m.add(A["short"] + 0.1 + j * 0.1, click(1800 + 150 * j, 0.012), gain=0.10)
m.add(A["km500"], bell(mtof(81), 0.9, 0.35), gain=0.09, verb=0.3)
m.add(A["munich"], pluck(mtof(73), 0.5, 0.6), gain=0.12)
m.add(A["vienna"], pluck(mtof(78), 0.5, 0.6), gain=0.12)
m.add(A["vienna"] + 0.05, whoosh(0.7, 400, 2800, seed=3), gain=0.12)

# ---------------------------------------------------------------- energy: kerosene heat, electric flow, 3x less
m.add(A["fuel"] + 0.25, whoosh(0.7, 300, 1500, seed=8), gain=0.12)
hiss = signal.sosfilt(sos("bandpass", [600, 2500]), noise(1.6, 9)) * np.sin(np.pi * tt(1.6) / 1.6) ** 2
m.add(A["quarter"] - 0.1, hiss, gain=0.10)
m.add(A["quarter"], sub_boom(0.6, 50), gain=0.25)
m.add(A["motor"] + 0.2, whoosh(0.7, 800, 4000, seed=10), gain=0.12)
for j, n in enumerate([78, 83, 85, 90]):
    m.add(A["ninety"] + j * 0.04, bell(mtof(n), 0.9, 0.3), gain=0.09, verb=0.35)
m.add(A["three"], sub_boom(0.8, 46), gain=0.4)
m.add(A["three"], snare(), gain=0.15)

# ---------------------------------------------------------------- cost: 6.60 counts down to 3
m.add(A["six"], click(1200, 0.03), gain=0.2)
tc = A["threed"] - 0.25
while tc < A["threed"] + 0.35:
    u = (tc - A["threed"] + 0.25) / 0.6
    m.add(tc, click(3000 - 1400 * u, 0.01), gain=0.09)
    tc += 0.035
m.add(A["threed"] + 0.4, bell(mtof(85), 1.0, 0.35), gain=0.10, verb=0.3)

# ---------------------------------------------------------------- CO2 counter, cars drive off
tc = A["co2"] + 0.3
while tc < A["forty"] + 0.35:
    u = (tc - A["co2"] - 0.3) / max(0.5, A["forty"] + 0.05 - A["co2"] - 0.3)
    m.add(tc, click(1600 + 1600 * u, 0.01), gain=0.07)
    tc += 0.05 + 0.06 * u ** 2
m.add(A["forty"] + 0.3, sub_boom(1.2, 44), gain=0.55)
for j, n in enumerate([66, 73, 78, 81]):
    m.add(A["forty"] + 0.32 + j * 0.04, bell(mtof(n), 1.4, 0.5), gain=0.08, verb=0.5)
m.add(A["nine"], kick(0.4), gain=0.3)
for j in range(9):
    m.add(A["road"] - 0.2 + j * 0.08, whoosh(0.5, 900, 300, seed=20 + j), gain=0.06, pan=-0.6 + j * 0.15)

# ---------------------------------------------------------------- the airliner, 2031, -40 %
m.add(A["plane"], whoosh(1.0, 200, 1800, seed=30), gain=0.2)
hum = np.sin(2 * np.pi * 110 * tt(2.5)) * 0.5 + np.sin(2 * np.pi * 220 * tt(2.5)) * 0.3
m.add(A["plane"] + 0.2, hum * np.sin(np.pi * tt(2.5) / 2.5) ** 2, gain=0.05)
m.add(A["battery1"] - 0.5, riser(0.8, 300, 1500), gain=0.10)
m.add(A["y2031"], sub_boom(0.8, 50), gain=0.35)
m.add(A["y2031"], bell(mtof(85), 1.0, 0.4), gain=0.09, verb=0.4)
m.add(A["pct40"] - 0.1, snare(), gain=0.22)
m.add(A["pct40"] - 0.1, sub_boom(0.8, 46), gain=0.45)

# ---------------------------------------------------------------- the catch: heavy thud, wear, better every year
m.add(A["catch"], tri(mtof(42), 0.8, rel=0.4), gain=0.12)
m.add(A["heavy"] + 0.05, sub_boom(1.0, 38), gain=0.7)
m.add(A["heavy"] + 0.05, kick(0.5), gain=0.5)
m.add(A["wears"], whoosh(0.8, 2000, 300, seed=40), gain=0.12)
for j in range(5):
    m.add(A["better"] + j * 0.08, pluck(mtof(73 + [0, 4, 7, 12, 16][j]), 0.6, 0.6), gain=0.11, verb=0.3)

# ---------------------------------------------------------------- home: glide back, riser into the frame-0 hit
m.add(A["home"], whoosh(END - A["home"], 300, 3000, seed=11), gain=0.14)
m.add(END - 0.6, riser(0.6, 300, 2400), gain=0.2)

# ---------------------------------------------------------------- narrator (last: ducks everything above)
cues = place([(T[k], TEXT[k]) for k, _ in LINES], end=END, max_late=0.08)
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
out = os.path.join(HERE, "v042.wav")
m.render(out, rt=1.4)
print(out)
