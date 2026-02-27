#!/usr/bin/env bash
# mux-audio.sh — Concatena le 9 tracce audio con pause sync e le mixa nel video muto
# Uso: ./mux-audio.sh  (deve girare nella cartella video-remotion)
set -e

OUT_DIR="./out"
AUDIO_DIR="./public/voiceover"
TMP_DIR="/tmp/remotion-audio-mux"
mkdir -p "$TMP_DIR"

# Scene durations (frames @30fps, incluso 1s padding) — deve corrispondere a Video.tsx
# slot_sec = (scene_duration - transition_frames) / 30  [tranne ultima]
# Transition: 12 frames = 0.4s
declare -A SLOT_SEC
SLOT_SEC["01"]="9.7"
SLOT_SEC["02"]="11.4"
SLOT_SEC["03"]="10.7"
SLOT_SEC["04"]="11.1"
SLOT_SEC["05"]="11.9"
SLOT_SEC["06"]="15.2"
SLOT_SEC["07"]="13.8"
SLOT_SEC["08"]="10.4"
SLOT_SEC["09"]="14.9"   # ultima scena, nessuna transizione

# Crea ogni clip audio paddata alla sua slot duration (silence pad)
CONCAT_LIST="$TMP_DIR/concat.txt"
> "$CONCAT_LIST"

for i in 01 02 03 04 05 06 07 08 09; do
  MP3="$AUDIO_DIR/$i-*.mp3"
  # Trova il file con glob
  FNAME=$(ls $AUDIO_DIR/${i}-*.mp3 2>/dev/null | head -1)
  if [ -z "$FNAME" ]; then
    echo "⚠️  File non trovato per scena $i, uso silence"
    # Crea silence pura
    ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t "${SLOT_SEC[$i]}" \
      "$TMP_DIR/${i}_padded.mp3" -q:a 3 2>/dev/null
  else
    # Pad audio to slot duration
    ffmpeg -y -i "$FNAME" \
      -af "apad=pad_dur=${SLOT_SEC[$i]}" \
      -t "${SLOT_SEC[$i]}" \
      "$TMP_DIR/${i}_padded.mp3" -q:a 3 2>/dev/null
    echo "✓  Scena $i: $FNAME (slot: ${SLOT_SEC[$i]}s)"
  fi
  echo "file '${i}_padded.mp3'" >> "$CONCAT_LIST"
done

# Concat all audio segments
cd "$TMP_DIR"
ffmpeg -y -f concat -safe 0 -i concat.txt -c:a aac -b:a 192k combined_audio.aac 2>/dev/null
echo "✓  Audio combinato: combined_audio.aac"
cd - > /dev/null

# Mux audio + muted video
MUTED_VIDEO="$OUT_DIR/fluxion_muted.mp4"
FINAL_VIDEO="$OUT_DIR/fluxion_tutorial.mp4"

if [ ! -f "$MUTED_VIDEO" ]; then
  echo "❌ Video muto non trovato: $MUTED_VIDEO"
  echo "   Prima esegui: npx remotion render src/index_muted.tsx FluxionTutorialMuted out/fluxion_muted.mp4"
  exit 1
fi

ffmpeg -y \
  -i "$MUTED_VIDEO" \
  -i "$TMP_DIR/combined_audio.aac" \
  -c:v copy \
  -c:a aac \
  -shortest \
  "$FINAL_VIDEO"

echo ""
echo "✅ Video finale: $FINAL_VIDEO"
ls -lh "$FINAL_VIDEO"
