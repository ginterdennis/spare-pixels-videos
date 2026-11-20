"""Spare Pixels — 'REN' Part 2 / Day 2: the water runs out.
Same look as Part 1 (world at 270x480, x4 / x8 close-ups, Silkscreen dialogue boxes), daytime rooftop.
Survival fact: never eat snow (it costs body heat and energy); melt clean snow in a black bag in the sun.
"""
import math, sys, os, subprocess
import numpy as np
import skia
import assets as A
import scene as S1   # reuse overlay helpers (pixel_box, shadow_text, layout, fonts)

W, H, LW, LH, FPS = 1080, 1920, 270, 480, 30
BPM = 104
BEAT = 60 / BPM
def b(x): return x * BEAT
hx = A.hx
clamp, smooth, ease_out, ease_back = S1.clamp, S1.smooth, S1.ease_out, S1.ease_back
fillp, pixel_box, shadow_text, layout, font = S1.fillp, S1.pixel_box, S1.shadow_text, S1.layout, S1.font
TXT, ACC, MUTED, INK = S1.TXT, S1.ACC, S1.MUTED, S1.INK
NEAREST = S1.NEAREST

# ---------------- timeline ----------------
T_EAT, T_HEAT, T_BAG, T_MELT, T_RATIO, T_FILL, T_INV = b(6), b(11), b(16), b(22), b(28), b(34), b(38)
T_UPD = [b(40), b(41.5), b(43)]           # bottle, granola, bags update
T_END, DURATION = b(46), b(57)
NFRAMES = int(round(DURATION * FPS))
DIALOG = [
    (0.0, T_EAT, "*Day* *2.* Ren's *water* runs out *today.* What now?", False),
    (T_EAT, T_HEAT, "Snow everywhere. But *never* *eat* *snow.*", True),
    (T_HEAT, T_BAG, "Melting it inside you burns *energy* and drops your *body* *heat.*", True),
    (T_BAG, T_MELT, "Ren fills a *black* *trash* *bag* with *clean,* *fresh* *snow.*", True),
    (T_MELT, T_RATIO, "*Black* soaks up *sunlight.* The snow melts. *No* *fire* *needed.*", True),
    (T_RATIO, T_FILL, "About *10* bottles of snow make *1* bottle of *water.*", True),
    (T_FILL, T_INV, "Ren fills the bottle. *1* *litre.*", True),
    (T_INV, T_END, "Day 2 survived. *Backpack* *updated.*", True),
    (T_END, b(51.5), "Which item saves *Ren* next? *Comment* *below.*", True),
    (b(51.5), DURATION + 1, "*Day* *3* next. Follow so *Ren* *survives.*", True),
]
CPS = 46

# ---------------- daytime world ----------------
YY, XX = np.mgrid[0:LH, 0:LW].astype(np.float32)
BAY = S1.BAYER_FULL
def lerpc(a, c, t): return np.array(a, np.float32) + (np.array(c, np.float32) - np.array(a, np.float32)) * t
SKY = np.zeros((LH, LW, 3), np.float32)
g = np.clip(YY / 330, 0, 1)
for c in range(3):
    SKY[..., c] = hx("5f8fd6")[c] + (hx("dbe7f6")[c] - hx("5f8fd6")[c]) * g
# dither into bands
SKY = np.floor(SKY / 10 + BAY[..., None] * 0.9) * 10
SUN_X, SUN_Y = 212, 70
sd = np.hypot(XX - SUN_X, YY - SUN_Y)
halo = np.clip(1 - sd / 70, 0, 1) ** 2
SKY += (halo * 60)[..., None] * (BAY[..., None] + 0.5 > 0.4)
SKY[sd < 13] = hx("fff6d6"); SKY[sd < 10] = hx("fffbec")
rng = np.random.default_rng(22)
BASE_Y = 322
FAR = S1.make_layer(5, 10, 24, 22, 72, 0.18)
MID = S1.make_layer(9, 14, 32, 45, 125, 0.5)
TOWER = S1.TOWER

