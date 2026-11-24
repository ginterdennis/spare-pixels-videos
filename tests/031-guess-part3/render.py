"""031 Guess it before the balls do (Part 3). Three pictures under a dark scratch-off cover; bouncing
balls uncover them. Strawberry (payoff 3.0 s), sunflower (10.0 s), watermelon close-up (17.5 s, rind hidden at the top). No pixel look: smooth
vector art (skia) and round soft-edged holes. Loops: the last second replays the kiwi's lead-in."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp, countdown
from sim import simulate, BOX, HB
import art

DUR = 21.5
X0, Y0 = (W - BOX) // 2, 610
BALL_COLS = [WHITE, PINK, CYAN, GOLD]
BG = vgrad()

ROUNDS = [
    dict(pic=art.strawberry, seed=1, cfg=dict(v0=420, p_spawn=0.5, cap=14, n0=2), t0=-2.7, end=3.0, name="STRAWBERRY.", col=PINK),
    dict(pic=art.sunflower, seed=6, cfg=dict(v0=420, p_spawn=0.5, cap=14, n0=2), t0=3.9, end=10.0, name="SUNFLOWER.", col=GOLD),
    dict(pic=art.watermelon, seed=126, cfg=dict(v0=380, p_spawn=0.4, cap=11, low_start=True), t0=10.9, end=17.5, name="WATERMELON.", col=PINK),
]
SWEEP = 0.32
yy, xx = np.mgrid[0:HB, 0:HB]
DIST = np.hypot(yy - HB / 2, xx - HB / 2); DIST /= DIST.max()
for R in ROUNDS:
    T = R["end"] - R["t0"] + 0.2
    R["FR"], rev, R["HITS"], R["BORN"] = simulate(seed=R["seed"], T=T, **R["cfg"])
    ts = R["end"] - R["t0"] - SWEEP              # local time the sweep starts
    rem = rev > ts
    rev[rem] = ts + 0.03 + DIST[rem] * (SWEEP - 0.06)
    R["REV"] = rev
    R["PIC"] = R["pic"]()
    R["ts"] = ts

# cover: dark slate with a diagonal sheen and fine grain (static)
rng = np.random.default_rng(2)
gy, gx = np.mgrid[0:BOX, 0:BOX]
sheen = 0.5 + 0.5 * np.sin((gx + gy) / BOX * math.pi * 1.6)
COVER = (np.array((30, 34, 60), float)[None, None] + sheen[..., None] * np.array((10, 11, 18), float)[None, None]
         + rng.normal(0, 2.2, (BOX, BOX, 1)))
# rounded corners
cm = Image.new("L", (BOX, BOX), 0)
ImageDraw.Draw(cm).rounded_rectangle((0, 0, BOX - 1, BOX - 1), radius=30, fill=255)
CORNER = np.asarray(cm, float)[..., None] / 255


def up(a):
    return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize((BOX, BOX), Image.BILINEAR))


def reveal(R, s):
    """Picture under cover for round R at local time s -> (rgb, coverage)."""
    age = s - R["REV"]
    m = np.clip(age / 0.10, 0, 1)
    fl = np.clip(1 - age / 0.28, 0, 1) * (age >= 0)
    M = up(m)[..., None]; F = up(fl)[..., None]
    pic = R["PIC"] * (1 - F * 0.75) + 255 * F * 0.75
    return COVER * (1 - M) + pic * M, float(np.mean(age >= 0))


def balls(im, R, s, alpha=1.0):
    if alpha <= 0 or s < 0:
        return
    FR, HITS, BORN = R["FR"], R["HITS"], R["BORN"]
    fi = min(int(s * FPS), len(FR) - 1)
    ov = Image.new("RGBA", (BOX + 120, BOX + 120), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (ht, hx, hy, bi) in HITS:
        a = s - ht
        if 0 <= a < 0.4:
            rr = 14 + a * 140
            al = int(170 * (1 - a / 0.4) * alpha)
            od.ellipse((hx + 60 - rr, hy + 60 - rr, hx + 60 + rr, hy + 60 + rr), outline=BALL_COLS[bi % 4] + (al,), width=4)
    for lag in range(6, 0, -1):
        j = fi - lag
        if j < 0:
            continue
        for bi, (bx, by) in enumerate(FR[j]):
            if BORN[bi] > s - lag / FPS:
                continue
            r = 15 * (1 - lag / 8)
            al = int(110 * (1 - lag / 7) * alpha)
            od.ellipse((bx + 60 - r, by + 60 - r, bx + 60 + r, by + 60 + r), fill=BALL_COLS[bi % 4] + (al,))
    for bi, (bx, by) in enumerate(FR[fi]):
        if BORN[bi] > s:
            continue
        pop = 1.0 if BORN[bi] == 0 else ease_out((s - BORN[bi]) / 0.18)
        spr, Rr = glow_sprite(15, BALL_COLS[bi % 4])
        if pop < 1:
            sz = max(2, int(2 * Rr * pop)); spr = spr.resize((sz, sz)); R2 = sz // 2
        else:
            R2 = Rr
        if alpha < 1:
            spr = spr.copy(); spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
        ov.alpha_composite(spr, (int(bx + 60 - R2), int(by + 60 - R2)))
    im.alpha_composite(ov, (X0 - 60, Y0 - 60))


def box_state(t):
    """-> (box rgb, round index for balls, local s, coverage, ball alpha)"""
    R1, R2, R3 = ROUNDS
    if t >= 20.5:                                  # loop lead-in: strawberry again, wipe over the watermelon
        s = t - DUR - R1["t0"]
        a, cov = reveal(R1, s)
        w = ease((t - 20.5) / 0.35) * BOX
        if w < BOX:
            b, _ = reveal(R3, 99)
            rows = (np.arange(BOX) < w)[:, None, None]
            a = np.where(rows, a, b)
        return a, 0, s, cov, ease((t - 20.5) / 0.3)
    for k, R in enumerate(ROUNDS):
        nxt = ROUNDS[k + 1]["t0"] if k < 2 else 99
        if t < nxt:
            s = t - R["t0"]
            a, cov = reveal(R, s)
            wipe0 = nxt - 0.35
            if k < 2 and t >= wipe0:                # cover slides back down for the next round
                w = ease((t - wipe0) / 0.35) * BOX
                rows = (np.arange(BOX) < w)[:, None, None]
                a = np.where(rows, COVER, a)
            ba = 1 - ease((s - R["ts"]) / SWEEP)
            return a, k, s, cov, ba
    raise ValueError


def top_text(d, t, lines, t_in, t_out):
    a = ease((t - t_in) / 0.18) * (1 - ease((t - t_out + 0.15) / 0.15))
    if a <= 0:
        return
    (l1, c1), sub = lines
    dy = 16 * (1 - ease((t - t_in) / 0.25))
    draw_rich(d, W / 2, 410 + dy, [(l1, lerpc(BG_TOP, c1, a))], font("Inter-Black", 104))
    if sub:
        draw_rich(d, W / 2, 500 + dy, [(x, lerpc(BG_TOP, c, a)) for x, c in sub], font("Inter-Bold", 54))


SCRIPT = [
    (3.9, 6.6, ("Harder one.", WHITE), [("Lock it in ", WHITE), ("early", GOLD), (".", WHITE)]),
    (6.6, 8.9, ("Got it yet?", WHITE), [("Say it out loud.", WHITE)]),
    (8.9, 9.95, ("Last chance...", PINK), None),
    (10.9, 13.6, ("Last one.", WHITE), [("The ", WHITE), ("hardest", GOLD), (" yet.", WHITE)]),
    (13.6, 16.3, ("Strawberry?", WHITE), [("Look ", WHITE), ("closer", GOLD), (".", WHITE)]),
    (16.3, 17.45, ("Last chance...", PINK), None),
]
HOOK = [[("Guess it before", WHITE)], [("the ", WHITE), ("balls", GOLD), (" do.", WHITE)]]


def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    a, k, s, cov, ba = box_state(t)
    a = BG[Y0:Y0 + BOX, X0:X0 + BOX].astype(float) * (1 - CORNER) + a * CORNER
    im.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (X0, Y0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((X0 - 8, Y0 - 8, X0 + BOX + 8, Y0 + BOX + 8), radius=36, outline=(70, 76, 118), width=3)
    balls(im, ROUNDS[k], s, ba)
    d = ImageDraw.Draw(im)
    # ---- opening (and the loop lead-in)
    if t < 3.0:
        hook_text(im, t, HOOK)
        countdown(im, t, 0.0, 3.0, W / 2, 1468, r=62)
    if t >= 20.9:
        hook_text(im, t, HOOK, alpha=ease((t - 20.9) / 0.5), punch=0)
    # ---- payoffs
    for R in ROUNDS:
        stamp(im, t, R["end"], [(R["name"], R["col"])], y=505, size=150 if len(R["name"]) < 8 else 116, hold=0.88)
    for (t_in, t_out, l1, sub) in SCRIPT:
        if t_in <= t < t_out:
            top_text(d, t, (l1, sub), t_in, t_out)
    # ---- HUD (after the opening, until the last payoff)
    if 3.9 <= t < 17.5:
        ha = ease((t - 3.9) / 0.3)
        fl = font("Inter-SemiBold", 28); fn = font("Inter-Black", 72)
        label(d, 320, 1442, "REVEALED", fl, lerpc(BG_BOT, MUTED, ha), spacing=5)
        label(d, 760, 1442, "ROUND", fl, lerpc(BG_BOT, MUTED, ha), spacing=5)
        draw_rich(d, 320, 1522, [(f"{cov * 100:.0f}%", lerpc(BG_BOT, WHITE, ha))], fn)
        draw_rich(d, 760, 1522, [(f"{k + 1}", lerpc(BG_BOT, GOLD, ha)), ("/3", lerpc(BG_BOT, WHITE, ha))], fn)
    # ---- CTA
    if 18.4 <= t < 20.6:
        ca = ease((t - 18.4) / 0.25) * (1 - ease((t - 20.35) / 0.25))
        draw_rich(d, W / 2, 380, [("Which one got you?", lerpc(BG_TOP, WHITE, ca))], font("Inter-Black", 92))
        draw_rich(d, W / 2, 530, [("1", lerpc(BG_TOP, GOLD, ca)), (", ", lerpc(BG_TOP, WHITE, ca)), ("2", lerpc(BG_TOP, PINK, ca)),
                                  (" or ", lerpc(BG_TOP, WHITE, ca)), ("3", lerpc(BG_TOP, CYAN, ca)), ("?", lerpc(BG_TOP, WHITE, ca))],
                  font("Inter-Black", 120))
        draw_rich(d, W / 2, 1482, [("Part 4 is harder. ", lerpc(BG_BOT, WHITE, ca)), ("Follow.", lerpc(BG_BOT, GOLD, ca))],
                  font("Inter-Bold", 54))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.5, 2.95, 3.1, 3.7, 6.0, 8.0, 10.1, 12.0, 14.5, 17.0, 17.6, 19.0, 20.7, 21.45]
        for t in ts:
            frame(int(round(t * FPS))).save(f"still_{t:05.2f}.png")
        for R in ROUNDS:
            loc = R["end"] - R["t0"]
            print(R["name"], " ".join(f"{x:.1f}:{np.mean(R['REV'] <= x) * 100:.0f}%" for x in np.arange(0.5, loc + 0.01, 0.5)))
    else:
        w = Writer("v031_video.mp4")
        for i in range(int(DUR * FPS)):
            w.write(frame(i))
        w.close(); print("frames", w.n)
