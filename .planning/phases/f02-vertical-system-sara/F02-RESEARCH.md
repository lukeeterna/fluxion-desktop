# Phase F02: Vertical System Sara — Research

**Researched:** 2026-03-04
**Domain:** Python 3.9 voice agent — vertical-aware NLU, guardrails, entity extraction
**Confidence:** HIGH (all findings from direct source inspection)

---

## Summary

F02 makes Sara "vertical-aware" by (1) injecting guardrails that redirect out-of-scope queries and (2) routing service entity extraction through the correct vertical's synonym table. The research reveals that most of the vertical infrastructure is already built: four vertical directories exist (`salone/`, `palestra/`, `medical/`, `auto/`), each with a `entities.py`, `config.json`, and `intents.py`. The orchestrator already reads `categoria_attivita` from the DB, exposes `set_vertical()`, and loads per-vertical FAQs. The `booking_state_machine.py` already defines four `CORRECTION_PATTERNS_*` dicts and passes `services_config` per-vertical to `extract_service()`. The `italian_regex.py` L0 layer already has a full `VERTICAL_SERVICES` dict with all synonyms for salone, palestra, medical, and auto.

**What is missing:** (a) No guardrail logic exists anywhere — no out-of-scope query detection, no vertical boundary enforcement. (b) The per-vertical `entities.py` extractors are never called from the orchestrator or FSM. The orchestrator uses only the generic `entity_extractor.py` functions. (c) The `vertical` field in `BookingContext` is set but never used to route entity extraction in the FSM. (d) No "professionally appropriate" guardrails exist (e.g., a salone Sara should not discuss medical diagnoses).

**Primary recommendation:** Build guardrails as a new L0-pre stage in `orchestrator.py` using pure regex keyword blocklists (zero latency impact, no LLM). Build the vertical entity extractor bridge as a thin wrapper in `entity_extractor.py` that delegates to the active vertical's synonym table from `italian_regex.VERTICAL_SERVICES`.

---

## Current State (What Already Exists)

### Vertical Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Vertical service synonyms | `src/italian_regex.py` — `VERTICAL_SERVICES` dict | COMPLETE — salone, palestra, medical, auto |
| Vertical per-service extractor | `verticals/salone/entities.py`, `verticals/medical/entities.py`, etc. | EXISTS but UNUSED by orchestrator |
| Vertical config JSON | `verticals/salone/config.json`, `verticals/medical/config.json`, etc. | EXISTS (intents, slots, FAQs, vars) |
| Vertical manager | `verticals/vertical_manager.py` | EXISTS (loads JSON configs) |
| Vertical integration | `src/vertical_integration.py` | EXISTS (adapter class, not used in hot path) |
| Vertical FAQ loader | `src/vertical_loader.py` | USED — loads FAQ files per vertical |
| Vertical correction patterns | `src/booking_state_machine.py` — `CORRECTION_PATTERNS_SALONE/PALESTRA/MEDICAL/AUTO` | COMPLETE — used in CONFIRMING state |
| Vertical context field | `BookingContext.vertical` (default `"salone"`) | EXISTS but never used to route NLU |
| `set_vertical()` in orchestrator | `src/orchestrator.py:1561` | EXISTS — reloads FAQs, updates context |
| `categoria_attivita` loaded from DB | `src/orchestrator.py:390` | WORKS — sets `_faq_vertical` |

### `extract_service()` Current Call Pattern

The generic extractor in `src/entity_extractor.py` takes `services_config` as a parameter:

```python
def extract_service(
    text: str,
    services_config: Dict[str, List[str]],   # <-- vertical-specific synonyms
    fuzzy_threshold: float = 0.8
) -> Optional[Tuple[str, float]]:
```

The `booking_state_machine.py` receives `services_config` at init time and calls `extract_service(text, self.services_config)`. In tests, the FSM is instantiated with `services_config=VERTICALE_SERVICES["salone"]` etc. In production (orchestrator), `BookingStateMachine(groq_nlu=self._groq_nlu)` is called with NO `services_config`, so it falls back to an internal default or empty dict.

The vertical synonyms are defined in BOTH places:
1. `src/italian_regex.py` — `VERTICAL_SERVICES` — used by `extract_multi_services()`
2. `tests/test_multi_verticale.py` — `VERTICALE_SERVICES` — test-only dict

