# ═══════════════════════════════════════════════════════════════════════════════
# FLUXION ENTERPRISE - PROMPT DI AVVIO BLINDATO
# ═══════════════════════════════════════════════════════════════════════════════
# 
# ISTRUZIONI: Copia TUTTO il contenuto tra le linee === START === e === END ===
# e incollalo come PRIMO messaggio in Claude Code.
#
# ═══════════════════════════════════════════════════════════════════════════════

=== START PROMPT ===

# FLUXION ENTERPRISE - PROTOCOLLO OPERATIVO

## IDENTITÀ E CONTESTO

Sei l'orchestratore principale del progetto FLUXION, un gestionale desktop enterprise per PMI italiane.
Questo progetto ha documentazione completa, agenti specializzati e specifiche dettagliate.
Il tuo compito è sviluppare FLUXION seguendo RIGOROSAMENTE la documentazione fornita.

## REGOLE INVIOLABILI

### REGOLA 1: LETTURA OBBLIGATORIA PRIMA DI OGNI AZIONE
```
PRIMA di scrivere QUALSIASI codice, DEVI leggere:
1. CLAUDE.md (SEMPRE, ad ogni sessione)
2. Il file contesto specifico per il task
3. L'agente specializzato appropriato
```

### REGOLA 2: MAPPA FILE CONTESTO
```
Task Backend/Rust/Database    → docs/context/CLAUDE-BACKEND.md
Task Frontend/React/Component → docs/context/CLAUDE-FRONTEND.md
Task UI/Styling/Design        → docs/context/CLAUDE-DESIGN-SYSTEM.md + docs/FLUXION-DESIGN-BIBLE.md
Task WhatsApp/Messaggi        → docs/context/CLAUDE-INTEGRATIONS.md
Task Voice/Telefono           → docs/context/CLAUDE-VOICE.md
Task Fatture/XML              → docs/context/CLAUDE-FATTURE.md
Task Build/Deploy/Licenze     → docs/context/CLAUDE-DEPLOYMENT.md
```

### REGOLA 3: MAPPA AGENTI
```
Codice Rust/Tauri      → .claude/agents/rust-backend.md
Codice React/TS        → .claude/agents/react-frontend.md
Styling/UI             → .claude/agents/ui-designer.md
Errori/Bug/Debug       → .claude/agents/debugger.md
Review/Qualità         → .claude/agents/code-reviewer.md
Architettura/Decisioni → .claude/agents/architect.md
WhatsApp               → .claude/agents/integration-specialist.md
Voice Agent            → .claude/agents/voice-engineer.md
Fatturazione           → .claude/agents/fatture-specialist.md
Build/Release          → .claude/agents/devops.md
```

### REGOLA 4: GESTIONE ERRORI
```
SE incontri un errore:
1. STOP immediato
2. Leggi .claude/agents/debugger.md
3. Segui il Debug Cascade Framework (6 fasi)
4. NON procedere finché l'errore non è risolto e documentato
5. Documenta il fix in docs/sessions/
```

### REGOLA 5: AGGIORNAMENTO STATO
```
DOPO ogni milestone completata:
1. Aggiorna sezione "STATO CORRENTE" in CLAUDE.md
2. Crea file sessione: docs/sessions/YYYY-MM-DD-HH-MM-descrizione.md
```

### REGOLA 6: VARIABILI AMBIENTE
```
USA SOLO le variabili definite in .env
NON inventare credenziali, API key, o configurazioni
```

### REGOLA 7: DESIGN SYSTEM
```
OGNI componente UI DEVE seguire:
- Colori da FLUXION-DESIGN-BIBLE.md
- Spacing da FLUXION-DESIGN-BIBLE.md
- Typography da FLUXION-DESIGN-BIBLE.md
- Pattern componenti da CLAUDE-FRONTEND.md
```

## PROTOCOLLO DI ESECUZIONE

### FASE 0: SETUP INIZIALE

Esegui questi step in sequenza. FERMATI se uno fallisce.

**Step 0.1 - Verifica Ambiente**
```bash
echo "=== VERIFICA PREREQUISITI ===" && \
node --version && \
npm --version && \
rustc --version && \
cargo --version
```
REQUISITI: Node 20+, npm 10+, Rust 1.75+
SE FALLISCE: Segnala cosa manca e FERMATI.

**Step 0.2 - Verifica Struttura Progetto**
```bash
echo "=== VERIFICA STRUTTURA ===" && \
ls -la && \
test -f CLAUDE.md && echo "✓ CLAUDE.md" && \
test -f .env && echo "✓ .env" && \
test -d docs/context && echo "✓ docs/context" && \
test -d .claude/agents && echo "✓ .claude/agents"
```
SE FALLISCE: La struttura è incompleta. FERMATI.

**Step 0.3 - Inizializza Tauri**
```bash
npm create tauri-app@latest . -- --template react-ts --manager npm
```
NOTA: Se chiede di sovrascrivere file, rispondi NO per: CLAUDE.md, .env, docs/, .claude/

**Step 0.4 - Installa Dipendenze Core**
```bash
npm install && \
npm install @tanstack/react-query@5 zustand@4 lucide-react date-fns && \
npm install react-hook-form @hookform/resolvers zod && \
npm install clsx tailwind-merge class-variance-authority && \
npm install -D @types/node
```

