import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

VIOLET = (160, 120, 255); GREEN = (90, 230, 150)
P1, P2, P3, PE = (0.0, 10.5), (10.8, 22.0), (22.3, 34.6), (34.6, 38.5)
DUR = PE[1]
SS = 2
RY0, RH = 400, 1060          # supersampled drawing region (y range)
BG = vgrad()

def pop(t, t0, d=0.18):
    u = (t - t0) / d
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return 1 + 0.25 * math.sin(math.pi * u) * (1 - u) - (1 - u) ** 3  # overshoot

def sq(d, cx, cy, s, fill, outline=None, rad=10):
    h = s / 2
    d.rounded_rectangle(((cx - h) * SS, (cy - h - RY0) * SS, (cx + h) * SS, (cy + h - RY0) * SS), radius=rad * SS, fill=fill, outline=outline, width=2 * SS if outline else 0)

def poly(d, pts, fill, outline=None, w=3):
    P = [(x * SS, (y - RY0) * SS) for x, y in pts]
    d.polygon(P, fill=fill)
    if outline: d.line(P + [P[0]], fill=outline, width=w * SS, joint="curve")

def eq(dd, y, parts, size=68, a=1.0):
    draw_rich(dd, W / 2, y, [(s, lerpc(BG_BOT, c, a)) for s, c in parts], font("Inter-Black", size))

# ---------------------------------------------------------------- proof 1: odd numbers make squares
L_COLS = [GOLD, PINK, CYAN, VIOLET, GREEN]
def p1(t, lay, d2):
    n, cs = 5, 118
    x0, y0 = W / 2 - n * cs / 2, 905 - n * cs / 2
    T = [-0.3] + [0.9 + k * 1.35 for k in range(n - 1)]
    done = 0
    for k in range(n):
        cells = [(i, j) for i in range(k + 1) for j in range(k + 1) if max(i, j) == k]
        cells.sort(key=lambda c: (c[0] - c[1]))
        for m, (i, j) in enumerate(cells):
            s = pop(t, T[k] + m * 0.06)
            if s > 0:
                sq(lay, x0 + (j + 0.5) * cs, y0 + (i + 0.5) * cs, (cs - 10) * s, L_COLS[k] + (255,))
        if t >= T[k]: done = k + 1
    # equation
    if done:
        parts = []
        for k in range(done):
            if k: parts.append((" + ", WHITE))
            parts.append((str(2 * k + 1), L_COLS[k]))
        eq(d2, 1420, parts, 72)
        eq(d2, 1515, [("= ", WHITE), (str(done * done), WHITE), (" = ", MUTED), (f"{done}²", GOLD)], 72)
    if t > T[-1] + 1.6:
        a = ease((t - T[-1] - 1.6) / 0.5)
        eq(d2, 1610, [("1 + 3 + 5 + … + (2n − 1) = n²", MUTED)], 42, a)

# ---------------------------------------------------------------- proof 2: staircase sum
def p2(t, lay, d2):
    n, cs = 6, 92
    x0, y0 = W / 2 - n * cs / 2, 905 - (n + 1) * cs / 2
    T0 = 0.4
    for i in range(n):
        for k in range(i + 1):
            s = pop(t, T0 + i * 0.42 + k * 0.05)
            if s > 0:
                r = n - k  # row from top (bottom row = n)
                sq(lay, x0 + (i + 0.5) * cs, y0 + (r + 0.5) * cs, (cs - 8) * s, CYAN + (255,))
    # pink copy: lifts off, rotates 180°, lands in the complement
    TA, TB = 3.5, 5.6
    if t >= TA:
        fade_out = 1 - ease((t - 7.6) / 0.7)
        u = ease((t - TA - 0.4) / (TB - TA - 0.4))
        alpha = int(255 * min(1, (t - TA) / 0.3) * fade_out)
        if alpha > 0:
            cx0 = x0 + n * cs / 2; cy_src = y0 + cs + n * cs / 2; cy_dst = y0 + n * cs / 2
            ang = math.pi * u
            lift = -150 * math.sin(math.pi * u)
            ccx, ccy = cx0 + 60 * math.sin(math.pi * u), lerp(cy_src, cy_dst, u) + lift
            for i in range(n):
                for k in range(i + 1):
                    px = x0 + (i + 0.5) * cs - cx0; py = y0 + (n - k + 0.5) * cs - cy_src
                    rx = px * math.cos(ang) - py * math.sin(ang); ry = px * math.sin(ang) + py * math.cos(ang)
                    h = (cs - 8) / 2
                    corners = [(-h, -h), (h, -h), (h, h), (-h, h)]
                    pts = [(ccx + rx + cx * math.cos(ang) - cy * math.sin(ang), ccy + ry + cx * math.sin(ang) + cy * math.cos(ang)) for cx, cy in corners]
                    poly(lay, pts, PINK + (alpha,))
    # rectangle outline + side labels
    if t >= TB + 0.2:
        a = ease((t - TB - 0.2) / 0.4) * (1 - ease((t - 7.6) / 0.7))
        if a > 0:
            lay.rounded_rectangle(((x0 - 8) * SS, (y0 - 8 - RY0) * SS, (x0 + n * cs + 8) * SS, (y0 + (n + 1) * cs + 8 - RY0) * SS), radius=14 * SS, outline=WHITE + (int(255 * a),), width=4 * SS)
            draw_rich(d2, x0 + n * cs / 2, y0 + (n + 1) * cs + 70, [("6", lerpc(BG_BOT, WHITE, a))], font("Inter-Black", 54))
            d2.text((x0 + n * cs + 50, y0 + (n + 1) * cs / 2), "7", font=font("Inter-Black", 54), fill=lerpc(BG_BOT, WHITE, a), anchor="mm")
    # equations
    if t >= T0:
        k = min(n, int((t - T0) / 0.42) + 1)
        if t < TB + 0.2:
            parts = []
            for i in range(k):
                if i: parts.append(("+", WHITE))
                parts.append((str(i + 1), CYAN))
            if k == n: parts += [(" = ", WHITE), ("?", GOLD)]
            eq(d2, 1440, parts, 74)
        elif t < 8.2:
            eq(d2, 1440, [("2", PINK), (" × (", WHITE), ("1+2+…+6", CYAN), (") = ", WHITE), ("6 × 7", WHITE)], 62)
        else:
            a = ease((t - 8.2) / 0.4)
            eq(d2, 1440, [("1+2+…+6", CYAN), (" = ", WHITE), ("42 ÷ 2", MUTED), (" = ", WHITE), ("21", GOLD)], 66, a)
    if t > 9.2:
        a = ease((t - 9.2) / 0.5)
        eq(d2, 1540, [("1 + 2 + … + n = n(n + 1) ÷ 2", MUTED)], 42, a)

