# FLUXION - Gestionale Desktop PMI Italiane

## Identity
- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Python voice agent
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Model**: Licenza LIFETIME desktop (NO SaaS, NO commissioni)
- **Voice**: "Sara" - assistente vocale prenotazioni (5-layer RAG pipeline)

## Critical Rules
1. Never commit API keys, secrets, or .env files
2. Always TypeScript (never JS), always async Tauri commands
3. Run tests before commit (see `.claude/rules/testing.md` for checklist)
4. A task is NOT complete until code works AND is verified (DB records, E2E)
5. Italian field names in APIs: `servizio`, `data`, `ora`, `cliente_id`
6. Dev on MacBook, test on iMac (192.168.1.7) - Tauri needs macOS 12+
7. Restart voice pipeline on iMac after ANY Python change

## Active Sprint
```yaml
branch: feat/workflow-tools
sprint: Week 4 Release (GDPR, Testing, Documentation)
completed: Week 1-3, Groq NLU, Italian Regex NLU, Gino+Mimmo Bug Fixes, Kimi 2.5 Flow, 5 Structural Bug Fixes
tests: 940 passing / 37 skipped
last_commit: 8a27f81 fix(voice): 5 structural bug fixes from Kimi 2.5 audit — 940 tests passing
next_step: GDPR audit trail + data retention policy
```

### Completato (2026-02-02) - 5 Structural Bug Fixes (Kimi 2.5 Audit)
- **BUG 6 (P0)**: "settimana prossima" + weekday now returns next week — conservative `elif` with `weekday > today_weekday` guard
- **BUG 1 (P0)**: "capelli" recognized as taglio — added to both `VERTICAL_SERVICES` and `DEFAULT_SERVICES`
- **BUG 4 (P0)**: Back-navigation WAITING_TIME → WAITING_DATE — weekday detection + change markers, extended `_check_interruption` skip
- **BUG 2 (P1)**: Service merge in WAITING_DATE — new services no longer silently dropped by `_update_context_from_extraction`
- **BUG 3 (P1)**: Reversed "settimana prossima" detected as ambiguous date — added `r"\bsettimana\s+(?:prossima|scorsa|corrente)\b"`
- 30 new tests across 3 test files, 940 total passing
- Key files: `entity_extractor.py` (BUG 6), `italian_regex.py` (BUG 1+3), `booking_state_machine.py` (BUG 1+2+4)

### Completato (2026-02-02) - Kimi 2.5 Sequential Conversation Flow
- **Guided identity collection**: nome → cognome → DB lookup → telefono (one field at a time)
- **2 new states**: `WAITING_SURNAME` (ask surname after name), `CONFIRMING_PHONE` (confirm phone before client creation)
- **`_extract_surname_from_text()` helper**: 4-phase extraction (contextual phrases, entity extractor, raw text, Groq fallback)
- **`_handle_idle` + `_handle_waiting_name` rerouted**: now go to WAITING_SURNAME instead of WAITING_SERVICE when client_id is missing
- **`client_by_name_surname` lookup** in orchestrator: precise name+surname search with name-only fallback for legacy clients
- **`check_week()` in availability_checker**: queries calendar for entire week, returns available days
- **"Settimana prossima" → calendar query**: shows actual available days instead of generic "Quale giorno?"
- **Slot display in WAITING_TIME**: `ask_time_with_slots` template wired to show available time slots
- **REGISTERING_PHONE → CONFIRMING_PHONE**: phone number confirmed before client creation
- **"tra due/tre settimane"** added to ambiguous date patterns
- 26 new tests (`test_kimi_flow.py`), 910 total passing
- Key files: `booking_state_machine.py` (2 states, 2 handlers, 6 templates, routing changes), `orchestrator.py` (2 new lookup branches, slot display), `availability_checker.py` (check_week), `italian_regex.py` (ambiguous date pattern)

### Completato (2026-01-31) - Mimmo Conversation Bug Fixes (6 fix)
- **WA FAQ handler (L0a)**: precompiled regex intercepts WhatsApp questions before Groq denial
- **should_exit propagation**: new `should_exit` field in OrchestratorResult — COMPLETED/CANCELLED/escalation close VoIP call
- **Content filter**: broader sexual harassment patterns in SEVERE (standalone "tette", body-focused, explicit terms)
- **Name blacklist**: "ciao", "tutti", "salve", "grazie", "niente" no longer extracted as client names
- **Reschedule/cancel context**: orchestrator searches by client_name when client_id is None
- **WhatsApp confirmation**: all verticals say "WhatsApp" + "Arrivederci!" (no more "SMS")
- 7 WA FAQ pattern tests + 3 updated regression tests
- Key files: `orchestrator.py` (L0a WA FAQ, should_exit, reschedule/cancel search), `booking_state_machine.py` (COMPLETED/CANCELLED close call, WhatsApp messages), `italian_regex.py` (sexual patterns), `entity_extractor.py` (name blacklist), `main.py` (should_exit in HTTP response)

