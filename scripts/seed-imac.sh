#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# FLUXION - Script Seed Dati Test per iMac
# Esegue automaticamente il seed del database dopo installazione
# ═══════════════════════════════════════════════════════════════════

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  FLUXION - Seed Dati Test per iMac"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Trova il database FLUXION
DB_PATHS=(
    "$HOME/Library/Application Support/it.fluxion.app/fluxion.db"
    "$HOME/Library/Application Support/com.fluxion.desktop/fluxion.db"
    "$HOME/Library/Application Support/fluxion/fluxion.db"
)

DB_PATH=""
for path in "${DB_PATHS[@]}"; do
    if [ -f "$path" ]; then
        DB_PATH="$path"
        break
    fi
done

if [ -z "$DB_PATH" ]; then
    echo -e "${RED}ERRORE: Database FLUXION non trovato!${NC}"
    echo ""
    echo "Percorsi verificati:"
    for path in "${DB_PATHS[@]}"; do
        echo "  - $path"
    done
    echo ""
    echo -e "${YELLOW}Assicurati di aver avviato FLUXION almeno una volta.${NC}"
    exit 1
fi

echo -e "${GREEN}Database trovato:${NC} $DB_PATH"
echo ""

# Percorso script SQL
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="$SCRIPT_DIR/seed-test-data.sql"

if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}ERRORE: File seed-test-data.sql non trovato in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}Esecuzione seed...${NC}"
echo ""
echo -e "${CYAN}NOTA: API key Groq viene caricata automaticamente da .env${NC}"
echo ""

# Esegui SQL
sqlite3 "$DB_PATH" < "$SQL_FILE"

# Carica API key Groq da .env (se esiste)
ENV_FILE="$SCRIPT_DIR/../.env"
if [ -f "$ENV_FILE" ]; then
    GROQ_KEY=$(grep "^GROQ_API_KEY=" "$ENV_FILE" | cut -d'=' -f2)
    if [ -n "$GROQ_KEY" ]; then
        echo -e "${CYAN}Inserimento API key Groq...${NC}"
        sqlite3 "$DB_PATH" "INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo) VALUES ('fluxion_ia_key', '$GROQ_KEY', 'string');"
        echo -e "${GREEN}API key Groq inserita!${NC}"
    fi
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  SEED COMPLETATO CON SUCCESSO!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Dati inseriti:"
    echo "  - 3 Operatori"
    echo "  - 10 Servizi"
    echo "  - 10 Clienti (con soprannomi per WhatsApp)"
    echo "  - 7 Appuntamenti (oggi e prossimi giorni)"
    echo "  - 10 Incassi (ultimi 3 giorni)"
    echo "  - 3 Chiusure cassa"
    echo "  - 3 Fatture test"
    echo "  - 3 Pacchetti cliente"
    echo "  - 3 Template WhatsApp"
    echo "  - 3 FAQ custom apprese"
    echo "  - Impostazioni + API Groq"
    echo ""
    echo -e "${CYAN}Ora puoi avviare FLUXION e testare tutte le funzionalita!${NC}"
else
    echo -e "${RED}ERRORE durante l'esecuzione del seed${NC}"
    exit 1
fi
