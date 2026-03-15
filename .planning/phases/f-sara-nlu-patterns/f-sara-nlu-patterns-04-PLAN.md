---
phase: f-sara-nlu-patterns
plan: "04"
type: execute
wave: 2
depends_on:
  - f-sara-nlu-patterns-01
  - f-sara-nlu-patterns-02
  - f-sara-nlu-patterns-03
files_modified:
  - voice-agent/src/orchestrator.py
  - voice-agent/tests/test_nlu_vertical_integration.py
autonomous: false

must_haves:
  truths:
    - "orchestrator._extract_vertical_key('hair_salone_bella') returns 'hair'"
    - "orchestrator._extract_vertical_key('beauty_centro_rosa') returns 'beauty'"
    - "orchestrator._extract_vertical_key('wellness_gym_fit') returns 'wellness'"
    - "orchestrator._extract_vertical_key('medico_studio_rossi') returns 'medico'"
    - "orchestrator._extract_vertical_key('professionale_studio_bianchi') returns 'professionale'"
    - "orchestrator._extract_vertical_key('salone_bella_vita') still returns 'salone' (legacy compat)"
    - "orchestrator._extract_vertical_key('medical_studio_rossi') still returns 'medical' (legacy compat)"
    - "check_vertical_guardrail integration test: passing 'hair' to orchestrator with OOS text returns blocked=True"
    - "pytest on iMac: ≥1488 existing PASS + new test_nlu_vertical_integration.py tests PASS"
    - "ROADMAP.md updated to mark F-SARA-NLU-PATTERNS complete"
  artifacts:
    - path: "voice-agent/src/orchestrator.py"
      provides: "Updated _extract_vertical_key() with new macro keys + legacy backward compat"
      contains: "\"hair\""
    - path: "voice-agent/tests/test_nlu_vertical_integration.py"
      provides: "Integration tests: orchestrator vertical key mapping + guardrail end-to-end"
      contains: "TestVerticalKeyMapping"
  key_links:
    - from: "voice-agent/src/orchestrator.py"
      to: "voice-agent/src/italian_regex.py"
      via: "check_vertical_guardrail(text, self._faq_vertical)"
      pattern: "check_vertical_guardrail"
    - from: "voice-agent/src/orchestrator.py"
      to: "voice-agent/src/entity_extractor.py"
      via: "extract_vertical_entities(text, self._faq_vertical)"
      pattern: "extract_vertical_entities"
---

<objective>
Wire the NLU layer changes from Waves A/B/C into the orchestrator: update _extract_vertical_key() to recognize new macro keys from setup.ts taxonomy, create integration tests covering all 6 verticals end-to-end, run full pytest suite on iMac (≥1488 PASS), and update ROADMAP.

Purpose: Waves A/B/C added all patterns and entity extraction, but the orchestrator still maps unknown keys like "hair_*" and "beauty_*" to "altro". This plan closes the final gap: the runtime mapping that ensures new macro-category businesses actually use the new patterns.

Output: Updated orchestrator.py + integration test file + iMac pytest run ≥1488 PASS + ROADMAP marked complete.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-RESEARCH.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-01-SUMMARY.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-02-SUMMARY.md
@.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-03-SUMMARY.md

@voice-agent/src/orchestrator.py
@voice-agent/src/italian_regex.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update _extract_vertical_key() in orchestrator.py to handle new macro keys</name>
  <files>voice-agent/src/orchestrator.py</files>
  <action>
Find `_extract_vertical_key()` at line 2075 in orchestrator.py. The current implementation:

```python
def _extract_vertical_key(self, verticale_id: str) -> str:
    VERTICALS = ["salone", "palestra", "wellness", "medical", "auto", "altro"]
    verticale_lower = verticale_id.lower()
    for v in VERTICALS:
        if verticale_lower.startswith(v):
            return v
    return "altro"
```

Replace the VERTICALS list with the complete set of new macro keys AND legacy keys. The method must:
1. Recognize new macro keys: hair, beauty, wellness, medico, auto, professionale
2. Keep legacy keys: salone, palestra, medical (for backward compat with existing businesses)
3. Return the key as-is when it is an exact known macro key
4. Fall back to prefix matching for composed IDs like "hair_salone_bella_vita"
5. Return "altro" only when no match found

