# Prompt ripartenza S314 — Task E-4 + Task D META-VINCOLO #18 (founder-bound BLOCKING) + post-D Task F closure C-FLUXI-002

> **Generato S313 chiusura verde-parziale** (Task E-PRE/E-1/E-2/E-3/E-6/E-7 ✅ CTO autonomous).
> **Pre-flight S313**: 5/5 PASS riusabile (vedi sotto). Riparti da Task E-4 SE founder accesso Stripe dashboard ora disponibile, altrimenti Task D direttamente.

## 🎯 DIRETTIVA LUKE (invariata da S308)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con primo CLOSED_WON validato end-to-end.

## ✅ S313 OUTCOME (evidence: `~/venture-os/state/s313-task-e-full-evidence.json`)

| Task | Status | Evidence |
|------|--------|----------|
| E-PRE | ✅ PASS | LICENSE_RECOVERY_SECRET put prod, 12→13 secrets |
| E-1   | ✅ PASS | ENVIRONMENT=production, KV `12dbb4f8...`, D1 `e065a108...` |
| E-2   | ✅ PASS | 13 secrets present |
| E-3   | ✅ PASS | Worker version `e18df659-bed2-4491-a8fe-9fef9e398b2e`, /health 200, 848.89 KiB |
| E-4   | ⏸ BLOCKED founder | Stripe LIVE webhook dashboard verify |
| E-5   | ⏭ SKIP REGOLA #15 | smoke prod = primo CLOSED_WON reale |
| E-6   | ✅ PASS | VOS C-LIC-001 resolved, gate VERDE |
| E-7   | ✅ PASS ⚠ anomalia | landing URL formato PROD (no `test_` prefix), HEAD 200; suffix coincidente con TEST → founder verify dashboard |
| F     | 🟡 partial | PLAN.md updated (PROSSIMA_AZIONE + C-LIC-001 RESOLVED). HANDOFF.md inesistente, ROADMAP_REMAINING.md stale (skip per context budget). C-FLUXI-002 NON resolved (bloccato D) |

## SCOPE S314 (ordine esecuzione)

### Task E-4 — Stripe webhook LIVE verify (founder dashboard)

1. Founder apre `https://dashboard.stripe.com/webhooks` (toggle LIVE mode top-right)
2. Verifica endpoint configurato = `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`
3. Eventi sottoscritti = `checkout.session.completed` (minimo)
4. SE manca: founder "Add endpoint" → CTO guida creazione + signing secret `whsec_...`
5. SE secret nuovo: CTO `cd fluxion-proxy && source ~/.claude/.env && export CLOUDFLARE_API_TOKEN=$CF_API_TOKEN && echo "<whsec>" | npx wrangler secret put STRIPE_WEBHOOK_SECRET`

### Task E-7-VERIFY — Landing checkout URL anomalia

Founder Stripe dashboard LIVE → "Payment Links" → confermare presenza `plink` con URL:
- `https://buy.stripe.com/bJe7sM19ZdWegU727E24000` (base €497)
- `https://buy.stripe.com/00w28sdWL8BU0V9fYu24001` (pro €897)

SE NON esistono LIVE = bug critico (landing punta a URL non LIVE). SE esistono = OK, fix doc memoria S305-S308 (erroneamente etichettati TEST).

### Task D — META-VINCOLO REGOLA #18 founder GUI activate (BLOCCANTE C-FLUXI-002)

**D-1 Smoke E2E email reale (PROD env, post E-4 OK)**:
1. Founder Stripe Payment Link LIVE €497 → carta REALE (founder può poi rimborsare via Stripe dashboard se zero cash flow)
2. CTO `wrangler tail` osserva webhook prod 200 + license sign + Resend send
3. /success render verify (CTO)
4. Founder Gmail `fluxion.gestionale@gmail.com` check email "FLUXION — Il tuo ordine è confermato!" da `FLUXION <licenze@fluxion-app.com>` + screenshot recovery URL cliccabile

**D-2 GUI activate FLUXION app**:
1. CTO: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev"` (background)
2. Founder wizard licenza → incolla email + clicca "Attiva" → Ed25519 unlock + screenshot

**D-3 Evidence**: `~/venture-os/state/s187-fase1-S314-production-validation.json` (tabella fonte D-1/D-2 + verdetto + Luke GO esplicito + bug residui)

**STOP META-VINCOLO**: CTO NON dichiara `production_ready` senza output reale D-1/D-2/D-3 letti da Luke.

### Task F — Closure C-FLUXI-002 post-D

```bash
cd /Volumes/MontereyT7/FLUXION
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002 --motivation "primo CLOSED_WON real S314 PASS D-1/D-2/D-3 evidence Luke GO"
python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
```

Update PLAN.md: rimuovi `[vedi C-FLUXI-002]` notes obsolete, marca C-FLUXI-002 `[RESOLVED S314]`.

## EVIDENCE GATE S314 closure verde

- [ ] E-4: Stripe webhook LIVE verified
- [ ] E-7-VERIFY: landing URL confermati LIVE
- [ ] D-1: email reale + inbox screenshot
- [ ] D-2: FLUXION app GUI activate PASS + screenshot
- [ ] D-3: S187 FASE 1 evidence + Luke GO esplicito
- [ ] F: VOS C-FLUXI-002 resolved + gate VERDE

## REGOLE ATTIVE S314

#4 critica strutturale · #14 CTO autonomous (E-4 setup/F) · #15 NO A/B · #16 research-first · **#18 META-VINCOLO (D BLOCCANTE)** · #20 CF token · #22 critique-then-ignore

## ARTEFATTI PRONTI

- Commit HEAD S313: `<commit-from-auto-close>` (Task E-PRE/E/F partial)
- Worker prod version: `e18df659-bed2-4491-a8fe-9fef9e398b2e`
- 13 secrets prod (incl. LICENSE_RECOVERY_SECRET nuovo)
- Resend domain `fluxion-app.com` id `6f986180-2eaf-41e2-8a40-53ebeefedbf0` verified
- Evidence S313: `~/venture-os/state/s313-task-e-full-evidence.json`

## DECISIONI LUKE PENDENTI (escalate post primo CLOSED_WON)

1. `magazzino` scope v1.0 o post-launch?
2. `9 verticali` fonte canonica?
3. macOS code signing → firma o ad-hoc + Gatekeeper page?
4. Nuovo CF token `Zone DNS Edit` 90d TTL?
5. DMARC `p=none` → `p=quarantine` schedule?
6. `ED25519_KID` secret prod — investigate usage, add/remove?

## NOTE OPERATIVE

- **Anomalia E-7**: landing URLs `bJe7sM19ZdWegU727E24000` + `00w28sdWL8BU0V9fYu24001` ritornano HTTP 200 sia con che senza prefisso `test_`. Statisticamente improbabile coincidenza ID. Possibile doc memoria S305-S308 errata (URL etichettati TEST sono in realtà LIVE). Founder verify Stripe dashboard Payment Links LIVE mode.
- **CF token `FLUXION-CTO-Deploy-90d`** (`3856673a...`) usato S313 deploy + secret put PROD → valido e in uso.
