# Prompt ripartenza S287 — Anello #1 landing→signup + anello #6 attivazione_app verified

## Stato chiusura S286 (CLOSED VERDE, Fase E completa 7/8 + chain-map 5/7 anelli VERIFIED + 2 safety + 1 dq PASS)

### Deliverable consegnati S286

1. **FSAF-09 dedupe email implementato** — `fluxion-proxy/src/routes/stripe-webhook.ts` riga 332-352, early-return su `LICENSE_CACHE.get(session:{id})` exists prima di KV write + sendConfirmationEmail. Sposta dichiarazione `sessionKey` su (commento `declared above for early-return check`).

2. **Vitest test FSAF-09 added** — `fluxion-proxy/tests/stripe-webhook.test.ts` `+75 righe`: test 'FSAF-09: resend of already-processed session skips email re-send (idempotent_replay)'. resendCalls counter via mockFetch isolato per-test, assert `resendCalls=1` invariato post-replay, `idempotent_replay=true` response body, `purchase.created_at` preserved. **14/14 PASS** in 17.35s (era 13/13 baseline S279).

3. **TypeScript strict** `npx tsc --noEmit` exit 0.

4. **Worker test re-deployato** `Current Version ID: 569bf166-e0ec-4503-93a3-67008359e485` con fix FSAF-09 attivo + `[env.test.triggers] crons = []` esplicito (fix carry-over S285 — no più ereditano `[triggers]` top-level su env test).

5. **FSAF-09 live verify PASS** — `stripe events resend evt_1TaIfzIW4bHDTsaHilob7QmV --webhook-endpoint we_1TaI32IW4bHDTsaHT0wtsmJ4` → `pending_webhooks=0` → KV `session:cs_test_a1OFmz...` `created_at` **invariato** `2026-05-23T17:03:11.614Z` (era previously updated 16:45→17:03 in S285 senza fix). Confronto evidence:
   - S285 pre-fix: resend overwrite KV + email re-send
   - S286 post-fix: resend → `idempotent_replay: true`, no KV write, no Resend API call

6. **Anello #5 email_consegna PROMOSSO VERIFIED**:
   - Coupon S286 v2: `BMStvGos` 100% off
   - Checkout: `cs_test_a1CYEFiXWEhxen333ZaHuuSszuM6Z8f1wsLoafAca7krFXhRiX8g115CXp`
   - **Email Resend account owner identificata**: `fluxion.gestionale@gmail.com` (verificata via Resend API direct test `403 validation_error`: "You can only send testing emails to your own email address (fluxion.gestionale@gmail.com)"). **NON `gianlucadistasi81@gmail.com`** (Claude userEmail = Luke personal Gmail).
   - Founder paga €0 → webhook fire → handler `sendConfirmationEmail` invoke Resend API live → `200 OK` → KV `purchase:fluxion.gestionale@gmail.com` `email_sent=true`.
   - **Founder conferma ricezione inbox Gmail** con email body completo: oggetto "Ordine confermato! FLUXION Base — €497", body 3-step (download macOS / install / activate via email).
   - Primo tentativo S286 con `gianlucadistasi81@gmail.com` fallito (`email_sent=false`) → root cause = email destinatario non-owner Resend sandbox → retry con owner email = PASS.

7. **Gate-state aggiornato `~/venture-os/state/gate-state-FLUXION.json`**:
   - `chain_map['5_email_consegna']` = `'VERIFIED'`
   - `safety_suite.passed` = `2` (FSAF-05 + FSAF-09)
   - `data_quality_suite.evidence['FDQ-01'].result` = `'PASS'` + `email_sent_flag=true` + `email_delivered_inbox_confirmed_by_founder=true` + `email_subject_received="Ordine confermato! FLUXION Base — €497"`
   - `production_ready` resta `false` (rings 1, 6, 7 still pending)

### Decisione CTO autonoma S286 (vincoli #14/#15/#16)

a) Email Resend owner **non chiesta a founder** prima di tentativo: ipotizzata `gianlucadistasi81@gmail.com` da `userEmail` context (probabile ma sbagliata). Dopo fail email_sent=false, interrogato Resend API direct → ottenuto reale owner email `fluxion.gestionale@gmail.com` in 1 call → retry checkout success. Tempo extra: ~2min. **Lezione**: per identificare Resend account owner, single source of truth = response `403 validation_error` di Resend API test send (no manual dashboard check founder).

b) Track-A.2 (custom domain Resend €10/anno) rifiutato S286 — anello #5 chiuso VERIFIED con sandbox owner email (sufficiente per Fase E gate). Custom domain rimane backlog strategica founder-decision (necessario solo se vendere a destinatari arbitrari pre-Fase F).

c) Track-C cleanup parziale: applicato solo `[env.test.triggers] crons = []` (impatto: stop F-3+F-4 cron waste su env test, ~288 invocations/giorno risparmiate). KV cleanup + coupon delete S285 differiti (audit trail S286 utile per regression test future).

