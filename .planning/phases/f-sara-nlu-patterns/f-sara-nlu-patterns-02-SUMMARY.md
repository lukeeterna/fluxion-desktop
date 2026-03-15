---
phase: f-sara-nlu-patterns
plan: "02"
subsystem: nlu
tags: [italian-regex, entity-extractor, vertical-guardrails, wellness, medico, pytest]

# Dependency graph
requires:
  - phase: f-sara-nlu-patterns
    plan: "01"
    provides: "hair+beauty NLU patterns, VerticalEntities.sub_vertical field, elif hair/beauty branches in extract_vertical_entities()"
provides:
  - VERTICAL_SERVICES[wellness] — 15 service groups for palestra/fitness center
  - VERTICAL_SERVICES[medico] — 18 service groups for medical/specialist clinic
  - VERTICAL_GUARDRAILS[wellness] — 21 multi-word patterns (hair/beauty/auto/medical/auto-verbform OOS)
  - VERTICAL_GUARDRAILS[medico] — 20 multi-word patterns (hair/beauty/auto/palestra/auto-verbform OOS)
  - Legacy aliases palestra->wellness, medical->medico in both dicts
  - _MEDICAL_SPECIALTIES extended: fisioterapia, osteopata, psicologo, nutrizionista, podologo, odontoiatria++
  - _WELLNESS_SUB_VERTICAL_KEYWORDS: personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali
  - extract_vertical_entities() elif branch for wellness/palestra vertical
  - 132-test parametrized test suite for wellness+medico NLU
affects:
  - f-sara-nlu-patterns-03
  - f-sara-nlu-patterns-04
  - orchestrator.py (uses check_vertical_guardrail + extract_vertical_entities)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Legacy aliases pattern: VERTICAL_SERVICES['palestra'] = VERTICAL_SERVICES['wellness'] — alias after dict definition"
    - "Verb-form auto guardrail patterns needed in every non-auto vertical for backward compat"
    - "Sub-vertical extraction via dict keyword loop — same pattern as hair/beauty"

key-files:
  created:
    - voice-agent/tests/test_wellness_medico_nlu.py
  modified:
    - voice-agent/src/italian_regex.py
    - voice-agent/src/entity_extractor.py

key-decisions:
  - "wellness guardrail includes visita medica/specialistica OOS (legacy palestra had this)"
  - "wellness guardrail includes cambiare le gomme verb-form (legacy palestra had this)"
  - "medico guardrail includes cambiare le gomme verb-form (legacy medical had this)"
  - "odontoiatria specialty keywords extended with invisalign/ortodonzia/sbiancamento for plan test coverage"
  - "cardiologica/cardiologico adjective forms added to cardiologia keywords"

patterns-established:
  - "Pattern: ogni new vertical alias MUST carry all legacy verb-form patterns from original dict"
  - "Pattern: test_wellness_medico_nlu.py structure mirrors test_guardrails.py (sys.path.insert, plain pytest classes)"

# Metrics
duration: 7min
completed: 2026-03-15
---

# Phase f-sara-nlu-patterns Plan 02: Wellness + Medico NLU Patterns Summary

**wellness (15 service groups, 21 guardrail patterns) and medico (18 service groups, 20 patterns) added to Sara's NLU layer, with full sub-vertical entity extraction and 132-test coverage, 0 failures**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-15T12:15:49Z
- **Completed:** 2026-03-15T12:22:49Z
- **Tasks:** 3
- **Files modified:** 3 (2 source + 1 test)

## Accomplishments
- VERTICAL_SERVICES and VERTICAL_GUARDRAILS extended with "wellness" (15 groups, 21 patterns) and "medico" (18 groups, 20 patterns) — both aliased to legacy palestra/medical keys
- _MEDICAL_SPECIALTIES extended with 5 new sub-verticals (fisioterapia, osteopata, psicologo, nutrizionista, podologo) plus adjective forms for cardiologia and extended odontoiatria
- _WELLNESS_SUB_VERTICAL_KEYWORDS added; extract_vertical_entities() handles wellness/palestra with 5 sub-vertical mappings
- 132 parametrized test cases, all passing, no regressions in existing 181 tests (313 total)

## Task Commits

1. **Task 1: VERTICAL_SERVICES + VERTICAL_GUARDRAILS wellness/medico** - `835fd65` (feat)
2. **Task 2: entity_extractor.py _MEDICAL_SPECIALTIES + _WELLNESS_SUB_VERTICAL_KEYWORDS** - `36c29e5` (feat)
3. **Task 3: test_wellness_medico_nlu.py + guardrail pattern fixes** - `4a9aa35` (feat)

