"""028: composite the Blender frames + the original's UI layer (Remotion Part1UI, transparent PNGs)
+ the JONAS / WASHER labels of s1, then mux 022's soundtrack unchanged (stream copy).

    python3 render.py FRAMES_DIR UI_DIR PROJ_JSON
FRAMES_DIR: f_0000.jpg ... f_0809.jpg from blender/build028.py (EEVEE on the Mac)
UI_DIR:     element-000.png ... from `npx remotion render build Part1UI <dir> --sequence --image-format=png`
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "kit"))
sys.path.insert(0, HERE)
import kit  # noqa: E402
import anim028 as A  # noqa: E402

FR, UI, PROJ = sys.argv[1], sys.argv[2], sys.argv[3]
SRC_AUDIO = os.path.join(ROOT, "videos", "022-biz-part1-laundry-stairs.mp4")
OUT = os.path.join(ROOT, "videos", "028-biz-part1-blender.mp4")
proj = {int(k): v for k, v in json.load(open(PROJ)).items()}
F = ImageFont.truetype(os.path.join(ROOT, "series", "is-this-a-business", "public", "Inter-Black.ttf"), 26)
INK, GOLD, WHITE = (28, 33, 64), (255, 201, 77), (251, 248, 242)


def label(im, x, y, text, bg, k):
    """pointer tip at (x, y); same shape as the 2D original's Label, Inter Black instead of the pixel font"""
    if k <= 0:
        return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tw = d.textlength(text, font=F) + 2 * len(text)
    w, h = tw + 32, 44
    cx, cy = x, y - 30 - h / 2
    d.polygon([(x - 10, cy + h / 2 - 2), (x, y), (x + 10, cy + h / 2 - 2)], fill=INK)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=11, fill=bg, outline=INK, width=4)
    xx = cx - tw / 2
    for ch in text:                                   # letter-spaced
        d.text((xx, cy - 1), ch, font=F, fill=INK, anchor="lm")
        xx += d.textlength(ch, font=F) + 2
    if k < 1:
        a = lay.getchannel("A").point(lambda v: int(v * k))
        lay.putalpha(a)
    im.alpha_composite(lay)


def main():
    tmp = OUT[:-4] + ".video.mp4"
    wr = kit.Writer(tmp)
    for f in range(A.N):
        t = f / A.FPS
        im = Image.open(os.path.join(FR, f"f_{f:04d}.jpg")).convert("RGBA")
        if t < A.T["s1"][1] and f in proj:
            k = 1 - A.tw(t, 1.9, 0.3)
            jx, jy = proj[f]["jonas"]
            wx, wy = proj[f]["washer"]
            label(im, jx, jy, "JONAS", GOLD, k)
            label(im, wx, wy, "WASHER", WHITE, k)
        ui = Image.open(os.path.join(UI, f"element-{f:03d}.png")).convert("RGBA")
        im.alpha_composite(ui)
        wr.write(im.convert("RGB"))
    wr.close()
    # 022's soundtrack, byte-identical (already -14 LUFS, 48 kHz AAC)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", SRC_AUDIO, "-map", "0:v", "-map", "1:a",
                    "-c", "copy", "-shortest", "-movflags", "+faststart", OUT], check=True)
    os.remove(tmp)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
