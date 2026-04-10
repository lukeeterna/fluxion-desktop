# Phase F: Advanced — EOU Detection + Acoustic Frustration

## Goal
Reduce interruptions ~30% via adaptive end-of-utterance detection, and detect caller frustration from acoustic signals (raised voice, fast speech) to trigger empathetic tone or auto-escalation.

## Research Sources
- `.claude/cache/agents/research-f1-eou-detection.md`
- `.claude/cache/agents/research-f2-acoustic-frustration.md`

---

## F1: End-of-Utterance Detection (4h)

### Approach: Tier 1 + Tier 2 (ZERO new deps)
LiveKit ONNX model deferred (Python 3.9 compat risk, 281MB, needs `transformers`). Simple heuristics get ~70% of benefit.

### F1-1: Adaptive Silence Duration (1.5h)
**File**: NEW `voice-agent/src/eou/__init__.py` + `adaptive_silence.py`

```python
def get_adaptive_silence_ms(transcript: str, fsm_state: str) -> int:
    words = transcript.split() if transcript else []
    wc = len(words)
    if wc <= 2:    return 400   # Quick answer
    if wc <= 6:    return 600   # Medium
    if wc > 6:     return 900   # Long, might pause mid-thought
    # State-aware: user thinking about specific data
    if fsm_state in ("waiting_name", "waiting_date", "waiting_service"):
        return 800
    return 700
```

**Integration**: `vad/ten_vad_integration.py` — accept dynamic `silence_duration_ms` per-call instead of fixed config. `vad/vad_pipeline_integration.py` — same.

**AC**: 
- `silence_duration_ms` varies based on context (400-900ms range)
- Short utterances ("si") get 400ms response time
- Long utterances get 900ms (no interruption)

### F1-2: Italian Sentence-Completion Heuristics (1.5h)
**File**: NEW `voice-agent/src/eou/sentence_completion.py`

```python
def sentence_complete_probability(text: str) -> float:
    # INCOMPLETE: ends with "e", "ma", "oppure", "perché", comma
    # COMPLETE: ends with "grazie", "ok", "si", "no", punctuation
    # Returns 0.0-1.0
```

**Integration**: `orchestrator.py` — after STT returns transcript, before calling FSM:
- If probability < 0.3: extend wait 500ms more (user still speaking)
- If probability > 0.7: proceed immediately
- Middle ground: use default timing

**AC**:
- "Vorrei un taglio e" → incomplete (0.2), wait longer
- "Si, confermo" → complete (0.9), proceed fast
- No new dependencies

### F1-3: Integration + Tests (1h)
**Files**: `orchestrator.py`, `voip_pjsua2.py`, NEW `tests/test_phase_f_eou.py`

Tests:
- Adaptive silence returns correct ms for each word count
- Sentence completion scores correct for 10+ Italian phrases
- Integration: process_audio respects dynamic silence

---

## F2: Acoustic Frustration Detection (8h)

### Approach: numpy-only DSP features (ZERO new deps)
All libs already on iMac: numpy 1.26.4, scipy 1.13.1.

### F2-1: AcousticFrustrationDetector class (3h)
**File**: NEW `voice-agent/src/acoustic_frustration.py`

Features (all numpy):
| Feature | Formula | What |
|---------|---------|------|
| RMS energy | `np.sqrt(np.mean(s**2))` | Raised voice |
| ZCR | `np.sum(np.abs(np.diff(np.sign(s))))` | Agitated speech |
| F0 pitch | Autocorrelation via `np.fft.rfft` | Emotional variation |
| RMS variance | `np.std(rms_history)` | Instability |

Class design:
- `__init__(sample_rate=16000)` — initialize with calibration window
- `calibrate(pcm_bytes)` — set baseline from first 2-3s of call
- `analyze_audio(pcm_bytes) -> FrustrationResult` — returns score 0.0-1.0
- Rolling window of last ~2s of features
- Gate on VAD output (only analyze speech frames)

**AC**:
- `analyze_audio()` completes in <2ms per chunk
- Calibrates per-caller (handles different phone volumes)
- Returns frustration_score 0.0-1.0

### F2-2: Score Fusion + ToneAdapter Integration (2h)
**Files**: `orchestrator.py`, `sentiment.py`

Fusion table:
| Acoustic | Text | Action |
|----------|------|--------|
| < 0.3 | any | No action |
| 0.3-0.5 | NONE/LOW | EMPATHETIC tone |
| > 0.5 | any | EMPATHETIC + shorter responses |
| > 0.7 | any | Auto-escalate (reuse E5 escalation_manager) |

Integration in `orchestrator.process_audio()`:
1. `acoustic_score = self.acoustic_detector.analyze_audio(pcm_bytes)`
2. After STT: `text_sentiment = self.sentiment.analyze(text)`
3. Fuse: `max(acoustic_score, text_frustration / 4.0)`
4. Feed fused score to `tone_adapter.update_tone()`

**AC**:
- Acoustic + text scores fused into single frustration signal
- ToneAdapter switches to EMPATHETIC on acoustic frustration
- Auto-escalate triggers at score > 0.7

### F2-3: Anti-Echo + VoIP Guard (1h)
**File**: `voip_pjsua2.py`, `acoustic_frustration.py`

Critical pitfalls:
- Skip analysis during TTS playback (check `_current_tx_rms > 0`)
- Gate on VAD speech detection only
- Handle 8kHz → 16kHz upsample correctly
- Italian prosody thresholds (higher than English)

**AC**:
- No false positives from Sara's own TTS audio
- No false positives on silence frames
- Thresholds tuned for Italian prosody

### F2-4: Tests (2h)
**File**: NEW `tests/test_phase_f_acoustic.py`

Tests:
- RMS calculation from known PCM samples
- Calibration sets correct baseline
- Frustration score rises on loud audio
- Score stays low on normal volume
- Anti-echo: score=0 during TTS
- Fusion: acoustic + text produce correct combined score
- Auto-escalate at 0.7+ threshold
- Italian prosody: normal expressive speech ≠ frustration

---

## Execution Order
```
F1-1 → F1-2 → F1-3 (sequential, each builds on previous)
F2-1 → F2-2 → F2-3 → F2-4 (sequential)
F1 and F2 are independent — can run in parallel if needed
```

## Verify
- All tests pass on MacBook + iMac
- Pipeline restart + health check
- E2E: process_audio with known frustration audio → escalation triggered
- E2E: short "si" → fast response (400ms silence)
- E2E: "vorrei un taglio e..." → extended wait (no interruption)
