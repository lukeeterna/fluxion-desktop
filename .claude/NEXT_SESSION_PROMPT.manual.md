# Prompt ripartenza S278 — backlog Gate 1 S184 (CTO discrezione, REGOLA #15)

## Stato chiusura S277 (VERDE, Track A Gate 1 critical path)

**S277 outcome**: B-4 Ed25519 license verify unit tests 5/5 PASS + 30/30 integration regression PASS. Track A roadmap pipeline — S184 Step 1 da `ROADMAP_S183_S190.md:75`. REGOLA #14 + REGOLA #15 PASS — 100% autonomous backend SSH+cargo, founder zero touch.

### Done S277
1. ✅ **Refactor `src-tauri/src/commands/license_ed25519.rs`** (+148 righe net): estratto `fn verify_license_signature_with_key(license, sig_b64, pubkey_hex)` da `verify_license_signature`. La fn pubblica ora delega in 1 riga passando `FLUXION_PUBLIC_KEY_HEX`. Zero breaking change esterno.
2. ✅ **5 unit test inline `#[cfg(test)] mod tests`** atomici:
   - `test_ed25519_roundtrip_signed_license_verifies` (happy path)
   - `test_ed25519_tampered_license_fails_verify` (tier escalation post-sign)
   - `test_ed25519_tampered_signature_fails_verify` (bit flip sig)
   - `test_ed25519_wrong_public_key_fails_verify` (cross-key attack)
   - `test_ed25519_canonical_json_serialization_stable` (serde determinism)
3. ✅ **Fixtures**: `fixture_license()` + `fixture_keypair()` (OsRng + SigningKey::generate) + `sign_license()`. NO dipendenza da chiave prod.
4. ✅ **iMac cargo test**: 5/5 PASS in 0.00s (compile 1m45s su Intel 2012).
5. ✅ **Regression**: 30/30 PASS (fatture 4 + clienti 4 + operatori 4 + supplier 5 + appuntamenti 9 + encryption_repair 4).
6. ✅ **Totale backend test post-S277: 35/35 PASS** (baseline +5).

### Analisi critica strutturale (vincolo #4)
- **Assunzione test**: `serde_json::to_string` produce JSON deterministico — verificato dal 5° test (anti-regression).
- **Cosa rompe a 30gg**: rotation pubkey prod → la `FLUXION_PUBLIC_KEY_HEX` cambia, ma `verify_license_signature_with_key` accetta pubkey come parametro → test indipendenti. ✅ rotation-safe.
- **Pattern noto**: ed25519-dalek 2 API ha breaking change vs 1.x (SigningKey vs Keypair). Test scritti su API 2.x corrente. ✅
- **Dove sovradimensiono**: 5° test (serde determinism) potrebbe essere considerato over-defensive. Lo tengo perché anti-regression critico — se serde introduce HashMap ordering, tutti gli altri 4 test diventano falsi positivi.

---

## TASK candidati S278 (CTO discrezione, REGOLA #15 — no A/B)

### Track A: continuare S184 Gate 1 B-5 backup integrity (highest ROI per gate critical path)
- ROADMAP_S183_S190.md Step 4-6 (~4h): backup SHA256 pre/post + WAL checkpoint + restore + concurrent + corrupted recovery.
- Pattern: integration test stile S271/S273 con tempdir + sqlite file backup/restore.
- Vantaggio: avanza Gate 1 al lancio, 100% backend autonomous, REGOLA #14 compatible.
- Effort: ~4h, agent `database-engineer`.

### Track B: live verify BUG-FATT-3 S276 + fix BUG-FATT-5 (richiede founder GUI)
- Live E2E founder GUI iMac con Keychain unlock per confermare S276 fix funziona end-to-end.
- Se OK, fix definitivo BUG-FATT-5: `<Toaster position="top-center" toastOptions={{style:{zIndex:9999}}} />` globale in `App.tsx` o `main.tsx`.
- Effort: ~30min live verify + ~30min fix toast.
- BLOCCATO se servizi iMac DOWN (HTTP Bridge :3001 / Voice :3002).

### Track C: S184 Step 2-3 B-4 E2E Stripe TEST → email → activate (infra-heavy)
- Setup CF Worker test secrets + Stripe TEST credentials + Resend test inbox.
- Richiede setup esterno (Stripe sandbox account già esiste? Resend `onboarding@resend.dev` già wired) → verifica preliminare.
- Effort: ~2.5h, agent `license-manager` + `e2e-tester`.

### Track D: founder-driven (priorità alta se emerge pain operativo)

---

## Vincoli S278
- **REGOLA #14**: CTO autonomous test+fix backend via SSH+cargo. Founder solo decisioni strategiche / GUI Keychain unlock.
- **REGOLA #15**: NO domande A/B su scope. Decide best ROI/risk e parti.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/schema config) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S278

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S277 close + backlog Gate 1.

REGOLA #15 attiva: decidi track autonomamente.

Track suggested: Track A (B-5 backup integrity 4h, gate critical path, 100% autonomous).

REGOLA #14: backend-side autonomous. Founder solo override su pain operativo.
```

---

**Provenienza S277 close**: VERDE pieno. 5/5 unit license + 30/30 regression + REGOLA #14 PASS + REGOLA #15 PASS. Commit S277 atomico in chiusura.
