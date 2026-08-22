#!/usr/bin/env bash
# FLUXION Sara — exact-SHA release gate.
#
# The gate never mutates the canonical iMac worktree. It creates a detached,
# per-run worktree for the immutable candidate SHA, starts a side-effect-free
# HTTP certification server on a separate localhost port, runs the real stress
# harness against that process, fetches the JSON report, and removes the
# candidate process/worktree on every exit path.
#
# Exit codes:
#   0  PASS (behavior green AND P95 < configured SLO)
#   1  Product/release gate FAIL
#   2  Certification infrastructure FAIL

set -euo pipefail

IMAC_HOST="${FLUXION_IMAC_HOST:-imac}"
IMAC_REPO="${FLUXION_IMAC_REPO:-/Volumes/MacSSD - Dati/fluxion}"
CANDIDATE_PORT="${FLUXION_CANDIDATE_PORT:-3102}"
P95_SLO_MS="${FLUXION_P95_SLO_MS:-2000}"
LOCAL_REPORT_DIR="${FLUXION_REPORT_DIR:-/Volumes/MontereyT7/FLUXION/docs/launch/sara-release-gate-reports}"
CERT_RUN_ID="${FLUXION_CERT_RUN_ID:-manual-$(date +%s)-$$}"
SAFE_RUN_ID="$(printf '%s' "$CERT_RUN_ID" | tr -c 'A-Za-z0-9._-' '_')"

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_SHA="${FLUXION_TARGET_SHA:-$(git -C "$SCRIPT_ROOT" rev-parse HEAD 2>/dev/null || true)}"
if ! printf '%s' "$TARGET_SHA" | grep -Eq '^[0-9a-f]{40}$'; then
    echo "BLOCKED: FLUXION_TARGET_SHA non valido: ${TARGET_SHA:-<empty>}"
    exit 2
fi

REMOTE_WORKTREE="/tmp/fluxion-sara-cert-${SAFE_RUN_ID}"
REMOTE_REPORT="/tmp/sara-release-gate-${SAFE_RUN_ID}.json"
REMOTE_LOG="/tmp/sara-cert-server-${SAFE_RUN_ID}.log"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOCAL_REPORT="${LOCAL_REPORT_DIR}/release-gate-${TIMESTAMP}-${TARGET_SHA:0:12}.json"
GATE_ARGS=("$@")

mkdir -p "$LOCAL_REPORT_DIR"

echo "════════════════════════════════════════════════════════════════"
echo "  FLUXION Sara Exact-SHA Release Gate"
echo "  target=${TARGET_SHA}"
echo "  iMac=${IMAC_HOST} candidate_port=${CANDIDATE_PORT}"
echo "════════════════════════════════════════════════════════════════"

# Run the complete candidate lifecycle in one SSH session so the remote trap
# always owns process + worktree cleanup. Arguments after the fixed six are the
# release_gate.py CLI options (tier, verbose, skip-extended, ...).
set +e
ssh "$IMAC_HOST" bash -s -- \
    "$IMAC_REPO" "$TARGET_SHA" "$REMOTE_WORKTREE" "$CANDIDATE_PORT" \
    "$REMOTE_REPORT" "$REMOTE_LOG" "${GATE_ARGS[@]}" <<'REMOTE'
set -euo pipefail

IMAC_REPO="$1"
TARGET_SHA="$2"
WORKTREE="$3"
PORT="$4"
REPORT="$5"
LOG="$6"
shift 6
GATE_ARGS=("$@")
PID=""

cleanup() {
    rc=$?
    set +e
    if [ -n "${PID:-}" ] && kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null || true
        for _ in 1 2 3 4 5; do
            kill -0 "$PID" 2>/dev/null || break
            sleep 0.2
        done
        kill -9 "$PID" 2>/dev/null || true
    fi
    if [ -d "$WORKTREE" ]; then
        git -C "$IMAC_REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
    fi
    git -C "$IMAC_REPO" worktree prune >/dev/null 2>&1 || true
    exit "$rc"
}
trap cleanup EXIT INT TERM

[ -d "$IMAC_REPO/.git" ] || { echo "BLOCKED: iMac repo non trovato: $IMAC_REPO"; exit 2; }

