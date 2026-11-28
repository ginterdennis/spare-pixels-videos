"""041 P vs NP: shared choreography for the three looks (A night grid, B notebook, C neon 3D).

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


# ------------------------------------------------------------------ shared data
RNG = np.random.default_rng(41)


def _sudoku(n, givens, seed):
    """A valid solved n^2 x n^2 sudoku (shuffled pattern) + a mask of given cells."""
    rng = np.random.default_rng(seed)
    N = n * n
    rows = [g * n + r for g in rng.permutation(n) for r in rng.permutation(n)]
    cols = [g * n + c for g in rng.permutation(n) for c in rng.permutation(n)]
    nums = rng.permutation(N) + 1
    grid = np.array([[nums[(n * (r % n) + r // n + c) % N] for c in cols] for r in rows])
    for k in range(N):                                   # sanity: rows, columns, boxes all distinct
        assert len(set(grid[k])) == N and len(set(grid[:, k])) == N
        br, bc = divmod(k, n)
        assert len(set(grid[br * n:(br + 1) * n, bc * n:(bc + 1) * n].ravel())) == N
    mask = np.zeros(N * N, bool)
    mask[rng.choice(N * N, givens, replace=False)] = True
    return grid, mask.reshape(N, N)


SUDOKU = {9: _sudoku(3, 26, 5), 16: _sudoku(4, 96, 6), 25: _sudoku(5, 225, 7)}
WAYS = {N: int(math.floor((N * N - SUDOKU[N][1].sum()) * math.log10(N))) for N in SUDOKU}   # 52, 192, 559
SUD_C, SUD_S = (540, 820), 780              # grid centre and size
HI_ROW, HI_COL, HI_BOX = 3, 6, 4            # highlighted row, column, box (9x9)

# route through 20 stops (2-opt tour)
ROUTE = RNG.random((20, 2))


def _tour(P):
    n = len(P)
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    tour = [0]
    left = set(range(1, n))
    while left:
        nxt = min(left, key=lambda j: D[tour[-1], j]); tour.append(nxt); left.remove(nxt)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b, c, d = tour[i - 1], tour[i], tour[j], tour[(j + 1) % n]
                if D[a, c] + D[b, d] < D[a, b] + D[c, d] - 1e-12:
                    tour[i:j + 1] = reversed(tour[i:j + 1]); improved = True
    return tour


TOUR = _tour(ROUTE)
NET = [3, 5, 5, 2]
NET_W = RNG.uniform(0.2, 1.0, 200)
PROOF = ["Assume there are finitely many primes.",
         "Multiply them all, then add 1.",
         "That number needs a new prime."]

# crack from the "=" (relative to its centre), jagged
def _crack():
    rng = np.random.default_rng(7)
    out = []
    for side in (-1, 1):
        pts = [(0.0, 0.0)]
        x, y = 0.0, 0.0
        while abs(x) < 560:
            x += side * rng.uniform(40, 90); y += rng.uniform(-40, 40)
            pts.append((x, y))
        out.append(pts)
    pts = [(0.0, 0.0)]; x, y = 0.0, 0.0
    while y < 330:
        y += rng.uniform(40, 70); x += rng.uniform(-35, 35); pts.append((x, y))
    out.append(pts)
    return out


CRACK = _crack()
SHARDS = []
for k in range(3):
    rng = np.random.default_rng(100 + k)
    sh = []
    for _ in range(16):
        ang = rng.uniform(0, 2 * math.pi)
        sh.append(dict(x=rng.uniform(-0.45, 0.45), y=rng.uniform(-0.6, 0.55), vx=math.cos(ang) * rng.uniform(300, 900),
                       vy=math.sin(ang) * rng.uniform(300, 900) - 300, rot=rng.uniform(-500, 500),
                       pts=[(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(3)], sz=rng.uniform(14, 34)))
    SHARDS.append(sh)

GX0, GY0, GPX, GPY, COLS, ROWS = 162, 680, 54, 38, 15, 20   # (v1 switch grid, kept for styles)
LOCK5_X = [220, 380, 540, 700, 860]
LOCK5_Y, LOCK5_S = 1395, 118
HOOK_Y1, HOOK_Y2 = 372, 500
PNP0 = (540, 1075, 300)            # frame-0 P = NP: centre x, baseline y, size
LOCK3_X, LOCK3_Y, LOCK3_S = [240, 540, 840], 940, 190


# ------------------------------------------------------------------ composite pieces
def draw_pnp(cv, S, cx, base, size, a=1.0, write=1.0, eq=1.0, eq_scale=1.0, eq_col=None, slash=0.0,
             q=0.0, col=None, glow=1.0):
    """P = NP with a hand-built equals sign (so it can slam in, gain a slash, flicker)."""
    if a <= 0:
        return
    col = S.INK if col is None else col
    eq_col = S.ACC if eq_col is None else eq_col
    role = "math"
    wP = tw("P", S.font_of(role), size)
    wN = tw("NP", S.font_of(role), size)
    eqw = 0.62 * size
    gap = 0.16 * size
    wq = tw("?", S.font_of(role), size) + gap if q > 0 else 0
    total = wP + gap + eqw + gap + wN + wq * clamp01(q)
    x = cx - total / 2
    S.text(cv, "P", x, base, role, size, col, a=a, align="l", write=write)
    S.text(cv, "NP", x + wP + 2 * gap + eqw, base, role, size, col, a=a, align="l", write=write)
    ex = x + wP + gap + eqw / 2
    ey = base - S.MATH_AXIS * size
    if eq > 0:
        th = 0.05 * size
        cv.save()
        cv.translate(ex, ey)
        cv.scale(eq_scale, eq_scale)
        for dy in (-0.085 * size, 0.085 * size):
            S.bar(cv, -eqw / 2, dy, eqw / 2, dy, th, eq_col, a * eq)
        if slash > 0:
            S.bar(cv, 0.16 * size, -0.25 * size, -0.16 * size, 0.25 * size, th, eq_col, a * slash)
        cv.restore()
    if q > 0:
        S.text(cv, "?", x + wP + 2 * gap + eqw + wN + gap, base, role, size, col, a=a * clamp01(q), align="l")
    return ex, ey, eqw


def draw_lock(cv, S, cx, cy, s, openv=0.0, a=1.0, write=1.0, col=None):
    if a <= 0:
        return
    col = S.INK if col is None else col
    body, sh, kh = lock_paths(cx, cy, s, openv)
    S.lock_fill(cv, body, a * clamp01(write * 2 - 1))
    S.stroke(cv, sh, col, s * 0.075, a, write)
    S.stroke(cv, body, col, s * 0.06, a, write)
    S.fill(cv, kh, col, a * clamp01(write * 2 - 1))


def hook_comp(cv, S, t, a=1.0, zoom=1.0, crack=0.0, openv=None, text_a=None, pnp_a=None, locks_a=None):
    """The frame-0 picture: hook words, giant P = NP, a row of 5 closed padlocks."""
    text_a = a if text_a is None else text_a
    pnp_a = a if pnp_a is None else pnp_a
    locks_a = a if locks_a is None else locks_a
    openv = openv or [0] * 5
    if text_a > 0:
        S.hook_text(cv, t, text_a)
    if pnp_a > 0:
        cx, base, size = PNP0
        cv.save()
        cv.translate(cx, base - size * 0.35)
        cv.scale(zoom, zoom)
        cv.translate(-cx, -(base - size * 0.35))
        r = draw_pnp(cv, S, cx, base, size, a=pnp_a)
        cv.restore()
        if crack > 0:
            ex, ey = cx, base - S.MATH_AXIS * size
            for pts in CRACK:
                S.stroke(cv, poly([(ex + x, ey + y) for x, y in pts]), S.ACC, 5, pnp_a, crack, kind="crack")
    if locks_a > 0:
        for i, x in enumerate(LOCK5_X):
            draw_lock(cv, S, x, LOCK5_Y, LOCK5_S, openv[i], locks_a)


# ------------------------------------------------------------------ the director (the script, v2)
def scene_hook(cv, S, t):
    if t < A["rw0"]:
        zoom = 1.06 - 0.06 * e_out(t / 2.4)
        crack = prog(t, A["crack"], 0.22)
        order = [2, 1, 3, 0, 4]
        openv = [0] * 5
        for j, i in enumerate(order):
            openv[i] = e_back(prog(t, A["crack"] + 0.05 + 0.08 * j, 0.14))
        shake = 9 * math.exp(-max(0, t - A["crack"]) * 9) * math.sin(t * 90) if t > A["crack"] else 0
        cv.save(); cv.translate(shake, 0)
        hook_comp(cv, S, t, 1.0, zoom, crack, openv)
        cv.restore()
    elif t < T["origin"] + 0.05:
        r = prog(t, A["rw0"], T["origin"] - A["rw0"])
        back = 1 - e_in(r, 1.5)
        hook_comp(cv, S, t, 1 - e_in(r, 1.3), 1.0 - 0.25 * e_in(r), back, [back] * 5, text_a=1 - prog(r, 0, 0.35))
        S.rewind(cv, t, math.sin(math.pi * r))


def scene_origin(cv, S, t):
    if t < A["rw0"] or t > A["sudoku"] + 0.4:
        return
    out = prog(t, A["sudoku"] - 0.28, 0.3)
    a0 = 1 - out
    cv.save(); cv.translate(0, -120 * e_in(out))
    p = prog(t, A["rw0"] + 0.05, A["year"] - A["rw0"] - 0.05)
    yr = int(round(2026 - 55 * e_io(p)))
    landed = t >= A["year"]
    bump = 1 + 0.12 * (1 - e_out(prog(t, A["year"], 0.25))) if landed else 1
    cv.save(); cv.translate(540, 560); cv.scale(bump, bump); cv.translate(-540, -560)
    S.text(cv, str(yr), 540, 640, "display", 250, S.ACC if landed else S.INK, a=a0 * prog(t, A["rw0"] + 0.12, 0.15))
    cv.restore()
    S.text(cv, "Stephen Cook", 540, 740, "body", 66, S.MUTED, a=a0, write=prog(t, A["cook"], 0.45))
    S.text(cv, "CHECK", 150, 1085, "display", 140, S.INK, a=a0, align="l", write=prog(t, A["checkw"], 0.3))
    tk = prog(t, A["tick"], 0.18)
    if tk > 0:
        ring = e_out(prog(t, A["tick"], 0.5))
        S.stroke(cv, circle(830, 1035, 70 + 40 * ring), S.GOOD, 4, a0 * (1 - ring) * 0.8, 1)
        S.stroke(cv, check_path(830, 1035, 120), S.GOOD, 16, a0, tk)
    S.text(cv, "FIND", 150, 1325, "display", 140, S.INK, a=a0, align="l", write=prog(t, A["findw"], 0.3))
    sp = prog(t, A["findw"] + 0.05, 0.2)
    if sp > 0:
        ang = (t - A["findw"]) * 360
        arc = skia.Path()
        arc.addArc(skia.Rect(830 - 70, 1275 - 70, 830 + 70, 1275 + 70), ang, 250)
        S.stroke(cv, arc, S.BAD, 10, a0 * sp, 1)
        S.text(cv, "?", 830, 1310, "display", 110, S.BAD, a=a0 * prog(t, A["qmark"], 0.2))
    cv.restore()


def _grid_lines(N, x0, y0, size):
    n = int(round(math.sqrt(N)))
    thin, thick = skia.Path(), skia.Path()
    c = size / N
    for k in range(N + 1):
        tgt = thick if k % n == 0 else thin
        tgt.moveTo(x0 + k * c, y0); tgt.lineTo(x0 + k * c, y0 + size)
        tgt.moveTo(x0, y0 + k * c); tgt.lineTo(x0 + size, y0 + k * c)
    return thin, thick


def draw_sudoku(cv, S, t, fr, N, a, draw=1.0, phase="full", hi=None, flash=0.0):
    """phase: 'full' (solved grid), 'empty' (only givens), 'try' (blanks cycle numbers)."""
    grid, mask = SUDOKU[N]
    cx, cy = SUD_C
    size = SUD_S
    x0, y0 = cx - size / 2, cy - size / 2
    c = size / N
    thin, thick = _grid_lines(N, x0, y0, size)
    if hi:
        for kind, k, ha in hi:
            if ha <= 0:
                continue
            if kind == "row":
                r = skia.Rect(x0, y0 + k * c, x0 + size, y0 + (k + 1) * c)
            elif kind == "col":
                r = skia.Rect(x0 + k * c, y0, x0 + (k + 1) * c, y0 + size)
            else:
                br, bc = divmod(k, 3)
                r = skia.Rect(x0 + bc * 3 * c, y0 + br * 3 * c, x0 + (bc + 1) * 3 * c, y0 + (br + 1) * 3 * c)
            cv.drawRect(r, paint(S.GOOD, a * ha * 0.28))
            cv.drawRect(r, paint(S.GOOD, a * ha, stroke=5))
    if flash > 0:
        cv.drawRect(skia.Rect(x0, y0, x0 + size, y0 + size), paint(S.GOOD, a * flash * 0.22))
    S.stroke(cv, thin, S.MUTED, 1.6 if N > 9 else 2.2, a * 0.8, draw)
    S.stroke(cv, thick, S.CYAN if hasattr(S, "CYAN") else S.INK, 3.5 if N > 9 else 5, a, draw)
    if draw < 0.6:
        return
    da = a * clamp01((draw - 0.6) / 0.4)
    role = "display" if N == 9 else "mono"
    fs = c * (0.62 if N == 9 else 0.5 if N == 16 else 0.42)
    rng = np.random.default_rng(fr // 2)
    rand = rng.integers(1, N + 1, (N, N))
    bad = rng.random((N, N)) < 0.06
    for r in range(N):
        for k in range(N):
            x, y = x0 + (k + 0.5) * c, y0 + (r + 0.62) * c
            v = int(grid[r, k])
            if mask[r, k]:
                col = S.INK
            elif phase == "full":
                col = S.ACC
            elif phase == "empty":
                continue
            else:
                v = int(rand[r, k])
                col = S.BAD if bad[r, k] else S.ACC
                if bad[r, k]:
                    cv.drawRect(skia.Rect(x - c / 2 + 2, y - 0.62 * c + 2, x + c / 2 - 2, y + 0.38 * c - 2), paint(S.BAD, da * 0.25))
            hl = False
            if hi and phase == "full":
                for kind, kk, ha in hi:
                    if ha > 0.5 and ((kind == "row" and r == kk) or (kind == "col" and k == kk) or
                                     (kind == "box" and (r // 3) * 3 + k // 3 == kk)):
                        hl = True
            S.text(cv, str(v), x, y + fs * 0.05, role, fs, S.GOOD if hl or flash > 0.5 else col, a=da)


def ways_bar(cv, S, y, label, exp, frac, col, a, xmax=900):
    """Label above, bar whose length is the exponent, 10^exp at its end."""
    if a <= 0:
        return
    S.label(cv, label, 90, y - 22, 34, S.MUTED, a, align="l")
    L = max(6, (xmax - 90 - 150) * frac)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(90, y, 90 + L, y + 34), 8, 8), paint(col, a))
    S.power(cv, "10", str(exp), 90 + L + 80, y + 32, 54, S.INK, a)


def scene_sudoku(cv, S, t, fr):
    if t < A["sudoku"] - 0.05 or t > A["gap"] + 0.7:
        return
    fold = e_in(prog(t, A["gap"], 0.55), 1.6)
    if fold >= 1:
        return
    cv.save()
    if fold > 0:
        cv.translate(540, 900); cv.scale(1 - 0.85 * fold, 1 - 0.85 * fold); cv.translate(-540, -900)
    a = 1 - fold
    # which grid, and morphs at "bigger"
    m1 = prog(t, A["bigger"], 0.45)
    m2 = prog(t, A["bigger"] + 0.95, 0.45)
    if t < A["bigger"]:
        stages = [(9, a, 1.0)]
    elif m2 <= 0:
        stages = [(9, a * (1 - m1), 1.0), (16, a * m1, m1)]
    else:
        stages = [(16, a * (1 - m2), 1.0), (25, a * m2, m2)]
    if t < A["empty"]:
        phase = "full"
    elif t < A["try"]:
        phase = "empty"
    else:
        phase = "try"
    hi = [("row", HI_ROW, window(t, A["row"], A["col"] - 0.05, 0.12, 0.2)),
          ("col", HI_COL, window(t, A["col"], A["box"] - 0.05, 0.12, 0.2)),
          ("box", HI_BOX, window(t, A["box"], A["box"] + 0.5, 0.12, 0.25))]
    flash = window(t, A["box"] + 0.55, A["box"] + 0.95, 0.08, 0.3) if t < A["solve"] else 0
    with S.plane(cv, "sudoku", t):
        for N, sa, dr in stages:
            if sa > 0.01:
                d = prog(t, A["sudoku"], 0.55) if N == 9 else dr
                draw_sudoku(cv, S, t, fr, N, sa, d, phase, hi if N == 9 else None, flash)
    # header word over the grid: CHECK: EASY  ->  SOLVE: HARD
    if t < A["solve"] - 0.05:
        ha = prog(t, A["checking"], 0.2) * (1 - prog(t, A["solve"] - 0.2, 0.2))
        S.text(cv, "CHECK", 520, 360, "display", 104, S.INK, a=ha, align="r")
        S.text(cv, "EASY", 560, 360, "display", 104, S.GOOD, a=ha * prog(t, A["easy"], 0.15), align="l")
    else:
        ha = prog(t, A["solve"], 0.2) * (1 - prog(t, A["bigger"] - 0.1, 0.25))
        S.text(cv, "SOLVE", 520, 360, "display", 104, S.INK, a=ha, align="r")
        S.text(cv, "HARD", 560, 360, "display", 104, S.BAD, a=ha * prog(t, A["hard"], 0.15), align="l")
    # grid size label while it grows
    ga = prog(t, A["bigger"], 0.2)
    if ga > 0:
        N = 9 if m1 < 0.5 else 16 if m2 < 0.5 else 25
        S.text(cv, f"{N} x {N}", 540, 360, "display", 104, S.INK, a=ga)
    # ways to fill it: counter + bars
    wa = prog(t, A["try"] + 0.2, 0.25)
    if wa > 0:
        e9 = WAYS[9] * e_out(prog(t, A["try"] + 0.2, 0.8))
        e = e9
        if t >= A["bigger"]:
            e = lerp(WAYS[9], WAYS[16], e_io(m1))
        if m2 > 0:
            e = lerp(WAYS[16], WAYS[25], e_io(m2))
        ways_bar(cv, S, 1300, "WAYS TO FILL IT", int(round(e)), e / WAYS[25], S.ACC, wa)
        aa = prog(t, A["atoms"], 0.25)
        if aa > 0:
            ways_bar(cv, S, 1430, "ATOMS IN THE UNIVERSE", 80, 80 / WAYS[25] * e_out(aa), S.CYAN if hasattr(S, "CYAN") else S.GOOD, aa)
    cv.restore()


def scene_gap(cv, S, t):
    if t < A["gap"] or t > A["opens"] + 1.2:
        return
    split = e_io(prog(t, A["locks"], 0.45))
    write = prog(t, A["gap"] + 0.12, 0.5)
    shatter_t = t - A["opens"]
    kinds = ["bank", "chat", "wallet"]
    icon_t = [A["bank"], (A["bank"] + A["wallet"]) / 2, A["wallet"]]
    fade_icons = 1 - prog(t, A["pnp"], 0.3)
    with S.plane(cv, "locks", t):
        for i in range(3):
            if split <= 0 and i != 1:
                continue
            cx = lerp(540, LOCK3_X[i], split)
            cy = lerp(900, LOCK3_Y, split)
            s = lerp(330, LOCK3_S, split)
            if shatter_t < 0:
                lift = -8 * e_out(prog(t, A["equals"], 0.2)) if t > A["equals"] else 0
                draw_lock(cv, S, cx, cy + lift, s, 0, 1.0, write)
            else:
                fl = 1 - prog(shatter_t, 0, 0.25)
                if fl > 0:
                    S.flash_disc(cv, cx, cy + s * 0.15, s * (0.6 + 1.2 * (1 - fl)), fl)
                for d in SHARDS[i]:
                    u = shatter_t
                    if u > 1.1:
                        continue
                    x = cx + d["x"] * s + d["vx"] * u
                    y = cy + s * 0.18 + d["y"] * s * 0.8 + d["vy"] * u + 900 * u * u
                    ang = math.radians(d["rot"] * u)
                    pts = []
                    for px, py in d["pts"]:
                        rx = px * math.cos(ang) - py * math.sin(ang)
                        ry = px * math.sin(ang) + py * math.cos(ang)
                        pts.append((x + rx * d["sz"], y + ry * d["sz"]))
                    S.shard(cv, poly(pts, close=True), 1 - prog(u, 0.5, 0.6))
            ia = prog(t, icon_t[i], 0.2) * fade_icons
            if ia > 0 and split > 0.5:
                pop = e_back(prog(t, icon_t[i], 0.25))
                cv.save(); cv.translate(LOCK3_X[i], 1205); cv.scale(pop, pop); cv.translate(-LOCK3_X[i], -1205)
                for pth in icon_paths(kinds[i], LOCK3_X[i], 1205, 120):
                    S.stroke(cv, pth, S.INK, 7, ia, 1)
                cv.restore()
        # the shortcut: one straight line cuts through every lock
        sc = prog(t, A["shortcut"], 0.3)
        if sc > 0 and shatter_t < 0.2:
            fa = 1 - prog(t, A["opens"], 0.2)
            S.stroke(cv, poly([(-40, LOCK3_Y + 40), (1120, LOCK3_Y + 10)]), S.ACC, 10, fa, e_out(sc))
    la = prog(t, A["locks"] + 0.45, 0.3) * fade_icons
    if la > 0:
        S.text(cv, "easy to check,", 540, 1400, "body", 62, S.GOOD, a=la)
        S.text(cv, "hard to find", 540, 1475, "body", 62, S.BAD, a=la)


def pnp_header(t):
    mv = e_io(prog(t, A["also"], 0.45))
    return 540, lerp(640, 400, mv), lerp(220, 130, mv)


def scene_pnp(cv, S, t):
    if t < A["pnp"] - 0.05 or t > A["new"]:
        return
    cx, base, size = pnp_header(t)
    w = prog(t, A["pnp"], 0.3)
    eqp = prog(t, A["equals"], 0.15)
    sc = 1.8 - 0.8 * e_out(eqp)
    draw_pnp(cv, S, cx, base, size, a=1, write=w, eq=clamp01(eqp * 3), eq_scale=sc)


def scene_also(cv, S, t, fr):
    if t < A["also"] + 0.25 or t > A["new"]:
        return
    panels = [("PERFECT ROUTES", 520, 860, A["routes"]), ("SMARTER AI", 885, 1195, A["ai"]),
              ("PROOFS BY MACHINE", 1220, 1520, A["proofs"])]
    for j, (name, y0, y1, t0) in enumerate(panels):
        pa = prog(t, min(t0 - 0.05, A["also"] + 0.3 + 0.15 * j), 0.25)
        if pa <= 0:
            continue
        with S.plane(cv, "panel", t, (y0 + y1) / 2):
            S.panel(cv, 80, y0, 1000, y1, pa)
            S.label(cv, name, 120, y0 + 50, 38, S.MUTED, pa, align="l")
            if t < t0 - 0.05:
                continue
            if name.startswith("PERFECT"):
                pts = [(140 + 800 * px, y0 + 85 + (y1 - y0 - 120) * py) for px, py in ROUTE]
                for k, (x, y) in enumerate(pts):
                    dp = e_back(prog(t, t0 + 0.02 * k, 0.15))
                    if dp > 0:
                        S.fill(cv, circle(x, y, 9 * dp), S.INK, pa)
                tour = [pts[k] for k in TOUR] + [pts[TOUR[0]]]
                lp = prog(t, t0 + 0.3, 0.8)
                if lp > 0:
                    S.stroke(cv, poly(tour), S.ACC, 6, pa, lp)
                if lp >= 1:
                    seg = (t - t0 - 1.1) * 6 % len(TOUR)
                    k = int(seg); u = seg - k
                    x = lerp(tour[k][0], tour[k + 1][0], u); y = lerp(tour[k][1], tour[k + 1][1], u)
                    S.fill(cv, circle(x, y, 13), S.ACC, pa)
            elif name.startswith("SMARTER"):
                cols = [180 + k * (720 / (len(NET) - 1)) for k in range(len(NET))]
                nodes = [[(cols[k], y0 + 95 + (y1 - y0 - 130) * (q + 0.5) / n) for q in range(n)] for k, n in enumerate(NET)]
                ep = prog(t, t0 + 0.1, 0.45)
                wv = (t - t0 - 0.3) * 1.6
                e = 0
                for k in range(len(NET) - 1):
                    for p0 in nodes[k]:
                        for p1 in nodes[k + 1]:
                            act = max(0.0, 1 - abs(wv % 1.6 - (k + 0.5) / len(NET) * 1.6) * 3)
                            S.stroke(cv, poly([p0, p1]), S.ACC if act > 0.3 else S.MUTED, 2.5 + 3 * act * NET_W[e],
                                     pa * (0.35 + 0.65 * act * NET_W[e]), ep)
                            e += 1
                for k, col in enumerate(nodes):
                    for q, (x, y) in enumerate(col):
                        np_ = e_back(prog(t, t0 + 0.04 * k, 0.15))
                        act = max(0.0, 1 - abs(wv % 1.6 - k / len(NET) * 1.6) * 3)
                        S.node(cv, x, y, 17 * np_, act, pa)
            else:
                lines = PROOF
                tot = sum(len(x) for x in lines)
                cp = prog(t, t0 + 0.05, max(0.4, A["proofs_end"] - t0 - 0.1))
                nchar = int(tot * cp)
                psz = fit_size(lines, S.font_of("proof"), 760, 50)
                y = y0 + 112
                for line in lines:
                    shown = line[:max(0, min(len(line), nchar))]
                    nchar -= len(line)
                    if shown:
                        S.text(cv, shown, 125, y, "proof", psz, S.INK, a=pa, align="l")
                    y += 62
                qe = prog(t, A["proofs_end"], 0.2)
                if qe > 0:
                    x = 125 + tw(lines[-1], S.font_of("proof"), psz) + 30
                    sq = e_back(qe)
                    S.fill(cv, rrect(x + 15, y - 62 - 15, 30 * sq, 30 * sq, 2), S.ACC, pa)


def scene_ends(cv, S, t, fr):
    """'The modern world would end' -> everything collapses to a point; 'a new one' -> a new grid blooms."""
    dc = max(0.35, min(0.7, A["new"] - A["ends"] - 0.08))
    if A["ends"] <= t < A["new"]:
        c = e_in(prog(t, A["ends"], dc), 2.2)
        s = max(0.001, 1 - c)
        cv.save(); cv.translate(540, 960); cv.scale(s, s); cv.rotate(40 * c); cv.translate(-540, -960)
        tt_ = min(t, A["ends"] - 1e-3)
        scene_pnp(cv, S, tt_)
        scene_also(cv, S, tt_, fr)
        cv.restore()
        if c > 0.6:
            S.point(cv, 540, 960, 6 + 10 * math.sin((t - A["ends"]) * 18) ** 2, clamp01((c - 0.6) / 0.4))
        return True
    if A["new"] <= t < A["experts"] + 0.6:
        S.bloom(cv, t, prog(t, A["new"], 1.0), 1 - prog(t, A["experts"] - 0.1, 0.6))
    return False


def scene_experts(cv, S, t):
    """P != NP?, 88 %, the unclaimed prize; then on "Just remember:" everything glides back to frame 0."""
    t0 = A["experts"] - 0.35
    if t < t0:
        return
    home = e_io(prog(t, A["home"], A["home_end"] - A["home"]))
    rt = t - A["remember"]
    if rt < 0:
        slash = prog(t, A["experts"] - 0.1, 0.25)
        q = prog(t, A["experts"] - 0.05, 0.2)
        eqc = S.INK
    else:
        flick = [1, 0, 1, 0, 0, 1, 0, 0, 0]
        k = int(rt * 30)
        slash = flick[k] if k < len(flick) else 0
        q = 1 - prog(rt, 0.05, 0.2)
        eqc = S.ACC
    base = lerp(650, PNP0[1], home)
    size = lerp(210, PNP0[2], home)
    zoom = lerp(1.0, 1.06, home)
    cv.save()
    cv.translate(540, base - size * 0.35); cv.scale(zoom, zoom); cv.translate(-540, -(base - size * 0.35))
    draw_pnp(cv, S, 540, base, size, a=1, write=prog(t, t0, 0.35), eq=prog(t, t0 + 0.1, 0.2), eq_col=eqc,
             slash=slash, q=q)
    cv.restore()
    fa = 1 - prog(t, A["home"] - 0.1, 0.3)
    pc = prog(t, A["bet"], max(0.4, A["false"] - A["bet"]))
    if pc > 0 and fa > 0:
        S.text(cv, f"{int(round(88 * e_out(pc, 2)))}%", 540, 1045, "display", 250, S.ACC, a=fa * prog(t, A["bet"], 0.15))
        S.text(cv, "of experts bet it's false", 540, 1135, "body", 56, S.INK, a=fa * prog(t, A["bet"] + 0.3, 0.3))
        S.text(cv, "2019 poll", 540, 1192, "body", 38, S.MUTED, a=fa * prog(t, A["bet"] + 0.3, 0.3))
    pa = prog(t, A["nobody"], 0.25) * fa
    if pa > 0:
        S.text(cv, "$1,000,000", 540, 1355, "display", 104, S.INK, a=pa)
        S.text(cv, "unclaimed", 540, 1420, "body", 48, S.BAD, a=pa)
    if home > 0:                         # the frame-0 picture comes back: hook words + 5 closed locks
        S.hook_text(cv, 0.0, home)
        for x in LOCK5_X:
            draw_lock(cv, S, x, LOCK5_Y, LOCK5_S, 0, home)


def draw_frame(cv, S, t, fr):
    S.bg(cv, t)
    with S.camera(cv, t):
        scene_hook(cv, S, t)
        scene_origin(cv, S, t)
        scene_sudoku(cv, S, t, fr)
        scene_gap(cv, S, t)
        collapsing = scene_ends(cv, S, t, fr)
        if not collapsing and t < A["ends"]:
            scene_pnp(cv, S, t)
            scene_also(cv, S, t, fr)
        scene_experts(cv, S, t)
    S.overlay(cv, t)
