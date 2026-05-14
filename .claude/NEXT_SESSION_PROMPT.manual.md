# S233 — Prompt ripartenza (handoff S232 → S233)

**Generato**: 2026-05-14 (chiusura S232 GREEN)
**Branch**: master @ `bf2c269` (MacBook + iMac sync, iMac repo NEEDS pull)
**Pipeline iMac**: STOPPED clean (PID 7800 terminato)
**Stato S232**: ✅ CLOSED GREEN — S232-P1 fix validato double-run 147/0/0 + 146/1/0

## TL;DR S232 outcome
- ✅ Fix S232-P1 (`orchestrator.py:1653`) commit `bc9f473` — 1 riga, surgical
- ✅ Run 1: **147 OK / 0 WARN / 0 FAIL** (ideale)
- ✅ Run 2: **146 OK / 1 WARN / 0 FAIL** (1 WARN = MEDICAL FAQ digiuno L4_groq cold, tech debt P2 noto)
- ✅ **Booking_keyword_miss = 0 su entrambi run** (target primario raggiunto)
- ✅ S231 regression (6 booking_keyword_miss AUTO Revisione + BEAUTY Epilazione) FIXED
- ✅ Baselines committed: `sara-gate-s232-run1-147-0-0.json` + `sara-gate-s232-run2-146-1-0.json`
- ✅ Edge case scan post-fix verde (E1 legitimate FAQ idle, E3 S127 keyword catch mid-booking)

## Stato repo
- MacBook: `bf2c269` ✅
- iMac: `bc9f473` — **PULL RICHIESTO** per allineare baselines (1 commit ahead su MacBook)
  ```bash
  ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION" && git pull origin master'
  ```
- iMac ha uncommitted Rust formatting drifts in `src-tauri/examples/ipc_bench.rs` + `commands/diagnostic.rs` + `commands/preflight.rs` + `src/lib.rs`. **NON related a S232**. Da decidere S233 se applicare `cargo fmt` cleanup o se sono drift legittimi pre-esistenti.

## Tech debt residuo (priorità decrescente)

### P2 — Streaming L4_groq → TTS chunked (MEDICAL/BEAUTY cold path)
- S232 P95 4309-7667ms su 141 campioni, MAX 10690ms
- Cold L4 path MEDICAL FAQ "Devo venire a digiuno?" → 8429ms in run2 (causa flake intermittente)
- Soluzione: streaming response Groq token-by-token + TTS chunked invece di wait-full-response
- File: `voice-agent/src/orchestrator.py` (L4 routing ~1860-1920), `voice-agent/src/tts/*`

### P3 — Per-tenant facility config Setup Wizard
- Sostituisce hardcoded S227-P1b defaults (piscina/parcheggio/aria condizionata) con config-driven
- File: `voice-agent/src/vertical_facilities.py` o equiv + Setup Wizard React

### P4 — Auto-spawn sidecar Tauri voice pipeline
- App Tauri lancia automaticamente `python main.py` come sidecar invece di richiedere launch manuale
- File: `src-tauri/tauri.conf.json` (`bundle.externalBin`), `src-tauri/src/lib.rs` (sidecar spawn)

### P5 — `--port=N` argparse main.py
- Multi-instance support (test parallel + dev local)
- File: `voice-agent/main.py`

### P6-9 (founder-deferred)
- Self-hosted CI runner (eseguire CI gate reale, MEMORY rule #7)
- PSTN integration test (Twilio/Vonage)
- Win MSI installer signing (SmartScreen mitigation)
- arm64 Universal Binary macOS

## Step S233 suggerite (decidere founder)

### Opzione A — Tech debt P2 (streaming L4)
1. Deep research streaming Groq API + TTS chunked (Edge-TTS/Piper)
2. Baseline P95 corrente: 4309ms (run1) / 7667ms (run2)
3. Target P95 sotto 5000ms su 2 run consecutivi
4. Rischio: streaming complica error recovery + state consistency

### Opzione B — Cleanup iMac drift + consolidate
1. `cargo fmt` su iMac uncommitted Rust files (verify NO logic change)
2. Sync MacBook + commit
3. Smoke test: build Rust + Tauri dev mode

### Opzione C — P4 sidecar Tauri auto-spawn
1. UX winner: user lancia FLUXION desktop → voice pipeline starts automatically
2. Riferimento: Tauri `externalBin` + Rust spawn process management
3. Cleanup PyInstaller bundle ~520MB

### Opzione D — Continua roadmap ROADMAP_REMAINING.md
Vedi `/Volumes/MontereyT7/FLUXION/ROADMAP_REMAINING.md` per prossima fase non-voice.

## Lezioni S232
1. **Smoking gun in docstring esistenti** — S220-P2 docstring ammetteva esplicitamente "bare day-of-week tokens like 'Sabato' get classified as info_orari by TF-IDF (conf ~0.48), spuriously blocking L2 slot filling". Il fix originale era partial. Pattern: leggere docstring autorevoli PRIMA di ipotizzare cause downstream.
2. **Disaccordo motivato vs piano S231** — pre-piano suggeriva revert 955e119 + alternative `intent_classifier.py:387-410`. Disaccordo motivato applicato: il fix era net-positive (PROFESSIONALE Dichiarazione 3→0 miss), revert avrebbe peggiorato. Approfondimento root cause secondario era la strada giusta.
3. **Double-run mandatorio (lezione S228 riapplicata)** — 1 WARN flake in run2 (digiuno cold L4) sarebbe stato classificato erroneamente come regression senza il confronto su 2 run. La flake è intermittente L4 cold-path, NON regressione.

## File rilevanti
- `voice-agent/src/orchestrator.py:1653` (fix S232-P1)
- `voice-agent/tests/e2e/baselines/sara-gate-s232-run1-147-0-0.json` (golden baseline)
- `voice-agent/tests/e2e/baselines/sara-gate-s232-run2-146-1-0.json` (acceptable baseline)
- `voice-agent/src/intent_classifier.py:387-410` (PRENOTAZIONE regex patterns, deferred extension)
- `voice-agent/src/nlu/semantic_classifier.py` (TF-IDF info_orari classification, tech debt deferred)
