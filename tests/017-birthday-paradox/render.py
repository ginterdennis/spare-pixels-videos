"""017: Birthday paradox. 23 people -> 50.7% that two share a birthday; 253 pairs; 70 people -> 99.9%.
Birthdays are drawn at random (seed 31, uniform over 365 days) and dropped into a pixel calendar."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *

DUR = 22.5
SEED = 31
MDAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MNAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MLET = "JFMAMJJASOND"
CUM = np.cumsum([0] + MDAYS)

BDAY = np.random.default_rng(SEED).integers(0, 365, 70)        # day-of-year 0..364


def md(doy):
    m = int(np.searchsorted(CUM, doy, side="right") - 1)
    return m, int(doy - CUM[m]) + 1


def P(n):
    p = 1.0
    for k in range(n): p *= (365 - k) / 365
    return 1 - p


# ---- timeline
T_P0, T_P23 = 0.2, 7.4            # people 1..23 arrive
T_WHY, T_LINES0, T_LINES1, T_BACK = 8.6, 9.3, 12.0, 13.4
T_P24, T_P70 = 13.8, 17.6          # people 24..70
T_CTA = 19.2
FALL = 0.22


def arrival(k):
    """arrival time of person k (0-based)."""
    if k < 23:
        u = k / 22
        return T_P0 + (T_P23 - T_P0) * (u ** 0.78)
    u = (k - 23) / 46
    return T_P24 + (T_P70 - T_P24) * (u ** 0.85)


ARR = [arrival(k) for k in range(70)]
# first time each person creates a match
MATCH_AT = {}
seen = {}
for k, b in enumerate(BDAY):
    b = int(b)
    if b in seen:
        MATCH_AT[k] = seen[b]
    else:
        seen[b] = k
FIRST = min(MATCH_AT)                  # 0-based index of first matching person (20 -> person 21)
T_MATCH = ARR[FIRST] + FALL
# time at which each person's cell turns pink (when they, or a later person, complete a match)
MT = [1e9] * 70
for k, p in MATCH_AT.items():
    tm = ARR[k] + FALL
    MT[k] = min(MT[k], tm); MT[p] = min(MT[p], tm)

PALETTE = [GOLD, CYAN, (120, 232, 150), (184, 150, 255), (255, 164, 96), (255, 236, 140)]
PCOL = [PALETTE[k % len(PALETTE)] for k in range(70)]

# calendar geometry
GX, GY = 150, 640
PX_, PY_ = 66, 23.6
CW, CH = 56, 18
BG = vgrad()


def cell_xy(doy):
    m, d = md(doy)
    return GX + m * PX_, GY + (d - 1) * PY_


def base_calendar():
    im = Image.fromarray(BG).convert("RGBA")
    d = ImageDraw.Draw(im)
    f = font("Inter-Bold", 26)
    for m in range(12):
        draw_rich(d, GX + m * PX_ + CW / 2, GY - 16, [(MLET[m], MUTED)], f)
        for dd in range(MDAYS[m]):
            x, y = GX + m * PX_, GY + dd * PY_
            d.rectangle((x, y, x + CW - 1, y + CH - 1), fill=(26, 30, 56))
    return im


CAL = base_calendar()


def fit(txt, name, size, maxw):
    f = font(name, size)
    while f.getlength(txt) > maxw and size > 20:
        size -= 2; f = font(name, size)
    return f


def people_count(t):
    return sum(1 for a in ARR if a + FALL <= t)


def header(d, t):
    fL = font("Inter-Bold", 30); fH = font("Inter-Black", 100); fM = font("Inter-Bold", 52)
    if t < T_MATCH:
        label(d, W / 2, 252, "IN A ROOM OF", fL, MUTED, spacing=6)
        draw_rich(d, W / 2, 360, [("23 people", GOLD)], fH)
        draw_rich(d, W / 2, 440, [("there's a ", WHITE), ("50% chance", GOLD)], fM)
        draw_rich(d, W / 2, 506, [("two share a birthday.", WHITE)], fM)
    elif t < T_WHY:
        m, dd = md(int(BDAY[FIRST]))
        n = people_count(t)
        label(d, W / 2, 252, f"PERSON {MATCH_AT[FIRST] + 1} AND PERSON {FIRST + 1}", fL, MUTED, spacing=5)
        sc = 1 + 0.15 * (1 - ease_out((t - T_MATCH) / 0.35))
        draw_rich(d, W / 2, 360, [("MATCH!", PINK)], font("Inter-Black", int(100 * sc)))
        draw_rich(d, W / 2, 440, [("Both born on ", WHITE), (f"{dd} {MNAMES[m]}.", PINK)], fM)
        if n >= 23:
            draw_rich(d, W / 2, 506, [("23 people: ", WHITE), ("50.7%", GOLD)], fM)
    elif t < T_BACK:
        label(d, W / 2, 252, "WHY SO LIKELY?", fL, MUTED, spacing=6)
        npairs = int(253 * ease((t - T_LINES0) / (T_LINES1 - T_LINES0))) if t > T_LINES0 else 0
        draw_rich(d, W / 2, 360, [(f"{npairs} pairs", GOLD)], fH)
        draw_rich(d, W / 2, 440, [("Not 23 chances.", WHITE)], fM)
        draw_rich(d, W / 2, 506, [("Every pair could match.", WHITE)], fM)
    else:
        label(d, W / 2, 252, "KEEP ADDING PEOPLE", fL, MUTED, spacing=6)
        n = max(23, people_count(t))
        draw_rich(d, W / 2, 360, [(f"{n} people", WHITE if n < 70 else GOLD)], fH)
        if n >= 70:
            draw_rich(d, W / 2, 440, [("99.9%", GOLD), (" chance", WHITE)], fM)
            draw_rich(d, W / 2, 506, [("of a shared birthday.", WHITE)], fM)


def stats(d, t):
    n = people_count(t)
    if t < T_P0: n = 0
    p = P(n)
    y = GY + 31 * PY_ + 58
    fL = font("Inter-Bold", 28); fN = font("Inter-Black", 54)
    d.text((GX, y), "PEOPLE", font=fL, fill=MUTED, anchor="ls")
    d.text((GX, y + 60), f"{n}", font=fN, fill=WHITE, anchor="ls")
    xr = GX + 12 * PX_ - (PX_ - CW)
    d.text((xr, y), "CHANCE OF A MATCH", font=fL, fill=MUTED, anchor="rs")
    d.text((xr, y + 60), f"{p * 100:.1f}%", font=fN, fill=GOLD if p >= 0.5 else WHITE, anchor="rs")
    # bar
    bx0, bx1, by = GX, xr, y + 86
    d.rounded_rectangle((bx0, by, bx1, by + 16), radius=8, fill=(30, 34, 62))
    d.rounded_rectangle((bx0, by, bx0 + max(16, (bx1 - bx0) * p), by + 16), radius=8, fill=GOLD if p >= 0.5 else CYAN)
    mx = bx0 + (bx1 - bx0) * 0.5
    d.line((mx, by - 8, mx, by + 24), fill=WHITE, width=3)


def draw_people(im, t, dim=1.0):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for k in range(70):
        a0 = ARR[k]
        if t < a0: break
        u = ease_out((t - a0) / FALL)
        x, y = cell_xy(int(BDAY[k]))
        yy = y - 160 * (1 - u)
        al = int(255 * min(1, (t - a0) / 0.08) * dim)
        matched = t >= MT[k]
        col = PINK if matched else PCOL[k]
        d.rectangle((x, yy, x + CW - 1, yy + CH - 1), fill=col + (al,))
        if matched:
            # flash glow for 0.9 s after the match lands
            age = t - MT[k]
            if 0 <= age < 0.9:
                g = 1 - age / 0.9
                gd.rectangle((x - 10, yy - 8, x + CW + 9, yy + CH + 7), fill=PINK + (int(200 * g * dim),))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    im.alpha_composite(glow); im.alpha_composite(ov)


def pairs_overlay(im, t):
    a = ease((t - T_WHY) / 0.4) * (1 - ease((t - T_BACK + 0.4) / 0.4))
    if a <= 0: return
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle((0, GY - 60, W, GY + 31 * PY_ + 20), fill=(8, 9, 20, int(248 * a)))
    cx, cy, R_ = W / 2, GY + 31 * PY_ / 2, 330
    pts = [(cx + R_ * math.sin(2 * math.pi * k / 23), cy - R_ * math.cos(2 * math.pi * k / 23)) for k in range(23)]
    nl = int(253 * ease((t - T_LINES0) / (T_LINES1 - T_LINES0))) if t > T_LINES0 else 0
    pairs = [(i, j) for i in range(23) for j in range(i + 1, 23)]
    for (i, j) in pairs[:nl]:
        d.line(pts[i] + pts[j], fill=(150, 170, 255, int(70 * a)), width=2)
    # the matching pair
    if t > T_LINES1 + 0.2:
        i, j = MATCH_AT[FIRST], FIRST
        g = ease((t - T_LINES1 - 0.2) / 0.3)
        d.line(pts[i] + pts[j], fill=PINK + (int(255 * a * g),), width=7)
    for k, (x, y) in enumerate(pts):
        c = PINK if (t > T_LINES1 + 0.2 and k in (FIRST, MATCH_AT[FIRST])) else PCOL[k]
        d.rectangle((x - 13, y - 13, x + 13, y + 13), fill=c + (int(255 * a),))
    im.alpha_composite(ov)


def frame(i):
    t = i / FPS
    im = CAL.copy()
    draw_people(im, t)
    pairs_overlay(im, t)
    d = ImageDraw.Draw(im)
    header(d, t)
    stats(d, t)
    if t >= T_CTA:
        a = ease((t - T_CTA) / 0.4)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 760, W - 70, 1170), radius=40, fill=(8, 9, 20, int(230 * a)))
        f1 = font("Inter-Black", 70)
        draw_rich(od, W / 2, 880, [("Comment your birthday", WHITE + (int(255 * a),))], fit("Comment your birthday", "Inter-Black", 70, 880))
        draw_rich(od, W / 2, 960, [("(day + month)", MUTED + (int(255 * a),))], font("Inter-Bold", 50))
        draw_rich(od, W / 2, 1075, [("Let's find a match.", GOLD + (int(255 * a),))], f1)
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 3.0, T_MATCH + 0.2, 8.2, 10.5, 12.8, 15.5, 18.5, 21.0]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
        print("first match person", FIRST + 1, "with", MATCH_AT[FIRST] + 1, md(int(BDAY[FIRST])), "t", round(T_MATCH, 2))
    else:
        w = Writer("v017_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
