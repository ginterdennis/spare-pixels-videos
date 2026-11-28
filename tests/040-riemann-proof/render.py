"""040 "Math's biggest problem just got solved." (NEWS #1, current-affairs explainer, made 27 Nov 2026).

The Riemann Hypothesis proof announced on 20 Nov 2026 (Levent Alpoege, working with Claude): what RH is,
the 17-million-line Lean proof, the machine check (21 Nov), the 76,000-line rewrite (25 Nov), why it
matters. Voice A+. Running number: LINES OF PROOF (HUD), from frame 0 to the end.
Scenes (times in timing.py): A strip + hook | B primes 1859 | C zeros snap onto the line | D 167 years |
E Lean code > how long? > 17 MILLION | F checkers PASSED > CORRECT | G cut to 76,000 | H RH band |
I IF-theorems become TRUE | J share card, hands back to frame 0.

    python3 render.py stills     # contact sheet of the busiest moments -> stills.jpg
    python3 render.py            # v040_video.mp4
"""
import sys, math, json, functools, os
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *
from hook import hook_text, stamp
from timing import T, DUR

HERE = os.path.dirname(os.path.abspath(__file__))
END = T["end"]
ZEROS = json.load(open(os.path.join(HERE, "zeros.json")))       # mpmath.zetazero(1..75).imag
DIM_BG = (8, 9, 20)

# ------------------------------------------------------------------ small drawing helpers
BG = Image.fromarray(vgrad()).convert("RGBA")


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def win(t, t0, t1, fi=0.25, fo=0.25):
    """opacity of something visible on [t0, t1) with fades."""
    if t < t0 or t >= t1:
        return 0.0
    a = 1.0
    if fi > 0:
        a = min(a, (t - t0) / fi)
    if fo > 0:
        a = min(a, (t1 - t) / fo)
    return clamp(a)


def fade(layer, a):
    if a >= 0.999:
        return layer
    layer = layer.copy()
    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    return layer


@functools.lru_cache(maxsize=4096)
def _text_layer(s, fname, size, col, stroke, spacing):
    f = font(fname, size)
    if spacing:
        w = int(sum(f.getlength(ch) for ch in s) + spacing * (len(s) - 1)) + 16
        h = int(size * 1.4) + 8
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_rich(d, w / 2, int(size * 1.05) + 4, [(s, col + (255,))], f, spacing=spacing)
        return im, w / 2, int(size * 1.05) + 4
    l, t_, r, b = f.getbbox(s, anchor="ls", stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 8, b - t_ + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = -l + 4, -t_ + 4
    d.text((ox, oy), s, font=f, fill=col + (255,), anchor="ls", stroke_width=stroke, stroke_fill=(6, 7, 16, 255))
    return im, ox + f.getlength(s) / 2, oy


def text(im, cx, y, s, fname="Inter-Black", size=80, col=WHITE, a=1.0, stroke=0, spacing=0, align="c", scale=1.0):
    """draw s with its baseline at y. align c: cx is the centre; l: cx is the left edge."""
    if a <= 0.01 or not s:
        return
    lay, ax, ay = _text_layer(s, fname, size, col, stroke, spacing)
    if align == "l":
        ax = ax - font(fname, size).getlength(s) / 2 if not spacing else 4
    if scale != 1.0:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
        ax, ay = ax * scale, ay * scale
    im.alpha_composite(fade(lay, a), (int(cx - ax), int(y - ay)))


def overlay(im, draw_fn, a=1.0, box=None):
    """draw with ImageDraw on a transparent layer, then composite with opacity a."""
    if a <= 0.01:
        return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    im.alpha_composite(fade(lay, a))


@functools.lru_cache(None)
def sprite(r, col, level):
    s, R = glow_sprite(r, col, glow=2.8)
    return fade(s, level / 10.0), R


def dot(im, x, y, r, col, a=1.0):
    lv = int(round(clamp(a) * 10))
    if lv <= 0:
        return
    s, R = sprite(r, col, lv)
    im.alpha_composite(s, (int(x - R), int(y - R)))


def panel(im, box, a=1.0, fill=(13, 15, 33), border=(70, 80, 120), radius=26, width=2, falpha=235):
    overlay(im, lambda d: d.rounded_rectangle(box, radius=radius, fill=fill + (falpha,), outline=border + (255,), width=width), a)


def headline(im, t, t0, t1, lines, y=330, gap=112, fi=0.2, fo=0.2):
    """top text block: lines = [(text, size, colour, appear_offset)]"""
    for k, (s, size, col, off) in enumerate(lines):
        a = win(t, t0 + off, t1, fi, fo)
        if a > 0:
            pop = 1.0 + 0.08 * (1 - ease_out(clamp((t - t0 - off) / 0.18)))
            text(im, W / 2, y + k * gap, s, "Inter-Black", size, col, a, stroke=4, scale=pop)


# ------------------------------------------------------------------ the critical strip (A, C, D, J)
SX0, SX1, LX = 300, 780, 540          # Re 0, Re 1, Re 1/2
SY0, SY1 = 560, 1370
K = 13.0                              # px per unit of height


def cam(t):
    return 8.0 + 2.6 * t


@functools.lru_cache(None)
def strip_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle((SX0, SY0 - 40, SX1, SY1 + 40), fill=CYAN + (20,))
    for x in (SX0, SX1):
        for y in range(SY0 - 40, SY1 + 40, 28):
            d.line((x, y, x, y + 14), fill=CYAN + (90,), width=3)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).line((LX, SY0 - 40, LX, SY1 + 40), fill=GOLD + (200,), width=18)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    lay = Image.alpha_composite(lay, glow)
    ImageDraw.Draw(lay).line((LX, SY0 - 40, LX, SY1 + 40), fill=GOLD + (255,), width=5)
    # soft vertical fade at top and bottom
    m = np.ones(H)
    ramp = 90
    m[SY0 - 40:SY0 - 40 + ramp] = np.linspace(0, 1, ramp)
    m[SY1 + 40 - ramp:SY1 + 40] = np.linspace(1, 0, ramp)
    a = np.asarray(lay.getchannel("A"), float) * m[:, None]
    lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    return lay


