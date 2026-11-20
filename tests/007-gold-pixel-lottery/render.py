import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *

TOTAL = 139_838_160
SW, SH, GAP = 1080, 1920, 180
COLS, ROWS = 10, 7
PER = SW * SH
NFULL = TOTAL // PER            # 67
REM = TOTAL - NFULL * PER       # 906,960
GOLD_K = 23; GLX, GLY = 650, 1060
gk_c, gk_r = GOLD_K % COLS, GOLD_K // COLS
GX = gk_c * (SW + GAP) + GLX; GY = gk_r * (SH + GAP) + GLY
GRID_W = COLS * SW + (COLS - 1) * GAP; GRID_H = ROWS * SH + (ROWS - 1) * GAP
Z0, ZF = 240.0, 0.075
A_END, B_END, C_END, D_END = 2.6, 11.0, 13.6, 21.0
DUR = 30.0
SCR_CX = gk_c * (SW + GAP) + SW / 2; SCR_CY = gk_r * (SH + GAP) + SH / 2
BGC = np.array(BG_BOT, np.uint8)
C1 = np.array((30, 36, 64), float); C2 = np.array((48, 56, 96), float)

def cam(t):
    """returns Z, world centre (cx, cy), screen anchor (ax, ay)"""
    if t < A_END:
        return Z0, (GX + 0.5, GY + 0.5), (540, 960)
    if t < B_END:
        u = ease((t - A_END) / (B_END - A_END))
        lz = math.log(Z0) * (1 - u)
        Z = math.exp(lz)
        f = 1 - lz / math.log(Z0)
        f = ease(f)
        return Z, (lerp(GX + 0.5, SCR_CX, f), lerp(GY + 0.5, SCR_CY, f)), (540, 960)
    if t < C_END:
        return 1.0, (SCR_CX, SCR_CY), (540, 960)
    u = ease((t - C_END) / (D_END - C_END))
    Z = math.exp(math.log(ZF) * u)
    f = ease(min(1, u * 1.3))
    return Z, (lerp(SCR_CX, GRID_W / 2, f), lerp(SCR_CY, GRID_H / 2, f)), (540, lerp(960, 930, f))

def hashv(tx, ty, k):
    h = (tx * 73856093) ^ (ty * 19349663) ^ (k * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h >> 7) & 1023) / 1023.0

def field_numpy(Z, C, A):
    xs = np.arange(W); ys = np.arange(H)
    wx = C[0] + (xs - A[0]) / Z; wy = C[1] + (ys - A[1]) / Z
    cc = np.floor(wx / (SW + GAP)).astype(np.int64); lx = wx - cc * (SW + GAP)
    rr = np.floor(wy / (SH + GAP)).astype(np.int64); ly = wy - rr * (SH + GAP)
    inx = (lx >= 0) & (lx < SW) & (cc >= 0) & (cc < COLS)
    iny = (ly >= 0) & (ly < SH) & (rr >= 0) & (rr < ROWS)
    tx = np.floor(lx).astype(np.int64); ty = np.floor(ly).astype(np.int64)
    K = rr[:, None] * COLS + cc[None, :]
    inside = iny[:, None] & inx[None, :] & (K <= NFULL)
    idx_in_screen = ty[:, None] * SW + tx[None, :]
    inside &= ~((K == NFULL) & (idx_in_screen >= REM))
    v = hashv(tx[None, :], ty[:, None], K)
    col = C1[None, None, :] * (1 - v[..., None]) + C2[None, None, :] * v[..., None]
    if Z >= 6:
        g = min(0.12, 2.0 / Z) if Z < 40 else 0.06
        fx = lx - tx; fy = ly - ty
        edge = (fx < g)[None, :] | (fx > 1 - g)[None, :] | (fy < g)[:, None] | (fy > 1 - g)[:, None]
        col = np.where(edge[..., None], col * 0.35, col)
    # gold ticket
    gold = (tx[None, :] + cc[None, :] * 0 == GLX) & (ty[:, None] == GLY) & (K == GOLD_K)
    col = np.where(gold[..., None], np.array(GOLD, float), col)
    out = np.where(inside[..., None], col, BGC.astype(float))
    return out.astype(np.uint8)

# texture of one full screen at Z=1 and the partial screen
_yy, _xx = np.mgrid[0:SH, 0:SW]
def screen_tex(k):
    v = hashv(_xx, _yy, k)
    col = (C1 * (1 - v[..., None]) + C2 * v[..., None])
    if k == NFULL:
        idx = _yy * SW + _xx
        col[idx >= REM] = BGC
    return Image.fromarray(col.astype(np.uint8))
TEX = screen_tex(5); TEXP = screen_tex(NFULL)

def field_tiles(Z, C, A):
    im = Image.new("RGB", (W, H), BG_BOT)
    tw, th = max(1, round(SW * Z)), max(1, round(SH * Z))
    t_full = TEX.resize((tw, th), Image.BOX)
    t_part = TEXP.resize((tw, th), Image.BOX)
    d = ImageDraw.Draw(im)
    for k in range(NFULL + 1):
        c, r = k % COLS, k // COLS
        x0 = A[0] + (c * (SW + GAP) - C[0]) * Z; y0 = A[1] + (r * (SH + GAP) - C[1]) * Z
        if x0 > W or y0 > H or x0 + tw < 0 or y0 + th < 0: continue
        im.paste(t_part if k == NFULL else t_full, (int(round(x0)), int(round(y0))))
        if Z < 0.6:
            d.rounded_rectangle((x0 - 2, y0 - 2, x0 + tw + 2, y0 + th + 2), radius=max(2, int(60 * Z)), outline=(80, 90, 140), width=2)
    return im

