# FLUXION — PRE-LAUNCH AUDIT 6 CATEGORIE (S245)

**Generato**: 2026-05-15
**Repo**: master `30bd1f8`
**Mandato founder S244**: "se devo partire deve essere tutto pronto e pienamente funzionante"
**Vincolo**: NO MVP, NO lancio parziale. Si shippa solo con tutti P0 verdi.

---

## CATEGORIA 1 — BUILD / DISTRIBUTION

### Tabella riassuntiva

| Feature/Aspetto | Stato | Evidence (file:line OR comando) | P0/P1/P2 | Effort |
|-----------------|-------|----------------------------------|----------|--------|
| macOS DMG ad-hoc signed | ⚠️ PARZIALE | `tauri.conf.json:32` `signingIdentity=null` (ad-hoc OK) + `bundle.targets=["dmg","app","nsis"]`. v1.0.0 DMG presente (74MB), v1.0.1 ZERO assets. | **P0** | 2-3h (re-trigger pipeline + asset attach) |
| macOS PKG installer | ❌ ASSENTE | Solo DMG configurato. `bundle.targets` NON include "pkg". v1.0.0 ha `.pkg` (71MB) ma generato fuori pipeline (manuale). | P1 | 2h (script PKG + integrazione CI) |
| Windows MSI/NSIS | ⚠️ PARZIALE | `bundle.targets` include "nsis" + `installer-hooks.nsh` (4907 byte) presente. NSIS lang IT+EN. **MSI NON configurato** (solo NSIS .exe). | **P0** | 3-4h (aggiungere wix MSI target + test signed) |
| Universal Binary (Intel+arm64) | ❌ NO | CI matrix `release-full.yml:36-43` = SOLO `macos-14` (arm64). Intel macos-13 escluso ("runner queue persistente"). Nessun `lipo` UB step. v1.0.0 ha solo `x64.dmg`. | **P0** | 4-6h (riabilitare macos-13 OR fare UB con lipo su iMac) |
| Auto-updater endpoint live | 🔴 **BROKEN** | `curl https://github.com/lukeeterna/fluxion-desktop/releases/latest/download/latest.json` → **HTTP 404**. `tauri.conf.json:71-77` punta a quell'URL ma `latest.json` mai pubblicato. | **P0** | 1h (generare + upload latest.json a v1.0.1) |
| Auto-updater signing key | 🔴 **DISABLED** | `release-full.yml:294-296` commenti: "TAURI_SIGNING_PRIVATE_KEY_PASSWORD secret mismatch — Auto-update infrastructure DISABILITATA temporaneamente". `createUpdaterArtifacts:false` in tauri.conf. Pubkey statica `RWRqEGaKs2CWiWHG...` ma firma assente. | **P0** | 1h founder action: rigenerare key `tauri signer generate` + secrets GH |
| Auto-updater client | ✅ OK | `src/hooks/use-updater.ts` + `src/components/updater/UpdateDialog.tsx` + plugin Rust `lib.rs:568`. Implementazione completa lato app. | — | — |
| Sidecar Voice Agent bundled | 🔴 **PLACEHOLDER** | `src-tauri/binaries/voice-agent-x86_64-apple-darwin` = shell script di 296 byte: `echo "voice-agent placeholder — use Python source in development"; exit 1`. Manca anche arm64 + windows binari. | **P0** | 2-3h per target (build PyInstaller su iMac + Win runner) |
| PyInstaller spec ufficiale | ✅ OK | `voice-agent/voice-agent.spec` esiste, ben strutturato (datas piper/silero_vad, espeak-ng-data inclusi). CI usa CLI inline invece dello spec (tech debt). | P1 | 30min (CI usare `.spec`) |
| Version checking client | ✅ OK (logica), 🔴 endpoint | `use-updater.ts:7` chiama `check()` plugin-updater che colpisce endpoint 404 → fallirà silente. | **P0** | parte di fix endpoint sopra |
| Version sync 3 file | 🔴 **MISMATCH** | `package.json:3 version=1.0.1` / `src-tauri/tauri.conf.json:4 version=1.0.1` / `src-tauri/Cargo.toml:3 version=1.0.0` → Cargo è 1.0.0 mentre Tauri 1.0.1 ⇒ binary `CARGO_PKG_VERSION=1.0.0` ≠ `appVersion`. | **P0** | 5min (bump Cargo.toml a 1.0.1) |
| macOS Gatekeeper mitigation page | ✅ OK | `landing/come-installare.html` (esiste, completa con FAQ + VirusTotal link + Obsidian/Calibre social proof) + `scripts/install/setup-mac.command` rimuove xattr `com.apple.quarantine`. | — | — |
| Windows SmartScreen mitigation | ✅ OK | `scripts/install/setup-win.bat` add Defender exclusion + remove MotW + firewall loopback. Distribuzione separata via GH Releases (NON nel MSI). | P1 | 1h (auto-include in MSI installer-hooks.nsh) |
| Entitlements macOS | ✅ OK | `src-tauri/entitlements.plist`: audio-input, network client/server, files RW, allow-jit, allow-unsigned-executable-memory, disable-library-validation, automation. Coerente con sidecar Python. | — | — |
| Compatibility minima | ⚠️ DRIFT | `tauri.conf.json:33 minimumSystemVersion=10.15` (Catalina). CLAUDE.md `architecture-distribution.md` dichiara **macOS 12+**. Win10+ non vincolato lato MSI. | P1 | 5min (allineare a 12.0) |
| Build script iMac | ⚠️ BROKEN | `scripts/build-on-imac.sh:25 IMAC_IP="192.168.1.7"` ma MEMORY.md attuale = **192.168.1.2** (DHCP fluttua .2/.12). Script chiama `./build-fluxion.sh` su iMac che probabilmente non esiste. | P1 | 30min (env var IMAC_IP + verifica `build-fluxion.sh`) |
| Pipeline CI full release | ⚠️ PARZIALE | `.github/workflows/release-full.yml` 600 righe, job 1-7 (setup→va→tauri→integration→manifest→audit→summary). Linux escluso da bundle (`tech debt #3`). macos-13 escluso. Trigger tag `v*.*.*` OK. | P1 | — (gap = UB già P0 sopra) |
| Distribuzione zero-cost | ✅ OK | CF Pages (`fluxion-landing.pages.dev`) + GitHub Releases gratis. Nessun S3/CDN paid. | — | — |
| Smoke test installer cross-OS | ✅ esiste | `.github/workflows/smoke-test-installers.yml` (5188 byte). v1.0.1 ZERO assets → smoke test mai eseguito su release reale. | P1 | (parte di re-trigger pipeline) |
| AV submission (VirusTotal) | ✅ docs | `scripts/install/docs/av-submission-guide.md` + `virustotal-setup.md` + workflow `virustotal-gate.yml` (9449 byte). Da rieseguire dopo nuovi MSI signed-or-not. | P1 | 1h (submit nuovi installer post-build) |

