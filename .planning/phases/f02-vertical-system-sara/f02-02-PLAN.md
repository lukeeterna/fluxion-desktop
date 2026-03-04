---
phase: f02-vertical-system-sara
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/orchestrator.py
  - voice-agent/src/entity_extractor.py
  - voice-agent/tests/test_vertical_entity_extractor.py
autonomous: true

must_haves:
  truths:
    - "BookingStateMachine is initialized with services_config from VERTICAL_SERVICES[verticale_id]"
    - "set_vertical() passes the updated services_config to the FSM so service extraction uses the correct vertical's synonyms"
    - "Medical specialty, urgency, and visit_type entities are extracted from user input"
    - "Auto vehicle plate (targa) and vehicle brand are extracted from user input"
    - "Entity extractor tests pass: >= 15 unit tests"
  artifacts:
    - path: "voice-agent/src/orchestrator.py"
      provides: "FSM initialized with services_config; set_vertical() re-passes services_config; guardrail call in process()"
      contains: "services_config=VERTICAL_SERVICES"
    - path: "voice-agent/src/entity_extractor.py"
      provides: "extract_vertical_entities() function for medical + auto"
      contains: "extract_vertical_entities"
    - path: "voice-agent/tests/test_vertical_entity_extractor.py"
      provides: "Unit tests for vertical entity extraction"
      contains: "extract_vertical_entities"
  key_links:
    - from: "voice-agent/src/orchestrator.py"
      to: "voice-agent/src/booking_state_machine.py"
      via: "BookingStateMachine(services_config=VERTICAL_SERVICES[verticale_id], groq_nlu=self._groq_nlu)"
      pattern: "services_config=VERTICAL_SERVICES"
    - from: "voice-agent/src/orchestrator.py"
      to: "voice-agent/src/italian_regex.py"
      via: "check_vertical_guardrail call in process() at L0-pre position"
      pattern: "check_vertical_guardrail"
    - from: "voice-agent/src/entity_extractor.py"
      to: "voice-agent/src/orchestrator.py"
      via: "extract_vertical_entities imported and available for use in entity extraction stage"
      pattern: "extract_vertical_entities"
---

<objective>
Wire the vertical services config into the FSM at init and inject guardrail check into the process pipeline. Also add vertical-specific entity extraction for medical and auto.

Purpose: The BookingStateMachine accepts `services_config` but never receives it in production (line 294 of orchestrator.py shows `BookingStateMachine(groq_nlu=self._groq_nlu)` with no services_config). This means Sara always uses a default/empty service list rather than the active vertical's synonyms. Similarly, `set_vertical()` updates context.vertical but does not re-pass services_config to the FSM. Both bugs block AC-2.

Output: `orchestrator.py` with fixed FSM init + `set_vertical()` fix + guardrail injection; `entity_extractor.py` with `extract_vertical_entities()`.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/f02-vertical-system-sara/f02-01-SUMMARY.md
@voice-agent/src/orchestrator.py
@voice-agent/src/entity_extractor.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix orchestrator — FSM init + set_vertical() + guardrail injection</name>
  <files>voice-agent/src/orchestrator.py</files>
  <action>
Make exactly three targeted changes to `orchestrator.py`.

**Change A — Import `VERTICAL_SERVICES` and `check_vertical_guardrail` at top of file.**

In the existing `italian_regex` import block (around lines 69-87), add `VERTICAL_SERVICES` and `check_vertical_guardrail` to the import list:

Before (line ~72-77):
```python
from .italian_regex import (
    prefilter, check_content, is_escalation as regex_is_escalation,
    ContentSeverity, RegexPreFilterResult,
    strip_fillers, is_ambiguous_date,
    extract_multi_services, get_service_synonyms,
)
```

After:
```python
from .italian_regex import (
    prefilter, check_content, is_escalation as regex_is_escalation,
    ContentSeverity, RegexPreFilterResult,
    strip_fillers, is_ambiguous_date,
    extract_multi_services, get_service_synonyms,
    VERTICAL_SERVICES, check_vertical_guardrail,
)
```

Apply the same addition in the fallback import block (lines ~78-83):
```python
from italian_regex import (
    prefilter, check_content, is_escalation as regex_is_escalation,
    ContentSeverity, RegexPreFilterResult,
    strip_fillers, is_ambiguous_date,
    extract_multi_services, get_service_synonyms,
    VERTICAL_SERVICES, check_vertical_guardrail,
)
```

