"""032 Spot the odd one out (explore: timed search puzzle, 3 rounds, no voice).
Round 1: one 9 among 6s (payoff 3.0 s). Round 2: one "rn" among "m"s (10.0 s). Round 3: one Q among Os
(17.5 s). Glyphs bob on frame 0, a 3-2-1 ring runs into each payoff, then everything dims except the odd one,
which turns gold inside a ring. Loops: the last second fades round 1 and the hook back in."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *
from hook import hook_text, stamp, countdown

DUR = 21.5
BX0, BY0, BOX = 160, 610, 760          # puzzle area (same box as the guessing game)
BG = vgrad()

ROUNDS = [
    dict(norm="6", odd="9", n=7, size=92, odd_rc=(4, 2), t0=-0.5, end=3.0, cd=(0.0, 3.0), word=("TOO EASY?", GOLD)),
    dict(norm="m", odd="rn", n=9, size=66, odd_rc=(2, 6), t0=3.9, end=10.0, cd=(7.0, 10.0), word=("GOT IT?", PINK)),
    dict(norm="O", odd="Q", n=12, size=50, odd_rc=(9, 1), t0=10.9, end=17.5, cd=(14.5, 17.5), word=("THERE.", CYAN)),
]
F = "Inter-Black"


def sprite(txt, size, col, scale=1.0):
    f = font(F, int(size * scale))
    w = int(text_w(txt, f)) + 20
    h = int(size * scale * 1.5)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((w / 2, h / 2), txt, font=f, fill=col + (255,), anchor="mm")
    return im


def dim(im, a):
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


for R in ROUNDS:
    R["cell"] = BOX / R["n"]
    R["sp_n"] = sprite(R["norm"], R["size"], WHITE)
    R["sp_o"] = sprite(R["odd"], R["size"], WHITE)
    R["sp_dim"] = dim(R["sp_n"], 0.22)
    R["sp_gold"] = sprite(R["odd"], R["size"], GOLD, 1.55)


def grid(im, R, s, reveal_k, alpha=1.0):
    """Draw round R at local time s (s=0 is the round start). reveal_k 0..1 = payoff state."""
    n, cell = R["n"], R["cell"]
    zoom = 1.0 + 0.035 * ease(min(1, max(0, s / 6)))
    cx, cy = BX0 + BOX / 2, BY0 + BOX / 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odd_pos = None
    for r in range(n):
        for c in range(n):
            ph = 0.9 * r + 1.7 * c
            bx = BX0 + (c + 0.5) * cell + 2.5 * math.sin(s * 2.2 + ph)
            by = BY0 + (r + 0.5) * cell + 3.5 * math.sin(s * 2.9 + ph * 1.3)
            x = cx + (bx - cx) * zoom
            y = cy + (by - cy) * zoom
            is_odd = (r, c) == R["odd_rc"]
            if is_odd:
                odd_pos = (x, y)
                if reveal_k > 0:
                    continue
                sp = R["sp_o"]
            else:
                sp = R["sp_dim"] if reveal_k > 0.5 else R["sp_n"]
                if 0 < reveal_k <= 0.5:
                    sp = dim(R["sp_n"], 1 - 0.78 * reveal_k * 2)
            if alpha < 1:
                sp = dim(sp, alpha)
            layer.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    if reveal_k > 0:
        x, y = odd_pos
        k = ease_out(min(1, reveal_k * 1.6))
        g = R["sp_gold"]
        sz = max(2, int(g.width * (0.65 + 0.35 * k))), max(2, int(g.height * (0.65 + 0.35 * k)))
        gs = g.resize(sz, Image.LANCZOS)
        rr = 0.95 * R["size"] * (1.4 - 0.4 * k) + 18
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rd.ellipse((x - rr, y - rr, x + rr, y + rr), outline=GOLD + (int(255 * k * alpha),), width=9)
        glow = ring.filter(ImageFilter.GaussianBlur(10))
        layer.alpha_composite(glow)
        layer.alpha_composite(glow)
        layer.alpha_composite(ring)
        if alpha < 1:
            gs = dim(gs, alpha)
        layer.alpha_composite(gs, (int(x - gs.width / 2), int(y - gs.height / 2)))
    im.alpha_composite(layer)


def top_text(d, t, l1, sub, t_in, t_out):
    a = ease((t - t_in) / 0.18) * (1 - ease((t - t_out + 0.15) / 0.15))
    if a <= 0:
        return
    text, c1 = l1
    dy = 16 * (1 - ease((t - t_in) / 0.25))
    draw_rich(d, W / 2, 410 + dy, [(text, lerpc(BG_TOP, c1, a))], font("Inter-Black", 104))
    if sub:
        draw_rich(d, W / 2, 500 + dy, [(x, lerpc(BG_TOP, c, a)) for x, c in sub], font("Inter-Bold", 54))


SCRIPT = [
    (3.9, 6.9, ("Harder.", WHITE), [("Don't ", WHITE), ("blink", GOLD), (".", WHITE)]),
    (6.9, 9.95, ("Still looking?", PINK), None),
    (10.9, 14.4, ("Last one.", WHITE), [("The ", WHITE), ("hardest", GOLD), (" yet.", WHITE)]),
    (14.4, 17.45, ("3 seconds left.", PINK), None),
]
HOOK = [[("Spot the ", WHITE), ("odd", GOLD)], [("one out.", WHITE)]]


def state(t):
    """-> (round, local s, reveal_k, alpha)"""
    if t >= 20.5:                                          # loop lead-in: round 1 again
        R = ROUNDS[0]
        return R, t - DUR - R["t0"], 0.0, ease((t - 20.5) / 0.4)
    for k, R in enumerate(ROUNDS):
        nxt = ROUNDS[k + 1]["t0"] if k < 2 else 99
        if t < nxt:
            s = t - R["t0"]
            rk = 0.0 if t < R["end"] else min(1.0, (t - R["end"]) / 0.35)
            a = 1.0
            if k < 2 and t >= nxt - 0.35:
                a = 1 - ease((t - (nxt - 0.35)) / 0.35)
            if k == 2 and t >= 18.3:
                a = 1 - 0.75 * ease((t - 18.3) / 0.3)
            return R, s, rk, a
    raise ValueError


def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((BX0 - 24, BY0 - 24, BX0 + BOX + 24, BY0 + BOX + 24), radius=36, fill=(20, 23, 44), outline=(70, 76, 118), width=3)
    R, s, rk, a = state(t)
    grid(im, R, s, rk, a)
    d = ImageDraw.Draw(im)
    if t < 3.0:
        hook_text(im, t, HOOK)
    if t >= 20.9:
        hook_text(im, t, HOOK, alpha=ease((t - 20.9) / 0.5), punch=0)
    for Rr in ROUNDS:
        c0, c1 = Rr["cd"]
        if c0 <= t < c1:
            countdown(im, t, c0, c1, W / 2, 1468, r=62)
        stamp(im, t, Rr["end"], [Rr["word"]], y=505, size=150, hold=0.85)
    for (t_in, t_out, l1, sub) in SCRIPT:
        if t_in <= t < t_out:
            top_text(d, t, l1, sub, t_in, t_out)
    if 3.9 <= t < 17.5 and not any(Rr["cd"][0] <= t < Rr["cd"][1] for Rr in ROUNDS):
        ha = ease((t - 3.9) / 0.3)
        draw_rich(d, W / 2, 1490, [("ROUND ", lerpc(BG_BOT, MUTED, ha)), (f"{ROUNDS.index(R) + 1}", lerpc(BG_BOT, GOLD, ha)), ("/3", lerpc(BG_BOT, WHITE, ha))], font("Inter-Black", 60))
    if 18.4 <= t < 20.6:
        ca = ease((t - 18.4) / 0.25) * (1 - ease((t - 20.35) / 0.25))
        draw_rich(d, W / 2, 380, [("Which round got you?", lerpc(BG_TOP, WHITE, ca))], font("Inter-Black", 88))
        draw_rich(d, W / 2, 530, [("1", lerpc(BG_TOP, GOLD, ca)), (", ", lerpc(BG_TOP, WHITE, ca)), ("2", lerpc(BG_TOP, PINK, ca)),
                                  (" or ", lerpc(BG_TOP, WHITE, ca)), ("3", lerpc(BG_TOP, CYAN, ca)), ("?", lerpc(BG_TOP, WHITE, ca))],
                  font("Inter-Black", 120))
        draw_rich(d, W / 2, 1482, [("Part 2 is harder. ", lerpc(BG_BOT, WHITE, ca)), ("Follow.", lerpc(BG_BOT, GOLD, ca))], font("Inter-Bold", 54))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "stills":
        for t in [float(x) for x in sys.argv[2:]]:
            frame(int(round(t * FPS))).save(f"still_{t:05.2f}.png")
    else:
        w = Writer("v032_video.mp4")
        for i in range(int(DUR * FPS)):
            w.write(frame(i))
        w.close(); print("frames", w.n)
