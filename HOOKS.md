# Hooks v2 (21 Nov 2026): rules for the first 3 seconds

Read this before making any video. Code: `kit/hook.py` (building blocks), `kit/hookcheck.py` (QA).

> **27 Nov 2026: read VIEWS.md first.** The 3-second rules below still hold, but H4 and H5 changed: the beat at second 2-3 must raise the stakes, not answer the question. Videos that answered at 3 s (same colour, guess, odd one out) lost two thirds of their viewers by second 10; 022, which kept its question open to the end, kept 74%.

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
| H4 | **First beat by 3.0 s that raises the stakes** (a stamp, a counter jump, a twist: "DELIVERED?", "LOCKED OUT", "BY FRIDAY!"). It must not answer the frame-0 question; the answer comes at the end (VIEWS.md V1-V2). A visible clock still helps. *(Until 27 Nov: "first payoff by 3.0 s".)* | hookcheck (timing) + you (it is not the answer) |
| H5 | **One question for the whole video.** Every beat after second 3 makes the same problem worse or the number bigger; no new, separate rounds. A new beat every 2-3 s. | you |
| H6 | **Frame 0 is the most striking frame of the video**, not the calmest. It is also the cover in the profile grid (set `thumbnailOffset` to ~300 ms). | hookcheck (contrast) + you |
| H7 | **Nothing to decode in 0-3 s:** no HUD labels, jargon, hedges or setup sentences. Context comes after the payoff. | you |
| H8 | **Caption line 1 = the hook words**, so the sound-off viewer and the caption say the same thing. | you |

**Voiced videos (since 22 Nov, voice A via `kit/voice.py`, see GROWTH.md "Voice"):** the narrator starts the hook words at 0.00 s (cue 0.0) over `hook_sfx()`, and the hook must still fit before the first payoff. Time the opening from `python3 kit/voice.py measure "<hook>"`: max 6 words is about 2-2.5 s at 1.1x. H1 and H8 still apply: the screen, the voice and caption line 1 say the same hook.

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
Per TikTok video with >= 100 For You views: retention at 1, 2, 3 and 5 s (Windsor `video_view_retention_second` / `video_view_retention_percentage`). Log `hold3` and `hold10` (and kept 3-to-10 = hold10 / hold3) in the posts.csv notes and the scoreboard. Since 27 Nov hold10 matters more than hold3 (VIEWS.md).
- Baseline (old hooks): 34-42% at 3 s.
- Target: >= 55% at 3 s by 30 Nov, then >= 65%.
- First v2 hooks: 020 v2 (Sun 22 Nov), 012 v2 (Tue 24 Nov), 021 v2 (Wed 25 Nov).
- If a pattern beats the others on hold3 over 3+ videos, use it more. If a v2 hook does not beat 42%, look at where the drop happens (1 s = frame 0 is weak; 2-3 s = the task is unclear or the payoff is late).
