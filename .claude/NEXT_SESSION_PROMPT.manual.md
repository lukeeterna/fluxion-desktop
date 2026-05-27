# Prompt ripartenza S305 — Task 1+2 S304 DONE (Brevo IP OFF + CF zombie audit no-op); carry-over 2 founder-bound Task 3+4

> ## ⚡ S304 OUTCOME (closed verde, autonomous CTO PASS, audit live ha prevenuto distruzione Track-B-S28)
>
> **Done (2/4 task S304)**:
> - **Task 1 ✅ Brevo IP allowlist OFF** — founder dashboard `https://app.brevo.com/security/authorised_ips` "Deactivate blocking" + conferma. CTO non ha potuto verificare via `curl /v3/account` (test rimandato a S305 pre-flight per evitare context inflation, founder ha riferito toast verde).
> - **Task 2 ✅ CF token cleanup NO-OP** — audit live via `CF_API_TOKEN_READ` (`3e1b247d...mode_fUlL` ha perm `User → API Tokens Read`) ha rivelato:
>   - `cd1221db...` (S301 SuperAdmin zombie) → **GIÀ ASSENTE** (auto-revoke o cleanup precedente)
>   - `1814e6dc...` (S301 marcato zombie `FLUXION-CTO-Claude-Full`) → **RINOMINATO** `FLUXION-Track-B-S28`, attivo, IN USO Track B test env S280s. **NON zombie, MEMORY.md S301 evidence sbagliata.**
>   - Lista finale 5 token tutti legittimi: Deploy-90d, mode_fUlL, Track-B-S28, Cloudflare Agent Token (auto), Workers AI (auto).
>   - **Zero operazioni distruttive eseguite. Track B salvato da audit live pre-action.**
>
> **Pattern S304 (REGOLA #16 research-first PASS + REGOLA #4 critica strutturale PASS)**:
> Memoria S301 marcava ID zombie ma snapshot statico — il token era stato rinominato per riuso Track B. Audit live tokens ha bloccato delete blind che avrebbe rotto Track B test env. **MEMORY.md S301 evidence va corretta in S305 chiusura sessione.**
>
> **Carry-over founder-bound S305 (2/4 task evidence gate)**:
> - Task 3 — FDQ-01 smoke real Stripe + Brevo email delivery (CTO autonomous post Task 1 verify HTTP 200)
> - Task 4 — META-VINCOLO REGOLA #18 founder GUI activate flow + S187 FASE 1 evidence per production_ready claim
>
> ## ⛔ PRE-FLIGHT S305 (≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short`
> 2. `source ~/.claude/.env`
> 3. **CF token capability** (deve restare 4/4 PASS):
>    ```bash
>    curl -sS "https://api.cloudflare.com/client/v4/user/tokens/verify" \
>      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('PASS' if d.get('success') else 'FAIL')"
>    # Expected: PASS (token 3856673a...Deploy-90d active)
>    ```
> 4. **Brevo /v3/account HTTP 200** (verifica Task 1 S304 propagato server):
>    ```bash
>    curl -sS -H "api-key: $BREVO_API_KEY" -w "\nHTTP=%{http_code}\n" https://api.brevo.com/v3/account | head -8
>    # Expected: HTTP=200 + JSON account
>    # Se HTTP=401 unrecognised IP → founder ricontrollare dashboard (toggle non saved or geo IP changed)
>    ```
> 5. **Live tokens audit** (verify no nuovi zombie tra S304→S305):
>    ```bash
>    curl -sS "https://api.cloudflare.com/client/v4/user/tokens" \
>      -H "Authorization: Bearer $CF_API_TOKEN_READ" | python3 -c "
>    import json,sys
>    d=json.load(sys.stdin)
>    for t in (d.get('result') or []):
>        print(t['id'][:10], t.get('status'), '|', t.get('name'))
>    "
>    # Expected: 5 token attivi (Deploy-90d, mode_fUlL, Track-B-S28, Cloudflare Agent Token, Workers AI)
>    ```
>
> ## SCOPE S305 — 2 task carry-over founder-bound + 1 MEMORY.md fix
>
> ### Task 0 — Fix MEMORY.md evidence S301 errata (CTO autonomous, 2 min, FIRST)
>
> MEMORY.md S301 entry afferma `1814e6dc...` = zombie `FLUXION-CTO-Claude-Full` da revocare. **Falso post-audit S304**: il token è stato rinominato `FLUXION-Track-B-S28` ed è in uso Track B. Update MEMORY.md S301+S302+S303 entries per chiarire che `1814e6dc` ≠ zombie.
>
> ### Task 3 — Smoke FDQ-01 Brevo channel real Stripe (CTO autonomous post pre-flight Brevo 200)
>
> Worker già deployato S303 con `BREVO_API_KEY` + `LICENSE_RECOVERY_SECRET` secrets. Worker test env `85d2a2e7-6c70-410c-9227-66b74357dd24` /health 200 OK.
>
> Procedura:
> 1. CTO verify Stripe Payment Link prod success_url → `/api/v1/checkout-success?session_id={CHECKOUT_SESSION_ID}` (Dashboard Stripe → Payment Links → FLUXION Base €497 → URLs).
> 2. Founder action: pagamento real Payment Link prod (base €497) con coupon test 100% + card 4242 4242 4242 4242 + email `fluxion.gestionale@gmail.com`.
> 3. CTO verify post:
>    - `stripe events list --limit 1` → evento `checkout.session.completed`
>    - Worker tail `wrangler tail --env test` → log invocation `/v1/webhooks/stripe` (REGOLA #17 production verify manual smoke)
>    - KV `wrangler kv:key list --env test` → key `session:cs_*` populated
>    - Brevo dashboard `Stats → Emails sent` → +1 con subject "FLUXION License" o equivalente
>    - Inbox `fluxion.gestionale@gmail.com` → verify delivery + payload+signature copy-paste link
> 4. Evidence file: `~/venture-os/state/fdq-01-smoke-S305.json` (timestamp + stripe_event_id + brevo_msgid + kv_key + recovery_url).
>
> ### Task 4 — META-VINCOLO REGOLA #18 (FOUNDER browser+CTO co-validate)
>
> Validate-then-implement S289 prompt S187 FASE 1 6-question evidence per production_ready claim:
> 1. Founder Stripe Payment Link reale → /success/ → activate email flow (GUI app iMac fisicamente al Mac, REGOLA #12 Keychain unlock)
> 2. Founder copy payload + signature da email Brevo → wizard activation app
> 3. CTO verify post: `gate-state-FLUXION.json` chain_map ring 6 attivazione_app evidence + `production_ready_meta_validation_passed=True`
> 4. GO Luke obbligatorio prima di chain_map promote o claim production-ready
>
> ## EVIDENCE GATE S305 closure verde
>
> - [ ] Pre-flight 5/5 PASS (git + env + CF token + Brevo HTTP 200 + tokens audit)
> - [ ] MEMORY.md fix S301 evidence Track-B-S28 corretto
> - [ ] FDQ-01 smoke real PASS: Stripe webhook → Brevo email delivered → inbox confermata (evidence JSON)
> - [ ] META-VINCOLO REGOLA #18 founder GO Luke documentato MEMORY.md S306
>
> ## FILES S304 modificati
>
> - `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file, S305 scope)
> - MEMORY.md NOT modified S304 (context budget 47%, fix deferred to S305 Task 0)
>
> ## CONTEXT BUDGET S304
>
> Boot ~22% + lavoro ~25% (audit + WebSearch label UI verification + pre-flight) = ~47% close. **Closing ordinato rispetto context-budget-gate.md** (sotto 50% BLOCK_CRITICAL per MEMORY.md edit).
>
> ## REGOLE ATTIVE + applicate S304
>
> - REGOLA #4 Critica strutturale — **applicata S304 PRE-DELETE PASS** (audit live ha rivelato Track B rinominato, blocked operazione distruttiva)
> - REGOLA #14 CTO autonomous test+fix (S269)
> - REGOLA #15 NO A/B questions (S274) — **applicata S304** (decisione closing vs continue Task 3 = scope decision motivata)
> - REGOLA #16 Research-first (S281) — **applicata S304 PASS** (audit live tokens prima di delete blind)
> - REGOLA #18 META-VINCOLO validate-then-implement (S289)
> - REGOLA #19 Persist segreti immediato (S300)
> - REGOLA #20 CF token screenshot + capability test mandatory (S301)
>
> ## Lezione S304 (nuovo pattern candidato REGOLA #21)
>
> **MEMORY.md token-by-ID snapshot ≠ token-live-state**. Token possono essere **rinominati/riscoperti** senza modificare ID. Cleanup operations DEVONO sempre re-auditare lista live (read perm necessario) PRIMA di delete. Pattern audit-before-destroy: anche se memoria è recente (3 giorni), token lifecycle non statico. Trigger save MEMORY.md S305 chiusura sessione se confermato cross-pattern.