### Sintesi P0 BLOCKING — Categoria 1

**8 gap P0** che impediscono lancio:

1. **v1.0.1 release ha ZERO assets** → `gh release view v1.0.1 --json assets` → `{"assets":[]}`. Auto-updater 404, nessuno può scaricare. *(re-triggerare pipeline OR ri-upload manuale)*
2. **`latest.json` endpoint 404** → auto-updater non funziona per chi installa v1.0.0 manuale. *(generare + upload)*
3. **Tauri signing key DISABLED** in CI → updater senza firma valida = client rifiuterà download. *(founder rigenera key)*
4. **Sidecar voice-agent = placeholder script** in repo (`exit 1`). PyInstaller binary non viene mai bundle se non da CI, ma CI bypassa con artifact rename. Locale `npm run tauri build` su iMac = sidecar broken. *(build su iMac + commit binari OR fix path artifact)*
5. **Universal Binary mancante** → Mac Intel utenti non hanno DMG dedicato. v1.0.0 aveva solo `x64.dmg` (= Intel). v1.0.1 niente. CLAUDE.md richiede entrambi. *(lipo UB o doppio target)*
6. **MSI Windows mancante** → solo NSIS .exe. CLAUDE.md "Windows MSI unsigned + SmartScreen mitigation page" come deliverable P0. *(aggiungere wix MSI target)*
7. **Version mismatch Cargo 1.0.0 vs Tauri/package 1.0.1** → binary self-report versione sbagliata, auto-updater compara `1.0.0 == latest` e dichiara "up to date" anche se latest=1.0.2. *(bump 5min)*
8. **`createUpdaterArtifacts: false`** in `tauri.conf.json:7` → pipeline non genera mai `.sig` files anche se signing fosse attivo. *(toggle true + verify)*

### Sintesi P1 quality — Categoria 1

- PKG installer macOS (DMG già copre, ma PKG migliora UX silent install gestiti)
- Setup-win.bat embedded in NSIS installer-hooks (oggi richiede download separato)
- `minimumSystemVersion 10.15 → 12.0` allineamento docs/codice
- `IMAC_IP` script build hardcoded `.7` invece di env var
- AV submission rerun post-rebuild
- PyInstaller CI usare `.spec` invece di CLI inline

### Sintesi P2 marketing — Categoria 1

- VirusTotal badge live su landing/installa
- Mirror download via CF Pages (oggi solo GitHub Releases, single point of failure se GH down)

### Dipendenze (sequenza fix P0)

```
[7] bump Cargo.toml 1.0.1
   └─→ [3] founder rigenera Tauri signing key + GH secrets
       └─→ [8] toggle createUpdaterArtifacts=true
           └─→ [4] build sidecar PyInstaller iMac (arm64+x86_64) + Win
               └─→ [5][6] aggiungere matrix macos-13 + wix MSI target in release-full.yml
                   └─→ tag v1.0.2 → trigger pipeline
                       └─→ [1] assets uploaded (DMG arm64, DMG x64, MSI, NSIS, voice-agent x3)
                           └─→ [2] generate-manifest job pubblica latest.json
                               └─→ ✅ Auto-updater funzionale end-to-end
```

