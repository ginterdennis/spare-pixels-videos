"""Spare Pixels — 'REN' Part 3 / Day 3: freezing night, no fire.
Night rooftop (Part 1 look: aurora, dead city). Survival fact: touch both terminals of a 9V battery to fine steel
wool; the thin fibres short the battery, heat up and burn, lighting dry tinder. Pack tip: store the battery away
from steel wool (it can start a fire in the bag).
"""
import math, sys, os, subprocess
import numpy as np
import skia
import assets as A
import scene as S1
import scene2 as S2

W, H, LW, LH, FPS = 1080, 1920, 270, 480, 30
BEAT = S1.BEAT
def b(x): return x * BEAT
hx = A.hx
clamp, smooth, ease_out, ease_back = S1.clamp, S1.smooth, S1.ease_out, S1.ease_back
fillp, pixel_box, shadow_text, layout, font = S1.fillp, S1.pixel_box, S1.shadow_text, S1.layout, S1.font
TXT, ACC, MUTED, INK, NEAREST = S1.TXT, S1.ACC, S1.MUTED, S1.INK, S1.NEAREST

# ---------------- timeline ----------------
T_ITEMS, T_TINDER, T_TOUCH, T_HOT, T_FIRE, T_TIP, T_INV = b(6), b(11), b(16), b(22), b(27), b(32), b(37)
T_CONTACT = b(19.0)
T_IGNITE = b(23.0)
T_UPD = [b(39), b(40.5), b(42)]      # battery, steel wool, granola
T_END, DURATION = b(45), b(56)
NFRAMES = int(round(DURATION * FPS))
DIALOG = [
    (0.0, T_ITEMS, "*Day* *3.* Tonight drops to *-15°C.* Ren has *no* *fire.*", False),
    (T_ITEMS, T_TINDER, "The lighter is *empty.* But the backpack has a *9V* *battery* and *steel* *wool.*", True),
    (T_TINDER, T_TOUCH, "First, *tinder:* dry cardboard torn into *thin* *strips.*", True),
    (T_TOUCH, T_HOT, "Fluff the steel wool. Touch *both* *terminals* to it.", True),
    (T_HOT, T_FIRE, "The thin wires *short* the battery and get *hot* enough to *burn.*", True),
    (T_FIRE, T_TIP, "Blow gently. *Fire.* Warmth, and now Ren can *boil* *water* too.", True),
    (T_TIP, T_INV, "*Pack* *tip:* keep the battery *away* from steel wool. It can start a fire *in* *your* *bag.*", True),
    (T_INV, T_END, "Day 3 survived. *Backpack* *updated.*", True),
    (T_END, b(50.5), "Which item saves *Ren* next? *Comment* *below.*", True),
    (b(50.5), DURATION + 1, "*Day* *4* next. Follow so *Ren* *survives.*", True),
]
CPS = 46

# ---------------- night world ----------------
YY, XX = S1.YY, S1.XX
rng = np.random.default_rng(33)
REN_X, REN_FEET = 104, 342
BK_X, BK_Y = 132, 340          # metal bucket top-left (18 x 14)
FX, FY = BK_X + 9, BK_Y + 2    # fire / mouth centre

def fire_level(t):
    return smooth(t, T_IGNITE, T_IGNITE + b(2.5)) * (0.75 + 0.25 * smooth(t, T_FIRE, T_FIRE + b(1)))

# steel wool blob on top of the tinder: per-pixel ignition times spreading from the contact point
WOOL = []
for y in range(BK_Y - 4, BK_Y + 1):
    for x in range(FX - 6, FX + 6):
        if ((x - FX) / 6.2) ** 2 + ((y - (BK_Y - 1.5)) / 2.8) ** 2 <= 1.0 and rng.uniform() < 0.92:
            d = math.hypot(x - (FX + 2), y - (BK_Y - 4))
            WOOL.append((x, y, T_CONTACT + d * 0.16 + rng.uniform(0, 0.25), rng.uniform(0, 6.28)))
CARD = [(FX - 7 + k * 2 + int(rng.integers(0, 2)), BK_Y + 1 - int(rng.integers(0, 2)), int(rng.integers(2, 4))) for k in range(8)]

