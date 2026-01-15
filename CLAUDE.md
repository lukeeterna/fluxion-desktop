# FLUXION - Stato Progetto

> **Procedure operative:** [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md)

---

## Progetto

**FLUXION**: Gestionale desktop enterprise per PMI italiane

- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Tailwind CSS 3.4
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Modello**: Licenza annuale desktop (NO SaaS, NO commissioni)

---

## Stato Corrente

```yaml
fase: 7
nome: "Voice Agent + WhatsApp + FLUXION IA"
ultimo_update: 2026-01-15
ci_cd_run: "#156 SUCCESS"
```

### In Corso

- [ ] Aggiungere `data-testid` ai componenti (E2E)
- [ ] WhatsApp QR scan UI
- [ ] GDPR encryption at rest

### Completato (Fase 7)

- [x] Voice Agent RAG integration (Week 1-3)
- [x] HTTP Bridge endpoints (15 totali)
- [x] Waitlist con priorità VIP
- [x] Disambiguazione cliente con data_nascita + soprannome (fallback)
- [x] Registrazione nuovo cliente via conversazione
- [x] Preferenza operatore con alternative
- [x] E2E Test Suite Playwright (smoke + dashboard)
- [x] **VoIP Integration (Week 4)** - SIP/RTP per Ehiweb (voip.py, 39 tests)
- [x] **WhatsApp Integration (Week 5)** - Client Python + templates + analytics (whatsapp.py, 52 tests)
- [x] **Voice Agent UI ↔ Pipeline Integration** - STT (Whisper) + NLU + TTS nel frontend
- [x] **Disambiguazione deterministica** - data_nascita → soprannome fallback ("Mario o Marione?")
- [x] **Release Sprint 2026-01-15** - TypeScript clean, E2E smoke 8/8, Voice Agent OK
- [x] **Fix test-suite.yml** - Nightly job condition (github.event_name == 'schedule')
- [x] **E2E Playwright fallback** - Firefox per macOS Big Sur compatibility
- [x] **NLU Upgrade** - spaCy + UmBERTo 4-layer pipeline (~100ms, 100% offline)
- [x] **TTS Upgrade** - Chatterbox Italian (9/10 quality) + Piper fallback
- [x] **Voice Assistant Rebrand** - Nome voce: "Sara" (uniformato su tutto il codebase)
- [x] **Stack Analysis** - `docs/analysis/STACK_ANALYSIS.md` + `PMI_VERTICALS_ANALYSIS.md`
- [x] **FAQ Verticali System** - 96 FAQ production-ready per 5 verticali (via Perplexity)
- [x] **Vertical Loader** - `vertical_loader.py` carica FAQ per verticale con sostituzione variabili
- [x] **SQL Seed Files** - `src-tauri/migrations/seeds/` (60 servizi default per verticale)
- [x] **Deployment Guide** - `docs/DEPLOYMENT.md` (checklist, SLA, benchmarks, security)
- [x] **n8n Workflows** - `n8n-workflows/shared/whatsapp-voice-bridge.json` (copy-paste ready)
- [x] **Architecture Diagrams** - `docs/images/` (5 PNG da Perplexity: gantt, latency, architecture)
- [x] **Integration Testing Guide** - `docs/INTEGRATION_TESTING_GUIDE.md` (6 test suites)
- [x] **Test Scripts** - `scripts/tests/` (voice, http, sqlite, whatsapp, master runner)
- [x] **MCP Server Complete** - `mcp-server/src/index.ts` (8 tools, 9 resources, SQLite integration)
- [x] **n8n Additional Workflows** - booking-reminder, loyalty-update (copy-paste ready)

### Prossimo (Priorità Fase 8)

- [ ] Aggiungere `data-testid` ai componenti
- [ ] WhatsApp QR scan UI
- [ ] GDPR encryption at rest
- [ ] Build + Licenze (Fase 8)

### Bug Aperti

| ID | Descrizione | Priority | Status |
|----|-------------|----------|--------|
| BUG-V2 | Voice UI si blocca dopo prima frase | P1 | ✅ RISOLTO |
| BUG-V3 | Paola ripete greeting invece di chiedere nome | P1 | ✅ RISOLTO |
| BUG-V4 | "mai stato" interpretato come nome "Mai" | P1 | ✅ RISOLTO |

### Fix Recenti (2026-01-15)

**BUG-V4 - NLU Upgrade** (`voice-agent/src/nlu/italian_nlu.py`):
- **Problema**: Voice agent interpretava "Io non sono mai stato da voi" come cliente "Mai"
- **Soluzione**: 4-layer NLU pipeline con spaCy + UmBERTo (regex → NER → intent → context)
- **Test**: "mai stato", "prima volta" → NUOVO_CLIENTE ✅

