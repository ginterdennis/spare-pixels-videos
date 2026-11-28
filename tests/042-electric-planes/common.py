"""042 electric planes: shared choreography for the two looks (neon 3D, cockpit HUD).

Every look draws the same beats at the same times (timing.py), so one narration and one score serve
all three. A look ("style") only decides how lines, fills, text and backgrounds are drawn, plus an
optional camera (C tilts some scenes into 3D). The director at the bottom (draw_frame) is the script.
"""
import functools, math, os
import numpy as np
import skia
from timing import A, T, END, DUR

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, "fonts"), "/home/claude/kit/fonts"]


# ------------------------------------------------------------------ small maths
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def prog(t, t0, d):
    return clamp01((t - t0) / d) if d > 0 else float(t >= t0)


def e_io(p):
    p = clamp01(p); return p * p * (3 - 2 * p)


def e_out(p, k=3):
    p = clamp01(p); return 1 - (1 - p) ** k


def e_in(p, k=2):
    return clamp01(p) ** k


def e_back(p, s=1.7):
    p = clamp01(p) - 1; return 1 + p * p * ((s + 1) * p + s)


def lerp(a, b, u):
    return a + (b - a) * u


def window(t, t0, t1, fin=0.2, fout=0.25):
    """1 inside [t0, t1] with fades in/out."""
    if t < t0 or t > t1 + fout:
        return 0.0
    return min(prog(t, t0, fin), 1 - prog(t, t1, fout))


# ------------------------------------------------------------------ fonts and text paths
@functools.lru_cache(None)
def typeface(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name + ".ttf")
        if os.path.isfile(p):
            return skia.Typeface.MakeFromFile(p)
    raise FileNotFoundError(name)


@functools.lru_cache(None)
def font(name, size):
    f = skia.Font(typeface(name), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


@functools.lru_cache(4096)
def _glyph_path(s, name, size):
    f = font(name, size)
    gl = f.textToGlyphs(s)
    xs = f.getXPos(gl)
    p = skia.Path()
    for g, x in zip(gl, xs):
        gp = f.getPath(g)
        if gp is not None:
            p.addPath(gp, x, 0)
    return p, f.measureText(s)


def text_path(s, name, size, x, y, align="c"):
    p, w = _glyph_path(s, name, round(size, 1))
    x0 = x - w / 2 if align == "c" else x - w if align == "r" else x
    q = skia.Path(p)
    q.offset(x0, y)
    return q, w


def tw(s, name, size):
    return _glyph_path(s, name, round(size, 1))[1]


def fit_size(lines, name, max_w, size):
    w = max(tw(s, name, 100) for s in lines) / 100
    return min(size, max_w / w) if w else size


# ------------------------------------------------------------------ colours / paints
def C(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(255 * clamp01(a)))


def paint(rgb, a=1.0, stroke=None, cap="round", blur=0, effect=None, blend=None):
    p = skia.Paint(AntiAlias=True, Color=C(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if effect is not None:
        p.setPathEffect(effect)
    if blend is not None:
        p.setBlendMode(blend)
    return p


def trim(u):
    return skia.TrimPathEffect.Make(0, clamp01(u)) if u < 1 else None


# ------------------------------------------------------------------ geometry (centred at 0,0)
def rrect(cx, cy, w, h, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), r, r))
    return p


def circle(cx, cy, r):
    p = skia.Path(); p.addCircle(cx, cy, r); return p


def poly(pts, close=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def lock_paths(cx, cy, s, openv=0.0):
    """Padlock of width s centred at (cx, cy). openv 0..1 lifts and swings the shackle."""
    bw, bh = s, s * 0.78
    by = cy + s * 0.18
    body = rrect(cx, by, bw, bh, s * 0.12)
    r = s * 0.27
    leg = s * 0.16
    top = by - bh / 2
    sh = skia.Path()
    sh.moveTo(cx - r, top + 2)
    sh.lineTo(cx - r, top - leg)
    sh.arcTo(skia.Rect(cx - r, top - leg - r, cx + r, top - leg + r), 180, 180, False)
    sh.lineTo(cx + r, top + 2)
    if openv > 0:
        m = skia.Matrix()
        m.setTranslate(0, -s * 0.26 * openv)
        m.preRotate(-28 * openv, cx - r, top)
        sh.transform(m)
    kh = skia.Path()
    kh.addCircle(cx, by - s * 0.05, s * 0.075)
    kh.addRect(skia.Rect(cx - s * 0.03, by - s * 0.03, cx + s * 0.03, by + s * 0.16))
    return body, sh, kh


def check_path(cx, cy, s):
    return poly([(cx - 0.42 * s, cy + 0.02 * s), (cx - 0.12 * s, cy + 0.32 * s), (cx + 0.46 * s, cy - 0.36 * s)])


def icon_paths(kind, cx, cy, s):
    """Outline icons (stroke paths) for bank, chat, wallet."""
    ps = []
    if kind == "bank":
        ps.append(poly([(cx - 0.5 * s, cy - 0.18 * s), (cx, cy - 0.5 * s), (cx + 0.5 * s, cy - 0.18 * s)], close=True))
        for i in range(4):
            x = cx - 0.33 * s + i * 0.22 * s
            ps.append(poly([(x, cy - 0.08 * s), (x, cy + 0.32 * s)]))
        ps.append(poly([(cx - 0.52 * s, cy + 0.44 * s), (cx + 0.52 * s, cy + 0.44 * s)]))
    elif kind == "chat":
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 0.5 * s, cy - 0.4 * s, cx + 0.5 * s, cy + 0.26 * s), 0.16 * s, 0.16 * s))
        ps.append(p)
        ps.append(poly([(cx - 0.22 * s, cy + 0.26 * s), (cx - 0.3 * s, cy + 0.48 * s), (cx - 0.02 * s, cy + 0.26 * s)]))
        for i in (-1, 0, 1):
            ps.append(circle(cx + i * 0.22 * s, cy - 0.07 * s, 0.045 * s))
    elif kind == "wallet":
        ps.append(rrect(cx, cy + 0.05 * s, 1.0 * s, 0.72 * s, 0.1 * s))
        ps.append(rrect(cx + 0.36 * s, cy + 0.05 * s, 0.3 * s, 0.26 * s, 0.08 * s))
        ps.append(circle(cx - 0.1 * s, cy - 0.38 * s, 0.17 * s))
        ps.append(circle(cx - 0.1 * s, cy - 0.38 * s, 0.08 * s))
    return ps


