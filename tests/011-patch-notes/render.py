import sys, math, textwrap
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

GREEN = (90, 230, 150); VIOLET = (170, 130, 255)
NOTES = [
    ("NEW", GREEN, ["Back pain now triggers at random. No cause required.",
                    "Unlocked: getting genuinely excited about a new sponge."]),
    ("CHANGED", GOLD, ["Hangover duration increased from 1 day to 3 days.",
                       "\"I'll do it tomorrow\" now stacks infinitely."]),
    ("FIXED", CYAN, ["Fixed a bug where you had free time.",
                     "Fixed all your friends being free on the same weekend."]),
    ("REMOVED", PINK, ["Removed the ability to sleep past 7:00.",
                       "Removed summer holidays. No replacement planned."]),
    ("KNOWN ISSUES", VIOLET, ["Walking into a room and forgetting why.",
                              "Saying \"you too\" when the waiter says enjoy your meal."]),
]
PX0, PY0, PX1, PY1 = 70, 430, 1010, 1470   # panel
IX0, IX1 = PX0 + 50, PX1 - 50
FM = font("JBMono-Bold", 40); FTAG = font("Silkscreen-Bold", 40)
CW = FM.getlength("M"); CPL = int((IX1 - IX0 - 50) // CW)
T_LOAD0, T_LOAD1 = 0.0, 2.4
CPS = 38.0
items = []   # (kind, text_lines, color, t_start, t_end, height)
t = T_LOAD1 + 0.3
for tag, col, lines in NOTES:
    items.append(("tag", [tag], col, t, t + 0.25, 86)); t += 0.45
    for ln in lines:
        wr = textwrap.wrap(ln, CPL)
        n = len(ln)
        dur = n / CPS
        items.append(("line", wr, col, t, t + dur, 56 * len(wr) + 26))
        t += dur + 1.15
T_DONE = t + 0.1
items.append(("done", ["UPDATE COMPLETE", "RESTART: NEVER"], GREEN, T_DONE, T_DONE + 0.3, 150))
DUR = T_DONE + 4.4
BG = vgrad()
SCAN = Image.new("RGBA", (PX1 - PX0, PY1 - PY0), (0, 0, 0, 0))
_sd = ImageDraw.Draw(SCAN)
for _y in range(0, PY1 - PY0, 4): _sd.line((0, _y, PX1 - PX0, _y), fill=(0, 0, 0, 38), width=1)

def content_height_until(tc):
    h = 0
    for kind, txt, col, t0, t1, hh in items:
        if tc >= t0: h += hh
    return h

def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy()).convert("RGBA")
    d = ImageDraw.Draw(im)
    # headline
    draw_rich(d, W / 2, 215, [("Adulting ", WHITE), ("v27.0", GOLD)], font("Inter-Black", 96))
    draw_rich(d, W / 2, 310, [("patch notes just dropped", MUTED)], font("Inter-Bold", 50))
    # panel (pixel double border)
    d.rectangle((PX0, PY0, PX1, PY1), fill=(12, 14, 30))
    for k, c in enumerate([(90, 98, 150), (40, 44, 80)]):
        o = 6 + k * 10
        d.rectangle((PX0 + o, PY0 + o, PX1 - o, PY1 - o), outline=c, width=6)
    # title bar
    d.rectangle((PX0 + 22, PY0 + 22, PX1 - 22, PY0 + 110), fill=(30, 34, 64))
    d.text((IX0 + 4, PY0 + 66), "ADULTING", font=font("Silkscreen-Bold", 48), fill=WHITE, anchor="lm")
    d.text((IX1 - 4, PY0 + 66), "PATCH 27.0", font=font("Silkscreen", 40), fill=GOLD, anchor="rm")
    CY0, CY1 = PY0 + 140, PY1 - 40   # content clip
    clip = Image.new("RGBA", (PX1 - PX0, CY1 - CY0), (0, 0, 0, 0)); cd = ImageDraw.Draw(clip)
    ox, oy = PX0, CY0
    if t < T_LOAD1 + 0.3:
        u = ease_out(min(1, max(0, (t - 0.15) / (T_LOAD1 - 0.4))), 2)
        cd.text((IX0 - ox, 120), "INSTALLING UPDATE...", font=font("Silkscreen", 40), fill=MUTED)
        bx0, bx1, by = IX0 - ox, IX1 - ox, 200
        cd.rectangle((bx0, by, bx1, by + 56), outline=(90, 98, 150), width=4)
        segs = 20
        for s in range(int(segs * u)):
            sw = (bx1 - bx0 - 16) / segs
            cd.rectangle((bx0 + 8 + s * sw + 2, by + 8, bx0 + 8 + (s + 1) * sw - 2, by + 48), fill=GREEN)
        cd.text(((bx0 + bx1) / 2, by + 110), f"{int(u * 100)}%", font=font("Silkscreen-Bold", 56), fill=WHITE, anchor="mm")
    else:
        visible_h = CY1 - CY0 - 20
        # scroll so the newest item stays visible (smooth)
        hs = sum(hh * ease((t - t0) / 0.4) for kind, txt, col, t0, t1, hh in items)
        scroll = max(0, hs - visible_h)
        y = 10 - scroll
        for kind, txt, col, t0, t1, hh in items:
            if t < t0: break
            if kind == "done": pass
            if kind == "tag":
                a = ease((t - t0) / 0.2)
                tw = FTAG.getlength(txt[0]) + 36
                cd.rectangle((IX0 - ox, y + 14, IX0 - ox + tw, y + 70), fill=lerpc((12, 14, 30), col, a))
                cd.text((IX0 - ox + 18, y + 42), txt[0], font=FTAG, fill=(12, 14, 30), anchor="lm")
            elif kind == "line":
                nchar = int((t - t0) * CPS)
                left = nchar
                for li, ln in enumerate(txt):
                    show = ln[:max(0, left)]; left -= len(ln) + 1
                    yy = y + 10 + li * 56
                    if li == 0: cd.text((IX0 - ox, yy), ">", font=FM, fill=col)
                    cd.text((IX0 - ox + 50, yy), show, font=FM, fill=WHITE)
                    if 0 < len(show) < len(ln) and (int(t * 8) % 2 == 0):
                        cx = IX0 - ox + 50 + FM.getlength(show)
                        cd.rectangle((cx + 2, yy + 4, cx + 22, yy + 48), fill=col)
            elif kind == "done":
                a = ease((t - t0) / 0.3)
                cd.line((IX0 - ox, y + 12, IX1 - ox, y + 12), fill=lerpc((12, 14, 30), (60, 66, 100), a), width=3)
                cd.text(((PX1 - PX0) / 2, y + 62), txt[0], font=font("Silkscreen-Bold", 48), fill=lerpc((12, 14, 30), GREEN, a), anchor="mm")
                if t > t0 + 0.6:
                    b = ease((t - t0 - 0.6) / 0.3)
                    cd.text(((PX1 - PX0) / 2, y + 120), txt[1], font=font("Silkscreen", 40), fill=lerpc((12, 14, 30), PINK, b), anchor="mm")
            y += hh
    im.alpha_composite(clip, (ox, oy))
    im.alpha_composite(SCAN, (PX0, PY0))
    # CTA under the panel
    if t >= T_DONE + 0.6:
        a = ease((t - T_DONE - 0.6) / 0.4)
        draw_rich(d, W / 2, 1580, [("What version are ", lerpc(BG_BOT, WHITE, a)), ("you", lerpc(BG_BOT, GOLD, a)), (" running?", lerpc(BG_BOT, WHITE, a))], font("Inter-Black", 60))
    return im.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ts = [0.0, 1.5, 9.0, 18.0, 26.0, DUR - 1]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88); print("DUR", DUR, "CPL", CPL)
    else:
        w = Writer("v011_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
