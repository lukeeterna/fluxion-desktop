# Prompt ripartenza S301 — Brevo IP allowlist + CF token Pages:Edit re-verify + landing deploy + META-VINCOLO REGOLA #18

> ## ⛔ PRE-FLIGHT (≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short` → solo `.claude/NEXT_SESSION_PROMPT.*` + `tools/VectCutAPI` submodule (ignorabile)
> 2. `cd fluxion-proxy && npx tsc --noEmit` → MUST 0 errors
> 3. `cd fluxion-proxy && npx vitest run` → MUST 36/36 PASS in <6s
> 4. `curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health` → `{"status":"ok"}`
> 5. **Brevo IP check** (auto-detect blockers):
>    ```bash
>    KEY=$(grep '^BREVO_API_KEY=' ~/.claude/.env | cut -d'=' -f2)
>    curl -sS -H "api-key: $KEY" https://api.brevo.com/v3/account | python3 -m json.tool | head -5
>    # IF "unauthorized" + "unrecognised IP" → bloccante S301 step 1
>    # IF success: {"email":"...","firstName":...} → procedi step 3 wrangler upload
>    ```
> 6. **CF token Pages check**:
>    ```bash
>    source ~/.claude/.env
>    curl -sS "https://api.cloudflare.com/client/v4/accounts/22ddff3a4ef544511523a841b3dcadf8/pages/projects" \
>      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('success'))"
>    # IF False → bloccante S301 step 4 (user re-verify token salvato)
>    # IF True → procedi step 5 wrangler pages deploy
>    ```

---

## Stato chiusura S300 (CLOSED ARANCIONE — Brevo HTTP key generata + persistita, IP allowlist + CF token Pages NON propagati server-side)

### Done S300 (autonomous CTO)

1. **Pre-flight 5/5 PASS** (git, vitest 36/36, worker health, tsc 0, smoke FDQ-01 5/5)
2. **REGOLA #19 nuova memorizzata** (`feedback_persist_secrets_immediately.md`): segreti forniti da Luke → persist mode 600 + alias `~/.claude/.env` PRIMA di usare. MAI re-chiedere: grep esaustivo prima. Se perso il riferimento ammetti errore, NON dire "non l'hai fornito".
3. **Brevo HTTP API key generata** (founder) + persistita (`~/.claude/.env` `BREVO_API_KEY=xkeysib-...` 89 chars). 3 tentativi falliti pre-correct path (SMTP key generata 2x per confusione UI Brevo tab `/keys/smtp` vs `/keys/api`).
4. **CF token Pages:Edit founder action** completata in UI ma NON propagata server-side (verify post-100s poll: `success=false` 10000 Auth error). Token attivo confirmed `FLUXION-CTO-Claude-Full` via fingerprint capability test (KV+Workers Scripts+D1 OK).
5. **TextEdit /tmp/brevo_key.txt** workflow paste/save (mode 600).

### Files modificati S300

