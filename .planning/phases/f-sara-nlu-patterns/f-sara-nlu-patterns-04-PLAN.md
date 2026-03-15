---
phase: f-sara-nlu-patterns
plan: "04"
type: execute
wave: 4
depends_on:
  - "01"
  - "02"
  - "03"
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
    - "Sara blocks 'voglio fare il tagliando' for a business with verticale_id 'hair_salone_bella'"
    - "pytest on iMac: ≥1488 existing PASS + new test_nlu_vertical_integration.py tests PASS, 0 FAIL"
    - "≥1 parametrized test case per synonym entry across test_hair_beauty_nlu.py, test_wellness_medico_nlu.py, test_auto_professionale_nlu.py"
    - "ROADMAP.md updated to mark F-SARA-NLU-PATTERNS complete"
  artifacts:
    - path: "voice-agent/src/orchestrator.py"
      provides: "Updated _extract_vertical_key() with new macro keys + legacy backward compat; lines 673 and 685 pass normalized vertical key (not raw verticale_id)"
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
Wire the NLU layer changes from Waves A/B/C into the orchestrator: update _extract_vertical_key() to recognize new macro keys from setup.ts taxonomy, fix a production bug on lines 673 and 685 where raw verticale_id is passed instead of the normalized key, create integration tests covering all 6 verticals end-to-end, run full pytest suite on iMac (≥1488 PASS), and update ROADMAP.

Purpose: Waves A/B/C added all patterns and entity extraction, but the orchestrator still maps unknown keys like "hair_*" and "beauty_*" to "altro". This plan closes the final gap: the runtime mapping that ensures new macro-category businesses actually use the new patterns. The bug on lines 673/685 is a production correctness issue — businesses with verticale_id "hair_salone_bella" would hit wrong guardrails without this fix.

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
  <name>Task 1: Update _extract_vertical_key() in orchestrator.py and fix lines 673 + 685</name>
  <files>voice-agent/src/orchestrator.py</files>
  <action>
PART A — Update _extract_vertical_key() method.

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

Replace the method body with the new implementation:

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

PART B — Fix production bug on lines 673 and 685 (MANDATORY).

Search orchestrator.py for the two call sites that pass raw `self.verticale_id` (or equivalent raw verticale_id variable) directly to `check_vertical_guardrail()` and `extract_vertical_entities()`.

Run this search to find them:
```bash
grep -n "check_vertical_guardrail\|extract_vertical_entities" voice-agent/src/orchestrator.py | head -20
```

For each occurrence on lines 673 and 685:
- If the call reads: `check_vertical_guardrail(text, self.verticale_id)` — change to: `check_vertical_guardrail(text, self._extract_vertical_key(self.verticale_id))`
- If the call reads: `extract_vertical_entities(text, self.verticale_id)` — change to: `extract_vertical_entities(text, self._extract_vertical_key(self.verticale_id))`

If `self._faq_vertical` is already set as a cached attribute (e.g., `self._faq_vertical = self._extract_vertical_key(self.verticale_id)` in __init__ or setup), use `self._faq_vertical` instead of calling the method inline — this avoids repeated computation. Confirm which pattern the codebase uses and apply consistently.

The fix is MANDATORY: without it, a business with verticale_id "hair_salone_bella" passes "hair_salone_bella" (not "hair") to guardrail/entity functions, which returns "altro" behavior (no guardrail active, all requests allowed — a silent correctness failure).

After the fix, verify with grep that no remaining call site passes raw verticale_id:
```bash
grep -n "check_vertical_guardrail\|extract_vertical_entities" voice-agent/src/orchestrator.py
```
All call sites must pass either `self._faq_vertical` or `self._extract_vertical_key(...)`.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION/voice-agent

# Confirm the new keys appear in orchestrator.py
grep -n "hair" voice-agent/src/orchestrator.py | head -10
```
Expected: lines showing "hair" as a recognized key in the NEW_VERTICALS list inside _extract_vertical_key.

```bash
# Confirm lines 673 and 685 no longer pass raw verticale_id
grep -n "check_vertical_guardrail\|extract_vertical_entities" voice-agent/src/orchestrator.py
```
Expected: all occurrences use `self._faq_vertical` or `self._extract_vertical_key(...)`, NOT bare `self.verticale_id`.

```bash
# Test the mapping logic end-to-end
python -c "
def _extract_vertical_key_impl(verticale_id):
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
    result = _extract_vertical_key_impl(vid)
    status = 'PASS' if result == expected else 'FAIL'
    if status == 'FAIL':
        all_pass = False
    print(f'{status}: {vid!r} -> {result!r} (expected {expected!r})')
