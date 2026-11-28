"""Narrator voice. Standard since 22 Nov 2026 (evening): "A+" (A-plus), the user's pick from 3 samples.

A+ = Chatterbox-Turbo (Resemble AI, MIT licence, official ONNX export, 8-bit language model) speaking
with voice A's timbre. The timbre comes from `voice_a_ref.wav`: 10.9 s of synthetic speech made with
Kokoro `am_michael` (the old voice A), so no real person is cloned. Chatterbox gives the delivery the
life the user missed in Kokoro ("very lifeless").

Runs on the cloud box's CPU: about 13-15 s of compute per 1 s of speech (2 cores), so a video's
narration takes 3-6 min. Needs huggingface.co + *.hf.co in the allowed domains (the user added them
on 22 Nov); `bash setup.sh` downloads the pinned model files (~1.8 GB) to ~/.cache.

Typical use inside an audio.py, AFTER the music and sound effects are in the mix:

    sys.path.insert(0, "/home/claude/kit")
    from voice import narrate, place
    cues = place([(0.0, "Find the missing pixel."), (3.0, "He fell out.")], end=mix.dur)
    spans = narrate(m, cues)

- Lines are generated with a fixed seed per text, cached on disk, and checked with Whisper: if the
  transcript doesn't match the words, the next seed is tried (up to 5). Takes are reproducible.
- `place()` moves a line later (never earlier) when the previous one would still be talking, and
  raises if the last line can't end before the video does. Time the visuals from `measure()`.
- Chatterbox-Turbo tags work inside lines: [gasp] [chuckle] [laugh] [sigh] [groan] [sniff]
  [clear throat]. Use them sparingly, at most one per line; they aren't spoken.
- If the model is missing, narrate() prints VOICE MISSING and the video renders with music only.

CLI:
    python3 kit/voice.py say "Text to read." out.wav     # quick test
    python3 kit/voice.py measure "Line one." "Line two." # seconds per line
    python3 kit/voice.py check "Line one." ...           # what Whisper hears for each line
    python3 kit/voice.py ok                              # is the voice usable here?
"""
import difflib
import hashlib
import math
import os
import re
import sys
import zlib

import numpy as np
from scipy import signal

VOICE = "A+"
SR = 48000                                  # matches kit.SR
CACHE = os.path.expanduser("~/.cache/spare-voice")
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "voice_a_ref.wav")

CB_ID = "ResembleAI/chatterbox-turbo-ONNX"
CB_REV = "d21799bd0354adb85e348b8a0442a8405110a2cf"          # pinned 22 Nov 2026
CB_DIR = os.path.expanduser("~/.cache/chatterbox-turbo-onnx")  # plain files (onnxruntime refuses
CB_SR = 24000                                                  # external data behind HF symlinks)
CB_FILES = dict(lm="language_model_quantized", embed="embed_tokens_quantized",
                enc="speech_encoder", dec="conditional_decoder")
START, STOP, SILENCE = 6561, 6562, 4299
KV_HEADS, HEAD_DIM = 16, 64
ASR_ID = "Systran/faster-whisper-base.en"
ASR_REV = "3d3d5dee26484f91867d81cb899cfcf72b96be6c"

_cb = None
_asr = None


# ------------------------------------------------------------------ setup / availability
def download():
    """Fetch the pinned model files (setup.sh calls this). Returns True on success."""
    from huggingface_hub import hf_hub_download, snapshot_download
    for name in CB_FILES.values():
        for suf in (".onnx", ".onnx_data"):
            hf_hub_download(CB_ID, subfolder="onnx", filename=name + suf, revision=CB_REV, local_dir=CB_DIR)
    for f in ("tokenizer.json", "tokenizer_config.json", "config.json"):
        hf_hub_download(CB_ID, f, revision=CB_REV, local_dir=CB_DIR)
    snapshot_download(ASR_ID, revision=ASR_REV)
    return voice_ok()


