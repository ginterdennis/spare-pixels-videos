"""Sigmoid Horizon brand kit for videos: the Neon Eclipse look, in skia-python.

Every new video uses this (rules: brand/README.md). It draws the brand's pieces onto a skia canvas of
1080 x 1920 so any renderer can use them: the ground (void + sparse stars), the horizon (planet edge in
the eclipse gradient with the pink sun ring rising behind it), the trajectory (an S-curve that draws
itself), the eclipse ring, the round icon (watermark), topic tags, series badges, the hook, big
numbers, labels, a progress bar and a source chip.

    import sys; sys.path.insert(0, "/home/claude/kit")
    import brand as B
    surf, cv = B.new_frame()
    B.frame0(cv, t, topic="ENERGY", lines=["WHY DOES", "CHARGING", "SLOW", "AT 80%?"], highlight=2,
             bar=("BATTERY", 0.8, "80%"))
    img = B.to_pil(surf)            # PIL image for kit.Writer, or B.to_rgb(surf) for a numpy array

`python3 kit/brand.py demo <outdir>` renders the reference frames (brand/reference/*.png).
Fonts: Unbounded (display), Inter (text), JetBrains Mono (numbers, labels) in kit/fonts.
"""
import functools
import math
import os
import random
import sys

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
W, H = 1080, 1920

# ---------------------------------------------------------------- palette (= brand/tokens.json)
VOID = (5, 3, 11)              # ground, ~80% of every frame together with NIGHT
NIGHT = (14, 10, 28)           # raised surfaces: cards, chips
DUSK = (30, 22, 54)            # hairlines, tracks, data grid
STAR = (242, 247, 255)         # text, white cores of neon lines
HAZE = (164, 157, 196)         # secondary text, labels, sources
MAGENTA = (255, 47, 208)       # eclipse gradient, left
ULTRAVIOLET = (176, 92, 255)   # eclipse gradient, middle
CYAN = (34, 230, 255)          # eclipse gradient, right; the trajectory
SUN_PINK = (255, 90, 223)      # only the eclipse ring and markers on a curve
FLARE = (255, 255, 255)
PLANET = (7, 4, 15)
GRADIENT = (MAGENTA, ULTRAVIOLET, CYAN)
TOPIC = {"MATHS": ULTRAVIOLET, "TECH": CYAN, "BUSINESS": (61, 255, 176), "SCIENCE": (91, 140, 255), "ENERGY": (255, 178, 58)}
SERIES = {"IS THIS A BUSINESS?": ((61, 255, 176), "STORY SERIES"), "RIGHT NOW": (MAGENTA, "DAILY EXPLAINER"),
          "THE CURVE": (CYAN, "WEEKLY CHART")}

SAFE = (90, 220, 930, 1500)    # x0, y0, x1, y1: keep text inside (platform UI covers the rest)
WATERMARK = (862, 236, 128)    # x, y, size of the round icon on every Shorts frame (top right)

FONT_FILES = {"display": "Unbounded-ExtraBold", "display_black": "Unbounded-Black", "display_bold": "Unbounded-Bold",
              "text": "Inter-SemiBold", "text_bold": "Inter-Bold", "text_regular": "Inter-Regular",
              "mono": "JBMono-Bold", "mono_semi": "JBMono-SemiBold"}


# ---------------------------------------------------------------- basics
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def logistic01(u, k=6.0):
    """The brand's easing: a logistic S-curve from 0 to 1 (slow start, fast middle, soft landing)."""
    u = clamp01(u)
    lo, hi = 1 / (1 + math.exp(k)), 1 / (1 + math.exp(-k))
    return (1 / (1 + math.exp(-k * (2 * u - 1))) - lo) / (hi - lo)


def prog(t, t0, dur, ease=logistic01):
    return ease(clamp01((t - t0) / dur)) if dur > 0 else float(t >= t0)


def col(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(round(255 * clamp01(a))))


def paint(rgb=STAR, a=1.0, stroke=None, blur=0.0, shader=None, cap="round"):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(clamp01(a))
    return p


