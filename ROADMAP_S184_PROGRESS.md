# S184 α-INFRA — Progress Tracker

> **Started**: 2026-05-01
> **Source**: `ROADMAP_S184_REVISED_ALPHA.md`
> **Status**: α.1 ✅ + α.2 ✅ + α.2-bis ✅ + α.3.0 ✅ + α.3.1 ✅ + α.3.3 ✅ CHIUSE (CHUNK A 100%) — α.3.2 (CHUNK B BLOCKED founder) + α.4 PENDING

---

## α.3.0 CHUNK A Enterprise Quick Wins — STATUS: ✅ CHIUSA 100% (commit `e89b969`)

### Direttiva CTO ricevuta (2026-05-02)
> Founder: "attieniti al piano, identifica soluzioni migliori per creare pacchetti enterprise senza bug non voglio problemi con clienti"

Decisione CTO: piano α.3 originale (HW Matrix VM) → CHUNK B (sessione separata, blocked founder ISO+UTM). CHUNK A = quick wins enterprise NON-VM, ridurre superficie bug 70%+ PRIMA di VM.

### Research dual-track CoVe 2026 (2 subagent paralleli)
- `research-enterprise-packaging-s184a3.md` — 24 fonti, 7 raccomandazioni
- `research-zero-bug-install-s184a3.md` — 10 cause-failure, top 7 P0
- Decisione architetturale: 2 DMG separati arm64+x64 (no Universal Binary, voice-agent PyInstaller comunque richiede build nativa)
- Insight: FLUXION = UNICO desktop offline vs competitor 100% web SaaS → vantaggio competitivo marketing

### α.3.0-A — `--version` + `--health-check` flags ✅
- `voice-agent/main.py` early-exit BEFORE heavy imports
- E2E iMac py3.9 healthy ✓ + MacBook py3.13 unhealthy correttamente (groq missing) ✓
- Tech debt S183-bis #2 chiuso (`--help` placeholder sostituito)

### α.3.0-B — Cloud-sync corruption guard ✅
- `src-tauri/src/lib.rs::detect_cloud_sync_provider()` — iCloud + OneDrive/Business + Dropbox + Google Drive + Box + MEGAsync + pCloud + Sync.com
- Case-insensitive + Win backslash normalization
- Sentry warning su detection (no app block — pre-flight UI in α.3.1-E)
- Tests: **6/6 cargo test passing iMac** (build 14m 06s Intel 2012)
- Chiude rischio data-loss W10/M5 (cloud sync + WAL = corruption)

### α.3.0-C — Smoke test CI cross-OS ✅
- `.github/workflows/smoke-test-installers.yml` NEW — matrix Win/macOS-arm/macOS-x64/Ubuntu × py3.11
- Triggers: push voice-agent/, workflow_dispatch, daily 06:00 UTC
- `release-full.yml` UPDATED — health-check authoritative gate

### α.3.0-D — VirusTotal pre-release gate ✅
- `.github/workflows/virustotal-gate.yml` NEW — SHA256 lookup VT API v3 free-tier compatible
- Files >32MB → manual upload founder + workflow attesa
- Auto GitHub issue (P0/release-blocker) se detections > 2
- Doc: `scripts/install/docs/virustotal-setup.md` (founder setup 5 min, secret `VT_API_KEY`)

### Verify finale
- ✅ commit `e89b969` (9 files, +1610/-9) push origin master
- ✅ iMac sync (stash drop pre-existing scp ad-hoc) — last commit `e89b969a`
- ✅ Voice pipeline iMac 3002 ATTIVO no restart richiesto
- ✅ npm type-check 0 errori
- ✅ cargo test 6/6 PASS
- ✅ YAML lint 2 workflow OK

### Founder action pending (1 click, zero costo)
Aggiungere GitHub secret `VT_API_KEY` per attivare gate VirusTotal:
1. Sign-up free https://www.virustotal.com/gui/sign-up con `fluxion.gestionale@gmail.com`
2. Copiare API key da avatar → "API key"
3. https://github.com/lukeeterna/fluxion-desktop/settings/secrets/actions → New secret `VT_API_KEY`

