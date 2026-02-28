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

# 5. Carica HANDOFF.md se esiste (resume da sessione precedente)
MEMORY_DIR="/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory"
HANDOFF="$MEMORY_DIR/HANDOFF.md"
if [ -f "$HANDOFF" ]; then
    echo "🔄 HANDOFF SESSIONE PRECEDENTE:"
    # Mostra solo le prime 20 righe significative
    grep -A 20 "## Stato al Momento" "$HANDOFF" 2>/dev/null | head -20
    echo ""
    echo "   → Leggi HANDOFF.md completo per contesto pieno"
fi

echo "═══════════════════════════════════════════════════════════════"
echo ""

# Set environment variables for Claude
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "export FLUXION_PROJECT_DIR=$PROJECT_DIR" >> "$CLAUDE_ENV_FILE"
    echo "export FLUXION_IMAC_HOST=$IMAC_HOST" >> "$CLAUDE_ENV_FILE"
fi

exit 0