PYTHON=""
for candidate in \
    "$IMAC_REPO/voice-agent/venv/bin/python3" \
    "$IMAC_REPO/voice-agent/.venv/bin/python3"; do
    if [ -x "$candidate" ]; then PYTHON="$candidate"; break; fi
done
[ -n "$PYTHON" ] || { echo "BLOCKED: venv Python iMac non trovato"; exit 2; }

ENV_FILE=""
for candidate in "$IMAC_REPO/voice-agent/.env" "$IMAC_REPO/.env"; do
    if [ -f "$candidate" ]; then ENV_FILE="$candidate"; break; fi
done
[ -n "$ENV_FILE" ] || { echo "BLOCKED: .env iMac non trovato"; exit 2; }

# Fetch refs only. Never checkout/reset/clean the canonical iMac worktree.
git -C "$IMAC_REPO" fetch --quiet origin
git -C "$IMAC_REPO" cat-file -e "$TARGET_SHA^{commit}" 2>/dev/null || {
    echo "BLOCKED: target SHA non disponibile su iMac: $TARGET_SHA"
    exit 2
}
[ ! -e "$WORKTREE" ] || { echo "BLOCKED: candidate worktree path esiste già: $WORKTREE"; exit 2; }
git -C "$IMAC_REPO" worktree add --detach --quiet "$WORKTREE" "$TARGET_SHA"

ACTUAL_SHA="$(git -C "$WORKTREE" rev-parse HEAD)"
[ "$ACTUAL_SHA" = "$TARGET_SHA" ] || {
    echo "BLOCKED: candidate SHA mismatch expected=$TARGET_SHA actual=$ACTUAL_SHA"
    exit 2
}
[ -z "$(git -C "$WORKTREE" status --porcelain)" ] || {
    echo "BLOCKED: candidate worktree non pulito"
    git -C "$WORKTREE" status --short
    exit 2
}

echo "IMAC_CANDIDATE_SHA=$ACTUAL_SHA"
echo "IMAC_CANONICAL_HEAD=$(git -C "$IMAC_REPO" rev-parse HEAD)"
echo "IMAC_CANONICAL_DIRTY_COUNT=$(git -C "$IMAC_REPO" status --porcelain | wc -l | tr -d ' ')"

CERT_SERVER="$WORKTREE/voice-agent/tests/e2e/cert_server.py"
RELEASE_GATE="$WORKTREE/voice-agent/tests/e2e/release_gate.py"
[ -f "$CERT_SERVER" ] || { echo "BLOCKED: cert_server.py assente nel candidato"; exit 2; }
[ -f "$RELEASE_GATE" ] || { echo "BLOCKED: release_gate.py assente nel candidato"; exit 2; }
"$PYTHON" -m py_compile "$CERT_SERVER" "$RELEASE_GATE"

# Fail if the candidate port is already occupied. Never kill an unknown process.
if curl -sf --max-time 1 "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    echo "BLOCKED: candidate port ${PORT} già occupata"
    exit 2
fi

nohup "$PYTHON" "$CERT_SERVER" \
    --env-file "$ENV_FILE" --sha "$TARGET_SHA" --host 127.0.0.1 --port "$PORT" \
    >"$LOG" 2>&1 &
PID=$!

echo "CERT_SERVER_PID=$PID"
echo "CERT_SERVER_LOG=$LOG"

HEALTH=""
for _ in $(seq 1 120); do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "BLOCKED: candidate server terminato durante startup"
        tail -80 "$LOG" || true
        exit 2
    fi
    HEALTH="$(curl -sf --max-time 2 "http://127.0.0.1:${PORT}/health" 2>/dev/null || true)"
    [ -n "$HEALTH" ] && break
    sleep 0.5
done
[ -n "$HEALTH" ] || {
    echo "BLOCKED: candidate health timeout"
    tail -80 "$LOG" || true
    exit 2
}

