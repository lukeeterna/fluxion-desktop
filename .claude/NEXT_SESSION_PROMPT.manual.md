# NEXT SESSION — FLUXION — R-01-bis GATE done, STOP per review Luke

> Implementazione R-01 GIÀ FATTA (commit d46e32f, branch audit/e2e-reality-check-s324).
> R-01-bis GATE eseguito. **Trovata 1 DIVERGENZA critica** vs direttiva GATE #2.
> ASPETTA ok Luke sul corrective PRIMA di toccare codice.

## GATE 3 grep (evidenza per MASTER R-01)

**GATE #1 — writer di `license_cache`:**
- `save_license()` = `src-tauri/src/commands/license_ed25519.rs:362-460` (id=1,
  ON CONFLICT UPDATE → re-bind automatico).
- Oggi popolata SOLO da `activate_license_ed25519` (paste, chiave legacy).
- Path EMAIL (`src/lib/activate-by-email.ts` → `activateByEmail()`) storicamente
  scriveva SOLO localStorage, mai un command Rust → mai `save_license` →
  **split-brain**. Fix d46e32f: email path ora chiama `activate_license_v1` →
  `save_license` (LicenseManager.tsx, crypto-persist fail-soft).

**GATE #2 — protezione esposizione payload+firma:**
- Recovery HMAC = `fluxion-proxy/src/routes/license-recovery.ts:42-46,107-110`
  (HMAC-SHA256(LICENSE_RECOVERY_SECRET, email) + constant-time compare).
- **DIVERGENZA**: il mio fix d46e32f espone `license_payload`+`license_signature`
  su `fluxion-proxy/src/routes/activate-by-email.ts:124-159`, endpoint che NON ha
  HMAC — controlla solo `email.includes('@')` (`activate-by-email.ts:67`).
  → Chiunque conosca l'email di un cliente può estrarre la sua licenza firmata
  (vettore enumeration/esfiltrazione). **VIOLA la direttiva GATE #2** ("stessa
  HMAC del recovery, non endpoint meno protetto").

**GATE #3 — tipo `issued_at`:**
- `fluxion-proxy/src/lib/ed25519-sign.ts:132` → `issued_at: number; // unix epoch
  seconds` (INT confermato). Canonical key-order L157,168.
- Rust `WorkerLicensePayloadV1.issued_at: i64` = MATCH. La firma è verificata sui
  byte raw del payload string (key-order preservato), int intatto. Conversione a
  RFC3339 solo per `FluxionLicense.issued_at: String` (storage locale, no
  migration).

## CORRECTIVE raccomandato (single, da approvare Luke)

Revertare l'esposizione su `activate-by-email.ts` (24-29 + 124-159) e far sì che
il path EMAIL del client chiami il recovery HMAC-protetto
`GET /api/v1/license/:email?token={hmac}` (che GIÀ ritorna payload+firma) →
`activate_license_v1`. Così: GATE #2 rispettato + Worker davvero minimale +
split-brain comunque chiuso. PROBLEMA aperto: il client deve poter calcolare il
token HMAC → o il token arriva nell'email (link recovery), o serve un modo lato
client. Da decidere con Luke PRIMA di implementare.

## DOPO ok Luke
1. Applicare corrective GATE #2.
2. G1 cargo test su iMac (5 test activate_v1_tests, vedi sotto).
3. G2 E2E sul path EMAIL (4242 → webhook → D1 → email → attivazione-da-email →
   license_cache → UI feature attive). Evidence in
   `~/venture-os/state/s<NN>-r01-evidence.json`.
4. Ri-attivazione (nuovo fingerprint, stessa email/license_id).

Branch prompt R-01-bis = `fix/license-interop-r01-s327` (lavoro attuale su
`audit/e2e-reality-check-s324`, valutare rebranch/cherry-pick).

## G1 comando (Rust build solo iMac)
```
git push origin <branch>
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git fetch && git checkout <branch> && git pull"
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/src-tauri' && cargo test license_ed25519 -- --nocapture 2>&1 | tail -40"
```
ATTESO: real_worker_license_derives_base_tier, alias_payload_signature_format_works,
tampered_payload→None, tampered_sig→None, unknown_kid→Err.
