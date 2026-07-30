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
DIRTY=$(git status --porcelain | grep -v '^\(.\{0\}\| M\|M \| R\|R \) tools/VectCutAPI' | grep -v 'src-tauri/fluxion\.db' | grep -v 'vos-out/decisions\.jsonl' || true)
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

# e) .claude/NEXT_SESSION_PROMPT.md NON esiste
[ ! -f ".claude/NEXT_SESSION_PROMPT.md" ] && result PASS "e) NEXT_SESSION_PROMPT.md assente" || result FAIL "e) NEXT_SESSION_PROMPT.md PRESENTE"

# f) HANDOFF.md NON esiste alla root
[ ! -f "HANDOFF.md" ] && result PASS "f) HANDOFF.md assente da root" || result FAIL "f) HANDOFF.md PRESENTE a root (DISCORDANZA)"

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