def bucket(img):
    rows = [
        "kkkkkkkkkkkkkkkkkk",
        "kGgggggggggggggGGk",
        ".kMMMMMMMMMMMMMMk.",
        ".kMhMMMMMMMMMMMMk.",
        ".kMhMMMMMMMMMMMMk.",
        ".kMMMMMMMMMMMMMMk.",
        "..kMMMMMMMMMMMMk..",
        "..kMMMMMMMMMMMMk..",
        "..kMhMMMMMMMMMMk..",
        "..kMMMMMMMMMMMMk..",
        "...kMMMMMMMMMMk...",
        "...kMMMMMMMMMMk...",
        "...kkkkkkkkkkkk...",
    ]
    pal = {"k": hx("0a0b14"), "G": hx("6a7090"), "g": hx("8a90b0"), "M": hx("4a5070"), "h": hx("7a82a8")}
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != ".": img[BK_Y + y, BK_X + x] = pal[c]

def battery_pos(t):
    """9V battery sprite (5x8) descending to touch the wool, then lifting away."""
    if t < T_TOUCH + b(0.5) or t > T_HOT + b(1.5): return None
    u = smooth(t, T_TOUCH + b(0.5), T_CONTACT)
    up = smooth(t, T_CONTACT + b(2.2), T_CONTACT + b(3.2))
    y = BK_Y - 22 + 14 * u - 18 * up
    return FX + 1, int(round(y))

def draw_battery(img, p):
    x, y = p
    img[y:y + 8, x:x + 5] = hx("2b3150")
    img[y + 1:y + 3, x:x + 5] = hx("d9893a")
    img[y + 8, x + 1] = hx("c9cede"); img[y + 8, x + 3] = hx("c9cede")   # terminals at the bottom (it's held upside down)
    img[y:y + 8, x] = hx("0a0b14"); img[y:y + 8, x + 4] = hx("0a0b14")

def flames(img, t, lvl):
    if lvl <= 0: return
    for x in range(FX - 7, FX + 8):
        u = abs(x - FX) / 7.5
        h = lvl * (11 * (1 - u ** 1.6)) * (0.75 + 0.25 * math.sin(t * 13 + x * 1.7) + 0.15 * math.sin(t * 7.3 - x * 0.9))
        top = BK_Y + 1 - h
        for y in range(int(top), BK_Y + 2):
            v = (BK_Y + 1 - y) / max(1.0, h)
            col = hx("fff3c4") if v < 0.25 else (hx("ffc247") if v < 0.55 else (hx("ff7b2e") if v < 0.85 else hx("d0402a")))
            if 0 <= y < LH: img[y, x] = col
    # embers / sparks rising
    for k in range(int(6 * lvl)):
        ph = (t * 0.7 + k * 0.173) % 1
        ex = FX - 5 + (k * 37) % 11 + int(2 * math.sin(t * 3 + k))
        ey = int(BK_Y - 4 - ph * 34)
        if ph < 0.85 and 0 <= ey < LH: img[ey, ex] = hx("ffb347") if ph < 0.5 else hx("a8502a")

def city_night(img, t):
    rim = np.array([30, 70, 90], np.float32) * 0.3
    for layer, bls, col, edge in (("far", S1.FAR, hx("191e3c"), hx("222a52")), ("mid", S1.MID, hx("0f1229"), hx("1a2044"))):
        for bd in bls:
            x0, x1, top = max(0, bd["x"]), min(LW, bd["x"] + bd["w"]), bd["top"]
            img[top:S1.BASE_Y, x0:x1] = col
            img[top:S1.BASE_Y, x0:min(x1, x0 + 1)] = edge
            img[top, x0:x1] = np.array(hx("cfd8f0"), np.float32) * 0.55     # snow on dark roofs
        if layer == "mid":
            tx, tw, tt = S1.TOWER["x"], S1.TOWER["w"], S1.TOWER["top"]
            img[tt:S1.BASE_Y, tx:tx + tw] = hx("0d1026"); img[tt:S1.BASE_Y, tx:tx + 1] = hx("1a2044")
            img[tt - 18:tt - 3, tx + 5:tx + 6] = hx("1a2044")

