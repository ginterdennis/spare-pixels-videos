"""041 P vs NP (v2, 27 Nov evening) timing: one source of truth for render.py and audio.py.
v2 after the user's notes: full sentences only, the example (a sudoku) laid out and explained,
no share/follow prompt, and a seamless loop: the last line ("Just remember:") runs into the first.
Line durations and word times come from words.json (voice A+ takes + Whisper word timestamps, words.py)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

LINES = [  # key, text
    ("hook", "Proving this would destroy the modern world as we know it."),
    ("origin", "In 1971, Stephen Cook asked: if an answer is easy to check, is it also easy to find?"),
    ("sudoku", "Think of a sudoku."),
    ("check", "Checking a finished one is easy: no number may repeat in a row, a column or a box."),
    ("solve", "But solving an empty one is hard, because you have to try number after number."),
    ("bigger", "Make the grid bigger, and there are more ways to fill it than atoms in the universe."),
    ("gap", "That gap is what keeps your bank and your crypto wallet safe."),
    ("pnp", "If P equals NP, there is a shortcut, and every lock opens."),
    ("also", "But we'd also get perfect routes, smarter AI, and machines that write their own proofs."),
    ("ends", "The modern world would end, and a new one would begin."),
    ("experts", "Most experts bet it's false, and nobody has proven it, not even AI."),
    ("remember", "Just remember:"),
]
GAP = {"hook": 0.42, "origin": 0.25, "sudoku": 0.12, "check": 0.22, "solve": 0.22, "bigger": 0.28, "gap": 0.18,
       "pnp": 0.22, "also": 0.22, "ends": 0.28, "experts": 0.15}
PAD = 0.18
LOOP_PAUSE = 0.32    # after "Just remember:" the video ends on frame 0 and the hook line starts again

TEXT = {k: s for k, s in LINES}
_W = {}
_path = os.path.join(HERE, "words.json")
if os.path.isfile(_path):
    _W = json.load(open(_path))


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


DUR = {}
for k, s in LINES:
    DUR[k] = _W[k]["dur"] if k in _W else 0.30 * len(s.split()) + 0.3

T = {}
t = 0.0
for k, _ in LINES:
    T[k] = round(t, 3)
    t += DUR[k] + GAP.get(k, PAD)
END = round(T["remember"] + DUR["remember"] + LOOP_PAUSE, 2)
T["end"] = END


def wt(key, word, end=False, occ=0):
    """Absolute time of a word inside a narrator line (start, or end with end=True)."""
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
A["crack"] = 2.40                                   # the 2-3 s beat: locks snap open (raises the stakes)
A["rw0"] = T["hook"] + DUR["hook"] + 0.02           # rewind starts
A["year"] = wt("origin", "1971", end=True)
A["cook"] = wt("origin", "stephen")
A["checkw"] = wt("origin", "check")
A["tick"] = wt("origin", "check", end=True)
A["findw"] = wt("origin", "find")
A["qmark"] = wt("origin", "find", end=True)
A["sudoku"] = T["sudoku"]
A["checking"] = T["check"]
A["row"] = wt("check", "row")
A["col"] = wt("check", "column")
A["box"] = wt("check", "box")
A["easy"] = wt("check", "easy")
A["solve"] = T["solve"]
A["empty"] = wt("solve", "empty")
A["hard"] = wt("solve", "hard")
A["try"] = wt("solve", "try")
A["bigger"] = wt("bigger", "bigger")
A["ways"] = wt("bigger", "ways")
A["atoms"] = wt("bigger", "atoms")
A["gap"] = T["gap"]
A["locks"] = wt("gap", "keeps")
A["bank"] = wt("gap", "bank")
A["wallet"] = wt("gap", "wallet")
A["pnp"] = T["pnp"]
A["equals"] = wt("pnp", "equals")
A["shortcut"] = wt("pnp", "shortcut")
A["opens"] = wt("pnp", "opens")
A["also"] = T["also"]
A["routes"] = wt("also", "perfect")
A["ai"] = wt("also", "smarter")
A["proofs"] = wt("also", "machines")
A["proofs_end"] = wt("also", "proofs", end=True)
A["ends"] = wt("ends", "end")
A["new"] = wt("ends", "new")
A["experts"] = T["experts"]
A["bet"] = wt("experts", "experts")
A["false"] = wt("experts", "false", end=True)
A["nobody"] = wt("experts", "nobody")
A["notai"] = wt("experts", "not")
A["remember"] = T["remember"]
A["home"] = T["remember"] - 0.25                    # glide back to the frame-0 picture
A["home_end"] = END - 2 / 30                         # ... fully there before the loop point

if __name__ == "__main__":
    for k, _ in LINES:
        print(f"{k:9s} {T[k]:6.2f} - {T[k] + DUR[k]:6.2f}")
    for k, v in A.items():
        print(f"  {k:10s} {v:6.2f}")
    print("end", END)