RNG = np.random.default_rng(40)
SCATTER = RNG.uniform(SX0 + 30, SX1 - 30, len(ZEROS))
SCATTER = np.where(np.abs(SCATTER - LX) < 60, SCATTER + np.sign(SCATTER - LX + 1e-3) * 90, SCATTER)


def draw_strip(im, t, a=1.0, c=None, snap=None):
    """snap = (t_start) : zeros start scattered and fly onto the line, staggered bottom to top."""
    if a <= 0.01:
        return
    im.alpha_composite(fade(strip_layer(), a))
    c = cam(t) if c is None else c
    for i, g in enumerate(ZEROS):
        y = SY1 - (g - c) * K
        if y < SY0 - 30 or y > SY1 + 30:
            continue
        e = clamp(min(y - (SY0 - 30), (SY1 + 30) - y) / 80)
        x = LX
        if snap is not None:
            u = ease_out(clamp((t - snap - (SY1 - y) / 900.0) / 0.45), 3)
            x = lerp(SCATTER[i], LX, u)
        dot(im, x, y, 11, GOLD, a * e)


# ------------------------------------------------------------------ HUD: LINES OF PROOF
LINES_FULL = 17374215                 # line count of the 20 Nov archive (riemannhypothesissolved.com; rh-trim: 17,374,242)
LINES_READ, LINES_COMPACT = 300000, 76000
CUT0, CUT1 = T["cut"] + 0.95, T["cut"] + 1.65


def lines_at(t):
    if t < T["lean"]:
        return int(1 + 37 * t + 3 * t * t)
    l0 = lines_at(T["lean"] - 1e-6)
    if t < T["big"]:
        u = (t - T["lean"]) / (T["big"] - T["lean"])
        return int(l0 * math.exp(math.log(LINES_FULL / l0) * u ** 2.2))
    if t < CUT0:
        return LINES_FULL
    if t < CUT1:
        u = ease(clamp((t - CUT0) / (CUT1 - CUT0)))
        return int(math.exp(lerp(math.log(LINES_FULL), math.log(LINES_COMPACT), u)))
    return LINES_COMPACT


