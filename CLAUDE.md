# Spare Pixels (TikTok @spare.pixels): how videos are made and posted

## Pipeline
1. `bash setup.sh` once per workspace (installs Python deps, links `/home/claude/kit`, copies REN fonts).
2. Each video has its own folder `tests/<id>-<slug>/` with `render.py` (frames → ffmpeg via `kit.Writer`) and `audio.py` (synth via `kit.Mix`), then `kit.mux(video, wav, out)` (loudnorm -14 LUFS).
   REN episodes live in `series/ren/src/` (`scene2.py` = Part 2 template; skia overlays; read `series/ren/README.md` and `state.json` first, update `state.json` after each episode).
3. Output 1080x1920, 30 fps, H.264. Render stills of the busiest moments and look at them before the full render.
4. Copy the final MP4 to `videos/<id>-<slug>.mp4` (photo posts: JPEGs in `photos/<id>-<slug>/`), commit, push.
5. Post through Metricool (brand/blogId `8233683`, timezone Europe/Berlin) with `createScheduledPost`, media = `https://raw.githubusercontent.com/ginterdennis/spare-pixels-videos/main/<path>`.
   `tiktokData.title` is REQUIRED (the call fails without it). `isAigc: false` (code-drawn, nothing realistic). Photo posts: JPEG, `autoAddMusic: true`.
6. Log every post in `posts.csv` (id, time, file, series, format, topic, hook, length, url, 48h metrics, notes incl. Metricool id).

## Style rules
- Look: dark navy gradient (`kit.BG_TOP/BG_BOT`), Inter Black headlines, accent GOLD #FFD36B / PINK / CYAN, small letter-spaced HUD labels with big numbers.
- The first frame must work on its own (hook text + something visible). Keep key content out of the top ~180 px and bottom ~380 px (TikTok UI).
- English. Original art, jokes and music only. No copyrighted characters, no real brand UIs, no real people.
- Fonts are Latin subsets: no arrows, no emoji inside the video (emoji are fine in captions).
- Facts must be checked with a web search before they go in a video.
- Glow sprites need glow >= 2.6, or they show as a square.

## Posting rules
- At least 60 min between posts; do not post the same format back to back.
- Default: send the user each video for an OK before it is scheduled, unless the user has approved automatic posting for that run.

## Format test (20 Nov 2026)
Formats 004-012 = simulation, calm loop, interactive, data, slideshow, explainer, seasonal, humour, story. See `posts.csv` and the Claude project doc `claude/format-test-2026-11-20.md`.
