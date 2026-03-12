# FLUXION — Handoff Sessione 57 → 58 (2026-03-12)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 1e1ad49
fix(sara): Sprint 2 P1 — 13 fix concorrenti, time pressure, slot waterfall, sessioni
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1323 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 57 — Sara Enterprise Sprint 2 (DONE)

### Tutti i 13 fix P1 implementati in commit atomico `1e1ad49`

| Fix | ID | Descrizione | Stato |
|-----|----|-------------|-------|
| P1-3 | — | Streaming LLM (già presente, verify only) | ✅ verificato |
| P1-10 | italian_regex.py | Anchors CONFERMA ("va beh", "esatto esatto") + RIFIUTO ("negativo", "negato") | ✅ |
| P1-11 | booking_state_machine.py | "anzi" standalone → chiede cosa cambiare | ✅ |
| P1-12 | italian_regex.py + orchestrator.py | is_time_pressure() + _time_pressure sticky flag + LLM hint urgenza | ✅ |
| P1-13 | entity_extractor.py + BSM | extract_exclude_days() + BookingContext.exclude_days field | ✅ |
| P1-9 | orchestrator.py | _trigger_wa_escalation_call con stato FSM completo | ✅ |
| P1-6 | orchestrator.py | Selezione ordinale slot (primo/secondo/terzo) quando alternatives presenti | ✅ |
| P1-7 | orchestrator.py | FAQ mid-booking resume — riagancia al flusso dopo risposta FAQ | ✅ |
| P1-5 | orchestrator.py | Slot waterfall — alternative_slots[:3] + proposta automatica primo slot | ✅ |
| P1-2 | orchestrator.py | Handler "first_available" + check_first_available() + exclude_days passaggio | ✅ |
| P1-1 | orchestrator.py | Multi-servizio — booking_data arricchito con context.services | ✅ |
| P1-4 | orchestrator.py | Fallback progressivo L3.8 — FAQ prima di error/timeout/ratelimit | ✅ |
| P1-8 | orchestrator.py | Per-session BSM state dict (_session_states) + persist/restore + cleanup | ✅ |

**pytest iMac S57**: 1323 PASS / 0 FAIL ✅

---

## PROSSIMA SESSIONE S58 — Sprint 3 / F02 Vertical Guardrail

> **Skill**: `fluxion-voice-agent`
> **Research valida**: `.claude/cache/agents/f02-nlu-comprehensive-patterns.md`

### Priorità S58:
1. **F02 Vertical Guardrail** — SPOSTAMENTO pattern fix, verb-form patterns, guardrail late check
2. **Live audio test** su iMac (T1-T5 scenari in `.claude/rules/voice-agent-details.md`)
3. **Latency P95** — target < 800ms (attuale ~1330ms — F03 in backlog)

---

## Riavvio pipeline iMac:
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
