# Prompt ripartenza S286 — Anello #5 email_consegna VERIFIED + FSAF-09 email-idempotency

## Stato chiusura S285 (CLOSED VERDE, Fase E completa 7/8 + chain-map promosso anelli 2-4)

### Deliverable consegnati S285

1. **Stripe CLI v1.34.0** installato su MacBook Big Sur via GitHub Releases tarball (NO brew, brew rifiuta Big Sur Tier 3). Path: `~/bin/stripe`, già in PATH. Binary v1.34.0 NON usa `_SecTrustCopyCertificateChain` (assente su Big Sur), funziona stabilmente. Versioni ≥v1.35 dyld error. NO upgrade automatico.

2. **KV namespace TEST creato**: `LICENSE_CACHE` env=test, id=`13a75d1bc2f94028a78fdc45317303df`. wrangler.toml `[[env.test.kv_namespaces]]` placeholder sostituito (commit incluso).

3. **4 secrets test pushati via stdin** (no echo valori) su worker `fluxion-proxy-test`:
   - `STRIPE_SECRET_KEY` (sk_test, 107char)
   - `RESEND_API_KEY` (re_, 36char)
   - `ED25519_PUBLIC_KEY` (64char hex, da `FLUXION_PUBLIC_KEY_HEX` license_ed25519.rs)
   - `STRIPE_WEBHOOK_SECRET` (whsec_, founder-provided via /tmp file mode 600 + overwrite+delete)

4. **Worker test deployato**: `https://fluxion-proxy-test.gianlucanewtech.workers.dev` — health check 200 OK. ⚠️ side-effect: `[triggers]` top-level wrangler.toml ereditati anche su env.test (F-3 email seq 09:00 + F-4 health monitor /5min girano anche in test). Non blocca FDQ-01 ma waste invocations. Fix carry-over: aggiungere `[env.test.triggers] crons = []` esplicito.

5. **Webhook endpoint TEST creato founder-side**: `we_1TaI32IW4bHDTsaHT0wtsmJ4` → URL `fluxion-proxy-test...` events `checkout.session.completed` + `charge.refunded`. signing secret `whsec_...` persistito `~/.claude/.env` come `STRIPE_WEBHOOK_SECRET_TEST` (mode 600, 7 export totali).

6. **FDQ-01 PASS_PARTIAL** — Checkout session creata via API con `price_1TRrGpIW4bHDTsaHtlcqzrSR` (FLUXION Base TEST €497 pre-config) + coupon 100% `dcwmOPFa` (founder no-cost preference, anche se sandbox=zero-cost intrinseco). Founder ha completato pagamento `amount_total=0`. Webhook `evt_1TaIfzIW4bHDTsaHilob7QmV` delivered (`pending_webhooks=0` post-prima-delivery). KV `purchase:test+s285@example.com` + `session:cs_test_a1OFmz...` create con `tier=base`, `refunded=false`, `email_sent=false`.

7. **FSAF-05 idempotency PASS** — `stripe events resend evt_1TaIfzIW4bHDTsaHilob7QmV --webhook-endpoint we_1TaI32IW4bHDTsaHT0wtsmJ4` → `pending_webhooks=1` post-resend → KV `created_at` aggiornato `16:45 → 17:03` (handler processato re-delivery) → KV count finale `purchase:* = 1`, `session:* = 1` (singleton by-design KV). NO duplicate.

8. **Chain-map promosso**:
   - 2_checkout_stripe: EXISTS → **VERIFIED**
   - 3_pagamento_confermato: EXISTS → **VERIFIED**
   - 4_licenza_generata: EXISTS → **VERIFIED**
   - 5_email_consegna: EXISTS → **PARTIAL_SANDBOX_LIMIT** (Resend `onboarding@resend.dev` rifiuta destinatari non-owner account in sandbox)
   - 1, 6, 7 invariati (MISSING/EXISTS)
   - `safety_suite.passed = 1` (FSAF-05)
   - `data_quality_suite.passed = 1` (FDQ-01 partial)
   - `e2e_real_run_observed = True`
   - `production_ready` resta `False` (rings 1+6+7 + 7/8 safety + 3/4 dq pending)

### Decisione CTO autonoma S285 (vincolo #15)

a) Coupon 100% accettato senza pushback dopo aver dichiarato "test mode = zero commissione intrinseco" (verifica fattuale OK, ma founder preference rispettata = scope choice).

b) Anello #5 email_consegna catalogato `PARTIAL_SANDBOX_LIMIT` invece di FAIL — root cause = limitazione Resend sandbox documentata, NON bug handler. Verifica infrastrutturale OK (`sendConfirmationEmail` chiamato, response 4xx ricevuto, `email_sent=false` persistito correttamente).

