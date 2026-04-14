# FLUXION — GDPR & Italian Privacy Law Audit
**Date:** 2026-04-14  
**Auditor:** legal-compliance-checker agent  
**Scope:** Full codebase — desktop app, voice agent, CF Worker, landing page  
**Standard:** EU GDPR (Reg. 2016/679) + D.Lgs. 196/2003 (Codice Privacy IT) as amended by D.Lgs. 101/2018

---

## Executive Summary

FLUXION's compliance posture is **strong for a desktop PMI product**. The architecture (local SQLite, no cloud storage of client PII) is inherently privacy-friendly. The codebase contains substantial GDPR infrastructure — audit logging, retention policies, anonymization, field-level encryption, consent tracking, and CSV export. However, **four concrete gaps** require attention before the product can be marketed as GDPR-compliant without qualification:

1. No Privacy Policy page exists at `landing/privacy`  
2. No cookie consent banner on the landing page (Cloudflare Analytics in use)  
3. Right to Erasure is soft-delete only — no hard-delete / full anonymization of PII fields in `clienti` table  
4. Voice agent: temp WAV files created with `delete=False` — cleanup in `finally` block but no explicit GDPR notice to callers

---

## 1. PII Inventory

### Sensitivity Classification

| Field | Table | Sensitivity | Art. 9 Special Category? |
|-------|-------|-------------|--------------------------|
| `nome`, `cognome` | `clienti` | HIGH | No |
| `email` | `clienti` | HIGH | No |
| `telefono` | `clienti` | HIGH | No |
| `data_nascita` | `clienti` | HIGH | No |
| `indirizzo`, `cap`, `citta`, `provincia` | `clienti` | MEDIUM | No |
| `codice_fiscale` | `clienti` | HIGH | No (fiscal, not health) |
| `partita_iva` | `clienti` | MEDIUM | No |
| `pec`, `codice_sdi` | `clienti` | MEDIUM | No |
| `note`, `tags`, `fonte` | `clienti` | MEDIUM | No |
| `consenso_marketing`, `consenso_whatsapp`, `data_consenso` | `clienti` | HIGH | No (consent records) |
| `media_consenso_*` | `clienti` (alt cols) | HIGH | No |
| `soprannome` | `clienti` | LOW | No |
| `contenuto` (message body) | `messaggi_whatsapp` | HIGH | No |
| `telefono` | `messaggi_whatsapp` | HIGH | No |
| `telefono`, `trascrizione` | `chiamate_voice` | HIGH | No |
| `user_input`, `response` | `voice_session_turns` | HIGH | No |
| `entities_json` | `voice_session_turns` | HIGH | No |
| `phone_number`, `cliente_nome` | `voice_sessions` | HIGH | No |
| **HEALTH DATA — Art. 9** | | | |
| `diagnosi_medica`, `diagnosi_fisioterapica`, `zone_trattate`, `valutazione_iniziale` | `schede_fisioterapia` | **CRITICAL** | **YES** |
| `gruppo_sanguigno`, `peso_kg`, `pressione_*`, `allergie_*`, `patologie_croniche`, `farmaci_attuali` | `schede_mediche` | **CRITICAL** | **YES** |
| `odontogramma`, `otturazioni`, `estrazioni`, `devitalizzazioni` | `schede_odontoiatriche` | **CRITICAL** | **YES** |
| `fototipo`, `tipo_pelle`, `allergie_*`, `peso_attuale`, `gravidanza`, `allattamento`, `patologie_attive` | `schede_estetica` | **CRITICAL** | **YES** |
| `nota_cliniche`, `note_private` | `schede_mediche` | **CRITICAL** | **YES** |
| `vaccinazioni`, `patologie`, `farmaci` | `schede_pet` | LOW (animal) | No |
| **VEHICLE DATA** | | | |
| `targa`, `telaio` (VIN) | `schede_veicoli` | MEDIUM | No |
| `numero_sinistro`, `compagnia` | `schede_carrozzeria` | MEDIUM | No |
| **FINANCIAL** | | | |
| Fattura fields (tax data, amounts) | `fatture` | HIGH | No |
| `denominazione`, `partita_iva`, `iban`, `bic` | `impostazioni_fatturazione` | HIGH | No |
| **OPERATOR DATA** | | | |
| `nome`, `cognome`, `email`, `telefono` | `operatori` | HIGH | No |
| **STAFF COMMISSIONI** | `operatori_commissioni` | MEDIUM | No |

