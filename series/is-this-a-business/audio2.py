"""Part 2 score + sound design, synced to src/part2.json -> out/part2.wav"""
import json
from audio_lib import *

T = json.load(open("src/part2.json"))
m = Mix(T["end"])
bed(m, 0, T["end"], gain=0.5, quiet=[(T["stop"], T["stop"] + 1.2)])
m.add(0.0, sub_boom(0.8, 50), gain=0.25)


def buzz(t, n=2):
    for k in range(n):
        d = 0.16
        s = np.sin(2 * np.pi * 160 * tt(d)) * np.sign(np.sin(2 * np.pi * 23 * tt(d)))
        m.add(t + k * 0.24, signal.sosfilt(sos("lowpass", 900), s) * np.clip((d - tt(d)) / 0.03, 0, 1), gain=0.3)


# sensor: hum while running, LED blips, then silence + END beeps + a "got it" chime
hum(m, 0, T["stop"] + 0.05)
for k in range(int(T["stop"] * 2)):
    m.add(k * 0.5 + 0.02, click(3400, 0.008), gain=0.12, pan=0.35)
beeps(m, T["stop"] + 0.15)
m.add(T["stop"] + 0.7, bell(mtof(84), 1.2, 0.4), gain=0.12, verb=0.4)
m.add(T["stop"] + 0.82, bell(mtof(91), 1.4, 0.5), gain=0.12, verb=0.4)

# flat: phone up, BUSY -> FREE
pop(m, T["s3"][0] + 0.2, 81)
pop(m, T["free3"], 88)
notify(m, T["free3"] + 0.05)

# trip down
steps(m, T["down4"][0], T["down4"][1])
zoom_in(m, T["s4"][1] - T["zoomIn"], T["zoomIn"])
thunk(m, T["s5"][0])

# load, scan, start
flop(m, T["load5"] + 0.1, 1)
flop(m, T["load5"] + 0.3, 2)
m.add(T["scan5"][0], pulse(1320, 0.08, 0.5, 0.02, 6000), gain=0.18)
m.add(T["scan5"][0] + 0.45, pulse(1760, 0.12, 0.5, 0.02, 6000), gain=0.2)
pop(m, T["phone5"], 84)
m.add(T["start5"], click(1200, 0.03), gain=0.3)
hum(m, T["start5"], T["s5"][1])

# back up
zoom_out(m, T["s6"][0], T["zoomOut"])
steps(m, T["up6"][0], T["up6"][1], up=True)

# phone buzzes: done, then the nudge
pop(m, T["s7"][0] + 0.05, 81)
buzz(T["done7"]); notify(m, T["done7"])
buzz(T["nudge7"], 3); notify(m, T["nudge7"] + 0.05)

# down + up with the laundry, payoff
zoom_out(m, T["s8"][0], T["zoomOut"])
steps(m, T["down8"][0], T["down8"][1])
steps(m, T["up8"][0], T["up8"][1], up=True)
ding_chord(m, T["total8"])
card(m, T["card"])
zoom_in(m, T["cardOut"] + 0.05, T["end"] - T["cardOut"])

m.render("out/part2.wav", rt=1.4)
print("out/part2.wav")
