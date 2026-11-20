"""021: 'This card order has NEVER existed.' 52 pixel cards shuffle on frame 0, then
52! = 80,658,175,...,000 (68 digits) by ~3 s, then: if 8 billion people had shuffled once a
second since the Big Bang (13.8 billion years) they'd have tried ~3.5 x 10^27 orders,
i.e. 0.(38 zeros)4 % of all orders. So a good shuffle is almost certainly a world first.
Facts: 52! from math.factorial; universe age 13.8 Gyr (Planck); McGill OSS / HMC Math Fun Facts."""
import sys, math, random
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

DUR = 20.5
S1, S2 = 0.12, 1.05            # opening shuffles
NUM = 2.2                      # 52! appears
CNT = 7.0                      # 8 billion people counter
PCT = 10.6                     # the tiny percentage
WF = 14.2                      # world first
CTA = 17.4
S3 = 19.4                      # last shuffle hands back to frame-0 order

F52 = math.factorial(52)
SH = 8e9 * 13.8e9 * 365.25 * 86400           # shuffles if 8 billion people, 1/s, since the Big Bang
PCTV = SH / F52 * 100
_e = math.floor(math.log10(PCTV))             # -39
PCT_STR = "0." + "0" * (-_e - 1) + str(int(PCTV / 10 ** _e)) + "%"
assert PCT_STR.startswith("0." + "0" * 38) and len(PCT_STR) == 42, PCT_STR

