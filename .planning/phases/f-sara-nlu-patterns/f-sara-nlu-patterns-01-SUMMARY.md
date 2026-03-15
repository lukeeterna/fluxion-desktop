---
phase: f-sara-nlu-patterns
plan: "01"
subsystem: voice-agent-nlu
tags: [python, italian-regex, entity-extractor, guardrails, hair, beauty, sub-vertical]

requires:
  - phase: f02-vertical-guardrail
    provides: "VERTICAL_GUARDRAILS dict, check_vertical_guardrail(), GuardrailResult dataclass, multi-word guardrail pattern rule"
  - phase: f02.1-temporal
    provides: "extract_vertical_entities(), VerticalEntities dataclass, auto/medical entity extraction"

provides:
  - VERTICAL_SERVICES["hair"] — 21 service groups with comprehensive Italian synonyms (incl. fade, barba_stilizzata, correzione_colore, tricologo)
  - VERTICAL_SERVICES["beauty"] — 16 service groups with comprehensive Italian synonyms (pulizia_viso, nail_art, epilazione_laser, spa, etc.)
  - VERTICAL_SERVICES["salone"] alias — points to hair dict for backward compat
  - VERTICAL_GUARDRAILS["hair"] — 30 multi-word OOS patterns (auto verb-forms, medical, palestra, professionale)
  - VERTICAL_GUARDRAILS["beauty"] — 18 multi-word OOS patterns (hair-specific, auto, medical, palestra)
  - VERTICAL_GUARDRAILS["salone"] alias — points to hair guardrail for backward compat
  - VerticalEntities.sub_vertical field (Optional[str]) for all verticals
  - _HAIR_SUB_VERTICAL_KEYWORDS + hair/salone branch in extract_vertical_entities()
  - _BEAUTY_SERVICE_KEYWORDS + beauty branch in extract_vertical_entities()
  - test_hair_beauty_nlu.py — 122 parametrized test cases, all passing

affects:
  - f-sara-nlu-patterns-02 (wellness + medico Wave B — builds on same guardrail/entity pattern)
  - f-sara-nlu-patterns-03 (auto + professionale Wave C)
  - f-sara-nlu-patterns-04 (orchestrator wiring — uses hair/beauty vertical keys)

tech-stack:
  added: []
  patterns:
    - "VERTICAL_SERVICES[key] = VERTICAL_SERVICES[other_key] — alias pattern for legacy compat"
    - "VERTICAL_GUARDRAILS[key] = VERTICAL_GUARDRAILS[other_key] — guardrail alias pattern"
    - "Sub-vertical keyword dict with keyword-match loop in extract_vertical_entities()"
    - "Test class structure: TestXGuardrails + TestXEntityExtraction with pytest.mark.parametrize"

key-files:
  created:
    - voice-agent/tests/test_hair_beauty_nlu.py
  modified:
    - voice-agent/src/italian_regex.py
    - voice-agent/src/entity_extractor.py

key-decisions:
  - "VERTICAL_SERVICES['salone'] = VERTICAL_SERVICES['hair'] alias post-dict — overrides original salone entry, 40+ backward compat tests pass"
  - "hair guardrail includes full verb-form auto patterns from original salone guardrail (cambiare gomme, far vedere la macchina, etc.)"
  - "sub_vertical field added to VerticalEntities as Optional[str] = None — zero-impact on existing medical/auto extraction"
  - "elif vertical in ('hair', 'salone') — single branch handles both keys for entity extraction"
  - "'medical' check updated to also match 'medico' key (prep for Wave B)"

patterns-established:
  - "Vertical alias: assign one dict key to another AFTER dict literal closes"
  - "Sub-vertical detection: iterate _X_SUB_VERTICAL_KEYWORDS, break on first match"
  - "Test parametrize: separate test methods per OOS category (auto, medical, palestra) + in-scope"

duration: 5min
completed: 2026-03-15
---

# Phase f-sara-nlu-patterns Plan 01: Hair and Beauty NLU Summary

