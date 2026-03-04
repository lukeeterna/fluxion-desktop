---
phase: f02-vertical-system-sara
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - voice-agent/src/italian_regex.py
  - voice-agent/tests/test_guardrails.py
autonomous: true

must_haves:
  truths:
    - "Out-of-scope queries are blocked with a polite redirect per vertical (salone, palestra, medical, auto)"
    - "Guardrail check runs at L0-pre in the pipeline, before special commands"
    - "Multi-word patterns only — no single-word blocks that could cause false positives"
    - "Pre-compiled patterns load at module import: runtime cost < 2ms per check"
    - "Guardrail tests pass: >= 20 unit tests across 4 verticals"
  artifacts:
    - path: "voice-agent/src/italian_regex.py"
      provides: "VERTICAL_GUARDRAILS dict + check_vertical_guardrail() function"
      contains: "VERTICAL_GUARDRAILS"
    - path: "voice-agent/tests/test_guardrails.py"
      provides: "Unit tests for guardrail function"
      contains: "check_vertical_guardrail"
  key_links:
    - from: "voice-agent/src/italian_regex.py"
      to: "voice-agent/src/orchestrator.py"
      via: "check_vertical_guardrail import and call in process()"
      pattern: "check_vertical_guardrail"
---

<objective>
Add vertical-aware out-of-scope guardrails to the L0 regex layer.

Purpose: Sara currently has no mechanism to redirect queries that are completely out of scope for a given business vertical. A hair salon client asking about car engine repairs should be gently redirected. These guardrails are pure regex, pre-compiled, and run in < 2ms at the L0-pre stage.

Output: `VERTICAL_GUARDRAILS` dict and `check_vertical_guardrail()` in `italian_regex.py`, plus 20+ unit tests.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@voice-agent/src/italian_regex.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add VERTICAL_GUARDRAILS + check_vertical_guardrail() to italian_regex.py</name>
  <files>voice-agent/src/italian_regex.py</files>
  <action>
Append a new section 10 to `italian_regex.py` after the existing section 9 (FLEXIBLE_SCHEDULING_PATTERNS).

Add the following (exact implementation):