# ------------------------------------------------------------------ layout constants kept for styles.py
HOOK_Y1, HOOK_Y2 = 372, 500
GX0, GY0, GPX, GPY, COLS, ROWS = 162, 680, 54, 38, 15, 20
GLOBE_C, GLOBE_R = (540, 1035), 395

# ------------------------------------------------------------------ globe + routes
RNG = np.random.default_rng(42)


def _sph(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


def _routes():
    out = []
    k = 0
    while len(out) < 32:
        lat1, lon1 = RNG.uniform(-50, 60), RNG.uniform(-180, 180)
        short = len(out) % 4 == 0                       # exactly 1 in 4
        if short:
            ang = RNG.uniform(7, 11); brg = RNG.uniform(0, 2 * math.pi)
            lat2 = float(np.clip(lat1 + ang * math.cos(brg), -60, 70))
            lon2 = lon1 + ang * math.sin(brg) / max(0.3, math.cos(math.radians(lat1)))
        else:
            lat2, lon2 = RNG.uniform(-50, 60), RNG.uniform(-180, 180)
            p, q = _sph(lat1, lon1), _sph(lat2, lon2)
            if not (35 < math.degrees(math.acos(np.clip(p @ q, -1, 1))) < 110):
                continue
        out.append(dict(a=_sph(lat1, lon1), b=_sph(lat2, lon2), short=short, ph=RNG.uniform(0, 1)))
    return out


ROUTES = _routes()


def _rot(t):
    """Globe rotation: one full turn per video (periodic over END), axis tilted 20 deg."""
    yaw = 2 * math.pi * t / END
    cy, sy = math.cos(yaw), math.sin(yaw)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    tl = math.radians(-20)
    Rx = np.array([[1, 0, 0], [0, math.cos(tl), -math.sin(tl)], [0, math.sin(tl), math.cos(tl)]])
    return Rx @ Ry


def _proj(v, cx, cy, R):
    return cx + v[0] * R, cy - v[1] * R, v[2]


def _segments(pts):
    """Split projected (x, y, z) points into visible runs (z > 0)."""
    runs, cur = [], []
    for x, y, z in pts:
        if z > -0.02:
            cur.append((x, y, z))
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def _slerp(a, b, u):
    om = math.acos(float(np.clip(a @ b, -1, 1)))
    if om < 1e-6:
        return a
    return (math.sin((1 - u) * om) * a + math.sin(u * om) * b) / math.sin(om)


def draw_globe(cv, S, t, cx, cy, R, a=1.0, dim_long=0.0, flash=0.0, planes=True):
    if a <= 0:
        return
    M = _rot(t)
    # wireframe
    for lat in (-60, -30, 0, 30, 60):
        pts = [_proj(M @ _sph(lat, lon), cx, cy, R) for lon in range(-180, 181, 6)]
        for run in _segments(pts):
            S.stroke(cv, poly([(x, y) for x, y, _ in run]), S.MUTED, 1.8, a * 0.45)
    for lon in range(-180, 180, 30):
        pts = [_proj(M @ _sph(lat, lon), cx, cy, R) for lat in range(-90, 91, 6)]
        for run in _segments(pts):
            S.stroke(cv, poly([(x, y) for x, y, _ in run]), S.MUTED, 1.8, a * 0.45)
    S.stroke(cv, circle(cx, cy, R), S.MUTED, 2.5, a * 0.7)
    # routes (raised great-circle arcs)
    for r in ROUTES:
        om = math.acos(float(np.clip(r["a"] @ r["b"], -1, 1)))
        h = 0.04 + 0.22 * om / math.pi
        pts = []
        for k in range(25):
            u = k / 24
            v = _slerp(r["a"], r["b"], u) * (1 + h * math.sin(math.pi * u))
            pts.append(_proj(M @ v, cx, cy, R))
        col = S.ELEC if r["short"] else S.KERO
        ra = a * (1 - 0.8 * dim_long if not r["short"] else 1)
        w = 5 if r["short"] else 3
        if r["short"] and flash > 0:
            w += 6 * flash
        for run in _segments(pts):
            S.stroke(cv, poly([(x, y) for x, y, _ in run]), col, w, ra)
        if planes:
            u = (t / END * (3 if r["short"] else 1) + r["ph"]) % 1
            v = _slerp(r["a"], r["b"], u) * (1 + h * math.sin(math.pi * u))
            x, y, z = _proj(M @ v, cx, cy, R)
            if z > 0:
                S.fill(cv, circle(x, y, 7 if r["short"] else 5), col, ra)
        if r["short"] and flash > 0:
            x, y, z = _proj(M @ (_slerp(r["a"], r["b"], 0.5) * (1 + h)), cx, cy, R)
            if z > 0:
                S.stroke(cv, circle(x, y, 20 + 60 * (1 - flash)), S.ELEC, 4, a * flash)


# ------------------------------------------------------------------ icons (paths, centred)
def plane_top(cx, cy, s, ang=0.0):
    """Generic airliner seen from above, nose to +x."""
    pts = [(0.50, 0), (0.42, 0.04), (0.10, 0.05), (-0.05, 0.42), (-0.14, 0.42), (-0.06, 0.05), (-0.36, 0.05),
           (-0.44, 0.17), (-0.50, 0.17), (-0.46, 0.0)]
    full = pts + [(x, -y) for x, y in reversed(pts[1:-1])]
    ca, sa = math.cos(ang), math.sin(ang)
    return poly([(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in full], close=True)


def car_side(cx, cy, s):
    p = skia.Path()
    p.moveTo(cx - 0.5 * s, cy + 0.12 * s)
    p.lineTo(cx - 0.48 * s, cy - 0.06 * s)
    p.lineTo(cx - 0.28 * s, cy - 0.10 * s)
    p.lineTo(cx - 0.14 * s, cy - 0.30 * s)
    p.lineTo(cx + 0.18 * s, cy - 0.30 * s)
    p.lineTo(cx + 0.34 * s, cy - 0.10 * s)
    p.lineTo(cx + 0.48 * s, cy - 0.06 * s)
    p.lineTo(cx + 0.5 * s, cy + 0.12 * s)
    p.close()
    p.addCircle(cx - 0.27 * s, cy + 0.14 * s, 0.1 * s)
    p.addCircle(cx + 0.27 * s, cy + 0.14 * s, 0.1 * s)
    return p


def battery(cx, cy, w, h):
    p = rrect(cx, cy, w, h, h * 0.16)
    p.addRect(skia.Rect(cx + w / 2, cy - h * 0.18, cx + w / 2 + w * 0.05, cy + h * 0.18))
    return p


def bolt(cx, cy, s):
    return poly([(cx + 0.08 * s, cy - 0.5 * s), (cx - 0.28 * s, cy + 0.06 * s), (cx - 0.02 * s, cy + 0.06 * s),
                 (cx - 0.1 * s, cy + 0.5 * s), (cx + 0.28 * s, cy - 0.08 * s), (cx + 0.02 * s, cy - 0.08 * s)], close=True)


def drop(cx, cy, s):
    p = skia.Path()
    p.moveTo(cx, cy - 0.5 * s)
    p.cubicTo(cx + 0.1 * s, cy - 0.25 * s, cx + 0.38 * s, cy, cx + 0.38 * s, cy + 0.15 * s)
    p.cubicTo(cx + 0.38 * s, cy + 0.38 * s, cx + 0.2 * s, cy + 0.5 * s, cx, cy + 0.5 * s)
    p.cubicTo(cx - 0.2 * s, cy + 0.5 * s, cx - 0.38 * s, cy + 0.38 * s, cx - 0.38 * s, cy + 0.15 * s)
    p.cubicTo(cx - 0.38 * s, cy, cx - 0.1 * s, cy - 0.25 * s, cx, cy - 0.5 * s)
    p.close()
    return p


def propeller(cx, cy, s, ang):
    p = skia.Path()
    for k in range(3):
        a = ang + k * 2 * math.pi / 3
        tip = (cx + math.cos(a) * s * 0.5, cy + math.sin(a) * s * 0.5)
        l = (cx + math.cos(a + 0.35) * s * 0.18, cy + math.sin(a + 0.35) * s * 0.18)
        r = (cx + math.cos(a - 0.35) * s * 0.18, cy + math.sin(a - 0.35) * s * 0.18)
        p.moveTo(cx, cy); p.lineTo(*l); p.lineTo(*tip); p.lineTo(*r); p.close()
    p.addCircle(cx, cy, s * 0.08)
    return p


def airliner_side(cx, cy, L):
    """Generic high-wing twin-prop regional airliner (side view). Returns (body, wing, nacelle, windows, tail)."""
    s = L
    body = skia.Path()
    body.moveTo(cx - 0.50 * s, cy - 0.005 * s)
    body.cubicTo(cx - 0.50 * s, cy - 0.04 * s, cx - 0.45 * s, cy - 0.055 * s, cx - 0.38 * s, cy - 0.055 * s)
    body.lineTo(cx + 0.30 * s, cy - 0.055 * s)
    body.lineTo(cx + 0.47 * s, cy - 0.08 * s)
    body.lineTo(cx + 0.50 * s, cy - 0.075 * s)
    body.lineTo(cx + 0.44 * s, cy + 0.02 * s)
    body.lineTo(cx + 0.30 * s, cy + 0.05 * s)
    body.lineTo(cx - 0.38 * s, cy + 0.05 * s)
    body.cubicTo(cx - 0.46 * s, cy + 0.05 * s, cx - 0.50 * s, cy + 0.03 * s, cx - 0.50 * s, cy - 0.005 * s)
    body.close()
    tail = poly([(cx + 0.34 * s, cy - 0.055 * s), (cx + 0.43 * s, cy - 0.22 * s), (cx + 0.49 * s, cy - 0.22 * s),
                 (cx + 0.47 * s, cy - 0.075 * s)], close=True)
    tail.addRect(skia.Rect(cx + 0.40 * s, cy - 0.235 * s, cx + 0.52 * s, cy - 0.215 * s))
    wing = rrect(cx - 0.02 * s, cy - 0.07 * s, 0.30 * s, 0.025 * s, 0.012 * s)
    nac = rrect(cx - 0.08 * s, cy - 0.04 * s, 0.16 * s, 0.045 * s, 0.02 * s)
    win = skia.Path()
    for k in range(18):
        x = cx - 0.33 * s + k * 0.033 * s
        win.addRRect(skia.RRect.MakeRectXY(skia.Rect(x, cy - 0.03 * s, x + 0.016 * s, cy - 0.012 * s), 3, 3))
    return body, wing, nac, win, tail


def hook_comp(cv, S, t, a=1.0, text_a=None, zoom=1.0, dim_long=0.0, flash=0.0):
    """The frame-0 picture: hook words over a rotating globe of routes, 1 in 4 of them electric."""
    text_a = a if text_a is None else text_a
    if a > 0:
        cx, cy = GLOBE_C
        cv.save(); cv.translate(cx, cy); cv.scale(zoom, zoom); cv.translate(-cx, -cy)
        draw_globe(cv, S, t, cx, cy, GLOBE_R, a, dim_long, flash)
        cv.restore()
    if text_a > 0:
        S.hook_text(cv, t, text_a)


# ------------------------------------------------------------------ the director (the script)
def scene_hook(cv, S, t):
    if t >= A["short"] + 0.6:
        return
    out = prog(t, A["short"] - 0.15, 0.6)
    flash = (1 - prog(t, A["flip"], 0.6)) if t >= A["flip"] else 0
    dim = e_out(prog(t, A["flip"], 0.25)) * (1 - out)
    zoom = 1.06 - 0.06 * e_out(t / 2.4) + 0.9 * e_in(out)
    hook_comp(cv, S, t, 1 - out, text_a=1 - prog(t, A["short"] - 0.2, 0.3), zoom=zoom, dim_long=dim, flash=flash)
    if t >= A["flip"] and t < A["short"]:
        S.text(cv, "1 IN 4", 540, 1505, "display", 86, S.ELEC, a=prog(t, A["flip"], 0.15) * (1 - out))


def scene_short(cv, S, t):
    if t < A["short"] - 0.2 or t > A["fuel"] + 0.3:
        return
    a = prog(t, A["short"] - 0.1, 0.3) * (1 - prog(t, A["fuel"] - 0.15, 0.3))
    if a <= 0:
        return
    S.label(cv, "SHORTER THAN 500 KM", 540, 330, 40, S.MUTED, a)
    # ruler 0..500 km
    x0, x1, ry = 120, 960, 520
    pk = (x1 - x0) / 500
    rp = prog(t, A["short"] + 0.1, 0.6)
    S.stroke(cv, poly([(x0, ry), (x1, ry)]), S.INK, 4, a, rp)
    for k in range(6):
        x = x0 + k * 100 * pk
        if (x - x0) / (x1 - x0) <= rp + 1e-6:
            S.stroke(cv, poly([(x, ry - 16), (x, ry + 16)]), S.INK, 3, a)
            S.text(cv, f"{k * 100}", x, ry + 62, "mono", 34, S.MUTED, a=a)
    S.text(cv, "500 km", x1, ry - 40, "display", 60, S.ELEC, a=a * prog(t, A["km500"], 0.2), align="r")
    # Munich -> Vienna, to scale
    my = 860
    mx, vx = x0, x0 + 355 * pk
    ma = prog(t, A["munich"], 0.2)
    va = prog(t, A["vienna"], 0.2)
    if ma > 0:
        S.fill(cv, circle(mx, my, 14 * e_back(ma)), S.INK, a)
        S.text(cv, "MUNICH", mx, my + 70, "display", 48, S.INK, a=a * ma, align="l")
    if va > 0:
        S.fill(cv, circle(vx, my, 14 * e_back(va)), S.INK, a)
        S.text(cv, "VIENNA", vx, my + 70, "display", 48, S.INK, a=a * va)
        ap = prog(t, A["vienna"] + 0.05, 0.6)
        arc = skia.Path(); arc.moveTo(mx, my); arc.quadTo((mx + vx) / 2, my - 220, vx, my)
        S.stroke(cv, arc, S.ELEC, 6, a, ap)
        if ap > 0.3:
            S.text(cv, "355 km", (mx + vx) / 2, my - 140, "mono", 44, S.ELEC, a=a * prog(t, A["vienna"] + 0.3, 0.2))
        if ap >= 1:
            u = ((t - A["vienna"] - 0.65) * 0.5) % 1
            px = (1 - u) ** 2 * mx + 2 * (1 - u) * u * (mx + vx) / 2 + u * u * vx
            py = (1 - u) ** 2 * my + 2 * (1 - u) * u * (my - 220) + u * u * my
            dx = 2 * (1 - u) * ((mx + vx) / 2 - mx) + 2 * u * (vx - (mx + vx) / 2)
            dy = 2 * (1 - u) * (my - 220 - my) + 2 * u * (my - (my - 220))
            S.fill(cv, plane_top(px, py, 70, math.atan2(dy, dx)), S.ELEC, a)
    # 1 in 4 flights
    ia = prog(t, A["short"] + 0.2, 0.3)
    for k in range(4):
        x = 270 + k * 180
        col = S.ELEC if k == 0 else S.MUTED
        S.fill(cv, plane_top(x, 1230, 130, -math.pi / 2), col, a * ia * (1 if k == 0 else 0.6))
    S.text(cv, "26.7% of all flights", 540, 1400, "body", 52, S.INK, a=a * ia)


def sankey(cv, S, t, y0, label, src_col, pct, pct_col, rest_lbl, t0, a):
    """Energy flow: a 100 % band splits into useful power (pct) and losses."""
    if a <= 0:
        return
    x0, xs, x1 = 110, 420, 900
    H_ = 220
    p = prog(t, t0, 0.6)
    S.label(cv, label, x0, y0 - 30, 40, S.MUTED, a, align="l")
    top = y0
    S.fill(cv, skia.Path().addRect(skia.Rect(x0, top, x0 + (xs - x0) * min(1, p * 2), top + H_)) or _rect(x0, top, x0 + (xs - x0) * min(1, p * 2), top + H_), src_col, a * 0.85)
    if p > 0.5:
        q = (p - 0.5) * 2
        hu = H_ * pct / 100
        # useful band (top) bends right and slightly up
        band = skia.Path()
        band.moveTo(xs, top); band.cubicTo(xs + 200, top, xs + 200, top - 40, xs + (x1 - xs) * q, top - 40)
        band.lineTo(xs + (x1 - xs) * q, top - 40 + hu); band.cubicTo(xs + 200, top - 40 + hu, xs + 200, top + hu, xs, top + hu)
        band.close()
        S.fill(cv, band, pct_col, a * 0.9)
        # loss band (bottom) bends down
        loss = skia.Path()
        lx = xs + (x1 - 200 - xs) * q
        loss.moveTo(xs, top + hu); loss.cubicTo(xs + 160, top + hu, xs + 160, top + hu + 120, lx, top + hu + 120)
        loss.lineTo(lx, top + H_ + 120); loss.cubicTo(xs + 160, top + H_ + 120, xs + 160, top + H_, xs, top + H_)
        loss.close()
        S.fill(cv, loss, S.MUTED, a * 0.35)
        if q > 0.6:
            S.text(cv, f"{pct}%", x1 - 10, top - 60, "display", 96, pct_col, a=a * prog(t, t0 + 0.45, 0.2), align="r")
            S.text(cv, rest_lbl, lx - 10, top + hu + 120 + (H_ - hu) / 2 + 18, "body", 44, S.INK, a=a * prog(t, t0 + 0.5, 0.2), align="r")


def _rect(l, tp, r, b):
    p = skia.Path(); p.addRect(skia.Rect(l, tp, r, b)); return p


def scene_energy(cv, S, t):
    if t < A["fuel"] - 0.2 or t > A["cost"] + 0.3:
        return
    a = prog(t, A["fuel"] - 0.1, 0.3) * (1 - prog(t, A["three"] - 0.1, 0.3))
    if a > 0:
        # kerosene: fuel drop -> 27 % power, 73 % heat
        S.fill(cv, drop(70, 540, 60), S.KERO, a)
        sankey(cv, S, t, 470, "KEROSENE", S.KERO, 27, S.KERO, "heat", min(A["quarter"] - 0.35, A["fuel"] + 0.25), a)
        # rising heat waves
        if t > A["quarter"] - 0.1:
            for k in range(4):
                x = 560 + k * 60
                ph = (t * 1.5 + k * 0.3) % 1
                wv = skia.Path()
                for j in range(12):
                    y = 980 - j * 14 - ph * 40
                    xx = x + 10 * math.sin(j * 0.9 + t * 6)
                    (wv.moveTo if j == 0 else wv.lineTo)(xx, y)
                S.stroke(cv, wv, S.KERO, 3, a * 0.5 * prog(t, A["quarter"] - 0.1, 0.3))
        # electric: battery -> 92 % power, 8 % loss
        ea = prog(t, A["motor"], 0.3)
        if ea > 0:
            S.fill(cv, bolt(70, 1160, 70), S.ELEC, a * ea)
            sankey(cv, S, t, 1090, "ELECTRIC", S.ELEC, 92, S.ELEC, "loss", min(A["ninety"] - 0.35, A["motor"] + 0.2), a * ea)
    # up to 3x less energy
    b = prog(t, A["three"] - 0.1, 0.35) * (1 - prog(t, A["cost"] - 0.15, 0.3))
    if b > 0:
        S.label(cv, "ENERGY PER PASSENGER", 540, 360, 40, S.MUTED, b)
        hk = 760 * e_out(prog(t, A["three"], 0.5))
        he = hk / 2.6
        base = 1300
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(200, base - hk, 440, base), 18, 18), paint(S.KERO, b * 0.9))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(640, base - he, 880, base), 18, 18), paint(S.ELEC, b * 0.9))
        S.text(cv, "KEROSENE", 320, base + 70, "display", 44, S.KERO, a=b)
        S.text(cv, "ELECTRIC", 760, base + 70, "display", 44, S.ELEC, a=b)
        S.text(cv, "UP TO 3x LESS", 760, base - he - 40, "display", 58, S.ELEC, a=b * prog(t, A["three"] + 0.35, 0.2))


