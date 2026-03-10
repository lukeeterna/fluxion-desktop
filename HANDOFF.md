# FLUXION — Handoff Sessione 45 → 46 (2026-03-10)

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
Branch: master | HEAD: 14538a7
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo errori pre-esistenti in listini.rs/media.rs (invariati, NON toccare)
iMac: sincronizzato ✅ | pipeline UP porta 3002 | Cloudflare Tunnel LaunchAgent attivo
```

---

## ✅ COMPLETATO SESSIONE 45

### P1.0 — Impostazioni Redesign (commit 14538a7)
**Impatto**: PMI trova qualsiasi impostazione in <10s — zero scroll infinito, zero abbandono

**File creati/modificati:**
- `src/hooks/use-impostazioni-status.ts` (NUOVO) — badge stato per 11 sezioni
  - Query: `get_smtp_settings` + `get_setup_config` + `useOrariLavoro` + `useImpostazioniFatturazione`
  - Logica: email (smtp_email_from+smtp_enabled), sara (gsk_...), orari (count>0), fatturazione (denominazione)
- `src/pages/Impostazioni.tsx` — riscrittura completa (sidebar Linear pattern)
  - Layout: `-m-6 flex min-h-full` / sidebar `w-60 sticky top-0 self-start max-h-screen`
  - 4 macro-gruppi: ATTIVITÀ / COMUNICAZIONE / AUTOMAZIONE / SISTEMA
  - 11 sezioni con `id` per deep-link + IntersectionObserver scroll-spy
  - `SectionHeader` con badge stato inline
  - Deep link: `useEffect` su `window.location.hash` al mount + `window.history.replaceState` al click
  - 8 rename plain language obbligatori applicati
- `src/pages/Dashboard.tsx` — aggiunto `QuickSetupBanner`
  - Mostra se Sara non attiva (error) O email non configurata (optional/warning)
  - Deep link `/impostazioni#sara` e `/impostazioni#email`
  - Dismissibile via `localStorage` key `fluxion-setup-banner-dismissed-v1`

### Acceptance Criteria verificati:
- ✅ AC-1: Discoverability — sidebar 4 gruppi, 11 sezioni visibili in <10s
- ✅ AC-2: Badge stato — ogni sezione ha ✅/⚠️/🔴/⚪
- ✅ AC-3: Plain language — zero "SMTP", "SDI", "QR" come label primari
- ✅ AC-4: Deep link — `/impostazioni#[id]` funziona con scrollIntoView
- ✅ AC-5: Quick setup banner — Dashboard mostra avvisi con deep-link
- ✅ AC-6: Sidebar sticky — `sticky top-0 self-start max-h-screen`
- ✅ type-check: 0 errori

---

## 🚀 PROSSIMO: P0.6 — Gmail OAuth2

**Prerequisito soddisfatto**: sezione "Email per le notifiche" esiste nella nuova sidebar

**Goal**: Aggiungere OAuth2 come opzione di autenticazione nella sezione email (IN AGGIUNTA a SMTP, non sostituzione)

### Architettura P0.6:
- `tauri-plugin-oauth` + PKCE + keychain macOS
- Trigger contestuale in `Fornitori.tsx` al primo invio ordine (NON nel wizard)
- Research file: `.claude/cache/agents/p06-onboarding-gmail-cove2026.md`
- NON aggiungere step al wizard (8 step rimangono 8)

### File chiave P0.6:
- `src-tauri/Cargo.toml` — aggiungere `tauri-plugin-oauth`
- `src-tauri/src/commands/settings.rs` — aggiungere comando OAuth2 token exchange
- `src/components/impostazioni/SmtpSettings.tsx` — aggiungere bottone "Connetti con Google"
- `src/pages/Fornitori.tsx` — trigger contestuale al primo invio email ordine

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
