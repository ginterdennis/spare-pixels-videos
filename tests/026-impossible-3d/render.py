"""026: three impossible objects, made in Blender (EEVEE, M3 MacBook Air), with the camera revealing each trick.

  1. Penrose triangle (0-7 s): looks closed from one exact angle (orthographic view along (1,1,1)).
     The camera swings off-axis at 2.45-3.25 s and shows an open bar; it snaps shut again at 6.35 s.
  2. Ames room (7-14.5 s): every vertex of a normal box room is slid along the line of sight from the
     peephole (p' = C + s(x)(p - C), s = exp(-x/3)). Two identical balls; one rolls right and looks 3x
     bigger. The lid comes off and the camera cranes up: the room is a wedge, the balls are the same.
  3. Sugihara's ambiguous cylinder (14.5-21.5 s): rim solved for two views at once (camera at 45 deg
     and its mirror image), so it is a circle from the front and a square in the mirror. Turned 180 deg
     the two swap; then the camera orbits and shows the bent rim.
  4. CTA on the triangle (21.5-24 s); the last frame hands back to frame 0 (seamless loop).

The 3D frames come from Blender (see blender/ and README.md). This script lays the hook, captions,
annotations and transitions on top and writes the silent MP4.
"""
import sys, os, json, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp, countdown

FR = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work/frames"
PROJ = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "/home/claude/work/proj.json"))
OUT = "v026_silent.mp4"
DUR = 24.0
N = int(DUR * FPS)

# beats (seconds), shared with audio.py
REV = 3.0          # triangle: swing done -> "IT'S REAL."
BACK = 5.55        # swing back starts
SNAP = 6.35        # triangle closes again
CUT2 = 7.0         # Ames room
ROLL0, ROLL1 = 7.55, 10.45
GREW = 10.45       # "3x BIGGER?!"
LID = 11.1         # lid off, crane up
SAME = 13.0        # rings + SAME SIZE
CUT3 = 14.5        # mirror
TURN0, TURN1 = 16.75, 18.1
ORBIT = 19.25      # camera shows the bent rim
CUT4 = 21.5        # CTA
CUTS = (CUT2, CUT3, CUT4)


def layer(im, fn, *a, **k):
    """draw with alpha on a separate layer, then blend (ImageDraw on RGBA does not blend)"""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(ov), *a, **k)
    im.alpha_composite(ov)


def fade(t, t0, d=0.25):
    return max(0.0, min(1.0, (t - t0) / d))


def hud(d, t, n, a=1.0):
    label(d, W / 2, 222, f"IMPOSSIBLE  {n} / 3", font("Inter-Bold", 30), MUTED + (int(235 * a),), spacing=6)


def sub(im, parts, y, size=62, a=1.0):
    """smaller caption line on a dark pill"""
    f = font("Inter-Black", size)
    wdt = sum(f.getlength(x) for x, _ in parts)
    lay = Image.new("RGBA", (int(wdt) + 64, int(size * 1.45)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), radius=28, fill=(8, 9, 20, int(200 * a)))
    x = 32
    for txt, col in parts:
        dd.text((x, lay.height * 0.74), txt, font=f, fill=col + (int(255 * a),), anchor="ls",
                stroke_width=3, stroke_fill=(6, 7, 16, int(255 * a)))
        x += f.getlength(txt)
    im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y - lay.height / 2)))


def pill(im, cx, cy, txt, col, a=1.0, size=40):
    f = font("Inter-Black", size)
    wdt = f.getlength(txt)
    lay = Image.new("RGBA", (int(wdt) + 44, int(size * 1.5)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), radius=lay.height // 2, fill=col + (int(240 * a),))
    dd.text((lay.width / 2, lay.height * 0.70), txt, font=f, fill=(8, 9, 20, int(255 * a)), anchor="ms")
    im.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def dashed(d, p0, p1, col, a, width=7, dash=26, gap=16, grow=1.0):
    x0, y0 = p0; x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0) * grow
    ux, uy = (x1 - x0) / max(1e-6, math.hypot(x1 - x0, y1 - y0)), (y1 - y0) / max(1e-6, math.hypot(x1 - x0, y1 - y0))
    s = 0.0
    while s < L:
        e = min(L, s + dash)
        d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=col + (int(255 * a),), width=width)
        s += dash + gap
    for (x, y) in (p0, (x0 + ux * L, y0 + uy * L)):
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=col + (int(255 * a),), outline=(8, 9, 20, int(255 * a)), width=3)


def ring(d, c, r, col, a, width=7):
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r), outline=col + (int(255 * a),), width=width)