**Change B — Fix BookingStateMachine initialization (line ~294).**

Before:
```python
self.booking_sm = BookingStateMachine(groq_nlu=self._groq_nlu)
```

After:
```python
_initial_services = VERTICAL_SERVICES.get(verticale_id, {}) if HAS_ITALIAN_REGEX else {}
self.booking_sm = BookingStateMachine(
    groq_nlu=self._groq_nlu,
    services_config=_initial_services,
)
```

**Change C — Fix set_vertical() to re-pass services_config to FSM (around line 1577).**

Current `set_vertical()` body:
```python
self._faq_vertical = vertical
self.verticale_id = vertical
self.booking_sm.context.vertical = vertical
```

Add one line after `self.booking_sm.context.vertical = vertical`:
```python
# Re-pass services config so FSM uses the correct vertical's synonym list
if HAS_ITALIAN_REGEX:
    self.booking_sm.services_config = VERTICAL_SERVICES.get(vertical, {})
```

**Change D — Inject guardrail check in process() at L0-pre position.**

In the `process()` method, after the existing L0-pre content filter block (after the `if HAS_ITALIAN_REGEX:` block that ends around line 523), add the guardrail check before the L0 Special Commands block.

Find the comment `# =====================================================================` that precedes `# LAYER 0: Special Commands` and insert BEFORE it:

```python
        # =====================================================================
        # LAYER 0-PRE: Vertical Guardrail
        # =====================================================================
        if response is None and HAS_ITALIAN_REGEX:
            _guardrail = check_vertical_guardrail(user_input, self.verticale_id)
            if _guardrail.blocked:
                response = _guardrail.redirect_response
                intent = f"guardrail_{self.verticale_id}"
                layer = ProcessingLayer.L0_SPECIAL
```

IMPORTANT: Only insert if `response is None` — this follows the existing pattern for L0 checks (content filter sets response, then guardrail only runs if not already handled).
  </action>
  <verify>
Run from MacBook:

```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
import sys
sys.path.insert(0, 'src')
# Verify VERTICAL_SERVICES import works
from italian_regex import VERTICAL_SERVICES, check_vertical_guardrail
assert 'salone' in VERTICAL_SERVICES
print('imports OK')
# Verify BookingStateMachine accepts services_config
from booking_state_machine import BookingStateMachine
sm = BookingStateMachine(services_config=VERTICAL_SERVICES['salone'])
assert sm.services_config is not None
print('FSM services_config OK')
"
```

Also run the type-check to ensure no Python syntax errors were introduced:
```bash
cd /Volumes/MontereyT7/FLUXION && npm run type-check 2>&1 | tail -5
```
(type-check only checks TypeScript; Python errors appear as import errors at runtime instead)
  </verify>
  <done>
`orchestrator.py` imports `VERTICAL_SERVICES` and `check_vertical_guardrail`.
`BookingStateMachine` is instantiated with `services_config=VERTICAL_SERVICES.get(verticale_id, {})`.
`set_vertical()` updates `self.booking_sm.services_config` when `HAS_ITALIAN_REGEX` is True.
Guardrail check block exists in `process()` between L0-PRE content filter and L0 Special Commands.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add extract_vertical_entities() to entity_extractor.py + tests</name>
  <files>
    voice-agent/src/entity_extractor.py
    voice-agent/tests/test_vertical_entity_extractor.py
  </files>
  <action>
**Part A — Add `extract_vertical_entities()` to entity_extractor.py**

Read the current `entity_extractor.py` to find where to append. Add a new section at the end of the file (after the last existing function/class):