print('All pass:', all_pass)
"
```
Expected: All PASS, all_pass: True

```bash
# Confirm guardrail fires for hair_salone_bella + tagliando
python -c "
from src.italian_regex import check_vertical_guardrail

def _extract_vertical_key_impl(vid):
    NEW_VERTICALS = ['hair', 'beauty', 'wellness', 'medico', 'professionale']
    LEGACY_VERTICALS = ['salone', 'palestra', 'medical', 'auto', 'altro']
    v_lower = vid.lower().strip()
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if v_lower == v or v_lower.startswith(v + '_') or v_lower.startswith(v + '-'):
            return v
    for v in NEW_VERTICALS + LEGACY_VERTICALS:
        if v_lower.startswith(v):
            return v
    return 'altro'

key = _extract_vertical_key_impl('hair_salone_bella')
r = check_vertical_guardrail('voglio fare il tagliando', key)
print('hair_salone_bella blocks tagliando OOS:', r.blocked)
"
```
Expected: hair_salone_bella blocks tagliando OOS: True
  </verify>
  <done>
- _extract_vertical_key() handles: hair, beauty, wellness, medico, professionale (new keys)
- Legacy keys salone, palestra, medical, auto still return correctly
- Composed IDs like "hair_salone_bella" extract to "hair"
- Unknown IDs return "altro"
- Lines 673 and 685: check_vertical_guardrail and extract_vertical_entities call sites now pass normalized key, not raw verticale_id
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

Add the standalone helper function at module level (replicate orchestrator logic for isolated testing):
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

SECTION 1 — TestVerticalKeyMapping:

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
    assert _extract_vertical_key_impl(verticale_id) == expected
```

SECTION 2 — TestNLUPipelineIntegration:

Tests guardrail check with vertical key extraction (simulates orchestrator runtime):

```python
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
    vertical_key = _extract_vertical_key_impl(verticale_id)
    result = check_vertical_guardrail(text, vertical_key)
    assert result.blocked == expect_blocked, (
        f"vertical_key={vertical_key!r}, text={text!r}: "
        f"expected blocked={expect_blocked}, got {result.blocked}"
    )
```

SECTION 3 — TestSubVerticalExtraction (sub_vertical for non-medico verticals):

```python
@pytest.mark.parametrize("verticale_id,text,expected_sub_vertical", [
    ("hair", "barba sfumata fade skin", "barbiere"),
    ("hair_salone_bella", "correzione colore Olaplex", "color_specialist"),
    ("beauty", "pulizia viso profonda", "estetista_viso"),
    ("beauty_centro_rosa", "ricostruzione unghie gel", "nail_specialist"),
    ("wellness", "corso di yoga nidra", "yoga_pilates"),
    ("wellness_gym_fit", "BJJ muay thai", "arti_marziali"),
    ("auto", "diagnosi OBD centralina", "elettrauto"),
    ("auto_officina", "detailing ceramica PPF", "detailing"),
    ("professionale", "dichiarazione 730 Unico", "commercialista"),
    ("professionale_studio", "consulenza legale divorzio", "avvocato"),
    # Legacy aliases
    ("salone", "extension cheratina I-tip", "extension_specialist"),
])
def test_sub_vertical_extraction(self, verticale_id, text, expected_sub_vertical):
    from src.entity_extractor import extract_vertical_entities
    vertical_key = _extract_vertical_key_impl(verticale_id)
    result = extract_vertical_entities(text, vertical_key)
    assert result.sub_vertical == expected_sub_vertical, (
        f"vertical_key={vertical_key!r}, text={text!r}: "
        f"expected sub_vertical={expected_sub_vertical!r}, got {result.sub_vertical!r}"
    )
```

SECTION 4 — TestMedicoSpecialtyExtraction (specialty field for medico):

