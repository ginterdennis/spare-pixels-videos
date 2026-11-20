import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from sim import simulate, N, CELL, BOX
from art import grid, ROWS

SEED = 6
FR, REV, HITS, BORN = simulate(seed=SEED, v0=340, p_spawn=0.35, cap=18, rrev=20, T=19.5)
BORN[0] = 0.0
T_SWEEP = 19.5
ART = grid().astype(float)
# sweep: remaining cells reveal in a radial wave from the centre
cy, cx = np.mgrid[0:N, 0:N]
dist = np.hypot(cy - 11.5, cx - 11.5)
rem = np.isinf(REV)
REV[rem] = T_SWEEP + 0.15 + dist[rem] / dist.max() * 0.9
T_FULL = REV.max()
T_END = 27.5
DUR = T_END
X0, Y0 = (W - BOX) // 2, 470
rng = np.random.default_rng(3)
TILE = np.array((24, 28, 48), float)[None, None, :] + rng.normal(0, 3, (N, N, 1))
BALL_COLS = [WHITE, PINK, CYAN, GOLD]
BG = vgrad()

def coverage(t): return float(np.mean(REV <= t))

def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy())
    # ---------- grid
    age = t - REV
    revealed = age >= 0
    k = np.clip(age / 0.28, 0, 1)[..., None]
    k = 1 - (1 - k) ** 3
    flash = np.array((255, 255, 255), float)
    col = np.where(revealed[..., None], flash * (1 - k) + ART * k, TILE)
    pix = np.repeat(np.repeat(col, CELL, 0), CELL, 1)
    # gaps between cells close at the end
    g = 3 * (1 - ease((t - (T_FULL + 0.2)) / 0.7))
    if g > 0.05:
        yy = np.arange(BOX) % CELL
        gm = (yy < g)
        mask = gm[:, None] | gm[None, :]
        pix[mask] *= 0.45
    # end pulse scale
    sc = 1 + 0.035 * math.sin(math.pi * min(1, max(0, (t - T_FULL - 0.2) / 0.6)))
    gimg = Image.fromarray(np.clip(pix, 0, 255).astype(np.uint8))
    if sc != 1:
        s = int(BOX * sc); gimg = gimg.resize((s, s), Image.NEAREST)
        im.paste(gimg, ((W - s) // 2, Y0 + (BOX - s) // 2))
    else:
        im.paste(gimg, (X0, Y0))
    d = ImageDraw.Draw(im)
    # frame border
    d.rounded_rectangle((X0 - 10, Y0 - 10, X0 + BOX + 10, Y0 + BOX + 10), radius=14, outline=(60, 66, 104), width=3)
    # ---------- balls (fade out after sweep)
    ba = 1 - ease((t - T_SWEEP) / 0.6)
    if ba > 0:
        fi = min(i, len(FR) - 1)
        ov = Image.new("RGBA", (BOX + 120, BOX + 120), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        # wall-hit rings
        for (ht, hx, hy, bi) in HITS:
            a = t - ht
            if 0 <= a < 0.4:
                rr = 14 + a * 140
                al = int(170 * (1 - a / 0.4) * ba)
                c = BALL_COLS[bi % 4]
                od.ellipse((hx + 60 - rr, hy + 60 - rr, hx + 60 + rr, hy + 60 + rr), outline=c + (al,), width=4)
        # trails
        for lag in range(6, 0, -1):
            j = fi - lag
            if j < 0: continue
            for bi, (bx, by) in enumerate(FR[j]):
                if BORN[bi] > t - lag / FPS: continue
                r = 16 * (1 - lag / 8)
                al = int(110 * (1 - lag / 7) * ba)
                c = BALL_COLS[bi % 4]
                od.ellipse((bx + 60 - r, by + 60 - r, bx + 60 + r, by + 60 + r), fill=c + (al,))
        for bi, (bx, by) in enumerate(FR[fi]):
            if BORN[bi] > t: continue
            pop = 1.0 if BORN[bi] == 0 else ease_out((t - BORN[bi]) / 0.18)
            spr, R = glow_sprite(16, BALL_COLS[bi % 4])
            if pop < 1:
                s = max(2, int(2 * R * pop)); spr = spr.resize((s, s)); R2 = s // 2
            else: R2 = R
            if ba < 1:
                spr = spr.copy(); a_ = spr.getchannel("A").point(lambda v: int(v * ba)); spr.putalpha(a_)
            ov.alpha_composite(spr, (int(bx + 60 - R2), int(by + 60 - R2)))
        im.paste(ov, (X0 - 60, Y0 - 60), ov)
    # ---------- text
    end_out = ease((t - (T_FULL + 0.3)) / 0.25)
    end = ease((t - (T_FULL + 0.6)) / 0.35)
    fT = font("Inter-Black", 92); fS = font("Inter-Bold", 58)
    if end_out < 1:
        a = 1 - end_out
        c = lerpc(BG_TOP, WHITE, a)
        draw_rich(d, W / 2, 300, [("Guess the picture", c)], fT)
        cov = coverage(t)
        if cov < 0.40 or t < 8: sub = [("before the ", WHITE), ("balls", GOLD), (" finish", WHITE)]
        elif cov < 0.72: sub = [("Lock in your ", WHITE), ("guess", GOLD), (" now.", WHITE)]
        else: sub = [("Last ", WHITE), ("chance", PINK), ("...", WHITE)]
        sub = [(s, lerpc(BG_TOP, cc, a)) for s, cc in sub]
        draw_rich(d, W / 2, 392, sub, fS)
    if end > 0:
        c = lerpc(BG_TOP, WHITE, end); g_ = lerpc(BG_TOP, GOLD, end)
        draw_rich(d, W / 2, 300 + 20 * (1 - end), [("It's a ", c), ("fox.", g_)], font("Inter-Black", 104))
        draw_rich(d, W / 2, 392 + 20 * (1 - end), [("When did you guess it?", c)], fS)
    # ---------- HUD
    fl = font("Inter-SemiBold", 28); fn = font("Inter-Black", 76)
    cov = coverage(t)
    nb = sum(1 for b in BORN if b <= t)
    if end_out < 1:
        a = 1 - end_out
        label(d, 330, 1440, "REVEALED", fl, lerpc(BG_BOT, MUTED, a), spacing=5)
        label(d, 750, 1440, "BALLS", fl, lerpc(BG_BOT, MUTED, a), spacing=5)
        draw_rich(d, 330, 1530, [(f"{cov*100:.0f}%", lerpc(BG_BOT, WHITE, a))], fn)
        draw_rich(d, 750, 1530, [(f"{max(nb, 0)}", lerpc(BG_BOT, WHITE, a))], fn)
    if end > 0:
        draw_rich(d, W / 2, 1470, [("Comment the ", lerpc(BG_BOT, WHITE, end)), ("%", lerpc(BG_BOT, GOLD, end)), (" you got it at", lerpc(BG_BOT, WHITE, end))], font("Inter-Bold", 54))
    return im

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "stills":
        for t in [0.0, 5.0, 12.5, 17.0, 20.1, 23.0]:
            frame(int(t * FPS)).save(f"still_{t:04.1f}.png")
        print("T_FULL", T_FULL, "cov@12.5", coverage(12.5))
    else:
        w = Writer("v004_video.mp4")
        for i in range(int(DUR * FPS)):
            w.write(frame(i))
        w.close(); print("frames", w.n)
