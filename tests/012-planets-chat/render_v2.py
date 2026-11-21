"""012 v2 (hook rebuild, 21 Nov 2026, HOOKS.md): cold open on the climax, then rewind.
v1 opened on a tiny "POV" pill over a still chat; the funny part (Pluto removed) came at ~35 s.
v2: frame 0 = the end of the chat with a 4-word hook "Pluto got KICKED out."; the red
"IAU removed Pluto" pops at 0.6 s (first payoff + boom), "Here's how it went." then a fast
rewind (scroll back to the top) at 2.2 s, and the whole v1 chat plays from 2.8 s.
All chat drawing comes from render.py (v1)."""
import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *
from hook import hook_text, stamp
import render as V1

COLD0 = V1.T_REMOVE - 0.6        # v1 time shown at frame 0 (Pluto's last message just sent)
POP = 0.6                        # removal pops in
SWAP = 1.45                      # second hook line
RW0, RW1 = 2.2, 2.8              # rewind
V1START = 3.0                    # v1 time where the main play starts (after v1's POV pill has faded)
OFF = RW1 - V1START              # t = v1_time + OFF in the main part
DUR = V1.DUR + OFF
T_CTA = V1.T_CTA + OFF


def v1_time(t):
    if t < RW0:
        return COLD0 + t
    if t < RW1:
        u = ease((t - RW0) / (RW1 - RW0))
        return (COLD0 + RW0) + (V1START - (COLD0 + RW0)) * u
    return t - OFF


def frame(i):
    t = i / FPS
    vt = v1_time(t)
    im = V1.frame(int(round(vt * FPS))).convert("RGBA")
    if t < RW0:
        if t < SWAP:
            hook_text(im, t, [[("Pluto got", WHITE)], [("KICKED out.", PINK)]], y=470)
        else:
            hook_text(im, t, [[("Here's how", WHITE)], [("it went down.", GOLD)]], y=470, t0=SWAP)
        stamp(im, t, POP, [("IAU removed Pluto", (255, 150, 170))], y=1150, size=78, panel=True)
    elif t < RW1 + 0.5:
        # rewind: scanlines + label
        u = (t - RW0) / (RW1 + 0.5 - RW0)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        if t < RW1:
            for y in range(0, H, 6):
                od.line((0, y, W, y), fill=(0, 0, 0, 70))
            off = int(40 * math.sin(t * 60))
            od.rectangle((0, 900 + off, W, 960 + off), fill=(255, 255, 255, 40))
        a = 1 - ease((t - RW1) / 0.5) if t >= RW1 else 1
        od.rounded_rectangle((W / 2 - 330, 760, W / 2 + 330, 900), radius=36, fill=(8, 9, 20, int(225 * a)))
        draw_rich(od, W / 2, 853, [("<< ", PINK + (int(255 * a),)), ("EARLIER THAT DAY", WHITE + (int(255 * a),))],
                  font("Inter-Black", 60))
        im.alpha_composite(ov)
    return im.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 0.8, 1.6, 2.4, 3.2, 5.0, 10.0]
        ims = [frame(int(t * FPS)).resize((360, 640)) for t in ts]
        st = Image.new("RGB", (360 * len(ims), 640))
        for k, x in enumerate(ims): st.paste(x, (k * 360, 0))
        st.save("stills_v2.jpg", quality=88); print("DUR", DUR, "T_CTA", T_CTA)
    else:
        w = Writer("v012v2_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
