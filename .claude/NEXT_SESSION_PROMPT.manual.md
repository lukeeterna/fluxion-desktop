# Prompt ripartenza S280 — backlog Gate 1 S184/S185

## Stato chiusura S279 (VERDE, Track B'' autonomous Worker test infra + gap fix)

**S279 outcome**: vitest setup `fluxion-proxy/` + gap fix sicurezza `phone-home.ts` refund check + 13 unit test PASS (stripe-webhook 4 + refund 3 + activate-by-email 2 + phone-home 4) in 3.27s, TS strict 0 err. REGOLA #14 + REGOLA #15 PASS — 100% autonomous (zero CF token/Stripe sandbox/founder).

### Done S279

1. ✅ **Pivot CTO REGOLA #15**: Track B originale (Stripe E2E full chain con TEST card 4242) richiedeva founder per `CLOUDFLARE_API_TOKEN` + Stripe sandbox + Resend test inbox + magic-link click. Pivot a Track B'' = autonomous Worker test infra + gap fix.
2. ✅ **vitest infra** in `fluxion-proxy/`: `vitest@^1.6.1` devDep, `vitest.config.ts` minimal (no `@cloudflare/vitest-pool-workers` per compat Big Sur), npm scripts `test` + `test:watch`, `tsconfig.json` include `tests/**/*.ts`.
3. ✅ **Gap fix sicurezza `phone-home.ts`** (S184 Step 3 core logic): legge `LICENSE_CACHE.get(purchase:{licensee_email})` → se `refunded === true` ritorna `{status: 'revoked', tier: 'expired', sara_enabled: false, sara_days_remaining: 0}`. Persiste `cacheEntry.last_phone_home` aggiornato anche su revoked (audit trail). Email normalizzata lowercase+trim, defensive parse JSON con fallback graceful.
4. ✅ **`tests/_helpers.ts`** (~210 righe): `MockKVNamespace` (get/put/delete/list/setJson/getJson), `makeEnv` (default Env con KV + 18 secrets sintetici), `makeLicense`/`makeCacheEntry` fixtures, `makeContext` (mock Hono Context: `req.text/json/header/raw`, `get/set`, `json(body, status?)` con `_captured`), `buildStripeSignature` (HMAC-SHA256 t=ts,v1=hex), `mockFetch` (override globalThis.fetch + restore).
5. ✅ **`tests/stripe-webhook.test.ts`** (4 test):
   - happy path checkout.session.completed → KV write `purchase:{email}` (refunded=false) + `session:{id}` + email_sent=true (Resend mock 200)
   - invalid signature (wrong secret) → 400 `Invalid signature`, zero KV write
   - missing customer_email → 200 ack `warning: no_customer_email` (Stripe expects 200, no retry storm)
   - unknown tier (amount=12345) → 200 ack `warning: unknown_tier`, zero KV write
6. ✅ **`tests/refund.test.ts`** (3 test, mock Stripe + Resend):
   - happy path: purchase entro 30gg → Stripe API call (`stripeCalls=1`) → KV `purchase.refunded=true` + audit `refund:{email}` with stripe_refund_id/tier
   - already refunded: 409 `ALREADY_REFUNDED` + `stripeCalls=0` (anti double-refund critical)
   - outside 30d window (45gg): 410 `REFUND_WINDOW_EXPIRED` + `stripeCalls=0` + KV refunded=false unchanged
7. ✅ **`tests/activate-by-email.test.ts`** (2 test):
   - happy path Pro: BUYER@example.com (case insensitive) → activated=true + tier=pro + features.sara_expires_at=null + KV `activation:{email}` tracked
   - refunded block (regression S279): purchase.refunded=true → 410 `PURCHASE_REFUNDED` + no activation tracked
8. ✅ **`tests/phone-home.test.ts`** (4 test):
   - happy path Pro: status=ok, tier=pro, sara_enabled=true, days_remaining=null
   - Base trial first call: trial_started_at persistito in KV, days_remaining=30
   - **S279 gap fix coverage**: refunded=true (email mixed case `Refunded@Example.com` normalizzata) → status=revoked, tier=expired, sara_enabled=false, sara_days_remaining=0, cacheEntry.last_phone_home aggiornato (audit)
   - defensive: corrupt JSON `{not valid json` in KV → fall through a normal flow, no crash, status=ok

### Verify S279
- `npm test`: **13/13 PASS in 3.27s**
- `npx tsc --noEmit`: **0 errori** (TS strict)
- Files modified: `phone-home.ts` (+34 lines refund check), `package.json` (+vitest devDep + scripts), `tsconfig.json` (+ tests/), `vitest.config.ts` (NEW), `tests/_helpers.ts` (NEW), 4× `tests/*.test.ts` (NEW)

### Analisi critica strutturale (vincolo #4)

