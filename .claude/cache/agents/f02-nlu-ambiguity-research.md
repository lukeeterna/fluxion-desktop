# F02 NLU Ambiguity Research — Sara Voice Agent

**Researched:** 2026-03-04
**Domain:** Italian NLU, verb conjugation gaps, guardrail completeness
**Confidence:** HIGH (all findings derived from reading actual source files)

---

## 1. Bug Analysis — "Ciao Sara sono Gino devo cambiare le gomme si può farlo?"

### Exact Root Cause (VERIFIED from source)

**Step 1 — Guardrail check (italian_regex.py line 730):**
The SALONE guardrail pattern for gomme is:
```python
r"\b(?:cambio\s+gomme|gomme\s+(?:invernali|estivi|nuove)|pneumatici\s+(?:invernali|estivi|nuovi))\b"
```
The input contains "cambiare le gomme" (infinitive verb + article). The pattern requires `cambio\s+gomme` (noun form, no article). The regex does NOT match. **Guardrail passes.**

**Step 2 — L1 intent classification (intent_classifier.py lines 410-421):**
The SPOSTAMENTO patterns include:
```python
r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?"
```
The `?` at the end makes the object **optional**. So `"cambiare"` alone (without `appuntamento`) matches this pattern. Input has "cambiare" → SPOSTAMENTO pattern fires with confidence 0.65.

**Step 3 — E4-S2 handler (orchestrator.py line 791):**
SPOSTAMENTO intent triggers `_handle_reschedule_block`. No `client_id` is known yet, so:
```python
response = "Per spostare un appuntamento, mi può dire il suo nome?"
intent = "reschedule_need_name"
```

### Why Groq was NOT involved
The bug occurs entirely at L1 (pattern-based intent classifier). Groq (L4) is never reached because `pattern_result.confidence = 0.65 >= 0.5` causes early return from `classify_intent()`. This is the correct diagnosis — the input matched a real pattern at L1.

### Summary of failure chain
```
Input: "Ciao Sara sono Gino devo cambiare le gomme si può farlo?"

L0-pre content filter:   PASS (clean)
L0-pre vertical guardrail: MISS — "cambiare le gomme" ≠ "cambio gomme" (verb form not covered)
L0 special commands:     PASS (no match)
L1 exact match:          PASS (no exact match)
L1b italian_regex:       PASS (not conferma/rifiuto/escalation)
L1 pattern_based:        HIT — "cambiare" matches SPOSTAMENTO pattern (object is optional via ?)
                         confidence=0.65 → returned as SPOSTAMENTO
E4-S2 handler:           Fires → "Per spostare un appuntamento, mi può dire il suo nome?"
```

---

## 2. Guardrail Verb-Form Gaps (Full List)

### 2.1 SALONE guardrail gaps

Current SALONE patterns use NOUN forms only. Italian car/gym services are commonly expressed with infinitive verbs:

| Current Pattern (noun) | Missing Verb Forms | Inputs That Leak Through |
|------------------------|-------------------|--------------------------|
| `cambio\s+gomme` | `cambiare\s+(?:le\s+)?gomme`, `fare\s+il\s+cambio\s+gomme` | "devo cambiare le gomme", "voglio fare il cambio gomme" |
| `cambio\s+olio` | `cambiare\s+(?:l'\s*)?olio`, `fare\s+il\s+cambio\s+olio` | "devo cambiare l'olio", "voglio fare il cambio olio" |
| `revisione\s+auto` | `fare\s+la\s+revisione`, `revisionare\s+l'auto`, `portare\s+l'auto\s+per\s+(?:la\s+)?revisione` | "devo fare la revisione", "porto l'auto per la revisione" |
| `tagliando\s+auto` | `fare\s+il\s+tagliando`, `portare\s+(?:la\s+macchina\|l'auto)\s+per\s+il\s+tagliando` | "devo fare il tagliando", "porto la macchina per il tagliando" |
| `personal\s+trainer` | already covered by exact phrase | — |
| `abbonamento\s+(?:mensile\|annuale\|palestra)` | `iscriversi\s+(?:in\s+)?palestra`, `fare\s+l'abbonamento` | "voglio iscrivermi in palestra", "voglio fare l'abbonamento" |
| `corso\s+di\s+(?:yoga\|pilates...)` | already covered by exact phrase | — |
| `visita\s+(?:medica\|specialistica...)` | already covered by exact phrase | — |

