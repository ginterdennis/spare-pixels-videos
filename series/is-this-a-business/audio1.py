"""Part 1 score + sound design, synced to src/part1.json -> out/part1.wav"""
import json
from audio_lib import *

T = json.load(open("src/part1.json"))
m = Mix(T["end"])
CU = [T["s2"], T["s4"], T["s6"], T["s8"]]
bed(m, 0, T["end"], gain=0.5, quiet=[tuple(T["s4"]), (T["s8"][0], T["s8"][0] + 1.6)])

# frame 0: start with a downbeat so the hook lands with sound
m.add(0.0, sub_boom(0.8, 50), gain=0.25)

# stairs (the overview walks)
steps(m, T["walk1"][0], T["walk1"][1])
for a, up in [("up3", True), ("down3", False), ("up5", True), ("down5", False), ("up7", True), ("down7", False), ("up9", True)]:
    steps(m, T[a][0], T[a][1], up=up)

# zooms between the house and the basement
for s in ["s1", "s3", "s5", "s7"]:
    zoom_in(m, T[s][1] - T["zoomIn"], T["zoomIn"])
for s in ["s3", "s5", "s7", "s9"]:
    zoom_out(m, T[s][0], T["zoomOut"])
for s in CU:
    thunk(m, s[0])

# time tags
for k in ["tag3", "tag5", "tag7"]:
    pop(m, T[k], 88)

# washer
hum(m, T["s2"][0], T["s2"][1])
beeps(m, T["s4"][0] + 0.15)                      # END beeps: done, but full
ticks(m, T["clock4"][0], T["clock4"][1])         # 20 minutes fly by
for k in range(int((T["move6"][1] - T["move6"][0]) * 2.6)):
    flop(m, T["move6"][0] + 0.19 + k / 2.6, seed=k)
m.add(T["start6"], click(1200, 0.03), gain=0.3)
hum(m, T["start6"], T["s6"][1])
hum(m, T["s8"][0], T["s8"][1], gain=0.4)
wahwah(m, T["s8"][0] + 0.3)                      # someone moved HIS laundry
slap(m, T["note8"])

# payoff + crowd + end card
ding_chord(m, T["total9"])
for k in range(int((T["card"] - T["crowd9"]) / 0.05)):
    t = T["crowd9"] + k * 0.05
    m.add(t, click(900 + (k * 377) % 1100, 0.018), gain=0.16, pan=((k * 0.37) % 1.2) - 0.6)
card(m, T["card"])
m.add(T["cardOut"], whoosh(0.4, 3000, 400, seed=9), gain=0.2)

m.render("out/part1.wav", rt=1.4)
print("out/part1.wav")
