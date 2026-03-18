# Skill: FLUXION Video Creator — Enterprise Grade

> Programmatic demo video creation from screenshots + Italian voiceover.
> Zero manual editing. ffmpeg + Edge-TTS pipeline.

## Purpose

Create a professional product demo video for FLUXION:
- 2-3 minute duration
- Italian voiceover (Edge-TTS IsabellaNeural)
- Screenshot slideshow with smooth transitions
- Background music (royalty-free)
- Subtitles (SRT) auto-generated
- Output: MP4 1080p ready for YouTube/Vimeo

## Architecture

```
Screenshots (PNG 1920x1080)
    ↓
Edge-TTS IsabellaNeural → voiceover WAV + SRT subtitles
    ↓
ffmpeg: combine images + audio + transitions + subtitles → MP4
    ↓
Upload to YouTube/Vimeo (manual or API)
```

## Tools Available

| Tool | Location | Purpose |
|------|----------|---------|
| ffmpeg 8.0 | MacBook `/usr/local/bin/ffmpeg` | Video assembly |
| Edge-TTS | MacBook `pip install edge-tts` | Italian voiceover |
| Playwright | MacBook `e2e-tests/` | Screenshot capture |

## Procedure

### Step 1: Script (Italian voiceover text)

Write narration script in Italian, one paragraph per screen:

```
DASHBOARD: "Ecco la tua dashboard. In un colpo d'occhio vedi gli appuntamenti
di oggi, il fatturato e le attività urgenti. Tutto quello che ti serve, subito."

CALENDARIO: "Il calendario ti mostra tutti gli appuntamenti. Puoi spostarli
con un click, e Sara li gestisce automaticamente."

[... per ogni schermata]
```

Rules for script:
- Linguaggio SEMPLICE, per titolari PMI
- MAI gergo tecnico
- Frasi brevi (max 20 parole)
- Tono: amichevole, professionale, rassicurante
- Durata target: 10-15 secondi per schermata

### Step 2: Generate Voiceover

```bash
# Generate per-screen audio files
edge-tts --voice it-IT-IsabellaNeural \
  --text "Ecco la tua dashboard..." \
  --write-media landing/video/01-dashboard.mp3 \
  --write-subtitles landing/video/01-dashboard.vtt

# Repeat for each screen
```

### Step 3: Measure Audio Duration

```bash
# Get duration of each audio file to sync with images
ffprobe -v quiet -show_entries format=duration \
  -of csv=p=0 landing/video/01-dashboard.mp3
```

### Step 4: Create Slideshow with Transitions

```bash
# Create video from images with crossfade transitions
ffmpeg -loop 1 -t $DURATION1 -i screenshots/01-dashboard.png \
       -loop 1 -t $DURATION2 -i screenshots/02-calendario.png \
       [...per ogni screen] \
       -filter_complex "[0:v]fade=t=out:st=$FADE1:d=0.5[v0]; \
                        [1:v]fade=t=in:st=0:d=0.5,fade=t=out:st=$FADE2:d=0.5[v1]; \
                        [...] \
                        [v0][v1]...[vN]concat=n=N:v=1:a=0[outv]" \
       -map "[outv]" -tune stillimage -pix_fmt yuv420p \
       landing/video/slideshow.mp4
```

### Step 5: Merge Audio + Video

```bash
# Concatenate all audio files
ffmpeg -i "concat:01.mp3|02.mp3|..." -c copy landing/video/voiceover.mp3

# Normalize audio to broadcast standard
ffmpeg -i voiceover.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" voiceover-norm.mp3

# Merge video + audio
ffmpeg -i slideshow.mp4 -i voiceover-norm.mp3 \
       -c:v copy -c:a aac -b:a 192k \
       -shortest landing/video/fluxion-demo.mp4
```

### Step 6: Add Subtitles (Burned-in)

```bash
ffmpeg -i fluxion-demo.mp4 \
       -vf "subtitles=subtitles.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF'" \
       landing/video/fluxion-demo-subtitled.mp4
```

### Step 7: Create Thumbnail

```bash
# Extract frame from dashboard section as video thumbnail
ffmpeg -i fluxion-demo.mp4 -ss 00:00:02 -frames:v 1 \
       landing/video/thumbnail.png
```

## Output Files

```
landing/video/
  fluxion-demo.mp4              # Final video (no subs)
  fluxion-demo-subtitled.mp4    # Final video (burned-in subs)
  thumbnail.png                 # YouTube thumbnail
  voiceover.mp3                 # Full voiceover audio
  subtitles.srt                 # Subtitle file
  script.md                     # Narration script
  segments/                     # Per-screen audio + video
```

## Quality Standards

- Resolution: 1920x1080 (1080p)
- Frame rate: 30fps
- Audio: AAC 192kbps, normalized to -16 LUFS
- Duration: 2-3 minutes
- File size target: <100MB
- Transitions: 0.5s crossfade between screens

## Upload

### YouTube
```bash
# Using yt-dlp or YouTube Data API v3
# Requires OAuth2 credentials (one-time setup)
# Title: "FLUXION — Il gestionale per la tua attività | Demo"
# Description: benefit-oriented, Italian
# Tags: gestionale, PMI, Italia, prenotazioni, fatture
```

### Vimeo
```bash
# Vimeo API or manual upload
# Privacy: unlisted or public
# Embed on landing page
```

## Trigger

- User asks for "video", "demo video", "YouTube", "Vimeo"
- After screenshot capture completes
- User invokes `/video-creator`

## Safety

- Runs entirely on MacBook
- Does NOT use iMac (Edge-TTS available on MacBook via pip)
- All generated content in `landing/video/` directory
