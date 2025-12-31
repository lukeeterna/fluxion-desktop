# 🎯 FLUXION ENTERPRISE - Master Orchestrator

> **LEGGIMI SEMPRE PER PRIMO** - Sono il cervello del progetto.
> Coordino agenti, gestisco stato, ottimizzo token.

---

## 📋 PROGETTO IN BREVE

**FLUXION** = Gestionale desktop enterprise per PMI italiane
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Tailwind CSS 4
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Modello**: Licenza annuale desktop (NO SaaS, NO commissioni)

---

## 🚦 STATO CORRENTE

```yaml
fase: 3
nome_fase: "Calendario + Booking (100% COMPLETATO ✅)"
data_inizio: "2025-12-30"
ultimo_aggiornamento: "2025-12-30T22:00:00"
completato:
  # Fase 0 - Setup
  - Struttura directory
  - Design Bible
  - Documentazione contesto
  - Tauri inizializzato (React 19 + TypeScript)
  - Dipendenze Node + Rust installate
  - shadcn/ui configurato (Tailwind CSS 3.4 + 18 componenti)
  - Schema database creato (001_init.sql - 9 tabelle)
  - Plugin Tauri backend installati (SQL, FS, Dialog, Store, Opener)
  # Fase 1 - Layout + Navigation
  - main.rs configurato con database SQLite + SQLx
  - MainLayout + Sidebar (240px/60px) + Header implementati
  - React Router configurato (6 routes)
  - Palette FLUXION custom applicata (Navy/Cyan/Teal/Purple)
  - 6 pagine navigabili create
  - Requisiti di sistema documentati (macOS 12+, Windows 10+)
  # Fase 2 - CRM Clienti ✅
  - Tauri commands CRUD (get_clienti, create_cliente, update_cliente, delete_cliente)
  - TypeScript types + Zod schemas (Cliente, CreateClienteInput, UpdateClienteInput)
  - TanStack Query hooks (useClienti, useCreateCliente, useUpdateCliente, useDeleteCliente)
  - ClientiPage con tabella responsive + search bar
  - ClienteDialog con form validazione (React Hook Form + Zod)
  - Soft delete implementato (deleted_at)
  - Empty state + Loading state + Error state
  - Test CRUD completo su macOS Monterey ✓
  - Bundle identifier aggiornato (com.fluxion.app)
  - Warning Rust/accessibilità fixati
  # Fase 3 - Calendario + Booking (100% COMPLETATO ✅)
  - Backend Rust completo (18 Tauri commands):
    - servizi.rs (5 CRUD + soft delete)
    - operatori.rs (5 CRUD + soft delete)
    - appuntamenti.rs (5 CRUD + conflict detection + JOIN queries)
  - TypeScript types + Zod schemas (Servizio, Operatore, Appuntamento)
  - TanStack Query hooks (useServizi, useOperatori, useAppuntamenti)
  - CalendarioPage - Griglia mensile con navigazione + appuntamenti visibili
  - ServiziPage + ServizioDialog - CRUD completo con validazione
  - OperatoriPage + OperatoreDialog - CRUD completo con ruoli
  - AppuntamentoDialog - Booking workflow con auto-fill prezzo/durata
  - Conflict detection automatico per appuntamenti sovrapposti
  - Auto-fill intelligente: seleziona servizio → compila prezzo/durata
  - Sidebar con 7 sezioni navigabili (+ Operatori)
  - Palette colori servizi/operatori personalizzabile
  - File test completo: testedebug/fase3/TEST-FASE-3.txt (1139 righe, 20 test, 31 screenshot)
  - TypeScript compila senza errori ✓
  - Workflow end-to-end completo: Cliente → Servizio → Operatore → Data/Ora → Appuntamento → Calendario ✓
in_corso: "Test Fase 3 completa su iMac Monterey (workflow booking end-to-end)"
prossimo: "Fase 4 - Edit appuntamenti + Gestione stati + WhatsApp reminders"
requisiti_sistema:
  windows: "Windows 10 build 1809+ o Windows 11"
  macos: "macOS 12 Monterey o superiore (NO Big Sur)"
  nota: "Tauri 2.x richiede WebKit API moderne"
```

