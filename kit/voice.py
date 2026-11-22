"""Narrator voice (22 Nov 2026). Standard voice = "A": Kokoro am_michael (US male), 1.1x speed.

The user picked voice A from three samples on 22 Nov 2026. Use it for every voiced video so the
account has one recognisable narrator. Kokoro-82M is Apache-2.0 and runs on the cloud box's CPU
(about 0.8 s of compute per 1 s of speech), so the nightly loop can voice videos on its own.
`bash setup.sh` installs it and downloads the pinned model files to ~/.cache/kokoro.

Typical use inside an audio.py, AFTER the music and sound effects are in the mix:

    sys.path.insert(0, "/home/claude/kit")
    from voice import narrate, measure
    spans = narrate(m, [(0.0, "How one load of laundry became 640 stairs."),
                        (3.1, "Jonas lives on floor four.")])

narrate() ducks everything already in the mix under each line, adds the voice dry and centred,
and raises if a line runs into the next cue or past the end. Plan scene times from the voice:
`measure(text)` (or `python3 kit/voice.py measure "line 1" "line 2"`) gives each line's length.
If the model is missing (setup's download blocked or failed), narrate() prints VOICE MISSING and
returns [] so the video still renders with music only; note "no voice" in posts.csv.

CLI:
    python3 kit/voice.py say "Text to read." out.wav      # quick listen / test
    python3 kit/voice.py measure "Line one." "Line two."  # seconds per line
    python3 kit/voice.py phonemes "A €10 box."            # pronunciation (IPA) after the fixes below
    python3 kit/voice.py check                             # is the voice usable here?
"""
import hashlib
import math
import os
import re
import sys

import numpy as np
from scipy import signal

VOICE = "am_michael"      # voice A
SPEED = 1.1
LANG = "en-us"
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))
MODEL = os.path.join(MODEL_DIR, "kokoro-v1.0.onnx")
VOICES = os.path.join(MODEL_DIR, "voices-v1.0.bin")
CACHE = os.path.expanduser("~/.cache/spare-voice")
SR = 48000                # matches kit.SR

_kokoro = None


def voice_ok():
    """True if the model files are present and kokoro-onnx imports."""
    if not (os.path.isfile(MODEL) and os.path.isfile(VOICES)):
        return False
    try:
        import kokoro_onnx  # noqa: F401
    except ImportError:
        return False
    return True


def _engine():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(MODEL, VOICES)
    return _kokoro


_NUM = r"(\d[\d,]*(?:\.\d+)?)"


def speakable(text):
    """Fix what the voice reads wrong. Kokoro reads "€10" as "euros ten", so currency becomes words.
    Numbers, %, and commas in numbers are read correctly. Spell out acronyms yourself ("E S P 32")."""
    def money(sym_sing, sym_plur):
        def f(m):
            n = m.group(1)
            return f"{n} {sym_sing if n in ('1', '1.00') else sym_plur}"
        return f
    # "a €10 box" -> "a 10 euro box" (an amount used as an adjective stays singular)
    text = re.sub(r"\b([Aa]n?) €\s?" + _NUM, r"\1 \2 euro", text)
    text = re.sub(r"€\s?" + _NUM, money("euro", "euros"), text)
    text = re.sub(r"\$\s?" + _NUM, money("dollar", "dollars"), text)
    text = re.sub(r"£\s?" + _NUM, money("pound", "pounds"), text)
    text = text.replace("€", " euros").replace("&", " and ")
    return re.sub(r"\s+", " ", text).strip()


def say(text, voice=VOICE, speed=SPEED):
    """Mono float32 speech at 48 kHz, peak 1.0, silence trimmed. Cached on disk by text+voice+speed."""
    text = speakable(text)
    key = hashlib.sha1(f"{voice}|{speed}|{LANG}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".npy")
    if os.path.isfile(path):
        return np.load(path)
    samples, sr = _engine().create(text, voice=voice, speed=speed, lang=LANG)
    x = signal.resample_poly(np.asarray(samples, dtype=np.float64), SR, sr)
    x = signal.sosfilt(signal.butter(2, 70, "highpass", fs=SR, output="sos"), x)
    # trim leading/trailing near-silence so cue times mean "the first word starts here"
    env = np.abs(x) > 0.02 * (np.max(np.abs(x)) or 1)
    idx = np.flatnonzero(env)
    if len(idx):
        x = x[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.08 * SR)]
    x = (x / (np.max(np.abs(x)) or 1)).astype(np.float32)
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, x)
    return x