def city(img):
    for layer, bls, col, edge in (("far", FAR, hx("9fb0cf"), hx("b9c7e0")), ("mid", MID, hx("7387ab"), hx("8a9cc0"))):
        for bd in bls:
            x0, x1, top = max(0, bd["x"]), min(LW, bd["x"] + bd["w"]), bd["top"]
            img[top:BASE_Y, x0:x1] = col
            img[top:BASE_Y, x0:min(x1, x0 + 1)] = edge
            img[top:top + 2, x0:x1] = hx("f2f6ff")           # snow on roofs
            r = np.random.default_rng(bd["seed"])
            for wy in range(top + 4, BASE_Y - 2, 4 if layer == "mid" else 5):
                for wx in range(bd["x"] + 2, bd["x"] + bd["w"] - 2, 3):
                    if r.uniform() < bd["win_p"] * 0.6 and 0 <= wx < LW - 1:
                        img[wy, wx] = np.array(col, np.float32) * 0.78                # dark windows: no power
        if layer == "mid":
            tx, tw, tt = TOWER["x"], TOWER["w"], TOWER["top"]
            img[tt:BASE_Y, tx:tx + tw] = hx("6a7da2"); img[tt:tt + 2, tx:tx + tw] = hx("f2f6ff")
            img[tt - 18:tt, tx + 5:tx + 6] = hx("6a7da2")
CITY = SKY.copy(); city(CITY)

# foreground: snowy parapet + roof (day palette)
PARAPET = 316
FG = np.zeros((LH, LW, 4), np.float32)
def rect(x0, y0, x1, y1, col):
    FG[max(0, y0):y1, max(0, x0):x1, :3] = col; FG[max(0, y0):y1, max(0, x0):x1, 3] = 255
rect(0, PARAPET + 2, LW, PARAPET + 9, hx("8a96b8"))
rect(0, PARAPET - 1, LW, PARAPET + 2, hx("f4f8ff"))
for y in range(PARAPET + 9, LH):
    t = (y - PARAPET - 9) / (LH - PARAPET - 9)
    col = lerpc(hx("e6eefa"), hx("b9c8e6"), t)
    FG[y, :, :3] = col
    FG[y, :, 3] = 255
# snow texture: soft blue shadows
tex = rng.uniform(0, 1, (LH, LW))
m = (tex < 0.08) & (YY > PARAPET + 10)
FG[m, :3] = hx("c9d6ee")
# AC unit with snow cap
rect(200, 350, 242, 378, hx("8d97b5")); rect(200, 347, 242, 352, hx("f4f8ff"))
for gx in range(206, 238, 3): rect(gx, 356, gx + 1, 374, hx("6f7897"))
rect(199, 378, 243, 380, hx("a9b6d6"))
# vent pipe
rect(38, 340, 44, 366, hx("8790b0")); rect(35, 334, 47, 340, hx("f4f8ff")); rect(38, 366, 44, 368, hx("a9b6d6"))
# antenna
rect(252, 262, 253, PARAPET, hx("6c7898"))
for yy in (272, 284, 296): rect(248, yy, 257, yy + 1, hx("6c7898"))
# footprints in the snow (Ren walked around)
for k in range(9):
    fx, fy = 112 + int(6 * math.sin(k * 0.9)) + k * 6, 352 + k * 4
    if fy < LH - 2: rect(fx, fy, fx + 2, fy + 1, hx("b3c2e2"))

REN_X, REN_FEET = 96, 342
REN_FRAMES = [A.ren_sprite(0), A.ren_sprite(1)]
BAG_X, BAG_Y = 124, 350       # top-left of the bag sprite (26 x 18)
SNOWFALL = [(rng.uniform(0, LW), rng.uniform(-LH, LH), rng.uniform(8, 16), rng.uniform(0, 6.28)) for _ in range(70)]

def melt_level(t):
    """0 = bag full of snow, 1 = all water"""
    return smooth(t, T_MELT + b(0.5), T_RATIO - b(0.3))