### 2.2 Critical gap: "portare la macchina/auto"

These phrases all describe auto services at salone context — NONE are currently blocked:
- "devo portare la macchina dal meccanico"
- "voglio portare l'auto a fare il tagliando"
- "ho la macchina da revisionare"
- "devo far revisionare l'auto"

### 2.3 PALESTRA guardrail gaps

| Current Pattern | Missing Forms |
|-----------------|--------------|
| `cambio\s+gomme` | `cambiare\s+(?:le\s+)?gomme` |
| `revisione\s+auto` | `fare\s+la\s+revisione\s+dell'auto` |
| `tagliando\s+auto` | `fare\s+il\s+tagliando` |

### 2.4 MEDICAL guardrail gaps (same pattern)

Same auto patterns — verb forms missing:
- `fare\s+la\s+revisione` (auto) missing
- `cambiare\s+le\s+gomme` missing

### 2.5 AUTO guardrail gaps

The AUTO guardrail blocks salone/palestra/medical content but has no in-scope false positive risk — the issue is the opposite: salone context must block auto content, not auto blocking its own.

---

## 3. NLU Ambiguity Patterns — Top 10

### 3.1 CRITICAL: "cambiare" → SPOSTAMENTO false positive

**Pattern (intent_classifier.py line 411):**
```python
r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?"
```
The trailing `?` makes the object optional. Any sentence containing "cambiare" (even "cambiare le gomme", "cambiare il colore") will match this pattern.

**Affected sentences at SALONE:**
- "devo cambiare le gomme" → SPOSTAMENTO (WRONG)
- "voglio cambiare il colore" → SPOSTAMENTO (WRONG — should be PRENOTAZIONE for color service)
- "mi potete cambiare l'appuntamento" → SPOSTAMENTO (CORRECT)

**Minimum fix:** Add object requirement — the pattern should require appointment-related object when no other context exists:
```python
# Before: optional object (fires on any "cambiare")
r"(cambia|cambiare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?"
# After: object required OR strong modal context
r"(cambia|cambiare)\s+(l[ao'\u2019]?\s*)?(appuntament|prenotazion|data|ora|orario)"
```

### 3.2 CRITICAL: "cancellare" → CANCELLAZIONE + ambiguous objects

**Pattern (intent_classifier.py line 393):**
```python
r"(posso|voglio|vorrei|devo)\s+(annullare?|cancellare?|disdire?)\s*((il|la|l')?\s*)?(mia?|mio)?\s*(appuntament|prenotazion)?"
```
Again `?` makes the object optional. "Voglio cancellare tutto" or "Posso cancellare?" matches as CANCELLAZIONE.

But note: there is also this more specific pattern first:
```python
r"(annulla|cancella|disdire?)\s+((il|la|l'|lo)\s+)?(mio|mia)?\s*(appuntament|prenotazion|visita)"
```
This one requires the object explicitly. The vulnerable pattern is the second one with modal verbs.

**Affected sentences:**
- "posso cancellare la partita" → CANCELLAZIONE (WRONG)
- "voglio cancellare l'appuntamento" → CANCELLAZIONE (CORRECT)

### 3.3 HIGH: "spostare" without context

**Pattern:** `r"\b(spostare?|anticipare?|posticipare?|rimandare?)\b\s+"` (line 421)
This is a standalone match — "spostare" alone triggers SPOSTAMENTO.

**Affected:**
- "posso spostare la sedia?" → SPOSTAMENTO (WRONG)
- "ho bisogno di spostare un impegno" → SPOSTAMENTO (may be intended but not booking-related)

### 3.4 HIGH: "revisione" at SALONE is in-scope (trattamento!)

The word "revisione" is in the AUTO services list (`italian_regex.py line 282`):
```python
"revisione": ["revisione", "revisione auto", "collaudo", "bollino blu"]
```
But "revisione" is also used generically ("facciamo una revisione del mio look"). The SALONE guardrail blocks only `revisione\s+auto` — standalone "revisione" is NOT blocked. So "devo fare una revisione dell'auto" passes through.