def gradient(x0, x1, stops=GRADIENT, y0=0.0, y1=0.0, alphas=None):
    cols = [col(c, alphas[i] if alphas else 1.0) for i, c in enumerate(stops)]
    pos = [i / (len(stops) - 1) for i in range(len(stops))]
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cols, pos)


@functools.lru_cache(None)
def typeface(role):
    p = os.path.join(FONTS, FONT_FILES.get(role, role) + ".ttf")
    return skia.Typeface.MakeFromFile(p)


@functools.lru_cache(None)
def font(role, size):
    f = skia.Font(typeface(role), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def measure(s, role, size, tracking=0.0):
    f = font(role, round(size, 1))
    return f.measureText(s) + tracking * size * max(len(s) - 1, 0)


def fit(lines, role, size, max_w):
    w = max(measure(s, role, 100) for s in lines) / 100
    return min(size, max_w / w) if w else size


def new_frame(w=W, h=H):
    surf = skia.Surface(w, h)
    return surf, surf.getCanvas()


def to_rgb(surf):
    a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return np.ascontiguousarray(a[:, :, :3])


def to_pil(surf):
    from PIL import Image
    return Image.fromarray(to_rgb(surf))


# ---------------------------------------------------------------- paths
def sigmoid_pts(x0, y0, x1, y1, k=5.4, n=180):
    """A real logistic S-curve from (x0, y0) to (x1, y1), normalised so it hits both ends."""
    lo, hi = 1 / (1 + math.exp(k)), 1 / (1 + math.exp(-k))
    pts = []
    for i in range(n + 1):
        u = i / n
        v = (1 / (1 + math.exp(-k * (2 * u - 1))) - lo) / (hi - lo)
        pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * v))
    return pts


def path_of(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    return p


def circle_path(cx, cy, r):
    p = skia.Path()
    p.addCircle(cx, cy, r)
    return p


def glow_stroke(cv, path, rgb=CYAN, w=7.0, a=1.0, shader=None, core=True, glow=1.0, cap="round"):
    """The brand's neon line: two blurred layers under a crisp line with a thin white core."""
    if a <= 0:
        return
    sh = shader
    cv.drawPath(path, paint(rgb, 0.45 * a * glow, stroke=w * 3.4, blur=w * 2.4, shader=sh, cap=cap))
    cv.drawPath(path, paint(rgb, 0.85 * a * glow, stroke=w * 1.7, blur=w * 0.8, shader=sh, cap=cap))
    cv.drawPath(path, paint(rgb, a, stroke=w, shader=sh, cap=cap))
    if core:
        cv.drawPath(path, paint(FLARE, 0.85 * a, stroke=max(w * 0.32, 1.2), cap=cap))


# ---------------------------------------------------------------- the three shapes
def ground(cv, t=0.0, loop=None, seed=7, n=110, w=W, h=H):
    """Void with sparse stars. With `loop` (seconds) the twinkle is periodic, so the last frame = frame 0."""
    cv.clear(col(VOID))
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.7, 2.3)
        base, ph = rnd.uniform(0.2, 0.85), rnd.uniform(0, 2 * math.pi)
        tw_ = 1.0 if not loop else 0.75 + 0.25 * math.sin(2 * math.pi * t / loop * rnd.choice((1, 2)) + ph)
        cv.drawCircle(x, y, r, paint(FLARE, base * tw_))


