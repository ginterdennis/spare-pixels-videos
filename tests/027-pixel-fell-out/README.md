# 027 The pixel that fell out (first Blender story, voiced)

24 s, 1080x1920, 30 fps, loops seamlessly. Made in Blender 5.3 (EEVEE) on the user's M3 MacBook Air, narrated by **voice A+** (Chatterbox-Turbo with voice A's timbre, `kit/voice.py`). Posted as `videos/027-pixel-fell-out-v2.mp4`; v1 (Kokoro voice A) never went out.

A screen built from 431 glowing 3D pixel tiles shows a pixel-art cat. One gold pixel of its eye is missing: it fell out, and it's a tiny gold cube with eyes. He tries three times to get back in. The cat helps, then sneezes him out again, and the video loops to the hook.

| Time | Beat | On screen / voice |
|---|---|---|
| 0-3.0 | **Hook:** push-in on the cat, eyes dart around and look down, 3-2-1 ring; whip down the screen to the desk | "Find the MISSING pixel." / "HE FELL OUT." at 3.0 |
| 3.0-5.3 | he waves (hop), turns to the screen, the camera tilts up to the hole (17x his height) | "Now he wants back in." |
| 5.3 | TRY 1: straight jump, far too short, dizzy | "Try one." / "NOPE." |
| 7.5 | TRY 2: sticky notes, books, mug rim (teeters), big leap, **splat** on the tiles, slides down the glass | "Try two." / "SO CLOSE." |
| 12.27 | TRY 3: he sulks; behind him the cat's paw tiles pop out of the screen, land palm-up, he hops on, the paw lifts him, he winks and hops backwards into the slot | "Try three." / "Wait... the CAT?!" / "HOME." at 16.65 |
| 17.4-19.45 | his eyes fade (he's just a pixel again), the cat smiles, "ah... ah..." | |
| 19.45 | **ACHOO:** a ring wave runs through every tile, he's shot out and falls back where frame 0 finds him | "AGAIN?!" |
| 20.43-24 | CTA over the same push-in that opens the video (the loop seam is mid-move) | "Name him." / "Best name stars in Part 2." / "Follow so you see it." (on screen only) |

## Files
- `art.py` → `art.json`: the 18x24 cat and its expressions (look l/c/r/u/d, blink, happy ^ ^, squeeze > <).
- `anim.py`: **every motion as a pure function of time** (hero poses with toy gravity g = 3 m/s², paw, tile ripples and tilts, cat expression, camera). No bpy, so it runs and gets tested in the cloud. `python3 anim.py` prints the event times.
- `blender/build.py`: builds the scene (desk, tile-wall monitor, hero, props, bokeh, lights, camera) and bakes `anim.py` into per-frame keys. Run in Blender: `BASE = "<folder with anim.py + art.json>"; exec(open(BASE + "/build.py").read())`.
- `render.py`: bloom + vignette, hook, stamps, TRY pills, CTA over the Blender frames.
- `audio.py`: chiptune theme in C (C-Am-F-G, 120 BPM, 4-bar phrase on the absolute bar grid so the loop lands on a bar line), one sound per event, formant-synth cat sneeze, then `narrate()` last.

## Voice
v2 (posted): voice A+, using the exact takes the user approved in the voice samples (cached into `~/.cache/spare-voice`), new takes for "Try two." / "Try three.", and `place()` for the cue times: the picture is fixed, so lines that run long start a little later ("Try one." +0.08 s, "Wait... the cat?!" +0.07 s); "[gasp] Again?!" starts on the sneeze. Whisper hears every line in the final mix.

v1 notes: Lines were written and measured first (`kit/voice.py measure`), then the scenes were retimed around them: TRY 1 moved from 4.8 s to 5.3 s so "Now he wants back in." finishes, and the paw now pops 0.68 s after "Try three." so the voice can say "Wait... the cat?!" as it happens. The voice says the on-screen words (CTA voice skips "Follow so you see it."). Pronunciation checked with `voice.py phonemes`. Voiced, so Buffer `isAiGenerated: true`.

**User verdict (22 Nov):** the look is great, the story is pointless. See GROWTH.md "Blender direction".

## How it was rendered
- EEVEE, 32 samples (64 looked the same on the DOF/motion-blur shots), motion blur 0.5 with `motion_blur_position = START` (no smear across hard cuts), raytracing on, view transform Standard. About 4 s per frame on the Air, ~50 min for 720 frames, as a background `Blender -b pixel_fell_out.blend -a`.
- Tiles share one bevelled-cube mesh; colour comes from the object colour (Object Info → emission 0.8 + base x0.3), so the cat's expressions are constant-interpolated colour keys and the hero turns into the cat's colour while he sits in the slot.

## Gotchas found
- **Never glob the home folder from Blender's Python.** Touching Desktop/Documents/Downloads makes macOS show privacy prompts inside Blender, which block its main thread; the MCP connector then times out and shows "failed" until the prompts are answered.
- `device_commit_files` right after writing to `/mnt/user-data/outputs` can send the previous version. Wait a few seconds and compare `md5sum` on both sides (`device_bash`) before running the build.
- `pip install bpy==5.3.0` (Python 3.13 venv) runs `build.py` in the cloud, and EEVEE even renders there through software GL (~30 s for a 25 % frame): good for API errors and framing checks while the Mac is busy or offline.
- Blender 5 actions have no `Action.fcurves`; `build.py` finds curves through `bpy_extras.anim_utils.action_get_channelbag_for_slot`.
- Python closures bind late: segment functions in `anim.py` that read loop variables reassigned later (`tk`, `tl`, `T`) silently used the later values. Every segment uses its own names now.
- Near-black pupils read as missing tiles, which spoils "find the missing pixel". Only the hole is black; pupils and features are violet tiles.
- A tile ripple that only pushes towards the camera is invisible head-on. Tilting each tile away from the wave centre makes the bevel highlights roll across the wall.
