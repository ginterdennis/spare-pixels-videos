"""The three looks for 041. Same choreography (common.py), different drawing.

A "Night grid": near-black with a faint drifting grid, Computer Modern (the LaTeX typeface), white
  hairlines, one amber accent. Things draw themselves in with clean wipes.
B "Notebook": cream graph paper, red margin, handwriting (Kalam/Caveat), black ink + red pen, every
  line slightly wobbly and 'boiling' like hand-drawn animation, text traced as outlines then inked.
C "Neon 3D": black space with drifting stars, Space Grotesk, glowing cyan/magenta lines (bloom),
  the switch grid, the big number and the panels tilted in perspective, extruded P = NP.
"""
import math
from contextlib import contextmanager
import numpy as np
import skia
from common import (W, H, A, END, font, tw, text_path, paint, trim, clamp01, prog, e_out, e_io, lerp, rrect,
                    circle, poly, HOOK_Y1, HOOK_Y2, GX0, GY0, GPX, GPY, COLS, ROWS)


class Base:
    _fr = 0
    MATH_AXIS = 0.34
    HOOK_SIZE = 120
    FONTS = {}
    BGC = (0, 0, 0)

    def font_of(self, role):
        return self.FONTS[role]

    # ---------------------------------------------------------------- primitives
    def stroke(self, cv, path, col, w, a=1.0, prg=1.0, kind=None):
        if a <= 0 or prg <= 0:
            return
        cv.drawPath(path, paint(col, a, stroke=w, effect=trim(prg)))

    def fill(self, cv, path, col, a=1.0):
        if a > 0:
            cv.drawPath(path, paint(col, a))

    def bar(self, cv, x0, y0, x1, y1, th, col, a):
        if a > 0:
            cv.drawLine(x0, y0, x1, y1, paint(col, a, stroke=th, cap="butt"))

    def lock_fill(self, cv, body, a):
        self.fill(cv, body, self.BGC, a)

    def text(self, cv, s, x, y, role, size, col, a=1.0, align="c", write=1.0):
        if a <= 0 or write <= 0 or not s:
            return 0
        name = self.font_of(role)
        f = font(name, round(size, 1))
        w = f.measureText(s)
        x0 = x - w / 2 if align == "c" else x - w if align == "r" else x
        self._text(cv, s, x0, y, f, name, size, w, col, a, write, role)
        return w

    def _text(self, cv, s, x0, y, f, name, size, w, col, a, write, role):
        if write < 1:
            cv.save()
            cv.clipRect(skia.Rect(x0 - size, y - size * 1.4, x0 + w * write, y + size * 0.6))
        cv.drawString(s, x0, y, f, paint(col, a))
        if write < 1:
            cv.restore()

    def rich(self, cv, parts, x, y, role, size, a):
        name = self.font_of(role)
        total = sum(tw(s, name, size) for s, _ in parts)
        xx = x - total / 2
        for s, col in parts:
            self.text(cv, s, xx, y, role, size, col, a=a, align="l")
            xx += tw(s, name, size)

    def label(self, cv, s, x, y, size, col, a, align="c"):
        if a <= 0:
            return
        name = self.font_of("label")
        sp = size * 0.16
        total = sum(tw(ch, name, size) + sp for ch in s) - sp
        xx = x - total / 2 if align == "c" else x
        f = font(name, round(size, 1))
        p = paint(col, a)
        for ch in s:
            cv.drawString(ch, xx, y, f, p)
            xx += tw(ch, name, size) + sp

    def power(self, cv, base, exp, x, y, size, col, a):
        name = self.font_of("body")
        wb, we = tw(base, name, size), tw(exp, name, size * 0.6)
        x0 = x - (wb + we + 4) / 2
        self.text(cv, base, x0, y, "body", size, col, a=a, align="l")
        self.text(cv, exp, x0 + wb + 4, y - size * 0.42, "body", size * 0.6, col, a=a, align="l")

    def stamp(self, cv, s, x, y, size, col, a):
        self.text(cv, s, x, y, "display", size, col, a=a)

    def hook_lines(self):
        return [[("This would ", self.INK), ("END", self.ACC)], [("the modern world.", self.INK)]]

    def share_lines(self):
        return [[("Send this to your", self.INK)], [("smartest friend.", self.ACC)]]

    def _two_lines(self, cv, lines, a):
        name = self.font_of("hook")
        wmax = max(sum(tw(s, name, 100) for s, _ in parts) for parts in lines) / 100
        size = min(self.HOOK_SIZE, 960 / wmax)
        for parts, y in zip(lines, (HOOK_Y1, HOOK_Y2)):
            self.rich(cv, parts, 540, y, "hook", size, a)

    def hook_text(self, cv, t, a):
        if a > 0:
            self._two_lines(cv, self.hook_lines(), a)

    def share_text(self, cv, t, a):
        if a > 0:
            self._two_lines(cv, self.share_lines(), a)

    def toggle(self, cv, x, y, pop, on, a, good=False, flash=0.0):
        if pop <= 0:
            return
        w, h = 42 * pop, 24 * pop
        pill = rrect(x, y, w, h, h / 2)
        c_on = self.GOOD if good else self.ACC
        if on:
            self.fill(cv, pill, c_on, a)
        else:
            self.stroke(cv, pill, self.MUTED, 2.5, a)
        kx = x + (w / 2 - h / 2) * (1 if on else -1)
        self.fill(cv, circle(kx, y, h * 0.34), self.BGC if on else self.MUTED, a)
        if flash > 0 and on:
            self.fill(cv, rrect(x, y, w + 10, h + 10, h), self.GOOD, a * flash * 0.35)

    def scanline(self, cv, x0, x1, y, a):
        cv.drawLine(x0, y, x1, y, paint(self.GOOD, a, stroke=5))
        cv.drawLine(x0, y, x1, y, paint(self.GOOD, a * 0.5, stroke=24, blur=10))

    def flash_disc(self, cv, x, y, r, a):
        cv.drawCircle(x, y, r, paint(self.ACC, a * 0.6, blur=r * 0.35))

    def shard(self, cv, path, a):
        self.fill(cv, path, self.INK, a)

    def panel(self, cv, x0, y0, x1, y1, a):
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 22, 22))
        self.stroke(cv, p, self.MUTED, 2, a * 0.6)

    def node(self, cv, x, y, r, act, a):
        if r <= 0:
            return
        self.fill(cv, circle(x, y, r), self.BGC, a)
        self.stroke(cv, circle(x, y, r), self.INK, 3, a)
        if act > 0:
            self.fill(cv, circle(x, y, r * 0.75), self.ACC, a * act)

    def point(self, cv, x, y, r, a):
        cv.drawCircle(x, y, r * 3, paint(self.ACC, a * 0.5, blur=r * 1.5))
        cv.drawCircle(x, y, r, paint(self.INK, a))

    def bloom(self, cv, t, b, a):
        if a <= 0:
            return
        r = 40 + 1300 * e_out(b, 2.5)
        self.stroke(cv, circle(540, 960, r), self.ACC, 6, a * (1 - b))
        cv.save()
        clip = skia.Path(); clip.addCircle(540, 960, r)
        cv.clipPath(clip, doAntiAlias=True)
        step = 90
        for k in range(-7, 8):
            gx = 540 + k * step
            self.stroke(cv, poly([(gx, 960 - r), (gx, 960 + r)]), self.MUTED, 2, a * 0.5)
        for k in range(-12, 13):
            gy = 960 + k * step
            self.stroke(cv, poly([(540 - r, gy), (540 + r, gy)]), self.MUTED, 2, a * 0.5)
        cv.restore()
        self.point(cv, 540, 960, 10 * (1 - b) + 2, a * (1 - b))

    def rewind(self, cv, t, amt):
        rng = np.random.default_rng(int(t * 30))
        for _ in range(14):
            y = rng.uniform(150, 1750)
            cv.drawLine(0, y, W, y, paint(self.INK, amt * rng.uniform(0.05, 0.25), stroke=rng.uniform(2, 10)))

    def glitch(self, cv, t, amt):
        rng = np.random.default_rng(int(t * 60))
        for _ in range(5):
            y = rng.uniform(450, 800)
            cv.drawRect(skia.Rect(0, y, W, y + rng.uniform(4, 22)), paint(self.ACC, amt * 0.35))

    @contextmanager
    def plane(self, cv, kind, t, cy=None):
        yield

    @contextmanager
    def camera(self, cv, t):
        yield

    def bg(self, cv, t):
        cv.clear(skia.Color(*self.BGC))

    def overlay(self, cv, t):
        pass

    def finish(self, surf, arr, t):
        pass


