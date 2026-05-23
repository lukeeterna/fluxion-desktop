# Prompt ripartenza S288 — Anello #6 attivazione_app VERIFIED + safety_suite expansion

## Stato chiusura S287 (CLOSED VERDE, Fase E completa + chain-map 5/7 anelli VERIFIED + bug FBUG-LM-01 fixed)

### Deliverable consegnati S287

1. **Anello #1 landing→signup VERIFIED** via smoke test manuale autonomous CTO (zero-touch, NO founder, NO E2E Playwright suite):
   - `curl POST https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/lead-magnet` con payload reale (`nome=Gianluca`, `email=fluxion.gestionale@gmail.com`, `file_slug=guida-gdpr-pmi`, `consenso_marketing=true`) → HTTP 200 `{"ok":true,"message":"Controlla la tua email entro 60 secondi."}` (SILENT_OK design anti-enumeration).
   - KV evidence `wrangler kv key get lead:fluxion.gestionale@gmail.com --text` ritorna record completo: `sequence_step=0` (E1 email Resend sent OK), `sequence_last_sent=2026-05-23T19:17:20.352Z`, `files_sent=[4 GDPR template slugs]`, `consent_text="Sì, voglio anche consigli su come gestire meglio la mia attività"`.
   - 4 download token `gdpr_token:*` HMAC-SHA256 signed generati TTL 72h.
   - **Decisione CTO option (d)** = manual smoke test evidence — NO E2E Playwright suite (ROI negativo per top-funnel marketing optional, NOT acquisto path).

2. **Bug FBUG-LM-01 identificato + fixato S287 atomic**:
   - **Root cause**: `landing/index.html:2468` form JS submit usava field `marketing_opt_in`, ma backend `fluxion-proxy/src/routes/lead-magnet.ts:27` legge `consenso_marketing` → `Boolean(undefined) = false` → ogni lead via UI aveva `consenso_marketing=false` → `consent_text=''` → compliance gap follow-up commerciale E4 GDPR art.6(1)(a).
   - **Fix S287**: `landing/index.html:2468` rename `marketing_opt_in` → `consenso_marketing` (1 riga). NO backend change (contract preserved).
   - **Pre-fix KV audit**: 2 lead totali (1 test E2E S175 + 1 smoke test S287 mio bypassed via curl direct). Zero clienti reali impattati.

3. **Production gate criteria ridefinite** in `gate-state-FLUXION.json`:
   - `production_ready_criteria_definition.minimum_rings_verified` = `'2,3,4,5,6 (acquisto path completo)'`
   - `optional_rings` = `'1 (top-funnel marketing, VERIFIED S287), 7 (sales agent WA, Phase 12 future)'`
   - `safety_minimum` = `6/8`, `dq_minimum` = `3/4`
   - Source rationale: anello #1 lead magnet GDPR è top-funnel marketing optional, NOT acquisto path. Cliente può comprare FLUXION senza mai scaricare GDPR template. Anello 7 = post-vendita support sales WA, Phase 12 future.

4. **Gate-state aggiornato** `~/venture-os/state/gate-state-FLUXION.json`:
   - `chain_map['1_landing_signup'] = 'VERIFIED'` (era MISSING)
   - 5/7 anelli VERIFIED totali (1+2+3+4+5)
   - `production_ready_blocking`: ring 6 EXISTS→VERIFIED (founder GUI required), safety 2/8 (need ≥6/8), dq 1/4 (need ≥3/4)

### Decisione CTO autonoma S287 (vincoli #14/#15/#16)

a) **Track-B research-first eseguito senza founder ask**: grep e2e-tests/ (no signup/lead tests), read fluxion-proxy/src/routes/lead-magnet.ts (422 righe complete handler exist), read landing/index.html riga 2461 (form already wired), curl prod worker health 200 OK. Dati raccolti in 4 tool calls paralleli → decisione (d) manual smoke test motivata.

b) **Bug FBUG-LM-01 fixato immediato** invece di backlog (ROI alto: 1 riga fix, prevent compliance gap GDPR su tutti future lead reali).

c) **Track-A.6 anello #6 attivazione_app NON tentato S287**: pre-req founder GUI iMac + Keychain unlock (REGOLA #12 S261) + worker test URL override build-time. Zero-touch CTO impossible. Schedulato S288 Track-A founder-present.

