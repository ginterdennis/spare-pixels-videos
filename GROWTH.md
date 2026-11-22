# Growth loop: 10,000 followers (TikTok @spare.pixels + Instagram @spare.pixel, combined)

> **Publishing moved to Buffer on 21 Nov 2026 (user decision: stay free).** Wherever the scheduled task's prompt says to post or count posts with Metricool (`createScheduledPost`, `getScheduledPosts`), use Buffer instead (`create_post`, `list_posts`; details in CLAUDE.md step 5 and "Publishing" below). Metricool is analytics only. If the Buffer tools are not loaded in a run, do not post via Metricool: report it and ask the user to add the Buffer connector to the scheduled task.

The user gave full autonomy on 20 Nov 2026: pick the content, make it, post it automatically, within TikTok's and Instagram's terms. Don't ask the user anything unless something only a human can do is blocking the account. In that case, give exact click-by-click steps.

Start (20 Nov 2026, 18:00): TikTok 1 follower, Instagram 0.

## Daily loop (scheduled task, every evening, plans the NEXT day)
1. **Followers.** TikTok: Windsor `tiktok_organic` `total_followers_count` (the account shows as "huh.neat" in Windsor's list but returns username `spare.pixels`), or Metricool `TKEV07`. Instagram: Metricool `IGEV01`. If combined >= 10,000: stop making videos, report, and switch the loop off.
2. **Data.** Per video for the last 14 days: views, retention at 1/2/3/5 s (`hold3` = at 3 s, see HOOKS.md), average watch (s and % of length), full-watch rate, likes, comments, shares, saves, new followers, For You share. Windsor has retention and traffic sources (TikTok only); Metricool has TikTok `TKPO*` and Instagram Reels `IGRE*` (incl. `IGRE27` retention, `IGRE30` skip rate). Fill `posts.csv` 48 h columns for posts that are 48 h+ old.
3. **Decide** (rules below), **make** the videos, **post** them, **log** them, **report**.

## TikTok reach recovery (ACTIVE since 21 Nov 2026; overrides the normal cadence below)
- **Why:** only 3 of 16 TikToks reached For You by 21 Nov (001, 006, 018); the rest got 0-7 views, mostly from the profile page. The account followed nobody, had no bio, had never liked or commented, had only ever uploaded through the API, and posted 11 videos on 20 Nov, so TikTok most likely treated it as a probable bot. Instagram reached people fine, so the content is not the blocker.
- **The user** did a one-time fix on 21 Nov (bio, phone/email verified, account status and For You eligibility checked, followed niche creators) and does a 10-minute in-app routine every evening 22-28 Nov (reminder 19:30: scroll niche For You, like, comment, follow 2-3 niche creators, reply to all comments). The user does NOT post or approve anything by hand: every Buffer post is `schedulingType: "automatic"`, never a reminder.
- **TikTok slots while recovery is active: exactly 2 a day, both automatic.**
  - **16:25 Berlin:** the strongest standalone video (illusions and number facts reach For You best). Alternates day by day between an exploit variant and an explore format; a follow-up (sequel) to a hit may take it.
  - **20:25 Berlin:** series parts, REN, or the best exploit video.
  - Never a third TikTok post on a day. Instagram cadence unchanged (below).
- **Never** delete TikTok videos, set them to private, or re-upload one. Leave flops up.
- **Exit:** when 5 TikTok posts in a row each reach For You (For You share >= 50% AND >= 200 views within 48 h), recovery ends: back to max 3 TikToks a day (third slot between 12:00 and 13:30), and tell the user in the report.
- **First run after 28 Nov:** if recovery is still active, ask under "Needs you:" whether the user can keep the 10-minute routine going for another week.
- Streak so far (newest last): 018 yes (566 views in 5 h, 98.5% FY) | 013 REN P2 pending (94% FY, 29 views at 1 h).

## Cadence after recovery (why: new accounts that post 5+ a day risk velocity throttling)
- TikTok: **max 3 posts a day**, at least 150 min apart, between 12:00 and 22:30 Berlin. Never the same format twice in a row.
- Instagram: cross-post every new video 30 min after its TikTok slot. Max 4 Reels a day.
- Ramp up to 4 TikToks a day only when the median of the last 9 TikTok posts is >= 500 views AND at least 6 of those 9 reached For You (For You share >= 50%).
- **Throttle alarm:** if the last 6 TikTok posts (all 24 h+ old) each have < 50 views and 0% For You, post only 1 a day for 3 days, then return to the normal cadence. Never delete videos and never repost an identical file (reposts without meaningful change are not eligible for For You).

## What counts as a winner
A video **has signal** if any of: views >= 1,000; average watch >= 50% of its length; full-watch rate >= 25%; or (views >= 300 and comments + shares >= 10 per 1,000 views). Followers per 1,000 views is the tie-breaker (it's what we actually need). The two watch-based tests count only with >= 20 views (010 and 005 showed 64-73% average watch on 0-3 views: noise).

## Explore / exploit (during recovery: the 16:25 slot alternates exploit/explore, 20:25 = series or best exploit; after recovery: 2 exploit + 1 explore TikTok slots a day)
- **Exploit**: New variants of the best formats (by signal, then For You share, then average watch %). A variant keeps what worked (hook type, length, CTA) but has a new subject. Never a recolour.
- **Explore**: a new format or a bold twist on a format.
- **Follow-up rule:** any video with >= 1,000 views or >= 5 new followers gets a "Part 2" or a close sequel within 48 h.
- **Retire rule:** a format with 3+ posts where none reached For You and average watch < 25% is retired. Write it in the scoreboard with the reason.
- **Research** (web search) every Sunday, and whenever nothing has had signal for 4 days in a row: what is working now in faceless science/illusion/satisfying/number-fact/story short-form. Pick formats we can make to a high standard with code.

## Production rules (on top of CLAUDE.md)
- **Hooks: follow `HOOKS.md` (v2, 21 Nov).** In short: a viewer task of max 6 words, big (`kit/hook.py` `hook_text`), over something already moving on frame 0, a sound hit at 0.00 s (`hook_sfx`), the first payoff by 3.0 s (ideally with a visible `countdown`), and the payoff opens the next question. No labels/jargon/hedges in 0-3 s. Caption line 1 = the hook words. Run `python3 kit/hookcheck.py <mp4> --hook "..." --reveal <s>` before scheduling; every check must pass. Why: on 001/006/018 (the only For You videos) only 34-42% were still watching at 3 s.
- 15–25 s long unless the format needs more. End so the loop hands back to frame 0.
- One comment prompt that's easy to answer (a number, 1/2/3, YES/NO, your birthday, tag a friend).
- Captions: hook + question + 4–6 hashtags. Instagram: drop TikTok-only tags (#fyp, #learnontiktok).
- Facts checked with a web search. Original art, jokes and music only. No real people, brands or copyrighted characters.
- Look at stills of the busiest moments before the full render and at a contact sheet of the final file. Mux audio at 48 kHz.
- `isAigc: false` / `isAiGenerated: false`: the videos are code-drawn graphics, nothing realistic. **Exception: `isAiGenerated: true` (TikTok and Instagram) on every video with the narrator voice.**

## Voice (since 22 Nov 2026; user decision)
- **Standard narrator = voice A+** (since 22 Nov evening): Chatterbox-Turbo (Resemble AI, MIT licence, official ONNX export, 8-bit language model, runs on the cloud CPU) speaking with voice A's timbre, via `kit/voice.py`. The timbre comes from `kit/voice_a_ref.wav` (10.9 s of synthetic Kokoro `am_michael` speech), so no real person is cloned. The user found Kokoro voice A "very lifeless" and picked A+ from 3 Chatterbox samples (A+, a US female, a UK male). One narrator for the whole account; don't switch voices without asking the user.
- **Voice it:** story series ("Is this a business?" Part 4+, REN Part 4+), number facts, data and explainers. The voice reads the hook at 0.00 s, so the opening has sound on frame 0 and works for people who don't read the text.
- **No voice:** illusions (incl. same colour, impossible objects), calm loops, slideshows. They work because people just look; a voice talks over the moment. Music + SFX as before.
- Anything else: the maker's call. Try voice on a new explore format if it carries information.
- **How:** write the lines first and `python3 kit/voice.py measure "line" ...` (A+ speaks a little slower than A: "Find the missing pixel." = 1.27 s, "Now he wants back in." = 1.31 s, "Name him. Best name stars in part two." = 2.83 s). Time the scenes around the lines. Give `place(wanted_cues, end=duration)` the wanted start times; it moves a line later only when the previous one is still talking, and raises if the last line would run past the end. Call `narrate(mix, cues)` LAST in `audio.py`; it ducks music and SFX 9 dB under each line.
- **Takes are checked automatically:** every line gets a fixed seed per text (reproducible) and Whisper (`faster-whisper` base.en) must hear exactly the line's words, otherwise up to 5 retakes; mismatches print `voice WARNING`. `python3 kit/voice.py check "line" ...` shows what Whisper hears. Cost: ~13-15 s of CPU per 1 s of speech (2 cores), ~3-6 min per video's narration.
- Tags work inside a line and are not spoken: `[gasp]`, `[chuckle]`, `[laugh]`, `[sigh]`, `[groan]`, `[sniff]`, `[clear throat]`. At most one per line, only where a person would really make that sound (027: "[gasp] Again?!" on the sneeze).
- Keep the big on-screen text (many people watch muted). The voice says the same words or a shorter version; never something different. Caption line 1 = hook words (H8) still applies.
- Euro/dollar/pound amounts are converted to words automatically ("€10" > "10 euros"). Spell out acronyms in the voice line ("E S P 32").
- Needs huggingface.co and *.hf.co in the claude.ai allowed domains (the user added them on 22 Nov). If `setup.sh` prints `VOICE MISSING`, make the video without voice, set `isAiGenerated: false`, note "no voice" in `posts.csv`, and mention it in the report.
- **Measure:** note `voice A+` or `no voice` in every `posts.csv` row's notes. After 3+ voiced TikToks with >= 100 For You views, compare their `hold3` and avg watch % with silent videos of the same format, and write the result in the learnings log.

## REN series (pixel-art survival, Day N = Part N)
- REN is just another format now: it gets a slot only while its last 2 episodes are at or above the median views of the last 10 TikTok posts. Otherwise set `"paused": true` and a reason in `series/ren/state.json` and use the slot for a winner. Re-check weekly.
- When making an episode: follow `series/ren/README.md` (bible) and `state.json` (single source of truth; update it after each episode). Hook "DAY N" + the problem as a question in the first 3 s; real, checked survival science, described safely; inventory screen; close "Which item saves Ren next?". 30–45 s. Safe area: nothing important above y=220 or below y=1450, nothing right of x=940 between y=780 and y=1500. Template code: `series/ren/src/` (latest episode under `episodes/`). Usual slot 20:25.

## "Is this a business?" series (illustrated story, Part N daily at 20:25)
- Made 20 Nov at the user's request, modelled on a series the user sent. Bible, cast, facts and build steps: `series/is-this-a-business/README.md` (Remotion; `finish.sh` does the colour-range fix + 48 kHz mux).
- Parts 1-3 (022-024): TikTok **Mon 23 16:25** (moved from Sun 22 20:25 on 22 Nov so 027 could post first, user's wish), **Tue 24, Wed 25** Nov at 20:25 (Part 1's caption says "Part 2 on Tuesday", still true). Part 1 IG Mon 23 16:55. Instagram: Part 1 Sun 22 20:55, Part 2 Tue 24 20:55, Part 3 still to add (Wed 25 20:55).
- Part 3 promises "If YES wins, Jonas builds it" (Part 4). Make Part 4 if Part 3's comments lean YES, or if Part 1 has signal; otherwise close the series with a short note in the learnings log. Track Part 2 views / Part 1 views (series carry-over).

## "Same colour" illusion series (exploit, 16:25)
- 018 (Part 1) is the best video on both networks (TikTok 98.5% For You, hold3 55%; IG 2,717 views, 54% avg watch). 025 = Part 2 (Mon 23 16:25), ends with "Part 3 is harder. Follow." **Part 3 is promised**: make it if 025 reaches For You, for a 16:25 slot 1-2 days later. Ideas not used yet: Koffka ring, White's illusion in grey, confetti illusion, colour cast (a red object under cyan light), Chubb.

## "Impossible objects" 3D series (Blender, 16:25)
- 026 (Part 1, Sun 22 16:25, IG 16:55): Penrose triangle, Ames room, Sugihara's ambiguous cylinder, each exposed by a camera move. First video made in **Blender** (EEVEE) on the user's M3 MacBook Air through the Blender MCP connector; how-to, maths and gotchas in `tests/026-impossible-3d/README.md`, scene in `tests/026-impossible-3d/blender/impossible_objects.blend`.
- Ends with "Part 2 is harder. Follow." **Part 2 is promised**: make it if 026 reaches For You or has signal. Ideas not used yet: Penrose stairs (ball climbs forever), Sugihara's "impossible motion" (balls roll uphill into a peak), Ames window, impossible fork, a second ambiguous cylinder shape (heart/star).
- **Blender only runs on the Mac** (the cloud box measured ~50 s/frame on the 20 Nov benchmark). It needs the Claude desktop app open and online and Blender running with the MCP add-on, so the nightly loop can't make these on its own: build them in a session with the user, or skip if `blender__get_addon_status` fails. Render time on the Air: 1.9 s/frame (simple scenes) to 7.8 s/frame (mirror with planar probe), about 42 min for 24 s. Frames come over in zips of ~100 frames (an 80 MB zip timed out).

## Blender direction (user, 22 Nov 2026): story first
- The user's verdict on 027: the look (lighting, animation, 3D) is "really great", but **the story is pointless** ("the pixel wants to get back" is not a story). Blender videos need a real story: a relatable problem, stakes the viewer feels, a character who wants something and a payoff or twist that is worth the wait.
- Blender videos don't have to be about pixels or in pixel style; the account name doesn't constrain the look. Directions the user named: **a realistic world built in Blender**, a **small/miniature world**, or **our normal formats in Blender, especially "Is this a business?"**, which the user thinks "could look insanely good" in 3D.
- Before building, write the story beat sheet (problem, stakes, three escalating beats, payoff/twist, CTA) and check it against: would someone retell this to a friend? If not, it isn't ready.

## "The pixel that fell out" 3D story (Blender, voiced)
- 027 (Sun 22 20:25, IG 20:55; moved from Fri 27 on 22 Nov because the user wanted it to be the next post, to see how the higher Blender quality does): a screen made of 431 glowing 3D pixel tiles shows a pixel-art cat; one gold pixel of its eye fell out and is a tiny cube with eyes. Hook "Find the MISSING pixel." (3-2-1 ring, payoff "HE FELL OUT." at 3.0 s); three tries to get back in; "HOME."; the cat sneezes him out again and the video loops. Voice A+ (`isAiGenerated: true`), file `videos/027-pixel-fell-out-v2.mp4` (v1 had Kokoro voice A and never posted). Code, timing and gotchas: `tests/027-pixel-fell-out/README.md`.
- Its CTA promises "Best name stars in Part 2". Make Part 2 only if 027 has signal (or 5+ name comments), and then give it a real story (see "Blender direction"); otherwise let it go.
- Read 027's numbers as the test of **Blender visual quality** (hold3, avg watch %, For You share vs the 2D videos), not of the story.
- Same Blender limits as 026 (Mac on, desktop app + Blender open). The scene is fully scripted (`anim.py` is pure Python; `blender/build.py` rebuilds and bakes it). Render time on the Air: ~4.3 s/frame at 32 samples (431 tile objects, DOF, motion blur), ~52 min for 24 s.

## Publishing (Buffer Free since 21 Nov) - check every run
- Metricool **Free = 20 published posts per calendar month** (counted per network). Cap hit 20 Nov 20:25. Metricool is now analytics only; its posts for TikTok were set to drafts on 21 Nov 00:40 so nothing doubles.
- **Buffer Free** publishes now (user decision 20 Nov 22:10: stay free). Connector `Buffer_com`, org `6b00d1f57c8fd27105398cbf`, TikTok channel `6b00d2e9ece6dfde5f3a8402`. Limits: 3 channels, **10 scheduled posts per channel at a time**, 1,000 API requests per channel per 30 days (plus 150 per 15 min, 600 per 24 h). No monthly post cap. TikTok itself allows about 15 API posts a day per account.
- Instagram channel `6b00de3bece6dfde5f3b8d7e` (spare.pixel, business) connected 21 Nov.
- 21 Nov 01:00: whole queue moved to Buffer. TikTok: 10 posts Sat 21 to Tue 24 (full). Instagram: 10 Reels Sat 21 to Mon 23 13:40 (full). Every Metricool copy (TikTok + IG) is a draft now.
- **IG backlog to add when the Buffer queue has room** (same captions as in posts.csv / the TikTok posts): 024 Biz P3 Wed 25 20:55, 005 circles Wed 25 12:25, 009 proofs Thu 26 12:25. Max 4 Reels a day, so new videos' IG cross-posts come first on their day and backlog items fill the rest. (21 Nov 21:50: 014, 023 and 007 added; 012 v2 is not cross-posted because 012 v1 is already on IG.)
- Queue on 22 Nov 14:35: TikTok 9 scheduled (Sun 22 16:25 **026**, 20:25 022 | Mon 23 16:25 025, 20:25 014 | Tue 24 16:25 012 v2, 20:25 023 | Wed 25 16:25 021 v2, 20:25 024 | Thu 26 16:25 **020** (moved from Sun 22 so 026 could post today, user's choice)). Instagram: 026 Sun 22 16:55, 020 moved to Thu 26 16:55. Free TikTok slot: Thu 26 20:25. 22 Nov 19:10 (user: 027 next): TikTok queue re-slotted: **Sun 22 20:25 027** (v2, voice A+; Buffer 6b0327a6846b0ee907a51eb9) + IG 20:55 (6b0327a7d5eabfb8ccc7cf86) | Mon 23 16:25 022 Biz P1 (+ IG 16:55), 20:25 014 REN P3 | Tue 24 16:25 025 same colour P2 (+ IG 16:55), 20:25 023 | Wed 25 16:25 021 v2, 20:25 024 | Thu 26 16:25 020 v2, 20:25 open | Fri 27 16:25 012 v2, 20:25 open.
- Each run: `list_posts` (status scheduled / sent / error) to count the queue, catch errors and fill missing tiktok_url values. If a Buffer post errors, fix and reschedule it; if the TikTok channel shows isDisconnected, ask the user to reconnect it in Buffer (exact steps).
- First Buffer TikTok posts confirmed sent and public on 21 Nov: 017 (13:11), 018 (16:41), 013 (20:26). Buffer's `get_post` returns the TikTok link in `externalLink`.

## Format scoreboard (update every run)
Numbers as of 21 Nov 21:45 (TikTok: Windsor; IG: Metricool, Friday's Reels only). * = not published yet. FY = For You share.
| Format | Posts | Reached For You (TikTok) | Best TikTok views | Avg watch % (TikTok) | Instagram | Status |
|---|---|---|---|---|---|---|
| illusion | 006, 019, 018, 020*, 025* | 006 (98%), 018 (98.5%) | 756 (006); 018 566 in 5 h, hold3 55% | 23% (006), 41% (018), 76% (019, 3 views) | 018: 2,717 views, 54% avg (best); 019: 145 | **exploit #1** (16:25); same-colour series Part 2 = 025 |
| number fact (doubling, scale, odds) | 001, 016, 017, 021* | 001 (98%) | 413 (001) | 23% (001), 40% (016), 31% (017) | 017: 141, 016: 130 | exploit (16:25) |
| REN series | 003, 013, 014* | 013 (94%, 1 h old) | 29 (013) | 11% (003), 26% (013); hold3 38% (013) | 003 IG sent 21 Nov | keep: last 2 eps (6, 29) >= median of last 10 TikToks (4); 20:25 |
| story series "Is this a business?" | 022*, 023*, 024* | – | – | – | – | scheduled Sun 22, Tue 24, Wed 25 at 20:25 |
| story / group chat | 012 v2* (Tue 24 16:25) | – | – | – | 012 v1: 126 views, 62% avg | explore |
| 3D illusion (Blender) | 026* | – | – | – | 026 IG Sun 22 16:55 | explore (Sun 22 16:25); Part 2 promised |
| 3D story (Blender, voiced) | 027* | – | – | – | 027 IG Sun 22 20:55 | explore (Sun 22 20:25, user's pick: test of Blender quality); Part 2 only with signal |
| simulation / guessing game | 002, 004 | none (profile only) | 6 | 5% (002), 36% (004) | 004 IG sent 21 Nov | watch (never reached FY, so no miss yet) |
| calm loop | 005 | none | 0 | – | backlog | watch |
| data | 007 | none | 7 | 30% | Tue 24 12:25 | watch |
| slideshow (photo) | 008 | none (29% search) | 6 | – | not on IG (9:16 photos) | watch |
| explainer | 009, 015 | 009 18% of 3 views | 6 | 19% (009), 15% (015) | 015 Sun 22 | watch |
| seasonal countdown | 010 | 30% of 3 views | 3 | 65% of 3 views (noise) | 166 views, 35% avg | watch |
| humour | 011 | none | 4 | 27% | 110 views | watch |
Nothing has "signal" by the strict definition yet (018: 566 views, 41% avg watch, 11% full watch on TikTok; on IG 54% avg watch). Followers per 1,000 views: 0 everywhere.

## Learnings log (newest first, one line each)
- 2026-11-22 (user feedback on 027): Blender quality is a clear step up ("the lighting, the animation... looks really good"), but a premise is not a story: "the pixel wants to get back" has no stakes or payoff, and the user called it pointless. Story beats come first, the 3D look second; "Is this a business?" in Blender is the user's top idea. Kokoro voice A sounded lifeless; Chatterbox-Turbo with the same timbre (A+) replaced it the same evening.
- 2026-11-22 (027, with the user): first voiced Blender story. Writing and measuring the voice lines first moved two beats (TRY 1 +0.5 s, the paw +0.5 s) and made the video 24 s instead of 23; scenes timed from the voice fit on the first try. `pip install bpy==5.3.0` in the cloud renders EEVEE stills (software GL, ~30 s at 25 %), so the whole storyboard can be checked before the Mac renders. Story hook = a viewer task about the story's premise ("Find the MISSING pixel.") rather than a teaser line.
- 2026-11-22 (voice, with the user): narrator voice added. Kokoro-82M (Apache-2.0) runs on the cloud CPU at ~0.8 s compute per 1 s of speech; the user picked voice A (`am_michael`, 1.1x). Existing videos were timed for silence: Part 1's hook line takes 3.5 s against a 2.95 s scene, so voiced videos must be timed from the voice lines (`voice.py measure`). Already-queued videos stay silent; voice starts with newly made ones.
- 2026-11-22 (026, with the user): Blender is practical on the user's M3 MacBook Air (EEVEE 1.9-7.8 s/frame vs ~50 s/frame with Cycles on the cloud box), so real 3D is now an option when the Mac is online. 3D allows a reveal 2D can't: the camera moves and the illusion breaks (Penrose triangle, Ames room, ambiguous cylinder). Watch whether 026's hold3 and For You share beat the 2D illusions.
- 2026-11-21 (21:45 run): Reach is coming back but nobody follows. 018 "same colour" is the best video on both networks (TikTok 566 views in 5 h, 98.5% For You, hold3 55% = first video at the hooks target; IG 2,717 views, 54% avg watch), and even REN P2 got 94% For You in its first hour, yet the accounts have 1 + 0 followers after ~5,350 views (TikTok ~1,800, IG ~3,500). A short claim + instant reveal holds people; nothing gives them a reason to follow. From now on every exploit video names its series part and ends with a reason to follow (025: "Part 3 is harder. Follow.").
- 2026-11-21 (recovery diagnosis): only 3 of 16 TikToks reached For You (001 paper folding, 006 afterimage, 018 same colour); the rest got 0-7 views, mostly from the profile page. The account followed nobody, had no bio, had never liked or commented, had only ever uploaded through the API, and posted 11 videos on 20 Nov: TikTok most likely treats it as a probable bot. Instagram reaches people fine, so content is not the blocker. Fix: user's one-time account fix + 10-min daily in-app routine (22-28 Nov), 2 automatic TikToks a day (16:25, 20:25), no deletes.
- 2026-11-21 (hooks): 3-second hold on the For You videos was 34% (001), 37% (006), 42% (018); target 55%+. Every old opening was a small headline strip over a still picture, 9-15 words, a statement instead of a task. Hooks v2 (`HOOKS.md`, `kit/hook.py`, `kit/hookcheck.py`); 020, 021 and 012 rebuilt as v2 before they post. Log `hold3` (retention at 3 s) for every video from now on.
- 2026-11-20 (21:40 run): Publishing capacity is the binding constraint: Metricool Free publishes only 20 posts per calendar month (counted per network) and the cap hit on day 2 at 20:25 (13 TikTok + 7 IG). Content-wise, both For You hits (001 "Fold a sheet of paper", 006 "Stare at the dot") open with a direct instruction to the viewer; the other 11 TikToks got 2-7 views, mostly from the profile page (never tested on For You).
- 2026-11-20: 11 TikToks posted on the account's 2nd day; only 001 and 006 reached For You. Capped TikTok at 3/day and moved 012/017/018 to Sat/Sun. First-3-seconds drop-off is the main weakness.

## Needs the user (only human-only things; keep empty when nothing is needed)
- (none) Buffer connector is on the loop since 21 Nov 01:05 (new task trig_019HqjNeore5QCVkAb6LWPx8; the old one without Buffer is switched off).
