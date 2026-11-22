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

# Narrator voice A (kit/voice.py): Kokoro-82M (Apache-2.0) in ONNX format, ~350 MB, approved by the user 22 Nov 2026.
# Files are pinned by SHA256. Not fatal: if the download is blocked or fails, videos render without narration.
KOKORO_DIR="${KOKORO_DIR:-$HOME/.cache/kokoro}"
KOKORO_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
voice_setup() {
  pip install -q --break-system-packages "kokoro-onnx==0.6.1" soundfile 2>/dev/null || return 1
  mkdir -p "$KOKORO_DIR"
  local f sum
  for f in "kokoro-v1.0.onnx 7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5" \
           "voices-v1.0.bin bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"; do
    set -- $f
    if ! echo "$2  $KOKORO_DIR/$1" | sha256sum -c --status 2>/dev/null; then
      curl -sSL --fail -o "$KOKORO_DIR/$1.part" "$KOKORO_URL/$1" || return 1
      echo "$2  $KOKORO_DIR/$1.part" | sha256sum -c --status || { rm -f "$KOKORO_DIR/$1.part"; echo "voice: checksum mismatch for $1"; return 1; }
      mv "$KOKORO_DIR/$1.part" "$KOKORO_DIR/$1"
    fi
  done
}
if voice_setup; then echo "voice ok (A: am_michael 1.1x)"; else echo "VOICE MISSING: videos will render without narration"; fi

which ffmpeg >/dev/null && echo "setup ok"
