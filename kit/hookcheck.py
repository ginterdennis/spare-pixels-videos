"""Hook QA for a finished MP4 (rules in HOOKS.md). Run before scheduling any video:

    python3 kit/hookcheck.py videos/020-black-dots-v2.mp4 --hook "Count the BLACK dots" --reveal 3.0

Prints PASS/FAIL per rule and writes <file>.hook.jpg: frames at 0 / 0.5 / 1 / 1.5 / 2 / 3 s,
phone-sized, with TikTok's UI zones shaded, so you see what a scroller sees.
Exit code 1 if a hard rule fails.
"""
import argparse, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
TIMES = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]


def frame_at(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32)


def loudness(path, t, d=0.25):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{t:.3f}", "-t", f"{d}", "-i", path, "-vn",
                          "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "max_volume" in line:
            return float(line.split("max_volume:")[1].split()[0])
    return -99.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--hook", required=True, help="the words on screen at frame 0")
    ap.add_argument("--reveal", type=float, required=True, help="second of the first payoff")
    a = ap.parse_args()

    fr = {t: frame_at(a.video, t) for t in TIMES}
    luma = {t: (fr[t] @ np.array([0.299, 0.587, 0.114], np.float32)) for t in TIMES}
    # motion between consecutive sampled frames inside the safe area
    safe = (slice(180, H - 380), slice(0, W - 140))
    motion = [float(np.mean(np.abs(luma[b][safe] - luma[a_][safe]))) for a_, b in zip(TIMES[:3], TIMES[1:4])]
    words = len(a.hook.split())
    peak0 = loudness(a.video, 0.0)
    contrast0 = float(np.std(luma[0.0]))

    checks = [
        ("H1 hook <= 6 words", words <= 6, f"{words} words"),
        ("H2 motion in first second", min(motion[:2]) > 1.5, "mean |dLuma| " + ", ".join(f"{m:.1f}" for m in motion)),
        ("H3 sound hit at 0.0-0.25 s", peak0 > -12, f"peak {peak0:.1f} dB"),
        ("H4 first payoff by 3.0 s", a.reveal <= 3.0, f"reveal {a.reveal:.1f} s"),
        ("H6 frame 0 contrast", contrast0 > 35, f"luma std {contrast0:.0f}"),
    ]
    ok = True
    for name, passed, info in checks:
        ok &= passed
        print(f"{'PASS' if passed else 'FAIL'}  {name:30s} {info}")
    print("Manual: H5 payoff opens a new question | H7 no labels/jargon/hedges in 0-3 s | H8 caption line 1 = hook")

    # contact sheet with TikTok UI zones shaded (top 180 px, bottom 380 px, right rail 140 px)
    tw, th = 270, 480
    sheet = Image.new("RGB", (len(TIMES) * (tw + 8), th + 40), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for k, t in enumerate(TIMES):
        im = Image.fromarray(fr[t].astype(np.uint8)).convert("RGBA")
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for box in [(0, 0, W, 180), (0, H - 380, W, H), (W - 140, 760, W, H - 380)]:
            sd.rectangle(box, fill=(255, 0, 80, 70))
        im = Image.alpha_composite(im, sh).convert("RGB").resize((tw, th))
        sheet.paste(im, (k * (tw + 8), 0))
        d.text((k * (tw + 8) + 6, th + 10), f"{t:.1f}s", fill=(0, 0, 0))
    out = a.video[:-4] + ".hook.jpg"
    sheet.save(out, quality=88)
    print("sheet:", out)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
