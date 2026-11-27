# 039 Which glass fills first? (explore, made 27 Nov 2026)

New format for the account: a water-pipe prediction puzzle. 15.8 s, no voice, skia vectors on the navy look.

- 0.0 s: "Which glass fills FIRST?" over a tap already pouring into glass 1, 3-2-1 ring.
- 2.8 s: "4? Look closer." (the obvious path is 1 > 2 > 4).
- 3.35 s: glass 1 reaches its LOW left pipe, so it stays at that height ("1 stays at this pipe") and never reaches the high right pipe: glass 3 never gets a drop.
- 5.6 s: glass 2 reaches its low pipe to 4: it is capped (BLOCKED).
- 8.7 s: glass 2 reaches its high pipe and overflows into the small glass 5.
- 12.2 s: GLASS 5. (gold) > 12.85 s CTA "Glass 3 never got a drop. Did you get it? Comment your number." > 15.0 s drains back to the frame-0 state (loop).

Physics: the plain overflow rule (a glass that is being fed stays at its lowest open outlet while that outlet can pass the flow; a capped outlet passes nothing). No outside facts.

Build: `python3 render.py stills` (contact sheet), `python3 render.py` (v039_video.mp4), `python3 audio.py` (v039.wav: pad bed, pouring noise whose pitch rises with the level, thunk at the cap, chord at the win), then mux at 48 kHz with loudnorm -14 (command in the 27 Nov run). hookcheck: all PASS (4 words, motion 6.5, peak -2.1 dB, reveal 2.8 s, contrast 41).

Read it on: hold3, average watch % and full-watch rate (built for completion: the answer comes at 12.2 s), comments per 1,000 views (a number 1-5). If avg watch >= 50% or comments >= 10 per 1,000: make Part 2 (a new layout, e.g. a leaking glass or two taps).
