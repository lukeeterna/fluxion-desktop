# FLUXION — Pre-Launch Audit Enterprise (S182)

> **Generato**: 2026-04-30 — sessione S182
> **Owner**: CTO autonomous mode (founder paga €220/mese)
> **Standard**: ISO 25010 / OWASP ASVS L1 / Apple HIG / GDPR / D.Lgs 206/2005
> **Direttiva**: NO compromessi feature — "completamente a pieno regime" S181
> **Vincolo**: zero costi (no domini, no SaaS pagati) — Resend free tier, Cloudflare free, Stripe 1.5%
> **Sources**: 4 research subagent paralleli S182 (`.claude/cache/agents/s182-{e2e-coverage,security-owasp-asvs-l1,performance-slo-baseline,legal-compliance}.md`)

---

## SOMMARIO ESECUTIVO

| Categoria | P0 BLOCKING | P1 follow-up | P2 maintenance | ETA P0 cumulativo |
|-----------|-------------|--------------|----------------|--------------------|
| A. Build & Distribution | 6 | 1 | 1 | ~5h |
| B. Functional E2E | 5 | 4 | 0 | ~36h |
| C. Security (OWASP ASVS L1) | 1 | 3 | 4 | ~2h |
| D. Performance | 2 | 5 | 1 | ~6.5h |
| E. Compliance (GDPR + D.Lgs 206) | 4 | 5 | 4 | ~2.5h |
| F. Customer Success | 4 | 3 | 2 | ~5h |
| **TOTALE** | **22** | **21** | **12** | **~57h** |

**Verdetto CTO**: Lancio **NON ammissibile** in stato attuale. 22 P0 BLOCKING. Stima realistica chiusura tutti P0: **~57h** (~7-8 sessioni full-time = sprint S183→S187 + buffer S188).

**Soft-launch ammissibile**: solo dopo Gate 1 (BUILD + FUNCTIONAL E2E P0 verde) + Gate 2 (SECURITY + COMPLIANCE P0 verde), su ≤5 founder-friend con SLA manual support, DISABLE Sara/SDI feature flag se non chiusi.

---

## CATEGORIA A — BUILD & DISTRIBUTION

| ID | Item | Status | Evidenza | Priorità | ETA | Agent | Dipendenze |
|----|------|--------|----------|----------|-----|-------|------------|
| A-1 | macOS Universal Binary (Intel x86_64 + ARM M1/M2/M3) | MISSING | Solo `Fluxion_1.0.0_x64.dmg` (S179, x86_64). PyInstaller voice-agent solo x86_64 — manca arm64. | P0 | 2h | `installer-builder` + `imac-operator` | iMac SSH disponibile |
| A-2 | Windows MSI build & code-signing prep | MISSING | Mai buildato. Mercato IT desktop PMI ~80% Win (IDC/Statista). | P0 | 3h | `installer-builder` + `code-signer` | Win10+ VM o GitHub Actions runner |
| A-3 | Auto-updater Tauri configurato + chiave firmare | MISSING | Tauri 2 supporta updater nativo. Non configurato. Senza updater = no security patching. | P0 | 2h | `update-manager` + `devops-automator` | GitHub Releases endpoint |
| A-4 | Code-signing ad-hoc macOS + entitlements + spctl | PARTIAL | DMG S179 firmato ad-hoc (`spctl rejected` atteso → ctrl+click utente). Doc Gatekeeper esiste (`landing/come-installare.html`). Universal Binary deve essere ri-firmato. | P0 (post A-1) | 1h | `code-signer` | A-1 done |
| A-5 | Windows MSI SmartScreen mitigation (no certificato) | MISSING | Vincolo zero costi → MSI unsigned. Servono doc/landing istruzioni "More info → Run anyway". | P0 (post A-2) | 1h | `code-signer` + `documentation-writer` | A-2 done |
| A-6 | Test installer su HW reale (Mac Intel + M1, Win10 + Win11) | MISSING | Mai testato distribuzione end-to-end. | P0 (post A-1..A-5) | 3h | `build-verifier` (su iMac + VM Win) | A-1..A-5 |
| A-7 | GitHub Releases v1.0.1 con DMG/MSI universal | PARTIAL | v1.0.0 esiste con solo DMG x86_64. Update wrangler.toml `DMG_DOWNLOAD_URL_MACOS` → v1.0.1. | P0 | 0.5h | `release-engineer` | A-1..A-6 |
| A-8 | Removal `*.backup*` files (`src-tauri/src.backup.20260205/`) | OPEN | `voice_pipeline.rs.backup.20260218_135028`, ASVS LOW-1. Distribuiti in DMG bundle se non escluso. | P1 | 0.25h | `devops-automator` | nessuna |