def fill_level(t):
    return smooth(t, T_BAG + b(1), T_BAG + b(4.5))

def draw_bag(img, t):
    """open black bag lying in the snow, seen from slightly above: the opening shows snow / water."""
    bx, by = BAG_X, BAG_Y
    BW, BH = 30, 18
    cx, cy = bx + BW / 2 - 0.5, by + 4.0            # centre of the opening
    rx, ry = 13.0, 3.6
    fl = fill_level(t); ml = melt_level(t)
    BAGC, BAGH, OUTL, RIM = hx("23273a"), hx("4a5276"), hx("0a0b14"), hx("5a6388")
    for y in range(by, by + BH):
        for x in range(bx, bx + BW):
            u = (x - (bx + BW / 2 - 0.5)) / (BW / 2)
            v = (y - by) / BH
            body_half = 1.0 - 0.18 * max(0.0, v - 0.55) / 0.45     # tapers at the bottom
            inside_body = abs(u) <= body_half and y >= cy
            e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e <= 1.0:                           # opening
                if fl <= 0.02: col = hx("15182a")
                else:
                    r = math.sqrt(e)
                    r_snow = 1.15 - 1.2 * smooth(ml, 0.25, 1.0)
                    if ml > 0 and r > r_snow:
                        sh = 0.5 + 0.5 * math.sin(t * 4 + x * 0.8 + y * 1.3)
                        col = hx("7fc0ff") if (sh > 0.86 and y <= cy) else (hx("3d8fe0") if y <= cy else hx("2f6fe0"))
                    else:
                        col = hx("ffffff") if (x - cx) > -3 and y <= cy else hx("dfe8f8")
                img[y, x] = col
            elif e <= 1.45:
                img[y, x] = RIM if y < cy else OUTL
            elif inside_body:
                edge = abs(u) > body_half - 0.09 or y == by + BH - 1
                img[y, x] = OUTL if edge else (BAGH if (x - bx) in (5, 6) and 6 < y - by < 14 else BAGC)
    # snow mound above the opening (shrinks first while melting)
    hh = 8 * fl * (1 - smooth(ml, 0.0, 0.5))
    if hh > 0.3:
        for x in range(int(cx - 10), int(cx + 11)):
            top = cy - hh * math.sqrt(max(0.0, 1 - ((x - cx) / 10.5) ** 2))
            for y in range(int(math.floor(top)), int(cy) + 1):
                img[y, x] = hx("ffffff") if (x - cx) > -3 and y < top + 2 else hx("dfe8f8")
    # sun glints on the plastic
    if T_MELT <= t < T_RATIO:
        for k in range(3):
            ph = (t * 0.9 + k * 0.33) % 1
            if ph < 0.25:
                gx, gy = bx + 4 + k * 9, by + 9 + (k % 2) * 3
                img[gy, gx] = hx("ffffff"); img[gy, gx + 1] = hx("cfd6ee")

def sun_rays(img, t, strength):
    if strength <= 0: return
    # diagonal light shafts from the sun towards the bag
    d = (XX - BAG_X - 13) * 0.62 + (YY - BAG_Y) * 0.78
    band = (np.sin(d * 0.35 - t * 2.2) > 0.55) & (YY < BAG_Y + 4) & (XX > BAG_X - 30)
    m = band & (BAY + 0.47 < strength * 0.5)
    img[m] = img[m] * 0.6 + np.array(hx("fff3c4"), np.float32) * 0.4