def scene_cost(cv, S, t):
    if t < A["cost"] - 0.2 or t > A["co2"] + 0.3:
        return
    a = prog(t, A["cost"] - 0.1, 0.3) * (1 - prog(t, A["co2"] - 0.15, 0.3))
    if a <= 0:
        return
    S.label(cv, "ENERGY BILL PER PASSENGER", 540, 340, 40, S.MUTED, a)
    S.text(cv, "200 km hop", 540, 420, "body", 52, S.INK, a=a)
    # running price: 6.60 -> 3.00
    v = 6.60
    if t >= A["threed"] - 0.25:
        v = lerp(6.60, 3.00, e_io(prog(t, A["threed"] - 0.25, 0.6)))
    col = S.KERO if v > 4.8 else S.ELEC
    pa = prog(t, A["six"] - 0.15, 0.2)
    S.text(cv, f"${v:.2f}", 540, 900, "display", 250, col, a=a * pa)
    # pump vs plug row
    S.fill(cv, drop(300, 1150, 90), S.KERO, a * pa)
    S.text(cv, "jet fuel", 300, 1260, "body", 44, S.KERO, a=a * pa)
    S.text(cv, "$6.60", 300, 1330, "mono", 50, S.KERO, a=a * pa)
    ea = prog(t, A["threed"] - 0.1, 0.25)
    S.fill(cv, bolt(780, 1150, 100), S.ELEC, a * ea)
    S.text(cv, "electricity", 780, 1260, "body", 44, S.ELEC, a=a * ea)
    S.text(cv, "~$3", 780, 1330, "mono", 50, S.ELEC, a=a * ea)


