# 036 Same colour (Part 3)

Promised at the end of 025 (Part 2), which reached For You on 26 Nov (100% FY, hold3 51%). 19.5 s (shorter than
018/025's 21-21.5 s, to push the completion rate). No pixel look: skia vector art at full resolution. No voice (illusion).

1. **No red apple** (colour constancy, after Kitaoka's "no red strawberries", ECVP 2015; checked on michaelbach.de 26 Nov):
   an original apple still life under an additive cyan layer + contrast; `art.py` clamps and asserts R <= max(G, B) for every
   pixel (`render.py` clamps again after resampling). Hook "This apple has NO red." (payoff "ZERO RED." 2.5 s), then an
   eyedropper swatch shows the apple's grey and the room fades to neutral grey.
2. **Koffka ring** (Kurt Koffka, Principles of Gestalt Psychology, 1935): one grey ring over a dark/light split; the halves
   slide apart at 8.6 s and look like two greys ("SAME GREY.").
3. **White's illusion**: grey bars on the black stripes (A) vs on the white stripes (B), identical grey (asserted); the
   stripes fade away at 14.3 s. The hook only asks "Darker grey: A or B?" (no claim about which looks darker).
- CTA "Which one got you? 1 2 3" + "Part 4 is harder. Follow." Loop: the apple fades back in.
- Build: `python3 audio.py && python3 render.py`, mux, re-encode audio at 48 kHz to `videos/036-same-colour-3.mp4`.
- hookcheck: all PASS (hook "This apple has NO red.", reveal 2.5).
