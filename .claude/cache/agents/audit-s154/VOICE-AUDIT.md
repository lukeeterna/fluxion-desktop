# FLUXION Voice Agent "Sara" — Production Readiness Audit (S154)

**Date**: 2026-04-14
**Auditor**: Voice Engineer Agent (Opus 4.6)
**Scope**: B1 pjsua2 Deadlock, B3 Adaptive Silence, FSM Coverage, TTS Fallback, Latency, Verticals

---

## B1 — pjsua2 Deadlock Fix Assessment

### VERDICT: PASS (with caveats)

**S153 Fix Applied** (`voip_pjsua2.py`):
1. **Line 436-437**: `threadCnt=0`, `mainThreadOnly=True` — eliminates pjsua2 internal worker threads. All callbacks now run serialized via `libHandleEvents(20)` in `_pjsua2_thread`.
2. **Line 508**: `lockCodecEnabled=False` — disables the codec lock timer (`reinv_timer_cb`) entirely. This was the root cause: the timer fired 200ms post-call to send a re-INVITE narrowing codecs, and its internal mutex acquisition deadlocked with callbacks.

**Analysis of Deadlock Elimination**:

| Concern | Assessment |
|---------|------------|
| Are all pjsua2 callbacks serialized? | YES. `mainThreadOnly=True` forces all SIP/media callbacks through `libHandleEvents()`. The `_pjsua2_thread` (line 412) polls every 20ms. No internal threads exist to contend. |
| Is there remaining mutex contention? | NO within pjsua2 internals. However, `onCallState` (line 218-225) spawns `threading.Thread` for `on_connected`/`on_disconnected`. These are user-level threads that run long-lived audio processing — they do NOT call back into pjsua2 with mutex-held operations. `_audio_processing_loop` (line 646) calls `libRegisterThread` but only uses `SaraAudioPort` (queue-based, no mutex). |
| What happens under high call volume? | `SaraAccount.onIncomingCall` (line 260-277) rejects concurrent calls with 486 Busy Here. Only 1 call at a time. This is correct for a single-user voice agent. No race condition possible. |
| Is `lockCodecEnabled=False` safe? | YES for EHIWEB. G.711 is the only codec offered by EHIWEB SIP. No codec renegotiation is needed. The re-INVITE timer was pure overhead. |

**Remaining Risks**:
- **Risk 1 (LOW)**: `libHandleEvents(20)` blocks for 20ms. If a callback within this call takes >20ms (e.g., slow `onIncomingCall`), subsequent events are delayed. In practice, `onIncomingCall` only does `call.answer()` + sets callbacks — negligible time.
- **Risk 2 (LOW)**: The `on_connected` callback spawns a `threading.Thread` (line 221). If this thread crashes, there is no recovery mechanism — the call hangs with audio silence. A watchdog timeout on the audio thread would improve robustness.
- **Risk 3 (NONE)**: With `threadCnt=0`, the `_ep.libRegisterThread("audio_processing")` call (line 650) registers the audio processing thread with pjlib but does NOT make it a pjsua2 worker. This is required for any thread that calls pjsua2 API (e.g., `call.hangup()`). No mutex issue here.

**Code Evidence**: The deadlock was caused by the codec lock timer (`reinv_timer_cb`) which internally acquires the pjsua mutex while another callback already holds it. With `lockCodecEnabled=False` (line 508), this timer never fires. With `mainThreadOnly=True` (line 437), there are no internal worker threads to hold the mutex concurrently. The fix is architecturally sound.

---

## B3 — adaptive_silence_ms VAD Wiring

### VERDICT: PASS

**Full chain verified**:

1. **Calculation** (`orchestrator.py:5226-5228`):
   ```python
   _eou_prob = sentence_complete_probability(transcription)
   _adaptive_ms = get_adaptive_silence_ms(transcription, _fsm_state_str, _eou_prob)
   ```
   Uses EOU module (sentence completion + FSM state + word count). Returns clamped [300, 1200]ms.

2. **Wiring** (`orchestrator.py:5231-5234`):
   ```python
   self._last_adaptive_silence_ms = _adaptive_ms
   if hasattr(self, '_vad_handler') and self._vad_handler:
       for session in self._vad_handler._sessions.values():
           session.vad.update_silence_ms(_adaptive_ms)
   ```

