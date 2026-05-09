# Prompt ripartenza S196 — Verify build S195 + E2E sintesi PiperVoice

**Generato**: 2026-05-09 (auto-close S195 context 62%)
**Sessione**: S195 (Piper Python API + collect_data_files spec fix)
**Commit**: `5f4aefe feat(S195): Piper Python API + collect_data_files spec fix`
**Branch**: master (push origin OK)

## Stato S195 alla chiusura

✅ **Spec fix applicato** (`voice-agent/voice-agent.spec`):
- `collect_data_files('piper')` → bundle `espeak-ng-data/` (REQUIRED phonemization)
- `collect_submodules('piper')` → bundle voice/config/const/phoneme_ids/...
- Models/tts file-by-file (evita edge case path-with-spaces)

✅ **Refactor `tts_engine.py`**:
- PiperVoice Python API in priorità (subprocess shebang-script broken in distribuzione)
- `_find_model()` ora controlla bundle dir (`get_bundle_root()` era unused)
- `_validate()` relaxed (ok se Python API OR binary)
- Eager `PiperVoice.load()` in `__init__`

✅ **Build iMac COMPLETATA** (exit 0, ~3min):
- `dist/voice-agent` = **208MB** (era 193MB S194, **+15MB** espeak-ng-data confermato bundled)
- Log: `Re-signing the EXE` + `Build complete!` in `/tmp/s195-build.log`
- Verifica MEIPASS contents + E2E sintesi = task primario S196.

## Task S196 — Verifica build + E2E

### PRIORITY 1 — Inspect MEIPASS contents (2 min) — build già OK
```bash
ssh imac "rm -rf /tmp/mei-s195 && mkdir /tmp/mei-s195 && (TMPDIR=/tmp/mei-s195 '/Volumes/MacSSD - Dati/fluxion/voice-agent/dist/voice-agent' --version > /dev/null 2>&1 &); sleep 3; MEI=\$(ls -d /tmp/mei-s195/_MEI* 2>/dev/null | head -1); find \$MEI \\( -name 'paola*.onnx' -o -path '*espeak-ng-data*it_dict' -o -path '*piper/voice.py' \\) | head -5"
# Atteso: 3 hit (model + espeak it_dict + piper voice.py extracted somewhere)
# NB: voice.py potrebbe essere SOLO in PYZ (non extracted come .py), accettabile.
```

### PRIORITY 3 — E2E synthesis (5 min)
```bash
# 1. Kill voice pipeline iMac (port 3002 conflict)
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 1"

# 2. Avvia sidecar bundled
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup ./dist/voice-agent > /tmp/sidecar-s195.log 2>&1 &"
sleep 3

# 3. Verifica health
ssh imac "curl -s http://127.0.0.1:3002/health"

# 4. E2E synthesize via Piper Python API
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/say -H 'Content-Type: application/json' -d '{\"text\":\"Ciao Sara test S196\",\"voice_engine\":\"piper\"}' -o /tmp/test-s196.wav -w 'HTTP=%{http_code} time=%{time_total}s\\n' && ls -la /tmp/test-s196.wav"
# Atteso: HTTP=200, file > 50KB WAV bytes
```

### PRIORITY 4 — Bench latency 10 frasi (5 min)
- Atteso P95 < 800ms (S193 baseline 590ms direct API; possibile +20-50ms overhead PiperVoice loaded vs subprocess)
- Update `docs/perf/D3-voice-latency.md` sezione S196

### PRIORITY 5 — Cleanup + restart pipeline iMac (2 min)
- `rm scripts/setup-piper.js` (orphan da S193)
- Restart pipeline iMac source mode (NOT sidecar) per dev workflow

## Files modificati S195 (committed)
- `voice-agent/voice-agent.spec` — collect_data_files + collect_submodules
- `voice-agent/src/tts_engine.py` — PiperVoice Python API
- `HANDOFF.md` — sezione S195 (S194 archived)
- `MEMORY.md` — Stato Corrente S195

## Tech debt residuo S196
- iMac aveva stash `s194-local` (pre-pull S195) — `git stash list` per verificare. Probabilmente droppabile (S195 contiene già le stesse modifiche più i fix).
- Pipeline voice iMac status: dopo verifica sidecar, restartare in source mode per dev sessions normali.

## Reminder vincoli
- Verifica root cause vero S195 (espeak-ng-data missing) **prima** di dichiarare distribution-ready.
- E2E test obbligatorio (NON solo `--health-check`, deve sintetizzare WAV reale).
- Se P95 sopra 800ms: regression vs S193, investigare overhead Python API.

## Come riprendere
1. `cd /Volumes/MontereyT7/FLUXION`
2. Apri questa sessione e continua dalla PRIORITY 1.
3. Se build su iMac fallita (controlla log): leggi errore in `/tmp/s195-build.log`, applica fix, rebuild.
