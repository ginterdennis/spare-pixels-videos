"""040 timing: one source of truth for render.py and audio.py.
Durations are voice A+ takes measured with `python3 kit/voice.py measure` (27 Nov 2026)."""

LINES = [  # key, text, measured seconds
    ("hook", "Math's biggest problem just got solved.", 2.80),
    ("ai", "With help from an AI.", 1.52),
    ("primes", "In 1859, Riemann bet the primes hide a pattern:", 3.91),
    ("line", "every key zero sits on one line.", 2.34),
    ("years", "167 years. No proof.", 2.55),
    ("lean", "Now there's a proof in Lean: code a computer checks.", 3.38),
    ("howlong", "How long is it?", 1.20),
    ("big", "17 million lines.", 1.80),
    ("check", "Nobody can read that. Machines checked it: correct.", 3.07),
    ("cut", "Five days later: 76,000 lines.", 3.24),
    ("tidy", "So the primes are as tidy as they can be.", 2.27),
    ("thm", "Every 'if this is true' theorem is now just true.", 3.07),
    ("share", "Send this to someone who hated math.", 2.07),
]
GAP = {"hook": 0.06, "primes": 0.10, "years": 0.12, "big": 0.25, "check": 0.25, "cut": 0.20, "thm": 0.18}
PAD = 0.16          # default pause after a line
TAIL = 1.15         # end card hold after the last line (incl. the loop hand-back)

T, DUR = {}, {}
t = 0.0
for k, text, d in LINES:
    T[k] = round(t, 3)
    DUR[k] = d
    t += d + GAP.get(k, PAD)
T["stamp_ai"] = 2.90            # WITH AN AI. (the 2-3 s beat: raises the stakes)
T["end"] = round(T["share"] + DUR["share"] + TAIL, 2)
TEXT = {k: text for k, text, _ in LINES}

if __name__ == "__main__":
    for k, _, d in LINES:
        print(f"{k:8s} {T[k]:6.2f} - {T[k] + d:6.2f}")
    print("end", T["end"])
