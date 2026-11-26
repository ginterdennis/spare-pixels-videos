# 037 Pause challenge (explore)

Why: on 26 Nov every TikTok since 23 Nov reached For You (100%) but stalled at 260-330 views; only 022 (61% avg watch,
35% full) was pushed further. A pause challenge is short (13.3 s) and makes people rewatch and comment a number.

- A stopwatch runs; each round asks to pause on an exact number. At 30 fps each number is on screen for one frame, and
  most hundredths never appear. The target frame is the only gold frame (pausing on gold = you won).
- Round 1: 1x, target 5.00 (frame 72 = 2.40 s), stamp "1 FRAME." at 2.6 s. Round 2: 2x, 8.00 (frame 181), "GONE."
  + "At 2x, most numbers never show." Round 3: 3x, 7.77 (frame 291), "IMPOSSIBLE?".
- CTA: "Stopped on gold? You won. Screenshot it. Comment your number. Tap to pause. Try again." Loop: the clock spins back to 2.60.
- Checked on the final file: frames 72, 181 and 291 are the only gold frames (4.97 / 5.00 / 5.03 around round 1).
- No voice, original SFX (ticks speed up with the clock), 48 kHz. hookcheck: all PASS (hook "Pause it on exactly 5.00", reveal 2.6).