New implementation:
```python
def _extract_vertical_key(self, verticale_id: str) -> str:
    """
    Extract vertical key from verticale_id string.

    Handles both new macro taxonomy (hair/beauty/wellness/medico/auto/professionale)
    and legacy keys (salone/palestra/medical) for backward compatibility.

    Examples:
        "hair" -> "hair"
        "hair_salone_bella" -> "hair"
        "beauty_centro_rosa" -> "beauty"
        "wellness_gym_fit" -> "wellness"
        "medico_studio_rossi" -> "medico"
        "professionale_studio_bianchi" -> "professionale"
        "salone_bella_vita" -> "salone"  (legacy)
        "medical_studio_rossi" -> "medical"  (legacy)
        "auto_officina_mario" -> "auto"
    """
    # New macro keys (setup.ts taxonomy) — check first for priority
    NEW_VERTICALS = ["hair", "beauty", "wellness", "medico", "professionale"]
    # Legacy keys (backward compat with existing businesses)
    LEGACY_VERTICALS = ["salone", "palestra", "medical", "auto", "altro"]

    verticale_lower = verticale_id.lower().strip()

    # Exact match check (covers simple keys like "hair", "auto", etc.)
    all_keys = NEW_VERTICALS + LEGACY_VERTICALS
    if verticale_lower in all_keys:
        return verticale_lower

    # Prefix match for composed IDs like "hair_salone_bella_vita"
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v + "_") or verticale_lower.startswith(v + "-"):
            return v

    # Legacy: startswith without separator (old behavior)
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v):
            return v

    return "altro"
```

IMPORTANT: Do not change anything else in orchestrator.py. Only replace the _extract_vertical_key() method body. The method signature stays the same.

After editing, also verify that any direct calls to check_vertical_guardrail in orchestrator.py pass `self._faq_vertical` (the key returned by _extract_vertical_key) and NOT the raw verticale_id. Search for `check_vertical_guardrail` usages in orchestrator.py. If any call passes the raw `verticale_id` instead of the normalized key, fix it to use `self._faq_vertical` or call `self._extract_vertical_key(verticale_id)` first.

Similarly check extract_vertical_entities() call sites in orchestrator.py. They should pass the normalized vertical key.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -c "
import sys
sys.path.insert(0, 'src')

# Test _extract_vertical_key without instantiating full orchestrator
# Use a simple mock to test the method logic in isolation
from unittest.mock import MagicMock
import types

# Import the method logic by copying it
def _extract_vertical_key(verticale_id):
    NEW_VERTICALS = ['hair', 'beauty', 'wellness', 'medico', 'professionale']
    LEGACY_VERTICALS = ['salone', 'palestra', 'medical', 'auto', 'altro']
    verticale_lower = verticale_id.lower().strip()
    all_keys = NEW_VERTICALS + LEGACY_VERTICALS
    if verticale_lower in all_keys:
        return verticale_lower
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v + '_') or verticale_lower.startswith(v + '-'):
            return v
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v):
            return v
    return 'altro'

tests = [
    ('hair', 'hair'),
    ('hair_salone_bella', 'hair'),
    ('beauty_centro_rosa', 'beauty'),
    ('wellness_gym_fit', 'wellness'),
    ('medico_studio_rossi', 'medico'),
    ('professionale_studio_bianchi', 'professionale'),
    ('salone_bella_vita', 'salone'),
    ('medical_studio', 'medical'),
    ('auto_officina_mario', 'auto'),
    ('palestra_fit', 'palestra'),
    ('unknown_xyz', 'altro'),
]
all_pass = True
for vid, expected in tests:
    result = _extract_vertical_key(vid)
    status = 'PASS' if result == expected else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    print(f'{status}: {vid!r} -> {result!r} (expected {expected!r})')
