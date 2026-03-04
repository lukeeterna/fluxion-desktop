# FLUXION — Handoff Sessione 17 (2026-03-04) — FINE SESSIONE

## 🎯 PROSSIMO TASK IMMEDIATO
**F02.1 — NLU Hardening** — tutto il research è già pronto, eseguire `/gsd:plan-phase F02.1`

---

## ✅ Completato Sessione 17

| Task | Commit | Note |
|------|--------|------|
| F02 Plan 01 — guardrails | b6963da,f88d88f,81eee77,2757147 | VERTICAL_GUARDRAILS 4 verticals, 33 test |
| F02 Plan 02 — orchestrator | bb98906,a1102d8,5cf0ab1 | FSM fix + entity extractor wired |
| Roadmap F02 done | e3f3b1d | ROADMAP_REMAINING.md ✅ |
| CoVe 2026 deep research | *(no commit)* | 6 file research in .claude/cache/agents/ |

**Voice test suite: 1197 PASS / 0 FAIL**

---

## 🔴 P0 Bug da Fixare in F02.1

| # | Bug | File da toccare |
|---|-----|----------------|
| 1 | "non voglio cancellare" → **cancella** | `orchestrator.py` negation guard |
| 2 | "no aspetti" → RIFIUTO non WAIT | `italian_regex.py` prefilter() |
| 3 | "alle tre" → 03:00 non 15:00 | `entity_extractor.py` extract_time() |
| 4 | "marted/gioved/venerd" STT troncato → data mancante | `entity_extractor.py` DAYS_IT |
| 5 | `extra_entities` F02 mai letti dal FSM | `booking_state_machine.py` |
| 6 | Verb-form guardrails mancanti (cambiare≠cambio) | `italian_regex.py` VERTICAL_GUARDRAILS |
| 7 | SPOSTAMENTO oggetto opzionale → falso positivo | `intent_classifier.py` |

**Bug trigger reale**: "Gino devo cambiare le gomme si può farlo?" → `reschedule_need_name` (SALONE)

---

## 📁 Research Files Pronti (NON rifare research)

| File | Usa per |
|------|---------|
| `.claude/cache/agents/f02-nlu-ambiguity-research.md` | Root cause + fix 3-layer |
| `.claude/cache/agents/f02-nlu-comprehensive-patterns.md` | Pattern verb-form pronti+150 test |
| `.claude/cache/agents/r1-sara-capabilities-audit.md` | Score card 15 aree |
| `.claude/cache/agents/r2-world-class-benchmarks.md` | Benchmark P50 491ms |
| `.claude/cache/agents/r3-italian-nlu-edge-cases.md` | 10 categorie edge cases IT |
| `.claude/cache/agents/r4-ux-conversation-patterns.md` | UX patterns world-class |

---

## 📋 Roadmap Post-F02

| Fase | Task | Status | Effort |
|------|------|--------|--------|
| **F02.1** | NLU Hardening (P0 bugs + verb-form + SPOSTAMENTO) | 🔄 NEXT | ~3h |
| **F03** | Latency P95 <800ms (Groq STT + streaming LLM) | ⏳ | 4-6h |
| **F04** | Booking Intelligence (WA reminders + hours DB + storico) | ⏳ | 4h |
| **F05** | LicenseManager tab Impostazioni | ⏳ | 1h |

---

## 📡 Decisione VoIP (fissata sessione 17)
- **Ora**: WhatsApp (live, zero infrastruttura)
- **Dopo F03**: EHIWEB numero IT + Telnyx WebSocket → Sara `/ws/voice`
- **Prerequisito**: Groq STT (Whisper CPU = 30s → impossibile per VoIP)

---

## Stato Git
```
Branch: master | HEAD: e3f3b1d
type-check: ✅ 0 errori
Voice tests: ✅ 1197 PASS / 0 FAIL
```
