"""037 Pause challenge (explore). A stopwatch runs; the viewer tries to pause the video on an exact number.
At 30 fps every number is on screen for ONE frame, and most hundredths never appear at all, so people
rewatch and try again (watch time > 100 %) and comment the number they stopped on.
Round 1: 1x speed, target 5.00 (on screen at 2.4 s, gold for that one frame), '1 FRAME.' at 2.6 s.
Round 2: 2x speed, target 8.00. Round 3: 3x speed, target 7.77. The target frame is the only gold frame:
pausing on gold = you won (screenshot it). Loops: the clock spins back to 2.60 and round 1 starts again.
No voice (a game: people look). No pixel look: skia rings, Inter digits."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import skia
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp

DUR = 13.3
CX, CY, RR = 540, 1000, 330
# (round start t, run start t, clock start value, speed, target value, freeze t, stamp text)
ROUNDS = [
    dict(t0=0.0, run=0.0, v0=2.60, speed=1, target=5.00, stop=2.6),
    dict(t0=4.1, run=4.55, v0=5.00, speed=2, target=8.00, stop=6.35),
    dict(t0=7.3, run=7.7, v0=1.77, speed=3, target=7.77, stop=10.0),
]
for R in ROUNDS:
    # frame on which the target shows (exact, on the 30 fps grid)
    k = round((R["target"] - R["v0"]) / R["speed"] * FPS)
    R["hit_i"] = round(R["run"] * FPS) + k
    assert abs(R["v0"] + k * R["speed"] / FPS - R["target"]) < 1e-9, R
REWIND0, REWIND1 = 12.65, 13.3
HOLDS = [1.3, 0.65, 0.9]                            # how long each round's stamp stays up                     # clock spins back to 2.60 for the loop
BG = vgrad()
rng = np.random.default_rng(3)
DOTS = rng.uniform(0, 1, (60, 4))                   # x, y, speed, size


def clock_state(i):
    """-> (value, round index, is_target_frame, frozen)"""
    t = i / FPS
    for k in range(2, -1, -1):
        R = ROUNDS[k]
        if t >= R["t0"]:
            break
    if t >= REWIND0:
        u = ease((t - REWIND0) / (REWIND1 - REWIND0))
        return lerp(ROUNDS[2]["v0"] + (round(ROUNDS[2]["stop"] * FPS) - round(ROUNDS[2]["run"] * FPS)) * 3 / FPS, ROUNDS[0]["v0"], u), 2, False, True
    run_i = round(R["run"] * FPS)
    stop_i = round(R["stop"] * FPS)
    j = min(max(i, run_i), stop_i) - run_i
    v = R["v0"] + j * R["speed"] / FPS
    return v, k, i == R["hit_i"], i >= stop_i


def ring(im, frac, col, glow=0.0, alpha=1.0):
    s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.Color(0, 0, 0, 0))
    rect = skia.Rect(CX - RR, CY - RR, CX + RR, CY + RR)
    c.drawCircle(CX, CY, RR + 26, skia.Paint(AntiAlias=True, Color=skia.Color(10, 11, 24, int(235 * alpha))))
    c.drawArc(rect, 0, 360, False, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=22,
                                              Color=skia.Color(44, 48, 78, int(255 * alpha))))
    if glow > 0:
        c.drawArc(rect, -90, 360 * frac, False, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=60,
                                                           Color=skia.Color(*col, int(120 * glow * alpha)),
                                                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
    c.drawArc(rect, -90, 360 * frac, False, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=22,
                                                       StrokeCap=skia.Paint.kRound_Cap, Color=skia.Color(*col, int(255 * alpha))))
    # 60 tick marks
    for k in range(60):
        a = 2 * math.pi * k / 60 - math.pi / 2
        r0 = RR - 44 if k % 5 == 0 else RR - 36
        c.drawLine(CX + r0 * math.cos(a), CY + r0 * math.sin(a), CX + (RR - 24) * math.cos(a), CY + (RR - 24) * math.sin(a),
                   skia.Paint(AntiAlias=True, Color=skia.Color(120, 126, 160, int(200 * alpha)), StrokeWidth=4 if k % 5 == 0 else 2))
    arr = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    im.alpha_composite(Image.fromarray(arr, "RGBA"))


def digits(d, v, col, size=250):
    txt = f"{v:.2f}"
    f = font("Inter-Black", size)
    # fixed-width layout so the number does not jitter: each char in its own cell
    cells = [f.getlength("0")] * len(txt)
    cells = [f.getlength(".") * 1.2 if ch == "." else f.getlength("0") for ch in txt]
    x = CX - sum(cells) / 2
    for ch, w_ in zip(txt, cells):
        d.text((x + w_ / 2, CY + size * 0.36), ch, font=f, fill=col, anchor="ms")
        x += w_


def bg_dots(im, t):
    d = ImageDraw.Draw(im)
    for (x, y, sp, sz) in DOTS:
        yy = (y * H - t * (30 + 60 * sp)) % H
        r = 2 + sz * 3
        d.ellipse((x * W - r, yy - r, x * W + r, yy + r), fill=(90, 96, 140, 70))


def chip(d, txt, col, a=1.0):
    f = font("Inter-Black", 54)
    w_ = f.getlength(txt)
    x, y = CX + RR - 40, CY - RR + 30
    d.rounded_rectangle((x - w_ / 2 - 26, y - 44, x + w_ / 2 + 26, y + 26), radius=30, fill=(8, 9, 20, int(240 * a)), outline=col + (int(255 * a),), width=4)
    d.text((x, y + 2), txt, font=f, fill=col + (int(255 * a),), anchor="ms")


HOOKS = [
    [[("Pause it on", WHITE)], [("exactly ", WHITE), ("5.00", GOLD)]],
    [[("2x speed.", PINK)], [("Pause on ", WHITE), ("8.00", GOLD)]],
    [[("3x speed.", CYAN)], [("Pause on ", WHITE), ("7.77", GOLD)]],
]
STAMPS = [("1 FRAME.", GOLD), ("GONE.", PINK), ("IMPOSSIBLE?", CYAN)]


def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    bg_dots(im, t)
    v, k, hit, frozen = clock_state(i)
    R = ROUNDS[k]
    col = GOLD if hit else (MUTED if frozen and t < REWIND0 else WHITE)
    ring_col = GOLD if hit else ((96, 100, 140) if frozen and t < REWIND0 else (PINK if k == 1 else CYAN if k == 2 and t < REWIND0 else GOLD))
    ring(im, v % 1.0, ring_col, glow=1.0 if hit else 0.35)
    d = ImageDraw.Draw(im)
    if hit:
        # the one gold frame: glow behind the digits
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse((CX - RR + 40, CY - RR + 40, CX + RR - 40, CY + RR - 40), fill=(255, 211, 107, 60))
        im.alpha_composite(g); d = ImageDraw.Draw(im)
    stamping = any(Rk["stop"] <= t < Rk["stop"] + HOLDS[kk] for kk, Rk in enumerate(ROUNDS))
    if not stamping:
        digits(d, v, col + (255,))
    # speed chip from round 2
    if k >= 1 and t < REWIND0:
        chip(d, f"{R['speed']}x", PINK if k == 1 else CYAN, ease((t - R["t0"]) / 0.25))
    # hooks (each round's task stays up until its stamp)
    if t < REWIND0:
        hook_text(im, t, HOOKS[k], y=392, size=118, t0=R["t0"])
    else:
        hook_text(im, t, HOOKS[0], y=392, size=118, alpha=ease((t - REWIND0) / 0.4), punch=0)
    # HUD after the opening: target + the round
    if 3.0 <= t < REWIND0:
        ha = ease((t - 3.0) / 0.3)
        fl = font("Inter-SemiBold", 28); fn = font("Inter-Black", 66)
        label(d, 330, 1440, "TARGET", fl, lerpc(BG_BOT, MUTED, ha), spacing=5)
        label(d, 750, 1440, "ROUND", fl, lerpc(BG_BOT, MUTED, ha), spacing=5)
        tgt = ROUNDS[k]["target"] if t >= R["t0"] + 0.2 else ROUNDS[max(0, k - 1)]["target"]
        draw_rich(d, 330, 1514, [(f"{tgt:.2f}", lerpc(BG_BOT, GOLD, ha))], fn)
        draw_rich(d, 750, 1514, [(f"{k + 1}", lerpc(BG_BOT, WHITE, ha)), ("/3", lerpc(BG_BOT, MUTED, ha))], fn)
    # payoffs
    for kk, Rk in enumerate(ROUNDS):
        stamp(im, t, Rk["stop"], [STAMPS[kk]], y=CY - 10, size=150 if kk < 2 else 120, hold=HOLDS[kk], panel=True)
    if 2.95 <= t < 4.0:
        a = ease((t - 2.95) / 0.25) * (1 - ease((t - 3.8) / 0.2))
        f = font("Inter-Bold", 48)
        draw_rich(d, CX, 1440 - 120, [("5.00", GOLD + (int(255 * a),)), (" was on screen for 1 frame.", WHITE + (int(255 * a),))], f)
    if 6.55 <= t < 7.35:
        a = ease((t - 6.55) / 0.2) * (1 - ease((t - 7.15) / 0.2))
        f = font("Inter-Bold", 46)
        draw_rich(d, CX, 1440 - 120, [("At 2x, most numbers never show.", WHITE + (int(255 * a),))], f)
    # CTA
    if 10.9 <= t < REWIND0:
        ca = ease((t - 10.9) / 0.3) * (1 - ease((t - REWIND0 + 0.25) / 0.25))
        ov = Image.new("RGBA", im.size, (8, 9, 20, int(170 * ca))); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 700, W - 70, 1300), radius=40, fill=(8, 9, 20, int(235 * ca)))
        draw_rich(od, W / 2, 840, [("Stopped on gold?", GOLD + (int(255 * ca),))], font("Inter-Black", 84))
        draw_rich(od, W / 2, 960, [("You won. Screenshot it.", WHITE + (int(255 * ca),))], font("Inter-Bold", 54))
        draw_rich(od, W / 2, 1130, [("Comment your number.", WHITE + (int(255 * ca),))], font("Inter-Black", 66))
        draw_rich(od, W / 2, 1230, [("Tap to pause. Try again.", MUTED + (int(255 * ca),))], font("Inter-Bold", 44))
        im.alpha_composite(ov)
    # round transition flash
    for tb in (ROUNDS[1]["t0"], ROUNDS[2]["t0"]):
        if tb - 0.1 < t < tb + 0.15:
            a = 1 - abs(t - tb) / 0.15
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(90 * max(0, a)))))
    return im.convert("RGB")


if __name__ == "__main__":
    for R in ROUNDS:
        print("target", R["target"], "frame", R["hit_i"], f"t={R['hit_i'] / FPS:.3f}")
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.0, ROUNDS[0]["hit_i"] / FPS, 2.7, 3.3, 4.3, ROUNDS[1]["hit_i"] / FPS, 6.5, 6.9, 7.5, ROUNDS[2]["hit_i"] / FPS, 10.2, 11.0, 11.5, 12.9, 13.25]
        ims = [frame(int(round(t * FPS))).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * 8, 480 * 2))
        for k, x in enumerate(ims): st.paste(x, ((k % 8) * 270, (k // 8) * 480))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v037_video.mp4")
        for i in range(int(round(DUR * FPS))): w.write(frame(i))
        w.close(); print("frames", w.n)
