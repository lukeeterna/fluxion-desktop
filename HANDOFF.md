# FLUXION — Handoff Sessione 52 → 53 (2026-03-12)

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
Branch: master | HEAD: c46e966
fix(sara): 'dopo le X' in CONFIRMING → suggerisce slot successivo + retry greet
Working tree: 1 file non committato (CLAUDE.md — modifiche minori)
type-check: 0 errori ✅
iMac: NON raggiungibile (192.168.1.2) — verificare connessione
```

---

## ✅ COMPLETATO SESSIONE 52

| Task | Output | Stato |
|------|--------|-------|
| CoVe 2026 Deep Research Temporal NLU | 2 research file in `.claude/cache/agents/` | ✅ |
| Benchmark world-class (Agente A) | `temporal-nlu-research-agente-a.md` | ✅ |
| Gap analysis codebase Sara (Agente B) | `temporal-nlu-research-agente-b.md` | ✅ |

**Fix c46e966 analizzato**: è un cerotto (hardcode +1h, non verifica slot reali, non trigga su "sì"). Da SOSTITUIRE con soluzione strutturale.

---

## 🎯 PRIORITÀ S53 — UNICO TASK

### F-TEMPORAL: TimeConstraint NLU System per Sara

**Business impact**: FLUXION primo e unico strumento italiano PMI con voice booking constraint-aware. Sara smette di loopare su "17:00" quando il cliente dice "dopo le 17".

**Problema reale** (dalla conversazione reale):
```
Fabrizio: "dopo le 17 che torno a lavorare"
Sara: "Riepilogo: alle 17:00 — conferma?"
Fabrizio: "no, DOPO le 17!"
Sara: "Perfetto! ora → 17:00. Confermi ora?"  ← LOOP INFINITO
```

**Root cause confermata** (`entity_extractor.py:579-586`):
```python
# ATTUALE — perde la semantica "dopo"
m = re.search(r'dopo\s+le\s+(\d{1,2})\b', text_n)
if m:
    return ExtractedTime(time=time(h, 0), is_approximate=True)  # ❌ "dopo" scompare
```

**Research files pronti**:
- `.claude/cache/agents/temporal-nlu-research-agente-a.md` — benchmark Dialogflow/Lex/Cal.com/TIMEX3
- `.claude/cache/agents/temporal-nlu-research-agente-b.md` — gap analysis Sara (file:linea esatti)

---

## 📐 ARCHITETTURA TARGET (CoVe 2026 — TIMEX3 ISO + Dialogflow CX pattern)

### TimeConstraintType enum (7 tipi)
```python
class TimeConstraintType(Enum):
    EXACT           = "exact"       # "alle 15:30"
    AFTER           = "after"       # "dopo le 17" — 28% dei casi italiani
    BEFORE          = "before"      # "prima delle 14"
    AROUND          = "around"      # "verso le 15", "intorno alle 15"
    RANGE           = "range"       # "tra le 14 e le 16"
    SLOT            = "slot"        # "mattina", "pomeriggio"
    FIRST_AVAILABLE = "first_available"  # "prima possibile", "quando siete liberi"
```

### TimeConstraint dataclass con matches()
```python
@dataclass
class TimeConstraint:
    constraint_type: TimeConstraintType
    anchor_time: Optional[time]     # AFTER/BEFORE/AROUND/EXACT
    range_start: Optional[time]     # RANGE only
    range_end: Optional[time]       # RANGE only
    slot_name: Optional[str]        # SLOT: "mattina", "pomeriggio"
    original_text: str
    confidence: float

    def matches(self, candidate: time) -> bool:
        if self.constraint_type == TimeConstraintType.AFTER:
            return candidate > self.anchor_time
        elif self.constraint_type == TimeConstraintType.BEFORE:
            return candidate < self.anchor_time
        elif self.constraint_type == TimeConstraintType.AROUND:
            delta = abs((candidate.hour*60+candidate.minute) - (self.anchor_time.hour*60+self.anchor_time.minute))
            return delta <= 30
        elif self.constraint_type == TimeConstraintType.RANGE:
            return self.range_start <= candidate <= self.range_end
        return True  # EXACT, FIRST_AVAILABLE, SLOT
