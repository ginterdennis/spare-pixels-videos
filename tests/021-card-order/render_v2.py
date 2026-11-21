"""021 v2 (hook rebuild, 21 Nov 2026, HOOKS.md). Same facts as v1, new opening:
- frame 0: cards already in mid-riffle + a 5-word question the viewer answers in their head
  ("Has this shuffle EVER happened?" - most people think: surely yes)
- 2.4 s: a NEVER. rubber stamp slams onto the deck (first payoff), then the 68-digit number
- every later beat uses the big hook-style text instead of the old small header strip
- 19 s instead of 20.5 s. Cards, number formatting and facts come from render.py (v1)."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text
import render as V1

DUR = 19.0
NEVER = 2.4
NUM = 4.3
CNT = 8.0
PCT = 11.2
WF = 14.0
CTA = 16.2
S3 = 17.9
V1.SHUF = [(-0.25, 0, 1), (0.95, 1, 2), (WF - 0.2, 2, 3), (CTA + 0.1, 3, 4), (S3, 4, 5)]

HOOK = [[("Has this shuffle", WHITE)], [("EVER happened?", GOLD)]]
BGc = V1.BGc


def big(im, t, t0, lines, size=104):
    hook_text(im, t, lines, size=size, t0=t0, check=False)


def rubber(im, t, t0, txt, cy, w=620, h=190, size=118, rot=-9):
    u = ease_out((t - t0) / 0.16, 3)
    if u <= 0:
        return
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((6, 6, w - 7, h - 7), radius=26, outline=PINK + (255,), width=14, fill=(8, 9, 20, 225))
    sd.text((w / 2, h / 2 + 4), txt, font=font("Inter-Black", size), fill=PINK + (255,), anchor="mm")
    sc = 1.7 - 0.7 * u
    st = st.resize((int(w * sc), int(h * sc))).rotate(rot, expand=True, resample=Image.BICUBIC)
    st = V1.fade_layer(st, min(1, u * 1.6))
    im.alpha_composite(st, (W // 2 - st.width // 2, int(cy - st.height // 2)))


def frame(i):
    t = i / FPS
    im = BGc.copy()
    if t < NUM:
        ca = 1.0
    elif t < WF - 0.4:
        ca = 1 - 0.88 * ease((t - NUM) / 0.35)
    else:
        ca = 0.12 + 0.88 * ease((t - WF + 0.4) / 0.4)
    im.alpha_composite(V1.fade_layer(V1.card_layer(t), ca))
    if NUM <= t < WF - 0.2:
        im.alpha_composite(Image.new("RGBA", (W, H), (8, 9, 20, int(120 * min(1, (t - NUM) / 0.3)))))
    d = ImageDraw.Draw(im, "RGBA")
    if t < NEVER:
        hook_text(im, t, HOOK)
    elif t < NUM:
        hook_text(im, t, HOOK, punch=0)
        rubber(im, t, NEVER, "NEVER.", 892)
        if t > NEVER + 0.45:
            V1.line_txt(d, 1330, [("The odds say: ", MUTED), ("not once. Ever.", WHITE)], 58, ease((t - NEVER - 0.45) / 0.25), name="Inter-Black")
    elif t < CNT:
        big(im, t, NUM, [[("Possible orders", WHITE)], [("of 52 cards:", GOLD)]])
        n = int(V1.NUM_CHARS * ease_out((t - NUM - 0.1) / 0.9, 2))
        V1.mono_block(d, V1.NUM_LINES, 760, 70, WHITE, nchars=n)
        if t > NUM + 1.4:
            V1.line_txt(d, 1470, [("An 8 with ", WHITE), ("67 digits", GOLD), (" after it.", WHITE)], 56,
                        ease((t - NUM - 1.4) / 0.3), name="Inter-Black")
    elif t < PCT:
        big(im, t, CNT, [[("8 billion people", WHITE)], [("since the Big Bang:", GOLD)]])
        u = ease_out((t - CNT - 0.2) / 2.2, 3)
        v = int(10 ** (math.log10(V1.SH) * u)) if u < 1 else int(V1.SH)
        V1.mono_block(d, V1.groups(v), 800, 70, WHITE)
        V1.line_txt(d, 1150, [("shuffles, one a second each", MUTED)], 50)
    elif t < WF:
        big(im, t, PCT, [[("They'd have tried", WHITE)], [("only this much:", GOLD)]])
        pl = [V1.PCT_STR[i:i + 14] for i in range(0, len(V1.PCT_STR), 14)]
        V1.mono_block(d, pl, 800, 74, GOLD, nchars=int(len(V1.PCT_STR) * ease_out((t - PCT - 0.1) / 0.6, 2)))
        if t > PCT + 1.0:
            V1.line_txt(d, 1180, [("of all possible orders.", WHITE)], 56, ease((t - PCT - 1.0) / 0.3), name="Inter-Black")
    elif t < CTA:
        big(im, t, WF, [[("Your next shuffle:", WHITE)], [("a world first.", GOLD)]])
        rubber(im, t, WF + 0.45, "WORLD FIRST", 892, w=700, size=92, rot=-7)
    else:
        big(im, t, CTA, [[("Tag the friend who", WHITE)], [("always shuffles.", GOLD)]])
        V1.line_txt(d, 1470, [("Every shuffle is history.", WHITE)], 56, ease((t - CTA - 0.3) / 0.3), name="Inter-Black")
    for tb in (NEVER, NUM, CNT, PCT, WF, CTA):
        if tb - 0.08 < t < tb + 0.12:
            k = 1 - abs(t - tb) / 0.12
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(60 * max(0, k)))))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.2, 2.5, 3.4, 5.8, 9.6, 12.8, 15.0, 17.0]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills_v2.jpg", quality=88)
    else:
        w = Writer("v021v2_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
