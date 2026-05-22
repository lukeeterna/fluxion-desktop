# Prompt ripartenza S281 — backlog Gate 1 + carry-over Track B/C

## Stato chiusura S280 (VERDE, Track A client-side propagation phone-home revoked)

**S280 outcome**: chiuso il loop S279 lato client. Worker (S279) già rispondeva `{status:'revoked', tier:'expired', sara_enabled:false}` per purchase refunded. S280 propaga lo stato nel DB SQLite `license_cache`, così che `get_license_status_ed25519` lo veda e `is_valid=false` blocchi tutto il gating feature/vertical lato Rust (era cachato SOLO in localStorage, volatile e clearabile).

### Done S280

1. ✅ **Pattern internal_** (S271/S273/S274/S275) — `internal_sync_license_status_from_phone_home(pool, status, tier)` in `src-tauri/src/commands/license_ed25519.rs`. Whitelist status accettati `{ok, expired, revoked, invalid}`. status='ok' no-op effettivo (solo `last_validated_at`), terminali UPDATE `status + tier + last_validated_at + updated_at`.
2. ✅ **Tauri command wrapper** `sync_license_status_from_phone_home_ed25519` delegate 1-riga. Registrato in `lib.rs:1148` invoke_handler.
3. ✅ **validation_code='REVOKED'** in `get_license_status_ed25519` (riga 539-541): branch dedicato per `status=='revoked'`, prima di `HARDWARE_MISMATCH`/`EXPIRED`. UI ottiene codice diagnostico corretto.
4. ✅ **By-construction safety** confermata: `is_valid` match a riga 523-534 ammette solo `"trial" | "active"`, tutti gli altri (incluso `"revoked"`) ricadono in `_ => false`. **NESSUNA modifica a `check_feature_access_ed25519` / `check_vertical_access_ed25519` richiesta** — il gating funziona già fail-safe via `if !status.is_valid { return Ok(false); }` (riga 694, 717). Scope ridotto da 4h a 2h.
5. ✅ **Frontend invocation** `src/hooks/use-phone-home.ts:62-86`: dopo `setResult(res)`, se `res.status !== 'offline'` invoca `invoke('sync_license_status_from_phone_home_ed25519', { status, tier, saraEnabled, saraDaysRemaining })`. Try/catch silent (backend older o DB error → fallback localStorage). Skip 'offline' per non scrivere stati derivati da cache locale.
6. ✅ **5 integration test** `src-tauri/tests/integration_license_revoke.rs` (PASS in 6.70s):
   - `test_sync_revoked_persists_status_and_tier_to_db` — happy path active/pro → revoked/expired, last_validated_at avanzato
   - `test_sync_ok_is_noop_for_status_tier_but_updates_audit_timestamp` — status='ok' preserva DB (firma Ed25519 locale autorevole), audit timestamp avanza
   - `test_sync_rejects_invalid_status_string` — input "garbage-from-fe" → Err + DB intatto (no scrittura parziale)
   - `test_sync_revoked_is_idempotent` — replay revoked payload → stato finale stabile
   - `test_sync_expired_and_invalid_also_propagate` — bonus coverage: 'expired' + 'invalid' UPDATE corretto

### Verify S280
- `cargo test --test integration_license_revoke`: **5/5 PASS in 6.70s** (compile 3m 20s su Intel iMac 2012)
- Regression suite iMac (clienti 4 + operatori 4 + supplier 5 + fatture 4 + appuntamenti 9 + encryption_repair 4 + backup 7) = **37/37 PASS, zero regression**
- **Totale backend S280: 42/42 PASS**
- `tsc --noEmit`: **0 errori** TS strict
- `eslint`: 0 errors, 17 warnings preesistenti in `e2e-tests/` (baseline S275-S279)

### Analisi critica strutturale (vincolo #4)