**Total PII tables: 15+ tables containing personal data**  
**Art. 9 special-category data: 4 tables** (`schede_mediche`, `schede_fisioterapia`, `schede_odontoiatriche`, `schede_estetica`)

**STATUS: COMPLIANT** — all fields documented above. Art. 9 data is present and requires explicit consent (basis: `art. 9(2)(h)` — medical/health professional purpose).

---

## 2. Data Retention

### Schema-level policies (migration 018)

| Category | Retention | Source |
|----------|-----------|--------|
| Personal data (`clienti`) | 7 years (2555 days) | Art. 2940 c.c. prescrizione |
| Consent records | 5 years after revocation | GDPR Art. 7(1) |
| Booking history | 3 years | Reasonable |
| Voice sessions | 1 year | Reasonable |
| Audit log | 7 years | Legal obligation |
| Financial/fatture | 10 years | D.P.R. 600/73 Art. 22 |

Configuration is stored in `gdpr_settings` table with `auto_purge_enabled = true` and `auto_anonymize_enabled = true`. The `anonymize_after_days = 90` setting applies to inactive records.

### Code implementation

`audit_service.rs::run_gdpr_anonymization()` marks records in `voice_session_turns` and `voice_audit_log` as anonymized via `mark_anonymized()`. `cleanup_expired_logs()` hard-deletes records past their `retention_until` date.

The view `v_voice_pending_anonymization` identifies records older than 30 days without anonymization.

**GAP:** These Tauri commands (`run_gdpr_anonymization`, `cleanup_expired_audit_logs`) are registered in `lib.rs` but there is no evidence of a **scheduled/automatic invocation** — no cron job, no app-startup trigger, no scheduler call found in the codebase. Retention policies exist on paper but depend on the operator manually triggering them from the UI.

**STATUS: PARTIAL**  
- Policy defined: YES  
- Code implemented: YES (audit tables)  
- Automatic execution: NOT VERIFIED — no scheduler call found  
- `clienti` table personal data retention: policy set in `gdpr_settings` but no purge function found targeting the `clienti` table itself

---

## 3. Right to Erasure (Art. 17 GDPR)

### What exists

- `delete_cliente` command: sets `deleted_at = datetime('now')` — this is a **soft delete only**
- Soft-deleted records remain in the database with all PII intact, just excluded from queries
- Audit trail is correctly logged on delete

### What is missing

- No **hard delete** function that removes PII fields from `clienti` after soft-delete
- No **anonymization** function that overwrites `nome`, `cognome`, `telefono`, `email`, `codice_fiscale` etc. with pseudonymous tokens for soft-deleted records
- No cascade anonymization for linked tables: `messaggi_whatsapp`, `chiamate_voice`, `voice_session_turns`, `schede_mediche`, `schede_fisioterapia`, etc.
- No `gdpr_erase_cliente` command exposed to frontend
- `gdpr_requests` table exists (migration 018) for tracking erasure requests, but no fulfillment handler found

**LEGAL ANALYSIS:** Under Art. 17 GDPR, a data subject (the end-customer of the PMI) can request erasure. The PMI owner (data controller) must comply within 30 days. Currently, the operator can "delete" a client from the UI but the PII remains in SQLite indefinitely. This is non-compliant with Art. 17 if a legitimate erasure request is made.

**Exception:** Art. 17(3)(b) allows retention for legal claims (fatture/booking for 7-10 years). However, even where retention is lawful, the fields that are *not* required for the legal basis (e.g., `nota`, `tags`, `data_nascita`, `indirizzo`) should be nullified.