def scene_co2(cv, S, t):
    if t < A["co2"] - 0.2 or t > A["plane"] + 0.3:
        return
    a = prog(t, A["co2"] - 0.1, 0.3) * (1 - prog(t, A["plane"] - 0.15, 0.3))
    if a <= 0:
        return
    # counter: CO2 saved per year (tonnes)
    ca = 1 - prog(t, A["cars"] - 0.1, 0.3)
    p = e_out(prog(t, A["co2"] + 0.3, max(0.5, A["forty"] + 0.35 - A["co2"] - 0.3)), 2)
    n = int(round(40_000_000 * p / 10_000) * 10_000)
    S.label(cv, "CO2 SAVED EVERY YEAR", 540, 360, 40, S.MUTED, a * ca)
    sz = fit_size([f"{40_000_000:,} t"], S.font_of("display"), 920, 150)
    S.text(cv, f"{n:,} t", 540, 620, "display", sz, S.ELEC, a=a * ca)
    S.text(cv, "if every flight under 500 km", 540, 720, "body", 46, S.INK, a=a * ca * prog(t, A["co2"] + 0.4, 0.3))
    S.text(cv, "went electric on clean power", 540, 780, "body", 46, S.INK, a=a * ca * prog(t, A["clean"], 0.3))
    S.text(cv, "(= 5% of aviation's fuel)", 540, 850, "body", 38, S.MUTED, a=a * ca * prog(t, A["forty"] + 0.3, 0.3))
    # cars: 90 icons, each = 100,000 cars; they drive off the road
    cars_a = prog(t, A["cars"], 0.3)
    if cars_a > 0:
        S.label(cv, "LIKE TAKING CARS OFF THE ROAD", 540, 360, 40, S.MUTED, a * cars_a)
        S.text(cv, "9,000,000 cars", 540, 520, "display", 120, S.ELEC, a=a * prog(t, A["nine"], 0.25))
        go = prog(t, A["road"] - 0.2, 1.4)
        for k in range(90):
            r, c = divmod(k, 9)
            x = 140 + c * 100 + 1400 * e_in(prog(go, (9 - c) * 0.04 + r * 0.02, 0.5), 2)
            y = 680 + r * 78
            ka = a * prog(t, A["cars"] + k * 0.006, 0.2)
            if x < 1200:
                S.fill(cv, car_side(x, y, 80), S.MUTED if go <= 0 else S.INK, ka * (1 - 0.6 * clamp01(go)))
        S.text(cv, "1 car = 100,000 cars", 540, 1500, "body", 36, S.MUTED, a=a * cars_a)


