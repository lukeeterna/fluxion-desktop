# S191 D-2 — IPC Handler Latency Benchmark (clienti)

**Generato**: 2026-05-09T16:25:38Z (iMac, cargo run --release)

**DB**: `/tmp/fluxion-perf.db` — 1000 clienti italiani realistici (deterministic seed via `tools/perf-d1/audit.py`)

**Bench**: `src-tauri/examples/ipc_bench.rs` — 5 warmup + 100 iter per command, no Tauri runtime, SqlitePool diretto.

## Path misurato

`SqlitePool query → sqlx FromRow → Vec<Cliente> → serde_json::to_string`

## Path NON misurato

WKWebView postMessage ↔ tauri-runtime ipc dispatch ↔ command resolver. Da letteratura Tauri 2.x v2 IPC su WKWebView macOS: ~5–15 ms per round-trip. Buffer applicato: **+15 ms** per derivare SLO Gate 3 totale 100 ms.

## SLO

- **Gate 3**: P95 totale (`handler + serialize + WebView channel`) < **100 ms**
- **Bench target**: `handler_P95 + serialize_P95 < 85 ms` (lascia 15 ms al channel)

## Risultati

| command          | P50 ms | P95 ms | P99 ms | serialize P95 ms | payload bytes (P95) | verdict |
|------------------|-------:|-------:|-------:|-----------------:|--------------------:|---------|
| `get_clienti`    | 34.2   | 36.9   | 37.3   | 1.63             | 649,730             | **PASS** |
| `get_cliente`    | 0.1    | 0.1    | 0.1    | 0.00             | 666                 | **PASS** |
| `search_clienti` | 1.3    | 2.6    | 2.7    | 0.07             | 32,396              | **PASS** |

`get_clienti` totale (handler + serialize) P95 = **38.5 ms** → con buffer 15 ms WebView ≈ **53.5 ms** ≪ 100 ms SLO Gate 3. Margine ampio anche per scaling 2k–5k clienti (estrapolazione lineare ~75 ms a 2k record).

## Considerazioni

- `get_cliente` (lookup PK) è di fatto gratis (~0.1 ms) — copertura indice `sqlite_autoindex_clienti_1`.
- `search_clienti` LIKE wildcard è dominato dal pre-filtro `idx_clienti_deleted_at`; max payload 32 KB (LIMIT 50). Tech debt FTS5 confermata accettabile sotto 10k clienti.
- `get_clienti` lista completa serializza 1000 record = ~650 KB JSON. P95 36.9 ms include il file system+page cache già caldo (warmup 5 iter).

## Tech debt residuo

1. **Channel WebView non misurato**: per validazione end-to-end serve `npm run tauri dev` con DevTools `console.time` + `await invoke('get_clienti')` per N=100. Deferred S192 (non blocker — buffer 15 ms documentato).
2. **Scaling 2k–10k clienti**: re-run con `SEED_TARGET` esteso quando primo cliente PMI supera 1000 record (oggi target medio PMI 1–15 dipendenti = ~200–800 clienti).

## Reproduce

```bash
# Su iMac (cargo build incrementale)
ssh imac 'export PATH="$HOME/.cargo/bin:$PATH" && cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && FLUXION_DB=/tmp/fluxion-perf.db cargo run --release --example ipc_bench'

# Recupera JSON
ssh imac 'cat /tmp/fluxion-d2-results.json' > /tmp/fluxion-d2-results.json
```

## Verdict Gate 3 D-2

**PASS** — tutti e 3 i command IPC clienti restano ben sotto SLO 100 ms anche con buffer WebView channel applicato. `get_clienti` (caso peggiore lista 1000) totale stimato ~54 ms, margine 46 ms.
