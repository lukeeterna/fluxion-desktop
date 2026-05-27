# Prompt ripartenza S303 — Token CF Write OK (S302 done), procedere carry-over S301: Brevo IP, wrangler deploy, landing FBUG-LM-01, META-VINCOLO REGOLA #18

> ## ⚡ S302 OUTCOME (closed verde, 4/4 capability test PASS)
>
> Nuovo token CF Write `FLUXION-CTO-Deploy-90d` creato e validato:
> - **Token ID**: `3856673a7ec292a464fd2fda89a1db78`
> - **Scopi**: Workers Scripts Edit + Workers KV Storage Edit + Pages Edit + Workers Tail Read
> - **Resource**: Account-specific (CF_ACCOUNT_ID terminante `...adf8`)
> - **TTL**: 90 giorni
> - **Persistito** in `~/.claude/.env`: `CF_API_TOKEN`, `CLOUDFLARE_API_TOKEN`, `CF_API_TOKEN_READ` (diagnosi), `CF_ACCOUNT_ID`
> - **Backup pre-write**: `~/.claude/.env.backup-pre-cf-write-20260527-103459`
>
> **Token diagnosi read-only S302**: `Fluxion_CTO_mode_fUlL` id `3e1b247d84192c17d9bf3cb55bb309b4` (resta in env come `CF_API_TOKEN_READ`).
>
> **File diagnosi**: `cf_permission_groups.json` (76KB, 360 entries) + `cf_permissions_map.md` (34KB, mapping) in repo root FLUXION. Tenere o gitignore (tua scelta — sono read-only senza segreti).
>
> ## ⛔ PRE-FLIGHT S303 (≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short`
> 2. `source ~/.claude/.env`
> 3. **CF token capability matrix nuovo Write token**:
>    ```bash
>    for ep in \
>      "user/tokens/verify" \
>      "accounts/${CF_ACCOUNT_ID}/pages/projects" \
>      "accounts/${CF_ACCOUNT_ID}/storage/kv/namespaces" \
>      "accounts/${CF_ACCOUNT_ID}/workers/scripts"; do
>      r=$(curl -sS "https://api.cloudflare.com/client/v4/$ep" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('PASS' if d.get('success') else 'FAIL')")
>      echo "  $ep → $r"
>    done
>    ```
>    MUST: 4/4 PASS (validato 2026-05-27 ore 10:34 S302).
>
> 4. **Brevo IP check** (carry-over S301 step 1):
>    ```bash
>    curl -sS -H "api-key: $BREVO_API_KEY" https://api.brevo.com/v3/account | python3 -m json.tool | head -5
>    # IF "unauthorized" + "unrecognised IP 151.72.29.96" → IP allowlist Brevo ancora ON
>    ```
>    Se 401 IP → founder dashboard Brevo → Settings → Security → "Restrict API access by IP" OFF + verify toast verde.
>
> 5. **Cleanup token zombie** (founder dashboard CF, MANUALE):
>    - Delete `1814e6dcf03313a9fe5da45be2833521` (FLUXION-CTO-Claude-Full, S300 incompleto)
>    - Delete `cd1221db034af8cbf959e5824b97b7df` (FLUXION-CTO-Claude-SuperAdmin, S301 scope vuoto)
>    - Mantenere SOLO: `3856673a...` (Deploy 90d) + `3e1b247d...` (read-only diagnosi)
>
> ## SCOPE S303 — task carry-over ordine ROI
>
> ### Task 1 — Wrangler deploy validate (15 min)
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> npx wrangler whoami  # MUST show token con account + 4 permessi
> npx wrangler deploy --env test --dry-run  # validate manifest
> ```
> Se OK → procedi Task 2. Se FAIL → diagnosi log wrangler + check env CF_API_TOKEN export attiva.
>
> ### Task 2 — Landing CF Pages re-deploy FBUG-LM-01 (S287 fix `marketing_opt_in`→`consenso_marketing`)
> Verifica auto-deploy CF dashboard `fluxion-landing` git-connected, oppure:
> ```bash
> cd /Volumes/MontereyT7/FLUXION/landing
> npx wrangler pages deploy . --project-name=fluxion-landing
> ```
> Verifica: `curl -sS https://fluxion-landing.pages.dev/ | grep -c consenso_marketing` MUST ≥1.
>
> ### Task 3 — Smoke E2E FDQ-01 Brevo channel post-IP-disable
> Solo dopo pre-flight 4 PASS (Brevo IP allowlist OFF):
> ```bash
> cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
> npx wrangler secret put BREVO_API_KEY --env test  # paste BREVO_API_KEY da env
> npx wrangler deploy --env test
> # Re-run smoke FDQ-01 con Stripe Payment Link coupon 100% + email Resend owner fluxion.gestionale@gmail.com
> ```
>
> ### Task 4 — META-VINCOLO REGOLA #18 (founder browser test, NOT autonomous)
> Validate-then-implement S289: founder reale browser test Stripe Payment Link → /success/ → activate flow GUI app iMac → REGOLA #12 Keychain unlock. Embed prompt S187 FASE 1 6-question evidence + GO Luke obbligatorio prima di production_ready claim qualunque.
>
> ## EVIDENCE GATE (S303 closure verde criteri)
>
> - [ ] CF token 4/4 capability test PASS (auto)
> - [ ] Brevo `/v3/account` HTTP 200 (post IP-disable)
> - [ ] `wrangler whoami` mostra account corretto
> - [ ] Landing CF Pages deploy verificato con `consenso_marketing` in HTML live
> - [ ] FDQ-01 Brevo: email reale ricevuta su fluxion.gestionale@gmail.com (founder conferma inbox)
> - [ ] META-VINCOLO REGOLA #18: founder GO Luke via prompt S187 evidence reale
>
> ## CONTEXT BUDGET
>
> Boot stimato ~22% (CLAUDE.md global+project + 6 rules + VOS inject + MEMORY.md). Headroom ~78%.
> Task 1-3 sono comandi specifici, sub-30% budget. Task 4 META-VINCOLO è founder-bounded.
>
> ## REGOLE ATTIVE (riassunto carry-over)
>
> - REGOLA #14 CTO autonomous test+fix (S269)
> - REGOLA #15 NO A/B questions (S274)
> - REGOLA #16 Research-first (S281)
> - REGOLA #18 META-VINCOLO validate-then-implement (S289 founder-input)
> - REGOLA #19 Persist segreti immediato (S300)
> - REGOLA #20 CF token screenshot + capability test mandatory (S301) — **applicata e PASS S302**
