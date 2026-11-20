#!/usr/bin/env bash
# Usage: bash finish.sh <n>   (out/part<n>_silent.mp4 + out/part<n>.wav -> out/part<n>.mp4)
# Remotion writes full-range BT.601; convert to standard range like the rest of the account, mux at 48 kHz, -14 LUFS.
set -e
n=$1
ffmpeg -v error -y -i out/part${n}_silent.mp4 -vf "scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p" \
  -c:v libx264 -crf 17 -preset slow -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv out/part${n}_tv.mp4
ffmpeg -v error -y -i out/part${n}_tv.mp4 -i out/part${n}.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -shortest -movflags +faststart out/part${n}.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,color_range,sample_rate:format=duration -of compact out/part${n}.mp4
