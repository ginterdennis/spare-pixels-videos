"""020 v2 (hook rebuild, 21 Nov 2026, HOOKS.md). Same illusion as v1, new opening:
- frame 0: big viewer task "How many BLACK dots?" (4 words) over the grid, which is already zooming in
- a 3-2-1 ring promises the answer at 3.0 s; sound hit + ticks
- 3.0 s: "ZERO." slams in, magnifier shows a white dot; then straight into the next challenge
- tighter: 17 s instead of 20 s, a new beat every 2-4 s; the CTA repeats the hook so the loop is seamless.
Grid, lens and bend code come from render.py (v1)."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp, countdown
import render as V1

DUR = 17.0
REV = 3.0             # ZERO
R2 = 5.2              # catch one
RUN = 6.9             # it runs away
R3 = 8.8              # bend the lines
BEND0, BEND1 = R3 + 0.3, R3 + 1.3
GONE = BEND1 + 0.15
CTA = 13.0
UNBEND0, UNBEND1 = 15.2, 16.2

HOOK = [[("How many", WHITE)], [("BLACK dots?", GOLD)]]


def sub(d, parts, a, y, size=54):
    V1.sub(d, parts, a, y=y, size=size)


def frame(i):
    t = i / FPS
    amp = 0.0
    if BEND0 <= t < UNBEND0:
        amp = 13.0 * ease((t - BEND0) / (BEND1 - BEND0))
    elif t >= UNBEND0:
        amp = 13.0 * (1 - ease((t - UNBEND0) / (UNBEND1 - UNBEND0)))
    # push-in from frame 0 (motion before anything else), eases back out for the loop
    zoom = 1.0 + 0.09 * ease(t / REV) if t < REV else 1.09 - 0.09 * ease((t - (DUR - 2.0)) / 2.0)
    im = V1.compose(V1.grid_img(t, amp, zoom))
    d = ImageDraw.Draw(im, "RGBA")
    if t < REV:
        hook_text(im, t, HOOK)
        countdown(im, t, 0.0, REV, W / 2, 1482, r=62)
    elif t < R2:
        stamp(im, t, REV, [("ZERO.", GOLD)], y=430, size=190)
        sub(d, [("Every dot is ", WHITE), ("white", GOLD), (".", WHITE)], ease((t - REV - 0.5) / 0.3), y=1492)
        V1.lens(im, t, (t - REV - 0.1) / 0.4 if t < R2 - 0.35 else (R2 - t) / 0.35)
    elif t < R3:
        hook_text(im, t, [[("Now catch", WHITE)], [("just ONE.", GOLD)]], size=124, t0=R2)
        if t < RUN:
            sub(d, [("Look right at it...", WHITE)], ease((t - R2 - 0.5) / 0.3), y=1492)
        else:
            stamp(im, t, RUN, [("It runs away.", PINK)], y=1492, size=74, flash=False)
    elif t < CTA:
        hook_text(im, t, [[("Now bend", WHITE)], [("the lines.", GOLD)]], size=124, t0=R3)
        if t >= GONE:
            stamp(im, t, GONE, [("The black dots are ", WHITE), ("gone", PINK), (".", WHITE)], y=1492, size=64, flash=False)
    else:
        hook_text(im, t, [[("How many did", WHITE)], [("you count?", GOLD)]], size=124, t0=CTA)
        sub(d, [("Comment your number", WHITE)], ease((t - CTA - 0.4) / 0.3), y=1492, size=58)
    for tb in (R2, R3, CTA):
        if tb - 0.08 < t < tb + 0.12:
            k = 1 - abs(t - tb) / 0.12
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(60 * max(0, k)))))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.0, 2.5, 3.1, 4.0, 6.0, 7.2, 10.5, 13.5]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills_v2.jpg", quality=88)
    else:
        w = Writer("v020v2_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