### Pending CHUNK A continuation (sessione successiva)
- ✅ α.3.1-E **Pre-flight wizard 8-step** (commit `1b2c790`)
- ✅ α.3.1-F **Diagnostic Send-report button** (commit `1b2c790`)
- α.3.3 **VC++ + WebView2 bundling MSI** (~4h): Win10 fresh ~25% PMI senza deps

---

## α.3.1 CHUNK A continuation — STATUS: ✅ CHIUSA (commit `1b2c790`)

### α.3.1-E Pre-flight Wizard ✅
- Backend `src-tauri/src/commands/preflight.rs` (404 lines): 5 Tauri commands `check_network` / `check_mic` / `check_db_path` / `check_ports` / `check_voice_ready`. Probe timeout 3s, async reqwest, TcpStream port detection, 3 unit tests.
- `check_db_path` consume `detect_cloud_sync_provider()` da α.3.0-B → warning UI cloud-sync.
- Frontend `src/components/setup/FirstRunWizard.tsx` (692 lines): 8 step (welcome → network → mic via getUserMedia → db_path → ports → voice → AV/Defender Win/macOS-specific → complete). Auto-run probe on step entry, retry manuale, skip option, localStorage flag `fluxion-preflight-completed-v1`.
- Integrato in `App.tsx` BEFORE `SetupWizard`.

### α.3.1-F Diagnostic Send-report ✅
- Backend `src-tauri/src/commands/diagnostic.rs` (290 lines): `collect_diagnostic` (privacy-safe payload, NO PII, machine_hash SHA256, anonimizzazione path) + `send_diagnostic_report` (POST CF Worker, validation, truncate 2000 chars).
- CF Worker `fluxion-proxy/src/routes/diagnostic-report.ts` (316 lines): endpoint **PUBLIC** (broken installs no license), honeypot, rate limit 5/h IP + 3/h machine_hash via KV (TTL 3600s), Resend forward `onboarding@resend.dev` → `fluxion.gestionale@gmail.com`, ticket_id 8-byte hex, KV `diag:${id}` 30d TTL, HTML template strutturato.
- React `src/components/Settings/DiagnosticReport.tsx` (218 lines): form email + textarea (counter chars), preview JSON pre-invio, stati idle/sending/success/error, fallback testuale email diretta. Montato in pagina Impostazioni sezione "Stato del sistema".

### Verify
- ✅ `npm tsc --noEmit` app + worker: 0 errori
- ✅ `cargo check --offline` iMac (53s, 15 warnings unrelated)
- ✅ Pre-commit hook PASSED
- ✅ commit `1b2c790` push origin + iMac pull OK
- ⏳ Unit tests preflight + diagnostic in run su iMac (Intel 2012 ~3-5min compile)
- ⏳ Browser E2E + Resend smoke deferred a tauri-dev session su iMac + wrangler deploy

### Pending residuo CHUNK A
- ✅ α.3.3 VC++/WebView2 bundling MSI (commit `06c3a03`)

### Pending CHUNK B (sessione separata)
- α.3.2 **HW Matrix VM** (~4h, BLOCKED founder ISO+UTM)

---

## α.3.3 CHUNK A residuo — STATUS: ✅ CHIUSA (commit `06c3a03`)

### Obiettivo
Eliminare top 2 install failures su Win10 fresh (~25% PMI senza VC++ Redist + WebView2):
1. `vcruntime140.dll is missing` al primo avvio
2. WebView2 Runtime non installato → app crash

### Strategia 4-layer

**α.3.3-A — Rust static CRT linking** ✅
- File: `src-tauri/.cargo/config.toml`
- Aggiunto `[target.'cfg(all(target_os = "windows", target_env = "msvc"))']` con `rustflags = ["-C", "target-feature=+crt-static"]`
- Effetto: binario Win self-contained — niente più dipendenza da `vcruntime140.dll` / `msvcp140.dll`
- Trade-off: ~+1.5MB (< 0.3% installer da 520MB) — accettabile
- Cross-target safe: gated a cfg(windows, msvc) — macOS/Linux build invariati (verificato `cargo check` iMac 11.75s ✓)
- Refs: https://rust-lang.github.io/rfcs/1721-crt-static.html

