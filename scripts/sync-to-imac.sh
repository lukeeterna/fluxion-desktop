#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════════
# Fluxion Git-Centric Workflow - Sync to iMac Build Server
# ═════════════════════════════════════════════════════════════════════════════
# Uso: ./scripts/sync-to-imac.sh [options]
# 
# Options:
#   --force         Salta verifiche e pusha comunque
#   --no-verify     Salta type-check (non consigliato)
#   --help          Mostra questo help
# ═════════════════════════════════════════════════════════════════════════════

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
FORCE=false
NO_VERIFY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --no-verify)
            NO_VERIFY=true
            shift
            ;;
        --help)
            echo "Uso: ./scripts/sync-to-imac.sh [options]"
            echo ""
            echo "Options:"
            echo "  --force         Salta verifiche e pusha comunque"
            echo "  --no-verify     Salta type-check (non consigliato)"
            echo "  --help          Mostra questo help"
            exit 0
            ;;
        *)
            echo -e "${RED}Opzione sconosciuta: $1${NC}"
            exit 1
            ;;
    esac
done

# Configurazione
GIT_BRANCH=$(git branch --show-current)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BUILD_TAG="build-imac-${TIMESTAMP}"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FLUXION Git-Centric Workflow - Sync to iMac${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1: Verifica Preliminari
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📋 Step 1: Verifica preliminari${NC}"

# Verifica siamo nel repo corretto
if [ ! -f "package.json" ] || [ ! -d "src-tauri" ]; then
    echo -e "${RED}❌ Errore: Non sei nella root del progetto Fluxion${NC}"
    exit 1
fi

# Verifica Git remote configurato
if ! git remote get-url origin &>/dev/null; then
    echo -e "${RED}❌ Errore: Git remote 'origin' non configurato${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Repository verificato${NC}"
echo -e "   Branch: ${CYAN}${GIT_BRANCH}${NC}"
echo -e "   Remote: ${CYAN}$(git remote get-url origin)${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 2: Type-Check (se non disabilitato)
# ═════════════════════════════════════════════════════════════════════════════
if [ "$NO_VERIFY" = false ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}🔍 Step 2: TypeScript Type-Check${NC}"
    
    if npm run type-check 2>&1; then
        echo -e "${GREEN}✅ Type-check passato${NC}"
    else
        echo -e "${RED}❌ Type-check fallito!${NC}"
        echo -e "   Correggi gli errori prima di procedere"
        echo -e "   Oppure usa ${YELLOW}--no-verify${NC} per saltare (non consigliato)"
        exit 1
    fi
    echo ""
fi

# ═════════════════════════════════════════════════════════════════════════════
# STEP 3: Gestione Modifiche
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📦 Step 3: Gestione modifiche Git${NC}"

if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Modifiche non committate:${NC}"
    git status --short
    echo ""
    
    read -p "Committare automaticamente? (y/n): " AUTO_COMMIT
    if [ "$AUTO_COMMIT" = "y" ]; then
        read -p "Messaggio commit [sync: Auto-commit pre-build ${TIMESTAMP}]: " COMMIT_MSG
        git add -A
        git commit -m "${COMMIT_MSG:-sync: Auto-commit pre-build ${TIMESTAMP}}"
        echo -e "${GREEN}✅ Commit creato${NC}"
    else
        echo -e "${YELLOW}⚠️  Modifiche non committate - push annullato${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Working directory pulita${NC}"
fi
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 4: Push a GitHub
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}🚀 Step 4: Push a GitHub${NC}"

# Crea tag per tracciare il build
if git rev-parse "${BUILD_TAG}" &>/dev/null; then
    git tag -d "${BUILD_TAG}" 2>/dev/null || true
fi
git tag "${BUILD_TAG}"

echo -e "   Tag creato: ${CYAN}${BUILD_TAG}${NC}"

# Push branch e tag
if git push origin "${GIT_BRANCH}" && git push origin "${BUILD_TAG}"; then
    echo -e "${GREEN}✅ Push completato${NC}"
else
    echo -e "${RED}❌ Push fallito${NC}"
    exit 1
fi
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: Istruzioni per iMac
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📋 Step 5: Prossimi passaggi sull'iMac${NC}"
echo ""
echo -e "${CYAN}Esegui questi comandi sull'iMac:${NC}"
echo ""
echo -e "   ${GREEN}cd '/Volumes/MacSSD - Dati/fluxion'${NC}"
echo -e "   ${GREEN}git pull origin master${NC}"
echo -e "   ${GREEN}npm install${NC}  ${YELLOW}# solo se package.json cambiato${NC}"
echo -e "   ${GREEN}cd src-tauri && cargo check --lib${NC}"
echo -e "   ${GREEN}npm run tauri build${NC}"
echo ""

# Salva stato per tracking
echo "${BUILD_TAG},${GIT_BRANCH},$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> .build-history.csv 2>/dev/null || true

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SYNC COMPLETATO ✅${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Tag build: ${CYAN}${BUILD_TAG}${NC}"
echo -e "Branch: ${CYAN}${GIT_BRANCH}${NC}"
echo ""
echo -e "${YELLOW}Nota:${NC} SSH all'iMac non è disponibile (porta 22 chiusa)"
echo -e "      Il build deve essere avviato manualmente sull'iMac"
