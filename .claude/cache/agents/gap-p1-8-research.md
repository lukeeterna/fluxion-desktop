# GAP-P1-8: Multi-Operator Selection — CoVe 2026 Research

> Generated: 2026-03-13 | Agent: research subagent B (codebase analysis)

---

## 1. Gold Standard 2026 — Competitor Analysis

### Fresha / Mindbody Pattern
Both platforms support "any of these staff" in booking flows:
- Web/app: multi-select checkboxes for staff preference
- Voice/chatbot: capture list → filter availability → present first match
- Key insight: the system stores a **preference list** (ordered or unordered), attempts
  each in sequence against availability, and books the first match. The user is
  informed *which* operator was booked, not just "someone was found."

### Retell / Vapi Voice Pattern (2026)
Modern voice booking agents handle conjunctions and disjunctions:
- **Disjunction** ("Mario o Giulia") → try Mario first, then Giulia
- **Conjunction** ("sia Marco che Laura") → same semantics as disjunction for booking
  (can't book both; pick first available)
- **Indifference** ("indifferente tra Marco e Laura") → try in listed order
- **Fallback** ("Marco o chiunque") → try Marco, then any available operator

### Gold Standard Decision
Store `operator_names: List[str]` (ordered list of preferences) on `BookingContext`.
During availability lookup, iterate the list and return the first available slot.
This is minimal change, fully backward compatible, and matches enterprise patterns.

---

## 2. Codebase Analysis

### Current Single-Operator Flow

**entity_extractor.py**
- `ExtractedOperator` dataclass: `name: str`, `original_text: str`, `confidence: float`
- `extract_operator(text)` → `Optional[ExtractedOperator]` — single name only
- `ExtractionResult.operator: Optional[ExtractedOperator]` — single field
- `ExtractionResult.operators` — does NOT exist yet
- `extract_entities(text)` at line 1663: `result.operator = extract_operator(text)`

**booking_state_machine.py**
- `BookingContext.operator_name: Optional[str]` — single string
- `BookingContext.operator_id: Optional[str]` — resolved after DB lookup
- `BookingContext.operator_requested: bool`
- `BookingContext.operator_gender_preference: Optional[str]` — "F"/"M"

Key write sites in BSM:
1. Line 990-992: `_update_context_from_extraction()` — `extracted.operator.name` → `ctx.operator_name`
2. Line 1030: `_apply_entity_update()` field "operator" → `ctx.operator_name`
3. Line 2303: `_handle_waiting_operator()` — uses `extract_name()`, not `extract_operator()`
4. Line 2345: `_extract_level1_entities()` — `extract_operator(user_lower).name` → `entities["operator"]`
5. Line 2779: correction handler → `ctx.operator_name = sanitize_name(valore)`

Key read sites:
- `ctx.operator_name` used in `get_summary()`, `to_dict()`, booking payload (lines 2653, 2716)
- `needs_db_lookup` with `lookup_type="operator"` and `lookup_params={"name": name.name, ...}`

### Gap
`extract_operator()` returns the first matched name only. Phrases like "Mario o Giulia"
would extract "Mario" (first match) and silently discard "Giulia". The BSM has no concept
of an ordered preference list.

---

## 3. Proposed Architecture — Minimal Change, Backward Compatible

### 3.1 New function in entity_extractor.py

```python
@dataclass
class ExtractedOperatorList:
    """Multiple operator preferences from Italian text."""
    names: List[str]           # Ordered list, first = highest preference
    is_any: bool               # True if "chiunque"/"qualsiasi" fallback included
    original_text: str
    confidence: float

def extract_operators_multi(text: str) -> Optional[ExtractedOperatorList]:
    """
    Extract multiple operator preferences from Italian.
    Returns None if no multi-operator pattern found.
    Caller should fall back to extract_operator() if this returns None.

    Handles:
    - "voglio Mario o Giulia"
    - "sia Marco che Laura"
    - "Marco, Giulia o chiunque"
    - "con Marco oppure con Luca"
    - "indifferente tra Marco e Laura"
    """
```

**Why a new function (not modifying `extract_operator()`):**
- `extract_operator()` is called in 4 separate places in the BSM + tests
- Changing its return type to a list breaks all callers
- New function = zero regression risk; old function untouched

### 3.2 Add `operators` field to ExtractionResult

```python
@dataclass
class ExtractionResult:
    ...
    operator: Optional[ExtractedOperator] = None        # UNCHANGED — backward compat
    operators: List[ExtractedOperator] = field(default_factory=list)  # NEW — multi
```

In `extract_entities()`, populate both:
```python
# Try multi first
multi = extract_operators_multi(text)
if multi and len(multi.names) > 1:
    result.operators = [ExtractedOperator(n, multi.original_text, multi.confidence)
                        for n in multi.names]
    result.operator = result.operators[0]   # backward compat: first = primary
else:
    result.operator = extract_operator(text)
    if result.operator:
        result.operators = [result.operator]
```

### 3.3 Add `operator_names` to BookingContext

```python
# In BookingContext dataclass — NEW field alongside operator_name
operator_names: List[str] = field(default_factory=list)  # ordered preference list
```

`operator_name` (single string) is kept unchanged for all existing read sites
(get_summary, to_dict, booking payload). It holds the *resolved* operator after
availability check, or the first preference before resolution.

### 3.4 BSM — _update_context_from_extraction() change (line 989-992)

Current:
```python
if extracted.operator and (force_update or not self.context.operator_name):
    self.context.operator_name = extracted.operator.name
    self.context.operator_requested = True
```

New (minimal addition):
```python
if extracted.operators and (force_update or not self.context.operator_name):
    self.context.operator_names = [op.name for op in extracted.operators]
    self.context.operator_name = extracted.operators[0].name   # primary
    self.context.operator_requested = True
elif extracted.operator and (force_update or not self.context.operator_name):
    self.context.operator_names = [extracted.operator.name]
    self.context.operator_name = extracted.operator.name
    self.context.operator_requested = True
```

### 3.5 BSM — _handle_waiting_operator() change (line 2287)

After extracting name(s), also check for multi via `extract_operators_multi()`:
```python
# Try multi-operator first
multi = extract_operators_multi(text)
if multi and len(multi.names) > 1:
    self.context.operator_names = multi.names
    self.context.operator_name = multi.names[0]
    self.context.operator_requested = True
    self.context.state = BookingState.CONFIRMING
    return StateMachineResult(
        next_state=BookingState.CONFIRMING,
        response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary()),
        needs_db_lookup=True,
        lookup_type="operator_multi",
        lookup_params={"names": multi.names, "date": self.context.date, "time": self.context.time}
    )

# Try single operator (existing path unchanged)
name = extract_name(text)
if name:
    ...
```

### 3.6 Availability lookup in orchestrator.py

When `lookup_type="operator_multi"`, iterate `names` list and return first available:
```python
async def _resolve_operator_multi(self, names: List[str], date: str, time: str) -> Optional[str]:
    """Try each operator in order; return first available name."""
    for name in names:
        op = await self._find_operator(name)
        if op and await self._check_availability(op["id"], date, time):
            return name
    return None  # None → book with any available
```

---

## 4. Regex Patterns — Italian Multi-Operator

### Pattern taxonomy

| Pattern type | Example | Regex |
|---|---|---|
| Disjunction with "o" | "Mario o Giulia" | `NAME\s+o\s+NAME` |
| Disjunction with "oppure" | "Marco oppure Luca" | `NAME\s+oppure\s+NAME` |
| Conjunction "sia...che" | "sia Marco che Laura" | `sia\s+NAME\s+che\s+NAME` |
| Enumeration with comma | "Mario, Giulia o Laura" | `NAME(?:,\s*NAME)+\s+o\s+NAME` |
| Indifference | "indifferente tra Marco e Laura" | `indifferente\s+tra\s+NAME\s+e\s+NAME` |
| Fallback "o chiunque" | "Marco o chiunque" | `NAME\s+o\s+(?:chiunque|qualsiasi|qualunque)` |
| "voglio X o Y" | "voglio Mario o Giulia" | `(?:voglio|vorrei)\s+NAME(?:\s+o\s+NAME)+` |
| "con X oppure con Y" | "con Marco oppure con Luca" | `con\s+NAME(?:\s+oppure\s+con\s+NAME)+` |

### Full regex implementation

```python
import re
from typing import List, Optional, Tuple

# Name token: capitalized Italian name (handles accented chars)
_NAME_TOKEN = r'[A-ZÀ-Ù][a-zà-ù]+(?:\s+[A-ZÀ-Ù][a-zà-ù]+)?'

MULTI_OP_PATTERNS: List[Tuple[str, bool]] = [
    # "sia Marco che Laura" — unordered conjunction
    (r'sia\s+(' + _NAME_TOKEN + r')\s+che\s+(' + _NAME_TOKEN + r')', False),
    # "indifferente tra Marco e Laura"
    (r'indifferente\s+tra\s+(' + _NAME_TOKEN + r')\s+e\s+(' + _NAME_TOKEN + r')', False),
    # "Marco oppure Luca" / "con Marco oppure con Luca"
    (r'(?:con\s+)?(' + _NAME_TOKEN + r')\s+oppure\s+(?:con\s+)?(' + _NAME_TOKEN + r')', False),
    # "voglio/vorrei Mario o Giulia"
    (r'(?:voglio|vorrei|preferisco)\s+(' + _NAME_TOKEN + r')(?:\s*,\s*(' + _NAME_TOKEN + r'))*\s+o\s+(' + _NAME_TOKEN + r')', False),
    # "Mario o Giulia" / "Marco, Giulia o chiunque"
    (r'(' + _NAME_TOKEN + r')(?:\s*,\s*' + _NAME_TOKEN + r')*\s+o\s+(' + _NAME_TOKEN + r'|chiunque|qualsiasi|qualunque)', True),
]

ANY_KEYWORDS = {'chiunque', 'qualsiasi', 'qualunque', 'chiunque sia disponibile'}
```

### Simpler implementation strategy

Rather than complex multi-group regex, use a two-step approach:
1. Detect if the text matches a multi-operator trigger pattern (any of the above)
2. If yes, extract all `_NAME_TOKEN` matches from the phrase + detect `is_any`

```python
_MULTI_TRIGGERS = [
    r'\bsia\b.+\bche\b',
    r'\bindifferente tra\b',
    r'\boppure\b',
    r'\bo\s+(?:chiunque|qualsiasi)',
    # Two or more capitalized names with "o" or "," between them
    r'[A-ZÀ-Ù][a-zà-ù]+\s+[oe]\s+[A-ZÀ-Ù][a-zà-ù]+',
    r'[A-ZÀ-Ù][a-zà-ù]+,\s*[A-ZÀ-Ù][a-zà-ù]+',
]

def extract_operators_multi(text: str) -> Optional[ExtractedOperatorList]:
    text_stripped = text.strip()

    # Step 1: check triggers
    trigger_matched = any(re.search(t, text_stripped, re.IGNORECASE)
                          for t in _MULTI_TRIGGERS)
    if not trigger_matched:
        return None

    # Step 2: extract all name tokens
    name_pattern = r'\b([A-ZÀ-Ù][a-zà-ù]+(?:\s+[A-ZÀ-Ù][a-zà-ù]+)?)\b'
    names = re.findall(name_pattern, text_stripped)

    # Step 3: filter blacklisted words (reuse OPERATOR_BLACKLIST)
    names = [n for n in names if n.lower() not in OPERATOR_BLACKLIST]

    if len(names) < 2:
        return None  # not actually multi — fall through to extract_operator()

    # Step 4: detect "any" fallback
    is_any = bool(re.search(r'\b(chiunque|qualsiasi|qualunque)\b', text_stripped, re.IGNORECASE))

    return ExtractedOperatorList(
        names=names,
        is_any=is_any,
        original_text=text_stripped,
        confidence=0.85
    )
```

**Why two-step:** avoids complex multi-group regex with optional captures that are
fragile in Python 3.9 (no `re` improvements from 3.11+). Simple trigger + findall
is easier to maintain and test.

---

## 5. Response Templates

Add to `TEMPLATES` dict in booking_state_machine.py:
```python
"confirm_operator_multi": "Ho capito! Cercherò disponibilità con {names}. {summary_rest}",
"operator_multi_resolved": "Ho trovato {name} disponibile. {confirm_text}",
"operator_multi_none": "Purtroppo nessuno tra {names} è disponibile in quel momento. Vuole scegliere un altro orario?",
```

get_summary() update — show list when `operator_names` has 2+ entries:
```python
if len(self.operator_names) > 1:
    parts.append(f"con {' o '.join(self.operator_names)}")
elif self.operator_name:
    parts.append(f"con {self.operator_name}")
```

---

## 6. Test Cases (10 cases)

### entity_extractor tests

```python
# TC-1: simple disjunction
def test_multi_op_o():
    result = extract_operators_multi("voglio Mario o Giulia")
    assert result is not None
    assert result.names == ["Mario", "Giulia"]
    assert result.is_any is False

# TC-2: sia...che conjunction
def test_multi_op_sia_che():
    result = extract_operators_multi("sia Marco che Laura")
    assert result is not None
    assert "Marco" in result.names and "Laura" in result.names

# TC-3: oppure
def test_multi_op_oppure():
    result = extract_operators_multi("con Marco oppure con Luca")
    assert result is not None
    assert result.names == ["Marco", "Luca"]

# TC-4: indifferente tra
def test_multi_op_indifferente():
    result = extract_operators_multi("indifferente tra Marco e Laura")
    assert result is not None
    assert "Marco" in result.names and "Laura" in result.names

# TC-5: fallback chiunque
def test_multi_op_chiunque():
    result = extract_operators_multi("Marco o chiunque")
    assert result is not None
    assert result.names == ["Marco"]
    assert result.is_any is True

# TC-6: comma-separated list
def test_multi_op_comma():
    result = extract_operators_multi("Marco, Giulia o Laura")
    assert result is not None
    assert len(result.names) == 3

# TC-7: single name → falls through to None
def test_multi_op_single_returns_none():
    result = extract_operators_multi("con Marco")
    assert result is None   # caller uses extract_operator() instead

# TC-8: no name → None
def test_multi_op_no_name():
    result = extract_operators_multi("voglio un appuntamento")
    assert result is None

# TC-9: backward compat — extract_entities returns operator set to first name
def test_extract_entities_operators_backward_compat():
    result = extract_entities("vorrei Mario o Giulia per domani alle 15")
    assert result.operator is not None
    assert result.operator.name == "Mario"
    assert len(result.operators) == 2
    assert result.operators[1].name == "Giulia"

# TC-10: BSM integration — operator_names populated
def test_bsm_multi_operator_context():
    bsm = BookingStateMachine()
    bsm.process("Ciao, vorrei un taglio domani con Mario o Giulia")
    assert bsm.context.operator_names == ["Mario", "Giulia"]
    assert bsm.context.operator_name == "Mario"  # primary
    assert bsm.context.operator_requested is True
```

---

## 7. Files to Modify

| File | Change | Lines |
|------|--------|-------|
| `entity_extractor.py` | Add `ExtractedOperatorList` dataclass after `ExtractedOperator` (line ~170) | +8 lines |
| `entity_extractor.py` | Add `_MULTI_TRIGGERS` list + `extract_operators_multi()` function after `extract_operator()` (after line 1188) | +50 lines |
| `entity_extractor.py` | Add `operators: List[ExtractedOperator]` field to `ExtractionResult` (after line 1577) | +2 lines |
| `entity_extractor.py` | Update `extract_entities()` to call `extract_operators_multi()` and populate both `operator` and `operators` (line 1663) | ~8 lines changed |
| `booking_state_machine.py` | Add `operator_names: List[str]` to `BookingContext` dataclass (after line 148) | +1 line |
| `booking_state_machine.py` | Update `_update_context_from_extraction()` to populate `operator_names` (line 989-992) | ~8 lines changed |
| `booking_state_machine.py` | Update `_handle_waiting_operator()` to check multi first (line 2287) | +15 lines |
| `booking_state_machine.py` | Update `get_summary()` to show list when `operator_names > 1` (line 233) | ~4 lines changed |
| `tests/test_entity_extractor.py` | Add TC-1 through TC-9 above | +70 lines |
| `tests/test_booking_state_machine.py` | Add TC-10 + BSM integration tests | +30 lines |

**No changes** to:
- `extract_operator()` (untouched)
- `extract_generic_operator()` (untouched)
- All existing BSM state handlers except `_handle_waiting_operator()` and `_update_context_from_extraction()`
- Rust/Tauri layer (operator_name string field unchanged in booking payload)
- DB schema (no migration needed — operator_names is in-memory only during booking flow; resolved to `operator_name` before save)

---

## 8. Acceptance Criteria (Measurable)

| # | Criterion | How to verify |
|---|-----------|---------------|
| AC-1 | `extract_operators_multi("voglio Mario o Giulia")` returns list with both names | pytest TC-1 |
| AC-2 | `extract_operators_multi("sia Marco che Laura")` returns list with both names | pytest TC-2 |
| AC-3 | `extract_operators_multi("con Marco oppure con Luca")` returns list with both names | pytest TC-3 |
| AC-4 | `extract_operators_multi("indifferente tra Marco e Laura")` returns list | pytest TC-4 |
| AC-5 | `extract_operators_multi("Marco o chiunque")` has `is_any=True` | pytest TC-5 |
| AC-6 | Single name input returns `None` from `extract_operators_multi()` | pytest TC-7 |
| AC-7 | `extract_entities()` backward compat: `result.operator.name == names[0]` when multi detected | pytest TC-9 |
| AC-8 | BSM `operator_names` populated as list after multi-op phrase | pytest TC-10 |
| AC-9 | `extract_operator()` function signature unchanged (no regression) | All existing operator tests pass |
| AC-10 | `npm run type-check` equivalent: `mypy` / existing pytest suite: 0 new failures | `pytest tests/ -v` on iMac |

---

## 9. Edge Cases & Risks

| Risk | Mitigation |
|------|-----------|
| "Marco e Laura sono disponibili?" — question, not preference | Trigger `_MULTI_TRIGGERS` won't fire unless wrapped in preference context ("voglio", "con", "sia...che") |
| Names in OPERATOR_BLACKLIST accidentally included | Reuse existing `OPERATOR_BLACKLIST` in step 3 of `extract_operators_multi()` |
| `operator_names` not serialized in `to_dict()` | Not required: `operator_name` (primary) already in payload; `operator_names` is ephemeral during booking |
| `operator_names` field breaks `BookingContext` `__post_init__` / JSON serialization | Use `field(default_factory=list)` — same pattern as `services`, `alternative_slots` |
| Capitalized false positives ("Domani Mattina") | Name pattern `[A-ZÀ-Ù][a-zà-ù]+` + trigger required → low false positive rate |
| 3+ names: "Mario, Giulia e Luca" | `re.findall` on name pattern captures all 3; comma trigger fires |

---

## 10. Implementation Order (Atomic Commits)

1. **Commit 1**: `feat(voice): add ExtractedOperatorList dataclass + extract_operators_multi()` — entity_extractor.py only
2. **Commit 2**: `feat(voice): ExtractionResult.operators field + extract_entities() multi-op support` — entity_extractor.py only
3. **Commit 3**: `feat(voice): BookingContext.operator_names + BSM multi-op handling` — booking_state_machine.py only
4. **Commit 4**: `test(voice): GAP-P1-8 multi-operator extraction tests` — tests only

Each commit independently testable. Commits 1-2 can be merged into one if desired.
