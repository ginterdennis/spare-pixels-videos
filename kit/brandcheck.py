"""Brand check for a finished video (Sigmoid Horizon, Neon Eclipse). Run before scheduling:

    python3 kit/brandcheck.py videos/<file>.mp4

Every check must PASS (exit code 0). Rules: brand/README.md.
  B1 ground    the frame is dark (void/night), not a light or coloured background
  B2 icon      the round brand icon is on screen at its place (top right, or top left in a series row)
  B3 palette   no large areas in colours outside the brand palette (old gold, warm paper, browns, greens)
  B4 loop      the last frame hands back to frame 0 (seamless loop, VIEWS.md V6)
"""
import argparse
import colorsys
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand as B  # noqa: E402

# hue bands (degrees) that belong to the brand: magenta/pink, ultraviolet, cyan, mint, ion blue, solar
BRAND_HUES = [(178, 335), (145, 168), (32, 40)]   # cyan..ultraviolet..magenta (incl. the gradient between), mint, solar
SKIN = (8, 34)          # skin tones of the illustrated cast are allowed (low-saturation oranges)
ICON_SPOTS = [(B.WATERMARK[0], B.WATERMARK[1], B.WATERMARK[2]),   # Shorts: top right, 128 px
              (48, 196, 76)]                                         # series row: top left, 76 px


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def frame_at(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", path, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B.W}x{B.H}", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(B.H, B.W, 3).astype(np.float32)


def last_frame(path, dur):
    for back in (0.04, 0.07, 0.1, 0.15):
        try:
            return frame_at(path, dur - back)
        except ValueError:
            continue
    raise SystemExit("could not read the last frame")


def lum(img):
    return (0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]) / 255.0


def check_ground(frames):
    """Median luminance of the frame border (where the ground shows) must be dark."""
    vals = []
    for f in frames:
        L = lum(f)
        border = np.concatenate([L[:, :60].ravel(), L[:, -60:].ravel(), L[:160].ravel(), L[-160:].ravel()])
        vals.append(float(np.median(border)))
    worst = max(vals)
    return worst <= 0.16, f"border luminance {worst:.2f} (max 0.16)"


def icon_template(size):
    surf, cv = B.new_frame(size, size)
    cv.clear(B.col(B.VOID))
    B.icon(cv, 0, 0, size)
    return lum(B.to_rgb(surf).astype(np.float32))


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


def check_icon(frames):
    best = 0.0
    for f in frames:
        L = lum(f)
        for x, y, s in ICON_SPOTS:
            tpl = icon_template(s)
            for dy in range(-14, 15, 2):
                for dx in range(-14, 15, 2):
                    x0, y0 = x + dx, y + dy
                    if x0 < 0 or y0 < 0 or x0 + s > B.W or y0 + s > B.H:
                        continue
                    best = max(best, ncc(L[y0:y0 + s, x0:x0 + s], tpl))
    return best >= 0.55, f"icon match {best:.2f} (min 0.55)"


def off_brand_fraction(f):
    small = f[::6, ::6] / 255.0
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in small.reshape(-1, 3)])
    h, s, v = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    vivid = (s > 0.45) & (v > 0.35)
    ok = np.zeros_like(vivid)
    for lo, hi in BRAND_HUES:
        ok |= (h >= lo) & (h <= hi)
    ok |= (h >= SKIN[0]) & (h <= SKIN[1]) & (s < 0.62)
    return float((vivid & ~ok).mean())


def check_palette(frames):
    worst = max(off_brand_fraction(f) for f in frames)
    return worst <= 0.02, f"off-brand colour area {worst * 100:.1f}% of the frame (max 2%)"


def check_loop(first, last):
    d = float(np.abs(first - last).mean())
    return d <= 14.0, f"first vs last frame mean difference {d:.1f} (max 14)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--no-loop", action="store_true", help="skip B4 (only for formats the user exempted)")
    a = ap.parse_args()
    dur = probe_duration(a.video)
    times = [0.0, dur * 0.25, dur * 0.5, dur * 0.75]
    frames = [frame_at(a.video, t) for t in times]
    results = [("B1 ground", *check_ground(frames)),
               ("B2 icon", *check_icon(frames[:3])),
               ("B3 palette", *check_palette(frames))]
    if not a.no_loop:
        results.append(("B4 loop", *check_loop(frames[0], last_frame(a.video, dur))))
    failed = False
    for name, ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {msg}")
        failed |= not ok
    print("brandcheck:", "FAILED (see brand/README.md)" if failed else "all passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
