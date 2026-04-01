# FLUXION Video Factory — CLAUDE.md

## Progetto
Pipeline automatica per generare video di vendita verticali per FLUXION (gestionale desktop PMI italiane).
Stack: Python 3.11+ · Veo 3 (Vertex AI) · Edge-TTS · FFmpeg · whatsapp-web.js

## Struttura
```
fluxion-video-factory/
  run_all.py                          ← Entry point principale
  video_factory/
    veo3_client.py                    ← API Vertex AI Veo 3
    runway_fallback.py                ← Fallback Runway Gen-4 (se Veo 3 non disponibile)
    script_generator.py               ← Script + prompt per 9 verticali
    assembly.py                       ← FFmpeg post-produzione
    qa_check.py                       ← Quality assurance automatico
    music_layer.py                    ← Musica di sottofondo (royalty-free)
    wa_distributor.py                 ← Upload + messaggi WA completi
    upload_distributor.py             ← YT + Vimeo + Cloudflare R2
  .claude/agents/                     ← Agent specializzati
  output/                             ← Video generati (gitignored)
  assets/music/                       ← Tracce royalty-free
```

## Environment variables richieste
```bash
GCP_PROJECT_ID=fluxion-video-factory
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
RUNWAY_API_KEY=...                    # fallback Runway ML
VIMEO_TOKEN=...                       # upload Vimeo
VIMEO_KEY=...
VIMEO_SECRET=...
YT_CLIENT_SECRETS=/path/to/yt.json   # upload YouTube
CLOUDFLARE_ACCOUNT_ID=...            # R2 hosting video
CLOUDFLARE_R2_TOKEN=...
R2_BUCKET_NAME=fluxion-videos
R2_PUBLIC_URL=https://videos.fluxion.app
```

## Come lavorare su questo progetto

### Generare un video singolo
```bash
python run_all.py --vertical parrucchiere
```

### Generare tutti i video
```bash
python run_all.py --vertical all
```

### Solo export prompt (review prima di spendere su Veo 3)
```bash
python run_all.py --export-prompts-only
```

### Skip Veo 3 se le clip esistono già
```bash
python run_all.py --vertical all --skip-veo3 --use-existing ./output
```

### QA su video esistente
```bash
python video_factory/qa_check.py --video output/parrucchiere/parrucchiere_video_9x16.mp4
```

### Upload e distribuzione
```bash
python video_factory/upload_distributor.py --vertical parrucchiere --targets vimeo r2
python video_factory/upload_distributor.py --vertical all --targets vimeo r2 youtube
```

## Regole immutabili (non modificare senza approvazione)

1. **Verticali**: 9 definite in `script_generator.py::VERTICALI` — aggiungi solo lì
2. **Voice**: sempre `it-IT-IsabellaNeural` — coerenza con SARA
3. **Durata**: 28–34 secondi totali — fuori range = QA fallisce
4. **Prezzo**: €497 deve apparire nel frame CTA — non rimuovere mai
5. **Brand**: "FLUXION" maiuscolo ovunque — mai "fluxion" o "il gestionale"
6. **WA format**: max 5 righe, zero emoji, zero formalismi — regola Luca Ferretti
7. **Privacy Veo 3**: nessun volto reale riconoscibile — prompt sempre "Italian [role] in 40s"

## Dipendenze Python
```txt
google-cloud-aiplatform>=1.60.0
google-cloud-storage>=2.16.0
google-auth>=2.29.0
ffmpeg-python>=0.2.0
edge-tts>=6.1.9
PyVimeo>=1.1.0
google-api-python-client>=2.120.0
google-auth-oauthlib>=1.2.0
boto3>=1.34.0          # Cloudflare R2 (S3-compatible)
requests>=2.31.0
tqdm>=4.66.0
```

## Note operative
- Rate limit Veo 3 preview: max 3 req/min — il client gestisce automaticamente sleep(20)
- Ogni verticale genera ~300MB di clip raw — tenere pulizia in output/*/clips/
- I prompt JSON in output/prompts/ vanno revisionati manualmente prima di generare
- Il frame CTA viene generato interamente da FFmpeg (non da Veo 3)
- Runway ML Gen-4 come fallback: qualità comparabile, ~$0.05/secondo
