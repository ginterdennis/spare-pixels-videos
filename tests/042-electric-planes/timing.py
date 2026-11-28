"""042 electric planes timing: one source of truth for render.py and audio.py (built like the 041 playbook).
Full sentences; the last line runs into the first on the loop ("...and that is why" > "Electric planes are coming...")."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

LINES = [  # key, text
    ("hook", "Electric planes are coming for one in four flights."),
    ("short", "That's how many flights are shorter than 500 kilometers, like Munich to Vienna."),
    ("fuel", "On a hop like that, a propeller plane turns only a quarter of its fuel into useful power."),
    ("motor", "An electric motor turns over 90 percent into power, so it needs up to three times less energy."),
    ("cost", "For each passenger on a 200 kilometer hop, the energy bill drops from about six dollars to about three."),
    ("co2", "If every flight under 500 kilometers went electric on clean power, we'd save up to 40 million tonnes of CO2 a year."),
    ("cars", "That's like taking nine million cars off the road."),
    ("plane", "A 36-seat airliner built to fly 200 kilometers on battery alone is planned for 2031."),
    ("promise", "Its maker promises 40 percent lower operating costs."),
    ("catch", "The catch is the battery: it's heavy, and it wears out."),
    ("loop", "But batteries get better every year, and that is why"),
]
GAP = {"hook": 0.40, "short": 0.22, "fuel": 0.12, "motor": 0.22, "cost": 0.25, "co2": 0.12, "cars": 0.28,
       "plane": 0.12, "promise": 0.25, "catch": 0.18}
PAD = 0.18
LOOP_PAUSE = 0.10    # "...and that is why" runs straight into the hook line on the loop

TEXT = {k: s for k, s in LINES}
_W = {}
_path = os.path.join(HERE, "words.json")
if os.path.isfile(_path):
    _W = json.load(open(_path))


_NUM = {str(i): w for i, w in enumerate("zero one two three four five six seven eight nine ten".split())}


def _norm(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return _NUM.get(w, w)          # Whisper writes "$6" / "3." / "9" for "six" / "three" / "nine"


DUR = {}
for k, s in LINES:
    DUR[k] = _W[k]["dur"] if k in _W else 0.30 * len(s.split()) + 0.3

T = {}
t = 0.0
for k, _ in LINES:
    T[k] = round(t, 3)
    t += DUR[k] + GAP.get(k, PAD)
END = round(T["loop"] + DUR["loop"] + LOOP_PAUSE, 2)
T["end"] = END


def wt(key, word, end=False, occ=0):
    want = _norm(word)
    if key in _W:
        hits = [w for w in _W[key]["words"] if _norm(w[0]) == want]
        if len(hits) <= occ:
            hits = [w for w in _W[key]["words"] if want and _norm(w[0]).startswith(want)]
        if len(hits) > occ:
            return T[key] + (hits[occ][2] if end else hits[occ][1])
    s = TEXT[key].lower()
    i = -1
    for _ in range(occ + 1):
        i = s.find(word.lower(), i + 1)
    i = max(i, 0)
    frac = (i + (len(word) if end else 0)) / len(s)
    return T[key] + DUR[key] * frac


A = {}
A["flip"] = 2.40                                    # the 2-3 s beat: a quarter of the routes flip to electric
A["short"] = T["short"]
A["km500"] = wt("short", "500")
A["munich"] = wt("short", "munich")
A["vienna"] = wt("short", "vienna")
A["fuel"] = T["fuel"]
A["quarter"] = wt("fuel", "quarter")
A["fuelw"] = wt("fuel", "fuel")
A["motor"] = T["motor"]
A["ninety"] = wt("motor", "90")
A["three"] = wt("motor", "three")
A["cost"] = T["cost"]
A["six"] = wt("cost", "six")
A["threed"] = wt("cost", "three")
A["co2"] = T["co2"]
A["clean"] = wt("co2", "clean")
A["forty"] = wt("co2", "40")
A["cars"] = T["cars"]
A["nine"] = wt("cars", "nine")
A["road"] = wt("cars", "road")
A["plane"] = T["plane"]
A["battery1"] = wt("plane", "battery")
A["y2031"] = wt("plane", "2031")
A["promise"] = T["promise"]
A["pct40"] = wt("promise", "40")
A["catch"] = T["catch"]
A["heavy"] = wt("catch", "heavy")
A["wears"] = wt("catch", "wears")
A["loop"] = T["loop"]
A["better"] = wt("loop", "better")
A["home"] = wt("loop", "every")                     # glide back to the frame-0 picture
A["home_end"] = END - 2 / 30

if __name__ == "__main__":
    for k, _ in LINES:
        print(f"{k:9s} {T[k]:6.2f} - {T[k] + DUR[k]:6.2f}")
    for k, v in A.items():
        print(f"  {k:10s} {v:6.2f}")
    print("end", END)
