# R4: World-Class Voice UX Patterns for Sara — Italian Booking Agent

**Researched:** 2026-03-04
**Domain:** Conversational UX, Voice Agent Design, Italian NLP
**Source:** Direct code analysis (booking_state_machine.py, orchestrator.py, vertical configs, whatsapp.py)
**Confidence:** HIGH (based on direct code inspection, not hypothesis)

---

## Executive Summary

Sara is a technically sophisticated voice agent with a 5-layer RAG pipeline, 23 FSM states, and enterprise-grade disambiguation. However, analysis reveals a **gap between implementation completeness and UX quality**: the happy path works well, but the experience degrades on friction points (latency, repetition, proactive suggestions) that are precisely what differentiate world-class from average.

The three most impactful improvements are: (1) consolidating multi-turn confirmations into a single "tutto giusto?" pass, (2) adding filler audio/TTS during the 1330ms processing gap, and (3) enabling proactive suggestions from customer history. These alone would move Sara from "functional" to "delightful".

**Primary recommendation:** Compress average booking turns from 6-7 to 4-5 by pre-filling from history and batching confirmation into one turn.

---

## AREA 1: Minimum Turn Booking

### Current Sara State: AVERAGE (6-8 turns for new client, 4-6 for returning)

**Traced FSM path for new client, best case:**

```
Turn 1: User calls → Sara greets → "Mi dice il suo nome?"                   [IDLE → WAITING_NAME]
Turn 2: User: "Marco Rossi" → Sara: "Piacere Marco! Mi dice il cognome?"    [WAITING_NAME → WAITING_SURNAME]
         (if name+surname given together, this turn is skipped)
Turn 3: Sara DB lookup → "Bentornato Marco! Come posso aiutarla?"            [→ WAITING_SERVICE]
         (or "Non la trovo, mi dà un numero?" for new client → 2 extra turns)
Turn 4: User: "Taglio" → Sara: "Bene, Taglio! Per quale giorno?"            [→ WAITING_DATE]
Turn 5: User: "Martedì" → Sara: "Martedì, perfetto. A che ora?"             [→ WAITING_TIME]
Turn 6: User: "Alle 15" → Sara: "Riepilogo: Taglio, martedì...Conferma?"   [→ CONFIRMING]
Turn 7: User: "Sì" → Sara: "Appuntamento confermato! Terminiamo..."         [→ ASKING_CLOSE_CONFIRMATION]
Turn 8: User: "Sì" → Sara: "Perfetto! A presto!"                           [→ COMPLETED]
```

**Minimum theoretical turns (Italian context): 4 turns**
- Turn 1: "Taglio martedì alle 3 con Marco" → all extracted in one message
- Turn 2: DB lookup result + "Bentornato Marco, confermo Taglio martedì 4 marzo alle 15 con nessuna preferenza operatore — va bene?"
- Turn 3: "Sì" → booking created + "Le mando la conferma su WhatsApp. Arrivederci!"
- Turn 4: (optional) Close confirmation

**What Sara CAN do today (code-verified):**
- `_handle_idle()` at line 1004-1014: if ALL fields provided in first message → jumps to CONFIRMING directly (skips WAITING_SERVICE/DATE/TIME)
- Entity extraction in `_update_context_from_extraction()` is greedy — extracts service+date+time from single utterance
- Operator preference is optional (skip path exists)
- `WAITING_NAME` + `WAITING_SURNAME` are TWO separate states even if user gives "Marco Rossi" → but auto-split in `sanitize_name_pair()` at line 477

**Gap identified:** For RETURNING clients (client_id known), Sara still asks all 3 booking fields fresh. No "you usually book taglio con Marco — same again?" path exists. History pre-fill is zero.

**World-class standard:**
- Return client + phone lookup: "Marco, vuole il solito taglio con Giulia? Ha disponibilità martedì e giovedì." → user picks time → done in 2-3 turns
- Pre-fill operator if client has a preferred operator stored

**Concrete improvements:**
1. After client identified (returning), fetch last booking from DB and offer as default
2. Operator preference: query most-used operator for this client and offer first
3. Collapse ASKING_CLOSE_CONFIRMATION into CONFIRMING turn: "Confermato! Le invio conferma WhatsApp — arrivederci!" (remove the extra turn)