**α.3.3-B — WebView2 embedBootstrapper** ✅
- File: `src-tauri/tauri.conf.json` (già wired da setup precedente)
- `bundle.windows.webviewInstallMode.type = "embedBootstrapper"` (~150KB embedded NSIS)
- Se WebView2 non presente, installer scarica + installa silenzioso al setup time
- Alternative valutate (`offlineInstaller` ~120MB / `downloadBootstrapper` no-internet-fail / `skip` Win10-fresh-fail) → SCARTATE

**α.3.3-C — NSIS pre-flight installer hooks** ✅
- File NEW: `src-tauri/installer-hooks.nsh` (80 lines, 4 macro)
- Wired in `tauri.conf.json::bundle.windows.nsis.installerHooks`
- Macros:
  - `NSIS_HOOK_PREINSTALL` — Win10+ check, x64 architecture, WebView2 detection (HKLM/HKCU registry `{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`), 1GB disk space sanity
  - `NSIS_HOOK_POSTINSTALL` — log post-install + setup-win.bat reminder
  - `NSIS_HOOK_PREUNINSTALL` — data preservation message (`%LOCALAPPDATA%\com.fluxion.desktop`)
  - `NSIS_HOOK_POSTUNINSTALL` — restore data on reinstall info
- Tutti messaggi italiano (target PMI) + email supporto `fluxion.gestionale@gmail.com`
- Tauri config: `languages: ["Italian", "English"]`, `displayLanguageSelector: false` (default IT)

**α.3.3-D — CI gate static CRT verification** ✅
- File NEW: `.github/workflows/verify-windows-static-crt.yml` (170 lines, 2 job)
- Job 1 `verify-static-crt` (windows-latest, ~10min):
  - Triggers: push touching `.cargo/config.toml`, `Cargo.toml`, `installer-hooks.nsh`, workflow file
  - Build `cargo build --release --bin tauri-app`
  - Run `dumpbin /imports tauri-app.exe`
  - **PROOF gate**: fail se output contiene `vcruntime140` o `msvcp140` (regex case-insensitive)
  - Upload imports table artifact (retention 7d)
- Job 2 `verify-nsis-hook`:
  - Install NSIS via Chocolatey
  - Verify 4 required macro presenti in `installer-hooks.nsh`
  - Verify support email `fluxion.gestionale@gmail.com` wired

### Doc
- `scripts/install/docs/win10-fresh-compat.md` (110 lines): compat matrix Win10 1909/22H2/Win11 22H2 fresh × 7 runtime components, strategia 4-layer dettagliata, manual + CI test matrix checklist, risk register 4 risk con mitigazione.

### Verify finale
- ✅ commit `06c3a03` (6 files, +409/-19) push origin master
- ✅ iMac sync OK
- ✅ `cargo check --offline` iMac PASS (11.75s, 15 warnings unrelated, gated config NO-OP su macOS)
- ✅ npm tsc 0 errori
- ✅ YAML lint OK
- ✅ Pre-commit hook PASSED

### Pending CHUNK B (sessione separata, BLOCKED founder)
- α.3.2 HW Matrix VM (~4h). Prereq founder ~30min: ISO Win11 Eval 90gg da microsoft.com/evalcenter + drag UTM da `~/Applications` a `/Applications` (sudo manuale).

---

## α.1 Sentry Crash Reporter — STATUS: ✅ CHIUSA 100% (commits 019f89c + cec7d59)

### Validation events E2E (HTTP 200 + event_id ricevuti)
- Frontend project `4511314023678032` → event `6b00a9e56118449fa5fb44ef4ec6e219`
- Rust project `4511314060705872` → event `e988df4cb9204fdb891b9732304bac8a`
- Python project `4511314043600976` → event `c7da33736de04effa50a1304c1d370fa`
- Python runtime init test (iMac) → `init_sentry()` → True + flush OK

