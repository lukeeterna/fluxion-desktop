#!/bin/bash
# Genera voiceover marketing 5 scene con say -v Federica (Italian macOS)
# Poi converte in MP3 via ffmpeg (imageio-ffmpeg)
# Eseguire su iMac: bash gen_marketing_audio.sh

set -e

OUTDIR="public/marketing"
mkdir -p "$OUTDIR"

# Path ffmpeg statico (imageio-ffmpeg installato su iMac)
FFMPEG=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" 2>/dev/null || echo "ffmpeg")

echo "Usando ffmpeg: $FFMPEG"
echo ""

# Voce italiana macOS — Federica (più naturale) o Alice come fallback
VOICE="Federica"
# Testa se Federica è disponibile, altrimenti usa Alice
if ! say -v Federica "" 2>/dev/null; then
  VOICE="Alice"
fi
echo "Voce selezionata: $VOICE"
echo ""

# ── MS01 — Hook (5s) ───────────────────────────────────────────────────────────
echo "Generando ms01..."
say -v "$VOICE" -r 145 \
  "Ogni volta che il tuo telefono squilla e non riesci a rispondere… perdi un cliente." \
  -o "$OUTDIR/ms01.aiff"

# ── MS02 — Pain Points (15s) ──────────────────────────────────────────────────
echo "Generando ms02..."
say -v "$VOICE" -r 145 \
  "Intanto Treatwell prende il 25% di ogni prenotazione che arriva dal tuo telefono. Ogni mese. Per sempre. Mindbody ti costa 8.400 euro all'anno. In tre anni hai bruciato 25.000 euro… per un software. Ma c'è una terza via." \
  -o "$OUTDIR/ms02.aiff"

# ── MS03 — Demo Fluxion (20s) ─────────────────────────────────────────────────
echo "Generando ms03..."
say -v "$VOICE" -r 145 \
  "FLUXION include Sara, la tua assistente AI che risponde al telefono 24 ore su 24, in italiano perfetto, e prenota per te mentre sei con il cliente. Il calendario si aggiorna in automatico. Nessun doppio appuntamento, nessuna confusione. E subito dopo, WhatsApp di conferma automatico. Il cliente è felice. Tu non hai fatto nulla. Funziona offline. Nessun server esterno. I tuoi dati restano sul tuo computer. Solo tuo." \
  -o "$OUTDIR/ms03.aiff"

# ── MS04 — Stats (15s) ────────────────────────────────────────────────────────
echo "Generando ms04..."
say -v "$VOICE" -r 145 \
  "Con Fluxion Enterprise a 897 euro una volta sola, risparmi 24.000 euro rispetto a Mindbody in tre anni. Zero commissioni sulle prenotazioni. Zero abbonamenti. Zero dipendenze. Sei libero." \
  -o "$OUTDIR/ms04.aiff"

# ── MS05 — CTA (15s) ──────────────────────────────────────────────────────────
echo "Generando ms05..."
say -v "$VOICE" -r 140 \
  "Fluxion. Il gestionale che lavora per te, non tu per lui. Scegli il tuo piano, una volta sola. Vai su fluxion punto app e inizia oggi." \
  -o "$OUTDIR/ms05.aiff"

# ── Converti AIFF → MP3 ───────────────────────────────────────────────────────
echo ""
echo "Conversione AIFF → MP3..."
for id in ms01 ms02 ms03 ms04 ms05; do
  "$FFMPEG" -y -i "$OUTDIR/${id}.aiff" -codec:a libmp3lame -qscale:a 2 "$OUTDIR/${id}.mp3" 2>/dev/null \
    && echo "  ✓ ${id}.mp3" \
    || echo "  ⚠ fallback: copio come-è (Remotion supporta anche AIFF)"
done

# ── Durate effettive ───────────────────────────────────────────────────────────
echo ""
echo "Durate file generati:"
for id in ms01 ms02 ms03 ms04 ms05; do
  FILE="$OUTDIR/${id}.mp3"
  [ -f "$FILE" ] || FILE="$OUTDIR/${id}.aiff"
  DUR=$("$FFMPEG" -i "$FILE" 2>&1 | grep -o 'Duration: [0-9:\.]*' | cut -d' ' -f2)
  echo "  ${id}: $DUR"
done

echo ""
echo "✅ Audio generato in $OUTDIR"
echo ""
echo "Prossimo step — render marketing video:"
echo "  npx remotion render src/index.tsx FluxionMarketing out/marketing_70s.mp4 --log=verbose"
