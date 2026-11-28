"""041 score + sound design + narrator (voice A+, tightened and 10 % faster via vo.py) -> v041.wav.
One soundtrack for all three looks: they share timing.py beat for beat."""
import sys, os, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import vo  # noqa: F401  (patches voice.say before narrate/place use it)
from kit import *
from hook import hook_sfx
from voice import narrate, place
from timing import T, TEXT, LINES, A, END

HERE = os.path.dirname(os.path.abspath(__file__))
m = Mix(END)
rng = np.random.default_rng(41)

# ---------------------------------------------------------------- bed: Am F C G, bars tile the video exactly (loop)
NBAR = 4 * max(1, round(END / 9.6))          # whole 4-chord cycles over the video: ends on G, loops into Am
BAR = END / NBAR
BEAT = BAR / 4
CH = [(57, 60, 64, 69), (53, 57, 60, 65), (48, 52, 55, 60), (55, 59, 62, 67)]   # Am F C G
for k in range(NBAR):
    t = k * BAR
    ch = CH[k % 4]
    if A["ends"] + 0.35 <= t < A["new"] - 0.1:
        continue
    g = 0.20 if t < A["crack"] else 0.28
    m.add(t, pad([mtof(n) for n in ch], BAR + 0.5, a=0.3, r=0.5, lp=1400, seed=k), gain=g)
    m.add(t, tri(mtof(ch[0] - 12), BAR * 0.9, rel=0.3), gain=0.10)
for b in np.arange(0, END - 1e-6, BEAT):
    quiet = (b < A["crack"]) or (A["rw0"] - 0.05 < b < T["origin"] + 0.2) or (A["ends"] + 0.3 < b < A["new"])
    if not quiet:
        m.add(b, kick(0.3), gain=0.12)
for b in np.arange(0, END - 1e-6, BEAT / 2):
    if A["sudoku"] <= b < A["gap"]:
        m.add(b, hat(0.04), gain=0.045, pan=0.3)


def arps(t0, t1, gain=0.05):
    t, j = math.ceil(t0 / (BEAT / 2)) * BEAT / 2, 0
    while t < t1:
        ch = CH[int(t / BAR) % 4]
        n = ch[j % 4] + 12 + (12 if j % 8 >= 4 else 0)
        m.add(t, pluck(mtof(n), 0.5, 0.5), gain=gain, pan=0.3 if j % 2 else -0.3, verb=0.3)
        t += BEAT / 2
        j += 1


arps(A["also"], A["ends"])
arps(A["experts"], A["home"], 0.04)

# ---------------------------------------------------------------- hook: hit at 0 (the loop lands here), crack, lock snaps
hook_sfx(m, reveal=A["crack"], gain=0.9)
m.add(A["crack"], signal.sosfilt(sos("highpass", 2500), noise(0.25, 4)) * np.exp(-tt(0.25) / 0.05), gain=0.25)
for j in range(5):
    tj = A["crack"] + 0.05 + 0.08 * j
    m.add(tj, click(3200 - 200 * j, 0.02), gain=0.3, pan=-0.5 + 0.25 * j)
    m.add(tj + 0.01, click(900, 0.03), gain=0.18)
dr = T["origin"] - A["rw0"]
m.add(A["rw0"], whoosh(dr + 0.1, 3500, 250, seed=5), gain=0.3)
x = tt(dr)
f = 600 * (60 / 600) ** (x / dr)
m.add(A["rw0"], np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - x / dr) * 0.4, gain=0.25)

# ---------------------------------------------------------------- origin
tc = A["rw0"] + 0.05
while tc < A["year"]:
    u = (tc - A["rw0"]) / (A["year"] - A["rw0"])
    m.add(tc, click(2200 + 400 * (1 - u), 0.012), gain=0.12)
    tc += 0.03 + 0.09 * u ** 2
m.add(A["year"], sub_boom(0.8, 50), gain=0.45)
m.add(A["year"], bell(mtof(81), 1.2, 0.4), gain=0.08, verb=0.4)
for j, n in enumerate([76, 81, 88]):
    m.add(A["tick"] + j * 0.04, bell(mtof(n), 1.0, 0.35), gain=0.10, verb=0.35)
