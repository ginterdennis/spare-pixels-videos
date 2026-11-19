"""Spare Pixels — 'REN' Part 1 / Day 1. Pixel-art world rendered at 270x480 and scaled x4 (or x8 for close-ups)."""
import math, sys, os, subprocess
import numpy as np
import skia
import assets as A

W, H = 1080, 1920
LW, LH = 270, 480
FPS = 30
BPM = 104
BEAT = 60 / BPM
def b(x): return x * BEAT

# ---------------- timeline (in beats) ----------------
T_STORM, T_GRID, T_NOHELP, T_WINTER, T_MEET, T_INV = b(6), b(10), b(14), b(18), b(22), b(28)
ITEM_T = [b(30 + 1.5 * i) for i in range(12)]
T_MATTER, T_END, DURATION = b(48), b(52), b(62)
NFRAMES = int(round(DURATION * FPS))
FLASHES = [(b(10.7), 62, 262), (b(11.6), 150, 236), (b(12.5), 228, 250)]
T_POWERDOWN = b(13)

DIALOG = [  # (start, end, text, typewriter?)  *word* = accent
    (0.0, T_STORM, "Can *Ren* survive the apocalypse with just *12* *items?*", False),
    (T_STORM, T_GRID, "A *solar* *storm* just hit Earth.", True),
    (T_GRID, T_NOHELP, "The *power* *grid* failed. Everywhere.", True),
    (T_NOHELP, T_WINTER, "No phones. No internet. *No* *help* *coming.*", True),
    (T_WINTER, T_MEET, "And *winter* is *21* *days* away.", True),
    (T_MEET, T_INV, "This is *Ren.* Everything Ren has fits in one *backpack.*", True),
    (T_MATTER, T_END, "Every item will *matter.*", True),
    (T_END, b(57), "Which item saves *Ren* first? *Comment* *below.*", True),
    (b(57), DURATION + 1, "*Day* *2* next. Follow so *Ren* *survives.*", True),
]
CPS = 46  # typewriter characters per second

def clamp(u, a=0.0, c=1.0): return max(a, min(c, u))
def smooth(x, a, c):
    u = clamp((x - a) / (c - a)); return u * u * (3 - 2 * u)
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def ease_back(u, s=2.0): u = clamp(u) - 1; return u * u * ((s + 1) * u + s) + 1
hx = A.hx

# ---------------- palette for the dithered sky ----------------
def lerp(a, c, t): return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, c))
SKY_TOP, SKY_HOR = hx("060816"), hx("26305f")
GREEN, TEAL, VIOLET, PINK = hx("39f0a0"), hx("1fb8a8"), hx("7a52f0"), hx("d05ce0")
GLOW = hx("6a3a3a")
PAL = [lerp(SKY_TOP, SKY_HOR, i / 7) for i in range(8)]
for base in (lerp(SKY_TOP, SKY_HOR, 0.35), lerp(SKY_TOP, SKY_HOR, 0.7)):
    for c in (GREEN, TEAL, VIOLET):
        for k in (0.3, 0.55, 0.8):
            PAL.append(lerp(base, c, k))
PAL += [GREEN, hx("a8ffd8"), lerp(VIOLET, PINK, 0.5), hx("3a2c4a"), hx("5a3a48"), hx("8a5048"),
        hx("cfe8ff"), hx("ffffff"), hx("9fd0ff")]
