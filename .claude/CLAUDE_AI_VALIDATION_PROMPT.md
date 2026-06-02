# VALIDATION PROMPT — Giudice esterno (Claude web) — R-01 license interop

> Incolla su claude.ai web. Valida che i claim del CTO siano coerenti coi DIFF
> reali, PRIMA di "R-01 CLOSED". Non bloccante per l'implementazione (già fatta).

## CONTESTO (fatti verificati da codice)

- Worker CF `fluxion-proxy` emette licenza V1: payload JSON 6 campi
  `{kid, license_id, customer_email, product, session_id, issued_at(int)}`,
  firma Ed25519 chiave v1 `0616ec…`. NESSUN hardware fingerprint nella firma.
- Client Tauri, 2 path attivazione:
  1. EMAIL (primario): FE `activateByEmail()` → POST `/api/v1/activate-by-email`
     → Worker lookup KV `purchase:{email}` → `{activated, tier, features}`.
     PRIMA del fix: FE salvava SOLO localStorage, NON invocava command Rust,
     NON popolava SQLite `license_cache`.
  2. PASTE MANUALE (fallback): `activate_license_ed25519` → chiave LEGACY
     `c61b3c…`, struct 11 campi, hardware-lock rigido → incompatibile con V1.
- UI legge stato via Rust `get_license_status_ed25519` (legge `license_cache`),
  NON da localStorage.
- Esiste GIÀ recovery `GET /api/v1/license/:email?token={hmac}` → ritorna
  `{license_id, tier, license_payload, license_signature, issued_at}`.
- Esiste GIÀ `verify_ed25519_signature_dalek` (chiave v1) con test su firma
  REALE Worker (S291) → `valid:true`.

## CLAIM DA VALIDARE

A) Path EMAIL era split-brain: cliente vede "attivato" ma feature gated da Rust
   restano bloccate (license_cache mai popolata). Day-1 = refund.
B) Fix = nuovo command Rust `activate_license_v1`: verifica firma V1 (riuso
   verifier), deriva `FluxionLicense` localmente (product→tier, issued_at
   int→string, `hardware_fingerprint` generato al 1° avvio = bind locale NON in
   firma), salva in `license_cache`; re-bind su ri-attivazione (save_license
   id=1 ON CONFLICT UPDATE).
C) Per chiudere lo split-brain email: aggiungere a `/api/v1/activate-by-email`
   i campi `license_payload`+`license_signature` (già in D1 `webhook_events`).
   Additivo: NON cambia schema firma né payload firmato → NON viola "Worker
   INTOCCATO" (= non cambiare schema firma).

## DIFF REALE (341 ins / 25 del, 7 file)

- `src-tauri/.../license_ed25519.rs` (+231): `ActivateLicenseV1Input` (serde
  alias payload/signature), `WorkerLicensePayloadV1`, helper puro
  `verify_and_derive_v1()` (Ok(None)=firma invalida, Ok(Some)=valida, Err=
  strutturale), command `activate_license_v1`. + mod `activate_v1_tests` con
  payload/firma REALI S291: real→Base, alias format, tamper payload→None,
  tamper sig→None, unknown kid→Err.
- `src-tauri/src/lib.rs` (+2): registra command in invoke_handler.
- `fluxion-proxy/.../activate-by-email.ts` (+31): D1 lookup additivo fail-soft.
- `src/hooks/use-license-ed25519.ts` (+19): hook `useActivateLicenseV1`.
- `src/lib/activate-by-email.ts` (+5): campi license_payload?/signature?.
- `src/components/license/LicenseManager.tsx` (+40): email path crypto-persist
  via `activate_license_v1` (fail-soft); handleActivate detect Worker V1 JSON →
  route V1 vs legacy; isPending combinato; data-testid.

Type-check TS: **EXIT=0, zero errori**. cargo test: DA ESEGUIRE su iMac (G1).

## DOMANDE

1. Claim A corretto, o esiste meccanismo non citato per cui email popolava già
   `license_cache`?
2. Claim C davvero additivo e privo di rischio crypto, o payload+firma nella
   risposta `activate-by-email` apre un vettore (esfiltrazione/replay) che
   giustifica tenere SOLO recovery URL HMAC?
3. issued_at int→string lato Rust vs unificare a int: quale rompe meno
   (save_license/migration/views/UNIQUE)?
4. Routing FE in `handleActivate` (JSON con `license_payload||payload` → V1,
   altrimenti legacy): edge-case che instradano male una licenza valida?

Rispondi CONFERMA / CONFUTA per ciascun claim + motivazione tecnica.
