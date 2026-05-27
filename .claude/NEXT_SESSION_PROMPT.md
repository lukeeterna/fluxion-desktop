# Prompt ripartenza S302 — CF SuperAdmin token recreate (screenshot mandatory) + S301 carry-over + Brevo IP + landing deploy + META-VINCOLO REGOLA #18

> ## ⛔ PRE-FLIGHT (≤30s)
>
> 1. `cd /Volumes/MontereyT7/FLUXION && git status --short` → solo `.claude/NEXT_SESSION_PROMPT.*` + `tools/VectCutAPI` (ignorabile)
> 2. `cd fluxion-proxy && npx tsc --noEmit` → MUST 0 errors
> 3. `cd fluxion-proxy && npx vitest run` → MUST 36/36 PASS in <6s
> 4. `curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health` → `{"status":"ok"}`
> 5. **CF token capability matrix** (auto-detect blockers):
>    ```bash
>    source ~/.claude/.env
>    for ep in \
>      "user/tokens/verify" \
>      "accounts/22ddff3a4ef544511523a841b3dcadf8/pages/projects" \
>      "accounts/22ddff3a4ef544511523a841b3dcadf8/storage/kv/namespaces" \
>      "accounts/22ddff3a4ef544511523a841b3dcadf8/workers/scripts" \
>      "accounts/22ddff3a4ef544511523a841b3dcadf8/r2/buckets" \
>      "user/tokens/permission_groups"; do
>      r=$(curl -sS "https://api.cloudflare.com/client/v4/$ep" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('PASS' if d.get('success') else 'FAIL')")
>      echo "  $ep → $r"
>    done
>    ```
>    - Token attuale `1814e6dcf03313a9fe5da45be2833521` (FLUXION-CTO-Claude-Full) → PASS solo su KV+Workers Scripts+self-verify. Pages/R2/Tokens FAIL atteso fino a S302 SuperAdmin success.
> 6. **Brevo IP check**:
>    ```bash
>    KEY=$(grep '^BREVO_API_KEY=' ~/.claude/.env | cut -d'=' -f2)
>    curl -sS -H "api-key: $KEY" https://api.brevo.com/v3/account | python3 -m json.tool | head -5
>    # IF "unauthorized" + "unrecognised IP" → bloccante S301 step 1 ancora attivo
>    ```

---

## Stato chiusura S301 (CLOSED ARANCIONE — CF SuperAdmin token creato ma scope account VUOTO, pattern UI summary≠commit confermato 3x, vecchio token ripristinato)

### Done S301 (autonomous CTO)

1. **Pre-flight 4/6 PASS** (git, tsc 0, vitest 36/36 in 3.63s, worker health). 2 BLOCCANTI carry-over S300 confermati: Brevo IP + CF token Pages denied server-side.
2. **CF token diagnosi tecnica** completata: `1814e6dc...` (FLUXION-CTO-Claude-Full) attivo (self-verify status:active) ma scope `Cloudflare Pages:Edit` non committed server-side → `10000 Authentication error` su `/pages/projects` mentre `/storage/kv/namespaces` PASS. Token globalmente valido (control test KV+Workers Scripts).
3. **WebFetch fonti ufficiali** estratti permessi CF (account+zone+user) verbatim da `developers.cloudflare.com/fundamentals/api/reference/permissions/` + raw mdx `cloudflare-docs/production/src/content/partials/fundamentals/zone-permissions-table.mdx`. Lista 25 permessi target documentata per recreation.
4. **Doc Cloudflare verificata** policy parent-child token: template `"Create Additional Tokens"` *"can create tokens with access to any of a user's resources"* → NO escalation limit, conferma path founder one-time → CTO autonomous future.
5. **Founder tentativo #1**: modifica token esistente `1814e6dc` aggiungendo Pages+R2+Token API → 3/4 nuovi permessi denied server (10000) + Pages ancora denied.
6. **Founder tentativo #2**: creazione NUOVO token `cd1221db034af8cbf959e5824b97b7df` (`FLUXION-CTO-Claude-SuperAdmin`, TTL 2030) → self-verify PASS, ma 7/9 endpoint account-scoped FAIL + `/accounts` ritorna `result:[]` → **scope account VUOTO server-side**.
7. **REGOLA #20 nuova** memorizzata (`feedback_cloudflare_token_screenshot_mandatory.md`): pattern UI summary ≠ server commit confermato 3x (S300 + S301 x2). Procedura screenshot mandatory + capability test PRIMA persist `~/.claude/.env`.
8. **Env restored**: `~/.claude/.env` ripristinato da backup `~/.claude/.env.backup-pre-superadmin-20260527-091830` → vecchio token `1814e6dc` attivo, KV/Workers Scripts PASS. Token zombie `cd1221db` persiste in dashboard CF (cleanup S302).

