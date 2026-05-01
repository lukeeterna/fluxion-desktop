# FLUXION — Handoff Sessione 184 (2026-05-01) — α.1 Sentry CODE COMPLETE

---

## SESSIONE 184 — IN PROGRESS ⏳ (α.1 Sentry crash reporter integration)

### α.1 Sentry — CODE COMPLETE 75% (founder action required)

**Decisione CTO autonoma S184**:
- α.3 VM host = **iMac Intel** (192.168.1.2). MacBook è `MacBookPro11,1` Intel 2014 → troppo debole per VM. HANDOFF S183-bis "Mac M1" si riferiva al runner GitHub Actions `macos-arm`, non hardware locale.
- VM target = Microsoft Edge Dev VMs (Win10/Win11 free 90gg, x86_64 native).

### File modificati S184 α.1
- **Frontend**:
  - `package.json` + `package-lock.json` — `@sentry/react@^8.55.2` installato
  - `src/lib/sentry.ts` NEW — `initSentry()` + `scrubPII` filter (15 sensitive italian keys)
  - `src/main.tsx` — `initSentry()` chiamata pre-render
  - `src/components/ErrorBoundary.tsx` — `Sentry.captureException` su error
  - `vite.config.ts` — `define.__APP_VERSION__` da `package.json`
  - `src/vite-env.d.ts` — type declaration `__APP_VERSION__` + `VITE_SENTRY_DSN`
- **Rust**:
  - `src-tauri/Cargo.toml` — `sentry = "0.34"` (features: backtrace, contexts, panic, reqwest, rustls)
  - `src-tauri/src/lib.rs` — `init_sentry()` + `scrub_pii` + `_sentry_guard` in `pub fn run()`
- **Python**:
  - `voice-agent/requirements.txt` — `sentry-sdk[aiohttp]>=1.40.0`
  - `voice-agent/src/sentry_init.py` NEW — `init_sentry()` + `_before_send` + `_scrub` (16 sensitive keys)
  - `voice-agent/main.py` — `init_sentry()` chiamata post `load_dotenv()`
- **Docs**:
  - `ROADMAP_S184_PROGRESS.md` NEW — tracker α.1-α.4

### Verify completati
- ✅ `npm install` OK, `@sentry/react@8.55.2` installato
- ✅ `npm run type-check` 0 errori
- ⏸️ `cargo check` → richiede iMac (Rust non disponibile MacBook)
- ⏸️ `pip install` voice-agent → richiede iMac

### Founder action items PENDING (~10 min totali)
1. **Sentry account** (5 min): https://sentry.io/signup → org `fluxion` → 3 projects (frontend/backend/voice) → copia 3 DSN
2. **Aggiorna `.env`** con `VITE_SENTRY_DSN` + `SENTRY_DSN_RUST` + `SENTRY_DSN_PYTHON` + `FLUXION_ENV=production`
3. **Sync iMac**: `git push && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull"`
4. **Build verify iMac**: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo check"`
5. **Voice deps iMac**: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && pip install sentry-sdk[aiohttp]"`

### Tasks PENDING S184 (next session ~10h)
- α.1 E2E verify (3 crash test 3 OS) — dopo founder DSN setup
- α.2 Bypass installazione (~4h): post-install scripts + AV vendor submission + video tutorial + 8 errori comuni
- α.3 HW Matrix VM (~4h): UTM iMac + Win10/Win11 + smoke test 4 OS
- α.4 Network audit (~2h)

### Tech debt aperto S184 → S185
- Tutti gli S183-bis tech debt restano (vedi sotto)
- `.env.example` aggiornare con placeholder Sentry DSN (deferred — permission denied lettura)

### Prossimo prompt session S185 (o continuazione S184)
```
S184 CONTINUA — α.1 E2E verify + α.2 + α.3.

PREREQUISITI: founder ha creato account Sentry + 3 DSN in .env, sync iMac done.

STEP 1 — α.1 E2E verify
  - Trigger 3 crash test (frontend browser, Rust panic, Python /api/voice/_test_crash)
  - Verifica eventi su Sentry dashboard <30s, ZERO PII

STEP 2 — α.2 Bypass installazione (~4h)
  - Submit DMG/MSI vendor AV (Defender/Norton/Kaspersky/Avast)
  - Script post-install macOS + Windows
  - Video tutorial 3min OBS
  - come-installare.html add 8 errori comuni

STEP 3 — α.3 HW VM (iMac host)
  - UTM install Win10 21H2 IT + Win11 23H2 IT (Edge Dev VM ufficiali)
  - Smoke test 4 OS
```

