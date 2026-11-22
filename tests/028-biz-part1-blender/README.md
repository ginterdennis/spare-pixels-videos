# 028: "Is this a business?" Part 1 in Blender (A/B test vs 022)

Same story, same timeline, same captions, counter, tags, end card and soundtrack as 022
(`series/is-this-a-business`, Remotion). Only the picture differs: a 3D cutaway apartment house
(5 floors + basement laundry room) rendered in Blender 5.3 EEVEE on the M3 Air. Silent like 022.

One deliberate UI difference: the small labels (series pill, "1 HOUR LATER" tags, STAIRS label,
card kicker, JONAS/WASHER) use Inter Black instead of the pixel font Silkscreen, because of the
no-pixel rule (user, 22 Nov). Captions, numbers and layout are identical.

## Files
- `anim028.py`: every motion as a function of time, ported 1:1 from `Part1.tsx` / `Building.tsx` /
  `part1.json` (Jonas's path and stair fraction `u`, zoom, close-up beats, washer state, clock, crowd).
  No bpy; `python3 anim028.py` prints a few checkpoints.
- `blender/build028.py`: builds the house, basement, washer, Jonas + 9 neighbours, camera, lights,
  bakes all 810 frames and writes `proj028.json` (screen positions for the s1 labels).
  Run in Blender with `BASE` = a folder holding `anim028.py`, `part1.json`, `build028.py`, `fonts/`.
- `render.py FRAMES UI PROJ`: Blender frames + JONAS/WASHER labels + the Remotion UI layer
  (`npx remotion render build Part1UI <dir> --sequence --image-format=png`, transparent PNGs) ->
  `videos/028-biz-part1-blender.mp4`, audio stream-copied from 022 (byte-identical soundtrack).

## Render (Mac)
Folder `~/Movies/spare-pixels-blender/028/`. Build: `Blender -b --factory-startup --python _build.py`
(`_build.py` sets `BASE` and execs `build028.py`). Frames: `Blender -b biz1_blender.blend -o frames/f_#### -a`
(~3.4 s/frame, 810 frames ~46 min). Bring the frames back in zips, then run `render.py`.

## Checks done
Cloud bpy builds + EEVEE stills of every beat, a Workbench animatic (every 10th frame),
composites with the UI layer; hookcheck on the final file.
