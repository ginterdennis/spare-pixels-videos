"""Render one look of 041.   python3 render.py A|B|C [stills [t1 t2 ...]]
Full render -> v041<look>.silent.mp4 (1080x1920, 30 fps, H.264 via kit.Writer)."""
import sys, os, time
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import skia
from PIL import Image
from kit import Writer
from common import W, H, FPS, END, A, draw_frame
from styles import STYLES

HERE = os.path.dirname(os.path.abspath(__file__))
look = sys.argv[1]
S = STYLES[look]()
S._fr = 0
arr = np.zeros((H, W, 4), np.uint8)
surf = skia.Surface(arr)
cv = surf.getCanvas()


def glitch_amt(t):
    yt = t - A["remember"]
    if 0 <= yt < 0.35:
        return 1 - yt / 0.35
    ct = t - A["crack"]
    if 0 <= ct < 0.14:
        return 0.6 * (1 - ct / 0.14)
    return 0.0


def post(fr, t):
    g = glitch_amt(t)
    if g <= 0:
        return
    rng = np.random.default_rng(fr)
    rgb = arr[:, :, :3]
    for _ in range(int(3 + 6 * g)):
        y0 = int(rng.uniform(300, 1500)); h = int(rng.uniform(8, 60))
        rgb[y0:y0 + h] = np.roll(rgb[y0:y0 + h], int(rng.uniform(-50, 50) * g), axis=1)
    s = int(10 * g)
    if s:
        rgb[:, :, 0] = np.roll(rgb[:, :, 0], s, axis=1)
        rgb[:, :, 2] = np.roll(rgb[:, :, 2], -s, axis=1)


def frame(fr):
    t = fr / FPS
    S._fr = fr
    cv.clear(skia.ColorBLACK)
    draw_frame(cv, S, t, fr)
    S.finish(surf, arr, t)
    post(fr, t)
    return arr[:, :, :3]


if len(sys.argv) > 2 and sys.argv[2] == "stills":
    times = [float(x) for x in sys.argv[3:]]
    tw_, th_ = 360, 640
    cols = 6
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw_ + 6), rows * (th_ + 30)), (255, 255, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for k, t in enumerate(times):
        im = Image.fromarray(frame(int(round(t * FPS))).copy()).resize((tw_, th_), Image.LANCZOS)
        x, y = (k % cols) * (tw_ + 6), (k // cols) * (th_ + 30)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + th_ + 6), f"{t:.1f}s", fill=(0, 0, 0))
    out = os.path.join(HERE, f"stills_{look}.jpg")
    sheet.save(out, quality=88)
    print(out)
    sys.exit(0)

n = int(round(END * FPS))
part, parts = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 and sys.argv[2] == "part" else (0, 1)
f0, f1 = n * part // parts, n * (part + 1) // parts
out = os.path.join(HERE, f"v041{look}.silent.mp4" if parts == 1 else f"v041{look}.part{part}.mp4")
w = Writer(out)
t0 = time.time()
for fr in range(f0, f1):
    w.write(frame(fr))
    if fr % 150 == 0:
        print(f"{look}: {fr}/{n} frames, {time.time() - t0:.0f}s", flush=True)
w.close()
print(out, f"{time.time() - t0:.0f}s")