**TTS Upgrade - Sara Voice** (`voice-agent/src/tts.py`):
- **Problema**: Aurora (Piper) aveva pause enfatiche randomiche, pronuncia italiana mediocre
- **Soluzione**: Multi-engine TTS con Chatterbox Italian (primario) + Piper Paola (fallback)
- **Nome voce**: Sara (unificato su tutto il codebase)
- **Qualità**: 9/10 (vs 6.5/10 Aurora), latenza 100-150ms CPU
- **File**: `docs/context/CHATTERBOX-ITALIAN-TTS.md`

**BUG-V3 - Greeting Loop Fix** (`orchestrator.py`):
- **Problema**: L1 intercettava CORTESIA ("Buongiorno") e rispondeva con altro greeting
- **Soluzione**: `is_first_turn` flag - L1 salta CORTESIA al primo turno, L2 sempre attivo
- **File**: `voice-agent/src/orchestrator.py` (linee ~340-430)

---

## Fasi Progetto

| Fase | Nome | Status |
|------|------|--------|
| 0 | Setup Iniziale | ✅ |
| 1 | Layout + Navigation | ✅ |
| 2 | CRM Clienti | ✅ |
| 3 | Calendario + Booking | ✅ |
| 4 | Fluxion Care | ✅ |
| 5 | Quick Wins Loyalty | ✅ |
| 6 | Fatturazione Elettronica | ✅ |
| 7 | Voice Agent + WhatsApp | 📋 IN CORSO |
| 8 | Build + Licenze | 📋 TODO |
| 9 | Moduli Verticali | 📋 TODO |

---

## Voice Agent Roadmap

| # | Funzionalità | Endpoint/File | Status |
|---|--------------|---------------|--------|
| 1 | Cerca clienti | `/api/clienti/search` | ✅ |
| 2 | Crea appuntamenti | `/api/appuntamenti/create` | ✅ |
| 3 | Verifica disponibilità | `/api/appuntamenti/disponibilita` | ✅ |
| 4 | Lista d'attesa VIP | `/api/waitlist/add` | ✅ |
| 5 | Disambiguazione data_nascita | `disambiguation_handler.py` | ✅ |
| 6 | Disambiguazione soprannome | `disambiguation_handler.py` | ✅ |
| 7 | Registrazione cliente | `/api/clienti/create` | ✅ |
| 8 | Preferenza operatore | `/api/operatori/list` | ✅ |

### Flusso Disambiguazione

```
1. "prenotazione per Mario Rossi"
   → "Ho trovato 2 clienti. Mi può dire la sua data di nascita?"

2. Data sbagliata (es. "10 gennaio 1980")
   → "Non ho trovato questa data. Mario o Marione?"

3. "Marione"
   → "Perfetto, Mario Rossi!" (cliente con soprannome)
```

---

## FAQ Verticali System

### File Produzione

| Verticale | File | FAQ | Generato |
|-----------|------|-----|----------|
| salone | `voice-agent/data/faq_salone.json` | 25 | Perplexity |
| wellness | `voice-agent/data/faq_wellness.json` | 24 | Perplexity |
| medical | `voice-agent/data/faq_medical.json` | 24 | Perplexity |
| auto | `voice-agent/data/faq_auto.json` | 23 | Perplexity |
| altro | `voice-agent/data/faq_altro.json` | 10 | Manuale |

### Architettura

```
1. Setup Wizard → utente sceglie categoria_attivita (salone/wellness/medical/auto/altro)
2. Orchestrator.start_session() → carica faq_{verticale}.json
3. vertical_loader.py → sostituisce {{VARIABILI}} con dati DB
4. FAQManager → keyword + semantic search (FAISS)
5. Sara risponde con dati personalizzati
```

### Roadmap Spreadsheet (TODO)

Convertire FAQ in formato spreadsheet interattivo con 2 fogli:

| Foglio | Contenuto |
|--------|-----------|
| **FAQ Database** | Tabella completa FAQ (ID, categoria, keywords, variabili) |
| **Variabili Configurazione** | Dizionario variabili (descrizione, esempio, tipo, obbligatorietà) |

**Vantaggi:**
- Gestione FAQ centralizzata
- Configurazione rapida nuove attività
- Base per automazione chatbot/CRM
- Versioning e tracking cambiamenti

**Esempio:** `FAQ Auto Officina.xlsx` (23 FAQ, ~50 variabili)

---

## Infrastruttura

```yaml
# Test Machines
iMac:
  host: imac (192.168.1.2)
  path: /Volumes/MacSSD - Dati/fluxion

Windows PC:
  host: 192.168.1.17
  path: C:\Users\gianluca\fluxion

# Porte
HTTP Bridge: 3001
Voice Pipeline: 3002
MCP Server: 5000
```

---

## Riferimenti Rapidi

