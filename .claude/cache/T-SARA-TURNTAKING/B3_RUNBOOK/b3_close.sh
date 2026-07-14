#!/usr/bin/env bash
set -euo pipefail
# ─────────────────────────────────────────────────────────────────────────────
# b3_close.sh — CHIUDE la finestra B3: ripristina la Sara di PRODUZIONE (pjsua2).
# IDEMPOTENTE: due run consecutivi = ok (se già in pjsua2+reg200 esce pulito).
# È anche il comando di EMERGENZA: rilanciarlo (anche due volte) riporta produzione.
# NON eseguire a mano in prep: il primo run vero è del founder (mandato B3-PREP).
#
# PREMESSE (VERIFICATE 2026-07-14): vedi b3_open.sh. R4: NESSUN launcher canonico
# su disco → il restore usa /tmp/b3/restore.sh generato da b3_open.sh (fallback ps).
# ─────────────────────────────────────────────────────────────────────────────
REPO="/Volumes/MacSSD - Dati/fluxion"
VA="$REPO/voice-agent"
PORT=3002
STATUS_URL="http://127.0.0.1:${PORT}/api/voice/voip/status"
WORK=/tmp/b3
RESTORE="$WORK/restore.sh"

echo "CHECKPOINT 1: stato attuale engine"
resp="$(curl -s --max-time 3 "$STATUS_URL" || true)"
echo "  status: ${resp:-（non raggiungibile）}"
if echo "$resp" | grep -qE '"engine":[[:space:]]*"pjsua2"' && echo "$resp" | grep -qE '"reg_status":[[:space:]]*200'; then
  echo "CHECKPOINT RESTORED (già in pjsua2+reg200 — idempotente, nulla da fare)"
  exit 0
fi

echo "CHECKPOINT 2: kill Sara-go se viva su :$PORT"
P="$(lsof -ti:${PORT} | head -1 || true)"
if [ -n "${P:-}" ]; then kill "$P" && sleep 2 || true; fi
for i in $(seq 1 10); do lsof -ti:${PORT} >/dev/null 2>&1 || break; sleep 1; done

echo "CHECKPOINT 3: restore Sara pjsua2 (R4: launcher canonico assente → restore.sh)"
if [ -x "$RESTORE" ]; then
  bash "$RESTORE" || true
else
  echo "  ERRORE: $RESTORE assente. b3_open.sh non è stato eseguito in questa finestra."
  echo "  FALLBACK MANUALE: cd '$VA'; set -a; . .env; set +a; nohup <python-di-sistema> main.py --port 3002 &"
  exit 4
fi

echo "CHECKPOINT 4: attendo engine=pjsua2 + reg 200 (max 30s)"
ok=0
for i in $(seq 1 30); do
  resp="$(curl -s --max-time 3 "$STATUS_URL" || true)"
  if echo "$resp" | grep -qE '"engine":[[:space:]]*"pjsua2"' && echo "$resp" | grep -qE '"reg_status":[[:space:]]*200'; then ok=1; break; fi
  sleep 1
done
if [ "$ok" = "1" ]; then
  echo "CHECKPOINT RESTORED"
else
  echo "TIMEOUT: pjsua2 non ripristinato entro 30s — rilancia b3_close.sh; se persiste, INTERVENTO MANUALE"
  exit 5
fi
