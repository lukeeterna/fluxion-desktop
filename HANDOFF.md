# FLUXION — Handoff Sessione 75 → 76 (2026-03-15)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 58c9782
docs(f-sara-nlu-patterns): add verification report — 22/22 passed
type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1896 PASS / 3 FAIL pre-esistenti / 27 skipped ✅
```

---

## COMPLETATO SESSIONE 75

### F-SARA-NLU-PATTERNS — FASE COMPLETA ✅

Enterprise-grade rewrite dell'NLU layer di Sara — 4 wave, 8 commit, 22/22 must-haves verified.

| Wave | Piano | Risultato |
|------|-------|-----------|
| A | 01 | hair + beauty: 21+16 service groups, 30+18 guardrail patterns, 122 test |
| B | 02 | wellness + medico: 15+18 service groups, 21+20 guardrail patterns, 132 test |
| C | 03 | auto extended + professionale, DURATION_MAP, OPERATOR_ROLES, 93 test |
| D | 04 | orchestrator wiring + bug fix lines 673+685 + 64 integration test |

**Total: 411 nuovi test NLU, 1896 PASS iMac**

**Bug produzione fixato**: lines 673+685 in orchestrator.py passavano `self.verticale_id` (raw) a `check_vertical_guardrail()` e `extract_vertical_entities()` invece di `self._faq_vertical` (normalizzato) → businesses con `hair_salone_bella` ottenevano comportamento "altro" silenziosamente.

**3 FAIL pre-esistenti non correlati**:
1. `test_holiday_handling.py::test_nearby_second_holiday` — fixture date-sensitive
2. `test_multi_verticale.py::TestPerformanceBenchmarks::test_intent_latency_consistency` — flaky timing
3. `test_multi_verticale.py::TestPerformanceBenchmarks::test_booking_flow_latency` — flaky timing

---

## PROSSIMA SESSIONE S76 — AZIONE IMMEDIATA

### P1 — PIANIFICARE F-SARA-VOICE (PRIORITÀ ASSOLUTA)

```
/gsd:plan-phase F-SARA-VOICE
```

**Cosa fa**: FluxionTTS Adaptive — Qwen3-TTS 0.6B + Piper fallback
- Research completo: `memory/project_qwen3tts_sara.md`
- Prerequisito: AudioWorklet ✅ (SODDISFATTO sessione 74)
- Goal: voce Sara più naturale, meno robotica, latency P95 <800ms

### P2 — F17 Windows build (dopo F-SARA-VOICE)
- Prerequisito: VAD Open-Mic ✅ (SODDISFATTO)

### P3 — F15 VoIP (bloccante su EHIWEB credentials)
- Quando arrivano: `/gsd:plan-phase F15`

---

## ARCHITETTURA NLU — STATO ATTUALE (POST S75)

### File modificati in S75
- `voice-agent/src/italian_regex.py` — 6 nuovi verticali + DURATION_MAP + OPERATOR_ROLES
- `voice-agent/src/entity_extractor.py` — sub_vertical field + 6 elif branches
- `voice-agent/src/orchestrator.py` — _extract_vertical_key() updated + bug fix
- `voice-agent/tests/test_hair_beauty_nlu.py` — 122 test
- `voice-agent/tests/test_wellness_medico_nlu.py` — 132 test
- `voice-agent/tests/test_auto_professionale_nlu.py` — 93 test
- `voice-agent/tests/test_nlu_vertical_integration.py` — 64 test

### Struttura verticali post-S75
```
VERTICAL_SERVICES/GUARDRAILS:
  hair (21 groups, 30 patterns) ← alias: salone
  beauty (16 groups, 18 patterns)
  wellness (15 groups, 21 patterns) ← alias: palestra
  medico (18 groups, 20 patterns) ← alias: medical
  auto (18 groups, extended) — unchanged key
  professionale (5 groups, 22 patterns) — nuovo

DURATION_MAP: 6 verticali × servizi (minuti)
OPERATOR_ROLES: 6 verticali × ruoli italiani
VerticalEntities.sub_vertical: Optional[str] — per tutti i verticali non-medico
```

---

## PROMEMORIA TECNICI
- **Riavvio pipeline iMac**: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && [python] main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"`
- **pytest iMac**: `ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && [python] -m pytest tests/ -v --tb=short 2>&1 | tail -40"`
- **type-check MacBook**: `npm run type-check`
- **Qwen3-TTS research**: `memory/project_qwen3tts_sara.md`
