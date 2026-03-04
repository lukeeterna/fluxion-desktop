---
phase: f02-vertical-system-sara
plan: "02"
subsystem: voice-agent
tags: [python, orchestrator, entity-extraction, vertical-guardrail, fsm, italian-nlp, regex]

# Dependency graph
requires:
  - phase: f02-01
    provides: "VERTICAL_GUARDRAILS dict + check_vertical_guardrail() + GuardrailResult in italian_regex.py"
provides:
  - "orchestrator.py imports VERTICAL_SERVICES and check_vertical_guardrail from italian_regex"
  - "BookingStateMachine initialized with services_config=VERTICAL_SERVICES.get(verticale_id, {})"
  - "set_vertical() re-passes services_config to FSM on vertical switch"
  - "process() injects vertical guardrail check before L0 Special Commands"
  - "process() calls extract_vertical_entities() and stores results in context.extra_entities"
  - "extract_vertical_entities(text, vertical) in entity_extractor.py — VerticalEntities dataclass"
  - "Medical: 10 specialties, 3 urgency levels, 5 visit types via regex"
  - "Auto: targa italiana (AB123CD format) + 38 brand patterns"
  - "25 unit tests in test_vertical_entity_extractor.py, all PASS"
affects:
  - f02-03
  - future-voice-agent-features
  - booking-state-machine-vertical-extensions

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "HAS_VERTICAL_ENTITIES guard: try/except import wraps extract_vertical_entities for graceful degradation"
    - "context.extra_entities dict: FSM context augmented with vertical-specific entities at L0-PRE"
    - "Vertical isolation: extract_vertical_entities returns empty VerticalEntities for non-targeted verticals"
    - "Brand pattern sort by length desc: multi-word brands matched before single-word (alfa romeo before alfa)"

key-files:
  created:
    - "voice-agent/tests/test_vertical_entity_extractor.py"
  modified:
    - "voice-agent/src/orchestrator.py"
    - "voice-agent/src/entity_extractor.py"

key-decisions:
  - "HAS_VERTICAL_ENTITIES guard separate from HAS_ITALIAN_REGEX to allow fine-grained feature disable"
  - "Guardrail check runs even if entity extraction import fails (separate guards)"
  - "entity extraction only runs if response is None — unblocked requests only"
  - "ginecologica/ginecologico adjective forms added to ginecologia keywords (bug fix)"

patterns-established:
  - "L0-PRE injection pattern: new pipeline stages inserted between L0-PRE content filter and L0 Special Commands"
  - "extra_entities dict on context: shared store for vertical-specific data accessible to all FSM layers"

# Metrics
duration: 5min
completed: "2026-03-04"
---

# Phase F02 Plan 02: Orchestrator Wiring + Vertical Entity Extraction Summary

**Vertical guardrail + entity extraction wired into orchestrator pipeline; BookingStateMachine now receives services_config from VERTICAL_SERVICES; medical specialty/urgency/visit_type and auto targa/brand extracted at L0-PRE**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-04T14:11:12Z
- **Completed:** 2026-03-04T14:15:59Z
- **Tasks:** 2
- **Files modified:** 3 (orchestrator.py, entity_extractor.py, test_vertical_entity_extractor.py)

## Accomplishments
- Fixed long-standing bug: BookingStateMachine now initialized with services_config from VERTICAL_SERVICES[verticale_id] instead of empty (Sara was always using default/empty service synonyms)
- Vertical guardrail check injected into process() pipeline at L0-PRE position, blocks off-vertical requests before special commands
- extract_vertical_entities() wired into process() at L0-PRE; results stored in booking_sm.context.extra_entities for FSM layer consumption
- set_vertical() now re-passes services_config on vertical switch (was previously leaving stale services_config after runtime vertical change)
- 25 unit tests for vertical entity extraction, all PASS; full suite 1197 PASS (was 1160)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix orchestrator — FSM init + set_vertical() + guardrail + entity extraction wiring** - `bb98906` (feat)
2. **Task 2: extract_vertical_entities() + test_vertical_entity_extractor.py** - `a1102d8` (feat)

**Plan metadata:** (to be added by final commit)

## Files Created/Modified
- `voice-agent/src/orchestrator.py` - Added VERTICAL_SERVICES/check_vertical_guardrail/extract_vertical_entities imports; fixed BookingStateMachine init; fixed set_vertical(); injected L0-PRE guardrail + entity extraction in process()
- `voice-agent/src/entity_extractor.py` - Appended _MEDICAL_SPECIALTIES, _MEDICAL_URGENCY_PATTERNS, _MEDICAL_VISIT_COMPILED, _TARGA_PATTERN, _AUTO_BRAND_PATTERN, VerticalEntities dataclass, extract_vertical_entities() function
- `voice-agent/tests/test_vertical_entity_extractor.py` - 25 unit tests across 6 test classes (TestMedicalSpecialty, TestMedicalUrgency, TestMedicalVisitType, TestAutoPlate, TestAutoBrand, TestVerticalIsolation)

## Decisions Made
- HAS_VERTICAL_ENTITIES guard kept separate from HAS_ITALIAN_REGEX: if entity extractor import fails, guardrail still runs (both are optional but independent)
- Entity extraction block condition: `response is None and HAS_ITALIAN_REGEX and HAS_VERTICAL_ENTITIES` — only runs when guardrail did not block, following existing L0 pattern
- Adjective forms added to ginecologia keywords: "ginecologica", "ginecologico" (real-world users say "visita ginecologica" not "una ginecologia")

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added ginecologica/ginecologico adjective forms to ginecologia keywords**
- **Found during:** Task 2 (running test_vertical_entity_extractor.py)
- **Issue:** Test input `"prenoto una visita ginecologica"` failed — keyword list only had `"ginecologia"` (noun) not `"ginecologica"` (adjective form)
- **Fix:** Added `"ginecologica"` and `"ginecologico"` to the `_MEDICAL_SPECIALTIES["ginecologia"]` keyword list
- **Files modified:** voice-agent/src/entity_extractor.py
- **Verification:** test_ginecologa_detected now PASS; 25/25 tests PASS
- **Committed in:** a1102d8 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix essential for correct medical specialty detection. No scope creep.

## Issues Encountered
- `python -c "from src.orchestrator import VoiceOrchestrator"` fails on MacBook due to missing venv packages (groq, aiohttp) — this is expected, orchestrator runs on iMac. Core python-level verification confirmed via individual module imports and the full pytest suite.

## Next Phase Readiness
- f02-02 complete: orchestrator is wired for vertical guardrails + entity extraction
- f02-03 (final plan in phase): any remaining vertical system integration or verification
- Voice pipeline restart on iMac required after syncing these Python changes
- Reminder: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"`

---
*Phase: f02-vertical-system-sara*
*Completed: 2026-03-04*
