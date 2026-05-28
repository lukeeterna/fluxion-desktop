# Prompt ripartenza S307 — Founder inbox verify S306 fix + FDQ-01 full smoke + META-VINCOLO REGOLA #18

> ## ⚡ S306 OUTCOME (CLOSED VERDE, FBUG-BREVO-SENDER-01 fixed Brevo→Resend swap)
>
> **Done S306 (CTO autonomous)**:
> - Fix FBUG-BREVO-SENDER-01: rimosso Brevo completamente da codebase (commit `481863a`, +29 / -125 righe)
> - Files: `fluxion-proxy/src/{email/sender.ts, routes/stripe-webhook.ts, lib/types.ts}` — Resend-only + `reply_to: fluxion.gestionale@gmail.com`
> - Validation 3 fonti: Claude.ai S306 tandem + WebSearch May 2026 + codebase grep
> - Gate: TS 0 errori, vitest 36/36 PASS, pre-commit PASSED
> - Deploy: worker `fluxion-proxy-test` version `f245b8ed`, health 200 OK
> - Cleanup: secret `BREVO_API_KEY` deleted da test env
> - CTO autonomous smoke (REGOLA #14): `POST /admin/email-sequence/preview` → `{sent:true, provider:"resend", provider_message_id:"58cf5601-0b53-4ee9-9abc-bdd8279ea42a"}` HTTP 200
> - VOS gate: `C-LIC-001` deferred tattico (orthogonal a S306 test env scope), runbook `STRIPE-UNBLOCK-FLUXION.md` tracks resolution prod
>
> **Pendente verify founder (CTO no Gmail access)**:
> - Inbox `fluxion.gestionale@gmail.com` deve contenere email Resend ID `58cf5601-0b53-4ee9-9abc-bdd8279ea42a` subject "FLUXION — Hai già attivato la tua licenza?"
>
> ## ⛔ PRE-FLIGHT S307 (≤45s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short && git log --oneline -3`
> 2. `source ~/.claude/.env`
> 3. **Worker test /health 200**:
>    ```bash
>    curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
>    ```
> 4. **VOS gate state**:
>    ```bash
>    python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
>    ```
> 5. **Verify Resend secret ancora attivo test env** (no smoke se RESEND_API_KEY mancante):
>    ```bash
>    cd fluxion-proxy && npx wrangler secret list --env test 2>&1 | grep RESEND_API_KEY
>    ```
>
> ## SCOPE S307
>
> ### Task A — Founder inbox verify S306 fix (FIRST, FOUNDER-BOUND)
>
> Founder controlla inbox `fluxion.gestionale@gmail.com` per email subject `"FLUXION — Hai già attivato la tua licenza?"` (Resend ID `58cf5601-0b53-4ee9-9abc-bdd8279ea42a`):
> - Branch verde se email in INBOX (deliverability OK con shared sender)
> - Branch giallo se email in SPAM/PROMOZIONI (deliverability degradata → anticipare upgrade dominio Task C)
> - Branch rosso se email assente dopo 1h (Resend pipeline issue → check Resend dashboard logs)
>
> ### Task B — FDQ-01 full smoke E2E (post Task A verde/giallo)
>
> Replay full smoke con codice S306 fix:
> 1. Avvio `wrangler tail --env test --format=json > /tmp/wrangler-tail-S307.log 2>&1 &`
> 2. Founder Stripe Payment Link test card 4242: `https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000` email `fluxion.gestionale@gmail.com`
> 3. CTO verify post:
>    - tail webhook 200 + signature verified + /success 200
>    - KV `purchase:fluxion.gestionale@gmail.com` updated timestamp
>    - D1 `webhook_events` row inserted (event_id, license_payload, email_sent_at)
>    - Resend logs: 1 email accepted, status `delivered` (check Resend dashboard)
>    - Inbox `fluxion.gestionale@gmail.com` → email "FLUXION — Il tuo ordine è confermato!" con payload + signature + recovery URL
> 4. Evidence file: `~/venture-os/state/fdq-01-smoke-S307.json` (timestamp + stripe_event_id + resend_msgid + kv_key + recovery_url + delivery_status)
>
> ### Task C — Anticipare upgrade dominio SE Task A giallo (deliverability)
>
> Trigger condizionato: SE Task A spam folder, anticipare path long-term Claude.ai S306 Q5:
> 1. Founder Cloudflare Registrar → registra `fluxion-app.com` (~€10/anno, persona fisica OK, NO P.IVA, NO Stripe Professional required)
> 2. Resend Dashboard → Domains → Add Domain → output DNS records (SPF TXT, DKIM CNAME, DMARC TXT)
> 3. Founder Cloudflare DNS panel → add 3 record TXT/CNAME → wait propagation (15min-2h)
> 4. Resend verify domain (button)
> 5. Code change: `RESEND_DEFAULT_FROM = 'FLUXION <licenze@fluxion-app.com>'` + `RESEND_REPLY_TO` invariato
> 6. Re-deploy worker test + re-smoke Task B
>
> ### Task D — META-VINCOLO REGOLA #18 (post Task B verde)
>
> Validate-then-implement S187 FASE 1 6-question evidence per production_ready claim (carry-over da S305):
> 1. Founder Stripe Payment Link test → /success/ → activate email flow (GUI app iMac fisicamente, REGOLA #12 Keychain unlock)
> 2. Founder copy payload + signature da email Resend → wizard activation app
> 3. CTO verify post: `gate-state-FLUXION.json` chain_map ring 5 first_delivery_quality evidence + `production_ready_meta_validation_passed=True`
> 4. GO Luke obbligatorio prima di chain_map promote o production_ready claim
>
> ### Task E — Optional: re-open C-LIC-001 critique (founder choice)
>
> S306 ha defer-tattico `C-LIC-001` per unblock test deploy. Se Luke vuole tracking attivo (visibile in `vos_plan gate`):
> ```bash
> python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-LIC-001 --motivation "[se prod credentials approval arrivato]"
> # OPPURE manualmente in PLAN.md cambia [DEFERRED:...] → [OPEN]
> ```
> Runbook `STRIPE-UNBLOCK-FLUXION.md` ha 6 step (~40min attivi + 1-3gg async Stripe) per resolution prod definitiva.
>
> ## EVIDENCE GATE S307 closure verde
>
> - [ ] Pre-flight 5/5 PASS
> - [ ] Task A inbox verify documentato (verde/giallo/rosso)
> - [ ] Task B FDQ-01 smoke 6/6 PASS (incluso Resend delivered + inbox)
> - [ ] Task D META-VINCOLO REGOLA #18 founder GO Luke documentato
> - [ ] Task C deferred se Task A verde, eseguito se Task A giallo
>
> ## REGOLE ATTIVE
>
> - REGOLA #4 Critica strutturale obbligatoria
> - REGOLA #14 CTO autonomous test+fix (S269) — applicata con successo S306 smoke
> - REGOLA #15 NO A/B questions (S274)
> - REGOLA #16 Research-first (S281) — applicata 3 fonti S306
> - REGOLA #18 META-VINCOLO validate-then-implement (S289) — gating production_ready claim Task D
> - REGOLA #19 Persist secrets immediately (S300) — applicata S306 `ADMIN_API_SECRET` fresh-generated test env
> - REGOLA #22 candidata (S305→S306 confermata): critique-then-ignore anti-pattern fixed con `vos_plan critique defer/resolve` enforcement
>
> ## CONTEXT BUDGET S306
>
> Chiusura ~60% (CLOSING_ONLY soglia 70-80% NOT raggiunta). Edit MEMORY.md + NEXT_SESSION_PROMPT permessi. PLAN.md edit avvenuto via `vos_plan critique defer` CLI (no direct Write — safe).
>
> ## LEZIONI S306
>
> 1. **CTO autonomous smoke pattern (REGOLA #14 applicato bene)**: admin endpoint `POST /admin/email-sequence/preview` valida il code path Resend identico al stripe-webhook senza dover triggerare Stripe Payment Link reale. Lesson: per swap email provider, prima di smoke E2E full triggerable, usare admin trigger isolato.
> 2. **VOS gate semantic vs tactical**: critique `C-LIC-001` (prod scope) bloccava operazione test scope (false positive). CTO autonomous decision = defer tattico con reason esplicito, NON forced-proceed silent. Pattern: gate semantic mismatch → defer documentato meglio di bypass.
> 3. **Over-engineering critique S296 risolto S306**: Brevo introduction era preventivo per scenario >100 vendite/giorno mai materializzato. Pattern: pre-launch volume realistico (<100/day pipeline mapping) prima di scegliere provider con free tier higher-cap.
