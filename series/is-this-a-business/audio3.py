"""Part 3 score + sound design, synced to src/part3.json -> out/part3.wav"""
import json
from audio_lib import *

T = json.load(open("src/part3.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.5)
m.add(0.0, sub_boom(0.8, 50), gain=0.25)
slap(m, 0.02)  # notice pinned


def printer(t, n=6):
    for k in range(n):
        m.add(t + k * 0.03, click(1800 + 300 * (k % 2), 0.012), gain=0.18, pan=-0.2)


def kaching(t):
    for k, n in enumerate([84, 88, 91, 96]):
        m.add(t + k * 0.04, bell(mtof(n), 1.0, 0.35), gain=0.12, pan=0.2, verb=0.4)
    m.add(t, noise(0.06, 3) * np.exp(-tt(0.06) / 0.01), gain=0.15)


def yes_blip(t):
    m.add(t, marimba(mtof(79), 0.3), gain=0.28, pan=0.15)
    m.add(t + 0.09, marimba(mtof(84), 0.4), gain=0.28, pan=0.15, verb=0.2)


def no_blip(t):
    m.add(t, tri(mtof(55), 0.16), gain=0.22)
    m.add(t + 0.15, tri(mtof(50), 0.3), gain=0.22)


def sock_blip(t):
    d = 0.5
    f = mtof(72) * (1 + 0.06 * np.sin(2 * np.pi * 7 * tt(d)))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt(d) / 0.25)
    m.add(t, s, gain=0.22, verb=0.3)


# receipt
pop(m, T["s2"][0], 81)
for k in ["r1", "r2", "r3"]:
    printer(T[k])
printer(T["rTotal"], 9)
m.add(T["rTotal"] + 0.05, bell(mtof(84), 1.0, 0.4), gain=0.12)
pop(m, T["rMonth"], 86)
kaching(T["rPaid"])

# the vote
zoom_out(m, T["s3"][0], 0.35)
votes = ["yes", "no", "yes", "sock", "yes", "no", "yes", "yes", "yes", "yes"]
for i, v in enumerate(votes):
    t = T["vote0"] + i * T["voteGap"]
    m.add(t, click(700, 0.03), gain=0.25)  # door
    {"yes": yes_blip, "no": no_blip, "sock": sock_blip}[v](t + 0.08)

# tally on the board
thunk(m, T["s4"][0])
for k in range(10):
    t = T["s4"][0] + 0.2 + k * 0.09
    m.add(t, signal.sosfilt(sos("bandpass", [2000, 6000]), noise(0.06, k)) * np.exp(-tt(0.06) / 0.02), gain=0.25, pan=-0.3 + 0.06 * k)
ding_chord(m, T["s4"][0] + 1.15)

card(m, T["card"])
m.add(T["cardOut"], whoosh(0.4, 3000, 400, seed=9), gain=0.2)

m.render("out/part3.wav", rt=1.4)
print("out/part3.wav")
