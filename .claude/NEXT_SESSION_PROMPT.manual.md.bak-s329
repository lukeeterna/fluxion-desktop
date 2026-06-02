# FLUXION — S329 resume — R-01-ter VERIFY (Rust cargo + E2E) → merge MASTER R-01

> Scritto 2026-06-02 a chiusura S328. Branch `fix/license-interop-r01-s327`.
> S328 ha CHIUSO l'implementazione R-01-ter (4 task + reorder). Restano solo VERIFY esterni.
> NON ri-implementare: tutto committato in `98fd7ec` + `6fd8838`. Parti dai gate.

## STATO VERIFICATO (committato, NON ri-aprire)
- Task 0 — webhook `charge.refunded` + `charge.dispute.created` → KV `purchase:{email}.refunded=true`
  (fail-soft 200). `stripe-webhook.ts` ~:373-498 + dispatch ~:549. Email: `billing_details.email ?? receipt_email`; dispute → `stripe.charges.retrieve(dispute.charge)`.
- Task 3b — `POST /api/v1/license/validate` (`license-validate.ts`, registrato in `index.ts` PRIMA di authMiddleware): `{status:valid|revoked, server_time firmato HMAC LICENSE_RECOVERY_SECRET}`. **FAIL-OPEN** su KV missing/corrupt.
- Task 3c/3d — Rust `LicenseStatus` + SELECT espongono `last_validated_at` + `licensee_email` (`license_ed25519.rs`). `use-phone-home.ts` chiama `validateLicenseHeartbeat(email)` accanto al phone-home → `decision==='lock'` forza `saraEnabled=false` (Sara-only lock, MAI blocco totale — `architecture-distribution.md`). Offline grace 7gg + clock-rollback guard. Banner revoked + grace per TUTTI i tier incl. Pro (reorder S328, no silent lock).
- Deferred ADR-007 (`docs/context/DECISIONS.md`): hardware binding, trigger = "primo abuso multi-macchina su cliente reale".
- Gate G1: `tsc --noEmit` app + proxy EXIT 0 (verificato 2× S328).

## PRIMO PASSO — Rust cargo check (RISCHIO #1, NON saltare)
Le modifiche Rust sono SOLO additive ma NON ancora compilate. sqlx fa compile-time query check:
le colonne `last_validated_at` E `licensee_email` DEVONO esistere in `license_cache` (verificare migrations).
```
git push -u origin fix/license-interop-r01-s327
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git fetch && git checkout fix/license-interop-r01-s327 && git pull && cargo check 2>&1 | tail -30"
```
Se sqlx fallisce su colonna mancante → aggiungere migration (NON è gap di codice, è schema). Evidence: cargo check Finished EXIT 0.

## GATE DI CHIUSURA (fatti terminali esterni)
- G2 E2E EMAIL-EMBED già coperto da suite S327 (37/37 proxy) — ri-confermare se toccato.
- G3 E2E REFUND (richiede deploy + Stripe TEST):
  1. CONFIG deploy: sottoscrivere `charge.refunded` + `charge.dispute.created` nel webhook Stripe (NON ancora fatto).
  2. Stripe TEST 4242 → acquisto → refund → KV `purchase:{email}.refunded:true`.
  3. `POST /validate` → `revoked` → app: `saraEnabled=false` + banner revoked.
  4. Mock `last_validated_at` -8gg + offline → LOCK; clock-rollback → LOCK.
- Stripe shapes flaggati `[VERIFIED-BY-KNOWLEDGE, non da .d.ts locale]`: confermare `dispute.charge` (string id) + `Charge.billing_details.email`/`receipt_email` contro SDK pinnato durante review.

## DOPO I GATE → merge MASTER R-01
`git checkout master && git merge --no-ff fix/license-interop-r01-s327` chiude MASTER R-01.

## BLOCKED-ON (non blocca verde, dipende da Luke/mondo reale)
- Deploy live proxy + landing → CF Registrar `fluxion-app.com` (Task A S308).
- Smoke €1 live + Luke GO (REGOLA #18 META-VINCOLO: NO production claim senza output reale letto da Luke).

## LIMITE NOTO DEL DESIGN (documentato, onesto)
Enforcement client-side: garanzia FORTE = revoca-online-immediata al 1° /validate. Offline = fiducia nel client (binario patchabile + clock-freeze aggira grazia). fail-open su KV-miss. Binding hardware DEFERRED-con-trigger (ADR-007).

## NOTA PROCESSO S328
L'hook `auto-close session` ha committato il lavoro dell'agent (`98fd7ec`) PRIMA del GO L0 di Luke — il gate "uncommitted fino ad approvazione" è stato bypassato da automazione. Contenuto corretto e poi approvato, ma valutare se l'hook auto-close debba escludere branch security-critical.
