"""036 round 1 art: an original apple still life (skia vector), then a cyan cast that leaves NO red pixel
(every pixel has R <= G and R <= B), after Kitaoka's 'no red strawberries' (colour constancy)."""
import math
import numpy as np
import skia

N = 1032                      # art resolution (panel is 860 px, so 1.2x headroom for the push-in)
CAST = np.array([0.0, 185.0, 200.0])
MIX = 0.55
CONTRAST = 1.3


def col(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def apple_path(cx, cy, r):
    p = skia.Path()
    top = cy - r * 0.78
    p.moveTo(cx, top + r * 0.10)
    p.cubicTo(cx + r * 0.35, top - r * 0.22, cx + r * 1.12, top - r * 0.05, cx + r * 1.0, cy + r * 0.12)
    p.cubicTo(cx + r * 0.92, cy + r * 0.70, cx + r * 0.55, cy + r * 1.02, cx + r * 0.22, cy + r * 0.98)
    p.cubicTo(cx + r * 0.10, cy + r * 0.95, cx - r * 0.10, cy + r * 0.95, cx - r * 0.22, cy + r * 0.98)
    p.cubicTo(cx - r * 0.55, cy + r * 1.02, cx - r * 0.92, cy + r * 0.70, cx - r * 1.0, cy + r * 0.12)
    p.cubicTo(cx - r * 1.12, top - r * 0.05, cx - r * 0.35, top - r * 0.22, cx, top + r * 0.10)
    p.close()
    return p


CX, CY, R = N * 0.5, N * 0.53, N * 0.27


def scene(mask_only=False):
    s = skia.Surface(N, N)
    c = s.getCanvas()
    ap = apple_path(CX, CY, R)
    if mask_only:
        c.clear(skia.Color(0, 0, 0, 0))
        c.drawPath(ap, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255)))
        return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., 3].astype(float) / 255
    # wall: warm white with a soft window light from the upper left
    c.drawRect(skia.Rect(0, 0, N, N), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (N * 0.25, N * 0.1), N * 1.1, [col('#FFF8EC'), col('#EFE4D2'), col('#D9CCB8')], [0, 0.55, 1])))
    # table: light wood with grain
    ty = N * 0.70
    c.drawRect(skia.Rect(0, ty, N, N), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, ty), (0, N)], [col('#D8A86C'), col('#B5834C')])))
    rng = np.random.default_rng(4)
    for k in range(26):
        y = ty + 8 + k * 12 + rng.uniform(-3, 3)
        p = skia.Path(); p.moveTo(0, y)
        for x in range(0, N + 60, 60):
            p.lineTo(x, y + 4 * math.sin(x / 140 + k))
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=col('#9C6E3C', 70), StrokeWidth=2.2, Style=skia.Paint.kStroke_Style))
    c.drawRect(skia.Rect(0, ty - 4, N, ty + 6), skia.Paint(Color=col('#8E6234', 120)))
    # shadow on the table
    c.drawOval(skia.Rect(CX - R * 1.05, CY + R * 0.78, CX + R * 1.25, CY + R * 1.12),
               skia.Paint(AntiAlias=True, Color=col('#4A2E14', 150), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18)))
    # apple body
    ap = apple_path(CX, CY, R)
    c.drawPath(ap, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (CX - R * 0.35, CY - R * 0.30), R * 1.55, [col('#FF8070'), col('#F23A44'), col('#C41C2C'), col('#8A1220')], [0, 0.38, 0.75, 1])))
    c.save(); c.clipPath(ap, doAntiAlias=True)
    # streaks and speckles: thin curved lines from the stem dimple to the bottom, following the round body
    for k in range(-9, 10):
        u = k / 9.5
        p = skia.Path(); p.moveTo(CX + u * R * 0.18, CY - R * 0.62)
        p.cubicTo(CX + u * R * 1.25, CY - R * 0.35, CX + u * R * 1.15, CY + R * 0.55, CX + u * R * 0.35, CY + R * 0.95)
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=col('#FFB04A' if k % 3 == 0 else '#8A0C18', 34),
                                 StrokeWidth=R * (0.035 if k % 3 == 0 else 0.05), Style=skia.Paint.kStroke_Style,
                                 MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4)))
    for k in range(70):
        x = CX + rng.uniform(-R, R); y = CY + rng.uniform(-R * 0.7, R)
        c.drawCircle(x, y, rng.uniform(2, 4.5), skia.Paint(AntiAlias=True, Color=col('#FFD7A0', 120)))
    # rim shadow at the bottom-right, highlight at the top-left
    c.drawCircle(CX + R * 0.55, CY + R * 0.55, R * 0.9, skia.Paint(AntiAlias=True, Color=col('#3A0408', 70),
                                                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 40)))
    c.drawOval(skia.Rect(CX - R * 0.72, CY - R * 0.55, CX - R * 0.30, CY - R * 0.05),
               skia.Paint(AntiAlias=True, Color=col('#FFFFFF', 150), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22)))
    c.drawOval(skia.Rect(CX - R * 0.60, CY - R * 0.46, CX - R * 0.44, CY - R * 0.30), skia.Paint(AntiAlias=True, Color=col('#FFFFFF', 210)))
    c.restore()
    # stem dimple, stem and leaf
    top = CY - R * 0.78 + R * 0.10
    c.drawOval(skia.Rect(CX - R * 0.16, top - R * 0.02, CX + R * 0.16, top + R * 0.12), skia.Paint(AntiAlias=True, Color=col('#5A0810', 200),
               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6)))
    st = skia.Path(); st.moveTo(CX - 4, top + R * 0.05); st.cubicTo(CX - 6, top - R * 0.2, CX + 10, top - R * 0.32, CX + R * 0.10, top - R * 0.42)
    c.drawPath(st, skia.Paint(AntiAlias=True, Color=col('#5B3A1E'), StrokeWidth=R * 0.075, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap))
    lf = skia.Path()
    bx, by = CX + R * 0.06, top - R * 0.22
    lf.moveTo(bx, by)
    lf.cubicTo(bx + R * 0.25, by - R * 0.40, bx + R * 0.70, by - R * 0.38, bx + R * 0.80, by - R * 0.20)
    lf.cubicTo(bx + R * 0.60, by + R * 0.05, bx + R * 0.25, by + R * 0.10, bx, by)
    lf.close()
    c.drawPath(lf, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(bx, by), (bx + R * 0.8, by - R * 0.3)], [col('#2E8B3A'), col('#6CC24A')])))
    c.drawLine(bx + 4, by - 4, bx + R * 0.74, by - R * 0.20, skia.Paint(AntiAlias=True, Color=col('#1E5E28', 180), StrokeWidth=4, Style=skia.Paint.kStroke_Style))
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(float)