PAL = np.array(PAL, np.float32)
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.47)
BAYER_FULL = np.tile(BAYER, (LH // 4 + 1, LW // 4 + 1))[:LH, :LW]

def quantize(img):
    """ordered-dither an RGB float image onto PAL"""
    x = img + BAYER_FULL[..., None] * 26
    flat = x.reshape(-1, 3)
    out = np.empty_like(flat)
    for s in range(0, flat.shape[0], 32768):
        blk = flat[s:s + 32768]
        d = ((blk[:, None, :] - PAL[None, :, :]) ** 2).sum(-1)
        out[s:s + 32768] = PAL[d.argmin(1)]
    return out.reshape(img.shape)

# ---------------- static world ----------------
rng = np.random.default_rng(21)
YY, XX = np.mgrid[0:LH, 0:LW].astype(np.float32)
SKY = np.zeros((LH, LW, 3), np.float32)
g = np.clip(YY / 320, 0, 1) ** 1.3
for c in range(3):
    SKY[..., c] = SKY_TOP[c] + (SKY_HOR[c] - SKY_TOP[c]) * g
STARS = [(int(rng.uniform(0, LW)), int(rng.uniform(0, 230)), rng.uniform(0.4, 1.0), rng.uniform(0, 6.28)) for _ in range(140)]

BASE_Y = 322   # city base hidden behind the parapet
def make_layer(seed, wmin, wmax, hmin, hmax, win_p):
    r = np.random.default_rng(seed); x = -6; bl = []
    while x < LW + 6:
        w = int(r.integers(wmin, wmax)); h = int(r.integers(hmin, hmax))
        bl.append(dict(x=x, w=w, top=BASE_Y - h, win_p=win_p, seed=int(r.integers(1e9))))
        x += w + int(r.integers(0, 3))
    return bl
FAR = make_layer(5, 10, 24, 22, 72, 0.18)
MID = make_layer(9, 14, 32, 45, 125, 0.5)
TOWER = dict(x=196, w=12, top=BASE_Y - 152)
WINDOWS = []   # (x, y, layer, color, off_time)
WCOLS = [hx("ffd36b"), hx("ffb347"), hx("ffe9a8"), hx("ff9e5e")]
for layer, bls in (("far", FAR), ("mid", MID + [dict(x=TOWER["x"], w=TOWER["w"], top=TOWER["top"], win_p=0.55, seed=77)])):
    for bd in bls:
        r = np.random.default_rng(bd["seed"])
        sx, sy = (3, 4) if layer == "mid" else (3, 5)
        for wy in range(bd["top"] + 4, BASE_Y - 2, sy):
            for wx in range(bd["x"] + 2, bd["x"] + bd["w"] - 2, sx):
                if r.uniform() < bd["win_p"] and 0 <= wx and wx + 1 < LW:
                    cx = (wx + 3) / LW
                    off = T_GRID + b(0.6) + cx * b(2.1) + r.uniform(0, b(0.45))
                    if r.uniform() < 0.04: off = T_POWERDOWN - r.uniform(0, b(0.15))
                    WINDOWS.append((wx, wy, layer, WCOLS[int(r.integers(4))], off, r.uniform(0, 6.28)))

# foreground: parapet, roof, rooftop objects (RGBA, static)
FG = np.zeros((LH, LW, 4), np.uint8)
def rect(a, x0, y0, x1, y1, col, alpha=255):
    a[max(0, y0):y1, max(0, x0):x1, :3] = col; a[max(0, y0):y1, max(0, x0):x1, 3] = alpha
PARAPET = 316
rect(FG, 0, PARAPET + 2, LW, PARAPET + 9, hx("1d2038"))
rect(FG, 0, PARAPET, LW, PARAPET + 2, hx("343a5c"))
for x in range(0, LW, 9):           # coping joints
    rect(FG, x, PARAPET, x + 1, PARAPET + 2, hx("262a46"))
for y in range(PARAPET + 9, LH):
    t = (y - PARAPET - 9) / (LH - PARAPET - 9)
    c0, c1 = np.array(hx("171a2e"), np.float32), np.array(hx("0b0c18"), np.float32)
    col = c0 + (c1 - c0) * t
    for x in range(LW):
        j = BAYER[y % 4, x % 4]
        cc = col + j * 10
        FG[y, x, :3] = np.clip(cc, 0, 255); FG[y, x, 3] = 255
rect(FG, 0, PARAPET + 9, LW, PARAPET + 10, hx("0c0d1a"))
# AC unit
rect(FG, 200, 350, 242, 378, hx("23273f")); rect(FG, 200, 350, 242, 352, hx("353b5e"))
for gx in range(206, 238, 3): rect(FG, gx, 356, gx + 1, 374, hx("15182a"))
rect(FG, 199, 378, 243, 380, hx("0a0b14"))
# vent pipe
rect(FG, 38, 340, 44, 366, hx("2a2e48")); rect(FG, 35, 336, 47, 340, hx("3a4066")); rect(FG, 38, 366, 44, 368, hx("0a0b14"))
# antenna mast (stands on the parapet)
rect(FG, 252, 262, 253, PARAPET, hx("2b3050"))
for yy in (272, 284, 296): rect(FG, 248, yy, 257, yy + 1, hx("2b3050"))
# roof gravel speckle
for _ in range(500):
    x, y = int(rng.uniform(0, LW)), int(rng.uniform(PARAPET + 12, LH))
    FG[y, x, :3] = hx("23263c") if rng.uniform() < 0.5 else hx("0a0b16")
SNOW_MASK = rng.uniform(0, 1, (LH, LW)).astype(np.float32)
SNOWFLAKES = [(rng.uniform(0, LW), rng.uniform(-LH, LH), rng.uniform(14, 32), rng.uniform(0, 6.28),
               rng.uniform(0.6, 1.6), 2 if rng.uniform() < 0.28 else 1) for _ in range(260)]

REN_X, REN_FEET = 104, 342
REN_FRAMES = [A.ren_sprite(0), A.ren_sprite(1)]

# ---------------- dynamic world ----------------
def storm_level(t):
    s = 0.32
    s += 0.95 * smooth(t, T_STORM - b(0.5), T_STORM + b(2.2))
    s -= 0.35 * smooth(t, T_NOHELP, T_WINTER)
    s += 0.08 * math.sin(t * 7) * smooth(t, T_STORM, T_STORM + b(1)) * (1 - smooth(t, T_GRID, T_NOHELP))
    return s

def aurora(t, S):
    sp = 1 + 1.2 * smooth(t, T_STORM, T_STORM + b(2)) * (1 - 0.6 * smooth(t, T_NOHELP, T_WINTER))
    ph = t * sp
    X = XX[:250]; Y = YY[:250]
    out = np.zeros((250, LW, 3), np.float32)
    for (y0, hh, amp, k1, k2, w1, w2, gain, hi) in ((156, 86, 18, 0.035, 0.09, 0.5, -0.8, 1.0, VIOLET),
                                                    (104, 58, 12, 0.05, 0.12, -0.35, 0.6, 0.55, PINK)):
        yb = y0 + amp * np.sin(k1 * X + w1 * ph) + 8 * np.sin(k2 * X + w2 * ph) + 5 * np.sin(0.017 * X + 0.2 * ph)
        h = hh + 22 * np.sin(0.05 * X + 0.3 * ph + 1)
        d = yb - Y
        f = np.where(d >= 0, np.exp(-d / (0.33 * h)) * (d <= h), np.exp(d / 2.5) * 0.7)
        rays = 0.5 + 0.5 * np.sin(1.05 * X + 2.2 * np.sin(0.13 * X + 0.7 * ph) + 1.6 * ph)
        rays = 0.45 + 0.55 * rays ** 2
        I = np.clip(S * gain * f * rays, 0, 1.3)[..., None]
        u = np.clip(d / h, 0, 1)[..., None]
        col = np.where(u < 0.5, np.array(GREEN) * (1 - u * 2) + np.array(TEAL) * (u * 2),
                       np.array(TEAL) * (2 - u * 2) + np.array(hi) * (u * 2 - 1))
        out += I * col * 0.85
    return out

def window_on(wd, t):
    x, y, layer, col, off, ph = wd
    if t >= off: return False
    if off - t < b(0.35):          # flicker before dying
        return math.sin(t * 60 + ph * 7) > -0.2
    return True

def world(t, shake=(0, 0)):
    S = storm_level(t)
    img = SKY.copy()
    img[:250] += aurora(t, S)
    lit = sum(1 for wd in WINDOWS if window_on(wd, t)) / max(1, len(WINDOWS))
    glow = np.clip((YY - 200) / 120, 0, 1) ** 2 * lit
    img += glow[..., None] * np.array(GLOW, np.float32)[None, None] * 0.9
    fl = 0.0
    for tf, fx, fy in FLASHES:
        a = t - tf
        if 0 <= a < 0.5: fl += math.exp(-a / 0.09)
    if fl > 0:
        img += fl * np.array([40, 70, 110], np.float32)
    img = quantize(np.clip(img, 0, 255))
    for x, y, br, ph in STARS:
        v = br * (0.65 + 0.35 * math.sin(t * 2.1 + ph * 5))
        if v > 0.55:
            img[y, x] = np.maximum(img[y, x], np.array([200, 210, 255]) * v)
    # city
    rim = np.array([30, 70, 90], np.float32) * clamp(S - 0.3)
    for layer, bls, col, edge in (("far", FAR, hx("191e3c"), hx("222a52")), ("mid", MID, hx("0f1229"), hx("1a2044"))):
        for bd in bls:
            x0, x1, top = max(0, bd["x"]), min(LW, bd["x"] + bd["w"]), bd["top"]
            img[top:BASE_Y, x0:x1] = col
            img[top:BASE_Y, x0:min(x1, x0 + 1)] = edge
            img[top, x0:x1] = np.clip(np.array(edge, np.float32) + rim, 0, 255)
        if layer == "mid":
            tx, tw, tt = TOWER["x"], TOWER["w"], TOWER["top"]
            img[tt:BASE_Y, tx:tx + tw] = hx("0d1026"); img[tt:BASE_Y, tx:tx + 1] = hx("1a2044")
            img[tt - 3:tt, tx + 2:tx + tw - 2] = hx("0d1026")
            img[tt - 18:tt - 3, tx + 5:tx + 6] = hx("1a2044")
            if t < T_POWERDOWN and (t % 1.2) < 0.55:
                img[tt - 19, tx + 5] = hx("ff3b30"); img[tt - 19, tx + 4] = hx("8a2020"); img[tt - 19, tx + 6] = hx("8a2020")
        for wd in WINDOWS:
            if wd[2] == layer and window_on(wd, t):
                c = np.array(wd[3], np.float32) * (0.6 if layer == "far" else 1.0)
                img[wd[1], wd[0]] = c
                if layer == "mid": img[wd[1], wd[0] + 1] = c * 0.85
    for tf, fx, fy in FLASHES:
        a = t - tf
        if 0 <= a < 0.35:
            r = 2 + 16 * ease_out(a / 0.35)
            m = ((XX - fx) ** 2 + (YY - fy) ** 2) < r * r
            inner = ((XX - fx) ** 2 + (YY - fy) ** 2) < (r * 0.55) ** 2
            img[m] = hx("9fd0ff") if a > 0.12 else hx("cfe8ff")
            img[inner] = hx("ffffff")
    # foreground
    a = FG[..., 3:4] / 255.0
    img = img * (1 - a) + FG[..., :3] * a
    sn = smooth(t, T_WINTER + b(1), T_WINTER + b(14))
    if sn > 0:
        cov = SNOW_MASK < 0.9 * sn
        rows = np.zeros(LH, bool); rows[PARAPET:PARAPET + 1] = True
        img[PARAPET][cov[PARAPET]] = hx("e9f0ff")
        img[PARAPET + 1][(SNOW_MASK[PARAPET + 1] < 0.5 * sn)] = hx("b9c6e8")
        roof = (SNOW_MASK < 0.07 * sn); roof[:PARAPET + 10] = False
        img[roof] = hx("4a5478")
        ac = SNOW_MASK[350, 200:242] < 0.9 * sn
        img[350, 200:242][ac] = hx("e9f0ff")
    # Ren
    fr = REN_FRAMES[int(t / 0.22) % 2]
    bob = 1 if (t % 2.4) > 1.2 else 0
    ry = REN_FEET - 32 + bob
    sa = fr[..., 3:4] / 255.0
    region = img[ry:ry + 32, REN_X:REN_X + 20]
    img[ry:ry + 32, REN_X:REN_X + 20] = region * (1 - sa) + fr[..., :3] * sa
    # falling snow
    if t > T_WINTER - 0.2:
        dens = smooth(t, T_WINTER - 0.2, T_WINTER + b(3))
        ts = t - T_WINTER
        for i, (x0, y0, v, ph, wob, size) in enumerate(SNOWFLAKES):
            if i / len(SNOWFLAKES) > dens: break
            y = (y0 + v * ts * (1.6 if size == 2 else 1.0)) % (LH + 20) - 10
            x = (x0 + 10 * ts + 4 * math.sin(ts * wob + ph)) % LW
            xi, yi = int(x), int(y)
            if 0 <= yi < LH - 1 and 0 <= xi < LW - 1:
                col = hx("e9f0ff") if size == 2 else hx("9aa8d0")
                img[yi:yi + size, xi:xi + size] = col
    return np.clip(img, 0, 255).astype(np.uint8)

# ---------------- overlay (full-res, Skia) ----------------
FD = "/home/claude/apoc/fonts/"
TF_PIX = skia.Typeface.MakeFromFile(FD + "pixelify-sans-latin-700.ttf")
TF_SILK = skia.Typeface.MakeFromFile(FD + "silkscreen-latin-700.ttf")
TF_SILK_R = skia.Typeface.MakeFromFile(FD + "silkscreen-latin-400.ttf")
def font(tf, s):
    f = skia.Font(tf, s); f.setEdging(skia.Font.Edging.kAlias); f.setHinting(skia.FontHinting.kNone); return f
TXT, ACC, MUTED, INK = hx("f2f4ff"), hx("ffd36b"), hx("8a90b8"), hx("0a0b14")
def c4(c, a=1.0): return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, clamp(a))
def fillp(c, a=1.0): return skia.Paint(Color4f=c4(c, a), AntiAlias=False)

def pixel_box(cv, x0, y0, x1, y1, a=1.0, fill=hx("0d0f1f"), border=TXT, inner=hx("4a5290")):
    s = 6
    cv.drawRect(skia.Rect.MakeLTRB(x0 + s, y0 + s, x1 - s, y1 - s), fillp(fill, 0.93 * a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + s, y0, x1 - s, y0 + s), fillp(border, a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + s, y1 - s, x1 - s, y1), fillp(border, a))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0 + s, x0 + s, y1 - s), fillp(border, a))
    cv.drawRect(skia.Rect.MakeLTRB(x1 - s, y0 + s, x1, y1 - s), fillp(border, a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 2 * s, y0 + 2 * s, x1 - 2 * s, y0 + 2 * s + 3), fillp(inner, a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 2 * s, y1 - 2 * s - 3, x1 - 2 * s, y1 - 2 * s), fillp(inner, a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 2 * s, y0 + 2 * s, x0 + 2 * s + 3, y1 - 2 * s), fillp(inner, a))
    cv.drawRect(skia.Rect.MakeLTRB(x1 - 2 * s - 3, y0 + 2 * s, x1 - 2 * s, y1 - 2 * s), fillp(inner, a))