def voice_ok():
    if not os.path.isfile(REF):
        return False
    for name in CB_FILES.values():
        if not (os.path.isfile(os.path.join(CB_DIR, "onnx", name + ".onnx"))
                and os.path.isfile(os.path.join(CB_DIR, "onnx", name + ".onnx_data"))):
            return False
    try:
        import onnxruntime, librosa, transformers  # noqa: F401
    except ImportError:
        return False
    return True


# ------------------------------------------------------------------ text
_NUM = r"(\d[\d,]*(?:\.\d+)?)"


def speakable(text):
    """Currency symbols become words ("€10" -> "10 euros"); spell out acronyms yourself ("E S P 32")."""
    def money(sing, plur):
        return lambda m: f"{m.group(1)} {sing if m.group(1) in ('1', '1.00') else plur}"
    text = re.sub(r"\b([Aa]n?) €\s?" + _NUM, r"\1 \2 euro", text)
    text = re.sub(r"€\s?" + _NUM, money("euro", "euros"), text)
    text = re.sub(r"\$\s?" + _NUM, money("dollar", "dollars"), text)
    text = re.sub(r"£\s?" + _NUM, money("pound", "pounds"), text)
    text = text.replace("€", " euros").replace("&", " and ")
    return re.sub(r"\s+", " ", text).strip()


_ALIAS = {"kilometers": "km", "kilometer": "km", "kilometres": "km", "kilometre": "km", "tonnes": "tons"}


def _words(s):
    # Whisper writes "km", "90%", "$6", "tons" for what A+ says as "kilometers", "90 percent", "six dollars",
    # "tonnes": compare them as the same words, or every such line burns 5 retakes (~6 min) for nothing (28 Nov).
    s = re.sub(r"\$\s?(\d+(?:\.\d+)?)", r"\1 dollars", s).replace("%", " percent")
    s = re.sub(r"\[[a-z ]+\]", " ", s.lower())
    s = re.sub(r"\b(\d+)\b", lambda m: _NUMWORDS.get(m.group(1), m.group(1)), s)
    return [_ALIAS.get(w, w) for w in re.sub(r"[^a-z0-9 ]", " ", s).split()]


_NUMWORDS = {str(i): w for i, w in enumerate("zero one two three four five six seven eight nine ten".split())}


# ------------------------------------------------------------------ Chatterbox-Turbo (ONNX, CPU)
class _Turbo:
    def __init__(self, threads=None):
        import onnxruntime as ort
        import librosa
        from transformers import AutoTokenizer
        from transformers.utils import logging as tlog
        tlog.set_verbosity_error()
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads or os.cpu_count() or 2
        self.s = {k: ort.InferenceSession(os.path.join(CB_DIR, "onnx", v + ".onnx"), so,
                                          providers=["CPUExecutionProvider"]) for k, v in CB_FILES.items()}
        self.tok = AutoTokenizer.from_pretrained(CB_DIR)
        ref, _ = librosa.load(REF, sr=CB_SR)
        self.spk = self.s["enc"].run(None, {"audio_values": ref[None, :].astype(np.float32)})

    def say(self, text, seed, temperature=0.8, top_k=1000, top_p=0.95, rep=1.2, max_new=800):
        """sampled decoding (like the PyTorch package's defaults); greedy decoding sounds flat"""
        rng = np.random.default_rng(seed)
        cond_emb, prompt_tok, spk_emb, spk_feat = self.spk
        ids = self.tok(text, return_tensors="np")["input_ids"].astype(np.int64)
        lm = self.s["lm"]
        x = np.concatenate((cond_emb, self.s["embed"].run(None, {"input_ids": ids})[0]), axis=1)
        b, n, _ = x.shape
        past = {i.name: np.zeros([b, KV_HEADS, 0, HEAD_DIM],
                                 dtype=np.float16 if i.type == "tensor(float16)" else np.float32)
                for i in lm.get_inputs() if "past_key_values" in i.name}
        mask = np.ones((b, n), dtype=np.int64)
        pos = np.arange(n, dtype=np.int64)[None, :]
        gen = [START]
        for _ in range(max_new):
            logits, *present = lm.run(None, dict(inputs_embeds=x, attention_mask=mask, position_ids=pos, **past))
            lg = logits[0, -1, :].astype(np.float64)
            prev = np.array(sorted(set(gen)))
            sc = lg[prev]
            lg[prev] = np.where(sc < 0, sc * rep, sc / rep)
            lg /= temperature
            kth = np.partition(lg, -top_k)[-top_k]
            lg[lg < kth] = -np.inf
            p = np.exp(lg - lg.max()); p /= p.sum()
            order = np.argsort(-p)
            keep = np.cumsum(p[order]) <= top_p
            keep[0] = True
            q = np.zeros_like(p); q[order[keep]] = p[order[keep]]; q /= q.sum()
            nxt = int(rng.choice(q.size, p=q))
            gen.append(nxt)
            if nxt == STOP:
                break
            x = self.s["embed"].run(None, {"input_ids": np.array([[nxt]], dtype=np.int64)})[0]
            mask = np.concatenate([mask, np.ones((b, 1), dtype=np.int64)], axis=1)
            pos = pos[:, -1:] + 1
            for j, k in enumerate(past):
                past[k] = present[j]
        if gen[-1] != STOP:
            raise RuntimeError(f"voice: no stop token for {text!r} (seed {seed})")
        toks = np.concatenate([prompt_tok, np.array([gen[1:-1]], dtype=np.int64),
                               np.full((1, 3), SILENCE, dtype=np.int64)], axis=1)
        return self.s["dec"].run(None, dict(speech_tokens=toks, speaker_embeddings=spk_emb,
                                            speaker_features=spk_feat))[0].squeeze(0).astype(np.float32)