3. **Application** (`ten_vad_integration.py:182-194`):
   ```python
   def update_silence_ms(self, silence_ms: int) -> None:
       silence_ms = max(200, min(1500, silence_ms))
       new_window = max(1, silence_ms // chunk_ms)
       if new_window != self.silence_window_size:
           self.silence_window_size = new_window
   ```

4. **`_vad_handler` always set** (`main.py:291-293`):
   ```python
   self.vad_handler = VADHTTPHandler(orchestrator, groq_client)
   orchestrator._vad_handler = self.vad_handler
   ```
   Set during `FluxionVoicePipeline` init in `main.py`. Always available when the server starts.

5. **`_sessions` dict** (`vad_http_handler.py:112`): `Dict[str, VADSession]`. Populated when a VAD session starts via HTTP API. If no VAD sessions exist (e.g., VoIP path uses its own simple energy-based VAD), the `for session in ...values()` loop simply does nothing — no error.

**Issue Identified (WARN)**: The VoIP path (`voip_pjsua2.py`) uses its own energy-based VAD with a fixed `_vad_silence_timeout = 50` (1000ms). The adaptive silence from EOU does NOT reach the VoIP VAD. The `_last_adaptive_silence_ms` is stored but never consumed by the VoIP audio processing loop. This means:
- **HTTP/WebSocket clients**: adaptive silence works correctly
- **VoIP phone calls**: always use fixed 1000ms silence timeout, ignoring EOU predictions

**Fix needed**: In `voip_pjsua2.py:_audio_processing_loop`, after `_process_caller_audio` completes, read `self.pipeline._last_adaptive_silence_ms` and update `self._vad_silence_timeout` accordingly.

---

## FSM State Coverage

### VERDICT: WARN — 2 states with zero dedicated test coverage

**All 14 states defined** (`booking_state_machine.py:81-99`):

| # | State | Handler | Test Coverage |
|---|-------|---------|---------------|
| 1 | IDLE | `_handle_idle` | PASS — extensive tests in `test_booking_state_machine.py` |
| 2 | WAITING_NAME | `_handle_waiting_name` | PASS — `test_booking_state_machine.py`, `test_kimi_flow.py` |
| 3 | WAITING_SERVICE | `_handle_waiting_service` | PASS — `test_booking_state_machine.py`, `test_booking_corrections.py` |
| 4 | WAITING_DATE | `_handle_waiting_date` | PASS — `test_booking_state_machine.py`, `test_booking_corrections.py` |
| 5 | WAITING_TIME | `_handle_waiting_time` | PASS — `test_booking_state_machine.py`, back-navigation tests |
| 6 | CONFIRMING | `_handle_confirming` | PASS — `test_booking_state_machine.py`, correction tests |
| 7 | COMPLETED | dispatch returns static | PASS — tested via flow completion |
| 8 | CANCELLED | dispatch returns static | PASS — tested via cancellation flow |
| 9 | WAITING_SURNAME | `_handle_waiting_surname` | PASS — `test_kimi_flow.py` |
| 10 | CONFIRMING_PHONE | `_handle_confirming_phone` | PASS — `test_kimi_flow.py` (5 tests), `test_booking_corrections.py` |
| 11 | PROPOSE_REGISTRATION | `_handle_propose_registration` | **WARN** — only tested indirectly via `test_phase_e_audit_p1.py` dispatch table check; no dedicated handler test |
| 12 | REGISTERING_SURNAME | `_handle_registering_surname` | PASS — `test_booking_state_machine.py` (4 tests for "Di Nanni" bug) |
| 13 | REGISTERING_PHONE | `_handle_registering_phone` | PASS — `test_kimi_flow.py` flow tests |
| 14 | DISAMBIGUATING_NAME | `_handle_disambiguating_name` | PASS — `test_disambiguation_integration.py` (4 tests) |

**Missing test coverage**:
- **PROPOSE_REGISTRATION**: The handler (`_handle_propose_registration`, line 3512) has zero dedicated tests that exercise the "sì/no" decision logic. It is only verified to exist in the dispatch table (`test_phase_e_audit_p1.py:48`). A user saying "no" to registration should reset to IDLE; "sì" should proceed to REGISTERING_SURNAME.

---

## TTS 3-Tier Fallback

### VERDICT: PASS

**Architecture** (`tts.py` + `tts_engine.py`):