def horizon(cv, rise=1.0, cx=540.0, top=1390.0, R=1500.0, sun_r=270.0, sun_dy=115.0, half=1200.0, glow=1.0, sun=True, a=1.0):
    """Planet edge in the eclipse gradient with the pink sun ring behind it. rise 0..1 lifts the sun."""
    cy = top + R
    planet = circle_path(cx, cy, R)
    if sun and rise > 0:
        sc = top + sun_dy + (1 - clamp01(rise)) * (sun_r + sun_dy + 20)
        cv.save()
        cv.clipPath(planet, skia.ClipOp.kDifference, True)
        cv.drawCircle(cx, sc, sun_r, paint(MAGENTA, 0.16 * a * glow, blur=40))
        glow_stroke(cv, circle_path(cx, sc, sun_r), SUN_PINK, 8, a=a, glow=glow)
        cv.restore()
    cv.drawPath(planet, paint(PLANET, a))
    ay = cy - math.sqrt(max(R * R - half * half, 0))
    arc = skia.Path()
    arc.addArc(skia.Rect(cx - R, cy - R, cx + R, cy + R), 270 - math.degrees(math.asin(min(half / R, 1))),
               2 * math.degrees(math.asin(min(half / R, 1))))
    sh = gradient(cx - half, cx + half)
    cv.drawPath(arc, paint(MAGENTA, 0.45 * a * glow, stroke=60, blur=28, shader=sh))
    cv.drawPath(arc, paint(MAGENTA, 0.9 * a * glow, stroke=16, blur=9, shader=sh))
    cv.drawPath(arc, paint(MAGENTA, a, stroke=7, shader=sh))
    cv.drawPath(arc, paint(FLARE, 0.85 * a, stroke=2))
    return ay


def trajectory(cv, x0, y0, x1, y1, p=1.0, k=5.4, w=7.0, a=1.0, head=True, glow=1.0):
    """The S-curve, fading in from transparent to cyan, drawn up to p (0..1), with a glowing head."""
    if p <= 0 or a <= 0:
        return None
    pts = sigmoid_pts(x0, y0, x1, y1, k)
    n = max(2, int(round(clamp01(p) * (len(pts) - 1))) + 1)
    sub = pts[:n]
    sh = gradient(x0, x1, (CYAN, CYAN, (232, 253, 255)), alphas=(0.0, 1.0, 1.0))
    path = path_of(sub)
    cv.drawPath(path, paint(CYAN, 0.45 * a * glow, stroke=w * 3.1, blur=w * 1.2, shader=sh))
    cv.drawPath(path, paint(CYAN, a, stroke=w, shader=sh))
    hx, hy = sub[-1]
    if head:
        cv.drawCircle(hx, hy, w * 3.7, paint(CYAN, 0.6 * a * glow, blur=w * 1.4))
        cv.drawCircle(hx, hy, w * 1.6, paint(FLARE, a))
    return hx, hy


def eclipse_ring(cv, cx, cy, r, a=1.0, w=6.0, dot=True):
    """Circle the one thing that matters."""
    glow_stroke(cv, circle_path(cx, cy, r), SUN_PINK, w, a=a)
    if dot:
        cv.drawCircle(cx, cy, w * 2.6, paint(FLARE, a))


# ---------------------------------------------------------------- the icon / watermark
def icon(cv, x, y, size, mono=None, a=1.0, ground_disc=True):
    """The round Neon Eclipse icon (matches brand/logo/sh-icon.svg): the full scene, as on the YouTube
    banner (thin lines, two-layer glow, white cores), cropped to a circle. mono = an RGB for one-colour."""
    s = size / 1000.0
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cy, R, top = 1560.0, 1040.0, 520.0
    x0 = 190.0
    surf = cy - math.sqrt(R * R - (x0 - 500) ** 2)
    if mono:
        cv.drawPath(circle_path(500, 500, 476), paint(mono, a, stroke=18))
        cv.save()
        cv.clipPath(circle_path(500, 500, 452), True)
        cv.translate(0, 70)
        planet = circle_path(500, cy, R)
        cv.save()
        cv.clipPath(planet, skia.ClipOp.kDifference, True)
        cv.drawPath(circle_path(500, top + 95, 235), paint(mono, a, stroke=18))
        cv.restore()
        arc = skia.Path()
        arc.addArc(skia.Rect(500 - R, cy - R, 500 + R, cy + R), 270 - math.degrees(math.asin(900 / R)), 2 * math.degrees(math.asin(900 / R)))
        cv.drawPath(arc, paint(mono, a, stroke=22))
        pts = sigmoid_pts(x0, surf - 18, 815, 185, k=5.2)
        cv.drawPath(path_of(pts[20:]), paint(mono, a, stroke=14))
        cv.drawCircle(*pts[-1], 22, paint(mono, a))
        cv.restore()
        cv.restore()
        return
    cv.save()
    cv.clipPath(circle_path(500, 500, 480), True)
    if ground_disc:
        cv.drawPaint(paint(VOID, a))
        rnd = random.Random(21)
        for _ in range(55):
            cv.drawCircle(rnd.uniform(0, 1000), rnd.uniform(0, 1000), rnd.uniform(0.7, 2.2), paint(FLARE, rnd.uniform(.2, .85) * a))
    cv.translate(0, 70)
    horizon(cv, rise=1.0, cx=500, top=top, R=R, sun_r=235, sun_dy=95, half=900, a=a)
    trajectory(cv, x0, surf - 18, 815, 185, p=1.0, k=5.2, w=7, a=a)
    cv.restore()
    cv.restore()


