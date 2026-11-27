"""Case 3 ("Locked out") score + sound design + narrator (voice A+), synced to src/c3p1.json -> out/c3p1.wav"""
import json
from audio_lib import *
from hook import hook_sfx
from voice import narrate, place

T = json.load(open("src/c3p1.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.42, quiet=[(T["reveal"], T["reveal"] + 0.8), (T["open"], T["open"] + 0.8), (T["die"], T["die"] + 0.6)])
hook_sfx(m, gain=0.8)


def error(t):
    m.add(t, tri(mtof(55), 0.16), gain=0.3)
    m.add(t + 0.17, tri(mtof(49), 0.36), gain=0.3)


def latch(t):
    """The door falling shut: a thud and the latch clicking in."""
    m.add(t, sub_boom(0.45, 60), gain=0.55)
    m.add(t, kick(0.25), gain=0.4)
    m.add(t + 0.03, click(1800, 0.02), gain=0.45)
    m.add(t + 0.09, click(2600, 0.015), gain=0.4)


def jingle(t, n=6):
    for k in range(n):
        m.add(t + k * 0.045, bell(mtof(96 + (k * 5) % 7), 0.25, 0.08), gain=0.06, pan=0.3 - 0.1 * k)


def register(t):
    """Till 'ka-ching' for the bill going up."""
    m.add(t, click(1500, 0.02), gain=0.3)
    m.add(t + 0.06, bell(mtof(91), 0.8, 0.3), gain=0.12, verb=0.3)
    m.add(t + 0.06, bell(mtof(96), 0.8, 0.3), gain=0.09, verb=0.3)


def power_down(t):
    d = 0.6
    x = tt(d)
    f = 900 * np.exp(-x / 0.18) + 60
    ph = np.cumsum(f) / SR
    m.add(t, np.sin(2 * np.pi * ph) * np.clip((d - x) / 0.1, 0, 1), gain=0.22)


# A: steps out, the door falls shut behind him, LOCKED OUT, keys inside
steps(m, 0.0, 0.42, gain=0.25, rate=0.16)
m.add(0.02, whoosh(0.4, 300, 1400), gain=0.18)
latch(T["slam"])
flop(m, T["slam"] + 0.32)
m.add(T["reveal"], sub_boom(0.5, 52), gain=0.4)
slap(m, T["reveal"])
error(T["reveal"] + 0.1)
pop(m, T["xray"], 79)
jingle(T["xray"] + 0.1)

# B: the call; the bill goes up twice
thunk(m, T["sB"][0])
beeps(m, T["sB"][0] + 0.15, n=2, f=440)
register(T["q1"])
pop(m, T["q2"], 76)
register(T["dbl"])
slap(m, T["dbl"])

# C: 70 minutes on the landing, the battery drops, the phone dies
thunk(m, T["sC"][0])
ticks(m, T["sC"][0] + 0.15, T["sC"][0] + 2.05, rate=0.12)
for t in (T["sC"][0] + 0.8, T["sC"][0] + 1.4):
    beeps(m, t, n=1, f=1760)
power_down(T["die"])

# D: the locksmith arrives, the door opens straight away, the invoice
thunk(m, T["sD"][0])
steps(m, T["sD"][0], T["sD"][0] + 0.75, gain=0.3, rate=0.16)
m.add(T["open"] - 0.25, click(3200, 0.02), gain=0.25)
m.add(T["open"], whoosh(0.45, 300, 1100), gain=0.2)
m.add(T["open"] + 0.05, marimba(mtof(72), 0.3), gain=0.18)
pop(m, T["bill"], 74)
slap(m, T["paid"])
m.add(T["paid"], sub_boom(0.4, 50), gain=0.3)

# E: the kiosk downstairs (shop bell), the key flies over, the receipt
thunk(m, T["sE"][0])
m.add(T["sE"][0] + 0.15, bell(mtof(88), 1.0, 0.4), gain=0.1, verb=0.35)
m.add(T["sE"][0] + 0.27, bell(mtof(84), 1.0, 0.4), gain=0.09, verb=0.35)
m.add(T["hand"], whoosh(0.6, 600, 2400, seed=8), gain=0.15)
jingle(T["hand"] + 0.6)
for k in range(3):
    pop(m, T["rcpt"] + (0.05, 0.2, 1.75)[k], 79 + k * 3)
ding_chord(m, T["rcpt"] + 1.8)

# F: the question, the card, loop back to the landing
pop(m, T["ask"], 84)
card(m, T["card"])
zoom_in(m, T["cardOut"] + 0.05, T["end"] - T["cardOut"])

cues = place([
    (0.0, "How one door click became €240."),
    (T["reveal"] + 0.6, "Locked out."),
    (T["sB"][0] + 0.05, "Locksmith: €120."),
    (T["q2"] + 0.02, "Saturday night? Double."),
    (T["sC"][0] + 0.07, "70 minutes in his socks."),
    (T["open"] + 0.02, "The door wasn't even locked."),
    (T["bill"] + 0.05, "That's 240 euros, please."),
    (T["sE"][0] + 0.07, "Idea: the kiosk keeps your spare key."),
    (T["rcpt"] + 0.02, "€2 a month. One lockout pays for 10 years."),
    (T["ask"] + 0.04, "Is this a business? Yes or no?"),
], end=T["end"], max_late=0.35)
spans = narrate(m, cues)
for s in spans:
    print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s['text']}")
m.render("out/c3p1.wav", rt=1.4)
print("out/c3p1.wav")
