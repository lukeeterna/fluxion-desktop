# PROMPT CC — SESSIONE B1 / R-01 (interop licenza, blocker revenue)

> Sessione DEDICATA, context fresco. Non incatenare ad altri blocchi.
> Ruoli: CC = esecutore · Claude AI web = giudice · Luke = autorità.
> Vincoli: L0 ask-always (diff + yes/no prima di scrivere file), chiusura ~60% context,
> nessun valore credenziale in chat/file. Codice revenue-critical → no edit sopra 50% context.

## ROOT CAUSE VERIFICATA (S327 research — code-truth, NON ri-verificare da zero)
Il blocker NON è "scrivere la crypto" (già fatta e testata). È **wiring + derivazione locale**.

**Cosa il FE chiama oggi** (sbagliato per licenze Worker):
- `src/hooks/use-license-ed25519.ts:108` → `invoke('activate_license_ed25519', { licenseData })`
- `src-tauri/.../license_ed25519.rs:604 activate_license_ed25519`:
  1. parsa `SignedLicense{ FluxionLicense(11 campi), signature }` (riga 611)
  2. verifica con chiave **LEGACY** `FLUXION_PUBLIC_KEY_HEX = c61b3c…` (riga 29/312),
     serializzando `FluxionLicense` a 11 campi
  3. impone `license.hardware_fingerprint == fingerprint` (riga 642) → hardware-lock RIGIDO

**Cosa il Worker emette** (`fluxion-proxy/.../stripe-webhook.ts` + `lib/ed25519-sign.ts`):
- payload `LicensePayloadV1` a **6 campi**: `kid, license_id, customer_email, product, session_id, issued_at(int)`
- firma con chiave **V1** `0616ec…`, **nessun** hardware fingerprint

→ I due non combaceranno MAI: `verify()` sempre false su licenza reale del Worker. Day-1 = cliente paga, attivazione fallisce, refund storm.

**Il verifier CORRETTO esiste già ed è wired al command ma orfano dal flusso:**
- `src-tauri/src/commands/license_ed25519_v1.rs`:
  - `verify_ed25519_signature_dalek(payload, sig_b64, kid)` → chiave V1 `0616ec…`, `verify_strict`
  - command Tauri `verify_license_signature_v1` registrato in `lib.rs:1153`
  - test `real_worker_signature_verifies_true` PASS su `REAL_PAYLOAD` = riga D1 reale S291
    (`evt_1TaKKhIW…`), commento "Verified roundtrip with worker POST /api/v1/verify → valid:true"
  - tamper payload/sig → false; unknown kid → Err. **Crypto interop GIÀ DIMOSTRATA.**

## DECISIONE GIÀ PRESA (modello b — NON ri-chiedere a Luke)
- Worker + landing **INTOCCATI**. Il client si adatta alla firma del Worker.
- Verificare la firma del Worker sul payload **6 campi V1** (riusare `verify_ed25519_signature_dalek`),
  poi **derivare `FluxionLicense` LOCALMENTE** dal payload verificato (product→tier, issued_at int→string, ecc.).
- Hardware-lock = **bind locale al 1° avvio, NON nella firma** (rischio pirateria B2B accettato).
  → NON rifiutare l'attivazione per fingerprint mismatch su licenze V1; salvare il fingerprint locale al primo activate.
- **Percorso ri-attivazione** in scope: reinstallo/cambio disco → ri-bind da stessa email/license_id
  (stessa licenza V1 re-attivabile, niente activation server, niente revoca online in v1).
- Unificare `issued_at` a **int** lato Rust per il path V1.
- Niente activation server / revoca online in v1.

## TASK B1 (ordine)
1. **PLAN** (no edit): definire la nuova funzione di activate V1 — nome (es. `activate_license_v1`
   o branch dentro `activate_license_ed25519` che detect-a il formato `{payload, signature, kid}`
   vs `SignedLicense`). Decidere shape input dal FE (probabile: il Worker/email consegna
   `{payload: string, signature: string, kid: string}`; verificare come il wizard riceve la licenza —
   leggere `use-license-ed25519.ts` + componente wizard activate + cosa Resend invia all'utente).
2. **IMPLEMENT** Rust:
   - parse `{payload, signature, kid}`; `verify_ed25519_signature_dalek` (esistente)
   - su valid: deserializza i 6 campi → costruisci `FluxionLicense` locale (mappa product→tier,
     genera/recupera hardware_fingerprint locale, issued_at int→string o unifica a int)
   - `save_license` (riusare path esistente)
   - ri-attivazione: se license_id già in `license_cache`, ri-bind invece di rifiutare
3. **FE**: wire `use-license-ed25519.ts` (o nuovo hook) per chiamare il command V1 con la licenza
   ricevuta. Tipare `invoke<T>()`. data-testid sul bottone activate.
4. **Cleanup issued_at**: unificare tipo (oggi `FluxionLicense.issued_at: String` vs payload int).
5. **REVIEW** `/fluxion-code-review`.
6. **VERIFY E2E reale** (acceptance):
   - `cargo test` su `license_ed25519_v1` + nuovi test activate V1 (real payload → success; tamper → fail)
   - **E2E reale**: carta test `4242 4242 4242 4242` → Stripe webhook (test env) → D1 row →
     payload+sig reali → wizard activate → `success:true` + tier corretto in `license_cache`.
     ⚠ Lo step GUI activate su iMac richiede founder fisicamente presente (Keychain GUI, REGOLA #12) —
     pianificare finestra founder-present o eseguire activate via test Rust con payload D1 reale.
   - tamper payload → activate fail; ri-attivazione stessa licenza → success (re-bind).
   - Salvare evidence (G1 cargo test + G2 E2E) in `~/venture-os/state/s<NN>-r01-evidence.json`.
7. NO "R-01 chiuso" senza output reale dei test letto da Luke (META-VINCOLO REGOLA #18).

## FILE CHIAVE
- `src-tauri/src/commands/license_ed25519_v1.rs` (verifier corretto, riusare)
- `src-tauri/src/commands/license_ed25519.rs` (activate legacy riga 604, FluxionLicense riga 47, save_license)
- `src-tauri/src/lib.rs:1153` (invoke_handler — registrare nuovo command se serve)
- `src/hooks/use-license-ed25519.ts:108` (FE activate)
- `fluxion-proxy/src/routes/stripe-webhook.ts` + `src/lib/ed25519-sign.ts` (Worker, READ-ONLY)
- `src-tauri/migrations/020_license_ed25519.sql` (schema license_cache)

## AUTOCRITICA (REGOLA #4) da validare in PLAN
- Assunzione: la licenza arriva al client come `{payload, signature, kid}`. Se invece il Worker/email
  consegna un blob diverso (es. base64 di tutto), il parse va adattato — VERIFICARE cosa Resend invia.
- issued_at int→string: attenzione a non rompere `save_license`/migration/UNIQUE/views esistenti (audit 4-point REGOLA #8).
- Ri-attivazione senza revoca = stessa licenza attivabile su N macchine → pirateria B2B (ACCETTATO da Luke).
- Coesistenza legacy `FluxionLicense` activate (trial/manuale) vs V1 (post-Stripe): non rompere il path trial.
