# Prompt ripartenza S296 — Brevo swap + email body update + deploy test + smoke E2E

> ## META-VINCOLO S296 (S294 decisione architetturale + S295 implementazione core code)
>
> **S294 decisione CTO GO Luke**: License-on-page primary + recovery HMAC + email Brevo backup, deep-link DEFERRED v1.1
> **S295 codice core implementato CLOSED VERDE**: route `/success/:session_id` + `/api/v1/license/:email?token={hmac}` + types update — TS PASS 0 errori
> **GATE founder S296 (max 10 min)**:
>   1. Brevo signup → API key generation → comunicare a CTO per `wrangler secret put BREVO_API_KEY --env test`
>   2. Stripe Dashboard Payment Link test → success_url = `https://fluxion-proxy-test.gianlucanewtech.workers.dev/success/{CHECKOUT_SESSION_ID}`
>
> **MAI dichiarare ring VERIFIED in prod** senza nuovo set 3 test reali letti da Luke (REGOLA #18 META-VINCOLO):
> - FDQ-01 prod: card 4242 → checkout sandbox prod → redirect success page → licenza visibile inline + recovery link funzionante
> - FSAF-05 prod: replay webhook prod 2x → 1 licenza + 1 delivery + D1 count invariato + idempotent_replay=true
> - Tauri activate-by-payload FE: estrai license_payload+signature da success page copy → `invoke('verify_license_signature_v1')` → activation success

---

## Stato chiusura S295 (CLOSED VERDE — code core delivery licenza zero-cost implementato + TS 0 err)

### Done S295

1. **Pre-flight S295 PASS 4/5**:
   - ✅ Env vars 4/4 SET (CLOUDFLARE_API_TOKEN, STRIPE_TEST_SECRET_KEY, RESEND_TEST_KEY, STRIPE_WEBHOOK_SECRET_TEST)
   - ❌ BREVO_API_KEY UNSET (founder gate Brevo signup)
   - ✅ Worker prod+test entrambi `health=ok`
   - ✅ Keypair S290 ENTRAMBI persistiti

2. **Verifica architettura existente (research-first REGOLA #16)**:
   - Stripe Checkout creation = **Stripe Payment Link Dashboard** (grep `success_url|sessions.create|payment_link` → 0 match in code, 4 match doc/landing/cache). Conferma `success_url` config = founder action Stripe Dashboard, NON code change.
   - `stripe-webhook.ts` S291: D1 webhook_events table contiene `license_payload` + `license_signature` per ogni session_id. Source of truth verificata.
   - Brevo API endpoint raggiungibile `https://api.brevo.com/v3/smtp/email` (401 unauthorized senza key = expected).

3. **Code core implementato (4 file modificati, TS PASS 0 errori)**:
   - **`fluxion-proxy/src/lib/types.ts`**: +`LICENSE_RECOVERY_SECRET?: string` + `BREVO_API_KEY?: string` su `Env` interface (optional per gradual rollout safe).
   - **`fluxion-proxy/src/routes/license-recovery.ts`** (NEW, ~150 righe): GET `/api/v1/license/:email?token={hmac}` — HMAC-SHA256 constant-time verify + D1 lookup most-recent by customer_email + JSON return `{license_id, tier, license_payload, license_signature, issued_at}`. Security headers: Referrer-Policy no-referrer + Cache-Control no-store + X-Content-Type-Options nosniff. Export helper `buildRecoveryUrl(baseUrl, secret, email)` riusato da checkout-success.
   - **`fluxion-proxy/src/routes/checkout-success.ts`** (NEW, ~260 righe): GET `/success/:session_id` — D1 lookup by session_id + render HTML success page (3 sezioni: download macOS + activation by-email + recovery link permanente) + sezione "attivazione manuale" copy-paste payload+signature. Pending page con meta-refresh 5s se D1 row not found (webhook race mitigation). Inline JS clipboard copy buttons. Tema dark consistency con email template esistente.
   - **`fluxion-proxy/src/index.ts`**: +2 import + 2 route registration (`GET /api/v1/license/:email` no-auth + `GET /success/:session_id` no-auth).

4. **Architettura confermata path Claude.ai S294**:
   - Single point of failure ELIMINATED: success_url (best-effort Stripe) + recovery link permanente HMAC + email backup Brevo = ridondanza 3-way.
   - Webhook idempotente FSAF-09 S279 + D1 webhook_events = canonical source of truth invariato.
   - Deep-link `fluxion://` DEFERRED v1.1: scope ridotto -3h, -3 edge case cross-platform (macOS bundle-only test, Windows single-instance plugin obbligatorio, doppio trigger debug).

### Files modificati S295

- `fluxion-proxy/src/lib/types.ts` (Edit +2 optional secrets in Env)
- `fluxion-proxy/src/routes/license-recovery.ts` (NEW ~150 righe)
- `fluxion-proxy/src/routes/checkout-success.ts` (NEW ~260 righe)
- `fluxion-proxy/src/index.ts` (Edit +2 import +2 route)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file — S296 scope)

### Non modificati S295 (deferred S296)

- `fluxion-proxy/src/routes/stripe-webhook.ts` — Brevo swap + email body update (license_payload+signature+recovery URL inline)
- `fluxion-proxy/src/email/sender.ts` — Brevo SMTP swap (sequence emails 2-4 post-purchase non-bloccanti, deferred lower priority)
- `fluxion-proxy/wrangler.toml` — no edit (founder action `wrangler secret put` per LICENSE_RECOVERY_SECRET + BREVO_API_KEY)
- Vitest tests per license-recovery + checkout-success — deferred S296 con context fresco

### Critica strutturale S295 (REGOLA #4)

1. **Assunzione nascosta**: assumo customer in success page legge "salva questo link permanente". Se non lo fa e perde anche email backup (spam folder + cestino svuotato) → recovery link recuperabile via supporto founder con accesso D1 → re-genera HMAC con `LICENSE_RECOVERY_SECRET` + email. Mitigation S296+: documentare procedura supporto in `docs/SUPPORT-RUNBOOK.md`.
2. **30/60/90gg**: KV `purchase:{email}` ha TTL 10 anni. D1 webhook_events permanente. `LICENSE_RECOVERY_SECRET` ROTATION breaking: ruotare secret invalida TUTTI i recovery link distribuiti. Mitigation: secret long-lived (10+ years), backup separato (KV `meta:license_recovery_secret_backup` cifrato), MAI ruotare salvo compromesso.
3. **Pattern errore noti**: D1 lookup customer_email senza index → table scan O(n). Verificare migration 016 (o creare 017): `CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email ON webhook_events(customer_email, created_at DESC)`. Deferred S296.
4. **Sovradimensione checkout-success.ts (~260 righe)**: HTML inline server-side rendered = anti-pattern moderno (preferirebbe SSR template engine). Trade-off: 1 file zero-dep + zero-build, deploy Worker single bundle, no React-server complexity. Accettabile per success page (1 URL, 1 view, no routing). Se cresce > 500 righe → estrarre template HTML in `templates/success.html` import string.

### Pending S296 (priority order)

| Priority | Task | Owner | Note |
|----------|------|-------|------|
| HIGH | Founder Brevo signup + API key | founder | `https://www.brevo.com/free-shop/` → signup Gmail OK 300/giorno permanente → SMTP & API → API Keys → "Generate a new API key" v3 → comunicare a CTO. |
| HIGH | CTO `wrangler secret put BREVO_API_KEY --env test` | CTO | Da `~/.claude/.env` post founder comunicazione, secret upload via stdin (no echo). |
| HIGH | CTO genera + uploada LICENSE_RECOVERY_SECRET | CTO | `openssl rand -hex 32` → `wrangler secret put LICENSE_RECOVERY_SECRET --env test`. Persisti backup in `~/.claude/.env.s295-recovery-secret` mode 600. |
| HIGH | CTO swap Resend→Brevo in stripe-webhook.ts | CTO | `sendConfirmationEmail` function: if `env.BREVO_API_KEY` → POST `https://api.brevo.com/v3/smtp/email` header `api-key: ${key}` body `{sender:{name:'FLUXION',email:'noreply@fluxion-app.brevosend.com'},to:[{email}],subject,htmlContent}`. Else fallback Resend (gradual rollout safe). |
| HIGH | CTO email body update | CTO | `buildEmailHtml` aggiunge sezione "Link di recupero permanente" + sezione "Attivazione manuale" (license_payload + signature copy). Riutilizza `buildRecoveryUrl` import da license-recovery. |
| HIGH | Founder Stripe Dashboard: Payment Link test success_url | founder | `https://dashboard.stripe.com/test/payment-links` → entrambi i Payment Link (Base €497 + Pro €897) → After payment → URL custom = `https://fluxion-proxy-test.gianlucanewtech.workers.dev/success/{CHECKOUT_SESSION_ID}` (placeholder letterale, Stripe sostituisce). |
| HIGH | CTO deploy --env test | CTO | `cd fluxion-proxy && wrangler deploy --env test` (assicurare CLOUDFLARE_API_TOKEN). |
| HIGH | CTO vitest test new routes | CTO | `tests/license-recovery.test.ts` (HMAC compute + D1 mock lookup + 401/403/404 paths). `tests/checkout-success.test.ts` (D1 found vs pending render). Target ≥ 8 test PASS aggregato. |
| HIGH | Smoke test E2E FDQ-01 test | CTO + founder | Founder pagamento card 4242 + coupon test 100% → Stripe redirect a `/success/cs_test_...` → verifica licenza inline + click "Copia payload" → console paste OK + click "Copia link" recovery → apri link in browser nuovo → JSON response 200 + same payload. Backup: email Brevo @brevosend.com ricevuta (founder Gmail). |
| MED | CTO D1 index su customer_email | CTO | Migration 017: `CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email ON webhook_events(customer_email, created_at DESC)`. Apply test + prod. |
| MED | CTO docs supporto runbook | CTO | `docs/SUPPORT-RUNBOOK.md`: aggiungere sezione "Cliente ha perso recovery link" → query D1 + re-compute HMAC + invia manualmente. |
| MED | CTO sender.ts Brevo swap (sequenza F-3) | CTO | Email sequence post-purchase non-bloccante. Stesso pattern stripe-webhook swap. |
| MED | Gate META-VINCOLO REGOLA #18 prod | CTO + founder GO | 3 test reali (FDQ-01 prod, FSAF-05 prod, Tauri activate-by-payload). Solo dopo S296 test verde → deploy prod + ring chain promosso. |
| LOW | KV cleanup test entries | CTO | `wrangler kv key list --binding LICENSE_CACHE --env test` + delete `purchase:test+*`, `session:cs_test_*`, `lead:*`. |
| LOW | `/api/v1/verify` debug endpoint cleanup | CTO | Post Tauri activate-by-payload verified: rimuovere route OR add `Bearer ADMIN_API_SECRET` auth. |
| LOW | wrangler v4 upgrade | CTO | BLOCKED Big Sur. |

### Vincoli S296 (non-negoziabili)

- **REGOLA #1 verifica fattuale**: ogni claim Brevo (endpoint, header `api-key`, sender rewrite @brevosend.com, free tier 300/giorno) verificato via test diretto post-API-key acquisition. WebFetch Brevo doc bloccata 401. Smoke test reale = canonical evidence.
- **REGOLA #3 raccomandazione singola**: no tabelle comparative con verdetti. Path Brevo confermato, no alternative riapertura senza dati nuovi.
- **REGOLA #4 critica strutturale**: 4 punti dopo ogni proposta CTO.
- **REGOLA #5 zero-cost rigoroso**: Brevo free 300/giorno + Cloudflare Worker free tier + D1 free tier + KV free tier. Zero capex.
- **REGOLA #14/#15/#16 CTO autonomous + research-first**: tutto codice + test in autonomia. Founder gate solo Brevo signup (richiede founder email + password fisicamente) + Stripe Dashboard update (Payment Link UI).
- **REGOLA #18 META-VINCOLO VALIDATE-THEN-IMPLEMENT**: production_ready_PROD solo post 3 test reali letti da Luke. S296 chiude su test env, prod gate distinto.
- **CLOSING_ONLY soglia ≥70% post system-reminders**: S296 monitor `/context` ogni 5 tool call, edit file critici BLOCKED sopra 50%. nuovi file (license-recovery.ts, checkout-success.ts, *.test.ts) = no critico.

### Pre-flight S296 (10s)

```bash
# 1. Env vars + keypair S290
zsh -c 'for V in CLOUDFLARE_API_TOKEN STRIPE_TEST_SECRET_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST BREVO_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
ls -la ~/.claude/.env.s290-ed25519-* | wc -l  # 2

# 2. Worker test health (NO prod deploy fino META-VINCOLO test verde)
curl -sS https://fluxion-proxy-test.gianlucanewtech.workers.dev/health

# 3. Codice S295 ancora in tree + TS pass
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy && npx tsc --noEmit && echo "TS PASS"

# 4. Verifica nuove route registrate
grep -n "license-recovery\|checkout-success" src/index.ts
```

### Carry-over backlog (defer post-S296)

- **FSAF-06..08**: 3DS fail, dual-machine, stolen card (TEST chain)
- **FDQ-02 SCA EU 3DS** (`4000002500003155` browser founder)
- **BACKLOG-DISPUTE-ALERT** + **BACKLOG-DISPUTE-AUTO-REVOKE** (S288)
- **BACKLOG-VOICE-SIDECAR-BUNDLE** (S289 Sara auto-start binary client)
- **Anello #7 sales agent WA** Phase 12
- **BUG-FATT-3** live verify GUI iMac + **BUG-FATT-5** toast z-index
- **Track E** migration 017 license_revoked status enum
- **Track F** force phone-home post Stripe webhook
- **LOGO email template** founder S286 (brand-guardian + visual-storyteller)
- **landing CF Pages re-deploy** post-FBUG-LM-01 S287
- **Migrazione legacy NODE-ED25519 → Ed25519 standard** S291 carry-over
- **tauri-plugin-deep-link v1.1**: `fluxion://activate?payload=...&sig=...` con single-instance plugin Windows + bundle macOS test gate

Ripartenza S296 = path completo `.claude/NEXT_SESSION_PROMPT.manual.md` (REGOLA #13 S267 no sintesi inline).
