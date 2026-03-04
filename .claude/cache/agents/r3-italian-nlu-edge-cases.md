# R3: Italian NLU Deep Analysis — All Edge Cases
# Sara Voice Agent — FLUXION

**Generated:** 2026-03-04
**Method:** Exhaustive linguistic analysis against production source code
**Files analyzed:**
- `voice-agent/src/italian_regex.py` — L0 patterns (850 lines)
- `voice-agent/src/intent_classifier.py` — L1 intent patterns (550 lines)
- `voice-agent/src/disambiguation_handler.py` — phonetic matching (840 lines)
- `voice-agent/src/entity_extractor.py` — entity extraction (700+ lines)
- `.claude/cache/agents/f02-nlu-comprehensive-patterns.md` — F02 prior research

**Reference date for analysis:** 2026-03-04 (actual production date)

---

## Legend

- **Sara status:** ✅ handled correctly | ⚠️ partially handled / risky | ❌ not handled / fails
- **Effort:** S = <2h | M = 2-8h | L = >8h
- **Fix approach:** regex | fsm | prompt | feature | wontfix

---

## CATEGORY 1: Verb Morphology Gaps

### 1.1 Booking Verbs — Complete Italian Conjugation Matrix

| Verb | Forms Sara sees | Forms Sara misses | Status | Fix |
|------|----------------|-------------------|--------|-----|
| prenotare | prenota, prenotare, prenotarsi, prenoto | prenotiamo, prenoterei, avrei prenotato, stavo prenotando | ⚠️ | regex S |
| fissare | fissare, fissa | fisserei, avrei fissato, fissato già? | ⚠️ | regex S |
| prendere appuntamento | prendere un appuntamento | avrei preso, ho già preso, voglio prenderne uno | ⚠️ | regex S |
| disdire | disdire, disdico | disdicono, l'ho disdetto, l'avevo disdetta | ⚠️ | regex S |
| cancellare | cancellare, cancella | l'ho cancellato, ho cancellato, cancellerei | ⚠️ | regex S |
| spostare | spostare, sposta | l'ho spostato, avevo spostato, l'avrei spostato | ⚠️ | regex S |
| cambiare | cambiare, cambia | cambio (noun!), l'avevo cambiata, cambierei | ❌ | regex M |
| modificare | modificare, modifica | modifico, ho modificato | ⚠️ | regex S |
| rimandare | rimandare, rimanda | rimanderei, avrei rimandato | ❌ | regex S |
| anticipare | anticipare, anticipa | anticiperei, l'ho anticipato | ⚠️ | regex S |
| posticipare | posticipare, posticipa | posticiperei | ❌ | regex S |

**Key missing patterns in `intent_classifier.py` L1:**

```python
# MISSING: passato prossimo forms
r"(ho|ho\s+già)\s+(prenotat[oa]|fissato|canc[ei]llato|spostato)"
# MISSING: condizionale (polite Italian)
r"(prenoter[ei]i|fisserei|cancellerei|sposterei)"
# MISSING: gerundio (ongoing)
r"(sto\s+(?:cercando\s+di\s+)?prenotar|stavo\s+prenotando)"
# MISSING: participio with auxiliary
r"(avevo|avrei)\s+(prenotat[oa]|fissato|spostato|cancellatoo)"
```

**Priority edge cases:**
- "l'ho cancellato" → ambiguous: cancellation confirmed or requesting? ❌
- "stavo prenotando" → interrupted booking flow ❌
- "avrei voluto prenotare" → conditional intent (soft) ⚠️
- "prenoterei per giovedì" → polite booking intent (very common) ❌

### 1.2 Salone Service Verbs

| Expression | Sara handles? | Notes |
|-----------|--------------|-------|
| "mi faccia un taglio" | ✅ | "taglio" in synonyms |
| "mi tagli i capelli" | ❌ | verb form not in pattern |
| "tagliameli corti" | ❌ | reflexive + adv combination |
| "li voglio corti" | ❌ | implicit service (haircut reference) |
| "voglio tingerli" | ❌ | reflexive pronoun |
| "li colori di rosso" | ❌ | verb form, direct object pronoun |
| "faccia la piega" | ✅ | "piega" in synonyms |
| "mi sistemi" | ❌ | generic "sistemare" = any service |
| "voglio farmi la barba" | ❌ | reflexive "farsi" |
| "sistemami i baffi" | ❌ | "baffi" not in synonym list |
| "sfoltisca un po'" | ❌ | "sfoltire" not in pattern |
| "accorciatemeli un po'" | ❌ | double pronoun clitic |

**Missing synonym: "baffi"** — should be added to `barba` synonyms in `VERTICAL_SERVICES["salone"]`.

### 1.3 Palestra Service Verbs

| Expression | Sara handles? | Notes |
|-----------|--------------|-------|
| "voglio iscrivermi" | ⚠️ | "iscrizione" in synonyms but not "iscrivermi" |
| "mi voglio abbonare" | ⚠️ | "abbonamento" in synonyms but not verb form |
| "voglio allenarmi" | ❌ | not in any pattern |
| "ho bisogno di un personal" | ⚠️ | "personal trainer" but not "personal" alone |
| "voglio fare pilates" | ✅ | "pilates" in synonyms |
| "partecipo alla lezione di" | ❌ | "partecipare" missing |
| "prenoto la classe" | ✅ | "classe" in synonyms |
| "mi metto in lista per lo spinning" | ⚠️ | waitlist + service combo — partial |

### 1.4 Medical Service Verbs

| Expression | Sara handles? | Notes |
|-----------|--------------|-------|
| "voglio visitarmi" | ❌ | reflexive form missing |
| "farmi visitare" | ❌ | causative missing |
| "ho bisogno di farmi vedere" | ❌ | "farsi vedere" = appointment request |
| "devo fare delle analisi" | ⚠️ | "analisi" in synonyms but "fare delle" prefix missing |
| "mi prescriva qualcosa" | ❌ | prescrivere = requesting a prescription |
| "ho bisogno del ricettario" | ❌ | "ricettario" not in patterns |
| "devo fare il vaccino" | ✅ | "vaccino" in synonyms |
| "mi serve il certificato per la palestra" | ⚠️ | partial — "certificato" recognized but "per la palestra" context lost |

### 1.5 Auto Service Verbs