def draw_airliner(cv, S, cx, cy, L, t, a):
    """Generic high-wing twin-prop regional airliner, side view (original drawing, no real type)."""
    body, wing, nac, win, tail = airliner_side(cx, cy, L)
    S.fill(cv, tail, S.BG2, a); S.stroke(cv, tail, S.INK, 4, a)
    S.fill(cv, body, S.BG2, a); S.stroke(cv, body, S.INK, 5, a)
    S.fill(cv, win, S.ELEC, a * 0.9)
    wing2 = rrect(cx - 0.03 * L, cy - 0.066 * L, 0.30 * L, 0.018 * L, 0.009 * L)
    S.fill(cv, wing2, S.INK, a)
    nac2 = rrect(cx - 0.085 * L, cy - 0.050 * L, 0.17 * L, 0.040 * L, 0.02 * L)
    S.fill(cv, nac2, S.BG2, a); S.stroke(cv, nac2, S.INK, 4, a)
    # propeller disc seen from the side: a thin glowing ellipse with a blade sweeping through it
    px, py = cx - 0.175 * L, cy - 0.050 * L
    disc = skia.Path(); disc.addOval(skia.Rect(px - 0.008 * L, py - 0.095 * L, px + 0.008 * L, py + 0.095 * L))
    S.fill(cv, disc, S.ELEC, a * 0.25)
    bl = 0.095 * L * math.cos(t * 50)
    S.stroke(cv, poly([(px, py - bl), (px, py + bl)]), S.ELEC, 5, a * 0.9)
    S.fill(cv, bolt(cx + 0.43 * L, cy - 0.13 * L, 0.06 * L), S.ELEC, a)


