# Prompt ripartenza S310 — Task C continue (Resend verify wait → code change → deploy → smoke FDQ-01) → Task D+E

> ## 🎯 DIRETTIVA LUKE S308 chiusura (invariata S309)
>
> **"Segui la roadmap e vai dritto verso la produzione con parametri VOS"**.
>
> Scope locked S310 = chiusura `C-FLUXI-002` (FBUG-RESEND-SHARED-SENDER-01) → primo €497. NO scope creep.
>
> Parametri VOS attivi: REGOLA #4 critica strutturale · #14 CTO autonomous · #15 NO A/B · #16 research-first · #18 META-VINCOLO validate-then-implement · #20 CF token. Soglie context: 40 WARN, 50 BLOCK_CRITICAL, 60 closing, 70 hard-stop.
>
> ## ⚡ S309 OUTCOME (closed verde Task A+B founder + Task C verify trigger sent)
>
> **Done S309**:
> - Pre-flight 6/6 PASS (git+env+/health 200+Resend domain not_started+VOS gate verde+CF zone empty)
> - **Task A founder DONE**: `fluxion-app.com` registrato su Cloudflare Registrar 2026-05-29 11:47:50Z, zone id `9fa739250bcbf39d157f76752c4d18fc`, plan Free Website, expiry 2027-05-29, auto-renew ON, registrant persona fisica IT no P.IVA, NS betty+rodney.ns.cloudflare.com
> - **Task B founder DONE**: 4 DNS records compilati via CF panel (token Deploy-90d senza `#dns_records:edit` → no API automation possibile):
>   1. TXT `resend._domainkey` → DKIM p=MIGfMA0G... (full key)
>   2. MX `send` priority 10 → feedback-smtp.eu-west-1.amazonses.com
>   3. TXT `send` → v=spf1 include:amazonses.com ~all
>   4. TXT `_dmarc` → v=DMARC1; p=none; rua=mailto:fluxion.gestionale@gmail.com (Bonus DMARC, raccomandato per Gmail 2024+ requirement)
> - **dig verify 4/4 PASS via 1.1.1.1** (record CF zone autoritativo, propagazione istantanea)
> - **Task C STARTED**: Resend verify trigger HTTP 200 sent → domain status `not_started` → `pending` (Resend-side async DNS check, tipico 1-30 min)
>
> **Evidence file**: `~/venture-os/state/fdq-01-smoke-S309.json`
>
> **Critica strutturale S309 (REGOLA #4)**:
> 1. Bot Fight Mode skip è stato giusto (record DNS only non proxati, zero effetto), MA dominio in futuro avrà landing → decisione re-evaluation post-prod
> 2. Token Deploy-90d limitato (no DNS Edit) ha forzato founder manual compilation = perdita tempo + rischio errori vs API automation. S310 considerare nuovo token con `Zone DNS Edit` (90d TTL) per future DNS ops
> 3. DMARC `p=none` è monitor-only safe, MA non protegge spoofing. Post stabilizzazione (1-2 settimane report rua) → upgrade `p=quarantine`
> 4. Resend verify async = no guarantee tempo. Pattern: poll ogni 5 min max 30 min, se ancora pending → DNS check error specifico via API
>
> ## ⛔ PRE-FLIGHT S310 (≤30s)
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION && git status --short && git log --oneline -3
> source ~/.claude/.env
> curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
> curl -sS https://api.resend.com/domains/6f986180-2eaf-41e2-8a40-53ebeefedbf0 -H "Authorization: Bearer ${RESEND_TEST_KEY}" | python3 -m json.tool | grep -A 1 '"status"' | head -10
> python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
> ```
>
> Expect: Resend domain `status: "verified"` o `pending`. Se pending → poll ogni 5 min max 30 min con `curl ... /verify` re-trigger se serve.
>
> ## SCOPE S310 (Task C continue → D → E)
>
> ### Task C-1 — Resend verify wait + retry
>
> 1. Check status corrente domain
> 2. Se `pending` → ritrigger POST /verify ogni 5 min max 6 retry (30 min totali)
> 3. Se ancora `pending` dopo 30 min → analisi DNS records sub-status (DKIM/SPF MX/SPF TXT individual) per identificare quale fallisce
> 4. Se `verified` → procedi Task C-2
>
> Comando re-trigger:
> ```bash
> source ~/.claude/.env && curl -sS -X POST https://api.resend.com/domains/6f986180-2eaf-41e2-8a40-53ebeefedbf0/verify -H "Authorization: Bearer ${RESEND_TEST_KEY}" -w "\nHTTP=%{http_code}\n"
> ```
>
> ### Task C-2 — Code change `from` sender
>
> File da modificare (ricerca esatto `onboarding@resend.dev` → 2 file confermati S307):
> - `fluxion-proxy/src/email/sender.ts`
> - `fluxion-proxy/src/routes/stripe-webhook.ts`
>
> Replace:
> ```ts
> from: 'onboarding@resend.dev'
> ```
> Con:
> ```ts
> from: 'FLUXION <licenze@fluxion-app.com>'
> ```
>
> Keep invariato: `reply_to: ['fluxion.gestionale@gmail.com']`
>
> ### Task C-3 — Gate + deploy
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> npx tsc --noEmit  # expect 0 errori
> npx vitest run  # expect 36/36 PASS
> npx wrangler deploy --env test  # deploy worker test
> ```
>
> ### Task C-4 — Smoke FDQ-01 fresh
>
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> npx wrangler tail --env test --format=json > /tmp/wrangler-tail-S310.log 2>&1 &
> TAIL_PID=$!
> sleep 2
> stripe trigger checkout.session.completed --api-key "$STRIPE_TEST_SECRET_KEY"
> sleep 10
> kill $TAIL_PID
> grep -E '"(status|provider|message_id|error)":' /tmp/wrangler-tail-S310.log | tail -30
> ```
>
> Expect:
> - webhook 200
> - `provider: "resend"`
> - `message_id: <uuid>` (NOT null)
> - `error: null`
> - NO `403 validation_error` (S307 failure mode)
>
> Verify delivery API:
> ```bash
> source ~/.claude/.env && curl -sS https://api.resend.com/emails/<MESSAGE_ID> -H "Authorization: Bearer ${RESEND_TEST_KEY}" | python3 -m json.tool
> ```
> Expect: `last_event: delivered`
>
> ### Task C-5 — Evidence file
>
> Aggiornare `~/venture-os/state/fdq-01-smoke-S310.json` con before/after delta + production_ready evidence.
>
> ### Task D — META-VINCOLO REGOLA #18 (post Task C verde)
>
> Founder GUI app iMac wizard activate flow + S187 FASE 1 evidence. GO Luke obbligatorio pre production_ready claim.
>
> ### Task E — Promote prod env (post C+D verde + founder GO)
>
> 1. Aggiorna `wrangler.toml [env.production]` con stesso Resend setup
> 2. Verify secret `RESEND_API_KEY` in prod env (potrebbe richiedere `wrangler secret put RESEND_API_KEY --env production`)
> 3. `wrangler deploy --env production`
> 4. Webhook endpoint prod Stripe Dashboard → punta a worker prod URL
> 5. Smoke prod env con stripe test trigger
> 6. Resolve VOS critique `C-LIC-001` post-prod-credentials available
>
> ## EVIDENCE GATE S310 closure verde
>
> - [ ] Pre-flight 5/5 PASS
> - [ ] Resend domain `status: verified` (DKIM+SPF green)
> - [ ] Code change committed (2 files updated)
> - [ ] tsc 0 errori + vitest 36/36
> - [ ] Worker test deployed
> - [ ] Smoke FDQ-01: webhook 200 + Resend 200 + delivered
> - [ ] Task D META-VINCOLO REGOLA #18 founder GO documentato (può slittare S311 se long flow)
>
> ## REGOLE ATTIVE S310
>
> - REGOLA #4 critica strutturale obbligatoria
> - REGOLA #14 CTO autonomous test+fix
> - REGOLA #15 NO A/B questions
> - REGOLA #16 research-first
> - REGOLA #18 META-VINCOLO validate-then-implement
> - REGOLA #20 CF token screenshot (vale anche per future Zone DNS Edit token)
> - REGOLA #22 candidata STRENGTHENED: critique-then-ignore mitigated via smoke con destinatario NON-owner (stripe trigger fresh)
>
> ## CONTEXT BUDGET S309
>
> Chiusura 67% (sopra soglia 60% closing CLAUDE.md vincolo #7) — closing ordinato attivato post VOS hook mandate. CLOSING_ONLY threshold (70-80%) NOT raggiunto, NEXT_SESSION_PROMPT.md edit permesso (non in slugs critici). MEMORY.md NON modificato S309 per context budget.
>
> ## DECISIONI LUKE PENDENTI (NON bloccanti, escalate post €497)
>
> 1. `magazzino` ASSENTE → scope v1.0 o post-launch?
> 2. `9 verticali` incoerenti tra 3 fonti → fonte canonica?
> 3. macOS code signing → firma per lancio o ad-hoc + pagina istruzioni Gatekeeper?
> 4. **NUOVA S309**: nuovo CF token con `Zone DNS Edit` (90d TTL) per future DNS automation? Costa 30s setup, evita founder manual compilation futura.
>
> ## LEZIONI S309
>
> 1. **CF token Deploy-90d gap identificato**: manca `Zone DNS Edit` → forced founder manual UI compilation per 4 record. Pattern: API automation > UI manual sempre (S301 lesson confermata). Pre-S310 considerare token upgrade.
> 2. **Resend verify async pattern**: trigger HTTP 200 immediate, ma status check DNS Resend-side può richiedere 1-30 min anche con record già propagati globalmente. Poll ogni 5 min, no busy-wait.
> 3. **DMARC raccomandazione ferma vs A/B**: VOS hook ha bloccato "DMARC fatto" / "skip" come violazione vincolo #3 (lista decisionale). Lezione: ogni feature ha raccomandazione singola motivata, non scelta utente. Applicato fix immediato.
> 4. **dig via @1.1.1.1 instant propagation**: zone autoritativa CF + query CF resolver = 0 cache delay. Pattern usato per skip wait propagazione globale.
