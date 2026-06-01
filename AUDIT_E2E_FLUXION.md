# AUDIT E2E FLUXION — Reality-Check Codice vs Realtà

> **Sessione**: S324 audit-only · **Branch**: `audit/e2e-reality-check-s324` · **Data**: 2026-06-01
> **Metodo**: trust-but-verify, ogni claim ancorato a `file:riga` reale via grep/read. NESSUN fix.
> **Fonte di verità**: il codice. PLAN.md/HANDOFF/MEMORY trattati come inaffidabili e cross-checkati.

## Workspace confermato

- **Path attivo**: `/Volumes/MontereyT7/FLUXION` (git root verificato, branch master di partenza).
- `/Volumes/MacSSD - Dati/FLUXION` e `/Volumes/MacSSD - Dati/fluxion` **NON esistono** su questa macchina (MacBook) — quel path è il mount dell'**iMac**, citato da CLAUDE.md per i comandi SSH. Nessuna ambiguità: sviluppo locale = MontereyT7.
- Nota: `git stash` contiene 2 WIP (`WIP-keep-staged-only`, `WIP on master 78d5095`) — **non toccati** in questa sessione.

---

## 1. PRODOTTO & VERTICALI

**Cos'è FLUXION oggi nel codice** — [VERIFICATO]
Gestionale desktop per PMI italiane. `src-tauri/tauri.conf.json:3` → `"productName": "Fluxion"`, identifier `com.fluxion.desktop`, category `Business`. Routing reale in `src/App.tsx:124-136`: `/clienti`, `/calendario`, `/fatture`, `/cassa`, `/voice`, `/fornitori`, `/analytics`.

**Tassonomia verticali** — [VERIFICATO] memoria "8 macro × 50 micro" **corretta**.
- `src/types/setup.ts:66-123` → `MACRO_CATEGORIE` = 8 esatte: `medico, beauty, hair, auto, wellness, professionale, pet, formazione`.
- `src/types/setup.ts:129-196` → `MICRO_CATEGORIE` = 50 (medico=10, beauty=7, hair=6, auto=7, wellness=6, professionale=5, pet=4, formazione=5).

**Schede cliente verticali** — [PARZIALE]
- `src/types/scheda-cliente.ts` → 9 schemi Zod entità (Odontoiatrica:28, Fisioterapia:82, Estetica:128, Parrucchiere:182, Fitness:246, Veicoli:294, Carrozzeria:338, Medica:410, **Pet:480**).
- `src/components/schede-cliente/` → 8 componenti `.tsx` reali: Carrozzeria, Estetica, Fisioterapia, Fitness, Medica, Odontoiatrica, Parrucchiere, Veicoli (+ Dynamic/Tabs/Wrapper).
- **BUG NOTO CONFERMATO**: `SchedaPet.tsx` NON esiste. `SchedaPetSchema` definito (riga 480) ma il default switch `SchedaClienteDynamic.tsx:278` cade su `<SchedaBase>` vuota → i 4 micro pet (toelettatura, veterinario, pensione_animali, dog_sitter) rendono scheda vuota.
- `professionale` (5 micro) e `formazione` (5 micro) hanno `hasScheda:false` (setup.ts:177-195) — nessun componente, by-design.

**Verticali realmente implementati (UI dedicata)**: 8 schede su 5 macro (medico, beauty, hair, auto, wellness). Pet, professionale, formazione = solo tassonomia.

---

## 2. STACK & VERSIONI — [VERIFICATO]