### Completato (2026-01-31) - 4 Gino Conversation Bug Fixes
- BUG 1: Surname "Di Nanni" no longer overwrites client_name "Gino"
- BUG 2: Multi-service "taglio e barba" → ["Taglio", "Barba"] with service_display
- BUG 4: `reset_for_new_booking()` preserves client identity
- BUG 5: Known client skips DB lookup on follow-up
- 12 regression tests, all live verified on iMac

### Completato (2026-01-31) - Comprehensive Italian Regex NLU Module
- **`italian_regex.py`** (NEW, 650+ lines): 8 pre-compiled regex categories for ~90% Italian NLU coverage without LLM
- **L0-PRE Content Filter**: 3 severity levels (MILD/MODERATE/SEVERE) with Italian blasphemies, threats, vulgar language
- **Escalation Detection**: 4 types (operator, frustration, role, callback) with WhatsApp notification trigger
- **Ambiguous Date Disambiguation**: "prossima settimana" asks which day instead of auto-picking Monday
- **Layer 1b Regex Reinforcement** in intent_classifier: conferma/rifiuto/escalation checked before pattern matching
- 208 tests, live verified on iMac: content filter, escalation, booking, disambiguation all working
- Key files: `italian_regex.py`, `intent_classifier.py` (L1b + expanded dicts), `orchestrator.py` (L0-PRE + WA escalation), `booking_state_machine.py` (ambiguous date)

### Completato (2026-01-30) - Dialog Redesign + Client Recognition
- Comprehensive Italian time regex, open dialog flow, anti-cascade guard, WhatsApp confirmation, client recognition/registration
- Key files: `entity_extractor.py`, `booking_state_machine.py`, `orchestrator.py`, `whatsapp.py`

### Completato (2026-01-29) - Groq NLU Fallback
- Groq LLM as L4 fallback only (regex handles core flow)
- `groq_nlu.py`: 4 state-specific extractors

### Evaluated & Rejected
- **TTS Kokoro migration**: REJECTED — Python 3.10+ blocker (iMac has 3.9), hallucinated API, Italian voices grade C

### Week 4 TODO
- [x] Integrate Kimi 2.5 conversation flow (2026-02-02)
- [x] 5 structural bug fixes from Kimi 2.5 audit (2026-02-02)
- [ ] GDPR audit trail
- [ ] Data retention policy
- [ ] Final regression testing
- [ ] Documentation
- [ ] v1.0 Release

## Context Routing

Before working on a domain, read the relevant reference doc:

| Domain | Read First |
|--------|-----------|
| Full project history | `docs/context/PROJECT-STATUS.md` |
| Bug tracking | `docs/context/BUG-TRACKER.md` |
| Voice pipeline architecture | `docs/context/VOICE-AGENT-RAG-ENTERPRISE.md` |
| Voice agent roadmap/endpoints | `docs/context/VOICE-AGENT-ROADMAP.md` |
| Database schema (Rust) | `docs/context/CLAUDE-BACKEND.md` |
| Frontend patterns | `docs/context/CLAUDE-FRONTEND.md` |
| Business model/licensing | `docs/context/BUSINESS-MODEL.md` |
| Infrastructure/services | `docs/context/INFRASTRUCTURE.md` |
| Supplier management | `docs/context/SUPPLIER-MANAGEMENT.md` |
| Design system | `docs/FLUXION-DESIGN-BIBLE.md` |
| Sprint epics/stories | `_bmad-output/planning-artifacts/voice-agent-epics.md` |
| Procedures | `docs/FLUXION-ORCHESTRATOR.md` |
| Deployment | `docs/DEPLOYMENT.md` |

## Infrastructure (Quick Reference)
```
iMac: 192.168.1.7 (runtime)
HTTP Bridge: port 3001 | Voice Pipeline: port 3002
Path iMac: /Volumes/MacSSD - Dati/fluxion
Path MacBook: /Volumes/MontereyT7/FLUXION
```