**Note**: tutti i build su iMac via SSH (MacBook = no Rust/build per direttiva CLAUDE.md). Universal Binary richiede Rosetta 2 + targets `aarch64-apple-darwin`+`x86_64-apple-darwin` + lipo per Python sidecar.

---

## CATEGORIA B — FUNCTIONAL E2E (HERO FEATURES)

| ID | Item | Status | Evidenza | Priorità | ETA | Agent | Dipendenze |
|----|------|--------|----------|----------|-----|-------|------------|
| B-1 | Sara live audio HW (microfono fisico → STT → FSM → TTS → speaker) | MISSING | `voice-agent/tests/e2e/test_voip_audio_e2e.py:1-332` testa solo audio sintetico Edge-TTS via HTTP, NON microfono reale. `t1_live_test.py` documentato in `voice-agent-details.md` come 🔴 ancora da fare. | P0 | 8h | `voice-tester` + `voice-engineer` | iMac fisico + microfono |
| B-2 | WhatsApp Cloud API reale (Meta Graph) — invio + delivery + signature webhook | MISSING | `voice-agent/tests/test_whatsapp.py:1-781` interamente mockati. ZERO test invio reale, ZERO test scheduler `reminder_scheduler.py:537`, ZERO test webhook HMAC Meta reale. | P0 | 6h | `whatsapp-automation` + `whatsapp-api-integrator` | account WA Business sandbox + token founder |
| B-3 | Fattura SDI sandbox (FatturaPA XSD validation + invio Aruba/Fattura24 sandbox + esito) | MISSING | `src-tauri/src/commands/fatture.rs:1-1652` NO `#[test]`. `e2e/tests/invoice.spec.ts:1-60` solo UI. Bug numerazione fattura = sanzione AdE D.Lgs 127/2015 art.1 c.6. | P0 | 12h | `fatture-specialist` + `api-tester` | account sandbox Aruba/Fattura24 |
| B-4 | License activation Ed25519 client-side E2E (Stripe TEST → email Resend → app activate → trial) | MISSING | `src-tauri/src/commands/license_ed25519.rs` NO `#[test]`. Solo synthetic backend KV (memory S179). | P0 | 6h | `license-manager` + `e2e-tester` | Stripe TEST keys + chiave pubblica Ed25519 embedded |
| B-5 | Backup/Restore SQLite WAL (integrity + concurrent + corrupted recovery) | MISSING | `src-tauri/src/commands/support.rs:391` NO test. Data loss = class action rischio per medical/dental art.30 GDPR. | P0 | 4h | `database-engineer` + `e2e-tester` | sandbox SQLite con dati seed |
| B-6 | Onboarding Wizard first-launch (verticale → branding → SDI → license → demo) | MISSING | `src/components/setup/SetupWizard.tsx` esiste, `src-tauri/src/commands/setup.rs` 1 unit test interno. ZERO E2E. | P1 | 3h | `onboarding-designer` + `e2e-tester` | nessuna |
| B-7 | Recall Scheduler (APScheduler T-24h/T-2h trigger + idempotency restart + paziente inattivi) | MISSING | `voice-agent/src/reminder_scheduler.py:537` no test funzionale dedicato. | P1 | 3h | `voice-engineer` + `api-tester` | nessuna |
| B-8 | Refund flow regression test repo-resident (Vitest/Wrangler) | PARTIAL | `fluxion-proxy/src/routes/refund.ts:1-403` E2E manuale documentato S179 (PI `pi_3TRs3PIW...`) ma non automatizzato. | P1 | 4h | `api-tester` | nessuna |
| B-9 | 7 Verticali smoke E2E (salone, beauty, palestra, medical, auto, dental, clinic) | PARTIAL | 117 unit test Rust + 9 integration appuntamenti, 0 test dedicati schede verticali. | P1 | 4h | `vertical-customizer` + `e2e-tester` | nessuna |