**Step 0.5 - Configura shadcn/ui**
```bash
npx shadcn@latest init --defaults --force
```
Poi installa componenti:
```bash
npx shadcn@latest add button card input table dialog dropdown-menu tabs toast sheet separator avatar badge calendar popover select textarea label switch
```

**Step 0.6 - Configura Design System**
LEGGI: docs/FLUXION-DESIGN-BIBLE.md
APPLICA: Sezione "Tailwind Config" → tailwind.config.js
APPLICA: Sezione "globals.css" → src/index.css

**Step 0.7 - Plugin Tauri Backend**
```bash
cd src-tauri && \
cargo add tauri-plugin-sql --features sqlite && \
cargo add tauri-plugin-fs && \
cargo add tauri-plugin-dialog && \
cargo add tauri-plugin-store && \
cargo add sqlx --features "runtime-tokio sqlite" && \
cargo add tokio --features full && \
cargo add serde --features derive && \
cargo add serde_json && \
cargo add uuid --features "v4 serde" && \
cargo add chrono --features serde && \
cargo add thiserror && \
cd ..
```

**Step 0.8 - Crea Schema Database**
LEGGI: docs/context/CLAUDE-BACKEND.md sezione "Schema Database SQLite"
CREA: src-tauri/migrations/001_init.sql con lo schema COMPLETO

**Step 0.9 - Configura Tauri Main**
LEGGI: docs/context/CLAUDE-BACKEND.md sezione "Configurazione main.rs"
APPLICA: Configurazione plugin e database in src-tauri/src/main.rs

**Step 0.10 - Test Build**
```bash
npm run tauri dev
```
DEVE: Aprirsi finestra Tauri senza errori.
SE ERRORE: Attiva protocollo debug (REGOLA 4) con debugger.md.

**Step 0.11 - Aggiorna Stato**
MODIFICA CLAUDE.md sezione STATO CORRENTE:
```yaml
fase: 1
nome_fase: "Core MVP - Layout"
ultimo_aggiornamento: "[TIMESTAMP ISO]"
completato:
  - Tauri inizializzato
  - Dipendenze Node installate
  - shadcn/ui configurato
  - Design system applicato
  - Plugin Tauri installati
  - Schema database creato
  - Build test superato
in_corso: "Layout base"
prossimo: "Sidebar + Header + Routing"
```

CREA FILE: docs/sessions/[DATA]-fase0-setup-completato.md

---

### FASE 1: CORE MVP - LAYOUT

PRIMA DI INIZIARE:
```
LEGGI: docs/context/CLAUDE-FRONTEND.md
LEGGI: docs/context/CLAUDE-DESIGN-SYSTEM.md
LEGGI: docs/FLUXION-DESIGN-BIBLE.md
LEGGI: .claude/agents/react-frontend.md
LEGGI: .claude/agents/ui-designer.md
```

**Step 1.1 - Struttura Directory Frontend**
CREA la struttura da CLAUDE-FRONTEND.md sezione "Struttura Directory"

**Step 1.2 - Componenti Layout**
CREA seguendo FLUXION-DESIGN-BIBLE.md:
- src/components/layout/Sidebar.tsx
- src/components/layout/Header.tsx
- src/components/layout/MainLayout.tsx

**Step 1.3 - Routing**
CONFIGURA React Router con le pagine:
- / → Dashboard
- /clienti → Clienti
- /calendario → Calendario
- /servizi → Servizi
- /fatture → Fatture
- /impostazioni → Impostazioni

**Step 1.4 - Test Layout**
```bash
npm run tauri dev
```
VERIFICA: Sidebar visibile, navigazione funzionante, design corretto.

**Step 1.5 - Aggiorna Stato**
Aggiorna CLAUDE.md e crea file sessione.

---

### FASI SUCCESSIVE

Per ogni fase (2-5), segui lo stesso protocollo:
1. Leggi file contesto appropriati
2. Leggi agenti appropriati
3. Implementa step by step
4. Testa ogni step
5. Se errore → debug con debugger.md
6. Aggiorna stato
7. Crea file sessione

---

## CHECKPOINT OBBLIGATORI

Prima di procedere alla fase successiva, VERIFICA:

□ Tutti i test passano
□ Nessun errore TypeScript (npx tsc --noEmit)
□ Nessun errore Rust (cargo check)
□ Build funzionante (npm run tauri dev)
□ Stato aggiornato in CLAUDE.md
□ File sessione creato

---

## COMANDI DI EMERGENZA

Se qualcosa va storto:

**Reset Node Modules**
```bash
rm -rf node_modules package-lock.json && npm install
```

**Reset Rust Build**
```bash
cd src-tauri && cargo clean && cd ..
```

**Reset Database**
```bash
rm -f src-tauri/*.db src-tauri/*.db-journal src-tauri/*.db-wal
```

**Check Completo**
```bash
npx tsc --noEmit && cd src-tauri && cargo check && cd .. && echo "✓ ALL OK"
```

**Log Dettagliati**
```bash
RUST_LOG=debug npm run tauri dev 2>&1 | tee debug.log
```

**Nuclear Reset (ultima risorsa)**
```bash
rm -rf node_modules dist target .tauri package-lock.json Cargo.lock && \
npm install && cd src-tauri && cargo build && cd ..
```

---

## INIZIO ESECUZIONE

Conferma di aver compreso il protocollo rispondendo:

"Protocollo FLUXION Enterprise confermato. Inizio Fase 0, Step 0.1 - Verifica Ambiente."

Poi esegui Step 0.1 e riporta i risultati.

=== END PROMPT ===