def world(t):
    img = CITY.copy()
    a = FG[..., 3:4] / 255.0
    img = img * (1 - a) + FG[..., :3] * a
    # scoops Ren took from the snow (appear while filling)
    if t >= T_BAG:
        k = int(clamp((t - T_BAG) / b(4)) * 6)
        for j in range(k):
            sx, sy = 162 + j * 5, 392 + (j % 2) * 4
            img[sy:sy + 2, sx:sx + 4] = hx("b3c2e2")
    draw_bag(img, t)
    sun_rays(img, t, smooth(t, T_MELT, T_MELT + b(1)) * (1 - smooth(t, T_RATIO, T_RATIO + b(1))))
    # Ren (shivers while talking about body heat)
    fr = REN_FRAMES[int(t / 0.22) % 2]
    bob = 1 if (t % 2.4) > 1.2 else 0
    shiver = (1 if int(t * 24) % 2 else -1) if T_HEAT + b(1) <= t < T_BAG else 0
    rx = REN_X + shiver
    ry = REN_FEET - 32 + bob
    sa = fr[..., 3:4] / 255.0
    region = img[ry:ry + 32, rx:rx + 20]
    img[ry:ry + 32, rx:rx + 20] = region * (1 - sa) + fr[..., :3] * sa
    # light snowfall
    for i, (x0, y0, v, ph) in enumerate(SNOWFALL):
        y = (y0 + v * t) % (LH + 20) - 10
        x = (x0 + 4 * t + 3 * math.sin(t * 0.9 + ph)) % LW
        xi, yi = int(x), int(y)
        if 0 <= yi < LH and 0 <= xi < LW: img[yi, xi] = hx("ffffff")
    return np.clip(img, 0, 255).astype(np.uint8)

# ---------------- overlays ----------------
F_DLG = font(S1.TF_SILK_R, 48)
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
                if k > 0: shadow_text(cv, w[:k], x, y, F_DLG, ACC if acc else TXT, sh=6)
                shown += len(w) + 1; x += ww + sp
        total = len(" ".join(w for ln in lines for w, _, _ in ln))
        if n >= total and (t * 2.5) % 1 < 0.6:
            tx, ty = x1 - 52, y1 - 34
            for i in range(4):
                cv.drawRect(skia.Rect.MakeLTRB(tx + i * 4, ty + i * 4, tx + 24 - i * 4, ty + i * 4 + 4), fillp(ACC))
        cv.restore()
        tab = "PART 2  DAY 2"
        ft = font(S1.TF_SILK, 24); tw_ = ft.measureText(tab)
        cv.drawRect(skia.Rect.MakeLTRB(x0 + 24, y0 - 22, x0 + 24 + tw_ + 28, y0 + 14), fillp(ACC))
        cv.drawString(tab, x0 + 38, y0 + 6, ft, fillp(INK))

def draw_title(cv, t):
    a = 1 - smooth(t, T_EAT - 0.25, T_EAT + 0.05)
    if a <= 0: return
    f = font(S1.TF_SILK, 192); s = "DAY 2"; w = f.measureText(s)
    shadow_text(cv, s, 540 - w / 2, 690, f, ACC, a, sh=10)

def bottle_grid(level):
    """WATER BOTTLE icon with a given water level 0..1 (10 inner rows: 4..13)."""
    base = [r for r in A.ITEMS[0]["grid"]]
    rows = []
    n_water = int(round(level * 10))
    for y, r in enumerate(base):
        if 4 <= y <= 13:
            inner = "".join("W" if c in "phsWH" else c for c in r)
            if (13 - y) >= n_water:
                inner = "".join("p" if c == "W" else c for c in inner)
            elif (13 - y) == n_water - 1:
                inner = "".join("s" if c == "W" else c for c in inner)
            if y < 13: inner = inner[:9] + ("H" if inner[9] == "W" else ("h" if inner[9] == "p" else inner[9])) + inner[10:]
            rows.append(inner)
        else:
            rows.append(r)
    return rows
def icon_image(rows, pal):
    return skia.Image.fromarray(A.grid_to_rgba(rows, pal), colorType=skia.kRGBA_8888_ColorType)
BPAL = A.ITEMS[0]["pal"]
SNOW_PAL = dict(BPAL); SNOW_PAL.update({"W": hx("ffffff"), "H": hx("dfe8f8"), "s": hx("ffffff"), "p": hx("ffffff"), "h": hx("ffffff")})

