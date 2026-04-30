# S182 — E2E Coverage Audit (Pre-Launch)

**Data**: 2026-04-30
**Scope**: 9 hero feature pubblicizzate in `https://fluxion-landing.pages.dev/`
**Standard**: ISO 25010 functional suitability + reliability
**Metodologia**: solo evidenze file:line, zero supposizioni
**CTO verdict**: 4 hero feature P0 BLOCKING lancio (live audio Sara, WhatsApp Cloud reale, SDI sandbox, license activation E2E)

---

## Hero Feature 1 — Voice Agent "Sara" 24/7 (Pro flagship)

- **Status**: PARTIAL
- **Test esistenti**:
  - `voice-agent/tests/test_booking_state_machine.py` (47k righe, FSM 23 stati unit) — `voice-agent/tests/test_booking_state_machine.py:1-1500+`
  - `voice-agent/tests/test_disambiguation.py:1-22k` (matching fonetico Levenshtein) + `test_disambiguation_integration.py`
  - `voice-agent/tests/test_pipeline_e2e.py:461-595` (`TestFullPipelineE2E` — pipeline 4-layer SIMULATA via `process_query()` interno, NON tocca HTTP `/api/voice/process`)
  - `voice-agent/tests/test_voice_agent_complete.py` (665 righe)
  - `voice-agent/tests/test_s158_live_full.py:1-285` (test live SU PIPELINE running su `127.0.0.1:3002`, multi-verticale, **input testuale**, no audio)
  - `voice-agent/tests/test_s158_multivertical.py:1-153`
  - `voice-agent/tests/test_p0_blockers.py:1-397` (buffer/pausa/combo/"il solito" — unit con mock)
  - `voice-agent/tests/e2e/test_voip_audio_e2e.py:1-332` — **UNICO test audio reale**: genera WAV con Edge-TTS Diego e POSTA `audio_hex` a `/api/voice/process` (richiede pipeline running)
  - `voice-agent/tests/test_waitlist_trigger.py:1-149` (gated `HAS_FULL_DEPS`, richiede iMac venv)
  - 64 test pytest totali in `voice-agent/tests/` + 11 in `voice-agent/tests/e2e/` + 3 in `voice-agent/tests/integration/`
- **Gap CRITICO**:
  1. **ZERO test live audio HW** (microfono fisico → STT Whisper.cpp → NLU → FSM → TTS → speaker fisico). `test_voip_audio_e2e.py` usa Edge-TTS sintetico in input → bypassa il "vero" path microfono+VAD.
  2. **Test live `t1_live_test.py`** referenziato in `voice-agent-details.md` come 🔴 "ancora da fare".
  3. **Pipeline running prerequisite** non automatizzato (i test richiedono `nohup python main.py` su iMac avviato manualmente).
  4. **5 scenari live** voluti dal product (Gino vs Gigio, Soprannome VIP, Chiusura Graceful, Flusso Perfetto, Waitlist) → solo Waitlist ha test (`test_waitlist_trigger.py`).