**Gap:** Production FSM does not receive `services_config` from the active vertical at startup.

### What Guardrails Exist Today

The L0 layer (`italian_regex.py`) has:
- Content filter (mild/moderate/severe language)
- Escalation detection
- Correction patterns
- No vertical out-of-scope detection whatsoever

---

## Gap Analysis (What Is Missing)

### Gap 1: No Guardrails (Primary Missing Feature)

No code exists to detect or redirect queries outside the business vertical's scope. A medical clinic Sara will happily discuss car engine repairs via Groq LLM if the question makes it to L4.

Missing: A vertical-aware out-of-scope detector that intercepts at L0-pre and responds with a polite redirect instead of falling through to L4-Groq.

### Gap 2: Production FSM Does Not Use Vertical Services Config

The orchestrator instantiates `BookingStateMachine(groq_nlu=self._groq_nlu)` without passing `services_config`. Service extraction in production falls back to defaults or fails. The test suite uses explicit `services_config` but production does not.

Missing: The orchestrator must pass the active vertical's `services_config` to the FSM at `start_session()` or when `set_vertical()` is called.

### Gap 3: The Per-Vertical `entities.py` Classes Are Orphaned

Each `verticals/*/entities.py` defines a `SaloneEntityExtractor`, `MedicalEntityExtractor`, etc. with `.extract_all()`. These are never imported or called anywhere in the production pipeline. They are dead code from an earlier design.

Decision needed: Either connect them to the pipeline, or use the existing `italian_regex.VERTICAL_SERVICES` synonyms (already battle-tested, pre-compiled, <1ms) as the single source of truth.

**Recommendation: Use `italian_regex.VERTICAL_SERVICES` as the entity source.** The per-vertical `entities.py` duplicates the synonym work with lower quality (no Levenshtein fuzzy matching, simpler regex). The generic `entity_extractor.py:extract_service()` with fuzzy matching is far superior.

### Gap 4: `BookingContext.vertical` Never Used for Routing

`BookingContext.vertical` is set when the orchestrator calls `set_vertical()`. But the FSM never reads `context.vertical` to select the active synonym table. The field exists without any consumer.

---

## Implementation Approach

### Guardrails Architecture

**Where to inject:** Between L0 (special commands) and L0a (WhatsApp FAQ) in `orchestrator.py:process()`. This is the L0-guardrail stage. Runs BEFORE intent classification, BEFORE FAQ, BEFORE Groq.

**Implementation:** Pure regex keyword blocklists — one dict per macro-vertical. NO LLM. NO external calls. Target: < 5ms worst case (realistically < 1ms with pre-compiled patterns).

**Data structure:**

```python
# In src/italian_regex.py (or new src/guardrails.py)
VERTICAL_GUARDRAILS: Dict[str, Dict[str, List[str]]] = {
    "salone": {
        "blocked_topics": [
            r"\b(?:diagnos[i]?|malattia|farmac[io]|ricetta|prescrizione)\b",
            r"\b(?:tagliando|gomm[e]|freni|motore|officina)\b",
            r"\b(?:abbonamento|corsi|palestra|personal\s+trainer)\b",
        ],
        "redirect_response": "Mi occupo delle prenotazioni per il salone. Posso aiutarla con un appuntamento?"
    },
    "medical": {
        "blocked_topics": [
            r"\b(?:taglio\s+capelli|piega|colore|barba|manicure|pedicure)\b",
            r"\b(?:tagliando|gomm[e]|freni|motore|officina)\b",
            r"\b(?:palestra|corso\s+di\s+yoga|abbonamento\s+mensile)\b",
        ],
        "redirect_response": "Sono Sara, l'assistente dello studio medico. Posso aiutarla a prenotare una visita?"
    },
    "palestra": {
        "blocked_topics": [
            r"\b(?:taglio\s+capelli|piega|colore|manicure)\b",
            r"\b(?:diagnos[i]?|prescrizione|farmac[io])\b",
            r"\b(?:tagliando|freni|gomm[e])\b",
        ],
        "redirect_response": "Sono Sara, l'assistente della palestra. Posso aiutarla con iscrizioni o prenotazione corsi?"
    },
    "auto": {
        "blocked_topics": [
            r"\b(?:taglio\s+capelli|piega|colore|manicure)\b",
            r"\b(?:diagnos[i]?\s+medic|prescrizione|farmac[io])\b",
            r"\b(?:yoga|pilates|palestra|abbonamento)\b",
        ],
        "redirect_response": "Mi occupo delle prenotazioni per l'officina. Posso aiutarla con un intervento o tagliando?"
    },
}
```

