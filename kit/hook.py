"""Hook kit v2 (21 Nov 2026). Opening-seconds building blocks that follow HOOKS.md.

Why: on the three videos that reached For You (001, 006, 018) only 34-42 % of viewers were
still there at second 3. Every opening was a small headline strip over a still picture.
These helpers make the opening a big, short viewer task over something already moving,
with a sound hit on frame 0 and a visible clock to the first payoff.

    from hook import *
    hook_text(im, t, [[("How many", WHITE)], [("BLACK dots?", GOLD)]])   # big task, punch-in
    countdown(im, t, 0.0, 3.0, W/2, 1560)                                 # 3-2-1 ring to the reveal
    stamp(im, t, 3.0, [("ZERO.", GOLD)], y=520)                           # slam-in payoff
    hook_sfx(mix, reveal=3.0, ticks=(0.0, 1.0, 2.0))                       # hit at 0, ticks, riser, boom
Check a finished file with:  python3 kit/hookcheck.py videos/<file>.mp4 --hook "<words on frame 0>" --reveal 3.0
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *

HOOK_SIZE = 112          # px, Unbounded ExtraBold (brand display face since 28 Nov; auto-shrinks to fit)
HOOK_FONT = "Unbounded-ExtraBold"
# New videos: prefer kit/brand.py hook()/frame0() for the full brand frame 0 (icon, tag, gradient word, horizon).
HOOK_Y = 400             # baseline of the first hook line (safe area starts at ~180)
MAX_WORDS = 6


def _words(lines):
    return sum(len("".join(t for t, _ in parts).split()) for parts in lines)


def _layer(lines, size, gap, panel, pad=(48, 34)):
    f = font(HOOK_FONT, size)
    widths = [sum(f.getlength(t) for t, _ in parts) for parts in lines]
    lw, lh = int(max(widths)) + 2 * pad[0], int(len(lines) * size * gap + 2 * pad[1])
    im = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if panel:
        d.rounded_rectangle((0, 0, lw - 1, lh - 1), radius=36, fill=(14, 10, 28, 215))   # brand night panel
    for k, parts in enumerate(lines):
        base = pad[1] + size * 0.86 + k * size * gap
        x = (lw - widths[k]) / 2
        for txt, col in parts:
            # dark outline keeps the text readable over bright or busy visuals
            d.text((x, base), txt, font=f, fill=col + (255,), anchor="ls",
                   stroke_width=max(3, size // 26), stroke_fill=(5, 3, 11, 255))
            x += f.getlength(txt)
    return im


def hook_text(im, t, lines, y=HOOK_Y, size=HOOK_SIZE, gap=1.08, panel=True, punch=0.16, alpha=1.0,
              t0=0.0, check=True):
    """Big centred viewer task. Fully readable on frame t0, then a short 1.10 -> 1.00 punch.
    lines: [[(text, colour), ...], ...]  (max 2 lines, max 6 words)."""
    if check:
        assert len(lines) <= 2 and _words(lines) <= MAX_WORDS, "hook: max 2 lines / 6 words"
    if alpha <= 0 or t < t0:
        return
    # shrink to fit: the panel at its punch-in scale (x1.10) must leave 60 px each side
    f = font(HOOK_FONT, size)
    widest = max(sum(f.getlength(t_) for t_, _ in parts) for parts in lines) + 96
    if widest * 1.10 > W - 120:
        size = int(size * (W - 120) / (widest * 1.10))
    lay = _layer(tuple(tuple(p) for p in lines), size, gap, panel)
    u = (t - t0) / punch if punch else 1
    s = 1.10 - 0.10 * ease_out(u) if u < 1 else 1.0
    if s != 1.0:
        lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    if alpha < 1:
        a = lay.getchannel("A").point(lambda v: int(v * alpha)); lay.putalpha(a)
    top = int(y - size * 0.86 - 34 - (lay.height - lay.height / s) / 2)
    im.alpha_composite(lay, (int(W / 2 - lay.width / 2), max(0, top)))


def stamp(im, t, t0, parts, y=520, size=170, dur=0.14, flash=True, panel=False, hold=None):
    """Payoff that slams in: scale 1.6 -> 1.0 in `dur`, with a white flash on impact."""
    if t < t0 or (hold is not None and t > t0 + hold):
        return
    u = (t - t0) / dur
    s = 1.6 - 0.6 * ease_out(u) if u < 1 else 1.0
    lay = _layer(((tuple(parts)),), size, 1.0, panel, pad=(30, 20))
    if s != 1.0:
        lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    a = min(1.0, u * 2)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y - lay.height / 2)))
    if flash and t - t0 < 0.12:
        k = 1 - (t - t0) / 0.12
        im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(90 * k))))


def countdown(im, t, t0, t1, cx, cy, r=74, col=GOLD, label_txt=None):
    """Ring that empties from t0 to t1 with the whole seconds left in the middle.
    A visible clock to the payoff is the cheapest open loop there is."""
    if not (t0 <= t < t1):
        return
    d = ImageDraw.Draw(im)
    left = t1 - t
    frac = left / (t1 - t0)
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=(8, 9, 20, 215))
    d.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=(60, 64, 90, 255), width=14)
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frac, fill=col + (255,), width=14)
    n = str(int(math.ceil(left - 1e-6)))
    f = font("Unbounded-ExtraBold", int(r * 0.9))
    d.text((cx, cy + r * 0.40), n, font=f, fill=WHITE + (255,), anchor="ms")
    if label_txt:
        draw_rich(d, cx, cy + r + 62, [(label_txt, MUTED + (255,))], font("JBMono-Bold", 30), spacing=4)


def hook_sfx(m, reveal=None, ticks=(), gain=1.0):
    """Sound hit on frame 0 (no silent lead-in), optional clock ticks, riser + boom at the reveal."""
    m.add(0.0, sub_boom(0.7, 52), gain=0.55 * gain)
    m.add(0.0, click(1800, 0.03), gain=0.35 * gain)
    m.add(0.0, whoosh(0.35, 3000, 300), gain=0.18 * gain)
    for k, x in enumerate(ticks):
        m.add(x, click(2600 if k % 2 else 2200, 0.025), gain=0.32 * gain)
        m.add(x, tri(mtof(84 + (k == len(ticks) - 1) * 5), 0.09), gain=0.10 * gain)
    if reveal is not None:
        m.add(max(0, reveal - 0.45), riser(0.45, 500, 2200), gain=0.22 * gain)
        m.add(reveal, sub_boom(1.1, 46), gain=0.7 * gain)
        m.add(reveal, snare(), gain=0.25 * gain)
        for j, nn in enumerate([81, 84, 88, 93]):
            m.add(reveal + j * 0.04, bell(mtof(nn), 1.2, 0.45), gain=0.10 * gain, verb=0.4)