```

### Mapping frasi italiane → tipo
| Frase | Tipo | Anchor |
|-------|------|--------|
| "dopo le 17" | AFTER | 17:00 |
| "dalle 17 in poi" | AFTER | 17:00 |
| "prima delle 14" | BEFORE | 14:00 |
| "verso le 15" / "sulle 15" | AROUND | 15:00 |
| "tra le 14 e le 16" | RANGE | 14:00–16:00 |
| "mattina" / "pomeriggio" | SLOT | nome slot |
| "prima possibile" | FIRST_AVAILABLE | — |
| "dopo il lavoro" | AFTER (semantico) | 18:00 |
| "dopo pranzo" | AFTER (semantico) | 13:30 |
| "a fine giornata" | AFTER (semantico) | 17:00 |

---

## 📋 PIANO IMPLEMENTAZIONE 3 FASI

### Fase 1 — entity_extractor.py (2-3h)
- Aggiungere `TimeConstraintType` enum + `TimeConstraint` dataclass
- Modificare `extract_time()` linee 579-596 per AFTER/BEFORE → constraint type
- Aggiungere semantic anchors italiani
- Aggiungere `extract_time_constraint()` entry point

### Fase 2 — booking_state_machine.py (2h)
- `BookingContext`: aggiungere `time_constraint: Optional[TimeConstraint] = None`
- `_update_context_from_extraction()`: propagare constraint + `time_display` corretto
- `get_summary()`: mostrare "dopo le 17:00" non "alle 17:00"
- **RIMUOVERE** fix c46e966 (sostituito)
- `_handle_confirming()`: usare `constraint.matches()` per proporre slot corretto

### Fase 3 — orchestrator.py + availability_checker.py (3h)
- Passare `time_constraint` al check availability
- Query filtrata per constraint type (AFTER → `WHERE ora > 'HH:MM'`)
- Ritornare primo slot che soddisfa `constraint.matches()`

### Test (2h)
- Nuovo file `tests/test_temporal_constraints.py` — 50+ test parametrici
- Aggiornare ~140 test esistenti impattati (time_display + constraint assertions)

---

## Acceptance Criteria (MISURABILI)

- [ ] "dopo le 17" → `TimeConstraint(AFTER, 17:00)` — MAI "17:00" exact
- [ ] Sara risponde "Capito, dopo le 17:00! Il primo slot disponibile è alle 18:00 — conferma?"
- [ ] Loop CONFIRMING risolto: nessuna ripetizione infinita
- [ ] "dopo il lavoro" → AFTER 18:00 (semantic anchor)
- [ ] `pytest tests/test_temporal_constraints.py` → 50+ PASS, 0 FAIL
- [ ] `pytest tests/ -v` → 0 regressioni sui test esistenti
- [ ] iMac: pipeline riavviata + test live T1-T5

---

## File Chiave da Leggere Prima di Toccare Codice
```
voice-agent/src/_INDEX.md                      # SEMPRE prima
voice-agent/src/entity_extractor.py            # linee 72-80, 579-596
voice-agent/src/booking_state_machine.py       # linee 110-169, 924-927, 2418-2442
voice-agent/src/orchestrator.py                # propagazione context
.claude/cache/agents/temporal-nlu-research-agente-a.md  # benchmark world-class
.claude/cache/agents/temporal-nlu-research-agente-b.md  # gap analysis esatto
```

---

## Checkout URLs LemonSqueezy (PERMANENTI — MAI richiedere)
- Base €497: `https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3`
- Pro €897: `https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702`
- Clinic €1.497: `https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023`
