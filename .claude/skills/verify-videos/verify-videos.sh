#!/usr/bin/env bash
# verify-videos.sh — QA frame-level FLUXION
# Usage: verify-videos.sh <path_to_video.mp4>
# Exit codes:
#   0 = tutti i check passati
#   1 = problemi rilevati
#   2 = errore invocazione / tool mancante

set -u

# ── Colors ────────────────────────────────────────────────────────────────────
if [ -t 1 ]; then
    RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; BLU=$'\033[34m'; BLD=$'\033[1m'; RST=$'\033[0m'
else
    RED=""; GRN=""; YEL=""; BLU=""; BLD=""; RST=""
fi

# ── Args ──────────────────────────────────────────────────────────────────────
if [ $# -lt 1 ]; then
    echo "Usage: $0 <video.mp4>" >&2
    exit 2
fi
VIDEO="$1"
if [ ! -f "$VIDEO" ]; then
    echo "${RED}ERROR${RST}: file not found: $VIDEO" >&2
    exit 2
fi

# ── Tool check ────────────────────────────────────────────────────────────────
for tool in ffmpeg ffprobe; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "${RED}ERROR${RST}: $tool not in PATH. Try: export PATH=\"/usr/local/bin:/opt/homebrew/bin:\$PATH\"" >&2
        exit 2
    fi
done

# ── Thresholds (override via env) ─────────────────────────────────────────────
FREEZE_MIN_DUR="${FREEZE_MIN_DUR:-0.5}"        # secondi
DUPE_MAX_PCT="${DUPE_MAX_PCT:-2.0}"            # percentuale
BLACK_MIN_DUR="${BLACK_MIN_DUR:-0.3}"          # secondi
SILENCE_MIN_DUR="${SILENCE_MIN_DUR:-1.0}"      # secondi
SILENCE_DB="${SILENCE_DB:--45}"                # dB threshold

# ── Report header ─────────────────────────────────────────────────────────────
echo "${BLD}=== VERIFY VIDEOS — FRAME-LEVEL QA ===${RST}"
echo "File: $VIDEO"
echo

FAILED=0

# ── METADATA via ffprobe ──────────────────────────────────────────────────────
echo "${BLU}[METADATA]${RST}"
META=$(ffprobe -v error -print_format json -show_format -show_streams "$VIDEO" 2>/dev/null)
if [ -z "$META" ]; then
    echo "  ${RED}FAIL${RST}: ffprobe returned empty metadata"
    FAILED=1
else
    DURATION=$(echo "$META" | awk -F'"' '/"duration"/ {print $4; exit}')
    WIDTH=$(echo "$META" | awk -F'[:, ]' '/"width"/ {for(i=1;i<=NF;i++) if($i~/[0-9]+/){print $i; exit}}')
    HEIGHT=$(echo "$META" | awk -F'[:, ]' '/"height"/ {for(i=1;i<=NF;i++) if($i~/[0-9]+/){print $i; exit}}')
    FPS_RAW=$(echo "$META" | awk -F'"' '/"r_frame_rate"/ {print $4; exit}')
    if [ -n "$FPS_RAW" ] && [ "$FPS_RAW" != "0/0" ]; then
        FPS=$(awk -v f="$FPS_RAW" 'BEGIN{split(f,a,"/"); if(a[2]+0>0) printf "%.2f", a[1]/a[2]; else print "0"}')
    else
        FPS="?"
    fi
    VCODEC=$(echo "$META" | awk -F'"' '/"codec_name"/ {print $4; exit}')
    BITRATE=$(echo "$META" | awk -F'"' '/"bit_rate"/ {print $4; exit}')
    echo "  duration=${DURATION:-?}s  resolution=${WIDTH:-?}x${HEIGHT:-?}  fps=${FPS}  vcodec=${VCODEC:-?}  bitrate=${BITRATE:-?}"
    HAS_AUDIO=$(echo "$META" | grep -c '"codec_type": "audio"')
    echo "  audio_streams=${HAS_AUDIO}"
fi
echo

# ── FREEZEDETECT ──────────────────────────────────────────────────────────────
echo "${BLU}[FREEZEDETECT]${RST}  (min_dur=${FREEZE_MIN_DUR}s, noise=0.003)"
FREEZE_LOG=$(ffmpeg -hide_banner -nostats -i "$VIDEO" \
    -vf "freezedetect=n=0.003:d=${FREEZE_MIN_DUR}" \
    -map 0:v:0 -f null - 2>&1 | grep "lavfi.freezedetect.freeze_start")
FREEZE_COUNT=$(echo "$FREEZE_LOG" | grep -c "freeze_start" || true)
if [ "$FREEZE_COUNT" -gt 0 ]; then
    echo "  ${RED}FAIL${RST}: $FREEZE_COUNT freeze event(s) detected"
    echo "$FREEZE_LOG" | head -10 | sed 's/^/    /'
    FAILED=1
else
    echo "  ${GRN}PASS${RST} (0 events)"
fi
echo

# ── MPDECIMATE (duplicate detection) ──────────────────────────────────────────
echo "${BLU}[MPDECIMATE]${RST}  (threshold=${DUPE_MAX_PCT}%)"
# Strategia: mpdecimate rimuove i duplicati; contiamo i frame *in uscita* dal
# filtro leggendo il contatore "frame=" finale di ffmpeg. Confronto con il
# totale da ffprobe → % duplicati.
MPD_LOG=$(ffmpeg -hide_banner -i "$VIDEO" \
    -vf "mpdecimate" \
    -map 0:v:0 -f null - 2>&1 | tail -3)
KEPT=$(echo "$MPD_LOG" | grep -oE "frame= *[0-9]+" | tail -1 | grep -oE "[0-9]+" | head -1)
TOTAL_FRAMES=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "$VIDEO" 2>/dev/null || echo "0")
if [ -n "$TOTAL_FRAMES" ] && [ "$TOTAL_FRAMES" -gt 0 ] && [ -n "${KEPT:-}" ] && [ "$KEPT" -gt 0 ]; then
    DUPED=$((TOTAL_FRAMES - KEPT))
    DUPE_PCT=$(awk -v d="$DUPED" -v t="$TOTAL_FRAMES" 'BEGIN{printf "%.2f", (d/t) * 100}')
    CMP=$(awk -v a="$DUPE_PCT" -v b="$DUPE_MAX_PCT" 'BEGIN{print (a+0 > b+0) ? "1" : "0"}')
    if [ "$CMP" = "1" ]; then
        echo "  ${RED}FAIL${RST}: ${DUPE_PCT}% frame duplicati (total=${TOTAL_FRAMES}, kept=${KEPT}, dropped=${DUPED}) — soglia ${DUPE_MAX_PCT}%"
        FAILED=1
    else
        echo "  ${GRN}PASS${RST} (${DUPE_PCT}% duplicates, total=${TOTAL_FRAMES}, kept=${KEPT})"
    fi
