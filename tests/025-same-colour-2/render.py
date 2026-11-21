"""025: 'Same colour' Part 2. Sequel to 018 (best TikTok + IG video so far: 98% For You, 55% still
watching at 3 s; IG 2,717 views, 54% avg watch). Same recipe: claim on frame 0, reveal by ~2.5 s,
three rounds, CTA 1/2/3, plus a reason to follow (Part 3).
1) Munker / chromatic assimilation: a 'blue' and a 'green' spiral arm are the same teal; orange or
   magenta stripes between them repaint them.
2) Cornsweet edge: left and right halves are the same grey; only a thin ramp at the seam differs.
   A pixel thumb covers the seam.
3) Lit cube (after Lotto & Purves): a brown tile on the lit top and an orange tile on the shaded side
   are the same pixels."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp

DUR = 21.5
R1, R2, R3, RC = 0.0, 6.6, 12.9, 18.3            # round starts, CTA
REV1, REV2, REV3 = 2.5, R2 + 2.7, R3 + 2.5        # first payoff of each round
BACK1 = 4.5                                       # round 1: stripes come back
BGc = vgrad().astype(np.float32)
NAVY = np.array([16, 18, 36], np.float32)
YY = np.arange(H)[:, None]; XX = np.arange(W)[None, :]

# ---------------------------------------------------------------- round 1: spiral
T_ = np.array([0, 236, 160], np.float32)          # the one teal
OR = np.array([255, 160, 0], np.float32)
MG = np.array([186, 0, 255], np.float32)
S = 6                                             # stripe height = pixel size
CX, CY, RAD = 540, 1010, 420
PITCH = 118.0
gy, gx = np.mgrid[0:H // S, 0:W // S]
gcx, gcy = (gx + 0.5) * S - CX, (gy + 0.5) * S - CY
G_R = np.hypot(gcx, gcy); G_TH = np.arctan2(gcy, gcx)
G_IN = G_R <= RAD
G_ODD = (gy % 2 == 1)                             # odd rows: magenta, even rows: orange
BG_SMALL = BGc[::S, ::S][:H // S, :W // S]


def spiral(t, stripes=1.0):
    """stripes 1 = full illusion, 0 = only the teal left on navy."""
    phase = (G_R / PITCH - (G_TH + 0.55 * t) / (2 * math.pi)) % 1.0
    arm_g = G_IN & (phase < 0.27)                 # teal replaces magenta rows -> next to orange -> looks green
    arm_b = G_IN & (phase >= 0.5) & (phase < 0.77)  # teal replaces orange rows -> next to magenta -> looks blue
    img = BG_SMALL.copy()
    stripe_col = np.where(G_ODD[..., None], MG, OR)
    bgin = NAVY * (1 - stripes) + stripe_col * stripes
    img[G_IN] = bgin[G_IN]
    img[arm_g & G_ODD] = T_
    img[arm_b & ~G_ODD] = T_
    # pixel rim around the disc
    rim = (G_R > RAD) & (G_R <= RAD + S * 1.5)
    img[rim] = img[rim] * 0.4 + np.array([60, 64, 96]) * 0.6
    big = np.repeat(np.repeat(img, S, 0), S, 1)
    return Image.fromarray(np.clip(big, 0, 255).astype(np.uint8)).convert("RGBA")


# sanity: both arms contain only the exact teal (checked on a frame)
def _check_spiral():
    a = np.asarray(spiral(1.0))[..., :3].reshape(-1, 3)
    cols = {tuple(c) for c in np.unique(a, axis=0)}
    assert tuple(T_.astype(np.uint8)) in cols


_check_spiral()

# ---------------------------------------------------------------- round 2: Cornsweet
CS_X0, CS_X1, CS_Y0, CS_Y1 = 100, 940, 650, 1330
SEAM = (CS_X0 + CS_X1) // 2
BASE, AMP, TAU = 122.0, 66.0, 34.0


def cornsweet_img():
    img = BGc.copy()
    x = np.arange(CS_X0, CS_X1, dtype=np.float32)
    v = np.where(x < SEAM, BASE + AMP * np.exp(-(SEAM - 1 - x) / TAU), BASE - AMP * np.exp(-(x - SEAM) / TAU))
    col = np.stack([v, v, v + 4], -1)
    img[CS_Y0:CS_Y1, CS_X0:CS_X1] = col[None, :, :]
    u8 = np.clip(np.round(img), 0, 255).astype(np.uint8)
    # check: 200 px from the seam both halves are the same value
    assert u8[900, SEAM - 220, 0] == u8[900, SEAM + 220, 0] == 122, (u8[900, SEAM - 220], u8[900, SEAM + 220])
    assert u8[900, CS_X0 + 5, 0] == u8[900, CS_X1 - 5, 0] == 122
    return Image.fromarray(u8).convert("RGBA")


CORN = cornsweet_img()
SKIN, SKIN_D, SKIN_L, NAIL = (236, 178, 140), (196, 132, 100), (250, 204, 170), (255, 226, 214)


def thumb(im, y_top):
    """Pixel-art thumb (P = 20 px blocks) pointing up, covering the seam from y_top down."""
    d = ImageDraw.Draw(im)
    P = 20; w = 15                                   # 300 px wide
    x0 = SEAM - w * P // 2
    rows = int((H - y_top) / P) + 1
    for j in range(rows):
        y = y_top + j * P
        inset = [4, 2, 1, 1, 0][j] if j < 5 else 0   # rounded tip
        for i in range(inset, w - inset):
            c = SKIN
            if i in (inset, w - 1 - inset): c = SKIN_D
            elif i == inset + 1: c = SKIN_L
            if 2 <= j <= 8 and 4 <= i <= 10: c = NAIL if not (j == 8 or i in (4, 10)) else (232, 190, 170)
            d.rectangle((x0 + i * P, y, x0 + (i + 1) * P - 1, y + P - 1), fill=c)
        if j == 12:
            for i in range(3, 12):
                d.rectangle((x0 + i * P, y + 8, x0 + (i + 1) * P - 1, y + 11), fill=SKIN_D)


# ---------------------------------------------------------------- round 3: lit cube
P3 = 10                                          # pixel size
NCX, NCY, SIDE = 540, 960, 330                   # near (front-top) corner of the cube, edge length
C30, S30 = math.cos(math.pi / 6), math.sin(math.pi / 6)
LV = np.array([-SIDE * C30, -SIDE * S30]); RV = np.array([SIDE * C30, -SIDE * S30]); DV = np.array([0.0, SIDE])
LIGHT_TOP, LIGHT_LEFT, LIGHT_RIGHT = 1.0, 0.78, 0.45
D_TILE = np.array([112, 58, 20], np.float32)     # what both compared tiles show on screen (brown)
ORANGE_TRUE = D_TILE / LIGHT_RIGHT               # = (249, 129, 44): the shaded tile is 'really' orange
PAL = {"c": (240, 226, 196), "p": (242, 104, 158), "m": (96, 214, 172), "l": (156, 136, 232), "s": (104, 178, 240),
       "o": tuple(ORANGE_TRUE), "n": tuple(D_TILE)}
NT = 4                                           # 4 x 4 tiles per face, own palette (not a puzzle-cube look)
TOP = ["cpms", "lnpc", "smlp", "pcsm"]           # [u][v]; 'n' = the brown tile, fully lit
LEFT = ["mslc", "pcms", "lpcm", "sclp"]          # [u][w]
RIGHT = ["scmp", "loms", "cpls", "mscl"]         # [v][w]; 'o' = the orange tile, in shadow
TOP_N, RIGHT_O = (1, 1), (1, 1)


def _solve(p, A, B):
    M = np.array([[A[0], B[0]], [A[1], B[1]]])
    return np.linalg.solve(M, p)


def cube_grid():
    """Rasterise the cube on a P3-pixel grid. Returns colour grid, face-id grid, (u,v) tile ids."""
    gh, gw = H // P3, W // P3
    img = BGc[::P3, ::P3][:gh, :gw].copy()
    face = np.zeros((gh, gw), np.int8); tile = np.full((gh, gw, 2), -1, np.int8)
    ys, xs = np.mgrid[0:gh, 0:gw]
    px = (xs + 0.5) * P3 - NCX; py = (ys + 0.5) * P3 - NCY
    pts = np.stack([px.ravel(), py.ravel()], 0)
    # floor shadow: the base rhombus stretched toward the lower right (light from the upper left)
    Minv0 = np.linalg.inv(np.array([[LV[0], RV[0]], [LV[1], RV[1]]]))
    base = (Minv0 @ (pts - DV[:, None])).T.reshape(gh, gw, 2)
    sh = (base[..., 0] >= -0.8) & (base[..., 0] <= 1) & (base[..., 1] >= 0) & (base[..., 1] <= 1.05)
    img[sh] = img[sh] * 0.35
    for fid, (A, B, rows, lit) in enumerate([(LV, RV, TOP, LIGHT_TOP), (LV, DV, LEFT, LIGHT_LEFT), (RV, DV, RIGHT, LIGHT_RIGHT)], 1):
        Minv = np.linalg.inv(np.array([[A[0], B[0]], [A[1], B[1]]]))
        uv = (Minv @ pts).T.reshape(gh, gw, 2)
        u, v = uv[..., 0], uv[..., 1]
        inside = (u >= 0) & (u < 1) & (v >= 0) & (v < 1) & (face == 0)
        fu, fv = u * NT, v * NT
        iu = np.clip(fu.astype(int), 0, NT - 1); iv = np.clip(fv.astype(int), 0, NT - 1)
        gap = (np.minimum(fu % 1, 1 - fu % 1) < 0.09) | (np.minimum(fv % 1, 1 - fv % 1) < 0.09)
        for a in range(NT):
            for b in range(NT):
                m = inside & (iu == a) & (iv == b) & ~gap
                col = np.array(PAL[rows[a][b]], np.float32) * lit
                img[m] = col
                tile[m] = (a, b)
        img[inside & gap] = np.array([24, 22, 30]) * lit + 6
        face[inside] = fid
    return img, face, tile


CUBE_G, CUBE_F, CUBE_T = cube_grid()
M_TOP = (CUBE_F == 1) & (CUBE_T[..., 0] == TOP_N[0]) & (CUBE_T[..., 1] == TOP_N[1])
M_RIGHT = (CUBE_F == 3) & (CUBE_T[..., 0] == RIGHT_O[0]) & (CUBE_T[..., 1] == RIGHT_O[1])
_cg = np.round(CUBE_G).astype(int)
assert (np.abs(_cg[M_TOP] - D_TILE) <= 0).all() and (np.abs(_cg[M_RIGHT] - D_TILE) <= 0).all(), "tiles differ"
# bridge between the two tile centres (same colour), on the grid
_ty, _tx = np.argwhere(M_TOP).mean(0); _ry, _rx = np.argwhere(M_RIGHT).mean(0)


def cube_img(isolate=0.0, bridge=0.0):
    g = CUBE_G.copy()
    keep = M_TOP | M_RIGHT
    if bridge > 0:
        n = 60
        for k in range(int(n * bridge) + 1):
            f = k / n
            y, x = _ty + (_ry - _ty) * f, _tx + (_rx - _tx) * f
            yi, xi = int(round(y)), int(round(x))
            g[yi - 1:yi + 2, xi - 1:xi + 2] = D_TILE
            keep = keep.copy(); keep[yi - 1:yi + 2, xi - 1:xi + 2] = True
    if isolate > 0:
        bgg = BGc[::P3, ::P3][:g.shape[0], :g.shape[1]]
        g[~keep] = g[~keep] * (1 - isolate) + NAVY * isolate
    big = np.repeat(np.repeat(g, P3, 0), P3, 1)
    out = BGc.copy(); out[:big.shape[0], :big.shape[1]] = big
    return Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8)).convert("RGBA")


CUBE = cube_img()

# ---------------------------------------------------------------- text
def head(d, t, t0, l1, l2, size=96, y1=372):
    a = 1.0 if t0 == 0 else ease((t - t0) / 0.25)
    f = font("Inter-Black", size)
    for k, parts in enumerate((l1, l2)):
        w_ = sum(f.getlength(x) for x, _ in parts)
        while w_ > W - 140:
            size -= 4; f = font("Inter-Black", size); w_ = sum(f.getlength(x) for x, _ in parts)
    for k, parts in enumerate((l1, l2)):
        y = y1 + k * int(size * 1.08)
        w_ = sum(f.getlength(x) for x, _ in parts); x = W / 2 - w_ / 2
        for txt, c in parts:
            d.text((x, y), txt, font=f, fill=c + (int(255 * a),), anchor="ls", stroke_width=4, stroke_fill=(6, 7, 16, int(255 * a)))
            x += f.getlength(txt)


def sub(d, t, t0, txt, y=1440, col=WHITE):
    if t < t0: return
    a = ease((t - t0) / 0.3)
    f = font("Inter-Bold", 50)
    d.text((W / 2, y), txt, font=f, fill=col + (int(255 * a),), anchor="ms", stroke_width=3, stroke_fill=(6, 7, 16, int(255 * a)))


def part_pill(d, t, rnd):
    if t < 3.2: return
    a = ease((t - 3.2) / 0.4)
    f = font("Inter-Bold", 30)
    label(d, W / 2, 232, f"SAME COLOUR  PART 2   {rnd}/3", f, MUTED + (int(255 * a),), spacing=5)


def pill_text(im, t, t0, txt, y=1440, col=WHITE, size=50):
    if t < t0: return
    a = ease((t - t0) / 0.3)
    f = font("Inter-Bold", size)
    w_ = f.getlength(txt)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle((W / 2 - w_ / 2 - 30, y - size - 14, W / 2 + w_ / 2 + 30, y + 26), radius=26, fill=(8, 9, 20, int(225 * a)))
    od.text((W / 2, y), txt, font=f, fill=col + (int(255 * a),), anchor="ms")
    im.alpha_composite(ov)


HOOK1 = [[("Blue and green?", WHITE)], [("SAME colour.", GOLD)]]
HOOK2 = [[("Put your thumb", WHITE)], [("on the line.", GOLD)]]
HOOK3 = [[("Brown and orange?", WHITE)], [("SAME tile.", GOLD)]]


def frame(i):
    t = i / FPS
    if t < R2:
        if t < REV1: st = 1.0
        elif t < BACK1: st = 1 - ease((t - REV1) / 0.45)
        else: st = ease((t - BACK1) / 0.6)
        im = spiral(t, st)
        hook_text(im, t, HOOK1, y=392, size=118)
        stamp(im, t, REV1, [("ONE TEAL.", CYAN)], y=1010, size=150, hold=BACK1 - REV1)
        pill_text(im, t, BACK1 + 0.3, "The stripes paint it.")
        part_pill(ImageDraw.Draw(im), t, 1)
    elif t < R3:
        im = CORN.copy()
        if t >= REV2 - 0.6:
            u = ease_out((t - (REV2 - 0.6)) / 0.6)
            thumb(im, int(lerp(H + 20, CS_Y0 - 40, u)))
        hook_text(im, t, HOOK2, y=392, size=118, t0=R2)
        if t < REV2 + 1.7:
            stamp(im, t, REV2, [("SAME GREY.", GOLD)], y=1440, size=120, panel=True)
        pill_text(im, t, REV2 + 1.7, "Your brain only reads the edge.")
        part_pill(ImageDraw.Draw(im), t, 2)
    elif t < RC + 0.5:
        if t < REV3: im = CUBE
        else:
            br = ease((t - REV3) / 0.5)
            iso = ease((t - REV3 - 0.5) / 0.5) * 0.94
            if t >= REV3 + 3.0: iso *= 1 - ease((t - REV3 - 3.0) / 0.5)
            im = cube_img(iso, br)
        im = im.copy()
        hook_text(im, t, HOOK3, y=392, size=118, t0=R3)
        if REV3 <= t < REV3 + 1.7:
            stamp(im, t, REV3, [("SAME.", GOLD)], y=1440, size=130, panel=True)
        pill_text(im, t, REV3 + 1.7, "Your brain brightens the shadow.")
        part_pill(ImageDraw.Draw(im), t, 3)
    else:
        im = CUBE.copy()
    # round transition flash
    for tb in (R2, R3):
        if tb - 0.12 < t < tb + 0.18:
            a = 1 - abs(t - tb) / 0.18
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(110 * max(0, a)))))
    if t >= RC:
        a = ease((t - RC) / 0.4)
        # last 0.6 s: the spiral fades back in so the loop hands back to frame 0
        if t >= DUR - 0.6:
            k = ease((t - (DUR - 0.6)) / 0.6)
            im = Image.blend(im, spiral(t - DUR, 1.0), k)
            a *= 1 - k
        ov = Image.new("RGBA", im.size, (8, 9, 20, int(170 * a))); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 700, W - 70, 1290), radius=40, fill=(8, 9, 20, int(235 * a)))
        draw_rich(od, W / 2, 830, [("Which one got you?", WHITE + (int(255 * a),))], font("Inter-Black", 76))
        draw_rich(od, W / 2, 1000, [("1", GOLD + (int(255 * a),)), ("   2   ", PINK + (int(255 * a),)), ("3", CYAN + (int(255 * a),))], font("Inter-Black", 128))
        draw_rich(od, W / 2, 1150, [("Part 3 is harder. ", MUTED + (int(255 * a),)), ("Follow.", GOLD + (int(255 * a),))], font("Inter-Bold", 50))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.5, 2.8, 5.5, 7.5, 9.6, 11.5, 13.5, 15.6, 17.0, 19.0, 21.3]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88)
        for t in ts[:1]:
            frame(int(t * FPS)).save("f0.png")
    else:
        w = Writer("v025_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