SKY_Q = None
def world(t):
    img = S1.SKY.copy()
    img[:250] += S1.aurora(t + 40, 0.62)
    img = S1.quantize(np.clip(img, 0, 255))
    for x, y, br, ph in S1.STARS:
        v = br * (0.65 + 0.35 * math.sin(t * 2.1 + ph * 5))
        if v > 0.55: img[y, x] = np.maximum(img[y, x], np.array([200, 210, 255]) * v)
    city_night(img, t)
    a = S1.FG[..., 3:4] / 255.0
    img = img * (1 - a) + S1.FG[..., :3] * a
    # snow from Day 1 still on the roof
    cov = S1.SNOW_MASK < 0.9
    img[S1.PARAPET][cov[S1.PARAPET]] = hx("e9f0ff")
    img[S1.PARAPET + 1][(S1.SNOW_MASK[S1.PARAPET + 1] < 0.5)] = hx("b9c6e8")
    roof = (S1.SNOW_MASK < 0.07); roof[:S1.PARAPET + 10] = False
    img[roof] = hx("4a5478")
    img[350, 200:242][S1.SNOW_MASK[350, 200:242] < 0.9] = hx("e9f0ff")
    # bucket + tinder + wool
    bucket(img)
    if t >= T_TINDER + b(1):
        k = int(clamp((t - T_TINDER - b(1)) / b(3)) * len(CARD))
        for (cx, cy, ln) in CARD[:k]:
            img[cy - ln + 1:cy + 1, cx] = hx("b98a4a"); img[cy - ln + 1, cx] = hx("d8aa66")
    if t >= T_TOUCH:
        lvl = fire_level(t)
        for (x, y, ti, ph) in WOOL:
            if lvl > 0.6: continue                      # wool burned down into the tinder
            if t >= ti:
                g = 0.55 + 0.45 * math.sin(t * 18 + ph * 4)
                col = hx("fff3c4") if g > 0.85 else (hx("ffb347") if g > 0.45 else hx("e0602a"))
                img[y, x] = col
            else:
                img[y, x] = hx("9aa0b8") if ((x + y) % 3) else hx("6b7088")
        p = battery_pos(t)
        if p: draw_battery(img, p)
        # contact sparks
        if T_CONTACT <= t < T_CONTACT + 1.2:
            for k in range(10):
                ph = ((t - T_CONTACT) * 2.2 + k * 0.1) % 1
                ang = k * 0.63 + 0.3
                sx = int(FX + 3 + math.cos(ang) * ph * 14); sy = int(BK_Y - 4 - math.sin(ang) * ph * 10 + ph * ph * 8)
                if 0 <= sy < LH and 0 <= sx < LW: img[sy, sx] = hx("fff3c4") if ph < 0.4 else hx("ffb347")
    lvl = fire_level(t)
    flames(img, t, lvl)
    # Ren (shivers until the fire takes)
    fr = S1.REN_FRAMES[int(t / 0.22) % 2]
    bob = 1 if (t % 2.4) > 1.2 else 0
    shiver = (1 if int(t * 24) % 2 else -1) if t < T_TINDER else 0
    rx, ry = REN_X + shiver, REN_FEET - 32 + bob
    sa = fr[..., 3:4] / 255.0
    region = img[ry:ry + 32, rx:rx + 20]
    img[ry:ry + 32, rx:rx + 20] = region * (1 - sa) + fr[..., :3] * sa
    # warm light from the fire (also glows on the wool before the flames)
    wl = max(lvl, 0.35 * smooth(t, T_CONTACT, T_CONTACT + 1.0) * (1 - smooth(t, T_HOT + b(3), T_FIRE)))
    if wl > 0:
        fl = 0.85 + 0.15 * math.sin(t * 11) * math.sin(t * 5.3)
        d = np.hypot(XX - FX, (YY - FY) * 1.25)
        glow = np.clip(1 - d / (70 * (0.6 + 0.4 * wl)), 0, 1) ** 1.6 * wl * fl
        img = img + glow[..., None] * np.array([150, 80, 30], np.float32)
    # light snowfall
    for i, (x0, y0, v, ph, wob, size) in enumerate(S1.SNOWFLAKES[:120]):
        y = (y0 + v * t) % (LH + 20) - 10
        x = (x0 + 6 * t + 4 * math.sin(t * wob + ph)) % LW
        xi, yi = int(x), int(y)
        if 0 <= yi < LH - 1 and 0 <= xi < LW - 1: img[yi:yi + size, xi:xi + size] = hx("e9f0ff") if size == 2 else hx("9aa8d0")
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
        tab = "PART 3  DAY 3"
        ft = font(S1.TF_SILK, 24); tw_ = ft.measureText(tab)
        cv.drawRect(skia.Rect.MakeLTRB(x0 + 24, y0 - 22, x0 + 24 + tw_ + 28, y0 + 14), fillp(ACC))
        cv.drawString(tab, x0 + 38, y0 + 6, ft, fillp(INK))

def draw_title(cv, t):
    a = 1 - smooth(t, T_ITEMS - 0.25, T_ITEMS + 0.05)
    if a <= 0: return
    f = font(S1.TF_SILK, 192); s = "DAY 3"; w = f.measureText(s)
    shadow_text(cv, s, 540 - w / 2, 690, f, ACC, a, sh=10)