def cast(img):
    """additive cyan layer + contrast; then no channel R may exceed max(G, B) (clamps the few edge pixels)."""
    out = img * MIX + CAST[None, None] * (1 - MIX)
    out = np.clip((out - 128) * CONTRAST + 128, 0, 255)
    out = np.round(out)
    out[..., 0] = np.minimum(out[..., 0], np.maximum(out[..., 1], out[..., 2]))
    return out


ORIG = scene()
MASK = scene(mask_only=True)
CASTED = cast(ORIG)
_u8 = np.round(CASTED).astype(int)
REDDEST = int((_u8[..., 0] - np.maximum(_u8[..., 1], _u8[..., 2])).max())
assert REDDEST <= 0, f"a pixel is reddish: R - max(G,B) = {REDDEST}"

if __name__ == "__main__":
    from PIL import Image
    a = Image.fromarray(np.clip(ORIG, 0, 255).astype(np.uint8)).resize((430, 430))
    b = Image.fromarray(np.clip(CASTED, 0, 255).astype(np.uint8)).resize((430, 430))
    sh = Image.new("RGB", (880, 430)); sh.paste(a, (0, 0)); sh.paste(b, (450, 0)); sh.save("art_sheet.png")
    ap = _u8[MASK > 0.99]
    print("reddest R-max(G,B):", REDDEST, " apple mean", ap.mean(0).round(1))
