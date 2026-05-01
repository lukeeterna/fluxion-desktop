---
name: ffmpeg concat demuxer audio duration bug
description: When concat demuxer concatenates MP4 files that each contain MP3→AAC audio, the total audio duration in the output can be ~1.84x longer than expected, while video duration is correct.
type: feedback
---

Using `ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac output.mp4` on files where audio was originally MP3 transcoded to AAC during mux step results in audio stream duration = ~1.84x the sum of individual durations. Video stream is correct.

**Why:** The concat demuxer doesn't correctly reset PTS for audio when the source files have video/audio stream duration mismatches (due to MP3 VBR headers vs AAC packet timing). The result is a valid but wrong audio stream that plays silence after the content ends.

**How to apply:** Never use concat demuxer on pre-muxed clips. Instead:
1. Concat VIDEO streams only (from -an video-only clips)
2. Concat AUDIO streams only (from WAV intermediates) 
3. Mux combined video + combined audio in a final step
4. Use WAV (pcm_s16le) for all intermediate audio concatenation, convert to AAC only at final mux

Scripts at: `/tmp/fluxion-video/scripts/assemble_v2_fixed.py` (working reference)
