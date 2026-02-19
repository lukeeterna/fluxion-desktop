#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════════
# Fluxion - Build su iMac (via script remoto se possibile)
# ═════════════════════════════════════════════════════════════════════════════
# Questo script tenta di eseguire il build sull'iMac usando diversi metodi
# ═════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

IMAC_IP="192.168.1.7"
IMAC_PATH="/Volumes/MacSSD - Dati/fluxion"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FLUXION - Trigger Build iMac${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Metodo 1: SSH (se disponibile)
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}🔍 Tentativo connessione SSH all'iMac...${NC}"

if nc -z -w 2 "${IMAC_IP}" 22 2>/dev/null; then
    echo -e "${GREEN}✅ SSH disponibile!${NC}"
    echo -e "${YELLOW}🚀 Avvio build remoto via SSH...${NC}"
    
    ssh "${IMAC_IP}" "cd '${IMAC_PATH}' && ./build-fluxion.sh"
    
    echo ""
    echo -e "${GREEN}✅ Build remoto completato${NC}"
    
    # Scarica il bundle
    read -p "Scaricare il bundle DMG? (y/n): " DOWNLOAD
    if [ "$DOWNLOAD" = "y" ]; then
        BUNDLE_PATH="${IMAC_PATH}/src-tauri/target/release/bundle/dmg"
        DMG_FILE=$(ssh "${IMAC_IP}" "ls ${BUNDLE_PATH}/*.dmg 2>/dev/null | head -1")
        if [ -n "$DMG_FILE" ]; then
            echo -e "${YELLOW}📥 Download: $(basename $DMG_FILE)${NC}"
            scp "${IMAC_IP}:${DMG_FILE}" ./dist/
            echo -e "${GREEN}✅ Download completato in ./dist/${NC}"
        fi
    fi
    
    exit 0
else
    echo -e "${YELLOW}⚠️  SSH non disponibile sulla porta 22${NC}"
    echo -e "   ${CYAN}L'iMac richiede abilitazione manuale di Remote Login${NC}"
fi

echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Metodo 2: Istruzioni manuali
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📋 Istruzioni per build manuale sull'iMac:${NC}"
echo ""
echo -e "${CYAN}1. Sull'iMac, apri Terminal e esegui:${NC}"
echo ""
echo -e "   ${GREEN}cd '${IMAC_PATH}'${NC}"
echo -e "   ${GREEN}git pull origin master${NC}"
echo -e "   ${GREEN}npm install${NC}  ${YELLOW}# se package.json è cambiato${NC}"
echo -e "   ${GREEN}npm run type-check${NC}"
echo -e "   ${GREEN}cd src-tauri && cargo check --lib${NC}"
echo -e "   ${GREEN}npm run tauri build${NC}"
echo ""
echo -e "${CYAN}2. Una volta completato, il bundle sarà in:${NC}"
echo -e "   ${GREEN}${IMAC_PATH}/src-tauri/target/release/bundle/${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Stato Git attuale
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📊 Stato corrente:${NC}"
echo -e "   Branch: ${CYAN}$(git branch --show-current)${NC}"
echo -e "   Ultimo commit: ${CYAN}$(git log -1 --oneline)${NC}"
echo ""

# Verifica modifiche da pushare
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  ATTENZIONE: Ci sono modifiche non committate!${NC}"
    git status --short
    echo ""
    echo -e "${CYAN}Esegui prima:${NC} ${GREEN}./scripts/sync-to-imac.sh${NC}"
else
    COMMITS_AHEAD=$(git rev-list --count origin/$(git branch --show-current 2>/dev/null || echo 'master')..HEAD 2>/dev/null || echo "0")
    if [ "$COMMITS_AHEAD" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ATTENZIONE: ${COMMITS_AHEAD} commit non pushati!${NC}"
        echo -e "${CYAN}Esegui:${NC} ${GREEN}git push origin $(git branch --show-current)${NC}"
    else
        echo -e "${GREEN}✅ Codice sincronizzato con GitHub${NC}"
    fi
fi

echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Suggerimento per abilitare SSH
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}💡 Per abilitare SSH futuro sull'iMac:${NC}"
echo ""
echo -e "   1. Apri ${CYAN}Preferenze di Sistema > Condivisione${NC}"
echo -e "   2. Attiva ${CYAN}Accesso remoto${NC} (Remote Login)"
echo -e "   3. Aggiungi l'utente corrente agli utenti consentiti"
echo ""
echo -e "   Questo permetterà build automatici futuri."
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