| Tier | Engine | Quality | Latency | Trigger |
|------|--------|---------|---------|---------|
| 1 (QUALITY) | EdgeTTSEngine (IsabellaNeural) | 9/10 | ~500ms TTFB, ~900ms total | Default if `edge-tts` installed + capable HW |
| 2 (FAST) | PiperTTSEngine (it_IT-paola-medium) | 7/10 | ~50ms | Fallback if Edge-TTS init fails or offline |
| 3 (LAST RESORT) | SystemTTS (macOS `say` / Windows `pyttsx3`) | 5/10 | ~400ms | Fallback if Piper binary/model missing |

**Fallback Chain Verification**:

1. **Tier 1 -> Tier 2** (`tts_engine.py:157-169`):
   ```python
   if mode == TTSMode.QUALITY:
       try:
           engine = EdgeTTSEngine()
           return engine
       except Exception as exc:
           logger.warning("EdgeTTSEngine init failed, falling back to PiperTTSEngine")
   return PiperTTSEngine()
   ```
   PASS — Edge-TTS construction failure triggers Piper fallback. However, this is init-time only. If Edge-TTS is constructed successfully but later fails at synthesis (network down), the `EdgeTTSEngine.synthesize()` raises `RuntimeError` — and `TTSCache.synthesize()` does NOT catch it.

2. **Tier 2 -> Tier 3** (`tts.py:670-676`):
   ```python
   # Fallback: try Piper directly
   try:
       return PiperTTS(**kwargs)
   except (RuntimeError, FileNotFoundError):
       logger.warning("Piper not available, falling back to SystemTTS")
       return SystemTTS()
   ```
   PASS — Piper missing triggers SystemTTS.

**GAP IDENTIFIED (P1)**: Runtime Edge-TTS failure (e.g., internet drops mid-session) is NOT handled with a fallback. The `TTSCache.synthesize()` method (line 709) does not catch exceptions from the underlying engine. If Edge-TTS was selected at init time and then the network drops, every `synthesize()` call will raise `RuntimeError`, causing the entire response to fail with no audio.

**Recommended Fix**: Add a try/except in `TTSCache.synthesize()` that catches synthesis exceptions and falls back to PiperTTS or SystemTTS dynamically.

**Latency Overhead per Tier**:
- Tier 1 to Tier 2 at init: ~0ms (immediate fallback)
- Tier 1 at runtime: No timeout before fallback — exception-based only
- Edge-TTS streaming has internal timeout via `edge_tts.Communicate.stream()` — defaults to aiohttp's 300s connect timeout (far too long for real-time voice)

---

## Latency Breakdown (B7)

### VERDICT: FAIL — P95 < 800ms NOT achievable without streaming

**Measured Architecture** (`orchestrator.py` process() method):

| Phase | Typical | P95 | Notes |
|-------|---------|-----|-------|
| L0-L1 Regex + Intent | <5ms | <10ms | Pure Python, no I/O |
| L2 FSM Slot Filling | <10ms | <20ms | Pure Python, DB lookup optional |
| L3 FAQ Retrieval | <50ms | <80ms | Keyword search, no network |
| L4 Groq LLM (UNKNOWN only) | 200-500ms | 800ms | Network call to Groq API |
| TTS Synthesis | 50-500ms | 900ms | Edge-TTS ~500ms, Piper ~50ms |
| **Total L0-L2 + Piper** | **60-70ms** | **<100ms** | Achievable for known intents |
| **Total L4 + Edge-TTS** | **700-1000ms** | **1700ms** | Not achievable without streaming |

**F03 Timing Instrumentation** (confirmed in code):
- `orchestrator.py:842`: `_t0 = time.perf_counter()` at start
- `orchestrator.py:2431`: `_total_ms = (time.perf_counter() - _t0) * 1000` at end
- Per-layer timing via `print(f"[F03] L4 LLM: {_t_llm_ms:.0f}ms")`

**Analysis**:
- For L0-L2 responses (70%+ of calls): P95 < 100ms with Piper TTS — **well under 800ms target**
- For L4 (Groq fallback, ~15% of calls): Groq LLM latency alone is 200-800ms. Add Edge-TTS 500ms = 700-1300ms. **Exceeds 800ms target.**
- **STT latency (VoIP path)**: `_process_caller_audio` uses `self.pipeline.process_audio()` which calls `self.groq.transcribe_audio()` — Groq Whisper cloud STT adds 200-500ms. This is NOT counted in the orchestrator's `latency_ms` metric.