- **Assunzione**: vitest plain TS senza `@cloudflare/vitest-pool-workers` copre 100% logica handler perché route handlers Hono sono pure async functions del subset `{c.env, c.req.text/json/header, c.get/set, c.json}` — nessun runtime workerd richiesto. **Conferma**: 13/13 PASS validano l'assunzione.
- **Cosa rompe a 30gg**: se Worker aggiunge dipendenza da `caches.default` (CF runtime cache) o Durable Objects, mock object si rompe → migrazione miniflare3 necessaria. Probabilità bassa: il flow refund/license è pure-KV.
- **Pattern noto risk**: 2 KV vulnerabilities (high) in npm audit dopo vitest install — propagated devDep di vite/esbuild. NON shippato in production Worker (devDep only). Mitigation: `npm audit fix` on-demand future sessione.
- **Sovradimensione evitata**: skip integration test cross-route (webhook→activate→refund→phone-home chain). Quel test richiede miniflare3, lo lascio come carry-over founder/CI quando setup [env.test].

### Out of scope mantenuto S279

- **Deploy `--env test`** worker su CF (richiede `CLOUDFLARE_API_TOKEN` + `wrangler.toml [env.test]` block + namespace KV separato)
- **Stripe TEST sandbox**: webhook endpoint test, signing secret test, card 4242 full E2E
- **Resend test inbox** + magic-link manual click
- **Client Rust Tauri**: nessuna modifica a `license_ed25519.rs` / `license.rs` — `PhoneHomeResponse.status='revoked'` è già nel type union (`'ok'|'expired'|'revoked'|'invalid'`) ma il client Rust al momento NON ramifica su status=revoked. GAP CLIENT separato.
- **Voice live audio** (B-1): pipeline DOWN al boot S278, microfono fisico richiesto

---

## TASK candidati S280 (CTO discrezione, REGOLA #15)

### Track A — Client Rust handle `status='revoked'` (~2-3h, autonomous)
- `src-tauri/src/commands/license.rs`: aggiungere logica che, su risposta phone-home con `status='revoked'`, marca license_cache come `tier='expired' status='revoked'` localmente + blocca features (`is_feature_enabled` ritorna false su Sara/loyalty/whatsapp).
- Integration test Rust: simula HTTP response mock con `status='revoked'` → assert license_cache aggiornata + Sara bloccata.
- Completa il loop S279 lato CLIENT del gap-fix.
- Effort: 2-3h, 100% autonomous SSH+cargo.

### Track B — Setup CF Worker test env + Stripe E2E (~5-6h, founder-bottleneck)
- Founder fornisce: `CLOUDFLARE_API_TOKEN` env var + Stripe TEST sandbox keys (sk_test_, whsec_test_) + Resend test API key.
- CTO: aggiungere `[env.test]` block in `wrangler.toml` + KV namespace test separato + `wrangler deploy --env test` + Stripe Dashboard webhook endpoint TEST + curl POST checkout completed event (TEST card 4242) → verify chain (KV purchase scritto, email Resend test arrivata, magic link funziona, activate-by-email response 200).
- Effort: ~2h founder credentials/setup + ~3h CTO scripting + verify.

### Track C — B-1 Voice live audio test (~4h, Gate 1 critical, founder presence)
- Pipeline iMac UP (porta 3002 down al boot S278) + WAV reali 5 scenari + microfono fisico per loopback.
- Agent: `voice-tester` + `voice-engineer`.
- Effort: ~4h, parziale autonomous (WAV pre-registrati SSH OK), parte live richiede founder.

### Track D — Audit cargo fmt residual iMac + igiene repo
- Vecchie sessioni hanno lasciato residui fmt non flushati su iMac. Cargo fmt run + commit pulito.
- Effort: 30min, 100% autonomous.

---

## Vincoli S280

- **REGOLA #14**: CTO autonomous via SSH+cargo+npm. Founder solo CF/Stripe/Resend credentials + microfono live.
- **REGOLA #15**: NO A/B questions. CTO decide track + parte.
- **REGOLA #6**: NO `Co-Authored-By` trailer.
- **Context budget**: parti sotto 30% raw. File critici (lib.rs/migrations/wrangler.toml [env.test] schema) → BLOCK_CRITICAL ≥50% raw.

---

## PROMPT START S280

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md per stato S279 close + backlog.

REGOLA #15 attiva: decidi track autonomamente.

Track suggested: Track A (client Rust handle status='revoked' ~2-3h, 100% autonomous, chiude loop S279 gap-fix lato client). In subordine Track D (igiene 30min) o Track B se founder fornisce CF token + Stripe sandbox keys all'avvio.

REGOLA #14: backend-side autonomous via SSH+cargo. Founder solo override su pain operativo.
```

---

**Provenienza S279 close**: VERDE pieno. 13/13 test worker PASS in 3.27s. Gap sicurezza phone-home.ts refund check chiuso lato Worker. Carry-over founder ridotto a solo CF/Stripe/Resend credentials per deploy `--env test`. Commit S279 atomico in chiusura.
