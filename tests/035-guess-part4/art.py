"""035 pictures: original vector art (skia), BOX x BOX RGB float arrays. Smooth shapes, no pixel look.
orange slice (round 1), pizza (round 2), peacock feather close-up (round 3: the eye-spot looks like an eye)."""
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


def orange():
    s, c = _surface('#2E6FB8')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), BOX * 0.8, [_col('#5FA3E8'), _col('#2A5FA8')])))
    R = 320
    c.drawCircle(C + 10, C + 16, R, skia.Paint(AntiAlias=True, Color=_col('#10284A', 130), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16)))
    c.drawCircle(C, C, R, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((C - 60, C - 60), R * 1.2,
                                                                                       [_col('#FFA62B'), _col('#F07A0C')])))
    c.drawCircle(C, C, R - 26, skia.Paint(AntiAlias=True, Color=_col('#FFF3DC')))           # pith
    n = 11
    rng = np.random.default_rng(5)
    for k in range(n):
        a0 = 2 * math.pi * k / n + 0.05; a1 = 2 * math.pi * (k + 1) / n - 0.05
        r0, r1 = 34, R - 46
        p = skia.Path()
        p.moveTo(C + r0 * math.cos((a0 + a1) / 2), C + r0 * math.sin((a0 + a1) / 2))
        p.lineTo(C + r1 * math.cos(a0 + 0.02), C + r1 * math.sin(a0 + 0.02))
        p.arcTo(skia.Rect(C - r1, C - r1, C + r1, C + r1), math.degrees(a0 + 0.02), math.degrees(a1 - a0 - 0.04), False)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((C, C), r1,
                                                                                    [_col('#FFC04D'), _col('#FF9A1F'), _col('#F57F0A')], [0, 0.6, 1])))
        c.save(); c.clipPath(p, doAntiAlias=True)
        for j in range(26):                                    # juice vesicles
            rr = rng.uniform(r0 + 20, r1 - 10); aa = rng.uniform(a0, a1)
            x, y = C + rr * math.cos(aa), C + rr * math.sin(aa)
            c.save(); c.translate(x, y); c.rotate(math.degrees(aa))
            c.drawOval(skia.Rect(-22, -6, 22, 6), skia.Paint(AntiAlias=True, Color=_col('#FFE2A0', 110)))
            c.restore()
        c.restore()
    c.drawCircle(C, C, 30, skia.Paint(AntiAlias=True, Color=_col('#FFF3DC')))
    c.drawArc(skia.Rect(C - R + 40, C - R + 40, C + R - 40, C + R - 40), 200, 60, False,
              skia.Paint(AntiAlias=True, Color=_col('#FFFFFF', 90), Style=skia.Paint.kStroke_Style, StrokeWidth=14, StrokeCap=skia.Paint.kRound_Cap))
    return _to_rgb(s)


def pizza():
    s, c = _surface('#C9A27A')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (BOX, BOX)], [_col('#D9B48A'), _col('#B98A5C')])))      # wooden board
    rng = np.random.default_rng(11)
    for k in range(18):
        y = 20 + k * 42
        c.drawLine(0, y, BOX, y + rng.uniform(-10, 10), skia.Paint(AntiAlias=True, Color=_col('#9A6E44', 60), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    R = 340
    c.drawCircle(C + 8, C + 14, R, skia.Paint(AntiAlias=True, Color=_col('#5A3A1A', 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.drawCircle(C, C, R, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((C, C), R, [_col('#F2C27A'), _col('#E0A050'), _col('#B8702C')], [0.8, 0.93, 1])))
    for k in range(40):                                        # charred crust spots
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(R - 34, R - 8)
        c.drawOval(skia.Rect(C + r * math.cos(a) - 10, C + r * math.sin(a) - 6, C + r * math.cos(a) + 10, C + r * math.sin(a) + 6),
                   skia.Paint(AntiAlias=True, Color=_col('#6E3A14', 130), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3)))
    c.drawCircle(C, C, R - 44, skia.Paint(AntiAlias=True, Color=_col('#C8321E')))     # sauce
    # melted cheese: blobby patches
    for k in range(26):
        a = rng.uniform(0, 2 * math.pi); r = math.sqrt(rng.uniform(0, 1)) * (R - 90)
        x, y = C + r * math.cos(a), C + r * math.sin(a)
        p = skia.Path(); m = 9; rr0 = rng.uniform(45, 80)
        for j in range(m + 1):
            th = 2 * math.pi * j / m; rr = rr0 * rng.uniform(0.7, 1.2)
            px, py = x + rr * math.cos(th), y + rr * math.sin(th)
            if j == 0: p.moveTo(px, py)
            else: p.lineTo(px, py)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col('#FFE28A', 235), PathEffect=skia.CornerPathEffect.Make(30)))
    # pepperoni
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2); r = 120 + 100 * (k % 2) + rng.uniform(-20, 20)
        if k == 8: r = 0
        x, y = C + r * math.cos(a), C + r * math.sin(a)
        c.drawCircle(x + 3, y + 4, 52, skia.Paint(AntiAlias=True, Color=_col('#5A1008', 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4)))
        c.drawCircle(x, y, 52, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial((x - 14, y - 14), 60, [_col('#D2402A'), _col('#A8241A')])))
        for j in range(5):
            c.drawCircle(x + rng.uniform(-30, 30), y + rng.uniform(-30, 30), rng.uniform(4, 7), skia.Paint(AntiAlias=True, Color=_col('#F08A6A', 160)))
    # basil leaves
    for k in range(5):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(60, 230)
        x, y = C + r * math.cos(a), C + r * math.sin(a)
        c.save(); c.translate(x, y); c.rotate(rng.uniform(0, 360))
        p = skia.Path(); p.moveTo(-34, 0); p.quadTo(0, -26, 34, 0); p.quadTo(0, 26, -34, 0); p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col('#2F8A3A')))
        c.drawLine(-28, 0, 28, 0, skia.Paint(AntiAlias=True, Color=_col('#1E5E28'), StrokeWidth=2, Style=skia.Paint.kStroke_Style))
        c.restore()
    # slice cuts
    for k in range(4):
        a = math.pi / 4 * k + 0.2
        c.drawLine(C - (R - 10) * math.cos(a), C - (R - 10) * math.sin(a), C + (R - 10) * math.cos(a), C + (R - 10) * math.sin(a),
                   skia.Paint(AntiAlias=True, Color=_col('#7A2A14', 90), StrokeWidth=4, Style=skia.Paint.kStroke_Style))
    return _to_rgb(s)