**Note coverage globale**:
- Python pytest: 78 file (64 root + 11 e2e + 3 integration)
- Rust: 117 `#[test]` in 14 file + 9 integration `integration_appuntamenti.rs`
- Frontend Vitest: **0** (`package.json:test:unit:frontend = "TODO"`)
- WebDriverIO: 10 spec | Playwright: 10 spec | Tests/e2e: 2 spec
- Test live HW microfono: **0**
- Test API esterne reali (WA Cloud / Stripe LIVE / SDI sandbox): **0**

---

## CATEGORIA C — SECURITY (OWASP ASVS L1)

| ID | Item | Status | Evidenza | Priorità | ETA | Agent | Dipendenze |
|----|------|--------|----------|----------|-----|-------|------------|
| C-1 | Admin Bearer auth: constant-time + split secret + rotation | OPEN | `fluxion-proxy/src/routes/admin-resend.ts:22-25` usa `===` non timing-safe. ASVS V2.10.1/V11.1.7. Stesso secret riusato per HMAC GDPR token (`admin-resend.ts:3` "no new secret needed"). Leak singolo = DELETE Resend domains + forge GDPR tokens. | **P0** | 2h | `cloudflare-engineer` + `security-auditor` | wrangler secret rotate |
| C-2 | HIGH-1: `landing/guida-pmi.html:3242,3246-3251` `innerHTML` + inline `onclick` con `sv.name` | OPEN | Future XSS risk se i nomi macro vengono da fetch/CMS/query-string. ASVS V5.3.3. | P1 | 1h | `frontend-developer` | nessuna |
| C-3 | MEDIUM-2: rate limit globale Worker public endpoints (`/rimborso`, `/consent-log`, `/activate-by-email`) | OPEN | `lead-magnet.ts:342-355` ha pattern rate-limit, replicare. KV write quota burn + enumeration. | P1 | 2h | `cloudflare-engineer` | nessuna |
| C-4 | MEDIUM-3: collapse refund enumeration error codes | OPEN | `refund.ts:266-275, 285-294` distinguono 404/409/410 → directory attack su email clienti. | P1 | 1h | `cloudflare-engineer` | nessuna |
| C-5 | MEDIUM-4: Stripe webhook timestamp tolerance ±5min `Math.abs` | OPEN | `stripe-webhook.ts:82-85` accetta eventi futuro. Replay window 10min vs 5min. ASVS V9.2.4. | P2 | 0.25h | `cloudflare-engineer` | nessuna |
| C-6 | MEDIUM-5/6: voice-agent CORS `startswith` + empty origin reflected | OPEN | `voice-agent/main.py:61-68, 64, 81, 90` — `localhost.evil.com` matcha. Defense-in-depth (bind 127.0.0.1) regge ma fragile. | P2 | 1.25h | `voice-engineer` | nessuna |
| C-7 | LOW-2/3: dynamic SQL allow-list assertion | OPEN | `src-tauri/src/infra/repositories/audit_repository.rs:316` + `voice-agent/src/caller_memory.py:201-205` — non injection oggi, fragili a futuri edit. | P2 | 0.75h | `database-engineer` + `voice-engineer` | nessuna |
| C-8 | LOW-1: `*.backup*` files in repo (vedi A-8) | OPEN | duplicato di A-8 — doppio impatto (security + size). | P2 | 0.25h | `devops-automator` | A-8 |

**Verified PASS** (no action): Stripe HMAC verify timing-safe (`stripe-webhook.ts:111-120`), Tauri `Command::new` static binaries, Python `subprocess` list-form no `shell=True`, voice-agent bind 127.0.0.1 + rate limit + LRU cap, Worker CORS allow-list non `*`, License middleware Ed25519 + revocation + HW fingerprint + 24h cache, NLU proxy 200/day rate limit, Lead-magnet honeypot+MX+token 72h+KV compare, NO secrets committed (verificato `tools/VectCutAPI/` placeholder + test fixture isolata).

