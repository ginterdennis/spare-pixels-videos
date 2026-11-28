# Views playbook (27 Nov 2026): getting one video past 50,000 views

The user asked on 27 Nov 2026 to optimise every video for views, with a target of 50,000+ views on a video. **Views are now the main goal.** Followers are still counted (the 10k stop condition stays), but every decision about what to make is judged by views first. Read this before making any video. It sits on top of HOOKS.md (first 3 seconds) and GROWTH.md (cadence and series rules).

## Why videos stall at ~300 views
Distribution is not the problem: every TikTok since 23 Nov reached For You (99-100%). Each one gets TikTok's first test batch of roughly 300 people, and only a video that holds that batch gets the next one. 022 is the only one that did (7,127 views).

The difference is **not** the first 3 seconds. It is seconds 3 to 10. TikTok retention (Windsor, 27 Nov 23:00 Berlin):

| Video | Format | Views | At 3 s | At 10 s | Kept from 3 s to 10 s | Avg watch | Full watch |
|---|---|---|---|---|---|---|---|
| 022 | Business case opener (laundry) | **7,127** | 69% | **51%** | **74%** | **61%** | **35%** |
| 033 | Business P5, opens on a conflict (2.5 h old) | 202 | 59% | 42% | 71% | 48% | 12% |
| 030 | Business P4, opens on a problem | 322 | 49% | 30% | 61% | 38% | 21% |
| 028 | 022's story in 3D | 262 | 56% | 33% | 59% | 44% | 28% |
| 029 | guess the picture, 3 rounds | 326 | 54% | 27% | 50% | 33% | 4% |
| 023 | Business P2, opens on the product | 291 | 53% | 26% | 49% | 39% | 18% |
| 036 | same colour P3, 3 rounds | 279 | 59% | 22% | 37% | 40% | 14% |
| 025 | same colour P2, 3 rounds | 313 | 52% | 20% | 38% | 35% | 6% |
| 018 | same colour P1, 3 rounds | 600 | 55% | 19% | 35% | 41% | 12% |
| 032 | odd one out, 3 rounds | 296 | 40% | 16% | 40% | 28% | 10% |
| 024 | Business P3, opens on maths | 271 | 31% | 6% | 19% | 17% | 4% |

**Reading:** the illusions and puzzles hold the first 3 seconds as well as 022 does (52-59%), then lose two thirds of those viewers by second 10. They answer their own question at second 3 ("SAME colour.", "KIWI.", "ZERO."), and an answered question is an exit. 022 asks "How did one load of laundry become 640 stairs?" and answers it at the end; a stairs counter keeps climbing in between. Stories that open on a problem or conflict keep 60-74% of their 3-second viewers until second 10; videos that open on an answer, a product or maths keep 19-50%.

The old hook rule H4 ("first payoff by 3 s") lifted the 3-second hold but built that exit into every video. It is replaced below.

## Leading indicators (read in the first 2-6 h, from the ~300-person test batch)
| Signal | Target | 022 | Typical now |
|---|---|---|---|
| Kept from 3 s to 10 s (`hold10 / hold3`) | >= 70% | 74% | 35-50% |
| Still watching at 10 s (`hold10`) | >= 50% | 51% | 16-33% |
| Average watch | >= 55% of length | 61% | 28-44% |
| Full watch | >= 35% | 35% | 4-28% |
| Shares per 1,000 views | >= 3 | 0.4 | 0-5 |

022 shows watch time alone carries a video to ~7,000. Shares are what it lacked for the next waves (3 shares and 0 comments on 7,127 views). On Instagram, sends per reach is one of the three signals Instagram's head names as most important for reaching non-followers, next to watch time and likes per reach.

## The rules (V1-V8)
| # | Rule |
|---|---|
| V1 | **One question, answered at the end.** Frame 0 opens a question the viewer wants answered ("How one parcel visited 7 flats."). The answer comes in the last 3-4 seconds. No beat before that may feel like the answer. |
| V2 | **The beat at second 2-3 raises the stakes; it does not answer.** A stamp like "DELIVERED?", "LOCKED OUT", "BY FRIDAY!" or a counter jumping. hookcheck's `--reveal` still has to be <= 3.0 s; that beat is now an escalation, not a payoff. |
| V3 | **A running number from frame 0 to the end** (stairs, €, flats, minutes, kg). The viewer stays to see the final number. Every 2-3 s it moves or something new happens, and each beat makes the problem worse. |
| V4 | **Problem first, idea last.** Business cases open on the problem a stranger gets in 3 s, never on the product, the price or the maths (024 opened on maths: 19% kept from 3 to 10 s). |
| V5 | **18-24 s.** 022 held at 27 s, but each second cut raises the full-watch rate. End on a frame that hands back to frame 0 so replays happen. |
| V6 | **No asks (user, 27 Nov evening, hard rule).** Never ask viewers to like, share, follow, save or send a video: not on screen, not in the voiceover, not in the caption. The user: "That's basically begging. We don't do that." Instead every video loops seamlessly back to frame 0 for rewatches (see "The 041 playbook", point 8). A comment question is still allowed. |
| V7 | **Plain, short English on screen.** Max 6 words per line, everyday words, numbers as digits. On 7 of the 16 For You videos with country data, 58-84% of viewers were in Germany or Austria, so many first viewers read English as a second language. |
| V8 | **Mix: 2 open-question stories a day on TikTok.** Business case openers at 12:55 and 20:25 (never back to back: the 16:25 slot sits between them). **16:25 = the daily current-affairs explainer since 28 Nov (user, 27 Nov; GROWTH.md "Daily current-affairs explainer")**; it is the day's explore slot. Explore videos follow V1 too: one question per video, the answer at the end. |

