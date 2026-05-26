# Prompt ripartenza S298 — Brevo HTTP API key + production gate META-VINCOLO + Tauri activate-by-payload

> ## ⛔ PRE-FLIGHT GIT-STATE CHECK (post-compact S297, ≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short` → `tools/VectCutAPI` submodule dirty (ignorabile) + eventuali nuovi file
> 2. `cd fluxion-proxy && npx vitest run` → MUST 36/36 PASS in <6s
> 3. `curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health` → `{"status":"ok"}`
> 4. `ls fluxion-proxy/tests/scripts/smoke_fdq01.py` → exists (5827 byte exec)
> 5. `zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py'` → re-run smoke FDQ-01 (~7s, MUST PASS 5/5)
>
> 5/5 PASS → S298 procede. Smoke script idempotente, ogni run crea synthetic session diverso.

---

## Stato chiusura S297 (CLOSED VERDE — smoke FDQ-01 + FSAF-05 PASS autonomous CTO)

### Done S297 (100% autonomous, zero founder touch)

1. **Pre-flight 4/4 PASS** (drift summary→git conservativo: S296 code era già in commit `cfc5674` auto-close).
2. **LICENSE_RECOVERY_SECRET uploaded** a Worker test (`wrangler secret put` via stdin, no echo).
3. **Worker test deployed**: `Version 31eb2811-ded1-496c-afb3-ae8f68c93e18`. Tutte 4 secrets correttamente bound + 3 nuove route registrate.
4. **Routes verify**:
   - ✅ `/health` 200 OK
   - ✅ `/api/v1/license/:email` 400 no token / 403 invalid token (no info leak)
   - ✅ `/success/:session_id` 200 HTML pending page (D1 empty → meta-refresh 5s)
5. **Stripe Payment Links updated via API** (CTO autonomous con STRIPE_TEST_SECRET_KEY):
   - `plink_1TRrGqIW4bHDTsaHeX8g37gD` Base €497 → `after_completion.redirect.url=/success/{CHECKOUT_SESSION_ID}` ✅
   - `plink_1TRrGrIW4bHDTsaH1KwXKrUJ` Pro €897 → idem ✅
6. **Brevo key Luke incollata in TextEdit `/tmp/brevo_key.txt`** = ❌ **SMTP password** `xsmtpsib-...` (90 byte), NON HTTP v3 API key. Test diretto `GET /v3/account` → **HTTP 401 "Key not found"**. File `rm -P` securizzato.
7. **Decisione CTO autonomous**: defer Brevo migration → smoke FDQ-01 con Resend esistente (`RESEND_API_KEY` già bound, sender `onboarding@resend.dev`, destinatario `fluxion.gestionale@gmail.com` = Resend account owner, funziona in sandbox).
8. **Smoke FDQ-01 PASS E2E** via `fluxion-proxy/tests/scripts/smoke_fdq01.py` (CTO autonomous, zero browser, zero founder):
   - Step 1: synthetic `checkout.session.completed` event firmato HMAC-SHA256 con `STRIPE_WEBHOOK_SECRET_TEST` → POST `/api/v1/webhook/stripe` → **HTTP 200** `email_sent:true license_id=ebaa54b5...`
   - Step 2: GET `/success/cs_test_smoke_S297_xxx` → **HTTP 200** 6370 byte HTML con `payload-data` + `signature-data` + `recovery-url` div inline
   - Step 3: GET recovery URL → **HTTP 200 JSON** `{license_id, tier, license_payload, license_signature}` (match HTML modulo HTML-escape)
   - Step 4: POST webhook REPLAY (stesso event_id) → **HTTP 200** `idempotent_replay:true email_resent:false` ✅ **FSAF-05 verified**
9. **Resend delivery confirmed** via `GET https://api.resend.com/emails`:
   - 18:00:33 UTC primo smoke → `last_event:delivered`
   - 18:01:02 UTC replay → `last_event:delivered` (idempotent path NON re-send, ma stesso payload from D1 row)
   - Subject: "FLUXION — Il tuo ordine è confermato!"
   - From: `FLUXION <onboarding@resend.dev>` (Resend sandbox default)
10. **Smoke script persistito**: `fluxion-proxy/tests/scripts/smoke_fdq01.py` (5827 byte exec) idempotent re-runnable.

### Files modificati S297

- **NEW**: `fluxion-proxy/tests/scripts/smoke_fdq01.py` (5827 byte exec, smoke FDQ-01 + FSAF-05)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (S298 scope)

