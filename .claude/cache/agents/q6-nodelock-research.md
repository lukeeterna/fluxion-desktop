# Q6 Node-Lock Server-Side — Research & Verifica a Sorgente (S372)

> Agente: backend-architect. Modalità: SOLO Read/Grep. Zero modifiche produzione.
> Tutto marcato [VERIFICATO file:riga] vs [ASSUNTO].

---

## 1. VERDETTO Q4 — Re-bind primitive: ESISTE (ed è automatica)

**[VERIFICATO `src-tauri/src/commands/license_ed25519.rs:712-714`]** — il commento sorgente dice esplicitamente:
> "Hardware-bind = macchina corrente al momento dell'attivazione (NON è nella firma): la ri-attivazione su stessa/nuova macchina re-binda (save_license id=1, ON CONFLICT UPDATE) invece di rifiutare."

**Meccanica del re-bind [VERIFICATO]:**
- `activate_license_v1` (`:799-830`) chiama `verify_and_derive_v1` (`:747`) → verifica SOLO la firma del Worker sui 6 campi del payload (kid, license_id, customer_email, product, session_id, issued_at). **Il fingerprint NON è nel payload firmato.**
- `:786` — la `FluxionLicense` derivata localmente prende `hardware_fingerprint: generate_fingerprint()` = **fingerprint della macchina CORRENTE**, non quello del payload.
- `:818` → `save_license` con `INSERT ... VALUES (1, ...) ON CONFLICT(id) DO UPDATE SET fingerprint = excluded.fingerprint` (`:419-420`). **Re-bind automatico:** ri-attivare su un nuovo PC sovrascrive il fingerprint di riga `id=1`.

**Escape-valve esiste:** il cliente che cambia PC/reinstalla rilancia `activate_license_v1` (incollando la stessa licenza dal link recovery) → si re-binda da solo, senza intervento. **NESSUN rischio lock-out dal binding attuale**, perché il binding non è nella firma ma derivato local-side ad ogni attivazione.

---

## 2. Punto di verifica fingerprint attivo nel GESTIONALE (non solo Sara)

