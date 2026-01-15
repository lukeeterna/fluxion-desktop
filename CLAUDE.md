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

### Fix Recenti (2026-01-14)

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
TTS_VOICE_MODEL=it_IT-paola-medium
WHATSAPP_PHONE=393281536308
```

---

## Workflow Sessione

1. **Inizio**: Leggi questo file → stato corrente
2. **Come fare**: Consulta [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md)
3. **Fine**: Aggiorna stato + crea sessione + commit

---

*Ultimo aggiornamento: 2026-01-15T11:45:00*