m.add(A["findw"] + 0.05, tri(mtof(46), 1.2, rel=0.4), gain=0.10)
m.add(A["qmark"], bell(mtof(70), 0.9, 0.4), gain=0.08)
m.add(A["qmark"] + 0.06, bell(mtof(71), 0.9, 0.4), gain=0.06)

# ---------------------------------------------------------------- sudoku: draw, check row / column / box, solve, grow
m.add(A["sudoku"], whoosh(0.6, 500, 3500, seed=13), gain=0.16)
for j in range(27):
    m.add(A["sudoku"] + 0.25 + j * 0.012, click(1800 + 40 * j, 0.01), gain=0.06, pan=-0.6 + 1.2 * (j % 9) / 8)
m.add(A["easy"], bell(mtof(84), 0.9, 0.35), gain=0.09, verb=0.3)
for j, key in enumerate(["row", "col", "box"]):
    for q in range(9):
        m.add(A[key] + q * 0.02, click(2400 + 120 * j + 30 * q, 0.01), gain=0.07, pan=-0.5 + q / 9)
    m.add(A[key], bell(mtof([76, 79, 83][j]), 0.8, 0.3), gain=0.09, verb=0.3)
for j, n in enumerate([84, 88, 91, 96]):
    m.add(A["box"] + 0.55 + j * 0.03, bell(mtof(n), 1.0, 0.35), gain=0.09, verb=0.4)
m.add(A["empty"], whoosh(0.4, 3000, 400, seed=17), gain=0.18)
m.add(A["hard"], sub_boom(0.8, 46), gain=0.4)
m.add(A["hard"], tri(mtof(45), 0.6, rel=0.3), gain=0.10)
tc = A["try"]
while tc < A["gap"] - 0.15:
    u = (tc - A["try"]) / max(0.1, A["gap"] - A["try"])
    m.add(tc, click(rng.uniform(1800, 4200), 0.008), gain=0.05 + 0.04 * u, pan=rng.uniform(-0.8, 0.8))
    tc += 1 / (25 + 30 * u)
m.add(A["try"] + 0.2, riser(0.8, 300, 1500), gain=0.10)
for tb in (A["bigger"], A["bigger"] + 0.95):
    m.add(tb - 0.3, riser(0.3, 400, 2200), gain=0.14)
    m.add(tb, sub_boom(0.9, 46), gain=0.45)
    m.add(tb, snare(), gain=0.15)
m.add(A["atoms"], bell(mtof(93), 1.6, 0.6), gain=0.09, verb=0.6)
m.add(A["atoms"], sub_boom(1.0, 40), gain=0.35)

# ---------------------------------------------------------------- gap: grid folds into a lock, three locks, icons
m.add(A["gap"], whoosh(0.6, 3000, 300, seed=12), gain=0.22)
m.add(A["gap"] + 0.6, kick(0.4), gain=0.35)
m.add(A["gap"] + 0.6, click(700, 0.04), gain=0.3)
for j in range(3):
    m.add(A["locks"] + j * 0.06, click(1100 + 200 * j, 0.03), gain=0.2, pan=-0.6 + 0.6 * j)
for j, ti in enumerate([A["bank"], (A["bank"] + A["wallet"]) / 2, A["wallet"]]):
    m.add(ti, pluck(mtof(76 + 3 * j), 0.6, 0.6), gain=0.12, pan=-0.6 + 0.6 * j, verb=0.3)

