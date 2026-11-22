"""Original vector pictures (skia), BOX x BOX RGB float arrays. Smooth shapes, no pixel look."""
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


def _arr(s):
    a = s.makeImageSnapshot().toarray()        # BGRA on most builds -> check channel order below
    return a


def _to_rgb(s):
    img = s.makeImageSnapshot()
    a = img.toarray(colorType=skia.kRGBA_8888_ColorType)
    return a[..., :3].astype(float)


def _p(**kw):
    p = skia.Paint(AntiAlias=True)
    for k, v in kw.items():
        setattr(p, k, v) if False else None
    return p


def _poly_path(pts):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    path.close()
    return path


def kiwi():
    s, c = _surface('#F49A7C')
    # soft vignette on the backdrop
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), BOX * 0.75, [_col('#FFB79A'), _col('#E57F63')])))
    R = 342
    c.drawCircle(C + 8, C + 14, R + 6, skia.Paint(AntiAlias=True, Color=_col('#9C4E3C', 120),
                 MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.drawCircle(C, C, R, skia.Paint(AntiAlias=True, Color=_col('#6E4A2A')))           # skin
    c.drawCircle(C, C, R - 13, skia.Paint(AntiAlias=True, Color=_col('#D7EC8E')))      # pale rim
    c.drawCircle(C, C, R - 22, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), R - 22, [_col('#C9EE6A'), _col('#8CCB34'), _col('#5E9E1E')], [0.0, 0.45, 1.0])))
    rng = np.random.default_rng(4)
    # radial streaks
    for k in range(64):
        a = k / 64 * 2 * math.pi + rng.uniform(-0.03, 0.03)
        r0, r1 = 90, rng.uniform(220, R - 30)
        p = skia.Paint(AntiAlias=True, Color=_col('#E4F7A8', int(rng.uniform(50, 110))), StrokeWidth=rng.uniform(3, 6),
                       Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap)
        c.drawLine(C + r0 * math.cos(a), C + r0 * math.sin(a), C + r1 * math.cos(a), C + r1 * math.sin(a), p)
    # core
    pts = []
    for k in range(80):
        a = k / 80 * 2 * math.pi
        rr = 78 + 7 * math.sin(3 * a + 0.4) + 4 * math.sin(7 * a)
        pts.append((C + rr * math.cos(a) * 1.08, C + rr * math.sin(a) * 0.92))
    c.drawPath(_poly_path(pts), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), 90, [_col('#FFFBE6'), _col('#EEF2B8')])))
    # seeds: black teardrops pointing outwards
    for k in range(78):
        a = k / 78 * 2 * math.pi + rng.uniform(-0.04, 0.04)
        rr = rng.uniform(100, 150)
        c.save()
        c.translate(C + rr * math.cos(a), C + rr * math.sin(a))
        c.rotate(math.degrees(a))
        c.drawOval(skia.Rect(-10, -5.5, 10, 5.5), skia.Paint(AntiAlias=True, Color=_col('#1B140E')))
        c.drawCircle(-3, -2, 1.8, skia.Paint(AntiAlias=True, Color=_col('#6B5A48')))
        c.restore()
    return _to_rgb(s)


def donut():
    s, c = _surface('#7FCBF0')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, 0), (BOX, BOX)], [_col('#A6DDF7'), _col('#5FB4E6')])))
    rng = np.random.default_rng(11)
    Ro, Ri = 340, 108
    ring = skia.Path()
    ring.addCircle(C, C, Ro)
    ring.addCircle(C, C, Ri, skia.PathDirection.kCCW)
    shadow = skia.Path(ring); shadow.offset(10, 18)
    c.drawPath(shadow, skia.Paint(AntiAlias=True, Color=_col('#2E6E9A', 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.drawPath(ring, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C), Ro, [_col('#B8742F'), _col('#E8AE62'), _col('#E39E4C'), _col('#B06A28')], [0.30, 0.55, 0.85, 1.0])))
    # icing with drips
    outer, inner = [], []
    for k in range(240):
        a = k / 240 * 2 * math.pi
        ro = 292 + 16 * math.sin(5 * a + 0.3) + 9 * math.sin(11 * a + 1.0) + 6 * math.sin(17 * a)
        ri = 140 + 7 * math.sin(6 * a + 0.8) + 4 * math.sin(13 * a)
        outer.append((C + ro * math.cos(a), C + ro * math.sin(a)))
        inner.append((C + ri * math.cos(a), C + ri * math.sin(a)))
    ic = _poly_path(outer)
    ic.addPath(_poly_path(inner[::-1]))
    ic.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(ic, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C - 40, C - 50), 330, [_col('#FFA6D2'), _col('#FF6FAF'), _col('#E9488F')], [0.0, 0.6, 1.0])))
    # glossy highlight
    c.drawArc(skia.Rect(C - 235, C - 235, C + 235, C + 235), 200, 70, False,
              skia.Paint(AntiAlias=True, Color=_col('#FFFFFF', 120), Style=skia.Paint.kStroke_Style, StrokeWidth=22, StrokeCap=skia.Paint.kRound_Cap))
    cols = ['#FFFFFF', '#FFD36B', '#5AC8FF', '#7C5CFF', '#5FE39A', '#FFF3B0']
    for k in range(95):
        for _ in range(50):
            a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(158, 272)
            break
        c.save()
        c.translate(C + rr * math.cos(a), C + rr * math.sin(a))
        c.rotate(rng.uniform(0, 180))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-15, -4.5, 15, 4.5), 4.5, 4.5),
                    skia.Paint(AntiAlias=True, Color=_col(cols[k % len(cols)])))
        c.restore()
    return _to_rgb(s)