**[VERIFICATO `:540-548`]** `get_license_status_ed25519` (lo status letto all'avvio dal frontend):
```rust
"active" => {
    if tier != LicenseTier::Trial && fp != fingerprint {
        false  // Hardware mismatch  (:544)
    } else { ... }
}
```
- `fp` = fingerprint salvato in `license_cache` (`:498`); `fingerprint` = `generate_fingerprint()` macchina corrente (`:463`).
- **Quindi il node-lock È GIÀ ATTIVO nel gestionale**: una licenza active su una macchina con fingerprint diverso → `is_valid=false`, `validation_code="HARDWARE_MISMATCH"` (`:558-559`).
- **MA** è sanato dal re-bind del §1: appena il cliente ri-attiva, `fp` viene riscritto = match. Funziona perché la licenza è recuperabile (chiunque abbia email+token recovery la riscarica e re-attiva).

**Conseguenza chiave per Q6:** il gate `fp != fingerprint` client-side è **bypassabile da un cracker** che incolla la licenza (firma valida) su qualsiasi PC → re-bind automatico. Il binding client-side NON impedisce condivisione/pirateria. Solo un binding **nella firma** (server-side) lo impedisce. È esattamente ciò che propone Q6.

---

## 3. generate_fingerprint — stabilità

**[VERIFICATO `:285-310`]** Composizione: `hostname : cpu_brand : total_memory : system_name` → SHA-256 → primi 16 byte hex.
- **Stabile a reinstall OS-stesso**: hostname e RAM possono cambiare (rinomina PC, upgrade RAM) → fingerprint cambia.
- **Cambia con hardware**: nuovo PC = nuovo fingerprint (corretto per node-lock).
- **Debolezza nota [VERIFICATO]**: dipende da hostname (utente-modificabile) e total_memory → NON robustissimo, ma sufficiente per anti-share B2B. (Esiste anche `license.rs:145` un secondo `generate_fingerprint` legacy — non usato dal path V1.)

---

## 4. Formato payload licenza firmato [VERIFICATO]

`fluxion-proxy/src/lib/ed25519-sign.ts:126-133` — `LicensePayloadV1` (6 campi, key-order canonico fisso `:160-169`):
```
kid: 'v1' | license_id | customer_email | product('base'|'pro') | session_id | issued_at(unix sec)
```
- Firma: `signEd25519(ED25519_PRIVATE_KEY_PKCS8, canonical)` (`:79-90`).
- Emessa in `stripe-webhook.ts:735-744`.
- Verifica client: `verify_and_derive_v1` deserializza `WorkerLicensePayloadV1` (stessi 6 campi, `license_ed25519.rs:733-742`).
- **Vincolo canonicalizzazione:** key-order esplicito perché Rust ri-serializza identico per la verifica. Aggiungere un campo richiede modifica COORDINATA Worker (canonicalize) + Rust (struct + ri-serializzazione verifica).

---

## 5. Fattibilità Q6 — server-side node-lock al retrieve

### (a) Canale app→Worker col fingerprint — GIÀ ESISTE
**[VERIFICATO `src/lib/phone-home.ts:195-204`]** L'app già fa `POST /api/v1/license/validate` body `{email}` dall'app (non dal browser). Si può estendere a `{email, fingerprint}`. Il fingerprint si ottiene già dal comando Tauri `get_machine_fingerprint_ed25519` (`license_ed25519.rs:833-836`).
- Il recovery attuale (`license-recovery.ts`) è GET browser-based con HMAC token → NON adatto a ricevere il fingerprint dall'app. **Q6 richiede un NUOVO endpoint POST app-based** (o estendere `/validate` a restituire la licenza ri-firmata).

### (b) Embeddare fingerprint nel payload — DA AGGIUNGERE
Aggiungere campo `device_fingerprint` a `LicensePayloadV1`. Impatto coordinato:
- `ed25519-sign.ts:126-133` (interface) + `:160-169` (canonicalize, key-order).
- `license_ed25519.rs:733-742` (`WorkerLicensePayloadV1` struct) + `:780-793` (usare `payload.device_fingerprint` invece di `generate_fingerprint()` a `:786`).
- `get_license_status_ed25519:544` resta invariato: confronterà il fp firmato vs macchina corrente → mismatch = lock REALE non bypassabile (la licenza è legata crittograficamente a quel device).

### (c) Ri-firma con chiave Worker — FATTIBILE, infra esiste
`signEd25519` + secret `ED25519_PRIVATE_KEY_PKCS8` già presenti sul Worker (`stripe-webhook.ts:744`). Un nuovo endpoint può ricostruire il payload (6 campi da D1 `webhook_events` + il `device_fingerprint` ricevuto dall'app), ri-firmarlo, restituirlo. Zero-cost (riusa CF Worker + chiave esistente).

---

## 6. Piano implementativo Q6 (step concreti)

> NON implementato. Step proposti per sessione di build su iMac.

1. **Worker — nuovo endpoint** `POST /api/v1/license/bind` (`fluxion-proxy/src/routes/`, nuovo file):
   input `{email, token(HMAC riuso `computeRecoveryToken`), device_fingerprint}`.
   - Refund-gate riuso `LICENSE_CACHE.get('purchase:'+email)` (license-recovery.ts:117-134).
   - D1 lookup riuso query `webhook_events` (license-recovery.ts:138-147).
   - Build payload con `device_fingerprint` + `signEd25519`. Restituisce `{license_payload, license_signature}`.
2. **ed25519-sign.ts**: aggiungi `device_fingerprint: string` a `LicensePayloadV1:126` + `canonicalizeLicensePayload:160` (key-order esplicito, in coda per retro-compat verifica vecchie licenze 6-campi → serve fallback verify).
3. **Rust `WorkerLicensePayloadV1:733`**: aggiungi `device_fingerprint: Option<String>`; in `verify_and_derive_v1:786` usa `payload.device_fingerprint.unwrap_or_else(generate_fingerprint)` (retro-compat: licenze vecchie senza campo → comportamento attuale).
4. **Frontend**: nuovo hook/flow che al primo activate chiama `get_machine_fingerprint_ed25519` → POST `/bind` → riceve licenza fingerprint-bound → `activate_license_v1`.
5. **Verifica firma**: il client deve verificare con lo STESSO canonical-order del Worker (campo in coda) — coordinare `license_ed25519_v1.rs` verifier.

---

## 7. Rischi / blocchi

- **[RISCHIO CANONICAL]** Aggiungere un campo al payload firmato rompe la verifica delle licenze GIÀ emesse (6 campi). MITIGAZIONE: dual-verify (prova 7-campi, fallback 6-campi) o `device_fingerprint: Option` con default. **OBBLIGATORIO** per non lockare i clienti S317/esistenti.
- **[RISCHIO LOCK-OUT con Q6]** Una volta che il fp è NELLA firma, cambiare PC richiede una NUOVA chiamata `/bind` per ri-firmare col nuovo fp. Se il refund-gate o D1 sono down → cliente pagante non può re-bindare offline. MITIGAZIONE: grace offline (phone-home già ha `loadValidateLastOk` cache) + il `/bind` deve essere idempotente e sempre disponibile.
- **[RISCHIO node-lock SENZA re-bind]** (scenario da evitare, NON è lo stato attuale): se si rimuovesse il re-bind automatico (§1) e si tenesse solo il check `:544`, si romperebbero: (1) cambio PC, (2) reinstall con hostname diverso, (3) upgrade RAM, (4) rinomina hostname. Tutti clienti PAGANTI → lock-out. **NON farlo.**
- **[VERIFICATO debolezza fingerprint]** hostname-based → poco robusto. Per node-lock crittografico considerare fingerprint più stabile (machine-id OS) ma è cambio invasivo, fuori scope Q6.

---

## Sintesi verdetti
- **Q4 re-bind**: ESISTE, automatico via `ON CONFLICT id=1 UPDATE fingerprint` (`:419-420`, `:712-714`). Escape-valve = ri-attivazione. Nessun rischio lock-out attuale.
- **Q6**: FATTIBILE zero-cost. Canale app→Worker già esiste (`phone-home.ts:199`). Manca: endpoint `/bind` POST, campo `device_fingerprint` nel payload firmato (coordinato Worker+Rust con retro-compat), ri-firma (infra presente). Il valore di Q6: rende il binding NON-bypassabile (oggi `:544` è aggirabile col re-bind).