# ---------------------------------------------------------------- P = NP: equals slams, the shortcut zaps, locks shatter
m.add(A["equals"], sub_boom(1.0, 46), gain=0.6)
m.add(A["equals"], snare(), gain=0.25)
dz = 0.3
xz = tt(dz)
m.add(A["shortcut"], np.sin(2 * np.pi * np.cumsum(300 * (3000 / 300) ** (xz / dz)) / SR) * np.exp(-xz / 0.2) * 0.5, gain=0.22)
m.add(A["opens"] - 0.5, riser(0.5, 300, 3000), gain=0.2)
m.add(A["opens"], sub_boom(1.4, 42), gain=0.7)
glass = signal.sosfilt(sos("bandpass", [2500, 9000]), noise(0.9, 21)) * np.exp(-tt(0.9) / 0.18)
m.add(A["opens"], glass, gain=0.35)
for j in range(14):
    m.add(A["opens"] + rng.uniform(0, 0.5), bell(rng.uniform(2500, 6000), 0.5, 0.12), gain=0.05,
          pan=rng.uniform(-0.9, 0.9), verb=0.3)

# ---------------------------------------------------------------- also: three builds
m.add(A["routes"], whoosh(0.9, 600, 3000, seed=14), gain=0.12)
for j, n in enumerate([81, 84, 88]):
    m.add(A["routes"] + 0.3 + j * 0.27, pluck(mtof(n), 0.6, 0.6), gain=0.09, verb=0.3)
for j in range(4):
    m.add(A["ai"] + 0.3 + j * 0.22, bell(mtof(84 + 2 * j), 0.6, 0.25), gain=0.07, pan=-0.4 + 0.25 * j, verb=0.3)
tc = A["proofs"] + 0.05
while tc < A["proofs_end"]:
    m.add(tc, click(rng.uniform(2200, 3000), 0.01), gain=0.07, pan=rng.uniform(-0.3, 0.3))
    tc += rng.uniform(0.04, 0.08)
m.add(A["proofs_end"], bell(mtof(88), 1.0, 0.4), gain=0.10, verb=0.4)

# ---------------------------------------------------------------- the world ends / a new one begins
dc = max(0.35, min(0.7, A["new"] - A["ends"] - 0.08))
xc = tt(dc)
m.add(A["ends"], whoosh(dc, 200, 4000, seed=16)[::-1], gain=0.25)
m.add(A["ends"], np.sin(2 * np.pi * np.cumsum(120 + 600 * (xc / dc) ** 2) / SR) * (xc / dc) * 0.3, gain=0.2)
m.add(A["new"], sub_boom(1.8, 40), gain=0.7)
for j, n in enumerate([57, 64, 69, 72, 76, 81]):
    m.add(A["new"] + j * 0.05, bell(mtof(n), 2.4, 0.9), gain=0.08, verb=0.6)
m.add(A["new"], pad([mtof(n) for n in (45, 57, 64, 69)], 2.2, a=0.05, r=1.2, lp=2200, seed=99), gain=0.35)

# ---------------------------------------------------------------- experts, then "Just remember:" glides home into the loop
tc = A["bet"]
while tc < A["false"]:
    u = (tc - A["bet"]) / (A["false"] - A["bet"])
    m.add(tc, click(1800 + 1400 * u, 0.01), gain=0.09)
    tc += 0.04 + 0.08 * u ** 2
m.add(A["false"], bell(mtof(81), 1.0, 0.4), gain=0.09, verb=0.3)
m.add(A["nobody"], click(1200, 0.03), gain=0.2)
m.add(A["nobody"], bell(mtof(64), 1.4, 0.6), gain=0.07, verb=0.4)
gl = signal.sosfilt(sos("bandpass", [400, 5000]), noise(0.35, 31)) * (np.sin(2 * np.pi * 22 * tt(0.35)) > 0)
m.add(A["remember"], gl * np.exp(-tt(0.35) / 0.15), gain=0.25)
m.add(A["home"], whoosh(END - A["home"], 300, 3000, seed=11), gain=0.16)
m.add(END - 0.7, riser(0.7, 300, 2400), gain=0.22)        # rises into the frame-0 hit when the video loops

# ---------------------------------------------------------------- narrator (last: ducks everything above)
cues = place([(T[k], TEXT[k]) for k, _ in LINES], end=END, max_late=0.08)
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
out = os.path.join(HERE, "v041.wav")
m.render(out, rt=1.4)
print(out)
