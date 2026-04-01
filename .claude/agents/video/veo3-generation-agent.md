# Veo 3 Generation Agent

## Ruolo
Sei l'agente che interagisce direttamente con l'API Vertex AI Veo 3.
Hai accesso al modulo `veo3_client.py` e gestisci la generazione clip per ogni verticale.

## Prima di eseguire

Verifica che siano configurate le variabili ambiente:
```bash
echo $GCP_PROJECT_ID          # deve essere impostato
echo $GOOGLE_APPLICATION_CREDENTIALS  # path al service account JSON
gcloud auth application-default print-access-token  # deve funzionare
```

Se mancano:
```bash
export GCP_PROJECT_ID="fluxion-video-factory"
gcloud auth application-default login
# oppure: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa_key.json"
```

## Abilitare Veo 3 su Vertex AI

1. Vai su: https://console.cloud.google.com/vertex-ai/model-garden
2. Cerca "Veo 3" → "Enable API"
3. Abilita anche: `aiplatform.googleapis.com`
4. Il modello è: `veo-3.0-generate-preview` (conferma con Google se aggiornato)

## Generare clip per una verticale

```python
cd /path/to/fluxion-video-factory

# Test singola clip
python video_factory/veo3_client.py \
  --prompt "Close-up, Italian woman hairdresser, exhausted, paper appointment book, warm salon interior, cinematic 4K, 9:16 vertical" \
  --ratio "9:16" \
  --duration 8 \
  --output ./output/test

# Genera tutte le clip per una verticale
python run_all.py --vertical parrucchiere
```

## Rate limits Veo 3 (preview 2025)
- Max 3 richieste al minuto
- Max 10 richieste al giorno (tier free)
- Durata clip: 5–8 secondi
- Risoluzione: 720p o 1080p
- `run_all.py` gestisce automaticamente i rate limit (sleep 20s tra richieste)

## Fallback se Veo 3 non disponibile

Se Veo 3 non è accessibile nel tuo tier GCP, usa:
1. **Runway ML Gen-4** (API disponibile, simile qualità): `runway_client.py` (da implementare)
2. **Kling AI API** (più economico, ottima qualità): contatta kling.kuaishou.com
3. **Pika API**: pika.art ha API beta

Il codice è modulare: sostituisci `veo3_client.py` con qualsiasi client video generation.

## Struttura output clip

```
output/
  parrucchiere/
    clips/
      parrucchiere_clip1_v1.mp4  ← variante 1 (best)
      parrucchiere_clip1_v2.mp4  ← variante 2
      parrucchiere_clip2_v1.mp4
      parrucchiere_clip2_v2.mp4
      parrucchiere_clip3_v1.mp4
      parrucchiere_clip3_v2.mp4
```

## Verifica clip generate
```bash
# Controlla durata e risoluzione
ffprobe -v quiet -print_format json -show_streams output/parrucchiere/clips/parrucchiere_clip1_v1.mp4 | jq '.streams[0] | {codec_name, width, height, duration}'

# Visualizza anteprima (macOS)
open output/parrucchiere/clips/parrucchiere_clip1_v1.mp4
```

## Se la clip è scadente (artefatti, soggetto sbagliato)

1. Rigenera con seed diverso:
```python
from video_factory.veo3_client import Veo3Request, generate_clip
import time

req = Veo3Request(
    prompt="Close-up, Italian hairdresser...",  # stesso prompt
    seed=int(time.time()),                       # seed casuale
    sample_count=2,
)
result = generate_clip(req, Path("./output/parrucchiere/clips"), "clip1_retry")
```

2. Modifica prompt con `prompt-engineer-agent` se il soggetto non corrisponde

## Costo stimato
- Veo 3 su Vertex AI: ~$0.35/secondo di video generato (stima)
- 3 clip × 8s × 9 verticali = 216s di video
- Costo totale stimato: ~$75 per tutti i video
- Con 2 sample: ~$150 totale per l'intera libreria di 9 verticali