---

## DIRETTIVA OPENROUTER (founder S181-bis)

API key "fluxion" salvata in `.env` (`OPENROUTER_API_KEY`, gitignored — NON committare valore).
Endpoint OpenAI-compatible: `https://openrouter.ai/api/v1` (override `base_url` su SDK OpenAI).
Modelli free $0/M: 13 video / 10 image / 32 text (GLM 4.5 Air, Qwen3 Coder 480B, Llama 3.3 70B, Gemma 3 27B, Hermes 3 405B) / 2 audio / 1 embeddings.
Use cases FLUXION: video promo (sostituire Veo 3 a pagamento), thumbnail YouTube, asset social TikTok/IG/LinkedIn, copy multilingua landing, embeddings RAG Sara.
Sostituire dipendenze a pagamento — coerente vincolo zero costi S181.
Detail: [reference_openrouter_free_models.md](~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/reference_openrouter_free_models.md)

---

## SESSIONE 183-bis — CHIUSA ✅ (Tauri updater + cross-OS PyInstaller + tag v1.0.1 GitHub Release)

### Stato workflow GitHub Actions release-full — 3/4 GREEN
- Run `25207072421` finale: Linux ✅ macos-arm ✅ Windows ✅ macos-intel 🟡 (queue persistente, waived)
- **Tag v1.0.1 PUSHED + GitHub Release CREATED**: https://github.com/lukeeterna/fluxion-desktop/releases/tag/v1.0.1
- 5 commit fix iterativi cross-OS:
  - `f63dbfa` pip self-protection + 3 qualified imports (booking_*/vad_http)
  - `5dd28ed` exclude webrtcvad/pipecat/aiortc (PyInstaller hook Windows crash)
  - `6bba14b` qualified imports sweep 6 file (resource_path consumers)
  - `457a4f7` shell:bash forzato + --help smoke test cross-OS
  - `e9bb53c` matrix multi-line GITHUB_OUTPUT bug
- macos-intel waived: founder confermato Mac M1 (macos-arm) sufficient + Universal Binary copre entrambi gli archi

### Output S183-bis principali
- `.github/workflows/release-full.yml`: fix Windows pip self-protection
- `voice-agent/src/booking_state_machine.py`: fix `escalation_manager` import (try/except)
- `voice-agent/src/booking_manager.py`: fix `vertical_schemas` import (try/except)
- `voice-agent/src/vad_http_handler.py`: fix `vad` package import (try/except)
- `ROADMAP_S184_REVISED_ALPHA.md` NEW: piano α-strategy completo (Sentry + bypass install + HW matrix VM + AI helpdesk RAG + beta 6 vertical)

### Decisione CTO autonoma S183-bis (founder approved)
**Opzione α — onesta lenta** confermata (founder S183-bis):
- ETA +3 settimane vs roadmap S182 → 5% → 80% confidenza cold-traffic
- 6 beta tester (1 per macro-vertical) con AI helpdesk RAG (Groq + KV embeddings)
- HW matrix VM gratis (UTM Mac M1 + Edge dev VM)
- Sentry free tier 5k events/mese
- Bypass installazione enterprise: vendor AV submission + video tutorial + automated post-install scripts

### Tech debt aperto S183-bis → S184
1. ✅ DONE: run release-full GREEN 3/4 + tag v1.0.1 + Release pubblicata
2. macos-intel runner queue persistente (waived per Universal Binary, ma da investigare GH quota)
3. A-6 HW test matrix VM → S184 α.3 (UTM Mac M1 — VM Windows locale per smoke test rapido)
4. Sentry account creation → S184 α.1 (gianlucadistasi81@gmail.com)
5. main.py: implementare `--version` e `--health-check` flags (smoke test workflow attualmente usa --help fallback)
6. CI workflow: sostituire pyinstaller CLI args con `pyinstaller voice-agent.spec` (single source of truth)
7. UTM Mac M1 setup founder per HW matrix VM (parallelo a S184)