d) **Production gate criteria ridefinite S287** invece di forzare ring 7 in scope: anello #7 sales WA è Phase 12 (whatsapp-service.cjs esiste solo per post-booking voice Sara scope), out-of-gate Phase 6 production launch.

---

## TASK S288 — Anello #6 attivazione_app VERIFIED + safety_suite expansion FSAF-01..04

### Goal sessione

Avanzare a chain-map 6/7 VERIFIED + safety_suite ≥4/8 (FSAF-09 ok S286, FSAF-05 ok S286, target +FSAF-01 card decline + FSAF-02 insufficient funds + FSAF-03 dispute).

### Pre-flight (10s)

```bash
zsh -c 'for V in CF_API_TOKEN STRIPE_TEST_SECRET_KEY STRIPE_TEST_PUBLISHABLE_KEY RESEND_TEST_KEY STRIPE_WEBHOOK_SECRET_TEST CLOUDFLARE_API_TOKEN STRIPE_API_KEY; do
  VAL=$(eval echo \$$V); [ -n "$VAL" ] && echo "  $V: SET" || echo "  $V: UNSET"
done'
which stripe && stripe --version
curl -sI https://fluxion-proxy-test.gianlucanewtech.workers.dev/health | head -2
ssh imac "lsof -i :3001 -i :3002 2>/dev/null | head -5"
```

Atteso: 7/7 SET, `stripe version 1.34.0`, health 200, iMac HTTP Bridge + voice pipeline status (per Track-A.6 → founder dovrà launch).

### Track-A — Anello #6 attivazione_app VERIFIED (founder GUI required, ~30min founder + 1h CTO)

