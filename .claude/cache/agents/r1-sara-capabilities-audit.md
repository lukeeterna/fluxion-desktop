# R1 — Sara Full Capabilities Audit
> Generated: 2026-03-04 | Based on actual code reading, no padding.

## Files Read
| File | Lines |
|------|-------|
| `src/booking_state_machine.py` | 3490 |
| `src/orchestrator.py` | 2710 |
| `src/intent_classifier.py` | 735 |
| `src/entity_extractor.py` | 1484 |
| `src/disambiguation_handler.py` | 839 |
| `src/analytics.py` | 993 |
| `src/whatsapp.py` | 1210 |
| `src/whatsapp_callback.py` | 408 |
| `src/italian_regex.py` | 849 |
| `src/sentiment.py` | 453 |
| `verticals/{salone,palestra,medical,auto}/` | config.json + faqs.json |
| `tests/` | 39 test files, 897 test functions |

---

## A. BOOKING FLOW

### Single Booking
**Score: ✅ DONE (with caveats)**

Complete slot-filling FSM. Flow:
1. IDLE → WAITING_NAME → WAITING_SURNAME → DB lookup → REGISTERING_PHONE (new) → CONFIRMING_PHONE → REGISTERING_CONFIRM → WAITING_SERVICE → WAITING_DATE → WAITING_TIME → WAITING_OPERATOR (optional) → CONFIRMING → COMPLETED → ASKING_CLOSE_CONFIRMATION

All 23 states implemented and dispatched in `process_message()` (lines 744-813 of booking_state_machine.py).

Caveats:
- `SERVICE_DISPLAY` dictionary (lines 289-295) is salone-only hardcoded (`taglio/piega/colore/barba/trattamento`). For palestra/medical/auto verticals, FSM uses `extracted.service` directly without a display mapping.
- `context.is_complete()` (line 226) only checks `service + date + time` — does NOT check client_id. A booking can reach CONFIRMING without a resolved client.

### Multi-Service
**Score: ⚠️ PARTIAL**

`extract_multi_services()` in italian_regex.py (lines 302-322) scans for multiple service synonyms in one utterance. `extract_services()` in entity_extractor.py returns a list. `BookingContext.services` (line 129) stores the list.

Gap: `context.get_summary()` (line 209) only shows `service_display` which is built as `" e ".join(display_names)`. However, the booking DB call `_create_booking()` sends a single `service` field (the first service). Multi-service bookings are not split into multiple DB records. If the backend only handles one service per prenotazione row, the second service is silently dropped.

### Operator Preference
**Score: ⚠️ PARTIAL**

`WAITING_OPERATOR` state exists. `extract_operator()` extracts operator name. `operator_id` and `operator_name` stored in context. Orchestrator calls `_search_operators()` (line 1188) at L2 when `lookup_type == "operator"`.

Gap: operator_gender_preference field exists in BookingContext (line 162) but no extraction logic reads it. No code in FSM handles "voglio una donna" or "preferisco un uomo" and maps it to gender filter.

Gap: `_search_operators()` returns a list; if multiple operators exist, orchestrator stores only the first (line 1194-1196). No interactive selection ("Con Valentina o con Marco?") is implemented.

### Time Slots / Availability
**Score: ✅ DONE**

`AvailabilityChecker` called at L2 when date selected. If slot unavailable: offers alternatives → `WAITING_TIME` reset, or proposes waitlist. Slot display shown via `ask_time_with_slots` template (line 501).

### Recurring Bookings
**Score: ❌ MISSING**

No state, no pattern, no DB call for recurring/periodic appointments. No concept of "ogni lunedì" or "stesso giorno ogni mese".

---

## B. DISAMBIGUATION

### Phonetic (Gino/Gigio, Maria/Mario)
**Score: ✅ DONE**

`PHONETIC_VARIANTS` dict (lines 118-132, disambiguation_handler.py) covers 12 name groups. `is_phonetically_similar()` (line 72) checks PHONETIC_VARIANTS first, then falls back to Levenshtein similarity (threshold 0.75).

`check_name_ambiguity()` (line 135) fires for single-match results when input similarity ≥ 0.85. Triggers birth-date confirmation.

Structural gap: PHONETIC_VARIANTS is static — no Roberto/Roberta, no Francesca/Francesco gender flip support (only one direction covered at line 127-128). The dict is asymmetric in places.

### Service Disambiguation
**Score: ❌ MISSING**