### 3.5 MEDIUM: "fare il tagliando" at SALONE

"Tagliando" alone is in the SALONE `VERTICAL_SERVICES` only under "auto". But the SALONE guardrail requires `tagliando\s+auto` as multi-word. So "devo fare il tagliando" (without "auto") is NOT blocked at salone, meaning it reaches L1 and Groq.

"Tagliando" is not in any SPOSTAMENTO or CANCELLAZIONE pattern, so it will likely fall to L4 Groq. Groq may handle it correctly but this is latency and unpredictability risk.

### 3.6 MEDIUM: "portare la macchina/auto" — no guardrail, no intent match

Sentences like "devo portare l'auto dal meccanico" or "porto la macchina per i freni" have:
- No guardrail match (no noun form of service)
- No intent pattern match at L1

These fall to L4 Groq. Groq will likely give a reasonable response but may not redirect to salone scope.

### 3.7 MEDIUM: "colore" ambiguity at MEDICAL

The MEDICAL guardrail does NOT block "colore della pelle" or "colore dei capelli." The comment in code says:
```
# RULE: Multi-word patterns ONLY — single words risk false positives.
# Example: "colore" alone blocks "colore della pelle" in medical context.
```
This is correct design choice. But "fare il colore" (hair coloring) at a medical office is not blocked. Low impact in practice but worth noting.

### 3.8 MEDIUM: "fare la piega" — SALONE in-scope, but "fare" prefix not in synonyms

The VERTICAL_SERVICES["salone"]["piega"] list contains:
```python
["piega", "messa in piega", "asciugatura", "styling", "acconciatura"]
```
"Fare la piega" would match via substring "piega" in `extract_multi_services`. But "fare la piega alle ginocchia" (bending knees) would also match "piega" — low practical risk.

### 3.9 LOW: "modifica" → SPOSTAMENTO false positive

Pattern: `r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+..."`
"Modifica" can trigger SPOSTAMENTO. "Voglio modificare i miei capelli" → potential false positive.

### 3.10 LOW: TF-IDF semantic classifier reinforcing wrong intent

The semantic classifier (`nlu/semantic_classifier.py`) is a TF-IDF model trained on booking-domain Italian. If the L1 pattern fires first at confidence 0.65, the semantic classifier is never reached. This is by design (L1 has threshold 0.5). But when L1 fires incorrectly, the pipeline exits before semantic correction can help.

---

## 4. Pipeline Injection Point Analysis

### Current pipeline order:
```
L0-pre content filter (italian_regex.check_content)
L0-pre vertical guardrail (italian_regex.check_vertical_guardrail)   ← MISSED HERE
L0-pre vertical entity extraction (entity_extractor.extract_vertical_entities)
L0 special commands (SPECIAL_COMMANDS dict)
L0a WhatsApp FAQ
L0b Advanced NLU (spaCy — only for "mai stato"/"prima volta" patterns)
L0c Sentiment Analysis (escalation, suppressed during booking)
L1 Intent classifier (exact match + pattern + TF-IDF)               ← WRONGLY MATCHED HERE
L2 Booking State Machine
L3 FAQ manager
L4 Groq LLM
```

### Where each fix should be injected

**Fix A (MINIMUM — regex): Extend guardrail patterns to cover verb forms.**
- Location: `italian_regex.py VERTICAL_GUARDRAILS["salone"]`
- Add verb-form patterns alongside noun forms
- Effect: "cambiare le gomme" is caught at L0-pre, never reaches L1
- Latency: ~0ms (pre-compiled regex)
- Risk: Must avoid false positives (e.g., "cambiare l'appuntamento" is valid at salone)

**Fix B (COMPREHENSIVE — L1 pattern hardening): Make SPOSTAMENTO object mandatory.**
- Location: `intent_classifier.py INTENT_PATTERNS[IntentCategory.SPOSTAMENTO]`
- Remove trailing `?` from object group
- Effect: "cambiare" alone no longer triggers SPOSTAMENTO
- Latency: 0ms (no extra processing)
- Risk: Could reduce recall for valid reschedule inputs like "voglio cambiare" (ambiguous)