Fuori repo:
- Worker test deploy `Version 31eb2811`
- Worker test secret `LICENSE_RECOVERY_SECRET` uploaded
- Stripe Payment Links Base+Pro updated to redirect
- `/tmp/brevo_key.txt` `rm -P` (secure wipe)

### Critica strutturale S297 (REGOLA #4)

1. **Brevo SMTP password ≠ v3 API key**: assunzione iniziale (incolla qualunque cosa da Brevo dashboard) non verificata. Pattern errore noto: prefix conventions vendor-specific (Stripe `sk_test_/pk_test_/whsec_`, Brevo `xkeysib_/xsmtpsib_`, Resend `re_`). S298 fix: chiedere a Luke **path esatto** in Brevo dashboard ("Settings → SMTP & API → tab **API Keys** in alto → bottone **Generate a new API key**" — NON "SMTP" tab).
2. **Resend sandbox limit non bloccante per smoke test**: destinatario test = account owner = OK. Per **PRODUCTION** (real customer email ≠ owner), Resend richiede custom domain verified (es. `fluxion-app.com` €10/anno, S286 backlog). Brevo path = zero-cost 300/giorno qualsiasi destinatario, MA serve HTTP API key corretta (gate founder).
3. **Synthetic webhook vs real Stripe Checkout**: smoke script firma manualmente con `STRIPE_WEBHOOK_SECRET_TEST` — questo testa il code path completo (verify signature → D1 write → email send → success page → recovery URL) MA NON esercita: (a) Stripe Checkout UI flow (card 4242 input), (b) Stripe SDK retry su 5xx, (c) browser cookie/storage. Per **production gate REGOLA #18**, smoke synthetic NON sufficiente — serve UNO test reale founder con Payment Link + card 4242 + coupon 100% in browser, end-to-end.
4. **Stripe Payment Link redirect = breaking change UX**: prima `hosted_confirmation` (Stripe default page "Thanks for your purchase"), ora `redirect` a `/success/{id}` (FLUXION custom page). Se `/success` route fail (404, 500, slow CF cold start), founder vede error page invece di "thanks". Mitigation: success page S296 ha pending state meta-refresh 5s se D1 row missing (gestisce race webhook-vs-redirect).

### Pending S298 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Founder Brevo **HTTP v3 API key** (`xkeysib-...` prefix) | founder | Dashboard Brevo → Settings → **SMTP & API** → tab "**API Keys**" (NON "SMTP") → "Generate a new API key" → copia → TextEdit `/tmp/brevo_key.txt` (CTO apre file con `touch + open -a TextEdit`). |
| HIGH | CTO `wrangler secret put BREVO_API_KEY --env test` | CTO | Post founder paste, verify prefix `xkeysib-` + test `GET /v3/account` HTTP 200 PRIMA di upload. |
| HIGH | CTO Brevo smoke email test | CTO | POST `/v3/smtp/email` con sender `noreply@<auto-subdomain>.brevosend.com` (verify via dashboard) o fallback `fluxion.gestionale@gmail.com` verified signup. Recipient = `fluxion.gestionale@gmail.com` → verifica delivery Resend-equivalent. |
| HIGH | CTO re-deploy worker test (Brevo active) | CTO | Post BREVO_API_KEY upload → re-deploy → re-run smoke `tests/scripts/smoke_fdq01.py` → verify email channel = Brevo (Resend log non incrementa) via `RESEND_API_KEY` unset trick or branch check. |
| HIGH | **META-VINCOLO REGOLA #18 production gate** — founder REAL browser test | CTO + founder GO | Founder: apri https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000 (Base Payment Link) → coupon test 100% → card `4242 4242 4242 4242` 12/30 CVC 123 → email `fluxion.gestionale@gmail.com` → submit → Stripe redirect a `/success/cs_test_xxx` → verify HTML inline + email Gmail inbox + click "Copia link" recovery. CTO: assist via Resend log + D1 query post-test. |
| HIGH | Tauri **activate-by-payload** FE smoke | CTO | Extract `license_payload` + `license_signature` da success page del test founder → simulate `invoke('verify_license_signature_v1', {payload, signature})` via debug endpoint or temporary Rust test on iMac → MUST return `{valid: true, license_id, tier}`. Backlog BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519 (S289 HIGH). |
| MED | CTO D1 index migration 017 | CTO | `CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email ON webhook_events(customer_email, created_at DESC)`. Apply test + prod. |
| MED | CTO `sender.ts` Brevo swap (sequenza F-3 post-purchase) | CTO | Email sequence non-bloccante, stesso pattern stripe-webhook swap. |
| MED | CTO docs support runbook | CTO | `docs/SUPPORT-RUNBOOK.md` sezione "Cliente perso recovery link" → query D1 + re-compute HMAC + invio manuale. |
| LOW | KV cleanup test entries | CTO | `wrangler kv key list --binding LICENSE_CACHE --env test` + delete `purchase:test+*`, `session:cs_test_smoke_*`. |
| LOW | D1 cleanup test rows | CTO | `wrangler d1 execute fluxion-webhook-events-test --command "DELETE FROM webhook_events WHERE session_id LIKE 'cs_test_smoke_%'"`. |
| LOW | `/api/v1/verify` debug endpoint cleanup | CTO | Post Tauri activate-by-payload verified: rimuovere route OR add `Bearer ADMIN_API_SECRET`. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur. |