# Prove the running process was launched from this exact detached worktree.
CMD="$(ps -p "$PID" -o command= 2>/dev/null || true)"
printf '%s\n' "$CMD" | grep -F "$CERT_SERVER" >/dev/null || {
    echo "BLOCKED: runtime command non punta al candidate worktree"
    echo "command=$CMD"
    exit 2
}
[ "$(git -C "$WORKTREE" rev-parse HEAD)" = "$TARGET_SHA" ] || exit 2
[ -z "$(git -C "$WORKTREE" status --porcelain)" ] || exit 2

echo "CERT_RUNTIME_COMMAND=$CMD"
echo "CERT_RUNTIME_HEALTH=$HEALTH"
echo "CERT_RUNTIME_SHA=$TARGET_SHA"

set +e
cd "$WORKTREE/voice-agent"
PIPELINE_URL="http://127.0.0.1:${PORT}" \
    "$PYTHON" tests/e2e/release_gate.py \
    --release-gate --report="$REPORT" "${GATE_ARGS[@]}"
GATE_EXIT=$?
set -e

echo "REMOTE_GATE_EXIT=$GATE_EXIT"
[ -f "$REPORT" ] || { echo "BLOCKED: report non prodotto"; exit 2; }
exit "$GATE_EXIT"
REMOTE
GATE_EXIT=$?
set -e

# Report is intentionally outside the remote worktree and survives cleanup.
set +e
scp -q "${IMAC_HOST}:${REMOTE_REPORT}" "$LOCAL_REPORT"
SCP_EXIT=$?
set -e
if [ "$SCP_EXIT" -ne 0 ] || [ ! -s "$LOCAL_REPORT" ]; then
    echo "BLOCKED: report non recuperabile (remote gate exit=$GATE_EXIT)"
    ssh "$IMAC_HOST" "tail -100 '$REMOTE_LOG' 2>/dev/null || true" || true
    exit 2
fi

# The roadmap contract is P95 < 2000ms. The historical inner Python harness
# treated that value as WARN-only; the release wrapper is authoritative and
# upgrades an SLO miss to a hard release failure without hiding the raw verdict.
set +e
python3 - "$LOCAL_REPORT" "$TARGET_SHA" "$P95_SLO_MS" "$GATE_EXIT" <<'PYEOF'
import hashlib
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
target_sha = sys.argv[2]
slo = int(sys.argv[3])
remote_exit = int(sys.argv[4])
r = json.loads(path.read_text(encoding="utf-8"))
lat = r.get("latency") or {}
p95 = lat.get("p95_ms")
inner = r.get("verdict")
p95_ok = isinstance(p95, (int, float)) and p95 < slo
effective = remote_exit == 0 and inner == "PASS" and p95_ok
r["exact_sha_release_gate"] = {
    "target_sha": target_sha,
    "remote_gate_exit": remote_exit,
    "inner_verdict": inner,
    "p95_ms": p95,
    "p95_slo_ms": slo,
    "p95_slo_pass": p95_ok,
    "effective_verdict": "PASS" if effective else "FAIL",
}
path.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"TARGET_SHA={target_sha}")
print(f"INNER_VERDICT={inner}")
print(f"P95_MS={p95}")
print(f"P95_SLO_MS={slo}")
print(f"P95_SLO_PASS={p95_ok}")
print(f"EFFECTIVE_VERDICT={'PASS' if effective else 'FAIL'}")
print(f"REPORT_SHA256={hashlib.sha256(path.read_bytes()).hexdigest()}")
sys.exit(0 if effective else 1)
PYEOF
EFFECTIVE_EXIT=$?
set -e

echo "REPORT=$LOCAL_REPORT"
echo "--- REPORT ---"
cat "$LOCAL_REPORT"
echo "--- END REPORT ---"

if [ "$GATE_EXIT" -gt 1 ]; then
    echo "RELEASE GATE: INFRASTRUCTURE FAIL (remote exit=$GATE_EXIT)"
    exit 2
fi
if [ "$GATE_EXIT" -ne 0 ] || [ "$EFFECTIVE_EXIT" -ne 0 ]; then
    echo "RELEASE GATE: FAIL — behavior or P95 SLO blocked release"
    exit 1
fi

echo "RELEASE GATE: PASS — exact SHA, behavior green, P95 < ${P95_SLO_MS}ms"
exit 0