def watermark(cv, a=1.0):
    """The round icon, top right, on every frame of a Short (brand rule)."""
    x, y, s = WATERMARK
    icon(cv, x, y, s, a=a)


# ---------------------------------------------------------------- type
def text(cv, s, x, y, role="text", size=46, rgb=STAR, a=1.0, align="l", tracking=0.0):
    """Plain text. align l/c/r. tracking in em (mono labels use 0.2)."""
    if not s or a <= 0:
        return 0
    f = font(role, round(size, 1))
    w = measure(s, role, size, tracking)
    x0 = x - w / 2 if align == "c" else x - w if align == "r" else x
    p = paint(rgb, a)
    if tracking:
        for ch in s:
            cv.drawString(ch, x0, y, f, p)
            x0 += f.measureText(ch) + tracking * size
    else:
        cv.drawString(s, x0, y, f, p)
    return w


def gradient_text(cv, s, x, y, role="display_black", size=150, a=1.0, align="l", glow=True, stops=GRADIENT):
    """Text filled with the eclipse gradient (once per frame: the hook's highlighted word)."""
    f = font(role, round(size, 1))
    w = f.measureText(s)
    x0 = x - w / 2 if align == "c" else x - w if align == "r" else x
    sh = gradient(x0, x0 + w, stops)
    blob = skia.TextBlob.MakeFromString(s, f)
    if glow:
        cv.drawTextBlob(blob, x0, y, paint(MAGENTA, 0.5 * a, blur=size * 0.08, shader=sh))
    cv.drawTextBlob(blob, x0, y, paint(MAGENTA, a, shader=sh))
    return w


def label(cv, s, x, y, rgb=HAZE, size=30, a=1.0, align="l"):
    """Upper-case mono label with 0.2em tracking."""
    return text(cv, s.upper(), x, y, "mono", size, rgb, a, align, tracking=0.2)


def pill(cv, s, x, y, rgb, size=30, a=1.0, align="l", fill_a=0.14):
    """A tinted pill with an outline (topic tags, PAID PARTNERSHIP)."""
    tw_ = measure(s, "mono", size, 0.12)
    padx, h = size * 0.8, size * 1.9
    w = tw_ + 2 * padx
    x0 = x - w / 2 if align == "c" else x - w if align == "r" else x
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y, w, h), h / 2, h / 2)
    cv.drawRRect(rr, paint(rgb, fill_a * a))
    cv.drawRRect(rr, paint(rgb, a, stroke=max(size / 13, 2)))
    text(cv, s, x0 + padx, y + h / 2 + size * 0.36, "mono", size, rgb, a, tracking=0.12)
    return w


def topic_tag(cv, topic, x=90, y=250, a=1.0, size=30):
    return pill(cv, topic.upper(), x, y, TOPIC[topic.upper()], size=size, a=a)