| Metric | Current | Target |
|--------|---------|--------|
| Turns (new client) | 7-9 | 5-6 |
| Turns (returning client, no history pre-fill) | 5-7 | 3-4 |
| Turns (returning client, with history pre-fill) | N/A today | 2-3 |

**User Impact:** HIGH
**Effort:** M (returning client pre-fill) + S (collapse close-confirm turn)

---

## AREA 2: Confirmation UX

### Current Sara State: AVERAGE — verbose, robotic

**Current confirmation template (line 506):**
```python
"confirm_booking": "Riepilogo: {summary}. Conferma?",
```

Where `get_summary()` (line 209) produces:
```
"Taglio, mercoledì 15 gennaio, alle 15:00, con Marco"
```

**Resulting Sara utterance:**
> "Riepilogo: Taglio, mercoledì 15 gennaio, alle 15:00, con Marco. Conferma?"

**Problems identified:**
1. "Riepilogo:" is robotic — sounds like reading from a form
2. Full date format for nearby dates is unnecessary (user already said "martedì" — just confirm "martedì")
3. Repeats every field even when the user just gave them two seconds ago
4. No warmth: no "Perfetto!" before the summary, no "La aspettiamo!" closing

**World-class standard:**
- Short confirmation for nearby dates: "Taglio martedì alle 3 con Marco — va bene?"
- Warm phrasing: "Perfetto, allora ci vediamo martedì alle 3 con Marco — confermo?"
- After booking: "Ottimo! Le mando la conferma su WhatsApp adesso."

**Confirmed what Sara does NOT do:**
- No "tutto giusto?" colloquial phrasing (only formal "Conferma?")
- No shortening of date when context is clear (always full "mercoledì 15 gennaio")
- No operator "con X" variation when operator is not set (outputs nothing, not "senza preferenza operatore")
- No "La aspettiamo!" warmth in booking_confirmed template

**Concrete improvements:**
1. Replace `"Riepilogo: {summary}. Conferma?"` with `"{warm_summary} — confermo?"` where warm_summary collapses nearby dates
2. Add response variations (3-4 alternatives chosen randomly to avoid robot feel)
3. Add "La aspettiamo!" or "Ci vediamo martedì!" to booking_confirmed
4. When operator absent: don't say "con None" — say nothing or "con qualsiasi operatore disponibile"

**User Impact:** HIGH
**Effort:** S (template changes only, no FSM changes needed)

---

## AREA 3: Graceful Error Recovery

### Current Sara State: PARTIAL — has 3-level correction in CONFIRMING but not in data collection states

**What Sara does in data collection states when it can't extract:**

From code:
```python
"service_not_understood": "Mi faccia capire meglio, che tipo di trattamento desidera?",
"date_not_understood": "Per quale giorno vorrebbe prenotare?",
"time_not_understood": "A che ora le andrebbe bene?",
```

**Problems identified:**
1. These are open re-asks with no partial extraction acknowledgment
2. No targeted disambiguation: "Ho capito che vuole il pomeriggio — lunedì o martedì?"
3. No turn counting before fallback — Sara will loop the same "Mi faccia capire meglio" indefinitely (no `clarifications_asked` counter in WAITING_DATE/TIME states, only in CONFIRMING at line 2630)
4. No STT confidence-aware re-ask (the `handle_input_with_confidence` method exists at line 648 but is only called if the pipeline passes confidence — the orchestrator's `process()` doesn't call it, uses `process_message()` directly at line 915)

**What Sara does well:**
- CONFIRMING state has 3-level correction (entity extraction → rejection → confirmation) at line 2405+
- Groq NLU fallback in CONFIRMING for complex corrections (line 2534)
- WAITING_TIME has back-navigation: if user says a weekday when asked for time, recognizes date change intent (line 2109)
- `corrections_made` counter prevents cascade cancellation after corrections

**World-class standard:**
- Partial extraction + targeted re-ask: "Ho capito martedì — a che ora?"
- After 2 failed extractions, switch to guided: "Le propongo: 10:00, 14:00 o 16:00 — quale preferisce?"
- Never the same error message twice in a row

