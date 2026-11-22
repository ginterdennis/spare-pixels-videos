# 026 Impossible objects (first Blender video)

24 s, 1080x1920, 30 fps. Three impossible objects, each one exposed by moving the camera. Loops seamlessly (frame 719 hands back to frame 0).

| Time | Object | Trick | Reveal |
|---|---|---|---|
| 0-7 s | Penrose triangle | An open L-shaped bar (3 beams along x, y, z). The end of the z beam is cut by beam X's silhouette swept along the view direction (1,1,1), so with an **orthographic** camera on that axis it looks closed. | 2.45-3.25 s the camera swings to (1,-0.3,0.35): open bar, "GAP". Snaps shut again at 6.35 s. |
| 7-14.5 s | Ames room | A normal box room (6 x 10.2 x 4.6 m) with every vertex slid along the ray from the peephole C: `p' = C + s(x)(p - C)`, `s = exp(-x/3)`. The image through the peephole is unchanged; the far-left corner is really 2.7x farther, the near-right one 0.37x. Patterns are UV-mapped before the warp, so tiles still look square. | Two identical balls (r = 0.6 m). One rolls right and looks 3.6x bigger. 11.1 s the ceiling flies off and the camera cranes up to a top-down view: a wedge-shaped room, two equal balls. |
| 14.5-21.5 s | Sugihara's ambiguous cylinder | Rim solved for two orthographic views at once: the camera (45 deg down) and its mirror image. Per rim point: `y = (vA - vB) / (2 sin phi)`, `z = (vA + vB) / (2 cos phi)`, with vA on a circle and vB on a square. Circle from the front, square in the mirror. | Turned 180 deg (16.75-18.1 s) the two swap; 19.25 s the camera orbits and shows the V-shaped rim. |
| 21.5-24 s | CTA | "Which one got you? Comment 1, 2 or 3" over the spinning triangle | ends exactly on frame 0's camera state |

## Files
- `blender/impossible_objects.blend`: the whole scene (three sets at x = 0 / 100 / 200, cameras `CamT` / `CamA` / `CamM` switched by timeline markers at 0 / 210 / 435 / 645; each set's lights keyed on only in its own section). All camera moves are baked per frame from Python (quaternions kept sign-continuous for motion blur).
- `render.py`: hook, captions, GAP line, SAME SIZE rings, CTA and cut flashes over the Blender frames. Needs `proj.json` (screen positions of the triangle ends, the balls and the mirror per frame, exported from Blender with `world_to_camera_view`).
- `audio.py`: 120 BPM score; every cut and the loop point land on a beat.

## How it was rendered
- Blender 5.3 on the user's MacBook Air (Apple M3, 10-core GPU, 24 GB), driven through the Blender MCP connector.
- EEVEE, 64 samples, motion blur 0.5, view transform Standard (brand colours stay exact). Planar light probe for the mirror.
- **1.9 s per frame**, about 23 min for 720 frames, launched as a background process (`Blender -b impossible_objects.blend -a`) so the UI stays free. JPEG q95 frames → zipped → staged into the cloud workspace → `render.py` → `kit.mux`.
- Compare: the 20 Nov benchmark on the 2-CPU cloud box (no GPU) measured ~50 s per frame with Cycles, so Blender is practical **only on the Mac**.

## Gotchas found
- Shadows and glossy reflections between the triangle's beams give the depth away. The triangle has shadows off and low gloss.
- `sin(pi)` is a tiny positive number: the rim generator must pick the front/back branch explicitly, or one rim point jumps to the other side and solidify shoots a spike across the frame.
- EEVEE's planar-probe reflection flips normals, so inside/outside colouring by normal breaks in the mirror. Use solidify `material_offset` (inner shell = second material) instead.
- Sun lights are global: keep every set's lights keyed to its own section, or one set lights another.
- With a warped floor, a light from above throws the ball's shadow sideways and the ball looks like it floats. Light the Ames room from the viewer's side.
- `look` previews in 4:3. Check the real 9:16 framing with quick 34 % JPEG renders.