| Expression | Sara handles? | Notes |
|-----------|--------------|-------|
| "fatemi il tagliando" | ✅ | "tagliando" in synonyms |
| "ho la macchina che non parte" | ✅ | "non parte" in synonyms |
| "mi si è accesa la spia" | ⚠️ | "spia" in synonyms but "mi si è accesa" construction missing |
| "le gomme sono lisce" | ❌ | "lisce" = worn tyres, not in patterns |
| "ho bisogno delle gomme invernali" | ✅ | via "gomme invernali" |
| "portarla a fare il tagliando" | ❌ | causative "portare a fare" missing |
| "faccio la revisione" | ✅ | "revisione" in synonyms |

**CRITICAL GAP for auto:** "gomme lisce" / "pneumatici consumati" / "freni che stridono" — symptom descriptions not in service synonyms.

---

## CATEGORY 2: Regional Expressions & Dialettismi

### 2.1 Formality Register Variants

**Verb person variants (Lei/tu/voi — all used in real calls):**

| Expression | Region | Sara handles? | Notes |
|-----------|--------|--------------|-------|
| "mi può fare un taglio?" | Standard (Lei) | ✅ | "mi fa" → PRENOTAZIONE via pattern |
| "mi fai un taglio?" | North/informal | ✅ | "mi fa" pattern |
| "mi fate un taglio?" | Formal plural | ❌ | "mi fate" missing |
| "faccia pure" | Tuscany/formal | ❌ | "faccia" = Lei subjunctive, not in patterns |
| "mi si può fare?" | Regional impersonal | ❌ | |
| "si può avere?" | Formal alternative | ❌ | |

### 2.2 Booking Synonyms by Region

| Canonical | Regional variant | Region | Status |
|-----------|-----------------|--------|--------|
| prenotare | fissare un appuntamento | general | ✅ |
| prenotare | prendere un appuntamento | North | ✅ |
| prenotare | mettersi d'accordo | South/informal | ❌ |
| prenotare | convenire un'ora | Tuscany | ❌ |
| prenotare | accordarsi | Center/South | ❌ |
| prenotare | fare una prenotazione | general | ✅ |
| disponibilità | posto | South ("c'è posto?") | ❌ |
| disponibilità | libero ("è libero giovedì?") | general | ❌ |
| disponibilità | buco ("avete un buco?") | informal | ❌ |
| disponibilità | posto libero | general | ❌ |

**Missing patterns in INTENT_PATTERNS[PRENOTAZIONE]:**
```python
r"c['è]\s+posto\b",                        # "c'è posto venerdì?"
r"\bè\s+liber[oa]\s+(?:giovedì|lunedì|...)", # "è libero giovedì?"
r"avete\s+(?:un\s+)?buco",                  # "avete un buco nel pomeriggio?"
r"avete\s+(?:posto|disponibilità|spazio)",   # general availability
r"(mettersi|metterci)\s+d'accordo",          # Southern idiom
r"\baccordarsi\b",                           # Tuscan/Center
```

### 2.3 Diminutivi Regionali (South Italian)

These are real inputs from Southern clients — current regex does NOT handle them:

| Diminutive | Meaning | Sara handles? | Fix |
|-----------|---------|--------------|-----|
| "appuntamentino" | appointment (affectionate) | ❌ | regex: `appuntament(?:ino)?` |
| "tagliettino" | small trim | ❌ | regex: `tagliett(?:ino)?` |
| "spuntatina" | light trim | ✅ | already in salone synonyms |
| "tagliettino" | affectionate haircut | ❌ | |
| "pieguccia" | quick blowdry | ❌ | |
| "visitina" | quick medical visit | ❌ | |
| "controllino" | quick checkup | ❌ | |
| "revisionina" | quick car checkup | ❌ | |

**Fix approach:** In `entity_extractor.py`, extend synonym matching to strip common diminutive suffixes: `-ino`, `-ina`, `-etto`, `-ella`, `-uccia` before matching against service synonyms.

### 2.4 Northern vs Southern Waitlist Language

| Expression | Region | Status |
|-----------|--------|--------|
| "mi metto in lista" | North | ✅ waitlist pattern |
| "mi metto in coda" | North/Center | ❌ |
| "mi scrivo" | South | ❌ |
| "segnatemi" | general | ❌ |
| "tenetemi in mente" | informal | ❌ |
| "mettete da parte" | informal | ❌ |

**Missing in INTENT_PATTERNS[WAITLIST]:**
```python
r"mett(?:ermi|imi)\s+in\s+coda",
r"\bsegnat(?:emi|ami|evi)\b",
r"\bscrivet(?:emi|ami)\b",
r"tenete(?:mi)?\s+(?:in\s+mente|da\s+parte)",
```

---

## CATEGORY 3: Negation Patterns

### 3.1 Current State Analysis

Sara's negation handling is concentrated in:
- `RIFIUTO_PATTERNS` (italian_regex.py line 119) — standalone "no"
- `is_rifiuto()` — returns (True, confidence)
- FSM: L0 rifiuto result can override intent in orchestrator

**The fundamental gap:** Negation is treated as a binary signal (`is_rifiuto=True`), but Italian negation modifies the main verb and its semantics.

### 3.2 Critical Negation Failure Cases

| Input | Sara interprets as | Should be | Status | Priority |
|-------|-------------------|-----------|--------|----------|
| "non voglio cancellare" | ⚠️ RIFIUTO → may cancel | keep appointment | ❌ | CRITICAL |
| "non ho detto giovedì" | UNKNOWN | date correction | ❌ | HIGH |
| "no aspetti" | RIFIUTO → closes? | pause, rethink | ❌ | HIGH |
| "non è quello che intendevo" | MISUNDERSTANDING (if detected) | full redo | ⚠️ | MEDIUM |
| "non mi cancelli" | ❌ not parsed | don't cancel | ❌ | CRITICAL |
| "non sposti" | ❌ | keep original | ❌ | HIGH |
| "non ancora" | RIFIUTO | wait / not now | ⚠️ | MEDIUM |
| "non sono sicuro" | RIFIUTO | ask again | ⚠️ | MEDIUM |
| "non è per me, è per mia moglie" | UNKNOWN | booking for other | ❌ | MEDIUM |

**Root cause: `is_rifiuto()` matches `\bnon\s+(?:voglio|desidero|intendo)\b`** — "non voglio cancellare" contains "non voglio" and triggers is_rifiuto=True. But in the FSM, if the current state is `ASKING_CLOSE_CONFIRMATION`, a rifiuto correctly means "don't close". The bug is that the pattern fires in booking context where "non voglio cancellare" should be parsed as a negated CANCELLAZIONE.