def scene_plane(cv, S, t):
    if t < A["plane"] - 0.2 or t > A["catch"] + 0.3:
        return
    a = prog(t, A["plane"] - 0.1, 0.3) * (1 - prog(t, A["catch"] - 0.15, 0.3))
    if a <= 0:
        return
    fly = e_out(prog(t, A["plane"], 0.9))
    cx = lerp(-500, 540, fly)
    cy = 760 + 10 * math.sin(t * 2.2)
    with S.plane(cv, "card", t):
        draw_airliner(cv, S, cx, cy, 940, t, a)
    S.text(cv, "36 SEATS", 540, 420, "display", 96, S.INK, a=a * prog(t, A["plane"] + 0.3, 0.25))
    pr = prog(t, A["promise"] - 0.1, 0.3)            # battery + year make way for the promise
    ba = prog(t, A["battery1"] - 0.6, 0.3) * (1 - pr)
    if ba > 0:
        fill = e_io(prog(t, A["battery1"] - 0.5, 0.8))
        S.stroke(cv, battery(500, 1060, 640, 120), S.INK, 5, a * ba)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(500 - 300, 1060 - 44, 500 - 300 + 600 * fill, 1060 + 44), 14, 14),
                     paint(S.ELEC, a * ba * 0.9))
        S.text(cv, "200 km on battery", 500, 1200, "body", 52, S.INK, a=a * ba)
    ya = prog(t, A["y2031"], 0.25)
    if ya > 0:
        sc = 1.4 - 0.4 * e_out(ya)
        cv.save(); cv.translate(540, 1380); cv.scale(sc, sc); cv.translate(-540, -1380)
        S.text(cv, "2031", 540, 1420, "display", 130, S.ELEC, a=a * ya * (1 - pr))
        cv.restore()
    pa = prog(t, A["pct40"] - 0.1, 0.2)
    if pa > 0:
        sc = 1.6 - 0.6 * e_out(prog(t, A["pct40"] - 0.1, 0.15))
        cv.save(); cv.translate(540, 1180); cv.scale(sc, sc); cv.translate(-540, -1180)
        S.text(cv, "-40%", 540, 1230, "display", 220, S.ELEC, a=a * pa)
        cv.restore()
        S.text(cv, "operating costs", 540, 1330, "body", 56, S.INK, a=a * pa)
        S.text(cv, "(the maker's claim)", 540, 1400, "body", 42, S.MUTED, a=a * pa)


