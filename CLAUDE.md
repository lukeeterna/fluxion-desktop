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
completed: Week 1-3, Groq NLU, Italian Regex NLU, Gino+Mimmo Bug Fixes
tests: 865 passing / 45 skipped
last_commit: e8b6ef1 fix(voice): Mimmo conversation bugs
next_step: Integrate Kimi 2.5 conversation flow output into state machine
```

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

### In Progress — Conversation Flow Redesign
- [ ] **Integrate Kimi 2.5 output** — user generated structured conversation flow via Kimi 2.5, output needs integration into `booking_state_machine.py`
- Prompt saved in: `docs/prompts/kimi-2.5-conversation-flow.md`
- Goal: sequential guided flow (name→surname→phone→service→date→time→confirm→WhatsApp→close call)
- Key changes: "settimana prossima" shows available days from calendar, multi-service, should_exit on completion

### Week 4 TODO
- [ ] Integrate Kimi 2.5 conversation flow
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