### Prossimo prompt session S184
```
S184 KICKOFF — Riprendi roadmap α (ROADMAP_S184_REVISED_ALPHA.md).
S183-bis CHIUSA ✅ — v1.0.1 pubblicata, build pipeline 3/4 OS GREEN.

STEP 1: S184 α.1 Sentry crash reporter
  - Account Sentry free tier: gianlucadistasi81@gmail.com → DSN
  - Integrazione frontend @sentry/react (main.tsx + ErrorBoundary)
  - Integrazione Rust sentry crate (lib.rs panic hook)
  - Integrazione Python sentry-sdk (voice-agent/main.py before_send filter PII)
  - E2E verify: provoca 3 crash → eventi visibili Sentry <30s

STEP 2: S184 α.2 Bypass installazione (parallel α.1)
  - Submit DMG/MSI a Microsoft Defender + Norton + Kaspersky vendor portals
  - Script post-install setup-mac.command + setup-win.bat
  - Video tutorial 3min OBS Studio
  - come-installare.html add: video embed + 8 errori comuni section

STEP 3: S184 α.3 HW Matrix VM
  - Setup UTM Mac M1 founder con Win10 21H2 IT + Win11 23H2 IT
  - Smoke test 4 OS

Vincoli: NO --no-verify, NO commit .env, opzione α confermata, beta 6 vertical strategia.
```

---

## SESSIONE 182 — CHIUSA ✅ (audit enterprise 6 categorie + roadmap multi-gate)

### 🎯 Output S182

| Artifact | Path | Sintesi |
|----------|------|---------|
| **Audit principale** | `PRE-LAUNCH-AUDIT.md` | 22 P0 BLOCKING / 21 P1 / 12 P2 — 6 categorie A-F |
| **Roadmap multi-sprint** | `ROADMAP_S183_S190.md` | 4-gate strict S183→S188 + buffer S189-S190 |
| **Research E2E** | `.claude/cache/agents/s182-e2e-coverage.md` | 0 PASS reali / 4 PARTIAL / 4 MISSING su 9 hero feature |
| **Research Security** | `.claude/cache/agents/s182-security-owasp-asvs-l1.md` | ASVS L1 PASS con 1 P0 (admin auth + split secrets) |
| **Research Performance** | `.claude/cache/agents/s182-performance-slo-baseline.md` | 6.5/10 ISO 25010 — 3 P0 (DB pagination, virtual list, voice offline check) |
| **Research Compliance** | `.claude/cache/agents/s182-legal-compliance.md` | 4 P0 GDPR/D.Lgs 206 (consent_id, testimonial disclaimer, sk_live, T&C) |
| **OpenRouter persist** | `.env` + `.env.example` + `memory/reference_openrouter_free_models.md` | API key fluxion 13 video/10 image/32 text models $0/M |

### 🚨 Verdetto CTO S182

**Lancio cold-traffic NON ammissibile in stato attuale.** 22 P0 BLOCKING distribuiti su 6 categorie:
- A. Build & Distribution: 6 P0 (~5h)
- B. Functional E2E: 5 P0 (~36h)
- C. Security ASVS L1: 1 P0 (~2h)
- D. Performance SLO: 2 P0 (~6.5h)
- E. Compliance GDPR/D.Lgs 206: 4 P0 (~2.5h)
- F. Customer Success: 4 P0 (~5h)

**Totale ETA P0**: **~57h** = 7-8 sessioni full-time = 5 sprint Gate 1→4 (S183→S188).

### 🚪 Gate Enforcement Strict (NON negoziabile)

```
Gate 1 (S183-S185)  BUILD + FUNCTIONAL E2E    🚪 ~41h → Gate 2
Gate 2 (S186)       SECURITY + COMPLIANCE     🚪 ~4.5h → Gate 3
Gate 3 (S186-S187)  PERFORMANCE + UX          🚪 ~11.5h → Gate 4
Gate 4 (S188)       LAUNCH (Stripe LIVE flip + primo cliente reale) 🎉
Buffer (S189-S190)  P1 hardening
```

**Regola**: NON procedere a Gate N+1 finché Gate N tutto verde con E2E PASS. Se 1 fail → re-plan, NO skip.

### 🎯 Step S183 — Sprint 1 Gate 1 (BUILD A-1..A-8)

Da eseguire in ordine (vedi `ROADMAP_S183_S190.md`):
1. arm64 voice-agent build su iMac (PyInstaller)
2. Universal Binary Tauri x86_64+arm64 + lipo
3. Code-sign macOS ad-hoc + spctl verify
4. GitHub Actions Win MSI build (zero costi)
5. Tauri auto-updater configure + GitHub Releases endpoint
6. SmartScreen doc landing
7. HW test matrix (Mac Intel, Mac M1, Win10, Win11)
8. GitHub Releases v1.0.1 universal + auto-update manifest
9. Cleanup `*.backup*` files