**Where in `orchestrator.py:process()`** — inject AFTER L0-pre content/escalation check but BEFORE special commands:

```python
# L0-GUARDRAIL (new): Vertical out-of-scope detection
if response is None and HAS_GUARDRAILS:
    guardrail_result = check_vertical_guardrail(user_input, self._faq_vertical)
    if guardrail_result.is_blocked:
        response = guardrail_result.redirect_response
        intent = "guardrail_out_of_scope"
        layer = ProcessingLayer.L0_SPECIAL
        # Do NOT escalate — user simply gets redirect
```

### Entity Extractor Bridge

**Where:** In `booking_state_machine.py` init and in `orchestrator.set_vertical()`.

The FSM already has `services_config` parameter. The fix is to pass the correct vertical's synonyms at orchestrator init and on `set_vertical()`:

```python
# In orchestrator.py __init__:
from .italian_regex import VERTICAL_SERVICES
_vertical_services = VERTICAL_SERVICES.get(self._faq_vertical, VERTICAL_SERVICES["salone"])
self.booking_sm = BookingStateMachine(
    groq_nlu=self._groq_nlu,
    services_config=_vertical_services  # ADD THIS
)

# In orchestrator.set_vertical():
self.booking_sm.services_config = VERTICAL_SERVICES.get(vertical, VERTICAL_SERVICES["salone"])
```

The `VERTICAL_SERVICES` in `italian_regex.py` already has comprehensive synonym lists for salone, palestra, medical, and auto — these are already pre-compiled for multi-service extraction and already used in tests.

### Domain-Specific Entity Extraction for Specialty/Vehicle

Medical vertical needs to extract `specialty` (cardiologo, dermatologo, etc.) and `urgency`. Auto vertical needs to extract `marca` and `targa`. These are NOT in the generic entity extractor.

**Approach:** Add thin vertical-specific extraction functions to `entity_extractor.py`, activated by vertical context:

```python
def extract_vertical_entities(
    text: str,
    vertical: str,
    services_config: Dict[str, List[str]]
) -> Dict[str, Any]:
    """Extract vertical-specific entities beyond standard service/date/time/name."""
    extras = {}

    if vertical == "medical":
        extras["specialty"] = _extract_medical_specialty(text)
        extras["urgency"] = _extract_medical_urgency(text)
        extras["visit_type"] = _extract_visit_type(text)

    elif vertical == "auto":
        extras["vehicle_plate"] = _extract_targa(text)
        extras["vehicle_brand"] = _extract_car_brand(text)

    elif vertical in ("salone", "hair"):
        extras["hair_length"] = _extract_hair_length(text)

    elif vertical in ("palestra", "wellness"):
        extras["trainer_name"] = extract_operator(text)  # reuse existing

    return extras
```

---

## File Map (Which Files to Touch)

### Files to MODIFY

| File | Change | Risk |
|------|--------|------|
| `voice-agent/src/italian_regex.py` | Add `VERTICAL_GUARDRAILS` dict + `check_vertical_guardrail()` function. Add to `RegexPreFilterResult` and `prefilter()`. | LOW — additive only |
| `voice-agent/src/orchestrator.py` | (1) Pass `services_config` to FSM at init. (2) Pass `services_config` in `set_vertical()`. (3) Inject guardrail check in `process()` between L0-pre and L0 special commands. | MEDIUM — existing pipeline, surgical edits |
| `voice-agent/src/entity_extractor.py` | Add `extract_vertical_entities()` function with medical specialty, urgency, auto plate/brand extractors. | LOW — new function, no changes to existing |

### Files to NOT MODIFY

| File | Reason |
|------|--------|
| `voice-agent/src/booking_state_machine.py` | `CORRECTION_PATTERNS_*` already correct. `services_config` param already exists. No changes needed. |
| `voice-agent/verticals/*/entities.py` | Dead code — do not wire up (would create duplication). |
| `voice-agent/verticals/vertical_manager.py` | Not in hot path, no changes needed. |
| `voice-agent/src/vertical_integration.py` | Not in hot path. |
| Any test files | Only ADD new test files. |