def pineapple():
    s, c = _surface('#A98BFF')
    c.drawRect(skia.Rect(0, 0, BOX, BOX), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (C, C * 1.1), BOX * 0.8, [_col('#BBA3FF'), _col('#8E6CF0')])))
    rng = np.random.default_rng(5)
    cx, cy, rx, ry = C, 492, 214, 252
    # crown leaves (behind the body)
    leaves = [(a, int(l * 0.84)) for a, l in [(-62, 190), (-40, 240), (-20, 285), (0, 300), (20, 280), (40, 238), (62, 185), (-82, 140), (82, 135)]]
    for k, (ang, ln) in enumerate(sorted(leaves, key=lambda x: -abs(x[0]))):
        col = ['#1E7F3A', '#2FA84F', '#47C463'][k % 3]
        a = math.radians(ang - 90)
        bx, by = cx + 18 * math.sin(math.radians(ang)), cy - ry + 46
        tip = (bx + ln * math.cos(a), by + ln * math.sin(a))
        nrm = (-math.sin(a), math.cos(a))
        w = 30
        path = skia.Path()
        path.moveTo(bx + nrm[0] * w, by + nrm[1] * w)
        path.quadTo(bx + ln * 0.55 * math.cos(a) + nrm[0] * w * 0.9, by + ln * 0.55 * math.sin(a) + nrm[1] * w * 0.9, *tip)
        path.quadTo(bx + ln * 0.55 * math.cos(a) - nrm[0] * w * 0.9, by + ln * 0.55 * math.sin(a) - nrm[1] * w * 0.9,
                    bx - nrm[0] * w, by - nrm[1] * w)
        path.close()
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=_col(col)))
        c.drawLine(bx, by, bx + ln * 0.8 * math.cos(a), by + ln * 0.8 * math.sin(a),
                   skia.Paint(AntiAlias=True, Color=_col('#9BE39B', 110), StrokeWidth=3, Style=skia.Paint.kStroke_Style))
    body = skia.Path(); body.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    sh = skia.Path(body); sh.offset(10, 16)
    c.drawPath(sh, skia.Paint(AntiAlias=True, Color=_col('#4B2E9A', 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14)))
    c.drawPath(body, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (cx - 60, cy - 70), 330, [_col('#FFE27A'), _col('#FFC23D'), _col('#E08A1E')], [0.0, 0.55, 1.0])))
    c.save(); c.clipPath(body, doAntiAlias=True)
    sp, ang = 60, math.radians(38)
    line = skia.Paint(AntiAlias=True, Color=_col('#B5701C'), StrokeWidth=5, Style=skia.Paint.kStroke_Style)
    for sgn in (1, -1):
        dx, dy = math.cos(ang) * sgn, math.sin(ang)
        nx, ny = -dy, dx
        for k in range(-14, 15):
            ox, oy = cx + nx * k * sp, cy + ny * k * sp
            c.drawLine(ox - dx * 700, oy - dy * 700, ox + dx * 700, oy + dy * 700, line)
    # an "eye" in every diamond: lattice centres
    d1 = np.array([math.cos(ang), math.sin(ang)]); d2 = np.array([-math.cos(ang), math.sin(ang)])
    n1 = np.array([-d1[1], d1[0]]); n2 = np.array([-d2[1], d2[0]])
    M = np.array([n1, n2])
    for i in range(-14, 15):
        for j in range(-14, 15):
            # point with n1.p = (i+.5)*sp and n2.p = (j+.5)*sp
            pt = np.linalg.solve(M, np.array([(i + 0.5) * sp, (j + 0.5) * sp]))
            px, py = cx + pt[0], cy + pt[1]
            if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 > 1.05:
                continue
            c.drawOval(skia.Rect(px - 9, py - 5, px + 9, py + 7), skia.Paint(AntiAlias=True, Color=_col('#8A4E14')))
            c.drawCircle(px - 3, py - 1, 2.2, skia.Paint(AntiAlias=True, Color=_col('#FFE9A8', 200)))
    c.restore()
    c.drawPath(body, skia.Paint(AntiAlias=True, Color=_col('#9A5A14', 160), StrokeWidth=4, Style=skia.Paint.kStroke_Style))
    return _to_rgb(s)


if __name__ == "__main__":
    from PIL import Image
    ims = [Image.fromarray(f().astype(np.uint8)) for f in (kiwi, donut, pineapple)]
    sheet = Image.new("RGB", (BOX * 3 + 40, BOX), (10, 10, 20))
    for k, im in enumerate(ims):
        sheet.paste(im, (k * (BOX + 20), 0))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save("art_sheet.png")
    print("ok")
