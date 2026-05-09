# FLUXION — Handoff Sessione 196 (E2E Piper sidecar PASS) (2026-05-09)

## SESSIONE 196 — ✅ CHIUSA Gate 3 D-3 RICONFERMATO con margine -49.5%

**Esito**: Bundle PyInstaller sidecar S195 (199MB, espeak-ng-data + paola onnx + piper module Python API) validato E2E HTTP `/api/voice/say`. Bench 10 frasi italiane production-realistic: **P95 404ms vs SLO 800ms** (margine -49.5%, miglioramento +32% vs S193 P95 590ms direct API). Sidecar self-contained, zero deps esterne runtime.

### Lavoro completato S196

1. ✅ **Bundle inspection** (`pyi-archive_viewer -l -r dist/voice-agent`):
   - `models/tts/it_IT-paola-medium.onnx` 58MB ✅
   - `models/tts/it_IT-paola-medium.onnx.json` ✅
   - `piper/espeak-ng-data/it_dict` 95KB + 100+ altri lang dict ✅
   - `piper/espeakbridge.so` ✅
   - PYZ modules: `piper.voice`, `piper.config`, `piper.phonemize_espeak` ✅
   - **Conclusione**: spec S195 (`collect_data_files('piper')` + `collect_submodules('piper')`) ha funzionato correttamente.

2. ✅ **Sidecar standalone E2E**:
   - Avviato `dist/voice-agent --port 3099 --host 127.0.0.1` (non disturba pipeline 3002)
   - `.tts_mode = fast` scritto in `~/Library/Application Support/Fluxion/voice-agent/.tts_mode`
   - Log conferma: `[TTSEngineSelector] PiperTTSEngine selected (fast mode)` + `PiperTTS: Python API voice loaded (model=_MEIPASS.../paola-medium.onnx)`
   - POST `/api/voice/say` ritorna `success=true` + `audio_base64` 112KB con header `RIFF...WAVEfmt` valido.

3. ✅ **Bench latency 10 frasi production-realistic**:
   | Metrica | Valore |
   |---------|--------|
   | P50 | **278.0 ms** |
   | **P95** | **404.1 ms** |
   | P99/MAX | 404.1 ms |
   | MIN | 209.7 ms |
   | AVG | 296.4 ms |
   | STDEV | 73.6 ms |

   Tutte 10 < 405ms, nessun outlier. WAV 64KB-129KB per utterance.

4. ✅ **Sync bundle**: `cp dist/voice-agent → src-tauri/binaries/voice-agent-x86_64-apple-darwin` (208MB, da S195 build) per Tauri sidecar packaging.

5. ✅ **Artefatto perf**: `docs/perf/D3-voice-latency.md` aggiornato con sezione "S196 RESULT" (tabella metriche + confronto progressivo S191→S193→S196 + reproduce instructions).

### Confronto progressivo Gate 3 D-3

| Run | Setup | P95 | Stato |
|-----|-------|-----|-------|
| S191 | Edge-TTS cloud fallback | 867 ms | ❌ FAIL |
| S193 | Piper subprocess `--user` install (direct API) | 590.8 ms | ✅ PASS |
| **S196** | **Piper Python API via sidecar bundle** (HTTP) | **404.1 ms** | **✅ PASS PRO** |

**Perché S196 outperform S193**:
1. PiperVoice eager-loaded in `__init__` → no cold-load (~200ms) primo synthesize
2. No subprocess fork/exec → Python API in-process zero IPC penalty
3. `asyncio.to_thread` non-blocking → server può servire concurrent

### Files modificati S196

- M `docs/perf/D3-voice-latency.md` (+60 righe sezione S196)
- M `HANDOFF.md` (questo file, ricreato post auto-close commit 42ef289)
- iMac side: bundle copiato `dist/voice-agent` → `src-tauri/binaries/voice-agent-x86_64-apple-darwin` (208MB)

### Stato Gate 3 — ✅ COMPLETO BLINDATO

- F-1 ✅ | F-2 ✅ | F-3 ✅ CODE COMPLETE | F-4 ✅ CODE COMPLETE
- D-1 ✅ | D-2 ✅ (P95 36.9ms) | **D-3 ✅ PASS PRO** (P95 404ms vs SLO 800ms)
- Bundle PyInstaller sidecar self-contained → distribuibile a end-user senza deps esterne.

### Tech debt residuo S197 (P2)

- `scripts/setup-piper.js` orphan — rimuovere (path mismatch confermato S193+S195+S196)
- `docs/launch/PRE-LAUNCH-AUDIT.md` NEW — Gate 3 readiness summary aggregato (D-1+D-2+D-3 + F-1..F-4)
- Deploy CF Worker F-3 + F-4 (S189-A still pending: founder action 2 cmd terminale per `wrangler secret put` + `wrangler deploy`)
- Founder action: rotate 2 CF tokens (S192 procedure)

### Tech debt P3 (deferred milestone)

- Bundle Linux/Windows sidecar (PyInstaller cross-compile). Questa S196 solo macOS x86_64.
- Universal Binary macOS arm64 (Apple Silicon native).

### Prompt ripartenza S197

```
S196 ✅ CHIUSA — Gate 3 D-3 PASS PRO P95 404ms (margine -49.5% vs SLO 800ms).
Bundle sidecar 208MB self-contained validato E2E.

PRIORITY 1 — PRE-LAUNCH-AUDIT.md NEW (~15 min):
  Aggregare Gate 3 readiness: F-1..F-4 + D-1+D-2+D-3 con metriche misurate.
  Format: tabella checklist 6 categorie (Build/Functional/Security/Perf/Compliance/CS) + sign-off.

PRIORITY 2 — Cleanup orphan scripts (~5 min):
  rm scripts/setup-piper.js (path mismatch S193+S195+S196).
  Verifica package.json non lo referenzia più.

PRIORITY 3 — Deploy CF F-3 + F-4 (founder action ~10 min):
  cd fluxion-proxy && npx wrangler secret put DISCORD_HEALTH_WEBHOOK_URL && npx wrangler deploy
  Then E2E: 5 email Gmail (sequence preview) + curl /admin/health/run-now

PRIORITY 4 — Founder ROTATE 2 CF tokens (S192 procedure, ~3 min dashboard).

PRIORITY 5 (deferred) — Bundle Win/Linux sidecar (cross-compile PyInstaller).
```