def hud(im, t):
    a = 1.0
    if t >= T["share"]:
        a = 0.0
    if t >= T["share"] - 0.3:
        a = clamp((T["share"] - t) / 0.3)
    if t > END - 0.55:                       # loop: hand back to frame 0
        a = clamp((t - (END - 0.55)) / 0.45)
    if a <= 0.01:
        return
    n = lines_at(t) if t < END - 0.6 else lines_at(0)
    col = WHITE
    if T["big"] <= t < CUT0:
        col = GOLD
    elif t >= CUT1 and t < END - 0.6:
        col = CYAN
    panel(im, (190, 1378, 890, 1556), a * 0.9, fill=DIM_BG, border=(50, 56, 86), radius=30, falpha=200)
    text(im, W / 2, 1428, "LINES OF PROOF", "Inter-Bold", 32, MUTED, a, spacing=6)
    pop = 1.0
    if T["big"] <= t < T["big"] + 0.25:
        pop = 1.0 + 0.18 * (1 - ease_out((t - T["big"]) / 0.25))
    text(im, W / 2, 1530, f"{n:,}", "Inter-Black", 104, col, a, scale=pop)


# ------------------------------------------------------------------ scene B: primes
def isprime(n):
    if n < 2:
        return False
    return all(n % p for p in range(2, int(n ** 0.5) + 1))


PRIMES = [n for n in range(2, 80) if isprime(n)]


def scene_primes(im, t, a):
    t0 = T["primes"] - 0.15
    u = t - t0
    s = 1.2 + 3.3 * u                       # the number at the centre
    sp = 132
    yl = 990
    overlay(im, lambda d: d.line((0, yl, W, yl), fill=MUTED + (110,), width=3), a)
    for n in range(max(1, int(s) - 6), int(s) + 7):
        x = LX + (n - s) * sp
        if x < -60 or x > W + 60:
            continue
        e = clamp(min(x + 60, W + 60 - x) / 160)
        if isprime(n):
            lit = clamp((s - n + 0.6) / 0.4)           # lights up as it reaches the centre
            dot(im, x, yl, 15, GOLD, a * e * (0.35 + 0.65 * lit))
            text(im, x, yl - 52, str(n), "Inter-Black", 68, GOLD, a * e * (0.45 + 0.55 * lit))
            # gap to the next prime
            q = next(p for p in PRIMES if p > n)
            x2 = LX + (q - s) * sp
            gl = lit * clamp((s - n) / 0.8)
            if gl > 0.02:
                hh = (x2 - x) * 0.42
                def arc(d, x=x, x2=x2, hh=hh):
                    d.arc((x, yl + 22 - hh / 2, x2, yl + 22 + hh / 2), 0, 180, fill=CYAN + (230,), width=5)
                overlay(im, arc, a * e * gl)
                text(im, (x + x2) / 2, yl + 22 + hh / 2 + 58, f"+{q - n}", "Inter-Black", 50, CYAN, a * e * gl)
        else:
            overlay(im, lambda d, x=x: d.line((x, yl - 14, x, yl + 14), fill=MUTED + (160,), width=4), a * e)
            text(im, x, yl - 46, str(n), "Inter-Bold", 42, MUTED, a * e * 0.7)


# ------------------------------------------------------------------ scene E: Lean code
CODE = [
    "import Mathlib",
    "open Complex Real Filter",
    "",
    "/-- every key zero has real part 1/2 -/",
    "theorem zero_re_half {s : Complex}",
    "    (h : riemannZeta s = 0) (h0 : 0 < s.re)",
    "    (h1 : s.re < 1) : s.re = 1 / 2 := by",
    "  by_contra hne",
    "  have hw := weight_pos s h0 h1 hne",
    "  exact absurd hw (not_lt.2 (main_bound s))",
    "",
    "lemma step_bound (x : Real) (hx : 1 < x) :",
    "    psi x - x <= C * sqrt x * log x ^ 2 := by",
    "  rw [psi_eq_sum, Finset.sum_sub_distrib]",
    "  apply Finset.sum_le_sum",
    "  intro p hp",
    "  gcongr",
    "  nlinarith [sq_nonneg (x - 1), hx]",
    "  simp only [mul_comm, mul_assoc]",
    "  positivity",
    "",
    "lemma window_le (y : Real) (hy : 2 <= y) :",
    "    G y <= log (2 * pi) + K * sqrt y := by",
    "  calc G y <= A y + B y := G_le_add y",
    "    _ <= log (2 * pi) + K * sqrt y := by",
    "      field_simp",
    "      ring_nf",
    "      linarith [A_le y hy, B_le y hy]",
    "  norm_num",
    "",
]
KW = {"theorem": PINK, "lemma": PINK, "import": PINK, "open": PINK, "have": PINK, "calc": PINK, "by_contra": CYAN,
      "exact": CYAN, "rw": CYAN, "apply": CYAN, "intro": CYAN, "gcongr": CYAN, "nlinarith": CYAN, "simp": CYAN,
      "positivity": CYAN, "field_simp": CYAN, "ring_nf": CYAN, "linarith": CYAN, "norm_num": CYAN}