**Fix for "non voglio cancellare":**
```python
# In orchestrator.py — before processing L0 rifiuto:
# If rifiuto AND contains cancell/annull/disdir → negate the nested intent
# i.e., "non voglio cancellare" = "voglio NON cancellare" = keep booking
import re
_NEGATED_CANCEL = re.compile(
    r"\bnon\s+(?:voglio|intendo|voglio|desidero)\s+(?:cancellare?|annullare?|disdire?)\b",
    re.IGNORECASE
)
# If matched → treat as CONFERMA (confirm keeping the booking)
```

### 3.3 "no aspetti" Pattern

This is one of the most common real-world inputs. A customer mid-booking says "no aspetti" (= "wait, hold on"). Sara currently treats "no" as RIFIUTO and may close the booking flow.

**Current handling:** "aspetti" is in CORRECTION_PATTERNS[WAIT] but "no aspetti" triggers is_rifiuto FIRST (before corrections), overriding the wait signal.

**Fix:** In L0 pipeline execution order (`prefilter()`), check WAIT correction BEFORE rifiuto for "no aspetti" patterns:
```python
# Priority: "no aspetti" / "no no aspetti" → WAIT, not RIFIUTO
_NO_ASPETTI = re.compile(r"^no\s+(?:no\s+)?aspett[ia]", re.IGNORECASE)
```

### 3.4 Date Corrections with Negation

| Input | Current behavior | Expected |
|-------|-----------------|---------|
| "non ho detto giovedì" | UNKNOWN → L4 Groq | CHANGE_DATE correction |
| "non giovedì, venerdì" | may parse BOTH days | date correction |
| "non alle 15, alle 16" | ⚠️ may extract 15 | time correction |
| "non ho detto Marco, ho detto Mario" | UNKNOWN | CHANGE_OPERATOR correction |

**Fix in CORRECTION_PATTERNS:**
```python
CorrectionType.CHANGE_DATE: [
    # ... existing patterns ...
    r"non\s+ho\s+detto\s+(?:lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)",
    r"non\s+(?:lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)[,;]?\s+(?:ma\s+)?(lunedì|martedì|...)",
],
CorrectionType.CHANGE_OPERATOR: [
    r"non\s+ho\s+detto\s+[A-Z]\w+[,;]?\s+(?:ho\s+detto|intendevo|volevo\s+dire)\s+[A-Z]\w+",
],
```

---

## CATEGORY 4: Implicit Booking Context

### 4.1 "Lo stesso di sempre" — Repeat Booking

**Current state:** ❌ Not handled. Goes to L4 Groq which has no access to booking history.

| Expression | Status | Fix approach |
|-----------|--------|-------------|
| "lo stesso di sempre" | ❌ | feature: session.last_booking lookup |
| "come l'ultima volta" | ❌ | feature |
| "il solito" | ❌ | feature |
| "il mio appuntamento fisso" | ❌ | feature |
| "ogni mese viene" | ❌ | recurring booking (future feature) |
| "la mia routine" | ❌ | feature |

**Architecture gap:** `session_manager.py` does not store `last_booking` in session context. The FSM `reset()` wipes `context["service"]`, `context["date"]` etc. To implement "lo stesso di sempre", we need:
1. Persist `last_booking_snapshot` in SQLite session store
2. In FSM `WAITING_SERVICE` handler, check for "solito/stesso" patterns and auto-fill
3. Effort: **L** (multi-file: session_manager + FSM + entity_extractor + new pattern)

### 4.2 Preferred Operator Implicit Reference

| Expression | Status | Fix |
|-----------|--------|-----|
| "come al solito con Marco" | ❌ | requires last_booking |
| "sempre con la Giulia" | ❌ | requires last_booking |
| "solo con lui" | ❌ | pronoun resolution (no referent) |
| "con la mia parrucchiera" | ❌ | "mia" = preferred operator, not in DB |
| "con chi vengo di solito" | ❌ | requires history lookup |

### 4.3 Third-Party Bookings ("per mia figlia")

**Current state:** ❌ The FSM collects `context["client_name"]` as the caller. Third-party bookings are not supported.

| Expression | Status | Expected behavior |
|-----------|--------|-----------------|
| "prenoto per mia figlia" | ❌ | collect daughter's name instead |
| "è per mio marito" | ❌ | switch name collection target |
| "prenoto per una mia amica" | ❌ | create/find separate client |
| "sono la mamma di Lucia" | ❌ | proxy booking |
| "faccio la prenotazione per il mio capo" | ❌ | proxy |

**Pattern to detect:**
```python
THIRD_PARTY_PATTERNS = [
    r"(?:prenoto|prenotazione)\s+per\s+(?:mia?|il\s+mio|la\s+mia|un[ao]\s+mi[ao])\s+\w+",
    r"(?:è|è\s+per)\s+(?:mia?|il\s+mio|la\s+mia)\s+\w+",
    r"sono\s+la?\s+(?:mamma|madre|moglie|sorella|figlia|amica|collega)\s+di\s+\w+",
    r"faccio\s+(?:io\s+)?(?:la\s+)?prenotazione\s+per\s+\w+",
]
```

**FSM change needed:** When third-party detected, set `context["booking_for_other"] = True` and ask "Mi dica il nome della persona per cui prenota."

**Effort: M** (new context slot, FSM handler modification, new patterns)

### 4.4 Multi-Person Booking ("siamo in due")

**Current state:** ❌ Completely unhandled. The FSM books exactly one service for one person.

| Expression | Status |
|-----------|--------|
| "siamo in due" | ❌ |
| "prenoto per me e mia sorella" | ❌ |
| "due appuntamenti" | ❌ |
| "taglio per me e colorazione per lei" | ❌ |
| "siamo un gruppo di tre" | ❌ (e.g., bridal party) |

**Fix approach:** This requires a major FSM redesign. Short-term: detect "siamo in due/tre/N" and respond "Mi dispiace, al momento posso gestire una prenotazione alla volta. Preferisce che le faccia la prima prenotazione e poi mi richiami per la seconda?" — Effort: S (detection + graceful degradation)

### 4.5 Same-Call Multiple Bookings ("e anche martedì")

| Expression | Status | Notes |
|-----------|--------|-------|
| "e anche martedì alle 10" | ❌ | second booking in same turn |
| "e prenotiamo anche per giovedì" | ❌ | |
| "aggiungi anche lunedì" | ❌ | |
| "faccio due appuntamenti" | ❌ | |

