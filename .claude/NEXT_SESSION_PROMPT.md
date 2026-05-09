# S195 — Sidecar Distribution Bundle Fix (datas + piper module)

S194 HANDOFF STRUTTURATO — chiusura context 61%. Sidecar build runtime OK, **distribution NOT ready** per missing datas.

## Stato sidecar attuale
- ✅ Build PyInstaller success (193MB) post 3 fix infrastructure
- ✅ Smoke `--version` + `--health-check` PASS
- ❌ TEMPDIR `_MEI*` NON contiene `models/tts/it_IT-paola-medium.onnx` (61MB)
- ❌ `piper/` package incompleto (solo `espeakbridge.so`, manca `voice.py`/`config.py`/etc)

## PRIORITY 1 — Fix bundle datas (~30 min iMac)

Edit `voice-agent/voice-agent.spec` — sostituire approccio manuale con `collect_*` helpers:

```python
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Sostituire piper_models block con:
piper_data = collect_data_files('piper', include_py_files=False)
datas.extend(piper_data)
hidden_imports += collect_submodules('piper')
```

Possibile causa secondaria: path con space `"/Volumes/MacSSD - Dati/fluxion"` rompe `Path(SPECPATH)` → considerare symlink `/tmp/fluxion` → repo.

Rebuild:
```bash
ssh imac "export PATH=\$HOME/Library/Python/3.9/bin:\$PATH && cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && bash build-sidecar.sh --clean"
```

Verifica TEMPDIR:
```bash
ssh imac "'/Volumes/MacSSD - Dati/fluxion/src-tauri/binaries/voice-agent-x86_64-apple-darwin' --health-check >/dev/null 2>&1 &
sleep 3 && TEMPDIR=\$(ls -td /var/folders/q7/*/T/_MEI* | head -1) && find \$TEMPDIR -name '*.onnx' && ls \$TEMPDIR/piper/voice.py"
```

## PRIORITY 2 — Sidecar offline-only test
Pipeline restart con sidecar (NOT system python):
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null
'/Volumes/MacSSD - Dati/fluxion/src-tauri/binaries/voice-agent-x86_64-apple-darwin' > /tmp/voice-pipeline-sidecar.log 2>&1 &"
sleep 5 && curl http://192.168.1.2:3002/health
```

## PRIORITY 3 — E2E HTTP bench
```bash
python3 tools/perf-d3/run_tts_bench.py --host http://192.168.1.2:3002
```
Atteso: P95 < 800ms (sintesi 591ms + HTTP/orchestrator overhead 50-100ms).

## PRIORITY 4 — Cleanup + audit
- `rm scripts/setup-piper.js` (orphan confermato S193)
- Crea `docs/launch/PRE-LAUNCH-AUDIT.md` — Gate 3 status + remaining tech debt: Win MSI sidecar build, code signing macOS+Win, Stripe live keys, ecc.

## Vincoli iMac

- **setuptools=69.5.1 PIN** (S194 downgrade per PyInstaller#9061). NON upgrade fino fix upstream.
- **appdirs=1.4.4** installato pip-user (richiesto da `pyi_rth_pkgres`).
- **PyInstaller 6.19.0** in `~/Library/Python/3.9/bin/` — richiede `export PATH=$HOME/Library/Python/3.9/bin:$PATH` via SSH.

## Files S194 (committed)
- M `voice-agent/src/tts_engine.py` (+5 macOS pip-user paths)
- M `voice-agent/voice-agent.spec` (`piper_onnx`→`piper`+`piper.voice`+`piper.config`+`appdirs`)
- M `HANDOFF.md` (S194 + S193 archived)
- M `MEMORY.md` (Stato Corrente S194)

CONTEXT BUDGET GATE attivo (vincolo #7): file critici sopra 50% NO edit.
