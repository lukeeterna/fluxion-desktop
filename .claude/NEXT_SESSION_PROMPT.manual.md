# Prompt ripartenza S300 — Brevo HTTP API key + REAL browser test FDQ-01 (META-VINCOLO REGOLA #18) + CF Pages re-deploy

> ## ⛔ PRE-FLIGHT GIT-STATE CHECK (post-S299, ≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short` → `tools/VectCutAPI` submodule dirty (ignorabile)
> 2. `cd fluxion-proxy && npx tsc --noEmit` → MUST 0 errors (S299 fix 4 cast)
> 3. `cd fluxion-proxy && npx vitest run` → MUST 36/36 PASS in <6s
> 4. `curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health` → `{"status":"ok"}`
> 5. `zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py'` → re-run smoke (~7s MUST 5/5)
>
> 5/5 PASS → S300 procede.

---

## Stato chiusura S299 (CLOSED VERDE — sender.ts Brevo swap + TS cast fix + KV/D1 cleanup, founder gate residuo HIGH x2)

### Done S299 (100% autonomous, zero founder touch)

1. **Pre-flight 5/5 PASS** (git, vitest 36/36, worker health, migration 0002 exists, smoke FDQ-01 idempotent)
2. **MED `checkout-success.test.ts` TS cast fix** (S298 carry-over):
   - 4 occorrenze `res.body as string` → `res.body as unknown as string`
   - tsc 0 errori fluxion-proxy
3. **MED `sender.ts` Brevo swap completo** (pattern S296 stripe-webhook):
   - NEW `sendViaBrevo` + `sendViaResend` private functions
   - `sendRaw` orchestrator gradual rollout (Brevo primary if `BREVO_API_KEY`, Resend fallback, NO_PROVIDER warn)
   - `SendEmailResult` esteso: `provider`+`providerMessageId` (rename da legacy `resendId`)
   - Consumer `admin-email-test.ts` updated (`provider`+`provider_message_id` JSON response)
   - vitest 36/36 PASS post-refactor
4. **LOW KV cleanup**: deleted `purchase:test+s285@example.com` (obsolete S285 test entry)
5. **LOW D1 cleanup**: `DELETE FROM webhook_events WHERE session_id LIKE 'cs_test_smoke_%'` → 5 righe deleted (4 cs_test_smoke + 1 timestamp shifted)
6. **LOW smoke FDQ-01 re-run post cleanup**: 5/5 PASS — nuovo `cs_test_smoke_S297_1779820952` con `license_id` Ed25519 fresh
7. **LOW EXPLAIN INDEX verify D1**: `SEARCH webhook_events USING INDEX idx_webhook_events_customer_email_created_desc (customer_email=?)` — ordered seek confirmed

### Files modificati S299 (catturati auto-close `afb35d3`)

- `fluxion-proxy/src/email/sender.ts` (+98 righe Brevo swap)
- `fluxion-proxy/src/routes/admin-email-test.ts` (+3 -1 provider fields)
- `fluxion-proxy/tests/checkout-success.test.ts` (4 cast fix)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (S300 scope)

Fuori repo:
- KV test entry purged
- D1 5 smoke rows purged → 1 fresh smoke row recreated

### Investigazioni S299 non-eseguite (deferred founder GO)

1. **NODE-ED25519 → standard Ed25519 migration** (S291 carry-over):
   - `auth.ts:7,64` import + caller `verifyEd25519` legacy → `lib/ed25519.ts` algo `NODE-ED25519` Workers extension
   - `ed25519-sign.ts` S291 ha già standard `Ed25519` algo per `/api/v1/verify` endpoint (dalek interop OK)
   - KV `lic:*` count PROD=0, TEST=0 (cache volatile 24h TTL, NON proof zero-usage)
   - Migration richiede: rotation `ED25519_PUBLIC_KEY` secret + refactor `auth.ts` + ri-firma eventuali license file-based legacy
   - **REGOLA #18 META-VINCOLO**: architectural change senza founder GO → deferred S301+
2. **landing CF Pages re-deploy FBUG-LM-01** (S287 carry-over):
   - Repo: `landing/index.html:2468` fix `consenso_marketing` PRESENT
   - Live `https://fluxion-landing.pages.dev/`: serve ancora VECCHIO `marketing_opt_in` → auto-deploy git push NOT configured
   - `wrangler pages deploy` fail: **token `CLOUDFLARE_API_TOKEN` manca permission `Pages:Edit`**
   - **Founder action**: extend CF API token con `Account/Cloudflare Pages:Edit` su https://dash.cloudflare.com/profile/api-tokens (1min) → CTO `wrangler pages deploy landing/ --project-name fluxion-landing`