**Fix C (DEFENSE-IN-DEPTH — context-aware L1): Check vertical context before routing SPOSTAMENTO.**
- Location: `orchestrator.py` E4-S2 handler block (line 791)
- Before routing to reschedule, check if input contains known out-of-scope nouns for the current vertical
- Effect: "cambiare gomme" at salone → redirect instead of reschedule_need_name
- Latency: <1ms (simple set lookup)

**Fix D (FUTURE — semantic guardrail using LLM-cached embeddings).**
- Use sentence embeddings to detect semantic out-of-scope at L0.5
- Not recommended for F02 (latency adds ~50-200ms per call)

### Recommended injection point order for F02:
1. Fix A first (guardrail verb forms) — catches the specific bug with zero latency
2. Fix B second (L1 SPOSTAMENTO hardening) — prevents the class of bugs
3. Fix C third (orchestrator context check) — final defense layer

---

## 5. World-Class Italian Voice Booking Agent — Acceptance Criteria

Based on analysis of the existing system and Italian UX research, "world-class" means:

### 5.1 Guardrail Completeness AC

- AC-G1: ALL noun forms AND verb infinitive forms AND common verb phrases for out-of-scope services are blocked per vertical
- AC-G2: False positive rate = 0 (no in-scope queries are blocked)
- AC-G3: Guardrail response is natural Italian: "Mi occupo del salone, posso aiutarla con taglio, colore o trattamenti?"
- AC-G4: Verified with parametric test matrix: 40+ input variants per service per vertical (10 out-of-scope per service: noun, infinitive, 1st/3rd person, with/without article, with/without "fare", STT artifact)

### 5.2 Intent Classification AC

- AC-I1: SPOSTAMENTO requires explicit booking-domain object OR strong modal context ("voglio spostare il mio appuntamento") — not triggered by generic "cambiare"
- AC-I2: CANCELLAZIONE requires explicit booking-domain object ("l'appuntamento", "la prenotazione", "la visita") — not triggered by generic "cancellare"
- AC-I3: Precision ≥ 95% on a 100-sentence held-out test set per intent class
- AC-I4: No regression: existing 1160 test suite continues to pass

### 5.3 Disambiguation AC

- AC-D1: When "cambiare" is detected in a sentence containing clear out-of-scope content, Sara redirects gracefully in <1 turn
- AC-D2: Sara never asks "Mi può dire il suo nome?" when the user clearly asked about a car service at a hair salon
- AC-D3: When ambiguity cannot be resolved by guardrail or pattern, Sara asks a clarifying question before classifying ("Vuole spostare un appuntamento?")

### 5.4 Response Quality AC

- AC-R1: Redirect responses reference what the vertical CAN do, not just what it cannot: "Non mi occupo di officine. Posso aiutarla con un taglio, una piega o un colore?"
- AC-R2: Redirect responses use formal Italian ("Lei", "la", "si") — no "tu" in redirect
- AC-R3: Max 1 redirect attempt per session topic — if user insists on out-of-scope, escalate to operator

### 5.5 Latency AC (from F03 target)

- AC-L1: Guardrail check adds ≤ 2ms total (pre-compiled regex)
- AC-L2: L1 intent classification adds ≤ 20ms
- AC-L3: No new Groq calls added by F02 fixes
- AC-L4: P95 end-to-end latency ≤ 800ms (F03 target — F02 must not regress below current ~1330ms)

---

## 6. Implementation Recommendations — Ordered by Impact/Effort

### Priority 1 — MUST DO (F02.1, <2h)

**1A. Extend SALONE guardrail with verb forms (italian_regex.py)**

