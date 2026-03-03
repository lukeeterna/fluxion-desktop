#!/bin/bash
# FLUXION Session End Hook (Stop)
# Scrive marker di sessione terminata e mostra reminder memory update

MEMORY_DIR="/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory"
CACHE_DIR="$HOME/.claude/cache"
MARKER_FILE="$CACHE_DIR/fluxion-memory-marker.json"
PROJECT_DIR="/Volumes/MontereyT7/FLUXION"

mkdir -p "$CACHE_DIR"

# Leggi ultimo commit
LAST_COMMIT=$(cd "$PROJECT_DIR" && git log --oneline -1 2>/dev/null || echo "N/A")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# Controlla se HANDOFF.md è più vecchio dell'ultimo commit
HANDOFF="$MEMORY_DIR/HANDOFF.md"
HANDOFF_MTIME=0
NEEDS_UPDATE=false

if [ -f "$HANDOFF" ]; then
  HANDOFF_MTIME=$(stat -f %m "$HANDOFF" 2>/dev/null || stat -c %Y "$HANDOFF" 2>/dev/null || echo 0)
fi

# Controlla marker da auto-memory.js
if [ -f "$MARKER_FILE" ]; then
  NEEDS_MEM=$(python3 -c "import json; d=json.load(open('$MARKER_FILE')); print(d.get('_needsMemoryUpdate', False))" 2>/dev/null || echo "False")
  if [ "$NEEDS_MEM" = "True" ]; then
    NEEDS_UPDATE=true
  fi
fi

# Scrivi marker sessione terminata
cat > "$MARKER_FILE" <<EOF
{
  "session_end": "$TIMESTAMP",
  "last_commit": "$LAST_COMMIT",
  "_needsMemoryUpdate": false,
  "_sessionClosed": true
}
EOF

# Mostra reminder solo se ci sono stati commit o aggiornamenti
if [ "$NEEDS_UPDATE" = "true" ]; then
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ⚡ FLUXION — Sessione terminata                             ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "  📝 Memory update pendente — CoVe 2026 FASE 5:"
  echo "     HANDOFF.md + MEMORY.md da aggiornare"
  echo ""
  echo "  Ultimo commit: $LAST_COMMIT"
  echo "  Timestamp:     $TIMESTAMP"
  echo ""
fi

exit 0