---

## CATEGORIA D — PERFORMANCE (SLO ENTERPRISE)

| ID | SLO | Target | Stato Stimato | Gap | Priorità | ETA | Bottleneck | Mitigazione |
|----|-----|--------|---------------|-----|----------|-----|------------|-------------|
| D-1 | DB query 1k clienti | <50ms p95 | ~60-150ms | +10-100ms | **P0** | 2h | `clienti.rs:116` no LIMIT/OFFSET, fetch_all 1k records | `get_clienti_paginated(page, page_size)` + index `idx_clienti_deleted_at` (esiste 036_missing_indexes.sql) |
| D-2 | Frontend pagination + virtualization Clienti | n/a | NO virtual list | UI breaks >2k clienti | **P0** | 4h | `src/pages/ClientiPage.tsx` no `react-window` | React Query `useInfiniteQuery` + `react-window` |
| D-3 | Voice pipeline E2E offline (Piper) latency check | <800ms p95 | UNKNOWN | da misurare | **P0** | 0.5h | iMac measurement | `curl http://127.0.0.1:3002/api/voice/process` con Piper forced |
| D-4 | Voice pipeline E2E online (Edge-TTS) | <800ms p95 | ~1330ms | +530ms 🔴 | **P0** (post-launch v1.1) | 12h | Edge-TTS 500ms + LLM serial | Streaming Groq SSE + parallel TTS prefetch |
| D-5 | App startup cold | <3000ms | ~2500-3200ms | borderline | P1 | 4h | SQLitePool init + 37 migrations seq + voice agent always-on | Lazy voice agent spawn (-600ms) |
| D-6 | IPC write `create_cliente` | <200ms p95 | ~150-300ms | edge case | P1 | 4h | Audit log 2nd insert serialized | Batch audit logs queue 100ms flush |
| D-7 | IPC read multi-record (appuntamenti, fatture) | <100ms p95 | borderline | follows D-1 | P1 | included in D-1 | Same pagination pattern | replicare `_paginated` |
| D-8 | UI scroll 60fps stable | 60fps | ~55-58fps | -2~-5fps | P1 | 8h | No virtualization tutti list pages | `react-window` su tutte multi-record pages |
| D-9 | Memory steady-state | <250MB | ~180-220MB | OK | P2 | monitor | OK | sysinfo telemetry post-launch |
| D-10 | Bundle size (frontend gz) | <5MB | ~2.1MB | OK | OK | monitor | OK | Vite manualChunks attivo |

**Score ISO 25010 performance efficiency**: 6.5/10 attuale → 7/10 post P0 → 8.5/10 post v1.1 streaming LLM.

---

## CATEGORIA E — COMPLIANCE (GDPR + D.Lgs 206/2005)

