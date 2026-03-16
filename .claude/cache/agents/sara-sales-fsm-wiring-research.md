# Sara Sales FSM Wiring — Research & Architecture Proposal

> Date: 2026-03-16 | Status: RESEARCH ONLY

---

## 1. Current Architecture Summary

### 1.1 Booking FSM (`booking_state_machine.py` — 3706 lines)

**BookingState enum** — 23 states:
- **Core flow**: IDLE -> WAITING_NAME -> WAITING_SERVICE -> WAITING_DATE -> WAITING_TIME -> WAITING_OPERATOR -> CONFIRMING -> COMPLETED/CANCELLED
- **Identity**: WAITING_SURNAME, CONFIRMING_PHONE
- **Registration**: PROPOSE_REGISTRATION -> REGISTERING_SURNAME -> REGISTERING_PHONE -> REGISTERING_CONFIRM
- **Waitlist**: CHECKING_AVAILABILITY -> SLOT_UNAVAILABLE -> PROPOSING_WAITLIST -> CONFIRMING_WAITLIST -> WAITLIST_SAVED
- **Disambiguation**: DISAMBIGUATING_NAME, DISAMBIGUATING_BIRTH_DATE
- **Close**: ASKING_CLOSE_CONFIRMATION

### 1.2 Orchestrator (`orchestrator.py` — 3441 lines)

Pipeline `process()` (line 556) — cascading `if response is None`:
1. **L0-PRE**: Content filter, escalation, vertical guardrail, entity extraction, medical urgency
2. **L0**: Special commands (aiuto, operatore, annulla)
3. **L0a**: WhatsApp FAQ intercept
4. **L0b**: Advanced NLU (spaCy)
5. **L0c**: Sentiment analysis
6. **L1**: Intent classification
7. **L2**: Disambiguation + Booking FSM (slot filling)
8. **L2.5**: Cancel/Reschedule flow
9. **L3**: FAQ retrieval
10. **L3.5**: Guided dialog
11. **L4**: Groq LLM fallback

### 1.3 Sales Dataset Structure

- `product_pitch` — 8 verticals with headline/pitch/key_number
- `objections` — 15 handlers with trigger_phrases + response
- `qualification_questions` — 6 sequential questions
- `closing_messages` — 3 tiers (base 497/pro 897/clinic 1497) + checkout URLs
- `followup_messages` — 5 templates (24h, 48h, 7d, post_purchase)
- `pain_points_by_vertical` — 8 verticals, 5-6 points each
- `competitive_comparison` — vs Fresha, Treatwell, Google Calendar, paper agenda
- `sara_personality_sales` — tone rules, 15 forbidden words, preferred replacements

---

## 2. Design Decision: Separate Module (RECOMMENDED)

### Option B: New SalesStateMachine class + SalesContext
- Parallel FSM in `sales_state_machine.py` with its own enum, context, dispatch
- Zero risk of regression on 1910+ existing tests
- Complete isolation from booking flow

---

## 3. Proposed SalesState Enum

```
IDLE
QUALIFYING_VERTICAL        # "Che tipo di attivita hai?"
QUALIFYING_EMPLOYEES       # "Quanti siete?"
QUALIFYING_VOLUME          # "Quanti appuntamenti al giorno?"
QUALIFYING_TOOL            # "Come gestisci le prenotazioni?"
QUALIFYING_PAIN            # "Quante chiamate perdi?"
PITCHING                   # Vertical-specific pitch delivery
HANDLING_OBJECTION         # Objection response from KB
CLOSING                    # Tier recommendation + checkout URL
FOLLOWUP_SCHEDULED         # WA followup queued
COMPLETED                  # Lead converted or gracefully exited
DECLINED                   # Lead said no definitively (3+ objections)
```

## 4. Tier Logic

- employees 1-2, no voice need -> Base (497)
- employees 3-8 OR wants Sara voice -> Pro (897)
- employees 9+ OR medical/clinic -> Clinic (1497)

## 5. Entry Point

New endpoint `/api/sales/process` in main.py.
New `process_sales()` method in orchestrator (NOT branching inside existing process()).
Detection: phone unknown + wa.me link click -> sales mode.

## 6. Integration (minimal changes to existing code)

- `orchestrator.py` — ~100 lines added (process_sales method)
- `main.py` — ~30 lines (3 new endpoints)
- `session_manager.py` — 1 line (SALES_WHATSAPP channel)
- **ZERO changes to booking_state_machine.py**

## 7. New Files

```
voice-agent/src/sales_state_machine.py     # ~500 lines
voice-agent/src/sales_kb_loader.py         # ~100 lines
voice-agent/tests/test_sales_fsm.py        # 40+ tests
```

## 8. Risks & Edge Cases

- **Mode confusion**: Lead says "vorrei prenotare" = PURCHASE intent, not booking
- **Re-entry**: Same phone re-contacts → load from sales_leads table
- **Price before qualification**: "quanto costa" → give range, then qualify
- **Forbidden words via Groq L4**: Post-filter sanitize_sales_response()
- **WhatsApp rate limits**: 60 msg/hour, scheduling needed for mass outreach

## 9. Open Questions for Founder

1. Voice or WhatsApp-only for sales?
2. Session timeout → auto-schedule followup?
3. Outbound or inbound only?
4. CRM: HubSpot Free or local SQLite first?