### New Files to CREATE

| File | Purpose |
|------|---------|
| `voice-agent/tests/test_guardrails.py` | Unit tests for vertical guardrail patterns (all 4 verticals) |
| `voice-agent/tests/test_vertical_entity_extractor.py` | Tests for `extract_vertical_entities()` (medical specialty, urgency, auto plate) |

---

## Risk / Edge Cases

### Risk 1: Guardrail False Positives
**Problem:** A patient at a medical clinic might say "Ho il colore della pelle che ha problemi" — this contains "colore" which would match the salone-in-medical blocklist.
**Mitigation:** Guardrails must require medical-specific context (e.g. "colore capelli", "taglio capelli"), not just the bare word "colore". Use multi-word patterns, not single-word blocklists.
**Confidence:** HIGH risk, must be addressed in pattern design.

### Risk 2: Test Suite Regression
**Problem:** 1160 tests must stay at 1160 PASS. FSM gets `services_config` in tests via fixture. If orchestrator now passes it differently, tests could fail.
**Mitigation:** The test suite instantiates `BookingStateMachine(services_config=VERTICALE_SERVICES["salone"])` directly — it bypasses the orchestrator. Changes to orchestrator's `__init__` will NOT break existing tests. Only NEW tests could fail.
**Confidence:** LOW risk if orchestrator-level change is limited to `__init__` and `set_vertical()`.

### Risk 3: Latency Budget
**Constraint:** Guardrails must add < 20ms (stated requirement: < 20ms, but given L0 is regex the realistic target is < 2ms).
**Mitigation:** All patterns pre-compiled at module load. `prefilter()` already runs in < 1ms. Adding guardrail check to `prefilter()` adds ~0.3ms.
**Confidence:** HIGH — pure regex with pre-compiled patterns is deterministic.

### Risk 4: Missing Vertical ("altro" / "wellness" / "professionale")
**Problem:** The schema has 6 macro-verticals (`medico`, `beauty`, `hair`, `auto`, `wellness`, `professionale`) but the orchestrator only supports 5 vertical keys (`salone`, `palestra`, `wellness`, `medical`, `auto`, `altro`). The `VerticalIntegration.detect_vertical_from_category()` maps `hair` macros to `salone`, `medical` macros to `medical`, `wellness` to `palestra`.
**Mitigation:** F02 should cover the 4 primary verticals (salone, palestra, medical, auto). `wellness` and `professionale` can share `salone` guardrails as a safe default. Document this clearly.

### Risk 5: `BookingStateMachine.services_config` Is Reset on `.reset()`
**Problem:** When `self.booking_sm.reset(full_reset=True)` is called, `services_config` may be reset to default.
**Mitigation:** Verify `reset()` preserves `services_config`. If not, orchestrator must re-pass it after reset. Check `booking_state_machine.py:reset()`.

---

## Acceptance Criteria Suggestions

### AC-1: Guardrails Block Out-of-Scope Topics
- `salone` Sara responds with redirect (not Groq answer) when asked about tagliando/freni/diagnosi medica/yoga course
- `medical` Sara responds with redirect when asked about taglio capelli/barba/tagliando auto/palestra
- `palestra` Sara responds with redirect when asked about taglio/diagnosi/tagliando
- `auto` Sara responds with redirect when asked about taglio capelli/diagnosi medica/yoga
- Redirect response is in Italian, polite, < 20 words
- Guardrail adds < 5ms latency (measure with `time.time()` before/after `check_vertical_guardrail()`)

### AC-2: Vertical Service Extraction Is Correct
- `salone` FSM extracts "taglio" from "vorrei un taglio" but NOT from "voglio fare yoga"
- `palestra` FSM extracts "yoga" from "vorrei fare yoga" but NOT from "voglio un taglio"
- `medical` FSM extracts "visita" from "vorrei prenotare una visita" but NOT "taglio"
- `auto` FSM extracts "tagliando" from "devo fare il tagliando" but NOT salone services
- Service extraction isolation tests (adapt `TestCrossVerticaleIsolation` in `test_multi_verticale.py`)

