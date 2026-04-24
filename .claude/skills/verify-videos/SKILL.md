---
name: verify-videos
description: QA frame-level per video generati da video-factory. Attiva quando l'utente menziona "verifica video", "controlla video", "freeze detect", "QA video", o ha appena generato/rigenerato un file in video-factory/output/. Esegue freezedetect + mpdecimate + blackdetect + silencedetect + idet e riporta problemi strutturati con exit code != 0 se trova freeze/black/silence anomali.
---

# Skill: /verify-videos — QA Video Frame-Level

> Controllo automatico qualità video prima di pubblicazione/embedding.
> Zero video con freeze frame, pattern duplicati, buchi audio o letterbox improprio devono passare in produzione.

## Quando si attiva

- Utente dice: "verifica video", "controlla video", "QA video", "check freeze", "frame-level video".
- Subito dopo la generazione di un file in `video-factory/output/**/*.mp4` (es. `landing_v4_16x9.mp4`, `parrucchiere_video_9x16.mp4`).
- Prima di upload YouTube/Vimeo/CF R2.
- Dopo ogni modifica a `video-factory/assemble_*.py`.

## Controlli eseguiti

| Filtro ffmpeg | Cosa cattura | Soglia di fail |
|---------------|--------------|----------------|
| `freezedetect` | Frame clonati (stream_loop degeneri, tpad=clone, encoder bug) | 1+ evento ≥ 0.5s |
| `mpdecimate` | Duplicati back-to-back (pad_video_to_audio, concat glitch) | > 2% frame duplicati |
| `blackdetect` | Schermate nere non intenzionali | 1+ evento ≥ 0.3s non a fine video |
| `silencedetect` | Buchi audio (bug music-mix, segmenti muti inaspettati) | 1+ evento ≥ 1.0s |
| `idet` | Interlacing anomalo (encoder misconfig) | BFF/TFF count > 5% |

Metadata `ffprobe` sempre stampati: durata, risoluzione, fps, codec, bitrate, streams.

## Come si usa

### Via Bash diretto
```bash
.claude/skills/verify-videos/verify-videos.sh <path_video>
# Esempio locale
.claude/skills/verify-videos/verify-videos.sh video-factory/output/landing_v4/landing_v4_16x9.mp4
# Esempio via SSH iMac
ssh imac 'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"; /Volumes/MacSSD\ -\ Dati/fluxion/.claude/skills/verify-videos/verify-videos.sh /Volumes/MacSSD\ -\ Dati/fluxion/video-factory/output/landing_v4/landing_v4_16x9.mp4'
```

### Exit code
- `0` → tutti i controlli passati, video pronto alla pubblicazione
- `1` → trovati problemi (dettagli stampati su stdout/stderr)
- `2` → file mancante, ffmpeg/ffprobe non trovati, errore di invocazione

## Output atteso (esempio)

```
=== VERIFY VIDEOS — FRAME-LEVEL QA ===
File: landing_v4_16x9.mp4

[METADATA]
  duration=143.21  width=1920  height=1080  fps=30.0  codec=h264  bitrate=3521k
  audio: aac 48000Hz stereo

[FREEZEDETECT]   PASS  (0 events)
[MPDECIMATE]     PASS  (1.2% duplicates, under 2% threshold)
[BLACKDETECT]    PASS  (0 events)
[SILENCEDETECT]  PASS  (0 events ≥ 1.0s)
[IDET]           PASS  (progressive_count=4296, interlaced ~0%)

✅ VIDEO READY (exit 0)
```

## Criteri enterprise (non negoziabili)

1. **Zero freeze** in landing/marketing video — ogni freeze è root cause di perdita fiducia utente.
2. **Duplicates ≤ 2%** — oltre significa pad_video_to_audio bacato o concat glitch.
3. **No black intermedi ≥ 0.3s** — fadeout finale OK, interruzioni non OK.
4. **No silence ≥ 1s** dove dovrebbe esserci voiceover o musica (segmenti di intro/outro esclusi).

## Integrazione Regola Zero FLUXION

Dopo ogni `assemble_landing_v4.py`, `assemble_all.py`, `assembly.py` → chiamare `/verify-videos` PRIMA di commit o upload. Se exit ≠ 0, bloccare la pipeline e investigare.

## Related
- `.claude/rules/e2e-testing.md` — test obbligatori per ogni modifica
- `video-factory/CLAUDE.md` — pipeline video factory
- `memory/project_enterprise_delta.md` — contratto qualità S167