```python
# =============================================================================
# VERTICAL-SPECIFIC ENTITY EXTRACTION
# =============================================================================
# Medical: specialty, urgency, visit_type
# Auto: vehicle_plate (targa italiana), vehicle_brand
# Python 3.9 compatible — regex only, no external libraries.


# --- Medical entities ---

_MEDICAL_SPECIALTIES: Dict[str, List[str]] = {
    "cardiologia": ["cardiologo", "cardiologa", "cardiologia", "cuore", "elettrocardiogramma", "ecg"],
    "dermatologia": ["dermatologo", "dermatologa", "dermatologia", "pelle", "nei", "mappatura nei"],
    "ortopedia": ["ortopedico", "ortopedica", "ortopedia", "ossa", "frattura", "articolazione"],
    "ginecologia": ["ginecologo", "ginecologa", "ginecologia", "pap test", "ecografia ginecologica"],
    "pediatria": ["pediatra", "pediatria", "bambino", "bimbo", "neonato"],
    "oculistica": ["oculista", "oculistica", "vista", "occhi", "miopia", "astigmatismo"],
    "odontoiatria": ["dentista", "denti", "carie", "otturazione", "estrazione", "devitalizzazione"],
    "neurologia": ["neurologo", "neurologia", "emicrania", "cefalea", "nervo"],
    "endocrinologia": ["endocrinologo", "endocrinologia", "tiroide", "diabete", "ormoni"],
    "reumatologia": ["reumatologo", "reumatologia", "artrite", "artrosi", "fibromialgia"],
}

_MEDICAL_URGENCY_PATTERNS = [
    (re.compile(r"\b(?:urgente|urgenza|urgentissimo|prima\s+possibile|subito|oggi\s+stesso|immediatamente)\b", re.IGNORECASE), "urgente"),
    (re.compile(r"\b(?:presto|appena\s+possibile|quanto\s+prima|questa\s+settimana)\b", re.IGNORECASE), "alta"),
    (re.compile(r"\b(?:quando\s+c['\u2019]è\s+posto|non\s+ho\s+fretta|con\s+calma|quando\s+volete)\b", re.IGNORECASE), "bassa"),
]

_MEDICAL_VISIT_TYPES = {
    "prima_visita": ["prima\s+visita", "prima\s+volta", "nuovo\s+paziente", "non\s+sono\s+mai\s+venuto"],
    "controllo": ["controllo", "follow.up", "follow\s+up", "visita\s+di\s+controllo", "ricontrollo"],
    "urgenza": ["urgenza", "pronto\s+soccorso", "urgente"],
    "certificato": ["certificato", "idoneità", "certificazione"],
    "vaccino": ["vaccino", "vaccinazione", "richiamo", "dose"],
}
_MEDICAL_VISIT_COMPILED = {
    vtype: re.compile(r"\b(?:" + "|".join(patterns) + r")\b", re.IGNORECASE)
    for vtype, patterns in _MEDICAL_VISIT_TYPES.items()
}


# --- Auto entities ---

# Italian targa pattern: 2 letters + 3 digits + 2 letters (post-1994)
# Old format: 2 letters + 5 digits (pre-1994, less common)
_TARGA_PATTERN = re.compile(
    r"\b([A-Z]{2}\s*\d{3}\s*[A-Z]{2})\b",
    re.IGNORECASE
)

_AUTO_BRANDS = [
    "alfa romeo", "audi", "bmw", "chevrolet", "chrysler", "citroen", "citroën",
    "dacia", "ds", "fiat", "ford", "honda", "hyundai", "jeep", "kia", "lancia",
    "land rover", "lexus", "maserati", "mazda", "mercedes", "mini", "mitsubishi",
    "nissan", "opel", "peugeot", "porsche", "renault", "seat", "skoda", "smart",
    "subaru", "suzuki", "tesla", "toyota", "volkswagen", "vw", "volvo",
]
# Sort by length descending to match multi-word brands first (e.g. "alfa romeo" before "alfa")
_AUTO_BRANDS.sort(key=len, reverse=True)
_AUTO_BRAND_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(b) for b in _AUTO_BRANDS) + r")\b",
    re.IGNORECASE
)


from dataclasses import dataclass as _dc_ve
from typing import Optional as _Opt


@_dc_ve
class VerticalEntities:
    """Vertical-specific entities extracted from user input."""
    # Medical
    specialty: _Opt[str] = None          # e.g. "cardiologia"
    urgency: _Opt[str] = None            # "urgente", "alta", "bassa"
    visit_type: _Opt[str] = None         # "prima_visita", "controllo", etc.
    # Auto
    vehicle_plate: _Opt[str] = None      # Targa italiana, e.g. "AB123CD"
    vehicle_brand: _Opt[str] = None      # e.g. "fiat", "audi"


def extract_vertical_entities(text: str, vertical: str) -> VerticalEntities:
    """
    Extract vertical-specific entities from user input.

    For 'medical': extracts specialty, urgency level, visit type.
    For 'auto': extracts vehicle plate (targa) and brand.
    For other verticals: returns empty VerticalEntities.

    Args:
        text: User input text
        vertical: Active vertical ('salone', 'palestra', 'medical', 'auto')

    Returns:
        VerticalEntities dataclass (all fields None if nothing found)
    """
    result = VerticalEntities()
    text_lower = text.strip().lower()

    if vertical == "medical":
        # Specialty detection
        for specialty, keywords in _MEDICAL_SPECIALTIES.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    result.specialty = specialty
                    break
            if result.specialty:
                break

        # Urgency detection
        for pattern, urgency_level in _MEDICAL_URGENCY_PATTERNS:
            if pattern.search(text):
                result.urgency = urgency_level
                break

        # Visit type detection
        for vtype, pattern in _MEDICAL_VISIT_COMPILED.items():
            if pattern.search(text):
                result.visit_type = vtype
                break

    elif vertical == "auto":
        # Vehicle plate (targa)
        targa_match = _TARGA_PATTERN.search(text)
        if targa_match:
            # Normalize: remove spaces, uppercase
            result.vehicle_plate = targa_match.group(1).replace(" ", "").upper()

        # Vehicle brand
        brand_match = _AUTO_BRAND_PATTERN.search(text)
        if brand_match:
            result.vehicle_brand = brand_match.group(1).lower()

    return result
```

