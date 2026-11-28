"""Voice A+ takes for every line (cached by kit/voice.py) -> durations + Whisper word times -> words.json."""
import json, os, sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
import vo  # noqa: F401  (tight takes)
import voice
from voice import SR
say = voice.say
from timing import LINES

HERE = os.path.dirname(os.path.abspath(__file__))
out = {}
for k, text in LINES:
    x = say(text)
    voice.hear(x[:SR])                                   # loads voice._asr
    import librosa
    a = librosa.resample(np.asarray(x, np.float32), orig_sr=SR, target_sr=16000)
    segs, _ = voice._asr.transcribe(a, language="en", beam_size=5, word_timestamps=True)
    words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
    out[k] = {"dur": round(len(x) / SR, 3), "words": words}
    print(f"{k:9s} {len(x) / SR:5.2f}s  " + " ".join(f"{w}@{s:.2f}" for w, s, _ in words), flush=True)
json.dump(out, open(os.path.join(HERE, "words.json"), "w"), indent=1)
