#!/bin/bash
# FLUXION Service Check Hook
# Verifica che HTTP Bridge e Voice Pipeline siano attivi

IMAC_HOST="imac"
HTTP_BRIDGE_PORT=3001
VOICE_PIPELINE_PORT=3002

check_service() {
    local port=$1
    local name=$2
    if ssh -o ConnectTimeout=3 $IMAC_HOST "lsof -i :$port" &>/dev/null; then
        echo "✅ $name (porta $port): ATTIVO"
        return 0
    else
        echo "❌ $name (porta $port): NON ATTIVO"
        return 1
    fi
}

echo "═══════════════════════════════════════════"
echo "  FLUXION Service Status Check"
echo "═══════════════════════════════════════════"

# Check iMac connectivity
if ! ping -c 1 -W 2 192.168.1.2 &>/dev/null; then
    echo "⚠️  iMac non raggiungibile (192.168.1.2)"
    echo "   Servizi non verificabili"
    exit 0  # Non bloccare, solo warning
fi

ERRORS=0

check_service $HTTP_BRIDGE_PORT "HTTP Bridge (Tauri)" || ((ERRORS++))
check_service $VOICE_PIPELINE_PORT "Voice Pipeline (Python)" || ((ERRORS++))

echo "═══════════════════════════════════════════"

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "⚠️  $ERRORS servizio/i non attivo/i!"
    echo ""
    echo "Per avviare su iMac:"
    echo "  HTTP Bridge:    npm run tauri dev"
    echo "  Voice Pipeline: cd voice-agent && python main.py"
fi

exit 0  # Non bloccare Claude, solo informativo