def frame(i):
    t = i / FPS
    im = Image.open(os.path.join(FR, f"f_{i:04d}.jpg")).convert("RGBA")
    d = ImageDraw.Draw(im)

    if t < CUT2:                                                  # 1. Penrose triangle
        if t < REV:
            hook_text(im, t, [[("Can this", WHITE)], [("EXIST?", GOLD)]])
            countdown(im, t, 0.0, REV, W / 2, 1530, r=60)
        elif t < BACK:
            layer(im, hud, t, 1, fade(t, REV))
            stamp(im, t, REV, [("IT'S REAL.", GOLD)], y=420, size=170)
            if t >= REV + 0.45:
                a = fade(t, REV + 0.45) * (1 - fade(t, BACK - 0.25))
                sub(im, [("Just ", WHITE), ("not closed", PINK), (".", WHITE)], 575, a=a)
                p = PROJ["tri"][str(i)]
                layer(im, dashed, p["xend"], p["ztop"], PINK, a, grow=ease(fade(t, REV + 0.45, 0.45)))
                mx, my = (p["xend"][0] + p["ztop"][0]) / 2, (p["xend"][1] + p["ztop"][1]) / 2
                pill(im, mx, my - 46, "GAP", PINK, a=a)
        else:
            layer(im, hud, t, 1)
            hook_text(im, t, [[("ONE angle", GOLD)], [("closes it.", WHITE)]], size=124, t0=BACK)
            if t >= SNAP:
                k = 1 - fade(t, SNAP, 0.18)
                if k > 0:
                    im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(70 * k))))

    elif t < CUT3:                                                # 2. Ames room
        layer(im, hud, t, 2)
        p = PROJ["ames"][str(i)]
        if t < GREW:
            hook_text(im, t, [[("Two SAME balls.", WHITE)], [("Watch one roll.", GOLD)]], size=104, t0=CUT2,
                      check=False)
        elif t < LID:
            stamp(im, t, GREW, [("3x BIGGER?!", PINK)], y=420, size=150, panel=True)
        elif t < SAME:
            hook_text(im, t, [[("It never", WHITE)], [("grew.", GOLD)]], size=124, t0=LID)
        else:
            hook_text(im, t, [[("The ROOM", GOLD)], [("is the trick.", WHITE)]], size=116, t0=SAME)
            a = fade(t, SAME + 0.1, 0.3)
            for key in ("ball", "twin"):
                x, y, r = p[key]
                layer(im, ring, (x, y), r + 18 + 8 * (1 - ease(a)), GOLD, a)
            (bx, by, br), (tx, ty, tr) = p["ball"], p["twin"]
            pill(im, (bx + tx) / 2 + 150, (by + ty) / 2, "SAME SIZE", GOLD, a=a, size=42)

    elif t < CUT4:                                                # 3. ambiguous cylinder
        # text sits higher here (and no HUD): the square in the mirror starts at y ~560
        if t < TURN0:
            hook_text(im, t, [[("Circle...", WHITE)], [("or SQUARE?", GOLD)]], y=330, size=110, t0=CUT3)
        elif t < TURN1 + 0.05:
            hook_text(im, t, [[("Now turn", WHITE)], [("it around.", GOLD)]], y=330, size=110, t0=TURN0)
        elif t < ORBIT:
            stamp(im, t, TURN1 + 0.05, [("SWAPPED.", GOLD)], y=380, size=160, panel=True)
        else:
            layer(im, hud, t, 3)
            stamp(im, t, ORBIT + 0.3, [("It's ", WHITE), ("NEITHER.", PINK)], y=420, size=150, flash=False, panel=True)
            if t >= ORBIT + 1.2:
                sub(im, [("The rim is ", WHITE), ("bent", PINK), (" to fool you.", WHITE)], 575,
                    a=fade(t, ORBIT + 1.2))

    else:                                                         # 4. CTA, loops to frame 0
        hook_text(im, t, [[("Which one", WHITE)], [("got you?", GOLD)]], size=124, t0=CUT4)
        a = fade(t, CUT4 + 0.35)

        def nums(dd):
            f = font("Inter-Black", 120)
            for k, (n, col) in enumerate((("1", GOLD), ("2", PINK), ("3", CYAN))):
                cx = W / 2 + (k - 1) * 190
                cy = 1545 - 10 * ease(a)
                dd.ellipse((cx - 72, cy - 72, cx + 72, cy + 72), fill=(8, 9, 20, int(215 * a)),
                           outline=col + (int(255 * a),), width=8)
                dd.text((cx, cy + 43), n, font=f, fill=col + (int(255 * a),), anchor="ms")
        layer(im, nums)
        sub(im, [("Comment ", WHITE), ("1, 2 or 3", GOLD)], 595, size=58, a=fade(t, CUT4 + 0.6))
        sub(im, [("Part 2 is harder. ", WHITE), ("Follow.", CYAN)], 690, size=44, a=fade(t, CUT4 + 1.0))

    for c in CUTS:                                                # flash-in on every cut
        if c <= t < c + 0.12:
            k = 1 - (t - c) / 0.12
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(110 * k))))
    return im.convert("RGB")


if __name__ == "__main__":
    only = [int(x) for x in os.environ.get("ONLY", "").split(",") if x]
    if only:
        for i in only:
            frame(i).save(f"/tmp/ov_{i:04d}.jpg", quality=90)
        sys.exit()
    wr = Writer(OUT)
    for i in range(N):
        wr.write(frame(i))
    print(wr.close(), N)
