#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

result() {
  local status="$1" label="$2"
  if [ "$status" = "PASS" ]; then
    echo "PASS $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label"
    FAIL=$((FAIL + 1))
  fi
}

# a) HEAD == origin/master
LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse origin/master 2>/dev/null)
[ "$LOCAL" = "$REMOTE" ] && result PASS "a) HEAD==origin/master" || result FAIL "a) HEAD!=origin/master ($LOCAL vs $REMOTE)"

# b) porcelain vuoto salvo carve-out
# Carve-out dichiarati (tutti volatili, nessuna semantica VOS):
#   tools/VectCutAPI            — submodule pointer, non sorgente applicativo
#   src-tauri/fluxion.db*       — DB runtime, modificato dal voice agent in produzione
#   vos-out/decisions.jsonl     — log append-only VOS
#   .claude/session_state.md    — debug log PreCompact (pre-compact.sh), volatile, derivabile da git log
#   .claude/NEXT_SESSION_PROMPT.md — log auto-generato da global_session_end.sh (AUTO_SENTINEL riga 1),
#                                    non contiene direttive operative CC; handoff operativi → HANDOFF.md (R25)
DIRTY=$(git status --porcelain \
  | grep -v '^\(.\{0\}\| M\|M \| R\|R \) tools/VectCutAPI' \
  | grep -v 'src-tauri/fluxion\.db' \
  | grep -v 'vos-out/decisions\.jsonl' \
  | grep -v '\.claude/session_state\.md' \
  | grep -v '\.claude/NEXT_SESSION_PROMPT\.md' \
  || true)
[ -z "$DIRTY" ] && result PASS "b) porcelain-clean-salvo-carveout" || result FAIL "b) porcelain-dirty: $(echo "$DIRTY" | head -3)"

# c) STATE.md e PROTOCOLLO.md esistono e non vuoti
[ -s "docs/judge/STATE.md" ]     && result PASS "c) docs/judge/STATE.md esiste" || result FAIL "c) docs/judge/STATE.md mancante/vuoto"
[ -s "docs/judge/PROTOCOLLO.md" ] && result PASS "c) docs/judge/PROTOCOLLO.md esiste" || result FAIL "c) docs/judge/PROTOCOLLO.md mancante/vuoto"

# d) HEAD ATTESO in STATE.md è antenato di HEAD (o uguale)
ATTESO=$(grep 'HEAD ATTESO:' docs/judge/STATE.md 2>/dev/null | awk '{print $NF}' | head -1)
if git merge-base --is-ancestor "$ATTESO" HEAD 2>/dev/null; then
  result PASS "d) STATE.md HEAD ATTESO ($ATTESO) raggiungibile da HEAD"
else
  result FAIL "d) STATE.md HEAD ATTESO ($ATTESO) NON raggiungibile da HEAD"
fi

# e) RIMOSSO — NEXT_SESSION_PROMPT.md è prodotto da global_session_end.sh ad ogni Stop,
#    ha AUTO_SENTINEL in riga 1, contenuto volatile senza semantica operativa CC.
#    L'invariante "nessun handoff in prosa fuori HANDOFF.md" è coperta dal controllo f) e da R25.
#    Un handoff manuale (operativo) verrebbe spostato a NEXT_SESSION_PROMPT.manual.md dall'hook stesso.

# f) HANDOFF.md NON esiste alla root
[ ! -f "HANDOFF.md" ] && result PASS "f) HANDOFF.md assente da root" || result FAIL "f) HANDOFF.md PRESENTE a root (DISCORDANZA)"

# g) runtime :3002 — il repo della macchina runtime deve coincidere con origin/master e voice-agent/ deve essere pulito
# Verifica via SSH (canale sempre disponibile dal MacBook). Se SSH fallisce: runtime non verificabile → FAIL (mai passare in silenzio).
RUNTIME_HOST="192.168.1.2"
RUNTIME_PATH="/Volumes/MacSSD - Dati/fluxion"
IMAC_HEAD=$(ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes \
  gianlucadistasi@"${RUNTIME_HOST}" \
  "cd '${RUNTIME_PATH}' && git rev-parse HEAD" 2>/dev/null || echo "UNREACHABLE")
if [ "$IMAC_HEAD" = "UNREACHABLE" ]; then
  result FAIL "g) runtime iMac (${RUNTIME_HOST}) non raggiungibile via SSH — runtime non verificabile"
else
  # Solo file tracked modificati (esclude ?? untracked — binari compilati, cache)
  IMAC_DIRTY=$(ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes \
    gianlucadistasi@"${RUNTIME_HOST}" \
    "cd '${RUNTIME_PATH}' && git status --porcelain voice-agent/ 2>/dev/null | grep -v '^??' || true" 2>/dev/null || echo "UNREACHABLE")
  ORIGIN_HEAD=$(git rev-parse origin/master 2>/dev/null)
  if [ "$IMAC_HEAD" != "$ORIGIN_HEAD" ]; then
    result FAIL "g) runtime iMac HEAD ($IMAC_HEAD) != origin/master ($ORIGIN_HEAD)"
  elif [ "$IMAC_DIRTY" = "UNREACHABLE" ] || [ -n "$IMAC_DIRTY" ]; then
    result FAIL "g) runtime iMac voice-agent/ tracked-dirty o non verificabile: $(echo "$IMAC_DIRTY" | head -3)"
  else
    result PASS "g) runtime iMac HEAD==origin/master e voice-agent/ pulito ($IMAC_HEAD)"
  fi
fi

# h) IMAC-PULSE.json esiste e non è stale (< 24h)
if python3 bin/vos_imac_pulse.py check 2>/dev/null; then
  result PASS "h) IMAC-PULSE.json fresco (< 24h)"
else
  result FAIL "h) IMAC-PULSE.json assente o stale (> 24h)"
fi

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