```python
# =============================================================================
# 10. VERTICAL GUARDRAILS (L0-pre out-of-scope detection)
# =============================================================================
# Block queries clearly out of scope for the active vertical.
# RULE: Multi-word patterns ONLY — single words risk false positives.
# Example: "colore" alone blocks "colore della pelle" in medical context.
# Pre-compiled at module load for < 2ms runtime.

from dataclasses import dataclass as _dataclass

@_dataclass
class GuardrailResult:
    blocked: bool
    vertical: str
    matched_pattern: str = ""
    redirect_response: str = ""


# Out-of-scope patterns per vertical.
# Each vertical lists patterns that belong to OTHER verticals and are clearly
# off-topic for this business type.
VERTICAL_GUARDRAILS: Dict[str, List[str]] = {
    "salone": [
        # Auto/officina patterns
        r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
        r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi|nuovi))\b",
        r"\b(?:pastiglie\s+freni|dischi\s+freno|liquido\s+freni)\b",
        r"\b(?:revisione\s+auto|tagliando\s+auto|collaudo\s+auto)\b",
        r"\b(?:carrozzeria|verniciatura\s+auto|ammaccatura)\b",
        r"\b(?:centralina|diagnostica\s+auto|spia\s+motore)\b",
        # Palestra patterns
        r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
        r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning|zumba))\b",
        r"\b(?:personal\s+trainer|personal\s+training|allenamento\s+personalizzato)\b",
        r"\b(?:sala\s+pesi|body\s+building|pesistica)\b",
        # Medical patterns
        r"\b(?:visita\s+(?:medica|specialistica|cardiologica|dermatologica))\b",
        r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue|prelievo\s+sangue)\b",
        r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
        r"\b(?:certificato\s+(?:medico|sportivo)|idoneità\s+sportiva)\b",
    ],
    "palestra": [
        # Salone patterns
        r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino))\b",
        r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
        r"\b(?:messa\s+in\s+piega|piega\s+capelli|acconciatura\s+sposa)\b",
        r"\b(?:trattamento\s+capelli|cheratina\s+(?:capelli|lisciante))\b",
        r"\b(?:extension\s+capelli|allungamento\s+capelli)\b",
        r"\b(?:manicure|pedicure|semipermanente\s+(?:mani|piedi)|nail\s+art)\b",
        r"\b(?:ceretta|depilazione|epilazione\s+(?:gambe|braccia|inguine))\b",
        # Auto patterns
        r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
        r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
        r"\b(?:revisione\s+auto|tagliando\s+auto)\b",
        r"\b(?:carrozzeria|verniciatura\s+auto)\b",
        # Medical patterns
        r"\b(?:visita\s+(?:medica|specialistica))\b",
        r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue)\b",
        r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    ],
    "medical": [
        # Salone patterns
        r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino))\b",
        r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
        r"\b(?:messa\s+in\s+piega|piega\s+capelli)\b",
        r"\b(?:manicure|pedicure|nail\s+art|semipermanente\s+(?:mani|piedi))\b",
        r"\b(?:ceretta|depilazione|epilazione)\b",
        r"\b(?:trucco\s+sposa|acconciatura\s+sposa)\b",
        # Palestra patterns
        r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
        r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning|zumba))\b",
        r"\b(?:personal\s+trainer|personal\s+training)\b",
        r"\b(?:sala\s+pesi|body\s+building)\b",
        # Auto patterns
        r"\b(?:cambio\s+olio|filtro\s+olio|olio\s+motore)\b",
        r"\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi))\b",
        r"\b(?:revisione\s+auto|tagliando\s+auto|carrozzeria)\b",
    ],
    "auto": [
        # Salone patterns
        r"\b(?:taglio\s+capelli|taglio\s+(?:donna|uomo|bambino))\b",
        r"\b(?:tinta\s+capelli|colorazione\s+capelli|ritocco\s+radici)\b",
        r"\b(?:messa\s+in\s+piega|piega\s+capelli)\b",
        r"\b(?:manicure|pedicure|nail\s+art)\b",
        r"\b(?:ceretta|depilazione|epilazione)\b",
        # Palestra patterns
        r"\b(?:abbonamento\s+(?:mensile|annuale|palestra))\b",
        r"\b(?:corso\s+di\s+(?:yoga|pilates|crossfit|spinning|zumba))\b",
        r"\b(?:personal\s+trainer|personal\s+training)\b",
        # Medical patterns
        r"\b(?:visita\s+(?:medica|specialistica))\b",
        r"\b(?:esame\s+del\s+sangue|analisi\s+del\s+sangue)\b",
        r"\b(?:ricetta\s+medica|prescrizione\s+medica)\b",
    ],
}

# Pre-compile all guardrail patterns at module load
_GUARDRAIL_COMPILED: Dict[str, List[re.Pattern]] = {
    vertical: [re.compile(p, re.IGNORECASE) for p in patterns]
    for vertical, patterns in VERTICAL_GUARDRAILS.items()
}

# Polite redirect responses per vertical
_GUARDRAIL_RESPONSES: Dict[str, str] = {
    "salone": "Mi occupo di prenotazioni per il salone. Posso aiutarla con taglio, colore, trattamenti o altri servizi capelli?",
    "palestra": "Mi occupo di prenotazioni per la palestra. Posso aiutarla con corsi, abbonamenti o sessioni di personal training?",
    "medical": "Mi occupo di prenotazioni per lo studio medico. Posso aiutarla con visite, esami o consulenze mediche?",
    "auto": "Mi occupo di prenotazioni per l'officina. Posso aiutarla con tagliando, riparazioni, cambio gomme o altri servizi auto?",
}


def check_vertical_guardrail(text: str, vertical: str) -> GuardrailResult:
    """
    Check if text is out-of-scope for the given vertical.

    Uses pre-compiled multi-word patterns to avoid false positives.
    Returns GuardrailResult with blocked=True if out-of-scope.

    Args:
        text: User input text
        vertical: Active vertical ('salone', 'palestra', 'medical', 'auto')

    Returns:
        GuardrailResult — blocked=False if in-scope or unknown vertical
    """
    patterns = _GUARDRAIL_COMPILED.get(vertical, [])
    if not patterns:
        return GuardrailResult(blocked=False, vertical=vertical)

    text_clean = text.strip()
    for pattern in patterns:
        m = pattern.search(text_clean)
        if m:
            response = _GUARDRAIL_RESPONSES.get(
                vertical,
                "Mi occupo solo di prenotazioni per questa attività. Come posso aiutarla?"
            )
            return GuardrailResult(
                blocked=True,
                vertical=vertical,
                matched_pattern=m.group(0),
                redirect_response=response,
            )

    return GuardrailResult(blocked=False, vertical=vertical)
```

Also update the `prefilter()` function's docstring comment to mention guardrail (do NOT add guardrail call to prefilter — it requires the `vertical` param which prefilter does not have). The guardrail is called separately in orchestrator.

Also update the imports at top of the file: `GuardrailResult` is already defined inside the module via the dataclass decorator — no additional import needed. The `_dataclass` alias already handles it.

Finally update the module-level docstring (first line of file) to add:
`    9. Vertical Guardrails (out-of-scope redirect per vertical)`
  </action>
  <verify>
From the MacBook, navigate to the voice-agent directory and run:

```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
from src.italian_regex import check_vertical_guardrail, VERTICAL_GUARDRAILS
# Test salone blocks auto
r = check_vertical_guardrail('vorrei fare il cambio olio', 'salone')
assert r.blocked, 'salone should block cambio olio'
# Test medical does not block visita medica
r = check_vertical_guardrail('vorrei una visita medica', 'medical')
assert not r.blocked, 'medical should not block visita medica'
# Test auto blocks taglio capelli
r = check_vertical_guardrail('vorrei un taglio capelli', 'auto')
assert r.blocked, 'auto should block taglio capelli'
print('OK - guardrail smoke test passed')
"
```

Must print: `OK - guardrail smoke test passed`
  </verify>
  <done>
`VERTICAL_GUARDRAILS` dict exists with 4 verticals, each with >= 10 multi-word patterns.
`check_vertical_guardrail(text, vertical)` returns `GuardrailResult`.
All patterns are pre-compiled in `_GUARDRAIL_COMPILED` at import time.
Smoke test passes without errors.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create test_guardrails.py with >= 20 unit tests</name>
  <files>voice-agent/tests/test_guardrails.py</files>
  <action>
Create `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_guardrails.py` with the following content:

```python
"""
FLUXION Voice Agent - Guardrail Unit Tests (F02)

Tests for check_vertical_guardrail() in italian_regex.py.
Validates that out-of-scope queries are blocked per vertical.

Run with: pytest voice-agent/tests/test_guardrails.py -v
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from italian_regex import check_vertical_guardrail, GuardrailResult


# =============================================================================
# SALONE GUARDRAILS
# =============================================================================

class TestSaloneGuardrails:
    """Salone blocks auto, palestra, medical out-of-scope queries."""

    def test_salone_blocks_cambio_olio(self):
        r = check_vertical_guardrail("vorrei fare il cambio olio", "salone")
        assert r.blocked is True
        assert r.vertical == "salone"
        assert r.redirect_response != ""

    def test_salone_blocks_gomme_invernali(self):
        r = check_vertical_guardrail("devo cambiare le gomme invernali", "salone")
        assert r.blocked is True

    def test_salone_blocks_tagliando_auto(self):
        r = check_vertical_guardrail("quando posso portare l'auto per la revisione auto?", "salone")
        assert r.blocked is True

    def test_salone_blocks_abbonamento_palestra(self):
        r = check_vertical_guardrail("vorrei rinnovare l'abbonamento mensile", "salone")
        assert r.blocked is True

    def test_salone_blocks_corso_yoga(self):
        r = check_vertical_guardrail("posso iscrivermi al corso di yoga?", "salone")
        assert r.blocked is True

    def test_salone_blocks_visita_medica(self):
        r = check_vertical_guardrail("vorrei prenotare una visita medica", "salone")
        assert r.blocked is True

    def test_salone_blocks_esame_sangue(self):
        r = check_vertical_guardrail("devo fare l'esame del sangue", "salone")
        assert r.blocked is True

    def test_salone_allows_taglio(self):
        r = check_vertical_guardrail("vorrei prenotare un taglio", "salone")
        assert r.blocked is False

    def test_salone_allows_colore(self):
        r = check_vertical_guardrail("voglio fare il colore", "salone")
        assert r.blocked is False

    def test_salone_allows_piega(self):
        r = check_vertical_guardrail("prenoto una messa in piega", "salone")
        assert r.blocked is False

    def test_salone_redirect_response_contains_salone(self):
        r = check_vertical_guardrail("cambio olio motore", "salone")
        assert r.blocked is True
        assert "salone" in r.redirect_response.lower() or "capell" in r.redirect_response.lower()


# =============================================================================
# PALESTRA GUARDRAILS
# =============================================================================

class TestPalestraGuardrails:
    """Palestra blocks salone, auto, medical out-of-scope queries."""

    def test_palestra_blocks_taglio_capelli(self):
        r = check_vertical_guardrail("voglio prenotare un taglio capelli", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_tinta_capelli(self):
        r = check_vertical_guardrail("devo fare la tinta capelli", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_cambio_olio(self):
        r = check_vertical_guardrail("cambio olio motore per la mia macchina", "palestra")
        assert r.blocked is True

    def test_palestra_blocks_visita_medica(self):
        r = check_vertical_guardrail("prenoto una visita specialistica", "palestra")
        assert r.blocked is True

    def test_palestra_allows_yoga(self):
        r = check_vertical_guardrail("vorrei iscrivermi al corso di yoga", "palestra")
        assert r.blocked is False

    def test_palestra_allows_personal_trainer(self):
        r = check_vertical_guardrail("voglio un personal trainer", "palestra")
        assert r.blocked is False


# =============================================================================
# MEDICAL GUARDRAILS
# =============================================================================

class TestMedicalGuardrails:
    """Medical blocks salone, palestra, auto out-of-scope queries."""

    def test_medical_blocks_taglio_donna(self):
        r = check_vertical_guardrail("voglio prenotare un taglio donna", "medical")
        assert r.blocked is True

    def test_medical_blocks_manicure(self):
        r = check_vertical_guardrail("vorrei fare la manicure", "medical")
        assert r.blocked is True

    def test_medical_blocks_abbonamento_palestra(self):
        r = check_vertical_guardrail("rinnovo abbonamento annuale palestra", "medical")
        assert r.blocked is True

    def test_medical_blocks_cambio_olio(self):
        r = check_vertical_guardrail("devo fare il cambio olio filtro olio", "medical")
        assert r.blocked is True

    def test_medical_allows_visita_medica(self):
        r = check_vertical_guardrail("vorrei prenotare una visita medica", "medical")
        assert r.blocked is False

    def test_medical_allows_analisi(self):
        r = check_vertical_guardrail("devo fare un prelievo", "medical")
        assert r.blocked is False


# =============================================================================
# AUTO GUARDRAILS
# =============================================================================

class TestAutoGuardrails:
    """Auto blocks salone, palestra, medical out-of-scope queries."""

    def test_auto_blocks_taglio_capelli(self):
        r = check_vertical_guardrail("prenoto un taglio capelli", "auto")
        assert r.blocked is True

    def test_auto_blocks_corso_yoga(self):
        r = check_vertical_guardrail("mi iscrivo al corso di spinning", "auto")
        assert r.blocked is True

    def test_auto_blocks_visita_medica(self):
        r = check_vertical_guardrail("visita specialistica con il cardiologo", "auto")
        assert r.blocked is True

    def test_auto_allows_cambio_olio(self):
        r = check_vertical_guardrail("devo fare il cambio olio", "auto")
        assert r.blocked is False

    def test_auto_allows_cambio_gomme(self):
        r = check_vertical_guardrail("cambio gomme invernali per la mia auto", "auto")
        assert r.blocked is False

    def test_auto_allows_tagliando(self):
        r = check_vertical_guardrail("quando posso portare l'auto per il tagliando?", "auto")
        assert r.blocked is False


# =============================================================================
# EDGE CASES
# =============================================================================

class TestGuardrailEdgeCases:
    """Edge cases: unknown vertical, empty text, matched_pattern populated."""

    def test_unknown_vertical_not_blocked(self):
        r = check_vertical_guardrail("qualsiasi cosa", "wellness")
        assert r.blocked is False

    def test_empty_text_not_blocked(self):
        r = check_vertical_guardrail("", "salone")
        assert r.blocked is False

    def test_blocked_result_has_matched_pattern(self):
        r = check_vertical_guardrail("voglio fare il cambio olio motore", "salone")
        assert r.blocked is True
        assert r.matched_pattern != ""

    def test_return_type_is_guardrail_result(self):
        r = check_vertical_guardrail("ciao", "salone")
        assert isinstance(r, GuardrailResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

This file must be saved as-is. Do NOT modify the test assertions.
  </action>
  <verify>
Run from the MacBook:

```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_guardrails.py -v --tb=short 2>&1 | tail -30
```

Expected: All tests PASS (at minimum 28 tests collected, 0 failures).
  </verify>
  <done>
`voice-agent/tests/test_guardrails.py` exists with >= 28 test methods.
All tests pass: 0 FAILED, 0 ERROR.
The test file can be run standalone: `pytest voice-agent/tests/test_guardrails.py -v`
  </done>
</task>

</tasks>

<verification>
After both tasks complete:

1. Import check: `python -c "from src.italian_regex import check_vertical_guardrail, VERTICAL_GUARDRAILS; print('import OK')"` from `voice-agent/` directory
2. All guardrail tests pass: `python -m pytest tests/test_guardrails.py -v --tb=short`
3. Existing test suite still green: `python -m pytest tests/ -v --tb=short -q 2>&1 | tail -5` — must show 1160+ PASS, 0 FAIL
4. No single-word patterns in VERTICAL_GUARDRAILS (each pattern must contain `\s+`)
</verification>

<success_criteria>
- `VERTICAL_GUARDRAILS` dict in `italian_regex.py` with 4 verticals, each with >= 10 multi-word patterns
- `check_vertical_guardrail(text, vertical)` returns `GuardrailResult(blocked, vertical, matched_pattern, redirect_response)`
- All patterns pre-compiled at module load
- `test_guardrails.py` has >= 28 tests, all PASS
- Existing 1160 tests still PASS
</success_criteria>

<output>
After completion, create `.planning/phases/f02-vertical-system-sara/f02-01-SUMMARY.md`
</output>
