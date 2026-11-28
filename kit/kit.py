"""Shared toolkit for Sigmoid Horizon (formerly Spare Pixels) videos: frames -> ffmpeg pipe, text, synth audio, mux."""
import os, subprocess, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import signal
from scipy.io import wavfile

W, H, FPS = 1080, 1920, 30
FONTS = os.path.join(os.path.dirname(__file__), "fonts")

# Brand palette: Sigmoid Horizon "Neon Eclipse" since 28 Nov 2026 (brand/README.md, kit/brand.py).
# The old names stay so existing helpers keep working; their values are now the brand's:
# BG = void, GOLD (the old accent) = sun-pink, PINK = magenta, CYAN = horizon cyan, MUTED = haze.
# Old spare.pixels values (navy gradient, gold #FFD36B) are kept in OLD_* only to re-render archived videos.
OLD_BG_TOP, OLD_BG_BOT, OLD_GOLD = (14, 16, 32), (6, 7, 16), (255, 211, 107)
BG_TOP = (5, 3, 11)
BG_BOT = (5, 3, 11)
WHITE = (242, 247, 255)
GOLD = (255, 90, 223)
PINK = (255, 47, 208)
CYAN = (34, 230, 255)
VIOLET = (176, 92, 255)
MUTED = (164, 157, 196)


@functools.lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), size)


def vgrad(top=BG_TOP, bot=BG_BOT, w=W, h=H):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, float)[None, None, :] * (1 - t) + np.array(bot, float)[None, None, :] * t
    return np.repeat(a, w, axis=1).astype(np.uint8)


def text_w(txt, f, spacing=0):
    if not txt:
        return 0
    return f.getlength(txt) + spacing * (len(txt) - 1)


def draw_rich(d, cx, y, parts, f, spacing=0, anchor="ms"):
    """parts = [(text, color), ...] drawn on one line centered at cx, baseline y."""
    total = sum(text_w(t, f, spacing) for t, _ in parts) + spacing * (len(parts) - 1 if spacing else 0)
    x = cx - total / 2
    for t, c in parts:
        if spacing:
            for ch in t:
                d.text((x, y), ch, font=f, fill=c, anchor="ls")
                x += f.getlength(ch) + spacing
        else:
            d.text((x, y), t, font=f, fill=c, anchor="ls")
            x += f.getlength(t)


def label(d, cx, y, txt, f, fill, spacing=4):
    """letter-spaced small caps label centred at cx (baseline y)."""
    draw_rich(d, cx, y, [(txt, fill)], f, spacing=spacing)


def ease(t):
    t = min(1, max(0, t)); return t * t * (3 - 2 * t)


def ease_out(t, p=3):
    t = min(1, max(0, t)); return 1 - (1 - t) ** p


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


@functools.lru_cache(None)
def glow_sprite(r, color, glow=2.6, alpha=0.55):
    """RGBA sprite of a ball with soft glow."""
    R = int(r * glow) + 4
    im = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    g = Image.new("L", (2 * R, 2 * R), 0)
    ImageDraw.Draw(g).ellipse((R - r * 1.25, R - r * 1.25, R + r * 1.25, R + r * 1.25), fill=int(255 * alpha))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.75))
    col = Image.new("RGBA", im.size, color + (0,))
    col.putalpha(g)
    im = Image.alpha_composite(im, col)
    d = ImageDraw.Draw(im)
    d.ellipse((R - r, R - r, R + r, R + r), fill=color + (255,))
    return im, R


class Writer:
    """Pipe RGB frames to ffmpeg. Writes to tmp name, renames on success."""

    def __init__(self, path, fps=FPS, w=W, h=H, crf=18):
        self.path, self.tmp = path, path[:-4] + ".tmp.mp4"
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", self.tmp],
            stdin=subprocess.PIPE)
        self.n = 0

    def write(self, frame):
        if isinstance(frame, Image.Image):
            frame = np.asarray(frame.convert("RGB"))
        self.p.stdin.write(np.ascontiguousarray(frame, dtype=np.uint8).tobytes())
        self.n += 1

    def close(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        os.replace(self.tmp, self.path)
        return self.path


def mux(video, wav, out, loud=-14):
    tmp = out[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", f"loudnorm=I={loud}:TP=-1.5:LRA=11", "-shortest", "-movflags", "+faststart", tmp],
                   check=True)
    os.replace(tmp, out)
    return out


# ---------------------------------------------------------------- audio
SR = 48000


def tt(d):
    return np.arange(int(d * SR)) / SR


def sos(kind, f, order=2):
    return signal.butter(order, f, kind, fs=SR, output="sos")


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR
        self.buf = np.zeros((self.n, 2))
        self.verb = np.zeros((self.n, 2))
        self.dur = dur

    def add(self, t0, sig, pan=0.0, gain=1.0, verb=0.0):
        i0 = int(round(t0 * SR))
        if i0 < 0:
            sig = sig[-i0:]; i0 = 0
        if i0 >= self.n or len(sig) == 0:
            return
        k = min(len(sig), self.n - i0)
        l = math.cos((pan + 1) * math.pi / 4) * 1.414
        r = math.sin((pan + 1) * math.pi / 4) * 1.414
        if sig.ndim == 2:
            self.buf[i0:i0 + k] += sig[:k] * gain
            if verb: self.verb[i0:i0 + k] += sig[:k] * gain * verb
            return
        self.buf[i0:i0 + k, 0] += sig[:k] * gain * l
        self.buf[i0:i0 + k, 1] += sig[:k] * gain * r
        if verb:
            self.verb[i0:i0 + k, 0] += sig[:k] * gain * l * verb
            self.verb[i0:i0 + k, 1] += sig[:k] * gain * r * verb

    def render(self, path, rt=1.8, seed=1):
        rng = np.random.default_rng(seed)
        n = int(rt * SR)
        t = np.arange(n) / SR
        out = self.buf.copy()
        if np.any(self.verb):
            for ch in range(2):
                ir = rng.standard_normal(n) * np.exp(-t * 6.9 / rt)
                ir = signal.sosfilt(sos("lowpass", 6000), ir)
                ir /= np.sqrt(np.sum(ir ** 2))
                wet = signal.fftconvolve(self.verb[:, ch], ir)[: self.n]
                out[:, ch] += wet * 0.6
        out = out[: int(self.dur * SR)]
        fade = min(len(out), int(0.05 * SR))
        out[-fade:] *= np.linspace(1, 0, fade)[:, None]
        pk = np.max(np.abs(out)) or 1
        out = out / pk * 0.89
        wavfile.write(path, SR, (out * 32767).astype(np.int16))
        return path


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.2, hold=None):
    t = np.arange(n) / SR
    dur = n / SR
    hold = dur - r if hold is None else hold
    e = np.where(t < a, t / a, np.where(t < a + d, 1 - (1 - s) * (t - a) / d, s))
    rel = np.clip((dur - t) / r, 0, 1)
    return e * rel