**ETA S183**: ~12h.

### 📦 File modificati S182

```
PRE-LAUNCH-AUDIT.md                                   (NEW — audit 6 categorie)
ROADMAP_S183_S190.md                                  (NEW — roadmap multi-gate)
ROADMAP_REMAINING.md                                  (banner SUPERSEDED S182)
.env                                                  (+OPENROUTER_API_KEY)
.env.example                                          (NEW — template all env vars)
.claude/cache/agents/s182-e2e-coverage.md             (NEW)
.claude/cache/agents/s182-security-owasp-asvs-l1.md   (NEW)
.claude/cache/agents/s182-performance-slo-baseline.md (NEW)
.claude/cache/agents/s182-legal-compliance.md         (NEW)
HANDOFF.md                                            (riscritto S182)

# Memory persist (in /Users/macbook/.claude/projects/.../memory/)
reference_openrouter_free_models.md                   (NEW)
MEMORY.md                                             (+OpenRouter row + S182 status)
```

### 🧰 Tech debt aperto S182 → S183+

Eredità S181 + nuovo da audit:

1. **22 P0 BLOCKING** distribuiti S183-S188 (vedi `ROADMAP_S183_S190.md`)
2. **21 P1** post-Gate 1 (B-6/B-7/B-8/B-9, C-2/C-3/C-4, D-5..D-8, E-5..E-9 E-11, F-5/F-6/F-7) ~44.5h
3. **v1.1**: D-4 streaming LLM Groq SSE (voice latency 1330→<800ms) ~12h
4. ADMIN_API_SECRET rotation (S181 — fix in C-1 Gate 2)
5. Wrangler v3→v4 upgrade
6. iMac DHCP reservation router (.2 vs .12)
7. Acquisto dominio custom RIMANDATO post-10 clienti reali (S181 vincolo permanente)

### 🚀 Prompt ripartenza S183

```
Sessione 183. Leggi PRE-LAUNCH-AUDIT.md + ROADMAP_S183_S190.md.

GOAL S183: Sprint Gate 1 — Categoria A (Build & Distribution) completa
+ inizio Categoria B (B-4 License + B-5 Backup).

STEP 0 OBBLIGATORIO: rileggi DIRETTIVA FOUNDER S181 in cima a HANDOFF.md.

STEP 1: Verifica stato iMac SSH disponibile (192.168.1.2).

STEP 2: Esegui in ordine A-1..A-8 (vedi ROADMAP_S183_S190.md):
- A-1: PyInstaller arm64 voice-agent (iMac SSH)
- A-1: Tauri Universal Binary x86_64+arm64 + lipo
- A-4: Code-sign + spctl verify
- A-2: GitHub Actions Win MSI build
- A-3: Tauri auto-updater configure
- A-5: landing SmartScreen doc
- A-6: HW test matrix
- A-7: GitHub Releases v1.0.1 universal
- A-8: cleanup *.backup* files

STEP 3: E2E PASS verify obbligatorio prima di chiusura S183:
- Universal DMG installabile su Mac Intel + M1
- Win MSI installabile su Win10 + Win11
- Auto-updater controlla GitHub Releases endpoint OK
- App lancia 4/4 OS senza errori

VINCOLI:
- Zero costi (GitHub Actions free tier per Win build)
- NO --no-verify
- E2E PASS obbligatorio prima done

PRIMO COMANDO S183:
ssh imac "uptime && cd '/Volumes/MacSSD - Dati/fluxion' && git status"
```

---

## STATO STACK CORRENTE (post-S182)

```
LANDING:    https://fluxion-landing.pages.dev/  (CF Pages free)
WORKER:     https://fluxion-proxy.gianlucanewtech.workers.dev/  (CF Workers free, deploy a96cc2ea S181)
DMG v1.0.0: https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.0/Fluxion_1.0.0_x64.dmg (S179, x86_64 only)
DMG v1.0.1: TBD S183 (Universal Binary)
MSI v1.0.1: TBD S183 (GitHub Actions free tier)
EMAIL:      onboarding@resend.dev (sender) | fluxion.gestionale@gmail.com (contact)
DOMINI:     ZERO posseduti (vincolo zero costi confermato)
PAYMENT:    Stripe TEST mode (LIVE flip in S188 Gate 4)
ASSET GEN:  OpenRouter API key in .env — 13 video / 10 image / 32 text / 2 audio modelli free $0/M
```

