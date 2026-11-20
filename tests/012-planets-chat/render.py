import sys, math
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from PIL import Image, ImageDraw
from kit import *

# who: (display name, name colour)
WHO = {
    "IAU": ("IAU (admin)", (255, 211, 107)), "Jupiter": ("Jupiter", (240, 170, 110)), "Earth": ("Earth", (90, 200, 255)),
    "Pluto": ("Pluto", (232, 196, 160)), "Neptune": ("Neptune", (110, 140, 255)), "Mercury": ("Mercury", (190, 190, 200)),
    "Venus": ("Venus", (255, 220, 120)), "Uranus": ("Uranus", (120, 230, 230)),
}
SCRIPT = [
    ("date", "AUG 24, 2006"),
    ("IAU", "Quick announcement. New rules for being a planet."),
    ("IAU", "1. Orbit the Sun\n2. Be round\n3. Clear your neighbourhood"),
    ("Jupiter", "easy. cleared mine ages ago"),
    ("Earth", "same. also I have life, just saying"),
    ("Pluto", "wait what does \"clear your neighbourhood\" mean"),
    ("Neptune", "it means you can't share your orbit with half the Kuiper Belt, Pluto"),
    ("Pluto", "they're my friends"),
    ("Mercury", "bro one year for you is 248 of Earth's"),
    ("Pluto", "Venus has a day longer than her year and nobody kicks HER out"),
    ("Venus", "leave me out of this"),
    ("Uranus", "can we focus, I'm literally spinning on my side over here"),
    ("IAU", "Also, Eris exists. She's about your size, Pluto."),
    ("Pluto", "who invited Eris"),
    ("sys", "IAU removed Pluto"),
    ("sys", "Pluto is now a dwarf planet"),
    ("Earth", "...should we tell him we still love him"),
]
FT = font("Inter-SemiBold", 40); FN = font("Inter-Bold", 30); FSY = font("Inter-SemiBold", 32)
MAXW = 640; PAD = 26; LH = 52
AX0, AY0, AY1 = 0, 330, 1410   # message area
def wrap(text):
    out = []
    for para in text.split("\n"):
        line = ""
        for w_ in para.split(" "):
            cand = (line + " " + w_).strip()
            if FT.getlength(cand) <= MAXW - 2 * PAD: line = cand
            else: out.append(line); line = w_
        out.append(line)
    return out
# timeline
items = []; t = 0.0
for who, text in SCRIPT:
    if who == "date":
        items.append(dict(kind="date", text=text, t=-0.5, h=90)); continue
    if who == "sys":
        t += 0.6
        items.append(dict(kind="sys", text=text, t=t, h=86)); t += 1.3; continue
    lines = wrap(text)
    typing = 0.0 if t == 0 else (0.45 if who != "Earth" else 0.3)
    tw = t + typing
    me = who == "Earth"
    h = PAD * 2 + LH * len(lines) + (0 if me else 40) + 18
    items.append(dict(kind="msg", who=who, lines=lines, t=(tw if tw > 0 else -0.3), t_typing=t, h=h, me=me))
    t = tw + 0.55 + len(text) * 0.037
T_END = t + 0.4
T_CTA = T_END
DUR = T_CTA + 4.6
T_REMOVE = next(it["t"] for it in items if it["kind"] == "sys")
BG = vgrad((16, 18, 30), (10, 11, 20))