| Componente | Reale (file:riga) | Note |
|---|---|---|
| Tauri | `2` — `src-tauri/Cargo.toml:17` + tauri-build `2`:14 | Tauri 2.x confermato |
| React | `^19.1.0` — `package.json:81` | |
| TypeScript | `~5.8.3` — `package.json:118` | |
| Vite | `^5.4.11` — `package.json:119` | |
| **SQLite driver** | **`sqlx = "0.7"`** — `Cargo.toml:31` | **NON rusqlite** (memoria errata: nessun rusqlite nel repo) |
| Ed25519 | `ed25519-dalek = "2"` — `Cargo.toml:36` | |
| Keychain | `keyring = "3.6"` | macOS Keychain + Win Credential Mgr |
| Migrazioni | `src-tauri/migrations/` = **41 file .sql** (001→041) + `seeds/` | |
| WhatsApp | `whatsapp-web.js ^1.34.4` — `package.json:88` | NON Business API ufficiale |

App version: `tauri.conf.json:3` = `1.0.1`; `package.json` name = `tauri-app` v1.0.1 (non rinominato "fluxion").

---

## 3. FEATURES CORE

| Feature | Stato | Evidenza |
|---|---|---|
| Anagrafica clienti | [VERIFICATO] | `commands/clienti.rs` (get:189, create:319, update:404, delete:427) + PII encrypt 263-300 + tab `migrations/001_init.sql:11` + `hooks/use-clienti.ts:33-104` invoke reali |
| Calendario appuntamenti | [VERIFICATO] | `commands/appuntamenti.rs` (get:398, create:564...) + **conflict detection reale** `check_conflicts()` 331 + `migrations/001_init.sql:122` + state machine `004_*.sql` |
| Servizi | [VERIFICATO] | `commands/servizi.rs` (68/86/95/135/176) + `001_init.sql:56` + `use-servizi.ts:31-90` |
| Dashboard/KPI | [VERIFICATO] | `commands/dashboard.rs` query SQL reali aggregate (COUNT appuntamenti:49, SUM fatture:97, top servizi:117), NO mock. `Dashboard.tsx:148-165` invoke reali |
| **Fatture / FatturaPA** | [VERIFICATO con caveat] | vedi sotto |

**FatturaPA — XML reale, NON placeholder.** `commands/fatture.rs:~1383-1790` `generate_fattura_xml()`:
- Namespace ufficiale v1.2 (riga 1390), XSD `fatturapa.gov.it` (1391).
- Header completo: `ProgressivoInvio` zero-pad 5 cifre (1407-1411), `CodiceDestinatario` (1429), PEC fallback su `0000000`.
- `CedentePrestatore`/`CessionarioCommittente` con dati fiscali; `DettaglioLinee`, `DatiRiepilogo`, regime forfettario RF19 → Natura N2.2 + RiferimentoNormativo; escape XML (`escape_xml` ~1790).
- Schema reale: `migrations/007_fatturazione_elettronica.sql` (tab fatture:54, sdi_esito RC/NS/MC/AT/DT, lifecycle bozza→pagata:105).

**Trasmissione SDI** — [PARZIALE] via **intermediari a pagamento**, NON connessione diretta Agenzia Entrate. Factory `fatture.rs:~410` con 3 provider: Fattura24 (`api.fattura24.com`:272), Aruba (`ews.aruba.it/ArubaSMSSender/...`:~310), OpenAPI.com (~380). **⚠ endpoint Aruba sospetto**: path `ArubaSMSSender` è un gateway SMS, probabilmente endpoint FE errato → provider Aruba potrebbe non funzionare. Fattura24/OpenAPI corretti. Richiede API key configurata + abbonamento esterno (rompe guardrail "zero costi" lato cliente).

---

## 4. WHATSAPP & VOICE AGENT

### WhatsApp
| Funzione | Stato | Evidenza |
|---|---|---|
| Daemon | [VERIFICATO] | `scripts/whatsapp-service.cjs:534-538` Client + LocalAuth, QR:547, session persist. Gestito da `commands/whatsapp.rs` |
| Promemoria appuntamenti -24h/-1h | [VERIFICATO] | `voice-agent/src/reminder_scheduler.py:106-141` APScheduler query SQLite + idempotenza JSON, auto-start `main.py:1277-1317` |
| Conferme prenotazione | [VERIFICATO] | `main.py:746-812` endpoint + `whatsapp.rs:629` + template `src/lib/whatsapp-1tap.ts:86-93` |
| Auguri compleanno | [PARZIALE] | query `loyalty.rs:1139` + card `Dashboard.tsx:225` + template:119-123 ma **nessun auto-sender schedulato** → solo alert + 1-tap manuale |
| Richiami (recall/follow-up) | [STUB] | solo template `whatsapp-1tap.ts:128-131`, nessun comando/scheduler/trigger |
| Recensioni | [DA FARE] | **zero codice** in src-tauri/src, src, scripts, voice-agent (0 match "recension" in path eseguibili) |