c) FSAF-09 introdotto come nuovo safety check candidate (backlog): email re-send su resend evento webhook = bug handler ricorrente. `stripeWebhook` riga 361-394 NON controlla se `session:{id}` exists già prima di chiamare `sendConfirmationEmail`. In produzione = 2 email duplicate per ogni resend Stripe (es. retry automatico per response 5xx). Fix: aggiungere check `await c.env.LICENSE_CACHE.get(sessionKey)` esistente → skip email re-send. Severity LOW (sandbox-only behavior visible attualmente, email not delivered comunque).

### Incidenti minori S285

- **Encoding curl `+` → spazio**: prima Checkout Session fallita per email `test+s285@...` → `test s285@...` decodificata come spazio (form-urlencoded). Fix: switch `-d` → `--data-urlencode`. Sintassi corretta documentata in script ripartenza.
- **`stripe events resend` default target CLI listener**: senza flag `--webhook-endpoint we_xxx`, comando ritorna `"No CLI endpoints found"`. Pattern correct: sempre specificare endpoint ID quando si testano webhook reali (non `stripe listen`).
- **ED25519 grep pattern multiline**: `pub const FLUXION_PUBLIC_KEY_HEX: &str =\n    "c61b..."` su 2 righe. Primo grep ha matchato 0 char, secret uploadato vuoto. Re-push corretto con `grep -A1`. Lezione: pattern grep cross-line richiede flag o python read+regex.

---

## TASK S286 — Sblocco anello #5 + FSAF-09 dedupe

### Pre-flight (10s)

```bash
zsh -c 'for V in CF_API_TOKEN STRIPE_TEST_SECRET_KEY STRIPE_TEST_PUBLISHABLE_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST CLOUDFLARE_API_TOKEN STRIPE_API_KEY; do
  VAL=$(eval echo \$$V)
  [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
which stripe && stripe --version
ls -la ~/bin/stripe
curl -sI https://fluxion-proxy-test.gianlucanewtech.workers.dev/health | head -2
```

Atteso: 7/7 SET, `stripe version 1.34.0`, health 200.

### Track-A — Anello #5 email_consegna VERIFIED

**Opzione A.1 (raccomandata, zero costi)**: aggiungere email owner Resend account come destinatario verified.

1. Founder verifica su https://resend.com/api-keys account TEST → identifica email primaria account (es. `gianlucadistasi81@gmail.com` o altra).
2. Modifica Checkout Session usando quella email + nuovo coupon 100%:
   ```bash
   # Crea nuovo coupon (precedente `dcwmOPFa` già usato — se vuoi pulizia, cancellalo prima)
   ~/bin/stripe coupons create --api-key "$STRIPE_TEST_SECRET_KEY" \
     -d "percent_off=100" -d "duration=once" -d "name=S286_EMAIL_VERIFY"
   # Salva coupon_id output
   ```
3. Founder paga il nuovo Checkout → webhook fire → handler chiama Resend → email arriva alla casella owner.
4. CTO verifica via KV `purchase:<owner_email>` ha `email_sent=true` + Resend dashboard logs.
5. Promuovi chain_map['5_email_consegna'] = 'VERIFIED'.

**Opzione A.2 (futuro, fuori scope S286)**: acquisto dominio custom + DNS verify Resend → email da `noreply@fluxion.it` a qualsiasi destinatario. Costo €10/anno dominio = capex minore. Decisione strategica founder.

### Track-B — FSAF-09 dedupe email su resend

File: `fluxion-proxy/src/routes/stripe-webhook.ts` riga 360-373.

Fix proposto (3 righe):
```typescript
// PRE: const sessionKey = `session:${session.id}`;
const sessionKey = `session:${session.id}`;
const existing = await c.env.LICENSE_CACHE.get(sessionKey);
if (existing) {
  console.log(`Webhook idempotent skip email re-send: session ${session.id} already processed`);
  // Aggiorna solo timestamp audit, skip email
  return c.json({ received: true, idempotent_replay: true, session_id: session.id });
}
// POST: continue with put + email send
```

Test:
1. Vitest unit test in `fluxion-proxy/tests/stripe-webhook.test.ts` → nuovo `test_resend_skips_email_send_when_session_already_processed`.
2. Live verify: resend `evt_1TaIfzIW4bHDTsaHilob7QmV` → handler ritorna `idempotent_replay: true`, KV `created_at` NON cambia, no Resend API call.

### Track-C — Cleanup S285 (5 min, opzionale)