else
    echo "  ${YEL}SKIP${RST} (total_frames=${TOTAL_FRAMES}, kept=${KEPT:-unset})"
fi
echo

# ── BLACKDETECT ───────────────────────────────────────────────────────────────
echo "${BLU}[BLACKDETECT]${RST}  (min_dur=${BLACK_MIN_DUR}s)"
BLACK_LOG=$(ffmpeg -hide_banner -nostats -i "$VIDEO" \
    -vf "blackdetect=d=${BLACK_MIN_DUR}:pic_th=0.98" \
    -map 0:v:0 -f null - 2>&1 | grep "black_start")
BLACK_COUNT=$(echo "$BLACK_LOG" | grep -c "black_start" || true)
if [ "$BLACK_COUNT" -gt 0 ]; then
    # Esclusione: ultimo evento a fine video (fadeout) tollerato
    LAST_BLACK_START=$(echo "$BLACK_LOG" | grep -o "black_start:[0-9.]*" | tail -1 | cut -d: -f2)
    if [ -n "$LAST_BLACK_START" ] && [ -n "${DURATION:-}" ]; then
        DIFF=$(awk -v d="$DURATION" -v b="$LAST_BLACK_START" 'BEGIN{printf "%.2f", d - b}')
        CMP=$(awk -v x="$DIFF" 'BEGIN{print (x+0 < 2.0) ? "1" : "0"}')
        if [ "$BLACK_COUNT" -eq 1 ] && [ "$CMP" = "1" ]; then
            echo "  ${GRN}PASS${RST} (1 evento finale, fadeout tollerato)"
        else
            echo "  ${RED}FAIL${RST}: $BLACK_COUNT eventi black, non tutti di fadeout"
            echo "$BLACK_LOG" | sed 's/^/    /'
            FAILED=1
        fi
    else
        echo "  ${YEL}WARN${RST}: $BLACK_COUNT eventi black"
        echo "$BLACK_LOG" | sed 's/^/    /'
    fi
