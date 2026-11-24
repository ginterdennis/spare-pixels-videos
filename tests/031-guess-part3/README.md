# 031 Guess it before the balls do (Part 3)

Sequel to 029 (Part 2), whose Instagram Reel got 1,312 views (39% avg watch) within a day, after 004 (Part 1,
1,286 IG views). Same engine as 029 (`sim.py`, `render.py`, `audio.py` copied), new original vector art in `art.py`.

- 3 rounds, escalating: strawberry (payoff 3.0 s, 3-2-1 ring), sunflower (10.0 s), watermelon close-up
  (17.5 s): red flesh + black seeds fill the box, the rind is a band along the top that stays covered until
  ~5.5 s into the round (seed 126, v0 380, p_spawn 0.4, cap 11, low_start; picked by `seeds.py`). Decoy line
  "Strawberry? Look closer." (callback to round 1).
- CTA "Which one got you? 1, 2 or 3?" + "Part 4 is harder. Follow." (Part 4 promised).
- No voice (guessing game). Music/SFX original (029's score), 48 kHz.
- Build: `python3 audio.py && python3 render.py && python3 -c "import sys; sys.path.insert(0,'/home/claude/kit'); from kit import mux; mux('v031_video.mp4','v031.wav','v031_mux.mp4')"`
  then `ffmpeg -i v031_mux.mp4 -c:v copy -c:a aac -b:a 160k -ar 48000 -movflags +faststart ../../videos/031-guess-part3.mp4`.
- hookcheck: all PASS (hook "Guess it before the balls do.", reveal 3.0).
- Part 4 ideas: zebra close-up vs "barcode?", peacock feather, a pizza vs "sunflower?", an orange slice vs "wheel?".
