# Research F2: Acoustic Frustration Detection

## Key Findings
1. **numpy-only approach is right.** RMS, ZCR, F0 via autocorrelation — all <2ms per chunk. No new deps needed.
2. **No viable ONNX emotion model.** Wav2Small PyTorch-only, SenseVoice 229MB+, audEERING needs transformers. All need PyTorch.
3. **Sara already has infrastructure.** `voip_pjsua2.py` has `_calc_frame_rms()`. Orchestrator receives PCM 16-bit 16kHz mono.
4. **Integration point:** TOP of `orchestrator.process_audio()`, before STT. <2ms overhead.

## Architecture
```
process_audio(pcm) → acoustic_detector.analyze(pcm) → STT → sentiment.analyze(text) → fuse scores → FSM
```

## Signal Features (numpy-only)
| Feature | Detects | Formula | Latency |
|---------|---------|---------|---------|
| RMS energy | Raised voice | `np.sqrt(np.mean(samples**2))` | <0.1ms |
| ZCR | Agitated speech | `np.sum(np.abs(np.diff(np.sign(samples))))` | <0.1ms |
| F0 pitch | Emotional variation | Autocorrelation via `np.fft.rfft` | <1ms |
| RMS variance | Instability | `np.std(rms_history)` | <0.1ms |
| Pitch std dev | Frustration contour | `np.std(pitch_history)` | <0.1ms |

## Critical Pitfalls
1. **Calibrate per-caller** — phone volumes vary 10-20x. Use first 2-3s as baseline.
2. **Gate on VAD** — only analyze speech frames, not silence.
3. **Skip TTS playback** — avoid analyzing Sara's own echo.
4. **Italian prosody** — naturally expressive, raise thresholds vs English.
5. **Sample rate** — audio arrives 8kHz G.711, upsampled to 16kHz.

## Score Fusion
| Acoustic | Text | Action |
|----------|------|--------|
| < 0.3 | NONE/LOW | No action |
| 0.3-0.5 | NONE/LOW | EMPATHETIC tone |
| > 0.5 | any | EMPATHETIC + shorter responses |
| > 0.7 | any | Auto-escalate to operator |

## New File: `voice-agent/src/acoustic_frustration.py`
- `AcousticFrustrationDetector` class
- `analyze_audio(pcm_bytes) -> dict` with rms, zcr, pitch_hz, frustration_score
- Adaptive baseline from first 2-3s of call
- Rolling window (~2s)
