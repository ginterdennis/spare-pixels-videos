import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import *
import render as R

m = Mix(R.DUR)
T_END = R.T1 + 0.75
# pads
m.add(0.0, pad([mtof(x) for x in [50, 57, 61, 64, 66]], 7.6, a=1.2, r=1.2, lp=1600, seed=1), gain=0.6, verb=0.4)
m.add(7.0, pad([mtof(x) for x in [47, 54, 57, 62, 66]], 7.6, a=1.2, r=1.2, lp=1600, seed=2), gain=0.6, verb=0.4)
m.add(13.8, pad([mtof(x) for x in [43, 50, 54, 59, 62]], 2.0, a=0.6, r=0.8, lp=1600, seed=3), gain=0.55, verb=0.4)
m.add(T_END, pad([mtof(x) for x in [38, 50, 57, 61, 64, 69]], R.DUR - T_END, a=0.3, r=2.5, lp=2600, seed=4), gain=0.7, verb=0.5)
# music box arpeggio (D major pentatonic random walk), 90 bpm eighths
scale = [62, 64, 66, 69, 71, 74, 76, 78, 81]
rng = np.random.default_rng(11)
idx = 4; t = 0.4
while t < R.T1:
    idx = int(np.clip(idx + rng.choice([-2, -1, 1, 2, 0]), 0, len(scale) - 1))
    m.add(t, bell(mtof(scale[idx]), 1.4, 0.45), pan=rng.uniform(-0.5, 0.5), gain=0.13, verb=0.6)
    t += 60 / 90 / 2 * (2 if rng.random() < 0.3 else 1)
# pencil scratch following the pen
n = int(R.DUR * SR)
tt_ = np.arange(n) / SR
u = np.clip((tt_ - R.T0) / (R.T1 - R.T0), 0, 0.99999)
active = (tt_ >= R.T0) & (tt_ < R.T1)
pdn = R.PD[(u * R.NT).astype(int)] & active
spd = np.abs(np.diff(R.TR, append=R.TR[:1]))
spd = spd[(u * R.NT).astype(int)]; spd = spd / spd.max()
amp = signal.sosfiltfilt(sos("lowpass", 30), pdn.astype(float) * (0.4 + 0.6 * spd))
scr = signal.sosfilt(sos("bandpass", [2500, 7000]), np.random.default_rng(5).standard_normal(n)) * amp
grain = 1 + 0.5 * signal.sosfilt(sos("lowpass", 60), np.random.default_rng(6).standard_normal(n))
m.add(0, scr * grain, gain=0.09)
# chimes at pen lifts
lifts = np.where(R.PD[:-1] & ~R.PD[1:])[0] / R.NT
for k, s_ in enumerate(lifts):
    tl = R.T0 + s_ * (R.T1 - R.T0)
    if tl < R.T1 - 0.2:
        m.add(tl, bell(mtof([81, 86][k % 2]), 2.0, 0.7), gain=0.25, verb=0.6)
# finish
for n_ in [62, 66, 69, 74, 78, 81]:
    m.add(T_END + (n_ - 62) * 0.012, bell(mtof(n_), 3.5, 1.3), gain=0.17, verb=0.7)
m.add(T_END, sub_boom(1.8, 40), gain=0.5)
m.render("v005.wav", rt=2.6)
print("lifts at", [round(R.T0 + s * (R.T1 - R.T0), 2) for s in lifts])
