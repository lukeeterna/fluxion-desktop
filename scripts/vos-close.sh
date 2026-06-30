#!/usr/bin/env bash
set -euo pipefail
REPO="/Volumes/MontereyT7/FLUXION"
cd "$REPO"
git rev-parse --is-inside-work-tree >/dev/null
test -f HANDOFF.md || { echo "FATAL: HANDOFF.md mancante"; exit 1; }
if git check-ignore -q HANDOFF.md; then echo "FATAL: HANDOFF.md è gitignored"; exit 1; fi
STUB='<!-- VOS-STUB --> NON CANONICO. Lo stato di sessione vive in /HANDOFF.md (root repo, tracciato, pushato). Questo file è solo un puntatore.'
for f in .claude/HANDOFF_CURRENT.md .claude/NEXT_SESSION_PROMPT.md .claude/NEXT_SESSION_PROMPT.manual.md; do
  if [ -e "$f" ]; then printf '%s\n' "$STUB" > "$f"; fi
done
git add HANDOFF.md CLAUDE.md scripts/vos-close.sh 2>/dev/null || true
for f in .claude/HANDOFF_CURRENT.md .claude/NEXT_SESSION_PROMPT.md .claude/NEXT_SESSION_PROMPT.manual.md; do
  if [ -e "$f" ] && ! git check-ignore -q "$f"; then git add "$f"; fi
done
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
open -a TextEdit "$REPO/HANDOFF.md" || true
echo "CHIUSURA OK · canonico: $REPO/HANDOFF.md"
