"""016: Get 1 euro every second. Millionaire in under 12 days (11.6), billionaire in 31 years 8 months,
trillion in 31,688 years. 1 pixel = 1 day, then 1 tile = 1 billion seconds (31.7 years)."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

DUR = 21.0
# ---- timeline (seconds) ----
T_GRID = 1.9          # coin hands over to the day grid
T_M0, T_M1 = 2.2, 4.3  # million: 11.574 cells fill
T_Z0, T_Z1 = 4.7, 6.4  # zoom out to the full billion grid
T_B1 = 9.0            # billion grid full
T_BR = 9.0            # billion reveal
T_S0, T_S1 = 10.9, 12.3  # block shrinks into tile 0
T_T1 = 15.4           # 1000 tiles full
T_TR = 15.5           # trillion reveal
T_CTA = 17.4

DAY = 86400
CELLS_M = 1e6 / DAY            # 11.574
CELLS_B = 1e9 / DAY            # 11574.07
GC = 108                       # billion grid columns/rows (108*108 = 11664 >= 11574)
TG = 32                        # trillion tile grid 32x32 (1000 used)
AREA = 832                     # grid area size in px
AX, AY = (W - AREA) // 2, 560  # grid area top-left
CX, CY = AX + AREA / 2, AY + AREA / 2
EMPTY = (28, 32, 58)
GOLD2 = (222, 170, 64)

BG = vgrad()
YY, XX = np.mgrid[AY:AY + AREA, AX:AX + AREA].astype(np.float32)


def fit(txt, name, size, maxw):
    f = font(name, size)
    while f.getlength(txt) > maxw and size > 20:
        size -= 2; f = font(name, size)
    return f


def cells_filled(t):
    """number of day-cells filled (float) at time t."""
    if t < T_M0: return 0.0
    if t < T_M1:
        return CELLS_M * ease_out((t - T_M0) / (T_M1 - T_M0), 1.6)
    if t < T_Z0 + 0.4: return CELLS_M
    # accelerate from million to billion
    u = min(1, (t - (T_Z0 + 0.4)) / (T_B1 - (T_Z0 + 0.4)))
    return CELLS_M * (CELLS_B / CELLS_M) ** (u ** 0.7)


def tiles_filled(t):
    if t < T_S1: return 1.0
    u = min(1, (t - T_S1) / (T_T1 - T_S1))
    return 1 + 999 * (u ** 1.8)


def grid_scale(t):
    """px per day-cell and screen pos of cell (0,0)."""
    s0, s1 = 64.0, AREA / GC
    # million view: 12 cells in a row, centred
    o0 = (CX - 6 * s0, CY - s0 / 2)
    o1 = (AX, AY)
    u = ease((t - T_Z0) / (T_Z1 - T_Z0)) if t > T_Z0 else 0
    s = s0 * (s1 / s0) ** u
    # anchor: world point lerps from (6, .5) to (54, 54) and is shown at screen centre
    ax, ay = lerp(6, GC / 2, u), lerp(0.5, GC / 2, u)
    return s, (CX - ax * s, CY - ay * s)


def draw_cells(img, s, ox, oy, nfill, alpha=1.0, solid_below=2.2):
    """img: float array (AREA,AREA,3) of the grid area. Draw the 108x108 day grid."""
    if s < solid_below:
        x0, y0 = int(round(ox - AX)), int(round(oy - AY))
        sz = max(1, int(round(GC * s)))
        img[max(0, y0):y0 + sz, max(0, x0):x0 + sz] = GOLD
        return
    cx = (XX - ox) / s; cy = (YY - oy) / s
    col = np.floor(cx); row = np.floor(cy)
    inside = (col >= 0) & (col < GC) & (row >= 0) & (row < GC)
    idx = row * GC + col
    inside &= idx < math.ceil(CELLS_B)
    gap = max(1.0, s * 0.10) if s >= 3.5 else 0.0
    fx = (cx - col) * s; fy = (cy - row) * s
    body = inside & (fx >= gap / 2) & (fx < s - gap / 2) & (fy >= gap / 2) & (fy < s - gap / 2)
    full = body & (idx < np.floor(nfill))
    part = body & (idx == np.floor(nfill)) & ((cx - col) < (nfill - np.floor(nfill)))
    year = np.floor(idx / 365.25)
    col_a = np.where((year % 2 == 0)[..., None], np.array(GOLD, np.float32), np.array(GOLD2, np.float32))
    empty = body & ~(full | part)
    img[empty] = img[empty] * (1 - alpha) + np.array(EMPTY, np.float32) * alpha
    on = full | part
    img[on] = img[on] * (1 - alpha) + col_a[on] * alpha


def coin(im, cx, cy, r, phase, alpha):
    """pixel-art gold coin with a spin (horizontal squash)."""
    if alpha <= 0: return
    P = 12
    n = int(2 * r / P)
    sq = 0.78 + 0.22 * math.cos(phase)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for j in range(n):
        for i in range(n):
            x = (i + 0.5) / n * 2 - 1; y = (j + 0.5) / n * 2 - 1
            rr = x * x + y * y
            if rr > 1: continue
            c = GOLD if rr < 0.62 else (226, 160, 46)
            if rr < 0.62 and (x + y) < -0.75: c = (255, 236, 170)
            if 0.62 <= rr < 0.72: c = (255, 226, 140)
            px = cx + (i - n / 2) * P * sq
            d.rectangle((px, cy + (j - n / 2) * P, px + max(1, P * sq) - 1, cy + (j - n / 2 + 1) * P - 1),
                        fill=c + (int(255 * alpha),))
    if sq > 0.35:
        f = font("Inter-Black", int(r * 0.9))
        tw = f.getlength("€1")
        txt = Image.new("RGBA", (int(tw) + 20, int(r * 1.2)), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((10, r * 0.95), "€1", font=f, fill=(140, 86, 10, int(255 * alpha)), anchor="ls")
        txt = txt.resize((max(1, int(txt.width * sq)), txt.height))
        ov.alpha_composite(txt, (int(cx - txt.width / 2), int(cy - r * 0.58)))
    im.alpha_composite(ov)


def money(v):
    return "€" + f"{int(round(v)):,}"


def text_block(d, lines, y0, alpha=1.0):
    """lines: list of (parts, font, dy). Centered."""
    y = y0
    for parts, f, dy in lines:
        y += dy
        draw_rich(d, W / 2, y, [(t, c + (int(255 * alpha),)) for t, c in parts], f)


def frame(i):
    t = i / FPS
    base = BG.copy().astype(np.float32)
    area = base[AY:AY + AREA, AX:AX + AREA]

    # ---------------- grid
    g_alpha = ease((t - T_GRID) / 0.35)
    if g_alpha > 0 and t < T_S0:
        s, (ox, oy) = grid_scale(t)
        draw_cells(area, s, ox, oy, cells_filled(t), g_alpha)
    elif t >= T_S0:
        # trillion: tile grid; tile 0 is the shrinking billion block
        pitch = AREA / TG; tsz = pitch - 2
        u = ease((t - T_S0) / (T_S1 - T_S0))
        bs = (AREA / GC) * (tsz / AREA) ** u        # px per day cell of the block
        tile_a = ease((t - T_S0 - 0.1) / 0.6)
        nt = tiles_filled(t)
        if tile_a > 0:
            for k in range(1, 1000):
                r, c = divmod(k, TG)
                x0, y0 = int(c * pitch), int(r * pitch)
                col = GOLD if k < nt else EMPTY
                if k % 32 in (0,) and k < nt: col = GOLD
                cur = area[y0:y0 + int(tsz), x0:x0 + int(tsz)]
                cur[:] = cur * (1 - tile_a) + np.array(col, np.float32) * tile_a
        draw_cells(area, bs, AX, AY, CELLS_B, 1.0)

    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)

    # ---------------- coin (hook)
    c_a = 1 - ease((t - T_GRID) / 0.3)
    if c_a > 0:
        coin(im, W / 2, CY + 20, 190, t * 5.0, c_a)
        d = ImageDraw.Draw(im)

    # ---------------- header text
    fH = font("Inter-Black", 100); fM = font("Inter-Bold", 54); fL = font("Inter-Bold", 30)
    if t < T_Z0:
        a = 1.0
        label(d, W / 2, 262, "IF YOU GOT", fL, MUTED + (255,), spacing=6)
        draw_rich(d, W / 2, 372, [("€1 every second", GOLD)], fit("€1 every second", "Inter-Black", 100, 960))
        draw_rich(d, W / 2, 452, [("Millionaire in under 12 days.", WHITE)], fM)
        draw_rich(d, W / 2, 522, [("Billionaire in ", WHITE), ("...?", PINK)], fM)
    elif t < T_S0:
        label(d, W / 2, 262, "BILLIONAIRE IN", fL, MUTED + (255,), spacing=6)
        ra = ease((t - T_BR) / 0.35)
        if ra <= 0:
            yrs = cells_filled(t) / 365.25
            if yrs < 1:
                draw_rich(d, W / 2, 380, [("...?", PINK)], fH)
            else:
                draw_rich(d, W / 2, 380, [(f"{int(yrs)} year{'s' if int(yrs) > 1 else ''}", WHITE)], fH)
        else:
            sc = 1 + 0.12 * (1 - ease_out((t - T_BR) / 0.4))
            f = font("Inter-Black", int(92 * sc))
            draw_rich(d, W / 2, 380, [("31 years, 8 months", GOLD)], fit("31 years, 8 months", "Inter-Black", int(92 * sc), 1000))
            draw_rich(d, W / 2, 470, [("Start at 18. ", WHITE), ("Billionaire at 49.", GOLD)], fM)
    else:
        label(d, W / 2, 262, "AND A TRILLION?", fL, MUTED + (255,), spacing=6)
        ra = ease((t - T_TR) / 0.35)
        if ra <= 0:
            yrs = tiles_filled(t) * 31.688 if t > T_S1 else 31.7
            draw_rich(d, W / 2, 380, [(f"{int(yrs):,} years", WHITE)], fH)
        else:
            draw_rich(d, W / 2, 380, [("31,688 years", GOLD)], fH)
            draw_rich(d, W / 2, 462, [("Start when mammoths", WHITE)], fM)
            draw_rich(d, W / 2, 530, [("still roamed Europe.", WHITE)], fM)

    # ---------------- scale legend under the grid
    fS = font("Inter-Bold", 30)
    if T_GRID + 0.2 < t < T_S0:
        la = ease((t - T_GRID - 0.2) / 0.3)
        label(d, W / 2, AY + AREA + 52, "1 PIXEL = 1 DAY", fS, MUTED + (int(255 * la),), spacing=5)
    elif t >= T_S0 + 0.6:
        la = ease((t - T_S0 - 0.6) / 0.3)
        label(d, W / 2, AY + AREA + 52, "1 SQUARE = 1 BILLION SECONDS = 31.7 YEARS", fit("1 SQUARE = 1 BILLION SECONDS = 31.7 YEARS", "Inter-Bold", 30, 940),
              MUTED + (int(255 * la),), spacing=3)
    # million label next to the row
    if T_M1 - 0.1 < t < T_Z0 + 0.3:
        la = ease((t - T_M1 + 0.1) / 0.3) * (1 - ease((t - T_Z0) / 0.3))
        draw_rich(d, W / 2, CY + 110, [("11.6 days", WHITE + (int(255 * la),))], font("Inter-Black", 64))

    # ---------------- money counter
    if t >= T_GRID:
        if t < T_S0:
            v = min(1e9, cells_filled(t) * DAY)
        else:
            v = min(1e12, tiles_filled(t) * 1e9) if t >= T_S1 else 1e9
        txt = money(v)
        f = fit(txt, "Inter-Black", 104, 980)
        hit = (abs(t - T_M1) < 0.25) or (abs(t - T_B1) < 0.25) or (abs(t - T_T1) < 0.25)
        draw_rich(d, W / 2, AY + AREA + 160, [(txt, GOLD if hit or v >= 1e6 else WHITE)], f)

    # ---------------- CTA
    if t >= T_CTA:
        a = ease((t - T_CTA) / 0.4)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 760, W - 70, 1160), radius=40, fill=(8, 9, 20, int(225 * a)))
        f1 = font("Inter-Black", 66)
        draw_rich(od, W / 2, 880, [("How old would you be", WHITE + (int(255 * a),))], f1)
        draw_rich(od, W / 2, 965, [("at your first billion?", GOLD + (int(255 * a),))], f1)
        draw_rich(od, W / 2, 1075, [("Comment it below", MUTED + (int(255 * a),))], font("Inter-Bold", 48))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 3.4, 5.5, 8.0, 9.6, 11.6, 14.0, 16.5, 19.5]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v016_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
