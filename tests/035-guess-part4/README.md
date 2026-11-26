# 035 Guess it before the balls do (Part 4)

Sequel to 031 (Part 3), whose Instagram Reel got 1,227 views in a day: the third guessing Reel in a row over 1,000
(004: 1,286, 029: 1,313). Same engine as 029/031 (`sim.py`, `render.py`, `audio.py` copied), new original vector art in `art.py`.

- 3 rounds, escalating: orange slice (payoff 3.0 s, 3-2-1 ring), pizza (10.0 s), peacock feather close-up (17.5 s; its
  blue centre stays covered until late: seed 73, low_start, picked by `seeds.py`). Decoy line "An eye? Look closer."
- CTA "Which one got you? 1, 2 or 3?" + "Part 5 is harder. Follow." (Part 5 promised).
- No voice (guessing game). Music/SFX original (029's score), 48 kHz.
- Build: `python3 audio.py && python3 render.py && python3 -c "import sys; sys.path.insert(0,'/home/claude/kit'); from kit import mux; mux('v035_video.mp4','v035.wav','v035_mux.mp4')"`
  then `ffmpeg -i v035_mux.mp4 -c:v copy -c:a aac -b:a 160k -ar 48000 -movflags +faststart ../../videos/035-guess-part4.mp4`.
- hookcheck: all PASS (hook "Guess it before the balls do.", reveal 3.0).
- Part 5 ideas: zebra close-up vs "barcode?", a kiwi-like cross-section that is actually a fig, a pineapple top vs "palm tree?", a lemon vs "sun?".