def pluck(f, d=0.9, bright=0.6):
    t = tt(d)
    s = np.zeros_like(t)
    for h in range(1, 7):
        s += (bright ** (h - 1)) * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + 2.2 * h))
    return s * np.minimum(1, t / 0.002) * 0.6


def bell(f, d=2.0, tau=0.7):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.25)
            + 0.2 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / 0.08)) * np.exp(-t / tau) * np.minimum(1, t / 0.002)


def pulse(f, d, duty=0.25, rel=0.06, lp=4200):
    t = tt(d); ph = (f * t) % 1
    s = np.where(ph < duty, 1.0, -1.0)
    s = signal.sosfilt(sos("lowpass", lp), s)
    return s * np.minimum(1, t / 0.003) * np.clip((d - t) / rel, 0, 1)


def tri(f, d, rel=0.05):
    t = tt(d); ph = (f * t) % 1
    s = 4 * np.abs(ph - 0.5) - 1
    return s * np.clip((d - t) / rel, 0, 1) * np.minimum(1, t / 0.004)


def pad(freqs, d, a=0.6, r=0.8, lp=1800, detune=0.004, seed=0):
    rng = np.random.default_rng(seed)
    t = tt(d)
    s = np.zeros((len(t), 2))
    for f in freqs:
        for k, dt in enumerate((-detune, 0, detune)):
            ph = rng.random()
            saw = 2 * ((f * (1 + dt) * t + ph) % 1) - 1
            pan = (k - 1) * 0.6
            s[:, 0] += saw * (1 - pan) * 0.5
            s[:, 1] += saw * (1 + pan) * 0.5
    for c in range(2):
        s[:, c] = signal.sosfilt(sos("lowpass", lp), s[:, c])
    env = np.minimum(1, t / a) * np.clip((d - t) / r, 0, 1)
    return s * env[:, None] / (len(freqs) * 3)


def noise(d, seed=0):
    return np.random.default_rng(seed).standard_normal(int(d * SR))


def kick(d=0.45):
    t = tt(d); f = 45 + 110 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)


def snare():
    t = tt(0.3)
    n = signal.sosfilt(sos("bandpass", [1200, 6000]), noise(0.3, 3)) * np.exp(-t / 0.07)
    return n + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)


def hat(d=0.06, seed=5):
    t = tt(d); return signal.sosfilt(sos("highpass", 7000), noise(d, seed)) * np.exp(-t / 0.015)


def click(f=2500, d=0.015):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / (d / 4))


def whoosh(d=1.0, f0=300, f1=4000, seed=2):
    n = noise(d, seed); t = tt(d)
    out = np.zeros_like(n)
    # sweep a bandpass by blocks
    blocks = 40
    L = len(n) // blocks
    for b in range(blocks):
        fc = f0 * (f1 / f0) ** (b / blocks)
        seg = signal.sosfilt(sos("bandpass", [fc * 0.7, min(fc * 1.4, SR / 2 - 100)]), n[b * L:(b + 1) * L + 2000])
        out[b * L:b * L + len(seg)][: len(out) - b * L] += seg[: len(out) - b * L] * np.hanning(len(seg))[: len(out) - b * L]
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * env


def riser(d=2.0, f0=200, f1=1600):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + signal.sosfilt(sos("highpass", 2000), noise(d, 9)) * 0.25 * (t / d)
    return s * (t / d) ** 2


def sub_boom(d=1.5, f=45):
    t = tt(d); return np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t / 0.08))) * np.exp(-t / 0.5)