**STATUS: NON-COMPLIANT**  
Soft delete only. No true erasure or field-level anonymization on request. The `gdpr_requests` table infrastructure exists but has no fulfillment backend.

---

## 4. Data Export / Right to Portability (Art. 20 GDPR)

### What exists

- `export_clienti_csv()`: exports `nome`, `cognome`, `email`, `telefono`, `data_nascita`, `citta`, `note`, consent flags, `created_at` — machine-readable CSV
- `export_appuntamenti_csv()`: exports booking history with client names, service, operator, duration, price, status, notes
- `export_support_bundle()`: ZIP bundle for diagnostics (contains DB copy — full PII export)

### Gaps

- No export for `schede_mediche`, `schede_fisioterapia`, `schede_odontoiatriche` — health data not portable
- No export for `messaggi_whatsapp` (communication history)
- No export for `voice_session_turns` / `chiamate_voice` (call transcripts)
- CSV export does not include `codice_fiscale`, `indirizzo`, `partita_iva` — incomplete portability

**STATUS: PARTIAL**  
Core customer data (clienti + appuntamenti) is exportable in machine-readable CSV. Sector-specific health records and communication history are not exportable. For verticals handling Art. 9 data (medical, dental, physio), this is a gap.

---

## 5. Consent Collection

### App-level

- `ClienteForm.tsx`: checkboxes for `consenso_marketing` and `consenso_whatsapp` with explicit label text. Consent state stored with `data_consenso` timestamp. **Compliant.**
- `MediaConsentModal.tsx`: explicit GDPR consent modal for clinical photos (Art. 9), with separate booleans for `consenso_interno`, `consenso_social`, `consenso_clinico`. **Compliant.**
- Consent fields stored in `clienti` table: `consenso_marketing`, `consenso_whatsapp`, `data_consenso`, `media_consenso_interno`, `media_consenso_social`, `media_consenso_clinico`, `media_consenso_data`. **Compliant.**

### First-launch consent

- `SetupWizard.tsx`: searched for privacy/GDPR acceptance — **not found**. No evidence of a first-use consent screen requiring the business owner to accept the privacy policy or acknowledge they are the data controller.

**STATUS: PARTIAL**  
Granular per-client consent collection is well-implemented. However, there is no first-launch consent for the app operator (the PMI owner) acknowledging their role as data controller and accepting terms of use. This is required under Art. 13 GDPR (information to data subjects) — the PMI owner must be informed before they start entering customer data.

---

## 6. Encryption at Rest

### What exists

`encryption.rs` implements **AES-256-GCM** field-level encryption with PBKDF2 key derivation (100,000 iterations, SHA-256). Sensitive fields identified in `SENSITIVE_FIELDS` constant:

- `nome`, `cognome`, `telefono`, `email`, `codice_fiscale`, `partita_iva`, `indirizzo`, `cap`, `citta`, `pec`, `data_nascita`

Tauri commands registered: `gdpr_init_encryption`, `gdpr_is_ready`, `gdpr_encrypt`, `gdpr_decrypt`.

### Critical gap

The encryption module **exists in code** but there is **no evidence it is actually called** when writing clienti to the database. A grep for `encrypt_field` across all Rust source files returned **zero matches in commands/clienti.rs or any repository layer**. The `SENSITIVE_FIELDS` list and encryption commands are implemented but appear to be unused infrastructure — PII is stored as plaintext in SQLite.

Similarly, `gdpr_init_encryption` is registered as a Tauri command but no call to it was found in the frontend setup flow or app initialization.

**gdpr_settings** table has `encryption_at_rest = 'true'` as a default value, but this is a configuration flag — it does not enforce encryption automatically.

**STATUS: NON-COMPLIANT**  
Encryption infrastructure exists but is not activated in the data write path. PII is stored as plaintext in SQLite. The `gdpr_settings` flag claims encryption is enabled but the code does not enforce it. This is the most significant technical compliance gap.

