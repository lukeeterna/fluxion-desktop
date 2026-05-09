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