**Concrete improvements:**
1. Add `clarifications_asked` counter to WAITING_DATE and WAITING_TIME handlers (mirrors CONFIRMING behavior)
2. After 2nd failed extraction in date/time: offer explicit options ("mattina, pomeriggio, o sera?")
3. In WAITING_TIME error recovery, acknowledge what was understood: "Ho capito {servizio} per {date_display} — a che ora preferisce?"
4. Wire `handle_input_with_confidence()` through the orchestrator pipeline so low-STT-confidence triggers graceful re-ask rather than extraction attempt on garbled text

**User Impact:** HIGH
**Effort:** M

---

## AREA 4: Proactive Information

### Current Sara State: PARTIAL — proactive for availability and alternatives, ZERO for history

**What Sara does proactively (code-verified):**
- Slot availability check before booking creation (line 926-953) — offers alternative times if slot unavailable
- Week availability query for "prossima settimana" (line 1120-1148)
- Waitlist offer when slot unavailable (line 951-953)
- WhatsApp confirmation sent immediately post-booking (fire-and-forget, line 971-975)

**What Sara does NOT do proactively:**
- No history pre-fill ("Di solito prenota il taglio con Marco — lo rivuole?")
- No upsell suggestion ("La volta scorsa ha fatto anche la piega — la aggiungiamo?")
- No preferred operator suggestion from history
- No "Marco è disponibile martedì alle 3" proactive offer when client is identified
- No loyalty/points balance ("Ha 8 punti — al prossimo appuntamento avrà un trattamento omaggio!")
- No "La settimana scorsa ha cambiato l'appuntamento — lo sa che può farlo via WhatsApp?" education

**World-class standard:**
After client identification, if returning client:
```
"Bentornato Marco! Ho visto che di solito prenota il taglio con Giulia —
 la devo prenotare anche questa volta, o desidera qualcosa di diverso?"
```

**Concrete improvements:**
1. After client lookup success (line 1003-1026), query last booking and offer as default: fetch `servizio`, `operatore` from last confirmed appointment
2. Operator: query most-used operator for this client (via HTTP bridge `/api/clienti/{id}/preferenze`) and offer first
3. Loyalty points: announce when threshold is close ("Le mancano 2 appuntamenti al trattamento omaggio!")
4. Appointment list: when cancelling, also ask "Le fisso subito un'altra data?"

**User Impact:** HIGH (significant WOW factor for returning clients)
**Effort:** M-L (requires DB queries for history, but infrastructure already in place via HTTP bridge)

---

## AREA 5: Persona and Voice Quality

### Current Sara State: AVERAGE — functional Italian but not warm or human-quality

**Response variation analysis (code-verified):**

Current templates (all are STATIC strings, no variation):
```python
"ask_service": "Come posso aiutarla? Mi dica che trattamento desidera.",
"ask_date": "Bene, {service}! Per quale giorno?",
"ask_time": "{date}, perfetto. A che ora le farebbe comodo?",
"confirm_booking": "Riepilogo: {summary}. Conferma?",
"booking_confirmed": "Prenotazione confermata! {summary}. La aspettiamo!",
"fallback": "Scusa, non ho capito bene. Puoi ripetere?"
```

**Problems identified:**
1. Zero response variation — same phrase every time for every question
2. Mixing "Lei" (formal) and "tu" forms: `config.json` greeting uses "ti aspettiamo" (informal), FSM uses "Le aspettiamo" (formal), WhatsApp templates use "ti" throughout. Inconsistency.
3. No customer name use after identification (except "Bentornato {name}!" once at login — never again mid-conversation)
4. No Italian conversational fillers: "Certo!", "Perfetto!", "Benissimo!" are barely used — mostly "D'accordo"
5. `change_ack` (line 517): `"Certo, mi dica."` — good but used for ALL change interruptions
6. No sentence-initial acknowledgment before asking: missing pattern "Capito! Per quale giorno?"

**World-class standard:**
- 3-5 variations per question, chosen randomly
- Always address by first name at least once per response after identification
- Consistent Lei throughout (or consistent tu — never mix)
- Sentence-initial filler: "Certo!", "Perfetto!", "Capisco!" before moving to next question
- End with forward-looking statement: "Perfetto!" + question, not question alone