def avatar(d, cx, cy, who, r=34):
    if who == "IAU":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 44, 70), outline=GOLD, width=3)
        d.text((cx, cy + 1), "IAU", font=font("Inter-Black", 22), fill=GOLD, anchor="mm"); return
    base = {"Jupiter": (214, 150, 100), "Earth": (60, 130, 230), "Pluto": (214, 184, 150), "Neptune": (70, 100, 230),
            "Mercury": (150, 150, 160), "Venus": (235, 200, 110), "Uranus": (110, 210, 220)}[who]
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=base)
    if who == "Jupiter":
        for k, dy in enumerate([-16, -4, 9, 20]):
            d.rectangle((cx - r + 6, cy + dy, cx + r - 6, cy + dy + 5), fill=(170, 100, 70) if k % 2 == 0 else (240, 200, 160))
        d.ellipse((cx + 6, cy + 6, cx + 18, cy + 14), fill=(190, 80, 60))
    if who == "Earth":
        for (x0, y0, x1, y1) in [(-20, -18, 2, 4), (6, -6, 24, 14), (-8, 10, 6, 24)]:
            d.ellipse((cx + x0, cy + y0, cx + x1, cy + y1), fill=(80, 200, 120))
    if who == "Pluto":   # the heart (Tombaugh Regio)
        hx_, hy_ = cx + 4, cy + 6
        d.ellipse((hx_ - 14, hy_ - 12, hx_, hy_ + 2), fill=(250, 236, 220)); d.ellipse((hx_ - 2, hy_ - 12, hx_ + 12, hy_ + 2), fill=(250, 236, 220))
        d.polygon([(hx_ - 14, hy_ - 4), (hx_ + 12, hy_ - 4), (hx_ - 1, hy_ + 14)], fill=(250, 236, 220))
    if who == "Uranus":
        d.line((cx - 4, cy - r - 6, cx + 4, cy + r + 6), fill=(200, 255, 255), width=3)
    if who == "Mercury":
        for (x, y, rr) in [(-10, -8, 6), (10, 6, 5), (-4, 14, 4)]:
            d.ellipse((cx + x - rr, cy + y - rr, cx + x + rr, cy + y + rr), fill=(120, 120, 130))
    if who == "Neptune":
        d.ellipse((cx - 14, cy - 10, cx + 2, cy), fill=(40, 60, 170))

def draw_item(d, it, y, t):
    if it["kind"] == "date":
        tw_ = FSY.getlength(it["text"]) + 50
        d.rounded_rectangle((W / 2 - tw_ / 2, y + 16, W / 2 + tw_ / 2, y + 70), radius=27, fill=(34, 38, 60))
        d.text((W / 2, y + 43), it["text"], font=FSY, fill=MUTED, anchor="mm"); return
    if it["kind"] == "sys":
        a = ease((t - it["t"]) / 0.25)
        red = it["text"].startswith("IAU removed")
        txt = it["text"]
        tw_ = FSY.getlength(txt) + 60
        fill = lerpc((16, 18, 30), (90, 30, 50) if red else (34, 38, 60), a)
        d.rounded_rectangle((W / 2 - tw_ / 2, y + 14, W / 2 + tw_ / 2, y + 72), radius=29, fill=fill)
        d.text((W / 2, y + 43), txt, font=FSY, fill=lerpc((16, 18, 30), (255, 150, 170) if red else WHITE, a), anchor="mm"); return
    s = pop_scale(t - it["t"])
    lines = it["lines"]; me = it["me"]
    bw = max(FT.getlength(l) for l in lines) + 2 * PAD
    if not me: bw = max(bw, FN.getlength(WHO[it["who"]][0]) + 2 * PAD)
    bh = it["h"] - 18
    if me: x1 = 1030; x0 = x1 - bw
    else: x0 = 140; x1 = x0 + bw
    cx, cy = (x0 + x1) / 2, y + bh / 2
    sx0, sy0 = cx + (x0 - cx) * s, cy + (y - cy) * s
    sx1, sy1 = cx + (x1 - cx) * s, cy + (y + bh - cy) * s
    col = (40, 110, 220) if me else (36, 40, 64)
    d.rounded_rectangle((sx0, sy0, sx1, sy1), radius=int(30 * s) + 1, fill=col)
    if s > 0.9:
        ty = y + PAD
        if not me:
            d.text((x0 + PAD, ty), WHO[it["who"]][0], font=FN, fill=WHO[it["who"]][1]); ty += 40
        for l in lines:
            d.text((x0 + PAD, ty), l, font=FT, fill=WHITE); ty += LH
    if not me: avatar(d, 80, y + bh - 34, it["who"])

def pop_scale(dt_):
    if dt_ <= 0: return 0.0
    u = min(1, dt_ / 0.2)
    return 1 + 0.06 * math.sin(math.pi * u) * (1 - u) - (1 - u) ** 3 * 0.6 if u < 1 else 1.0