def shadow_text(cv, s, x, y, f, col, a=1.0, sh=6):
    cv.drawString(s, x + sh, y + sh, f, fillp(INK, a))
    cv.drawString(s, x, y, f, fillp(col, a))

def layout(text, f, maxw):
    words = []
    for w in text.upper().split():
        acc = w.startswith("*") and w.endswith("*")
        words.append((w.strip("*"), acc))
    sp = f.measureText(" ")
    lines, cur, cw = [], [], 0
    for w, acc in words:
        ww = f.measureText(w)
        if cur and cw + sp + ww > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, acc, ww)); cw += (sp if cw else 0) + ww
    lines.append(cur)
    return lines, sp

F_DLG = font(TF_SILK_R, 48)
def draw_dialog(cv, t):
    for (t0, t1, text, tw) in DIALOG:
        if not (t0 <= t < t1): continue
        e = t - t0
        lines, sp = layout(text, F_DLG, 860)
        x0, y0, x1 = 60, 236, 1020
        lh = 64
        y1 = y0 + 50 + lh * len(lines) + 26
        pop = ease_back(e / 0.18) if tw else 1.0
        cv.save(); cv.translate(540, y0); cv.scale(1, 0.85 + 0.15 * pop); cv.translate(-540, -y0)
        pixel_box(cv, x0, y0, x1, y1)
        n = len(text.replace("*", "")) if not tw else int(e * CPS)
        shown = 0
        for li, ln in enumerate(lines):
            x = x0 + 46; y = y0 + 48 + 50 + li * lh
            for w, acc, ww in ln:
                k = max(0, min(len(w), n - shown))
                if k > 0:
                    shadow_text(cv, w[:k], x, y, F_DLG, ACC if acc else TXT, sh=6)
                shown += len(w) + 1; x += ww + sp
        total = len(" ".join(w for ln in lines for w, _, _ in ln))
        if n >= total and (t * 2.5) % 1 < 0.6:
            tx, ty = x1 - 52, y1 - 34
            for i in range(4):
                cv.drawRect(skia.Rect.MakeLTRB(tx + i * 4, ty + i * 4, tx + 24 - i * 4, ty + i * 4 + 4), fillp(ACC))
        cv.restore()
        # tab label
        tab = "PART 1  DAY 1"
        ft = font(TF_SILK, 24)
        tw_ = ft.measureText(tab)
        cv.drawRect(skia.Rect.MakeLTRB(x0 + 24, y0 - 22, x0 + 24 + tw_ + 28, y0 + 14), fillp(ACC))
        cv.drawString(tab, x0 + 38, y0 + 6, ft, fillp(INK))

