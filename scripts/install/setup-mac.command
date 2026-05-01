#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# FLUXION — Setup macOS post-installazione (S184 α.2)
# Rimuove com.apple.quarantine xattr da Fluxion.app per evitare loop Gatekeeper
# Distribuito dentro il DMG accanto a Fluxion.app
# ═══════════════════════════════════════════════════════════════════

set -u

APP_PATH="/Applications/Fluxion.app"
LOG_FILE="${HOME}/Library/Logs/Fluxion/setup-mac.log"

mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════════"
echo "  FLUXION — Setup macOS post-installazione"
echo "  $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ── 1. Verifica installazione ────────────────────────────────────
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Errore: Fluxion.app NON trovato in /Applications/"
    echo ""
    echo "   Prima di lanciare questo script:"
    echo "   1. Apri il file Fluxion_1.0.1_x64.dmg"
    echo "   2. Trascina Fluxion.app nella cartella Applicazioni"
    echo "   3. Torna qui e fai doppio-click su questo script"
    echo ""
    read -r -p "Premi INVIO per chiudere..."
    exit 1
fi

echo "✓ Fluxion.app trovato in /Applications/"
echo ""

# ── 2. Mostra attributi correnti ─────────────────────────────────
QUARANTINE=$(xattr "$APP_PATH" 2>/dev/null | grep -c "com.apple.quarantine" || true)
if [ "$QUARANTINE" -eq 0 ]; then
    echo "✓ Attributo quarantine già rimosso. Nessuna azione necessaria."
    echo ""
    echo "  Puoi avviare Fluxion da Launchpad o da /Applications/Fluxion.app"
    echo ""
    read -r -p "Premi INVIO per chiudere..."
    exit 0
fi

# ── 3. Richiede sudo + rimuove quarantine ────────────────────────
echo "Sto rimuovendo l'attributo Gatekeeper (richiede password Mac)..."
echo "Questo serve a evitare che macOS chieda conferma a ogni avvio."
echo ""

if ! sudo -v; then
    echo "❌ Password non valida o accesso negato."
    echo "   Riprova oppure contatta supporto: fluxion.gestionale@gmail.com"
    read -r -p "Premi INVIO per chiudere..."
    exit 1
fi

sudo xattr -dr com.apple.quarantine "$APP_PATH"
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo "❌ Errore rimozione quarantine (exit code $RESULT)."
    echo "   Controlla il log: $LOG_FILE"
    read -r -p "Premi INVIO per chiudere..."
    exit $RESULT
fi

# ── 4. Verifica finale ───────────────────────────────────────────
QUARANTINE_AFTER=$(xattr "$APP_PATH" 2>/dev/null | grep -c "com.apple.quarantine" || true)
if [ "$QUARANTINE_AFTER" -ne 0 ]; then
    echo "⚠️  Attributo ancora presente dopo rimozione. Riavvia Mac e riprova."
    read -r -p "Premi INVIO per chiudere..."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✓ SETUP COMPLETATO"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Ora puoi avviare Fluxion normalmente:"
echo "    • Launchpad → cerca \"Fluxion\""
echo "    • Oppure: /Applications/Fluxion.app"
echo ""
echo "  Log salvato in: $LOG_FILE"
echo ""
read -r -p "Premi INVIO per chiudere..."
exit 0