def scene_catch(cv, S, t):
    if t < A["catch"] - 0.2 or t > A["home"] + 0.6:
        return
    a = prog(t, A["catch"] - 0.1, 0.3) * (1 - prog(t, A["home"] - 0.1, 0.5))
    if a <= 0:
        return
    S.label(cv, "THE CATCH", 540, 360, 44, S.KERO, a * (1 - prog(t, A["loop"] - 0.1, 0.25)))
    # a heavy battery drops in
    dropp = e_in(prog(t, A["heavy"] - 0.25, 0.3), 2)
    by = lerp(300, 820, dropp)
    bump = 0
    if t > A["heavy"] + 0.05:
        bump = 10 * math.exp(-(t - A["heavy"] - 0.05) * 10) * math.sin((t - A["heavy"]) * 60)
    cv.save(); cv.translate(0, bump)
    S.stroke(cv, battery(520, by, 520, 260), S.INK, 7, a)
    health = 1.0
    if t > A["wears"]:
        health = lerp(1.0, 0.8, e_io(prog(t, A["wears"], 0.8)))
    if t > A["loop"]:
        health = lerp(0.8, 1.0, e_io(prog(t, A["better"], 0.6)))
    fillw = 480 * health
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(520 - 240, by - 110, 520 - 240 + fillw, by + 110), 18, 18),
                 paint(S.ELEC if health > 0.9 else S.KERO, a * 0.85))
    cv.restore()
    if t > A["heavy"] and t < A["loop"] + 0.3:
        S.text(cv, "HEAVY", 540, 1110, "display", 96, S.INK, a=a * prog(t, A["heavy"], 0.2) * (1 - prog(t, A["loop"], 0.3)))
    if t > A["wears"] and t < A["better"] - 0.1 + 0.3:
        S.text(cv, f"{int(round(health * 100))}% health", 540, 1230 if t < A["better"] else 1300, "mono", 56, S.KERO if health < 0.95 else S.ELEC,
               a=a * prog(t, A["wears"], 0.2) * (1 - prog(t, A["better"] - 0.1, 0.25)))
    # better every year: bars growing (illustrative, no figures)
    ga = prog(t, A["better"] - 0.1, 0.3)
    if ga > 0:
        for k in range(5):
            h_ = (80 + k * 55) * e_out(prog(t, A["better"] + k * 0.08, 0.35))
            x = 300 + k * 120
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 40, 1480 - h_, x + 40, 1480), 10, 10), paint(S.ELEC, a * ga))
        S.text(cv, "BETTER EVERY YEAR", 540, 1200, "display", 64, S.ELEC, a=a * ga)


def scene_home(cv, S, t):
    """'...and that is why' -> glide back to the frame-0 picture (globe + hook words), ready for the loop."""
    if t < A["home"]:
        return
    h = e_io(prog(t, A["home"], A["home_end"] - A["home"]))
    hook_comp(cv, S, t, a=h, text_a=h, zoom=lerp(0.6, 1.06, h))


def draw_frame(cv, S, t, fr):
    S.bg(cv, t)
    with S.camera(cv, t):
        scene_hook(cv, S, t)
        scene_short(cv, S, t)
        scene_energy(cv, S, t)
        scene_cost(cv, S, t)
        scene_co2(cv, S, t)
        scene_plane(cv, S, t)
        scene_catch(cv, S, t)
        scene_home(cv, S, t)
    S.overlay(cv, t)