print('All pass:', all_pass)
"
```
Expected: All PASS, all_pass: True
  </verify>
  <done>
- _extract_vertical_key() handles: hair, beauty, wellness, medico, professionale (new keys)
- Legacy keys salone, palestra, medical, auto still return correctly
- Composed IDs like "hair_salone_bella" extract to "hair"
- Unknown IDs return "altro"
- check_vertical_guardrail and extract_vertical_entities call sites verified
  </done>
</task>

<task type="auto">
  <name>Task 2: Create test_nlu_vertical_integration.py — end-to-end integration tests for all 6 verticals</name>
  <files>voice-agent/tests/test_nlu_vertical_integration.py</files>
  <action>
Create `voice-agent/tests/test_nlu_vertical_integration.py`. This file tests the FULL integration stack: _extract_vertical_key → check_vertical_guardrail → extract_vertical_entities — using the same pipeline that orchestrator.py runs.

Module-level docstring:
```python
"""
Integration tests for NLU vertical pipeline: orchestrator key mapping + guardrail + entity extraction.
Phase: f-sara-nlu-patterns (Wave D)
Verifies: all 6 macro-verticals wire correctly end-to-end after Waves A/B/C.
Tests run on iMac where pytest suite executes.
"""
```

SECTION 1 — TestVerticalKeyMapping (tests _extract_vertical_key logic):

Import the method from the module (use a helper that replicates the logic, or import VoiceOrchestrator and test via the method):
```python
# Option: import the extracted function from orchestrator if it's a pure static method
# Otherwise replicate the logic for isolated testing
```

Use parametrize on (verticale_id, expected_key) tuples:
```python
@pytest.mark.parametrize("verticale_id,expected", [
    ("hair", "hair"),
    ("beauty", "beauty"),
    ("wellness", "wellness"),
    ("medico", "medico"),
    ("auto", "auto"),
    ("professionale", "professionale"),
    ("hair_salone_bella_vita", "hair"),
    ("hair-centro-capelli", "hair"),
    ("beauty_centro_rosa", "beauty"),
    ("wellness_gym_fit", "wellness"),
    ("medico_studio_rossi", "medico"),
    ("professionale_studio_bianchi", "professionale"),
    # Legacy keys — must still work
    ("salone", "salone"),
    ("salone_bella_vita", "salone"),
    ("palestra", "palestra"),
    ("palestra_fit_club", "palestra"),
    ("medical", "medical"),
    ("medical_studio_medico", "medical"),
    # Unknown
    ("unknown_xyz", "altro"),
    ("", "altro"),
])
def test_extract_vertical_key(self, verticale_id, expected):
    ...
```

For the test body, since _extract_vertical_key is an instance method, either:
- Instantiate VoiceOrchestrator with a mock verticale_id (if feasible without full setup)
- Or replicate the logic as a standalone function for testing

Preferred approach: replicate the new _extract_vertical_key logic as a standalone test helper function at the top of the test file, and test the logic directly. This avoids needing full orchestrator instantiation.

SECTION 2 — TestNLUPipelineIntegration (tests guardrail + entity extraction with correct vertical keys):

```python
class TestNLUPipelineIntegration:
    """
    End-to-end tests: vertical key → guardrail check → entity extraction.
    Simulates what orchestrator.py does in production.
    """

    @pytest.mark.parametrize("verticale_id,text,expect_blocked", [
        # hair vertical — blocks auto OOS
        ("hair", "voglio fare il tagliando", True),
        ("hair_salone_bella", "cambio olio motore", True),
        # hair vertical — allows hair services
        ("hair", "vorrei un taglio capelli", False),
        ("hair_salone_bella", "barba sfumata fade", False),
        # beauty vertical — blocks hair OOS
        ("beauty", "taglio capelli donna", True),
        ("beauty_centro_rosa", "tinta capelli biondi", True),
        # beauty vertical — allows beauty services
        ("beauty", "pulizia viso profonda", False),
        ("beauty_centro_rosa", "epilazione laser gambe", False),
        # wellness vertical — blocks auto OOS
        ("wellness", "cambio olio motore", True),
        ("wellness_gym_fit", "tagliando auto scaduto", True),
        # wellness vertical — allows fitness
        ("wellness", "corso di yoga mattutino", False),
        ("wellness_gym_fit", "WOD crossfit domani", False),
        # medico vertical — blocks palestra OOS
        ("medico", "abbonamento mensile palestra", True),
        ("medico_studio_rossi", "corso di yoga", True),
        # medico vertical — allows medical services
        ("medico", "visita medica specialistica", False),
        ("medico_studio_rossi", "fisioterapia posturale", False),
        # auto vertical — blocks hair OOS
        ("auto", "taglio capelli donna", True),
        ("auto_officina", "tinta capelli biondi", True),
        # auto vertical — allows auto services
        ("auto", "cambio olio motore", False),
        ("auto_officina", "revisione ministeriale", False),
        # professionale vertical — blocks auto OOS
        ("professionale", "cambio olio motore", True),
        ("professionale_studio", "fare il tagliando", True),
        # professionale vertical — allows professionale services
        ("professionale", "dichiarazione dei redditi 730", False),
        ("professionale_studio", "consulenza legale separazione", False),
        # legacy keys still work
        ("salone", "cambio olio motore", True),
        ("salone_bella_vita", "taglio capelli donna", False),
        ("medical_studio", "abbonamento palestra", True),
        ("medical_studio", "visita medica", False),
    ])
    def test_guardrail_with_vertical_key(self, verticale_id, text, expect_blocked):
        from src.italian_regex import check_vertical_guardrail
        vertical_key = _extract_vertical_key_impl(verticale_id)  # test helper
        result = check_vertical_guardrail(text, vertical_key)
        assert result.blocked == expect_blocked, (
            f"vertical_key={vertical_key!r}, text={text!r}: "
            f"expected blocked={expect_blocked}, got {result.blocked}"
        )
