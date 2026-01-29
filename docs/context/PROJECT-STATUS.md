# Fluxion Project Status (Full History)

> This file contains the complete project history. CLAUDE.md only contains the active sprint.
> Read this file when you need context about past work or completed phases.

## Stato Corrente

```yaml
fase: 7.6
nome: "Voice Agent Multi-Vertical"
ultimo_update: 2026-01-29
ci_cd_run: "#158 SUCCESS"
branch: feat/workflow-tools
```

## Sprint Voice Agent v1.0 (4 settimane)

- **Week 1**: P0 fixes COMPLETATO
- **Week 2**: P1 improvements COMPLETATO
- **Week 3**: Quality (Silero VAD, Disambiguation, Corrections) COMPLETATO
- **Week 4**: Release (GDPR, Testing, Documentation) TODO

## Completato (2026-01-29) - Week 3 Sprint Quality

| Task | File | Status |
|------|------|--------|
| E7-S4 Silero VAD | `voice-agent/src/vad/ten_vad_integration.py` | 11/11 tests |
| E3-S1/S2 Disambiguation | `voice-agent/src/disambiguation_handler.py` | 49/49 tests |
| E4-S3 Vertical Corrections | `voice-agent/src/booking_state_machine.py` | 65/65 tests |

- Replaced TEN VAD with Silero VAD (ONNX Runtime, 95% accuracy, 32ms chunks)
- Added cognome-based disambiguation strategy
- Fixed restaurant num_coperti regex
- 273 core tests, 624 total, 18 pre-existing failures (async)

## Completato (2026-01-28) - Week 2 Sprint P1

- **E7-S2**: Semantic Intent Classifier (TF-IDF, ~10ms, no PyTorch)
- **E7-S3**: Guided Dialog integration as Layer 3.5
- **E1-S2**: Italian date extraction (fra/tra X giorni/settimane)
- **E1-S3**: Fuzzy service matching (Levenshtein distance)
- **E5-S1**: FAQ per vertical con variable substitution
- **E6-S1**: Waitlist integration

## Completato (2026-01-27) - Week 1 Sprint P0

- **E7-S1**: Hybrid STT Engine (whisper.cpp + Groq fallback)
- **E1-S1**: Slot availability check
- **E4-S1**: Cancel appointment end-to-end
- **E4-S2**: Reschedule appointment end-to-end
- Intent Classifier Upgrade (CANCELLAZIONE, SPOSTAMENTO patterns)
- Session Isolation Bug Fix
- SARA Corrections VERIFIED LIVE

## Completato (2026-01-26)

- Fix VAD Manual Stop Bug
- Fix React Hooks Error
- TEN VAD Integration (standalone, no cloud)
- Frontend VAD Integration
- Voice Agent Validation (YELLOW LIGHT)
- Multi-Vertical Agent System (5 verticals)

## Completato (2026-01-25)

- Voice Agent Strategy Analysis
- Bug Fix session_manager.py (infinite recursion)
- Test LIVE Voice Agent (3 critical bugs identified)

## Completato (2026-01-24)

- Claude Code Hooks system
- Fix Voice Agent "Antonio" (pipeline restart)

## Completato (2026-01-23)

- Voice Agent Full Integration Fix (VA-01 through VA-08)
- Intent SPOSTAMENTO
- Waitlist Integration
- Voice Agent Auto-Greet
- Error Handling VoiceAgent

## Completato (2026-01-22)

- Fix Voice Agent UI Microphone Bug (BUG-V5)
- E2E Testing Playwright Setup
- HTTP Fallback Browser Mode

## Completato (2026-01-21)

- Guided Dialog Engine
- Test Suite 409 passed
- Claude Code Skills (3 skill files)

## Completato (Fase 7.5 - 2026-01-16)

- Fornitori Page UI completa
- Excel Import (SheetJS + mammoth.js)
- 14 Rust commands per suppliers

## Completato (Fase 7)

- Voice Agent RAG integration
- HTTP Bridge endpoints (15 totali)
- Waitlist con priorita VIP
- Disambiguazione cliente
- VoIP Integration (SIP/RTP per Ehiweb)
- WhatsApp Integration
- GDPR Encryption (AES-256-GCM)

## Fasi Progetto

| Fase | Nome | Status |
|------|------|--------|
| 0 | Setup Iniziale | Done |
| 1 | Layout + Navigation | Done |
| 2 | CRM Clienti | Done |
| 3 | Calendario + Booking | Done |
| 4 | Fluxion Care | Done |
| 5 | Quick Wins Loyalty | Done |
| 6 | Fatturazione Elettronica | Done |
| 7 | Voice Agent + WhatsApp | In Corso |
| 8 | Build + Licenze | TODO |
| 9 | Moduli Verticali | TODO |