**Fix:** Similar to multi-person — detect and gracefully offer sequential booking. Effort: S for degradation, L for real multi-booking.

---

## CATEGORY 5: Temporal Ambiguity (Italian Specific)

### 5.1 Relative Dates

**Current state in `entity_extractor.py`:**
- ✅ "domani" → +1 day
- ✅ "dopodomani" → +2 days
- ✅ "oggi" → +0 days
- ❌ "ieri" → -1 day (WHY is ieri in RELATIVE_DATES? Client cannot book yesterday — this is a data contamination risk. Should be removed or redirected)

**Missing relative date expressions:**
```python
# NOT in RELATIVE_DATES list:
"fra una settimana"    # +7 days
"tra una settimana"    # +7 days
"fra due settimane"    # +14 days
"la prossima settimana" # is_ambiguous_date but no resolution → falls through
"il mese prossimo"     # is_ambiguous_date but no resolution
"prima possibile"      # → first_available lookup
"appena possibile"     # → first_available lookup
"tra qualche giorno"   # vague → ask clarification
"questa settimana"     # is_ambiguous_date but no resolution
```

### 5.2 "lunedì prossimo" vs "lunedì" — The Classic Ambiguity

**Current handling in `entity_extractor.py` (lines ~191-210):**
```python
# Same day requested → always default to next week
if days_ahead == 0:
    days_ahead = 7
```

This means if today is Monday and user says "lunedì", Sara books for NEXT Monday (+7 days). This is correct in many contexts but wrong if the user means "this Monday" (i.e., within the same week).

**Real edge cases:**
- User calls Monday at 8am, says "lunedì pomeriggio" → means TODAY afternoon ❌
- User calls Friday, says "lunedì" → means next Monday ✅ (current behavior correct)
- User says "lunedì prossimo" explicitly → +7 days from next occurrence ✅
- User says "lunedì di questa settimana" → this Monday (may already be past) ❌

**Missing: "domenica prossima" ambiguity.** In Italy, "domenica prossima" when said on a Monday could mean either the coming Sunday (6 days) or the one after (13 days). Sara correctly disambiguates "prossima settimana + day" but not "domenica prossima" standalone.

### 5.3 Time-of-Day Expressions (Italian Standards)

**Current TimeSlot mappings vs Italian conventions:**

| Expression | Sara maps to | Italian convention | Correct? |
|-----------|-------------|-------------------|---------|
| "mattina" | 10:00 | 8:00–12:00 range | ⚠️ |
| "mattina presto" | 08:00 | before 9:00 | ✅ |
| "prima mattina" | 08:00 | 7:00–9:00 | ✅ |
| "mezzogiorno" | 12:00 | 12:00–13:00 | ✅ |
| "pranzo" | 13:00 | 12:30–13:30 | ✅ |
| "pomeriggio" | 15:00 | 14:00–18:00 range | ⚠️ |
| "primo pomeriggio" | ❌ MISSING | 13:00–15:00 | ❌ |
| "tardo pomeriggio" | 17:00 | 16:00–18:00 | ✅ |
| "sera" | 19:00 | 18:00–21:00 | ✅ |
| "dopo pranzo" | ❌ MISSING | 13:30–15:00 | ❌ |
| "verso le 3" | ❌ depends on PM/AM | in Italy ALWAYS 15:00 | ❌ |

**Critical: "verso le 3" ambiguity.** Italians almost never say "alle 3 di pomeriggio" — they just say "alle 3" and context implies PM (businesses are open PM). The current `extract_time()` likely returns 03:00 (AM) for "alle 3". This would cause a booking at 3am.

**Verify in entity_extractor.py:** Check if there is an AM/PM disambiguation heuristic. Based on the code reviewed, `TimeSlot` enum maps "sera"→19:00 but no AM/PM logic for bare hour numbers.

**Fix for AM/PM:**
```python
# In extract_time() — after extracting bare hour:
# If hour <= 8 AND no explicit "di mattina"/"AM" indicator → add 12 (assume PM)
# This matches Italian business convention: 9-20 working hours
if extracted_hour in range(1, 9) and not has_morning_indicator(text):
    extracted_hour += 12  # "alle 3" → 15:00
```

### 5.4 "il 15" — Which Month?

**Current handling:** `extract_date()` Pattern 3 handles `\b(\d{1,2})\s+([a-z]+)\s+(\d{2,4})\b` (day + month name + year). But bare "il 15" without month name is NOT handled.

```python
# MISSING: bare day number resolution
r"\bil\s+(\d{1,2})\b"  # "il 15" → which month?
```

**Fix:** When bare day number is detected: if the day is still upcoming this month → book this month; else book next month. Sara should confirm: "Il 15 di questo mese, giusto? Sarebbe [date in full]."

### 5.5 Vague Time Expressions

| Expression | Status | Mapping needed |
|-----------|--------|---------------|
| "presto" | ❌ | 08:00–09:00 |
| "tardino" | ❌ | 17:00–18:00 |
| "non troppo presto" | ❌ | after 09:00 |
| "non troppo tardi" | ❌ | before 17:00 |
| "verso le" | ❌ | approximate time |
| "intorno alle" | ❌ | approximate time |
| "sui mezzogiorno" | ❌ | ~12:00 |
| "alle ore 10 e mezza" | ⚠️ | 10:30 — "e mezza" handled? |
| "alle 10 e un quarto" | ❌ | 10:15 |
| "alle 10 e tre quarti" | ❌ | 10:45 |
| "primo pomeriggio" | ❌ | 13:00–14:00 |
| "dopo pranzo" | ❌ | 13:30 |

**Pattern additions needed in entity_extractor.py:**
```python
# Approximate time
r"(?:verso|intorno\s+alle?|sui?)\s+(?:le\s+)?(\d{1,2})",
# Fractions
r"(\d{1,2})\s+e\s+(?:mezza|mezzo)",     # → +30 min
r"(\d{1,2})\s+e\s+un\s+quarto",         # → +15 min
r"(\d{1,2})\s+e\s+tre\s+quarti",        # → +45 min
r"(\d{1,2})\s+e\s+(?:un\s+)?quarto",   # → +15 min
# Vague slots
("primo pomeriggio", TimeSlot.PRANZO),   # add to TIME_SLOTS
("dopo pranzo", TimeSlot.PRANZO),
("presto la mattina", TimeSlot.MATTINA_PRESTO),
```

