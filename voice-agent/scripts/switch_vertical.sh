#!/bin/bash
# ================================================================
# FLUXION - Switch Vertical DB & Restart Voice Pipeline
# ================================================================
# Usage: ./switch_vertical.sh <vertical_name>
# Example: ./switch_vertical.sh salone
#          ./switch_vertical.sh barbiere
#
# Available verticals:
#   salone, barbiere, beauty, odontoiatra, fisioterapia,
#   gommista, toelettatura, palestra, medical
#
# What it does:
#   1. Copies the vertical DB to the main fluxion.db location
#   2. Kills the voice pipeline (port 3002)
#   3. Restarts the voice pipeline with FLUXION_DB_PATH set
# ================================================================

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERTICAL_DBS_DIR="$SCRIPT_DIR/../data/vertical_dbs"
PROJECT_ROOT="$SCRIPT_DIR/../.."
VOICE_AGENT_DIR="$SCRIPT_DIR/.."

# DB target paths (voice agent looks in these locations)
TAURI_DB="$HOME/Library/Application Support/com.fluxion.desktop/fluxion.db"
PROJECT_DB="$PROJECT_ROOT/src-tauri/fluxion.db"

# Voice pipeline
VOICE_PORT=3002
VOIP_PORT=5080
PYTHON="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"

# --- Validation ---
if [ $# -lt 1 ]; then
    echo "Usage: $0 <vertical_name>"
    echo ""
    echo "Available verticals:"
    for f in "$VERTICAL_DBS_DIR"/*.db; do
        [ -f "$f" ] && echo "  $(basename "$f" .db)"
    done
    exit 1
fi

VERTICAL="$1"
SOURCE_DB="$VERTICAL_DBS_DIR/${VERTICAL}.db"

if [ ! -f "$SOURCE_DB" ]; then
    echo "ERROR: Database not found: $SOURCE_DB"
    echo ""
    echo "Available verticals:"
    for f in "$VERTICAL_DBS_DIR"/*.db; do
        [ -f "$f" ] && echo "  $(basename "$f" .db)"
    done
    echo ""
    echo "Run create_vertical_dbs.py first to generate the DBs."
    exit 1
fi

echo "================================================================"
echo "FLUXION — Switching to vertical: $VERTICAL"
echo "================================================================"

# --- Step 1: Copy DB ---
echo ""
echo "[1/3] Copying $VERTICAL.db to target locations..."

# Copy to Tauri app data path
mkdir -p "$(dirname "$TAURI_DB")"
cp "$SOURCE_DB" "$TAURI_DB"
echo "  -> $TAURI_DB"

# Also copy to project root (fallback path)
cp "$SOURCE_DB" "$PROJECT_DB"
echo "  -> $PROJECT_DB"

# Also copy to voice-agent/ root (relative path used by start_session)
cp "$SOURCE_DB" "$VOICE_AGENT_DIR/fluxion.db"
echo "  -> $VOICE_AGENT_DIR/fluxion.db"

# --- Step 2: Kill existing pipeline ---
echo ""
echo "[2/3] Stopping voice pipeline..."

# Kill process on port 3002
PIDS_3002=$(lsof -ti:$VOICE_PORT 2>/dev/null || true)
if [ -n "$PIDS_3002" ]; then
    echo "  Killing processes on port $VOICE_PORT: $PIDS_3002"
    kill -9 $PIDS_3002 2>/dev/null || true
else
    echo "  No process on port $VOICE_PORT"
fi

# Kill process on port 5080 (VoIP)
PIDS_5080=$(lsof -ti:$VOIP_PORT 2>/dev/null || true)
if [ -n "$PIDS_5080" ]; then
    echo "  Killing processes on port $VOIP_PORT: $PIDS_5080"
    kill -9 $PIDS_5080 2>/dev/null || true
else
    echo "  No process on port $VOIP_PORT"
fi

sleep 2

# --- Step 3: Restart pipeline ---
echo ""
echo "[3/3] Starting voice pipeline with $VERTICAL DB..."

# Set FLUXION_DB_PATH to the Tauri location (highest priority in _find_db_path)
export FLUXION_DB_PATH="$TAURI_DB"
export DYLD_LIBRARY_PATH="$VOICE_AGENT_DIR/lib/pjsua2"
export PYTHONUNBUFFERED=1

cd "$VOICE_AGENT_DIR"

# Check if Python exists
if [ ! -f "$PYTHON" ]; then
    # Fallback to system python3
    PYTHON=$(which python3 2>/dev/null || which python 2>/dev/null)
    if [ -z "$PYTHON" ]; then
        echo "ERROR: Python not found"
        exit 1
    fi
fi

nohup "$PYTHON" main.py --port $VOICE_PORT > /tmp/voice-pipeline.log 2>&1 &
NEW_PID=$!

echo "  Pipeline started with PID: $NEW_PID"
echo "  FLUXION_DB_PATH=$FLUXION_DB_PATH"
echo "  Log: /tmp/voice-pipeline.log"

# Wait for health check
echo ""
echo "Waiting for pipeline to start..."
for i in $(seq 1 15); do
    sleep 1
    if curl -s "http://127.0.0.1:$VOICE_PORT/health" > /dev/null 2>&1; then
        echo ""
        echo "================================================================"
        echo "SUCCESS: Voice pipeline running on port $VOICE_PORT"
        echo "Vertical: $VERTICAL"
        echo ""
        # Show business name from DB
        BUSINESS_NAME=$(sqlite3 "$TAURI_DB" "SELECT valore FROM impostazioni WHERE chiave='nome_attivita'" 2>/dev/null || echo "?")
        MACRO=$(sqlite3 "$TAURI_DB" "SELECT valore FROM impostazioni WHERE chiave='macro_categoria'" 2>/dev/null || echo "?")
        NUM_SERVIZI=$(sqlite3 "$TAURI_DB" "SELECT COUNT(*) FROM servizi WHERE attivo=1" 2>/dev/null || echo "?")
        NUM_OPERATORI=$(sqlite3 "$TAURI_DB" "SELECT COUNT(*) FROM operatori WHERE attivo=1" 2>/dev/null || echo "?")
        echo "Business:  $BUSINESS_NAME"
        echo "Category:  $MACRO"
        echo "Services:  $NUM_SERVIZI"
        echo "Operators: $NUM_OPERATORI"
        echo "================================================================"
        echo ""
        echo "Test command:"
        echo "  curl -X POST http://127.0.0.1:$VOICE_PORT/api/voice/process \\"
        echo "    -H 'Content-Type: application/json' \\"
        echo "    -d '{\"text\":\"Buongiorno, vorrei prenotare\"}'"
        exit 0
    fi
    printf "."
done

echo ""
echo "WARNING: Pipeline did not respond to health check after 15s"
echo "Check logs: tail -50 /tmp/voice-pipeline.log"
exit 1