```python
@pytest.mark.parametrize("verticale_id,text,expected_specialty", [
    ("medico", "fisioterapia posturale tecarterapia", "fisioterapia"),
    ("medico_studio", "seduta psicologo TCC", "psicologo"),
    ("medico_studio_rossi", "osteopata manipolazione osteopatica", "osteopata"),
    ("medical_studio", "nutrizionista BIA piano alimentare", "nutrizionista"),
])
def test_medico_specialty_extraction(self, verticale_id, text, expected_specialty):
    from src.entity_extractor import extract_vertical_entities
    vertical_key = _extract_vertical_key_impl(verticale_id)
    result = extract_vertical_entities(text, vertical_key)
    assert result.specialty == expected_specialty, (
        f"vertical_key={vertical_key!r}, text={text!r}: "
        f"expected specialty={expected_specialty!r}, got {result.specialty!r}"
    )
```

Use `pytest.mark.parametrize` for all test methods. Use plain pytest classes (no unittest.TestCase).
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
- TestSubVerticalExtraction: ≥11 cases (sub_vertical for hair/beauty/wellness/auto/professionale)
- TestMedicoSpecialtyExtraction: ≥4 cases (specialty field for medico, separate method)
- All PASS on MacBook before iMac run
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
Full NLU vertical rewrite across 4 plans:
- Wave A (Plan 01): hair + beauty patterns, guardrails, entity extraction, 60+ tests
- Wave B (Plan 02): wellness + medico patterns, guardrails, entity extraction, 50+ tests
- Wave C (Plan 03): auto extended + professionale, DURATION_MAP, OPERATOR_ROLES, 50+ tests
- Wave D (Plan 04): orchestrator wiring (including line 673/685 production bug fix) + integration tests

Before this checkpoint, Claude pushes to iMac and runs the full pytest suite.
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
   git commit -m "feat(f-sara-nlu-patterns): complete NLU vertical rewrite — 6 macros x 17 sub-verticals"
   git push origin master
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
   ```

2. Run full pytest suite on iMac:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -40"
   ```

3. Run new NLU test files specifically to confirm counts:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && source venv/bin/activate && python -m pytest tests/test_hair_beauty_nlu.py tests/test_wellness_medico_nlu.py tests/test_auto_professionale_nlu.py tests/test_nlu_vertical_integration.py -v 2>&1 | tail -20"
   ```

4. Verify counts:
   - Full suite total PASS must be ≥ 1488 (existing baseline) + new test counts
   - FAIL must be 0
   - All 4 new test files must appear in the run output

5. Quick functional smoke test on iMac:
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
  <resume-signal>Type "approved" when pytest shows ≥1488 PASS / 0 FAIL with all 4 new test files included. Or describe any failures to fix.</resume-signal>
</task>

</tasks>

<verification>
Full verification after checkpoint approval:

1. pytest on iMac: ≥1488 PASS + new tests, 0 FAIL
2. Orchestrator key mapping: all 6 new macros + all legacy keys map correctly
3. Lines 673 and 685: guardrail/entity calls verified to use normalized key, not raw verticale_id
4. Guardrail integration: new vertical IDs like "hair_salone_bella" correctly dispatch to "hair" patterns
5. Entity extraction integration: all 6 verticals return sub_vertical or specialty

Update ROADMAP.md F-SARA-NLU-PATTERNS status to COMPLETE after approval.
</verification>

<success_criteria>
- orchestrator.py _extract_vertical_key() handles all 6 new macro keys + all legacy keys
- Lines 673 and 685 fixed: check_vertical_guardrail and extract_vertical_entities receive normalized key
- test_nlu_vertical_integration.py: ≥50 integration test cases covering full pipeline split into sub_vertical (non-medico) + specialty (medico) sections
- iMac pytest: ≥1488 PASS (existing) + all new test cases PASS, 0 FAIL
- ROADMAP.md F-SARA-NLU-PATTERNS marked COMPLETE with final test count
- STATE.md updated with completed phase
</success_criteria>

<output>
After checkpoint approval and ROADMAP update, create `.planning/phases/f-sara-nlu-patterns/f-sara-nlu-patterns-04-SUMMARY.md`
</output>