### Vincoli S298 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: Brevo `xkeysib-` HTTP API testato `GET /v3/account` PRIMA di `wrangler secret put`. NO assumption.
- **REGOLA #14/#15/#16 CTO autonomous**: smoke + verify in autonomia, founder gate solo creazione Brevo HTTP key + REAL browser test FDQ-01.
- **REGOLA #18 META-VINCOLO**: production_ready NON declaration senza founder browser test reale (smoke synthetic NON conta).
- **CLOSING_ONLY ≥70%**: monitor `/context` ogni 5 tool call.

### Pre-flight S298 (≤30s)

```bash
# 1. Env vars + recovery secret backup
zsh -c 'source ~/.claude/.env 2>/dev/null
for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'

# 2. Worker test health + routes
curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health
curl -sS -o /dev/null -w "HTTP %{http_code}\n" https://fluxion-proxy-test.gianlucanewtech.workers.dev/success/cs_test_nonexistent

# 3. Smoke re-run (idempotent)
cd /Volumes/MontereyT7/FLUXION
zsh -c 'source ~/.claude/.env; export STRIPE_WEBHOOK_SECRET_TEST; python3 fluxion-proxy/tests/scripts/smoke_fdq01.py' | tail -15

# 4. TS + vitest baseline
cd fluxion-proxy && npx tsc --noEmit && echo "TS PASS"
npx vitest run 2>&1 | tail -5  # expect 36/36 PASS
```

### Carry-over backlog (defer post-S298)

- **Brevo HTTP API key** (xkeysib-) post founder
- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** card `4000002500003155` real browser founder
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** (S289 HIGH, S298 partial via smoke)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** + **BUG-FATT-5** toast z-index
- **Track E** migration 017 license_revoked status enum (parziale: idx customer_email S298)
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** (S286 founder brand-guardian + visual-storyteller)
- **landing CF Pages re-deploy** post-FBUG-LM-01 S287
- **Resend custom domain** (€10/anno + DNS records) — alternativa a Brevo se founder preferisce single-vendor
- **Migrazione legacy NODE-ED25519 → Ed25519 standard** S291 carry-over
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...`
- **pre_write_gate.py refactor**: regex whole-word + escludere `.test.ts`/`.spec.ts`

### Tabella anelli chain post-S297

| Ring | Stato | Evidence S297 |
|------|-------|---------------|
| 1 landing→signup | VERIFIED (S287) | curl POST /api/v1/lead-magnet + KV lead row |
| 2 checkout_stripe | VERIFIED (S285) | Stripe session + Payment Link API |
| 3 pagamento_confermato | VERIFIED (S285) | Stripe event evt_xxx + KV purchase row |
| 4 licenza_generata | **VERIFIED test smoke S297** | Synthetic webhook → license_id Ed25519 signed in D1 |
| 5 email_consegna | **VERIFIED test smoke S297** | Resend `last_event:delivered` 2 email |
| 6 attivazione_app | VERIFIED test (S289 founder GUI) — prod gate pending Tauri activate-by-payload S298 |
| 7 sales_agent_wa | MISSING (Phase 12) |

**production_ready_PROD = FALSE** (gate REGOLA #18 META-VINCOLO: smoke synthetic ≠ real browser test). S298 chiude su prod gate dopo founder REAL browser test.

Ripartenza S298 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267).
