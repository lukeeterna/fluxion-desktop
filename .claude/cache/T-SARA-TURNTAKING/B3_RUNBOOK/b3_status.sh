#!/usr/bin/env bash
set -euo pipefail
# ─────────────────────────────────────────────────────────────────────────────
# b3_status.sh — fotografia read-only: quale engine gira su :3002 e con quale
# processo. Non tocca nulla. NESSUN secret a stdout (lo status espone username/
# server del DID per design dell'app, MAI la password).
# ─────────────────────────────────────────────────────────────────────────────
PORT=3002
STATUS_URL="http://127.0.0.1:${PORT}/api/voice/voip/status"

echo "== STATUS ENDPOINT =="
curl -s --max-time 5 "$STATUS_URL" || echo "(status non raggiungibile)"
echo ""
echo "== PROCESSO :$PORT =="
PID="$(lsof -ti:${PORT} | head -1 || true)"
if [ -n "${PID:-}" ]; then ps -o pid=,command= -p "$PID"; else echo "nessun processo su :$PORT"; fi
