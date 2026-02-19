#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════════
# Fluxion Setup - Script per iMac Build Server
# ═════════════════════════════════════════════════════════════════════════════
# Da eseguire UNA VOLTA sull'iMac per configurare l'ambiente di build
# ═════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  FLUXION - Setup iMac Build Server${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Verifica prerequisiti
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}🔍 Verifica prerequisiti${NC}"

# Check Rust/Cargo
if command -v cargo &> /dev/null; then
    echo -e "${GREEN}✅ Cargo: $(cargo --version)${NC}"
else
    echo -e "${RED}❌ Cargo non trovato. Installa Rust:${NC}"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check rustc
if command -v rustc &> /dev/null; then
    echo -e "${GREEN}✅ Rustc: $(rustc --version)${NC}"
else
    echo -e "${RED}❌ Rust non trovato${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
else
    echo -e "${YELLOW}⚠️  Node.js non trovato. Installazione...${NC}"
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo -e "${RED}❌ Installa Node.js manualmente da https://nodejs.org${NC}"
        exit 1
    fi
fi

# Check Git
if command -v git &> /dev/null; then
    echo -e "${GREEN}✅ Git: $(git --version)${NC}"
else
    echo -e "${RED}❌ Git non trovato${NC}"
    exit 1
fi

echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Setup directory progetto
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📁 Setup directory progetto${NC}"

PROJECT_PATH="/Volumes/MacSSD - Dati/fluxion"

if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${YELLOW}📁 Creazione directory...${NC}"
    mkdir -p "$PROJECT_PATH"
fi

cd "$PROJECT_PATH"

# Clone repository se necessario
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 Clonazione repository...${NC}"
    read -p "GitHub username: " GH_USER
    git clone "https://github.com/${GH_USER}/fluxion-desktop.git" .
else
    echo -e "${GREEN}✅ Repository già presente${NC}"
fi

echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Installazione dipendenze
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}📦 Installazione dipendenze${NC}"

echo -e "   Installazione npm packages..."
npm install

echo -e "   ${GREEN}✅ Dipendenze installate${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Setup hook post-merge (auto-install dopo pull)
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}⚙️  Setup Git hooks${NC}"

mkdir -p .git/hooks

cat > .git/hooks/post-merge << 'HOOK'
#!/bin/bash
# Post-merge hook: auto-install dipendenze se package.json cambia

CHANGED_FILES=$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)

if echo "$CHANGED_FILES" | grep --quiet "package.json"; then
    echo "📦 package.json cambiato, esecuzione npm install..."
    npm install
fi

if echo "$CHANGED_FILES" | grep --quiet "Cargo.toml"; then
    echo "📦 Cargo.toml cambiato, aggiornamento dipendenze Rust..."
    cd src-tauri && cargo fetch
fi
HOOK

chmod +x .git/hooks/post-merge
echo -e "${GREEN}✅ Hook post-merge configurato${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Setup script build rapido
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}⚙️  Setup script build rapido${NC}"

cat > build-fluxion.sh << 'BUILDSCRIPT'
#!/bin/bash
# Build script rapido per Fluxion su iMac

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  FLUXION BUILD - iMac${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Pull ultimi cambiamenti
echo -e "${YELLOW}📥 Pull ultimi cambiamenti...${NC}"
git pull origin $(git branch --show-current)

# Verifica
echo -e "${YELLOW}🔍 Verifica TypeScript...${NC}"
npm run type-check

echo -e "${YELLOW}🔍 Verifica Rust...${NC}"
cd src-tauri
cargo check --lib

# Build
echo -e "${YELLOW}🔨 Build Tauri...${NC}"
cd ..
npm run tauri build

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  BUILD COMPLETATO ✅${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "App bundle in: ${CYAN}src-tauri/target/release/bundle/${NC}"
BUILDSCRIPT

chmod +x build-fluxion.sh
echo -e "${GREEN}✅ Script build-fluxion.sh creato${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# Configurazione completata
# ═════════════════════════════════════════════════════════════════════════════
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SETUP COMPLETATO ✅${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Comandi disponibili:${NC}"
echo ""
echo -e "   ${GREEN}./build-fluxion.sh${NC}        # Build completo"
echo -e "   ${GREEN}git pull && npm install${NC}   # Aggiornamento"
echo ""
echo -e "${YELLOW}Nota:${NC} Per abilitare SSH (opzionale):"
echo -e "      ${CYAN}System Preferences > Sharing > Remote Login${NC}"