# ---------------------------------------------------------------- proof 3: Pythagoras by rearrangement
A_, B_ = 3, 4; N7 = 7; CS3 = 110
X3, Y3 = W / 2 - N7 * CS3 / 2, 905 - N7 * CS3 / 2
def U(p): return (X3 + p[0] * CS3, Y3 + p[1] * CS3)
TRI1 = {"tl": [(0, 0), (3, 0), (0, 4)], "tr": [(7, 0), (3, 0), (7, 3)], "br": [(7, 7), (7, 3), (4, 7)], "bl": [(0, 7), (4, 7), (0, 4)]}
# first vertex = right angle. targets (same vertex order)
TRI2 = {"tl": [(3, 3), (3, 0), (7, 3)], "tr": [(7, 0), (3, 0), (7, 3)], "br": [(3, 7), (3, 3), (0, 7)], "bl": [(0, 3), (0, 7), (3, 3)]}
MOVES = {"br": (2.6, 3.7), "tl": (3.9, 5.1), "bl": (5.3, 6.5)}
def rigid(src, dst, u):
    s = np.array(src, float); dd = np.array(dst, float)
    a0 = math.atan2(*(s[1] - s[0])[::-1]); a1 = math.atan2(*(dd[1] - dd[0])[::-1])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    ang = da * u; c, sn = math.cos(ang), math.sin(ang)
    piv = s[0] * (1 - u) + dd[0] * u
    rel = s - s[0]
    return [tuple(piv + np.array([r[0] * c - r[1] * sn, r[0] * sn + r[1] * c])) for r in rel]