def draw_title(cv, t):
    a = 1 - smooth(t, T_STORM - 0.25, T_STORM + 0.05)
    if a <= 0: return
    f = font(TF_SILK, 192)
    s = "DAY 1"
    w = f.measureText(s)
    shadow_text(cv, s, 540 - w / 2, 690, f, ACC, a, sh=10)

ICON_IMGS = [skia.Image.fromarray(A.item_rgba(it), colorType=skia.kRGBA_8888_ColorType) for it in A.ITEMS]
NEAREST = skia.SamplingOptions(skia.FilterMode.kNearest)
PX0, PY0, PX1, PY1 = 70, 478, 910, 1412
GX0, GY0, SW, SH, GAPX, GAPY = 95, 668, 250, 168, 20, 14

def draw_inventory(cv, t):
    if t < T_INV - 0.05: return
    e = t - T_INV
    off = (1 - ease_out(e / 0.42)) * 1500
    cv.save(); cv.translate(0, off)
    pixel_box(cv, PX0, PY0, PX1, PY1, fill=hx("0b0d1c"))
    n = sum(1 for ti in ITEM_T if t >= ti)
    fh = font(TF_SILK, 40)
    shadow_text(cv, "REN'S BACKPACK", PX0 + 34, PY0 + 74, fh, TXT, sh=4)
    cnt = f"{n}/12"
    shadow_text(cv, cnt, PX1 - 34 - fh.measureText(cnt), PY0 + 74, fh, ACC, sh=4)
    # status row
    sf = smooth(t, T_MATTER - b(0.5), T_MATTER + b(1.5))
    labels = [("WATER", "0.5 L", 0.5, hx("3d8fe0")), ("FOOD", "3 BARS", 0.6, hx("3fa34d")), ("WINTER", "21 DAYS", 1.0, hx("cfe8ff"))]
    fl, fv = font(TF_SILK_R, 16), font(TF_SILK, 24)
    for i, (lab, val, frac, col) in enumerate(labels):
        x0 = GX0 + i * (SW + GAPX); y0 = PY0 + 98
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + 60), fillp(hx("171a33")))
        cv.drawString(lab, x0 + 12, y0 + 26, fl, fillp(MUTED))
        segs = 5; filled = frac * segs * sf
        segw = (SW - 24 - 4 * 6) / segs
        for s_ in range(segs):
            sx = x0 + 12 + s_ * (segw + 6)
            on = s_ + 1 <= filled + 1e-6
            cv.drawRect(skia.Rect.MakeLTRB(sx, y0 + 38, sx + segw, y0 + 50), fillp(col if on else hx("2c3160")))
        if sf > 0.05:
            cv.drawString(val, x0 + SW - 12 - fv.measureText(val), y0 + 28, fv, fillp(TXT, sf))
    fn, fs = font(TF_SILK_R, 24), font(TF_SILK_R, 16)
    for i, it in enumerate(A.ITEMS):
        r, c = divmod(i, 3)
        x0 = GX0 + c * (SW + GAPX); y0 = GY0 + r * (SH + GAPY)
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + SH), fillp(hx("141730")))
        ti = ITEM_T[i]
        if t < ti:
            cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + 3), fillp(hx("262a4a")))
            continue
        a = t - ti
        sc = 0.4 + 0.6 * ease_back(a / 0.22, 2.6)
        flash = math.exp(-a / 0.12)
        brd = tuple(int(v1 + (v2 - v1) * flash) for v1, v2 in zip(hx("3a4180"), hx("ffffff")))
        for (l, tp, rr, bt) in ((x0, y0, x0 + SW, y0 + 4), (x0, y0 + SH - 4, x0 + SW, y0 + SH),
                                (x0, y0, x0 + 4, y0 + SH), (x0 + SW - 4, y0, x0 + SW, y0 + SH)):
            cv.drawRect(skia.Rect.MakeLTRB(l, tp, rr, bt), fillp(brd))
        cx, cy = x0 + SW / 2, y0 + 70
        cv.save(); cv.translate(cx, cy); cv.scale(sc, sc)
        cv.drawImageRect(ICON_IMGS[i], skia.Rect.MakeXYWH(-48, -48, 96, 96), NEAREST)
        cv.restore()
        na = clamp(a / 0.15)
        nm = it["name"]
        cv.drawString(nm, cx - fn.measureText(nm) / 2, y0 + SH - 18, fn, fillp(TXT, na))
        if it["sub"]:
            sb = it["sub"].upper()
            cv.drawString(sb, x0 + SW - 14 - fs.measureText(sb), y0 + 30, fs, fillp(ACC, na))
    # selector cursor hopping across items at the end (invites the viewer to pick one)
    if t >= T_END:
        k = int((t - T_END) / (BEAT / 2)) % 12
        r, c = divmod(k, 3)
        x0 = GX0 + c * (SW + GAPX); y0 = GY0 + r * (SH + GAPY)
        for (l, tp, rr, bt) in ((x0 - 6, y0 - 6, x0 + SW + 6, y0), (x0 - 6, y0 + SH, x0 + SW + 6, y0 + SH + 6),
                                (x0 - 6, y0 - 6, x0, y0 + SH + 6), (x0 + SW, y0 - 6, x0 + SW + 6, y0 + SH + 6)):
            cv.drawRect(skia.Rect.MakeLTRB(l, tp, rr, bt), fillp(ACC))
    cv.restore()