def peacock():
    """Close-up of a peacock feather's eye-spot: it fills the box, fine barbs everywhere."""
    s, c = _surface('#0F3A2A')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C + 40), BOX * 0.75, [_col('#3A8A3A'), _col('#21602E'), _col('#0E3422')], [0, 0.6, 1])))
    ex, ey = C, C + 20
    rng = np.random.default_rng(21)
    # shaft from the bottom up to the eye
    c.drawLine(C, BOX + 10, C, ey + 200, skia.Paint(AntiAlias=True, Color=_col('#E8E0B0', 170), StrokeWidth=9, Style=skia.Paint.kStroke_Style))
    # outer barbs: fine strands curving outwards from the shaft, golden green
    for side in (-1, 1):
        for k in range(95):
            y0 = BOX + 40 - k * 9
            p = skia.Path(); p.moveTo(C, y0)
            p.cubicTo(C + side * 120, y0 - 60, C + side * 260, y0 - 110, C + side * 430, y0 - 120)
            col = ['#A8D050', '#78B040', '#D0C050', '#58A040'][k % 4]
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=_col(col, 120), StrokeWidth=2.6, Style=skia.Paint.kStroke_Style))
    soft = lambda r: skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r)
    def ring(rx, ry, dy, col, blur=6, shader=None):
        p = skia.Path(); p.addOval(skia.Rect(ex - rx, ey - ry + dy, ex + rx, ey + ry + dy))
        paint = skia.Paint(AntiAlias=True, Color=_col(col), MaskFilter=soft(blur))
        if shader is not None: paint.setShader(shader)
        c.drawPath(p, paint)
    ring(318, 350, -6, '#C8D85A', 10)                 # pale gold-green fringe
    ring(290, 318, 0, '#A07A2E', 6)                   # bronze
    ring(262, 286, 10, '#C89A48', 5)                  # copper highlight
    ring(244, 262, 16, '#1E9478', 6, skia.GradientShader.MakeRadial((ex - 60, ey - 50), 320, [_col('#62E0B8'), _col('#22A084'), _col('#127058')]))
    # dark blue centre: a rounded kidney (small notch at the top), soft edge
    hp = skia.Path()
    hx, hy, hs = ex, ey + 46, 150
    hp.moveTo(hx, hy - hs * 0.62)
    hp.cubicTo(hx + hs * 0.55, hy - hs * 1.02, hx + hs * 1.12, hy - hs * 0.55, hx + hs * 1.02, hy + hs * 0.18)
    hp.cubicTo(hx + hs * 0.92, hy + hs * 0.82, hx + hs * 0.35, hy + hs * 1.02, hx, hy + hs * 1.0)
    hp.cubicTo(hx - hs * 0.35, hy + hs * 1.02, hx - hs * 0.92, hy + hs * 0.82, hx - hs * 1.02, hy + hs * 0.18)
    hp.cubicTo(hx - hs * 1.12, hy - hs * 0.55, hx - hs * 0.55, hy - hs * 1.02, hx, hy - hs * 0.62)
    hp.close()
    c.drawPath(hp, skia.Paint(AntiAlias=True, MaskFilter=soft(4), Shader=skia.GradientShader.MakeRadial((hx - 40, hy - 40), 210,
                                                                                  [_col('#3E72F0'), _col('#1C34A8'), _col('#0C1658')], [0, 0.6, 1])))
    # barbs across the eye: radial strands from the centre (the feather texture)
    for k in range(220):
        a = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(20, 120); r1 = rng.uniform(200, 380)
        col = ['#FFFFFF', '#9FFFE0', '#FFE8A0'][k % 3]
        c.drawLine(hx + r0 * math.cos(a), hy + r0 * math.sin(a) * 1.1, hx + r1 * math.cos(a), hy + r1 * math.sin(a) * 1.1,
                   skia.Paint(AntiAlias=True, Color=_col(col, 26), StrokeWidth=1.8, Style=skia.Paint.kStroke_Style))
    c.drawOval(skia.Rect(hx - 80, hy - 70, hx - 30, hy - 30), skia.Paint(AntiAlias=True, Color=_col('#FFFFFF', 60), MaskFilter=soft(12)))
    return _to_rgb(s)


if __name__ == "__main__":
    from PIL import Image
    ims = [Image.fromarray(np.clip(f(), 0, 255).astype(np.uint8)) for f in (orange, pizza, peacock)]
    sheet = Image.new("RGB", (BOX * 3 + 40, BOX), (10, 10, 20))
    for k, im in enumerate(ims):
        sheet.paste(im, (k * (BOX + 20), 0))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save("art_sheet.png")
    print("ok")