### AC-3: Medical-Specific Entities Extracted
- "Ho dolore forte, è urgente" → `urgency = "alta"`
- "Dal cardiologo" → `specialty = "cardiologia"`
- "Visita dermatologica" → `specialty = "dermatologia"`
- "Prima visita" → `visit_type = "prima_visita"`

### AC-4: Auto-Specific Entities Extracted
- "La targa è AB123CD" → `vehicle_plate = "AB123CD"`
- "Ho una Fiat Panda" → `vehicle_brand = "fiat"`

### AC-5: Test Suite Stays Green
- `npm run type-check` passes (no TS changes in F02)
- `pytest voice-agent/tests/ -v` → 1160 PASS / 0 FAIL (existing) + new tests
- New tests: `test_guardrails.py`, `test_vertical_entity_extractor.py`

---

## Code Examples

### Guardrail Function Pattern
```python
# src/italian_regex.py — add to existing module

@dataclass
class GuardrailResult:
    is_blocked: bool
    redirect_response: str = ""
    blocked_topic: str = ""

# Key design: use MULTI-WORD patterns to avoid false positives
VERTICAL_GUARDRAILS: Dict[str, Dict] = {
    "salone": {
        "blocked_patterns": [
            # Medical topics
            r"\b(?:diagnos[i]?|prescrizione\s+medic|farmac[io]\s+(?:da\s+prendere|prescritto))\b",
            r"\b(?:visita\s+medic|dottore|medico\s+curante|specialista\s+medic)\b",
            # Auto topics
            r"\b(?:tagliando|cambio\s+(?:olio|gomme|freni)|officina|meccanico|carrozzeria)\b",
            # Gym topics
            r"\b(?:abbonamento\s+(?:mensile|annuale|palestra)|corso\s+di\s+yoga|personal\s+trainer\s+per)\b",
        ],
        "redirect": "Mi occupo del salone. Posso aiutarla con un appuntamento per taglio, colore o altri servizi?"
    },
    # ... other verticals
}

_GUARDRAIL_COMPILED: Dict[str, List[re.Pattern]] = {
    vertical: [re.compile(p, re.IGNORECASE) for p in data["blocked_patterns"]]
    for vertical, data in VERTICAL_GUARDRAILS.items()
}

def check_vertical_guardrail(text: str, vertical: str) -> GuardrailResult:
    """Check if text is out-of-scope for the given vertical. <1ms."""
    patterns = _GUARDRAIL_COMPILED.get(vertical, [])
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return GuardrailResult(
                is_blocked=True,
                redirect_response=VERTICAL_GUARDRAILS[vertical]["redirect"],
                blocked_topic=m.group(0)
            )
    return GuardrailResult(is_blocked=False)
```

### Services Config Bridge in Orchestrator
```python
# src/orchestrator.py __init__ — add VERTICAL_SERVICES import and pass to FSM
from .italian_regex import VERTICAL_SERVICES as _VERTICAL_SERVICES

# In __init__:
_vertical_services = _VERTICAL_SERVICES.get(self._faq_vertical, _VERTICAL_SERVICES.get("salone", {}))
self.booking_sm = BookingStateMachine(
    groq_nlu=self._groq_nlu,
    services_config=_vertical_services
)

# In set_vertical():
self.booking_sm.services_config = _VERTICAL_SERVICES.get(vertical, _VERTICAL_SERVICES.get("salone", {}))
```

### Medical Specialty Extractor
```python
# src/entity_extractor.py — new function

_MEDICAL_SPECIALTY_PATTERNS = {
    "cardiologia": [r"\b(?:cardiologo|cardiologica?|cardio|cuore|elettrocardiogramma|ecg)\b"],
    "dermatologia": [r"\b(?:dermatologo|dermatologica?|nei|pelle|acne|mappatura\s+nei)\b"],
    "ortopedia": [r"\b(?:ortopedico|ortopedica?|osso|ossa|frattura|colonna)\b"],
    "oculistica": [r"\b(?:oculista|vista|occhi|occhiali|lenti)\b"],
    "ginecologia": [r"\b(?:ginecologo|ginecologica?|pap\s+test|mammografia)\b"],
    "pediatria": [r"\b(?:pediatra|pediatrica?|bambino|bambina|figlio)\b"],
    "fisioterapia": [r"\b(?:fisioterapista|fisioterapia|riabilitazione|seduta)\b"],
    "odontoiatria": [r"\b(?:dentista|odontoiatra|denti|carie|otturazione)\b"],
}

_MEDICAL_SPECIALTY_COMPILED = {
    spec: [re.compile(p, re.IGNORECASE) for p in patterns]
    for spec, patterns in _MEDICAL_SPECIALTY_PATTERNS.items()
}

def _extract_medical_specialty(text: str) -> Optional[str]:
    """Extract medical specialty from text. Source: research F02."""
    for specialty, patterns in _MEDICAL_SPECIALTY_COMPILED.items():
        for pattern in patterns:
            if pattern.search(text):
                return specialty
    return None
```

