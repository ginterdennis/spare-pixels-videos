"""019: 'There is no green in this video.' Lilac-chaser style illusion (phi motion + negative afterimage +
Troxler fading). 12 blurred pink discs on grey; one disc is missing at a time, stepping clockwise every
4 frames (0.133 s). Nothing green is ever drawn."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *

DUR = 21.0
T_STOP = 16.5          # chaser stops, all discs shown
T_CTA = 17.8
STEP = 4               # frames per step
GREY = (190, 190, 192)
PINKD = (238, 128, 214)
INK = (20, 22, 40)
CX, CY, RR, DR = W // 2, 960, 300, 64


def disc_layer(missing):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = Image.new("L", (W, H), 0); d = ImageDraw.Draw(a)
    for k in range(12):
        if k == missing: continue
        ang = 2 * math.pi * k / 12
        x, y = CX + RR * math.sin(ang), CY - RR * math.cos(ang)
        d.ellipse((x - DR, y - DR, x + DR, y + DR), fill=255)
    a = a.filter(ImageFilter.GaussianBlur(20))
    col = Image.new("RGBA", (W, H), PINKD + (0,)); col.putalpha(a)
    return col


def fit(txt, name, size, maxw):
    f = font(name, size)
    while f.getlength(txt) > maxw and size > 20:
        size -= 2; f = font(name, size)
    return f


def base(missing, phase):
    im = Image.new("RGBA", (W, H), GREY + (255,))
    im.alpha_composite(disc_layer(missing))
    d = ImageDraw.Draw(im)
    # fixation cross
    d.rectangle((CX - 22, CY - 4, CX + 22, CY + 4), fill=(0, 0, 0, 255))
    d.rectangle((CX - 4, CY - 22, CX + 4, CY + 22), fill=(0, 0, 0, 255))
    fB = font("Inter-Black", 82); fM = font("Inter-Bold", 48)
    if phase == 0:
        draw_rich(d, W / 2, 300, [("There is ", INK), ("NO green", (196, 40, 150))], fB)
        draw_rich(d, W / 2, 392, [("in this video.", INK)], fB)
        draw_rich(d, W / 2, 476, [("Stare at the + and don't move your eyes.", INK)], fit("Stare at the + and don't move your eyes.", "Inter-Bold", 46, 960))
        draw_rich(d, W / 2, 1470, [("Keep staring. Watch the pink.", (70, 72, 92))], fM)
    else:
        draw_rich(d, W / 2, 300, [("There was never", INK)], fB)
        draw_rich(d, W / 2, 392, [("a green dot.", INK)], fB)
        draw_rich(d, W / 2, 476, [("And the pink never left.", (196, 40, 150))], fM)
    return im


BASES = [base(k, 0) for k in range(12)]
STOPPED = base(-1, 1)


def frame(i):
    t = i / FPS
    if t < T_STOP:
        missing = (i // STEP) % 12
        im = BASES[missing].copy()
        d = ImageDraw.Draw(im)
        # quiet seconds counter under the cross (helps answer the comment question)
        s = int(t)
        d.text((CX, CY + 78), f"{s}s", font=font("Inter-Bold", 34), fill=(128, 128, 136, 255), anchor="ms")
    else:
        im = STOPPED.copy()
    if t >= T_CTA:
        a = ease((t - T_CTA) / 0.4)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 1100, W - 70, 1470), radius=40, fill=(14, 16, 32, int(235 * a)))
        f1 = font("Inter-Black", 62)
        draw_rich(od, W / 2, 1200, [("How many seconds until", WHITE + (int(255 * a),))], fit("How many seconds until", "Inter-Black", 62, 880))
        draw_rich(od, W / 2, 1280, [("the pink vanished?", GOLD + (int(255 * a),))], f1)
        draw_rich(od, W / 2, 1390, [("Comment your number", MUTED + (int(255 * a),))], font("Inter-Bold", 46))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 0.2, 5.0, 16.0, 17.0, 19.5]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
        a = np.asarray(frame(10 * FPS)).astype(int)
        # no pixel may be green-dominant
        print("max(G - max(R,B)) =", int((a[..., 1] - np.maximum(a[..., 0], a[..., 2])).max()))
    else:
        w = Writer("v019_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