def code_line_parts(s):
    if s.strip().startswith("/-"):
        return [(s, MUTED)]
    ind = len(s) - len(s.lstrip())
    w = s.strip().split(" ", 1)
    first = w[0]
    col = KW.get(first, WHITE)
    rest = (" " + w[1]) if len(w) > 1 else ""
    return [(" " * ind + first, col), (rest, (205, 210, 230))]


@functools.lru_cache(maxsize=512)
def code_row(i, gutter):
    """one rendered code line (gutter number + coloured code) as a layer."""
    f = font("JBMono", 30)
    lay = Image.new("RGBA", (930, 44), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((150, 32), f"{gutter:>9,}"[-9:], font=f, fill=(90, 96, 130, 255), anchor="rs")
    x = 172
    for s, col in code_line_parts(CODE[i % len(CODE)]):
        d.text((x, 32), s, font=f, fill=col + (255,), anchor="ls")
        x += f.getlength(s)
    return lay


def big_panel(im, t, a, box=(70, 560, 1010, 1340)):
    if a <= 0.01:
        return
    panel(im, box, a, fill=(10, 12, 28), border=(60, 70, 110))
    x0, y0, x1, y1 = box
    text(im, x0 + 36, y0 + 50, "RiemannHypothesis.lean", "JBMono-Bold", 30, MUTED, a, align="l")
    overlay(im, lambda d: d.line((x0 + 2, y0 + 72, x1 - 2, y0 + 72), fill=(60, 70, 110, 255), width=2), a)
    top = lines_at(t)
    rows = int((y1 - y0 - 100) / 42)
    frac = (lines_at(t) - int(lines_at(t)))
    for r in range(rows):
        g = max(1, top - rows + r + 1)
        lay = code_row(g % len(CODE), g)
        im.alpha_composite(fade(lay, a * clamp(min(r + 1, rows - r) / 2.0)), (x0 - 40, int(y0 + 90 + r * 42)))


def file_card(d, x, y, w, h, seed, scroll, col_a):
    d.rounded_rectangle((x, y, x + w, y + h), radius=max(4, int(w * 0.06)), fill=(12, 14, 30, col_a), outline=(70, 82, 125, col_a), width=2)
    rng = np.random.default_rng(seed)
    lens = rng.uniform(0.25, 0.92, 40)
    cols = [PINK, CYAN, WHITE, WHITE, (205, 210, 230), MUTED]
    lh = max(5, h / 9)
    n = int((h - lh) / lh)
    off = int(scroll) % 40
    for r in range(n):
        k = (r + off) % 40
        lw = (w - w * 0.18) * lens[k]
        c = cols[(k * 7 + seed) % len(cols)]
        yy = y + lh * 0.8 + r * lh
        d.rounded_rectangle((x + w * 0.1, yy, x + w * 0.1 + lw, yy + max(2, lh * 0.38)), radius=2, fill=c + (int(col_a * 0.8),))


def grid(im, t, a, cols, rows, t_in, box=(70, 560, 1010, 1340)):
    if a <= 0.01:
        return
    x0, y0, x1, y1 = box
    g = 14 if cols < 5 else 10
    cw = (x1 - x0 - g * (cols - 1)) / cols
    ch = (y1 - y0 - g * (rows - 1)) / rows
    s = 1.0 + 0.12 * (1 - ease_out(clamp((t - t_in) / 0.35)))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    speed = 9 + 40 * clamp((t - T["howlong"]) / (T["big"] - T["howlong"]))

    def fn(d):
        for r in range(rows):
            for c in range(cols):
                x = cx + ((x0 + c * (cw + g)) - cx) * s
                y = cy + ((y0 + r * (ch + g)) - cy) * s
                file_card(d, x, y, cw * s, ch * s, r * 31 + c * 7 + cols, t * speed * (1 + (r * cols + c) % 3), 235)
    overlay(im, fn, a)


# ------------------------------------------------------------------ scene F: checkers
CHECKERS = ["LEAN KERNEL", "NANODA", "CON-LECHE", "CON-RON"]


def scene_check(im, t, a):
    for i, name in enumerate(CHECKERS):
        y = 590 + i * 136
        ti = T["check"] + 0.15 + i * 0.12
        ai = a * clamp((t - ti) / 0.2)
        if ai <= 0.01:
            continue
        dx = 60 * (1 - ease_out(clamp((t - ti) / 0.3)))
        passed = t >= T["check"] + 1.55 + i * 0.28
        panel(im, (110 + dx, y, 970 + dx, y + 118), ai, fill=(14, 16, 34),
              border=CYAN if passed else (70, 80, 120), width=3 if passed else 2)
        text(im, 150 + dx, y + 76, name, "JBMono-Bold", 46, WHITE, ai, align="l")
        if passed:
            k = ease_out(clamp((t - (T["check"] + 1.55 + i * 0.28)) / 0.2))
            def tick(d, y=y, k=k, dx=dx):
                pts = [(770 + dx, y + 60), (795 + dx, y + 84), (840 + dx, y + 34)]
                if k < 0.5:
                    p1 = (lerp(pts[0][0], pts[1][0], k * 2), lerp(pts[0][1], pts[1][1], k * 2)); d.line([pts[0], p1], fill=CYAN + (255,), width=11)
                else:
                    p2 = (lerp(pts[1][0], pts[2][0], (k - 0.5) * 2), lerp(pts[1][1], pts[2][1], (k - 0.5) * 2)); d.line([pts[0], pts[1], p2], fill=CYAN + (255,), width=11, joint="curve")
            overlay(im, tick, ai)
            text(im, 905 + dx, y + 78, "OK", "Inter-Black", 52, CYAN, ai)
        else:
            dots = "." * (1 + int(t * 6) % 3)
            text(im, 900 + dx, y + 74, "CHECKING" + dots, "Inter-Bold", 34, MUTED, ai)
    text(im, W / 2, 1172, "LEAN FRO + MATHLIB, 21 NOV", "Inter-Bold", 32, MUTED, a * clamp((t - T["check"] - 2.4) / 0.3), spacing=5)


# ------------------------------------------------------------------ scene G: the cut
def scene_cut(im, t, a):
    x0, x1 = 400, 680
    yb, yt = 1215, 560
    full = yb - yt
    n = lines_at(t)
    h = max(3, full * n / LINES_FULL)
    def bars(d):
        for y in range(yt, yb, 26):
            d.line((x0, y, x0, y + 13), fill=MUTED + (150,), width=3)
            d.line((x1, y, x1, y + 13), fill=MUTED + (150,), width=3)
        d.line((x0, yt, x1, yt), fill=MUTED + (150,), width=3)
        d.rectangle((x0 + 6, yb - h, x1 - 6, yb), fill=GOLD + (255,))
        d.line((x0 - 40, yb + 2, x1 + 40, yb + 2), fill=MUTED + (200,), width=4)
    overlay(im, bars, a)
    text(im, W / 2, yt - 22, "20 NOV: 17,374,215", "Inter-Bold", 34, MUTED, a, spacing=4)
    k = clamp((t - CUT1) / 0.25)
    text(im, W / 2, yb + 72, "25 NOV: 76,000", "Inter-Black", 58, CYAN, a * k)
    text(im, W / 2, yb + 124, "(READABLE VERSION: 300,000)", "Inter-Bold", 28, MUTED, a * k, spacing=4)


# ------------------------------------------------------------------ scene H: the RH band
def _band_data():
    from scipy.special import expi
    N = 1_000_000
    sieve = np.ones(N + 1, bool); sieve[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    pi = np.cumsum(sieve)
    xs = np.unique(np.geomspace(2657, N, 700).astype(int))
    err = expi(np.log(xs)) - pi[xs]                    # li(x) - pi(x)
    band = np.sqrt(xs) * np.log(xs) / (8 * np.pi)      # Schoenfeld 1976: |pi - li| < this for x >= 2657, iff RH
    return xs, err, band


BAND = _band_data()


def scene_band(im, t, a):
    xs, err, band = BAND
    X0, X1, YC = 110, 970, 900
    sc = 330 / band.max()
    lx = np.log(xs)
    px = X0 + (lx - lx[0]) / (lx[-1] - lx[0]) * (X1 - X0)
    reveal = ease(clamp((t - T["tidy"] - 0.1) / 1.6))
    nshow = max(2, int(len(xs) * reveal))
    up = [(px[i], YC - band[i] * sc) for i in range(len(xs))]
    dn = [(px[i], YC + band[i] * sc) for i in range(len(xs))][::-1]
    def fn(d):
        d.polygon(up + dn, fill=CYAN + (38,))
        d.line(up, fill=CYAN + (200,), width=4)
        d.line(dn[::-1], fill=CYAN + (200,), width=4)
        d.line((X0, YC, X1, YC), fill=MUTED + (90,), width=2)
        pts = [(px[i], YC - err[i] * sc) for i in range(nshow)]
        d.line(pts, fill=GOLD + (255,), width=6, joint="curve")
    overlay(im, fn, a)
    if nshow > 2:
        dot(im, px[nshow - 1], YC - err[nshow - 1] * sc, 12, GOLD, a)
    text(im, W / 2, YC - 360, "THE PRIMES NEVER LEAVE THIS BAND", "Inter-Bold", 30, CYAN, a * clamp((t - T["tidy"] - 0.5) / 0.3), spacing=4)
    text(im, W / 2, YC + 400, "PRIMES UP TO 1,000,000", "Inter-Bold", 30, MUTED, a, spacing=5)


# ------------------------------------------------------------------ scene I: IF-theorems become TRUE
CARDS = [("IF RH IS TRUE,", "primes hug their curve."),
         ("IF RH IS TRUE,", "prime gaps stay small."),
         ("IF GRH IS TRUE,", "fast prime tests need no luck.")]


def scene_thm(im, t, a):
    t_true = T["thm"] + 2.05
    for i, (cond, body) in enumerate(CARDS):
        y = 590 + i * 245
        ti = T["thm"] + 0.1 + i * 0.15
        ai = a * clamp((t - ti) / 0.2)
        if ai <= 0.01:
            continue
        dy = 40 * (1 - ease_out(clamp((t - ti) / 0.3)))
        tt_i = t_true + i * 0.22
        done = t >= tt_i
        panel(im, (100, y + dy, 980, y + 205 + dy), ai, fill=(15, 17, 37), border=GOLD if done else (70, 80, 120), width=3 if done else 2)
        text(im, 140, y + 50 + dy, "THEOREM", "Inter-Bold", 26, MUTED, ai, spacing=5, align="l")
        f = font("Inter-Black", 52)
        text(im, 140, y + 112 + dy, cond, "Inter-Black", 52, PINK, ai * (0.55 if done else 1), align="l")
        text(im, 140, y + 172 + dy, body, "Inter-Bold", 44, WHITE, ai, align="l")
        if done:
            k = ease_out(clamp((t - tt_i) / 0.2))
            wlen = f.getlength(cond)
            overlay(im, lambda d, y=y, dy=dy, k=k, wlen=wlen: d.line((136, y + 94 + dy, 136 + (wlen + 8) * k, y + 94 + dy), fill=PINK + (255,), width=8), ai)
            s = 1.5 - 0.5 * ease_out(clamp((t - tt_i) / 0.16))
            text(im, 850, y + 122 + dy, "TRUE.", "Inter-Black", 64, GOLD, ai * clamp((t - tt_i) / 0.1), stroke=4, scale=s)


# ------------------------------------------------------------------ scene J: share card
def scene_share(im, t, a):
    text(im, W / 2, 640, "JUST HAPPENED, EXPLAINED", "Inter-Bold", 32, CYAN, a, spacing=6)
    text(im, W / 2, 790, "Send this to someone", "Inter-Black", 86, WHITE, a, stroke=4)
    text(im, W / 2, 900, "who hated math.", "Inter-Black", 100, GOLD, a, stroke=4)
    text(im, W / 2, 1050, "Heard about it? YES or NO", "Inter-Bold", 50, MUTED, a * clamp((t - T["share"] - 0.6) / 0.3))


HOOK = [[("Math's biggest problem", WHITE)], [("just got ", WHITE), ("SOLVED.", GOLD)]]


# ------------------------------------------------------------------ frame
def frame(t):
    im = BG.copy()
    # A: strip + hook (0 .. primes)
    aA = win(t, 0, T["primes"] - 0.05, 0, 0.3)
    draw_strip(im, t, aA)
    if t < T["primes"] - 0.05:
        ha = clamp((T["primes"] - 0.05 - t) / 0.3)
        hook_text(im, t, HOOK, alpha=ha)
        if t >= T["stamp_ai"]:
            stamp(im, t, T["stamp_ai"], [("WITH AN ", WHITE), ("AI.", CYAN)], y=760, size=150, panel=True)
    # B: primes
    aB = win(t, T["primes"] - 0.15, T["line"] - 0.05, 0.3, 0.3)
    if aB > 0:
        headline(im, t, T["primes"] - 0.15, T["line"] - 0.05, [("1859", 170, GOLD, 0.0), ("The primes hide a pattern.", 66, WHITE, 0.25)], y=420, gap=150)
        text(im, W / 2, 250, "RIEMANN'S BET", "Inter-Bold", 34, MUTED, aB, spacing=6)
        scene_primes(im, t, aB)
    # C + D: zeros snap onto the line, then 167 years
    aC = win(t, T["line"] - 0.15, T["lean"] - 0.05, 0.3, 0.3)
    if aC > 0:
        dim = 1.0 - 0.6 * ease(clamp((t - T["years"]) / 0.4))
        draw_strip(im, t, aC * dim, snap=T["line"] + 0.35)
        headline(im, t, T["line"] - 0.15, T["years"], [("Every key zero:", 84, WHITE, 0.0), ("on ONE line.", 104, GOLD, 0.55)], y=360, gap=120)
    if T["years"] <= t < T["lean"] - 0.05:
        aD = win(t, T["years"], T["lean"] - 0.05, 0.15, 0.3)
        u = ease_out(clamp((t - T["years"]) / 1.0))
        yr = int(round(1859 + 167 * u))
        text(im, W / 2, 820, str(yr), "Inter-Black", 210, WHITE, aD, stroke=5)
        text(im, W / 2, 940, "167 YEARS", "Inter-Black", 84, GOLD, aD * clamp((t - T["years"] - 0.2) / 0.2), stroke=4)
        if t >= T["years"] + 1.8:
            stamp(im, t, T["years"] + 1.8, [("NO PROOF.", PINK)], y=1130, size=140, panel=True, flash=False)
    # E: Lean
    aE = win(t, T["lean"] - 0.1, T["check"] - 0.05, 0.3, 0.3)
    if aE > 0:
        if t < T["howlong"]:
            headline(im, t, T["lean"] - 0.1, T["howlong"], [("A proof in Lean:", 96, WHITE, 0.0), ("code a computer checks.", 60, CYAN, 0.9)], y=340, gap=100)
        else:
            headline(im, t, T["howlong"], T["check"], [("How long is it?", 110, GOLD, 0.0)], y=400, fi=0.1)
        g0 = T["howlong"] + 0.25
        big_panel(im, t, aE * (1 - clamp((t - g0) / 0.3)))
        levels = [(g0, 3, 4), (g0 + 0.5, 5, 7), (g0 + 1.0, 8, 11)]
        for k, (tl, c_, r_) in enumerate(levels):
            nxt = levels[k + 1][0] if k + 1 < len(levels) else 1e9
            ag = aE * clamp((t - tl) / 0.25) * (1 - clamp((t - nxt) / 0.25))
            grid(im, t, ag, c_, r_, tl)
        if t >= T["big"]:
            stamp(im, t, T["big"], [("17 MILLION", GOLD)], y=860, size=150, panel=True)
        if t >= T["big"] + 0.3:
            stamp(im, t, T["big"] + 0.3, [("LINES.", WHITE)], y=1030, size=120, panel=True, flash=False)
        if t >= T["big"] + 0.8:
            text(im, W / 2, 1185, "IN 175,187 FILES", "Inter-Black", 46, CYAN, aE * clamp((t - T["big"] - 0.8) / 0.2), stroke=4, spacing=3)
    # F: checkers
    aF = win(t, T["check"] - 0.05, T["cut"] - 0.05, 0.25, 0.3)
    if aF > 0:
        headline(im, t, T["check"] - 0.05, T["cut"] - 0.05, [("Nobody can read that.", 84, WHITE, 0.0), ("Machines checked it.", 66, CYAN, 1.3)], y=340, gap=100)
        scene_check(im, t, aF)
        if t >= T["check"] + 2.75:
            stamp(im, t, T["check"] + 2.75, [("CORRECT.", GOLD)], y=1268, size=118, panel=True)
    # G: the cut
    aG = win(t, T["cut"] - 0.05, T["tidy"] - 0.05, 0.25, 0.3)
    if aG > 0:
        headline(im, t, T["cut"] - 0.05, T["tidy"] - 0.05, [("5 days later:", 100, WHITE, 0.0)], y=360)
        scene_cut(im, t, aG)
        if t >= CUT1 + 0.35:
            stamp(im, t, CUT1 + 0.35, [("229x SHORTER.", CYAN)], y=900, size=110, panel=True, flash=False)
    # H: band
    aH = win(t, T["tidy"] - 0.05, T["thm"] - 0.05, 0.25, 0.3)
    if aH > 0:
        headline(im, t, T["tidy"] - 0.05, T["thm"] - 0.05, [("Primes:", 100, WHITE, 0.0), ("as tidy as possible.", 84, GOLD, 0.35)], y=320, gap=105)
        scene_band(im, t, aH)
    # I: theorems
    aI = win(t, T["thm"] - 0.05, T["share"] - 0.05, 0.25, 0.3)
    if aI > 0:
        headline(im, t, T["thm"] - 0.05, T["share"] - 0.05, [("Every \"IF RH...\" theorem", 76, WHITE, 0.0), ("is now just TRUE.", 92, GOLD, 2.0)], y=340, gap=105)
        scene_thm(im, t, aI)
    # J: share card, then hand back to frame 0
    aJ = win(t, T["share"] - 0.1, END - 0.3, 0.25, 0.3)
    loop = clamp((t - (END - 0.6)) / 0.5)
    if t >= T["share"] - 0.1:
        draw_strip(im, 0.0, max(0.25 * clamp((t - T["share"] + 0.1) / 0.3), loop), c=cam(0.0))
        scene_share(im, t, aJ)
        if loop > 0:
            hook_text(im, 1.0, HOOK, alpha=loop)
    hud(im, t)
    return im


def stills():
    ts = [0.0, 1.0, T["stamp_ai"] + 0.3, T["primes"] + 2.5, T["line"] + 1.3, T["years"] + 1.6, T["lean"] + 2.0,
          T["howlong"] + 0.9, T["big"] + 1.0, T["check"] + 2.9, T["cut"] + 2.0, T["tidy"] + 1.8,
          T["thm"] + 2.8, T["share"] + 1.0, END - 0.3, END - 1 / 30]
    ims = [frame(t).convert("RGB").resize((270, 480), Image.LANCZOS) for t in ts]
    sheet = Image.new("RGB", (270 * 8, 480 * 2), (0, 0, 0))
    for k, s in enumerate(ims):
        sheet.paste(s, ((k % 8) * 270, (k // 8) * 480))
    sheet.save(os.path.join(HERE, "stills.jpg"), quality=88)
    for k, t in enumerate(ts):
        if len(sys.argv) > 2:
            frame(t).convert("RGB").save(f"/tmp/f040_{k:02d}.jpg", quality=90)
    print("stills.jpg", [round(t, 2) for t in ts])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        stills()
    elif len(sys.argv) > 1 and sys.argv[1] == "at":
        for s in sys.argv[2:]:
            frame(float(s)).convert("RGB").save(f"/tmp/at_{s}.jpg", quality=90)
    else:
        n = int(round(END * FPS))
        w = Writer(os.path.join(HERE, "v040_video.mp4"))
        for i in range(n):
            w.write(frame(i / FPS))
            if i % 150 == 0:
                print(i, "/", n, flush=True)
        w.close()
        print("v040_video.mp4", n, "frames")
