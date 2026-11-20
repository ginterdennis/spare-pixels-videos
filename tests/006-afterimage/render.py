import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from scene import scene, adapt_image, gray_image, GW, GH

PX = 20
SRC = scene()
A = Image.fromarray(np.kron(adapt_image(SRC), np.ones((PX, PX, 1))).astype(np.uint8))
G = Image.fromarray(np.kron(gray_image(SRC), np.ones((PX, PX, 1))).astype(np.uint8))
T_SWITCH = 18.0
T_TXT2 = 22.0
DUR = 29.0
DOT = (W // 2, 45 * PX + PX // 2)

def pill_text(im, lines, y, alpha):
    """lines: list of (parts, font). Draw on a dark rounded pill."""
    if alpha <= 0: return
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    widths = [sum(f.getlength(t) for t, _ in parts) for parts, f in lines]
    hs = [f.size * 1.25 for _, f in lines]
    bw = max(widths) + 90; bh = sum(hs) + 50
    d.rounded_rectangle((W / 2 - bw / 2, y, W / 2 + bw / 2, y + bh), radius=34, fill=(8, 9, 20, int(200 * alpha)))
    yy = y + 25
    for (parts, f), h in zip(lines, hs):
        draw_rich(d, W / 2, yy + f.size * 0.95, [(t, c + (int(255 * alpha),)) for t, c in parts], f)
        yy += h
    im.alpha_composite(ov)

def frame(i):
    t = i / FPS
    im = (A if t < T_SWITCH else G).copy().convert("RGBA")
    d = ImageDraw.Draw(im)
    # fixation dot + countdown ring
    x, y = DOT
    if t < T_SWITCH:
        u = t / T_SWITCH
        R = 40
        d.ellipse((x - R - 4, y - R - 4, x + R + 4, y + R + 4), outline=(0, 0, 0, 120), width=12)
        d.arc((x - R, y - R, x + R, y + R), start=-90, end=-90 + 360 * (1 - u), fill=(255, 255, 255, 255), width=7)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(0, 0, 0, 255))
    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255, 255))
    fT = font("Inter-Black", 74); fS = font("Inter-Bold", 46)
    a1 = 1 - ease((t - 3.6) / 0.5)
    pill_text(im, [([("Stare at the dot", WHITE)], fT), ([("for 18 seconds. ", WHITE), ("Don't look away.", GOLD)], fS),
                   ([("Keep staring when it changes.", WHITE)], fS)], 170, a1)
    a2 = ease((t - T_TXT2) / 0.5)
    if a2 > 0:
        sub = [("Your brain is adding the colour.", GOLD)] if t >= 24.0 else [(" ", WHITE)]
        pill_text(im, [([("This picture is", WHITE)], fT), ([("black & white.", WHITE)], fT), (sub, fS)], 170, a2)
    a3 = ease((t - 25.5) / 0.5)
    if a3 > 0:
        pill_text(im, [([("Did it work? Comment ", WHITE), ("YES", GOLD), (" or ", WHITE), ("NO", PINK)], font("Inter-Black", 58))], 1190, a3)
    return im.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in [0.0, 10.0, 18.5, 24.5, 27.0]]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v006_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