def series_badge(cv, name, x=90, y=250, a=1.0, size=30):
    rgb, sub = SERIES[name.upper()]
    tw_ = max(measure(name.upper(), "display_bold", size * 1.3), measure(sub, "mono", size * 0.7, 0.25))
    w, h = tw_ + 150, size * 5.6
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 26, 26)
    cv.drawRRect(rr, paint(NIGHT, 0.92 * a))
    cv.drawRRect(rr, paint(rgb, 0.35 * a, stroke=12, blur=6))
    cv.drawRRect(rr, paint(rgb, a, stroke=4))
    cv.drawCircle(x + 60, y + h / 2, 16, paint(rgb, a))
    cv.drawCircle(x + 60, y + h / 2, 30, paint(rgb, 0.6 * a, stroke=3))
    label(cv, sub, x + 110, y + h * 0.36, rgb, size * 0.7, a)
    text(cv, name.upper(), x + 110, y + h * 0.72, "display_bold", size * 1.3, STAR, a)
    return w, h


def hook(cv, t, lines, highlight=None, x=90, y=560, size=112, hi_size=150, a=1.0, breathe=True):
    """The frame-0 hook: Unbounded upper case, one highlighted line in the eclipse gradient.
    Fully visible at t=0 (frame 0 must work alone) with a slow periodic breathe for motion."""
    max_w = SAFE[2] - x
    plain = [s for i, s in enumerate(lines) if i != highlight]
    size = fit(plain, "display", size, max_w) if plain else size
    if highlight is not None:
        hi_size = fit([lines[highlight]], "display_black", hi_size, max_w)
    s = 1.0 + (0.012 * math.sin(2 * math.pi * t / 2.4) if breathe else 0.0)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    yy = 0.0
    for i, line in enumerate(lines):
        if i == highlight:
            yy += hi_size * 0.08
            gradient_text(cv, line, 0, yy + hi_size * 0.1, "display_black", hi_size, a)
            yy += hi_size * 1.12
        else:
            text(cv, line, 0, yy, "display", size, STAR, a)
            yy += size * 1.14
    cv.restore()
    return y + yy


def big_number(cv, base, x=540, y=960, size=300, exp=None, a=1.0):
    """A big number in mono with the eclipse gradient; exp draws a superscript (10^80)."""
    w = gradient_text(cv, base, x if exp is None else x - measure(exp, "mono", size * 0.5) / 2, y, "mono", size, a,
                      align="c" if exp is None else "c")
    if exp:
        xe = x - measure(exp, "mono", size * 0.5) / 2 + w / 2 + size * 0.05
        gradient_text(cv, exp, xe, y - size * 0.57, "mono", size * 0.5, a, stops=(ULTRAVIOLET, CYAN))
    return w


def progress_bar(cv, frac, name, value, x=90, y=1090, w=810, a=1.0):
    """A running number as a bar: label left, value right, gradient fill."""
    label(cv, name, x, y, HAZE, 30, a)
    text(cv, value, x + w, y, "mono", 30, STAR, a, align="r", tracking=0.05)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y + 26, w, 26), 13, 13)
    cv.drawRRect(rr, paint(DUSK, a))
    if frac > 0:
        fw = max(26, w * clamp01(frac))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y + 26, fw, 26), 13, 13),
                     paint(MAGENTA, a, shader=gradient(x, x + w, (SUN_PINK, ULTRAVIOLET, CYAN))))


def source_chip(cv, s, y=1420, a=1.0):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(90, y, 900, 80), 16, 16)
    cv.drawRRect(rr, paint(NIGHT, a))
    cv.drawRRect(rr, paint(DUSK, a, stroke=2))
    label(cv, s, 130, y + 50, HAZE, 26, a)


def grid(cv, y0=300, y1=1500, step=90, a=0.8):
    p = skia.Path()
    for x in range(90, 1000, step):
        p.moveTo(x, y0); p.lineTo(x, y1)
    for y in range(y0, y1 + 1, step):
        p.moveTo(90, y); p.lineTo(990, y)
    cv.drawPath(p, paint(DUSK, a, stroke=2))