**Concrete improvements:**
1. Replace all static template strings with response arrays + random selection:
   ```python
   ASK_DATE_VARIANTS = [
       "Bene, {service}! Per quale giorno?",
       "Perfetto, {service}. Quando preferisce venire?",
       "{service}, ottima scelta! Che giorno le torna comodo?",
   ]
   def pick(variants): return random.choice(variants)
   ```
2. Fix Lei/tu inconsistency — standardize to LEI throughout (professional Italian business standard)
3. After client identified, use first name in 50% of subsequent responses: "Certo {nome}, per quale giorno?"
4. Add "Capisco!" / "Ho capito!" acknowledgment before re-asks in error recovery

**User Impact:** MEDIUM (quality feel, repeat business perception)
**Effort:** S (template changes + random selection, no FSM changes)

---

## AREA 6: Latency UX

### Current Sara State: BAD — 1330ms P95 with silence during processing

**Measured latency context (from CLAUDE.md and voice-agent-details.md):**
- Current P95: ~1330ms
- Target: <800ms
- Pipeline: STT → L0-L4 orchestrator → TTS = cumulative

**Architecture review for latency:**
- L0 (regex): <1ms
- L1 (intent classifier): <5ms
- L2 (booking SM): <10ms
- L3 (FAQ): <50ms
- L4 (Groq API): ~800-1200ms (dominant bottleneck)
- TTS (Piper): unmeasured but adds ~100-300ms

**What Sara does during processing (code-verified):**
Looking at orchestrator `process()` — there is NO filler/intermediate response mechanism. The pipeline is entirely synchronous from the user's perspective: user speaks, silence, Sara responds. The `asyncio.ensure_future()` is only used for WhatsApp (non-blocking side effect), not for filler speech.

**Perceived latency acceptability thresholds (IVR industry standard):**
- <400ms: imperceptible — feels instant
- 400-700ms: barely noticeable — acceptable
- 700-1000ms: slightly slow — most users tolerate
- 1000-1500ms: noticeably slow — some users think it froze
- >1500ms: users hang up or speak again (double-speaks)

**At 1330ms P95, Sara is in the "noticeably slow" zone and near hang-up risk.**

**Strategies to reduce PERCEIVED latency without changing actual latency:**

1. **Filler audio injection** (highest ROI, S effort): After VAD detects end-of-speech, immediately play a short filler (200-500ms) while processing:
   - "Un momento..."
   - *soft typing sound*
   - "Sto verificando..."
   This makes 1330ms feel like 830ms (filler plays during first 500ms of processing)

2. **Streaming LLM responses** (medium ROI, L effort): Already noted as TODO in voice-agent-details.md. Groq supports streaming — start TTS as tokens arrive. Reduces perceived wait from 1330ms to ~400ms for L4 responses.

3. **Cache hot paths** (medium ROI, M effort): For L2 (booking SM) responses that don't need DB lookup — pre-synthesize the 10 most common TTS responses (ask_name, ask_service, ask_date, ask_time, confirm, welcome_back). TTSCache class already exists at line 304 but only caches synthesized audio post-generation, not pre-generated.

4. **Barge-in during silence** (low ROI, L effort): Detect if user starts speaking again during Sara's processing delay and handle double-speak gracefully.

**Current Sara filler mechanisms: NONE detected in code.**

**Concrete improvements:**
1. Add filler injection: immediately after VAD end-of-speech → synthesize and play short filler → then process
2. Pre-synthesize 10 most-common responses at startup and store as bytes
3. Track latency per layer and log warnings when L4 is hit for inputs that could have been L2

**User Impact:** HIGH (removes "did it freeze?" anxiety)
**Effort:** S (filler injection) + M (pre-synthesis cache) + L (streaming LLM)

---

## AREA 7: Session Memory

### Current Sara State: GOOD — context preserved within call, some gaps

**What Sara remembers within a call (code-verified):**

`BookingContext` dataclass (line 110-168) carries:
- `client_id`, `client_name`, `client_surname`, `client_phone` — persisted across booking resets
- `service`, `services`, `date`, `time`, `operator_name` — booking-specific, cleared on `reset()`
- `was_interrupted`, `previous_state`, `corrections_made` — interruption tracking
- `vertical`, `disambiguation_candidates`, `disambiguation_attempts` — disambiguation tracking

**`reset()` method (line 595):** Soft reset (default) preserves client identity but clears booking fields. Used after booking completion so second booking in same call doesn't need re-identification.

