import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import *
from fourier import build_path, coeffs, trace
from glyph import outline

NAME = "Emma"; K = 200
z, PEN = build_path(NAME, M=4096)
z = np.conj(z)  # y down
bb = (z.real.min(), z.real.max(), z.imag.min(), z.imag.max())
SC = 900 / (bb[1] - bb[0])
CX, CY = W / 2, 900
z = (z - complex((bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2)) * SC + complex(CX, CY)
C0, C, KK = coeffs(z)
NT = 8000
TR, S = trace(C0, C, KK, K, NT)
PD = PEN[(S * len(PEN)).astype(int)]
T0, T1 = 0.4, 14.4         # drawing time
T_FADE = T1 + 0.2
DUR = 20.0
SS = 2                     # supersample for the drawing region
RX0, RY0, RW, RH = 0, 420, W, 1060  # region for circles/trace

def s_at(t):
    u = min(1, max(0, (t - T0) / (T1 - T0)))
    return u
BG = vgrad()
# filled name for the end (from outline polygon)
g = outline(NAME)
def fill_mask():
    m = Image.new("L", (RW * SS, RH * SS), 0); dm = ImageDraw.Draw(m)
    def tf(pts):
        p = np.array(pts); zz = np.conj(p[:, 0] + 1j * p[:, 1])
        zz = (zz - complex((bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2)) * SC + complex(CX, CY)
        return [((q.real - RX0) * SS, (q.imag - RY0) * SS) for q in zz]
    for x in getattr(g, "geoms", [g]):
        dm.polygon(tf(x.exterior.coords), fill=255)
        for h in x.interiors: dm.polygon(tf(h.coords), fill=0)
    return m.resize((RW, RH), Image.LANCZOS)
FILL = fill_mask()

def frame(i):
    t = i / FPS
    s = s_at(t)
    im = Image.fromarray(BG.copy()).convert("RGBA")
    lay = Image.new("RGBA", (RW * SS, RH * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    off = complex(RX0, RY0)
    def P(q): return ((q.real - RX0) * SS, (q.imag - RY0) * SS)
    # trace up to s
    n = int(s * NT)
    trc = TR[:n]
    tr_layer = Image.new("RGBA", lay.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tr_layer)
    if n > 1:
        pts = [P(q) for q in trc]
        run = []
        for a in range(n):
            if PD[a]: run.append(pts[a])
            else:
                if len(run) > 1: td.line(run, fill=GOLD + (255,), width=7 * SS // 2, joint="curve")
                run = []
        if len(run) > 1: td.line(run, fill=GOLD + (255,), width=7 * SS // 2, joint="curve")
    # circles + arms
    ca = 1 - ease((t - T1) / 0.8)
    if ca > 0:
        terms = C[:K] * np.exp(2j * np.pi * KK[:K] * s)
        chain = C0 + np.concatenate([[0], np.cumsum(terms)])
        for j in range(K):
            r = abs(C[j]) * SS
            if r < 1.2: continue
            cx, cy = P(chain[j])
            al = int((150 if j < 6 else 95 if j < 25 else 55 if j < 80 else 30) * ca)
            col = (150, 200, 255) if j % 2 else (255, 140, 210)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (al,), width=2 * SS if j < 25 else SS)
        arm = [P(q) for q in chain[: min(K, 140) + 1]]
        d.line(arm, fill=(240, 244, 255, int(210 * ca)), width=2 * SS)
        tip = P(chain[-1])
        d.ellipse((tip[0] - 7 * SS, tip[1] - 7 * SS, tip[0] + 7 * SS, tip[1] + 7 * SS), fill=WHITE + (int(255 * ca),))
    lay = lay.resize((RW, RH), Image.LANCZOS)
    trs = tr_layer.resize((RW, RH), Image.LANCZOS)
    glow = trs.filter(ImageFilter.GaussianBlur(14))
    # fill at the end
    fa = ease((t - T_FADE) / 0.9)
    reg = im.crop((RX0, RY0, RX0 + RW, RY0 + RH))
    if fa > 0:
        fl = Image.new("RGBA", (RW, RH), GOLD + (0,))
        fl.putalpha(FILL.point(lambda v: int(v * 0.92 * fa)))
        reg = Image.alpha_composite(reg, fl)
    reg = Image.alpha_composite(reg, glow)
    reg = Image.alpha_composite(reg, glow)
    reg = Image.alpha_composite(reg, trs)
    reg = Image.alpha_composite(reg, lay)
    im.paste(reg, (RX0, RY0))
    im = im.convert("RGB"); d2 = ImageDraw.Draw(im)
    # text
    fT = font("Inter-Black", 92); fS = font("Inter-Bold", 58)
    eo = ease((t - (T1 + 0.4)) / 0.3); ei = ease((t - (T1 + 0.75)) / 0.4)
    if eo < 1:
        a = 1 - eo
        draw_rich(d2, W / 2, 300, [("200 circles.", lerpc(BG_TOP, WHITE, a))], fT)
        draw_rich(d2, W / 2, 392, [("One pen. ", lerpc(BG_TOP, WHITE, a)), ("Watch what they write.", lerpc(BG_TOP, GOLD, a))], fS)
        fl_ = font("Inter-SemiBold", 28); fn = font("Inter-Black", 76)
        label(d2, 330, 1440, "CIRCLES", fl_, lerpc(BG_BOT, MUTED, a), spacing=5)
        label(d2, 750, 1440, "WRITTEN", fl_, lerpc(BG_BOT, MUTED, a), spacing=5)
        draw_rich(d2, 330, 1530, [(f"{K}", lerpc(BG_BOT, WHITE, a))], fn)
        draw_rich(d2, 750, 1530, [(f"{s*100:.0f}%", lerpc(BG_BOT, WHITE, a))], fn)
    if ei > 0:
        dy = 20 * (1 - ei)
        draw_rich(d2, W / 2, 300 + dy, [("Comment your ", lerpc(BG_TOP, WHITE, ei)), ("name.", lerpc(BG_TOP, GOLD, ei))], fT)
        draw_rich(d2, W / 2, 392 + dy, [("The circles will write it next.", lerpc(BG_TOP, WHITE, ei))], fS)
    return im

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        for t in [0.0, 4.0, 9.0, 14.0, 16.5]:
            frame(int(t * FPS)).save(f"still_{t:04.1f}.png")
        from PIL import Image as I
        import glob
        fs = sorted(glob.glob("still_*.png")); ims = [I.open(f).resize((360, 640)) for f in fs]
        st = I.new("RGB", (360 * len(ims), 640))
        for k_, x in enumerate(ims): st.paste(x, (k_ * 360, 0))
        st.save("stills.jpg", quality=88)
    else:
        w = Writer("v005_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