| ID | Item | Status | Evidenza | Priorità | ETA | Agent | Norma | Rischio |
|----|------|--------|----------|----------|-----|-------|-------|---------|
| E-1 | `consent_id` collegato all'email acquirente via `client_reference_id` Stripe Payment Link | OPEN | `landing/checkout-consent.html:205-226` POST `/api/v1/consent-log` riceve consent_id ma redirect Payment Link statico senza `client_reference_id`. `stripe-webhook.ts` non legge né salva `consent_id`. Onere prova art.59 NON soddisfatto. | **P0** | 0.5h | `cloudflare-engineer` + `frontend-developer` | D.Lgs 206/2005 art.59 lett.o + Cass. III 13281/2024 | AGCM PS12847/2025 €35.000 documentato |
| E-2 | Testimonianze landing senza disclaimer "ricostruzioni rappresentative" | OPEN | `landing/index.html:2098-2148` 4 testimonial Marco S./Giulia M./Luca T./Antonio F. — FLUXION ZERO clienti reali al lancio. AGCM PS11969 Treatwell 2022 €200.000. | **P0** | 0.25h | `content-creator` + `legal-compliance-checker` | D.Lgs 206/2005 art.21+23 | sanzione AGCM concreta |
| E-3 | Stripe `sk_live_` configurato in Worker → garanzia 30gg operativa | OPEN | `refund.ts:202-212` ritorna 503 se manca `STRIPE_SECRET_KEY`. Garanzia prominente in landing → 503 al primo tentativo = chargeback + AGCM. | **P0** | 0.2h | `devops-automator` | D.Lgs 206/2005 art.21+59 | chargeback + segnalazione |
| E-4 | T&C generali (`landing/termini.html`) | OPEN | Esiste solo `termini-rimborso.html`. Manca: licenza lifetime nature, limitazione responsabilità AI services, definizione "aggiornamenti inclusi". | **P0** | 1.5h | `legal-compliance-checker` + `content-creator` | D.Lgs 206/2005 art.49 + Direttiva 2011/83/UE | rischio formale |
| E-5 | Retention privacy.html vs codice — nota distintiva | OPEN | `privacy.html:153` 10 anni vs `migrations/018_gdpr_audit_logs.sql:60` retention 2555 giorni (7 anni). | P1 | 0.5h | `legal-compliance-checker` | GDPR art.13 par.2 | incoerenza documentale |
| E-6 | Copy "consenso digitale firmato" → "registrato con timestamp" | OPEN | `landing/index.html:1839` claim impreciso (no firma CAD D.Lgs 82/2005). | P1 | 0.25h | `content-creator` | GDPR art.7 par.1 | valore probatorio debole |
| E-7 | `guida-pmi.html` informativa art.13 GDPR per Sara (responsabilità PMI) | OPEN | `voice-agent/src/booking_state_machine.py:3526` "implicit consent". Va documentato che PMI deve esporre informativa. | P1 | 0.33h | `documentation-writer` | GDPR art.13 + art.4 n.11 | rischio reputazionale |
| E-8 | Privacy.html §2.5-bis art.22 GDPR per Sara (decisioni automatizzate) | OPEN | Sara waitlist + recall = decisioni automatizzate, non menzionato. | P1 | 0.33h | `legal-compliance-checker` | GDPR art.22 | trasparenza obbligatoria |
| E-9 | Lead magnet unsubscribe — 1-click vs mailto | OPEN | `landing/index.html:2398` dichiara "1 click" ma `lead-magnet.ts:240` usa mailto. Garante può sanzionare. | P1 | 0.5h | `cloudflare-engineer` | GDPR art.7 par.3 + D.Lgs 196/2003 art.130 | discrepanza → segnalazione |
| E-10 | PBKDF2 salt random per installazione | OPEN | `src-tauri/src/encryption.rs:25` `DEFAULT_SALT = b"FLUXION_GDPR_SALT_v1"` hardcoded. | P2 | 3h | `backend-architect` + `security-auditor` | GDPR art.32 | rainbow tables cross-installazione |
| E-11 | Listini fornitori tier badge corretto Base & Pro | OPEN | `landing/index.html:1929` "Salone & Officina & Estetica" no tier; feature list Pro (`:2065`) include listini → ambiguo. | P1 | 0.33h | `content-creator` | D.Lgs 206/2005 art.21 | inganno per omissione |
| E-12 | Cookie banner verifica + Tailwind CDN | OPEN | `privacy.html §6` "nessun cookie" — verificare DevTools che Tailwind CDN non setti cookie. | P2 | 0.5h | `frontend-developer` | D.Lgs 196/2003 art.122 | rischio formale |
| E-13 | WhatsApp QR code disclosure ToS rischio ban | PASS | Disclosure landing:2278 corretta. Aggiungere nota in `guida-pmi.html` su numero dedicato consigliato. | P2 | 0.17h | `documentation-writer` | WhatsApp ToS (no norma IT) | rischio operativo cliente |
| E-14 | Privacy.html §3 specificare dominio mittente `@resend.dev` | OPEN | `privacy.html:123` dice "Resend, Inc." senza specificare dominio. Vincolo zero costi confermato S181. | P2 | 0.17h | `legal-compliance-checker` | GDPR art.12 | trasparenza |

