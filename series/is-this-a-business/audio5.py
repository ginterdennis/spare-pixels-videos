"""Part 5 score + sound design + narrator (voice A+), synced to src/part5.json -> out/part5.wav"""
import json
from audio_lib import *
from hook import hook_sfx
from voice import narrate, place

T = json.load(open("src/part5.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.42, quiet=[(T["stamp"], T["stamp"] + 0.8), (T["zero"], T["zero"] + 0.7)])
hook_sfx(m, gain=0.8)


def error(t):
    """Low two-note 'nope'."""
    m.add(t, tri(mtof(55), 0.16), gain=0.3)
    m.add(t + 0.17, tri(mtof(49), 0.36), gain=0.3)


def stamp(t):
    m.add(t, sub_boom(0.5, 52), gain=0.4)
    slap(m, t)


# A: notice slapped on the running washer, BY FRIDAY stamp
slap(m, 0.03)
hum(m, 0, T["sA"][1])
stamp(T["stamp"])
error(T["stamp"] + 0.1)

# B: the counter rolls back to 640, every door opens
thunk(m, T["sB"][0])
ticks(m, T["roll"][0], T["roll"][1], rate=0.05)
m.add(T["roll"][1], sub_boom(0.6, 46), gain=0.3)
for i in range(6):
    t = T["nb0"] + i * T["nbGap"]
    pop(m, t, 72 + (i * 5) % 12)

# C: the landlord, the phone, the zero
thunk(m, T["sC"][0])
wahwah(m, T["who"] + 0.05)
pop(m, T["phone"], 79)
for i in range(3):
    m.add(T["phone"] + 0.15 + i * 0.25, click(1800 + 300 * i, 0.02), gain=0.2, pan=0.3)
m.add(T["zero"] - 0.4, riser(0.4), gain=0.18)
ding_chord(m, T["zero"])
m.add(T["zero"] + 0.1, whoosh(0.5), gain=0.2)

# D: "I own 12 houses." + a box pops on every house
pop(m, T["own"], 84)
thunk(m, T["grid0"])
for i in range(12):
    t = T["grid0"] + 0.5 + i * T["gridGap"]
    m.add(t, marimba(mtof(72 + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19][i]), 0.3), gain=0.18, pan=(i % 3 - 1) * 0.4)
m.add(T["grid0"] + 0.5 + 12 * T["gridGap"] + 0.05, bell(mtof(91), 1.2, 0.5), gain=0.12, verb=0.4)

# E: notice crossed out, "Make me 12."
thunk(m, T["sE"][0])
m.add(T["cross"], whoosh(0.3), gain=0.25)
m.add(T["cross"] + 0.25, whoosh(0.3), gain=0.25)
slap(m, T["note"])
notify(m, T["note"] + 0.1)
ding_chord(m, T["note"] + 0.5, notes=(77, 81, 84, 89))

# card + loop back to the basement
card(m, T["card"])
zoom_in(m, T["cardOut"] + 0.05, T["end"] - T["cardOut"])

cues = place([
    (0.0, "The landlord found the box."),
    (T["stamp"], "Remove it by Friday."),
    (T["sB"][0] + 0.05, "No box means 640 stairs again."),
    (T["panic"] + 0.05, "The whole house panics."),
    (T["sC"][0] + 0.1, "Jonas showed him one number."),
    (T["sC"][0] + 1.9, "Angry washer notes since the box: zero."),
    (T["sD"][0] + 0.05, "He owns 12 houses."),
    (T["grid0"] + 0.05, "He wants a box in all of them."),
    (T["sE"][0] + 0.1, "From 640 stairs to 12 customers."),
    (T["ask"] + 0.05, "Would your landlord say yes?"),
    (T["card"] + 0.1, "Case one: closed."),
], end=T["end"])
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
m.render("out/part5.wav", rt=1.4)
print("out/part5.wav")