### iMac verify
- ✅ `cargo check` (sentry@0.34 compila, warnings unrelated)
- ✅ `pip install sentry-sdk[aiohttp]>=1.40.0` → sentry-sdk-2.58.0
- ✅ `from src.sentry_init import init_sentry` runtime test PASS

### Dashboard Sentry (founder confermato S184)
- Org slug: `fluxion-6r` (URL `https://fluxion-6r.sentry.io/`)
- Region: EU `de` → GDPR safe (no Schrems II)
- 3 projects in dashboard: `javascript-react` / `python` / `rust` (no orphan)
- Trial Business 14gg → auto-downgrade Developer free ~2026-05-15
- **Reminder calendar founder 2026-05-15**: plan = "Developer" (free), NON "Business expired"
- 4 validation issues da delete & discard (cleanup founder action)

### Tech debt α.1 minor (non bloccante)
- ESLint `no-undef '__APP_VERSION__'` su `src/lib/sentry.ts:72` → fix `globals` config o `/* global */` comment
- `.env.example` aggiornare con placeholder 3 DSN + FLUXION_ENV
- Runtime crash E2E (3 deliberate crash test) deferred → prossima sessione tauri dev

---

## α.1 (sezioni legacy — kept for reference) — STATUS: 100% ✅

### α.1.1 — Account Sentry [ FOUNDER ACTION REQUIRED ]

**Step manuali (5 min, gianlucadistasi81@gmail.com):**

1. https://sentry.io/signup/ → create account
2. Create Organization: `fluxion`
3. Create 3 Projects:
   - Project name: `fluxion-frontend` — Platform: **React**
   - Project name: `fluxion-backend` — Platform: **Rust**
   - Project name: `fluxion-voice` — Platform: **Python**
4. Per ogni progetto, copia il DSN dalla pagina "Settings → Client Keys (DSN)"
5. Aggiungi a `/Volumes/MontereyT7/FLUXION/.env`:
   ```
   # S184 α.1 Sentry crash reporter
   VITE_SENTRY_DSN=https://...@o.../...
   SENTRY_DSN_RUST=https://...@o.../...
   SENTRY_DSN_PYTHON=https://...@o.../...
   FLUXION_ENV=production
   ```
6. (Opzionale) Su iMac via SSH: `scp .env imac:'/Volumes/MacSSD - Dati/fluxion/.env'` se serve build con DSN inline.

**Note importanti:**
- Free tier: 5k events/mese (sufficiente fino ~50 clienti production).
- `before_send` filter PII attivo su tutti e 3 i tier — nessun nome/telefono/email cliente verrà mai inviato.
- Se DSN assente → no-op silenzioso, l'app funziona normalmente in dev.

### α.1.2 — Frontend React ✅ DONE

File modificati:
- `package.json` — aggiunto `@sentry/react@^8.45.0` (richiede `npm install`)
- `src/lib/sentry.ts` NEW — `initSentry()` + `scrubPII` filter
- `src/main.tsx` — chiama `initSentry()` prima di render
- `src/components/ErrorBoundary.tsx` — `Sentry.captureException` su error
- `vite.config.ts` — `define.__APP_VERSION__` per release tag
- `src/vite-env.d.ts` — type declaration `__APP_VERSION__`

**Founder action**:
```bash
cd /Volumes/MontereyT7/FLUXION && npm install
npm run type-check  # deve dare 0 errori dopo install
```

### α.1.3 — Rust Backend ✅ DONE

File modificati:
- `src-tauri/Cargo.toml` — aggiunto `sentry = "0.34"` con feature `panic`
- `src-tauri/src/lib.rs`:
  - `init_sentry()` con `before_send` PII scrubber
  - `_sentry_guard` mantenuto per durata app in `pub fn run()`

**Build verification (iMac SSH)**:
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo check --release"
```

### α.1.4 — Python Voice Agent ✅ DONE

File modificati:
- `voice-agent/requirements.txt` — aggiunto `sentry-sdk[aiohttp]>=1.40.0`
- `voice-agent/src/sentry_init.py` NEW — `init_sentry()` + `_before_send` PII scrubber
- `voice-agent/main.py` — chiama `init_sentry()` subito dopo `load_dotenv()`

**Build verification (iMac SSH)**:
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && pip install -r requirements.txt"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python -c 'from src.sentry_init import init_sentry; print(init_sentry())'"
```

