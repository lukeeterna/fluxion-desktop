#!/usr/bin/env bash
# launch_rig_fixed.sh — VERSIONE CORRETTA di launch_rig.sh (FIX-OBS 2026-07-17)
# Differenza unica: SARA_TEST_CAPTURE=1 aggiunto all'export riga 57.
# Applicare manualmente: cp vos/runs/20260717/1-FIX-OBS/launch_rig_fixed.sh \
#   .claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh
#
# INVARIANTI NON NEGOZIABILI:
#   - SOLO high-port loopback (sara :3003, regstub 127.0.0.1:15062, RTP 15090, bridge 8399).
#   - MAI :3002 (pjsua2 baseline), MAI trunk EHIWEB/DID, MAI Traccar 5062/5090.
#   - Idempotente: pulizia SOLO delle 4 high-port del rig.
# Eseguito SU iMac (via: ssh imac 'bash -s' < launch_rig_fixed.sh).
set -uo pipefail

VA="${VA_DIR:-/Volumes/MacSSD - Dati/FLUXION/voice-agent}"
REG_PORT=15062
SARA_PORT=3003
LOCAL_PORT=15090
BRIDGE_PORT=8399
SIP_SERVER="127.0.0.1:${REG_PORT}"

# ---------------- GUARD: aborta se punta a :3002 o al trunk ----------------
guard() {
  local bad=0 blob="${SIP_SERVER}|${SARA_PORT}|${LOCAL_PORT}|${BRIDGE_PORT}"
  for P in "$SARA_PORT" "$LOCAL_PORT" "$BRIDGE_PORT" "$REG_PORT"; do
    case "$P" in 3002|5062|5090) echo "GUARD-ABORT: porta protetta usata dal rig: $P"; bad=1;; esac
  done
  case "$SIP_SERVER" in 127.0.0.1:*) ;; *) echo "GUARD-ABORT: SIP server non loopback: $SIP_SERVER"; bad=1;; esac
  case "${SIP_SERVER##*:}" in 3002|5062|5090) echo "GUARD-ABORT: SIP server su porta protetta: $SIP_SERVER"; bad=1;; esac
  case "$blob" in *0972536918*|*ehiweb*) echo "GUARD-ABORT: riferimento trunk EHIWEB ($blob)"; bad=1;; esac
  [ "$bad" = 0 ] || { echo "RIG NON avviato (guard fallita)"; exit 2; }
  echo "GUARD OK: solo high-port loopback ($blob)"
}
guard

[ -d "$VA" ] || { echo "ABORT: voice-agent dir mancante: $VA"; exit 3; }
cd "$VA"

# ---------------- idempotenza: pulizia SOLO 4 high-port del rig -------------
for P in "$SARA_PORT" "$REG_PORT" "$LOCAL_PORT" "$BRIDGE_PORT"; do
  case "$P" in 3002|5062|5090) echo "SKIP porta protetta $P"; continue;; esac
  for pid in $(lsof -ti :"$P" 2>/dev/null || true); do
    echo "kill stale pid=$pid su :$P"; kill "$pid" 2>/dev/null || true
  done
done
sleep 1

# ---------------- regstub (UAS loopback: 200 OK a REGISTER/OPTIONS) ---------
REGBIN=./tools/gospike/regstub_darwin_amd64
[ -x "$REGBIN" ] || { echo "ABORT: regstub bin mancante/non eseguibile: $REGBIN"; exit 4; }
nohup "$REGBIN" -bind 127.0.0.1 -port "$REG_PORT" > /tmp/rig_regstub.log 2>&1 &
REG_PID=$!
echo "regstub pid=$REG_PID -> 127.0.0.1:$REG_PORT"
sleep 1

# ---------------- sara3003 (go engine puntato allo stub) -------------------
set -a; [ -f .env ] && source .env 2>/dev/null || true; set +a
# FIX-OBS (2026-07-17): SARA_TEST_CAPTURE=1 aggiunto (era assente nel vecchio script).
# GoEngineVoIPManager.__init__:188 legge la var in os.getenv DOPO che Python parte.
# python-dotenv load_dotenv() usa override=False → non sovrascrive env già impostato.
# Senza questo export, _capture resta False e zero WAV vengono scritti.
export VOIP_SIP_SERVER="$SIP_SERVER" VOICE_ENGINE=go VOIP_BRIDGE_PORT="$BRIDGE_PORT" VOIP_LOCAL_PORT="$LOCAL_PORT" SARA_TEST_CAPTURE=1
# re-guard DOPO source .env: se .env forza trunk, l'override deve vincere.
[ "$VOIP_SIP_SERVER" = "$SIP_SERVER" ] || { echo "GUARD-ABORT: override VOIP_SIP_SERVER fallito ($VOIP_SIP_SERVER)"; exit 2; }
case "$VOIP_SIP_SERVER" in 127.0.0.1:*) ;; *) echo "GUARD-ABORT: VOIP_SIP_SERVER non loopback dopo source"; exit 2;; esac
PYBIN=venv/bin/python; [ -x "$PYBIN" ] || PYBIN=python3
nohup "$PYBIN" main.py --port "$SARA_PORT" > /tmp/rig_sara3003.log 2>&1 &
SARA_PID=$!
echo "sara3003 pid=$SARA_PID -> :$SARA_PORT (engine=go, sip=$VOIP_SIP_SERVER, CAPTURE=1)"

# ---------------- health: registered:true entro 25s -----------------------
for i in $(seq 1 25); do
  sleep 1
  st=$(curl -s "http://127.0.0.1:${SARA_PORT}/api/voice/voip/status" 2>/dev/null || true)
  st_ns="${st// /}"
  case "$st_ns" in
    *'"registered":true'*) echo "RIG UP (${i}s): $st"; echo "PIDS reg=$REG_PID sara=$SARA_PID"; exit 0;;
  esac
done
echo "RIG health TIMEOUT — ultime righe sara3003:"; tail -8 /tmp/rig_sara3003.log
exit 5