Add to `VERTICAL_GUARDRAILS["salone"]`:
```python
# Verb forms of auto services (MISSING — root cause of bug)
r"\b(?:cambiare|cambio)\s+(?:le\s+)?gomme\b",
r"\b(?:cambiare|cambio)\s+(?:l['']?\s*)?olio\b",
r"\b(?:fare\s+(?:il\s+)?|portare\s+(?:la\s+macchina|l['']auto)\s+(?:a\s+)?(?:fare\s+il\s+)?)\s*(?:tagliando|revisione)\b",
r"\b(?:fare\s+la\s+revisione|revisionare)\b",
r"\bportare\s+(?:la\s+macchina|l['']auto)\s+(?:dal\s+meccanico|per\s+(?:i\s+)?(?:freni|gomme|olio|tagliando|revisione))\b",
```

Also extend PALESTRA and MEDICAL with the same verb forms.

**Acceptance test:** `check_vertical_guardrail("devo cambiare le gomme si può farlo", "salone")` returns `blocked=True`.

**1B. Harden SPOSTAMENTO pattern in intent_classifier.py**

Change SPOSTAMENTO patterns to require object:
```python
# BEFORE (vulnerable — object optional):
r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?",

# AFTER (hardened — object required for generic verbs):
r"(sposta|spostare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?",  # "spostare" can stay flexible
r"(cambia|cambiare|modifica|modificare)\s+(l[ao'\u2019]?\s*)?(appuntament|prenotazion|data|ora|orario)",  # "cambiare" REQUIRES object
```

Keep: `r"(posso|vorrei|devo|voglio)\s+(sposta|cambia|modifica|anticipar|posticipare?|rimandare?)"` — this is safe because it requires modal verb context.

**Acceptance test:** `classify_intent("devo cambiare le gomme").category` = UNKNOWN (not SPOSTAMENTO).

### Priority 2 — SHOULD DO (F02.1, <3h)

**2A. Add 40-variant parametric test for guardrail completeness (test_guardrails.py)**

For each vertical × each service category × each form (noun, infinitive, "fare il ...", "portare per ...", "ho bisogno di ...", STT artifact):

```python
# Example parametric tests to add:
@pytest.mark.parametrize("text", [
    "devo cambiare le gomme",
    "cambiare le gomme invernali",
    "voglio cambiare l'olio",
    "devo fare il cambio olio",
    "porto l'auto per la revisione",
    "fare il tagliando",
    "ho bisogno di una revisione auto",
    "si può farlo gomme",  # STT artifact
    "devo fare i freni",
])
def test_salone_blocks_auto_verbs(text):
    r = check_vertical_guardrail(text, "salone")
    assert r.blocked is True, f"LEAK: '{text}' not blocked at salone"
```

**2B. Add context check in orchestrator E4-S2 handler**

At orchestrator.py line 791, before routing SPOSTAMENTO:
```python
# DEFENSE-IN-DEPTH: If SPOSTAMENTO at salone and input contains auto nouns
# that guardrail missed, redirect instead of reschedule
if intent_result.category == IntentCategory.SPOSTAMENTO:
    if HAS_ITALIAN_REGEX:
        _guardrail_late = check_vertical_guardrail(user_input, self.verticale_id)
        if _guardrail_late.blocked:
            response = _guardrail_late.redirect_response
            intent = f"guardrail_late_{self.verticale_id}"
            layer = ProcessingLayer.L0_SPECIAL
            # Skip the reschedule logic below
```

### Priority 3 — NICE TO HAVE (F02.2 or F03)

**3A. Add NLU clarification question for ambiguous "cambiare"**

When "cambiare" is detected without a clear object, ask:
"Vuole spostare un appuntamento o posso aiutarla con altro?"

This handles the case where a genuine customer wants both (ambiguous input).

**3B. Extend to sub-vertical-aware guardrails**

Based on `sub-verticals-research.md`, some sub-verticals have services that overlap (e.g., "trattamento" exists in salone AND medical). Add sub-vertical context to guardrail checks.

**3C. Log all guardrail misses for continuous improvement**

Add to orchestrator: when L1 fires SPOSTAMENTO/CANCELLAZIONE after guardrail passed, log the input for review. This creates a training corpus for future pattern improvements.

---

## 7. Proposed Phase Scope

### F02.1 (NLU Ambiguity Fix — urgent, same session)

