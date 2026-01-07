#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# FLUXION - Script pulizia cache Windsurf
# Eseguire con: bash scripts/clean_windsurf_cache.sh
# Per installare come cron permanente: bash scripts/clean_windsurf_cache.sh --install
# ═══════════════════════════════════════════════════════════════════

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Percorsi cache Windsurf su macOS
WINDSURF_CACHE_PATHS=(
    "$HOME/Library/Application Support/Windsurf/Cache"
    "$HOME/Library/Application Support/Windsurf/CachedData"
    "$HOME/Library/Application Support/Windsurf/CachedExtensionVSIXs"
    "$HOME/Library/Application Support/Windsurf/CachedExtensions"
    "$HOME/Library/Application Support/Windsurf/GPUCache"
    "$HOME/Library/Caches/Windsurf"
)

# Funzione pulizia
clean_cache() {
    echo -e "${YELLOW}🧹 Pulizia cache Windsurf...${NC}"

    total_freed=0

    for path in "${WINDSURF_CACHE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            # Calcola dimensione prima
            size_before=$(du -sk "$path" 2>/dev/null | cut -f1)

            # Rimuovi contenuto
            rm -rf "$path"/*

            echo -e "${GREEN}  ✓ Pulito: $path${NC}"
            echo -e "    Liberati: ${size_before}KB"
            total_freed=$((total_freed + size_before))
        else
            echo -e "  ⚪ Non trovato: $path"
        fi
    done

    echo ""
    echo -e "${GREEN}✅ Pulizia completata!${NC}"
    echo -e "   Spazio totale liberato: $((total_freed / 1024))MB"
    echo ""
}

# Funzione installazione cron
install_cron() {
    echo -e "${YELLOW}📅 Installazione job pulizia automatica...${NC}"

    # Percorso assoluto dello script
    SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/clean_windsurf_cache.sh"

    # Crea LaunchAgent per macOS (esegue ogni giorno alle 03:00)
    PLIST_PATH="$HOME/Library/LaunchAgents/com.fluxion.windsurf-cache-clean.plist"

    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fluxion.windsurf-cache-clean</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardErrorPath</key>
    <string>/tmp/windsurf-cache-clean.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/windsurf-cache-clean.log</string>
</dict>
</plist>
EOF

    # Carica il LaunchAgent
    launchctl unload "$PLIST_PATH" 2>/dev/null
    launchctl load "$PLIST_PATH"

    echo -e "${GREEN}✅ LaunchAgent installato!${NC}"
    echo -e "   Path: $PLIST_PATH"
    echo -e "   Esecuzione: ogni giorno alle 03:00"
    echo ""
    echo -e "Per disinstallare:"
    echo -e "   launchctl unload $PLIST_PATH"
    echo -e "   rm $PLIST_PATH"
}

# Funzione disinstallazione
uninstall_cron() {
    PLIST_PATH="$HOME/Library/LaunchAgents/com.fluxion.windsurf-cache-clean.plist"

    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
        rm "$PLIST_PATH"
        echo -e "${GREEN}✅ LaunchAgent disinstallato${NC}"
    else
        echo -e "${YELLOW}⚠️ LaunchAgent non trovato${NC}"
    fi
}

# Main
case "$1" in
    --install)
        install_cron
        ;;
    --uninstall)
        uninstall_cron
        ;;
    *)
        clean_cache
        ;;
esac
