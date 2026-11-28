"""Voice A+ takes with long inner pauses shortened (Chatterbox leaves up to ~1.9 s of silence mid-line).
Import this BEFORE using voice.say/measure/narrate: it patches voice.say so every caller gets tight takes."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import voice

SR = voice.SR
_orig_say = voice.say
KEEP = {"Not even AI. Yet.": 0.45}       # dramatic beat before "Yet." stays a little longer
MAX_PAUSE = 0.24
TEMPO = 1.10                              # A+ reads slowly; 10 % faster, pitch kept (ffmpeg atempo)


def tighten(x, keep=MAX_PAUSE, thr=0.035):
    hop = int(0.01 * SR)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1))
    silent = rms < thr * (np.max(np.abs(x)) or 1)
    out, i, last = [], 0, 0
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            run = (j - i) * hop
            if i > 0 and j < n and run > keep * SR:
                cut0 = i * hop + int(keep * SR / 2)
                cut1 = j * hop - int(keep * SR / 2)
                seg = x[last:cut0].copy()
                fade = int(0.02 * SR)
                seg[-fade:] *= np.linspace(1, 0, fade)
                out.append(seg)
                last = cut1
                nxt = x[cut1:cut1 + fade]
                x = x.copy(); x[cut1:cut1 + fade] = nxt * np.linspace(0, 1, len(nxt))
            i = j
        else:
            i += 1
    out.append(x[last:])
    return np.concatenate(out).astype(np.float32)


def speed(x, tempo=TEMPO):
    import subprocess
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"atempo={tempo}", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=np.asarray(x, np.float32).tobytes(), capture_output=True, check=True)
    y = np.frombuffer(r.stdout, np.float32).copy()
    return y / (np.max(np.abs(y)) or 1)


_cache = {}


def say(text, check=True, tries=5):
    if text not in _cache:
        _cache[text] = speed(tighten(_orig_say(text, check=check, tries=tries), keep=KEEP.get(text, MAX_PAUSE) * TEMPO))
    return _cache[text]


voice.say = say
