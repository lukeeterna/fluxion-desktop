# Prompt ripartenza S313 — Task E-PRE + Task E prod deploy + Task D META-VINCOLO #18 + Task F sync

> **Generato S312 chiusura ordinata** (context 64% > soglia 60% vincolo #7).
> **Pre-flight S312 = 5/5 PASS** (eseguito, evidence inline sotto). Riparti DIRETTAMENTE da Task E-PRE.

## 🎯 DIRETTIVA LUKE (invariata da S308)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con prod deploy ready + founder GUI activate validato.

## ✅ PRE-FLIGHT S312 — già DONE (5/5 PASS, riusare evidence)

1. **git**: clean ( M `.claude/NEXT_SESSION_PROMPT.md` + m `tools/VectCutAPI` pre-esistenti); HEAD = `b23fcac` (S311 CLOSE VERDE)
2. **/health prod**: `HTTP=200` `{"status":"ok","service":"fluxion-proxy","version":"1.0.0","timestamp":"2026-05-29T20:19:07.845Z"}`
3. **/health test**: `HTTP=200` `{"status":"ok",...,"timestamp":"2026-05-29T20:19:08.181Z"}`
4. **VOS gate**: `GATE OK (/Volumes/MontereyT7/FLUXION/PLAN.md): nessuna CRITIQUE [OPEN]`
5. **LICENSE_RECOVERY_SECRET prod count**: `0` → conferma S311 finding, **Task E-PRE BLOCKING attivo**

## SCOPE S313 (ordine esecuzione, ripartenza diretta)

### Task E-PRE — LICENSE_RECOVERY_SECRET prod (NUOVO S312/S313, BLOCKING, CTO autonomous)

```bash
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
RECOVERY_SECRET=$(openssl rand -hex 32)
echo "$RECOVERY_SECRET" | npx wrangler secret put LICENSE_RECOVERY_SECRET
npx wrangler secret list 2>&1 | grep LICENSE_RECOVERY_SECRET
# Expect: present in list
```

**CRITICA REGOLA #4**: nuovo secret prod NON shared con test env. Document in evidence.

### Task E — Prod deploy (post E-PRE)

**E-1**: `head -50 wrangler.toml | grep -E "ENVIRONMENT|database_id|kv_namespace"` → expect ENVIRONMENT="production", D1 `e065a108`, KV `12dbb4f8`

**E-2**: `npx wrangler secret list` → expect 13 secrets, LICENSE_RECOVERY_SECRET present

**E-3 Deploy (NO --env flag)**:
```bash
source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
npx wrangler deploy 2>&1 | tail -20
curl -sS https://fluxion-proxy.gianlucanewtech.workers.dev/health -w "\nHTTP=%{http_code}\n"
```

**E-4**: Stripe webhook LIVE endpoint founder dashboard verify (`https://dashboard.stripe.com/webhooks` LIVE mode) = `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`. Se TEST → CTO guida creazione LIVE + `whsec_...` → `npx wrangler secret put STRIPE_WEBHOOK_SECRET`

**E-5**: smoke prod SKIP (REGOLA #15 NO A/B locked S311) — validate via primo CLOSED_WON reale + `wrangler tail`

**E-6**: `python3 ~/.vos/vos_plan.py critique resolve C-LIC-001 --reason "Stripe PROD + LICENSE_RECOVERY_SECRET active post S313 prod deploy"`

**E-7**: `grep -E "buy.stripe.com" landing/checkout-consent.html` → se `test_` → founder Payment Links PROD + swap + redeploy CF Pages landing

### Task D — META-VINCOLO REGOLA #18 founder GUI activate (BLOCCANTE, INVARIATO)

**D-1 Smoke E2E email reale (PROD env post E-3)**:
1. Founder Stripe Payment Link PROD (o TEST se preferisce no cash flow) → carta reale
2. /success render (CTO `wrangler tail`)
3. Founder Gmail `fluxion.gestionale@gmail.com` check email "FLUXION — Il tuo ordine è confermato!" da `FLUXION <licenze@fluxion-app.com>` + screenshot recovery URL cliccabile

**D-2 GUI activate**:
1. CTO: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev"` (background)
2. Founder wizard email + "Attiva" → Ed25519 unlock + screenshot

**D-3 Evidence**: `~/venture-os/state/s187-fase1-S313-production-validation.json` (tabella fonte + verdetto + Luke GO esplicito + bug residui)

**STOP**: CTO NON dichiara `production_ready` senza output reale D-1/D-2/D-3 letti da Luke.

### Task F — Doc sync

1. PLAN.md C-FLUXI-002 → `[RESOLVED S310-S313]` + evidence path
2. ROADMAP_REMAINING.md: primo €497 ready, next milestone = first CLOSED_WON
3. HANDOFF.md S313 summary

## EVIDENCE GATE S313 closure verde

- [x] Pre-flight 5/5 PASS (eseguito S312, evidence sopra)
- [ ] E-PRE: LICENSE_RECOVERY_SECRET prod populated + verified
- [ ] E-1/E-2/E-3: prod deploy + /health 200
- [ ] E-4: Stripe webhook LIVE prod endpoint
- [ ] E-6: VOS critique C-LIC-001 resolved
- [ ] E-7: landing checkout URL PROD
- [ ] D-1: email reale + inbox screenshot
- [ ] D-2: FLUXION app GUI activate PASS + screenshot
- [ ] D-3: S187 FASE 1 evidence + Luke GO esplicito
- [ ] F: PLAN.md + ROADMAP_REMAINING.md + HANDOFF.md updated

## REGOLE ATTIVE S313

#4 critica strutturale · #14 CTO autonomous (E-PRE/E/F) · #15 NO A/B · #16 research-first · #18 META-VINCOLO (D BLOCCANTE) · #20 CF token · #22 critique-then-ignore candidata

## ARTEFATTI PRONTI

- Commit HEAD: `b23fcac` (S311 CLOSE VERDE)
- Resend domain `fluxion-app.com` id `6f986180-2eaf-41e2-8a40-53ebeefedbf0` verified
- Evidence S311: `~/venture-os/state/s311-preflight-findings.json`
- Worker test: `258b0cd1-2148-412f-99e6-876cd4d9b159`
- Stripe Payment Links TEST: base €497 `plink_1TRrGqIW4bHDTsaHeX8g37gD` / pro €897 `plink_1TRrGrIW4bHDTsaH1KwXKrUJ`

## FINDING S311 RICONFERMATO S312 PRE-FLIGHT

`LICENSE_RECOVERY_SECRET` MISSING in prod (count=0) — usato in `stripe-webhook.ts:452-453`, `checkout-success.ts:247,273`, `license-recovery.ts:81`. Optional type → no crash MA recovery URL assente in email post-€497 → refund storm risk. **Task E-PRE BLOCCA E-3 deploy**.

## DECISIONI LUKE PENDENTI (escalate post €497 reale)

1. `magazzino` scope v1.0 o post-launch?
2. `9 verticali` fonte canonica?
3. macOS code signing → firma o ad-hoc + Gatekeeper page?
4. Nuovo CF token `Zone DNS Edit` 90d TTL?
5. DMARC `p=none` → `p=quarantine` schedule?
6. Stripe Payment Link TEST → PROD swap (cash flow vs validate)?
7. `ED25519_KID` secret prod — investigate usage, add/remove?

## CHIUSURA S312 (motivo)

Context 64% > soglia 60% closing (CLAUDE.md vincolo #7). Pre-flight 5/5 done, riparti S313 da Task E-PRE.
