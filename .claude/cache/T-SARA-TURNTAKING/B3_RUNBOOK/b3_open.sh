#!/usr/bin/env bash
set -euo pipefail
# ─────────────────────────────────────────────────────────────────────────────
# b3_open.sh — APRE la finestra B3: sostituisce la Sara di PRODUZIONE (engine
# pjsua2) con la Sara-go (VOICE_ENGINE=go + SARA_TEST_CAPTURE=1) sulla porta 3002.
# Genera /tmp/b3/restore.sh dalla command-line CATTURATA A RUNTIME (non assunta).
# NON eseguire a mano: il primo run vero è del founder (mandato B3-PREP).
#
# PREMESSE (VERIFICATE in sessione 2026-07-14; DISCORDANZA se smentite a runtime):
#  - repo iMac ........ /Volumes/MacSSD - Dati/fluxion
#  - main.py avviato con argv RELATIVO ("main.py --port 3002") → cwd = voice-agent
#    (lsof cwd via SSH cross-user rende "/", inaffidabile: si usa $VA dove main.py risiede)
#  - .env COMPLETO (contiene VOIP_SIP_PASS) → voice-agent/.env  (la root .env NON ha PASS)
#  - status endpoint .. /api/voice/voip/status → {"engine":..,"sip":{"reg_status":200}}
#  - NESSUN launchd né launcher canonico per :3002 → produzione avviata a mano (nohup)
# ─────────────────────────────────────────────────────────────────────────────
REPO="/Volumes/MacSSD - Dati/fluxion"
VA="$REPO/voice-agent"
ENVFILE="$VA/.env"
PORT=3002
STATUS_URL="http://127.0.0.1:${PORT}/api/voice/voip/status"
WORK=/tmp/b3
mkdir -p "$WORK"
RESTORE="$WORK/restore.sh"
PIDFILE="$WORK/sara_go.pid"
LOG="$WORK/sara_go.log"

echo "CHECKPOINT 1: cattura command-line Sara viva su :$PORT"
PID="$(lsof -ti:${PORT} | head -1 || true)"
if [ -z "${PID:-}" ]; then echo "ABORT: nessun processo su :$PORT (Sara non viva) — non apro"; exit 2; fi
ARGV="$(ps -o command= -p "$PID")"
echo "  pid=$PID"
echo "  argv=$ARGV"

echo "CHECKPOINT 2: genero restore.sh dalla command-line runtime"
cat > "$RESTORE" <<EOF
#!/usr/bin/env bash
# restore.sh — AUTOGENERATO da b3_open.sh (cattura runtime, non assunta).
# Rilancia la Sara di PRODUZIONE con la ESATTA argv catturata: engine pjsua2
# (nessun VOICE_ENGINE=go, nessuna capture). Idempotenza gestita da b3_close.sh.
set -euo pipefail
cd "$VA"
P="\$(lsof -ti:${PORT} | head -1 || true)"
[ -n "\${P:-}" ] && kill "\$P" && sleep 2 || true
for i in \$(seq 1 10); do lsof -ti:${PORT} >/dev/null 2>&1 || break; sleep 1; done
set -a; . "$ENVFILE"; set +a
nohup $ARGV > /tmp/b3/sara_restore.log 2>&1 &
echo "restore: rilanciato pid \$! (argv: $ARGV)"
EOF
chmod +x "$RESTORE"
echo "  restore.sh scritto: $RESTORE"

echo "CHECKPOINT 3: kill Sara di produzione (pjsua2) pid=$PID"
kill "$PID"
for i in $(seq 1 10); do lsof -ti:${PORT} >/dev/null 2>&1 || break; sleep 1; done

echo "CHECKPOINT 4: rilancio Sara-go (VOICE_ENGINE=go + SARA_TEST_CAPTURE=1)"
cd "$VA"
set -a; . "$ENVFILE"; set +a
VOICE_ENGINE=go SARA_TEST_CAPTURE=1 nohup $ARGV > "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "  sara-go pid=$(cat "$PIDFILE") log=$LOG"

echo "CHECKPOINT 5: attendo engine=go + reg 200 (max 30s)"
ok=0
for i in $(seq 1 30); do
  resp="$(curl -s --max-time 3 "$STATUS_URL" || true)"
  if echo "$resp" | grep -qE '"engine":[[:space:]]*"go"' && echo "$resp" | grep -qE '"reg_status":[[:space:]]*200'; then ok=1; break; fi
  sleep 1
done
if [ "$ok" = "1" ]; then
  echo "CHECKPOINT GO-UP"
else
  echo "TIMEOUT: engine!=go o reg!=200 entro 30s → eseguo restore"
  bash "$RESTORE" || true
  echo "ABORT-RESTORED"
  exit 3
fi