def _engine():
    global _cb
    if _cb is None:
        _cb = _Turbo()
    return _cb


def hear(x, sr=SR):
    """What Whisper (base.en) hears in a clip."""
    global _asr
    from faster_whisper import WhisperModel
    import librosa
    if _asr is None:
        _asr = WhisperModel(ASR_ID, device="cpu", compute_type="int8", revision=ASR_REV)
    a = librosa.resample(np.asarray(x, dtype=np.float32), orig_sr=sr, target_sr=16000)
    return " ".join(s.text for s in _asr.transcribe(a, language="en", beam_size=5)[0]).strip()


def _trim(x, sr):
    env = np.abs(x) > 0.02 * (np.max(np.abs(x)) or 1)
    idx = np.flatnonzero(env)
    return x[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.08 * sr)] if len(idx) else x


def say(text, check=True, tries=5):
    """Mono float32 speech at 48 kHz, peak 1.0, silence trimmed. Cached on disk.
    With check=True a take is only accepted when Whisper hears exactly the words of the line."""
    text = speakable(text)
    base = zlib.crc32(text.encode()) % 2 ** 31
    key = hashlib.sha1(f"{VOICE}|{CB_REV}|{text}|{check}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".npy")
    if os.path.isfile(path):
        return np.load(path)
    want = _words(text)
    best = None
    for k in range(tries):
        try:
            w = _engine().say(text, seed=base + k)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            continue
        x = signal.resample_poly(w.astype(np.float64), SR, CB_SR)
        x = signal.sosfilt(signal.butter(2, 70, "highpass", fs=SR, output="sos"), x)
        x = _trim(x, SR)
        x = (x / (np.max(np.abs(x)) or 1)).astype(np.float32)
        if not check:
            best = x
            break
        heard = hear(x)
        r = difflib.SequenceMatcher(None, want, _words(heard)).ratio()
        if best is None or r > best[0]:
            best = (r, x, heard)
        if r == 1.0:
            break
        print(f"voice: retake {k + 1} for {text!r}: heard {heard!r}", file=sys.stderr)
    if best is None:
        raise RuntimeError(f"voice: could not generate {text!r}")
    if check:
        r, x, heard = best
        if r < 1.0:
            print(f"voice WARNING: best take for {text!r} is heard as {heard!r} ({r:.2f})", file=sys.stderr)
    else:
        x = best
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, x)
    return x


def measure(text):
    """Seconds the line takes, for planning scene times before rendering the visuals."""
    return len(say(text)) / SR