Scheduler reale solo per promemoria appuntamenti. Compleanni/richiami/recensioni non automatizzati.

### Voice Agent "Sara"
| Aspetto | Stato | Evidenza |
|---|---|---|
| HTTP server | [VERIFICATO] | `voice-agent/main.py:348` porta 3002, route `_setup_routes:382-429` (/health, /api/voice/{greet,process,say,reset,status}, voip/status...) |
| **FSM stati** | [VERIFICATO — 14 stati, NON 23] | `booking_state_machine.py:98-116` `BookingState(Enum)` = 14 (IDLE, WAITING_NAME/SERVICE/DATE/TIME, CONFIRMING, COMPLETED, CANCELLED, WAITING_SURNAME, CONFIRMING_PHONE, PROPOSE_REGISTRATION, REGISTERING_SURNAME/PHONE, DISAMBIGUATING_NAME). Header riga 10 dice "8 states". **Memoria + voice-agent-details.md "23 stati" = ERRATO** |
| RAG layers | [VERIFICATO — 5 layer] | `orchestrator.py` L0-L4 (special/intent/FSM/FAQ/Groq). `main.py:1143` stampa "4-layer" (nomenclatura incoerente) |
| STT/TTS/VAD | [VERIFICATO] | STT Groq Whisper large-v3 + whisper.cpp fallback (`stt.py:67-110`); TTS Edge-TTS + Piper + `say` (`tts.py:425-441`); VAD Silero ONNX + webrtcvad |
| **SIP/VoIP telefonico** | [PARZIALE — credential-gated] | `voip_pjsua2.py` 1366 righe reali (SIPConfig:162-190 default `sip.vivavox.it`, VoIPManager start/hangup/onIncomingCall). `.so`/`.dylib` presenti in `lib/pjsua2/`. MA attivo solo se env `VOIP_SIP_USER` set (`main.py:1321-1336`). Numero 0972536918 + cred EHIWEB **non nel repo** (.env non committato su iMac) |
| Test | [VERIFICATO] | `voice-agent/tests/` = 69 file; e2e=8 (test_voip_audio_e2e, test_sara_massive), integration=3; `test_booking_state_machine.py` 1258 righe |

**Verdetto telefono**: path HTTP-testo funziona end-to-end (coperto da test). Chiamata telefonica reale = codice SIP completo ma attivazione runtime dipende da `.env` deployato su iMac, non testabile dal MacBook.

---

## 5. PAGAMENTO & LICENZA

**Cloudflare Worker** `fluxion-proxy/src/routes/stripe-webhook.ts` — [VERIFICATO codice completo]
- Verifica firma Stripe via WebCrypto: `constructEventAsync(...createSubtleCryptoProvider())` riga 410-416, 400 su fail:420.
- Tier detection `detectTier():38-51` legge `metadata.tier ?? metadata.plan` PRIMO (43), fallback amount map (49700→base, 89700→pro).
- Firma Ed25519: `signEd25519(...)`:516 → `lib/ed25519-sign.ts:79-91` `crypto.subtle.sign('Ed25519',...)`, payload `LicensePayloadV1` canonicalizzato (160-169).
- D1 dedup: `INSERT OR IGNORE INTO webhook_events`:300, replay path 465-501.
- Resend sender: `licenze@fluxion-app.com` (`stripe-webhook.ts:186`, fix S310).

