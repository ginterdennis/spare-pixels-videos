"""Case 2 Part 1 ("The parcel") score + sound design + narrator (voice A+), synced to src/c2p1.json -> out/c2p1.wav"""
import json
from audio_lib import *
from hook import hook_sfx
from voice import narrate, place

T = json.load(open("src/c2p1.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.42, quiet=[(T["reveal"], T["reveal"] + 0.8), (T["since"], T["since"] + 0.7)])
hook_sfx(m, gain=0.8)


def error(t):
    m.add(t, tri(mtof(55), 0.16), gain=0.3)
    m.add(t + 0.17, tri(mtof(49), 0.36), gain=0.3)


def knock(t, n=2):
    for k in range(n):
        m.add(t + k * 0.16, sub_boom(0.12, 110), gain=0.5)
        m.add(t + k * 0.16, click(900, 0.02), gain=0.3)


# A: door opens, "delivered" ping, empty doormat
m.add(0.02, whoosh(0.4, 200, 1200), gain=0.2)
notify(m, 0.12)
m.add(T["reveal"], sub_boom(0.5, 52), gain=0.4)
slap(m, T["reveal"])
error(T["reveal"] + 0.1)

# B: the delivery photo, the walk down to 2A
pop(m, T["photo"][0], 79)
m.add(T["photo"][0] + 0.55, click(2200, 0.02), gain=0.25)
m.add(T["photo"][0] + 0.6, marimba(mtof(84), 0.3), gain=0.16)
thunk(m, T["walk0"])

# B + C: every leg = quick steps, every arrival = a knock + pop for the neighbour's answer
for i, (a, b) in enumerate(T["legs"]):
    steps(m, a, b, gain=0.32, rate=0.07)
    if i < len(T["legs"]) - 1:
        knock(b - 0.05)
        pop(m, b + 0.12, 76 + (i * 3) % 12)
m.add(T["stairsLine"], riser(0.5), gain=0.15)

# D: knock on 4B, the door opens, "since Tuesday"
thunk(m, T["sD"][0])
knock(T["knock"], 3)
m.add(T["knock"] + 0.5, whoosh(0.4, 300, 900), gain=0.15)
wahwah(m, T["since"] + 0.1)
m.add(T["handover"], marimba(mtof(72), 0.3), gain=0.18)

# E: December: parcels pile up at every door
thunk(m, T["sE"][0])
for k in range(30):
    t = T["sE"][0] + 0.3 + (k / 30) * (1.2 / 2.2)
    m.add(t, click(1200 + 40 * (k % 9), 0.02), gain=0.12, pan=((k % 5) - 2) * 0.2)
m.add(T["sE"][0] + 0.9, bell(mtof(88), 1.0, 0.5), gain=0.08, verb=0.4)

# card + loop back to the landing
card(m, T["card"])
zoom_in(m, T["cardOut"] + 0.05, T["end"] - T["cardOut"])

cues = place([
    (0.0, "How one parcel visited 7 flats."),
    (T["reveal"] + 0.05, "Delivered. Where?"),
    (T["photo"][0] + 0.05, "The photo shows the wrong door."),
    (T["legs"][0][1] + 0.05, "That neighbor passed it on."),
    (T["sC"][0] + 0.1, "So did the next one."),
    (T["next2"], "And the next. And the next."),
    (T["stairsLine"], "160 stairs later..."),
    (T["flat7"] + 0.05, "Flat 7 was right next door."),
    (T["since"] + 0.05, "It's been there since Tuesday."),
    (T["sE"][0] + 0.1, "Now picture December."),
    (T["ask"] + 0.05, "Where does your parcel end up?"),
    (T["card"] + 0.1, "Part 2: one box by the front door."),
], end=T["end"])
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
m.render("out/c2p1.wav", rt=1.4)
print("out/c2p1.wav")