def p3(t, lay, d2):
    a_in = ease(t / 0.6)
    # frame
    lay.rectangle(((X3 - 6) * SS, (Y3 - 6 - RY0) * SS, (X3 + N7 * CS3 + 6) * SS, (Y3 + N7 * CS3 + 6 - RY0) * SS), fill=(16, 19, 40, 255), outline=(90, 98, 150, int(255 * a_in)), width=3 * SS)
    # c² fill
    ca = a_in * (1 - ease((t - 2.2) / 0.35))
    if ca > 0:
        poly(lay, [U(p) for p in [(3, 0), (7, 3), (4, 7), (0, 4)]], GOLD + (int(235 * ca),))
    # a², b² fills
    fa = ease((t - 6.7) / 0.5)
    if fa > 0:
        for (x0, y0, n_, col) in [(0, 0, 3, PINK), (3, 3, 4, CYAN)]:
            for i in range(n_):
                for j in range(n_):
                    s_ = pop(t, 6.7 + (i + j) * 0.04)
                    if s_ > 0:
                        sq(lay, X3 + (x0 + j + 0.5) * CS3, Y3 + (y0 + i + 0.5) * CS3, (CS3 - 8) * s_, col + (int(255 * fa),), rad=8)
    # triangles
    for key in ["tl", "tr", "br", "bl"]:
        if key in MOVES:
            m0, m1 = MOVES[key]; u = ease((t - m0) / (m1 - m0))
        else: u = 0
        pts = rigid(TRI1[key], TRI2[key], u)
        poly(lay, [U(p) for p in pts], (74, 85, 150, int(255 * a_in)), outline=(150, 162, 230, int(255 * a_in)), w=3)
    # labels
    fL = font("Inter-Black", 56)
    la = a_in * (1 - ease((t - 2.2) / 0.35))
    if la > 0:
        c_ = lerpc(BG_BOT, WHITE, la)
        d2.text(U((1.5, -0.45)), "a", font=fL, fill=c_, anchor="mm"); d2.text(U((5.0, -0.45)), "b", font=fL, fill=c_, anchor="mm")
        d2.text(U((-0.45, 2.0)), "b", font=fL, fill=c_, anchor="mm"); d2.text(U((-0.45, 5.5)), "a", font=fL, fill=c_, anchor="mm")
        d2.text(U((3.5, 3.5)), "c²", font=font("Inter-Black", 96), fill=lerpc(GOLD, (20, 20, 30), la), anchor="mm")
        d2.text(U((5.25, 1.15)), "c", font=fL, fill=c_, anchor="mm")
    if fa > 0:
        d2.text(U((1.5, 1.5)), "a²", font=font("Inter-Black", 80), fill=lerpc(PINK, (20, 20, 30), fa), anchor="mm")
        d2.text(U((5.0, 5.0)), "b²", font=font("Inter-Black", 96), fill=lerpc(CYAN, (20, 20, 30), fa), anchor="mm")
    # equations
    if t < 7.0:
        eq(d2, 1440, [("c²", GOLD)] + ([(" = ?", WHITE)] if t > 2.4 else []), 80, a_in)
    else:
        eq(d2, 1440, [("c²", GOLD), (" = ", WHITE), ("a²", PINK), (" + ", WHITE), ("b²", CYAN)], 80)
    if t > 8.3:
        a = ease((t - 8.3) / 0.4)
        eq(d2, 1540, [("25", GOLD), (" = ", WHITE), ("9", PINK), (" + ", WHITE), ("16", CYAN)], 56, a)

def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy())
    lay_img = Image.new("RGBA", (W * SS, RH * SS), (0, 0, 0, 0)); lay = ImageDraw.Draw(lay_img)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(txt)
    fade = 1.0; idx = None
    for k, (seg, fn) in enumerate([(P1, p1), (P2, p2), (P3, p3)]):
        if seg[0] <= t < seg[1] + 0.3:
            lt = t - seg[0]
            fade = min(1, (seg[1] + 0.3 - t) / 0.3) if t > seg[1] else 1.0
            fade *= min(1, lt / 0.25) if k else 1.0
            fn(lt, lay, d2); idx = k
            break
    small = lay_img.resize((W, RH), Image.LANCZOS)
    if fade < 1:
        small.putalpha(small.getchannel("A").point(lambda v: int(v * fade)))
        txt.putalpha(txt.getchannel("A").point(lambda v: int(v * fade)))
    base = im.convert("RGBA")
    base.alpha_composite(small, (0, RY0)); base.alpha_composite(txt)
    d = ImageDraw.Draw(base)
    # hook / progress / end
    ha = 1 - ease((t - 2.3) / 0.4)
    if ha > 0:
        draw_rich(d, W / 2, 250, [("3 proofs.", lerpc(BG_TOP, WHITE, ha))], font("Inter-Black", 96))
        draw_rich(d, W / 2, 345, [("Zero ", lerpc(BG_TOP, WHITE, ha)), ("words.", lerpc(BG_TOP, GOLD, ha))], font("Inter-Black", 96))
    if idx is not None and t > 2.5:
        pa = min(1, (t - 2.5) / 0.4) * fade
        for k in range(3):
            c = GOLD if k == idx else (60, 66, 100)
            cx = W / 2 + (k - 1) * 60
            d.rounded_rectangle((cx - 18, 290 - 18, cx + 18, 290 + 18), radius=6, fill=lerpc(BG_TOP, c, pa))
    if t >= PE[0]:
        a = ease((t - PE[0]) / 0.4)
        draw_rich(d, W / 2, 820, [("Which one", lerpc(BG_TOP, WHITE, a))], font("Inter-Black", 100))
        draw_rich(d, W / 2, 935, [("clicked?", lerpc(BG_TOP, GOLD, a))], font("Inter-Black", 100))
        for k, c in enumerate([GOLD, CYAN, PINK]):
            cx = W / 2 + (k - 1) * 170
            s = 110 * pop(t, PE[0] + 0.4 + k * 0.12)
            if s > 0:
                d.rounded_rectangle((cx - s / 2, 1080 - s / 2, cx + s / 2, 1080 + s / 2), radius=16, fill=c)
                d.text((cx, 1080), str(k + 1), font=font("Inter-Black", int(64 * s / 110) + 1), fill=BG_BOT, anchor="mm")
        draw_rich(d, W / 2, 1260, [("Comment the number.", lerpc(BG_TOP, MUTED, a))], font("Inter-Bold", 50))
    return base.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ts = [0.0, 8.5, 15.5, 20.0, 24.0, 27.5, 32.0, 36.5]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v009_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