def draw_thermo(cv, t):
    if not (T_HEAT + b(0.5) <= t < T_BAG): return
    e = t - T_HEAT - b(0.5)
    a = clamp(e / 0.2) * (1 - smooth(t, T_BAG - 0.25, T_BAG))
    x0, y0 = 780, 760
    pixel_box(cv, x0 - 40, y0 - 40, x0 + 200, y0 + 520, a)
    # tube
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 56, y0 + 20, x0 + 104, y0 + 380), fillp(hx("2c3160"), a))
    lvl = 0.8 - 0.45 * smooth(e, 0.6, 2.4)
    top = y0 + 20 + (1 - lvl) * 360
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 64, top, x0 + 96, y0 + 380), fillp(hx("e0453a"), a))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 40, y0 + 370, x0 + 120, y0 + 450), fillp(hx("e0453a"), a))
    for k in range(6):
        cv.drawRect(skia.Rect.MakeLTRB(x0 + 108, y0 + 40 + k * 60, x0 + 128, y0 + 46 + k * 60), fillp(TXT, a))
    # down arrow
    if e > 0.8 and (t * 3) % 1 < 0.7:
        for i in range(5):
            cv.drawRect(skia.Rect.MakeLTRB(x0 - 4 + i * 6, y0 + 150 + i * 6, x0 + 44 - i * 6, y0 + 156 + i * 6), fillp(hx("9fd0ff"), a))
        cv.drawRect(skia.Rect.MakeLTRB(x0 + 14, y0 + 90, x0 + 26, y0 + 150), fillp(hx("9fd0ff"), a))

def draw_ratio(cv, t):
    if not (T_RATIO - 0.05 <= t < T_FILL): return
    e = t - T_RATIO
    a = clamp(e / 0.25) * (1 - smooth(t, T_FILL - 0.25, T_FILL))
    pixel_box(cv, 70, 740, 1010, 1330, a)
    snow = icon_image(bottle_grid(1.0), SNOW_PAL); water = icon_image(bottle_grid(1.0), BPAL)
    for i in range(10):
        ti = 0.15 + i * 0.12
        if e < ti: continue
        r, c = divmod(i, 5)
        x, y = 120 + c * 96, 800 + r * 140
        sc = ease_back(clamp((e - ti) / 0.2), 2.4)
        cv.save(); cv.translate(x + 48, y + 64); cv.scale(sc, sc)
        cv.drawImageRect(snow, skia.Rect.MakeXYWH(-48, -48, 96, 96), NEAREST); cv.restore()
    fl = font(S1.TF_SILK, 40)
    if e > 1.5:
        shadow_text(cv, "10x SNOW", 140, 1150, fl, TXT, a, sh=4)
        shadow_text(cv, "=", 645, 1000, font(S1.TF_SILK, 96), ACC, a, sh=6)
    if e > 1.9:
        sc = ease_back(clamp((e - 1.9) / 0.25), 2.4)
        cv.save(); cv.translate(850, 960); cv.scale(sc, sc)
        cv.drawImageRect(water, skia.Rect.MakeXYWH(-128, -128, 256, 256), NEAREST); cv.restore()
        f36 = font(S1.TF_SILK, 36); shadow_text(cv, "1x WATER", 850 - f36.measureText("1x WATER") / 2, 1150, f36, hx("7fc0ff"), a, sh=4)
    fs = font(S1.TF_SILK_R, 28)
    if e > 2.3:
        shadow_text(cv, "FRESH SNOW IS MOSTLY AIR", 140, 1260, fs, MUTED, a, sh=3)

