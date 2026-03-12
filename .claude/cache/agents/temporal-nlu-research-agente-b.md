# CoVe 2026 — Agente B: Gap Analysis Sara Codebase
> Data: 2026-03-12 | Sessione 52

## Root Cause Esatta

### Codepath Bug "dopo le 17"

```
User: "dopo le 17" (in WAITING_TIME o CONFIRMING)
    ↓
entity_extractor.py:579-586 extract_time()
    Regex: r'dopo\s+le\s+(\d{1,2})\b'
    Returns: ExtractedTime(time=17:00, is_approximate=True)
    ❌ SEMANTIC LOSS: "dopo" scompare, diventa boolean generico
    ↓
booking_state_machine.py:924-927 _update_context_from_extraction()
    context.time = "17:00"
    context.time_display = "alle 17:00"
    context.time_is_approximate = True
    ↓
FSM → CONFIRMING: "Riepilogo: alle 17:00 — conferma?"
    ↓
User: "no, dopo le 17!" (non sta rifiutando — sta correggendo)
    ↓
Fix c46e966 (lines 2418-2442) matching "dopo le X"
    → Suggerisce +1h hardcoded (18:00)
    ❌ Non verifica slot reali
    ❌ Loop se utente rifiuta ancora
    ❌ NON trigga se utente dice "sì" (nessun "dopo" nel testo)
```

## Perché il Fix c46e966 Non Funziona

1. **Caso "sì"**: Utente dice "sì, ma dopo le 17". Regex cerca "dopo" ma l'utente potrebbe dire solo "sì" → context rimane "17:00" → booking creato a 17:00 (sbagliato)
2. **Hardcode +1h**: suggerisce sempre +1h senza availability check → potrebbe suggerire slot occupato
3. **Solo in CONFIRMING**: il problema inizia in WAITING_TIME quando l'entity extractor perde il semantic marker

## Struttura Dati Attuale vs Necessaria

### ExtractedTime (entity_extractor.py:72-80) — ATTUALE
```python
@dataclass
class ExtractedTime:
    time: time
    original_text: str
    confidence: float
    is_approximate: bool    # ❌ binario — insufficiente
    # MANCA: time_constraint_type
    # MANCA: time_constraint_bound
```

### BookingContext (booking_state_machine.py:110-169) — ATTUALE
```python
@dataclass
class BookingContext:
    time: Optional[str] = None
    time_display: Optional[str] = None
    time_is_approximate: bool = False    # ❌ binario
    # MANCA: time_constraint: Optional[TimeConstraint]
```

## Coverage Matrix Attuale

| Pattern | Stato | Linea | Problema |
|---------|-------|-------|----------|
| "alle 15:30" | ✅ | 492-502 | OK |
| "dopo le 17" | ⚠️ BROKEN | 579-586 | Perde "dopo" |
| "prima delle 14" | ⚠️ BROKEN | 589-596 | Perde "prima" |
| "verso le 10" | ✅ | 599-606 | is_approximate=True (ok) |
| "tra le 14 e le 16" | ✅ | 551-562 | Ritorna midpoint |
| "mattina/pomeriggio" | ✅ | 626-634 | Default slot time |

## Gap Completi per Severità

| Gap | File | Linea | Severità |
|-----|------|-------|----------|
| No `time_constraint_type` field | entity_extractor.py | 72-80 | P0 |
| "dopo le X" perde semantica | entity_extractor.py | 579-586 | P0 |
| "prima delle X" perde semantica | entity_extractor.py | 589-596 | P0 |
| `time_display` sempre "alle HH:MM" | booking_state_machine.py | 926 | P1 |
| Fix CONFIRMING solo parziale | booking_state_machine.py | 2418-2442 | P1 |
| No availability filtering per constraint | orchestrator.py/availability_checker.py | — | P1 |
| "dopo le X:MM" (con minuti) | entity_extractor.py | 579-586 | P1 |
| Compound constraints | — | — | P2 |

## Piano Modifica File per File

### Fase 1 — entity_extractor.py (2-3h)
- Aggiungere `TimeConstraintType` enum
- Aggiungere `TimeConstraint` dataclass con metodo `matches(candidate: time) -> bool`
- Modificare `extract_time()` per "dopo le X" → `TimeConstraint(AFTER, 17:00)`
- Modificare `extract_time()` per "prima delle X" → `TimeConstraint(BEFORE, 14:00)`
- Aggiungere anchor semantici: "dopo il lavoro" → AFTER 18:00

### Fase 2 — booking_state_machine.py (2h)
- `BookingContext`: aggiungere campo `time_constraint: Optional[TimeConstraint]`
- `_update_context_from_extraction()`: propagare constraint + aggiornare `time_display`
- `get_summary()`: mostrare "dopo le 17:00" invece di "alle 17:00"
- Rimuovere fix c46e966 (sostituito da soluzione strutturale)

### Fase 3 — orchestrator.py + availability_checker.py (3h)
- Passare `time_constraint` a check availability
- Query filtrata: `WHERE ora > '17:00'` per AFTER, ecc.
- Ritornare primo slot che soddisfa `constraint.matches()`

## Test da Aggiornare

| File | N test impattati | Tipo impatto |
|------|-----------------|--------------|
| test_entity_extractor.py | ~40 | Assertion su `time_constraint_type` |
| test_booking_state_machine.py | ~50 | `time_display` cambia |
| test_orchestrator.py | ~30 | Availability con constraint |
| test_availability_checker.py | ~20 | Filtering constraint |

**Nuovo file**: `tests/test_temporal_constraints.py` — 50+ test parametrici
