#!/usr/bin/env bash
# mux one look with the shared soundtrack: loudnorm -14 LUFS, AAC at 48 kHz (Instagram rejects >48 kHz)
set -e
L=$1
OUT=../../videos/042-electric-planes$2.mp4
ffmpeg -v error -y -i v042$L.silent.mp4 -i v042.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -shortest -movflags +faststart ${OUT%.mp4}.tmp.mp4
mv ${OUT%.mp4}.tmp.mp4 $OUT
echo $OUT