else
    echo "  ${GRN}PASS${RST} (0 events)"
fi
echo

# ── SILENCEDETECT ─────────────────────────────────────────────────────────────
echo "${BLU}[SILENCEDETECT]${RST}  (min_dur=${SILENCE_MIN_DUR}s, threshold=${SILENCE_DB}dB)"
if [ "${HAS_AUDIO:-0}" -gt 0 ]; then
    SIL_LOG=$(ffmpeg -hide_banner -nostats -i "$VIDEO" \
        -af "silencedetect=noise=${SILENCE_DB}dB:d=${SILENCE_MIN_DUR}" \
        -map 0:a:0 -f null - 2>&1 | grep "silence_start")
    SIL_COUNT=$(echo "$SIL_LOG" | grep -c "silence_start" || true)
    if [ "$SIL_COUNT" -gt 0 ]; then
        echo "  ${YEL}WARN${RST}: $SIL_COUNT silence event(s)"
        echo "$SIL_LOG" | head -10 | sed 's/^/    /'
        if [ "$SIL_COUNT" -gt 2 ]; then
            FAILED=1
        fi
    else
        echo "  ${GRN}PASS${RST} (0 events ≥ ${SILENCE_MIN_DUR}s)"
    fi
else
    echo "  ${YEL}SKIP${RST} (no audio stream)"
fi
echo

# ── IDET (interlacing) ────────────────────────────────────────────────────────
echo "${BLU}[IDET]${RST}  (interlacing)"
IDET_LOG=$(ffmpeg -hide_banner -nostats -i "$VIDEO" \
    -vf "idet" -frames:v 500 -map 0:v:0 -f null - 2>&1 | grep -E "Multi frame|Single frame")
if [ -n "$IDET_LOG" ]; then
    echo "$IDET_LOG" | sed 's/^/    /'
    # idet emette la riga preliminaria (tutti 0) + la riga finale con i valori veri → prendi l'ultima
    MULTI_FINAL=$(echo "$IDET_LOG" | grep "Multi" | tail -1)
    PROG=$(echo "$MULTI_FINAL" | grep -oE "Progressive: *[0-9]+" | grep -oE "[0-9]+" | head -1)
    TFF=$(echo "$MULTI_FINAL" | grep -oE "TFF: *[0-9]+" | grep -oE "[0-9]+" | head -1)
    BFF=$(echo "$MULTI_FINAL" | grep -oE "BFF: *[0-9]+" | grep -oE "[0-9]+" | head -1)
    if [ -n "${PROG:-}" ] && [ -n "${TFF:-}" ] && [ -n "${BFF:-}" ]; then
        INTERLACED=$((TFF + BFF))
        TOTAL_I=$((PROG + INTERLACED))
        if [ "$TOTAL_I" -gt 0 ]; then
            I_PCT=$(awk -v i="$INTERLACED" -v t="$TOTAL_I" 'BEGIN{printf "%.1f", (i/t)*100}')
            CMP=$(awk -v x="$I_PCT" 'BEGIN{print (x+0 > 5.0) ? "1" : "0"}')
            if [ "$CMP" = "1" ]; then
                echo "  ${RED}FAIL${RST}: ${I_PCT}% interlaced (soglia 5%)"
                FAILED=1
            else
                echo "  ${GRN}PASS${RST} (${I_PCT}% interlaced)"
            fi
        fi
    fi
else
    echo "  ${YEL}SKIP${RST} (idet non ha prodotto statistiche)"
fi
echo

# ── Verdetto finale ───────────────────────────────────────────────────────────
if [ "$FAILED" -eq 0 ]; then
    echo "${GRN}${BLD}✅ VIDEO READY${RST} (exit 0)"
    exit 0
else
    echo "${RED}${BLD}❌ VIDEO HAS ISSUES${RST} (exit 1)"
    exit 1
fi
