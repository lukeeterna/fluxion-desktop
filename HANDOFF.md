# FLUXION — Handoff Sessione 53 → 54 (2026-03-12)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 6616124
feat(sara): availability filtering by TimeConstraint + test_temporal_constraints.py (58 test)
Working tree: clean
type-check: 0 errori ✅
pytest: 58 PASS (temporal) + 1308 PASS totali (2 failure pre-esistenti non correlati)
iMac: NON raggiungibile s53 — verificare connessione prima di sync
```

---

## ✅ COMPLETATO SESSIONE 53 — F-TEMPORAL: TimeConstraint NLU System

### Commit atomici
| Commit | File | Descrizione |
|--------|------|-------------|
| `9ace839` | `entity_extractor.py` | TimeConstraintType enum + TimeConstraint dataclass (TIMEX3) |
| `7cad242` | `booking_state_machine.py` | FSM constraint-aware + rimozione cerotto c46e966 |
| `6616124` | `orchestrator.py` + `test_temporal_constraints.py` | Slot filtering + 58 test |

### Acceptance criteria verificati
- [x] "dopo le 17" → `TimeConstraint(AFTER, 17:00)` — MAI "17:00" exact
- [x] `time_display` = "dopo le 17:00" non "alle 17:00"
- [x] Loop CONFIRMING eliminato: Sara mostra constraint corretto dall'inizio
- [x] "dopo il lavoro" → AFTER 18:00 (semantic anchor)
- [x] "dopo pranzo" → AFTER 13:30, "a fine giornata" → AFTER 17:00
- [x] `pytest tests/test_temporal_constraints.py` → 58 PASS, 0 FAIL
- [x] `pytest tests/ -v` → 0 nuove regressioni (1308 PASS, 2 failure pre-esistenti)
- [x] `npm run type-check` → 0 errori
- [ ] iMac: git pull + pipeline riavviata + test live T1-T5 ← **TODO quando iMac raggiungibile**

### Architettura implementata (TIMEX3 ISO Standard)
```
entity_extractor.py:
  - TimeConstraintType (7 tipi: EXACT/AFTER/BEFORE/AROUND/RANGE/SLOT/FIRST_AVAILABLE)
  - TimeConstraint dataclass con matches() + display()
  - ExtractedTime.time_constraint: Optional[TimeConstraint]
  - ExtractedTime.get_display() — constraint-aware
  - _SEMANTIC_ANCHORS: 6 frasi italiane → constraint
  - extract_time_constraint() entry point

booking_state_machine.py:
  - BookingContext.time_constraint_type: Optional[str] — serializzabile JSON
  - BookingContext.time_constraint_anchor: Optional[str] — serializzabile JSON
  - _update_context_from_extraction(): tc.display() per time_display
  - _handle_waiting_time(): constraint propagation in tutti i path
  - RIMOSSO: cerotto c46e966 (hardcode +1h)

orchestrator.py:
  - Slot filtering per TimeConstraint in L2 availability check
  - Ricostruzione TimeConstraint da stringhe context
  - Primo slot alternativo che soddisfa constraint → selezionato automaticamente
```

---

## 🎯 PRIORITÀ S54 — PROSSIME FASI DA ROADMAP_REMAINING.md

Leggi `ROADMAP_REMAINING.md` per la fase successiva.

---

## TODO iMac (da fare quando raggiungibile)
1. `git pull origin master` su iMac (`/Volumes/MacSSD - Dati/FLUXION`)
2. Riavvio voice pipeline porta 3002
3. Test live T1-T5 con audio reale (verifica "dopo le 17" → "dopo le 17:00" in risposta Sara)

## ✅ Fix aggiuntivi s53
- `660d235` — hook `check-services.sh` + `session-start.sh`: sostituito `ping 192.168.1.2` con `ssh -o BatchMode=yes imac true` — iMac ora appare ✅ in ogni sessione

---

## Checkout URLs LemonSqueezy (PERMANENTI — MAI richiedere)
- Base €497: `https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3`
- Pro €897: `https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702`
- Clinic €1.497: `https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023`