---

## 7. Voice Data — Audio Recordings

### What happens to audio

1. **Live call audio:** Captured by pjsua2/SIP layer in memory buffers
2. **STT processing:** Written to `tempfile.NamedTemporaryFile(suffix=".wav", delete=False)` for processing by whisper.cpp or faster-whisper
3. **Cleanup:** `finally: Path(audio_path).unlink()` — temp file is deleted after transcription (both STT engines)
4. **Transcription stored:** `voice_session_turns.user_input` stores the text transcript (not audio)
5. **Retention policy:** Voice sessions: 1 year, turns anonymized after 30 days (schema)

### Positive findings

- No permanent audio file storage found — audio is processed transiently
- Temp files are cleaned up in `finally` blocks
- Transcripts stored separately from audio
- Retention policy defined for voice session data

### Gaps

1. **No caller notification:** The Sara greeting ("Benvenuto!") does not include any statement that the call is processed by AI or that conversation text is stored. Under Art. 13 GDPR and the Italian Garante guidelines on telephone recordings, the caller must be informed at the start of the call.

   Required disclosure: "Questa chiamata è gestita da un assistente automatico. La conversazione verrà elaborata per gestire la prenotazione e conservata per [X] giorni."

2. **`delete=False` risk:** `NamedTemporaryFile(delete=False)` means the OS will not auto-delete the file if the process crashes before reaching the `finally` block. A crash during STT leaves a WAV file of the caller's voice on disk indefinitely.

3. **Sentiment analysis stored:** `chiamate_voice.sentiment` and `voice_session_turns.sentiment` store inferred emotional state — this is derived personal data. Retention policy applies.

**STATUS: PARTIAL**  
Audio is not permanently stored. However, the absence of a caller disclosure statement is a concrete violation of Italian privacy law for automated phone systems (Provvedimento Garante 2017 + Art. 13 GDPR).

---

## 8. Cloud Processing — CF Worker NLU

### What data transits the CF Worker

- **NLU requests:** The `body` of the request is passed directly from the app to Groq/Cerebras. This body contains the LLM conversation messages including user speech transcripts.
- **License validation:** Email address stored in Cloudflare KV (`purchase:{email}` key)
- **Phone-home:** License key (email), tier, trial status — no client PII

### PII in NLU requests

The `nluProxy` function passes `body` (the full request from the app) directly to the LLM provider: `const requestBody = { ...body, model: provider.model }`. No PII stripping or sanitization is performed. The `body` originates from the voice agent's conversation context in `orchestrator.py`.

If the conversation context includes client names or phone numbers (e.g., "Sara, prenota per Mario Rossi"), this PII transits the CF Worker and reaches Groq's/Cerebras's EU or US servers.

### DPA status

- **Groq:** Groq provides a standard DPA. FLUXION has no documented DPA with Groq found in the codebase.
- **Cerebras:** Similar situation.
- **Cloudflare Workers:** Cloudflare's standard DPA covers Workers/KV data processing. This covers the email stored in KV.
- No `DPA.md` or DPA reference file found in the repository.

### GDPR position

Under Art. 28 GDPR, when FLUXION (as data processor for the PMI owner) sub-processes data through Groq/Cerebras, a sub-processor DPA is required. If names/phone numbers reach Groq servers in the US, and no SCCs (Standard Contractual Clauses) or adequacy decision exists for the data transfer, this is a violation of Art. 46 GDPR (international transfers).

**STATUS: NON-COMPLIANT**  
No documented DPA with Groq/Cerebras. PII may transit to US-based LLM providers without adequate safeguards. This is the most legally exposed gap in the cloud processing chain.

**Mitigation available:** The NLU requests should strip or pseudonymize client names and phone numbers before sending to the LLM proxy. The intent can be extracted from conversation text without transmitting `"Mario Rossi, +39 347 123 4567"` to Groq.

---

## 9. Privacy Policy — Landing Page