def count_at(t):
    Z, _, _ = cam(t)
    if t < C_END:
        return min(PER, (1080 / Z) * (1920 / Z))
    u = ease((t - C_END) / (D_END - C_END))
    return math.exp(math.log(PER) + (math.log(TOTAL) - math.log(PER)) * u)

def shade(im):
    a = np.asarray(im).astype(float)
    g = np.ones(H)
    g[:560] = np.linspace(0.12, 1, 560) ** 1.4
    g[-560:] = np.linspace(1, 0.4, 560)
    return Image.fromarray((a * g[:, None, None]).astype(np.uint8))

def frame(i):
    t = i / FPS
    Z, C, A = cam(t)
    im = Image.fromarray(field_numpy(Z, C, A)) if Z >= 0.999 else field_tiles(Z, C, A)
    im = shade(im).convert("RGBA")
    d = ImageDraw.Draw(im)
    # gold glow marker
    sx = A[0] + (GX + 0.5 - C[0]) * Z; sy = A[1] + (GY + 0.5 - C[1]) * Z
    pul = 0.5 + 0.5 * math.sin(t * 5)
    if Z < 60:
        R = 10 + 4 * pul
        spr, Rr = glow_sprite(int(R), GOLD, glow=3.2, alpha=0.8)
        im.alpha_composite(spr, (int(sx - Rr), int(sy - Rr)))
    if Z < 3:
        rr = 34 + 10 * pul
        d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=GOLD + (200,), width=4)
    # phase C border = edges of one phone screen
    if Z <= 1.0 and t < D_END:
        a = ease((t - B_END) / 0.4) * (1 - ease((t - C_END - 1.6) / 0.8))
        if a > 0:
            x0 = A[0] + (gk_c * (SW + GAP) - C[0]) * Z; y0 = A[1] + (gk_r * (SH + GAP) - C[1]) * Z
            d.rounded_rectangle((x0 + 6, y0 + 6, x0 + SW * Z - 6, y0 + SH * Z - 6), radius=int(60 * Z) + 4, outline=WHITE + (int(220 * a),), width=6)
    # ---------- text
    fT = font("Inter-Black", 84); fS = font("Inter-Bold", 52)
    def two(l1, l2, a, y=250, c2=WHITE):
        draw_rich(d, W / 2, y, [(s, cc + (int(255 * a),)) for s, cc in l1], fT)
        draw_rich(d, W / 2, y + 96, [(s, cc + (int(255 * a),)) for s, cc in l2], fT)
    def win(t0, t1, fi=0.3, fo=0.3):
        return ease((t - t0) / fi) * (1 - ease((t - t1) / fo))
    a = win(-1, A_END + 0.4)
    if a > 0: two([("This ", WHITE), ("gold pixel", GOLD)], [("is your lottery ticket.", WHITE)], a)
    a = win(A_END + 0.7, B_END - 0.3)
    if a > 0: two([("Every other pixel", WHITE)], [("is a ", WHITE), ("losing", PINK), (" ticket.", WHITE)], a)
    a = win(B_END, C_END + 2.2)
    if a > 0: two([("One phone screen =", WHITE)], [("2,073,600 tickets.", GOLD)], a)
    a = win(C_END + 2.6, D_END + 0.2)
    if a > 0: two([("The jackpot needs", WHITE)], [("67.4", GOLD), (" screens of them.", WHITE)], a)
    a = win(D_END + 0.5, 99)
    if a > 0:
        draw_rich(d, W / 2, 230, [("Your odds: ", WHITE + (int(255 * a),))], fS)
        draw_rich(d, W / 2, 335, [("1 in 139,838,160", GOLD + (int(255 * a),))], font("Inter-Black", 96))
    # ---------- HUD
    n = count_at(t)
    fl = font("Inter-SemiBold", 28); fn = font("Inter-Black", 64)
    hud_a = 1 - ease((t - (D_END + 2.6)) / 0.4)
    if hud_a > 0:
        label(d, 330, 1590, "TICKETS", fl, MUTED + (int(255 * hud_a),), spacing=5)
        label(d, 760, 1590, "SCREENS", fl, MUTED + (int(255 * hud_a),), spacing=5)
        draw_rich(d, 330, 1670, [(f"{int(round(n)):,}", WHITE + (int(255 * hud_a),))], fn)
        draw_rich(d, 760, 1670, [(f"{n / PER:.1f}" if n >= PER * 0.95 else f"{n / PER:.3f}" if n > 20000 else "–", WHITE + (int(255 * hud_a),))], fn)
    a = ease((t - (D_END + 3.0)) / 0.4)
    if a > 0:
        draw_rich(d, W / 2, 1580, [("EuroMillions · Eurojackpot · Lotto 6aus49", MUTED + (int(255 * a),))], font("Inter-SemiBold", 34))
        draw_rich(d, W / 2, 1660, [("Would you still play? ", WHITE + (int(255 * a),)), ("Comment.", GOLD + (int(255 * a),))], font("Inter-Black", 56))
    return im.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ts = [0.0, 5.0, 9.0, 12.0, 17.0, 26.0]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v007_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