**Verifica client Rust** `src-tauri/src/commands/license_ed25519.rs` — [VERIFICATO]
- `verify_license_signature_with_key():318-354` ed25519-dalek `VerifyingKey::from_bytes` + `verify()`:350, ritorna `Ok(false)` su tamper (no panic).
- Tamper detection coperto da unit test (Pro→Enterprise, bit-flip sig, wrong key).

**⚠ MISMATCH SCHEMA (gap E2E reale)**: il Worker firma `LicensePayloadV1` (kid, license_id, customer_email, product, session_id, issued_at) ma il Rust verifica `FluxionLicense` (hardware_fingerprint, licensee_name, enabled_verticals — struct:47-80). **Sono due formati paralleli**: nessun interop Worker→Rust verificato live. `PLAN.md:311` ammette: *"Wizard activate GUI live — unico anello cliente mai eseguito E2E"*.

**I "7 test"** — [PARZIALE]
- `fluxion-proxy/tests/stripe-webhook.test.ts` = **8 `it()`** (non 7): happy path:71, invalid sig→400:139, missing email:165, unknown tier:200, **FSAF-05 replay dedup:234**, replay+email NULL:300, **roundtrip+tamper:380**, /verify endpoint:424.
- `license_ed25519.rs:929-1060` = 5 `#[test]` Rust (roundtrip, tamper license, tamper sig, wrong key, canonical JSON).
- **FDQ-01**: `fluxion-proxy/tests/scripts/smoke_fdq01.py` esiste (synthetic checkout→Worker→success→replay), richiede credenziali live, mai in CI.
- `scripts/license-delivery/e2e_test.py` = **STALE LemonSqueezy** (webhook `/webhook/lemonsqueezy`, tier `clinic` inesistente) — non l'architettura Stripe attuale.
- **Nessun artifact di pass automatico nel repo** (no test-results JSON, no CI run). Evidenza solo narrativa umana: `PLAN.md:304` "smoke €1 Base S317 + Pro S319 webhook 200 + Resend delivered + refund". **Memoria "0/7 VERIFIED" è obsoleta**: i test esistono (codice completo) ma non c'è prova di esecuzione automatica; gli smoke €1 sono manuali documentati.

---

## 6. BUILD & DISTRIBUZIONE

| Aspetto | Stato | Evidenza |
|---|---|---|
| Target bundle | [VERIFICATO] | `tauri.conf.json:47` `["dmg","app","nsis"]`. WiX block:52 ma MSI non in targets |
| CI/CD | [PARZIALE] | 9 workflow in `.github/workflows/`. `ci.yml` = solo type-check+lint+pytest (NO build Tauri). `release.yml`/`release-full.yml` = build cross-platform reale via tauri-action ma **updater signing commentato** (`release-full.yml:299-300`, secret password mismatch) |
| Code signing | [STUB — ad-hoc] | `tauri.conf.json:44` `signingIdentity: null`, nessun cert Apple Dev. `entitlements.plist` ad-hoc (app-sandbox:false, disable-library-validation:true → incompatibile notarization). **Nessuna notarizzazione, nessun APPLE_CERTIFICATE in CI** |
| Auto-updater | [CONFIGURATO MA DISABILITATO] | `tauri.conf.json:63-70` active:true endpoint GitHub releases, MA `createUpdaterArtifacts:false`:32 + signing CI commentato → nessun .sig prodotto |
| Artifact buildati | [PARZIALE] | `releases/v1.0.0/Fluxion_1.0.0_x64.dmg` + `.pkg` (solo **Intel**). **Nessun ARM .dmg, nessun .exe/.msi Windows** |

---

## 7. STATO CREDENZIALI — COSA BLOCCA IL PRIMO FATTURATO

