"""027 "The pixel that fell out": text, bloom and grade over the Blender frames (EEVEE, M3 MacBook Air).

Story (all times come from anim.py, the same functions Blender baked):
  Narrated by voice A (Kokoro am_michael 1.1x, audio.py): the voice says the on-screen words.
  0-3 s   HOOK  "Find the MISSING pixel." over a push-in on the tile cat, 3-2-1 ring; the cat's eyes dart
                 around and look down; the camera whips down the screen -> "HE FELL OUT." (3.0 s)
  TRY 1   straight jump, 1/5 of the way          -> "NOPE."
  TRY 2   pad -> books -> mug rim -> leap, splat -> "SO CLOSE."
  TRY 3   the cat's paw pixels come out of the screen and lift him -> "HOME." (click into the eye)
  twist   the cat sneezes, a ripple runs through the tiles, he flies out again -> "AGAIN?!"
  CTA     "Name him." / best name stars in Part 2 / Follow.  The camera ends on frame 0 (loop).

    python3 render.py <frames dir>            writes v027_silent.mp4
    ONLY=0,90,300 python3 render.py <frames>  writes /tmp/ov_XXXX.jpg stills
"""
import sys, os, math
sys.path.insert(0, "/home/claude/kit")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from kit import *
from hook import hook_text, stamp, countdown
import anim

EV = anim.build()
FR = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work027/frames"
OUT = "v027_silent.mp4"
DUR = anim.END
N = anim.N
REV = EV["reveal"]


def fade(t, t0, d=0.25):
    return max(0.0, min(1.0, (t - t0) / d))


def win(t, t0, t1, fi=0.2, fo=0.2):
    """alpha for something shown from t0 to t1 with fades"""
    if t < t0 or t >= t1:
        return 0.0
    return min(1.0, (t - t0) / fi if fi else 1.0, (t1 - t) / fo if fo else 1.0)


def sub(im, parts, y, size=62, a=1.0):
    """caption line on a dark pill"""
    if a <= 0:
        return
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
    if a <= 0:
        return
    f = font("Inter-Black", size)
    wdt = f.getlength(txt)
    lay = Image.new("RGBA", (int(wdt) + 48, int(size * 1.5)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), radius=lay.height // 2, fill=col + (int(240 * a),))
    dd.text((lay.width / 2, lay.height * 0.70), txt, font=f, fill=(8, 9, 20, int(255 * a)), anchor="ms")
    im.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def fit(parts, size, maxw=960):
    """shrink a stamp so it never runs off the frame (stamp() lands at its full size)"""
    f = font("Inter-Black", size)
    w = sum(f.getlength(x) for x, _ in parts) + 60
    return size if w <= maxw else int(size * maxw / w)


def st(im, t, t0, parts, size, **k):
    stamp(im, t, t0, parts, size=fit(parts, size), **k)


def tries(im, t):
    """TRY 1 / 2 / 3 pill with three dots, top centre"""
    for n, (t0, t1) in enumerate(((EV["try1"], EV["try2"]), (EV["try2"], EV["try3"]), (EV["try3"], EV["click"])), 1):
        a = win(t, t0 + 0.05, t1 - 0.05, 0.15, 0.15)
        if a > 0:
            u = fade(t, t0 + 0.05, 0.18)
            pill(im, W / 2, 268 - 12 * (1 - ease_out(u)), f"TRY {n}", (GOLD, CYAN, PINK)[n - 1], a, size=60)


def bloom(arr):
    """soft glow from the bright tiles (done here, not in Blender: exact control, same look every frame)"""
    small = arr[::4, ::4].astype(np.float32) / 255
    lum = small @ np.array([0.299, 0.587, 0.114], np.float32)
    mask = np.clip((lum - 0.84) / 0.16, 0, 1)[..., None]
    hi = small * mask
    g = ndimage.gaussian_filter(hi, sigma=(5, 5, 0)) * 0.30 + ndimage.gaussian_filter(hi, sigma=(14, 14, 0)) * 0.22
    g = np.repeat(np.repeat(g, 4, axis=0), 4, axis=1)[: arr.shape[0], : arr.shape[1]]
    out = arr.astype(np.float32) / 255
    out = 1 - (1 - out) * (1 - g)                       # screen blend
    # vignette
    yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    out *= (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    return np.clip(out * 255, 0, 255).astype(np.uint8)


VIG = None


def frame(i):
    t = i / anim.FPS
    src = np.asarray(Image.open(os.path.join(FR, f"f_{i:04d}.jpg")).convert("RGB"))
    im = Image.fromarray(bloom(src)).convert("RGBA")

    # ---- hook: viewer task on frame 0, clock to the reveal
    if t < REV:
        hook_text(im, t, [[("Find the", WHITE)], [("MISSING pixel.", GOLD)]])
        countdown(im, t, 0.0, REV, W / 2, 1520, r=60)
    st(im, t, REV, [("HE FELL OUT.", GOLD)], 150, y=420, panel=True, hold=0.85)
    sub(im, [("Now he wants ", WHITE), ("back in.", GOLD)], 300, size=70,
        a=win(t, REV + 0.9, EV["try1"] - 0.12, 0.15, 0.12))

    # ---- three tries
    tries(im, t)
    st(im, t, EV["nope"] + 0.05, [("NOPE.", PINK)], 140, y=430, panel=True, hold=EV["try2"] - EV["nope"] - 0.2)
    st(im, t, EV["splat"], [("SO ", WHITE), ("CLOSE.", PINK)], 140, y=430, panel=True,
       hold=EV["try3"] - EV["splat"] - 0.12)
    st(im, t, EV["paw_pop"] + 0.27, [("Wait... ", WHITE), ("the CAT?!", CYAN)], 120, y=430,
       panel=True, flash=False, hold=EV["onpaw_takeoff"] - EV["paw_pop"] - 0.2)
    st(im, t, EV["click"], [("HOME.", GOLD)], 170, y=430, panel=True, hold=EV["squeeze"] - EV["click"] - 0.25)

    # ---- the twist
    st(im, t, EV["achoo"], [("ACHOO!", WHITE)], 150, y=430, panel=True, hold=EV["eject"] + 0.12 - EV["achoo"])
    st(im, t, EV["eject"] + 0.14, [("AGAIN?!", PINK)], 160, y=430, panel=True, flash=False,
       hold=EV["cta"] - EV["eject"] - 0.24)

    # ---- CTA (ends on the frame-0 camera, so the loop restarts cleanly)
    if t >= EV["cta"]:
        # stacked high: the eyes and the hole stay clear as the push-in hands back to frame 0
        hook_text(im, t, [[("Name him.", GOLD)]], y=360, size=140, t0=EV["cta"])
        sub(im, [("Best name stars in ", WHITE), ("Part 2", GOLD)], 478, size=54, a=fade(t, EV["cta"] + 0.85))
        sub(im, [("Follow so you see it.", CYAN)], 556, size=40, a=fade(t, EV["cta"] + 1.6))
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