**Effort totale P0 Categoria 1**: ~12-16h sequenziali (founder action #3 unico blocker non self-serve).

---

## CATEGORIA 2 — FUNCTIONAL E2E

### Tabella riassuntiva

| Feature | Stato | Evidence | P0/P1/P2 | Effort |
|---------|-------|----------|----------|--------|
| Gestionale: Calendario | ⚠️ PARZIALE | `src/pages/Calendario.tsx` esiste, 10× "appuntamento". **Drag&drop NON verificato** (no @dnd-kit / FullCalendar in package.json o file). | **P0** | 4-8h (integrare lib o testare custom impl) |
| Gestionale: Clienti CRUD | ✅ OK base | `src-tauri/src/commands/clienti.rs` + `src/pages/Clienti.tsx`. Schede verticali via `019_schede_clienti_verticali.sql` + 027/028/035. | — | — |
| Gestionale: Import CSV clienti | ❓ UNKNOWN | Nessun grep `csv\|papaparse` veloce. Da verificare. | P1 | 2-3h se mancante |
| Gestionale: Servizi/Operatori | ✅ presente | `commands/servizi.rs`, `commands/operatori.rs` + pages. `024_operatori_features.sql`. `src/pages/Operatori.tsx` = 4 righe → **stub** non implementato. | **P0** | 4-6h (implementare CRUD operatori UI) |
| Gestionale: Cassa | ✅ presente | `commands/cassa.rs` + `src/pages/Cassa.tsx`. | — | — |
| Fatture elettroniche SDI | ✅ presente | `commands/fatture.rs:1131-1318` `generate_fattura_xml` con `<FatturaElettronicaHeader>` strutturato + multi-provider `029_sdi_multi_provider.sql`. **Conformità XSD SDI NON validata in CI.** | **P0** | 3-4h (validator XSD + golden test) |
| WhatsApp integration | 🔴 **NON-ENTERPRISE** | `scripts/whatsapp-service.cjs` usa **`whatsapp-web.js`** (Web reverse-engineered, viola ToS WA, ban rischio). NON è Business API ufficiale, NON Baileys. Per clienti paganti €497-897 = unacceptable. | **P0** | 12-20h (migrare a WA Business API OR Baileys con riserva ToS) |
| WhatsApp template approvati | ❌ ASSENTE | Nessuna gestione template Business. Solo invio testo libero (whatsapp-web.js style). | P1 | 4-6h (post WA Business API) |
| WhatsApp reminder/campagne | ✅ schema | `022_whatsapp_invii_pacchetti.sql` migration esiste. Logica invio sopra stack non-enterprise. | (eredita P0 stack) | — |
| Voice Sara telefono (VoIP) | 🔴 **BROKEN** | Pipeline DOWN_OK. Bug pjsua2 SIGABRT non risolto S233→S244 (9 fix S232-S239 falsificati live). Founder mandato: path B1 downgrade pjsip 2.15.1 OR D Asterisk ARI Docker. | **P0** | B1: 2-4h / D: 8-16h |
| Voice Sara web/Tauri | ⚠️ DA VERIFICARE | `src/pages/VoiceAgent.tsx` (903 righe) + `voice.rs` command. Stato test live web ignoto. | **P0** | 2-3h (E2E test web flow) |
| Voice Sara latency | ⚠️ DRIFT | Attuale ~1330ms vs target P95 <800ms (CLAUDE.md). | P1 | 4-8h (streaming LLM + chunked TTS) |
| Marketing: Loyalty | ✅ OK | `commands/loyalty.rs` (1201 righe) con `loyalty_visits/loyalty_threshold` + pacchetto integration. | — | — |
| Marketing: Pacchetti | ✅ OK | Stesso file loyalty.rs gestisce pacchetti (`pacchetto_id/pacchetto_nome`). | — | — |
| Marketing: Scadenze | ❓ UNKNOWN | Da verificare cron/scheduler per scadenze pacchetti. | P1 | 2h (verifica) |
| 9 verticali schede personalizzate | ⚠️ DRIFT 8/9 | `src/types/setup.ts:80-127` 8 macro categorie (medico, beauty, hair, auto, wellness, professionale, pet, formazione). **CLAUDE.md dichiara 9** (saloni, palestre, medical, auto, odonto, vet, servizi, immobiliare, **assicurazioni**). "assicurazioni" assente (incluso in professionale?), "immobiliare" come micro dentro professionale. | P1 | 1h (aggiungere macro `assicurazioni` o aggiornare docs a 8 macro/17 micro) |
| Setup wizard zero-friction | ✅ presente | `src/components/setup/FirstRunWizard.tsx` + `SetupWizard.tsx`. 7 step (azienda, regime, IA key, categoria macro+micro, tier, WA/Ehiweb, Groq). | P1 | 2h (UX test cross-OS prima utilizzo) |
| E2E test suite | ⚠️ presente, stato run? | `e2e/tests/`: 01-smoke, 02-navigation, 03-clienti-crud, 04-servizi-validation, 05-appuntamenti-conflict, booking, cashier, crm, invoice, voice — 10 spec. **Ultimo run su CI: ignoto.** | **P0** | 2h (run completo locale + fix red) |
| TypeScript strict | ✅ EXCELLENT | `npx tsc --noEmit` → 0 errori. 0 `: any` esplicite in src/. | — | — |
| DB migrations | ✅ OK | 37 migration versionate. Ultima `037_gdpr_art9_consent.sql`. | — | — |

### Sintesi P0 BLOCKING — Categoria 2

1. **Calendario drag&drop NON implementato/verificato** — hero feature gestionale. Senza drag&drop UX = competitor (Fresha/Treatwell) immediatamente migliori.
2. **Operatori page = stub 4 righe** — `src/pages/Operatori.tsx` non implementato. Mandatory per multi-staff.
3. **WhatsApp-web.js stack NON enterprise** — viola ToS WA, ban rischio per clienti paganti. Migrare a WA Business API OR Baileys con consenso esplicito ToS.
4. **Sara VoIP broken** — bug pjsua2 9 fix falsificati. Decisione architetturale B1 (downgrade) vs D (Asterisk ARI). Deferred S244, da risolvere prima del lancio.
5. **Sara web/Tauri E2E non testato live** — `VoiceAgent.tsx` 903 righe non significa "funziona".
6. **FatturaPA conformità XSD non validata in CI** — SDI rifiuta XML non conformi → cliente bloccato post-vendita. Validator obbligatorio.
7. **E2E suite stato run ignoto** — 10 spec esistenti ma ultimo verde non tracciato.

### Sintesi P1 quality — Categoria 2

- Import CSV clienti (verifica presenza)
- Sara latency 1330→<800ms (streaming LLM, chunked TTS)
- WhatsApp template Business API approvati
- Verticali drift docs vs codice (assicurazioni)
- Setup Wizard UX test cross-OS
- Marketing scadenze cron scheduler

### Dipendenze Cat 2

```
[stub Operatori] indipendente
[Calendario d&d] indipendente
[Sara VoIP B1/D] indipendente (path founder decision)
[Sara web E2E] dipende da pipeline up
[WA Business API] richiede founder action (account Meta Business)
[FatturaPA validator] indipendente
[E2E run] dipende da: stub Operatori risolto + Calendario d&d
```

**Effort totale P0 Cat 2**: ~30-50h (range a seconda path Sara B1 vs D).



## CATEGORIA 3 — SECURITY

### Tabella riassuntiva

| Aspetto | Stato | Evidence | P0/P1/P2 | Effort |
|---------|-------|----------|----------|--------|
| Ed25519 license verify | ✅ OK | `commands/license_ed25519.rs:1-200` usa `ed25519_dalek::{Signature, Verifier, VerifyingKey}`. Pubkey hardcoded `c61b3c91…7d39`. Hardware-locked via fingerprint. Trial 30gg + grace 7gg offline. | — | — |
| Stripe webhook signature | ✅ OK | `fluxion-proxy/src/routes/stripe-webhook.ts` verifica HMAC-SHA256 + `STRIPE_WEBHOOK_SECRET` env. Fallback `signature verification failed` → 401. | — | — |
| Encryption at rest (AES-256-GCM) | 🔴 **SALT STATICO** | `src-tauri/src/encryption.rs:25` `DEFAULT_SALT = b"FLUXION_GDPR_SALT_v1"` HARDCODED. PBKDF2 100k iter. Stesso salt per ogni installazione = rainbow-table feasibility se DB rubato. Per-installation random salt richiesto (salvato in keychain/credential manager). | **P0** | 3-4h (salt random gen + secure store + migration cifratura esistente) |
| Master password flow | ⚠️ UNKNOWN | `init_encryption(master_password, device_id)` esposto via `gdpr_init_encryption` IPC. Da verificare: chi sceglie/conserva master_password? Auto-generated keychain? User-input setup wizard? Se in DB plain text = catastrofe. | **P0** | 2-3h (audit + fix se necessario) |
| Tauri capabilities allowlist | ✅ OK base | `src-tauri/capabilities/default.json` = `core:default` only (single window "main"). Tauri 2.x `core:default` è conservativo (no fs/shell/process scope esposto). NON espande `fs:allow-*`, `shell:allow-*`. | P1 | 30min (review espliciti se necessari) |
| Tauri CSP | 🔴 **DISABLED** | `tauri.conf.json:csp = null`. Mai impostata Content-Security-Policy. XSS surface su qualsiasi `dangerouslySetInnerHTML` o `eval`. Tauri docs raccomandano CSP `default-src 'self'; script-src 'self'` minimo. | **P0** | 1h (config + test no-regression UI) |
| CF Worker NLU rate limit | ✅ OK (KV fallback) | `fluxion-proxy/src/routes/nlu-proxy.ts` enforce `MAX_NLU_CALLS_PER_DAY=200` per machine_hash via KV (no paid binding). Reset giornaliero. | — | — |
| CF Worker rate limit diagnostic | ✅ OK | `routes/diagnostic-report.ts` 5/h IP + 3/h machine, KV-based. | — | — |
| CF Worker CORS allowlist | ✅ OK | `index.ts` Hono `cors({ origin: [...]})` con array esplicito (NON `*`). | — | — |
| .env in repo | ✅ gitignored | `.gitignore:49` `.env`. `git check-ignore -v .env` conferma ignored. .env presente in MacBook working dir = dev locale OK. | — | — |
| Secrets hardcoded grep | ✅ CLEAN | Grep `password\|api_key\|sk_live\|token = "…"` su .ts/.tsx/.rs/.py/.cjs/.toml → 0 match commitati. | — | — |
| GDPR audit log | ✅ OK | Migration `018_gdpr_audit_logs.sql` schema completo: action/entity/data_before/data_after/changed_fields/gdpr_category/legal_basis/retention_until/ip/user_agent. CHECK constraints validi. Retention policies in `gdpr_settings` configurabili. | — | — |
| Sentry PII scrubbing | ✅ OK | `src-tauri/src/lib.rs sentry::init` con `send_default_pii: false`, `before_send: scrub_pii`, `traces_sample_rate: 0.0` (errors only — coerente free tier). | — | — |
| `cargo audit` in CI | ❌ ASSENTE | Nessun job `cargo-audit` o `cargo-deny` in `.github/workflows/`. Vulnerabilità note dipendenze Rust ignote. | **P0** | 1h (job CI + fix RUSTSEC se presenti) |
| `npm audit` in CI | ❌ NON BLOCCANTE | Nessun gate npm audit. Vite/React ha CVE storiche basse, da auto-fix. | P1 | 30min (job CI + audit-level=high) |
| OWASP ASVS L2 formale | ❌ ASSENTE | Nessun report ASVS. Mancano: V2 Auth (single-user desktop OK), V3 Session, V8 Data Protection (vedi salt sopra), V9 Comms, V14 Config. | P1 | 4-6h (audit report + remediation backlog) |
| HTTP Bridge 3001 auth | ❓ UNKNOWN | Voice agent Python ↔ Rust Tauri via porta 3001 localhost. Da verificare: token auth o solo loopback bind? Se exposed = chiunque su LAN può chiamare. | **P0** | 2h (audit binding + token shared secret) |

### Sintesi P0 BLOCKING — Categoria 3

**5 gap P0 sicurezza**:

1. **Encryption salt statico** — `DEFAULT_SALT = "FLUXION_GDPR_SALT_v1"` hardcoded. Senza per-installation salt random salvato in OS keychain, un DB rubato + brute-force master password = full PII leak. CTO mandatory pre-lancio.
2. **Master password flow ignoto** — se chiesta a setup-wizard senza secure storage = rischio. Audit veloce richiesto.
3. **CSP null** — XSS surface su React 19 desktop app. Tauri 2.x raccomanda CSP esplicita minima.
4. **`cargo audit` mancante in CI** — vulnerabilità note dipendenze Rust possono entrare in v1.0.x. Job free su GH Actions.
5. **HTTP Bridge 3001 auth** — verificare bind 127.0.0.1 + shared secret tra Python ↔ Rust (se LAN-exposed = RCE potenziale).

### Sintesi P1 — Categoria 3

- `npm audit` CI gate (audit-level=high)
- OWASP ASVS L2 audit report formale
- Tauri capabilities review espliciti

**Effort totale P0 Cat 3**: ~8-12h.

---

## CATEGORIA 4 — PERFORMANCE

### Tabella riassuntiva

| Aspetto | Stato | Evidence | P0/P1/P2 | Effort |
|---------|-------|----------|----------|--------|
| SLO definiti | ✅ presenti | `.claude/cache/agents/s182-performance-slo-baseline.md`. SLO P95: startup <2s, IPC <100ms, query <50ms, Sara end-to-end <800ms, UI 60fps. | — | — |
| IPC benchmark | ✅ OK script | `src-tauri/examples/ipc_bench.rs` (S191 D-2) misura `get_clienti`/`get_cliente`/`search_clienti` P50/P95/P99. **Ultimo run live: ignoto.** Eseguire pre-lancio. | **P0** | 1h (run su iMac + report committed) |
| DB indices coverage | ✅ OK | 114 `CREATE INDEX` distribuiti in 37 migration. Tutte le query con WHERE su FK hanno index. | — | — |
| SQLite WAL + PRAGMA | ❓ DA VERIFICARE | Da verificare in `lib.rs` init pool: `journal_mode=WAL`, `synchronous=NORMAL`, `cache_size`, `mmap_size`, `foreign_keys=ON`. | P1 | 1h (audit pool init + benchmark before/after) |
| Sara latency P95 | ⚠️ DRIFT | Attuale ~1330ms vs target <800ms (MEMORY.md). Streaming LLM + chunked TTS non implementati. | P1 | 4-8h |
| Startup time | ❓ DA VERIFICARE | Nessuna misura live recente trovata. | P1 | 2h (profiling cold start macOS + Win) |
| React UI render | ❓ DA VERIFICARE | TanStack Query usato? Memoization? List virtualization su Clienti/Appuntamenti se >1000 row? | P1 | 2-3h (audit + react-window se serve) |
| Bundle size | ❓ DA VERIFICARE | `dist/` size + treeshaking + lazy routes. | P1 | 1h |
| Voice pipeline P95 endpoints | ❓ DA VERIFICARE | `/api/voice/process` latency p50/p95/p99 sotto carico. | P1 | 2h (apachebench/wrk) |

### Sintesi P0 BLOCKING — Categoria 4

**1 gap P0**:

1. **IPC benchmark mai eseguito live** — `ipc_bench.rs` script esiste S191 ma nessun report committed. Senza P95 misurato = SLO non verificato pre-lancio. Eseguire su iMac, salvare risultati `.claude/cache/agents/s246/d2-ipc-bench-live.json`.

### Sintesi P1 — Categoria 4

- Sara latency 1330→<800ms (streaming + chunked TTS)
- Startup time cold profiling
- PRAGMA SQLite audit
- React render audit (virtualization Clienti page se >1000)
- Bundle size analysis

**Effort totale P0 Cat 4**: ~1h.

---

## CATEGORIA 5 — COMPLIANCE

### Tabella riassuntiva

| Aspetto | Stato | Evidence | P0/P1/P2 | Effort |
|---------|-------|----------|----------|--------|
| Privacy policy landing | ✅ presente | `landing/privacy.html` esiste. | P1 | 1h (legal review founder/lawyer) |
| Terms & Conditions | ✅ presente | `landing/termini.html` esiste. | P1 | 1h (legal review) |
| Termini rimborso D.Lgs 206/2005 | ✅ OK | `landing/termini-rimborso.html` cita art. 52, art. 59 lett.o, garanzia 30gg volontaria. Conforme codice consumo software digitale. | — | — |
| Cookie banner landing | ❓ DA VERIFICARE | Da verificare `index.html` / `come-installare.html` per banner. Se Google Fonts/Analytics presenti = obbligo banner. | **P0** | 2-3h (banner cookieconsent.com o equivalente OSS + audit script terze parti) |
| Checkout consent (TOS+Privacy) | ✅ presente | `landing/checkout-consent.html` esiste — flow consenso esplicito pre-Stripe. | — | — |
| GDPR registro trattamenti | ⚠️ schema OK, doc TBD | `gdpr_settings` + `audit_log` Migration 018. Documento Art. 30 GDPR (registro attività trattamento) richiesto per titolare (FLUXION = data processor lato cliente). | P1 | 4-6h (template Art.30 + DPA template per clienti) |
| GDPR export (right to access) | ⚠️ schema | `fluxion-proxy/src/routes/gdpr-download.ts` esiste lato Worker (lead magnet). Export desktop app dati cliente: da verificare comando IPC. | **P0** | 2-3h (comando `export_cliente_data` IPC + JSON dump) |
| GDPR erasure (right to be forgotten) | ⚠️ schema | `action ANONYMIZE` previsto in audit_log. Da verificare comando UI cancellazione cliente con anonimizzazione audit. | **P0** | 2-3h (comando `anonymize_cliente` + UI button) |
| GDPR consenso esplicito | ✅ schema | Migration `037_gdpr_art9_consent.sql` (ultima). Consensi Art. 9 dati particolari (salute clinica/odonto/vet). | P1 | 2h (UI fitness consenso categoria verticale) |
| FatturaPA conformità XSD | 🔴 **NO CI** | `commands/fatture.rs:1131-1318` genera XML SDI ma **nessun validator XSD in CI**. SDI rifiuta XML non conformi → cliente bloccato post-vendita. Schema XSD `Schema_VFPR12.xsd` ufficiale Agenzia Entrate. | **P0** | 3-4h (validator XSD + golden test fixture + CI gate) [duplicato Cat 2] |
| FatturaPA SDI provider multi | ✅ schema | Migration `029_sdi_multi_provider.sql`. Aruba/FattureInCloud/Notebook/etc. | P1 | — |
| FatturaPA invio reale test | ❓ DA VERIFICARE | Test di invio reale verso SDI (sandbox Agenzia Entrate o provider sandbox)? | **P0** | 4-6h (test E2E sandbox con almeno 1 provider) |
| GDPR DPA (Data Processing Agreement) | ❌ ASSENTE | FLUXION processa PII clienti per conto del cliente (titolare). Serve template DPA Art. 28 GDPR per scaricare in checkout. | **P0** | 3-4h (template DPA + landing integration) |
| Codice Fiscale validation | ❓ DA VERIFICARE | Validator CF (omocodia + check digit) per anagrafica cliente? | P1 | 1h (lib o custom) |
| P.IVA validation VIES | ❓ DA VERIFICARE | Validator P.IVA italiana (algoritmo Luhn) + opt-in lookup VIES per FatturaPA estera B2B. | P1 | 2h |
| Conservazione sostitutiva fatture | ⚠️ FUORI SCOPE | Obbligo 10 anni fatture B2B. SDI provider tipicamente offrono (Aruba inclusa). Documentare delega cliente. | P1 | 1h (clausola TOS + FAQ) |

### Sintesi P0 BLOCKING — Categoria 5

**5 gap P0 compliance**:

1. **Cookie banner landing** — se Google Analytics/Fonts/CF Insights presenti su `index.html` = obbligo GDPR/Garante. Audit script terze parti + banner.
2. **GDPR export comando IPC** — `right to access` Art. 15 GDPR richiede export dati cliente in formato strutturato. Schema c'è, comando IPC da verificare/implementare.
3. **GDPR erasure comando IPC** — `right to be forgotten` Art. 17 GDPR. Anonimizzazione audit_log prevista, UI button + comando da verificare.
4. **FatturaPA XSD validator + invio sandbox** — senza validator CI + test invio reale SDI sandbox = primo cliente che emette fattura blocca. Doppio gap (dup Cat 2 + sandbox test).
5. **GDPR DPA template** — Art. 28 GDPR. FLUXION = data processor verso titolare-cliente. Senza DPA firmato = cliente non può legalmente usare FLUXION per dati personali clienti.

### Sintesi P1 — Categoria 5

- Legal review privacy.html + termini.html
- Documento registro trattamenti Art. 30 (interno FLUXION)
- UI consenso Art. 9 dati particolari medico/clinica
- CF/P.IVA validator
- Clausola conservazione sostitutiva 10 anni

**Effort totale P0 Cat 5**: ~14-20h.

---

## CATEGORIA 6 — CUSTOMER SUCCESS

### Tabella riassuntiva

| Aspetto | Stato | Evidence | P0/P1/P2 | Effort |
|---------|-------|----------|----------|--------|
| Setup Wizard zero-friction | ✅ presente | `src/components/setup/FirstRunWizard.tsx` + `SetupWizard.tsx`. 7 step (azienda/regime/IA key/categoria macro+micro/tier/WA-Ehiweb/Groq). | P1 | 2h (UX test cross-OS + screencast) |
| Video tutorial install | ✅ presente | `landing/come-installare.html` embed `assets/video/fluxion-tutorial-install.mp4` + captions IT. | P1 | 1h (verifica asset reale presente vs 404) |
| FAQ landing | ✅ presente | `landing/faq.html` + `come-installare.html` ha FAQ install section. | P1 | 2h (review completezza FAQ Sara/WA/Fatture/Stripe) |
| Help center in-app | ❓ UNKNOWN | Da verificare `src/pages/` per `Help.tsx` o `Support.tsx` o link uscita landing. | **P0** | 3-4h (panel help integrato + link FAQ + contatto) |
| Diagnostic report button | ✅ OK | `src/components/Settings/DiagnosticReport.tsx` + CF Worker route `diagnostic-report.ts` invia email a `fluxion.gestionale@gmail.com`. Honeypot + rate limit + KV audit. | — | — |
| Self-healing voice agent | ✅ docs | `.claude/rules/architecture-distribution.md`: health check /health ogni 30s, 3 fail → kill+restart+notifica. Da verificare implementazione concreta. | **P0** | 2-3h (audit implementation + test fault injection) |
| Auto-update trasparente | ⚠️ partial | `src/hooks/use-updater.ts` + `UpdateDialog.tsx` lato client. Endpoint 404 (vedi Cat 1 P0) → niente notifica update finché latest.json non pubblicato. | (eredita Cat 1) | — |
| Onboarding email post-acquisto | ✅ Resend | `fluxion-proxy/src/routes/stripe-webhook.ts` triggers email Resend post-payment. Sequence email F-3 cron daily 09:00 UTC. | P1 | 2h (test E2E sequence + content review) |
| Trial 30gg gestione | ✅ presente | `fluxion-proxy/src/routes/trial-status.ts` + license_ed25519 trial_days. UI Trial banner countdown da verificare. | P1 | 1h (UI banner trial conta giorni residui) |
| Sentry crash reporter | ✅ configured | Sentry Rust (`lib.rs sentry::init`) + Frontend (`src/main.tsx`). Config zero-cost: `traces_sample_rate=0.0`, `send_default_pii=false`, `before_send=scrub_pii`. Solo errors. | — | — |
| Sentry account plan verify | 🔴 **TODAY** | Trial Business 14gg signup 2026-05-01 → auto-downgrade Developer free **~2026-05-15** (oggi). MEMORY.md: founder verifica plan=Developer (free) NON Business expired (paid). NO carta credito. | **P0** | 5min (founder login Sentry verify plan) |
| Refund flow | ✅ presente | `fluxion-proxy/src/routes/refund.ts` Stripe Refund API. Garanzia 30gg. | P1 | 1h (test E2E refund TEST MODE 4242) |
| Multi-language UI | ❓ DA VERIFICARE | Tutto IT. Per launch nazionale OK. Mai un EN per touristic salons/clinic. | P2 | 4-6h (futuro, post-launch) |
| Backup/Restore DB | ❓ UNKNOWN | Funzione backup DB SQLite + restore? Cliente che cambia PC o crash disk. | **P0** | 3-4h (comando IPC export DB + import + UI Impostazioni) |
| Update changelog visibile | ❓ DA VERIFICARE | Post-update Tauri, modale o pagina changelog visibile? | P1 | 1h |
| Discord/Telegram community? | ⚠️ founder choice | Canale support pre-vendita / community post-vendita? Decisione marketing pure. | P2 | — |
| Onboarding video Sara setup | ❓ DA VERIFICARE | Sara setup richiede Ehiweb credentials + Groq API key. Video tutorial dedicato? | **P0** | 4-6h (script + screencast su iMac + upload Vimeo/YT) |

### Sintesi P0 BLOCKING — Categoria 6

**5 gap P0 customer success**:

1. **Help center in-app** — utente bloccato cerca aiuto dentro l'app. Senza panel Help (FAQ embedded + link landing + contatto diagnostic), fricton support spikes.
2. **Self-healing implementation audit** — docs dicono "health check /health ogni 30s, kill+restart 3 fail". Verificare codice concreto presente in `voice-agent/` o `src-tauri/` (watchdog). Senza = Sara crash silente.
3. **Sentry plan verify TODAY** — 2026-05-15 = oggi è downgrade day. Founder login verifica `fluxion.gestionale@gmail.com` Sentry → Developer free. Se Business expired senza carta = service down. **5 minuti**.
4. **Backup/Restore DB** — cliente perde tutto se crash disk senza export DB. Comando IPC + UI Impostazioni > Backup.
5. **Video tutorial Sara setup** — Sara è il key differentiator. Setup Ehiweb+Groq complicato senza video → activation rate basso → churn alto pre-renewal.

### Sintesi P1 — Categoria 6

- Setup Wizard UX test cross-OS
- FAQ completezza Sara/WA/Fatture/Stripe
- Trial banner countdown UI
- Refund flow E2E test TEST MODE
- Update changelog visibile post-update
- Sequence onboarding email E2E test

**Effort totale P0 Cat 6**: ~12-17h.

---

## SINTESI FINALE — 6 CATEGORIE

### Totale P0 BLOCKING

| Cat | Nome | P0 | Effort range |
|-----|------|-----|--------------|
| 1 | Build/Distribution | 8 | 12-16h |
| 2 | Functional E2E | 7 | 30-50h |
| 3 | Security | 5 | 8-12h |
| 4 | Performance | 1 | 1h |
| 5 | Compliance | 5 | 14-20h |
| 6 | Customer Success | 5 | 12-17h |
| **TOT** | | **31 P0** | **77-116h** |

**Range realistico pre-launch**: ~85-100h sequential (alcune parallelizzabili → ~60-75h wall-clock se 2 stream paralleli).

### Decisioni founder ricorrenti (CTO recommendations)

- **D1 Sara VoIP** → **D Asterisk ARI Docker** (zero-cost, enterprise-robust, +6h vs B1 ma definitivo).
- **D2 WhatsApp stack** → **A Meta Business API (Pro €897)** + **B Baileys+consenso (Base €497)**. **RIFIUTO whatsapp-web.js** (viola ToS).
- **D3 Verticali count** → **aggiornare docs a 8 macro/17 micro** (codice OK, doc drift).

### Sequenza fix consigliata (4 fasi)

```
FASE A (Founder actions, parallel ~1d):
  - D1/D2/D3 decisioni
  - Sentry plan verify (5min)
  - Rigenerare Tauri signing key + GH secrets (1h)
  - Aprire account Meta Business API (D2 path A)
  - Aprire account Ehiweb commerciale (Cat 2 P1)

FASE B (CTO autonomous, Security + Performance + Compliance fondamenta, ~25-35h):
  - Cat 3: encryption salt random + CSP + cargo audit CI + HTTP Bridge auth
  - Cat 4: ipc_bench live run + report
  - Cat 5: FatturaPA XSD validator + GDPR export/erasure IPC + cookie banner + DPA template

FASE C (CTO autonomous, Build + Functional core, ~40-60h):
  - Cat 1: bump Cargo 1.0.1 → toggle createUpdaterArtifacts → sidecar build → MSI/UB targets → release pipeline → latest.json
  - Cat 2: Operatori CRUD UI + Calendario d&d + WA stack migration (post D2) + Sara VoIP fix (post D1) + Sara web E2E + E2E suite verde
  - Cat 6: help center in-app + backup/restore DB + video tutorial Sara

FASE D (Pre-launch validation, ~8-12h):
  - Smoke test installers cross-OS (macOS arm64+x64, Win10/11)
  - VirusTotal submission
  - E2E suite 10 spec verde su CI
  - FatturaPA sandbox SDI invio reale
  - Refund flow E2E TEST MODE
  - Sentry capture test → email founder
```

### Vincoli mantenuti

- **Zero costi**: tutti i fix usano free tier (CF Pages, GH Releases, Sentry Developer, Stripe 1.5%, Resend 3000/mo, Edge-TTS, Groq free). Solo D2 path A Meta Business API ha costo per-template ($0.05-0.15/msg) ma è per Pro €897 only.
- **Enterprise grade**: zero `any`, zero `--no-verify`, zero workaround. Whatsapp-web.js eliminato.
- **No MVP, no parziale**: shipping solo con 31 P0 verdi.

### Stato audit S246

✅ **6/6 categorie chiuse**.
🔴 **31 P0 enumerati**.
⚙️ **Decisioni D1/D2/D3** in attesa conferma founder.
🚫 **NESSUN commit di codice S246** (audit only, no scope creep).