---

## CATEGORY 6: Phonetic STT Confusion (beyond Gino/Gigio)

### 6.1 Italian Name Confusions (Whisper ggml-small)

These are documented Whisper confusions for Italian names:

| Actual | STT output | Similarity | Status |
|--------|-----------|------------|--------|
| Marco | Mario | 0.71 | ⚠️ Levenshtein catches at threshold 0.75 — BORDERLINE |
| Marco | Mirko | 0.71 | ❌ |
| Lucia | Giulia | 0.55 | ❌ not caught |
| Piero | Pietro | 0.78 | ✅ caught by Levenshtein |
| Gino | Gigio | variant | ✅ PHONETIC_VARIANTS |
| Sara | Sarah | 0.8 | ✅ |
| Chiara | Clara | 0.83 | ✅ |
| Giovanni | Giovanna | 0.89 | ✅ |
| Stefano | Stéfano | 0.92 | ✅ accent diff |
| Francesca | Francesco | 0.87 | ✅ |
| Valentina | Valentino | 0.90 | ✅ |
| Roberto | Roberta | 0.88 | ✅ caught |
| Luca | Lucia | 0.73 | ⚠️ borderline |
| Giuseppe | Giusi | 0.57 | ❌ but "giusi" → variant? |
| Carmelo | Carmela | 0.88 | ✅ |
| Rosaria | Rosario | 0.88 | ✅ |

**Add to PHONETIC_VARIANTS in disambiguation_handler.py:**
```python
"marco": ["mario", "mirko", "marco"],        # Marco ↔ Mario ↔ Mirko
"lucia": ["giulia", "luisa", "lucia"],       # Lucia ↔ Giulia
"luca": ["lucia"],                           # Luca ↔ Lucia
"giusi": ["giuseppina", "giuseppe"],         # Giusi (nickname for Giuseppina)
"dario": ["mario", "danio"],                 # Dario ↔ Mario (1-char diff)
```

### 6.2 Service Term STT Confusions

| Actual word | STT common error | Impact |
|------------|-----------------|--------|
| "salone" | "salome" | ❌ service lookup fails |
| "colorazione" | "colorazione" → usually ok | ✅ |
| "colore" | "dolore" | ❌ medical/salone confusion |
| "piega" | "prega" (pray!) | ❌ service not found |
| "barba" | "barba" → ok | ✅ |
| "manicure" | "manicure" / "manicura" | ⚠️ |
| "pedicure" | "pedicure" / "pedicura" | ⚠️ |
| "tagliando" | "tagliando" → ok | ✅ |
| "revisione" | "revisione" → ok | ✅ |
| "pilates" | "pilates" / "pi lates" | ⚠️ spacing |
| "yoga" | "yoga" → ok | ✅ |
| "spinning" | "spinning" / "spin ning" | ⚠️ |
| "crossfit" | "cross fit" | ⚠️ two words |

**Add to service synonyms:**
- "salome" → salone (STT error protection)
- "prega" → piega (hairdressing)
- "manicura" → manicure
- "pedicura" → pedicure
- "pi lates" → pilates
- "cross fit" → crossfit (already partially: "cross training" in synonyms)

### 6.3 Number Confusions (Critical for Phone/Time)

| Actual | STT error | Context |
|--------|----------|---------|
| "tre" → 3 | "tray" (English), "trè" | phone number digit |
| "sei" → 6 | "se'" (truncated), "say" | phone digit AND "sei" = you ARE |
| "uno" → 1 | "un'" (article), "una" | phone digit AND article |
| "otto" → 8 | "auto" (!!) | TIME: "alle otto" → "alle auto" |
| "nove" → 9 | "non ve" | phone digit |
| "zero" → 0 | "serò" (dialectal future) | phone prefix |
| "due" → 2 | "do" (STT artifact) | |