### Critica strutturale S299 (REGOLA #4)

1. **Brevo swap untestato runtime senza HTTP key**: `sender.ts` Brevo gradual rollout code-ready, unit tests 36/36 PASS, ma runtime path `sendViaBrevo` MAI invocato (BREVO_API_KEY unset). Carry-over S300 smoke email seq F-3 + Brevo `GET /v3/account` 200 check obbligatorio post upload key.
2. **Naming refactor `resendId` → `providerMessageId` breaking change**: solo 1 consumer interno (`admin-email-test.ts`) aggiornato. Se in futuro nuovi consumer leggono response JSON `resend_id` field (es. monitoring dashboard), break silenzioso. Mitigation: documentare in `docs/SUPPORT-RUNBOOK.md` schema response cambiato S299. Defer (LOW).
3. **CF Pages re-deploy gap = 3 giorni** (S287 fix 23-mag → S299 26-mag): durante questa finestra ogni form submit landing UI ha portato `consenso_marketing=false` (gap compliance GDPR follow-up commerciale). Mitigation: post re-deploy S300, audit KV `lead:*` con `sequence_step=0 AND consent_text=''` per identify lead pre-fix → eventuale opt-in retro-attivo via E1 follow-up email.
4. **D1 cleanup smoke ha rimosso anche row recovery URL S298 reference**: license_id `766a4ad4...` (smoke S298) deleted in S299. Reference NEXT_SESSION_PROMPT S299 menzionava quel payload per Tauri verify test. Mitigation: ri-eseguire smoke FDQ-01 S300 + estrarre nuovo payload se needed. Impact zero (test deterministico ripetibile).

### Pending S300 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Founder Brevo **HTTP v3 API key** (`xkeysib-...` prefix) | founder | Dashboard Brevo → Settings → **SMTP & API** → tab "**API Keys**" (NON "SMTP") → "Generate a new API key" → copia → TextEdit `/tmp/brevo_key.txt`. Pattern errore noto S297: founder ha inviato SMTP password (`xsmtpsib-...`) — assicurarsi tab "API Keys" in alto, NON "SMTP". |
| HIGH | CTO Brevo smoke test pre-upload | CTO | Post founder paste: `curl -H "api-key: <KEY>" https://api.brevo.com/v3/account` → MUST HTTP 200 (NON 401). Solo dopo → `wrangler secret put BREVO_API_KEY --env test`. |
| HIGH | CTO Brevo smoke email + re-deploy + re-run smoke FDQ-01 | CTO | POST `/v3/smtp/email` sender `noreply@<auto-subdomain>.brevosend.com` (verify dashboard) o fallback `fluxion.gestionale@gmail.com` signup-verified. Recipient `fluxion.gestionale@gmail.com` → check delivery. Re-deploy worker test. Re-run smoke FDQ-01 → verify email channel switch Resend→Brevo (Resend log non incrementa). |
| HIGH | Founder CF API token extension Pages:Edit | founder | Dashboard CF → My Profile → API Tokens → edit token corrente → permission `Account/Cloudflare Pages:Edit` → Save. ~1min. |
| HIGH | CTO landing CF Pages re-deploy FBUG-LM-01 | CTO | `cd landing && npx wrangler pages deploy . --project-name fluxion-landing --commit-dirty=true --branch main` → verify https://fluxion-landing.pages.dev/ contiene `consenso_marketing` (NON `marketing_opt_in`). |
| HIGH | **META-VINCOLO REGOLA #18 production gate** — founder REAL browser test | CTO + founder GO | Founder: https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000 (Base Payment Link S297) → coupon test 100% (es. `dcwmOPFa`) → card `4242 4242 4242 4242` 12/30 CVC 123 → email `fluxion.gestionale@gmail.com` → submit → redirect a `/success/cs_test_xxx`. Verifiche: (a) HTML inline payload+sig+recovery, (b) email Gmail inbox subject "FLUXION — Il tuo ordine è confermato!", (c) click "Copia link" recovery → JSON ok. CTO: assist via `wrangler tail --env test` + D1 query post-test. |
| MED | KV lead audit pre/post FBUG-LM-01 | CTO | Post CF Pages re-deploy: `wrangler kv key list --binding LEAD_MAGNET_KV` (binding name TBD) → identify `lead:*` con `consent_text=''` → ROI compliance retro-fit opt-in. |
| LOW | `/api/v1/verify` debug endpoint cleanup | CTO | Post Tauri activate-by-payload PROD verified: rimuovere route OR add `Bearer ADMIN_API_SECRET`. |
| LOW | Doc `SUPPORT-RUNBOOK.md` schema response `provider`+`provider_message_id` rename | CTO | 5min. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur. |