ICON = {it["key"]: skia.Image.fromarray(A.item_rgba(it), colorType=skia.kRGBA_8888_ColorType) for it in A.ITEMS}
def draw_items(cv, t):
    """lighter (empty, crossed out) vs battery + steel wool"""
    if not (T_ITEMS + 0.4 <= t < T_TINDER): return
    e = t - T_ITEMS - 0.4
    a = clamp(e / 0.2) * (1 - smooth(t, T_TINDER - 0.25, T_TINDER))
    pixel_box(cv, 90, 760, 990, 1260, a)
    fn = font(S1.TF_SILK_R, 28)
    for k, (key, name, ti) in enumerate([("lighter", "EMPTY", 0.0), ("battery", "9V BATTERY", 0.5), ("steelwool", "STEEL WOOL", 0.8)]):
        if e < ti: continue
        cx = 240 + k * 300
        sc = ease_back(clamp((e - ti) / 0.22), 2.4)
        cv.save(); cv.translate(cx, 960); cv.scale(sc, sc)
        p = skia.Paint(); p.setAlphaf(0.45 if key == "lighter" else 1.0)
        cv.drawImageRect(ICON[key], skia.Rect.MakeXYWH(-96, -96, 192, 192), NEAREST, p); cv.restore()
        shadow_text(cv, name, cx - fn.measureText(name) / 2, 1150, fn, MUTED if key == "lighter" else TXT, a, sh=3)
        if key == "lighter" and e > 0.3:
            for i in range(14):
                cv.drawRect(skia.Rect.MakeLTRB(cx - 84 + i * 12, 876 + i * 12, cx - 72 + i * 12, 888 + i * 12), fillp(hx("e0453a"), a))
    if e > 1.2:
        shadow_text(cv, "+", 540 - 22 + 150, 985, font(S1.TF_SILK, 72), ACC, a, sh=5)

def draw_tip(cv, t):
    if not (T_TIP + 0.4 <= t < T_INV): return
    e = t - T_TIP - 0.4
    a = clamp(e / 0.2) * (1 - smooth(t, T_INV - 0.25, T_INV))
    pixel_box(cv, 190, 880, 890, 1300, a, border=hx("e0453a"))
    for k, key in enumerate(["battery", "steelwool"]):
        cx = 370 + k * 340
        cv.drawImageRect(ICON[key], skia.Rect.MakeXYWH(cx - 80, 920, 160, 160), NEAREST)
    # red "keep apart" bars between them
    if (t * 3) % 1 < 0.75:
        for i in range(3):
            cv.drawRect(skia.Rect.MakeLTRB(520 + i * 0, 930 + i * 52, 560, 966 + i * 52), fillp(hx("e0453a"), a))
    f = font(S1.TF_SILK, 40)
    s = "PACK THEM APART"
    shadow_text(cv, s, 540 - f.measureText(s) / 2, 1200, f, hx("ff8a7a"), a, sh=4)

PX0, PY0, PX1, PY1 = S2.PX0, S2.PY0, S2.PX1, S2.PY1
GX0, GY0, SW, SH, GAPX, GAPY = S2.GX0, S2.GY0, S2.SW, S2.SH, S2.GAPX, S2.GAPY
ICONS = [skia.Image.fromarray(A.item_rgba(it), colorType=skia.kRGBA_8888_ColorType) for it in A.ITEMS]
BOTTLE_FULL = S2.BOTTLE_FULL
SUB_OLD = {it["key"]: it["sub"] for it in A.ITEMS}
SUB_OLD.update({"bottle": "full 1 l", "granola": "x2", "bags": "1 in use"})     # state after Day 2
SUB_NEW = {"battery": "low", "steelwool": "half pad", "granola": "x1"}
UPD_KEYS = ["battery", "steelwool", "granola"]

