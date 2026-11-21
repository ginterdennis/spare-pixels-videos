# Hooks v2 (21 Nov 2026): rules for the first 3 seconds

Read this before making any video. Code: `kit/hook.py` (building blocks), `kit/hookcheck.py` (QA).

## Why this exists
On the three TikToks that reached For You, most viewers were gone before the video started paying off:

| Video | Views | Still watching at 1 s / 2 s / 3 s / 5 s | Avg watch |
|---|---|---|---|
| 001 paper folding | 412 | 67% / 46% / 34% / 25% | 23% |
| 006 afterimage | 756 | 69% / 51% / 37% / 23% | 23% |
| 018 same colour | 96 | 76% / 52% / 42% / 35% | 29% |

Marketing benchmarks (rough, not official TikTok numbers) put a good 3-second hold at 60-70%+. We are at 34-42%.

**What the old openings had in common** (frame-by-frame audit of 001, 006, 015, 016, 017, 018, 019, 020, 021, 012):
1. A still picture for the first 1-2 s (moon, checkerboard, grid, yellow square, coin, chat). Reads as a slide or an ad.
2. A small headline strip (84 px) at the top, with the lower half of the screen empty navy.
3. 9-15 words to read before the point lands (017, 006, 016, 021). Reading costs the first 2-3 s.
4. Statements instead of a task: "A and B are the SAME colour" gives the answer away and gives the viewer nothing to do. The two biggest videos (001 "Fold a sheet of paper", 006 "Stare at the dot") both told the viewer to do something.
5. Labels, jargon and hedges on frame 0: "SCINTILLATING GRID", "ILLUSION 1 OF 3", "(almost certainly)".
6. 001 and 006 started silent (-44 dB / -35 dB in the first quarter-second).

## The rules
| # | Rule | Checked by |
|---|---|---|
| H1 | **A task, not a topic.** Max 6 words, max 2 lines, big (`hook_text`, 132 px, auto-fits). A question or instruction the viewer answers in their head: count, guess, pick, stare, predict. | hookcheck |
| H2 | **Moving on frame 0.** The visual is already mid-action: cards mid-riffle, zoom already pushing in, the chat already scrolling. No still title card. | hookcheck |
| H3 | **Sound on frame 0.** `hook_sfx()` puts a hit at 0.00 s. No fade-in from silence. | hookcheck |
| H4 | **First payoff by 3.0 s**, and if possible a visible clock to it (`countdown()` 3-2-1 ring). A visible deadline is the cheapest open loop. | hookcheck |
| H5 | **The payoff opens the next question.** "ZERO." then "Now catch just ONE." Never let the video feel finished at second 3. A new beat every 2-4 s after that. | you |
| H6 | **Frame 0 is the most striking frame of the video**, not the calmest. It is also the cover in the profile grid (set `thumbnailOffset` to ~300 ms). | hookcheck (contrast) + you |
| H7 | **Nothing to decode in 0-3 s:** no HUD labels, jargon, hedges or setup sentences. Context comes after the payoff. | you |
| H8 | **Caption line 1 = the hook words**, so the sound-off viewer and the caption say the same thing. | you |

## Hook patterns (rotate; don't use the same one twice in a row)
1. **Count / guess with a clock.** "How many BLACK dots?" + 3-2-1 ring, payoff "ZERO." (020 v2)
2. **Doubt question.** Ask something the viewer is sure about, then stamp the opposite. "Has this shuffle EVER happened?" > NEVER. (021 v2)
3. **Cold open + rewind** (stories, series, chats). Open on the climax, then "Here's how it went down." and rewind. "Pluto got KICKED out." (012 v2)
4. **Instruction with stakes** (illusions). "Stare at the dot. Don't blink." The effect must start within 3 s (006 made viewers wait 18 s; only 10% were left).
5. **Wrong answer first.** Show the answer most people give, crossed out at 2 s: "Most people say 183."
6. **The number is the picture.** Frame 0 is the shocking number, already counting up; the question comes with it: "31,688 years. For what?"

## Before scheduling a video
```
python3 kit/hookcheck.py videos/<file>.mp4 --hook "<words on frame 0>" --reveal <seconds>
```
All automated checks must PASS. Then open `<file>.hook.jpg` (frames 0-3 s with TikTok's UI zones shaded) and confirm H5, H7, H8 yourself.

## How we measure it
Per TikTok video with >= 100 For You views: retention at 1, 2, 3 and 5 s (Windsor `video_view_retention_second` / `video_view_retention_percentage`). Log `hold3` in the posts.csv notes and the scoreboard.
- Baseline (old hooks): 34-42% at 3 s.
- Target: >= 55% at 3 s by 30 Nov, then >= 65%.
- First v2 hooks: 020 v2 (Sun 22 Nov), 012 v2 (Tue 24 Nov), 021 v2 (Wed 25 Nov).
- If a pattern beats the others on hold3 over 3+ videos, use it more. If a v2 hook does not beat 42%, look at where the drop happens (1 s = frame 0 is weak; 2-3 s = the task is unclear or the payoff is late).
