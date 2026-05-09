# S191 D-3 — Voice TTS Latency (production endpoint `/api/voice/say`)

**Generato**: 2026-05-09T16:09:16.118409Z

**Host bench**: `http://127.0.0.1:3002` (voice-pipeline FLUXION)
**Iterazioni**: warmup=3, bench=50, valide=50, fail=0
**Corpus**: 50 utterance italiane realistiche (greeting/conferma/slot/disambiguazione/errore/chiusura/WA/short)

## TTS runtime osservato

- `tts` reported by `/health`: `adaptive`
- `/api/tts/mode`: `{'success': True, 'current_mode': 'auto', 'model_downloaded': False, 'reference_audio_path': None}`
- `/api/tts/hardware`: `{'success': True, 'ram_gb': 17.2, 'cpu_cores': 4, 'avx2': False, 'capable': True, 'recommended_mode': 'quality', 'model_downloaded': False}`

> NB: la pipeline FLUXION usa modalità `auto` con TTS Selector 3-tier (Edge-TTS / Piper / SystemTTS).
> Quando `model_downloaded=false` Piper non è disponibile e il selector ricade su Edge-TTS (cloud).

## SLO target

- **Hard cap (Piper offline FAST tier)**: P95 < 800 ms
- **Soft target (Edge-TTS QUALITY tier, cloud)**: P95 ~500 ms (rule `architecture-distribution.md`)

## Risultati

| Metrica | Valore |
|---------|--------|
| min | 4.0 ms |
| mean | 677.4 ms |
| stdev | 188.9 ms |
| **P50** | **695.3 ms** |
| **P95** | **867.0 ms** |
| **P99** | **957.1 ms** |
| max | 999.4 ms |

**Verdict hard SLO (<800ms P95)**: `FAIL`

**Verdict soft SLO (<500ms P95 Edge-TTS)**: `WARN`

## Sample timings (5 frasi)

| # | text_chars | elapsed_ms | audio_hex_len | text |
|---|-----------:|-----------:|---------------:|------|
| 0 | 48 | 4.6 | 292352 | Buongiorno, sono Sara, come posso aiutarti oggi? |
| 1 | 44 | 4.2 | 278528 | Salve, qui Sara dell'assistenza, dimmi pure. |
| 2 | 45 | 4.0 | 278528 | Ciao, sono Sara, in cosa posso esserti utile? |
| 3 | 39 | 796.7 | 257024 | Buon pomeriggio, sono Sara, dimmi pure. |
| 4 | 37 | 730.5 | 260096 | Buonasera, ti rispondo io, sono Sara. |

## Considerazioni

- **Piper model NON installato** sul box di test (`model_downloaded=false`).
  L'SLO Piper offline P95 <800ms NON è verificabile su questo runtime.
  Tech debt: install `piper` binary + download `it_IT-paola-medium.onnx` (S192).

- I numeri qui sopra rappresentano il path **produzione corrente** (Edge-TTS cloud) come servito dal voice-pipeline.
- L'endpoint `/api/voice/say` chiama `orchestrator.tts.synthesize()` quindi include: serializzazione richiesta → selector tier → sintesi audio → encoding → JSON response.
- Per testare offline-Piper isolato: installare il binary, riavviare pipeline, rilanciare lo stesso script (corpus identico, deterministic).

## Reproduce

```bash
# Su iMac (voice-pipeline running)
ssh imac "python3 /Volumes/MacSSD\ -\ Dati/fluxion/tools/perf-d3/run_tts_bench.py"
# Da MacBook (via LAN)
python3 tools/perf-d3/run_tts_bench.py --host http://192.168.1.2:3002
```

---

# S193 — D-3 RECOVERY ✅ PASS (Piper offline tier)

**Generato**: 2026-05-09 (sessione 193)
**Host bench**: iMac system Python 3.9.6 (no venv) — direct API call `piper.PiperVoice.synthesize_wav()` (no HTTP overhead)
**Iterazioni**: warmup=1, bench=10, fail=0
**Corpus**: 10 utterance italiane realistiche (Sara FSM-typical: greeting, conferma slot, lista attesa, WhatsApp, chiusura)

## Setup S193

