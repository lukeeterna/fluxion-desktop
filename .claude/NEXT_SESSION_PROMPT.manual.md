# Prompt ripartenza S312 — Task E-PRE LICENSE_RECOVERY_SECRET prod + Task D META-VINCOLO #18 + Task E prod deploy + Task F sync

> ## 🎯 DIRETTIVA LUKE (invariata da S308)
>
> **"Segui la roadmap e vai dritto verso la produzione con parametri VOS"**.
>
> Scope locked S312 = chiusura `C-FLUXI-002` con prod deploy ready + founder GUI activate validato.
>
> Parametri VOS attivi: REGOLA #4 critica strutturale · #14 CTO autonomous · #15 NO A/B · #16 research-first · #18 META-VINCOLO validate-then-implement · #20 CF token. Soglie context: 40 WARN, 50 BLOCK_CRITICAL, 60 closing, 70 hard-stop.
>
> ## ⚡ S311 OUTCOME (CLOSED VERDE preflight 5/5, structural findings Task E, founder-bound Task D deferred)
>
> **Done S311**:
> - Pre-flight 5/5 PASS (git clean, /health 200, Resend `verified`, VOS gate OK, iMac path accessible)
> - Task E read-only investigation completata
> - Evidence file: `~/venture-os/state/s311-preflight-findings.json`
>
> **Findings strutturali S311 (REGOLA #4)**:
> 1. **wrangler.toml top-level = prod config**: KV `12dbb4f8...` + D1 `e065a108...` + `vars.ENVIRONMENT="production"`. `[env.production]` NOT needed. S311 prompt E-3 sintassi `--env production` ERRATA → S312 usa `wrangler deploy` (no flag).
> 2. **12 secrets prod present** (vs 7 expected): bonus 5 = ADMIN_API_SECRET, CEREBRAS_API_KEY, DISCORD_HEALTH_WEBHOOK_URL, ED25519_PUBLIC_KEY_V1, OPENROUTER_API_KEY. ED25519_PRIVATE_KEY renamed → ED25519_PRIVATE_KEY_PKCS8.
> 3. **🚨 BLOCKING**: `LICENSE_RECOVERY_SECRET` **MISSING in prod env** — usato in `stripe-webhook.ts:452-453`, `checkout-success.ts:247,273`, `license-recovery.ts:81`. Optional in type (`Env.LICENSE_RECOVERY_SECRET?:`), gracefully no-crash, **MA**: customer email post-€497 SENZA recovery URL link → cliente perde licenza al primo refresh → refund storm. Task E-PRE necessario PRIMA di E-3 deploy prod.
> 4. **ED25519_KID**: NON in secrets NON in [vars] — verify usage in code S312 (potrebbe essere unused legacy).
>
> ## ⛔ PRE-FLIGHT S312 (≤30s)
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION && git status --short && git log --oneline -3
> source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
> curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
> cd fluxion-proxy && npx wrangler secret list 2>&1 | grep -c LICENSE_RECOVERY_SECRET
> # Expect 0 (still missing) → Task E-PRE required
> ```
>
> ## SCOPE S312 (ordine esecuzione)
>
> ### Task E-PRE — LICENSE_RECOVERY_SECRET prod (NUOVO S312, BLOCKING)
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> # Generate value (CTO autonomous):
> RECOVERY_SECRET=$(openssl rand -hex 32)
> echo "$RECOVERY_SECRET" | npx wrangler secret put LICENSE_RECOVERY_SECRET
> # Verify:
> npx wrangler secret list 2>&1 | grep LICENSE_RECOVERY_SECRET
> # Expect: present in list
> ```
>
> **CRITICA REGOLA #4**: Generare nuovo secret prod NON va usato per re-sign URL test esistenti. Decision CTO: clean secret prod, mai shared con test. Document in evidence file.
>
> ### Task D — META-VINCOLO REGOLA #18 founder GUI activate (BLOCCANTE pre production_ready, INVARIATO S311)
>
> Steps founder-bound (CTO guida, Luke esegue su iMac GUI):
>
> **D-1: Smoke E2E con email reale (su PROD env, post E-3 deploy)**
> 1. Founder apre Stripe Payment Link PROD (founder genera in Stripe LIVE dashboard se ancora TEST → vedi E-7)
> 2. Founder paga con carta REALE (€497 vero) — oppure usa Stripe Payment Link TEST se Luke vuole evitare cash flow prima del primo cliente
> 3. /success page render verify (CTO autonomous `wrangler tail`)
> 4. Founder check Gmail inbox `fluxion.gestionale@gmail.com` per email "FLUXION — Il tuo ordine è confermato!" da `FLUXION <licenze@fluxion-app.com>` — verify recovery URL link CLICCABILE + screenshot
>
> **D-2: GUI activate flow su FLUXION app iMac**
> 1. CTO: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev"` (background)
> 2. Founder: apre FLUXION app, wizard email + click "Attiva" → verify Ed25519 unlock
> 3. Founder screenshot post-activation
>
> **D-3: S187 FASE 1 evidence file**
> Compilare `~/venture-os/state/s187-fase1-S312-production-validation.json` con: tabella fonte (smoke + screenshot inbox + screenshot activate), verdetto `production_ready_for_revenue: true|false`, founder GO esplicito Luke timestamp + statement, bug residui.
>
> **STOP point**: CTO NON dichiara `production_ready` senza output reale D-1/D-2/D-3 letti da Luke.
>
> ### Task E — Prod deploy (post Task E-PRE done)
>
> **E-1: Verify wrangler.toml top-level prod** (re-confirm S311 finding)
> ```bash
> head -50 wrangler.toml | grep -E "ENVIRONMENT|database_id|kv_namespace"
> # Expect: ENVIRONMENT="production", D1 id e065a108, KV 12dbb4f8
> ```
>
> **E-2: Secrets verify**
> ```bash
> npx wrangler secret list | python3 -c "import sys, json, re; r=sys.stdin.read(); arr=json.loads(re.search(r'\[.*\]', r, re.S).group(0)); print(len(arr), 'secrets'); print('LICENSE_RECOVERY_SECRET:', any(s['name']=='LICENSE_RECOVERY_SECRET' for s in arr))"
> # Expect: 13 secrets, LICENSE_RECOVERY_SECRET: True
> ```
>
> **E-3: Deploy prod (NO --env flag)**
> ```bash
> source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
> npx wrangler deploy 2>&1 | tail -20
> curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> ```
>
> **E-4: Stripe webhook LIVE endpoint** (founder dashboard action)
> Verify `https://dashboard.stripe.com/webhooks` LIVE mode endpoint = `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`. Se ancora TEST → CTO guida founder creazione LIVE endpoint, copia `whsec_...` → `npx wrangler secret put STRIPE_WEBHOOK_SECRET` (overwrite).
>
> **E-5: Smoke prod skip** (REGOLA #15 NO A/B, decisione locked S311): validate solo via primo CLOSED_WON reale con `wrangler tail` monitoring attivo (no automated test for prod webhook).
>
> **E-6: VOS critique C-LIC-001 resolve**
> ```bash
> python3 ~/.vos/vos_plan.py critique resolve C-LIC-001 --reason "Stripe PROD credentials + LICENSE_RECOVERY_SECRET active post S312 prod deploy"
> ```
>
> **E-7: Landing → checkout consent prod URL**
> ```bash
> grep -E "buy.stripe.com" landing/checkout-consent.html
> # If test_ → founder genera Payment Links PROD (€497 + €897) in Stripe LIVE → swap URL → deploy CF Pages landing
> ```
>
> ### Task F — Doc sync
>
> 1. PLAN.md C-FLUXI-002 → `[RESOLVED S310-S312]` con evidence path
> 2. ROADMAP_REMAINING.md: marca primo €497 ready, next milestone = first CLOSED_WON real customer
> 3. HANDOFF.md S312 summary
>
> ## EVIDENCE GATE S312 closure verde
>
> - [ ] Pre-flight 6/6 PASS (including LICENSE_RECOVERY_SECRET=0 check)
> - [ ] E-PRE: LICENSE_RECOVERY_SECRET prod populated + verified in list
> - [ ] E-1/E-2/E-3: prod deploy + /health 200
> - [ ] E-4: Stripe webhook LIVE prod endpoint configured
> - [ ] E-6: VOS critique C-LIC-001 resolved
> - [ ] E-7: landing checkout URL PROD (or decisione Luke su test→prod swap)
> - [ ] D-1: email reale received + inbox screenshot
> - [ ] D-2: FLUXION app GUI activate PASS + screenshot
> - [ ] D-3: S187 FASE 1 evidence file + founder GO esplicito Luke
> - [ ] F: PLAN.md + ROADMAP_REMAINING.md + HANDOFF.md updated
>
> ## REGOLE ATTIVE S312
>
> - REGOLA #4 critica strutturale (S311 finding LICENSE_RECOVERY_SECRET = strengthening)
> - REGOLA #14 CTO autonomous (E-PRE + E-1/E-2/E-3 + E-6 autonomous; D founder-bound only)
> - REGOLA #15 NO A/B questions (E-5 smoke prod skip locked)
> - REGOLA #16 research-first
> - REGOLA #18 META-VINCOLO validate-then-implement (Task D BLOCCANTE)
> - REGOLA #20 CF token
> - REGOLA #22 candidata: critique-then-ignore — S311 finding LICENSE_RECOVERY_SECRET = exact pattern (test-only secret not promoted to prod = silent revenue blocker)
>
> ## ARTEFATTI S311 PRONTI PER S312
>
> - Commit S310: `587d554` (Resend domain custom)
> - Commit S311: pending (handoff + evidence)
> - Resend domain id: `6f986180-2eaf-41e2-8a40-53ebeefedbf0` (verified)
> - Evidence S311: `~/venture-os/state/s311-preflight-findings.json`
> - Evidence S310: `~/venture-os/state/fdq-01-smoke-S310.json`
> - Worker test deployed: `258b0cd1-2148-412f-99e6-876cd4d9b159`
> - Stripe Payment Links TEST: base €497 `plink_1TRrGqIW4bHDTsaHeX8g37gD` / pro €897 `plink_1TRrGrIW4bHDTsaH1KwXKrUJ`
>
> ## DECISIONI LUKE PENDENTI (NON bloccanti, escalate post €497 reale)
>
> 1. `magazzino` ASSENTE → scope v1.0 o post-launch?
> 2. `9 verticali` incoerenti tra 3 fonti → fonte canonica?
> 3. macOS code signing → firma per lancio o ad-hoc + Gatekeeper page?
> 4. Nuovo CF token con `Zone DNS Edit` (90d TTL) future DNS automation?
> 5. DMARC upgrade `p=none` → `p=quarantine` post 1-2 settimane rua reports — schedule reminder?
> 6. **NUOVA S312**: Stripe Payment Link TEST → PROD swap (cash flow first vs validate flow)?
> 7. **NUOVA S312**: ED25519_KID secret prod — investigate usage, decide se aggiungere o rimuovere reference da codice.
>
> ## LEZIONI S311
>
> 1. **wrangler.toml top-level = production**: pattern Cloudflare Workers (env override solo per non-default). S311 prompt assumed `[env.production]` required = errore. Pattern: prima di scrivere `--env <name>`, leggere wrangler.toml struttura.
> 2. **Test-only secret = silent prod blocker**: LICENSE_RECOVERY_SECRET aggiunto in test env Track-B S280s, mai promoted a prod. Optional type (`?:`) graceful = no crash ma feature degradata silenziosamente. Mitigazione strutturale: secret list diff test vs prod PRE-deploy obbligatorio.
> 3. **REGOLA #4 critica strutturale strengthening**: S311 read-only preflight ha catturato 3 finding strutturali (top-level prod, secret count mismatch, LICENSE_RECOVERY_SECRET missing) PRIMA del deploy = pattern preventivo applicato. Continua S312.
