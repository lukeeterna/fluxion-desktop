# Research F1: End-of-Utterance (EOU) Detection

## Key Findings

1. **LiveKit EOU is TEXT-BASED, not audio-based.** Takes STT-transcribed conversation history, outputs end-of-turn probability.
2. **ONNX model exists (Apache 2.0).** English-only: 66MB/~15-45ms. Multilingual (Italian): 281MB/~50-160ms. HuggingFace `livekit/turn-detector`.
3. **Python 3.9 dependency problem.** Requires `transformers` + `tokenizers` (~500MB deps). Newer versions need Python 3.10+.
4. **80% of benefit from simple heuristics with ZERO new deps.**

## Recommended 3-Tier Architecture

### Tier 1: Adaptive Silence Duration (ZERO deps — implement first)
Current: fixed `silence_duration_ms = 700`. Replace with context-aware:
- 2 words or less: 400ms ("si", "no" — respond fast)
- 3-6 words: 600ms
- 7+ words: 900ms (user might pause mid-thought)
- WAITING_NAME/DATE/SERVICE states: 800ms (thinking)

### Tier 2: Italian Sentence-Completion Heuristics (ZERO deps)
After STT, before triggering response:
- INCOMPLETE patterns: ends with `e`, `ma`, `oppure`, `perché`, `quando`, comma
- COMPLETE patterns: ends with `grazie`, `arrivederci`, `ok`, `si`, `no`, punctuation
- If incomplete: extend wait, optionally play "mhm"
- If complete: proceed immediately

### Tier 3: ONNX Model (future, only if Tier 1-2 insufficient)
- Multilingual (281MB, ~400MB RAM, ~50-160ms latency)
- Must verify Python 3.9 compat on iMac
- Only run when silence is borderline (500-900ms)

## Integration Points
- `voice-agent/src/vad/ten_vad_integration.py` — make silence_duration_ms dynamic
- `voice-agent/src/orchestrator.py` — add post-STT sentence completion check
- New: `voice-agent/src/eou/adaptive_silence.py` + `sentence_completion.py`

## Competitor Approaches
| Platform | Approach | Result |
|----------|----------|--------|
| Retell.ai | Proprietary + tone/pause | "Interruption Sensitivity Slider" |
| Vapi | Deepgram Flux word-level | Word-level turn detection |
| LiveKit | SmolLM2/Qwen2.5 transformer | 39% interruption reduction |
| VideoSDK | NAMO v1 ONNX 23+ langs | 97.3% accuracy claimed |

## Recommendation
Plan Tier 1 + Tier 2 as main tasks (4h). Tier 3 as optional future gated on results.
