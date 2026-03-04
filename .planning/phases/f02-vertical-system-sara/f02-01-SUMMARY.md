---
phase: f02-vertical-system-sara
plan: 01
subsystem: voice-agent
tags: [python, regex, nlp, guardrails, vertical, l0-layer, italian]

# Dependency graph
requires:
  - phase: voice-agent-core
    provides: italian_regex.py L0 regex layer with pre-compiled patterns
provides:
  - VERTICAL_GUARDRAILS dict with 4 verticals (salone, palestra, medical, auto)
  - check_vertical_guardrail(text, vertical) -> GuardrailResult function
  - GuardrailResult dataclass (blocked, vertical, matched_pattern, redirect_response)
  - 33 unit tests covering all verticals and edge cases
affects:
  - f02-02 (entity extractor vertical-aware)
  - f02-03 (orchestrator integration — L0-pre guardrail call)
  - voice-agent orchestrator.py (will import and call check_vertical_guardrail)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Multi-word-only regex patterns for vertical guardrails (no single-word blocks)"
    - "Pre-compiled pattern dict at module load for < 2ms runtime"
    - "GuardrailResult dataclass with blocked/vertical/matched_pattern/redirect_response"
    - "Polite Italian redirect responses per vertical"

key-files:
  created:
    - voice-agent/tests/test_guardrails.py
  modified:
    - voice-agent/src/italian_regex.py

key-decisions:
  - "Multi-word patterns only — avoids false positives (e.g. 'colore' alone would break medical)"
  - "Context-word patterns for manicure/pedicure: 'la manicure', 'fare la manicure' etc."
  - "Ceretta/depilazione require compound: 'ceretta gambe', 'depilazione laser'"
  - "GuardrailResult uses _dataclass_gr alias to avoid naming collision with existing dataclass import"

patterns-established:
  - "Section 10 appended to italian_regex.py following existing section numbering convention"
  - "Each new vertical data dict uses Dict[str, List[str]] type with pre-compilation companion"

# Metrics
duration: 6min
completed: 2026-03-04
---

# Phase F02 Plan 01: Vertical Guardrails Summary

**VERTICAL_GUARDRAILS dict with 52 multi-word Italian regex patterns across 4 verticals (salone/palestra/medical/auto) + check_vertical_guardrail() function, 33 unit tests all passing**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-03-04T14:00:48Z
- **Completed:** 2026-03-04T14:06:36Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added section 10 to `italian_regex.py` with `VERTICAL_GUARDRAILS` dict (4 verticals, 11-14 patterns each) and `check_vertical_guardrail()` function
- `GuardrailResult` dataclass returns `blocked`, `vertical`, `matched_pattern`, `redirect_response`
- All patterns pre-compiled at module import time for < 2ms runtime
- 33 unit tests across 5 test classes — all PASS; full suite 1172 PASS, 0 regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: VERTICAL_GUARDRAILS + check_vertical_guardrail()** - `b6963da` (feat)
2. **Task 2: test_guardrails.py — 33 unit tests** - `f88d88f` (test)
3. **Auto-fix: enforce multi-word-only rule** - `81eee77` (fix) — see Deviations

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `voice-agent/src/italian_regex.py` - Added section 10: VERTICAL_GUARDRAILS dict, GuardrailResult dataclass, _GUARDRAIL_COMPILED pre-compilation, _GUARDRAIL_RESPONSES, check_vertical_guardrail() function; updated module docstring
- `voice-agent/tests/test_guardrails.py` - New: 33 unit tests across TestSaloneGuardrails, TestPalestraGuardrails, TestMedicalGuardrails, TestAutoGuardrails, TestGuardrailEdgeCases

## Decisions Made

- Used `from dataclasses import dataclass as _dataclass_gr` alias to avoid collision with existing `dataclass` import in the file
- Manicure/pedicure patterns use article/verb context: `(?:la|una|fare la|...) manicure` to satisfy multi-word constraint while still matching natural Italian speech
- Ceretta/epilazione/depilazione require body part or modifier context: `ceretta gambe`, `depilazione laser`, etc.
- `gomme invernali` added alongside `cambio gomme` after test revealed the base pattern missed this common variant

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] salone gomme pattern missed "gomme invernali" without "cambio"**

- **Found during:** Task 2 (running tests)
- **Issue:** Pattern `\b(?:cambio\s+gomme|pneumatici\s+(?:invernali|estivi|nuovi))\b` required "cambio gomme" or "pneumatici invernali". Test input "devo cambiare le gomme invernali" did not match.
- **Fix:** Extended pattern to `(?:cambio\s+gomme|gomme\s+(?:invernali|estivi|nuove)|pneumatici\s+...)`
- **Files modified:** `voice-agent/src/italian_regex.py`
- **Verification:** `test_salone_blocks_gomme_invernali` PASS
- **Committed in:** f88d88f (Task 2 commit)

**2. [Rule 1 - Bug] Single-word patterns violated plan's multi-word-only rule**

- **Found during:** Post-task verification (`each pattern must contain \s+`)
- **Issue:** `\b(?:ceretta|depilazione|epilazione)\b` in medical and auto verticals were pure single-word alternations with no `\s`. `\b(?:manicure|pedicure|nail\s+art)\b` in auto was similarly problematic.
- **Fix:** Replaced with context-word patterns: `(?:(?:la|una|fare la|...) manicure|manicure \w+|...)` and `(?:ceretta gambe|depilazione laser|epilazione laser|...)`
- **Files modified:** `voice-agent/src/italian_regex.py`
- **Verification:** `python3 -c "for v, pats in ...: assert '\\s' in p"` passes; all 33 tests still PASS
- **Committed in:** 81eee77 (fix commit)

---

**Total deviations:** 2 auto-fixed (2x Rule 1 - Bug)
**Impact on plan:** Both fixes improve pattern correctness and adhere to the multi-word-only safety rule. No scope creep.

## Issues Encountered

- `python -m pytest` invoked the wrong Python (3.12 without pytest); used `python3 -m pytest` (Python 3.13 with pytest 8.3.5) — resolved immediately
- VAD tests (`test_vad_skill.py`, `test_vad_file.py`) have pre-existing collection errors due to missing ONNX hardware dependencies on MacBook — not related to this work

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `check_vertical_guardrail(text, vertical)` is ready to be imported in `orchestrator.py` at L0-pre stage (f02-03)
- `GuardrailResult` dataclass is importable from `src.italian_regex`
- Entity extractor (f02-02) can proceed in parallel — no blocking dependency on this plan
- 33 tests establish coverage baseline for guardrail feature

---
*Phase: f02-vertical-system-sara*
*Completed: 2026-03-04*