def draw_inventory(cv, t):
    if t < T_INV - 0.05: return
    e = t - T_INV
    off = (1 - ease_out(e / 0.42)) * 1500
    cv.save(); cv.translate(0, off)
    pixel_box(cv, PX0, PY0, PX1, PY1, fill=hx("0b0d1c"))
    fh = font(S1.TF_SILK, 40)
    shadow_text(cv, "REN'S BACKPACK", PX0 + 34, PY0 + 74, fh, TXT, sh=4)
    shadow_text(cv, "12/12", PX1 - 34 - fh.measureText("12/12"), PY0 + 74, fh, ACC, sh=4)
    u2 = smooth(t, T_UPD[2], T_UPD[2] + 0.4)
    labels = [("WATER", "1.0 L", 1.0, hx("3d8fe0")),
              ("FOOD", "1 BAR" if u2 > 0.5 else "2 BARS", 0.4 - 0.2 * u2, hx("3fa34d")),
              ("WINTER", "19 DAYS", 0.95 - 0.05 * smooth(t, T_INV + 0.4, T_INV + 1.2), hx("cfe8ff"))]
    fl, fv = font(S1.TF_SILK_R, 16), font(S1.TF_SILK, 24)
    for i, (lab, val, frac, col) in enumerate(labels):
        x0 = GX0 + i * (SW + GAPX); y0 = PY0 + 98
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + SW, y0 + 60), fillp(hx("171a33")))
        cv.drawString(lab, x0 + 12, y0 + 26, fl, fillp(MUTED))
        segs = 5; filled = frac * segs
        segw = (SW - 24 - 4 * 6) / segs
        for s_ in range(segs):
            sx = x0 + 12 + s_ * (segw + 6)
            cv.drawRect(skia.Rect.MakeLTRB(sx, y0 + 38, sx + segw, y0 + 50), fillp(col if s_ + 1 <= filled + 1e-6 else hx("2c3160")))
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
        base = hx("8a6a20") if (upd and t >= tu) else hx("3a4180")
        brd = tuple(int(v1 + (v2 - v1) * flash) for v1, v2 in zip(base, hx("ffffff")))
        for (l, tp, rr, bt) in ((x0, y0, x0 + SW, y0 + 4), (x0, y0 + SH - 4, x0 + SW, y0 + SH),
                                (x0, y0, x0 + 4, y0 + SH), (x0 + SW - 4, y0, x0 + SW, y0 + SH)):
            cv.drawRect(skia.Rect.MakeLTRB(l, tp, rr, bt), fillp(brd))
        cx, cy = x0 + SW / 2, y0 + 70
        sc = 1.0 + (0.25 * math.sin(math.pi * clamp((t - tu) / 0.3)) if upd and t >= tu else 0)
        icon = BOTTLE_FULL if key == "bottle" else ICONS[i]
        cv.save(); cv.translate(cx, cy); cv.scale(sc, sc)
        cv.drawImageRect(icon, skia.Rect.MakeXYWH(-48, -48, 96, 96), NEAREST); cv.restore()
        nm = it["name"]
        cv.drawString(nm, cx - fn.measureText(nm) / 2, y0 + SH - 18, fn, fillp(TXT))
        sub = SUB_NEW[key] if (upd and t >= tu) else SUB_OLD[key]
        if sub:
            sb = sub.upper()
            cv.drawString(sb, x0 + SW - 14 - fs.measureText(sb), y0 + 30, fs, fillp(hx("ff9e5e") if (upd and t >= tu) else ACC))
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
    if T_TINDER <= t < T_FIRE:
        return 12, FX, BK_Y - 12
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
    for tc in (T_TINDER, T_FIRE):
        if 0 <= t - tc < 0.12: cv.drawPaint(fillp(TXT, 0.45 * (1 - (t - tc) / 0.12)))
    if 0 <= t - T_CONTACT < 0.1: cv.drawPaint(fillp(hx("ffe9a8"), 0.35 * (1 - (t - T_CONTACT) / 0.1)))
    dim = 0.0
    if T_ITEMS + 0.4 <= t < T_TINDER: dim = ease_out((t - T_ITEMS - 0.4) / 0.3) * (1 - smooth(t, T_TINDER - 0.25, T_TINDER))
    if T_TIP + 0.4 <= t < T_INV: dim = ease_out((t - T_TIP - 0.4) / 0.3) * 0.7 * (1 - smooth(t, T_INV - 0.25, T_INV))
    if t >= T_INV: dim = ease_out((t - T_INV) / 0.3)
    if dim > 0: cv.drawPaint(fillp(hx("05060e"), 0.62 * dim))
    draw_title(cv, t)
    draw_items(cv, t)
    draw_tip(cv, t)
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
        print(f"duration {DURATION:.2f}s frames {NFRAMES}; contact {T_CONTACT:.2f} ignite {T_IGNITE:.2f} fire {T_FIRE:.2f} tip {T_TIP:.2f} inv {T_INV:.2f}")
    elif sys.argv[1] == "stills":
        from PIL import Image
        ims = []
        for s in sys.argv[2:]:
            arr = frame(float(s)).toarray(colorType=skia.kRGBA_8888_ColorType)
            ims.append(Image.fromarray(arr[..., :3]).resize((270, 480)))
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("/home/claude/v014_stills.jpg", quality=88)
    elif sys.argv[1] == "chunk":
        render_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
