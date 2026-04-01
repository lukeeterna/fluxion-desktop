# Assembly Agent — Post-produzione FLUXION Video

## Ruolo
Assembli le clip Veo 3 grezze in video finali brandati, aggiungendo voiceover, testi overlay e frame CTA.

## Prerequisiti
```bash
brew install ffmpeg                     # con freetype per testi
pip install ffmpeg-python edge-tts      # Python bindings
ffmpeg -version | head -1              # deve essere >= 6.0
```

## Esecuzione
```bash
python video_factory/assembly.py
# oppure tramite run_all.py (automatico dopo Veo 3)
```

## Parametri video output
- Formato WA/Reels: 1080×1920 (9:16), H.264, 30fps, AAC 192kbps
- Formato YT/Vimeo: 1920×1080 (16:9) con letterbox, stessi codec
- Durata totale target: 28–34 secondi
- Thumbnail: JPEG qualità 95, frame t=18s (momento trasformazione)

---

# Voiceover Agent — Edge-TTS Isabella Neural

## Ruolo
Genera il voiceover italiano per i video usando Edge-TTS con la voce IsabellaNeural.
La voce di FLUXION è la stessa voce di SARA: coerenza di brand.

## Voce ufficiale FLUXION
- Voice: `it-IT-IsabellaNeural`
- Rate: `+5%` (leggermente più veloce, ritmo commerciale)
- Stile segmento dolore: `empathetic`
- Stile segmento trasformazione: `hopeful`
- Stile CTA: `confident` (tono più deciso)

## Test voce
```python
import asyncio
import edge_tts

async def test():
    tts = edge_tts.Communicate(
        "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre.",
        voice="it-IT-IsabellaNeural",
        rate="+5%"
    )
    await tts.save("test_voiceover.mp3")

asyncio.run(test())
# Riproduci: afplay test_voiceover.mp3
```

## Script narrazione per verticale
Generato da `script_generator.py::build_narration_script()`.
Ogni segmento ha un `start_sec` che indica quando inizia il voiceover nella timeline.

---

# QA Agent — Verifica qualità video

## Ruolo
Verifica che ogni video prodotto rispetti le specifiche prima della distribuzione.

## Checklist QA automatica

```python
# Esegui automaticamente dopo assembly:
python video_factory/qa_check.py --video output/parrucchiere/parrucchiere_video_9x16.mp4
```

### Checks eseguiti:
1. **Durata**: 25–36 secondi (fuori range → warning)
2. **Risoluzione**: 1080×1920 per 9:16, 1920×1080 per 16:9
3. **FPS**: 29.97 o 30 (non 24 — per mobile)
4. **Audio**: presenza traccia audio, peak level < -3dBFS
5. **Prezzo visibile**: frame analysis ~t=27s deve mostrare "€497" (OCR check)
6. **Logo FLUXION**: frame finale deve contenere il brand name
7. **Durata frame CTA**: almeno 5 secondi
8. **Codec**: H.264 video, AAC audio (compatibilità WA)
9. **File size**: < 50MB (limite WA per video)
10. **Bitrate**: 4–8 Mbps video (ottimale streaming mobile)

## QA manuale — cosa guardare
- Il soggetto Veo 3 corrisponde alla verticale (parrucchiere = salone reale)
- Nessun artefatto visibile nei primi 3 secondi (frame di apertura critico)
- Il testo overlay è leggibile su tutti gli sfondi
- La transizione verso il frame CTA è fluida (dissolvenza 0.5s)
- Il voiceover è sincronizzato con le scene
- "FLUXION" si legge chiaramente nell'ultimo frame

## Fix comuni

### Artefatti Veo 3 nei primi frame
```bash
# Taglia i primi 0.5s di ogni clip
ffmpeg -i input.mp4 -ss 0.5 -c copy output_trimmed.mp4
```

### Testo overlay non leggibile
Modifica in `assembly.py`: aumenta `boxborderw=20` e cambia `fontcolor=yellow`

### Video troppo grande per WA (>50MB)
```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset slow output_compressed.mp4
```

### Audio troppo basso
```bash
ffmpeg -i input.mp4 -filter:a "volume=2.0" output_louder.mp4
```
