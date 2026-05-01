# S184 α-INFRA — Progress Tracker

> **Started**: 2026-05-01
> **Source**: `ROADMAP_S184_REVISED_ALPHA.md`
> **Status**: α.1 CHIUSA ✅ (LIVE 3-tier validato E2E) — α.2/α.3/α.4 PENDING

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

## α.2 Bypass Installazione — STATUS: PENDING (next session)

Tasks da S184 roadmap:
- α.2.1-α.2.2 Post-install scripts macOS + Windows
- α.2.3-α.2.4 Vendor AV submission (Microsoft Defender, Norton, Kaspersky, Avast)
- α.2.5 Video tutorial 3min OBS
- α.2.6 `come-installare.html` add 8 errori comuni
- α.2.7 First-run network failure modal

ETA: ~4h. Riprendere dopo α.1 E2E verify.

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