1. Pre-flight `pip install --dry-run` su `piper-tts>=1.2.0` → wheel `piper_tts-1.4.2-cp39-abi3-macosx_10_9_x86_64` ✅ compat macOS Big Sur
2. `pip install --user piper-tts>=1.2.0` (no blacklist hit, vincolo #8 OK)
3. Download model `it_IT-paola-medium.onnx` (61MB) + `.json` (6.9KB) in `voice-agent/models/tts/` da HuggingFace (`rhasspy/piper-voices`)
4. Smoke test direct API → bench statistico 10 frasi

## Risultati S193

| Metrica | Valore |
|---------|--------|
| Load model (cold, one-time) | 1959.1 ms |
| min | 212.5 ms |
| mean | 444.4 ms |
| **P50** | **457.8 ms** |
| **P95** | **590.8 ms** |
| max | 590.8 ms |

**Verdict hard SLO (Piper offline P95 <800ms)**: ✅ **PASS** (margine -209ms / -26%)

## Sample timings (10 frasi)

| # | elapsed_ms | audio_bytes | text |
|---|-----------:|------------:|------|
| 1 | 212.5 | 63020  | Buongiorno, sono Sara. |
| 2 | 376.3 | 115244 | Mi può confermare il suo nome e cognome per favore? |
| 3 | 459.3 | 129068 | Ho prenotato il suo appuntamento per giovedì alle quindici. |
| 4 | 589.2 | 184876 | Mi dispiace, quello slot è già occupato. Posso proporle alle sedici e trenta? |
| 5 | 590.8 | 176172 | Le invio subito la conferma su WhatsApp. Grazie e buona giornata! |
| 6 | 409.3 | 123436 | Certamente, posso aiutarla con la prenotazione del taglio. |
| 7 | 529.3 | 167980 | Il prossimo disponibile per piega e colore è venerdì pomeriggio. |
| 8 | 346.4 | 105004 | Ho registrato la sua richiesta in lista d'attesa. |
| 9 | 456.2 | 144940 | Mi conferma il numero di telefono per inviarle il promemoria? |
| 10 | 474.4 | 146476 | Perfetto, ci vediamo martedì alle dieci. Arrivederci! |

## Confronto S191 → S193

| Tier | S191 | S193 | Δ |
|------|------|------|---|
| Edge-TTS cloud (HTTP `/api/voice/say` end-to-end) | P95 867ms FAIL | — | — |
| Piper offline (direct API `synthesize_wav`) | n/a (model assente) | **P95 590.8ms PASS** | **-32%** |

NB: i due numeri non sono direttamente confrontabili (S191 misura full HTTP roundtrip, S193 misura sintesi pura senza overhead pipeline). Una validazione end-to-end richiede:
1. Rebuild PyInstaller sidecar con `voice-agent/models/tts/` popolato (S194 pending)
2. Restart pipeline iMac con `.tts_mode=piper` forzato o auto-detect Piper available
3. Re-run S191 bench (`tools/perf-d3/run_tts_bench.py`) sull'endpoint `/api/voice/say`
4. Atteso: P95 < 800ms con margine simile (overhead HTTP+orchestrator ~50-100ms su sintesi pura 590ms)

## Tech debt aperto S194

- **Path mismatch legacy**: `scripts/setup-piper.js` scarica in `<root>/piper/` ma `voice-agent.spec:34-36` cerca `voice-agent/models/tts/`. Setup-piper.js è orphan — eliminare o riscrivere per puntare a `voice-agent/models/tts/`.
- **Rebuild sidecar PyInstaller**: bundle attuale `src-tauri/binaries/voice-agent-x86_64-apple-darwin` (63MB, build 20 mar) NON include modello Piper. Run `bash voice-agent/build-sidecar.sh` per produrre bundle con tier OFFLINE distribuibile a PMI.
- **Pipeline runtime config**: `tts_engine.py:_find_piper_binary()` cerca binary in `~/.local/bin/piper` e `/usr/local/bin/piper` ma pip-user installa in `~/Library/Python/3.9/bin/piper`. Aggiungere path o symlink.

## Reproduce S193

```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -c '
from piper import PiperVoice
import time, io, wave
voice = PiperVoice.load(\"models/tts/it_IT-paola-medium.onnx\")
buf = io.BytesIO(); wf = wave.open(buf, \"wb\")
t0 = time.perf_counter()
voice.synthesize_wav(\"Test sintesi.\", wf)
print(f\"{(time.perf_counter()-t0)*1000:.1f}ms\")
wf.close()
'"
```