- `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/feedback_persist_secrets_immediately.md` (NEW)
- `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md` (+1 riga REGOLA #19)
- `~/.claude/.env` (+1 var `BREVO_API_KEY` mode 600)
- `/tmp/brevo_key.txt` (Brevo HTTP key persistita)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (S301 scope)

### Critica strutturale S300 (REGOLA #4)

1. **Pattern UI Brevo "Generate SMTP Key" default**: la pagina `/settings/keys/smtp` ha button principale "Generate SMTP key" prominent + tab secondario "API keys & MCP" piccolo. Founder ha cliccato 2x button principale (genera SMTP `xsmtpsib-` 90 chars) prima di trovare tab API. Lesson: SE Brevo serve di nuovo, **link diretto da memoria** `https://app.brevo.com/settings/keys/api` E **istruzione esplicita** "click tab 'API keys & MCP' SUBITO, NON cliccare button Generate principale".
2. **Pattern propagazione UI → server** (CF + Brevo entrambi): founder dichiara "fatto" su UI ma capability test API rivela change NON committed server-side. Possibile causa: (a) modal "Continue to summary" → "Update token" step finale mancato, (b) session expired durante navigation, (c) toggle Brevo IP allowlist diverso da quello atteso. Mitigation S301: **screenshot della schermata di conferma post-save** prima di chiudere, oppure F5 page e re-verify visualmente la modifica.
3. **Test diretto MacBook → Brevo IP-blocked by design**: anche se IP allowlist disabilitato, CF Workers usa pool IP rotanti → test smoke email post deploy DEVE essere fatto via `wrangler tail` log durante POST `/v3/smtp/email` da worker, NON `curl` diretto dal MacBook. Pre-deploy `GET /v3/account` da MacBook serve solo a validare formato key.
4. **3 round failed Brevo key paste**: 2 SMTP keys + 1 API key totali. Pattern noto S297 stesso identico bug. Memorizzata in `feedback_persist_secrets_immediately.md` come reference per future Brevo onboarding, ma manca embed esplicito in pre-action-check skill su keyword "brevo" → suggerimento per skill update.

### Pending S301 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Brevo IP allowlist disable verify | founder | Vai su https://app.brevo.com/security/authorised_ips → cerca toggle "**Restrict API access by IP**" → mettilo **OFF** → salva → screenshot conferma post-save. Se toggle non c'è, opzione fallback "Add IP" → `0.0.0.0/0` (allow all). |
| HIGH | CF token Pages:Edit re-verify | founder | Vai su https://dash.cloudflare.com/profile/api-tokens → click **FLUXION-CTO-Claude-Full** → verifica presenza riga `Account | Cloudflare Pages | Modifica` + sezione "Risorse account" = `Includi: Tutti gli account` OPPURE `Account specifici` con account selezionato → "Continua al riepilogo" → "**Aggiorna token**" → screenshot conferma toast verde post-save. |
| HIGH | CTO Brevo smoke + `wrangler secret put` + worker re-deploy | CTO | Post-founder IP fix: `curl /v3/account` MUST 200 → `cd fluxion-proxy && echo "$BREVO_API_KEY" \| npx wrangler secret put BREVO_API_KEY --env test` → `npx wrangler deploy --env test` → re-run smoke FDQ-01 verify Brevo channel via `wrangler tail --env test` durante smoke. |
| HIGH | CTO landing CF Pages re-deploy FBUG-LM-01 | CTO | Post-founder CF token fix: `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --commit-dirty=true --branch=main` → verify `curl -sS https://fluxion-landing.pages.dev/ \| grep -c consenso_marketing` MUST 1 (NON `marketing_opt_in`). |
| HIGH | META-VINCOLO REGOLA #18 — Founder REAL browser test FDQ-01 | CTO + founder GO | https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000 (Base Payment Link S297) → coupon `dcwmOPFa` (100%) → card 4242 → email `fluxion.gestionale@gmail.com` → redirect `/success/cs_test_xxx`. Verifiche: (a) HTML inline payload+sig+recovery, (b) email Gmail subject **delivered via Brevo** (NON Resend), (c) recovery link copy → JSON ok. CTO assist `wrangler tail --env test` + D1 query post-test. |
| MED | KV lead audit pre/post FBUG-LM-01 | CTO | Post CF Pages re-deploy: `wrangler kv key list --binding LEAD_MAGNET_KV` → identify lead `consent_text=''` → ROI compliance retro-fit. |
| LOW | Cleanup Brevo SMTP keys generate per errore | founder | https://app.brevo.com/settings/keys/smtp → cancella `fluxion-proxy-test` SMTP key (NON serve, generata 2x per confusione UI) |
| LOW | `feedback_persist_secrets_immediately.md` → embed pattern Brevo in pre-action-check skill | CTO | 10min, update `~/.claude/skills/pre-action-check/SKILL.md` con keyword "brevo" → istruzioni dirette tab API. |

### Vincoli S301 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: Brevo `/v3/account` 200 PRIMA di `wrangler secret put` (no assumption "IP fixato").
- **REGOLA #14/#15/#16 CTO autonomous**: founder touch SOLO su (a) Brevo IP disable, (b) CF token re-save, (c) Stripe browser test. Tutto il resto CTO.
- **REGOLA #18 META-VINCOLO**: production_ready NON declaration senza founder browser test reale.
- **REGOLA #19 NUOVA**: secrets `xkeysib-` Brevo già in `~/.claude/.env` mode 600 + `/tmp/brevo_key.txt` (cleanup post-success non necessario, file mode 600).
- **CLOSING_ONLY ≥70%**: monitor `/context` ogni 5 tool call.

### Pre-flight env check S301

```bash
zsh -c 'source ~/.claude/.env 2>/dev/null
for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET (len=${#VAL})" || echo "  $V: UNSET"
done'
# expect ALL SET, BREVO_API_KEY len=89
```

### Carry-over backlog (defer post-S301)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** card `4000002500003155` real browser founder
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** (S289 HIGH)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** + **BUG-FATT-5** toast z-index (deferred S267)
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** (S286 brand-guardian + visual-storyteller)
- **Resend custom domain** (€10/anno + DNS records) — alternativa a Brevo
- **NODE-ED25519 → Ed25519 standard migration** (S291/S299 carry-over)
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...`
- **pre_write_gate.py refactor**: regex whole-word + escludere `.test.ts`/`.spec.ts`

### Tabella anelli chain post-S300

Identica a S299 (zero promote in S300):

| Ring | Stato | Evidence |
|------|-------|----------|
| 1 landing→signup | VERIFIED backend, **broken UI** (FBUG-LM-01 deploy gap) | curl OK / UI `marketing_opt_in` MISMATCH |
| 2 checkout_stripe | VERIFIED (S285) |
| 3 pagamento_confermato | VERIFIED (S285) |
| 4 licenza_generata | VERIFIED test smoke (S299) |
| 5 email_consegna | VERIFIED test smoke Resend (S297) | Brevo PROD gate S301 (IP allowlist + smoke email) |
| 6 attivazione_app | VERIFIED smoke S298 + S289 founder GUI | META-VINCOLO REGOLA #18 founder REAL browser test pending |
| 7 sales_agent_wa | MISSING (Phase 12) |

**production_ready_PROD = FALSE** (META-VINCOLO REGOLA #18: smoke synthetic ≠ real browser test + landing UI FBUG-LM-01 deploy gap + Brevo channel non-attivo).

Ripartenza S301 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267).
