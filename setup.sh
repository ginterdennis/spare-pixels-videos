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
which ffmpeg >/dev/null && echo "setup ok"