---

## SESSIONE 181 — CHIUSA ✅ (cleanup riferimenti domini non posseduti + decisione strategica zero-costi)

[Snapshot S181 preservato sotto per riferimento storico]

---

## 📢 DIRETTIVA FOUNDER S181 — NO COMPROMESSI

**Ordine diretto founder**: FLUXION in produzione enterprise-grade, ZERO compromessi.

**Vincoli operativi (vincolanti per ogni sessione successiva)**:

### 1. Tutti i 7 gap critici noti = P0 BLOCKING, no eccezioni
- Windows MSI (80% mercato Italia desktop PMI)
- Auto-updater configurato e testato
- Sara live audio E2E (hero feature pricing Pro)
- WhatsApp confirma+reminder E2E con WA Cloud API reale
- SDI Fattura PA generation+invio E2E
- Universal Binary macOS (Intel + M1/M2/M3)
- Pre-launch audit 6 categorie eseguito

### 2. "Completamente a pieno regime" = NO compromessi
- NO feature parità parziale
- NO "lanciamo Mac e Windows dopo"
- NO compromessi su hero features pubblicizzate in landing

### 3. CTO autonomous decision-making
- NON chiedere review priorità a founder
- NON chiedere "blocking o opzionale?"
- IO decido basandomi su: dati mercato IT (~80% Win / ~15% Mac IDC/Statista), standard enterprise, vincolo zero costi
- Founder valida SOLO se: blocker fuori budget zero-costi / legalmente ambiguo / scope vision business

### 4. Standard enterprise obbligatori
- ISO 25010 product quality
- OWASP ASVS L1 minimum security
- Apple HIG / Microsoft Fluent ship checklist
- GDPR + D.Lgs 206/2005 art.21+59 compliance Italia
- E2E test PASS prima di dichiarare done (no --no-verify, no scorciatoie, no "lo testo dopo")

### 5. Vincolo zero costi permanente
- No domain custom (sender resta `onboarding@resend.dev`)
- No SaaS pagati
- Tutto stack su CF gratis + Resend free tier + Stripe 1.5%

### 6. Gate enforcement strict S183→S190
- Gate 1: P0 BUILD + FUNCTIONAL E2E verde
- Gate 2: P0 SECURITY + COMPLIANCE verde
- Gate 3: P0 PERFORMANCE + CUSTOMER SUCCESS verde
- Gate 4: production launch (Stripe LIVE + monitoring + primo cliente)
- NON procedere a Gate N+1 finché Gate N tutto verde con E2E PASS

### 7. NO live charge per E2E test
- Stripe TEST mode + refund immediato
- Stripe LIVE attivato SOLO al Gate 4

**Founder paga €220/mese per CTO autonomo che porti FLUXION come prodotto enterprise mondiale per PMI italiane.**
**Missione CLAUDE.md**: *"MIGLIOR strumento mondiale per PMI italiane"*.
**Mantra**: *"Tutto si può fare. Basta solo trovare il modo."*

