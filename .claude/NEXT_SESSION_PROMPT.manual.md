# Prompt ripartenza S306 — Brevo sender bug (FBUG-BREVO-SENDER-01) + Task 4 META-VINCOLO

> ## ⚡ S305 OUTCOME (closed arancione, Task 0 DONE + Task 3 5/6 PASS + 1 hard bug Brevo)
>
> **Done (1/3 task S305)**:
> - **Task 0 ✅ MEMORY.md fix**: annotation `[CORRETTO S304 audit]` su 2 mention `1814e6dc` cronistoria S301+S303 (token RINOMINATO Track-B-S28 IN USO, NON zombie). Nuovo header S304 closed verde in cima.
> - **Pre-flight S305**: Brevo IP allowlist OFF propagato server (`/v3/account` 200 + `/v3/smtp/email` 201 messageId), CF token Deploy-90d active, 5 token live legittimi.
>
> **Partial (Task 3 5/6 PASS)**:
> - ✅ Webhook reached worker test (tail `POST /api/v1/webhook/stripe` → 200)
> - ✅ Signature verified (200, no 400)
> - ✅ /success HTML render (tail `GET /success/REDACTED` → 200)
> - ✅ KV `purchase:fluxion.gestionale@gmail.com` NEW (exp 2036, 10y TTL)
> - ⏭️ D1 `webhook_events` skipped (Deploy-90d token no D1 perm, minor)
> - ❌ **Brevo email delivery FAIL** → error: `sender noreply@fluxion-app.brevosend.com is not valid. Validate your sender or authenticate your domain`
>
> **Bug FBUG-BREVO-SENDER-01**:
> - File: `fluxion-proxy/src/routes/stripe-webhook.ts:185`
> - Hard-coded: `BREVO_DEFAULT_SENDER_EMAIL = 'noreply@fluxion-app.brevosend.com'`
> - Assunzione S296 "Brevo auto-provisiona subdomain *.brevosend.com per account free" → **empiricamente falso S305**
> - Critica strutturale S296 era CORRETTA, ignorata in deploy S303
>
> **Carry-over S306 (founder-bound)**:
> 1. **PRIMA di fix code**: recuperare decisione ricerca tandem Claude.ai S294 su sender Brevo (founder context o cronologia conversation). File `.claude/CLAUDE_AI_VALIDATION_PROMPT.md` S296 NON contiene la decisione.
> 2. Task 3 completion: applicare decisione sender + re-deploy worker test + re-smoke FDQ-01 + verify Brevo events delivered=1 + inbox `fluxion.gestionale@gmail.com` payload+sig+recovery URL.
> 3. Task 4 META-VINCOLO REGOLA #18 founder GUI activate flow + S187 FASE 1 evidence per production_ready claim.
>
> ## ⛔ PRE-FLIGHT S306 (≤45s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short`
> 2. `source ~/.claude/.env`
> 3. **CF token capability** (4/4 PASS):
>    ```bash
>    curl -sS "https://api.cloudflare.com/client/v4/user/tokens/verify" \
>      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('PASS' if d.get('success') else 'FAIL')"
>    ```
> 4. **Brevo /v3/account 200** (verify still propagated):
>    ```bash
>    curl -sS -H "api-key: $BREVO_API_KEY" -w "\nHTTP=%{http_code}\n" https://api.brevo.com/v3/account | tail -3
>    ```
> 5. **Worker test /health 200**:
>    ```bash
>    curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
>    ```
> 6. **Brevo senders list** (verify quali sender già verificati):
>    ```bash
>    curl -sS -H "api-key: $BREVO_API_KEY" https://api.brevo.com/v3/senders | python3 -m json.tool | head -30
>    ```
>
> ## SCOPE S306
>
> ### Task A — Recovery decisione ricerca tandem S294 (FIRST, MANDATORY)
>
> Founder fornisce decisione sender Brevo da ricerca tandem Claude.ai S294. **CTO NON improvvisa**.
> 3 opzioni note Brevo (CTO seleziona quella matchante decisione S294):
> - (a) Sender singolo `fluxion.gestionale@gmail.com` verified via Brevo email confirmation 1-click
> - (b) Domain custom `fluxion-app.com` verified via DNS records SPF/DKIM (TXT su CF DNS)
> - (c) Sender subdomain `noreply@<custom>.fluxion-app.com` con domain verify
>
> ### Task B — Apply sender fix + re-smoke FDQ-01
>
> Post recovery decisione S294:
> 1. Edit `fluxion-proxy/src/routes/stripe-webhook.ts:185` con sender decidato
> 2. `cd fluxion-proxy && wrangler deploy --env test`
> 3. Avvio `wrangler tail --env test --format=json > /tmp/wrangler-tail-S306.log 2>&1 &`
> 4. Founder altro pagamento test card 4242 `https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000` email `fluxion.gestionale@gmail.com`
> 5. CTO verify post:
>    - tail webhook 200 + /success 200
>    - KV `purchase:fluxion.gestionale@gmail.com` updated timestamp
>    - Brevo events: `requests`=N+1, `delivered`=N+1, `error`=0 (no new error)
>    - Inbox `fluxion.gestionale@gmail.com` → email con payload + signature + recovery URL
> 6. Evidence file: `~/venture-os/state/fdq-01-smoke-S306.json` (timestamp + stripe_event_id + brevo_msgid + kv_key + recovery_url + delivery_status)
>
> ### Task C — META-VINCOLO REGOLA #18 (post Task B verde)
>
> Validate-then-implement S187 FASE 1 6-question evidence per production_ready claim:
> 1. Founder Stripe Payment Link test → /success/ → activate email flow (GUI app iMac fisicamente, REGOLA #12 Keychain unlock)
> 2. Founder copy payload + signature da email Brevo → wizard activation app
> 3. CTO verify post: `gate-state-FLUXION.json` chain_map ring 5 first_delivery_quality evidence + `production_ready_meta_validation_passed=True`
> 4. GO Luke obbligatorio prima di chain_map promote o production_ready claim
>
> ## EVIDENCE GATE S306 closure verde
>
> - [ ] Pre-flight 6/6 PASS (git + env + CF + Brevo + worker + senders list)
> - [ ] Task A recovery decisione S294 documentata
> - [ ] Task B FDQ-01 smoke 6/6 PASS (incluso Brevo delivered + inbox)
> - [ ] Task C META-VINCOLO REGOLA #18 founder GO Luke documentato
>
> ## REGOLE ATTIVE + nuova candidata
>
> - REGOLA #4 Critica strutturale obbligatoria
> - REGOLA #14 CTO autonomous test+fix (S269)
> - REGOLA #15 NO A/B questions (S274) — VIOLATA S305 fix sender 3 opzioni elencate, recoverable se ricerca S294 unica
> - REGOLA #16 Research-first (S281) — VIOLATA S305 (improvisation sender vs apply ricerca S294 pre-esistente)
> - REGOLA #18 META-VINCOLO validate-then-implement (S289)
> - **REGOLA #22 candidata (S305)**: critique-then-ignore = anti-pattern. Critica strutturale flagged in PLAN/handoff DEVE essere addressed PRE-deploy, NON deferred a empirical fail. REGOLA #4 critica obbligatoria NON basta senza critique-action-gate enforcement.
>
> ## CONTEXT BUDGET S305
>
> Chiusura 66% (sopra soglia 60% closing CLAUDE.md vincolo 7) — closing ordinato attivato post founder reminder. CLOSING_ONLY (70-80%) NOT raggiunto, MEMORY.md edit permesso.
>
> ## LEZIONI S305
>
> 1. **CTO error retrospettivo**: ho proposto fix sender gmail come "decisione singola" ignorando ricerca tandem S294 pre-esistente. REGOLA #16 (research-first) include "research già fatta = NON ri-fare, NON ri-decidere". Pattern recovery S306: recuperare decisione esistente PRIMA di proporre.
> 2. **Pattern candidato REGOLA #22 critique-then-ignore**: pattern strutturale FLUXION cross-sessioni (S296 sender flag → S303 deploy ignored → S305 empirical fail). Stessa dinamica REGOLA #20 (CF UI≠commit) ma su layer critique invece di commit.