# ---------------------------------------------------------------- cards
CW, CH, PX, PY = 74, 104, 81, 116
GL, GT = (W - 13 * PX) // 2 + (PX - CW) // 2, 660
SUITS = {
    "H": [".XX.XX.", "XXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."],
    "D": ["...X...", "..XXX..", ".XXXXX.", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."],
    "S": ["...X...", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", "...X...", "..XXX.."],
    "C": ["..XXX..", "..XXX..", "XXXXXXX", "XXXXXXX", "XX.X.XX", "...X...", "..XXX.."],
}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
RED, INK = (226, 52, 72), (22, 24, 40)


def make_card(rank, suit):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=9, fill=(248, 246, 240, 255), outline=(200, 196, 186, 255), width=2)
    col = RED if suit in "HD" else INK
    f = font("Inter-Black", 30 if rank != "10" else 26)
    d.text((9, 6), rank, font=f, fill=col + (255,), anchor="lt")
    p = 5; grid = SUITS[suit]
    ox, oy = (CW - 7 * p) // 2 + 6, CH - 7 * p - 12
    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            if ch == "X":
                d.rectangle((ox + i * p, oy + j * p, ox + (i + 1) * p - 1, oy + (j + 1) * p - 1), fill=col + (255,))
    return im


CARDS = [make_card(r, s) for s in "SHDC" for r in RANKS]
rng = random.Random(52)
ORD = []                                   # slot order per stage: ORD[k][card] = slot
for _ in range(6):
    p = list(range(52)); rng.shuffle(p); ORD.append(p)
ORD[-1] = ORD[0]                           # last shuffle returns to the frame-0 layout
DELAY = [rng.random() * 0.3 for _ in range(52)]
SHUF = [(S1, 0, 1), (S2, 1, 2), (WF - 0.2, 2, 3), (CTA + 0.1, 3, 4), (S3, 4, 5)]
MOVE = 0.42


def slot_xy(s):
    return GL + (s % 13) * PX, GT + (s // 13) * PY


def card_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stage = 0; moving = None
    for ts, a, b in SHUF:
        if t >= ts: stage = b; moving = (ts, a, b)
    items = []
    for c in range(52):
        if moving and t < moving[0] + 0.3 + MOVE + 0.05:
            ts, a, b = moving
            u = ease((t - ts - DELAY[c]) / MOVE)
            x0, y0 = slot_xy(ORD[a][c]); x1, y1 = slot_xy(ORD[b][c])
            x = lerp(x0, x1, u); y = lerp(y0, y1, u) - 70 * math.sin(math.pi * u)
            items.append((u * (1 - u), c, x, y))
        else:
            x, y = slot_xy(ORD[stage][c]); items.append((0, c, x, y))
    for _, c, x, y in sorted(items):          # flying cards on top
        lay.alpha_composite(CARDS[c], (int(round(x)), int(round(y))))
    return lay


def fade_layer(lay, a):
    if a >= 0.999: return lay
    al = np.asarray(lay.getchannel("A"), np.float32) * a
    lay = lay.copy(); lay.putalpha(Image.fromarray(al.astype(np.uint8))); return lay


BGc = Image.fromarray(vgrad()).convert("RGBA")


def head(d, top, l1, l2, a=1.0, size=78):
    label(d, W / 2, 250, top, font("Inter-Bold", 30), MUTED + (int(255 * a),), spacing=6)
    draw_rich(d, W / 2, 352, [(x, c + (int(255 * a),)) for x, c in l1], font("Inter-Black", size))
    draw_rich(d, W / 2, 448, [(x, c + (int(255 * a),)) for x, c in l2], font("Inter-Black", size))


def line_txt(d, y, parts, size, a=1.0, name="Inter-Bold"):
    draw_rich(d, W / 2, y, [(x, c + (int(255 * a),)) for x, c in parts], font(name, size))


def groups(n):
    s = f"{n:,}".split(",")
    return [",".join(s[i:i + 4]) + ("," if i + 4 < len(s) else "") for i in range(0, len(s), 4)]


NUM_LINES = groups(F52)                    # 6 lines
NUM_CHARS = sum(len(x) for x in NUM_LINES)


def mono_block(d, lines, y0, size, col, a=1.0, nchars=None, step=None):
    f = font("JBMono-Bold", size); step = step or int(size * 1.18)
    left = None
    n = 10 ** 9 if nchars is None else nchars
    for k, ln in enumerate(lines):
        vis = ln[:max(0, n)]; n -= len(ln)
        if left is None:
            left = (W - f.getlength(max(lines, key=len))) / 2
        d.text((left, y0 + k * step), vis, font=f, fill=col + (int(255 * a),), anchor="ls")


def frame(i):
    t = i / FPS
    im = BGc.copy()
    # card grid visibility
    if t < NUM:
        ca = 1.0
    elif t < WF - 0.4:
        ca = 1 - 0.88 * ease((t - NUM) / 0.35)
    else:
        ca = 0.12 + 0.88 * ease((t - WF + 0.4) / 0.4)
    im.alpha_composite(fade_layer(card_layer(t), ca))
    if NUM <= t < WF - 0.2:
        dim = Image.new("RGBA", (W, H), (8, 9, 20, int(120 * min(1, (t - NUM) / 0.3))))
        im.alpha_composite(dim)
    d = ImageDraw.Draw(im)
    if t < NUM:
        head(d, "SHUFFLE A DECK", [("This card order has", WHITE)], [("NEVER existed.", GOLD)])
        line_txt(d, 530, [("(almost certainly)", MUTED)], 40)
    elif t < CNT:
        head(d, "52 CARDS", [("52 cards can be ordered", WHITE)], [("in this many ways:", GOLD)], size=72)
        n = int(NUM_CHARS * ease_out((t - NUM - 0.1) / 0.9, 2))
        mono_block(d, NUM_LINES, 700, 70, WHITE, nchars=n)
        if t > NUM + 1.4:
            line_txt(d, 1430, [("An 8 with ", WHITE), ("67 digits", GOLD), (" after it.", WHITE)], 50, ease((t - NUM - 1.4) / 0.3))
    elif t < PCT:
        head(d, "IMAGINE", [("8 billion people shuffling", WHITE)], [("every second since", WHITE)], size=66)
        line_txt(d, 540, [("the Big Bang", GOLD)], 66, name="Inter-Black")
        u = ease_out((t - CNT - 0.2) / 2.4, 3)
        v = int(10 ** (math.log10(SH) * u)) if u < 1 else int(SH)
        mono_block(d, groups(v), 760, 70, WHITE)
        line_txt(d, 1110, [("shuffles", MUTED)], 50)
    elif t < WF:
        head(d, "IN ALL THAT TIME", [("they'd have tried", WHITE)], [("only this much:", GOLD)], size=72)
        pl = [PCT_STR[i:i + 14] for i in range(0, len(PCT_STR), 14)]
        mono_block(d, pl, 760, 74, GOLD, nchars=int(len(PCT_STR) * ease_out((t - PCT - 0.1) / 0.6, 2)))
        if t > PCT + 1.0:
            line_txt(d, 1140, [("of all possible orders.", WHITE)], 52, ease((t - PCT - 1.0) / 0.3))
    elif t < CTA:
        head(d, "SO", [("Your next good shuffle:", WHITE)], [("a WORLD FIRST.", GOLD)], size=74)
        u = ease_out((t - WF - 0.5) / 0.35, 3)
        if u > 0:
            st = Image.new("RGBA", (640, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((6, 6, 633, 163), radius=24, outline=GOLD + (255,), width=12, fill=(8, 9, 20, 200))
            sd.text((320, 88), "WORLD FIRST", font=font("Inter-Black", 86), fill=GOLD + (255,), anchor="mm")
            sc = 1.6 - 0.6 * u
            st = st.resize((int(640 * sc), int(170 * sc))).rotate(-8, expand=True, resample=Image.BICUBIC)
            st = fade_layer(st, min(1, u * 1.5))
            im.alpha_composite(st, (W // 2 - st.width // 2, 890 - st.height // 2))
    else:
        a = ease((t - CTA) / 0.4)
        head(d, "SHUFFLE A DECK", [("Tag the friend who", WHITE)], [("always shuffles.", GOLD)], a)
        line_txt(d, 1430, [("Every shuffle is history.", WHITE)], 50, a)
    for tb in (NUM, CNT, PCT, WF, CTA):
        if tb - 0.1 < t < tb + 0.16:
            k = 1 - abs(t - tb) / 0.16
            im.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, int(60 * max(0, k)))))
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 0.4, 3.5, 6.0, 9.0, 12.5, 15.5, 18.5, 20.4]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills.jpg", quality=88)
        frame(0).save("f0.png"); frame(int(6.0 * FPS)).save("f6.png"); frame(int(12.5 * FPS)).save("f125.png")
    else:
        w = Writer("v021_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
