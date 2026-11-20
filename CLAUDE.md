# Spare Pixels (TikTok @spare.pixels): how videos are made and posted

## Pipeline
1. `bash setup.sh` once per workspace (installs Python deps, links `/home/claude/kit`, copies REN fonts).
2. Each video has its own folder `tests/<id>-<slug>/` with `render.py` (frames → ffmpeg via `kit.Writer`) and `audio.py` (synth via `kit.Mix`), then `kit.mux(video, wav, out)` (loudnorm -14 LUFS).
   REN episodes live in `series/ren/src/` (`scene2.py` = Part 2 template; skia overlays; read `series/ren/README.md` and `state.json` first, update `state.json` after each episode).
   Remotion (React) videos: see `tests/015-no-yellow/README.md` (render, convert Remotion's full-range output to standard range, mux at 48 kHz).
3. Output 1080x1920, 30 fps, H.264. Render stills of the busiest moments and look at them before the full render.
4. Copy the final MP4 to `videos/<id>-<slug>.mp4` (photo posts: JPEGs in `photos/<id>-<slug>/`), commit, push.
5. Post through **Buffer** (connector `Buffer_com`; since 21 Nov, because Metricool Free only publishes 20 posts a month). Organization `6b00d1f57c8fd27105398cbf` ("My organization"), TikTok channel `6b00d2e9ece6dfde5f3a8402` (spare.pixels), timezone Europe/Berlin. `create_post` with `schedulingType: automatic`, `mode: customScheduled`, `dueAt` with the Berlin offset (e.g. `2026-11-21T13:10:00+01:00`), `text` = caption, `assets [{"video":{"url":"https://raw.githubusercontent.com/ginterdennis/spare-pixels-videos/main/<path>","metadata":{"thumbnailOffset":<ms>}}}]`, `metadata {"tiktok":{"title":"...","isAiGenerated":false}}` (code-drawn, nothing realistic). Buffer Free: max 10 scheduled posts per channel at a time and 1,000 API requests per channel per 30 days, so schedule 1-3 days ahead and refill daily. Metricool (brand `8233683`) is now for analytics only; do not publish there (its 20 free posts a month are a spare from the 1st).
6. Log every post in `posts.csv` (id, time, file, series, format, topic, hook, length, url, 48h metrics, notes incl. Buffer post id).
7. Cross-post every video to Instagram too (@spare.pixel): a separate Buffer `create_post` on the Instagram channel (`list_channels` for its id) with the same video URL, `metadata {"instagram":{"type":"reel","shouldShareToFeed":true,"isAiGenerated":false}}`, 30 min after the TikTok slot. Drop TikTok-only hashtags (#fyp, #learnontiktok). Note the IG time and Buffer id in `posts.csv` notes.
   Instagram rejects audio above 48 kHz: always mux at `-ar 48000` (kit.mux() leaves 96 kHz). Instagram feed photos must be 4:5 to 1.91:1, so 9:16 photo posts need a 4:5 version.

## Style rules
- Look: dark navy gradient (`kit.BG_TOP/BG_BOT`), Inter Black headlines, accent GOLD #FFD36B / PINK / CYAN, small letter-spaced HUD labels with big numbers.
- The first frame must work on its own (hook text + something visible). Keep key content out of the top ~180 px and bottom ~380 px (TikTok UI).
- English. Original art, jokes and music only. No copyrighted characters, no real brand UIs, no real people.
- Fonts are Latin subsets: no arrows, no emoji inside the video (emoji are fine in captions).
- Facts must be checked with a web search before they go in a video.
- Glow sprites need glow >= 2.6, or they show as a square.

## Posting rules
- Growth goal and the daily loop's rules live in `GROWTH.md` (read it first). TikTok: max 3 posts a day, 150+ min apart (new-account throttle risk); Instagram: max 4 Reels a day.
- At least 60 min between posts; do not post the same format back to back.
- Default: send the user each video for an OK before it is scheduled, unless the user has approved automatic posting for that run.

## Format test (20 Nov 2026)
Formats 004-012 = simulation, calm loop, interactive, data, slideshow, explainer, seasonal, humour, story. See `posts.csv` and the Claude project doc `claude/format-test-2026-11-20.md`.
