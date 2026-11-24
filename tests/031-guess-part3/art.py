"""031 pictures: original vector art (skia), BOX x BOX RGB float arrays. Smooth shapes, no pixel look.
strawberry (round 1), sunflower (round 2), watermelon close-up with the rind at the top (round 3)."""
import math
import numpy as np
import skia
from sim import BOX

C = BOX / 2


def _col(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _surface(bg):
    s = skia.Surface(BOX, BOX)
    c = s.getCanvas()
    c.clear(_col(bg))
    return s, c


def _to_rgb(s):
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    return a[..., :3].astype(float)


def _P(**kw):
    p = skia.Paint(AntiAlias=True)
    for k, v in kw.items():
        getattr(p, 'set' + k)(v)
    return p


def strawberry():
    s, c = _surface('#9FE3C9')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), BOX * 0.75, [_col('#C4F2DE'), _col('#6CCCA8')])))
    # berry body: rounded heart / cone
    body = skia.Path()
    top, bot = 190, 690
    body.moveTo(C, bot)
    body.cubicTo(C - 120, bot - 40, C - 330, 430, C - 300, 300)
    body.cubicTo(C - 280, 200, C - 120, top, C, top + 20)
    body.cubicTo(C + 120, top, C + 280, 200, C + 300, 300)
    body.cubicTo(C + 330, 430, C + 120, bot - 40, C, bot)
    body.close()
    sh = skia.Path(body); sh.offset(10, 16)
    c.drawPath(sh, skia.Paint(AntiAlias=True, Color=_col('#2F7F63', 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.drawPath(body, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C - 70, 330), 420, [_col('#FF6B6B'), _col('#E8263A'), _col('#B3122A')], [0.0, 0.55, 1.0])))
    # seeds: little yellow teardrops in a curved lattice, each in a small dimple
    c.save(); c.clipPath(body, doAntiAlias=True)
    rng = np.random.default_rng(3)
    for row in range(14):
        y = 250 + row * 34
        off = (row % 2) * 27
        for k in range(-8, 9):
            x = C + k * 54 + off + rng.uniform(-4, 4)
            yy = y + 0.00045 * (x - C) ** 2 + rng.uniform(-3, 3)
            c.drawOval(skia.Rect(x - 10, yy - 7, x + 10, yy + 9), skia.Paint(AntiAlias=True, Color=_col('#9E1023', 150)))
            c.save(); c.translate(x, yy); c.rotate(rng.uniform(-20, 20))
            c.drawOval(skia.Rect(-5, -8, 5, 7), skia.Paint(AntiAlias=True, Color=_col('#FFE27A')))
            c.restore()
    c.restore()
    c.drawArc(skia.Rect(C - 250, 250, C + 120, 600), 200, 50, False,
              skia.Paint(AntiAlias=True, Color=_col('#FFFFFF', 90), Style=skia.Paint.kStroke_Style, StrokeWidth=20, StrokeCap=skia.Paint.kRound_Cap))
    # green leaves (calyx) on top + stem
    for k in range(7):
        a = math.radians(-170 + k * 27)
        ln = 150 if k % 2 == 0 else 120
        bx, by = C, top + 40
        tip = (bx + ln * math.cos(a) * 1.25, by + ln * math.sin(a) * 0.55 + 25)
        nrm = (-math.sin(a), math.cos(a))
        w = 26
        p = skia.Path()
        p.moveTo(bx + nrm[0] * w, by + nrm[1] * w * 0.5)
        p.quadTo((bx + tip[0]) / 2 + nrm[0] * w, (by + tip[1]) / 2 + nrm[1] * w, *tip)
        p.quadTo((bx + tip[0]) / 2 - nrm[0] * w, (by + tip[1]) / 2 - nrm[1] * w, bx - nrm[0] * w, by - nrm[1] * w * 0.5)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col(['#1E8A3A', '#2FB052'][k % 2])))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(C - 12, top - 70, C + 12, top + 30), 12, 12), skia.Paint(AntiAlias=True, Color=_col('#2A7A35')))
    return _to_rgb(s)


