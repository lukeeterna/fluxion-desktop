# Prompt ripartenza S299 — Brevo HTTP API key + REAL browser test FDQ-01 (META-VINCOLO REGOLA #18)

> ## ⛔ PRE-FLIGHT GIT-STATE CHECK (post-S298, ≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short` → `tools/VectCutAPI` submodule dirty (ignorabile)
> 2. `cd fluxion-proxy && npx vitest run` → MUST 36/36 PASS in <6s
> 3. `curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health` → `{"status":"ok"}`
> 4. `ls fluxion-proxy/migrations/0002_webhook_events_recovery_index.sql` → exists
> 5. `zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py'` → re-run smoke (~7s MUST 5/5)
>
> 5/5 PASS → S299 procede.

---

## Stato chiusura S298 (CLOSED VERDE — Tauri activate-by-payload smoke verified + D1 composite index + runbook extended)

### Done S298 (100% autonomous, zero founder touch)

1. **Pre-flight 5/5 PASS** smoke FDQ-01 idempotent re-run S297.
2. **Tauri activate-by-payload smoke E2E** (HIGH #3 prompt S298):
   - Estratto `license_payload` + `license_signature` da recovery URL S298 fresco (license_id `766a4ad4...`)
   - POST `/api/v1/verify` worker → **HTTP 200 `{"kid":"v1","valid":true}`** (WebCrypto verify side)
   - SSH iMac `cargo test --release --lib commands::license_ed25519_v1::tests` → **8/8 PASS** in 8m 21s (real_worker_signature_verifies_true + tamper + edge + Tauri command shape)
   - Interop dalek ↔ WebCrypto S291 confirmed transitively → payload S298 verifies dalek
3. **D1 migration 0002 composite index** (MED prompt S298):
   - NEW `fluxion-proxy/migrations/0002_webhook_events_recovery_index.sql`
   - `CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email_created_desc ON webhook_events(customer_email, created_at DESC)`
   - Applied test D1 remote (`wrangler d1 execute --remote`) — `changes:1, sql_duration:3.36ms`
   - **EXPLAIN QUERY PLAN verified**: `SEARCH webhook_events USING INDEX idx_webhook_events_customer_email_created_desc (customer_email=?)` — ordered seek, zero sort
4. **SUPPORT-RUNBOOK extended** (MED prompt S298):
   - `docs/SUPPORT-RUNBOOK.md` ISSUE B2 workaround section S298 update:
     - Replaced obsolete "founder genera key manuale" con S295/S296/S298 workflow
     - 4 sub-step: D1 row verify / replay email / recovery URL HMAC re-compute / activate-by-payload Rust verify
     - Reference files: `license-recovery.ts`, `checkout-success.ts`, `0002_*.sql`
5. **TS root + vitest baseline**: `npm run type-check` PASS (root tauri-app), `vitest 36/36 PASS` fluxion-proxy

### Files modificati S298

- **NEW**: `fluxion-proxy/migrations/0002_webhook_events_recovery_index.sql` (composite index)
- `docs/SUPPORT-RUNBOOK.md` (Edit B2 +50 righe S298 recovery workflow)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (S299 scope)

Fuori repo:
- D1 test schema: `idx_webhook_events_customer_email_created_desc` applied

### Critica strutturale S298 (REGOLA #4)

1. **Smoke synthetic ≠ REAL browser test (REGOLA #18 unmet)**: HIGH #3 verified via curl+worker+cargo, ma production_ready REGOLA #18 META-VINCOLO richiede founder real flow card 4242 + Stripe Checkout UI + redirect `/success/` + click "Copia link" recovery. CTO può fare TUTTO il restante autonomous, ma il bottone Stripe Checkout submit serve cliccato dal browser founder. Smoke synthetic copre code path 100%, NON UX path 100%.
2. **fluxion-proxy/tests/checkout-success.test.ts 4 TS errori pre-existing (S296)**: `ReadableStream<any> as string` cast pattern in mock — vitest runtime OK (36/36 PASS) ma `tsc --noEmit` fluxion-proxy fail. Pre-commit hook ROOT (tauri-app/) NON cattura — sub-package fluxion-proxy/ separato. Carry-over LOW: refactor mock cast `as unknown as string` o tipo `Response['body']` proper.
3. **Composite index idx_webhook_events_customer_email_created_desc redundancy con idx_webhook_events_customer_email single-column (0001)**: single retained intentionally (storage ~negligible, future-safe per query non-ordered). Cleanup possibile `DROP INDEX idx_webhook_events_customer_email` post-prod verified, ma rischio rollback ↗︎ ROI 0. Defer.
4. **Brevo migration deferred indefinitamente senza HTTP key founder**: smoke FDQ-01 conferma Resend sandbox funziona per `fluxion.gestionale@gmail.com` (account owner). Per PRODUCTION reale (clienti random), serve Brevo HTTP API o Resend custom domain (€10/anno DNS records). Decisione vendor strategica = founder choice, NON CTO autonomous.

### Pending S299 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Founder Brevo **HTTP v3 API key** (`xkeysib-...` prefix) | founder | Dashboard Brevo → Settings → **SMTP & API** → tab "**API Keys**" (NON "SMTP") → "Generate a new API key" → copia → TextEdit `/tmp/brevo_key.txt`. Pattern errore noto S297: founder ha inviato SMTP password (`xsmtpsib-...`) — assicurarsi tab "API Keys" in alto, NON "SMTP". |
| HIGH | CTO Brevo smoke test pre-upload | CTO | Post founder paste, CTO `GET https://api.brevo.com/v3/account` con Authorization `api-key: <KEY>` — MUST HTTP 200 (NON 401). Solo dopo → `wrangler secret put BREVO_API_KEY --env test`. |
| HIGH | CTO Brevo smoke email + re-deploy | CTO | POST `/v3/smtp/email` sender `noreply@<auto-subdomain>.brevosend.com` (verify dashboard) o fallback `fluxion.gestionale@gmail.com` signup-verified. Recipient `fluxion.gestionale@gmail.com` → check delivery. Re-deploy worker test. Re-run smoke FDQ-01 → verify email channel switch Resend→Brevo (Resend log non incrementa). |
| HIGH | **META-VINCOLO REGOLA #18 production gate** — founder REAL browser test | CTO + founder GO | Founder: https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000 (Base Payment Link S297) → coupon test 100% (es. `dcwmOPFa`) → card `4242 4242 4242 4242` 12/30 CVC 123 → email `fluxion.gestionale@gmail.com` → submit → redirect a `/success/cs_test_xxx`. Verifiche: (a) HTML inline payload+sig+recovery, (b) email Gmail inbox subject "FLUXION — Il tuo ordine è confermato!", (c) click "Copia link" recovery → JSON ok. CTO: assist via `wrangler tail --env test` + D1 query post-test. |
| MED | CTO `sender.ts` Brevo swap (sequenza F-3 post-purchase) | CTO | Email sequence non-bloccante, stesso pattern stripe-webhook S296. Code-ready post BREVO_API_KEY upload. |
| MED | Fix tests/checkout-success.test.ts TS cast errori | CTO | 4 errori `ReadableStream<any> as string` → `as unknown as string`. ~5min. Defer se Brevo prioritario. |
| LOW | KV cleanup test entries | CTO | `wrangler kv key list --binding LICENSE_CACHE --env test` + delete `purchase:test+*`, `session:cs_test_smoke_*`. |
| LOW | D1 cleanup test rows | CTO | `wrangler d1 execute fluxion-webhook-events-test --env test --remote --command "DELETE FROM webhook_events WHERE session_id LIKE 'cs_test_smoke_%'"`. |
| LOW | `/api/v1/verify` debug endpoint cleanup | CTO | Post Tauri activate-by-payload PROD verified: rimuovere route OR add `Bearer ADMIN_API_SECRET`. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur. |

### Vincoli S299 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: Brevo `xkeysib-` HTTP API testato `GET /v3/account` PRIMA di `wrangler secret put`. NO assumption.
- **REGOLA #14/#15/#16 CTO autonomous**: smoke + verify in autonomia, founder gate solo creazione Brevo HTTP key + REAL browser test FDQ-01.
- **REGOLA #18 META-VINCOLO**: production_ready NON declaration senza founder browser test reale (smoke synthetic NON conta — S298 confirma code path 100% OK, UX path needs founder).
- **CLOSING_ONLY ≥70%**: monitor `/context` ogni 5 tool call.

### Pre-flight S299 (≤30s)

```bash
# 1. Env vars
zsh -c 'source ~/.claude/.env 2>/dev/null
for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'

# 2. Worker test health + new endpoint check
curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health
curl -sS -X POST https://fluxion-proxy-test.gianlucanewtech.workers.dev/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"payload":"test","signature_base64":"AAAA","kid":"v1"}'  # expect kid:v1 valid:false (ok)

# 3. Smoke re-run + D1 composite index verify
cd /Volumes/MontereyT7/FLUXION
zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py' | tail -15
zsh -c 'source ~/.claude/.env; export CLOUDFLARE_API_TOKEN
cd fluxion-proxy && npx wrangler d1 execute fluxion-webhook-events-test --env test --remote \
  --command "EXPLAIN QUERY PLAN SELECT license_id FROM webhook_events WHERE customer_email=? ORDER BY created_at DESC LIMIT 1;"' 2>&1 | grep -i "using index"

# 4. TS + vitest baseline
cd fluxion-proxy && npx vitest run 2>&1 | tail -5  # expect 36/36 PASS
```

### Carry-over backlog (defer post-S299)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** card `4000002500003155` real browser founder
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** (S289 HIGH, S298 partial via smoke — S299 close su founder browser test)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** + **BUG-FATT-5** toast z-index
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** (S286 founder brand-guardian + visual-storyteller)
- **landing CF Pages re-deploy** post-FBUG-LM-01 S287
- **Resend custom domain** (€10/anno + DNS records) — alternativa a Brevo
- **Migrazione legacy NODE-ED25519 → Ed25519 standard** S291 carry-over
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...`
- **pre_write_gate.py refactor**: regex whole-word + escludere `.test.ts`/`.spec.ts`

### Tabella anelli chain post-S298

| Ring | Stato | Evidence S298 |
|------|-------|---------------|
| 1 landing→signup | VERIFIED (S287) | curl POST /api/v1/lead-magnet + KV lead row |
| 2 checkout_stripe | VERIFIED (S285) | Stripe session + Payment Link API |
| 3 pagamento_confermato | VERIFIED (S285) | Stripe event evt_xxx + KV purchase row |
| 4 licenza_generata | VERIFIED test smoke (S297) | Synthetic webhook → license_id Ed25519 signed D1 |
| 5 email_consegna | VERIFIED test smoke (S297) | Resend `last_event:delivered` 2 email (Brevo PROD gate carry-over) |
| 6 attivazione_app | **VERIFIED smoke S298 + S289 founder GUI** | Tauri verify_license_signature_v1 dalek 8/8 PASS + worker /api/v1/verify valid:true payload S298 fresco — prod gate REGOLA #18 pending founder REAL browser test |
| 7 sales_agent_wa | MISSING (Phase 12) |

**production_ready_PROD = FALSE** (REGOLA #18 META-VINCOLO: smoke synthetic ≠ real browser test). S299 chiude su prod gate dopo founder REAL browser test + Brevo HTTP key upload.

Ripartenza S299 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267).