# ===================================================================================== A
class NightGrid(Base):
    name = "A-night-grid"
    FONTS = {"hook": "cmb10", "math": "cmr10", "display": "cmr10", "body": "cmr10", "mono": "cmtt10",
             "label": "cmr10", "proof": "cmti10"}
    BGC = (11, 12, 17)
    INK = (240, 238, 230)
    MUTED = (124, 129, 146)
    ACC = (255, 184, 72)
    GOOD = (122, 214, 156)
    BAD = (240, 112, 102)
    MATH_AXIS = 0.25
    HOOK_SIZE = 124

    def __init__(self):
        self.vig = skia.GradientShader.MakeRadial(skia.Point(540, 900), 1250,
                                                  [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 170)],
                                                  [0.0, 0.55, 1.0])

    def bg(self, cv, t):
        cv.clear(skia.Color(*self.BGC))
        off = (t * 14) % 60
        minor = paint((255, 255, 255), 0.045, stroke=1.2)
        major = paint((255, 255, 255), 0.085, stroke=1.6)
        for k in range(-1, 20):
            x = k * 60 + off
            cv.drawLine(x, 0, x, H, major if (k % 5 == 0) else minor)
        for k in range(-1, 34):
            y = k * 60 + off
            cv.drawLine(0, y, W, y, major if (k % 5 == 0) else minor)

    def overlay(self, cv, t):
        p = skia.Paint(Shader=self.vig)
        cv.drawRect(skia.Rect(0, 0, W, H), p)

    def _text(self, cv, s, x0, y, f, name, size, w, col, a, write, role):
        if write < 1:
            cv.save()
            cv.clipRect(skia.Rect(x0 - size, y - size * 1.4, x0 + w * write, y + size * 0.6))
        cv.drawString(s, x0, y, f, paint(col, a))
        if write < 1:
            cv.restore()
            xe = x0 + w * write
            cv.drawLine(xe, y - size * 0.75, xe, y + size * 0.1, paint(self.ACC, a, stroke=max(2, size * 0.02)))


