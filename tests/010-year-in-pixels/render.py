import sys, math, datetime as dt
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

YEAR = 2026
DAYS = [dt.date(YEAR, 1, 1) + dt.timedelta(days=i) for i in range(365)]
TODAY = dt.date(YEAR, 11, 20)
NT = (TODAY - dt.date(YEAR, 1, 1)).days + 1          # 324 lit incl. today
LEFT = 365 - NT                                       # 41
assert NT == 324 and LEFT == 41
MC = ["#8EC5FF", "#A9B8FF", "#8FE3B0", "#6FD68A", "#B6E36A", "#FFE066", "#FFC247", "#FF9F40", "#FF7B4A", "#E85D5D", "#C85BD0", "#8B6CFF"]
MC = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in MC]
COLS, CELL, GAP = 19, 50, 7
GX0 = (W - COLS * CELL) / 2; GY0 = 375
T_FILL0, T_FILL1 = 0.3, 8.6
def f(u): return 0.5 - 0.5 * math.cos(math.pi * u) if u < 0.85 else None
def lit_time(d):  # d: 1..NT
    u = d / NT
    # slow start, fast middle, slow last stretch
    w = (1 - math.cos(math.pi * u)) / 2
    w = 0.65 * w + 0.35 * u ** 3 * 0 + 0.35 * u
    return T_FILL0 + (T_FILL1 - T_FILL0) * (0.6 * u + 0.4 * (1 - math.cos(math.pi * u)) / 2)
LT = [lit_time(d) for d in range(1, NT + 1)]
LT[0] = -0.2
T_TODAY = LT[-1]
T_LEFT = T_TODAY + 1.6
T_STATS = T_LEFT + 2.4
T_CTA = T_STATS + 3.0
DUR = T_CTA + 4.2
BG = vgrad()

def cell_xy(i):
    r, c = divmod(i, COLS)
    return GX0 + c * CELL + CELL / 2, GY0 + r * CELL + CELL / 2

def pop(t, t0, d=0.16):
    u = (t - t0) / d
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return 1 + 0.3 * math.sin(math.pi * u) * (1 - u) - (1 - u) ** 3

def current_index(t):
    return sum(1 for x in LT if x <= t)

def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    d = ImageDraw.Draw(im)
    n_lit = current_index(t)
    pul = 0.5 + 0.5 * math.sin(t * 6)
    shimmer_on = t >= T_LEFT
    for k in range(365):
        x, y = cell_xy(k)
        h = (CELL - GAP) / 2
        if k < NT:
            s = pop(t, LT[k])
            # always draw the empty slot underneath
            d.rounded_rectangle((x - h, y - h, x + h, y + h), radius=7, outline=(46, 52, 84), width=2, fill=(18, 21, 40))
            if s > 0:
                c = MC[DAYS[k].month - 1]
                if k == NT - 1: c = GOLD
                hs = h * s
                d.rounded_rectangle((x - hs, y - hs, x + hs, y + hs), radius=7, fill=c)
        else:
            oc = (46, 52, 84)
            if shimmer_on:
                a = ease((t - T_LEFT - (k - NT) * 0.03) / 0.25)
                wave = 0.5 + 0.5 * math.sin(t * 3 - (k - NT) * 0.35)
                oc = lerpc((46, 52, 84), lerpc((150, 160, 220), WHITE, wave), a)
            d.rounded_rectangle((x - h, y - h, x + h, y + h), radius=7, outline=oc, width=3 if shimmer_on else 2, fill=(18, 21, 40))
    # today glow
    if t >= T_TODAY:
        x, y = cell_xy(NT - 1)
        spr, R = glow_sprite(int(CELL * 0.5), GOLD, glow=2.4, alpha=0.6 + 0.3 * pul)
        im.alpha_composite(spr, (int(x - R), int(y - R)))
        d.rounded_rectangle((x - CELL / 2 + 3, y - CELL / 2 + 3, x + CELL / 2 - 3, y + CELL / 2 - 3), radius=7, fill=GOLD)
        rr = CELL * (0.75 + 0.15 * pul)
        d.rounded_rectangle((x - rr, y - rr, x + rr, y + rr), radius=12, outline=GOLD + (220,), width=4)
    # ---------- text
    fT = font("Inter-Black", 88); fS = font("Inter-Bold", 52)
    def win(t0, t1, fi=0.3, fo=0.3): return ease((t - t0) / fi) * (1 - ease((t - t1) / fo))
    a = win(-1, T_TODAY + 0.1)
    if a > 0:
        draw_rich(d, W / 2, 205, [("2026", lerpc(BG_TOP, GOLD, a)), (" in 365 pixels", lerpc(BG_TOP, WHITE, a))], fT)
        day = DAYS[max(0, min(NT, n_lit) - 1)]
        draw_rich(d, W / 2, 295, [(day.strftime("%b %-d").upper() if n_lit else "JAN 1", lerpc(BG_TOP, WHITE, a)), (f"   ·   DAY {max(1, n_lit)}", lerpc(BG_TOP, MUTED, a))], fS)
    a = win(T_TODAY + 0.35, T_LEFT - 0.05)
    if a > 0:
        draw_rich(d, W / 2, 205, [("This pixel is ", lerpc(BG_TOP, WHITE, a)), ("today.", lerpc(BG_TOP, GOLD, a))], fT)
        draw_rich(d, W / 2, 295, [("NOV 20   ·   DAY 324", lerpc(BG_TOP, MUTED, a))], fS)
    a = win(T_LEFT + 0.1, 99)
    if a > 0:
        draw_rich(d, W / 2, 205, [("41 pixels ", lerpc(BG_TOP, WHITE, a)), ("left.", lerpc(BG_TOP, PINK, a))], fT)
        draw_rich(d, W / 2, 295, [("Make them count.", lerpc(BG_TOP, MUTED, a))], fS)
    # stats under the grid
    a = win(T_STATS, T_CTA - 0.1)
    if a > 0:
        fl = font("Inter-SemiBold", 28); fn = font("Inter-Black", 66)
        for k, (lab, val) in enumerate([("DAYS", "41"), ("HOURS", "984"), ("MINUTES", "59,040")]):
            cx = W / 2 + (k - 1) * 320
            label(d, cx, 1450, lab, fl, lerpc(BG_BOT, MUTED, a), spacing=5)
            draw_rich(d, cx, 1528, [(val, lerpc(BG_BOT, WHITE, a))], fn)
    a = win(T_CTA, 99)
    if a > 0:
        draw_rich(d, W / 2, 1455, [("One more lights up every day.", lerpc(BG_BOT, WHITE, a))], font("Inter-Bold", 50))
        draw_rich(d, W / 2, 1530, [("Follow to watch 2026 ", lerpc(BG_BOT, WHITE, a)), ("run out.", lerpc(BG_BOT, GOLD, a))], font("Inter-Black", 56))
    return im.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ts = [0.0, 4.0, T_TODAY + 0.8, T_LEFT + 1.5, T_STATS + 1, T_CTA + 1.5]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88); print("DUR", DUR, "T_TODAY", T_TODAY)
    else:
        w = Writer("v010_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