### Files modificati S301

- `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/feedback_cloudflare_token_screenshot_mandatory.md` (NEW)
- `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md` (+REGOLA #20 + stato S301)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (S302 procedura screenshot mandatory)
- `~/.claude/.env` (modificato + ripristinato) + `~/.claude/.env.backup-pre-superadmin-20260527-091830` (backup conservato)
- `/tmp/cf_superadmin_token.txt` (valore token zombie persiste, mode 600)

### Critica strutturale S301 (REGOLA #4)

1. **Pattern UI summary ≠ commit ricorre 3x = root cause processo**: NON è bug Cloudflare, è gap UX form CF dashboard combinato con assenza checklist visiva founder-side. Mitigation deterministica: skill `pre-action-check` arricchita con keyword `cloudflare token` → injection inline reminder "screenshot toast verde mandatory, NO riepilogo summary pre-commit". Senza enforcement skill, pattern si ripeterà S302.
2. **Token zombie cleanup richiede catch-22**: revocare `cd1221db` via API richiede token con `User → API Tokens Write` … che è proprio il permesso che il token zombie non ha + il vecchio `1814e6dc` non ha. Solo path: founder GUI cleanup OPPURE nuovo SuperAdmin S302 includere User:API Tokens Write + revoke programmatico subito dopo persist.
3. **3 tentativi falliti = ROI negativo continuare via Founder GUI**: alternativa zero-cost = `wrangler` CLI con OAuth interactive `wrangler login` (browser flow gestito da CF, no token manuale). Trade-off: token OAuth wrangler-managed in `~/.wrangler/config/default.toml` non visibile a curl directe → richiede wrapping shell per operazioni REST API. Carry-over decision S302 SE founder tentativo #3 fallisce.
4. **Brevo bloccante ortogonale**: non risolto in S301 (no founder action su Brevo richiesta). Resta `401 unrecognised IP` → blocca smoke FDQ-01 Brevo channel + production_ring 5 email_consegna gate.

### Pending S302 (priority order — minimal touch founder)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | **Cleanup token zombie** `cd1221db` | founder | https://dash.cloudflare.com/profile/api-tokens → click 3 punti accanto a `FLUXION-CTO-Claude-SuperAdmin` → "Elimina" → conferma. Screenshot toast verde "Token eliminato". |
| HIGH | **Recreate SuperAdmin token** con procedura screenshot mandatory | founder | Vai a https://dash.cloudflare.com/profile/api-tokens → Crea Token → **Custom token** (non template). Fill form completo (vedi sezione "Procedura founder screenshot mandatory" sotto). Dopo "Continua al riepilogo" → controlla che riepilogo mostri ESATTAMENTE l'account scope + 25 permessi → **click bottone "Crea Token"** (NON solo continuare) → attendi pagina post-creazione che mostra il VALORE token + bottone "Copia" → screenshot di QUESTA pagina (NON del riepilogo precedente). Incolla token in TextEdit `/tmp/cf_superadmin_token.txt` mode 600 (CTO aprirà file). Dichiara done. |
| HIGH | CTO capability test full-scope 9 endpoint + persist | CTO | Post-founder paste: self-verify, /accounts result≠[], /pages/projects PASS, /user/tokens/permission_groups PASS, KV PASS, Workers Scripts PASS, R2 PASS, D1 PASS, Workers Tail PASS. Se 9/9 PASS → persist `~/.claude/.env` `CLOUDFLARE_API_TOKEN` + backup + revoke vecchio `1814e6dc` via API + revoke zombie se persiste. |
| HIGH | **Brevo IP allowlist disable** | founder | https://app.brevo.com/security/authorised_ips → toggle "Restrict API access by IP" → OFF → screenshot toast conferma. |
| HIGH | CTO Brevo smoke + `wrangler secret put` + worker re-deploy | CTO | Post-Brevo fix: `curl /v3/account` MUST 200 → `echo "$BREVO_API_KEY" \| npx wrangler secret put BREVO_API_KEY --env test` → `npx wrangler deploy --env test` → smoke FDQ-01 verify Brevo via `wrangler tail --env test`. |
| HIGH | CTO landing CF Pages re-deploy FBUG-LM-01 | CTO | Post-CF SuperAdmin: `cd landing && npx wrangler pages deploy . --project-name=fluxion-landing --commit-dirty=true --branch=main` → verify `curl -sS https://fluxion-landing.pages.dev/ \| grep -c consenso_marketing` MUST 1. |
| HIGH | META-VINCOLO REGOLA #18 — Founder REAL browser test FDQ-01 | CTO + founder GO | https://buy.stripe.com/test_bJe7sM19ZdWegU727E24000 (Base Payment Link) → coupon `dcwmOPFa` (100%) → card 4242 → email `fluxion.gestionale@gmail.com` → redirect `/success/cs_test_xxx`. Verifiche: (a) HTML inline payload+sig+recovery, (b) email Gmail subject **delivered via Brevo**, (c) recovery link copy → JSON ok. CTO assist `wrangler tail --env test` + D1 query post-test. |
| MED | Skill `pre-action-check` arricchita keyword `cloudflare token` | CTO | `~/.claude/skills/pre-action-check/SKILL.md` → aggiungi sezione "Cloudflare token modify/create" con istruzioni screenshot mandatory toast verde + URL diretto. ~15min. |
| MED | KV lead audit pre/post FBUG-LM-01 | CTO | Post landing deploy: `wrangler kv key list --binding LEAD_MAGNET_KV` → identify lead `consent_text=''` → ROI compliance retro-fit. |
| LOW | Cleanup Brevo SMTP keys duplicate | founder | https://app.brevo.com/settings/keys/smtp → cancella SMTP key generata 2x per errore. |

---

## Procedura founder screenshot mandatory (CF Token SuperAdmin recreate)

### Step 1 — Apri form Custom Token
- URL: https://dash.cloudflare.com/profile/api-tokens
- Click pulsante blu **"Crea Token"** in alto a destra
- Scroll fino in fondo → riga **"Crea token personalizzato"** → click **"Get started"** / **"Inizia"** a destra

### Step 2 — Compila form Custom Token (NON template Create Additional Tokens, serve scope esteso)

**Nome token**: `FLUXION-CTO-Claude-SuperAdmin-v2`

**Sezione "Autorizzazioni"** (clicca **"+ Aggiungi altro"** per ogni riga, totale **25 righe**):

Account scope (14 righe) — per ognuna selezionare dropdown 1=`Account`, dropdown 2=nome permesso, dropdown 3=`Modifica` (o `Lettura` per Read-only):
1. `Account` | `Cloudflare Pages` | `Modifica`
2. `Account` | `Script Workers` | `Modifica`
3. `Account` | `Archiviazione KV Workers` | `Modifica`
4. `Account` | `Archiviazione R2 Workers` | `Modifica`
5. `Account` | `D1` | `Modifica`
6. `Account` | `Workers Tail` | `Lettura`
7. `Account` | `Workers AI` | `Modifica`
8. `Account` | `Log` | `Modifica`
9. `Account` | `Impostazioni account` | `Lettura`
10. `Account` | `Fatturazione` | `Lettura`
11. `Account` | `Analisi account` | `Lettura`
12. `Account` | `Indirizzi instradamento email` | `Modifica`
13. `Account` | `Queues` | `Modifica`
14. `Account` | `Turnstile` | `Modifica`

Zone scope (7 righe):
15. `Zona` | `DNS` | `Modifica`
16. `Zona` | `SSL e certificati` | `Modifica`
17. `Zona` | `Eliminazione cache` | `Eliminazione` (unica opzione)
18. `Zona` | `Impostazioni zona` | `Modifica`
19. `Zona` | `Zona` | `Lettura`
20. `Zona` | `Route Workers` | `Modifica`
21. `Zona` | `Regole pagina` | `Modifica`

User scope (4 righe):
22. `Utente` | `Token API` | `Modifica`
23. `Utente` | `Token API` | `Lettura`
24. `Utente` | `Dettagli utente` | `Lettura`
25. `Utente` | `Membership` | `Lettura`

**Sezione "Risorse account"** ⚠️ CRITICO (questo è lo step skippato in S301 → scope VUOTO):
- Dropdown 1: `Includi`
- Dropdown 2: `Account specifico`
- Dropdown 3: seleziona **`Gianlucanewtech@gmail.com's Account`** (oppure `combaretrovamiauto-enterprise's Account` se label diversa — è lo stesso account ID `22ddff3a4ef544511523a841b3dcadf8`)

**Sezione "Risorse zona"**:
- Dropdown 1: `Includi`
- Dropdown 2: `Tutte le zone di un account`
- Dropdown 3: seleziona stesso account sopra

**Sezione "Filtro indirizzi IP client"**: lascia vuoto

**Sezione "TTL"**: lascia entrambi i campi data vuoti (= no expiry)

📸 **SCREENSHOT #1**: della pagina form completa con TUTTI i 25 permessi + Account Resources visibili. Incollalo in chat PRIMA di cliccare Continua.

### Step 3 — Riepilogo pre-commit

Click **"Continua al riepilogo"** in basso.

Pagina riepilogo mostra:
- Nome token
- Lista permessi (verifica = 25 voci)
- Account/Zone resources (verifica account selezionato)

📸 **SCREENSHOT #2**: del riepilogo completo. Incollalo in chat.

### Step 4 — Commit finale (questo è lo step skippato S301)

Click **"Crea Token"** (bottone blu in fondo al riepilogo, NON "Modifica" o "Indietro").

Pagina post-creazione mostra:
- Titolo: **"Token API creato con successo"** o simile
- Riquadro con il **valore token** in mono-spazio (~50-90 chars, prefix `cfut_` o simile)
- Bottone **"Copia"** accanto al token
- Avviso: "Questo token verrà mostrato solo ora"

📸 **SCREENSHOT #3** ⚠️ CRITICO: della pagina post-creazione con valore token visibile. Incollalo in chat.

### Step 5 — Paste in TextEdit

Quando dichiari done, CTO esegue:
```bash
touch /tmp/cf_superadmin_token_v2.txt && chmod 600 /tmp/cf_superadmin_token_v2.txt && open -a TextEdit /tmp/cf_superadmin_token_v2.txt
```
Incolla token nel file aperto → CMD+S → dichiara `paste done`.

CTO poi: capability test 9 endpoint, se 9/9 PASS → persist env, revoke vecchio token, procedi carry-over.

---

## Vincoli S302 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: capability test 9 endpoint PRIMA di persist `~/.claude/.env`. NO assumption "scope OK".
- **REGOLA #14/#15/#16 CTO autonomous**: founder touch SOLO su (a) cleanup zombie + recreate token CON SCREENSHOTS, (b) Brevo IP disable, (c) Stripe browser test finale. Tutto il resto CTO.
- **REGOLA #18 META-VINCOLO**: production_ready NON declaration senza founder browser test reale.
- **REGOLA #20 NUOVA**: screenshot post-toast verde mandatory + capability test multi-scope PRIMA persist `~/.claude/.env`. NO fiducia su dichiarazione "fatto" founder senza screenshots.
- **CLOSING_ONLY ≥70%**: monitor `/context` ogni 5 tool call.

## Pre-flight env check S302

```bash
zsh -c 'source ~/.claude/.env 2>/dev/null
for V in CLOUDFLARE_API_TOKEN CLOUDFLARE_API_TOKEN_ID STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET (len=${#VAL})" || echo "  $V: UNSET"
done'
# expect: CLOUDFLARE_API_TOKEN SET (token corrente 1814e6dc, post-S302 sostituito)
# expect: BREVO_API_KEY SET len=89
# expect: STRIPE_TEST_SECRET_KEY SET, RESEND_TEST_KEY SET, STRIPE_WEBHOOK_SECRET_TEST SET
```

## Carry-over backlog (defer post-S302)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card
- **FDQ-02 SCA EU 3DS** card `4000002500003155` real browser founder
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-ACTIVATE-BY-EMAIL-SIGNED-ED25519** (S289 HIGH)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** + **BUG-FATT-5** toast z-index (deferred S267)
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** (S286 brand-guardian + visual-storyteller)
- **Resend custom domain** (€10/anno + DNS records, post-SuperAdmin DNS:Edit) — alternativa a Brevo
- **NODE-ED25519 → Ed25519 standard migration** (S291/S299 carry-over)
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...`
- **pre_write_gate.py refactor**: regex whole-word + escludere `.test.ts`/`.spec.ts`

## Tabella anelli chain post-S301

Identica a S300 (zero promote in S301):

| Ring | Stato | Evidence |
|------|-------|----------|
| 1 landing→signup | VERIFIED backend, **broken UI** (FBUG-LM-01 deploy gap) | curl OK / UI `marketing_opt_in` MISMATCH |
| 2 checkout_stripe | VERIFIED (S285) |
| 3 pagamento_confermato | VERIFIED (S285) |
| 4 licenza_generata | VERIFIED test smoke (S299) |
| 5 email_consegna | VERIFIED test smoke Resend (S297) | Brevo PROD gate S302 (IP allowlist + smoke email) |
| 6 attivazione_app | VERIFIED smoke S298 + S289 founder GUI | META-VINCOLO REGOLA #18 founder REAL browser test pending |
| 7 sales_agent_wa | MISSING (Phase 12) |

**production_ready_PROD = FALSE** (META-VINCOLO REGOLA #18: smoke synthetic ≠ real browser test + landing UI FBUG-LM-01 deploy gap + Brevo channel non-attivo + CF SuperAdmin token pending).

Ripartenza S302 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267).
