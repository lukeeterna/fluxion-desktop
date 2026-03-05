#!/bin/bash
# PreCompact hook — salva stato sessione prima di /compact
{
  echo "## Session State $(date '+%Y-%m-%d %H:%M')"
  echo "Branch: $(git branch --show-current)"
  echo "Last commit: $(git log --oneline -1)"
  echo ""
  echo "Modified files:"
  git status --short | head -15
  echo ""
  echo "Phase from HANDOFF:"
  head -5 HANDOFF.md
} > .claude/session_state.md
echo "✅ session_state.md aggiornato ($(wc -l < .claude/session_state.md | tr -d ' ') righe)"