### Vincoli S300 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: Brevo `xkeysib-` HTTP API testato `GET /v3/account` PRIMA di `wrangler secret put`. NO assumption.
- **REGOLA #14/#15/#16 CTO autonomous**: smoke + verify in autonomia, founder gate solo creazione Brevo HTTP key + CF Pages:Edit token + REAL browser test FDQ-01.
- **REGOLA #18 META-VINCOLO**: production_ready NON declaration senza founder browser test reale (smoke synthetic NON conta — S298 confirma code path 100% OK, UX path needs founder).
- **CLOSING_ONLY ≥70%**: monitor `/context` ogni 5 tool call.

### Pre-flight S300 (≤30s)

```bash
# 1. Env vars
zsh -c 'source ~/.claude/.env 2>/dev/null
for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'

# 2. Worker test health + TS + vitest baseline
curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy && npx tsc --noEmit && echo "TSC OK"
npx vitest run 2>&1 | tail -5  # expect 36/36 PASS

# 3. Smoke re-run + D1 composite index verify
cd /Volumes/MontereyT7/FLUXION
zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py' | tail -15

# 4. Landing prod state verify (post-deploy gate)
curl -sS https://fluxion-landing.pages.dev/ | grep -c "consenso_marketing\|marketing_opt_in"
# expect: 1 match consenso_marketing post-deploy, currently still marketing_opt_in
```

### Carry-over backlog (defer post-S300)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** card `4000002500003155` real browser founder
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** (S289 HIGH, S298 partial via smoke — S300 close su founder browser test)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** + **BUG-FATT-5** toast z-index (deferred S267, NO tracking detail trovato S299)
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** (S286 founder brand-guardian + visual-storyteller)
- **Resend custom domain** (€10/anno + DNS records) — alternativa a Brevo
- **NODE-ED25519 → Ed25519 standard migration** (S291 carry-over, S299 investigato: REGOLA #18 META-VINCOLO founder GO required, auth.ts:7,64 unique caller, PROD KV `lic:*`=0)
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...`
- **pre_write_gate.py refactor**: regex whole-word + escludere `.test.ts`/`.spec.ts` (S296 lesson, hook NOT trovato in `~/.claude/hooks/` S299 — path TBD)

### Tabella anelli chain post-S299

| Ring | Stato | Evidence |
|------|-------|----------|
| 1 landing→signup | VERIFIED (S287) backend, **broken UI** (FBUG-LM-01 deploy gap S299) | curl POST /api/v1/lead-magnet OK + KV lead row OK / UI form `marketing_opt_in` MISMATCH |
| 2 checkout_stripe | VERIFIED (S285) | Stripe session + Payment Link API |
| 3 pagamento_confermato | VERIFIED (S285) | Stripe event evt_xxx + KV purchase row |
| 4 licenza_generata | VERIFIED test smoke (S299) | Synthetic webhook → license_id Ed25519 signed D1 |
| 5 email_consegna | VERIFIED test smoke Resend (S297) | Brevo PROD gate S300 (HTTP key + smoke email) |
| 6 attivazione_app | **VERIFIED smoke S298 + S289 founder GUI** | Tauri verify_license_signature_v1 dalek 8/8 PASS + worker /api/v1/verify valid:true — prod gate REGOLA #18 pending founder REAL browser test |
| 7 sales_agent_wa | MISSING (Phase 12) |

**production_ready_PROD = FALSE** (REGOLA #18 META-VINCOLO: smoke synthetic ≠ real browser test + landing UI FBUG-LM-01 deploy gap). S300 chiude su prod gate dopo: Brevo HTTP key + CF Pages:Edit token + CTO re-deploy + founder REAL browser test.

Ripartenza S300 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267).