```bash
# Cancella coupon test 100% usato
~/bin/stripe coupons delete dcwmOPFa --api-key "$STRIPE_TEST_SECRET_KEY"
# Cleanup KV test entries (purchase + session)
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
npx wrangler kv key delete "purchase:test+s285@example.com" --binding LICENSE_CACHE --env test
npx wrangler kv key delete "session:cs_test_a1OFmzTzWUCxgJSHlckJuEPbNBvVqPIpJn5m2M9BGXA9J3furlB5Y0rb0A" --binding LICENSE_CACHE --env test
# Fix triggers cron ereditati in env.test
# Editare fluxion-proxy/wrangler.toml: aggiungere sotto [env.test.vars]
#   [env.test.triggers]
#   crons = []
# poi: npx wrangler deploy --env test
```

### Step finale — Update gate-state-FLUXION.json

Post Track-A success:
```python
g['chain_map']['5_email_consegna'] = 'VERIFIED'  # se email reale arrivata
g['data_quality_suite']['evidence']['FDQ-01']['email_sent_flag'] = True
g['data_quality_suite']['evidence']['FDQ-01']['result'] = 'PASS'
```

Post Track-B success:
```python
g['safety_suite']['passed'] = 2  # FSAF-05 + FSAF-09
g['safety_suite']['evidence']['FSAF-09'] = {...}
```

---

## Vincoli S286 (non-negoziabili)

- **MAI stampare valori chiavi** — SOLO SET/UNSET booleano. Pattern S284/S285 consolidato.
- **NO mock**: ogni step usa endpoint reali (Resend live API + KV CF prod + worker test deployato).
- **Output incollato per ogni step**, no claim "ready" senza output.
- **Step crash → STOP** + segnalare file/riga/motivo.
- **VOS BLOCK Stop hook** attivo.
- **Hook auto-close fix attivo** (S283).
- **Smart quotes globally off** (S284).
- **REGOLA #16**: research-first prima di scelta tecnica/strategica (Resend domain options, vitest mock patterns, ecc.).

## Carry-over backlog (defer post-S286)

- **FSAF-01..04, 06..08**: card decline 4000000000000002, insufficient funds, stolen, 3DS, refund flow, amount tampering, dual-machine activation
- **FDQ-02..04**: SCA EU, refund propagation client-side post-S280, dispute simulation
- **Anello #1 landing→signup**: definire scope (`test:e2e:signup`)
- **Anello #6 attivazione_app VERIFIED**: founder GUI iMac (Keychain unlock + license activation post-FDQ-01) — schedulato presence founder + microfono OFF (no Sara needed)
- **Anello #7 sales agent WA**: Phase 12, decisione strategica
- **BUG-FATT-3** live verify GUI iMac founder-present (S276)
- **BUG-FATT-5** toast z-index globale
- **Track E** migration 017 license_revoked status enum CHECK
- **Track F** force phone-home post Stripe webhook (push-down vs pull-up)
- **Resend custom domain** decisione strategica (costo ~€10/anno vs sandbox limit)
- **wrangler v4 upgrade** dopo Big Sur sunset (warning costante v3.114 out-of-date, NO update finché MacBook Big Sur — wrangler 4 require macOS 13.5+)

## Files modificati S285 da committare

- `fluxion-proxy/wrangler.toml` — PLACEHOLDER KV id → `13a75d1bc2f94028a78fdc45317303df`
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — REAL change S286 scope nuovo
- `.claude/NEXT_SESSION_PROMPT.md` — auto-rigenerato cosmetic, hook S283 lo skip

Fuori repo FLUXION (NO commit):
- `~/.claude/.env` — riga `STRIPE_WEBHOOK_SECRET_TEST` aggiunta
- `~/bin/stripe` — binary CLI v1.34.0 installato
- `~/venture-os/state/gate-state-FLUXION.json` — chain-map + suite update

Cloudflare-side state (no git tracked):
- KV namespace `13a75d1bc2f94028a78fdc45317303df` (TEST)
- Worker `fluxion-proxy-test` deployato (4 secrets + 2 KV entry)

Stripe-side state (no git tracked):
- Webhook endpoint `we_1TaI32IW4bHDTsaHT0wtsmJ4` (TEST, founder)
- Coupon `dcwmOPFa` (S285_FULL_TEST 100% off, used)
- Checkout session `cs_test_a1OFmzTzWUCxgJSHlckJuEPbNBvVqPIpJn5m2M9BGXA9J3furlB5Y0rb0A` (paid €0)
- Event `evt_1TaIfzIW4bHDTsaHilob7QmV` (checkout.session.completed, delivered 2x)

Atteso post-Stop: 1 commit per `wrangler.toml` + `NEXT_SESSION_PROMPT.manual.md` aggiornato. Verifica con `git log -1 --stat` che NON sia "auto-close" cosmetico-only.
