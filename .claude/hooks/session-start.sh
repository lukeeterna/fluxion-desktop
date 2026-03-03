#!/bin/bash
# FLUXION SessionStart Hook
# Carica contesto e verifica ambiente all'avvio sessione

PROJECT_DIR="/Volumes/MontereyT7/FLUXION"
IMAC_HOST="imac"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           FLUXION - Session Start                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Mostra stato git
echo "📁 Git Status:"
cd "$PROJECT_DIR"
BRANCH=$(git branch --show-current 2>/dev/null)
COMMIT=$(git log --oneline -1 2>/dev/null)
echo "   Branch: $BRANCH"
echo "   Ultimo commit: $COMMIT"

# 2. Check modifiche non committate
CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHANGES" -gt 0 ]; then
    echo "   ⚠️  $CHANGES file modificati non committati"
fi

echo ""

# 3. Verifica servizi su iMac
echo "🖥️  Servizi iMac (192.168.1.2):"
if ping -c 1 -W 2 192.168.1.2 &>/dev/null; then
    # HTTP Bridge
    if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $IMAC_HOST "lsof -i :3001" &>/dev/null 2>&1; then
        echo "   ✅ HTTP Bridge (3001): ATTIVO"
    else
        echo "   ❌ HTTP Bridge (3001): NON ATTIVO"
    fi

    # Voice Pipeline
    if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $IMAC_HOST "lsof -i :3002" &>/dev/null 2>&1; then
        echo "   ✅ Voice Pipeline (3002): ATTIVO"
    else
        echo "   ❌ Voice Pipeline (3002): NON ATTIVO"
    fi
else
    echo "   ⚠️  iMac non raggiungibile"
fi

echo ""

# 4. Carica info progetto da CLAUDE.md
echo "📋 Stato Progetto (da CLAUDE.md):"
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
    # Estrai fase e ultimo update
    FASE=$(grep -m1 "^fase:" "$PROJECT_DIR/CLAUDE.md" | sed 's/fase: //')
    NOME=$(grep -m1 "^nome:" "$PROJECT_DIR/CLAUDE.md" | sed 's/nome: //' | tr -d '"')
    UPDATE=$(grep -m1 "^ultimo_update:" "$PROJECT_DIR/CLAUDE.md" | sed 's/ultimo_update: //')

    echo "   Fase: $FASE - $NOME"
    echo "   Ultimo update: $UPDATE"

    # Mostra task in corso
    echo ""
    echo "📌 Task In Corso:"
    grep -A1 "### In Corso" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | grep "^\- \[ \]" | head -3 | while read line; do
        echo "   $line"
    done
fi

echo ""

# 5. Carica HANDOFF.md + controlla staleness memoria
MEMORY_DIR="/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory"
HANDOFF="$MEMORY_DIR/HANDOFF.md"
MARKER_FILE="$HOME/.claude/cache/fluxion-memory-marker.json"

if [ -f "$HANDOFF" ]; then
    echo "🔄 HANDOFF SESSIONE PRECEDENTE:"
    # Mostra prossimi task da HANDOFF
    grep -A 8 "## 🎯 PROSSIMI TASK" "$HANDOFF" 2>/dev/null | head -8
    echo ""
    echo "   → Leggi HANDOFF.md completo per contesto pieno"
fi

# 6. Controlla se MEMORY è stale rispetto a git log
LAST_COMMIT_TIME=$(cd "$PROJECT_DIR" && git log -1 --format="%at" 2>/dev/null || echo 0)
HANDOFF_MTIME=$(stat -f %m "$HANDOFF" 2>/dev/null || echo 0)

if [ "$LAST_COMMIT_TIME" -gt "$HANDOFF_MTIME" ] 2>/dev/null; then
    LAST_COMMIT_MSG=$(cd "$PROJECT_DIR" && git log --oneline -1 2>/dev/null)
    echo "⚠️  MEMORY STALE — commit più recente di HANDOFF.md:"
    echo "   $LAST_COMMIT_MSG"
    echo "   → Aggiorna HANDOFF.md + MEMORY.md (CoVe 2026 FASE 5)"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo ""

# Set environment variables for Claude
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "export FLUXION_PROJECT_DIR=$PROJECT_DIR" >> "$CLAUDE_ENV_FILE"
    echo "export FLUXION_IMAC_HOST=$IMAC_HOST" >> "$CLAUDE_ENV_FILE"
fi

exit 0