def measure(text, **kw):
    """Seconds the line takes, for planning scene times before rendering the visuals."""
    return len(say(text, **kw)) / SR


def _rms(a):
    return float(np.sqrt(np.mean(a ** 2))) if len(a) else 0.0


def narrate(mix, cues, duck_db=-9.0, lead_db=8.0, gap=0.1, voice=VOICE, speed=SPEED):
    """Add narration to a kit.Mix. Call it LAST (after music + sound effects).

    cues: [(start_seconds, text), ...] in time order. Each line starts exactly at its cue.
    duck_db: how far the music/SFX already in the mix dip under the voice (80 ms in, 250 ms out).
    lead_db: voice loudness over the mix's average level (before ducking).
    Returns [{"t0", "t1", "text"}] (use it to check on-screen text lines up with the voice).
    """
    if not cues:
        return []
    if not voice_ok():
        print("VOICE MISSING: kokoro model not found in", MODEL_DIR, "- rendering without narration "
              "(run `bash setup.sh`; note 'no voice' in posts.csv)", file=sys.stderr)
        return []

    cues = sorted(cues)
    lines = [(t0, text, say(text, voice=voice, speed=speed)) for t0, text in cues]
    spans = []
    for k, (t0, text, x) in enumerate(lines):
        t1 = t0 + len(x) / SR
        nxt = lines[k + 1][0] if k + 1 < len(lines) else mix.dur
        if t1 > nxt - (gap if k + 1 < len(lines) else 0.0):
            what = f"the next cue at {nxt:.2f}s" if k + 1 < len(lines) else f"the end ({mix.dur:.2f}s)"
            raise ValueError(f"voice line {k + 1} \"{text}\" runs {t0:.2f}-{t1:.2f}s, past {what}. "
                             "Shorten the line or move the cue.")
        spans.append({"t0": round(t0, 3), "t1": round(t1, 3), "text": text})

    n = mix.n
    active = mix.buf[: int(mix.dur * SR)]
    loud = np.abs(active).max(axis=1) > 1e-4
    ref = _rms(active[loud]) if loud.any() else 0.1

    # ducking envelope over everything already in the mix
    g = np.zeros(n)
    for s in spans:
        g[int(s["t0"] * SR): min(n, int(s["t1"] * SR))] = 1.0
    att, rel = int(0.08 * SR), int(0.25 * SR)
    env = np.zeros(n)
    level = 0.0
    a_step, r_step = 1.0 / att, 1.0 / rel
    for i in range(n):  # simple attack/release follower
        level = min(1.0, level + a_step) if g[i] > level else max(g[i], level - r_step)
        env[i] = level
    # look-ahead so the dip has started when the first word lands
    env = np.concatenate([env[att:], np.zeros(att)])
    env = np.maximum(env, g)
    gain = 1.0 - env * (1.0 - 10 ** (duck_db / 20))
    mix.buf *= gain[:, None]
    mix.verb *= gain[:, None]

    target = ref * 10 ** (lead_db / 20)
    for (t0, _, x), s in zip(lines, spans):
        mix.add(t0, x * (target / (_rms(x) or 1)), pan=0.0)
    return spans


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        print("voice ok" if voice_ok() else f"VOICE MISSING ({MODEL_DIR})")
        sys.exit(0 if voice_ok() else 1)
    if cmd == "measure":
        for line in sys.argv[2:]:
            print(f"{measure(line):6.2f} s  {line}")
    elif cmd == "phonemes":  # how each line will be pronounced (IPA), for checking odd words without listening
        for line in sys.argv[2:]:
            print(f"{speakable(line)}\n  -> {_engine().tokenizer.phonemize(speakable(line), LANG)}")
    elif cmd == "say":
        from scipy.io import wavfile
        x = say(sys.argv[2])
        wavfile.write(sys.argv[3], SR, (x * 0.89 * 32767).astype(np.int16))
        print(f"{sys.argv[3]}: {len(x) / SR:.2f} s")
    else:
        print(__doc__)