# ---------------- frame ----------------
def camera(t):
    """(zoom, cx, cy) in low-res pixels; integer zooms keep the pixel grid crisp"""
    if T_MEET <= t < T_INV:
        return 8, REN_X + 10, REN_FEET - 52
    return 4, LW / 2, LH / 2

def frame(t):
    img = world(t)
    rgba = np.dstack([img, np.full((LH, LW), 255, np.uint8)])
    simg = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    z, cx, cy = camera(t)
    vw, vh = W / z, H / z
    x0 = clamp(cx - vw / 2, 0, LW - vw); y0 = clamp(cy - vh / 2, 0, LH - vh)
    x0, y0 = round(x0), round(y0)
    shk = 0
    for tf, fx, fy in FLASHES:
        if 0 <= t - tf < 0.25: shk = 1
    if 0 <= t - T_POWERDOWN < 0.3: shk = 1
    dx = (4 if (int(t * 40) % 2) else -4) * shk
    cv.drawImageRect(simg, skia.Rect.MakeXYWH(x0, y0, vw, vh), skia.Rect.MakeXYWH(dx, 0, W, H), NEAREST)
    # cut flash into the close-up
    if 0 <= t - T_MEET < 0.12:
        cv.drawPaint(fillp(TXT, 0.5 * (1 - (t - T_MEET) / 0.12)))
    if t >= T_INV:
        cv.drawPaint(fillp(hx("05060e"), 0.62 * ease_out((t - T_INV) / 0.3)))
    draw_title(cv, t)
    draw_inventory(cv, t)
    draw_dialog(cv, t)
    return surf.makeImageSnapshot()

def render_chunk(f0, f1, out):
    tmp = out[:-4] + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-threads", "1", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(frame(fi / FPS).toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: sys.exit("ffmpeg failed")

if __name__ == "__main__":
    if sys.argv[1] == "info":
        print(f"duration {DURATION:.2f}s frames {NFRAMES}; inv {T_INV:.2f} items {ITEM_T[0]:.2f}..{ITEM_T[-1]:.2f} end {T_END:.2f}")
        print("windows", len(WINDOWS))
    elif sys.argv[1] == "stills":
        for s in sys.argv[2:]:
            frame(float(s)).save(f"still_{float(s):05.2f}.png", skia.kPNG)
    elif sys.argv[1] == "chunk":
        render_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
