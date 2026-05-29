# Prompt ripartenza S311 — Task D META-VINCOLO #18 founder GUI activate + Task E prod promote

> ## 🎯 DIRETTIVA LUKE (invariata da S308)
>
> **"Segui la roadmap e vai dritto verso la produzione con parametri VOS"**.
>
> Scope locked S311 = chiusura definitiva `C-FLUXI-002` (post Task C verde S310) → primo €497 ready.
>
> Parametri VOS attivi: REGOLA #4 critica strutturale · #14 CTO autonomous · #15 NO A/B · #16 research-first · #18 META-VINCOLO validate-then-implement · #20 CF token. Soglie context: 40 WARN, 50 BLOCK_CRITICAL, 60 closing, 70 hard-stop.
>
> ## ⚡ S310 OUTCOME (closed verde Task C 5/5, FBUG-RESEND-SHARED-SENDER-01 RESOLVED)
>
> **Done S310** (commit `587d554`):
> - Pre-flight 4/4 PASS
> - **C-1**: Resend domain `fluxion-app.com` `status: verified` (DKIM+SPF MX+SPF TXT all green via 1 retry POST /verify)
> - **C-2**: `from` swap in 2 file (`fluxion-proxy/src/email/sender.ts:33` + `fluxion-proxy/src/routes/stripe-webhook.ts:185`) → `FLUXION <licenze@fluxion-app.com>` (reply_to preserved)
> - **C-3**: tsc 0 errori + vitest 36/36 PASS (4.36s) + `wrangler deploy --env test` version `258b0cd1-2148-412f-99e6-876cd4d9b159`
> - **C-4 SMOKE FDQ-01 PASS**: `stripe trigger checkout.session.completed --override 'checkout_session:metadata[tier]=base'` → webhook 200 → Resend ID `72eff6e9-c160-488b-b579-ee36e23f3ef6` → API verify: `from=FLUXION <licenze@fluxion-app.com>`, `to=stripe@example.com` (NON-owner!), `reply_to=fluxion.gestionale@gmail.com`, `last_event=sent`, NO 403 validation_error (vs S307 fail mode)
> - **C-5**: evidence `~/venture-os/state/fdq-01-smoke-S310.json`
>
> **Critica strutturale S310 (REGOLA #4)**:
> 1. `last_event=sent` (NOT `delivered`): stripe@example.com è RFC reserved test domain, mai SMTP-resolved. Task D founder GUI test DEVE usare email reale per confermare end-to-end delivery+inbox+spam folder.
> 2. License recovery URL embedded in email punta a worker TEST env. Task E prod promote: verify codice genera worker URL based on ENVIRONMENT var (`fluxion-proxy.gianlucanewtech.workers.dev` per prod).
> 3. Custom domain unlocks Resend free tier 100/day 3000/mo per recipient illimitato. Trigger upgrade Resend Pro $20/mese = >25 vendite/giorno sostenute 7gg (locked S306 Claude.ai research).
> 4. DMARC `p=none` monitor-only. Post 1-2 settimane rua reports (`fluxion.gestionale@gmail.com`) → upgrade `p=quarantine` per spoofing protection.
>
> ## ⛔ PRE-FLIGHT S311 (≤30s)
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION && git status --short && git log --oneline -3
> source ~/.claude/.env
> curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> curl -sS https://api.resend.com/domains/6f986180-2eaf-41e2-8a40-53ebeefedbf0 -H "Authorization: Bearer ${RESEND_TEST_KEY}" | python3 -c "import sys, json; d=json.load(sys.stdin); print('status:', d['status'])"
> python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
> ssh imac "ls -la '/Volumes/MacSSD - Dati/fluxion' 2>&1 | head -3"
> ```
>
> Expect: git clean, /health 200, Resend `verified`, VOS gate OK, iMac fluxion path accessible.
>
> ## SCOPE S311
>
> ### Task D — META-VINCOLO REGOLA #18 founder GUI activate (BLOCCANTE pre production_ready)
>
> **Prompt S187 FASE 1 (research+validation tabella fonte+verdetto+evidenza) PRIMA di dichiarare CLOSED qualsiasi anello/ring production-critical.**
>
> Steps founder-bound (CTO guida, Luke esegue su iMac GUI):
>
> **D-1: Smoke E2E con email reale**
> 1. Founder apre Stripe Payment Link TEST: `https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000` (€497 base)
> 2. Founder paga con test card `4242 4242 4242 4242`, exp `12/29`, CVC `123`, customer email = `fluxion.gestionale@gmail.com` (account-owner)
> 3. /success page render verify (CTO autonomous tail)
> 4. Founder check Gmail inbox `fluxion.gestionale@gmail.com` per email "FLUXION — Il tuo ordine è confermato!" da `FLUXION <licenze@fluxion-app.com>` (check anche Spam + Promozioni)
> 5. Founder screenshot inbox preview email
>
> **D-2: GUI activate flow su FLUXION app iMac**
> 1. CTO: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev"` (build+run app)
> 2. Founder: apre FLUXION app, wizard activation prompt → inserisce email `fluxion.gestionale@gmail.com`
> 3. Founder: clicca "Attiva" → app fa request `/api/v1/activate-by-email` → verify Ed25519 → unlock UI
> 4. Founder screenshot post-activation (UI unlocked)
>
> **D-3: S187 FASE 1 evidence file**
> Compilare `~/venture-os/state/s187-fase1-S311-production-validation.json` con:
> - Tabella fonte: smoke evidence JSON, screenshot inbox, screenshot activate
> - Verdetto: `production_ready_for_revenue: true|false`
> - Founder GO esplicito Luke: timestamp + statement
> - Bug residui identificati (se any)
>
> **STOP point**: CTO NON dichiara `production_ready` senza output reale D-1/D-2/D-3 letti da Luke.
>
> ### Task E — Promote prod env (post Task D verde + founder GO esplicito)
>
> **E-1: wrangler.toml [env.production]**
> ```bash
> cat fluxion-proxy/wrangler.toml | grep -A 20 "\[env.production\]"
> # Verify: KV LICENSE_CACHE prod namespace, D1 fluxion-webhook-events prod, vars ENVIRONMENT="production"
> ```
>
> **E-2: Secrets prod env**
> ```bash
> cd fluxion-proxy
> npx wrangler secret list --env production 2>&1
> # Expect 7+ secrets: ED25519_KID, ED25519_PRIVATE_KEY, ED25519_PUBLIC_KEY, LICENSE_RECOVERY_SECRET, RESEND_API_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
> # Se RESEND_API_KEY mancante: npx wrangler secret put RESEND_API_KEY --env production
> ```
>
> **E-3: Deploy prod**
> ```bash
> source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
> npx wrangler deploy --env production 2>&1 | tail -20
> curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> ```
>
> **E-4: Stripe webhook endpoint prod**
> Verify dashboard `https://dashboard.stripe.com/webhooks` endpoint LIVE punta a `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`. Se ancora TEST → creare endpoint LIVE prod.
>
> **E-5: Smoke prod env**
> Replay un evento test esistente verso prod endpoint NON è sicuro (rischia duplicare email). Alternativa: smoke prod con webhook_secret prod via dry-run curl signed payload. **Decisione CTO autonomous (REGOLA #15 NO A/B)**: skip smoke prod automatizzato, validate solo via primo CLOSED_WON reale (€497 cliente vero) con monitoring `wrangler tail --env production` attivo.
>
> **E-6: VOS critique C-LIC-001**
> ```bash
> python3 ~/.vos/vos_plan.py critique resolve C-LIC-001 --reason "Stripe PROD credentials available post-deploy production env S311"
> ```
>
> **E-7: Landing → checkout consent prod URL**
> Verify `landing/checkout-consent.html` Stripe URL = PROD Payment Link (NOT test_). Se test_ ancora attivo: swap a prod Payment Link `https://buy.stripe.com/PROD_link` (founder genera in Stripe dashboard LIVE).
>
> ### Task F — Update PLAN.md + ROADMAP_REMAINING.md
>
> 1. PLAN.md C-FLUXI-002 → status `[RESOLVED S310-S311]` con evidence path
> 2. ROADMAP_REMAINING.md: marca primo €497 ready, next milestone = first CLOSED_WON real customer
>
> ## EVIDENCE GATE S311 closure verde
>
> - [ ] Pre-flight 5/5 PASS
> - [ ] D-1: email reale fluxion.gestionale@gmail.com received + inbox screenshot
> - [ ] D-2: FLUXION app GUI activate PASS + screenshot
> - [ ] D-3: S187 FASE 1 evidence file + founder GO esplicito Luke
> - [ ] E-1/E-2/E-3: prod env deployed + /health 200
> - [ ] E-4: Stripe webhook LIVE prod endpoint configured
> - [ ] E-6: VOS critique C-LIC-001 resolved
> - [ ] E-7: landing checkout URL prod
> - [ ] F: PLAN.md + ROADMAP_REMAINING.md updated
>
> ## REGOLE ATTIVE S311
>
> - REGOLA #4 critica strutturale obbligatoria
> - REGOLA #14 CTO autonomous test+fix (D-1 tail + E deploy)
> - REGOLA #15 NO A/B questions (smoke prod skip decision)
> - REGOLA #16 research-first
> - REGOLA #18 META-VINCOLO validate-then-implement (Task D BLOCCANTE)
> - REGOLA #20 CF token
> - REGOLA #22 candidata STRENGTHENED: critique-then-ignore mitigated
>
> ## ARTEFATTI S310 PRONTI PER S311
>
> - Commit S310: `587d554` (4 files, 21+/19-)
> - Resend domain id: `6f986180-2eaf-41e2-8a40-53ebeefedbf0` (verified)
> - Worker test deployed: `258b0cd1-2148-412f-99e6-876cd4d9b159`
> - Resend test email evidence: ID `72eff6e9-c160-488b-b579-ee36e23f3ef6`
> - Evidence file: `~/venture-os/state/fdq-01-smoke-S310.json`
> - Stripe Payment Links TEST: base €497 `plink_1TRrGqIW4bHDTsaHeX8g37gD` / pro €897 `plink_1TRrGrIW4bHDTsaH1KwXKrUJ`
>
> ## DECISIONI LUKE PENDENTI (NON bloccanti, escalate post €497 reale)
>
> 1. `magazzino` ASSENTE → scope v1.0 o post-launch?
> 2. `9 verticali` incoerenti tra 3 fonti → fonte canonica?
> 3. macOS code signing → firma per lancio o ad-hoc + pagina istruzioni Gatekeeper?
> 4. Nuovo CF token con `Zone DNS Edit` (90d TTL) per future DNS automation?
> 5. **NUOVA S310**: DMARC upgrade `p=none` → `p=quarantine` post 1-2 settimane rua reports — schedule reminder?
>
> ## LEZIONI S310
>
> 1. **Resend verify async timing**: trigger HTTP 200 immediate, ma DNS check Resend-side ha richiesto ~10 min + 1 re-trigger. Pattern S309 confermato: poll ogni 5 min, no busy-wait.
> 2. **stripe trigger override sintassi**: `--override 'checkout_session:metadata[tier]=base'` PASS, `customer_email` override invalid_request_error. Per email override usare fixture path o `--api-key` + manual session create.
> 3. **last_event=sent vs delivered**: stripe@example.com (RFC reserved) mai SMTP-resolved → `sent` è max ottenibile in smoke trigger. Per delivered evidence DEVE usare email reale (Task D founder).
> 4. **REGOLA #4 critica strutturale strengthening**: S310 ha catturato `last_event=sent ≠ delivered` come limitazione del test → preventivamente flag per Task D senza founder discovery painful.