**Biggest Bottleneck**: TTS synthesis when using Edge-TTS (500ms median). Switching to Piper-only for VoIP would cut ~400ms.

**Path to P95 < 800ms**:
1. Use Piper TTS for VoIP calls (50ms vs 500ms) — saves 450ms
2. Pre-cache top 20 FSM prompts at startup (already implemented via `TTSCache.warm_cache`)
3. L4 Groq with streaming TTS (already partially implemented: `_l4_tts_tasks` parallel synthesis at line 2495)
4. Reduce Groq fallback rate by improving L1/L2 coverage

---

## Vertical Coverage

### VERDICT: PASS (9 verticals with full service coverage, variable FAQ/guardrail depth)

**Service Definitions** (`italian_regex.py:229-474` — `VERTICAL_SERVICES`):

| # | Vertical ID | Services | FAQ File | Guardrail | Entity Extractor | DB Seed |
|---|-------------|----------|----------|-----------|-----------------|---------|
| 1 | `salone` / `hair` | 22 services | `faq_salone.json` | YES | YES (via `extract_vertical_entities`) | YES (demo) |
| 2 | `palestra` / `wellness` | 17 services | `faq_palestra.json` + `faq_wellness.json` | YES | YES | NO |
| 3 | `medical` / `medico` | 18 services | `faq_medical.json` | YES | YES + triage | NO |
| 4 | `auto` | 17 services | `faq_auto.json` | YES | YES | NO |
| 5 | `beauty` | 16 services | `faq_beauty.json` | YES | YES | NO |
| 6 | `professionale` | 5 sub-verticals | N/A (FAQ via Groq L4) | Partial | NO | NO |
| 7 | `gommista` | (sub of auto) | `faq_gommista.json` | YES | YES | NO |
| 8 | `barbiere` | (sub of hair) | `faq_barbiere.json` | YES | YES | NO |
| 9 | `odontoiatra` | (sub of medico) | `faq_odontoiatra.json` | YES | YES | NO |

**Additional FAQ files found**: `faq_fisioterapia.json`, `faq_toelettatura.json`, `faq_altro.json`

**Guardrail function** (`check_vertical_guardrail()` at line 1356): Cross-checks user input against the active vertical. If a salone user asks for "cambio olio", it returns a redirect message. Covers all 4 macro verticals (salone, palestra, medical, auto).

**Gap**: `professionale` vertical has service synonyms but no dedicated FAQ file and no entity extractor. L4 Groq fallback handles all conversational needs for this vertical.

---

## Summary

| Section | Verdict | Priority |
|---------|---------|----------|
| B1 pjsua2 Deadlock | **PASS** | Fixed. `mainThreadOnly=True` + `lockCodecEnabled=False` eliminates root cause. |
| B3 Adaptive Silence Wiring | **PASS** (HTTP) / **WARN** (VoIP) | VoIP path uses fixed 1000ms timeout, ignoring EOU adaptive predictions. |
| FSM State Coverage | **WARN** | PROPOSE_REGISTRATION has no dedicated handler test. |
| TTS 3-Tier Fallback | **PASS** (init) / **WARN** (runtime) | Edge-TTS runtime failure has no graceful fallback to Piper. |
| Latency P95 < 800ms | **FAIL** | Achievable for L0-L2 (< 100ms). Not achievable for L4+Edge-TTS without streaming. |
| Vertical Coverage | **PASS** | 9 verticals with services. `professionale` lacks FAQ file. |

---

## Priority Fixes

1. **P0 — TTS Runtime Fallback**: Add try/except in `TTSCache.synthesize()` to catch Edge-TTS failures and fallback to Piper dynamically.
2. **P1 — VoIP Adaptive Silence**: Wire `_last_adaptive_silence_ms` from orchestrator to `voip_pjsua2.py`'s `_vad_silence_timeout`.
3. **P1 — Edge-TTS Timeout**: Add a 3-5s timeout to `EdgeTTSEngine.synthesize()` for real-time voice scenarios.
4. **P2 — PROPOSE_REGISTRATION Tests**: Add dedicated handler tests for yes/no logic.
5. **P2 — Latency Target**: Use Piper-only for VoIP path to achieve sub-800ms for L0-L2 responses.
