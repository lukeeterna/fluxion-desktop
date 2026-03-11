# FLUXION — Handoff Sessione 47 → 48 (2026-03-11)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 838f393
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo errori pre-esistenti in listini.rs/media.rs (invariati, NON toccare)
iMac: NON sincronizzato (build Rust richiesta su iMac per F14+F13)
```

---

## ✅ COMPLETATO SESSIONE 47

### P1.0 — Impostazioni Redesign (verificato pre-esistente)
Già implementato in sessione precedente — sidebar verticale 240px, badge stato, plain language, deep link, scroll-spy, banner Dashboard. TypeScript 0 errori confermati. Roadmap aggiornata.

### F14 — Security Hardening (commit 0397284)
**Impatto**: voice agent non più esposto su rete locale LAN

- `voice-agent/main.py`: bind `0.0.0.0` → `127.0.0.1` (default + CLI arg `--host`)
- CORS middleware: `Access-Control-Allow-Origin: *` → localhost origins only (`http://localhost`, `http://127.0.0.1`, `tauri://localhost`)
- Rate limiting middleware: max 100 req/min sliding window per IP (429 on exceed)
- `src-tauri/src/http_bridge.rs`: `CorsLayer::allow_origin(Any)` → `AllowOrigin::list([localhost origins])`
- ⚠️ Groq API key in keychain: rimandato — tauri-plugin-stronghold beta; chiave in SQLite locale (accettabile v1)

### F13 — SQLite Backup & Auto-export (commit 63d09ba)
**Impatto**: PMI non perde dati se il disco si guasta — protezione automatica

**Rust (support.rs):**
- `DiagnosticsInfo.days_since_last_backup: Option<i64>` — età in giorni dell'ultimo backup
- `run_auto_backup_if_needed`: VACUUM INTO se ultimo backup > 24h + prune > 30gg
- `prune_old_backups(dir, max_days)`: helper interno per retention
- `export_clienti_csv(output_path)`: CSV anagrafica clienti (no deleted)
- `export_appuntamenti_csv(output_path)`: CSV appuntamenti con JOIN clienti+servizi+operatori
- lib.rs: 3 comandi registrati + spawn auto-backup on startup (non-blocking)

**TypeScript:**
- `DiagnosticsPanel.tsx`: banner ⚠️ se backup > 7gg o assente + bottone "Backup ora"
- `DiagnosticsPanel.tsx`: sezione "Esporta Dati CSV" con save-dialog
- `useImpostazioniStatus`: `diagnostica` badge = warning se backup > 7gg
- `use-support.ts`: `useExportClientiCsv` + `useExportAppuntamentiCsv`
- `types/support.ts`: `days_since_last_backup` aggiunto

---

## ✅ COMPLETATO SESSIONE 47 (aggiunta)

### F12 — Voice Agent File Index (commit a59e37f)
**ROI**: -30/40% token per sessioni voice agent

- `voice-agent/src/_INDEX.md`: 226 righe — indice completo dei 3 file (7229 righe totali)
  - `booking_state_machine.py` (3506 righe): 23 stati FSM, tutti i _handle_* + righe esatte
  - `orchestrator.py` (2831 righe): 5-layer pipeline range + tutti i metodi
  - `italian_regex.py` (892 righe): 12 gruppi pattern + costanti + classi
- `scripts/update_voice_index.py`: auto-aggiorna header + conteggi righe (--check per CI)
- `.husky/pre-commit`: step 4 aggiunto — ri-genera index se voice-agent/src/*.py staged

## 🚀 PROSSIMO: da ROADMAP_REMAINING.md

Sprint 3 rimanente:
- **F11** — Docker voice agent (3h) — ambiente riproducibile
- **F07** — LemonSqueezy webhook (pendente config dashboard)
- ~~F12~~ ✅ ~~F13~~ ✅ ~~F14~~ ✅

---

## ⚠️ TODO PRODUZIONE APERTI

1. `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` reali in `src-tauri/src/commands/settings.rs`
2. Groq API key in keychain macOS (rimandato post-tauri-plugin-stronghold stable)
3. Cargo check iMac (build Rust F14+F13 non ancora compilata su iMac)

---

## INFRA ATTIVA

### iMac (192.168.1.12)
```bash
# Sync + riavvio pipeline
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### cargo check iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/src-tauri' && cargo check 2>&1 | grep -v 'DATABASE_URL\|E0282\|listini\|media' | tail -20"
```
