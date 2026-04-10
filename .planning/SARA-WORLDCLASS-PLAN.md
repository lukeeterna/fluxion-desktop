# SARA World-Class Plan — Merged Research + Audit S142

## Sources Merged
1. Voice Agent World-Class 2026 (deep research) — VALIDATED: 60-85% already exists
2. Voice Agent Humanness 2026 (deep research) — VALIDATED: 3/6 confirmed missing, 3/6 partial
3. S142 Audit: FSM (15 bugs), NLU (7 bugs), RAG (3 critical), VoIP (17 issues), UX (11 friction points)
4. VoIP ISP Compatibility (all Italian ISP types)
5. Feasibility Analysis (voice-engineer + compatibility research)
6. Codebase Validation (explore agent — file:line evidence for each claim)

## Current State: Level 1-2 (Functional + Partially Fluid)
## Target: Level 4 (Personalized) — realistic for 2026 launch

---

## PHASE A: Quick Wins (10h) — Latency + Polish
> Goal: P95 latency <800ms, greeting 0ms, goodbye bulletproof

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| A1 | Edge-TTS streaming (`stream()` vs `save()`) | tts_engine.py | 3h | -300ms perceived |
| A2 | Greeting pre-synthesis with business_name | tts.py + main.py | 2h | Greeting 0ms |
| A3 | Silence timeout 1500ms→1000ms | voip_pjsua2.py | 2h | -500ms/turn |
| A4 | FSM state per turn in analytics | analytics.py | 1h | Debug capability |
| A5 | Auto-summary post-call via Groq | analytics.py + orchestrator.py | 3h | Business value |

## PHASE B: Humanness Core (12h) — Level 2→3
> Goal: Sara sounds natural, not robotic

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| B1 | Filler pre-DB-lookup ("Un momento...") | orchestrator.py | 1h | No silence during lookup |
| B2 | Mirror in confirmation (name + slot echo) | booking_state_machine.py | 1h | Perceived listening |
| B3 | Goodbye variants by context | intent_classifier.py + orchestrator.py | 1h | Not repetitive |
| B4 | Backchannel engine ("Capisco.", "Certo.") | NEW backchannel_engine.py + voip_pjsua2.py | 3h | +40% naturalness |
| B5 | Tone adapter (neutral/frustrated/positive) | NEW tone_adapter.py + orchestrator.py | 5h | Adaptive UX |
| B6 | Prosody injection (SSML pauses + rate) | NEW prosody_injector.py + tts_engine.py | 4h | Uncanny valley |

## PHASE C: Memory + Personalization (8h) — Level 3→4
> Goal: Sara remembers returning callers

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| C1 | caller_memory SQLite table | NEW caller_memory.py | 2h | Cross-call persistence |
| C2 | Phone number extraction from SIP INVITE | voip_pjsua2.py + orchestrator.py | 1h | Caller identification |
| C3 | Personalized greeting for returning callers | session_manager.py + orchestrator.py | 2h | "Bentornato Mario!" |
| C4 | Preferred slot suggestion | booking_state_machine.py + caller_memory.py | 3h | "Di solito martedì 10:00" |

## PHASE D: Audit Backlog P0 (10h) — Reliability
> Goal: No hallucination, no stuck states, CGNAT support

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| D1 | L4 Groq guardrail anti-hallucination | orchestrator.py | 3h | No fake availability |
| D2 | Conversation history (last 3 turns to L4) | orchestrator.py | 2h | Context preserved |
| D3 | FAQ unresolved variables logging + fix | faq_manager.py + orchestrator.py | 2h | Complete FAQ |
| D4 | TURN server (coturn Oracle Free Tier) | voip_pjsua2.py + config | 5h | 20% more PMI supported |

## PHASE E: Audit Backlog P1 (15h) — Robustness
> Goal: All FSM paths work, graceful escalation

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| E1 | Clean dead FSM states (8 of 23) | booking_state_machine.py | 3h | Cleaner code |
| E2 | Exit path from registration | booking_state_machine.py | 2h | No infinite loops |
| E3 | Slot suggestion (1 slot, not list of 3) | booking_state_machine.py | 2h | Fewer turns |
| E4 | Remove ASKING_CLOSE_CONFIRMATION | booking_state_machine.py + orchestrator.py | 2h | -1 turn |
| E5 | Graceful escalation with context handoff | NEW escalation_manager.py | 3h | Human gets summary |
| E6 | Global 3-strike escalation counter | orchestrator.py | 2h | Auto-escalate |
| E7 | UDP keepalive 15s for CGNAT | voip_pjsua2.py | 1h | NAT traversal |

## PHASE F: Advanced (12h) — Level 4 Polish
> Goal: World-class edge cases

| # | Task | File | Hours | Impact |
|---|------|------|-------|--------|
| F1 | LiveKit EOU ONNX direct (text-based) | NEW eou_detector.py + voip_pjsua2.py | 4h | -30% interruptions |
| F2 | Acoustic frustration (RMS + speech rate) | sentiment.py + voip_pjsua2.py | 8h | Implicit frustration |

---

## SCHEDULING — Sprint Order

### Sprint S143-S144: Phase A + B1-B3 (13h)
Quick wins + basic humanness. Testable immediately.

### Sprint S145-S146: Phase C + D (18h) 
Memory + reliability. Biggest UX leap.

### Sprint S147-S148: Phase B4-B6 + E (27h)
Advanced humanness + robustness.

### Sprint S149+: Phase F (12h)
Polish and advanced features.

---

## METRICS TO TRACK

| Metric | Current | Target Phase A | Target Phase C |
|--------|---------|---------------|----------------|
| Greeting latency | ~500ms | 0ms | 0ms |
| P95 turn latency | ~4600ms | <2000ms | <1500ms |
| Turns per booking | 6-8 | 5-6 | 3-4 |
| Goodbye exit rate | ~60% | 95% | 99% |
| False interruptions | ~20% | ~15% | ~10% |
| Returning caller recognition | 0% | 0% | 90% |
| CSAT (estimated) | Level 1-2 | Level 2 | Level 4 |