**Part B — Create test_vertical_entity_extractor.py**

Create `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_vertical_entity_extractor.py`:

```python
"""
FLUXION Voice Agent - Vertical Entity Extractor Tests (F02)

Tests for extract_vertical_entities() in entity_extractor.py.
Validates medical specialty/urgency/visit_type and auto plate/brand extraction.

Run with: pytest voice-agent/tests/test_vertical_entity_extractor.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from entity_extractor import extract_vertical_entities, VerticalEntities


# =============================================================================
# MEDICAL — SPECIALTY
# =============================================================================

class TestMedicalSpecialty:

    def test_cardiologo_detected(self):
        r = extract_vertical_entities("vorrei una visita dal cardiologo", "medical")
        assert r.specialty == "cardiologia"

    def test_dermatologo_detected(self):
        r = extract_vertical_entities("devo fare il controllo dei nei dal dermatologo", "medical")
        assert r.specialty == "dermatologia"

    def test_pediatra_detected(self):
        r = extract_vertical_entities("bilancio di salute per il mio bambino", "medical")
        assert r.specialty == "pediatria"

    def test_oculista_detected(self):
        r = extract_vertical_entities("voglio controllare la vista dall'oculista", "medical")
        assert r.specialty == "oculistica"

    def test_ginecologa_detected(self):
        r = extract_vertical_entities("prenoto una visita ginecologica", "medical")
        assert r.specialty == "ginecologia"

    def test_no_specialty_generic_visit(self):
        r = extract_vertical_entities("vorrei prenotare una visita generica", "medical")
        assert r.specialty is None


# =============================================================================
# MEDICAL — URGENCY
# =============================================================================

class TestMedicalUrgency:

    def test_urgente_detected(self):
        r = extract_vertical_entities("ho bisogno urgente di una visita", "medical")
        assert r.urgency == "urgente"

    def test_subito_detected(self):
        r = extract_vertical_entities("mi serve un appuntamento subito", "medical")
        assert r.urgency == "urgente"

    def test_presto_detected(self):
        r = extract_vertical_entities("mi serve appena possibile", "medical")
        assert r.urgency == "alta"

    def test_calma_detected(self):
        r = extract_vertical_entities("non ho fretta, quando c'è posto", "medical")
        assert r.urgency == "bassa"

    def test_no_urgency_neutral(self):
        r = extract_vertical_entities("vorrei prenotare una visita domani", "medical")
        assert r.urgency is None


# =============================================================================
# MEDICAL — VISIT TYPE
# =============================================================================

class TestMedicalVisitType:

    def test_prima_visita_detected(self):
        r = extract_vertical_entities("è la prima volta che vengo", "medical")
        assert r.visit_type == "prima_visita"

    def test_controllo_detected(self):
        r = extract_vertical_entities("devo fare un follow-up", "medical")
        assert r.visit_type == "controllo"

    def test_vaccino_detected(self):
        r = extract_vertical_entities("devo fare la vaccinazione antinfluenzale", "medical")
        assert r.visit_type == "vaccino"


# =============================================================================
# AUTO — PLATE
# =============================================================================

class TestAutoPlate:

    def test_targa_standard_detected(self):
        r = extract_vertical_entities("la mia targa è AB123CD", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_targa_with_spaces(self):
        r = extract_vertical_entities("targa AB 123 CD", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_targa_lowercase_normalized(self):
        r = extract_vertical_entities("la targa è ab123cd", "auto")
        assert r.vehicle_plate == "AB123CD"

    def test_no_targa_in_generic_text(self):
        r = extract_vertical_entities("devo fare il cambio olio", "auto")
        assert r.vehicle_plate is None


# =============================================================================
# AUTO — BRAND
# =============================================================================

class TestAutoBrand:

    def test_fiat_detected(self):
        r = extract_vertical_entities("ho una Fiat Punto da portare", "auto")
        assert r.vehicle_brand == "fiat"

    def test_alfa_romeo_detected(self):
        r = extract_vertical_entities("ho un'Alfa Romeo Giulia", "auto")
        assert r.vehicle_brand == "alfa romeo"

    def test_volkswagen_detected(self):
        r = extract_vertical_entities("la mia Volkswagen Golf fa rumore", "auto")
        assert r.vehicle_brand == "volkswagen"

    def test_no_brand_if_not_mentioned(self):
        r = extract_vertical_entities("devo fare il tagliando", "auto")
        assert r.vehicle_brand is None


# =============================================================================
# CROSS-VERTICAL ISOLATION
# =============================================================================

class TestVerticalIsolation:

    def test_salone_returns_empty_entities(self):
        r = extract_vertical_entities("voglio un taglio", "salone")
        assert r.specialty is None
        assert r.vehicle_plate is None
        assert r.vehicle_brand is None

    def test_palestra_returns_empty_entities(self):
        r = extract_vertical_entities("yoga alle 18", "palestra")
        assert r.specialty is None
        assert r.vehicle_plate is None

    def test_return_type_is_vertical_entities(self):
        r = extract_vertical_entities("ciao", "medical")
        assert isinstance(r, VerticalEntities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```
  </action>
  <verify>