---

## State of the Art

| Old Approach | Current Approach | Impact for F02 |
|--------------|------------------|----------------|
| Per-vertical extractor classes in `verticals/*/entities.py` | Generic `entity_extractor.py` with `services_config` param | Use generic extractor + VERTICAL_SERVICES config |
| No guardrails | Add regex L0-guardrail | New feature, < 1ms |
| `BookingStateMachine()` with no services_config in production | Pass VERTICAL_SERVICES[vertical] at init | Fix silent failure |

---

## Open Questions

1. **Does `BookingStateMachine.reset()` preserve `services_config`?**
   - What we know: `reset()` is called at start of every session
   - What's unclear: Whether it resets `self.services_config` to default or preserves it
   - Recommendation: Verify by reading `booking_state_machine.py:reset()` (lines ~450-500) before implementing; if it resets, the orchestrator must re-pass services_config after reset

2. **Should `wellness` and `professionale` macro-verticals have their own guardrails?**
   - What we know: `wellness` maps to `palestra` vertical, `professionale` has no vertical in the voice agent
   - What's unclear: Whether `professionale` (commercialista, avvocato) needs Sara at all
   - Recommendation: Use `salone` guardrails as fallback for unknown verticals (safest)

3. **`beauty` macro maps to which guardrail vertical?**
   - What we know: `beauty` micro-categories are estetista_viso/corpo, nail_specialist, spa — these are all handled by `salone` vertical FAQ
   - What's unclear: Do estetisti have unique out-of-scope risks different from salone?
   - Recommendation: Map `beauty` to `salone` guardrails for F02

---

## Sources

### Primary (HIGH confidence — direct source inspection)

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/italian_regex.py` — VERTICAL_SERVICES dict, prefilter(), ContentFilter, all L0 patterns
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py` — VoiceOrchestrator.__init__(), process(), set_vertical(), _extract_vertical_key(), _load_vertical_faqs()
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/entity_extractor.py` — extract_service(), extract_services(), extract_vertical_entities(), Levenshtein fuzzy matching
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/booking_state_machine.py` — BookingContext.vertical, CORRECTION_PATTERNS_*, BookingStateMachine.__init__()
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/vertical_integration.py` — VerticalIntegration class, detect_vertical_from_category()
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/vertical_loader.py` — VERTICAL_FAQ_MAP, load_faqs_for_vertical()
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/salone/entities.py` — SaloneEntityExtractor (dead code)
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/salone/config.json` — full vertical config schema
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/medical/entities.py` — MedicalEntityExtractor (dead code)
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/medical/config.json` — medical slot definitions (specialty slot)
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_multi_verticale.py` — existing vertical isolation tests
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_vertical_corrections.py` — CORRECTION_PATTERNS_* test coverage
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/vertical_schemas.py` — customer card schemas per vertical
- `/Volumes/MontereyT7/FLUXION/src/types/setup.ts` — MACRO_CATEGORIE, MICRO_CATEGORIE, vertical mapping
- `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/sub-verticals-research.md` — domain entity research per sub-vertical

---

## Metadata

**Confidence breakdown:**
- Current state inventory: HIGH — all findings from direct file inspection
- Gap analysis: HIGH — confirmed by tracing call paths in orchestrator
- Guardrail pattern design: MEDIUM — patterns look reasonable but need validation against real STT output edge cases
- Latency impact: HIGH — pure regex, pre-compiled, same pattern as existing L0

**Research date:** 2026-03-04
**Valid until:** 2026-04-04 (stable codebase, no external dependencies)
