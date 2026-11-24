"""Part 4 score + sound design + narrator (voice A+), synced to src/part4.json -> out/part4.wav"""
import json
from audio_lib import *
from hook import hook_sfx
from voice import narrate, place

T = json.load(open("src/part4.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.42, quiet=[(T["nosig"], T["nosig"] + 0.9), (T["concrete"], T["concrete"] + 0.8)])
hook_sfx(m, gain=0.8)


def buzz(t, n=2):
    for k in range(n):
        d = 0.16
        s = np.sin(2 * np.pi * 160 * tt(d)) * np.sign(np.sin(2 * np.pi * 23 * tt(d)))
        m.add(t + k * 0.24, signal.sosfilt(sos("lowpass", 900), s) * np.clip((d - tt(d)) / 0.03, 0, 1), gain=0.3)


def error(t):
    """Low two-note 'nope'."""
    m.add(t, tri(mtof(55), 0.16), gain=0.3)
    m.add(t + 0.17, tri(mtof(49), 0.36), gain=0.3)


# A: box pressed on, washer running, NO SIGNAL
slap(m, 0.05)
hum(m, 0, T["sA"][1])
pop(m, T["nosig"], 76)
error(T["nosig"] + 0.05)

# B: 4B walks down for nothing, BUSY?!, walks back up
thunk(m, T["sB"][0])
hum(m, T["sB"][0], T["sB"][1], gain=0.25)
steps(m, T["down"][0], T["down"][1])
zoom_in(m, T["busy"] - T["zoomIn"], T["zoomIn"])
wahwah(m, T["busy"] + 0.05)
zoom_out(m, T["up"][0] - 0.15, T["zoomOut"])
steps(m, T["up"][0], T["up"][1], up=True)

# C: walking down, bars drop
thunk(m, T["sC"][0])
steps(m, T["walk"][0], T["walk"][1], gain=0.3, rate=0.1)
for k in range(4):
    m.add(T["walk"][0] + 0.55 + k * 0.72, tri(mtof(79 - 3 * k), 0.12), gain=0.14, pan=0.3)
m.add(T["concrete"], sub_boom(0.8, 44), gain=0.35)
slap(m, T["concrete"] + 0.02)

# D: the relay box goes up, signal climbs, bars come back, sock
thunk(m, T["sD"][0])
slap(m, T["place"])
pop(m, T["place"] + 0.05, 84)
for k in range(6):
    m.add(T["relay"] + k * 0.25, click(2600 + 200 * k, 0.015), gain=0.18, pan=0.2)
for k in range(4):
    m.add(T["bars"] + k * 0.15, marimba(mtof(76 + 3 * k), 0.4), gain=0.2, pan=0.25)
m.add(T["bars"] + 0.6, bell(mtof(88), 1.2, 0.5), gain=0.1, verb=0.4)
m.add(T["sock"], marimba(mtof(96), 0.3), gain=0.18, pan=0.4)
m.add(T["sock"] + 0.08, marimba(mtof(100), 0.4), gain=0.16, pan=0.4, verb=0.3)

# E: the NO voter gets the first ping
pop(m, T["sE"][0] + 0.1, 81)
buzz(T["ping"])
notify(m, T["ping"])
ding_chord(m, T["ping"] + 1.6)

# card + loop back to the basement
card(m, T["card"])
zoom_in(m, T["cardOut"] + 0.05, T["end"] - T["cardOut"])

cues = place([
    (0.0, "Jonas built it. Day one: silence."),
    (3.2, "The app said free. It wasn't."),
    (5.8, "A hundred and sixty stairs, for nothing."),
    (8.6, "Floor by floor, the Wi-Fi dies."),
    (11.5, "Concrete eats it."),
    (12.85, "The fix: a second six-euro chip at the basement door."),
    (16.6, "It passes the message upstairs."),
    (18.9, "The first ping goes to... the guy who voted no."),
    (22.5, "Next: the landlord finds out."),
], end=T["end"])
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
m.render("out/part4.wav", rt=1.4)
print("out/part4.wav")