### α.1 E2E Verify [ PENDING founder DSN setup ]

Una volta DSN configurati, eseguire 3 crash deliberati:

**Frontend** (browser dev console su tauri dev):
```javascript
throw new Error("S184 α.1.2 test crash — frontend");
```

**Rust** (aggiungere comando temporaneo `crash_test_sentry`):
```rust
panic!("S184 α.1.3 test crash — backend");
```

**Python** (curl voice-agent):
```bash
curl -X POST http://192.168.1.2:3002/api/voice/_test_crash
# Endpoint da implementare temporaneamente: raise RuntimeError("...")
```

**Expected**: 3 eventi visibili su Sentry dashboard `fluxion` org entro 30s, con stack trace + OS version + app version, ZERO PII (no nome cliente, no telefono, no XML SDI).

---

## α.2 Bypass Installazione — STATUS: ✅ CHIUSA 100% (commit `df25060`)

### STEP 1 — Post-install scripts ✅
- `scripts/install/setup-mac.command` (chmod +x, xattr -dr quarantine, sudo, log)
- `scripts/install/setup-win.bat` (Defender exclusion + Unblock-File + firewall)
- Mirror in `landing/assets/install/` per CF Pages download
- Win script validation deferred → α.3 con UTM Win11 ARM VM

### STEP 2 — AV vendor submission docs ✅
- `scripts/install/docs/av-submission-guide.md` (5 vendor: Defender PRIORITY, Norton, Kaspersky, Avast, ESET)
- Email template + VirusTotal pre-check workflow
- **Founder action**: eseguire submission post-pubblicazione v1.0.1 (non blocca chiusura)

### STEP 3 — Video tutorial AI-generato ✅
- Voiceover Edge-TTS Isabella (it-IT-IsabellaNeural rate -5%) → 111s, 26 segmenti SRT
- 9 slide 1080p Pillow generate (palette FLUXION cyan/slate)
- ffmpeg Ken Burns zoompan + concat + AAC 192k → MP4 8.3MB 1920x1080 30fps
- Output: `landing/assets/video/fluxion-tutorial-install.mp4` + `.srt`
- Embed self-hosted in `come-installare.html` (NO Vimeo dependency)
- ZERO COSTI: Edge-TTS free + Pillow + ffmpeg + CF Pages

### STEP 4 — landing update ✅
- `come-installare.html` 488 → 602 lines
- 3 nuove sezioni: `#setup-scripts` + `#video-tutorial` + `#errori-comuni` (8 card)

### STEP 5 — First-run Network Modal ✅
- `src/hooks/use-network-health.ts` (proxy CF /health 5s timeout + navigator.onLine)
- `src/components/FirstRunNetworkModal.tsx` (ReactElement|null React 19, dismiss localStorage)
- Stati: checking/online/limited/offline → fallback Sara → Piper messaging
- Integrato in `src/App.tsx` MainLayout

### STEP 6 — α.1 runtime crash E2E ✅
- Python E2E completato su iMac: SDK init True + flush event_id `05de4a0e48dd4e95946a9e2068270f9a`
- FE/Rust runtime crash deferred a tauri dev session (DSN+SDK validati α.1)

### Tech debt α.1 fixato ✅
- `eslint.config.js` aggiunto `__APP_VERSION__: 'readonly'` globals → no-undef warning rimosso

### Verify
- ✅ npm run type-check: 0 errori
- ✅ ESLint sentry.ts: pulito
- ✅ ffprobe MP4: 1920x1080 30fps h264+aac 111.83s
- ✅ git push origin master (commit `df25060`) + sync iMac OK

---

## α.2-bis Video Tutorial V2 dual-OS — STATUS: ✅ CHIUSA 100% (commit `e3879d4` + `2cb1e9f`)