### Email template ricevuto (founder confirmed S286)

```
Ordine confermato!
FLUXION Base — €497

Ciao,
Grazie per aver scelto FLUXION Base! Ecco tutto quello che ti serve per iniziare.

Passo 1 — Scarica FLUXION
▼ Scarica per macOS  (macOS 12 o superiore, Intel/Apple Silicon)

Versione Windows in arrivo. Se sei su Windows, scrivi a fluxion.gestionale@gmail.com per essere avvisato al rilascio.

Passo 2 — Installa
Apri il file scaricato e segui le istruzioni. Guida passo-passo

Passo 3 — Attiva la licenza
Al primo avvio, FLUXION ti chiede la tua email. Inserisci:
fluxion.gestionale@gmail.com
FLUXION verifica il tuo acquisto automaticamente. Nessun codice da copiare.

Hai bisogno di aiuto? Scrivici a fluxion.gestionale@gmail.com
FLUXION — Il gestionale per la tua attività
```

**Backlog NEW founder-input**: aggiungere **logo FLUXION** nel template email (post-production). File template Resend: `fluxion-proxy/src/routes/stripe-webhook.ts` riga 200-250 (`sendConfirmationEmail` HTML body). Skill `marketing/brand-guardian` + `marketing/content-creator` o `design/visual-storyteller` per asset.

---

## TASK S287 — Anello #6 attivazione_app VERIFIED + anello #1 landing→signup scope decision

### Goal sessione