- **Stripe Payment Links LIVE** già nel landing: `landing/checkout-consent.html:125` €497 + `:131` €897 (`buy.stripe.com` produzione). Cliente raggiungerebbe checkout reale.
- **HARD BLOCKER #1 — secret Worker non settati**: `wrangler.toml:26-39` + `lib/types.ts:8-36` richiedono `STRIPE_WEBHOOK_SECRET`, `STRIPE_SECRET_KEY`, `RESEND_API_KEY`, `ED25519_PRIVATE_KEY` via `wrangler secret put`. Se assenti → cliente paga ma nessuna licenza/email. (Memoria S316 dice settati su prod — **da verificare con `wrangler secret list`, non confermabile dal solo codice**.)
- **HARD BLOCKER #2 — 3 route Resend ancora rotte**: `lead-magnet.ts:276`, `diagnostic-report.ts:186`, `refund.ts:187` usano ancora `onboarding@resend.dev` (solo verso account-owner). **FBUG-RESEND risolto SOLO sul path licenze principale, non ovunque** (memoria "risolto S310" parziale).
- **SOFT BLOCKER #3 — nessun build ARM macOS**: download consegna `Fluxion_1.0.0_x64.dmg` (`wrangler.toml:57`, `sender.ts:110`) → Apple Silicon riceve Intel/Rosetta.
- **SOFT BLOCKER #4 — nessun installer Windows** buildato/pubblicato.
- **COSMETICO #5 — auto-updater disabilitato**: clienti v1.0.0 non riceveranno update automatici.

---

## DOVE LA REALTÀ DIVERGE DA QUANTO SI CREDE (lista secca)

1. **SQLite = sqlx 0.7, NON rusqlite** (memoria errata; nessun rusqlite nel repo). `Cargo.toml:31`.
2. **FSM Sara = 14 stati, NON 23** (memoria + `.claude/rules/voice-agent-details.md` errati). `booking_state_machine.py:98-116`.
3. **RAG = 5 layer nel codice ma `main.py:1143` stampa "4-layer"** — incoerenza nomenclatura.
4. **SchedaPet.tsx mancante** → 4 micro pet rendono scheda vuota. Schema esiste, UI no.
5. **"7 test 0/7 VERIFIED" obsoleto**: 8 vitest + 5 rust + smoke FDQ-01 esistono (codice completo), ma **nessuna prova di pass automatico nel repo**; solo smoke €1 manuali narrativi (S317/S319).
6. **FBUG-RESEND risolto solo parzialmente**: path licenze OK, ma lead-magnet/diagnostic-report/refund ancora `onboarding@resend.dev` rotti.
7. **Mismatch schema licenza Worker↔Rust**: `LicensePayloadV1` ≠ `FluxionLicense`. Interop cliente reale **mai testato E2E** (`PLAN.md:311`).
8. **PLAN.md cita LemonSqueezy** (`e2e_test.py` stale) — architettura reale è **Stripe + CF Worker**.
9. **"Pronto a vendere" smentito da build**: solo 1 DMG Intel, **niente ARM, niente Windows** nonostante pricing multi-OS.
10. **Auto-updater configurato ma disabilitato** (signing commentato, `createUpdaterArtifacts:false`).
11. **Endpoint SDI Aruba sospetto** (`ArubaSMSSender` = gateway SMS, non FE) → provider Aruba probabilmente non funzionante.
12. **SDI via intermediari a pagamento** (Fattura24/Aruba/OpenAPI) → richiede abbonamento esterno, attrito col guardrail "zero costi".
13. **VoIP telefonico credential-gated**: codice pjsua2 completo ma `.env` (VOIP_SIP_USER, EHIWEB) non nel repo → non verificabile da MacBook.

---

## NOTA METODOLOGICA

Audit code-only via 5 agenti read-only paralleli (grep/read), ogni claim ancorato a file:riga.
Non eseguito a runtime: type-check, `cargo check`, `cargo test`, vitest, server Sara (port 3002 attivo su iMac ma non interrogato in questo audit). I claim runtime ("funziona end-to-end") restano da validare con esecuzione reale prima di qualsiasi dichiarazione "production ready".
