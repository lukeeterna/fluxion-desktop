# FLUXION — Next Session Prompt (S192)

**Generato**: 2026-05-09 (S191 closing partial @ context 60% gate)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit prima chiusura S191**: `6f8b27a feat(S190 D-1): SQLite EXPLAIN audit clienti 1000 — 8/8 PASS no migration`

## Stato S191

CHIUSURA PARTIAL per soglia context budget 60% (vincolo #7 CLAUDE.md).

- D-3 Voice TTS misurato → FAIL hard SLO. P95 867 ms vs target 800 ms.
- D-2 IPC IN PROGRESS (cargo build/run lanciato in background su iMac, da recuperare).
- Tech debt P0 emersa: Piper binary + model NON installati su iMac dev. TTS production usa Edge-TTS cloud.

## Priority S192 (ordinate)

### P1 — Recupera risultati D-2 IPC bench

```bash
# Check background task output (cargo build/run)
ssh imac 'tail /private/tmp/claude-501/-Volumes-MontereyT7-FLUXION/e6c26282-20c7-4ecd-a265-d7f493602a0c/tasks/b3tgip3pv.output 2>/dev/null'

# Re-run idempotente (build incrementale ~1-2 min se cache hot)
ssh imac 'export PATH="$HOME/.cargo/bin:$PATH" && cd "/Volumes/MacSSD - Dati/fluxion/src-tauri" && FLUXION_DB=/tmp/fluxion-perf.db cargo run --release --example ipc_bench'

# Recupera JSON
ssh imac 'cat /tmp/fluxion-d2-results.json' > /tmp/fluxion-d2-results.json

# Scrivi report → docs/perf/D2-ipc-latency.md
# Schema: 3 commands (get_clienti / get_cliente / search_clienti) × P50/P95/P99 + serialize bytes + verdict
# SLO target: handler+serialize P95 < 85 ms (buffer 15 ms WebView channel = SLO Gate 3 100 ms totale)
```

### P2 — Tech debt P0 Piper bundle verification

Architettura promette tier FAST/OFFLINE Piper ~50ms TTFB ma su iMac `model_downloaded=false`.
Il finding D-3 (P95 867ms Edge-TTS cloud) potrebbe non riflettere latenza cliente reale **se** Piper è bundled nell'installer distribuito.

Step:
1. Verifica `src-tauri/tauri.conf.json` sezione `bundle.externalBin` per voice-agent sidecar
2. Verifica `voice-agent/` per PyInstaller spec / build script — Piper download/include?
3. Se NO: aggiungere step build (`piper-cli` install + download `it_IT-paola-medium.onnx` ~30 MB)
4. Se SI: re-run D-3 bench contro bundle distribuito con TTS forced=piper

### P3 — Push origin master sbloccato

4 commit pendenti dietro origin (S189-B, S190, S191, S191 closing). Push fallito:
```
remote rejected: master -> master (push declined due to repository rule violations)
```

Investigare:
```bash
gh api repos/lukeeterna/fluxion-desktop/branches/master/protection 2>&1 | head -30
gh api repos/lukeeterna/fluxion-desktop/secret-scanning/alerts 2>&1 | head -20
```

### P4 — PRE-LAUNCH-AUDIT.md update

Schema attuale ha conflitto naming:
- D-2 = frontend virtualization clienti (`react-window`)
- D-3 = voice latency UNKNOWN

Update:
- Rinominare D-2 frontend → D-2a, aggiungere D-2b IPC misurato S191/S192
- D-3 voice → FAIL con ref `docs/perf/D3-voice-latency.md` + tech debt Piper bundle

## File creati/modificati S191

- NEW `tools/perf-d3/run_tts_bench.py` (~250 righe, replicabile)
- NEW `docs/perf/D3-voice-latency.md` (report finding 50 utterance)
- NEW `src-tauri/examples/ipc_bench.rs` (~280 righe, replicabile)
- NEW `tools/perf-d2/` (dir vuota, run script TBD S192)
- M `src-tauri/Cargo.toml` (+5 righe `[[example]] ipc_bench`)
- M `HANDOFF.md` (sezione S191 closing)
- M `MEMORY.md` (entry S191)

## Stato runtime iMac (al closing)

- voice-pipeline UP su `127.0.0.1:3002` (PID 18004, log `/tmp/fluxion-voice.log`)
- DB seed perf `/tmp/fluxion-perf.db` rigenerato (1000 clienti italiani)
- Cargo background task `b3tgip3pv` (output `/private/tmp/claude-501/.../tasks/b3tgip3pv.output`)
- Repo `/Volumes/MacSSD - Dati/fluxion` HEAD `9c5ab5c` (S188), file S191 sincronizzati via scp

## Gate 3 status post-S191

| Item | Stato |
|------|-------|
| F-1 FAQ | COMPLETE |
| F-2 Runbook | COMPLETE |
| F-3 Email sequence | LIVE |
| F-4 Health monitor | LIVE |
| D-1 SQLite query perf | COMPLETE (S190 — 8/8 PASS, P95 24.5 ms) |
| D-2 IPC <100ms benchmark | IN PROGRESS S192 (recover) |
| D-3 Voice TTS | FAIL S191 (P95 867ms; tech debt Piper bundle) |

## Vincoli sessione

- Context Budget Gate attivo: file critici sopra 50% NO edit (HELPDESK.md, CLAUDE.md autorevole, PLAN.md, .claude/rules/*.md, migrations/**, tauri.conf.json, *.schema.json, openapi*, *.proto, *.graphql).
- Tutti i tool/script nuovi (perf-d2, perf-d3) sono idempotenti e replicabili.