When user says an ambiguous term (e.g., "trattamento" could be cheratina/botox/ricostruzione), the FSM accepts the generic term and passes it forward without prompting for clarification. No `service_disambiguation` state exists.

### Date Disambiguation
**Score: ✅ DONE**

`is_ambiguous_date()` (italian_regex.py line 584) detects vague references ("prossima settimana", "tra due settimane"). When detected, FSM skips date extraction and prompts for a specific day. Implemented via `_update_context_from_extraction()` (lines 912-916 of booking_state_machine.py).

### Time Disambiguation
**Score: ⚠️ PARTIAL**

Approximate times ("mattina", "pomeriggio") resolved to fixed slots via `TimeSlot` enum (entity_extractor.py lines 38-46). Sara confirms the mapped time. No resolution when user says "non troppo presto" or "dopo pranzo ma non troppo tardi".

---

## C. RESCHEDULE / CANCEL

### Cancel Flow
**Score: ⚠️ PARTIAL**

CANCELLAZIONE intent detected at L1 (orchestrator.py lines 722-788). If client_id known: fetches appointments via HTTP Bridge → `_get_client_appointments()`. Handles 0/1/many results. User selects appointment by date. Confirmation requested.

DB update: `_cancel_appointment_db()` calls HTTP Bridge. No SQLite fallback for cancel DB write (only HTTP Bridge). If Bridge is offline, cancel fails silently.

Gap: no "undo cancel" flow. No notification sent when appointment cancelled.

### Reschedule Flow
**Score: ⚠️ PARTIAL**

SPOSTAMENTO intent detected at L1 (lines 791-855). Same pattern as cancel: asks for new date, then time. `_handle_reschedule_flow()` called in L2.5 block (line 1206).

Gap: same HTTP Bridge dependency for DB write. No SQLite fallback.

Gap: the SPOSTAMENTO pattern in `intent_classifier.py` (line 411):
```python
r"(sposta|spostare|cambia|cambiare|modifica|modificare)\s+(l[ao]?\s+)?(appuntament|prenotazion|data|ora|orario)?"
```
The trailing `?` on the object group fires on "cambiare le gomme" → false SPOSTAMENTO. Documented in f02-nlu-comprehensive-patterns.md.

### No-Show Handling
**Score: ❌ MISSING**

No no-show state, no "sei sicuro di voler cancellare?" escalation for last-minute cancel, no penalty warning triggered via voice.

---

## D. WAITLIST

### Add to Waitlist
**Score: ✅ DONE**

`PROPOSING_WAITLIST` state and `WAITLIST_SAVED` state implemented. `waiting_for_waitlist_confirm` flag in context (line 153). Triggered when slot unavailable (orchestrator.py line 952). `_add_to_waitlist()` called via HTTP Bridge.

### Notification When Slot Opens
**Score: ❌ MISSING**

Sara adds the client to the waitlist table. But there is no mechanism in the voice agent to notify the client when a slot opens. Notification would require a background polling job (not present) or Tauri-side logic (not implemented in voice layer). This is a known open gap.

---

## E. CLIENT RECOGNITION

### New vs Returning
**Score: ✅ DONE**

`WAITING_NAME` handler checks `NEW_CLIENT_INDICATORS` (booking_state_machine.py line 1099). Returning client: DB lookup by name (SQLite fallback available). New client: `PROPOSE_REGISTRATION` → guided registration flow.

`booking_sm.reset()` uses soft reset by default (preserves client_id/name/phone across bookings in the same session) — fix implemented at lines 595-622.

### VIP Handling
**Score: ❌ MISSING**

`BookingContext` has no VIP flag. PHONETIC_VARIANTS has a soprannome system but no VIP priority queue. Waitlist code in orchestrator.py references "VIP priority" in docstring but `_add_to_waitlist()` passes no priority parameter to DB.

### Nickname Support
**Score: ⚠️ PARTIAL**

`PHONETIC_VARIANTS` enables phonetic matching. `check_nickname_match()` (disambiguation_handler.py line 705) returns a synthetic client dict. `_get_unique_identifiers()` (line 573) prefers soprannome field if present in DB.

Gap: no nickname stored at registration time. No "soprannome" collected during `REGISTERING_CONFIRM` flow.

---

## F. VERTICAL AWARENESS

### Guardrails
**Score: ✅ DONE (F02 implemented)**