## Files Created/Modified
- `voice-agent/src/italian_regex.py` — VERTICAL_SERVICES[wellness/medico], VERTICAL_GUARDRAILS[wellness/medico], _GUARDRAIL_RESPONSES entries, legacy aliases palestra/medical
- `voice-agent/src/entity_extractor.py` — _MEDICAL_SPECIALTIES extended (5 new + adjectives/odontoiatria), _WELLNESS_SUB_VERTICAL_KEYWORDS dict, elif wellness/palestra branch in extract_vertical_entities()
- `voice-agent/tests/test_wellness_medico_nlu.py` — 132 parametrized tests: TestWellnessGuardrails (36), TestMedicoGuardrails (35), TestWellnessEntityExtraction (30), TestMedicoEntityExtraction (31)

## Decisions Made
- **wellness guardrail includes visita medica/specialistica**: The legacy "palestra" guardrail blocked these; the alias must preserve this behavior or existing tests fail. Added explicitly to "wellness".
- **wellness + medico get cambiare-le-gomme verb-form pattern**: Same reason — legacy palestra/medical had `cambiar[ei]..gomm[ea]` verb-form. Required for backward compat.
- **odontoiatria keywords extended**: Plan test case "invisalign aligner ortodonzia" expected specialty="odontoiatria" but existing keywords only had noun forms ("dentista", "denti" etc.). Added invisalign/ortodonzia/sbiancamento denti to close coverage gap.
- **cardiologica/cardiologico adjective forms**: "visita cardiologica" (adjective) does not substring-match "cardiologia" (noun). Added adjective forms so "visita cardiologica urgente" correctly returns specialty=cardiologia.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing verb-form auto patterns in wellness guardrail**
- **Found during:** Task 3 (regression testing)
- **Issue:** VERTICAL_GUARDRAILS["palestra"] was aliased to VERTICAL_GUARDRAILS["wellness"], but wellness lacked the `cambiar[ei]..gomm[ea]` verb-form pattern and `visita medica/specialistica` that legacy palestra had — causing 2 regression failures in test_guardrails.py
- **Fix:** Added `visita medica/specialistica` and `cambiar[ei]..gomm[ea]` patterns to wellness guardrail; added `cambiar[ei]..gomm[ea]` to medico guardrail
- **Files modified:** voice-agent/src/italian_regex.py
- **Verification:** 313 tests pass (no regressions)
- **Committed in:** 4a9aa35 (Task 3 commit)

**2. [Rule 1 - Bug] _MEDICAL_SPECIALTIES[odontoiatria] missing invisalign/ortodonzia**
- **Found during:** Task 3 (test execution)
- **Issue:** "invisalign aligner ortodonzia" expected specialty=odontoiatria but keyword list only had noun forms like "dentista", "denti"
- **Fix:** Added invisalign, aligner dentale, ortodonzia, ortodontista, sbiancamento denti, odontoiatra, pulizia denti to odontoiatria keywords
- **Files modified:** voice-agent/src/entity_extractor.py
- **Committed in:** 4a9aa35 (Task 3 commit)

**3. [Rule 1 - Bug] _MEDICAL_SPECIALTIES[cardiologia] missing adjective forms**
- **Found during:** Task 2 (verify step)
- **Issue:** "visita cardiologica" doesn't substring-match "cardiologia" — Python `"cardiologia" in "cardiologica"` is False
- **Fix:** Added cardiologica, cardiologico adjective forms
- **Files modified:** voice-agent/src/entity_extractor.py
- **Committed in:** 36c29e5 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs in legacy keyword/pattern coverage)
**Impact on plan:** All fixes required for backward compat and test coverage. No scope creep.

## Issues Encountered
- Initial edit placed "wellness" dict outside VERTICAL_SERVICES closing brace (IndentationError). Fixed by correcting the insertion point (beauty's `},` then `wellness` stays inside the outer `}`). Same issue for VERTICAL_GUARDRAILS. Both resolved in Task 1 before commit.

## Next Phase Readiness
- Wave B complete: wellness + medico verticals fully covered in NLU layer
- Plan 03 (Wave C — professionale + auto expansion) ready to execute
- Plan 04 (Wave D — orchestrator vertical key normalization) will fix the production bug in orchestrator.py lines 673+685 that passes raw `self.verticale_id` instead of normalized key

---
*Phase: f-sara-nlu-patterns*
*Completed: 2026-03-15*