**What gets LOST between FSM state transitions:**
1. Operator preference mentioned early in conversation: If user says "voglio Marco" during WAITING_SERVICE but operator extraction fires, it IS captured in `operator_name`. But if user mentions it as a side comment and then changes topic, it may be overwritten by a later `force_update=False` extraction.
2. Tentative date mentioned before service: If user says "sì magari martedì" in IDLE before specifying service, `_handle_idle()` extracts date but `_update_context_from_extraction` skips it if context.date is already set on second extraction — actually the issue is the reverse: if date is set from early mention, it carries correctly.
3. Phone number across sessions: NOT persisted (each call starts fresh DB lookup).

**Identified gap:** Operator preference mentioned informally before WAITING_OPERATOR state may not be reliably captured if user says it during IDLE (e.g., "Vorrei prenotare un taglio, possibilmente con Giulia" — "Giulia" as operator is in the same utterance as service, and `extract_all()` does extract operator — this works. But if user says "se c'è Giulia libera" in WAITING_DATE state, the operator extraction in `_update_context_from_extraction` at line 940-943 will capture it only if `not self.context.operator_name` — so it works correctly the first time).

**What Sara does NOT remember:**
- Preferred time window ("di solito vengo il pomeriggio") — not extracted, not stored
- Previous appointment history (last service, last operator) — not queried at session start
- Failed booking attempts within the call — not tracked

**Concrete improvements:**
1. At client identification (line 1003-1026), fetch and store `preferred_operator` and `preferred_service` from DB history into context (new optional fields)
2. Track `preferred_time_window` ("mattina"/"pomeriggio"/"sera") as stated by user and use as tie-breaker when presenting availability options

**User Impact:** MEDIUM
**Effort:** S (add 2 context fields + 1 DB query on client lookup)

---

## AREA 8: WhatsApp Post-Booking UX

### Current Sara State: PARTIAL — sends confirmation but format is mediocre; no reminder scheduling

**WhatsApp confirmation format (from whatsapp.py, verified):**

```
*Prenotazione Confermata!*

Ciao {nome},
il tuo appuntamento e' confermato:

  {servizio}
  {data}
  {ora}
  con {operatore}  (only if operator set)

Ti aspettiamo da {attivita}!

Per modificare o cancellare, rispondi qui o chiamaci.
Consiglia {attivita} a un amico: chi ti presenta riceve il 10% di sconto sul primo trattamento!
```

**Reminder templates exist (code-verified):**
- `reminder_24h()` at line 289: exists, formatted correctly
- `reminder_2h()` at line 303: exists, formatted correctly
- `cancellazione()` at line 312: exists

**BUT: Reminders are never actually scheduled (code-verified).** The `_send_wa_booking_confirmation()` in orchestrator (line 1948) only sends the confirmation template. No reminder scheduling logic exists in the codebase. The templates exist but are orphaned.

**Format issues:**
1. "il tuo appuntamento e'" — missing accent (should be "è") — encoding issue
2. Missing booking date in Italian format — uses raw `data` from context which may be "2026-03-10" (YYYY-MM-DD) not "martedì 10 marzo"
3. The referral CTA ("chi ti presenta riceve il 10% di sconto") is good but fires on EVERY confirmation — should be conditional
4. No calendar add link ("Aggiungi al calendario")
5. No address/location information

**Concrete improvements:**
1. Fix encoding: "e'" → "è" in WhatsApp templates
2. Pass `date_display` (Italian format) not `date` (YYYY-MM-DD) to WhatsApp template
3. Implement reminder scheduling: at booking creation, schedule `reminder_24h` for T-24h and `reminder_2h` for T-2h (requires a scheduler — cron, APScheduler, or Tauri task)
4. Add address line to WhatsApp template (from business config)
5. Make referral CTA conditional (only for clients with >1 booking, not brand-new registrations)

**User Impact:** MEDIUM-HIGH (reminders alone reduce no-shows significantly)
**Effort:** M (reminder scheduler) + S (format fixes)

---

## AREA 9: Escalation to Human

### Current Sara State: GOOD — escalation exists but is one-size-fits-all

**Escalation mechanisms (code-verified):**

