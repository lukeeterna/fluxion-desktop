#!/bin/bash
# ============================================================
# Fluxion Demo Video Creator — via ZeroClaw agent
# Uso: ./scripts/create-demo-video.sh
# Output: /tmp/fluxion-demo/demo.mp4
# ============================================================
set -e

VOICE_AGENT="http://localhost:3002"
OUTPUT_DIR="/tmp/fluxion-demo"
OUTPUT_VIDEO="$OUTPUT_DIR/demo.mp4"

echo "=== Fluxion Demo Video Creator ==="
echo ""

# 1. Check prerequisiti
echo "[1/5] Verifica prerequisiti..."
command -v zeroclaw >/dev/null 2>&1 || { echo "❌ zeroclaw non installato. Esegui: brew install zeroclaw"; exit 1; }
command -v ffmpeg >/dev/null 2>&1   || { echo "❌ ffmpeg non installato. Esegui: brew install ffmpeg"; exit 1; }

# 2. Verifica voice agent attivo
echo "[2/5] Verifica voice agent su $VOICE_AGENT..."
HEALTH=$(curl -sf "$VOICE_AGENT/health" 2>/dev/null) || { echo "❌ Voice agent non attivo su porta 3002"; exit 1; }
echo "✅ Voice agent: $HEALTH"

# 3. Prepara directory
echo "[3/5] Prepara output directory..."
mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/frame_*.png  # Pulisce run precedenti

# 4. Lancia agente ZeroClaw
echo "[4/5] Lancio agente ZeroClaw (fluxion_demo)..."
echo ""

zeroclaw agent \
  --agent fluxion_demo \
  -m "
Crea il demo video di Fluxion. Segui questi passi esatti:

STEP 1: Prepara directory
  shell: mkdir -p /tmp/fluxion-demo

STEP 2: Health check voice agent
  http_request: GET http://localhost:3002/health

STEP 3: Screenshot iniziale (mostra terminale)
  screenshot: /tmp/fluxion-demo/frame_001.png

STEP 4: Demo turn 1 - saluto cliente
  http_request: POST http://localhost:3002/api/voice/reset {}
  http_request: POST http://localhost:3002/api/voice/process {\"text\": \"Buongiorno, sono Marco Rossi\"}
  shell: sleep 1
  screenshot: /tmp/fluxion-demo/frame_002.png

STEP 5: Demo turn 2 - richiesta prenotazione
  http_request: POST http://localhost:3002/api/voice/process {\"text\": \"Vorrei prenotare un taglio per domani alle 15\"}
  shell: sleep 1
  screenshot: /tmp/fluxion-demo/frame_003.png

STEP 6: Demo turn 3 - conferma
  http_request: POST http://localhost:3002/api/voice/process {\"text\": \"Sì, perfetto\"}
  shell: sleep 1
  screenshot: /tmp/fluxion-demo/frame_004.png

STEP 7: Screenshot finale
  screenshot: /tmp/fluxion-demo/frame_005.png

STEP 8: Monta video con ffmpeg
  shell: ffmpeg -y -framerate 1 -pattern_type glob -i '/tmp/fluxion-demo/frame_*.png' -c:v libx264 -pix_fmt yuv420p -vf 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2' /tmp/fluxion-demo/demo.mp4

Quando hai finito, conferma il path del video: /tmp/fluxion-demo/demo.mp4
"

# 5. Verifica output
echo ""
echo "[5/5] Verifica output..."
if [ -f "$OUTPUT_VIDEO" ]; then
  SIZE=$(du -sh "$OUTPUT_VIDEO" | cut -f1)
  DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT_VIDEO" 2>/dev/null | xargs printf "%.0f" 2>/dev/null || echo "?")
  echo "✅ Video creato: $OUTPUT_VIDEO"
  echo "   Dimensione: $SIZE"
  echo "   Durata: ${DURATION}s"
  echo ""
  echo "Prossimo passo: carica su YouTube (non in elenco) e invia link a LemonSqueezy"
  open "$OUTPUT_DIR"
else
  echo "⚠️  Video non trovato. Controlla i log zeroclaw sopra."
fi