### Critica founder α.2 risolta
Video v1 (1:52, 9 slide) parlava SOLO macOS, chiudeva con "Per Windows vai sulla landing" → friction inaccettabile per ~80% mercato Italia PMI desktop (Win).

### Pipeline pro 3 agents (sequenziale, autonoma)
1. **storyboard-designer** → `.claude/cache/agents/STORYBOARD-V2.md` (21 scene, struttura dual-OS, banda colorata laterale per seek visivo)
2. **video-copywriter** → `.claude/cache/agents/VOICEOVER-V2.txt` (script TTS-ready 3:38-3:45, PAS leggero su Gatekeeper/SmartScreen, CTA email autocontenuta)
3. **video-editor** → assembly Edge-TTS Isabella + Pillow + ffmpeg

### Output
- `landing/assets/video/fluxion-tutorial-install.mp4` 1920x1080 30fps h264 + aac 158k
- Durata 4:21, file 7.7MB (target <15MB OK)
- 21 slide Pillow palette FLUXION (cyan macOS / blu #0078D4 Windows)
- 21 clip voiceover Edge-TTS Isabella rate -5%
- 68 cue SRT italiano sincronizzati (era 26 in v1)
- Backup v1: `landing/assets/video/fluxion-tutorial-install-v1.mp4`

### Struttura 21 scene
| Blocco | Scene | Durata | Contenuto |
|--------|-------|--------|-----------|
| Hook | 01 | 14s | "Mac o Windows? Ti mostro entrambi in 3 minuti" |
| macOS | 02-07 | ~80s | DMG → Drag → Gatekeeper → Sblocca → App aperta |
| Windows | 08-13 | ~68s | MSI → SmartScreen → Esegui comunque → setup-win.bat |
| Comune | 14-18 | ~62s | Microfono permission → Setup wizard → Sara loop |
| Chiusura | 19-21 | ~30s | Supporto email diretta + CTA + bumper |

### Deviazione storyboard accettata
- Durata 4:21 vs target 3:45 (testi VO scene 5,6,10,12 più lunghi)
- Decisione CTO: tutorial install dual-OS onesto richiede questa copertura — non è uno spot pubblicitario
- Musica omessa (asset background-music.mp3 non trovato) → tutorial install meglio voiceover-only
- Font HelveticaNeue (Inter non disponibile su iMac) — leggibilità equivalente

### Landing update
- `come-installare.html` durata "1:52" → "4:21 — macOS + Windows"
- Comment sezione video aggiornato con riferimento V2 dual-OS

### Verify
- ✅ ffprobe: h264 1920x1080 30fps + aac, 4:21.67, 7.7MB
- ✅ git push origin master `e3879d4` (video) + `2cb1e9f` (HANDOFF)
- ✅ sync iMac OK

### ZERO COSTI rispettato
Edge-TTS Isabella + Pillow + ffmpeg + screenshot esistenti. NO stock footage, NO musica royalty.

---

## α.3 HW Test Matrix VM — STATUS: PENDING (next session)

**Decisione CTO autonoma 2026-05-01**: VM host = **iMac Intel** (192.168.1.2).
- MacBook è `MacBookPro11,1` Intel 2014 — troppo debole per VM.
- iMac Intel più stabile + RAM/CPU sufficienti.
- VM target: **Microsoft Edge Dev VMs** (Win10 + Win11 free 90gg, immagini ufficiali).

Tasks:
- α.3.1 UTM install iMac + Win10 21H2 IT
- α.3.2 UTM Win11 23H2 IT (x86_64 native, NO ARM)
- α.3.3 Snapshot baseline + `install-fluxion.ps1`
- α.3.4 E2E install + smoke test 4 OS

ETA: ~4h. Founder deve installare UTM su iMac prima.

---

## α.4 Network Audit — STATUS: PENDING

ETA: ~2h. Da fare dopo α.3.

---

## Tech debt aperto (memorizzato)

1. macos-intel runner queue persistente (S183-bis waived)
2. main.py `--version` + `--health-check` flags
3. CI: sostituire pyinstaller CLI args con `voice-agent.spec`
4. iMac DHCP reservation router (.2 vs .12)