def draw_fill(cv, t):
    if not (T_FILL - 0.05 <= t < T_INV): return
    e = t - T_FILL
    a = clamp(e / 0.2) * (1 - smooth(t, T_INV - 0.2, T_INV))
    pixel_box(cv, 290, 720, 790, 1360, a)
    lvl = 0.5 + 0.5 * smooth(e, 0.3, 1.9)
    img = icon_image(bottle_grid(lvl), BPAL)
    cv.drawImageRect(img, skia.Rect.MakeXYWH(540 - 192, 770, 384, 384), NEAREST)
    fl = font(S1.TF_SILK, 56)
    txt = f"{lvl:.1f} L"
    shadow_text(cv, txt, 540 - fl.measureText(txt) / 2, 1270, fl, ACC if lvl >= 0.999 else TXT, a, sh=5)

# inventory (same layout as Part 1, with updated states)
PX0, PY0, PX1, PY1 = 70, 478, 910, 1412
GX0, GY0, SW, SH, GAPX, GAPY = 95, 668, 250, 168, 20, 14
ICONS = [skia.Image.fromarray(A.item_rgba(it), colorType=skia.kRGBA_8888_ColorType) for it in A.ITEMS]
BOTTLE_FULL = icon_image(bottle_grid(1.0), BPAL)
SUB_OLD = {it["key"]: it["sub"] for it in A.ITEMS}
SUB_NEW = {"bottle": "full 1 l", "granola": "x2", "bags": "1 in use"}
UPD_KEYS = ["bottle", "granola", "bags"]

def draw_inventory(cv, t):
    if t < T_INV - 0.05: return
    e = t - T_INV
    off = (1 - ease_out(e / 0.42)) * 1500
    cv.save(); cv.translate(0, off)
    pixel_box(cv, PX0, PY0, PX1, PY1, fill=hx("0b0d1c"))
    fh = font(S1.TF_SILK, 40)
    shadow_text(cv, "REN'S BACKPACK", PX0 + 34, PY0 + 74, fh, TXT, sh=4)
    shadow_text(cv, "12/12", PX1 - 34 - fh.measureText("12/12"), PY0 + 74, fh, ACC, sh=4)
    u0 = smooth(t, T_UPD[0], T_UPD[0] + 0.4); u1 = smooth(t, T_UPD[1], T_UPD[1] + 0.4); u2 = smooth(t, T_UPD[2], T_UPD[2] + 0.4)
    labels = [("WATER", "1.0 L" if u0 > 0.5 else "0.5 L", 0.5 + 0.5 * u0, hx("3d8fe0")),
              ("FOOD", "2 BARS" if u1 > 0.5 else "3 BARS", 0.6 - 0.2 * u1, hx("3fa34d")),
              ("WINTER", "20 DAYS", 1.0 - 0.05 * smooth(t, T_INV + 0.4, T_INV + 1.2), hx("cfe8ff"))]
    fl, fv = font(S1.TF_SILK_R, 16), font(S1.TF_SILK, 24)
    for i, (lab, val, frac, col) in enumerate(labels):
        x0 = GX0 + i * (SW + GAPX); y0 = PY0 + 98
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + 60), fillp(hx("171a33")))
        cv.drawString(lab, x0 + 12, y0 + 26, fl, fillp(MUTED))
        segs = 5; filled = frac * segs
        segw = (SW - 24 - 4 * 6) / segs
        for s_ in range(segs):
            sx = x0 + 12 + s_ * (segw + 6)
            on = s_ + 1 <= filled + 1e-6
            cv.drawRect(skia.Rect.MakeLTRB(sx, y0 + 38, sx + segw, y0 + 50), fillp(col if on else hx("2c3160")))
        cv.drawString(val, x0 + SW - 12 - fv.measureText(val), y0 + 28, fv, fillp(TXT))
    fn, fs = font(S1.TF_SILK_R, 24), font(S1.TF_SILK_R, 16)
    for i, it in enumerate(A.ITEMS):
        r, c = divmod(i, 3)
        x0 = GX0 + c * (SW + GAPX); y0 = GY0 + r * (SH + GAPY)
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + SH), fillp(hx("141730")))
        key = it["key"]
        upd = key in UPD_KEYS
        tu = T_UPD[UPD_KEYS.index(key)] if upd else None
        flash = math.exp(-(t - tu) / 0.18) if upd and t >= tu else 0.0
        brd = tuple(int(v1 + (v2 - v1) * flash) for v1, v2 in zip(hx("3a4180"), hx("ffffff")))
        if upd and t >= tu: brd = tuple(int(v1 + (v2 - v1) * max(flash, 0.0)) for v1, v2 in zip(hx("8a6a20"), hx("ffffff")))
        for (l, tp, rr, bt) in ((x0, y0, x0 + SW, y0 + 4), (x0, y0 + SH - 4, x0 + SW, y0 + SH),
                                (x0, y0, x0 + 4, y0 + SH), (x0 + SW - 4, y0, x0 + SW, y0 + SH)):
            cv.drawRect(skia.Rect.MakeLTRB(l, tp, rr, bt), fillp(brd))
        cx, cy = x0 + SW / 2, y0 + 70
        sc = 1.0 + (0.25 * math.sin(math.pi * clamp((t - tu) / 0.3)) if upd and t >= tu else 0)
        icon = BOTTLE_FULL if (key == "bottle" and t >= T_UPD[0]) else ICONS[i]
        cv.save(); cv.translate(cx, cy); cv.scale(sc, sc)
        cv.drawImageRect(icon, skia.Rect.MakeXYWH(-48, -48, 96, 96), NEAREST); cv.restore()
        nm = it["name"]
        cv.drawString(nm, cx - fn.measureText(nm) / 2, y0 + SH - 18, fn, fillp(TXT))
        sub = SUB_NEW[key] if (upd and t >= tu) else SUB_OLD[key]
        if sub:
            sb = sub.upper()
            cv.drawString(sb, x0 + SW - 14 - fs.measureText(sb), y0 + 30, fs, fillp(hx("7fc0ff") if (upd and t >= tu) else ACC))
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
    if T_BAG <= t < T_RATIO:
        return 8, BAG_X + 15, BAG_Y - 16
    return 4, LW / 2, LH / 2

