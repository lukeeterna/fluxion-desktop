#!/usr/bin/env bash
# restore.sh — AUTOGENERATO da b3_open.sh (cattura runtime, non assunta).
# Rilancia la Sara di PRODUZIONE con la ESATTA argv catturata: engine pjsua2
# (nessun VOICE_ENGINE=go, nessuna capture). Idempotenza gestita da b3_close.sh.
set -euo pipefail
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
P="$(lsof -ti:3002 | head -1 || true)"
[ -n "${P:-}" ] && kill "$P" && sleep 2 || true
for i in $(seq 1 10); do lsof -ti:3002 >/dev/null 2>&1 || break; sleep 1; done
set -a; . "/Volumes/MacSSD - Dati/fluxion/voice-agent/.env"; set +a
nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/b3/sara_restore.log 2>&1 &
echo "restore: rilanciato pid $! (argv: /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002)"
