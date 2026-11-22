# 029 Guess it before the balls do (Part 2)

Sequel to 004 (pixel reveal fox), whose Instagram Reel got 1,284 views (37% avg watch) and was the
2nd-best Reel on the account. Remade with **no pixel look** (user rule 22 Nov): smooth vector art
drawn with skia (`art.py`) under a dark scratch-off cover; bouncing balls (`sim.py`) uncover round,
soft-edged trails.

- 3 rounds, escalating: kiwi (payoff 3.0 s, frame 0 already ~33% uncovered, 3-2-1 ring),
  donut (10.0 s), pineapple (17.5 s; balls start low so the crown stays hidden: "A waffle? Look closer.").
- CTA 18.4-20.5: "Which one got you? 1, 2 or 3?" + "Part 3 is harder. Follow." (Part 3 promised).
- Loop: 20.5-21.5 replays the kiwi's lead-in (sim time 1.7-2.7 s) and fades the hook back in, so the
  last frame flows into frame 0.
- No voice (guessing game: people look). Music/SFX original (`audio.py`), 48 kHz, -14.6 LUFS.
- Build: `python3 audio.py && python3 render.py && python3 -c "from kit import mux; mux('v029_video.mp4','v029.wav','v029_mux.mp4')"`
  then re-encode audio at 48 kHz (`-c:v copy -c:a aac -b:a 160k -ar 48000`) to `videos/029-guess-before-balls.mp4`.
- Seeds: kiwi 1, donut 6, pineapple 97 (`low_start=True`; chosen by `seeds.py`: crown 1% uncovered at 5 s, 72% total by the sweep).
- hookcheck: all PASS (hook "Guess it before the balls do.", reveal 3.0).
- Part 3 ideas: a watermelon round slice vs "ladybug?", a sunflower ("pizza?"), a peacock feather,
  a zebra close-up ("barcode?"); keep the "A ___? Look closer." beat on the hardest round.