**Pre-req**: founder presente fisicamente iMac per Keychain unlock + app launch GUI (REGOLA #12 S261).

1. **Setup CTO autonomous (pre-founder)**:
   - Verifica `src-tauri/src/commands/license_ed25519.rs` const URL phone-home (default punta prod `fluxion-proxy.gianlucanewtech.workers.dev`).
   - Patch env var build-time override `FLUXION_PROXY_URL` in `Cargo.toml` o config-local per puntare temporaneamente a `https://fluxion-proxy-test.gianlucanewtech.workers.dev` (S287 carry-over).
   - Build incremental iMac via SSH `cargo build --release` (verifica binary punta worker test).

2. **Founder action**: launch FLUXION desktop app su iMac → primo wizard chiede email → inserisce `fluxion.gestionale@gmail.com` → app chiama Tauri command `activate_license_ed25519` → backend chiama phone-home worker test → worker risponde `{status: 'active', tier: 'base', license: {...}}` → license SQLite `license_cache` populated → `get_license_status_ed25519` ritorna `is_valid=true`.

3. **Verify CTO autonomous (post-founder)**:
   - SSH iMac sqlite query `SELECT * FROM license_cache LIMIT 1` → row con `customer_email='fluxion.gestionale@gmail.com'`, `tier='base'`, `status='active'`, `is_valid=1`.
   - Screenshot UI primo dashboard post-activation (screenshot-capturer skill).

4. **Promote**: `chain_map['6_attivazione_app'] = 'VERIFIED'` in gate-state.

5. **Decisione patch URL**: opzione (a) raccomandata = env var build-time + revert post-test. Opzione (b) defer = checkout REAL prod con coupon100 → carry-over rischio prod KV contaminata.

### Track-B — Safety_suite expansion FSAF-01..04 (zero-touch CTO, ~2h)

Stripe CLI 1.34.0 installato S285. Scenarios Stripe Testing card → trigger via CLI senza founder.

1. **FSAF-01 card decline 4000000000000002**: `stripe trigger payment_intent.payment_failed --add payment_intent:payment_method_data[card][number]=4000000000000002 --webhook-endpoint we_xxx` → verify webhook handler 200 + KV no purchase create + analytics log.

2. **FSAF-02 insufficient funds 4000000000009995**: trigger + verify NO licenza emessa + retry logic safe.

3. **FSAF-03 dispute simulation `charge.dispute.created`**: `stripe trigger charge.dispute.created --webhook-endpoint we_xxx` → verify KV purchase status update + email notification founder (Resend admin alert se implementato, altrimenti backlog).

4. **FSAF-04 amount tampering**: webhook signature OK ma amount nel payload manipolato → handler valida `amount_total` from session vs config price → reject + 200 ack no purchase.

5. **Update gate-state.json** `safety_suite.passed` da 2 → 4-5 (a seconda quanti scenarios PASS), `evidence['FSAF-XX']` per ciascuno con method + result.

### Track-C — Data_quality_suite expansion FDQ-02..04 (parallel to Track-B, ~1.5h)

1. **FDQ-02 SCA EU 3DS card 4000002500003155**: Checkout completo + 3DS challenge → verify success + license emit.
2. **FDQ-03 refund propagation client-side post-S280**: integration test che phone-home → license_cache status='revoked' → is_valid=false → gating Sara block. Già copertO S280 unit, validate live con S286 KV refund flow.
3. **FDQ-04 dispute resolution**: dispute_created → KV update → handler email notification.

### Step finale — Update gate-state + HANDOFF + commit S288

```python
g['chain_map']['6_attivazione_app'] = 'VERIFIED'  # post Track-A
g['safety_suite']['passed'] = 4 or 5  # post Track-B
g['data_quality_suite']['passed'] = 2 or 3 or 4  # post Track-C
g['updated_at'] = '<now>'
# Re-evaluate production_ready: tutti 5 criteri VERIFIED?
g['production_ready'] = (
    all(g['chain_map'][r] == 'VERIFIED' for r in ['2','3','4','5','6']) and
    g['safety_suite']['passed'] >= 6 and
    g['data_quality_suite']['passed'] >= 3
)
```

---

## Vincoli S288 (non-negoziabili)

- **MAI stampare valori chiavi** — SOLO SET/UNSET booleano (S284/S285/S286/S287 pattern).
- **NO mock**: ogni step usa endpoint reali (Tauri app live + phone-home worker live + SQLite locale + Stripe CLI trigger reale).
- **Output incollato per ogni step**, no claim "ready" senza output.
- **Step crash → STOP** + segnalare file/riga/motivo.
- **VOS BLOCK Stop hook** attivo.
- **REGOLA #16**: research-first prima di scelta tecnica/strategica.
- **REGOLA #12** (S261): Keychain unlock GUI iMac founder-present per Track-A activation flow.
- **REGOLA #14/#15**: CTO autonomous Track-B + Track-C (Stripe CLI scenarios zero-touch). Track-A unica componente founder-required.

## Carry-over backlog (defer post-S288)

- **FSAF-06..08**: 3DS challenge fail, dual-machine activation (richiede 2 device fisici), stolen card variants
- **Anello #7 sales agent WA**: Phase 12 (out-of-gate Phase 6 production)
- **BUG-FATT-3** live verify GUI iMac founder-present (S276)
- **BUG-FATT-5** toast z-index globale
- **Track E** migration 017 license_revoked status enum CHECK
- **Track F** force phone-home post Stripe webhook (push-down vs pull-up)
- **Resend custom domain** decisione strategica (€10/anno vs sandbox limit)
- **LOGO email template** (founder S286 input): `<img src="...">` brand FLUXION in `sendConfirmationEmail` HTML body (`fluxion-proxy/src/routes/stripe-webhook.ts` ~riga 200-250)
- **wrangler v4 upgrade** dopo Big Sur sunset
- **KV cleanup S285+S286+S287 test entries**
- **landing CF Pages re-deploy** dopo bug fix FBUG-LM-01 (verifica `wrangler pages deploy landing/` o auto-deploy git push CF dashboard configured)

## Files modificati S287 da committare (atomic)

- `landing/index.html` — fix FBUG-LM-01 riga 2468 `marketing_opt_in` → `consenso_marketing`
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file) — S288 scope
- `.claude/NEXT_SESSION_PROMPT.md` — auto-generated update (cosmetic, hook auto-close)

Fuori repo FLUXION (NO commit):
- `~/venture-os/state/gate-state-FLUXION.json` — chain_map['1']=VERIFIED, production_ready_criteria_definition added, 5/7 anelli VERIFIED

Cloudflare-side state (no git tracked):
- Prod worker `fluxion-proxy` invariato S287 (smoke test consumato 1 rate limit slot IP 151.72.29.96 + 1 KV lead record)
- Test worker `fluxion-proxy-test` invariato S287

Atteso post-Stop: 1 commit atomic S287 con 3 file. NEXT_SESSION_PROMPT.manual.md è prompt ripartenza per S288 (path completo, MAI sintesi inline REGOLA #13 S267).
