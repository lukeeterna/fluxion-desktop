# Prompt ripartenza S196 — E2E sintesi PiperVoice (build PASS)

**Generato**: 2026-05-09 (auto-close S195 context 74%)
**Last commit**: `67a69a8 auto-close S195: PyInstaller build OK 208MB`
**Branch**: master (pushed)

## Stato S195 alla chiusura

✅ **Build PyInstaller PASS** — `dist/voice-agent` 208MB (era 193MB S194, +15MB espeak-ng-data confermato bundled)
✅ **Spec fix** — `collect_data_files('piper')` + `collect_submodules('piper')`
✅ **Refactor `tts_engine.py`** — PiperVoice Python API priorità + `_find_model()` controlla bundle dir

⏳ **MEIPASS inspection PARZIALE** — `--health-check` exit troppo presto:
- MEI dir size = 316MB (vs originale 65 file mid-extraction → estrazione progredita)
- `find _MEI -name '*.onnx'` = vuoto durante --health-check (cleanup pre-completion)
- **Verifica completa = avvio sidecar full pipeline + grep MEI mentre running**

## PRIORITY S196

### 1. Inspect MEIPASS sidecar full-running (3 min)
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 1
rm -rf /tmp/mei-s196 && mkdir /tmp/mei-s196
TMPDIR=/tmp/mei-s196 nohup '/Volumes/MacSSD - Dati/fluxion/voice-agent/dist/voice-agent' > /tmp/sidecar-s196.log 2>&1 &
sleep 8
MEI=\$(ls -d /tmp/mei-s196/_MEI* | head -1)
echo MEI=\$MEI SIZE=\$(du -sh \$MEI | awk '{print \$1}')
find \$MEI -name 'paola*.onnx' -o -path '*espeak-ng-data*it_dict' -o -path '*piper/voice.py' | head -5
curl -s http://127.0.0.1:3002/health"
# Atteso: 3 hit (model + it_dict + voice.py) + status:healthy
```

### 2. E2E synthesize (5 min)
```bash
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/say \\
  -H 'Content-Type: application/json' \\
  -d '{\"text\":\"Ciao Sara test S196\",\"voice_engine\":\"piper\"}' \\
  -o /tmp/test-s196.wav -w 'HTTP=%{http_code} time=%{time_total}s\\n' && \\
  ls -la /tmp/test-s196.wav"
# Atteso: HTTP=200, file > 50KB
```

### 3. Bench latency 10 frasi vs SLO 800ms (5 min)
- Update `docs/perf/D3-voice-latency.md` sezione S196
- Confronta vs S193 baseline (590ms direct API)

### 4. Cleanup post-validation (2 min)
- `git stash drop` su iMac (stash `s194-local` ora obsoleto)
- `rm scripts/setup-piper.js` (orphan S193)
- Restart pipeline iMac source mode (kill sidecar, riavvia `python main.py`)

### 5. Close Gate 3 distribution-ready (S196 final)
- Doc `docs/launch/PRE-LAUNCH-AUDIT.md` con checklist 6 categorie verde
- HANDOFF + MEMORY + commit chiusura

## Files toccati S195
- `voice-agent/voice-agent.spec` (collect hooks)
- `voice-agent/src/tts_engine.py` (PiperVoice API)
- HANDOFF.md sezione S195

## Tech debt
- iMac stash `s194-local` (`git stash list`) — drop dopo verifica E2E
- `scripts/setup-piper.js` orphan
- Pipeline voice iMac da restart in source mode dopo test sidecar