# ===================================================================================== B
class Notebook(Base):
    name = "B-notebook"
    FONTS = {"hook": "kalam-latin-700-normal", "math": "kalam-latin-700-normal", "display": "kalam-latin-700-normal",
             "body": "kalam-latin-400-normal", "mono": "kalam-latin-700-normal", "label": "kalam-latin-700-normal",
             "proof": "caveat-latin-700-normal"}
    BGC = (247, 243, 231)
    INK = (26, 28, 38)
    MUTED = (112, 118, 134)
    ACC = (212, 38, 56)
    GOOD = (22, 132, 76)
    BAD = (212, 38, 56)
    MATH_AXIS = 0.36
    HOOK_SIZE = 126

    def __init__(self):
        rng = np.random.default_rng(3)
        g = (rng.normal(0, 1, (H // 2, W // 2)) * 9).clip(-30, 30)
        tex = np.zeros((H // 2, W // 2, 4), np.uint8)
        tex[..., 0] = tex[..., 1] = tex[..., 2] = (128 + g).astype(np.uint8)
        tex[..., 3] = 255
        self.grain = skia.Image.fromarray(tex)
        self.vig = skia.GradientShader.MakeRadial(skia.Point(540, 960), 1300,
                                                  [skia.Color(0, 0, 0, 0), skia.Color(60, 40, 0, 0), skia.Color(60, 40, 0, 70)],
                                                  [0.0, 0.6, 1.0])

    def _seed(self):
        return self._fr // 3          # line boil: wobble pattern changes every 3 frames

    def stroke(self, cv, path, col, w, a=1.0, prg=1.0, kind=None):
        if a <= 0 or prg <= 0:
            return
        dev = 1.4 + w * 0.08
        for k, (aa, ww, dd) in enumerate(((1.0, w, dev), (0.35, w * 0.55, dev * 1.6))):
            eff = skia.DiscretePathEffect.Make(16, dd, self._seed() * 7 + k * 101)
            if prg < 1:
                eff = skia.PathEffect.MakeCompose(eff, skia.TrimPathEffect.Make(0, clamp01(prg)))
            cv.drawPath(path, paint(col, a * aa, stroke=ww, effect=eff))

    def bar(self, cv, x0, y0, x1, y1, th, col, a):
        self.stroke(cv, poly([(x0, y0), (x1, y1)]), col, th, a)

    def _text(self, cv, s, x0, y, f, name, size, w, col, a, write, role):
        if write < 1:
            path, _ = text_path(s, name, size, x0, y, align="l")
            cv.drawPath(path, paint(col, a, stroke=max(1.5, size * 0.022),
                                    effect=skia.TrimPathEffect.Make(0, clamp01(write * 1.5))))
            fa = clamp01(write * 2.2 - 1.2)
            if fa > 0:
                cv.drawString(s, x0, y, f, paint(col, a * fa))
            return
        cv.drawString(s, x0, y, f, paint(col, a))

    def bg(self, cv, t):
        cv.clear(skia.Color(*self.BGC))
        blue = paint((96, 150, 214), 0.28, stroke=1.4)
        blue2 = paint((96, 150, 214), 0.45, stroke=2)
        for k in range(0, 24):
            x = 30 + k * 48
            cv.drawLine(x, 0, x, H, blue2 if k % 5 == 0 else blue)
        for k in range(0, 41):
            y = 24 + k * 48
            cv.drawLine(0, y, W, y, blue2 if k % 5 == 0 else blue)
        cv.drawLine(96, 0, 96, H, paint((220, 70, 80), 0.55, stroke=3))

    def overlay(self, cv, t):
        p = skia.Paint(BlendMode=skia.BlendMode.kOverlay)
        p.setAlphaf(0.5)
        cv.drawImageRect(self.grain, skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)
        cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=self.vig))

    def hook_text(self, cv, t, a):
        super().hook_text(cv, t, a)
        if a > 0:
            name = self.font_of("hook")
            size = min(self.HOOK_SIZE, 960 / (max(tw("This would END", name, 100), tw("the modern world.", name, 100)) / 100))
            w_all = tw("This would END", name, size)
            x1 = 540 + w_all / 2
            x0 = x1 - tw("END", name, size)
            self.stroke(cv, poly([(x0 - 4, HOOK_Y1 + 16), ((x0 + x1) / 2, HOOK_Y1 + 22), (x1 + 6, HOOK_Y1 + 12)]), self.ACC, 7, a)

    def scanline(self, cv, x0, x1, y, a):
        cv.drawRect(skia.Rect(x0, y - 16, x1, y + 16), paint((120, 220, 90), a * 0.45))   # highlighter
        self.stroke(cv, poly([(x0, y), (x1, y)]), self.GOOD, 4, a)

    def toggle(self, cv, x, y, pop, on, a, good=False, flash=0.0):
        if pop <= 0:
            return
        w, h = 42 * pop, 24 * pop
        pill = rrect(x, y, w, h, h / 2)
        c_on = self.GOOD if good else self.INK
        if on:
            self.fill(cv, pill, c_on, a * 0.9)
        self.stroke(cv, pill, self.INK, 2.6, a)
        kx = x + (w / 2 - h / 2) * (1 if on else -1)
        self.fill(cv, circle(kx, y, h * 0.3), self.BGC if on else self.INK, a)
        if flash > 0 and on:
            cv.drawRect(skia.Rect(x - w / 2 - 4, y - h / 2 - 4, x + w / 2 + 4, y + h / 2 + 4), paint((120, 220, 90), a * flash * 0.5))

    def flash_disc(self, cv, x, y, r, a):
        # a pen-drawn burst instead of light
        for k in range(14):
            ang = k / 14 * 2 * math.pi
            self.stroke(cv, poly([(x + math.cos(ang) * r * 0.45, y + math.sin(ang) * r * 0.45),
                                  (x + math.cos(ang) * r, y + math.sin(ang) * r)]), self.ACC, 5, a)

    def point(self, cv, x, y, r, a):
        self.fill(cv, circle(x, y, r), self.INK, a)

    def node(self, cv, x, y, r, act, a):
        if r <= 0:
            return
        self.fill(cv, circle(x, y, r), self.BGC, a)
        if act > 0:
            self.fill(cv, circle(x, y, r * 0.8), self.ACC, a * act)
        self.stroke(cv, circle(x, y, r), self.INK, 3, a)

    def rewind(self, cv, t, amt):
        # eraser smudges
        rng = np.random.default_rng(int(t * 30))
        for _ in range(9):
            y = rng.uniform(250, 1650); x = rng.uniform(-100, 600)
            cv.drawRect(skia.Rect(x, y, x + rng.uniform(300, 700), y + rng.uniform(20, 60)),
                        paint(self.BGC, amt * 0.8, blur=8))

    def glitch(self, cv, t, amt):
        rng = np.random.default_rng(int(t * 60))
        for _ in range(4):
            y = rng.uniform(470, 760)
            self.stroke(cv, poly([(rng.uniform(100, 400), y), (rng.uniform(600, 980), y + rng.uniform(-20, 20))]), self.ACC, 4, amt)

    def finish(self, surf, arr, t):
        pass


# ===================================================================================== C
def _persp(cx, cy, w, h, rx=0.0, ry=0.0, f=1500.0, sc=1.0, pcx=None, pcy=None):
    pcx = cx if pcx is None else pcx
    pcy = cy if pcy is None else pcy
    src, dst = [], []
    for x, y in ((cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)):
        X, Y, Z = (x - cx) * sc, (y - cy) * sc, 0.0
        Y, Z = Y * math.cos(rx) - Z * math.sin(rx), Y * math.sin(rx) + Z * math.cos(rx)
        X, Z = X * math.cos(ry) + Z * math.sin(ry), -X * math.sin(ry) + Z * math.cos(ry)
        k = f / (f + Z)
        src.append(skia.Point(x, y))
        dst.append(skia.Point(pcx + X * k, pcy + Y * k))
    m = skia.Matrix()
    m.setPolyToPoly(src, dst)
    return m


class Neon(Base):
    name = "C-neon-3d"
    FONTS = {"hook": "space-grotesk-latin-700-normal", "math": "space-grotesk-latin-700-normal",
             "display": "space-grotesk-latin-700-normal", "body": "space-grotesk-latin-500-normal",
             "mono": "JBMono-Bold", "label": "space-grotesk-latin-500-normal", "proof": "JBMono"}
    BGC = (3, 4, 10)
    INK = (226, 244, 255)
    MUTED = (92, 118, 156)
    ACC = (255, 62, 172)
    GOOD = (70, 255, 186)
    BAD = (255, 176, 46)
    CYAN = (60, 210, 255)
    MATH_AXIS = 0.34
    HOOK_SIZE = 118

    def __init__(self):
        rng = np.random.default_rng(9)
        self.stars = rng.random((240, 3))
        self.sm = skia.Surface(270, 480)
        self.sm2 = skia.Surface(135, 240)
        self.vig = skia.GradientShader.MakeRadial(skia.Point(540, 960), 1250,
                                                  [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 190)],
                                                  [0.0, 0.5, 1.0])

    def stroke(self, cv, path, col, w, a=1.0, prg=1.0, kind=None):
        if a <= 0 or prg <= 0:
            return
        core = tuple(int(lerp(c, 255, 0.45)) for c in col)
        cv.drawPath(path, paint(col, a, stroke=w * 1.25, effect=trim(prg)))
        cv.drawPath(path, paint(core, a, stroke=max(1.5, w * 0.45), effect=trim(prg)))

    def _text(self, cv, s, x0, y, f, name, size, w, col, a, write, role):
        if write < 1:
            cv.save()
            cv.clipRect(skia.Rect(x0 - size, y - size * 1.4, x0 + w * write, y + size * 0.6))
        if role in ("math", "hook", "display") and size >= 90:
            depth = int(min(14, size / 18))
            dark = tuple(int(c * 0.28) for c in col)
            for k in range(depth, 0, -1):
                cv.drawString(s, x0 + k * 1.1, y + k * 1.5, f, paint(dark, a))
        cv.drawString(s, x0, y, f, paint(col, a))
        if write < 1:
            cv.restore()
            xe = x0 + w * write
            cv.drawLine(xe, y - size * 0.8, xe, y + size * 0.12, paint((255, 255, 255), a, stroke=max(3, size * 0.03)))

    def bg(self, cv, t):
        cv.clear(skia.Color(*self.BGC))
        # drifting stars (parallax)
        for x, y, z in self.stars:
            sp = (1 + (z > 0.6)) * H / END          # 1 or 2 screen heights per video: periodic over END
            yy = (y * H - t * sp) % H
            r = 0.8 + 2.2 * z
            cv.drawCircle(x * W, yy, r, paint((150, 200, 255), 0.25 + 0.5 * z))
        # perspective floor at the bottom, scrolling toward the viewer
        hy = 1560
        p = paint(self.CYAN, 0.22, stroke=2)
        for k in range(-12, 13):
            cv.drawLine(540 + k * 40, hy, 540 + k * 260, H, p)
        off = (t * round(0.9 * END) / END) % 1   # periodic over END
        for j in range(8):
            u = ((j + off) / 8) ** 2
            y = hy + (H - hy) * u
            cv.drawLine(0, y, W, y, paint(self.CYAN, 0.08 + 0.25 * u, stroke=2))

    @contextmanager
    def plane(self, cv, kind, t, cy=None):
        m = None
        if kind == "grid":
            gw, gh = (COLS - 1) * GPX + 120, (ROWS - 1) * GPY + 100
            gcx, gcy = GX0 + (COLS - 1) * GPX / 2, GY0 + (ROWS - 1) * GPY / 2
            m = _persp(gcx, gcy, gw, gh, rx=math.radians(-34), ry=math.radians(6 * math.sin(t * 0.9)), f=1400,
                       sc=1.0, pcy=gcy - 10)
        elif kind == "sudoku":
            m = _persp(540, 820, 800, 800, rx=math.radians(-12), ry=math.radians(9 * math.sin(t * 0.8)), f=1700)
        elif kind == "number":
            m = _persp(540, 850, 900, 700, rx=math.radians(-8), ry=math.radians(14 * math.sin(t * 0.7)), f=1600)
        elif kind == "panel" and cy is not None:
            side = {690: 1, 1040: -1, 1370: 1}.get(int(cy), 1)
            m = _persp(540, cy, 920, 320, ry=math.radians(13 * side), f=1500)
        elif kind == "locks":
            m = _persp(540, 1000, 900, 700, rx=math.radians(-10), ry=math.radians(8 * math.sin(t * 1.1)), f=1500)
        if m is not None:
            cv.save(); cv.concat(m)
        try:
            yield
        finally:
            if m is not None:
                cv.restore()

    @contextmanager
    def camera(self, cv, t):
        w = 2 * math.pi * t / END                  # periodic over END: the last frame flows into frame 0
        s = 1.0 + 0.015 * math.sin(2 * w)
        cv.save()
        cv.translate(540, 960); cv.rotate(0.6 * math.sin(w)); cv.scale(s, s); cv.translate(-540, -960)
        try:
            yield
        finally:
            cv.restore()

    def panel(self, cv, x0, y0, x1, y1, a):
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), 22, 22))
        self.fill(cv, p, (10, 16, 34), a * 0.85)
        self.stroke(cv, p, self.CYAN, 2.5, a * 0.8)

    def toggle(self, cv, x, y, pop, on, a, good=False, flash=0.0):
        if pop <= 0:
            return
        w, h = 42 * pop, 24 * pop
        pill = rrect(x, y, w, h, h / 2)
        c_on = self.GOOD if good else self.ACC
        if on:
            self.fill(cv, pill, c_on, a)
        else:
            cv.drawPath(pill, paint(self.CYAN, a * 0.7, stroke=2.2))
        kx = x + (w / 2 - h / 2) * (1 if on else -1)
        self.fill(cv, circle(kx, y, h * 0.32), (255, 255, 255) if on else self.CYAN, a)
        if flash > 0 and on:
            self.fill(cv, rrect(x, y, w + 8, h + 8, h), self.GOOD, a * flash * 0.5)

    def lock_fill(self, cv, body, a):
        self.fill(cv, body, (8, 12, 28), a)

    def shard(self, cv, path, a):
        self.fill(cv, path, self.ACC, a)

    def overlay(self, cv, t):
        cv.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=self.vig))

    def finish(self, surf, arr, t):
        """Neon bloom: blur a small copy of the frame and add it back."""
        img = surf.makeImageSnapshot()
        samp = skia.SamplingOptions(skia.FilterMode.kLinear)
        cv = surf.getCanvas()
        for s, k, sig, alpha in ((self.sm, 4, 3.0, 0.75), (self.sm2, 8, 4.0, 0.6)):
            sc = s.getCanvas()
            sc.clear(skia.ColorBLACK)
            sc.drawImageRect(img, skia.Rect(0, 0, W / k, H / k), samp)
            p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(sig, sig), BlendMode=skia.BlendMode.kPlus)
            p.setAlphaf(alpha)
            cv.save(); cv.scale(k, k)
            cv.drawImage(s.makeImageSnapshot(), 0, 0, samp, p)
            cv.restore()


STYLES = {"A": NightGrid, "B": Notebook, "C": Neon}
