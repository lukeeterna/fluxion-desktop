# Prompt ripartenza S304 — Task 1+2 S303 DONE (CF Pages FBUG-LM-01 live, worker deploy bonus); carry-over 4 founder-bound

> ## ⚡ S303 OUTCOME (closed verde, autonomous CTO PASS)
>
> **Done autonomous (3/6 evidence gate PASS, 3 bonus)**:
> - CF token Write `3856673a...` capability matrix 4/4 PASS (Workers Scripts + KV + Pages + Tail)
> - `wrangler whoami` account `22ddff3a...adf8` (Gianlucanewtech@gmail.com)
> - `wrangler deploy --env test --dry-run` PASS 851 KiB / 123 KiB gzip
> - **Landing CF Pages re-deploy fluxion-landing** 92 files / 7s — deploy id `d5daa095`
>   - Fix FBUG-LM-01 LIVE: `curl https://fluxion-landing.pages.dev/ | grep consenso_marketing` → ✅ 1 (era `marketing_opt_in` bug)
>   - Pattern: CF Pages `source_type: None` → deploy manuale obbligatorio, NO git-trigger
> - **Bonus**: `wrangler secret put BREVO_API_KEY --env test` + `wrangler deploy --env test` v `85d2a2e7` + /health 200 OK
>
> **Carry-over founder-bound (3/6 evidence gate)**:
> - Brevo IP `151.72.29.96` allowlist ancora ON → 401 `/v3/account`
> - Token zombie CF `1814e6dc...` + `cd1221db...` da revocare
> - FDQ-01 smoke real Stripe + Brevo email delivery
> - META-VINCOLO REGOLA #18 founder GUI activate flow
>
> ## ⛔ PRE-FLIGHT S304 (≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short`
> 2. `source ~/.claude/.env`
> 3. **CF token sanity** (deve restare 4/4 PASS):
>    ```bash
>    for ep in "user/tokens/verify" "accounts/${CF_ACCOUNT_ID}/pages/projects" \
>              "accounts/${CF_ACCOUNT_ID}/storage/kv/namespaces" \
>              "accounts/${CF_ACCOUNT_ID}/workers/scripts"; do
>      r=$(curl -sS "https://api.cloudflare.com/client/v4/$ep" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('PASS' if d.get('success') else 'FAIL')")
>      echo "  $ep → $r"
>    done
>    ```
> 4. **Brevo IP check** (DEVE essere 200 ora se founder ha disabilitato allowlist):
>    ```bash
>    curl -sS -H "api-key: $BREVO_API_KEY" https://api.brevo.com/v3/account | python3 -m json.tool | head -8
>    # 200 + JSON account → procedi Task 3 (smoke FDQ-01)
>    # 401 unrecognised IP → ancora bloccato, NEXT ACTION founder dashboard
>    ```
> 5. **Cleanup token zombie verifica** (post founder GUI):
>    ```bash
>    curl -sS "https://api.cloudflare.com/client/v4/user/tokens" \
>      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "
>    import json,sys
>    d=json.load(sys.stdin)
>    for t in (d.get('result') or []):
>        print(t['id'][:8], t.get('status'), t.get('name'))
>    "
>    # MUST: solo 3856673a (Deploy) + 3e1b247d (read-only diagnosi) attivi
>    # NO: 1814e6dc (FLUXION-CTO-Claude-Full), cd1221db (SuperAdmin)
>    ```
>
> ## SCOPE S304 — 4 task carry-over founder-bound, ordine ROI
>
> ### Task 1 — Brevo IP allowlist disable (FOUNDER, 2 min)
>
> Dashboard Brevo:
> 1. Go to `https://app.brevo.com/security/authorised_ips`
> 2. Toggle "Restrict API access by IP" → **OFF**
> 3. Save → toast verde "Settings updated"
> 4. Screenshot post-toast (REGOLA #20 pattern propagazione UI→server fail)
> 5. Reply CTO: "Brevo IP allowlist OFF"
>
> **CTO verify post**: `curl -sS -H "api-key: $BREVO_API_KEY" https://api.brevo.com/v3/account | head -10` → HTTP 200 + JSON account.
>
> ### Task 2 — Cleanup token zombie CF (FOUNDER, 3 min)
>
> Dashboard CF `https://dash.cloudflare.com/profile/api-tokens`:
> - Delete `FLUXION-CTO-Claude-Full` id `1814e6dcf03313a9fe5da45be2833521` (S300 incompleto)
> - Delete `FLUXION-CTO-Claude-SuperAdmin` id `cd1221db034af8cbf959e5824b97b7df` (S301 scope vuoto)
> - Mantenere SOLO `FLUXION-CTO-Deploy-90d` `3856673a...` + `Fluxion_CTO_mode_fUlL` (read-only) `3e1b247d...`
>
> **CTO verify post**: curl `/user/tokens` → 2 token attivi, no zombie.
>
> ### Task 3 — Smoke FDQ-01 Brevo channel real Stripe (CTO autonomous post Task 1)
>
> Solo dopo Task 1 PASS (Brevo IP 200):
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> # Worker già deployato S303 con BREVO_API_KEY secret + LICENSE_RECOVERY_SECRET secret.
> # Verify config success_url Payment Link Stripe Dashboard → /api/v1/checkout-success?session_id={CHECKOUT_SESSION_ID}
> # Real smoke (founder action):
> #   1. Stripe Payment Link prod (base €497) con coupon 100%
> #   2. Card 4242 4242 4242 4242, email fluxion.gestionale@gmail.com
> #   3. /success/ → verify HTML inline payload + recovery URL
> #   4. Brevo email inbox fluxion.gestionale@gmail.com → verify delivery + payload+signature copy-paste link
> # CTO verify post: stripe events list → 1 event checkout.session.completed → resend to webhook
> ```
>
> **Evidence**: Resend dashboard email_sent=false (perché Brevo primary se key set, REGOLA #17). Brevo dashboard `Stats → Emails sent` +1. KV `session:cs_test_*` populated.
>
> ### Task 4 — META-VINCOLO REGOLA #18 (FOUNDER browser+CTO co-validate)
>
> Validate-then-implement S289 prompt S187 FASE 1 6-question evidence:
> 1. Founder Stripe Payment Link reale → /success/ → activate email flow (GUI app iMac SE già installato, ELSE wizard onboarding)
> 2. REGOLA #12 Keychain unlock requirement: founder fisicamente al iMac
> 3. Founder copy payload + signature da email Brevo → wizard activation
> 4. CTO verify post: `gate-state-FLUXION.json` chain_map updated + production_ready_meta_validation_passed=True
> 5. GO Luke obbligatorio prima di chain_map promote o claim production-ready
>
> ## EVIDENCE GATE (S304 closure verde criteri)
>
> - [ ] CF token 4/4 capability PASS (deve restare)
> - [ ] Brevo `/v3/account` HTTP 200 (post Task 1 founder)
> - [ ] Token zombie revocati (verify curl `/user/tokens` 2 attivi)
> - [ ] FDQ-01 smoke real PASS: Stripe webhook → Brevo email delivered → inbox confermata
> - [ ] META-VINCOLO REGOLA #18 founder GO Luke documentato in MEMORY.md S305
>
> ## FILES S303 modificati
>
> - `MEMORY.md` (+ stato S303 entry)
> - `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file)
> - Worker deploy: `fluxion-proxy-test` v `85d2a2e7-6c70-410c-9227-66b74357dd24`
> - CF Pages deploy: `fluxion-landing` id `d5daa095`
> - Secret `BREVO_API_KEY` added to worker test env (8 secrets totali)
>
> ## CONTEXT BUDGET S303
>
> Boot ~22% + lavoro ~6% = ~28%. Headroom ~72% rimasto. Closing nominale.
>
> ## REGOLE ATTIVE
>
> - REGOLA #14 CTO autonomous test+fix (S269) — **applicata S303 PASS**
> - REGOLA #15 NO A/B questions (S274)
> - REGOLA #16 Research-first (S281) — **applicata pre-flight S303 PASS** (rivelato CF Pages source_type:None)
> - REGOLA #18 META-VINCOLO validate-then-implement (S289)
> - REGOLA #19 Persist segreti immediato (S300)
> - REGOLA #20 CF token screenshot + capability test mandatory (S301)