**Verified PASS pricing/disclosure**:
- Base €497 / Pro €897 coerenti landing + codice (`license_ed25519.rs:204` Pro `max_verticals: 1`, `:195` Sara solo Pro)
- 7 footnote disclosure (slot €40-€80, NLU 200/giorno, GDPR €20M, garanzia 30gg, SDI, WA, Sara VoIP) tutte ADEGUATE

**Verified PASS 7 feature post-S173**: Sara Waitlist FSM, Recall scheduler `:537`, GDPR audit logs `migrations/018`, AES-256-GCM `encryption.rs:11-14`, Backup `DiagnosticsPanel.tsx`, SDI multi-provider `migrations/029`, Listini storico `migrations/031`.

---

## CATEGORIA F — CUSTOMER SUCCESS

| ID | Item | Status | Evidenza | Priorità | ETA | Agent | Dipendenze |
|----|------|--------|----------|----------|-----|-------|------------|
| F-1 | FAQ pubblica landing con 20+ domande PMI (installazione, attivazione, garanzia, refund, GDPR, Sara, WhatsApp, SDI) | PARTIAL | Landing index ha sezione FAQ minima. Manca pagina dedicata `landing/faq.html` con search + ancore. | **P0** | 2h | `support-responder` + `content-creator` | nessuna |
| F-2 | Support runbook (gianlucadistasi `support-responder` + email template top-20 issue) | MISSING | Nessun playbook formale. Email contatto `fluxion.gestionale@gmail.com`. Senza runbook = SLA non gestibile. | **P0** | 1.5h | `support-responder` | nessuna |
| F-3 | Email transactional sequence (welcome, attivazione, primo accesso, day-3, day-7, day-30) | MISSING | Solo email post-purchase one-shot. Resend free tier 100/giorno OK per primi mesi. | **P0** | 1.5h | `email-marketer` | Resend API |
| F-4 | Self-healing/health monitoring infrastructure (Worker /health, voice-pipeline /health, alert founder) | PARTIAL | Worker `/health` esiste (smoke test S181). Voice agent `/health` esiste. Manca alerting (CF Workers email/Discord/Telegram free). | **P0** | 1h | `infrastructure-maintainer` + `self-healing-monitor` | nessuna |
| F-5 | Empty states + error messages audit (whimsy + actionability) | OPEN | Audit visivo non eseguito. Microcopy generico non revisionato. | P1 | 2h | `whimsy-injector` + `frontend-developer` | nessuna |
| F-6 | Troubleshooting guide (Gatekeeper rejection, SmartScreen, license activation fail, Sara no audio, voice latency, backup fail) | PARTIAL | Solo `landing/come-installare.html` Gatekeeper. Manca `landing/troubleshooting.html` con problemi noti. | P1 | 2h | `documentation-writer` | nessuna |
| F-7 | Onboarding video (3-5min) primo avvio + activation flow | MISSING | Tech debt aperto S180. | P1 | 4h | `video-editor` + `storyboard-designer` + `video-copywriter` | A-1..A-7 done (build pronto) |
| F-8 | Telemetry/analytics (privacy-compliant: anonymous error reporting + activation funnel) | MISSING | No telemetry. Per primi clienti basta CF Worker logs + Resend deliverability. | P2 | 3h | `analytics-reporter` | nessuna |
| F-9 | Pre-launch QA checklist + manual scenario test (5 verticali smoke) | MISSING | Nessuna checklist QA strutturata. | P2 | 2h | `e2e-tester` + `studio-producer` | nessuna |

**Note**: F-1..F-4 sono P0 perché senza FAQ + runbook + email seq + monitoring, primo cliente reale = caos support. Costo zero.

---

## RIEPILOGO P0 BLOCKING (22 ITEM, ~57h)

### Critici (must-have prima Gate 4 launch)

**A. BUILD (5h)**: A-1 Universal Binary (2h) + A-2 Win MSI (3h) + A-3 Auto-updater (2h) + A-4 sign mac (1h) + A-5 SmartScreen doc (1h) + A-6 HW test (3h) + A-7 GitHub Releases (0.5h)

**B. FUNCTIONAL (36h)**: B-1 Sara live audio (8h) + B-2 WhatsApp Cloud (6h) + B-3 SDI sandbox (12h) + B-4 License client (6h) + B-5 Backup/Restore (4h)

