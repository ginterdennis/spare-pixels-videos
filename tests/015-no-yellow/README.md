# 015 "Your phone has zero yellow lights" (first Remotion video)

32 s explainer: zoom 450x into a yellow screen (only red + green subpixels on), why the eye still sees yellow
(same cone signal as 580 nm light), quick cards for white / black / brown / magenta, zoom out over a pixel sunset,
"Comment a colour. I'll zoom into it." CTA. Loops: the sun expands back into the opening yellow screen.

Unlike the other tests this one is rendered with **Remotion** (React), not `render.py`.

## Build
```bash
cd tests/015-no-yellow
mkdir -p public && cp ../../kit/fonts/{Inter-Black,Inter-ExtraBold,Inter-Bold,Inter-SemiBold,Silkscreen,Silkscreen-Bold,JBMono-Bold}.ttf public/
npm ci
npx remotion bundle src/index.ts --out-dir build
node stills.mjs 0 9.9 16.7 22.9 30.6        # check the busiest moments first (stills/)
CHS=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
npx remotion render build NoYellow out/video_silent.mp4 --browser-executable=$CHS --concurrency=2 --crf=16 --x264-preset=slow
python3 audio.py                             # score from the kit, synced to src/timing.json -> out/score.wav
# Remotion writes full-range BT.601; convert to standard range like the other videos, then mux at 48 kHz
ffmpeg -i out/video_silent.mp4 -vf "scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p" \
  -c:v libx264 -crf 17 -preset slow -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv out/video_tv.mp4
ffmpeg -i out/video_tv.mp4 -i out/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -shortest -movflags +faststart out/015-no-yellow.mp4
```

## Files
- `src/timing.json`: every scene time, read by both the video and `audio.py`.
- `src/PixelWorld.tsx`: canvas renderer for the 380x463-pixel "screen" (solid image when far, RGB subpixel stripes when close).
- `src/Video.tsx`: the whole film as a pure function of time `t` (headlines, HUD, scenes, loop hand-off).

## Facts (checked 20 Nov 2026)
- Phone screens are built from red, green and blue subpixels only; yellow = red + green on.
- Red + green light stimulates the M and L cones like 580 nm yellow light (metamer).
- Brown is dark orange seen next to something brighter.
- Magenta has no single wavelength (red + blue, nothing in the middle).