1. **Keyword-triggered** (L0 special commands, line 212-215): "operatore", "persona", "umano", "parlo con qualcuno" → immediate escalation
2. **Regex-triggered** (italian_regex `is_escalation`, line 532): pattern-based detection
3. **Sentiment-triggered** (line 628-643): `SentimentAnalyzer` detects frustration, escalates IF not in active booking flow (correctly suppressed during booking to avoid false positives from "no"/"ma")
4. **STT confidence** (line 648-671): `handle_input_with_confidence()` exists but NOT wired into orchestrator pipeline
5. **Content filter SEVERE** (line 512-516): terminates session, also escalates

**What happens on escalation:**
- Response: "La metto in contatto con un operatore, un attimo..."
- `should_escalate=True` set on `OrchestratorResult`
- WhatsApp escalation call optionally triggered (`_trigger_wa_escalation_call`, line 539)
- The frontend (`main.py` route) handles `should_escalate` from the response — but the actual call transfer mechanism is NOT implemented (Sara says "La metto in contatto" but there's no actual call routing)

**Missing escalation triggers:**
1. After N failed extractions in a row (no counter exists in WAITING_DATE/TIME — only in CONFIRMING via `clarifications_asked`)
2. Medical emergencies in medical vertical — triage_rules in config detect symptoms but the orchestrator doesn't read them (they are in config.json but no code loads or acts on `triage_rules`)
3. "Voglio parlare con qualcuno" after booking completion (user may want to discuss something not covered)

**World-class standard:**
- After 3 consecutive failed understanding turns: "Mi scusi, ho difficoltà a capirla bene. Preferisce parlare con un nostro operatore?"
- For medical urgent symptoms: "Sembra urgente — La metto subito in contatto con il nostro personale."
- Warm handoff: before escalating, summarize what's been collected ("Ho annotato che cerca un taglio per martedì — lo dico all'operatore")

**Concrete improvements:**
1. Add global `consecutive_failures` counter to orchestrator — after 3 consecutive turns with no state advance → offer escalation
2. Read `triage_rules` from medical vertical config and trigger escalation on symptom match
3. On escalation, include context summary in WA message to operator: "Cliente {nome} cercava {servizio} per {data} — ha chiesto l'operatore"
4. Implement actual call transfer integration (SIP or phone provider webhook)

**User Impact:** MEDIUM (edge case but critical when it happens)
**Effort:** S (failure counter + triage trigger) + L (actual call transfer)

---

## AREA 10: Business Hours / Availability

### Current Sara State: BAD — critical gap for basic questions

**Code analysis:**

The `faq` section in `salone/config.json` (line 193) has:
```json
"answer": "Siamo aperti {{GIORNI_APERTURA}} dalle {{ORARIO_APERTURA}} alle {{ORARIO_CHIUSURA}}. {{NOTE_ORARI}}"
```

The `variables` section has hardcoded values:
```json
"GIORNI_APERTURA": "dal martedi' al sabato",
"ORARIO_APERTURA": "09:00",
"ORARIO_CHIUSURA": "19:00"
```

**Problem 1: Business hours are hardcoded in config.json, not read from DB.**

The Tauri/SQLite DB has a `setup_config` table (migration 021) with business configuration. Sara reads `nome_attivita` from DB at session start (line 402-407) but does NOT read hours. If the business changes its hours in the Fluxion app, Sara's answer remains wrong.

**Problem 2: Real-time operator availability is not checked before suggesting operators.**

When Sara collects operator preference, she does not verify if that operator is available on the requested date/time. The `availability_checker.py` exists (imported at line 51) and is used for slot availability (line 1093) but NOT for operator-specific availability.

**Problem 3: "Il mio operatore preferito c'è?" cannot be answered.**

Sara has no mechanism to check if a specific operator has availability on a given day. The FSM accepts operator preference and stores it, then tries to create a booking — if the operator isn't available, the booking creation may fail silently.

**World-class standard:**
- "Siete aperti domani?" → Sara checks DB for tomorrow's schedule (not hardcoded config)
- "C'è Marco martedì?" → Sara queries operator calendar and responds definitively
- "A che ora chiudete?" → Real-time answer from DB configuration

**Concrete improvements:**
1. Add HTTP bridge endpoint `/api/config/orari` — returns actual business hours from `setup_config` table
2. At session start (alongside `_load_business_config()`), also load and cache business hours
3. Add operator availability check when operator name is collected: query `/api/operatori/{id}/disponibilita?date={date}` before proceeding
4. Replace FAQ `{{ORARIO_APERTURA}}` etc. with live DB values, not config.json placeholders

**User Impact:** HIGH (answering "siete aperti?" incorrectly destroys trust instantly)
**Effort:** M (DB endpoint + session load) + S (FAQ variable substitution from DB)

---

## Summary Priority Matrix

| Area | Current | Impact | Effort | Priority |
|------|---------|--------|--------|----------|
| A6: Latency filler audio | BAD | HIGH | S | P1 |
| A2: Confirmation verbosity | AVERAGE | HIGH | S | P1 |
| A5: Response variation + Lei/tu fix | AVERAGE | MEDIUM | S | P1 |
| A10: Business hours from DB | BAD | HIGH | M | P1 |
| A1: History pre-fill for returning clients | AVERAGE | HIGH | M | P2 |
| A3: Error recovery + turn counting | PARTIAL | HIGH | M | P2 |
| A8: WhatsApp reminders | PARTIAL | MEDIUM-HIGH | M | P2 |
| A4: Proactive history suggestions | POOR | HIGH | M-L | P3 |
| A7: Session memory gaps | GOOD | MEDIUM | S | P3 |
| A9: Escalation after N failures | GOOD | MEDIUM | S | P3 |

---

## Directly Implementable Quick Wins (P1)

These require NO FSM architecture changes — only template and orchestrator tweaks:

### QW1: Filler Audio Injection (2h effort)
```python
# In orchestrator.process(), after VAD end-of-speech:
FILLER_RESPONSES = ["Un attimo...", "Sto verificando...", "Certo..."]
# Pre-synthesize these at startup, serve immediately before actual response
```

### QW2: Confirmation Template Replace (1h effort)
```python
# Replace static string with warm variants
CONFIRM_VARIANTS = [
    "Perfetto! {summary} — confermo?",
    "{summary}, va bene così?",
    "Tutto giusto? {summary}.",
]
```

### QW3: Lei/Tu Consistency Audit (1h effort)
- Grep all template strings for "ti", "tuo", "tuoi" — replace with "Le", "Suo", "Suoi"
- Grep `config.json` `responses` section — standardize
- Check WhatsApp templates — these may correctly use informal "tu" (WhatsApp is informal channel)

### QW4: Business Hours from DB (4h effort)
```python
# In _load_business_config() (already called at session start, line 401):
if db_config.get("orario_apertura"):
    self._business_hours = {
        "apertura": db_config["orario_apertura"],
        "chiusura": db_config["orario_chiusura"],
        "giorni": db_config["giorni_apertura"],
    }
# Inject into FAQ manager for live substitution
```

### QW5: Collapse ASKING_CLOSE_CONFIRMATION (30min effort)
Replace the two-turn close sequence with single-turn: after CONFIRMING confirmation, set `should_exit=True` immediately and include WhatsApp notification in the response text. Saves 1 turn from every booking.

---

## Sources

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/booking_state_machine.py` — FSM states, templates, handlers
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py` — 5-layer pipeline, WA sending, availability
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/salone/config.json` — salone vertical config, FAQs, variables
- `/Volumes/MontereyT7/FLUXION/voice-agent/verticals/medical/config.json` — medical config, triage_rules
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/whatsapp.py` — WhatsApp templates (conferma, reminder_24h, reminder_2h)
- `/Volumes/MontereyT7/FLUXION/.claude/rules/voice-agent-details.md` — latency measurements, pipeline architecture

**Confidence breakdown:**
- FSM turn count analysis: HIGH (direct code trace)
- Template verbosity analysis: HIGH (direct string inspection)
- Error recovery gaps: HIGH (code verified, no counter in date/time states)
- Latency handling: HIGH (no filler found in orchestrator.process())
- WhatsApp reminders: HIGH (templates exist, scheduling does not)
- Business hours: HIGH (hardcoded in config.json, not DB-driven)
- Proactive history: HIGH (zero code found for history pre-fill)

**Research date:** 2026-03-04
**Valid until:** 2026-04-04 (code-based, stable)