**C. SECURITY (2h)**: C-1 admin auth + split secrets (2h)

**D. PERFORMANCE (6.5h)**: D-1 DB pagination (2h) + D-2 frontend virtual (4h) + D-3 voice offline check (0.5h)

**E. COMPLIANCE (2.5h)**: E-1 client_reference_id (0.5h) + E-2 disclaimer testimonial (0.25h) + E-3 Stripe sk_live (0.2h) + E-4 T&C generali (1.5h)

**F. CUSTOMER SUCCESS (5h)**: F-1 FAQ (2h) + F-2 runbook (1.5h) + F-3 email seq (1.5h) + F-4 monitoring (1h)

**TOTALE P0**: ~57h = ~7-8 sessioni full-time

### Alta priorità post-Gate 1 (P1, 21 item)

B-6/B-7/B-8/B-9 (E2E onboarding/recall/refund/verticali — 14h), C-2/C-3/C-4 (security XSS/rate limit/enumeration — 4h), D-5/D-6/D-7/D-8 (performance startup/write/read/scroll — 16h+), E-5/E-6/E-7/E-8/E-9/E-11 (compliance docs+config — 2.5h), F-5/F-6/F-7 (UX empty/troubleshooting/video — 8h).

---

## DIPENDENZE GATE & SEQUENCING

```
Gate 1 (BUILD + FUNCTIONAL E2E):
  A-1 → A-4 (sign post-build)
  A-2 → A-5 (SmartScreen doc post-build)
  A-1 + A-2 → A-3 (auto-updater testato cross-platform)
  A-1..A-3 → A-6 (HW test)
  A-6 → A-7 (release) → B-4 (license E2E richiede DMG/MSI installabile)
  B-1, B-2, B-3, B-5 indipendenti tra loro (paralleli)

Gate 2 (SECURITY + COMPLIANCE):
  C-1 indipendente
  E-1 → E-3 (sk_live serve a refund operativo)
  E-2, E-4 indipendenti

Gate 3 (PERFORMANCE + CUSTOMER SUCCESS):
  D-1 → D-2 (frontend richiede paginated API)
  D-3 indipendente (test only)
  F-1..F-4 indipendenti
  F-7 onboarding video richiede A-1..A-7 done (UI da catturare)

Gate 4 (LAUNCH):
  Stripe TEST → LIVE flip
  A-7 + B-4 + E-3 → primo cliente reale possibile
  Monitoring F-4 attivo PRIMA del primo cliente
```

---

## TECH DEBT EREDITATO PRESERVATO

1. ADMIN_API_SECRET rotazione/rimozione post-S182 (S181)
2. Wrangler v3→v4 upgrade (S181)
3. Acquisto dominio custom RIMANDATO post-10 clienti reali (S181 vincolo permanente)
4. iMac DHCP reservation router consolidare .2 vs .12 fluttua (S179)
5. `purchase:fluxion.gestionale@gmail.com` pre-S174 verifica payment_intent migration (S179)
6. Audit Stripe customer Base/Pro swap pre-S175 (S178 — ZERO clienti reali → bassa priorità)
7. `voice-agent/src/orchestrator.py` voice latency 1330ms vs 800ms — fix v1.1 streaming LLM (D-4 P0 post-launch)

---

## OUTPUT ARTIFACTS S182

- `PRE-LAUNCH-AUDIT.md` (questo file)
- `ROADMAP_S183_S190.md` (sprint plan multi-gate)
- `.claude/cache/agents/s182-e2e-coverage.md`
- `.claude/cache/agents/s182-security-owasp-asvs-l1.md`
- `.claude/cache/agents/s182-performance-slo-baseline.md`
- `.claude/cache/agents/s182-legal-compliance.md`

---

**Verdetto finale CTO**: lancio cold-traffic ammissibile **SOLO dopo Gate 4 (S188+)**. Soft-launch beta-tester ≤5 founder-friend ammissibile dopo Gate 2 (S185) con feature flag SDI/Backup disabilitati se ancora open. Procedo Gate 1 in S183.
