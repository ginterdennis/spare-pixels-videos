"""036: 'Same colour' Part 3 (promised at the end of 025; 025 reached For You on 26 Nov). Same recipe as
018/025 (claim on frame 0, payoff by 2.5 s, three rounds, CTA 1/2/3 + reason to follow), but shorter
(19.5 s) and with no pixel look: smooth vector art (skia), full resolution.
1) Colour constancy (after Kitaoka's 'no red strawberries', ECVP 2015): an apple under a cyan cast. No pixel
   is red (R <= max(G, B), asserted in art.py); the brain discounts the blue-green light and sees red.
   Proof: everything around the apple fades to navy and it is grey.
2) Koffka ring (Kurt Koffka, Principles of Gestalt Psychology, 1935): one grey ring over a dark/light split looks
   uniform; slide the halves apart and they look like two greys. Nothing changes colour.
3) White's illusion: grey bars on the black stripes (A) vs on the white stripes (B), same grey (asserted).
   The stripes fade away and the bars are identical."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import skia
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp
import art

DUR = 19.5
R1, R2, R3, RC = 0.0, 6.2, 11.9, 17.6
REV1, REV2, REV3 = 2.5, R2 + 2.4, R3 + 2.4
PX0, PY0, PS = 110, 590, 860                       # picture panel
BGc = vgrad()
NAVY = np.array([16, 18, 36], np.float32)
NEUTRAL = np.array([122, 122, 122], np.float32)

# rounded-corner mask for the panel
_cm = Image.new("L", (PS, PS), 0)
ImageDraw.Draw(_cm).rounded_rectangle((0, 0, PS - 1, PS - 1), radius=34, fill=255)
CORNER = np.asarray(_cm, np.float32)[..., None] / 255
BG_PANEL = BGc[PY0:PY0 + PS, PX0:PX0 + PS].astype(np.float32)


def put_panel(arr):
    """composite a PS x PS float RGB array into a full frame (RGBA PIL)."""
    out = BGc.astype(np.float32).copy()
    out[PY0:PY0 + PS, PX0:PX0 + PS] = BG_PANEL * (1 - CORNER) + arr * CORNER
    im = Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8)).convert("RGBA")
    ImageDraw.Draw(im).rounded_rectangle((PX0 - 6, PY0 - 6, PX0 + PS + 6, PY0 + PS + 6), radius=38, outline=(70, 76, 118), width=3)
    return im


# ---------------------------------------------------------------- round 1: the apple
CAST_IM = Image.fromarray(art.CASTED.astype(np.uint8))
MASK_IM = Image.fromarray((art.MASK * 255).astype(np.uint8))


def apple_view(t):
    if t < 1.6:
        z = 1.16 - 0.16 * ease_out(t / 1.6)
    else:
        z = 1.0 + 0.035 * (t - 1.6) / 4.6
    cs = art.N / 1.08 / z                     # crop size in art px (z=1 shows the middle 93% of the art)
    cx = art.N / 2 + 10 * math.sin(t * 1.3)
    cy = art.N / 2 + 8 * math.sin(t * 1.7 + 1)
    box = (cx - cs / 2, cy - cs / 2, cx + cs / 2, cy + cs / 2)
    a = np.asarray(CAST_IM.resize((PS, PS), Image.BICUBIC, box=box), np.float32).copy()
    a[..., 0] = np.minimum(a[..., 0], np.maximum(a[..., 1], a[..., 2]))   # resampling must not create a reddish pixel
    m = np.asarray(MASK_IM.resize((PS, PS), Image.BICUBIC, box=box), np.float32)[..., None] / 255
    return a, m


_ay, _ax = int(art.CY + art.R * 0.15), int(art.CX + art.R * 0.1)
SWATCH = tuple(int(v) for v in np.round(art.CASTED[_ay - 30:_ay + 30, _ax - 30:_ax + 30].reshape(-1, 3).mean(0)))
assert SWATCH[0] <= max(SWATCH[1], SWATCH[2]), SWATCH


def swatch(im, t):
    """eyedropper: a ring on the apple, a line to a big disc filled with the sampled colour."""
    if not (3.9 <= t < 5.6): return
    a = ease((t - 3.9) / 0.25) * (1 - ease((t - 5.3) / 0.3))
    pop = ease_out((t - 3.9) / 0.3)
    # where the sample point lands in the panel at time t (same crop maths as apple_view)
    z = 1.0 + 0.035 * (t - 1.6) / 4.6
    cs = art.N / 1.08 / z
    cx = art.N / 2 + 10 * math.sin(t * 1.3); cy = art.N / 2 + 8 * math.sin(t * 1.7 + 1)
    px = PX0 + (_ax - (cx - cs / 2)) / cs * PS; py = PY0 + (_ay - (cy - cs / 2)) / cs * PS
    sx, sy, r = PX0 + PS - 150, PY0 + 150, 92 * pop
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.line((px, py, sx, sy), fill=(255, 255, 255, int(230 * a)), width=5)
    d.ellipse((px - 26, py - 26, px + 26, py + 26), outline=(255, 255, 255, int(255 * a)), width=6)
    d.ellipse((sx - r - 8, sy - r - 8, sx + r + 8, sy + r + 8), fill=(255, 255, 255, int(255 * a)))
    d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=SWATCH + (int(255 * a),))
    im.alpha_composite(ov)


def round1(t):
    a, m = apple_view(t)
    iso = 0.0
    if 3.7 <= t < 5.9:
        iso = ease((t - 3.7) / 0.5) * (1 - ease((t - 5.3) / 0.5))
    if iso > 0:
        a = a * (1 - iso * (1 - m)) + NEUTRAL * iso * (1 - m)    # neutral grey room: no colour cue left
    return a


# ---------------------------------------------------------------- round 2: Koffka ring
DARK, LIGHT, RING = (50, 54, 72), (198, 202, 214), (128, 128, 132)
RO, RI = 250, 150


def koffka(s):
    """s = local round time. Halves slide apart from REV2 and back at the end of the round."""
    sp = 0.0
    loc_rev = REV2 - R2
    if s >= loc_rev:
        sp = ease((s - loc_rev) / 0.45)
    if s >= 4.8:
        sp *= 1 - ease((s - 4.8) / 0.5)
    sc = 0.9 + 0.1 * ease_out(s / 0.7) if s < 0.7 else 1.0
    surf = skia.Surface(PS, PS); c = surf.getCanvas()
    c.drawRect(skia.Rect(0, 0, PS / 2, PS), skia.Paint(Color=skia.Color(*DARK)))
    c.drawRect(skia.Rect(PS / 2, 0, PS, PS), skia.Paint(Color=skia.Color(*LIGHT)))
    cx, cy = PS / 2, PS / 2 + 10
    ro, ri = RO * sc, RI * sc
    for side, dy in ((-1, -150 * sp), (1, 150 * sp)):
        c.save()
        clip = skia.Rect(0, 0, PS / 2, PS) if side < 0 else skia.Rect(PS / 2, 0, PS, PS)
        c.clipRect(clip)
        c.translate(0, dy)
        p = skia.Path()
        p.addCircle(cx, cy, ro); p.addCircle(cx, cy, ri, skia.PathDirection.kCCW)
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=skia.Color(*RING)))
        c.restore()
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


_k = koffka(0.9).astype(int)
assert tuple(_k[PS // 2 + 10, PS // 2 - 200]) == RING and tuple(_k[PS // 2 + 10, PS // 2 + 200]) == RING

# ---------------------------------------------------------------- round 3: White's illusion
SH = 40                                             # stripe height
BLK, WHT, GRY = (14, 14, 20), (236, 236, 242), (128, 128, 132)
COLW = 220
AX, BX = 130, PS - 130 - COLW                       # column x (panel coords)
Y_A0, Y_A1 = 4 * SH, 18 * SH                        # rows covered by the columns


def whites(s):
    fade = 0.0
    loc_rev = REV3 - R3
    if s >= loc_rev:
        fade = ease((s - loc_rev) / 0.45)
    if s >= 4.7:
        fade *= 1 - ease((s - 4.7) / 0.5)
    img = np.zeros((PS, PS, 3), np.float32)
    rows = (np.arange(PS) // SH) % 2 == 0            # True = black stripe
    img[rows] = BLK; img[~rows] = WHT
    img = img * (1 - fade) + NAVY * fade
    yy = np.arange(PS)
    inrange = (yy >= Y_A0) & (yy < Y_A1)
    a_rows = inrange & rows                          # A: grey on the black stripes
    b_rows = inrange & ~rows                         # B: grey on the white stripes
    img[a_rows, AX:AX + COLW] = GRY
    img[b_rows, BX:BX + COLW] = GRY
    return img


_w = whites(0.5)
assert (_w[Y_A0, AX + 5] == np.array(GRY)).all() and (_w[Y_A0 + SH, BX + 5] == np.array(GRY)).all()


def ab_labels(im, t, a):
    if a <= 0: return
    d = ImageDraw.Draw(im)
    f = font("Inter-Black", 64)
    for x, txt, col in ((PX0 + AX + COLW / 2, "A", GOLD), (PX0 + BX + COLW / 2, "B", CYAN)):
        y = PY0 + Y_A0 - 62
        d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(8, 9, 20, int(225 * a)), outline=col + (int(255 * a),), width=5)
        d.text((x, y + 23), txt, font=f, fill=col + (int(255 * a),), anchor="ms")


# ---------------------------------------------------------------- text helpers
def part_pill(d, t, rnd):
    if t < 3.2: return
    a = ease((t - 3.2) / 0.4)
    label(d, W / 2, 232, f"SAME COLOUR  PART 3   {rnd}/3", font("Inter-Bold", 30), MUTED + (int(255 * a),), spacing=5)


def pill_text(im, t, t0, txt, y=1440, col=WHITE, size=50, t1=None):
    if t < t0 or (t1 is not None and t >= t1): return
    a = ease((t - t0) / 0.3)
    if t1 is not None: a *= 1 - ease((t - t1 + 0.3) / 0.3)
    f = font("Inter-Bold", size)
    w_ = f.getlength(txt)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle((W / 2 - w_ / 2 - 30, y - size - 14, W / 2 + w_ / 2 + 30, y + 26), radius=26, fill=(8, 9, 20, int(225 * a)))
    od.text((W / 2, y), txt, font=f, fill=col + (int(255 * a),), anchor="ms")
    im.alpha_composite(ov)


HOOK1 = [[("This apple has", WHITE)], [("NO ", GOLD), ("red.", GOLD)]]
HOOK2 = [[("One grey ring.", WHITE)], [("Watch it ", WHITE), ("split.", GOLD)]]
HOOK3 = [[("Darker grey:", WHITE)], [("A", GOLD), (" or ", WHITE), ("B", CYAN), ("?", WHITE)]]


def frame(i):
    t = i / FPS
    if t < R2:
        im = put_panel(round1(t))
        hook_text(im, t, HOOK1, y=392, size=118)
        stamp(im, t, REV1, [("ZERO RED.", CYAN)], y=1010, size=150, hold=1.15, panel=True)
        swatch(im, t)
        pill_text(im, t, 3.9, "Without the blue light: grey.", t1=5.5)
        pill_text(im, t, 5.5, "Your brain paints it red.", col=GOLD)
        part_pill(ImageDraw.Draw(im), t, 1)
    elif t < R3:
        s = t - R2
        im = put_panel(koffka(s))
        hook_text(im, t, HOOK2, y=392, size=118, t0=R2)
        if REV2 + 0.45 <= t < REV2 + 1.8:
            stamp(im, t, REV2 + 0.45, [("SAME GREY.", GOLD)], y=1440, size=118, panel=True)
        pill_text(im, t, REV2 + 1.8, "Your brain compares it to each side.", size=44)
        part_pill(ImageDraw.Draw(im), t, 2)
    elif t < RC + 0.5:
        s = t - R3
        im = put_panel(whites(min(s, RC - R3)))
        ab_labels(im, t, ease((t - R3) / 0.3))
        hook_text(im, t, HOOK3, y=392, size=118, t0=R3)
        if REV3 + 0.45 <= t < REV3 + 1.8:
            stamp(im, t, REV3 + 0.45, [("SAME GREY.", GOLD)], y=1440, size=118, panel=True)
        pill_text(im, t, REV3 + 1.8, "The stripes change your eyes.", size=48)
        part_pill(ImageDraw.Draw(im), t, 3)
    else:
        im = put_panel(whites(RC - R3))
        ab_labels(im, t, 1.0)
    # round transition flash
    for tb in (R2, R3):
        if tb - 0.12 < t < tb + 0.18:
            a = 1 - abs(t - tb) / 0.18
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(110 * max(0, a)))))
    if t >= RC:
        a = ease((t - RC) / 0.4)
        # last 0.5 s: the apple (frame-0 view) fades back in so the loop hands back to frame 0
        if t >= DUR - 0.5:
            k = ease((t - (DUR - 0.5)) / 0.5)
            f0 = put_panel(round1(0.0))
            hook_text(f0, 0.3, HOOK1, y=392, size=118)
            im = Image.blend(im, f0, k)
            a *= 1 - k
        ov = Image.new("RGBA", im.size, (8, 9, 20, int(170 * a))); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 700, W - 70, 1290), radius=40, fill=(8, 9, 20, int(235 * a)))
        draw_rich(od, W / 2, 830, [("Which one got you?", WHITE + (int(255 * a),))], font("Inter-Black", 76))
        draw_rich(od, W / 2, 1000, [("1", GOLD + (int(255 * a),)), ("   2   ", PINK + (int(255 * a),)), ("3", CYAN + (int(255 * a),))], font("Inter-Black", 128))
        draw_rich(od, W / 2, 1150, [("Part 4 is harder. ", MUTED + (int(255 * a),)), ("Follow.", GOLD + (int(255 * a),))], font("Inter-Bold", 50))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.0, 2.6, 4.5, 5.7, 7.0, 9.3, 10.6, 12.5, 14.9, 16.2, 18.2, 19.3]
        ims = [frame(int(round(t * FPS))).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88)
        frame(0).save("f0.png")
    else:
        w = Writer("v036_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