### Current state

The landing page (`landing/index.html`) contains:
- Line 358: "Nomi, numeri e appuntamenti rimangono sul tuo computer. Nessuna azienda esterna li vede."
- Line 2004: "Sei in regola con la legge sulla privacy (GDPR) perche' non c'e' nessun trasferimento di dati a terzi."
- Footer (line 2110-2114): Links to "Acquista", "FAQ", "Supporto" — **no Privacy Policy link**

No `privacy.html` page exists in `landing/`. No `termini.html` page exists in `landing/`.

**LEGAL REQUIREMENT:** Under Art. 13 GDPR, when personal data is collected (the buyer's email via Stripe checkout), the data controller must provide a privacy notice. The Stripe checkout collects the buyer's email, name, and payment data. The landing page drives traffic to Stripe — a privacy policy is mandatory before or at the point of collection.

Additionally, the claim "sei in regola con il GDPR" on the landing page is potentially misleading if said compliance gaps exist. This statement should be qualified.

**STATUS: NON-COMPLIANT**  
No Privacy Policy page. No Terms of Service page. Footer does not link to either. This is a hard requirement under Art. 13 GDPR and the Italian Codice del Consumo (D.Lgs. 206/2005) for e-commerce.

---

## 10. Cookie Consent — Landing Page

### What cookies/tracking are used

A full scan of `landing/index.html` found:
- **Google Fonts** (lines 10-11): `fonts.googleapis.com` and `fonts.gstatic.com` — these set third-party cookies and transmit the visitor's IP to Google
- **Tailwind CDN** (line 12): `cdn.tailwindcss.com` — external script, potential third-party tracking
- **No Cloudflare Web Analytics** beacon script found — CF analytics not actively deployed on this landing

The Google Fonts embed is the primary concern: the Italian Garante (Provvedimento 09/12/2021 on Google Fonts) ruled that loading Google Fonts via CDN transfers visitor IP addresses to Google's US servers and violates GDPR without consent. The Garante issued a formal ruling against this practice in 2022.

### Cookie banner

**No cookie banner found** in `landing/index.html`.

**STATUS: NON-COMPLIANT**  
Google Fonts loaded from CDN transmits visitor IPs to Google without consent. No cookie consent banner. Fix: self-host the Inter font or use system fonts. If Google Fonts CDN is retained, a cookie/tracking consent banner is required.

---

## Compliance Summary

| Category | Status | Severity |
|----------|--------|----------|
| 1. PII Inventory | COMPLIANT | — |
| 2. Data Retention — policy | COMPLIANT | — |
| 2. Data Retention — automated execution | PARTIAL | MEDIUM |
| 3. Right to Erasure (Art. 17) | NON-COMPLIANT | HIGH |
| 4. Data Export / Portability (Art. 20) | PARTIAL | MEDIUM |
| 5. Consent collection — per client | COMPLIANT | — |
| 5. Consent collection — first launch | PARTIAL | MEDIUM |
| 6. Encryption at rest | NON-COMPLIANT | HIGH |
| 7. Voice data — audio cleanup | COMPLIANT | — |
| 7. Voice data — caller notification | NON-COMPLIANT | HIGH |
| 8. CF Worker — DPA with sub-processors | NON-COMPLIANT | HIGH |
| 8. CF Worker — PII in NLU requests | PARTIAL | HIGH |
| 9. Privacy Policy page | NON-COMPLIANT | CRITICAL |
| 10. Cookie consent (Google Fonts) | NON-COMPLIANT | HIGH |

---

## Remediation Roadmap

### Priority 1 — CRITICAL (block launch)

**P1-A: Privacy Policy + Terms page**  
Create `landing/privacy.html` and `landing/termini.html`. Add links to footer.  
Privacy policy must cover: data controller identity, categories of data collected, legal basis (Art. 6 + Art. 9 for health verticals), retention periods, rights (access, erasure, portability), sub-processors (Stripe, Resend, Groq/Cerebras), international transfers.  
Effort: 2 hours (copy + legal text). Template available.

**P1-B: Google Fonts — self-host or system font fallback**  
Replace CDN embed with locally-served font files or system-font stack. Eliminates the need for a cookie banner.  
Effort: 30 minutes.

### Priority 2 — HIGH (resolve before first paying customer)

**P2-A: Right to Erasure — hard delete / anonymize**  
Implement `gdpr_erase_cliente(id)` Rust command that:
1. Overwrites PII fields with `"[RIMOSSO]"` / null (nome, cognome, telefono, email, codice_fiscale, indirizzo, note)
2. Deletes linked `messaggi_whatsapp`, `voice_session_turns` for the client
3. Nullifies linked health records (schede_mediche etc.)
4. Sets `deleted_at` and logs ANONYMIZE action in audit_log
5. Preserves booking records with anonymized client reference (for financial retention)

Effort: 4-6 hours.

**P2-B: Activate field-level encryption**  
Wire `encrypt_field()` / `decrypt_field()` into the `clienti` create/update path in `commands/clienti.rs`. Call `gdpr_init_encryption()` at app startup (use device UUID as device_id, derive master key from license email).  
Effort: 4 hours.

**P2-C: DPA with Groq and Cerebras**  
Sign Groq's DPA (available at console.groq.com/legal). Sign Cerebras DPA or remove Cerebras from the fallback chain if no DPA available. Document both in `docs/DPA-REGISTER.md`.  
Effort: 30 minutes (sign online) + documentation.

**P2-D: PII stripping before NLU proxy**  
In `orchestrator.py` or `nlu-proxy.ts`, strip or pseudonymize client names and phone numbers from the conversation context before sending to Groq. The LLM needs the utterance text, not the identified entity values.  
Effort: 2-3 hours in orchestrator.py.

**P2-E: Caller notification in Sara greeting**  
Modify the Sara opening greeting to include a brief GDPR disclosure:  
`"Benvenuto in [nome attività]. Sono Sara, l'assistente automatica. La conversazione sarà elaborata per gestire la sua prenotazione. Premi 0 per parlare con un operatore."`  
Effort: 30 minutes in booking_state_machine.py saluto config.

### Priority 3 — MEDIUM (resolve within 30 days of launch)

**P3-A: Automatic retention job**  
Add a scheduler call (using FLUXION's existing scheduler infrastructure — 5 jobs already running) to execute `run_gdpr_anonymization` and `cleanup_expired_audit_logs` daily.  
Effort: 1 hour.

**P3-B: First-launch consent screen**  
Add a step to `SetupWizard.tsx` that:
- Displays the Privacy Policy summary
- Asks the operator to confirm they are the data controller
- Records acceptance with timestamp in `impostazioni` table
- Blocks app use until accepted  
Effort: 2 hours.

**P3-C: Export for health records**  
Add CSV/JSON export for `schede_mediche`, `schede_fisioterapia`, `schede_odontoiatriche` per client. Required for portability under Art. 20 for health verticals.  
Effort: 2-3 hours.

---

## Notes on Architecture

The core architectural decision — **local SQLite, data never leaves the device** — is the strongest privacy-by-design element in FLUXION. Under Art. 25 GDPR (privacy by design), storing all client data locally without cloud sync significantly reduces the attack surface and limits FLUXION's exposure as a data processor.

The `gdpr_settings` table, `audit_log` infrastructure, `gdpr_requests` workflow, and `anonymized_at` markers in `voice_session_turns` demonstrate that considerable thought has been applied to GDPR compliance. The gaps identified above are implementation gaps, not architectural ones — the foundation is sound.

The most sensitive data category in the codebase is Art. 9 health data in the medical/dental/physio verticals. For these verticals, the legal basis is Art. 9(2)(h) (medical professional purposes) and explicit consent under Art. 9(2)(a). Both bases require the PMI owner to have a formal privacy notice for their patients — FLUXION should provide a template in the product for this purpose.