| Risorsa | Path |
|---------|------|
| **Procedure Operative** | `docs/FLUXION-ORCHESTRATOR.md` |
| **Voice Agent RAG Enterprise** | `docs/context/VOICE-AGENT-RAG-ENTERPRISE.md` |
| **Stack Analysis** | `docs/analysis/STACK_ANALYSIS.md` |
| **PMI Verticali** | `docs/analysis/PMI_VERTICALS_ANALYSIS.md` |
| **Chatterbox TTS** | `docs/context/CHATTERBOX-ITALIAN-TTS.md` |
| **FAQ Verticali** | `voice-agent/data/faq_*.json` |
| **Vertical Loader** | `voice-agent/src/vertical_loader.py` |
| **SQL Seeds** | `src-tauri/migrations/seeds/seed_*.sql` |
| **Prompts Perplexity** | `docs/prompts/PROMPT_GENERA_*.md` |
| **Template Spreadsheet** | `docs/templates/FAQ Auto Officina.xlsx` |
| **Deployment Guide** | `docs/DEPLOYMENT.md` |
| **n8n Workflows** | `n8n-workflows/shared/*.json` |
| **Architecture Images** | `docs/images/*.png` |
| **Integration Testing** | `docs/INTEGRATION_TESTING_GUIDE.md` |
| **MCP Server Guide** | `docs/MCP_SERVER_IMPLEMENTATION.md` |
| **Test Scripts** | `scripts/tests/run-all-tests.sh` |
| **n8n Auto Workflows** | `n8n-workflows/auto/*.json` |
| **n8n Salone Workflows** | `n8n-workflows/salone/*.json` |
| Voice Agent Base | `docs/context/CLAUDE-VOICE.md` |
| Fasi Completate | `docs/context/COMPLETED-PHASES.md` |
| Cronologia Sessioni | `docs/context/SESSION-HISTORY.md` |
| Decisioni Architetturali | `docs/context/DECISIONS.md` |
| Schema DB | `docs/context/CLAUDE-BACKEND.md` |
| Design System | `docs/FLUXION-DESIGN-BIBLE.md` |

---

## Agenti (25)

Routing completo in [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md#routing-matrix)

| Dominio | Agente | File Contesto |
|---------|--------|---------------|
| Backend | `@agent:rust-backend` | CLAUDE-BACKEND.md |
| Frontend | `@agent:react-frontend` | CLAUDE-FRONTEND.md |
| Voice | `@agent:voice-engineer` | CLAUDE-VOICE.md |
| **Voice RAG** | `@agent:voice-rag-specialist` | VOICE-AGENT-RAG-ENTERPRISE.md |
| Fatture | `@agent:fatture-specialist` | CLAUDE-FATTURE.md |
| Test E2E | `@agent:e2e-tester` | docs/testing/ |
| Debug | `@agent:debugger` | — |

---

## Environment

```bash
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556
GITHUB_TOKEN=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
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it
TTS_ENGINE=chatterbox           # Primary: Chatterbox Italian (9/10)
TTS_FALLBACK=piper              # Fallback: Piper paola-medium (7.5/10)
TTS_VOICE_NAME=Sara             # Unified voice assistant name
WHATSAPP_PHONE=393281536308
```

---

## Workflow Sessione

1. **Inizio**: Leggi questo file → stato corrente
2. **Come fare**: Consulta [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md)
3. **Fine**: Aggiorna stato + crea sessione + commit

---

## MCP Server (Claude Code Integration)

### Setup

```bash
cd mcp-server
npm install
npm run build
```

### Claude Desktop Config

Aggiungi a `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxion": {
      "command": "node",
      "args": ["/Volumes/MontereyT7/FLUXION/mcp-server/dist/index.js"]
    }
  }
}
```

### Tools Disponibili (8)

| Tool | Descrizione |
|------|-------------|
| `search_clienti` | Cerca clienti per telefono/nome/email |
| `create_appuntamento` | Crea nuovo appuntamento |
| `get_disponibilita` | Slot disponibili per data |
| `get_faq` | FAQ per verticale |
| `list_servizi` | Lista servizi |
| `list_operatori` | Lista operatori |
| `get_cliente` | Dettagli cliente |
| `get_appuntamenti_cliente` | Appuntamenti cliente |

### Resources (9)

- `fluxion://clienti` - Tutti i clienti
- `fluxion://servizi` - Tutti i servizi
- `fluxion://appuntamenti/oggi` - Appuntamenti di oggi
- `fluxion://faq/{salone|wellness|medical|auto}` - FAQ per verticale
- `fluxion://stats` - Statistiche sistema

---

## Performance SLA (Target)

| Layer | Operation | Target | Status |
|-------|-----------|--------|--------|
| L0 | Regex match | <1ms | OK |
| L1 | Intent (spaCy) | <5ms | OK |
| L2 | Slot filling | <10ms | OK |
| L3 | FAISS search | <50ms | OK |
| L4 | Groq LLM | <500ms | OK |
| E2E | Voice in -> out | <2000ms | OK |

Dettagli completi: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

---

*Ultimo aggiornamento: 2026-01-15T21:15:00*