def place(cues, end=None, gap=0.1, max_late=None):
    """cues [(wanted_start, text), ...] -> [(start, text), ...]: each line starts at its wanted time,
    or just after the previous line ends (+gap) if that one is still talking. Raises if the last line
    runs past `end`, or if a line would start more than `max_late` seconds after its wanted time."""
    out, t_free = [], -1e9
    for t, text in sorted(cues):
        s = max(t, math.ceil(t_free * 1000 + 1) / 1000)       # round up: narrate() checks the gap exactly
        if max_late is not None and s - t > max_late:
            raise ValueError(f"voice: {text!r} would start {s - t:.2f}s late (max {max_late}s). Shorten a line.")
        d = measure(text)
        out.append((s, text))
        t_free = s + d + gap
    if end is not None and t_free - gap > end:
        raise ValueError(f"voice: the last line ends at {t_free - gap:.2f}s, after the end ({end:.2f}s).")
    return out


# ------------------------------------------------------------------ mixing
def _rms(a):
    return float(np.sqrt(np.mean(a ** 2))) if len(a) else 0.0


def narrate(mix, cues, duck_db=-9.0, lead_db=8.0, gap=0.1):
    """Add narration to a kit.Mix. Call it LAST (after music + sound effects).

    cues: [(start_seconds, text), ...] in time order (use place() to resolve overlaps).
    duck_db: how far the music/SFX already in the mix dip under the voice (80 ms in, 250 ms out).
    lead_db: voice loudness over the mix's average level (before ducking).
    Returns [{"t0", "t1", "text"}].
    """
    if not cues:
        return []
    if not voice_ok():
        print("VOICE MISSING: Chatterbox model or reference not found (run `bash setup.sh`; it needs "
              "huggingface.co and *.hf.co in the allowed domains). Rendering without narration; "
              "note 'no voice' in posts.csv", file=sys.stderr)
        return []
    cues = sorted(cues)
    lines = [(t0, text, say(text)) for t0, text in cues]
    spans = []
    for k, (t0, text, x) in enumerate(lines):
        t1 = t0 + len(x) / SR
        nxt = lines[k + 1][0] if k + 1 < len(lines) else mix.dur
        if t1 > nxt - (gap if k + 1 < len(lines) else 0.0):
            what = f"the next cue at {nxt:.2f}s" if k + 1 < len(lines) else f"the end ({mix.dur:.2f}s)"
            raise ValueError(f"voice line {k + 1} \"{text}\" runs {t0:.2f}-{t1:.2f}s, past {what}. "
                             "Shorten the line or move the cue (see place()).")
        spans.append({"t0": round(t0, 3), "t1": round(t1, 3), "text": text})

    n = mix.n
    active = mix.buf[: int(mix.dur * SR)]
    loud = np.abs(active).max(axis=1) > 1e-4
    ref = _rms(active[loud]) if loud.any() else 0.1
    g = np.zeros(n)
    for s in spans:
        g[int(s["t0"] * SR): min(n, int(s["t1"] * SR))] = 1.0
    att, rel = int(0.08 * SR), int(0.25 * SR)
    env = np.zeros(n)
    level = 0.0
    a_step, r_step = 1.0 / att, 1.0 / rel
    for i in range(n):
        level = min(1.0, level + a_step) if g[i] > level else max(g[i], level - r_step)
        env[i] = level
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
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ok"
    if cmd == "ok":
        print("voice ok (A+)" if voice_ok() else "VOICE MISSING")
        sys.exit(0 if voice_ok() else 1)
    if cmd == "download":
        sys.exit(0 if download() else 1)
    if cmd == "measure":
        for line in sys.argv[2:]:
            print(f"{measure(line):6.2f} s  {line}")
    elif cmd == "check":
        for line in sys.argv[2:]:
            print(f"{line!r} -> heard {hear(say(line))!r}")
    elif cmd == "say":
        from scipy.io import wavfile
        x = say(sys.argv[2])
        wavfile.write(sys.argv[3], SR, (x * 0.89 * 32767).astype(np.int16))
        print(f"{sys.argv[3]}: {len(x) / SR:.2f} s")
    else:
        print(__doc__)