Avanzare verso production_ready: chain-map 5/7 → 6/7 (anello #6) + decisione strategica anello #1 (scope `npm run test:e2e:signup` open).

### Pre-flight (10s)

```bash
zsh -c 'for V in CF_API_TOKEN STRIPE_TEST_SECRET_KEY STRIPE_TEST_PUBLISHABLE_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST CLOUDFLARE_API_TOKEN STRIPE_API_KEY; do
  VAL=$(eval echo \$$V)
  [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
which stripe && stripe --version
curl -sI https://fluxion-proxy-test.gianlucanewtech.workers.dev/health | head -2
ssh imac "lsof -i :3001 -i :3002 2>/dev/null | head -5"
```

Atteso: 7/7 SET, `stripe version 1.34.0`, health 200, iMac HTTP Bridge + voice pipeline status (se OFF → richiede founder restart per Track-A.6).

### Track-A — Anello #6 attivazione_app VERIFIED (founder GUI required)

**Pre-req**: founder presente fisicamente iMac per Keychain unlock + app launch GUI (REGOLA #12 S261).

1. **Setup**: KV `purchase:fluxion.gestionale@gmail.com` già populated S286 (tier=base, refunded=false, email_sent=true, payment_intent=null perché coupon100). License attivabile via `activate_license_ed25519` con email key.

2. **Founder action**: launch FLUXION desktop app su iMac → primo wizard chiede email → inserisce `fluxion.gestionale@gmail.com` → app chiama Tauri command `activate_license_ed25519` → backend chiama phone-home worker test → worker risponde con `{status: 'active', tier: 'base', license: {...}}` → license SQLite `license_cache` populated → `get_license_status_ed25519` ritorna `is_valid=true`.

3. **Verify**:
   - SSH iMac sqlite query `license_cache`: `SELECT * FROM license_cache LIMIT 1` → row con `customer_email='fluxion.gestionale@gmail.com'`, `tier='base'`, `status='active'`, `is_valid=1`.
   - Screenshot UI primo dashboard post-activation (founder + screenshot-capturer skill).

4. **Promote**: `chain_map['6_attivazione_app'] = 'VERIFIED'` in gate-state.

5. **Caveat noto**: worker test URL `https://fluxion-proxy-test.gianlucanewtech.workers.dev` deve essere temporaneamente puntato dal binary FLUXION iMac. Verificare `src-tauri/src/commands/license_ed25519.rs` const URL phone-home (default punta prod `fluxion-proxy.gianlucanewtech.workers.dev`). Opzioni:
   - (raccomandato) env var build-time override `FLUXION_PROXY_URL` in Cargo.toml o config.toml local — temporaneo per S287
   - (alternativo) skip Track-A.6 in env.test e rebuild punta direttamente prod (richiede checkout Stripe REAL con card 4242 in prod sandbox → escalation costi/complessità)

### Track-B — Anello #1 landing→signup scope decision (zero-touch CTO research)

Anello #1 status: `MISSING` — nessuno script `npm run test:e2e:signup` esiste, no handler proxy `lead-magnet.ts` (esiste) e2e-tested.

Research-first (REGOLA #16) per decidere scope:
1. Grep `e2e-tests/tests/` per pattern signup/lead/landing.
2. Read `fluxion-proxy/src/routes/lead-magnet.ts` per capire endpoint signature.
3. Read `landing/` (se esiste) per HTML signup form.
4. **Output**: raccomandazione singola motivata — (a) skip anello #1 da production gate (lead magnet = marketing optional, NON acquisto path) ridefinendo `production_ready` criteria; (b) implement E2E signup test in 2-4h con Playwright + mock Resend lead capture; (c) defer S288+ con scope precisa.

Decisione CTO autonoma post-research, no founder ask (vincolo #15).

### Track-C — Production gate redefinition (se Track-B sceglie opzione a)

Se anello #1 ridefinito out-of-gate-production:
- `production_ready` criteria nuove: rings 2-6 VERIFIED + safety ≥6/8 + dq ≥3/4 + ring 7 (sales agent) acknowledged Phase 12 future.
- Update `VOS-PRODUCTION-PROTOCOL.md` Parte 4.2 marca anello #1 come "marketing-optional (acquisition top-funnel), non gating".
- Allinea gate-state.json `blocking_reason` + `production_ready` evaluation logic.

### Step finale — Update gate-state-FLUXION.json + HANDOFF + commit S287

```python
g['chain_map']['6_attivazione_app'] = 'VERIFIED'  # post Track-A
g['updated_at'] = '<now>'
g['chain_map_evidence']['6_attivazione_app']['s287_verification'] = {...}
# Track-B outcome update accordingly
```

---

## Vincoli S287 (non-negoziabili)

- **MAI stampare valori chiavi** — SOLO SET/UNSET booleano (S284/S285/S286 pattern).
- **NO mock**: ogni step usa endpoint reali (Tauri app live + phone-home worker live + SQLite locale).
- **Output incollato per ogni step**, no claim "ready" senza output.
- **Step crash → STOP** + segnalare file/riga/motivo.
- **VOS BLOCK Stop hook** attivo.
- **Hook auto-close fix attivo** (S283).
- **REGOLA #16**: research-first prima di scelta tecnica/strategica.
- **REGOLA #12** (S261): Keychain unlock GUI iMac founder-present per Track-A activation flow.

## Carry-over backlog (defer post-S287)

- **FSAF-01..04, 06..08**: card decline 4000000000000002, insufficient funds, stolen, 3DS, refund flow, amount tampering, dual-machine activation (richiedono Stripe CLI scenarios + multi-machine setup)
- **FDQ-02..04**: SCA EU 3DS card, refund propagation client-side post-S280, dispute simulation
- **Anello #7 sales agent WA**: Phase 12, decisione strategica founder
- **BUG-FATT-3** live verify GUI iMac founder-present (S276)
- **BUG-FATT-5** toast z-index globale
- **Track E** migration 017 license_revoked status enum CHECK
- **Track F** force phone-home post Stripe webhook (push-down vs pull-up)
- **Resend custom domain** decisione strategica (€10/anno vs sandbox limit) — sblocca destinatari arbitrari
- **LOGO email template** (founder S286 input): aggiungere `<img src="...">` brand FLUXION in `sendConfirmationEmail` HTML body (`fluxion-proxy/src/routes/stripe-webhook.ts` ~riga 200-250)
- **wrangler v4 upgrade** dopo Big Sur sunset (warning costante v3.114 out-of-date, NO update finché MacBook Big Sur — wrangler 4 require macOS 13.5+)
- **KV cleanup S285+S286 test entries** (audit trail valore conservato, low-priority cleanup)

## Files modificati S286 da committare

- `fluxion-proxy/src/routes/stripe-webhook.ts` — +14 righe FSAF-09 early-return + commento sessionKey
- `fluxion-proxy/tests/stripe-webhook.test.ts` — +75 righe test FSAF-09
- `fluxion-proxy/wrangler.toml` — `[env.test.triggers] crons = []` esplicito
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S287 scope

Fuori repo FLUXION (NO commit):
- `~/venture-os/state/gate-state-FLUXION.json` — chain_map['5']=VERIFIED, safety 2/8, dq 1/4 PASS

Cloudflare-side state (no git tracked):
- Worker `fluxion-proxy-test` re-deploy Version ID `569bf166-e0ec-4503-93a3-67008359e485`
- KV `purchase:fluxion.gestionale@gmail.com` + `session:cs_test_a1CYEF...` + `purchase:gianlucadistasi81@gmail.com` (orfana, cleanup low-prio) + S285 entries

Stripe-side state (no git tracked):
- Coupon `aUiqn9rM` (S286_EMAIL_VERIFY, used wrong email)
- Coupon `BMStvGos` (S286_VERIFY_V2, used owner email — PASS)
- Coupon `dcwmOPFa` (S285_FULL_TEST, used)
- Checkout sessions: cs_test_a1vZ4y (wrong email), cs_test_a1CYEF (PASS), cs_test_a1OFmz (S285)
- Event `evt_1TaIfzIW4bHDTsaHilob7QmV` (S285, delivered 2x: orig + FSAF-09 verify resend)

Atteso post-Stop: 1 commit per file proxy + wrangler + NEXT_SESSION_PROMPT.manual.md aggiornato. Verifica con `git log -1 --stat` che NON sia "auto-close" cosmetico-only.