def frame(i):
    t = i / FPS
    im = Image.fromarray(BG.copy())
    d = ImageDraw.Draw(im)
    # messages (scroll so the newest is in view)
    vis = [it for it in items if t >= it.get("t_typing", it["t"]) - 0.0001]
    hs = 0.0
    for it in items:
        if t >= it["t"]: hs += it["h"] * ease((t - it["t"]) / 0.3)
    typing_it = next((it for it in items if it["kind"] == "msg" and it.get("t_typing", 0) <= t < it["t"]), None)
    if typing_it: hs += 100
    area_h = AY1 - AY0
    scroll = max(0, hs - area_h + 20)
    y = AY0 + 10 - scroll
    for it in items:
        if t < it["t"]: break
        if y + it["h"] > AY0 - 200: draw_item(d, it, y, t)
        y += it["h"] * ease((t - it["t"]) / 0.3)
    if typing_it:
        me = typing_it["me"]
        x0 = 140 if not me else 1030 - 150
        d.rounded_rectangle((x0, y + 4, x0 + 150, y + 84), radius=30, fill=(36, 40, 64) if not me else (40, 110, 220))
        for k in range(3):
            ph = math.sin(t * 9 - k * 0.9)
            d.ellipse((x0 + 38 + k * 30 - 9, y + 44 - 9 - 6 * ph, x0 + 38 + k * 30 + 9, y + 44 + 9 - 6 * ph), fill=(170, 176, 210))
        if not me: avatar(d, 80, y + 50, typing_it["who"])
    # header (drawn last so messages scroll under it)
    d.rectangle((0, 0, W, AY0 - 10), fill=(22, 24, 40))
    d.line((0, AY0 - 10, W, AY0 - 10), fill=(44, 48, 74), width=2)
    d.text((60, 250), "<", font=font("Inter-Bold", 56), fill=CYAN, anchor="mm")
    spr, R = glow_sprite(30, (255, 196, 70), glow=3.0, alpha=0.5)
    im.paste(spr, (150 - R, 250 - R), spr)
    d = ImageDraw.Draw(im)
    d.text((210, 228), "The Planets", font=font("Inter-Black", 48), fill=WHITE, anchor="lm")
    removed = t >= T_REMOVE
    fl = 1 - ease((t - T_REMOVE) / 1.2) if removed else 0
    d.text((210, 280), f"{8 if removed else 9} members", font=font("Inter-SemiBold", 32), fill=lerpc(MUTED, (255, 120, 150), fl), anchor="lm")
    # input bar
    d.rectangle((0, AY1 + 10, W, AY1 + 130), fill=(22, 24, 40))
    d.rounded_rectangle((50, AY1 + 32, 1030, AY1 + 108), radius=38, fill=(36, 40, 64))
    d.text((90, AY1 + 70), "Message", font=font("Inter-SemiBold", 36), fill=(110, 116, 150), anchor="lm")
    # POV hook pill at the start
    a = 1 - ease((t - 2.6) / 0.4)
    if a > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((90, 860, 990, 1080), radius=40, fill=(8, 9, 18, int(235 * a)))
        draw_rich(od, W / 2, 950, [("POV: ", GOLD + (int(255 * a),)), ("the planets' group chat", WHITE + (int(255 * a),))], font("Inter-Black", 58))
        draw_rich(od, W / 2, 1030, [("on the day Pluto got voted out", MUTED + (int(255 * a),))], font("Inter-Bold", 42))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    # CTA at the end
    if t >= T_CTA:
        a = ease((t - T_CTA) / 0.4)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((70, 760, 1010, 1160), radius=44, fill=(8, 9, 18, int(240 * a)))
        draw_rich(od, W / 2, 880, [("Should Pluto be", WHITE + (int(255 * a),))], font("Inter-Black", 70))
        draw_rich(od, W / 2, 965, [("a planet again?", GOLD + (int(255 * a),))], font("Inter-Black", 70))
        draw_rich(od, W / 2, 1075, [("YES", (90, 230, 150, int(255 * a))), ("  or  ", MUTED + (int(255 * a),)), ("NO", PINK + (int(255 * a),)), ("  in the comments", MUTED + (int(255 * a),))], font("Inter-Bold", 46))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    return im

if __name__ == "__main__":
    if sys.argv[1:] == ["stills"]:
        ts = [0.0, 6.0, 15.0, 24.0, T_REMOVE + 0.8, T_CTA - 0.5, DUR - 1]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        st = Image.new("RGB", (270 * len(ims), 480))
        for k, x in enumerate(ims): st.paste(x, (k * 270, 0))
        st.save("stills.jpg", quality=88); print("DUR", DUR, "T_REMOVE", T_REMOVE)
    else:
        w = Writer("v012_video.mp4")
        for i in range(int(DUR * FPS)): w.write(frame(i))
        w.close(); print("frames", w.n)
