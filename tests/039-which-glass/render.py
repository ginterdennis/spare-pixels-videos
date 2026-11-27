"""039 Which glass fills first? (explore, 27 Nov 2026). A tap pours into glass 1; pipes lead to glasses 2-5.
The viewer picks a number before the 3-2-1 ring runs out. "4? Look closer." at 2.8 s (the obvious path is
1 > 2 > 4). The water then plays it out: 1 drains into 2 through its LOW left pipe (so 1 never reaches its high
right pipe and glass 3 never gets a drop); 2's low pipe to 4 is capped (BLOCKED at ~5.6 s); 2 climbs to its high
pipe and overflows into the small glass 5, which fills first (GLASS 5. at ~12.2 s). CTA: comment your number.
Loops: everything drains back to the frame-0 state. No voice (a puzzle: people look). No pixel look (skia vectors).
Physics is the plain overflow rule: a glass that is being fed stays at its lowest OPEN outlet while that outlet
can pass the flow; a capped outlet passes nothing."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import skia
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp, countdown

DUR = 15.8
REVEAL = 2.8
WATER = (92, 196, 255)
WATER_D = (40, 120, 210)
GLASS = (210, 222, 245)

# glasses: centre x, top y, bottom y, top width, bottom width
G = {
    1: dict(x=540, top=560, bot=790, tw=230, bw=170),
    2: dict(x=330, top=905, bot=1135, tw=230, bw=170),
    3: dict(x=780, top=905, bot=1135, tw=230, bw=170),
    4: dict(x=150, top=1250, bot=1440, tw=190, bw=140),
    5: dict(x=540, top=1290, bot=1440, tw=150, bw=110),
}


def wall_x(g, h, side):
    """x of the left (-1) or right (+1) wall at fill height h (0..1)."""
    w = g["bw"] + (g["tw"] - g["bw"]) * h
    return g["x"] + side * w / 2


def hy(g, h):
    return g["bot"] - (g["bot"] - g["top"]) * h


# pipes: from glass, outlet height, side, to glass, capped?
PIPES = [
    dict(a=1, h=0.30, side=-1, b=2, cap=False),
    dict(a=1, h=0.72, side=1, b=3, cap=False),
    dict(a=2, h=0.24, side=-1, b=4, cap=True),
    dict(a=2, h=0.86, side=1, b=5, cap=False),
]
for p in PIPES:
    ga, gb = G[p["a"]], G[p["b"]]
    y = hy(ga, p["h"])
    x0 = wall_x(ga, p["h"], p["side"])
    p["pts"] = [(x0, y), (gb["x"], y), (gb["x"], gb["top"] - 34)]
    p["len"] = sum(math.dist(p["pts"][k], p["pts"][k + 1]) for k in range(2))

# ---- timeline (seconds): levels are piecewise linear, flows follow from them
T1_OUT = 3.35            # glass 1 reaches its low left pipe
P12 = (3.35, 3.85)       # water travels through pipe 1 -> 2
T2_CAP = 5.6             # glass 2 reaches the capped pipe to 4
T2_HIGH = 8.7            # glass 2 reaches its high pipe to 5
P25 = (8.7, 9.15)
T5_FULL = 12.2
CTA = 12.85
DRAIN0, DRAIN1 = 15.0, 15.8
L1_0 = 0.12              # glass 1's level on frame 0 (the tap is already pouring)


def levels(t):
    l1 = L1_0 + (0.30 - L1_0) * min(1, max(0, t / T1_OUT))
    l2 = 0.0 if t < P12[1] else 0.86 * min(1, (t - P12[1]) / (T2_HIGH - P12[1]))
    l5 = 0.0 if t < P25[1] else min(1.0, (t - P25[1]) / (T5_FULL - P25[1]))
    if t >= DRAIN0:     # drain back to the frame-0 state for the loop
        u = ease((t - DRAIN0) / (DRAIN1 - DRAIN0))
        l1, l2, l5 = lerp(l1, L1_0 - 0.0, u), lerp(l2, 0, u), lerp(l5, 0, u)
    return {1: l1, 2: l2, 3: 0.0, 4: 0.0, 5: l5}


def pipe_fill(p, t):
    """0..1 of the pipe length filled with flowing water."""
    if t >= DRAIN0:
        return 0.0
    if p["b"] == 2:
        return min(1, max(0, (t - P12[0]) / (P12[1] - P12[0])))
    if p["b"] == 5:
        return min(1, max(0, (t - P25[0]) / (P25[1] - P25[0])))
    if p["b"] == 4:     # water enters the stub up to the cap once glass 2 is that high
        return 0.06 if t >= T2_CAP - 0.1 else 0.0
    return 0.0


BG = vgrad()
rng = np.random.default_rng(9)
BUB = rng.uniform(0, 1, (40, 3))


def P(c, a=255):
    return skia.Color(c[0], c[1], c[2], a)


def glass_path(g, h0=0.0, h1=1.0, inset=0.0):
    yb, yt = hy(g, h0), hy(g, h1)
    path = skia.Path()
    path.moveTo(wall_x(g, h0, -1) + inset, yb)
    path.lineTo(wall_x(g, h1, -1) + inset, yt)
    path.lineTo(wall_x(g, h1, 1) - inset, yt)
    path.lineTo(wall_x(g, h0, 1) - inset, yb)
    path.close()
    return path


def poly(pts, upto=None):
    path = skia.Path()
    path.moveTo(*pts[0])
    if upto is None:
        for q in pts[1:]:
            path.lineTo(*q)
        return path
    left = upto
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        d = math.dist(a, b)
        if left >= d:
            path.lineTo(*b); left -= d
        else:
            f = left / d if d else 0
            path.lineTo(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            break
    return path


def stroke(w, c, a=255, cap=skia.Paint.kRound_Cap):
    return skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, Color=P(c, a), StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)


def fill(c, a=255):
    return skia.Paint(AntiAlias=True, Color=P(c, a))


def scene(t):
    s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.Color(0, 0, 0, 0))
    L = levels(t)
    # ---- pipes (tube, then water inside)
    for p in PIPES:
        path = poly(p["pts"])
        c.drawPath(path, stroke(40, (12, 14, 30), 255))
        c.drawPath(path, stroke(30, (70, 78, 118), 255))
        c.drawPath(path, stroke(18, (34, 38, 66), 255))
        k = pipe_fill(p, t)
        if k > 0:
            c.drawPath(poly(p["pts"], k * p["len"]), stroke(16, WATER, 255))
        # stream falling from the pipe end into the target glass while it flows
        if k >= 1 and p["b"] in (2, 5) and t < DRAIN0:
            gb = G[p["b"]]
            x = gb["x"]
            y0 = gb["top"] - 34
            y1 = hy(gb, L[p["b"]])
            wob = 2 * math.sin(t * 40)
            c.drawRect(skia.Rect(x - 7 + wob, y0, x + 7 + wob, y1), fill(WATER, 235))
            c.drawCircle(x, y1, 14 + 3 * math.sin(t * 25), fill((210, 240, 255), 150))
        if p["cap"]:
            x0, y0 = p["pts"][0]
            cx = x0 - 38
            c.drawRoundRect(skia.Rect(cx - 14, y0 - 26, cx + 14, y0 + 26), 6, 6, fill((200, 70, 80)))
            c.drawRoundRect(skia.Rect(cx - 14, y0 - 26, cx + 14, y0 + 26), 6, 6, stroke(5, (12, 14, 30), 255))
    # ---- tap + stream into glass 1
    g1 = G[1]
    c.drawRoundRect(skia.Rect(540 - 30, 440, 700, 488), 18, 18, fill((180, 188, 214)))
    c.drawRoundRect(skia.Rect(540 - 30, 440, 700, 488), 18, 18, stroke(6, (12, 14, 30), 255))
    c.drawRect(skia.Rect(520, 470, 560, 516), fill((180, 188, 214)))
    c.drawRect(skia.Rect(520, 470, 560, 516), stroke(6, (12, 14, 30), 255))
    c.drawRoundRect(skia.Rect(640, 412, 690, 440), 8, 8, fill((200, 70, 80)))
    if t < DRAIN0:
        wob = 2 * math.sin(t * 37)
        c.drawRect(skia.Rect(531 + wob, 516, 549 + wob, hy(g1, L[1])), fill(WATER, 240))
        c.drawCircle(540, hy(g1, L[1]), 16 + 3 * math.sin(t * 22), fill((210, 240, 255), 150))
    # ---- glasses: back, water, front rim
    for n, g in G.items():
        c.drawPath(glass_path(g), fill(GLASS, 28))
        lv = L[n]
        if lv > 0.002:
            c.drawPath(glass_path(g, 0.0, lv, inset=7), fill(WATER, 225))
            # surface line + a few bubbles
            ys = hy(g, lv)
            c.drawLine(wall_x(g, lv, -1) + 9, ys, wall_x(g, lv, 1) - 9, ys, stroke(6, (200, 238, 255), 230))
            for (bx, by, bs) in BUB[n * 7:(n + 1) * 7]:
                yy = g["bot"] - ((by + t * (0.3 + bs)) % 1) * (g["bot"] - ys)
                if yy < ys + 8:
                    continue
                xx = g["x"] + (bx - 0.5) * g["bw"] * 0.7
                c.drawCircle(xx, yy, 3 + 4 * bs, fill((220, 245, 255), 110))
        path = glass_path(g)
        c.drawPath(path, stroke(9, (12, 14, 30), 255))
        c.drawPath(path, stroke(5, GLASS, 255))
        c.drawLine(wall_x(g, 0.92, -1) + 16, hy(g, 0.88), wall_x(g, 0.35, -1) + 18, hy(g, 0.35), stroke(6, (255, 255, 255), 60))
    arr = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return Image.fromarray(arr, "RGBA")


def badge(d, n, x, y, col, a=1.0, big=False):
    r = 40 if big else 34
    d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(255 * a),), outline=(12, 14, 30, int(255 * a)), width=6)
    d.text((x, y + r * 0.36), str(n), font=font("Inter-Black", int(r * 1.15)), fill=(12, 14, 30, int(255 * a)), anchor="ms")


def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    sc = scene(t)
    win = 1.0 if T5_FULL <= t < DRAIN0 else 0.0
    # glass 5 glow when it wins
    if win:
        k = ease((t - T5_FULL) / 0.3)
        g = G[5]
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((g["x"] - 120, g["top"] - 40, g["x"] + 120, g["bot"] + 100), radius=40, outline=GOLD + (int(220 * k),), width=10)
        sc.alpha_composite(ov)
    # number badges (top-left of each glass)
    for n, g in G.items():
        col = GOLD if (n == 5 and win) else WHITE
        badge(ImageDraw.Draw(sc), n, g["x"], g["bot"] + 52, col, big=(n == 5 and win))
    # slow push-in on the opening (and back out into the loop) so frame 0 is already moving
    z = 1.0 + 0.07 * (1 - ease(min(1.0, t / 3.0))) if t < 3.0 else (1.0 + 0.07 * ease((t - DRAIN0) / (DUR - DRAIN0)) if t >= DRAIN0 else 1.0)
    if z != 1.0:
        cx, cy = 540, 900
        big = sc.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = int(cx * z - cx), int(cy * z - cy)
        sc = big.crop((ox, oy, ox + W, oy + H))
    im.alpha_composite(sc)
    d = ImageDraw.Draw(im)
    # BLOCKED callout at the cap
    if T2_CAP - 0.05 <= t < T2_CAP + 2.4:
        a = ease((t - T2_CAP + 0.05) / 0.2) * (1 - ease((t - T2_CAP - 2.1) / 0.3))
        p = PIPES[2]
        x0, y0 = p["pts"][0]
        cx = x0 - 38
        pr = 52 + 10 * max(0, 1 - (t - T2_CAP) / 0.25)
        d.ellipse((cx - pr, y0 - pr, cx + pr, y0 + pr), outline=(255, 90, 100, int(255 * a)), width=8)
        f = font("Inter-Black", 46)
        tx, ty = cx - 40, y0 + 100
        w_ = f.getlength("BLOCKED")
        d.rounded_rectangle((tx - w_ / 2 - 22, ty - 46, tx + w_ / 2 + 22, ty + 14), radius=16, fill=(8, 9, 20, int(235 * a)), outline=(255, 90, 100, int(255 * a)), width=5)
        d.text((tx, ty), "BLOCKED", font=f, fill=(255, 110, 120, int(255 * a)), anchor="ms")
    # glass 1 holds at its low pipe (a small "stays here" marker)
    if 4.0 <= t < 8.0:
        a = ease((t - 4.0) / 0.3) * (1 - ease((t - 7.7) / 0.3))
        g = G[1]
        y = hy(g, 0.30)
        f = font("Inter-Bold", 34)
        d.text((g["x"] - g["tw"] / 2 - 70, y - 34), "1 stays at this pipe", font=f, fill=MUTED + (int(255 * a),), anchor="rs")
    # hook + countdown (frame 0: task over a pouring tap)
    if t < REVEAL + 0.6:
        hook_text(im, t, [[("Which glass fills ", WHITE), ("FIRST?", GOLD)]], y=330, size=104,
                  alpha=1 - ease((t - REVEAL - 0.3) / 0.3))
    elif t >= DRAIN0 - 0.2:
        hook_text(im, t, [[("Which glass fills ", WHITE), ("FIRST?", GOLD)]], y=330, size=104, alpha=ease((t - DRAIN0 + 0.2) / 0.4), punch=0)
    countdown(im, t, 0.0, REVEAL, 930, 680, r=70)
    stamp(im, t, REVEAL, [("4? ", WHITE), ("Look closer.", GOLD)], y=860, size=96, hold=1.25, panel=True)
    stamp(im, t, T5_FULL, [("GLASS 5.", GOLD)], y=1160, size=150, hold=CTA - T5_FULL, panel=True)
    # mid-video caption (top area, after the hook leaves)
    d = ImageDraw.Draw(im)
    if REVEAL + 0.9 <= t < CTA - 0.2:
        a = ease((t - REVEAL - 0.9) / 0.3) * (1 - ease((t - CTA + 0.5) / 0.3))
        f = font("Inter-Black", 58)
        txt = "Watch the water." if t < T2_CAP else ("2 fills up instead." if t < T2_HIGH else "Over the top pipe...")
        draw_rich(d, W / 2, 340, [(txt, WHITE + (int(255 * a),))], f)
    # CTA
    if CTA <= t < DRAIN0:
        ca = ease((t - CTA) / 0.3) * (1 - ease((t - DRAIN0 + 0.25) / 0.25))
        ov = Image.new("RGBA", im.size, (8, 9, 20, int(150 * ca))); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 760, W - 70, 1260), radius=40, fill=(8, 9, 20, int(235 * ca)), outline=GOLD + (int(255 * ca),), width=5)
        draw_rich(od, W / 2, 880, [("Glass 3 never got a drop.", WHITE + (int(255 * ca),))], font("Inter-Bold", 54))
        draw_rich(od, W / 2, 1020, [("Did you get it?", GOLD + (int(255 * ca),))], font("Inter-Black", 92))
        draw_rich(od, W / 2, 1150, [("Comment your number.", WHITE + (int(255 * ca),))], font("Inter-Black", 66))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.5, 2.9, 4.5, 5.7, 8.0, 10.0, 12.3, 13.5, 15.3]
        ims = [frame(int(round(t * FPS))).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * 5, 480 * ((len(ims) + 4) // 5)))
        for k, x in enumerate(ims): st.paste(x, ((k % 5) * 270, (k // 5) * 480))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v039_video.mp4")
        for i in range(int(round(DUR * FPS))): w.write(frame(i))
        w.close(); print("frames", w.n)