Run from MacBook:

```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_vertical_entity_extractor.py -v --tb=short 2>&1 | tail -30
```

Expected: All tests PASS (at minimum 23 tests collected, 0 failures).

Also verify the import:
```bash
python -c "from src.entity_extractor import extract_vertical_entities, VerticalEntities; print('OK')"
```
  </verify>
  <done>
`extract_vertical_entities(text, vertical)` exists in `entity_extractor.py` and returns `VerticalEntities`.
Medical: specialty (10 specialties), urgency (3 levels), visit_type (5 types) extracted correctly.
Auto: vehicle_plate (targa normalized to uppercase no-space), vehicle_brand (normalized to lowercase) extracted correctly.
All 23+ tests in `test_vertical_entity_extractor.py` pass.
  </done>
</task>

</tasks>

<verification>
After both tasks complete:

1. Python import check:
   ```bash
   cd /Volumes/MontereyT7/FLUXION/voice-agent
   python -c "from src.orchestrator import VoiceOrchestrator; print('orchestrator OK')"
   ```
2. Entity extractor tests all pass: `python -m pytest tests/test_vertical_entity_extractor.py -v`
3. Existing tests still green: `python -m pytest tests/ -q 2>&1 | tail -5` must show 1160+ PASS, 0 FAIL
4. Grep confirms FSM fix: `grep "services_config=VERTICAL_SERVICES" voice-agent/src/orchestrator.py`
5. Grep confirms guardrail injected: `grep "check_vertical_guardrail" voice-agent/src/orchestrator.py`
</verification>

<success_criteria>
- `orchestrator.py` line ~294: `BookingStateMachine(groq_nlu=self._groq_nlu, services_config=_initial_services)`
- `orchestrator.py` `set_vertical()`: sets `self.booking_sm.services_config = VERTICAL_SERVICES.get(vertical, {})`
- `orchestrator.py` `process()`: guardrail check block present between L0-PRE content filter and L0 Special Commands
- `entity_extractor.py`: `extract_vertical_entities(text, vertical)` returns `VerticalEntities`
- `test_vertical_entity_extractor.py`: 23+ tests, all PASS
- 1160 existing tests still PASS
</success_criteria>

<output>
After completion, create `.planning/phases/f02-vertical-system-sara/f02-02-SUMMARY.md`
</output>
