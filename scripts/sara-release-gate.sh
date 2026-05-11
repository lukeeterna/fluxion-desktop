#!/usr/bin/env bash
# FLUXION Sara — Release Gate automation (S200)
# Esegue test_sara_release_gate via SSH iMac, fetch report, propaga exit code.
#
# Uso:
#   ./scripts/sara-release-gate.sh             # full gate (tier 1+2+3)
#   ./scripts/sara-release-gate.sh --tier=1    # solo core deep
#   ./scripts/sara-release-gate.sh --verbose   # log dettagliato
#
# Exit codes:
#   0  PASS (Sara pronta per release)
#   1  FAIL (release bloccata)
#   2  Errore infrastruttura (pipeline down, SSH fail, etc.)

set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────
IMAC_HOST="${FLUXION_IMAC_HOST:-imac}"
IMAC_REPO="/Volumes/MacSSD - Dati/fluxion"
REMOTE_REPORT="/tmp/sara-release-gate.json"
LOCAL_REPORT_DIR="/Volumes/MontereyT7/FLUXION/docs/launch/sara-release-gate-reports"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOCAL_REPORT="${LOCAL_REPORT_DIR}/release-gate-${TIMESTAMP}.json"

# Arg passthrough (passa --tier=N --verbose --skip-extended etc al python)
PYTHON_ARGS="--release-gate --report=${REMOTE_REPORT}"
for arg in "$@"; do
    PYTHON_ARGS="${PYTHON_ARGS} ${arg}"
done

mkdir -p "${LOCAL_REPORT_DIR}"

# ── Step 1: Health check pipeline iMac ───────────────────────────────
echo "════════════════════════════════════════════════════════════════"
echo "  FLUXION Sara Release Gate — $(date +%H:%M:%S)"
echo "════════════════════════════════════════════════════════════════"
echo
echo "[1/4] Health check pipeline iMac (porta 3002)..."

HEALTH_STATUS="$(ssh "${IMAC_HOST}" "curl -sf --max-time 5 http://127.0.0.1:3002/health || echo DOWN" 2>/dev/null || echo "SSH_FAIL")"

if [[ "${HEALTH_STATUS}" == "SSH_FAIL" ]]; then
    echo "❌ FATAL: SSH ${IMAC_HOST} non raggiungibile"
    exit 2
fi
if [[ "${HEALTH_STATUS}" == "DOWN" ]]; then
    echo "❌ FATAL: Pipeline iMac porta 3002 non risponde"
    echo "   Avvio richiesto:  ssh ${IMAC_HOST} \"cd '${IMAC_REPO}/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &\""
    exit 2
fi
echo "✅ Pipeline UP: $(echo "${HEALTH_STATUS}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"v={d.get('version','?')} stt={d.get('features',{}).get('stt','?')} tts={d.get('features',{}).get('tts','?')}\")")"

# ── Step 2: Sync repo iMac con master ────────────────────────────────
echo
echo "[2/4] Sync repo iMac con origin/master..."
ssh "${IMAC_HOST}" "cd '${IMAC_REPO}' && git pull origin master --quiet" || {
    echo "⚠️  WARN: git pull fallito, procedo comunque (repo iMac potrebbe essere stale)"
}

# ── Step 3: Esegui release gate ──────────────────────────────────────
echo
echo "[3/4] Esecuzione release gate su iMac (può richiedere 3-5 min)..."
echo "      Args: ${PYTHON_ARGS}"
echo

# Run + cattura exit code (set +e per non abortire qui)
set +e
ssh "${IMAC_HOST}" "cd '${IMAC_REPO}/voice-agent' && source venv/bin/activate 2>/dev/null; python3 tests/e2e/release_gate.py ${PYTHON_ARGS}"
GATE_EXIT=$?
set -e

# ── Step 4: Fetch report ─────────────────────────────────────────────
echo
echo "[4/4] Fetch report JSON..."
scp -q "${IMAC_HOST}:${REMOTE_REPORT}" "${LOCAL_REPORT}" || {
    echo "⚠️  WARN: report non recuperabile (gate exit=${GATE_EXIT})"
}

if [[ -f "${LOCAL_REPORT}" ]]; then
    echo "📄 Report locale: ${LOCAL_REPORT}"
    echo
    echo "── Sintesi ────────────────────────────────────────────────"
    python3 - "${LOCAL_REPORT}" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    r = json.load(f)
print(f"Verdict:    {r['verdict']}")
print(f"Pipeline:   v{r.get('pipeline_version','?')}")
print(f"Durata:     {r.get('duration_sec','?')}s")
print(f"Totals:     OK={r['totals']['ok']} WARN={r['totals']['warn']} FAIL={r['totals']['fail']}")
if r.get('latency'):
    lat = r['latency']
    slo = lat.get('gates', {}).get('p95_slo_target_ms', lat.get('target_ms', '?'))
    print(f"Latency:    P50={lat['p50_ms']}ms P95={lat['p95_ms']}ms (SLO target <{slo}ms)")
    if 'slow_sample_ratio' in lat:
        print(f"Slow %:     {lat['slow_sample_ratio']*100:.0f}% sample > {lat['slow_sample_threshold_ms']}ms")
print(f"Verticali:  T1={len(r.get('tier1_verticals_core',[]))} T2={len(r.get('tier2_verticals_extended',[]))}")
if r['totals']['fail'] > 0:
    print(f"\nFailures ({r['totals']['fail']}):")
    for line in r.get('failures', [])[:10]:
        print(f"  {line}")
    if len(r.get('failures', [])) > 10:
        print(f"  ... +{len(r['failures']) - 10} altre — vedi {sys.argv[1]}")
PYEOF
    echo "─────────────────────────────────────────────────────────"
fi

# ── Verdict finale ───────────────────────────────────────────────────
echo
if [[ ${GATE_EXIT} -eq 0 ]]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "  ✅ RELEASE GATE: PASS — Sara pronta per release"
    echo "════════════════════════════════════════════════════════════════"
    exit 0
elif [[ ${GATE_EXIT} -eq 1 ]]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "  ❌ RELEASE GATE: FAIL — release BLOCCATA"
    echo "  Vedi report: ${LOCAL_REPORT}"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
else
    echo "════════════════════════════════════════════════════════════════"
    echo "  ⚠️  RELEASE GATE: ERRORE INFRASTRUTTURA (exit=${GATE_EXIT})"
    echo "════════════════════════════════════════════════════════════════"
    exit 2
fi
