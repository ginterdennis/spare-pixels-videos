import sys
sys.path.insert(0, "/home/claude/kit")
from PIL import Image, ImageDraw
from kit import *
im = Image.fromarray(vgrad()); d = ImageDraw.Draw(im)
draw_rich(d, W / 2, 250, [("8 pixel ", WHITE), ("wallpapers", GOLD)], font("Inter-Black", 92))
draw_rich(d, W / 2, 330, [("drawn with code, pixel by pixel", MUTED)], font("Inter-Bold", 44))
tw, th, gx, gy = 225, 400, 24, 56
x0 = (W - (4 * tw + 3 * gx)) // 2; y0 = 420
for i in range(8):
    c, r = i % 4, i // 4
    x, y = x0 + c * (tw + gx), y0 + r * (th + gy)
    th_ = Image.open(f"wall_{i+1}.png").resize((tw, th), Image.NEAREST)
    m = Image.new("L", (tw, th), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, tw - 1, th - 1), radius=22, fill=255)
    im.paste(th_, (x, y), m)
    d.rounded_rectangle((x - 2, y - 2, x + tw + 1, y + th + 1), radius=24, outline=(70, 76, 120), width=3)
    bx, by = x + 14, y + th - 70
    d.rounded_rectangle((bx, by, bx + 56, by + 56), radius=14, fill=(8, 9, 20))
    d.text((bx + 28, by + 30), str(i + 1), font=font("Inter-Black", 38), fill=GOLD, anchor="mm")
draw_rich(d, W / 2, 1400, [("Which number are you ", WHITE), ("taking?", GOLD)], font("Inter-Black", 60))
draw_rich(d, W / 2, 1470, [("swipe for the full wallpapers", MUTED)], font("Inter-SemiBold", 38))
im.save("slide_0_cover.png")
for k, x in enumerate([im] + [Image.open(f"wall_{i}.png") for i in range(1, 9)]):
    x.convert("RGB").save(f"008-wallpapers-{k:02d}.jpg", quality=93, subsampling=0)
print("ok")