### Fasi Progetto

| # | Fase | Status | Durata |
|---|------|--------|--------|
| 0 | Setup Iniziale | ✅ COMPLETATO | 1 sett |
| 1 | Layout + Navigation | ✅ COMPLETATO | 1 giorno |
| 2 | CRM Clienti | ✅ COMPLETATO | 1 giorno |
| 3 | Calendario + Booking | ✅ COMPLETATO | 1 giorno |
| 4 | Servizi + Operatori | ⚪ TODO | 2 giorni |
| 5 | Fatturazione | ⚪ TODO | 3 giorni |
| 6 | WhatsApp + Notifiche | ⚪ TODO | 2 giorni |
| 7 | Voice Agent | ⚪ TODO | 3 giorni |
| 8 | Build + Licenze | ⚪ TODO | 2 giorni |

---

## 💻 WORKFLOW SVILUPPO

### Ambiente Multi-Macchina

```yaml
macbook_sviluppo:
  ruolo: "Sviluppo + Debug"
  attività:
    - Scrittura codice (Rust + React + TypeScript)
    - Debug e review
    - Git operations
    - Installazione dipendenze
  nota: "NON può eseguire `npm run tauri dev` (macOS < 12 Monterey)"

imac_monterey:
  ruolo: "Testing + Run"
  attività:
    - Esecuzione `npm run tauri dev`
    - Test funzionalità UI
    - Verifiche integrazione
    - Screenshot e feedback
  requisiti: "macOS 12 Monterey o superiore"
```

### Workflow Tipico

1. **Su MacBook** → Scrivi/modifica codice
2. **Sync/Transfer** → Passa codice a iMac (git, rsync, ecc.)
3. **Su iMac** → Esegui `npm run tauri dev` e testa
4. **Feedback** → Riporta eventuali errori/bug
5. **Loop** → Torna a step 1

**IMPORTANTE**: Gli agenti lavorano sempre su MacBook per sviluppo, ma i test runtime vanno fatti su iMac.

---

## 🤖 SISTEMA AGENTI

### Regola d'Oro
> **UN SOLO AGENTE alla volta. MAI confusione.**

### Come Funziona

```
[Tu chiedi qualcosa]
       ↓
[Orchestrator analizza]
       ↓
[Seleziona agente corretto]
       ↓
[Agente lavora con il SUO contesto]
       ↓
[Aggiorna stato in CLAUDE.md]
```

### Tabella Routing Agenti

| Keyword nella richiesta | Agente da usare | File contesto |
|------------------------|-----------------|---------------|
| `tauri`, `rust`, `backend`, `database`, `sqlite`, `api` | `rust-backend` | CLAUDE-BACKEND.md |
| `react`, `component`, `hook`, `state`, `ui`, `frontend` | `react-frontend` | CLAUDE-FRONTEND.md |
| `design`, `colori`, `layout`, `css`, `tailwind`, `stile` | `ui-designer` | CLAUDE-DESIGN-SYSTEM.md |
| `voice`, `voce`, `whisper`, `tts`, `chiamata`, `pipecat` | `voice-engineer` | CLAUDE-VOICE.md |
| `whatsapp`, `messaggio`, `notifica`, `reminder` | `integration-specialist` | CLAUDE-INTEGRATIONS.md |
| `fattura`, `xml`, `sdi`, `partita iva`, `fiscale` | `fatture-specialist` | CLAUDE-FATTURE.md |
| `build`, `release`, `update`, `deploy`, `licenza` | `devops` | CLAUDE-DEPLOYMENT.md |
| `review`, `refactor`, `ottimizza`, `bug`, `test` | `code-reviewer` | (tutti i file) |
| `architettura`, `decisione`, `struttura`, `piano` | `architect` | CLAUDE-INDEX.md |

### Invocazione Agente

