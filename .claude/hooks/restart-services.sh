#!/bin/bash
# FLUXION Service Restart Script
# Riavvia i servizi su iMac

IMAC_HOST="imac"
FLUXION_PATH="/Volumes/MacSSD - Dati/fluxion"

echo "🔄 Riavvio servizi FLUXION su iMac..."
echo ""

# 1. Riavvia Voice Pipeline
echo "1. Riavvio Voice Pipeline..."
ssh $IMAC_HOST "bash -l -c 'pkill -f \"python main.py\" 2>/dev/null || true'"
sleep 2
ssh $IMAC_HOST "bash -l -c 'cd \"$FLUXION_PATH/voice-agent\" && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &'"
echo "   ✅ Voice Pipeline riavviato"

# 2. Verifica HTTP Bridge (non riavviare Tauri automaticamente)
echo ""
echo "2. Verifica HTTP Bridge..."
if ssh -o ConnectTimeout=3 $IMAC_HOST "lsof -i :3001" &>/dev/null; then
    echo "   ✅ HTTP Bridge già attivo"
else
    echo "   ⚠️  HTTP Bridge non attivo"
    echo "   Per avviare manualmente su iMac:"
    echo "   cd \"$FLUXION_PATH\" && npm run tauri dev"
fi

echo ""
echo "═══════════════════════════════════════════"

# Verifica finale
sleep 3
echo ""
echo "📊 Stato finale:"
if ssh -o ConnectTimeout=3 $IMAC_HOST "lsof -i :3001" &>/dev/null; then
    echo "   ✅ HTTP Bridge (3001): ATTIVO"
else
    echo "   ❌ HTTP Bridge (3001): NON ATTIVO"
fi

if ssh -o ConnectTimeout=3 $IMAC_HOST "lsof -i :3002" &>/dev/null; then
    echo "   ✅ Voice Pipeline (3002): ATTIVO"
else
    echo "   ❌ Voice Pipeline (3002): NON ATTIVO"
fi

exit 0