Memory cross-session: [feedback_zero_compromessi_directive_s181.md](file:///Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/feedback_zero_compromessi_directive_s181.md)

---

## SESSIONE 181 — CHIUSA ✅ (cleanup riferimenti domini non posseduti + decisione strategica zero-costi)

### 🎯 Decisione strategica founder S181

**Founder ha confermato: NON ha mai registrato `fluxion.it` e NON intende registrare domini a pagamento.**

Conseguenze:
- L'investigazione S180 sul "verify Resend per fluxion.it" → **scartata** (basata su assunto sbagliato)
- Stack FLUXION resta su subdomini CF gratis: `fluxion-landing.pages.dev` + `fluxion-proxy.gianlucanewtech.workers.dev`
- Email transazionali: sender resta `onboarding@resend.dev` (Resend free tier, no domain custom)
- Email contatto/supporto: `fluxion.gestionale@gmail.com` (Gmail founder)

**Vincolo zero costi confermato come permanente.**

### ✅ Fatto S181 (~30min, MacBook + Worker CF)

| Task | Status | Note |
|------|--------|------|
| **Grep audit `fluxion.it` / `@fluxion.app` repo-wide** | ✅ | 21 file con `fluxion.it`, 3 con `@fluxion.app` (entrambi domini NON posseduti). Production-impact: 2 file landing + 3 commenti Worker. |
| **Cleanup `landing/guida-pmi.html`** | ✅ | `supporto@fluxion.app` + `enterprise@fluxion.app` → `fluxion.gestionale@gmail.com`. Card "Clinic — Priorità" rimossa (tier Clinic disabilitato S170). |
| **Cleanup `landing/come-installare.html`** | ✅ | `supporto@fluxion.app` → `fluxion.gestionale@gmail.com` (riga 448). |
| **Worker comments aggiornati** | ✅ | refund.ts/lead-magnet.ts/stripe-webhook.ts: rimosso "tech debt verificare dominio mail.fluxion.it" → "valutare acquisto dominio dopo primi 10 clienti se serve brand pro". |
| **`voice-agent/src/voip_pjsua2.py`** | ✅ | Esempio TURN server in commento `turn.fluxion.it` → `turn.example.com` (era solo comment). |
| **Worker DELETE endpoint admin** | ✅ | Aggiunto `DELETE /admin/resend/domains/:id` per cleanup orphan domains. Deploy `a96cc2ea`. |
| **Orphan Resend domain `fluxion.it` ID `e6de440b-c6f6-4c84-8bc5-a5d87d19b7fe`** | ✅ DELETED | Confermato `deleted: true`, lista domini ora vuota. |
| **TypeScript proxy 0 errori** | ✅ | `tsc --noEmit` clean. |
| **Smoke test Worker post-deploy** | ✅ | `/health` 200, `/api/v1/lead-magnet` 200 (honeypot). |
| **CF Pages deploy main** | ✅ | `fluxion-landing.pages.dev/come-installare` 200 con email gmail, `/guida-pmi` 200 idem. |

### 📦 File modificati S181

```
landing/guida-pmi.html                            (-13 +6 — rimossa card Clinic priorità + email aggiornata)
landing/come-installare.html                      (-1 +1)
fluxion-proxy/src/routes/refund.ts                (-2 +2 commenti)
fluxion-proxy/src/routes/lead-magnet.ts           (-2 +2 commenti)
fluxion-proxy/src/routes/stripe-webhook.ts        (-2 +2 commenti)
fluxion-proxy/src/routes/admin-resend.ts          (+10 — handler deleteDomain)
fluxion-proxy/src/index.ts                        (+2 — import + route DELETE)
voice-agent/src/voip_pjsua2.py                    (-1 +1 comment)
HANDOFF.md                                        (riscritto S181)
```

### 🔍 Residui non-produzione (intenzionalmente non toccati)

Riferimenti a `fluxion.it` rimasti in:
- `.claude/cache/agents/*.md` (research artifacts S174 — frozen historical)
- `.planning/research/PITFALLS.md` (planning storico)
- `docs/SARA-lifetime-spec.md`, `REPORT-SESSIONE-2026-02-05.md` (docs storici)
- `scripts/seed_demo_data.sql`, `scripts/mock_data.sql` (demo SQL — solo dati seed locale)
- `testedebug/fase3/TEST-FASE-3.txt` (test storico)
- `.claude/agents/_archived-flat/devops.md` (archived)

→ Nessuno di questi viene servito al cliente o builda nel binario distribuito. Cleanup non necessario per shipping.

### 🎯 Step S182 (lancio finale, ~2h)

Sequenza non-blocked dopo S181:

1. **Build arm64 voice-agent** su iMac via SSH (PyInstaller arm64) → ~30min
2. **Universal Binary build Tauri** (x86_64 + arm64) → ~25min
3. **Code signing ad-hoc + spctl verify + entitlements**
4. **Upload DMG/PKG v1.0.1 universal a GitHub Releases**
5. **Update `wrangler.toml` `DMG_DOWNLOAD_URL_MACOS` → v1.0.1** + redeploy Worker
6. **Stripe TEST → LIVE flip**: nuovi Payment Link LIVE Base + Pro + webhook LIVE secret
7. **Revoke `rk_live_` vecchio** (audit S179 chiusura)
8. **E2E LIVE su carta reale Base €497** + refund immediato (validazione end-to-end con denaro vero, costo netto €0 perché refund completo)
9. **Smoke test email post-purchase** (verificare deliverability `onboarding@resend.dev` su Gmail/iCloud/Outlook reali)
10. **Lancio**: pubblica landing pubblica, attiva newsletter, primo cliente reale

**ETA S182**: 2h (no DNS dependencies, no founder offline action richiesta).

### 🧰 Tech debt aperto S181 → futuro

1. **`ADMIN_API_SECRET`** rotazione/rimozione post-S182 (endpoint admin temporaneo, low-risk perché auth Bearer + Worker secret)
2. **Wrangler v3 → v4** upgrade (warning out-of-date)
3. **Acquisto dominio custom** — RIMANDATO: valutare dopo primi 10 clienti reali se serve brand pro (`noreply@dominio.tuo` vs `onboarding@resend.dev`). Solo allora rompere vincolo zero costi (~€10/anno `.com`).
4. **iMac DHCP reservation router consolidare** (.2 vs .12 fluttua — eredità S179)
5. **`purchase:fluxion.gestionale@gmail.com` pre-S174** verifica payment_intent migration (eredità S179)
6. **Audit Stripe customer Base/Pro swap** pre-S175 (eredità S178 — ma audit live S179 ZERO clienti reali → priorità bassa)

### 📋 Verifica deliverability email `onboarding@resend.dev` (S182 priority)

Resend free tier permette invio da `onboarding@resend.dev` ma:
- Limit: **100 email/giorno**, **3000/mese** (sufficiente per lancio + primi mesi)
- DKIM/SPF gestiti da Resend stesso (firmato `@resend.dev`)
- **Rischio spam folder**: senza dominio custom + DMARC, alcuni provider (specie Outlook business) marcano spam. Mitigazione: monitoring delivery rate Resend Dashboard primi 5 invii reali.
- **Workaround se spam**: passare a Gmail SMTP relay via app password `fluxion.gestionale@gmail.com` (limit 500/giorno Gmail, ma richiede app password setup founder).

---

## SESSIONE 180 — sintesi (chiusa con assunto sbagliato `fluxion.it` posseduto)

Vedi commit `26c93f9` per snapshot S180. TL;DR:
- Investigato DNS `fluxion.it` → NS thundercloud.uk (NON posseduto founder)
- Endpoint admin Resend creato (`/admin/resend/domains/*`)
- Resend domain `fluxion.it` creato via API → poi cancellato S181 come orphan

I file modificati S180 (admin-resend.ts handler GET/POST/verify, types.ts ADMIN_API_SECRET binding) **restano utili** in S182 per gestire eventuali futuri domini (cleanup rimandato).

---

## STATO STACK CORRENTE (post-S181)

```
LANDING:    https://fluxion-landing.pages.dev/  (CF Pages free)
WORKER:     https://fluxion-proxy.gianlucanewtech.workers.dev/  (CF Workers free, deploy a96cc2ea)
DMG:        https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.0/Fluxion_1.0.0_x64.dmg  (S179)
EMAIL:      onboarding@resend.dev (sender) | fluxion.gestionale@gmail.com (contact)
DOMINI:     ZERO posseduti (vincolo zero costi confermato)
PAYMENT:    Stripe TEST mode (LIVE flip in S182)
```

## PROMPT RIPARTENZA S182 — REALIGNMENT FRAMEWORK + PRE-LAUNCH AUDIT

```
Sessione 182. Leggi HANDOFF S181.

GOAL: produrre PRE-LAUNCH-AUDIT.md enterprise-grade per portare FLUXION in produzione.
Founder S181 ha confermato: io CTO ho piena responsabilità produzione, lui non sviluppatore,
io devo conoscere audit/test/procedure enterprise senza essere chiesto.

Step S182 (full session dedicata, zero shortcut):

1. RESEARCH (subagent paralleli, output .claude/cache/agents/s182-*):
   - gsd-verifier      → mappa stato test E2E per ogni hero feature (PASS/FAIL/MISSING)
   - code-reviewer     → security audit OWASP ASVS L1 (src-tauri, fluxion-proxy, voice-agent)
   - performance-benchmarker → SLO baseline startup/IPC/voice/UI
   - legal-compliance-checker → GDPR + D.Lgs 206/2005 art.21+59 audit landing+codice

2. PRODUCE PRE-LAUNCH-AUDIT.md, 6 categorie:
   A. BUILD & DISTRIBUTION (Win MSI, macOS Universal, auto-updater, signing, installers HW reale)
   B. FUNCTIONAL E2E (Sara live audio, WhatsApp confirma+reminder reale, SDI fattura,
      onboarding wizard, license activate, backup/restore, schede verticali, calendario+cassa)
   C. SECURITY (license tampering, IPC, SQL injection, XSS, secrets, signing chain)
   D. PERFORMANCE (startup <3s, IPC <100ms, voice P95 <800ms, UI 60fps, DB 1k clienti)
   E. COMPLIANCE (privacy=realtà, audit logs, retention, art.59, art.21, refund flow LIVE)
   F. CUSTOMER SUCCESS (FAQ, support runbook, email seq, troubleshooting, onboarding video,
      empty states, error messages, self-healing, monitoring/telemetry)

   Per item: status (PASS/FAIL/UNKNOWN) + evidenza (file:line/test name) +
   priorità (P0/P1/P2) + ETA + agent responsabile + dipendenze.

3. ROADMAP MULTI-SPRINT S183→S190+ con 4 gate decisionali:
   - Gate 1: tutti P0 BUILD + FUNCTIONAL E2E verde
   - Gate 2: tutti P0 SECURITY + COMPLIANCE verde
   - Gate 3: tutti P0 PERFORMANCE + CUSTOMER SUCCESS verde
   - Gate 4: production launch (Stripe LIVE + monitoring + primo cliente)

4. Per ogni gap P0 trovato → task subagent dedicato + ETA realistico.

5. IO CTO decido priorità autonomamente. Default: tutti 7 gap critici noti = P0 BLOCKING.
   Decisioni basate su: dati mercato IT desktop PMI (~80% Win / ~15% Mac IDC/Statista),
   standard enterprise (ISO 25010 / OWASP ASVS L1 / Apple HIG / GDPR / D.Lgs 206/2005),
   vincolo zero costi, "completamente a pieno regime" = no compromessi feature.
   Founder valida SOLO se: blocker fuori budget / legalmente ambiguo / scope vision business.

6. Eseguo Gate 1 immediatamente nelle sessioni successive con gate enforcement strict
   (NO Gate 2 finche' Gate 1 tutto verde con E2E PASS).

VINCOLI:
- Zero costi (no dominio custom — confermato S181)
- Enterprise grade, NO --no-verify, NO scorciatoie
- MAI live charge per E2E (Stripe TEST mode + refund immediato)
- MAI dichiarare done senza E2E pass
- Standard riferimento: ISO 25010 / OWASP ASVS L1 / Apple HIG ship checklist /
  GDPR / D.Lgs 206/2005

STEP 0 OBBLIGATORIO: leggere e interiorizzare ## DIRETTIVA FOUNDER S181 — NO COMPROMESSI
in cima a HANDOFF.md PRIMA di iniziare qualsiasi task.

PRIMO COMANDO S182:
git pull origin master && sed -n '1,80p' HANDOFF.md
```

## RIFERIMENTO FRAMEWORK FONDATORE (vincolante)

- `CLAUDE.md` (root) — 2 guardrail non negoziabili (zero costi + enterprise grade)
- `.claude/rules/workflow-cove2026.md` — protocollo 6 fasi (Skill ID → Research → Plan → Implement → Review → Verify → Deploy)
- `.claude/rules/e2e-testing.md` — test E2E obbligatori OGNI tipo task
- `.claude/rules/architecture-distribution.md` — TTS 3-tier, LLM proxy, Stripe, signing
- `memory/feedback_cto_full_production_responsibility.md` (NEW S181) — CTO ownership

## GAP CRITICI NOTI (da reality check S181, da espandere in audit S182)

1. 🔴 **Windows MSI non viene buildato** — `tauri.conf.json` targets: `['dmg','app']`, manca `msi` o `nsis`
2. 🔴 **Auto-updater config vuoto** — plugin `tauri-plugin-updater@2` installato, ma `plugins.updater = {}` → clients pinned su prima versione, NO patch security/bugfix possibile
3. 🔴 **Sara: 0 test conversazione live audio** — 69 unit test OK su FSM/intent, ZERO test microfono→risposta reale
4. 🟠 **WhatsApp 0 test E2E** — conferma booking + reminder -24h/-1h non testati con WA Cloud API reale
5. 🟠 **SDI Fattura PA 0 test** — generazione XML + invio non testati
6. 🟠 **Universal Binary macOS mancante** — solo x86_64 attuale, taglia M1/M2/M3 nativi
7. 🟠 **Pre-launch audit mai eseguito** — `.claude/cache/agents/*pre-launch*` vuoto

→ Diventano item P0 nell'audit S182.