```

SECTION 3 — TestEntityExtractionIntegration:

```python
class TestEntityExtractionIntegration:
    @pytest.mark.parametrize("verticale_id,text,expected_sub_vertical", [
        ("hair", "barba sfumata fade skin", "barbiere"),
        ("hair_salone_bella", "correzione colore Olaplex", "color_specialist"),
        ("beauty", "pulizia viso profonda", "estetista_viso"),
        ("beauty_centro_rosa", "ricostruzione unghie gel", "nail_specialist"),
        ("wellness", "corso di yoga nidra", "yoga_pilates"),
        ("wellness_gym_fit", "BJJ muay thai", "arti_marziali"),
        ("medico", "fisioterapia posturale tecarterapia", "fisioterapia"),
        ("medico_studio", "seduta psicologo TCC", "psicologo"),
        ("auto", "diagnosi OBD centralina", "elettrauto"),
        ("auto_officina", "detailing ceramica PPF", "detailing"),
        ("professionale", "dichiarazione 730 Unico", "commercialista"),
        ("professionale_studio", "consulenza legale divorzio", "avvocato"),
        # Legacy aliases
        ("salone", "extension cheratina I-tip", "extension_specialist"),
        ("medical_studio", "osteopata manipolazione osteopatica", "osteopata"),
    ])
    def test_entity_extraction_with_vertical_key(self, verticale_id, text, expected_sub_vertical):
        from src.entity_extractor import extract_vertical_entities
        vertical_key = _extract_vertical_key_impl(verticale_id)
        result = extract_vertical_entities(text, vertical_key)
        assert result.sub_vertical == expected_sub_vertical or result.specialty == expected_sub_vertical, (
            f"vertical_key={vertical_key!r}, text={text!r}: "
            f"expected sub_vertical/specialty={expected_sub_vertical!r}, got sub_vertical={result.sub_vertical!r}, specialty={result.specialty!r}"
        )
```

Note on TestEntityExtractionIntegration: medico specialty detection goes to result.specialty (not sub_vertical). The assertion should check EITHER field:
- For hair/beauty/wellness/auto/professionale: check result.sub_vertical
- For medico: check result.specialty

Adjust the parametrize assertion accordingly or split into two test methods.

Add the standalone helper function at module level:
```python
def _extract_vertical_key_impl(verticale_id: str) -> str:
    """Standalone implementation of orchestrator._extract_vertical_key for testing."""
    NEW_VERTICALS = ["hair", "beauty", "wellness", "medico", "professionale"]
    LEGACY_VERTICALS = ["salone", "palestra", "medical", "auto", "altro"]
    verticale_lower = verticale_id.lower().strip()
    all_keys = NEW_VERTICALS + LEGACY_VERTICALS
    if verticale_lower in all_keys:
        return verticale_lower
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v + "_") or verticale_lower.startswith(v + "-"):
            return v
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if verticale_lower.startswith(v):
            return v
    return "altro"
```
  </action>
  <verify>
On MacBook first (to confirm logic):
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent
python -m pytest tests/test_nlu_vertical_integration.py -v 2>&1 | tail -30
```
Expected: All PASS on MacBook.
  </verify>
  <done>
