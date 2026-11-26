"""037 audio (original): stopwatch ticks every quarter clock-second (so they speed up with 2x / 3x), pitch rising
toward the target, a bright ding on the one target frame, a boom + stamp hit when the clock freezes, a pulse
bass that gets busier each round, a rewind whoosh into the loop. No voice. 48 kHz."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from kit import *
from hook import hook_sfx
import render as R

m = Mix(R.DUR)
BPM = 120; BEAT = 60 / BPM
CH = [[45, 52, 57], [41, 48, 53], [43, 50, 55], [40, 47, 52]]     # Am F G Em (low)
for b in range(int(R.DUR / (2 * BEAT)) + 1):
    t0 = b * 2 * BEAT
    if t0 >= R.DUR: break
    m.add(t0, pad([mtof(x) for x in CH[b % 4]], 2 * BEAT + 0.2, a=0.08, r=0.4, lp=1200, seed=b), gain=0.35, verb=0.3)
hook_sfx(m, reveal=R.ROUNDS[0]["stop"])
for k, Rd in enumerate(R.ROUNDS):
    run_i, stop_i = round(Rd["run"] * FPS), round(Rd["stop"] * FPS)
    # ticks on every quarter of a clock second
    last_q = None
    for i in range(run_i, stop_i + 1):
        v = Rd["v0"] + (i - run_i) * Rd["speed"] / FPS
        q = int(np.floor(v * 4 + 1e-9))
        if last_q is not None and q != last_q:
            prox = 1 - min(1.0, abs(Rd["target"] - v) / 2.5)
            m.add(i / FPS, click(2000 + 1400 * prox, 0.02), gain=0.28)
            m.add(i / FPS, tri(mtof(72 + int(12 * prox)), 0.05), gain=0.06 + 0.06 * prox)
        last_q = q
    # the one target frame
    th = Rd["hit_i"] / FPS
    for j, n in enumerate([84, 88, 91, 96]):
        m.add(th + j * 0.02, bell(mtof(n), 1.0, 0.35), gain=0.16, verb=0.4)
    # freeze: stamp hit (round 1's is in hook_sfx)
    ts = Rd["stop"]
    if k > 0:
        m.add(ts - 0.35, riser(0.35, 500, 2000), gain=0.2)
        m.add(ts, sub_boom(1.0, 48), gain=0.65)
        m.add(ts, snare(), gain=0.25)
    m.add(ts + 0.02, pulse(mtof(40), 0.35, duty=0.5, lp=900), gain=0.18)      # low buzz: missed
    # pulse bass, busier each round
    t = Rd["run"]
    n = 0
    while t < ts - 0.05:
        if n % (4 // (k + 1) if k < 2 else 1) == 0:
            m.add(t, kick(), gain=0.45)
        m.add(t, pulse(mtof(CH[int(t / (2 * BEAT)) % 4][0]), 0.12, duty=0.3, lp=700), gain=0.12)
        t += BEAT / 2; n += 1
for tb in (R.ROUNDS[1]["t0"], R.ROUNDS[2]["t0"]):
    m.add(tb - 0.3, whoosh(0.5, 400, 4000), gain=0.28)
m.add(R.REWIND0, whoosh(0.65, 4000, 300), gain=0.3)
for j, n in enumerate([76, 79, 84]):
    m.add(10.9 + j * 0.12, bell(mtof(n), 1.4, 0.5), gain=0.12, verb=0.5)
m.render("v037.wav", rt=1.6)
print("ok")