`check_vertical_guardrail()` (italian_regex.py line 816) fires at L0-PRE before any other layer. 4 verticals × ~12 patterns each, pre-compiled. Redirect responses are vertical-specific.

Known gap (from f02-nlu-comprehensive-patterns.md): guardrails are noun-phrase only — no verb form patterns ("cambiare" in salone context would not be blocked). Single-word out-of-scope terms like "yoga" alone are not blocked (only "corso di yoga" multi-word).

### Entity Extraction Per Vertical
**Score: ⚠️ PARTIAL**

`extract_vertical_entities()` (entity_extractor.py line 1433) handles:
- medical: specialty (10 specialties), urgency (3 levels), visit_type (5 types)
- auto: vehicle_plate (regex), vehicle_brand (38 brands)
- salone: nothing beyond generic entity extraction
- palestra: nothing beyond generic entity extraction

Entities stored in `booking_sm.context.extra_entities` (orchestrator.py lines 560-568) as a dict. The FSM states do NOT read from `extra_entities`. The data is extracted and stored but never acted upon in subsequent turns. This is a data dead-end.

### FAQ Per Vertical
**Score: ✅ DONE**

Each vertical has `faqs.json` with keyword-indexed answers. `vertical_loader.py` loads FAQ by vertical key. `FAQManager` loaded at session start.

Gap: FAQ answers are static hardcoded strings (e.g., salone faq_orari says "martedì al sabato: ... dalle 9:00 alle 19:00"). These do not pull from the DB. If the business changes their hours, the FAQ is stale.

---

## G. WHATSAPP INTEGRATION

### Reminder Sending
**Score: ⚠️ PARTIAL**

`WhatsAppClient` initialized in orchestrator. `_send_wa_booking_confirmation()` called fire-and-forget after booking creation (orchestrator.py lines 971-975). Second safety-net call at call-close (line 1417-1420).

`_last_booking_data` now includes `client_name` and `client_phone` (fix in P1 session).

Gap: no scheduled reminder (e.g., 24h before appointment). WhatsApp confirmation is sent immediately after booking, not at appointment time minus 24h. No cron/scheduler exists in voice agent.

### Confirm/Cancel Callbacks
**Score: ✅ DONE**

`whatsapp_callback.py` handles POST from whatsapp-service.cjs. `CONFIRM_PATTERN` and `CANCEL_PATTERN` (lines 33-41) cover Italian affirmatives/negatives. `_mark_confirmed()` and `_cancel_appointment()` update DB directly via sqlite3. `_lookup_pending_appointment()` falls back to SQLite if session not in memory.

Rate limit: 3 msg/min per phone (line 94). Dedup cache: 24h TTL (line 404).

Gap: cancel via WhatsApp does NOT trigger voice-agent-side cancel flow. It only sets `stato = 'cancellato'` in DB. No follow-up message like "Vuole riprennotare?"

### Free Text Handling
**Score: ✅ DONE**

`_handle_free_text()` (line 285) forwards to full orchestrator pipeline via `start_session()` + `process()`. WhatsApp session maintains `WAPhoneSession` with 30-minute expiry.

Gap: WhatsApp session has no memory of previous booking context across sessions (30-min timeout hard-coded, no persist to SQLite).

---

## H. ERROR RECOVERY

### Graceful Degradation
**Score: ✅ DONE**

- HTTP Bridge offline: SQLite fallback for client search, config load
- Groq timeout: caught at orchestrator.py lines 1351-1354, returns "sto impiegando troppo"
- Groq rate limit (429): caught at lines 1356-1362, returns "momentaneamente sovraccarica"
- Groq unexpected: caught lines 1370-1374
- STT low confidence: `handle_input_with_confidence()` (booking_state_machine.py line 648) returns repeat request if score < 0.7

### Fallback to Human
**Score: ⚠️ PARTIAL**

Escalation response is "La metto in contatto con un operatore, un attimo...". `should_escalate=True` and `should_exit=True` are set. WhatsApp escalation call triggered via `_trigger_wa_escalation_call()`.

Gap: actual human-transfer mechanism is WhatsApp only. If WA client is None or offline, escalation is announced verbally but nothing concrete happens. No SIP transfer, no callback queuing.

### When Nothing Matches
**Score: ⚠️ PARTIAL**

Falls through to Groq (L4). If Groq fails too: returns Italian "ho avuto un problema tecnico". No "I'll have a human call you back" fallback after L4 failure.

---

## I. MULTI-TURN CONTEXT