def frame(t):
    img = world(t)
    rgba = np.dstack([img, np.full((LH, LW), 255, np.uint8)])
    simg = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    z, cx, cy = camera(t)
    vw, vh = W / z, H / z
    x0 = clamp(cx - vw / 2, 0, LW - vw); y0 = clamp(cy - vh / 2, 0, LH - vh)
    cv.drawImageRect(simg, skia.Rect.MakeXYWH(round(x0), round(y0), vw, vh), skia.Rect.MakeXYWH(0, 0, W, H), NEAREST)
    if 0 <= t - T_BAG < 0.12: cv.drawPaint(fillp(TXT, 0.5 * (1 - (t - T_BAG) / 0.12)))
    if 0 <= t - T_RATIO < 0.12: cv.drawPaint(fillp(TXT, 0.4 * (1 - (t - T_RATIO) / 0.12)))
    dim = max(ease_out((t - T_RATIO) / 0.3) * (1 - smooth(t, T_INV - 0.3, T_INV)) if T_RATIO <= t < T_INV else 0,
              ease_out((t - T_INV) / 0.3) if t >= T_INV else 0)
    if dim > 0: cv.drawPaint(fillp(hx("05060e"), 0.62 * dim))
    draw_title(cv, t)
    draw_thermo(cv, t)
    draw_ratio(cv, t)
    draw_fill(cv, t)
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
        print(f"duration {DURATION:.2f}s frames {NFRAMES}; bag {T_BAG:.2f} melt {T_MELT:.2f} ratio {T_RATIO:.2f} inv {T_INV:.2f} end {T_END:.2f}")
    elif sys.argv[1] == "stills":
        from PIL import Image
        ims = []
        for s in sys.argv[2:]:
            arr = frame(float(s)).toarray(colorType=skia.kRGBA_8888_ColorType)
            ims.append(Image.fromarray(arr[..., :3]).resize((270, 480)))
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("/home/claude/v013_stills.jpg", quality=88)
    elif sys.argv[1] == "chunk":
        render_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