Quando serve un agente, scrivi:

```
@agente:[nome-agente]
Descrizione task...
```

Esempio:
```
@agente:rust-backend
Crea lo schema SQLite per la tabella clienti
```

---

## 📁 STRUTTURA FILE

```
FLUXION/
├── CLAUDE.md                 ← SEI QUI (leggi sempre primo)
├── .env                      ← Variabili ambiente
├── QUICKSTART.md             ← Guida avvio rapido
│
├── docs/
│   ├── context/              ← Contesto per agenti
│   │   ├── CLAUDE-INDEX.md       ← Mappa navigazione
│   │   ├── CLAUDE-BACKEND.md     ← Rust + Tauri + SQLite
│   │   ├── CLAUDE-FRONTEND.md    ← React + TypeScript
│   │   ├── CLAUDE-DESIGN-SYSTEM.md ← Design tokens + UI
│   │   ├── CLAUDE-INTEGRATIONS.md  ← WhatsApp + API
│   │   ├── CLAUDE-VOICE.md       ← Voice Agent
│   │   ├── CLAUDE-FATTURE.md     ← Fatturazione elettronica
│   │   └── CLAUDE-DEPLOYMENT.md  ← Build + Release
│   │
│   ├── sessions/             ← Log sessioni (auto-generati)
│   │   └── YYYY-MM-DD-HH-MM-descrizione.md
│   │
│   └── FLUXION-DESIGN-BIBLE.md  ← Bibbia visiva completa
│
├── .claude/
│   └── agents/               ← Definizioni agenti
│       ├── architect.md
│       ├── rust-backend.md
│       ├── react-frontend.md
│       ├── ui-designer.md
│       ├── voice-engineer.md
│       ├── integration-specialist.md
│       ├── fatture-specialist.md
│       ├── devops.md
│       └── code-reviewer.md
│
├── mcp/
│   └── config.json           ← Configurazione MCP servers
│
├── templates/
│   └── demo/                 ← Dati demo per test
│
├── assets/
│   └── logo_fluxion.jpg      ← Logo brand
│
└── src/                      ← Codice sorgente (dopo init)
```

---

## 📝 CONVENZIONE NAMING FILE

### Sessioni e Log

```
YYYY-MM-DD-HH-MM-descrizione-breve.md
```

Esempi:
- `2025-12-28-18-30-setup-tauri-init.md`
- `2025-12-29-09-15-schema-database-clienti.md`
- `2025-12-29-14-00-componente-calendario.md`

### Perché questo formato?
1. **Ordinamento cronologico** automatico
2. **Ricerca facile** per data
3. **Nessuna collisione** di nomi
4. **Tracciabilità** completa

---

## 🔄 WORKFLOW SESSIONE

### Inizio Sessione

1. **Leggi CLAUDE.md** (questo file)
2. **Controlla stato corrente** (sezione 🚦)
3. **Identifica task** da completare
4. **Seleziona agente** appropriato
5. **Carica contesto** minimo necessario

### Durante Sessione

1. **Un agente alla volta**
2. **Aggiorna stato** dopo ogni milestone
3. **Crea file sessione** se modifiche significative

### Fine Sessione

1. **Aggiorna sezione 🚦** con nuovo stato
2. **Salva file sessione** in `docs/sessions/`
3. **Commit** se usi git

---

## ⚡ OTTIMIZZAZIONE TOKEN

### Regole

1. **NON leggere tutto** - Solo file necessari per il task
2. **Usa MCP filesystem** - Accesso diretto, no copia in chat
3. **Agenti specializzati** - Ognuno conosce solo il suo dominio
4. **State in YAML** - Compatto, parsabile
5. **Sessioni separate** - Non accumulare storia in CLAUDE.md

### Cosa Leggere per Task