### Within Session
**Score: ✅ DONE**

`BookingContext` persists across turns via `self.booking_sm.context`. Soft reset on new booking preserves client identity (client_id, name, phone, email). `_current_session` maintained per orchestrator instance.

`session_manager.add_turn()` (line 1385) records each turn. `_last_response` stored for "repeat" command.

### Across Sessions (Persistence)
**Score: ⚠️ PARTIAL**

`SessionManager` persists to `~/.fluxion/voice_sessions.db` (SQLite). Sessions expire (TTL managed). Recovery on restart via `_recover_sessions()`.

Gap: BookingContext slot state is NOT persisted across sessions. If call drops mid-booking, the FSM state (WAITING_TIME, etc.) is lost. Only session metadata (session_id, outcome) persists. The client must restart from scratch.

---

## J. OPERATOR ROUTING

### Preferred Operator
**Score: ⚠️ PARTIAL**

`extract_operator()` extracts a name from "con Mario" / "da Valentina" patterns. Stored in `context.operator_name`. Passed to `_create_booking()` as `operatore`.

Gap: no validation that the extracted operator name exists in DB. "con chiunque" or "con qualsiasi" → `operator_name` is set to that phrase verbatim.

### Operator Availability
**Score: ❌ MISSING**

`_search_operators()` returns the operator list but does NOT check operator availability for a specific date/time. The availability check (`_check_slot_availability()`) does NOT filter by operator schedule.

### Operator Skills
**Score: ❌ MISSING**

No operator-skill mapping. "Chi fa la cheratina?" would fall to Groq (L4). No skills table queried.

---

## K. LATENCY PROFILE

### Current Estimates (from code analysis, not live measurement)

| Layer | Target | Actual | Notes |
|-------|--------|--------|-------|
| L0 Pre-filter (regex) | <1ms | <1ms | Pre-compiled patterns |
| L0 Guardrail | <2ms | <2ms | Pre-compiled per vertical |
| L0 Sentiment | <5ms | <5ms | Keyword-based, no ML |
| L1 Intent (exact match) | <1ms | <1ms | O(1) dict lookup |
| L1 Intent (pattern) | <20ms | <20ms | ~15 regex patterns per category |
| L2 FSM + entity extract | <10ms | ~15-25ms | Multiple regex passes |
| L2 HTTP Bridge lookup | <200ms | 50-500ms | Variable: HTTP call or SQLite |
| L3 FAQ retrieval | <50ms | <50ms | Keyword scan |
| L4 Groq | <500ms | 400-800ms | Network-dependent |
| TTS synthesis | — | 200-400ms | Piper local |

**Known bottleneck**: Every booking turn that needs a DB lookup goes through HTTP Bridge first (5s timeout before SQLite fallback). On Bridge-offline scenarios, this adds 5 seconds per lookup. Orchestrator.py `_search_client()` timeout is `aiohttp.ClientTimeout(total=5)` (line 1709).

**P95 estimate**: ~1330ms (per MEMORY.md). STT adds another 30s (Whisper ggml-small on iMac). E2E including STT is completely outside target.

---

## L. LANGUAGE QUALITY

### Italian Naturalness
**Score: ✅ DONE**

Templates use natural Italian (lines 496-552, booking_state_machine.py). No robotic "ENTER DATE" style prompts. Responses are conversational.

### Formality (Lei vs tu)
**Score: ⚠️ PARTIAL**

Templates consistently use "Lei" form (formal). Greetings in CORTESIA_EXACT use "Le" for formal and "ti/ti" for informal based on the input word (e.g., "ciao" → "come posso aiutarti?", "buongiorno" → "come posso aiutarla?"). Good situational switching.

Gap: Groq system prompt (line 1664) instructs Sara to use "Lei" always, but there is no injection of formality preference from context. If user switches to informal ("ciao, sei figa eh"), Groq might mirror informal mode inconsistently.

### Regional Expressions
**Score: ❌ MISSING**

No regional variant handling. Sicilian "mi dà" / Neapolitan "mo" / Milanese "adess" → not in any synonym list. These fall to Groq if they appear.

---

## M. EDGE CASES

### Long Pauses / Background Noise
**Score: ❌ MISSING**

VAD (Silero ONNX) implemented in `vad_wrapper.py`. VAD detects end-of-speech. But there is no timeout handler for long silence — if user goes silent, the pipeline hangs waiting for input. No "Ci sei?" prompt after N seconds of silence.

