# NEXT SESSION — FLUXION — R-01 VERIFY (license interop)

> R-01 CODE COMPLETO + type-check TS GREEN. Manca SOLO la VERIFY su iMac (cargo
> test = G1) + E2E (G2). NON dichiarare R-01 CLOSED senza output test reale letto
> da Luke (META-VINCOLO REGOLA #18).

## STATO (implementazione fatta, NON ancora verificata)

Branch: `audit/e2e-reality-check-s324`. Commit locale presente, NON pushato.
7 file modificati (341 ins / 25 del). Tutti additivi, schema firma INTOCCATO.

- `src-tauri/src/commands/license_ed25519.rs` (+231): command `activate_license_v1`
  + helper puro `verify_and_derive_v1` + mod test `activate_v1_tests` (5 test,
  payload/firma REALI S291).
- `src-tauri/src/lib.rs`: command registrato in invoke_handler.
- `fluxion-proxy/src/routes/activate-by-email.ts`: D1 lookup additivo fail-soft
  → ritorna license_payload+signature.
- `src/hooks/use-license-ed25519.ts`: hook `useActivateLicenseV1`.
- `src/lib/activate-by-email.ts`: campi license_payload?/signature?.
- `src/components/license/LicenseManager.tsx`: email path crypto-persist + route
  V1 vs legacy in handleActivate + data-testid.

Verificato questa sessione: `npx tsc --noEmit` EXIT=0 zero errori. Import Rust
coerenti (base64::Engine L13, chrono DateTime/Utc L14).

## STEP 1 — VALIDATION GATE (prima di procedere)

Incolla `.claude/CLAUDE_AI_VALIDATION_PROMPT.md` su claude.ai web. ASPETTA il
verdetto di Luke (incollato). Se CONFUTA claim A/B/C → riapri investigazione,
NON procedere a deploy.

## STEP 2 — G1: cargo test su iMac (Rust build SOLO iMac, regola FLUXION)

Il codice è su branch feature locale, NON pushato. Per testare su iMac serve
sincronizzare. Opzione pulita (NO push master):
```
git push origin audit/e2e-reality-check-s324
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git fetch origin && git checkout audit/e2e-reality-check-s324 && git pull"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo test license_ed25519 -- --nocapture 2>&1 | tail -40"
```
ATTESO: 5 test `activate_v1_tests` PASS (real_worker_license_derives_base_tier,
alias_payload_signature_format_works, tampered_payload→None, tampered_sig→None,
unknown_kid→Err) + i test legacy esistenti invariati.

## STEP 3 — G2: E2E reale (card 4242)

Stripe TEST `4242 4242 4242 4242` → webhook test env → D1 `webhook_events` row
con license_payload+signature → recovery JSON / email payload → wizard activate
→ `success:true` + tier corretto in `license_cache` (NON solo localStorage).
Tamper → fail. Ri-attivazione → success (re-bind id=1).
NB: GUI activate iMac richiede founder fisicamente presente (Keychain GUI,
REGOLA #12) OPPURE activate via Rust test con payload D1 reale.

## STEP 4 — EVIDENCE + DEPLOY

- Salva G1+G2 in `~/venture-os/state/s<NN>-r01-evidence.json`.
- Worker change → `cd fluxion-proxy && wrangler deploy` (deploy additivo).
- FE/Rust → build iMac.
- Luke legge output reale → SOLO ALLORA "R-01 CLOSED".

## ROOT CAUSE (per contesto)

Path EMAIL primario era split-brain: cliente vede "attivato" (localStorage) ma
UI legge `get_license_status_ed25519` (license_cache) → resta trial → Day-1
refund. Fix = `activate_license_v1` verifica firma kid:v1 + deriva FluxionLicense
locale + popola license_cache. Worker emette V1 6-campi (no hw fingerprint),
legacy `activate_license_ed25519` aspettava 11-campi hw-lock → mai match.
