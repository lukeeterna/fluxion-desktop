---
name: FLUXION tutorial install v2 pipeline
description: Production notes for the 21-scene macOS+Windows installation tutorial video generated 2026-05-01
type: project
---

Video tutorial v2 produced 2026-05-01 — dual OS (macOS + Windows) installation guide.

**Output:**
- `/Volumes/MontereyT7/FLUXION/landing/assets/video/fluxion-tutorial-install.mp4` — 1920x1080 h264 30fps aac 7.7MB 4:21
- `/Volumes/MontereyT7/FLUXION/landing/assets/video/fluxion-tutorial-install.srt` — 68 cues Italian
- v1 backup: `fluxion-tutorial-install-v1.mp4`

**Why:** v1 covered macOS only, founder required v2 covering both OS.

**Production scripts (all in /tmp/fluxion-video/scripts/):**
- `generate_slides_v2.py` — Pillow 21 slides 1920x1080
- `generate_voiceover_v2.py` — Edge-TTS it-IT-IsabellaNeural rate=-5% → 21 MP3
- `assemble_v2_fixed.py` — correct concat approach (video-only + audio-only then mux)

**Font:** HelveticaNeue.ttc (macOS system, index 0=regular index 1=bold) — no Inter available
**Palette:** bg #0f172a, cyan #06b6d4 (macOS), blue #0078D4 (Windows), yellow #fbbf24, text #e2e8f0
**Slide durations:** TTS actual duration + 0.5s padding, minimum 4.0s per scene
**Total TTS:** 247.5s, total video: 261.7s (21 clips)
**Background music:** `landing/assets/background-music.mp3` — was NOT present on build machine; video produced without music
**No zoompan** — confirmed broken on this ffmpeg 8.0 build; used scale+fade instead

**How to apply:** For any future FLUXION video, reuse these scripts as base. Background music path needs verification before production.