| Task | File da leggere |
|------|-----------------|
| Setup progetto | CLAUDE.md + QUICKSTART.md |
| Backend/Database | CLAUDE-BACKEND.md |
| Componente React | CLAUDE-FRONTEND.md + CLAUDE-DESIGN-SYSTEM.md |
| Stile/Layout | CLAUDE-DESIGN-SYSTEM.md + DESIGN-BIBLE.md |
| Voice Agent | CLAUDE-VOICE.md |
| WhatsApp | CLAUDE-INTEGRATIONS.md |
| Fatture | CLAUDE-FATTURE.md |
| Build/Deploy | CLAUDE-DEPLOYMENT.md |

---

## 🔧 VARIABILI AMBIENTE

Definite in `.env`:

```bash
# AI/LLM
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556

# GitHub  
GITHUB_TOKEN=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
GITHUB_REPO=fluxion-desktop

# Licenze
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae

# VoIP
VOIP_PROVIDER=ehiweb
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it

# WhatsApp
WHATSAPP_PHONE=+393281536308

# Azienda (test)
AZIENDA_NOME="Automation Business"
AZIENDA_PARTITA_IVA=02159940762
AZIENDA_CF=DSTMGN81S12L738L
REGIME_FISCALE=RF19
```

---

## 🎯 PROSSIME AZIONI

### ✅ Fase 0 - COMPLETATA
1. [x] Inizializzare progetto Tauri
2. [x] Installare dipendenze (shadcn/ui, Tailwind, Lucide)
3. [x] Configurare SQLite + SQLx
4. [x] Creare schema database (9 tabelle)
5. [x] Implementare layout base (Sidebar + Header)
6. [x] Test build completato

### ✅ Fase 1 - COMPLETATA
1. [x] Configurare main.rs con plugin Tauri
2. [x] Database SQLite inizializzato con migrations
3. [x] MainLayout + Sidebar (240px/60px) + Header
4. [x] React Router configurato (6 routes)
5. [x] Palette FLUXION custom applicata
6. [x] Requisiti di sistema documentati

### ✅ Fase 2 - CRM Clienti (COMPLETATA)
1. [x] Creare `src-tauri/src/commands/clienti.rs` con CRUD commands
2. [x] Creare `src/types/cliente.ts` TypeScript types
3. [x] Installare TanStack Query: `npm install @tanstack/react-query`
4. [x] Creare hooks `src/hooks/use-clienti.ts`
5. [x] Implementare `ClientiTable.tsx` con shadcn/ui Table
6. [x] Creare `ClienteForm.tsx` con React Hook Form + Zod
7. [x] Implementare search e filtering
8. [x] Test CRUD completo su macOS Monterey
9. [x] Fix bundle identifier + warning accessibilità

### 🟡 Fase 3 - Calendario + Booking (PROSSIMA)

**IMPORTANTE**: Prima di iniziare, leggere:
- `docs/context/CLAUDE-BACKEND.md` (Schema appuntamenti/servizi/operatori)
- `docs/context/CLAUDE-DESIGN-SYSTEM.md` (Componenti calendario)

**Task previsti**:
1. [ ] Creare Tauri commands per appuntamenti CRUD
2. [ ] Implementare CalendarioPage con vista mensile/settimanale/giornaliera
3. [ ] Sistema drag & drop per spostare appuntamenti
4. [ ] Gestione disponibilità operatori (orari lavoro)
5. [ ] Gestione conflitti e sovrapposizioni slot
6. [ ] Filtri per operatore/servizio/stato
7. [ ] Notifiche appuntamenti (WhatsApp/Email reminder)
8. [ ] Test booking workflow completo

---

## 📚 RIFERIMENTI RAPIDI

| Risorsa | Path |
|---------|------|
| Design Bible | `docs/FLUXION-DESIGN-BIBLE.md` |
| Design Tokens | `docs/context/CLAUDE-DESIGN-SYSTEM.md` |
| Schema DB | `docs/context/CLAUDE-BACKEND.md` |
| API Reference | `docs/context/CLAUDE-INTEGRATIONS.md` |
| Voice Agent | `docs/context/CLAUDE-VOICE.md` |

---

*Ultimo aggiornamento: 2025-12-30T10:00:00*