### Customer Getting Angry
**Score: ✅ DONE (with gaps)**

`SentimentAnalyzer` tracks cumulative frustration (5-turn window). Escalation threshold = 6 cumulative points. Sentiment escalation suppressed during active booking (orchestrator.py line 629-645, FIX-1 CoVe2026).

Gap: "basta" alone scores 4 points → immediate escalation. But "aspetta un attimo, basta con sto colore" (legitimate correction) also hits "basta" (weight 4). No context-sensitivity on individual high-weight keywords.

### Kids in Background
**Score: ❌ MISSING**

No background noise classification. If a child says "voglio il gelato" in the background, the STT transcribes it and the pipeline processes it as user input. No speaker diarization.

### STT Artifacts
**Score: ✅ DONE**

`strip_fillers()` (italian_regex.py line 57) removes "ehm", "uhm", "allora", "dunque", etc. CORTESIA_ALIASES handles STT typos ("buongorno" → "buongiorno", "grazzie" → "grazie").

---

## N. ANALYTICS

### What Is Tracked
**Score: ✅ DONE**

`ConversationLogger` (analytics.py) writes to `~/.fluxion/voice_analytics.db`.

Per-turn: `user_input`, `intent`, `intent_confidence`, `response`, `latency_ms`, `layer_used`, `sentiment`, `frustration_level`, `used_groq`, `escalated`, `entities_extracted` (JSON).

Per-session: `verticale_id`, `outcome`, `total_turns`, `total_latency_ms`, `groq_usage_count`, `escalation_reason`, `booking_created`, `booking_id`, `user_satisfaction`.

VoIP call logs: separate `voip_calls` table with duration, RTP packet counts, audio quality score (MOS).

FAQ effectiveness: `faq_effectiveness` table (was_helpful flag — but never actually set to True/False by orchestrator).

### What Is Not Tracked
- Which booking_state transitions occurred (no FSM path logging)
- Which guardrail blocked which query
- Service requested vs service booked (mismatch rate)
- Client disambiguation outcome
- WhatsApp confirmation delivery status
- `user_satisfaction` is in schema but never populated (no post-call survey mechanism)

### What Decisions It Enables
- `get_failed_queries()` returns inputs that triggered Groq/low-confidence/frustration → enables FAQ gap identification
- `get_escalation_reasons()` aggregates escalation types → enables frustration root cause analysis
- Layer usage distribution → enables latency optimization targeting
- `get_latency_stats()` → P50/P95 computation available but not surfaced in UI

---

## Summary Score Card

| Area | Score | Critical Gap |
|------|-------|-------------|
| A. Booking Flow (single) | ✅ | multi-service second service dropped |
| A. Booking Flow (multi-service) | ⚠️ | only first service sent to DB |
| A. Booking Flow (recurring) | ❌ | not implemented |
| B. Disambiguation (phonetic) | ✅ | static dict, incomplete |
| B. Disambiguation (service) | ❌ | no "which trattamento?" flow |
| B. Disambiguation (date/time) | ✅ | approximate times fixed |
| C. Reschedule/Cancel | ⚠️ | Bridge-only DB write, no SQLite fallback |
| D. Waitlist | ✅ / ❌ | add works, notification absent |
| E. Client Recognition | ✅ | no VIP, no nickname at registration |
| F. Vertical Guardrails | ✅ | noun-only, verb forms bypass |
| F. Vertical Entity Extraction | ⚠️ | extracted but not used by FSM |
| G. WhatsApp (reminder) | ⚠️ | immediate send only, no scheduled reminder |
| G. WhatsApp (callbacks) | ✅ | confirm/cancel work |
| H. Error Recovery | ✅ | WA escalation hollow if offline |
| I. Multi-turn Context | ✅ | FSM state not persisted across sessions |
| J. Operator Routing | ⚠️ | no availability/skills check |
| K. Latency | ⚠️ | P95 ~1330ms (target 800ms); STT ~30s |
| L. Language Quality | ✅ | no regional expressions |
| M. Edge Cases | ⚠️ | no silence timeout, no speaker diarization |
| N. Analytics | ✅ | satisfaction never populated |

---

## Top 10 Actionable Gaps (by impact)