Scope:
1. Extend `VERTICAL_GUARDRAILS` with verb forms for all 4 verticals (1A)
2. Harden SPOSTAMENTO pattern in `intent_classifier.py` (1B)
3. Add parametric tests to `test_guardrails.py` (2A)
4. Add late guardrail check in orchestrator E4-S2 (2B)

Files changed:
- `voice-agent/src/italian_regex.py` — `VERTICAL_GUARDRAILS` dict
- `voice-agent/src/intent_classifier.py` — `INTENT_PATTERNS[SPOSTAMENTO]`
- `voice-agent/src/orchestrator.py` — E4-S2 handler (3 lines)
- `voice-agent/tests/test_guardrails.py` — add ~40 parametric tests

Acceptance criteria:
- `test_guardrails.py` 100% pass including new parametric tests
- Full suite 1160+ PASS / 0 FAIL maintained
- `classify_intent("devo cambiare le gomme").category != SPOSTAMENTO`
- `check_vertical_guardrail("devo cambiare le gomme si può farlo", "salone").blocked == True`

Effort: ~4h (1h regex, 1h L1 fix, 1h tests, 1h verify)

### F02.2 (Already in progress per existing PLANs)

Based on `.planning/phases/f02-vertical-system-sara/` existing plans, this continues the guardrail + entity extractor work. The F02.1 fixes above are prerequisite patches that should land first.

### F03 (Latency — separate, future)

The latency target (<800ms P95) is separate from NLU ambiguity. F02 fixes add ~0ms latency (pre-compiled regex). Do not conflate F02 scope with F03.

---

## 8. Complete List of Verb-Form Gaps by Vertical

### SALONE — all missing patterns

```
Input phrase              | Leaks through guardrail? | Root cause
--------------------------+--------------------------+----------------------------------
"cambiare le gomme"       | YES (BUG)                | Missing infinitive form
"cambiare l'olio"         | YES                      | Missing infinitive form
"fare il cambio olio"     | YES                      | Missing "fare il X" form
"fare il cambio gomme"    | YES                      | Missing "fare il X" form
"fare il tagliando"       | YES                      | Missing "fare il X" form
"fare la revisione"       | YES                      | Missing "fare la X" form
"portare l'auto per..."   | YES                      | No "portare auto" pattern
"devo far riparare..."    | YES                      | No "far + infinitive" pattern
"iscrivermi in palestra"  | YES                      | Missing "iscriversi" verb
"fare l'abbonamento"      | YES                      | Missing "fare l'abbonamento"
"yoga domani"             | NO — not present as noun  | "yoga" standalone not blocked
```

### PALESTRA — missing verb forms (mirrors salone for auto)

```
"cambiare le gomme"       | YES                      | Same as salone
"cambiare l'olio"         | YES                      | Same as salone
"fare il tagliando"       | YES                      | Same as salone
"taglio capelli domani"   | NO — blocked             | "taglio capelli" is covered
"fare la tinta"           | YES                      | "tinta capelli" required, not "fare la tinta"
```

### MEDICAL — missing verb forms

```
"cambiare le gomme"       | YES                      | Same gap
"fare il tagliando"       | YES                      | Same gap
"fare la manicure"        | NO — blocked             | "fare (la|una?) manicure" is covered (line 770)
"fare la ceretta gambe"   | NO — blocked             | Covered (line 771)
```

### AUTO — no in-scope false positive risk from verb forms

Auto correctly blocks salone/palestra/medical patterns. No verb-form gaps identified for auto blocking other verticals (auto ALLOWS its own services, including verb forms via `service_synonyms`).

---

## Sources

All findings are HIGH confidence — derived directly from reading production source files:

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/italian_regex.py` — VERTICAL_GUARDRAILS (lines 726-849)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/intent_classifier.py` — INTENT_PATTERNS SPOSTAMENTO (lines 409-421), pattern_based_intent (lines 475-547)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py` — process() pipeline order (lines 505-915), E4-S2 handler (lines 791-855)
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_guardrails.py` — existing test coverage
- `/Volumes/MontereyT7/FLUXION/voice-agent/tests/test_multi_verticale.py` — cross-vertical isolation tests

**Research date:** 2026-03-04
**Valid until:** 2026-04-03 (stable codebase, 30-day validity)