- **Priorità**: **P0** (Sara è l'unica feature differenziante Pro €897, se non funziona live → lancio ritirato).
- **ETA**: 8h (4h script `t1_live_audio.py` con 5 WAV reali registrati + harness `subprocess.Popen(arecord/sox)` per validare loopback speaker; 2h fixture pipeline auto-start; 2h CI gate `pytest -m live_audio`).

---

## Hero Feature 2 — WhatsApp Conferma + Reminder appuntamenti

- **Status**: PARTIAL (solo unit test con mock)
- **Test esistenti**:
  - `voice-agent/tests/test_whatsapp.py:1-781` — 27 test classi (config, message, rate limiter, templates conferma/reminder24h/reminder2h/cancellazione/benvenuto/compleanno) **interamente mockati** (riga 15: `from unittest.mock import AsyncMock, MagicMock, patch`; riga 503: `whatsapp_client.send_message(...)` → mock pipeline)
  - `voice-agent/tests/test_whatsapp_callback.py:1-391` (callback inbound mockato)
  - `voice-agent/tests/integration/test_whatsapp.py:1-2309` (file presente, 76 righe)
  - `scripts/tests/test-whatsapp-webhook.sh` (script bash one-shot)
  - Source: `voice-agent/src/whatsapp.py` + `voice-agent/src/whatsapp_callback.py` + `voice-agent/src/reminder_scheduler.py`
- **Gap CRITICO**:
  1. **ZERO test invio reale WhatsApp Cloud API** (Meta Graph) — nessun `WHATSAPP_ACCESS_TOKEN` exercise, nessun smoke send a numero test sandbox.
  2. **ZERO test scheduler reminder reale** — `reminder_scheduler.py` (recall T-24h / T-2h appuntamento) non ha test integration; solo `test_phase_g_business_intelligence.py` lo grep-matcha.
  3. **ZERO test E2E delivery** — non si verifica che messaggio arrivi davvero, non si testa stato `delivered/read`.
  4. **Webhook inbound** `whatsapp_callback.py` testato con mock → produzione potrebbe fallire su signature HMAC reale Meta.
- **Priorità**: **P0** (no-show appointment è il caso d'uso principale "Comunicazione" → senza reminder reale il valore percepito crolla).
- **ETA**: 6h (3h account WhatsApp Business sandbox Meta + token; 1h test reale `pytest -m whatsapp_live` con send a numero test founder; 1h scheduler integration; 1h webhook signature validation).

---

## Hero Feature 3 — Fattura Elettronica SDI (FatturaPA)

- **Status**: **MISSING** (zero test E2E)
- **Test esistenti**:
  - **NESSUNO** in voice-agent, src-tauri/tests, e2e/tests (`grep -rn fattura\|sdi` → 0 match nei test, solo file .pyc cache).
  - `e2e/tests/invoice.spec.ts:1-60` (WebDriverIO) — test SOLO di navigazione/UI ("apre dialog nuova fattura", "ha selettore cliente") → NON genera XML, NON invia a SDI, NON valida FatturaPA schema.
  - Source: `src-tauri/src/commands/fatture.rs:1-1652` (1652 righe — `cliente_codice_sdi`, `xml_filename`, `xml_content`, `sdi_provider`, `fattura24_api_key`) + `src/components/impostazioni/SdiProviderSettings.tsx` + migrations `026/029_sdi_*.sql`.
  - 0 `#[test]` / `#[tokio::test]` in `fatture.rs` (verificato grep).
- **Gap CRITICO**:
  1. **ZERO unit test XML generation** (FatturaPA 1.2.2 schema XSD validation).
  2. **ZERO test sandbox SDI** (provider Aruba/Fattura24 hanno endpoint test gratuiti).
  3. **ZERO test progressivo/numerazione** — bug numerazione fattura = sanzione AdE.
  4. **ZERO E2E** "crea fattura → genera XML → invia provider → ricevi `sdi_id_trasmissione` → conferma `sdi_esito=consegnata`".
  5. **Compliance D.Lgs 127/2015 art.1 c.6** — fattura SDI obbligatoria B2B → bug = legale per cliente.
- **Priorità**: **P0** (compliance fiscale italiana; impossibile vendere "fattura elettronica" senza E2E).
- **ETA**: 12h (4h schema XSD validator pytest; 3h sandbox account Aruba/Fattura24; 3h test E2E invio sandbox+ricezione esito; 2h test numerazione progressiva con concurrency).

---

## Hero Feature 4 — Calendario + Cassa + Clienti + Schede verticali (7)

- **Status**: PARTIAL (best coverage del progetto)
- **Test esistenti**:
  - **Calendario/Appuntamenti**: `src-tauri/tests/integration_appuntamenti.rs:1-?` — 9 test integration (`test_workflow_happy_path_completo`:23, `test_workflow_override_warnings`:104, `test_workflow_rifiuto_operatore`:174, `test_workflow_cancellazione`:214, `test_hard_block_data_passata`:259, `test_modifica_appuntamento`:300, `test_persistenza_e_reload`:365, `test_soft_delete`:410, `test_find_by_operatore_and_date_range`:448).
  - **Rust unit tests**: `grep -c "#\[(test|tokio::test)\]" src-tauri/src/` → 117 test totali in 14 file (commands/setup.rs:1, services/appuntamento_service.rs:6, encryption.rs:6, commands/settings.rs:1, domain/appuntamento_aggregate.rs:30, commands/rag.rs:7, domain/errors.rs:6, infra/repositories/audit_repository.rs:6, commands/analytics.rs:6, domain/audit.rs:12, infra/repositories/appuntamento_repo.rs:4, services/validation_service.rs:12, services/festivita_service.rs:10, services/audit_service.rs:10).
  - **WebDriverIO E2E**: `e2e/tests/01-smoke.spec.ts`, `02-navigation.spec.ts`, `03-clienti-crud.spec.ts`, `04-servizi-validation.spec.ts`, `05-appuntamenti-conflict.spec.ts`, `booking.spec.ts`, `cashier.spec.ts`, `crm.spec.ts`.
  - **Playwright**: `e2e-tests/tests/` (10 spec): `accessibility.spec.ts`, `clienti.spec.ts`, `dashboard.spec.ts`, `impostazioni.spec.ts`, `mock-debug.spec.ts`, `screenshots.spec.ts`, `smoke.spec.ts`, `user-journeys.spec.ts`, `visual.spec.ts`.
  - **Cassa command** ha `backup\|export\|import` references in `commands/cassa.rs`.
- **Gap CRITICO**:
  1. **0 test per 7 verticali** (salone, beauty, palestra, medical, auto, dental, clinic) lato schede cliente — `test_multi_verticale.py` esiste solo voice (29k righe NLU per verticale, NON UI/persistenza scheda).
  2. **Cassa**: nessun test scontrino + chiusura giornaliera + Z-report (compliance commerciale art.2 D.M. 21/12/1992 NON validata).
  3. **Listini storico variazioni** (claim landing): zero test.
  4. **Status reale Playwright suite** non noto (tests/e2e/voice-agent.test.ts:1-40 controlla `__TAURI__` → richiede build app + bridge running).
- **Priorità**: **P1** (la base ha 117 unit test Rust + 9 integration + ~20 E2E spec → coverage ragionevole; gap su 7 verticali può essere mitigato con smoke verticale singolo).
- **ETA**: 4h (2h E2E Playwright smoke per ogni verticale carica scheda + crea cliente vertical-specific; 2h test cassa Z-report + scontrino numerazione).

---

## Hero Feature 5 — Onboarding Wizard zero-friction

- **Status**: **MISSING**
- **Test esistenti**:
  - `src/components/setup/SetupWizard.tsx` (esiste).
  - `src-tauri/src/commands/setup.rs` (esiste, ha 1 unit test interno).
  - **0 test E2E wizard** (grep `onboarding|setup.*wizard|SetupWizard` su `e2e/tests/`, `tests/e2e/`, `src-tauri/tests/` → 0 match).
  - `e2e-tests/tests/impostazioni.spec.ts` esiste ma copre Impostazioni post-setup, NON il wizard primo avvio.
- **Gap CRITICO**:
  1. **ZERO test "first-launch experience"** (verticale selection → branding → SDI provider → license trial → demo dati). Primo impatto del cliente = unico shot di conversion.
  2. **ZERO test idempotenza setup** (rerun wizard non duplica record).
  3. **ZERO test offline first-launch** (claim landing: "Calendario/clienti/cassa funzionano OFFLINE" — non validato in onboarding).
- **Priorità**: **P1** (impact alto su churn 30gg ma non blocca compliance/lancio; mitigabile con manual QA pre-lancio).
- **ETA**: 3h (script Playwright headless multi-verticale dry-run + reset DB tra run + assertion DB schema post-wizard).

---

## Hero Feature 6 — License Activation Ed25519 via email

- **Status**: PARTIAL (backend deploy + synthetic E2E pass, manca client-side)
- **Test esistenti**:
  - **Backend**: `fluxion-proxy/src/routes/activate-by-email.ts:1-134` (validazione license attiva, blocca se `purchase.refunded === true`). E2E synthetic (memory S179): `webhook → KV write purchase 10y + session 30d → email_sent=true`.
  - **Client Rust**: `src-tauri/src/commands/license_ed25519.rs` (esiste) + `src-tauri/src/commands/license.rs`. **0 `#[test]` / `#[tokio::test]`** (verificato grep).
  - 0 test E2E end-to-end "Stripe payment → email arrivata → cliente apre app → inserisce email → verifica Ed25519 → trial attivato".
- **Gap CRITICO**:
  1. **ZERO test client-side Ed25519 verify** — se chiave pubblica embedded sbagliata o scaduta → tutti gli acquisti bricked.
  2. **ZERO test offline license cache** (cliente offline 7gg deve usare cache; non testato).
  3. **ZERO test refund → license blacklist propagation** (memory S174 backend lo fa, ma client non testato che blocchi).
  4. **ZERO test phone-home** (`fluxion-proxy/src/routes/phone-home.ts` esiste, no test client).
  5. **ZERO test multi-device** (Pro lifetime su 1 device? 2 device? rules non testate).
- **Priorità**: **P0** (chiave del business model; bug = revenue loss diretto).
- **ETA**: 6h (2h Rust unit test Ed25519 round-trip; 2h E2E completo Stripe TEST → mail Resend → app install → activate; 2h offline cache + refund propagation).

---

## Hero Feature 7 — Backup/Restore SQLite

- **Status**: **MISSING**
- **Test esistenti**:
  - Source: `src-tauri/src/commands/support.rs:391` (`pub async fn backup_database`), `support.rs:698` (chiamata interna), `src-tauri/src/lib.rs:595` (registrazione `commands::backup_database`).
  - Frontend: `src/components/impostazioni/DiagnosticsPanel.tsx` (UI esiste).
  - **0 test E2E** (`grep backup` su `e2e/tests/`, `tests/e2e/`, `src-tauri/tests/` → 0 match).
  - **0 unit test** in `support.rs`.
- **Gap CRITICO**:
  1. **ZERO test backup integrity** (SHA256 check post-backup).
  2. **ZERO test restore** (worst case: cliente rompe DB, restore deve funzionare → mai testato).
  3. **ZERO test WAL checkpoint** (backup di DB live SQLite WAL → rischio corruzione).
  4. **ZERO test backup automatico schedulato** (claim "Backup" implicito daily, non testato).
- **Priorità**: **P0** (data loss = class action rischio per PMI con 5 anni dati clienti; recall scheda paziente medical/dental è obbligo art.30 GDPR).
- **ETA**: 4h (1h test backup → modifica DB → restore → assert dati identici via hash; 1h test WAL+SHM checkpoint; 1h test concurrent backup mentre app scrive; 1h test restore offline + corrupted DB).

---

## Hero Feature 8 — Recall Scheduler (`reminder_scheduler.py`)

- **Status**: **MISSING** (logica esiste, test 0)
- **Test esistenti**:
  - Source: `voice-agent/src/reminder_scheduler.py:627` (memory S173 conferma "Recall scheduler reale, recall T-24h/T-2h").
  - Solo `voice-agent/tests/test_phase_g_business_intelligence.py` ha grep-match testuale, no test funzionale dedicato.
  - **0 test E2E APScheduler trigger reale**.
- **Gap CRITICO**:
  1. **ZERO test che timer effettivamente scatta** (APScheduler con cron expression non testato).
  2. **ZERO test recall idempotency** (server riavviato → no duplicate reminder).
  3. **ZERO test integration WhatsApp send + recall queue**.
  4. **ZERO test "non viene da 2 mesi"** (claim landing card 9): recall paziente inattivi non testato.
- **Priorità**: **P1** (impact business diretto ma non blocca P0 lancio; comunque feature di vendita prominente).
- **ETA**: 3h (1h fake-clock APScheduler + assert send call; 1h idempotency restart; 1h recall paziente inattivi query SQL).

---

## Hero Feature 9 — Garanzia 30gg refund LIVE (Stripe API)

- **Status**: PARTIAL (synthetic E2E pass, no test repo-resident)
- **Test esistenti**:
  - **Source**: `fluxion-proxy/src/routes/refund.ts:1-403` (validation, idempotency `refund:{email}`, age <30gg, Stripe Refund API + Idempotency-Key, audit log, Resend email, blacklist).
  - **E2E manuale documentato (memory S179)**: PI `pi_3TRs3PIW4bHDTsaH0SAWHrkq` → refund `re_3TRs3PIW4bHDTsaH0We94shN` €497 SUCCEEDED + KV `refunded=true` + email Resend OK.
  - **0 test automatizzati** in `fluxion-proxy/` (cercato `*.test.ts|*.spec.ts` → solo node_modules).
- **Gap CRITICO**:
  1. **ZERO test repo-resident** (test E2E è solo manuale-via-curl in chat, non riproducibile in CI).
  2. **ZERO test "refund window expired"** (giorno 31).
  3. **ZERO test "double refund"** (idempotency Stripe).
  4. **ZERO test "purchase NOT FOUND"** (email senza acquisto).
  5. **ZERO test fee EU non rimborsate** (memory S174 BLOCKER #2 noto: €7.71 Base / €13.71 Pro merchant cost).
  6. Prossimo S182 secondo memory: "E2E carta reale con refund immediato" — sarà manual, non automated.
- **Priorità**: **P1** (legalmente bound a D.Lgs 206/2005 + landing claim "30gg soddisfatti o rimborsati"; manual E2E S179 fa da copertura, ma serve regression).
- **ETA**: 4h (Vitest/Wrangler unittest mock Stripe + KV; 3 scenari refund: valid/expired/duplicate; CI gate prima di deploy Worker).

---

## Coverage Globale

| Metrica | Valore |
|---------|--------|
| **Test totali Python** (voice-agent) | 64 root + 11 e2e + 3 integration = **78 file pytest** |
| **Test totali Rust** | 117 unit `#[test]` in 14 file + 9 integration `integration_appuntamenti.rs` |
| **Test totali frontend (vitest)** | **0** (`package.json:test:unit:frontend` = "TODO: Install vitest and configure") |
| **E2E suite** | WebDriverIO 10 spec (`e2e/tests/`) + Playwright 10 spec (`e2e-tests/tests/`) + 2 spec (`tests/e2e/`) |
| **Test live HW (microfono fisico)** | **0** (gap critico Sara) |
| **Test live audio sintetico (Edge-TTS WAV via HTTP)** | 27 invocazioni in `test_voip_audio_e2e.py` |
| **Test live API esterne (WhatsApp Cloud / Stripe LIVE / SDI)** | **0** (tutti mock) |
| **Test compliance fiscale (FatturaPA XSD)** | **0** |
| **Test backup/restore** | **0** |
| **Test license Ed25519 client** | **0** |
| **Pass rate noto** | UNKNOWN (nessun CI pipeline running, ultimo `pytest tests/ -v` non documentato S179-S181) |

### Gap P0 BLOCKING lancio (4)

1. **Sara live audio HW** — 8h
2. **WhatsApp Cloud API reale** — 6h
3. **Fattura SDI sandbox** — 12h
4. **Backup/restore + License Ed25519 client** — 4h + 6h = 10h

**TOTALE P0**: **36h** di lavoro test-engineering pre-lancio.

### Gap P1 (3)

1. **Onboarding wizard** — 3h
2. **Recall scheduler** — 3h
3. **Refund regression Vitest** — 4h
4. **7 verticali smoke** — 4h

**TOTALE P1**: **14h** post-lancio settimana 1.

### CTO verdict

**Lancio "completamente a pieno regime" come da MEMORY S181 = NO COMPROMESSI.**

Sui 9 hero feature pubblicizzati:
- 1 PASS reale: NESSUNO
- 4 PARTIAL accettabili con manual QA: Sara, WhatsApp, License, Refund
- 4 MISSING: SDI, Onboarding, Backup, Recall (di cui 2 P0)
- 0 risk-free per release-to-production

**Raccomandazione CTO**: bloccare lancio S182 fino a chiusura P0 (36h = ~5 giorni full-time). Alternativa: lancio "soft" beta-tester max 5 founder-friend con SLA manual support 24/7 + disclaimer feature-flag su SDI/Backup. **Non vendere a freddo a sconosciuti finché P0 non passa CI.**

---

**File**: `.claude/cache/agents/s182-e2e-coverage.md`
**Generato**: 2026-04-30, sessione S182, audit pre-launch
