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
6. Dev on MacBook, test on iMac (192.168.1.9) - Tauri needs macOS 12+
7. Restart voice pipeline on iMac after ANY Python change

## Active Sprint
```yaml
branch: feat/workflow-tools
sprint: Week 4 Release (GDPR, Testing, Documentation)
completed: Week 1 P0, Week 2 P1, Week 3 Quality, Groq NLU Fallback
tests: 509 core / 612 total passing
last_commit: d324457 feat(voice): Groq LLM fallback for Italian NLU edge cases
```

### Completato (2026-01-29) - Groq NLU Fallback
- Regex handles ~90% Italian input, Groq LLM covers remaining ~10%
- `groq_nlu.py` (new): 4 state-specific extractors (surname, phone_correction, confirming, time_preference)
- `booking_state_machine.py`: 3 Groq fallback patches (REGISTERING_SURNAME, REGISTERING_PHONE, CONFIRMING)
- `entity_extractor.py`: interjection blacklist, operator blacklist, "dopo le X" time patterns
- `orchestrator.py`: wired GroqNLU to BookingStateMachine
- **Live verified on iMac**: all 4 bug scenarios pass (Ehi! rejected, dopo le 17 = 17:00, no garbage operator)

### Pending Evaluation
- [ ] **TTS Migration: Piper to Kokoro** - see `/Users/macbook/Downloads/tts_migration.md`

### Week 4 TODO
- [ ] Evaluate TTS Kokoro migration proposal
- [ ] GDPR audit trail
- [ ] Data retention policy
- [ ] Regression testing
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
iMac: 192.168.1.9 (runtime)
HTTP Bridge: port 3001 | Voice Pipeline: port 3002
Path iMac: /Volumes/MacSSD - Dati/fluxion
Path MacBook: /Volumes/MontereyT7/FLUXION
```