**CRITICAL: "alle auto"** — "alle otto" (at 8 o'clock) transcribed as "alle auto" (cars!). This is a real STT error documented with Italian Whisper models. Current time extraction: `re.search(r"alle?\s+(\d{1,2})", text)` would not match "alle auto". But it could trigger the AUTO vertical guardrail if active for a salone!

**Fix:** In `entity_extractor.py`, add post-processing for known STT number errors:
```python
STT_NUMBER_FIXES = {
    r"\balle\s+auto\b": "alle otto",           # "alle otto"
    r"\ball[e']?\s+due\s+auto\b": "alle due",  # edge case
    r"\btray\b": "tre",                         # English STT artifact
    r"\b(?:say|sè)\b(?=.*(?:appuntamento|ore|alle))": "sei",  # contextual
}
```

### 6.4 Day Name STT Truncations

Common Whisper outputs for Italian days:

| Actual | STT output | Status |
|--------|-----------|--------|
| "martedì" | "marted" (no accent, truncated) | ❌ not in DAYS_IT |
| "giovedì" | "gioved" | ❌ |
| "venerdì" | "venerd" | ❌ |
| "mercoledì" | "mercoled" | ❌ |
| "lunedì" | "lunedi" (no accent) | ✅ DAYS_IT has both |
| "sabato" | "sabato" | ✅ |
| "domenica" | "domenica" | ✅ |

**Fix in DAYS_IT:**
```python
"marted": 1,    # STT truncation
"gioved": 3,    # STT truncation
"venerd": 4,    # STT truncation
"mercoled": 2,  # STT truncation
```

---

## CATEGORY 7: Interruptions & Restarts

### 7.1 Current Handling Assessment

**In `CORRECTION_PATTERNS` (italian_regex.py):**
- ✅ CorrectionType.WAIT: "aspetti", "un attimo", "un momento"
- ✅ CorrectionType.REPEAT: "ripeta", "non ho capito"
- ✅ CorrectionType.SLOWER: "più piano", "lentamente"
- ✅ CorrectionType.GENERIC_CHANGE: "torniamo indietro", "ricominciamo"
- ❌ CorrectionType.ABANDON: "lasci stare tutto" (= total abandon, not just a slot)

### 7.2 Unhandled Interruption Patterns

| Expression | Current | Expected |
|-----------|---------|---------|
| "aspetti aspetti" (double) | ✅ WAIT (aspetti matches) | ✅ |
| "lasci stare" | ✅ RIFIUTO (exact) | ✅ if FSM handles |
| "lasci stare tutto" | ❌ | abandon entire session |
| "ricominci da capo" | ✅ GENERIC_CHANGE "ricominciamo" | ✅ |
| "dimentichi tutto" | ❌ | session reset |
| "ricominciamo tutto" | ✅ "ricominciamo" | ✅ |
| "mi fermo" | ❌ | pause/stop |
| "mi dia un secondo" | ⚠️ WAIT via "secondo" | ✅ |
| "sto cercando" | ❌ | hold pattern, user looking for info |
| "ho sbagliato numero" | ❌ | wrong number → RIFIUTO + close |
| [silence > 10s] | ❌ | Sara should prompt: "Mi sente?" |
| [silence > 30s] | ❌ | Sara should close gracefully |

**Add to CORRECTION_PATTERNS:**
```python
CorrectionType.GENERIC_CHANGE: [
    # ... existing ...
    r"(?:dimentichi|dimentica|dimentico)\s+(?:tutto|quello\s+che)",
    r"(?:lasci|lascia)\s+stare\s+tutto",
    r"ho\s+sbagliato\s+numero",
],
```

**Silence handling:** Not a regex problem — this is a VAD + orchestrator timeout issue. The `vad_wrapper.py` should emit a "silence_timeout" event after N seconds which the orchestrator handles with a re-prompt.

### 7.3 Mid-Topic-Change

| Expression | Current | Expected |
|-----------|---------|---------|
| "Ah sì, ma prima un'altra cosa" | ❌ | note interrupt, handle digression |
| "mentre ci sono" | ❌ | secondary question follows |
| "un'ultima cosa" | ❌ | user adding question before closing |
| "ah dimenticavo" | ❌ | afterthought |
| "anzi sì, mi sono ricordato" | ⚠️ "anzi" → CHANGE | partial |

These are conversational pivots that Groq L4 handles naturally but the lower layers miss. The risk is that the FSM is in state WAITING_SERVICE and the user says "ah sì, ma mentre ci sono — avete la ceretta?" — Sara may treat this as a service selection.

**Minimal fix:** Add "mentre ci sono" / "dimenticavo" / "un'altra cosa" as WAIT signals that temporarily pause slot-filling:
```python
CorrectionType.WAIT: [
    # ... existing ...
    r"(?:mentre\s+(?:ci\s+sono|ho\s+(?:lei|te)|sono\s+qui))",
    r"(?:ah\s+)?dimenticavo",
    r"un[''']altra\s+cosa",
    r"un'?ultimissima\s+(?:cosa|domanda|questione)",
]
```

---

## CATEGORY 8: Emotional States

### 8.1 Frustration Handling

**Sara's content filter (Level 1 MILD):** "uff", "argh", "che palle", "mannaggia"
**Sara's escalation trigger:** "non voglio parlare con un robot"

**Gap: Frustration without profanity**

| Expression | Current | Expected |
|-----------|---------|---------|
| "ma quante volte devo dirlo" | ❌ → UNKNOWN → L4 | empathy + repeat |
| "l'ho già detto" | ❌ | acknowledge + repeat |
| "non capisce niente" | ❌ MODERATE ("capisce" = no match) | empathy + redirect |
| "non mi capisce" | ❌ | empathy + clarification |
| "è impossibile" | ❌ | empathy + offer human |
| "non riesco a farmi capire" | ❌ | empathy + offer human |
| "ma è difficile?" | ❌ | empathy |
| "ma che tipo di sistema è questo" | ❌ | empathy |
| "ho perso la pazienza" | ❌ | escalation offer |
| "basta così" | ⚠️ "basta" → RIFIUTO | could be frustration OR close |

**Add FRUSTRATION_PATTERNS (new category):**
```python
FRUSTRATION_PATTERNS = [
    r"(?:ma\s+)?quante\s+volte\s+(?:devo\s+(?:dirlo|ripeterlo)|l['']ho\s+detto)",
    r"(?:ma\s+)?l['']ho\s+già\s+detto",
    r"non\s+(?:mi\s+)?(?:capisce|capisce\s+niente|capite)",
    r"non\s+riesco\s+(?:a\s+)?(?:farmi\s+capire|spiegarmi)",
    r"(?:ho\s+perso\s+la\s+pazienza|non\s+ne\s+posso\s+più)",
    r"(?:è\s+)?impossibile\s+(?:parlare|capirsi|comunicare)",
    r"che\s+(?:tipo\s+di|roba\s+è\s+questa|sistema\s+è\s+questo)",
]
```

**Sara's response when frustration detected:** "Mi scusi se non sono riuscita a capire. Posso metterla in contatto con un nostro operatore che la aiuterà direttamente." → Offer escalation proactively.

### 8.2 Urgency Signals

| Expression | Current | Expected |
|-----------|---------|---------|
| "è urgente è urgente" | ❌ UNKNOWN | note urgency + expedite or escalate |
| "ho bisogno SUBITO" | ❌ | first_available + urgency flag |
| "emergenza" | ❌ | immediate escalation (especially medical) |
| "mi fa un dolore terribile" | ❌ (medical) | emergency escalation |
| "è scoppiata una gomma" | ❌ (auto) | urgency + immediate slot |
| "devo assolutamente venire oggi" | ⚠️ | PRENOTAZIONE + today date |

**For medical vertical specifically, "emergenza" / "dolore forte" MUST escalate.**

### 8.3 Affectionate/Positive Responses

| Expression | Current | Expected |
|-----------|---------|---------|
| "sei un amore" | ❌ SEVERE? ("sei" + "?" triggers?) | warm acknowledgment |
| "sei gentilissima" | ❌ | warm acknowledgment |
| "grazie mille siete bravissimi" | ✅ → CORTESIA grazie | ✅ |
| "sei bravissima" | ❌ | warm "grazie!" |
| "mi piace come lavorate" | ❌ | warm acknowledgment |

**Check: "sei un amore"** — Does the SEVERE pattern trigger? Looking at the code: `r"\b(?:sei\s+(?:sexy|gnocca|bona|figa))\b"` — "sei un amore" does NOT trigger severe. But there is no positive response either. Goes to UNKNOWN → L4 Groq responds generically.

**Add to CORTESIA_EXACT or a new COMPLIMENT handler:**
```python
"sei un amore": ("compliment", IntentCategory.CORTESIA, "Grazie mille, è molto gentile!"),
"sei gentilissima": ("compliment_f", IntentCategory.CORTESIA, "Grazie, fa molto piacere!"),
"bravissimi": ("compliment_plural", IntentCategory.CORTESIA, "Grazie, siamo qui per lei!"),
"sei bravissima": ("compliment_adj", IntentCategory.CORTESIA, "Grazie mille!"),
```

### 8.4 Rude Inputs (Non-Profanity)

| Expression | Current | Expected |
|-----------|---------|---------|
| "sei stupida" | ⚠️ MODERATE "stupido" | ✅ handled |
| "non capisci niente" | ❌ | gentle rebuke |
| "sei inutile" | ❌ | gentle rebuke + offer human |
| "che cretinata" | ⚠️ MODERATE "cretino" (gender variant) | ✅ "cretinata" — check if regex catches |
| "sistema di merda" | ✅ MODERATE "merda" | ✅ |
| "fate schifo" | ⚠️ "schifo" in MILD | ✅ |
| "siete incapaci" | ❌ | gentle rebuke |

---

## CATEGORY 9: Business Context Ambiguity (Knowledge Gaps)

### 9.1 Price Queries

| Expression | Current | Gap |
|-----------|---------|-----|
| "quanto costa un taglio?" | ⚠️ → INFO intent → FAQ | FAQ has no prices (DB-dependent) |
| "avete un listino prezzi?" | ⚠️ → INFO | same gap |
| "più o meno quanto viene?" | ❌ | INFO but no data |
| "costa molto?" | ❌ | INFO but no data |
| "è caro?" | ❌ | INFO but no data |

**Current behavior:** INFO intent goes to L3 FAQ which does keyword search. If FAQ DB has price info, it responds. Otherwise L4 Groq responds with "Non ho informazioni sui prezzi, le consiglio di contattarci direttamente."

**Gap to document:** Sara cannot quote prices from the services DB. The pricing field (`prezzo`) exists in the DB schema (services table) but the FAQ layer does not query it. **Feature gap — not a regex/NLU issue.**

### 9.2 Business Hours Queries

| Expression | Current | Gap |
|-----------|---------|-----|
| "siete aperti sabato?" | ⚠️ → INFO | hours not in FAQ |
| "fino a che ora siete aperti?" | ⚠️ → INFO | same |
| "aprite la domenica?" | ⚠️ → INFO | same |
| "quando chiudete?" | ⚠️ → INFO | same |
| "siete aperti adesso?" | ❌ | needs real-time check |

**Feature gap:** Business hours should be stored in `impostazioni` DB and queryable by Sara. This is a data layer issue, not NLU.

### 9.3 Location/Address Queries

| Expression | Current | Privacy concern |
|-----------|---------|----------------|
| "dove siete?" | ⚠️ → INFO → FAQ | Privacy: address in FAQ DB → OK |
| "come si arriva?" | ❌ | navigation not in scope |
| "siete in centro?" | ❌ | partial location |
| "avete parcheggio?" | ❌ | FAQ-dependent |
| "siete vicino alla stazione?" | ❌ | relative location |

**These should all go to L3 FAQ.** The issue is that FAQ keyword coverage for location is thin.

### 9.4 Operator Availability

| Expression | Current | Expected |
|-----------|---------|---------|
| "c'è il dottore oggi?" | ⚠️ → INFO or UNKNOWN | check operator schedule |
| "c'è Marco disponibile domani?" | ⚠️ → partially handled | availability check |
| "chi c'è lunedì?" | ❌ | operator list query |
| "lavora Giulia questa settimana?" | ❌ | operator schedule query |
| "è in ferie la Roberta?" | ❌ | vacation status |

**Partial gap:** The FSM WAITING_OPERATOR state can lookup operator availability via DB. But the intent "who is available" before starting a booking is not classified — falls through to Groq.

---

## CATEGORY 10: Multi-Service Booking

### 10.1 Current Implementation

`extract_multi_services()` in `italian_regex.py` (lines 302-322):
- Uses substring matching of service synonyms
- Returns list of matched service IDs
- Called by FSM when `has_multi_service_intent=True`

**Current coverage:**

| Expression | Status |
|-----------|--------|
| "taglio e colore" | ✅ both detected |
| "taglio e barba" | ✅ both detected |
| "manicure e pedicure" | ✅ both detected |
| "taglio, barba e colore" | ✅ triple detected |
| "piega e trattamento" | ✅ both detected |

### 10.2 Multi-Service Gaps

| Expression | Status | Notes |
|-----------|--------|-------|
| "taglio per me e manicure per mia sorella" | ❌ | multi-person + multi-service |
| "taglio oggi e piega giovedì" | ❌ | multi-date + multi-service |
| "taglio e poi vorrei anche la barba" | ⚠️ | "poi anche" connector may not work |
| "me lo fate in un'unica soluzione?" | ❌ | asking if combo is possible |
| "quanto tempo ci vuole per taglio e colore?" | ❌ → INFO | duration query for combo |
| "fatemi tutto insieme" | ❌ | implicit combo without naming services |
| "il pacchetto completo" | ❌ | package booking concept |
| "tutto quanto" | ❌ | vague all-services |

### 10.3 Two Dates in One Call (CRITICAL FSM BUG)

**Scenario:** Customer says "taglio per domani e poi mi prenoti anche giovedì per la piega."

**Current behavior:** FSM collects first date (domani), first service (taglio), enters CONFIRMING state. The second "e poi giovedì per la piega" is received during CONFIRMING — FSM does not know how to handle it. It may:
1. Ignore it (slot already filled)
2. Override the first booking (if date extraction fires again)
3. Escalate to Groq

**Expected:** Complete first booking, then ask "Vuole che prenoti anche giovedì per la piega?"

**Fix approach (medium-term):** Queue second booking request. After first booking confirmed, ask "Ho anche notato che vuole prenotare giovedì per la piega. Confermo anche questa?"

---

## SYNTHESIS: Priority Fix Matrix

### P0 — Critical (production blockers, real data corruption)

| ID | Issue | File | Effort |
|----|-------|------|--------|
| C3-1 | "non voglio cancellare" → triggers RIFIUTO not NEGATED_CANCEL | orchestrator.py | S |
| C3-2 | "no aspetti" → RIFIUTO not WAIT | italian_regex.py prefilter order | S |
| C5-3 | "alle otto" → "alle auto" STT → wrong AM/PM + vertical confusion | entity_extractor.py + stt_postprocess | S |
| C5-4 | bare hour "alle 3" → books 03:00 AM not 15:00 PM | entity_extractor.py | S |
| C6-4 | "marted/gioved/venerd" STT truncation → date not extracted | entity_extractor.py DAYS_IT | S |

### P1 — High Impact (common real-world scenarios)

| ID | Issue | File | Effort |
|----|-------|------|--------|
| C2-2 | "c'è posto?" / "è libero?" / "avete un buco?" → not PRENOTAZIONE | intent_classifier.py | S |
| C5-2 | "lunedì" when today IS Monday → books next week not today | entity_extractor.py | S |
| C5-5 | "alle 10 e mezza/quarto/tre quarti" not extracted | entity_extractor.py | S |
| C1-1 | "prenoterei" / "avrei voluto prenotare" (condizionale) → UNKNOWN | intent_classifier.py | S |
| C5-1 | "tra una settimana" / "primo pomeriggio" / "dopo pranzo" missing | entity_extractor.py | S |
| C8-1 | Frustration without profanity → no empathy | italian_regex.py | M |
| C6-1 | Marco/Mario, Lucia/Giulia PHONETIC_VARIANTS additions | disambiguation_handler.py | S |

### P2 — Medium Impact (nice-to-have, improves UX)

| ID | Issue | File | Effort |
|----|-------|------|--------|
| C4-3 | "per mia figlia" third-party booking | orchestrator.py + FSM | M |
| C2-3 | Diminutives: "appuntamentino", "tagliettino" | entity_extractor.py | S |
| C7-2 | "mentre ci sono" / "dimenticavo" mid-topic pivots | italian_regex.py | S |
| C8-2 | Urgency detection → priority slot + escalation | orchestrator.py | M |
| C1-2 | "baffi" missing from salone synonyms | italian_regex.py | S |
| C3-3 | Negated date corrections ("non ho detto giovedì") | italian_regex.py | S |
| C8-3 | "sei un amore" → warm acknowledgment not Groq fallback | intent_classifier.py | S |
| C9-4 | "c'è il dottore oggi?" → INFO not UNKNOWN | intent_classifier.py | S |
| C4-4 | "siamo in two" → graceful multi-person degradation | orchestrator.py | S |

### P3 — Low Impact (edge cases, future features)

| ID | Issue | File | Effort |
|----|-------|------|--------|
| C4-1 | "lo stesso di sempre" → repeat booking | session_manager + FSM | L |
| C4-5 | Same-call multi-booking ("e anche giovedì") | FSM | L |
| C4-4 | Full multi-person booking support | FSM redesign | L |
| C7-3 | Silence timeout handling | VAD + orchestrator | M |
| C9-1 | Price queries from services DB | faq_manager + DB | M |
| C9-2 | Business hours from impostazioni | faq_manager + DB | M |

---

## IMPLEMENTATION NOTES

### Note 1: "ieri" in RELATIVE_DATES

`entity_extractor.py` RELATIVE_DATES contains `("ieri", -1)`. This returns yesterday's date for booking. A customer CANNOT book for yesterday. This should be removed or handled with "Mi dispiace, non posso prenotare per date passate." — however it may be intentional for cancellation context ("ieri ho prenotato e voglio cancellare"). Keep but add guard in FSM to reject past dates.

### Note 2: "cambia" Verb Noun Collision

Italian "cambio" is both:
- Verb (cambio = I change): "cambio l'appuntamento"
- Noun (cambio = exchange/gear): "cambio marce", "cambio gomme"

The SPOSTAMENTO pattern catches "cambia" (imperative/he-changes). The auto vertical has "cambio_olio", "cambio gomme". With the F02 fix (requiring explicit booking object), this should be safe — but monitor.

### Note 3: "sei" Ambiguity

Italian "sei" is both:
- Number 6: "metti il sei marzo"
- Pronoun "you are": "sei un amore", "sei stupida", "sei un robot"

In phone number dictation, "sei" means 6. In other contexts it's 2nd person singular. The STT confusion of "sei" → "se'" noted in Category 6 would only matter in phone number collection context (WAITING_PHONE state in FSM).

### Note 4: Sentence-Level Negation Scope

Italian negation "non" has scope that extends across the entire predicate. The current architecture processes single tokens or short patterns. For cases like "non ho detto che volevo cancellare ma spostare" — a full sentence negation analysis would require the Groq layer. The P0 fixes above cover only the most common 2-3 word patterns.

### Note 5: Vertical-Specific Urgency

Different verticals should escalate urgency differently:
- **Medical**: "dolore forte" / "emergenza" / "febbre alta" → immediate human escalation
- **Auto**: "gomma scoppiata" / "non parte" → first available slot today
- **Salone**: "matrimonio domani" / "cerimonia" → priority slot
- **Palestra**: urgency is generally LOW — waitlist sufficient

Currently all urgency falls to L4 Groq with no vertical-specific routing.

---

## APPENDIX: Dialect Quick Reference

### Neapolitan/Southern
| Neapolitan | Standard Italian | Sara handles? |
|-----------|-----------------|--------------|
| "aggia prenotà" | "devo prenotare" | ❌ |
| "jammo" | "andiamo" / "dai" | ❌ |
| "m'adda fà nu taglio" | "devo farmi un taglio" | ❌ |
| "'o barbiere" | "il barbiere" | ❌ |

**Note:** Whisper generally transcribes heavy Neapolitan dialect to Standard Italian or near-standard. These patterns are unlikely to survive intact to the NLU layer. Low priority.

### Venetian/Northern
| Venetian | Standard | Sara handles? |
|---------|---------|--------------|
| "gh'è posto?" | "c'è posto?" | ❌ |
| "vignirò" | "verrò" | ❌ |
| "doman" | "domani" | ❌ |

**Note:** Same as Neapolitan — Whisper normalizes most Venetian dialect. Low priority.

### Sicilian
| Sicilian | Standard | Sara handles? |
|---------|---------|--------------|
| "vogghiu" | "voglio" | ❌ |
| "apposgnu" | "appuntamento" | ❌ |

**Note:** Whisper normalizes these heavily. Low priority unless customer base is specifically Sicilian.

**Bottom line:** Dialects are handled at the STT layer by Whisper normalization. The NLU layer can assume ~standard Italian input. Regional vocabulary (C2 category) is more important than morphological dialect.

---

**File size:** ~450 lines
**Next step:** Use this document to implement P0+P1 fixes in F02 sprint.
**Cross-reference:** `f02-nlu-comprehensive-patterns.md` for SPOSTAMENTO fix + guardrail patterns.
