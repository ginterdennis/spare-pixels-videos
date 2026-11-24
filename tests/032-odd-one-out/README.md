# 032 Spot the odd one out (explore: timed search puzzle)

First run after the TikTok reach recovery ended (24 Nov) gets a third daily slot; this is its explore video.
A viewer task with a clock in every round, built from glyphs in Inter Black (no pixel look, no voice).

- Round 1: one 9 among 49 sixes (3-2-1 ring, payoff "TOO EASY?" at 3.0 s).
- Round 2: one "rn" among 81 "m"s (ring 7-10 s, "GOT IT?" at 10.0 s).
- Round 3: one Q among 144 Os, low on the left (ring 14.5-17.5 s, "THERE." at 17.5 s).
- Payoff: everything dims, the odd one turns gold inside a glowing ring. Glyphs bob from frame 0, the grid zooms slowly.
- CTA "Which round got you? 1, 2 or 3?" + "Part 2 is harder. Follow." Loop: round 1 and the hook fade back in.
- Build: `python3 audio.py && python3 render.py && python3 -c "import sys; sys.path.insert(0,'/home/claude/kit'); from kit import mux; mux('v032_video.mp4','v032.wav','v032_mux.mp4')"`, then re-encode audio at 48 kHz to `videos/032-odd-one-out.mp4`.
- hookcheck: all PASS (hook "Spot the odd one out.", reveal 3.0).
- Part 2 ideas (if it reaches For You with avg watch >= 25%, or IG >= 1,000 views): a b among ds, 1 l among Il, emoji-free vector icons (one clock at a different time, one key with a different bit), colour-shade odd one out.