# ---------------------------------------------------------------- composed frames (the templates)
def frame0(cv, t, topic, lines, highlight=None, bar=None, rise=1.0, loop=None):
    """Frame 0 / hook template: ground, horizon with the sun, topic tag, watermark, hook, optional bar."""
    ground(cv, t, loop)
    horizon(cv, rise=rise)
    topic_tag(cv, topic)
    watermark(cv)
    hook(cv, t, lines, highlight)
    if bar:
        progress_bar(cv, bar[1], bar[0], bar[2])


def data_frame(cv, t, topic, base, exp, caption, sub=None, source="SOURCE · [CITATION]", loop=None):
    ground(cv, t, loop)
    grid(cv)
    topic_tag(cv, topic, y=210)
    watermark(cv)
    big_number(cv, base, 540, 960, 300, exp)
    trajectory(cv, 140, 1060, 940, 1010, p=1.0, k=6, w=6)
    text(cv, caption, 540, 1170, "text", 50, STAR, align="c")
    if sub:
        text(cv, sub, 540, 1232, "text_regular", 38, HAZE, align="c")
    source_chip(cv, source)


def chapter_frame(cv, t, part, title, highlight, marker=0.5, loop=None):
    ground(cv, t, loop)
    watermark(cv)
    label(cv, f"PART {part}", 540, 420, CYAN, 36, align="c")
    text(cv, title, 540, 545, "display", fit([title], "display", 84, 900), STAR, align="c")
    gradient_text(cv, highlight, 540, 690, "display_black", fit([highlight], "display_black", 120, 900), align="c")
    trajectory(cv, 110, 1420, 970, 860, p=1.0, k=6.2, w=8, head=False)
    pts = sigmoid_pts(110, 1420, 970, 860, 6.2)
    mx, my = pts[int(marker * (len(pts) - 1))]
    eclipse_ring(cv, mx, my, 62)


def sponsor_frame(cv, t, line1="[One honest sentence about", line2="why it fits this video.]", loop=None):
    ground(cv, t, loop)
    horizon(cv, top=1520, sun_r=230, sun_dy=100)
    watermark(cv)
    label(cv, "SUPPORTED BY", 540, 600, HAZE, 32, align="c")
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(200, 650, 680, 260), 18, 18)
    p = paint(HAZE, 0.8, stroke=3)
    p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
    cv.drawRRect(rr, p)
    label(cv, "[SPONSOR LOGO]", 540, 790, HAZE, 34, align="c")
    text(cv, line1, 540, 1030, "text", 46, STAR, align="c")
    text(cv, line2, 540, 1092, "text", 46, STAR, align="c")
    pill(cv, "PAID PARTNERSHIP", 540, 1150, SUN_PINK, 26, align="c")


def demo(outdir):
    os.makedirs(outdir, exist_ok=True)
    frames = {
        "hook": lambda cv: frame0(cv, 0.0, "ENERGY", ["WHY DOES", "CHARGING", "SLOW", "AT 80%?"], 2, ("BATTERY", 0.8, "80%")),
        "data": lambda cv: data_frame(cv, 0.0, "SCIENCE", "10", "80", "atoms in the observable universe", "(a common estimate)"),
        "chapter": lambda cv: chapter_frame(cv, 0.0, 2, "THE INFLECTION", "POINT"),
        "sponsor": lambda cv: sponsor_frame(cv, 0.0),
    }
    for name, fn in frames.items():
        surf, cv = new_frame()
        fn(cv)
        to_pil(surf).save(os.path.join(outdir, f"{name}.png"))
        print(os.path.join(outdir, f"{name}.png"))
    # the trajectory drawing itself, for motion reference
    surf, cv = new_frame(1080, 640)
    ground(cv, 0, None, n=40, w=1080, h=640)
    for i, p in enumerate((0.15, 0.35, 0.55, 0.75, 1.0)):
        trajectory(cv, 80, 600 - i * 0 , 1000, 80, p=p, w=6, a=0.25 + 0.15 * i, head=(p == 1.0))
    to_pil(surf).save(os.path.join(outdir, "trajectory-draw-on.png"))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        demo(sys.argv[2] if len(sys.argv) > 2 else "brand/reference")
    else:
        print(__doc__)
