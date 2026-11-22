#!/usr/bin/env bash
# One-time setup for a fresh workspace. Run from the repo root: bash setup.sh
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
pip install -q --break-system-packages shapely skia-python fonttools scipy numpy pillow matplotlib 2>/dev/null || true
# renderers import the kit from /home/claude/kit
ln -sfn "$REPO/kit" /home/claude/kit
# REN scenes expect their fonts here
mkdir -p /home/claude/apoc/fonts
cp "$REPO/kit/fonts/PixelifySans-Bold.ttf" /home/claude/apoc/fonts/pixelify-sans-latin-700.ttf
cp "$REPO/kit/fonts/Silkscreen-Bold.ttf" /home/claude/apoc/fonts/silkscreen-latin-700.ttf
cp "$REPO/kit/fonts/Silkscreen.ttf" /home/claude/apoc/fonts/silkscreen-latin-400.ttf

# Narrator voice A+ (kit/voice.py; user's pick on 22 Nov 2026): Chatterbox-Turbo (Resemble AI, MIT) as ONNX,
# speaking with voice A's synthetic timbre (kit/voice_a_ref.wav). Model files (~1.8 GB) + Whisper base.en
# (word check) come from Hugging Face at pinned revisions; huggingface.co and *.hf.co must be in the
# allowed domains (added by the user on 22 Nov). Not fatal: without them videos render without narration.
voice_setup() {
  pip install -q --break-system-packages "onnxruntime==1.29.0" "transformers==5.24.0" "librosa==1.0.1" \
    "huggingface_hub==2.4.0" "faster-whisper==1.2.1" soundfile 2>/dev/null || return 1
  HF_HUB_DISABLE_PROGRESS_BARS=1 python3 "$REPO/kit/voice.py" download >/dev/null 2>&1
}
if voice_setup; then echo "voice ok (A+: Chatterbox-Turbo, voice A timbre)"; else echo "VOICE MISSING: videos will render without narration"; fi

which ffmpeg >/dev/null && echo "setup ok"