**hair and beauty verticals added to Sara NLU: 21+16 service synonym groups, 30+18 guardrail patterns, sub-vertical entity detection (barbiere/color_specialist/tricologo/extension_specialist for hair; estetista_viso/corpo/nail_specialist/epilazione_laser/spa for beauty), 122 tests all passing**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-15T12:04:23Z
- **Completed:** 2026-03-15T12:09:41Z
- **Tasks:** 3/3
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- VERTICAL_SERVICES["hair"] with 21 groups covering all sub-verticals (taglio, fade, barba_stilizzata, correzione_colore, tricologo, extension++) — salone aliased to hair for backward compat
- VERTICAL_SERVICES["beauty"] with 16 groups (pulizia_viso, peeling, radiofrequenza_viso, nail_art, epilazione_laser, circuito_spa++) — zero prior coverage, now complete
- VERTICAL_GUARDRAILS["hair"] (30 patterns) + VERTICAL_GUARDRAILS["beauty"] (18 patterns) with alias for salone
- VerticalEntities.sub_vertical field + keyword dicts + extraction branches for hair/beauty — 317 tests total, 0 failures

## Task Commits

1. **Task 1: Expand VERTICAL_SERVICES and VERTICAL_GUARDRAILS** - `4d0e6c1` (feat)
2. **Task 2: Add sub_vertical field and hair/beauty entity extraction** - `e11e890` (feat)
3. **Task 3: Create test_hair_beauty_nlu.py** - `c7366ba` (test)

## Files Created/Modified

- `voice-agent/src/italian_regex.py` — Added hair (21 groups) + beauty (16 groups) VERTICAL_SERVICES; hair (30 patterns) + beauty (18 patterns) VERTICAL_GUARDRAILS; salone aliases; hair/beauty _GUARDRAIL_RESPONSES
- `voice-agent/src/entity_extractor.py` — Added VerticalEntities.sub_vertical field; _HAIR_SUB_VERTICAL_KEYWORDS + _BEAUTY_SERVICE_KEYWORDS dicts; elif hair/salone and beauty branches in extract_vertical_entities(); medical -> medico alias prep
- `voice-agent/tests/test_hair_beauty_nlu.py` — 122 parametrized test cases across 4 classes: TestHairGuardrails (41), TestBeautyGuardrails (31), TestHairEntityExtraction (21), TestBeautyEntityExtraction (18), all PASS

## Decisions Made

- **salone alias approach**: `VERTICAL_SERVICES["salone"] = VERTICAL_SERVICES["hair"]` after dict literal — overrides the original salone entry in the dict, making them the same object. All 50 existing test_guardrails.py tests pass.
- **hair guardrail includes full verb-form patterns**: The original salone guardrail had verb-form auto patterns (cambiare gomme, far vedere la macchina, etc.) that weren't in the plan's "hair" patterns. Added them to ensure backward compat — 3 tests that were failing are now passing.
- **sub_vertical = None default**: No-impact on medical/auto existing extraction. Only hair/beauty branches set it.
- **elif in ("hair", "salone")**: Single branch handles both keys — avoids code duplication.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing verb-form auto patterns in hair guardrail**

- **Found during:** Task 1 verification (`python3 -m pytest tests/test_guardrails.py`)
- **Issue:** The plan listed simplified patterns for the "hair" guardrail that omitted the full verb-form auto patterns present in the original "salone" guardrail (e.g., `cambiar[ei] ... gomme`, `far[ei]? vedere la macchina`). Since "salone" is now aliased to "hair", these 3 test cases would fail.
- **Fix:** Added the complete verb-form auto patterns from the original salone guardrail into the "hair" guardrail entry — same patterns, same coverage.
- **Files modified:** `voice-agent/src/italian_regex.py`
- **Verification:** All 50 test_guardrails.py tests pass (was 47 before fix)
- **Committed in:** `4d0e6c1` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Essential bug fix for backward compat. No scope creep. Guardrail now has 30 patterns instead of planned 20 minimum.

## Issues Encountered

None beyond the auto-fixed verb-form pattern gap above.

## Next Phase Readiness

- Wave A (hair + beauty) complete — Wave B (wellness + medico) can proceed in parallel
- Plan 02 (f-sara-nlu-patterns-02) ready to execute: wellness/medico guardrails + entity extraction
- Plan 03 (DURATION_MAP + OPERATOR_ROLES data structures) ready
- Plan 04 (orchestrator wiring + bug fix for self.verticale_id key normalization) ready
- No blockers. All 317 affected tests pass.

---
*Phase: f-sara-nlu-patterns*
*Completed: 2026-03-15*