1. **LATENCY** — Groq route P95 ~1330ms. Worst path: HTTP Bridge timeout (5s) + Groq (800ms). Fix: reduce Bridge timeout to 1s, add aggressive SQLite caching.
2. **STT** — Whisper ggml-small on iMac CPU: ~30s. Must switch to ggml-tiny or Groq STT cloud for real-time use.
3. **MULTI-SERVICE DB** — Second+ services silently dropped. Need to either loop bookings or aggregate services into one record.
4. **CANCEL/RESCHEDULE NO SQLite fallback** — Bridge offline = cancel fails with no user feedback. Add SQLite write fallback.
5. **OPERATOR AVAILABILITY** — Operator preference accepted but not validated against schedule. Booking may be created for an operator on their day off.
6. **VERTICAL ENTITY DEAD-END** — Medical specialty, urgency, visit_type extracted but never read by FSM states. These fields must drive prompts and DB booking fields.
7. **SILENCE TIMEOUT** — No "Ci sei?" prompt. Pipeline hangs indefinitely on user silence.
8. **SCHEDULED WA REMINDER** — Immediate confirmation sent, but no 24h-before reminder. This is the highest-value WhatsApp feature for no-show reduction.
9. **FAQ STALE DATA** — FAQ answers are static strings. Business hours, prices, services must pull from DB at runtime, not from faqs.json at startup.
10. **SERVICE DISAMBIGUATION** — "trattamento" accepted without clarifying "cheratina, botox, o maschera?". Creates booking with generic service name that the calendar won't render correctly.

---

## Test Coverage Analysis

| Category | Test File | Test Count | Coverage |
|----------|-----------|------------|---------|
| Booking FSM | test_booking_state_machine.py | 70 | High |
| Entity extraction | test_entity_extractor.py | 63 | High |
| Italian regex | test_italian_regex.py | 55 | Medium |
| WhatsApp | test_whatsapp.py | 52 | Medium |
| Disambiguation | test_disambiguation.py | 49 | High |
| Vertical corrections | test_vertical_corrections.py | 46 | Medium |
| Guardrails | test_guardrails.py | 33 | Medium |
| Voice agent complete | test_voice_agent_complete.py | 34 | Medium |
| Analytics | test_analytics.py | 34 | Medium |
| Error recovery | test_error_recovery.py | 30 | Medium |
| Guided dialog | test_guided_dialog.py | 38 | Medium |
| Cancel/reschedule | test_cancel_reschedule.py | 22 | Low |
| Vertical entity extractor | test_vertical_entity_extractor.py | 25 | Medium |
| VOIP | test_voip.py | 39 | Unknown (iMac only) |

**Not tested at all**:
- Silence timeout (does not exist in code)
- Scheduled WA reminders (not implemented)
- No-show handling (not implemented)
- Multi-service DB write correctness
- Operator availability validation
- Vertical entity → FSM slot pipeline

**Total: 897 test functions across 39 files. 1160 reported passing on iMac (includes integration tests that need live DB).**

---

## Key Line References

| Topic | File | Line |
|-------|------|------|
| BookingState enum (23 states) | booking_state_machine.py | 73-102 |
| BookingContext dataclass | booking_state_machine.py | 110-170 |
| TEMPLATES dict | booking_state_machine.py | 496-552 |
| FSM dispatch | booking_state_machine.py | 744-813 |
| Soft reset (P1 fix) | booking_state_machine.py | 595-622 |
| Pipeline layers (L0-L4) | orchestrator.py | 507-1374 |
| Sentiment guard during booking | orchestrator.py | 629-645 |
| Fire-and-forget WA | orchestrator.py | 971-975 |
| HTTP Bridge timeout 5s | orchestrator.py | 1709 |
| Groq system prompt | orchestrator.py | 1664-1685 |
| PHONETIC_VARIANTS | disambiguation_handler.py | 118-132 |
| VERTICAL_SERVICES dict | italian_regex.py | 218-284 |
| VERTICAL_GUARDRAILS dict | italian_regex.py | 726-798 |
| CORTESIA_EXACT (50+ phrases) | intent_classifier.py | 79-216 |
| INTENT_PATTERNS | intent_classifier.py | 371-471 |
| extract_vertical_entities | entity_extractor.py | 1433-1483 |
| FRUSTRATION_KEYWORDS | sentiment.py | 61-100 |
| WORD_BOUNDARY_KEYWORDS | sentiment.py | 105-108 |
| WA confirm/cancel patterns | whatsapp_callback.py | 33-41 |
| Rate limit 3/min | whatsapp_callback.py | 94 |
| ConversationLogger schema | analytics.py | 103-198 |