- **Assunzione**: `licensee_email` nel JWT firmato Ed25519 è coerente con `licensee_email` in `license_cache` DB. Conferma da `activate_license_ed25519` flow che popola entrambi. OK.
- **Cosa rompe a 30/60gg**: se Worker aggiunge nuovo status (es. `"suspended-billing"`), client default a `Err("Invalid phone-home status")` → catch silent in FE → fallback localStorage UI gating. Soft-degrade safe, no crash.
- **Pattern noto risk**: nessuno. localStorage clear non più bypass (DB SQLite persiste); attacker con accesso filesystem può alterare DB, ma in quel caso ha già accesso a license_data/signature plain → fuori threat model.
- **Sovradimensione evitata**: skip migration per estendere CHECK su colonna `status` (SQLite non enforce enum a meno di CHECK explicit; non c'è CHECK su status nella migration 015). Skip refactor di `get_license_status_ed25519` per testabilità isolata (logica già coperta indirettamente da behavior `is_valid=false` su status non-whitelist).

### Out of scope mantenuto S280

- **migration extension** `CHECK(status IN ('trial','active','expired','suspended','revoked','invalid'))` — non strict per safety, costa migration nuova (017_license_revoked_status.sql) per zero value funzionale immediato. Considerare se future audit DBA segnala.
- **Sara block runtime** in Python voice agent (porta 3002): se Sara è invocata da Rust http_bridge mentre license è revoked, Rust deve già rifiutare via `check_feature_access_ed25519("voice_agent")` → Ok(false) → no chiamata Python. Verificato per code-path lettura. Live test richiede pipeline UP (B-1).
- **Phone-home a startup**: `usePhoneHome` runs `useEffect` mount + 24h interval. Se utente non riavvia app dopo refund, status='revoked' attivo solo dopo phone-home successivo. Mitigation futura: forza phone-home dopo navigazione admin Stripe webhook → fuori scope S280.

---

## TASK candidati S281 (CTO discrezione, REGOLA #15)

### Track B — Setup CF Worker test env + Stripe E2E (~5-6h, founder-bottleneck per credenziali)
- Founder fornisce: `CLOUDFLARE_API_TOKEN` env var + Stripe TEST sandbox keys (sk_test_, whsec_test_) + Resend test API key.
- CTO: `[env.test]` block in `wrangler.toml` + KV namespace test separato + `wrangler deploy --env test` + Stripe Dashboard webhook endpoint TEST + curl POST checkout completed event (TEST card 4242) → verify chain (KV `purchase:{email}` scritto, email Resend test arrivata, magic link, activate-by-email response 200, phone-home post-refund ritorna `status='revoked'`).
- Effort: ~2h founder credentials/setup + ~3h CTO scripting + verify.
- **Chiude Gate 1 B-4 Step 2 (E2E Stripe full chain con TEST card 4242)** rimasto open da S279.

### Track C — B-1 Voice live audio test (~4h, Gate 1 critical, founder presence)
- Pipeline iMac UP (porta 3002 DOWN al boot S278-S280) + WAV reali 5 scenari (Gino/Gigio, soprannome VIP, chiusura graceful, flusso perfetto, WAITLIST) + microfono fisico per loopback.
- Agent: `voice-tester` + `voice-engineer`.
- Effort: ~4h, parziale autonomous (WAV pre-registrati SSH OK), parte live richiede founder + microfono.

### Track D — Audit cargo fmt residual iMac + igiene repo (30min, 100% autonomous)
- Vecchie sessioni lasciano residui fmt non flushati su iMac. `cargo fmt --check` su iMac → fix se diff → commit pulito.

### Track E — Migration `017_license_revoked_status.sql` opzionale (~30min, 100% autonomous, low-priority)
- Aggiunge CHECK constraint enum esteso su `status` per documentation + safety futura. Solo se DBA audit lo segnala (S280 non lo richiede strict).

### Track F — Force phone-home post Stripe webhook refund (~1-2h, autonomous)
- Server-side push notification al client per forzare phone-home immediato senza attendere 24h interval. Richiede infra: SSE? polling più frequente? webhook reverse? Spike di research necessaria prima di pianificazione.

---

## Vincoli S281

- **REGOLA #14**: CTO autonomous via SSH+cargo+npm. Founder solo CF/Stripe/Resend credentials + microfono live.
- **REGOLA #15**: NO A/B questions. CTO decide track + parte.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/wrangler.toml [env.test] schema) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S281

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S280 close + backlog.

REGOLA #15 attiva: decidi track autonomamente.

Track suggested: Track D (igiene cargo fmt ~30min, 100% autonomous) per warm-up + Track B se founder fornisce CF/Stripe/Resend credentials all'avvio (chiude Gate 1 B-4 Step 2). In subordine Track F (research force phone-home post webhook ~1-2h spike).

REGOLA #14: backend-side autonomous via SSH+cargo. Founder solo override su pain operativo o per fornire credentials test env.
```

---

**Provenienza S280 close**: VERDE pieno. 5/5 test integration_license_revoke + 37/37 regression = 42/42 PASS. Gap S279 chiuso lato client (Rust DB + FE invocation). Sara/loyalty/whatsapp/api_access bloccati by-construction su `status='revoked'` via `is_valid=false` propagation. Carry-over founder = solo Track B credentials per Gate 1 closure.
