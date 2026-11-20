"""020: scintillating grid. 'Count the black dots' -> there are none (reveal at 2.6 s),
try to catch one (they flee from where you look), then bend the streets and the black dots
vanish (Geier et al. 2008, Perception 37: 651-665: curving the streets stops both the Hermann
spots and the scintillation). Ends on the straight grid again so the loop hands back to frame 0."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

DUR = 20.0
REV = 2.6            # "there are zero"
R2 = 7.4             # catch one
R3 = 11.6            # bend the lines
BEND0, BEND1 = R3 + 0.9, R3 + 2.1
CTA = 16.4
UNBEND0, UNBEND1 = 18.6, 19.7

GX0, GX1, GY0, GY1 = 0, W, 600, 1410          # grid area
P = 96                                         # street pitch
BW = 15                                        # street width
DR = 13.0                                      # dot radius
GREY, WHITE_D = 118.0, 255.0
X0, Y0 = W / 2 + P / 2, 1073.0   # lattice origin (intersection)
YYg, XXg = np.mgrid[GY0:GY1, GX0:GX1].astype(np.float32)
BGc = vgrad()


def grid_img(t, amp=0.0, zoom=1.0, cx=W / 2, cy=(GY0 + GY1) / 2, xs=None, ys=None):
    """Return float32 HxW grey image of the scintillating grid (black bg, grey streets, white dots)."""
    xs = XXg if xs is None else xs; ys = YYg if ys is None else ys
    x = (xs - cx) / zoom + cx; y = (ys - cy) / zoom + cy
    # slow drift helps the scintillation
    x = x + 6 * math.sin(t * 0.7); y = y + 4 * math.cos(t * 0.5)
    pw = BW / 2
    # horizontal streets: y = Y0 + j*P + amp*sin(pi*(x-X0)/P)  (passes through the lattice points)
    oh = amp * np.sin(np.pi * (x - X0) / P)
    slope_h = amp * np.pi / P * np.cos(np.pi * (x - X0) / P)
    dy = np.mod(y - Y0 - oh + P / 2, P) - P / 2
    dh = np.abs(dy) / np.sqrt(1 + slope_h ** 2)
    ov = amp * np.sin(np.pi * (y - Y0) / P)
    slope_v = amp * np.pi / P * np.cos(np.pi * (y - Y0) / P)
    dx = np.mod(x - X0 - ov + P / 2, P) - P / 2
    dv = np.abs(dx) / np.sqrt(1 + slope_v ** 2)
    pxs = 1.0 / zoom
    street = np.clip((pw - np.minimum(dh, dv)) / pxs + 0.5, 0, 1)
    img = street * GREY
    lx = np.mod(x - X0 + P / 2, P) - P / 2; ly = np.mod(y - Y0 + P / 2, P) - P / 2
    dd = np.sqrt(lx * lx + ly * ly)
    dot = np.clip((DR - dd) / pxs + 0.5, 0, 1)
    return img * (1 - dot) + WHITE_D * dot


def compose(g):
    out = BGc.astype(np.float32).copy()
    out[GY0:GY1, GX0:GX1] = g[..., None]
    # soft fade into the navy at the top/bottom edges of the grid
    fade = 40
    for k in range(fade):
        a = (k + 1) / (fade + 1)
        out[GY0 + k] = out[GY0 + k] * a + BGc[GY0 + k] * (1 - a)
        out[GY1 - 1 - k] = out[GY1 - 1 - k] * a + BGc[GY1 - 1 - k] * (1 - a)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")


def head(d, l1, l2, a=1.0, top="SCINTILLATING GRID"):
    label(d, W / 2, 250, top, font("Inter-Bold", 30), MUTED + (int(255 * a),), spacing=6)
    draw_rich(d, W / 2, 352, [(x, c + (int(255 * a),)) for x, c in l1], font("Inter-Black", 84))
    draw_rich(d, W / 2, 450, [(x, c + (int(255 * a),)) for x, c in l2], font("Inter-Black", 84))


def sub(d, parts, a, y=540, size=46):
    draw_rich(d, W / 2, y, [(x, c + (int(255 * a),)) for x, c in parts], font("Inter-Bold", size))


def lens(im, t, u):
    """magnifier over one intersection showing the dot is white."""
    lx, ly = X0 - P, Y0 - P          # one lattice point inside the grid
    r = int(170 * ease_out(u))
    if r < 4:
        return
    mag = 4.2
    ys, xs = np.mgrid[ly - r:ly + r, lx - r:lx + r].astype(np.float32)
    # magnified view of the same grid around (lx, ly)
    g = grid_img(t, 0.0, 1.0, xs=(xs - lx) / mag + lx, ys=(ys - ly) / mag + ly)
    tile = Image.fromarray(np.repeat(np.clip(g, 0, 255).astype(np.uint8)[..., None], 3, 2)).convert("RGBA")
    m = Image.new("L", tile.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    tile.putalpha(m)
    cx, cy = int(lx), int(ly)             # magnifier sits right on the dot
    d = ImageDraw.Draw(im)
    im.alpha_composite(tile, (cx - r, cy - r))
    d.ellipse((cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), outline=GOLD + (255,), width=10)


def frame(i):
    t = i / FPS
    amp = 0.0
    if BEND0 <= t < UNBEND0:
        amp = 13.0 * ease((t - BEND0) / (BEND1 - BEND0))
    elif t >= UNBEND0:
        amp = 13.0 * (1 - ease((t - UNBEND0) / (UNBEND1 - UNBEND0)))
    zoom = 1.0 + 0.05 * math.sin(math.pi * min(1, t / DUR))
    im = compose(grid_img(t, amp, zoom))
    d = ImageDraw.Draw(im)
    if t < REV:
        head(d, [("Count the", WHITE)], [("BLACK dots.", GOLD)])
    elif t < R2:
        head(d, [("There are", WHITE)], [("ZERO.", GOLD)])
        sub(d, [("Every dot is ", WHITE), ("white", GOLD), (".", WHITE)], ease((t - REV - 0.35) / 0.3))
        sub(d, [("Your eyes add the black.", WHITE)], ease((t - REV - 1.6) / 0.3), y=1492, size=50)
        lens(im, t, (t - REV - 0.2) / 0.5 if t < R2 - 0.4 else (R2 - t) / 0.4)
    elif t < R3:
        head(d, [("Try to catch", WHITE)], [("ONE black dot.", GOLD)])
        sub(d, [("Look right at it...", WHITE)], ease((t - R2 - 0.6) / 0.3))
        sub(d, [("It runs away.", PINK)], ease((t - R2 - 2.2) / 0.3), y=1492, size=56)
    elif t < CTA:
        head(d, [("Now bend", WHITE)], [("the lines.", GOLD)])
        if t >= BEND1:
            sub(d, [("The black dots are ", WHITE), ("gone", PINK), (".", WHITE)], ease((t - BEND1 - 0.2) / 0.3))
            sub(d, [("Curves break the illusion.", WHITE)], ease((t - BEND1 - 1.4) / 0.3), y=1492, size=50)
    else:
        a = ease((t - CTA) / 0.4)
        head(d, [("How many did", WHITE)], [("you count?", GOLD)], a)
        sub(d, [("Comment your number", WHITE)], a, y=1492, size=56)
    for tb in (REV, R2, R3, CTA):
        if tb - 0.1 < t < tb + 0.16:
            k = 1 - abs(t - tb) / 0.16
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(70 * max(0, k)))))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 3.4, 5.0, 9.5, 12.6, 14.5, 17.5, 19.9]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
        frame(0).save("f0.png"); frame(int(4.5 * FPS)).save("f45.png"); frame(int(14.5 * FPS)).save("f145.png")
    else:
        w = Writer("v020_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
