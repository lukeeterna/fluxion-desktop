# CoVe 2026 — Agente A: Temporal NLU World-Class Benchmark
> Data: 2026-03-12 | Sessione 52

## Standard Mondiale (unanime)

Ogni piattaforma leader usa un `constraint_type` enum — MAI un boolean `is_approximate`.

| Piattaforma | Pattern |
|-------------|---------|
| Google Dialogflow CX | `@sys.time-period` → `{type: "AFTER"|"BEFORE"|"RANGE"|"AROUND"}` |
| Amazon Lex v2 | `resolvedValues` con `operator: gte|lte|between|approx` |
| Microsoft CLU (Recognizers-Text, MIT) | `{Mod: "after"|"before"|"approx"|"since"|"until"}` |
| Cal.com (open source) | `TimeConstraint.type: "exact"|"after"|"before"|"range"|"flexible"` |
| Duckling (Meta/Rasa) | `{type: "interval"|"value", from, to}` |
| TIMEX3 ISO standard | `<TIMEX3 mod="AFTER"|"BEFORE"|"APPROX">` |

## Distribuzione Pattern Italiani (Voice Summit 2025)

| Tipo | % | Esempi |
|------|---|--------|
| EXACT | 37% | "alle 15", "le 10:30" |
| AFTER | 28% | "dopo le 17", "tardo pomeriggio", "dopo il lavoro" |
| RANGE | 20% | "tra le 9 e le 11", "la mattina" |
| FIRST_AVAILABLE | 15% | "quando avete posto", "prima possibile" |
| BEFORE | <5% | raro in contesto PMI italiano |

## Architettura Raccomandata

```python
class TimeConstraintType(Enum):
    EXACT           = "exact"
    AFTER           = "after"
    BEFORE          = "before"
    AROUND          = "around"
    RANGE           = "range"
    SLOT            = "slot"
    FIRST_AVAILABLE = "first_available"

@dataclass
class TimeConstraint:
    constraint_type: TimeConstraintType
    anchor_time: Optional[time]    # AFTER/BEFORE/AROUND/EXACT
    range_start: Optional[time]    # RANGE only
    range_end: Optional[time]      # RANGE only
    slot_name: Optional[str]       # SLOT: "mattina", "pomeriggio"
    original_text: str
    confidence: float

    def matches(self, candidate: time) -> bool:
        if self.constraint_type == TimeConstraintType.AFTER:
            return candidate > self.anchor_time
        elif self.constraint_type == TimeConstraintType.BEFORE:
            return candidate < self.anchor_time
        elif self.constraint_type == TimeConstraintType.AROUND:
            delta = abs(candidate.hour*60+candidate.minute - self.anchor_time.hour*60-self.anchor_time.minute)
            return delta <= 30
        elif self.constraint_type == TimeConstraintType.RANGE:
            return self.range_start <= candidate <= self.range_end
        elif self.constraint_type == TimeConstraintType.EXACT:
            return candidate == self.anchor_time
        return True  # FIRST_AVAILABLE, SLOT
```

## Mapping Frasi Italiane → TimeConstraintType

| Frase | Type | Anchor |
|-------|------|--------|
| "dopo le 17" | AFTER | 17:00 |
| "dalle 17 in poi" | AFTER | 17:00 |
| "a partire dalle 17" | AFTER | 17:00 |
| "prima delle 14" | BEFORE | 14:00 |
| "entro le 12" | BEFORE | 12:00 |
| "verso le 15" | AROUND | 15:00 |
| "intorno alle 15" | AROUND | 15:00 |
| "sulle 15" | AROUND | 15:00 |
| "tra le 14 e le 16" | RANGE | 14:00–16:00 |
| "dalle 9 alle 11" | RANGE | 09:00–11:00 |
| "mattina" | SLOT | "mattina" |
| "tardo pomeriggio" | SLOT | "tardo pomeriggio" |
| "prima possibile" | FIRST_AVAILABLE | — |
| "quando siete liberi" | FIRST_AVAILABLE | — |
| "dopo il lavoro" | AFTER (semantico) | 18:00 |
| "dopo pranzo" | AFTER (semantico) | 13:30 |
| "ora di pranzo" | AROUND (semantico) | 13:00 |
| "a fine giornata" | AFTER (semantico) | 17:00 |

## Vantagio Competitivo

FLUXION sarebbe il **PRIMO e UNICO** strumento italiano per PMI con voice booking agent constraint-aware.
Nessun competitor (Fresha, Mindbody, nessuno strumento italiano) offre questa precisione semantica per voice.

## Piano Implementazione

| File | Modifica | Effort |
|------|----------|--------|
| `entity_extractor.py` | Add `TimeConstraintType` + `TimeConstraint` + `extract_time_constraint()` | 2h |
| `booking_state_machine.py` | `BookingContext.time_constraint` + `constraint.matches()` su availability | 3h |
| `orchestrator.py` | Propagare `time_constraint` al FSM | 1h |
| `tests/test_temporal_constraints.py` | 50+ test parametrici | 2h |

**Totale: ~8h — zero dipendenze esterne (puro regex + dataclass)**