def sunflower():
    s, c = _surface('#7FB8F0')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (0, BOX)], [_col('#9CCBF7'), _col('#5E9CE0')])))
    cx, cy = C, C
    # two rings of petals
    for ring, (n, L, Wd, col, rot) in enumerate([(22, 330, 52, '#F2A818', 8), (22, 300, 48, '#FFD23F', 0)]):
        for k in range(n):
            a = math.radians(k * 360 / n + rot)
            c.save(); c.translate(cx, cy); c.rotate(math.degrees(a))
            p = skia.Path()
            p.moveTo(120, 0)
            p.quadTo(220, -Wd, L, 0)
            p.quadTo(220, Wd, 120, 0)
            p.close()
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col(col)))
            c.drawLine(150, 0, L - 30, 0, skia.Paint(AntiAlias=True, Color=_col('#E08A10', 110), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
            c.restore()
    # seed disc
    c.drawCircle(cx + 6, cy + 10, 175, skia.Paint(AntiAlias=True, Color=_col('#3A230F', 110), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
    c.drawCircle(cx, cy, 172, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (cx, cy), 172, [_col('#2A1A0C'), _col('#5A3517'), _col('#7A4A1E')], [0.0, 0.7, 1.0])))
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(420):
        r = 8.0 * math.sqrt(i)
        if r > 162:
            break
        a = i * golden
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        sz = 3.2 + r / 60
        c.drawOval(skia.Rect(x - sz, y - sz * 0.8, x + sz, y + sz * 0.8),
                   skia.Paint(AntiAlias=True, Color=_col('#C08A3E' if i % 3 else '#E2B45E', 220)))
    return _to_rgb(s)


def watermelon():
    """Close-up: red flesh with black seeds fills the box; the rind is a band along the TOP only."""
    s, c = _surface('#E8384F')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, BOX * 1.1), BOX * 1.0, [_col('#FF5A6A'), _col('#EE3A50'), _col('#D42640')], [0.0, 0.6, 1.0])))
    # juicy sheen streaks
    rng = np.random.default_rng(8)
    for k in range(40):
        x = rng.uniform(0, BOX); y = rng.uniform(190, BOX)
        c.drawLine(x, y, x + rng.uniform(-30, 30), y + rng.uniform(30, 70),
                   skia.Paint(AntiAlias=True, Color=_col('#FF8A96', 90), StrokeWidth=4, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    # seeds: black teardrops in loose arcs
    for row in range(5):
        yb = 300 + row * 95
        for k in range(7):
            x = 60 + k * 106 + (row % 2) * 50 + rng.uniform(-14, 14)
            y = yb + 30 * math.sin(x / BOX * math.pi) + rng.uniform(-12, 12)
            c.save(); c.translate(x, y); c.rotate(rng.uniform(-35, 35))
            p = skia.Path(); p.moveTo(0, -20); p.cubicTo(13, -8, 12, 14, 0, 16); p.cubicTo(-12, 14, -13, -8, 0, -20); p.close()
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col('#1A1414')))
            c.drawOval(skia.Rect(-4, -10, 1, -2), skia.Paint(AntiAlias=True, Color=_col('#8A7A7A')))
            c.restore()
    # rind band at the top: pale flesh edge, white-green, light green, dark green with stripes
    def band(y0, y1, col):
        p = skia.Path()
        p.moveTo(0, 0); p.lineTo(BOX, 0); p.lineTo(BOX, y1)
        for i in range(40, -1, -1):
            x = BOX * i / 40
            p.lineTo(x, y1 + 18 * math.sin(x / BOX * math.pi))
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col(col)))
    band(0, 210, '#FFB3B8')
    band(0, 185, '#E9F7D2')
    band(0, 150, '#9ED46A')
    band(0, 110, '#2E7D32')
    for k in range(9):
        x0 = k * 95 - 20
        p = skia.Path(); p.moveTo(x0, 0)
        for j in range(12):
            p.lineTo(x0 + 18 * math.sin(j * 1.3) + j * 2, j * 10)
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col('#1B5E20'), StrokeWidth=26, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    return _to_rgb(s)


if __name__ == "__main__":
    from PIL import Image
    ims = [Image.fromarray(f().astype(np.uint8)) for f in (strawberry, sunflower, watermelon)]
    sheet = Image.new("RGB", (BOX * 3 + 40, BOX), (10, 10, 20))
    for k, im in enumerate(ims):
        sheet.paste(im, (k * (BOX + 20), 0))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save("art_sheet.png")
    print("ok")
