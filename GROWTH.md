# Growth loop: 10,000 followers (TikTok @spare.pixels + Instagram @spare.pixel, combined)

The user gave full autonomy on 20 Nov 2026: pick the content, make it, post it automatically, within TikTok's and Instagram's terms. Don't ask the user anything unless something only a human can do is blocking the account. In that case, give exact click-by-click steps.

Start (20 Nov 2026, 18:00): TikTok 1 follower, Instagram 0.

## Daily loop (scheduled task, every evening, plans the NEXT day)
1. **Followers.** TikTok: Windsor `tiktok_organic` `total_followers_count` (the account shows as "huh.neat" in Windsor's list but returns username `spare.pixels`), or Metricool `TKEV07`. Instagram: Metricool `IGEV01`. If combined >= 10,000: stop making videos, report, and switch the loop off.
2. **Data.** Per video for the last 14 days: views, average watch (s and % of length), full-watch rate, likes, comments, shares, saves, new followers, For You share. Windsor has retention and traffic sources (TikTok only); Metricool has TikTok `TKPO*` and Instagram Reels `IGRE*` (incl. `IGRE27` retention, `IGRE30` skip rate). Fill `posts.csv` 48 h columns for posts that are 48 h+ old.
3. **Decide** (rules below), **make** the videos, **post** them, **log** them, **report**.

## Cadence (why: new accounts that post 5+ a day risk velocity throttling)
- TikTok: **max 3 posts a day**, at least 150 min apart, between 12:00 and 22:30 Berlin. Never the same format twice in a row.
- Instagram: cross-post every new video 30 min after its TikTok slot. Max 4 Reels a day.
- Ramp up to 4 TikToks a day only when the median of the last 9 TikTok posts is >= 500 views AND at least 6 of those 9 reached For You (For You share >= 50%).
- **Throttle alarm:** if the last 6 TikTok posts (all 24 h+ old) each have < 50 views and 0% For You, post only 1 a day for 3 days, then return to 3. Never delete videos in bulk and never repost an identical file (reposts without meaningful change are not eligible for For You).

## What counts as a winner
A video **has signal** if any of: views >= 1,000; average watch >= 50% of its length; full-watch rate >= 25%; or (views >= 300 and comments + shares >= 10 per 1,000 views). Followers per 1,000 views is the tie-breaker (it's what we actually need).

## Explore / exploit (every day's 3 TikTok slots)
- 2 slots: **exploit**. New variants of the best formats (by signal, then For You share, then average watch %). A variant keeps what worked (hook type, length, CTA) but has a new subject. Never a recolour.
- 1 slot: **explore**. A new format or a bold twist on a format.
- **Follow-up rule:** any video with >= 1,000 views or >= 5 new followers gets a "Part 2" or a close sequel within 48 h.
- **Retire rule:** a format with 3+ posts where none reached For You and average watch < 25% is retired. Write it in the scoreboard with the reason.
- **Research** (web search) every Sunday, and whenever nothing has had signal for 4 days in a row: what is working now in faceless science/illusion/satisfying/number-fact/story short-form. Pick formats we can make to a high standard with code.

## Production rules (on top of CLAUDE.md)
- **Frame 0 = the claim**, big, plus something already moving or visible. **First payoff by second 3.** A new payoff or escalation every 3–5 s after that. Data from 20 Nov: on the only two videos that reached For You, half the viewers were gone by second 2 and two thirds by second 3.
- 15–25 s long unless the format needs more. End so the loop hands back to frame 0.
- One comment prompt that's easy to answer (a number, 1/2/3, YES/NO, your birthday, tag a friend).
- Captions: hook + question + 4–6 hashtags. Instagram: drop TikTok-only tags (#fyp, #learnontiktok).
- Facts checked with a web search. Original art, jokes and music only. No real people, brands or copyrighted characters.
- Look at stills of the busiest moments before the full render and at a contact sheet of the final file. Mux audio at 48 kHz.
- `isAigc: false` / `isAiGenerated: false`: the videos are code-drawn graphics, nothing realistic.

## REN series (pixel-art survival, Day N = Part N)
- REN is just another format now: it gets a slot only while its last 2 episodes are at or above the median views of the last 10 TikTok posts. Otherwise set `"paused": true` and a reason in `series/ren/state.json` and use the slot for a winner. Re-check weekly.
- When making an episode: follow `series/ren/README.md` (bible) and `state.json` (single source of truth; update it after each episode). Hook "DAY N" + the problem as a question in the first 3 s; real, checked survival science, described safely; inventory screen; close "Which item saves Ren next?". 30–45 s. Safe area: nothing important above y=220 or below y=1450, nothing right of x=940 between y=780 and y=1500. Template code: `series/ren/src/` (latest episode under `episodes/`). Usual slot 20:25.

## "Is this a business?" series (illustrated story, Part N daily at 20:25)
- Made 20 Nov at the user's request, modelled on a series the user sent. Bible, cast, facts and build steps: `series/is-this-a-business/README.md` (Remotion; `finish.sh` does the colour-range fix + 48 kHz mux).
- Parts 1-3 (022-024) are scheduled Sun 22, Mon 23, Tue 24 Nov at 20:25 TikTok / 20:55 Instagram. Those evening slots are taken; plan around them.
- Part 3 promises "If YES wins, Jonas builds it" (Part 4). Make Part 4 if Part 3's comments lean YES, or if Part 1 has signal; otherwise close the series with a short note in the learnings log. Track Part 2 views / Part 1 views (series carry-over).

## Format scoreboard (update every run)
| Format | Posts | Reached For You | Best views | Avg watch % | Status |
|---|---|---|---|---|---|
| number fact (doubling, scale) | 001, 016, 017, 021 | 001 (98%) | 397 | 23% (001) | exploit |
| illusion | 006, 018, 019, 020 | 006 (96%) | 277 | 20% (006) | exploit |
| simulation / guessing game | 002, 004 | none yet | 4 | – | watch |
| calm loop | 005 | none yet | 0 | – | watch |
| data | 007 | none yet | 6 | 28% | watch |
| slideshow (photo) | 008 | none yet | 2 | – | watch |
| explainer | 009, 015 | none yet | 6 | – | watch |
| seasonal countdown | 010 | none yet | 1 | – | watch |
| humour | 011 | – | – | – | pending |
| story / group chat | 012 | – | – | – | pending |
| REN series | 003, 013, 014 | none yet | 6 | 12% (003) | watch |
| story series "Is this a business?" | 022, 023, 024 (Sun-Tue 20:25) | – | – | – | scheduled |

## Learnings log (newest first, one line each)
- 2026-11-20: 11 TikToks posted on the account's 2nd day; only 001 and 006 reached For You. Capped TikTok at 3/day and moved 012/017/018 to Sat/Sun. First-3-seconds drop-off is the main weakness.

## Needs the user (only human-only things; keep empty when nothing is needed)
- (none)
