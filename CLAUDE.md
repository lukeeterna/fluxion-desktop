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
completed: Week 1-3, Groq NLU Fallback, Comprehensive Regex + Dialog + Anti-cascade
tests: 638 passing / 45 skipped
last_commit: b897a25 feat(voice): comprehensive Italian time regex, open dialog, anti-cascade, WA confirmation
```

### Completato (2026-01-30) - Regex-Only NLU + Dialog Redesign
- **Comprehensive Italian time regex** (6-phase priority): "17 e 30", "un quarto", "meno un quarto", "del pomeriggio", "verso le", "tra le X e le Y" — no LLM needed for 95%+ of inputs
- **Open dialog flow**: no service listing, natural questions ("Come posso aiutarla?"), one field at a time
- **Anti-cascade guard**: corrections_made > 0 prevents accidental cancellation during corrections
- **WhatsApp confirmation** post-booking: cordiale + referral CTA ("10% sconto primo trattamento")
- **Live verified on iMac**: full booking + correction flow tested (15:00 → 16:30 senza cancellare)
- Key files: `entity_extractor.py` (rewrite extract_time), `booking_state_machine.py` (templates + anti-cascade), `orchestrator.py` (WA integration), `whatsapp.py` (conferma template)

### Completato (2026-01-29) - Groq NLU Fallback
- Groq LLM as L4 fallback only (regex handles core flow)
- `groq_nlu.py`: 4 state-specific extractors
- **Live verified on iMac**: Ehi! rejected, dopo le 17 = 17:00, no garbage operator

### Evaluated & Rejected
- **TTS Kokoro migration**: REJECTED — Python 3.10+ blocker (iMac has 3.9), hallucinated API, Italian voices grade C, existing Chatterbox (9/10) already better

### Week 4 TODO
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
iMac: 192.168.1.7 (runtime)
HTTP Bridge: port 3001 | Voice Pipeline: port 3002
Path iMac: /Volumes/MacSSD - Dati/fluxion
Path MacBook: /Volumes/MontereyT7/FLUXION
```
