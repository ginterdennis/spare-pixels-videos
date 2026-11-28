# 040 "Math's biggest problem just got SOLVED." (NEWS #1, current-affairs explainer, made 27 Nov 2026)

First video of the daily current-affairs slot (user, 27 Nov: "one video a day on current affairs ... make a video about the Riemann Hypothesis: what it is, that it got proven, the implications, how the proof was made, the lines of Lean code, how absurd and how cool that is, voiced over. Post that today."). 36.3 s, voice A+, PIL/numpy frames via `kit.Writer`, no pixel look.

## Beats (times from `timing.py`, which both `render.py` and `audio.py` read)
- 0.0 hook "Math's biggest problem just got SOLVED." over the critical strip, real zeta zeros (mpmath, `zeros.json`) drifting along the gold line Re = 1/2. HUD "LINES OF PROOF" counts from frame 0 (the running number).
- 2.9 stamp "WITH AN AI." (raises the stakes).
- 4.5 "1859 / The primes hide a pattern.": number line, primes light up, gap arcs +1 +2 +2 +4.
- 8.6 "Every key zero: on ONE line.": zeros scattered across the strip snap onto the line.
- 11.1 "1859 > 2026 / 167 YEARS / NO PROOF."
- 13.7 "A proof in Lean: code a computer checks." scrolling Lean-style code (illustrative, not the real files) > 17.3 "How long is it?" files multiply, counter races > 18.6 "17 MILLION LINES. IN 175,187 FILES".
- 20.7 "Nobody can read that. Machines checked it.": Lean kernel, nanoda, con-leche, con-ron OK > "CORRECT." (Lean FRO + Mathlib, 21 Nov).
- 24.0 "5 days later:" bar 17,374,215 collapses to 76,000 (readable version 300,000) > "229x SHORTER."
- 27.4 "Primes: as tidy as possible.": li(x) - pi(x) for x from 2,657 to 1,000,000 inside the band sqrt(x) log x / 8 pi (Schoenfeld 1976: holds for all x >= 2657 exactly when RH is true).
- 29.9 "Every 'IF RH...' theorem is now just TRUE.": cards (von Koch 1901, Cramer 1920 prime gaps, Miller 1976 test under GRH) lose their IF.
- 33.1 share card "Send this to someone who hated math." + "Heard about it? YES or NO", then hands back to frame 0.

## Facts and sources (checked 27 Nov 2026)
- Announcement 20 Nov 2026, Levent Alpoege (Anthropic) "working with Claude", RH + GRH for Dirichlet L-functions, Lean archive of 175,187 files, ~17.4 million lines (17,374,215 per riemannhypothesissolved.com; rh-trim counted 17,374,242 incl. one more file). Sources: Lean community blog joint statement (Lean FRO + Mathlib Initiative, 21 Nov: "full confidence"), M. Rubinstein's Waterloo page, nasqret/riemann-rev, Science, Science News, Nature.
- Checkers: Lean's kernel, con-leche, con-ron (Lean FRO statement), nanoda (Rubinstein, nasqret dashboard).
- 25 Nov: Luke Sernau and colleagues at Anthropic with Claude: ~300,000-line readable and ~76,000-line compact rewrites of the same five theorems (Rubinstein; 17,374,215 / 76,000 = 229x).
- Not claimed: no human-readable paper is out yet (Rubinstein's 265-page explainer is a work in progress); the Clay $1M prize needs publication in a qualifying outlet + 2 years (claymath.org rules). Both go in the caption.

## Build
`python3 render.py stills` > `python3 render.py` (~30 s) > `python3 audio.py` > mux at 48 kHz with loudnorm -14 (CLAUDE.md). hookcheck: all PASS (6 words, motion 8.9, peak -1.5 dB, reveal 2.9 s, contrast 37). Whisper on the final mix hears every line.
