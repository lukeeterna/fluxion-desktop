#!/usr/bin/env bash
set -euo pipefail
REPO="/Volumes/MontereyT7/FLUXION"
cd "$REPO"
git rev-parse --is-inside-work-tree >/dev/null
test -f HANDOFF.md || { echo "FATAL: HANDOFF.md mancante"; exit 1; }
if git check-ignore -q HANDOFF.md; then echo "FATAL: HANDOFF.md è gitignored"; exit 1; fi
# VOS-HANDOFF-IGNORE: gli effimeri .claude/* sono gitignored e NON vengono più
# ne' stub-izzati ne' ri-aggiunti. L'UNICO handoff committato e' /HANDOFF.md (root).
git add HANDOFF.md CLAUDE.md scripts/vos-close.sh 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "chore(handoff): chiusura sessione — HANDOFF.md canonico"
  echo "COMMIT creato."
else
  echo "Nessuna modifica gestita da committare (idempotente, ok)."
fi
if git remote | grep -q .; then
  git push 2>&1 || echo "PUSH FALLITO/UPSTREAM ASSENTE — durabilità off-machine NON garantita"
else
  echo "NESSUN REMOTE — solo commit locale; off-machine durability assente (infra gap)"
fi
echo "HANDOFF.md aggiornato: $REPO/HANDOFF.md — incollalo al giudice."
echo "CHIUSURA OK · canonico: $REPO/HANDOFF.md"
