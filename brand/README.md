# Sigmoid Horizon: brand rules for every video (since 28 Nov 2026)

The account is now **Sigmoid Horizon** (formerly spare.pixels), with the tagline "The shape of what's next." The user picked the **Neon Eclipse** logo and asked on 28 Nov 2026 that **all future videos stay in that style**. This file is the binding spec for videos. `kit/brandcheck.py` enforces the basics, and the video can't be scheduled until it passes.

- Full brand book (voice, logo rules, colours, type, motion, safe zones): design system "Sigmoid Horizon", https://claude.ai/artifact/PTiYzXYNhYDdL9zgrxrLk6
- Applied designs (video templates, thumbnails, merch, business): brand kit canvas, https://claude.ai/artifact/Dz6MBS8h84uteSxtT7Eu4Y
- Here: `logo/` and `graphics/` (SVG), `tokens.json` (colours, type, spacing), `reference/` (what frames must look like).

## The look in one paragraph
A dark **void** ground with sparse stars. Near the bottom sits a planet's edge, the **horizon arc**, in the **eclipse gradient** (magenta `#FF2FD0` → ultraviolet `#B05CFF` → horizon-cyan `#22E6FF`, always left to right). A **pink sun ring** (`#FF5ADF`) rises behind it. A thin **cyan trajectory**, a real S-curve, climbs from the planet into the sky and ends in a white point. Every neon line has two soft glow layers and a thin white core. Text is starlight `#F2F7FF` or haze `#A49DC4` on void `#05030B` or night `#0E0A1C`.

## Must, on every new video
1. **Colours only from `tokens.json`.** The gradient appears once per frame, on the horizon arc or one highlighted hook word. Sun-pink is only for the ring and for markers on a curve. Topic colours are only for tags.
2. **Type:** Unbounded (display: hooks and titles, upper case), Inter (captions and body), JetBrains Mono (numbers, counters, labels, sources). The fonts are in `kit/fonts`.
3. **The round icon on every frame:** top right at x 862, y 236, 128 px (`brand.watermark`). In a series row with a running number at the top right (the Business series), the icon starts the row at the top left (x 48, y 196, 76 px).
4. **Frame 0:** a topic tag (MATHS, TECH, BUSINESS, SCIENCE, ENERGY) or the series badge; the hook in Unbounded (max 6 words) with one line in the gradient, already moving; the horizon at the bottom wherever the scene allows (`brand.frame0`). HOOKS.md and VIEWS.md still apply.
5. **Safe zone:** text inside x 90–930 and y 220–1500.
6. **Seamless loop** (VIEWS.md V6): the last frame is frame 0. Background motion (star twinkle, camera drift) is periodic over the length (`brand.ground(cv, t, loop=length)`).
7. **Before scheduling:** `python3 kit/brandcheck.py videos/<file>.mp4` must pass (B1 dark ground, B2 icon in place, B3 no off-brand colour areas, B4 loop), next to `kit/hookcheck.py`.
8. **Topics:** a mix of maths, technology, business, science and energy. AI stays low-key: it can appear inside a story but is never the theme or the default pick. No politics. No asks (no like, follow, share, save or subscribe).

## How, per engine
- **skia-python / PIL videos** (explainers, current-affairs, number facts, puzzles): `kit/brand.py`.
  - Shapes: `ground`, `horizon(rise=…)`, `trajectory(p=…)` (draws itself; use `logistic01` easing), `eclipse_ring`, `icon` and `watermark`.
  - Type: `hook` (one gradient line), `gradient_text`, `text`, `label`, `big_number(base, exp)`, `progress_bar`, `source_chip`, `topic_tag`, `series_badge`.
  - Templates: `frame0`, `data_frame`, `chapter_frame`, `sponsor_frame`. `python3 kit/brand.py demo <dir>` renders the reference frames.
  - Surfaces: `new_frame()`; `to_pil()` / `to_rgb()` to hand frames to `kit.Writer`.
  - `kit.py`'s old colour names (BG_TOP/BG_BOT, GOLD, PINK, CYAN, MUTED) now hold brand values, and `hook.py` draws in Unbounded on a night panel. Old renders can use `OLD_*`.
- **041 / 042 explainer engine** (`tests/041-p-vs-np/`): style C "neon 3D" is the starting point. Use brand colours and fonts (Unbounded / Inter / JetBrains Mono instead of Space Grotesk), add the icon and the topic tag, and put the horizon in the opening and closing frame. **The cockpit HUD look (042) is retired for new videos.**
- **"Is this a business?" (Remotion):** `series/is-this-a-business/src/theme.ts` has `LOOK = 'neon'`. That gives the night version of the same house and cast: lavender line art on dark walls, Jonas in cyan, and the brand UI (night caption cards, icon + series row, mono counter with the gradient, sun-pink tags, night end card). In new scenes use only `C.*`, `BRAND.*` or `nc(paperHex, neonHex)`, never a bare hex. In the neon look `C.white` is a night panel, `C.ink` is the light line and text colour, `C.shade` dims the frame, and `HARD_SHADOW` is a glow. Copy the newest case (`src/Case3P1.tsx`) as the template. References: `reference/business-neon-*.jpg`.
- **Blender:** a void world with emissive materials in brand colours only. The icon, tag and type go on as an overlay with `kit/brand.py`.

## Never
- The old looks: warm paper, the navy gradient with gold `#FFD36B`, the cockpit HUD green, pixel art, the Silkscreen font.
- Emoji or arrows inside the video (the fonts are Latin subsets).
- Thick, flat strokes for the trajectory or the horizon. They are thin lines of light with glow.

## Reference frames (`reference/`)
`hook.jpg` (frame 0), `data.jpg` (data callout), `chapter.jpg` (chapter card), `sponsor.jpg` (sponsor card, always disclosed), and `business-neon-0s/6s/19s.jpg` (the Business series in the neon look). New videos should look like they belong next to these.
