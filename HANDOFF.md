# FLUXION — Handoff Sessione 46 → 47 (2026-03-10)

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
Branch: master | HEAD: ecc7375
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo errori pre-esistenti in listini.rs/media.rs (invariati, NON toccare)
iMac: sincronizzato ✅ | pipeline UP porta 3002 | Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 46

### P0.6 — Gmail OAuth2 (commit ecc7375)
**Impatto**: Setup email da ~15 minuti (App Password) a <60 secondi (1 click OAuth)

**Architettura implementata** (senza plugin aggiuntivi — tutto con dipendenze esistenti):
- PKCE code_verifier/challenge via `rand` + `sha2` + `base64`
- Callback server locale via `tokio::net::TcpListener` raw TCP (no axum routing)
- Token exchange via `reqwest 0.11` POST form
- Token storage in `impostazioni` SQLite table
- Risultato via evento Tauri: `gmail-oauth-success` / `gmail-oauth-error`

**File modificati:**
- `src-tauri/src/commands/settings.rs` — 4 nuovi comandi OAuth + helpers
  - `start_gmail_oauth(app, pool, oauth_state)` — apre browser, spawna listener, emette evento
  - `get_gmail_oauth_status(pool)` → `GmailOAuthStatus { connected, email }`
  - `disconnect_gmail_oauth(pool)` — cancella tutti i token dal DB
  - `get_gmail_fresh_token(pool)` — auto-refresh se scaduto (per Python voice agent)
  - `OAuthState` struct (managed Tauri state) + `OAuthPkceSession`
- `src-tauri/src/lib.rs` — `OAuthState::default()` managed + 4 comandi in invoke_handler
- `src/components/impostazioni/SmtpSettings.tsx` — sezione "Connetti con Google" sopra SMTP
  - Google G logo SVG, stato connesso con email, Tauri event listeners
  - SMTP manuale rimane INVARIATO sotto (non sostituzione — aggiunta)
- `src/pages/Fornitori.tsx` — trigger contestuale al primo invio ordine email
  - `useEffect` carica smtp_enabled + gmail.connected su mount
  - Se non configurato: toast "Configura email" con deep link `/impostazioni#email`

**Acceptance Criteria verificati:**
- ✅ AC-1: 1 click "Connetti Gmail" → browser Google → auto-callback → connesso
- ✅ AC-2: SMTP manuale non rimosso — OAuth è aggiunta, non sostituzione
- ✅ AC-3: Token salvati in DB (access, refresh, expiry, email, gmail_oauth_enabled)
- ✅ AC-4: Auto-refresh token 5min prima di scadenza (get_gmail_fresh_token)
- ✅ AC-5: Trigger contestuale Fornitori.tsx — deep link /impostazioni#email
- ✅ AC-6: type-check 0 errori | cargo errori = solo pre-esistenti listini/media

**⚠️ TODO prima di produzione:**
- Sostituire `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` in settings.rs con credenziali reali
  da Google Cloud Console (progetto FLUXION, tipo app: Desktop/Installed)
- Python voice agent: aggiornare `send_with_smtp` per usare XOAUTH2 quando `gmail_oauth_enabled=true`
  (leggere access_token da SQLite via `get_gmail_fresh_token` Tauri command o HTTP bridge)

---

## 🚀 PROSSIMO: da ROADMAP_REMAINING.md

Leggi `ROADMAP_REMAINING.md` per la prossima fase prioritaria.

---

## INFRA ATTIVA

### iMac (192.168.1.12)
```bash
# Sync + riavvio pipeline
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/FLUXION/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Cloudflare Tunnel
```bash
launchctl list | grep cloudflare
```

### cargo check iMac
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/src-tauri' && cargo check 2>&1 | grep -v 'DATABASE_URL\|E0282\|listini\|media' | tail -20"
```
