"""018: three 'same colour' illusions, each revealed within ~3 s.
1) Checkerboard + soft shadow: dark tile A in light == light tile B in shadow (exact same RGB).
2) Two pixel hearts behind yellow vs blue stripes (same RGB heart pixels).
3) One flat grey bar on a stepped dark-to-light background."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *

DUR = 21.0
R1, R2, R3, RC = 0.0, 6.4, 12.4, 17.6        # round starts, CTA
REV1, REV2, REV3 = 3.0, R2 + 2.9, R3 + 2.4    # reveal times
BGc = vgrad()
NAVY = np.array([16, 18, 36], np.float32)

# ---------------------------------------------------------------- round 1: board
TS, NB = 112, 7
BX, BY = (W - TS * NB) // 2, 600
LIGHT = np.array([200, 200, 200], np.float32)
DARK = np.array([116, 116, 116], np.float32)
K = 116 / 200                                # shadow multiplier: light tile in full shadow == DARK
A_T, B_T = (6, 5), (3, 5)                    # (col,row): A dark tile in light, B light tile in shadow
BALL = (BX + 5.5 * TS, BY + 2.35 * TS, 104)


def tile_rect(c, r):
    return BX + c * TS, BY + r * TS, BX + (c + 1) * TS, BY + (r + 1) * TS


def build_board():
    img = BGc.astype(np.float32).copy()
    for r in range(NB):
        for c in range(NB):
            x0, y0, x1, y1 = tile_rect(c, r)
            img[y0:y1, x0:x1] = LIGHT if (c + r) % 2 == 0 else DARK
    # soft shadow cast toward the lower left
    m = Image.new("L", (W, H), 0)
    bx, by, br = BALL
    ImageDraw.Draw(m).polygon([(650, 900), (744, 1060), (640, 1700), (-200, 1700), (-200, 1200)], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(26)), np.float32) / 255
    shade = 1 - (1 - K) * m
    board = np.zeros((H, W), bool); board[BY:BY + TS * NB, BX:BX + TS * NB] = True
    img[board] = img[board] * shade[board][:, None]
    # checks: A and B identical everywhere
    ax0, ay0, ax1, ay1 = tile_rect(*A_T); bx0, by0, bx1, by1 = tile_rect(*B_T)
    u8 = np.clip(np.round(img), 0, 255).astype(np.uint8)
    a = u8[ay0:ay1, ax0:ax1]; b = u8[by0:by1, bx0:bx1]
    assert (a == 116).all() and (b == 116).all(), (a.min(), a.max(), b.min(), b.max())
    im = Image.fromarray(u8).convert("RGBA")
    # pixel-art ball (lit from the upper right), drawn on top
    d = ImageDraw.Draw(im)
    P = 13; n = int(2 * br / P) + 1
    L = np.array([0.55, -0.55, 0.63]); L /= np.linalg.norm(L)
    base = np.array([80, 196, 130], float)
    for j in range(n):
        for i in range(n):
            x = (i + 0.5) * P - br; y = (j + 0.5) * P - br
            rr = (x * x + y * y) / br ** 2
            if rr > 1: continue
            nz = math.sqrt(1 - rr); nn = np.array([x / br, y / br, nz])
            lam = max(0.0, float(nn @ L))
            c = base * (0.32 + 0.8 * lam) + (90 if lam > 0.93 else 0)
            c = tuple(int(min(255, v)) for v in c)
            d.rectangle((bx - br + i * P, by - br + j * P, bx - br + (i + 1) * P - 1, by - br + (j + 1) * P - 1), fill=c)
    return im


BOARD = build_board()

# ---------------------------------------------------------------- round 2: hearts
HEART = ["..XX...XX..",
         ".XXXX.XXXX.",
         "XXXXXXXXXXX",
         "XXXXXXXXXXX",
         "XXXXXXXXXXX",
         ".XXXXXXXXX.",
         "..XXXXXXX..",
         "...XXXXX...",
         "....XXX....",
         ".....X....."]
HP = 40
HX = (W // 2 - 260, W // 2 + 260)
HY = 1000
HEART_RGB = np.array([232, 62, 92], np.float32)
YEL = np.array([255, 214, 0], np.float32)
BLU = np.array([30, 96, 255], np.float32)
S_PITCH, S_ON = 28, 14
Z_Y0, Z_Y1 = 640, 1360


def heart_mask():
    m = np.zeros((H, W), bool)
    for cx in HX:
        x0 = cx - len(HEART[0]) * HP // 2; y0 = HY - len(HEART) * HP // 2
        for j, row in enumerate(HEART):
            for i, ch in enumerate(row):
                if ch == "X":
                    m[y0 + j * HP:y0 + (j + 1) * HP, x0 + i * HP:x0 + (i + 1) * HP] = True
    return m


HM = heart_mask()
YY = np.arange(H)[:, None]; XXc = np.arange(W)[None, :]


def hearts_img(stripe_frac):
    """stripe_frac 1 = full stripes, 0 = no stripes."""
    img = BGc.astype(np.float32).copy()
    zone = (YY >= Z_Y0) & (YY < Z_Y1)
    img[np.broadcast_to(zone, (H, W))] = NAVY
    img[HM] = HEART_RGB
    if stripe_frac > 0:
        on = int(round(S_ON * stripe_frac))
        stripe = zone & (((YY - Z_Y0) % S_PITCH) < on)
        left = np.broadcast_to(stripe & (XXc < W // 2), (H, W)); right = np.broadcast_to(stripe & (XXc >= W // 2), (H, W))
        img[left] = YEL; img[right] = BLU
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")


HEARTS_FULL = hearts_img(1.0)
assert np.all(np.asarray(HEARTS_FULL)[..., :3][HM & ~((((YY - Z_Y0) % S_PITCH) < S_ON))] == HEART_RGB.astype(np.uint8))

# ---------------------------------------------------------------- round 3: bar
G_X0, G_X1, G_Y0, G_Y1 = 110, 970, 660, 1340
NBANDS = 16
BAR = np.array([126, 126, 132], np.float32)


def bar_img(bg_frac):
    img = BGc.astype(np.float32).copy()
    bw = (G_X1 - G_X0) / NBANDS
    for k in range(NBANDS):
        v = lerp(10, 245, k / (NBANDS - 1))
        c = np.array([v, v, v + 6], np.float32)
        c = NAVY * (1 - bg_frac) + c * bg_frac
        img[G_Y0:G_Y1, int(G_X0 + k * bw):int(G_X0 + (k + 1) * bw)] = c
    img[930:1070, 170:910] = BAR
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


BAR_FULL = bar_img(1.0)

# ---------------------------------------------------------------- text helpers
def fit(txt, name, size, maxw):
    f = font(name, size)
    while f.getlength(txt) > maxw and size > 20:
        size -= 2; f = font(name, size)
    return f


def head(d, t0, t, round_no, l1, l2, sub=None, sub_t=None):
    fL = font("Inter-Bold", 30)
    label(d, W / 2, 252, f"ILLUSION {round_no} OF 3", fL, MUTED, spacing=6)
    a = ease((t - t0) / 0.25) if t0 > 0 else 1
    draw_rich(d, W / 2, 352, [(x, c + (int(255 * a),)) for x, c in l1], font("Inter-Black", 80))
    draw_rich(d, W / 2, 446, [(x, c + (int(255 * a),)) for x, c in l2], font("Inter-Black", 80))
    if sub and t >= sub_t:
        sa = ease((t - sub_t) / 0.3)
        draw_rich(d, W / 2, 528, [(x, c + (int(255 * sa),)) for x, c in sub], font("Inter-Bold", 46))


def tag(d, cx, cy, txt, a=1.0):
    f = font("Inter-Black", 62)
    d.text((cx, cy), txt, font=f, fill=(255, 255, 255, int(255 * a)), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0, int(200 * a)))


def frame(i):
    t = i / FPS
    if t < R2:
        im = BOARD.copy(); d = ImageDraw.Draw(im)
        (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1) = tile_rect(*A_T), tile_rect(*B_T)
        # reveal 1: a bar of the exact same grey joins A and B
        if t >= REV1:
            u = ease((t - REV1) / 0.6)
            xL, xR = (bx0 + bx1) / 2, (ax0 + ax1) / 2
            d.rectangle((xL, (ay0 + ay1) / 2 - 22, xL + (xR - xL) * u, (ay0 + ay1) / 2 + 22), fill=(116, 116, 116, 255))
        # isolate: everything except A, B and the bar fades to navy
        if t >= REV1 + 1.2:
            u = ease((t - REV1 - 1.2) / 0.5) * 0.92
            ov = Image.new("RGBA", im.size, (16, 18, 36, int(255 * u)))
            keep = Image.new("L", im.size, 0); kd = ImageDraw.Draw(keep)
            kd.rectangle((BX, BY, BX + TS * NB - 1, BY + TS * NB - 1), fill=255)
            for r_ in [(ax0, ay0, ax1 - 1, ay1 - 1), (bx0, by0, bx1 - 1, by1 - 1), (bx1, (ay0 + ay1) / 2 - 22, ax0, (ay0 + ay1) / 2 + 22)]:
                kd.rectangle(r_, fill=0)
            ov.putalpha(Image.fromarray((np.asarray(keep, np.float32) * u).astype(np.uint8)))
            im.alpha_composite(ov); d = ImageDraw.Draw(im)
        ta = 1 - ease((t - REV1) / 0.3)
        if ta > 0:
            tag(d, (ax0 + ax1) / 2, (ay0 + ay1) / 2, "A", ta); tag(d, (bx0 + bx1) / 2, (by0 + by1) / 2, "B", ta)
        head(d, 0, t, 1, [("A and B are the", WHITE)], [("SAME colour.", GOLD)],
             [("Your brain subtracts the shadow.", WHITE)], REV1 + 1.3)
    elif t < R3:
        u = 1 - ease((t - REV2) / 0.9) if t >= REV2 else 1.0
        im = HEARTS_FULL.copy() if u >= 1 else hearts_img(u)
        d = ImageDraw.Draw(im)
        head(d, R2, t, 2, [("These hearts are the", WHITE)], [("SAME colour.", GOLD)],
             [("The stripes repaint them.", WHITE)], REV2 + 1.0)
    elif t < RC + 0.5:
        u = 1 - ease((t - REV3) / 0.8) if t >= REV3 else 1.0
        im = BAR_FULL.copy() if u >= 1 else bar_img(u)
        d = ImageDraw.Draw(im)
        head(d, R3, t, 3, [("This grey bar is", WHITE)], [("ONE colour.", GOLD)],
             [("The background shades it.", WHITE)], REV3 + 0.9)
    else:
        im = bar_img(0.0); d = ImageDraw.Draw(im)
    # round transition flash
    for tb in (R2, R3):
        if tb - 0.12 < t < tb + 0.18:
            a = 1 - abs(t - tb) / 0.18
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(110 * max(0, a)))))
    if t >= RC:
        a = ease((t - RC) / 0.4)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 760, W - 70, 1170), radius=40, fill=(8, 9, 20, int(235 * a)))
        f1 = font("Inter-Black", 72)
        draw_rich(od, W / 2, 890, [("Which one fooled you?", WHITE + (int(255 * a),))], fit("Which one fooled you?", "Inter-Black", 72, 880))
        draw_rich(od, W / 2, 1045, [("1", GOLD + (int(255 * a),)), ("   2   ", PINK + (int(255 * a),)), ("3", CYAN + (int(255 * a),))], font("Inter-Black", 120))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 3.4, 5.5, 7.5, 10.8, 13.0, 15.9, 19.0]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
        frame(0).save("f0.png"); frame(int(7.5 * FPS)).save("f75.png")
    else:
        w = Writer("v018_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
