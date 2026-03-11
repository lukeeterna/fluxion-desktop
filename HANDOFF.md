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
Branch: master | HEAD: 8670efa
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo errori pre-esistenti in listini.rs/media.rs (invariati, NON toccare)
iMac: NON sincronizzato — pull + cargo check richiesto a inizio s48
```

---

## ✅ COMPLETATO SESSIONE 47

| Task | Commit | Impatto |
|---|---|---|
| P1.0 Impostazioni Redesign | pre-esistente | verificato, roadmap aggiornata |
| F14 Security Hardening | 0397284 | bind 127.0.0.1, CORS localhost-only, rate 100/min |
| F13 SQLite Backup | 63d09ba | auto-backup giornaliero, prune 30gg, CSV export, alert |
| F12 Voice Agent Index | a59e37f | `_INDEX.md` naviga 7229 righe in secondi, auto-update hook |

### Dettaglio F14 — Security Hardening
- `voice-agent/main.py`: bind `0.0.0.0` → `127.0.0.1` + rate limiting 100 req/min + CORS localhost-only
- `src-tauri/src/http_bridge.rs`: `CorsLayer::allow_origin(Any)` → `AllowOrigin::list` localhost only
- ⚠️ Groq key in keychain: rimandato (tauri-plugin-stronghold beta)

### Dettaglio F13 — SQLite Backup & Auto-export
- `support.rs`: `run_auto_backup_if_needed` (VACUUM INTO, prune 30gg), `export_clienti_csv`, `export_appuntamenti_csv`, `days_since_last_backup` in DiagnosticsInfo
- `DiagnosticsPanel.tsx`: banner ⚠️ backup > 7gg + sezione CSV export
- `useImpostazioniStatus`: `diagnostica` badge = warning se backup > 7gg

### Dettaglio F12 — Voice Agent File Index
- `voice-agent/src/_INDEX.md`: mappa metodo→riga per booking_state_machine.py (3506), orchestrator.py (2831), italian_regex.py (892)
- `scripts/update_voice_index.py`: auto-aggiorna conteggi a ogni commit che tocca `voice-agent/src/*.py`
- `.husky/pre-commit`: step 4 aggiunto

---

## 🚀 PROSSIMO: F11 — Docker Voice Agent

**Goal**: ambiente riproducibile — elimina "funziona su iMac non su MacBook"
**Effort**: 3h | **Sprint**: 3

**Deliverables**:
- [ ] `voice-agent/Dockerfile`: Python 3.9-slim, ONNX Runtime, aiohttp, sqlite3
- [ ] `voice-agent/docker-compose.yml`: volume mount per DB locale, porta 3002
- [ ] `voice-agent/requirements-docker.txt`: deps identiche a iMac (senza torch/faiss)
- [ ] README aggiornato con sezione Docker

**ROI**: onboarding nuovo dev 10 min invece di 2h setup

---

## ⚠️ TODO PRODUZIONE APERTI (non bloccanti)

1. `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` reali in `src-tauri/src/commands/settings.rs`
2. Groq API key in keychain macOS (post-tauri-plugin-stronghold stable)
3. **Cargo check iMac** — build Rust F14+F13 non ancora compilata su iMac (fare a inizio s48)

---

## AZIONI OBBLIGATORIE INIZIO S48

```bash
# 1. Sync iMac
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"

# 2. Cargo check (verifica F14 http_bridge.rs compila)
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/src-tauri' && cargo check 2>&1 | grep -v 'DATABASE_URL\|E0282\|listini\|media' | tail -20"

# 3. Riavvio pipeline con nuovo bind 127.0.0.1
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"

# 4. Verifica pipeline UP
curl -s http://127.0.0.1:3002/health
```
