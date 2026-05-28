# Prompt ripartenza S308 — Founder action Cloudflare Registrar fluxion-app.com + Resend domain verify + S307 fix promote

> ## ⚡ S307 OUTCOME (CLOSED ROSSO STRUTTURALE, CTO autonomous smoke ha rivelato production blocker)
>
> **Done S307 (CTO autonomous, NO founder bound)**:
> - Pre-flight 5/5 PASS (git+env+/health 200+VOS gate verde+RESEND_API_KEY secret presente)
> - Task A inbox verify bypass via Resend API GET /emails/58cf5601 → `last_event: delivered` ✅ (delivery confermato infra, folder placement opaco)
> - Task B method 1 (replay evt_1TbjH6 esistente) → idempotent_replay no-op (atteso, codepath idempotency OK)
> - Task B method 2 (stripe trigger FRESH checkout.session.completed) → webhook 200 + Resend **403 validation_error**: "You can only send testing emails to your own email address... To send emails to other recipients, please verify a domain at resend.com/domains"
> - Resend domains list = VUOTO → conferma sender `onboarding@resend.dev` test-mode restricted to account-owner
> - **FBUG-RESEND-SHARED-SENDER-01 identificato**: S306 fix Brevo→Resend con shared sender NON funziona per produzione (customer.email !== owner email)
> - Resend domain `fluxion-app.com` PRE-PROVISIONATO pending verification: id `6f986180-2eaf-41e2-8a40-53ebeefedbf0`, region `eu-west-1`, status `not_started`, 3 DNS records ottenuti
>
> **Evidence file**: `~/venture-os/state/fdq-01-smoke-S307.json` con: bug ID + 3 fonti validation + DNS records target + founder action checklist
>
> **Critica strutturale S307 (REGOLA #4)**:
> 1. Assunzione S306 nascosta: tandem research + WebSearch May 2026 confermato Resend free tier MA generalizzato "onboarding@resend.dev works for all recipients" → FALSO empirico
> 2. Pattern critique-then-ignore confermato 4x (S296→S303→S305→S306→S307): ogni email provider swap necessita smoke con destinatari NON-owner PRE production claim
> 3. Bias confirmation: smoke S306 admin/email-sequence/preview era owner→owner, non testa non-owner path
> 4. Costo non-fix: prima vendita reale day 1 = customer no email = refund/support storm
>
> **Task C PROMOSSO** da `deferred post-CLOSED_WON` → `REQUIRED IMMEDIATE PRE-LAUNCH` (production blocker)
>
> ## ⛔ PRE-FLIGHT S308 (≤45s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short && git log --oneline -3`
> 2. `source ~/.claude/.env`
> 3. **Worker test /health 200**:
>    ```bash
>    curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
>    ```
> 4. **Resend domain status check**:
>    ```bash
>    source ~/.claude/.env && curl -sS https://api.resend.com/domains/6f986180-2eaf-41e2-8a40-53ebeefedbf0 \
>      -H "Authorization: Bearer ${RESEND_TEST_KEY}" | python3 -m json.tool
>    ```
>    Expect post-founder-DNS-config: `status: "verified"` (initially `not_started`)
> 5. **VOS gate state**:
>    ```bash
>    python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
>    ```
>
> ## SCOPE S308
>
> ### Task A — Founder action Cloudflare Registrar (FIRST, FOUNDER-BOUND, ~€10/anno)
>
> Founder Luke:
> 1. Vai a `https://dash.cloudflare.com/?to=/:account/domains/register/fluxion-app.com`
> 2. Verify disponibilità `fluxion-app.com` (.com Cloudflare wholesale ~$10.46/anno)
> 3. Checkout — persona fisica OK (NO P.IVA required), payment method founder
> 4. Post-registration: dominio appare in CF account zones
>
> **CTO verify post**:
> ```bash
> source ~/.claude/.env && curl -sS "https://api.cloudflare.com/client/v4/zones?account.id=${CF_ACCOUNT_ID}&name=fluxion-app.com" \
>   -H "Authorization: Bearer ${CF_API_TOKEN}" | python3 -m json.tool
> ```
>
> ### Task B — Founder action CF DNS records (post Task A, ~5min)
>
> Founder Luke aggiunge 3 records DNS a `fluxion-app.com` zone (CF DNS panel):
>
> | Type | Name | Value | Priority | TTL | Proxy |
> |------|------|-------|----------|-----|-------|
> | TXT | `resend._domainkey` | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDqkHv6sGk1C7n0J/Yau0YrcGbM4PifQBtmX1HmCSvr7IsyXk8Ui1GY5qPrgRC+CKInBH2+ArTt6BU7jTVcNrNQ8nn+Ni0hWOu54sGaRFPy1k2qW8bjgU/CYhVefbVQrOBUnsI/1vV3q4z7xH7CWojWo4uKQ5SXQkj7njqecFWFvwIDAQAB` | — | Auto | DNS only |
> | MX | `send` | `feedback-smtp.eu-west-1.amazonses.com` | 10 | Auto | DNS only |
> | TXT | `send` | `v=spf1 include:amazonses.com ~all` | — | Auto | DNS only |
>
> Bonus (consigliato post-verify):
>
> | TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:fluxion.gestionale@gmail.com` | — | Auto | DNS only |
>
> **NOTA**: NO proxy CF (record DNS only). Wait propagation 15min-2h.
>
> ### Task C — CTO autonomous verify Resend + code promote (post Task B propagated)
>
> 1. Trigger Resend domain verification:
>    ```bash
>    source ~/.claude/.env && curl -sS -X POST https://api.resend.com/domains/6f986180-2eaf-41e2-8a40-53ebeefedbf0/verify \
>      -H "Authorization: Bearer ${RESEND_TEST_KEY}" -w "\nHTTP=%{http_code}\n"
>    ```
>    Expect `status: "verified"` (DKIM+SPF green) — se `pending` retry +5min
> 2. Code change `fluxion-proxy/src/email/sender.ts` + `fluxion-proxy/src/routes/stripe-webhook.ts`:
>    - `from: 'FLUXION <licenze@fluxion-app.com>'` (replace `onboarding@resend.dev`)
>    - `reply_to: ['fluxion.gestionale@gmail.com']` invariato
> 3. Gate: tsc 0 errori + vitest 36/36
> 4. Commit + deploy:
>    ```bash
>    cd fluxion-proxy && npx wrangler deploy --env test
>    ```
> 5. Re-smoke FDQ-01 fresh stripe trigger (NO metadata override per default fixture customer):
>    ```bash
>    npx wrangler tail --env test --format=json > /tmp/wrangler-tail-S308.log 2>&1 &
>    stripe trigger checkout.session.completed --api-key "$STRIPE_TEST_SECRET_KEY"
>    sleep 8 && grep -A 5 '"logs":' /tmp/wrangler-tail-S308.log | tail -30
>    ```
>    Expect: webhook 200 + Resend send 200 (NO 403) + log "email sent provider=resend message_id=<uuid>"
> 6. Verify Resend delivery API:
>    ```bash
>    curl -sS https://api.resend.com/emails/<msg_id> -H "Authorization: Bearer ${RESEND_TEST_KEY}"
>    ```
>    Expect `last_event: delivered`
> 7. Evidence: `~/venture-os/state/fdq-01-smoke-S308.json` con before/after delta + production_ready evidence
>
> ### Task D — META-VINCOLO REGOLA #18 (post Task C verde)
>
> Validate-then-implement S187 FASE 1: founder GUI app iMac wizard activate flow (carry-over da S305+S306+S307). REGOLA #18 GO Luke obbligatorio prima di production_ready claim su ring first_delivery_quality.
>
> ### Task E — Promote prod env (post Task C+D verde + founder GO)
>
> 1. Aggiorna `wrangler.toml [env.production]` con stesso Resend setup
> 2. Verify secret `RESEND_API_KEY` in prod env
> 3. `wrangler deploy --env production`
> 4. Webhook endpoint prod Stripe Dashboard → punta a worker prod URL
> 5. Re-smoke prod env con stripe trigger (test mode keys ok per test path)
> 6. Resolve VOS critique `C-LIC-001` post-prod-credentials available
>
> ## EVIDENCE GATE S308 closure verde
>
> - [ ] Pre-flight 5/5 PASS
> - [ ] Task A `fluxion-app.com` registered (CF zone list shows it)
> - [ ] Task B 3 DNS records propagated (verify dig)
> - [ ] Task C Resend domain verified + code deploy + smoke FDQ-01 fresh: webhook 200 + Resend 200 (NO 403) + email delivered
> - [ ] Task D META-VINCOLO REGOLA #18 founder GO Luke documentato
>
> ## REGOLE ATTIVE S308
>
> - REGOLA #4 Critica strutturale obbligatoria — S307 ha esposto bias confirmation S306
> - REGOLA #14 CTO autonomous test+fix (S269) — S307 ha applicato bypass Resend API + stripe CLI in autonomia
> - REGOLA #15 NO A/B questions (S274)
> - REGOLA #16 Research-first (S281) — 2 WebSearch verificate finding S307
> - REGOLA #18 META-VINCOLO validate-then-implement — Task D
> - REGOLA #22 candidata STRENGTHENED (S307): critique-then-ignore confermato 4x. Mitigazione: ogni email provider/sender change DEVE avere smoke con destinatario NON-owner pre production claim
>
> ## CONTEXT BUDGET S307
>
> Chiusura ~55-60% (gate soglia 60% rispettato). Edit MEMORY.md + NEXT_SESSION_PROMPT permessi. Files modificati: 1 evidence (~/venture-os/state/fdq-01-smoke-S307.json), 1 prompt (this file), MEMORY.md.
>
> ## LEZIONI S307
>
> 1. **CTO autonomous bypass pattern WIN**: Task A "founder Gmail inbox verify" risolto via Resend API GET /emails/{id} → `last_event: delivered`. Task B "stripe payment link founder" risolto via stripe CLI trigger fresh + replay. Zero founder interruptions during smoke.
> 2. **Bias confirmation in tandem research**: Claude.ai S306 + WebSearch May 2026 hanno DETTO il vero ma INCOMPLETO. "Resend free tier 100/day" è dato corretto. "onboarding@resend.dev shared sender suitable pre-launch" è inferenza fallace (test-mode restricted to owner). Lesson: tandem research deve essere validata con E2E smoke su corner case non solo happy path.
> 3. **Production smoke autonomous via stripe CLI**: pattern `stripe trigger checkout.session.completed --add metadata[...]` triggera webhook reale signed by Stripe infra → webhook endpoint test riceve REAL signature → handler executes REAL code path. Founder NOT needed for full E2E webhook validation. Solo per: payment method input (Cloudflare Registrar, etc) e GUI app activate.
> 4. **Resend domain pre-provisioning autonomous**: API POST /domains crea record pending + output DNS records target SENZA domain reale registrato. Permette CTO preparation pre founder action.