- test_nlu_vertical_integration.py created with ≥50 integration test cases
- TestVerticalKeyMapping: ≥20 cases
- TestNLUPipelineIntegration: ≥28 cases
- TestEntityExtractionIntegration: ≥14 cases
- All PASS on MacBook before iMac run
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
Full NLU vertical rewrite across 4 plans:
- Wave A (Plan 01): hair + beauty patterns, guardrails, entity extraction, 60+ tests
- Wave B (Plan 02): wellness + medico patterns, guardrails, entity extraction, 50+ tests
- Wave C (Plan 03): auto extended + professionale, DURATION_MAP, OPERATOR_ROLES, 50+ tests
- Wave D (Plan 04): orchestrator wiring + integration tests

Before this checkpoint, run the full pytest suite on iMac to confirm ≥1488 PASS + all new tests pass.
  </what-built>
  <how-to-verify>
1. Push changes to iMac:
   ```bash
   git add voice-agent/src/italian_regex.py voice-agent/src/entity_extractor.py \
           voice-agent/src/orchestrator.py \
           voice-agent/tests/test_hair_beauty_nlu.py \
           voice-agent/tests/test_wellness_medico_nlu.py \
           voice-agent/tests/test_auto_professionale_nlu.py \
           voice-agent/tests/test_nlu_vertical_integration.py
   git commit -m "feat(f-sara-nlu-patterns): complete NLU vertical rewrite — 6 macros × 17 sub-verticals"
   git push origin master
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
   ```

2. Run pytest on iMac:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -40"
   ```

3. Verify counts:
   - Total PASS must be ≥ 1488 (existing) + new test counts
   - FAIL must be 0
   - Confirm new test files appear in the run output

4. Quick functional smoke test:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -c \"
   from src.italian_regex import check_vertical_guardrail, VERTICAL_SERVICES, DURATION_MAP, OPERATOR_ROLES
   from src.entity_extractor import extract_vertical_entities
   print('hair keys:', len(VERTICAL_SERVICES['hair']))
   print('professionale keys:', len(VERTICAL_SERVICES['professionale']))
   print('DURATION_MAP verticals:', list(DURATION_MAP.keys()))
   print('OPERATOR_ROLES verticals:', list(OPERATOR_ROLES.keys()))
   r = check_vertical_guardrail('tagliando auto scaduto', 'hair')
   print('hair blocks auto OOS:', r.blocked)
   r2 = check_vertical_guardrail('dichiarazione dei redditi', 'professionale')
   print('professionale allows commercialista:', not r2.blocked)
   e = extract_vertical_entities('fisioterapia posturale tecarterapia', 'medico')
   print('medico fisioterapia specialty:', e.specialty)
   \""
   ```
   Expected: hair keys: 20+, professionale keys: 5+, 6 DURATION_MAP verticals, 6 OPERATOR_ROLES, blocked: True, allows: True, specialty: fisioterapia
  </how-to-verify>
  <resume-signal>Type "approved" when pytest shows ≥1488 PASS / 0 FAIL with new test files included. Or describe any failures to fix.</resume-signal>
</task>

</tasks>

<verification>
Full verification after checkpoint approval:

1. pytest on iMac: ≥1488 PASS + new tests, 0 FAIL
2. Orchestrator key mapping: all 6 new macros + all legacy keys map correctly
3. Guardrail integration: new vertical IDs correctly dispatch to new pattern sets
4. Entity extraction integration: all 6 verticals return sub_vertical or specialty

Update ROADMAP.md F-SARA-NLU-PATTERNS status to ✅ COMPLETE after approval.
</verification>

<success_criteria>
- orchestrator.py _extract_vertical_key() handles all 6 new macro keys + all legacy keys
- test_nlu_vertical_integration.py: ≥50 integration test cases covering full pipeline
- iMac pytest: ≥1488 PASS (existing) + all new test cases PASS, 0 FAIL
- ROADMAP.md F-SARA-NLU-PATTERNS marked ✅ COMPLETE with final test count
- STATE.md updated with completed phase
</success_criteria>

<output>
After checkpoint approval and ROADMAP update, create `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-04-SUMMARY.md`
</output>
