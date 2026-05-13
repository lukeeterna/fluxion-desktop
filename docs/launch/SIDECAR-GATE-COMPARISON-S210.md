# Sidecar Release-Gate Comparison — S210

**Test**: release-gate Tier 1 (--skip-extended) eseguito contro sidecar PyInstaller 74MB vs baseline source venv.

## Risultati

| Metric | Source venv (S208 baseline) | Sidecar 74MB (S210) | Delta |
|--------|----------------------------:|--------------------:|------:|
| Verdict | PASS | PASS | ✅ |
| OK | 130 | 101 | -29 (tier2+DB skipped) |
| WARN | 56 | 61 | +5 (latency tail) |
| **FAIL** | **0** | **0** | **=** |
| Tests run | 185 | 162 | tier1+latency only |
| Duration | 703s | 675s | -28s |
| Samples | 162 | 147 | latency probes |
| P50 latency | 905ms | 1236ms | +331ms |
| P95 latency | 9795ms | 11340ms | +1545ms |
| Slow ratio | 17.9% | 15% | -2.9pp |

**Verticals 0 FAIL**: AUTO/BEAUTY/MEDICAL/PALESTRA/PROFESSIONALE/SALONE.

## Conclusioni

### ✅ Sidecar funzionale validated
Zero regressione comportamentale rispetto a source venv. Il fix S208 (`NameError text` → `_update_context_from_extraction(text="")`) è correttamente bundled nel binary 74MB. Pjsua2 dylib resolution S209 idem.

### ⚠️ Latency degradata sidecar (+331ms P50, +1545ms P95)
**Root cause primaria**: il sidecar bundle 74MB NON include i Piper TTS voice models (`it_IT-paola-medium.onnx` ~63MB). Log sidecar startup mostra:
```
WARNING: AdaptiveTTS selector failed (Piper voice model not found:
  /Users/<user>/Library/Application Support/Fluxion/voice-agent/models/tts/it_IT-paola-medium.onnx.
  Download it_IT-paola-medium.onnx to voice-agent/models/tts/), falling back to PiperTTS
WARNING: Piper not available: Piper binary not found. Install with: pip install piper-tts
WARNING: Using SystemTTS as last resort
```

**Conseguenze**:
1. Fallback a SystemTTS (`say` macOS) — audio qualità inferiore.
2. SystemTTS `say` ha startup overhead per-call (no daemon mode).
3. Edge-TTS (cloud, quality tier) usata quando rete OK ma fallback SystemTTS quando si forza fast-path.

### Trade-off bundle size

| Opzione | Bundle size | Pro | Contro |
|---------|-------------|-----|--------|
| **Attuale (74MB no Piper model)** | 74MB | small download | TTS fallback SystemTTS, audio degradato |
| **Bundle Piper model** | ~137MB (+63MB) | TTS Piper offline funziona | size +85% |
| **Download on-first-run** | 74MB iniziale + lazy 63MB | small initial | richiede `tts_download_manager.py` working + UX onboarding |

**Recommendation**: opzione 3 — già esiste `src/tts_download_manager.py` (line 113 voice-agent.spec hidden_imports). Verificare che il sidecar lo invochi su startup detect-missing-model. Se non lo fa, è bug shipping.

## Tech debt aggiunto S210

1. **Piper voice model NOT bundled in sidecar** — verificare `tts_download_manager.py` auto-download on first start. Se manca, audio degradato per primi clienti reali.
2. **Sidecar P50 +331ms vs source** — investigation: PyInstaller bootloader extract overhead? UPX decompression? Cold start vs warm cache differences.
3. **Sidecar log startup mostra `httpx HTTP/1.1 200 OK` Groq call al boot** (12:45:42) — pre-warm o probe? Controllare se è leak di telemetry / costo $ token.

## Conclusione S210

**Sidecar 74MB è SAFE per shipping (zero FAIL)** ma con caveat audio quality (SystemTTS fallback). Per release production-grade audio:
- (P0 ship) verificare auto-download Piper model on first run
- OR (P1 alternativa) bundle Piper model in sidecar (137MB)

Decisione bundle vs lazy-download → S211 dopo verifica `tts_download_manager.py` behavior.

---
**Test eseguito**: S210 (2026-05-13 12:46 CEST)
**Report**: `docs/launch/sara-release-gate-reports/release-gate-20260513-124606.json`
**Pipeline restored**: source venv pid 66680 post-test (sidecar killed clean)