## The 041 playbook (user, 27 Nov: "Wow, it's so good." Keep doing this.)
What 041 "P vs NP" (v2, `tests/041-p-vs-np/`, `videos/041-p-vs-np.mp4`) did differently from the earlier videos. Use it for every explainer and current-affairs video, and take from it for every voiced video.
1. **Script first.** Write the whole narration, check every fact with web search, and lock it before building anything. **Full sentences only** (the user: never bullet-point fragments like "300 switches. Check one setting: instant."). The voice explains; the screen shows short labels.
2. **One everyday example, laid out step by step.** Not an abstract claim but something everyone knows (a sudoku): show it, say the rule out loud, show the contrast (checking = instant; solving = trying number after number), show why it explodes (the grid grows 9x9 > 16x16 > 25x25), then give a comparison the viewer can feel (a "ways to fill it" bar shooting past an "atoms in the universe" bar).
3. **Every visual lands on its word.** Whisper word timestamps (`words.py` > `words.json`) drive the timeline through `timing.wt(line, word)`: the row lights up on "row", the column on "column", the locks shatter on "opens".
4. **Tight narration.** Pauses inside a line are cut to 0.24 s and the take is sped up 10% with ffmpeg `atempo` (pitch unchanged), then re-checked with Whisper (`vo.py`). A+ reads slowly otherwise.
5. **A stakes ladder, not a list.** Hook claim > where it came from > the example > what it means for you (your bank, your wallet) > what breaks > what we would gain > the twist (the world ends, a new one begins) > the honest answer (88% of experts bet against it, $1M unclaimed).
6. **Banger hook, then rewind.** Frame 0: the claim in max 6 words plus the giant subject, already moving. At 2.4 s the stakes beat (a crack, padlocks snap open), then a rewind to the origin story.
7. **A real visual world, not slides.** **Since 28 Nov 2026 the world is the brand's Neon Eclipse (`brand/README.md`, `kit/brand.py`): brand colours and fonts, the round icon top right, a topic tag on frame 0, the horizon in the opening and closing frames. The cockpit HUD look (042) is retired for new videos.** The user picked "neon 3D" from three looks (A night grid, B notebook, C neon): black starfield, glowing cyan and magenta lines with bloom, planes tilted in 3D perspective (skia `Matrix.setPolyToPoly`), extruded headline text, a slow camera drift. Engine: skia-python; choreography in `common.py`, the look in `styles.py` (all three looks still render). About 0.5 s per frame on the 2-CPU box: render in two halves in parallel (`render.py C part 0 2` and `part 1 2`), then concat.
8. **A seamless loop instead of any ask.** The last line runs into the first ("...not even AI. Just remember:" > "Proving this would destroy the modern world as we know it."). The last frame is frame 0 (measured seam: one normal frame step). The music's bars tile the whole length (a 4-chord cycle that ends on the chord before the first one), a riser lands on the frame-0 hit, and all background motion (stars, floor grid, camera drift) is periodic over the length.
9. **Length follows the explanation.** 041 runs 44 s, longer than V5's 18-24 s, because every line teaches something. Judge it on hold10, average watch and rewatches before changing the length rule.
10. **Honest caption, no ask.** Hook words, then the context and caveats that did not fit in the video (who, when, what is confirmed, what is not), then hashtags.

## What happens to each format
- **"Is this a business?" case openers (exploit #1):** two a day on TikTok and Instagram. A new everyday case each time (`series/is-this-a-business/CASES.md`). A case that passes 1,000 views gets a Part 2 within 48 h, and Part 2 opens on a new problem or conflict, never on the fix.
- **Same colour, guess the picture, odd one out, black dots (3 rounds, answer at 3 s):** no new 3-round versions. Remake as **one round with the answer at the end**: e.g. a countdown while the balls uncover one picture, decoy guesses on screen ("A waffle?"), the answer in the last 3 s. Instagram keeps getting the 3-round guessing game while it passes 1,000 views there (3 of 3 so far).
- **Pause challenge (037), which glass (039):** already built with the answer at the end; read them on hold10 and full watch.
- **Number facts, REN, group chat:** no new ones unless rebuilt around V1 and V3.

## Captions
- Line 1: the hook words (H8).
- Line 2: context and caveats in plain words (who, when, what is confirmed). No ask (V6).
- Line 3 (optional): one comment question.
- 4-5 hashtags including one plain search phrase people type, e.g. `#businessidea`, `#sidehustle`, `#lockedout`, `#parcel`.

## Measuring
- Every run logs per TikTok video: `hold3`, `hold10`, kept 3-to-10 (%), average watch %, full watch %, shares per 1,000 views, and the top viewer country. Windsor: `video_view_retention_second` / `video_view_retention_percentage`, `video_shares`, `video_audience_countries_*`.
- After 3 videos built on V1-V8: compare their kept 3-to-10 and average watch with the table above and write the result in the GROWTH.md learnings log.
- 50,000 views on any video (TikTok or Instagram) = goal met; say so in the report and make a Part 2 within 24 h.

## Looked at and not changed (27 Nov)
- **Voice A+ stays** (user decision). Voiced posts carry TikTok's AI label, and TikTok now lets viewers dial AI content down in Manage Topics. So far voice shows no watch-time penalty (033, voiced, kept 71% from 3 to 10 s; 030 61%). Bring it to the user only if voiced videos fall clearly behind silent ones on V-built cases.
- **Posting times stay** (12:55 / 16:25 / 20:25 Berlin). The test batches are European (DE, AT, GB, NL, Nordics), so these are midday, afternoon and evening for them.
- **Country mix:** test batches swing between mostly German/Austrian and mostly British/Nordic. Average watch is not clearly better either way, so no language switch; V7 covers it.
