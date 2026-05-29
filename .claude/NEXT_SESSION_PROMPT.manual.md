# Prompt ripartenza S316 — Stripe outage S315 → retry F1-F4 + scope S315 invariato

> **Generato S315 chiusura verde parziale** (S0 ✅ HTTP Bridge UP, F1-F4 BLOCCATO Stripe outage esterno).
> **Stripe status pagina S315 (Luke screenshot)**: "We're currently investigating an issue. Our engineering team is looking into an error on this page." → impossibile founder creare LIVE Payment Links durante outage.

## 🎯 DIRETTIVA LUKE (invariata)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con primo CLOSED_WON validato end-to-end.

## ✅ S315 OUTCOME

| Task | Status | Evidence |
|------|--------|----------|
| S0 — HTTP Bridge iMac 3001 | ✅ DONE | tauri-app PID 19684 listening `127.0.0.1:3001`, log `/tmp/fluxion-tauri-dev.log` su iMac: `🌉 HTTP Bridge started on http://127.0.0.1:3001` + `🚀 Application ready` |
| F1-F4 Founder Stripe LIVE | 🔴 BLOCKED_EXTERNAL | Stripe outage in corso: "We're currently investigating an issue" |
| C1-C5 — | ⏸ blocked-by F1-F4 | — |
| E-4 — | ⏸ blocked-by Stripe LIVE access | — |
| D — | ⏸ blocked-by E-4 + C1-C5 | — |
| F — | ⏸ blocked-by D | — |

**Nota S0**: HTTP Bridge listening su localhost (NOT 0.0.0.0). Per Task D-2 GUI activate founder deve essere fisicamente all'iMac (≈ già piano S315 D-2). Curl remoto da MacBook non funziona by design Tauri dev.

**Nota Keychain**: log boot shows `GDPR encryption deferred: Keychain read failed: User interaction is not allowed` → REGOLA #12 nota: live verify Keychain richiede founder GUI launch fisica. Task D-2 founder all'iMac risolve.

## SCOPE S316 (ordine esecuzione)

### Pre-flight S316 — Stripe status check (CTO autonomous, BLOCKING)

```bash
# Stripe status JSON
curl -sS https://www.stripewebservices.com/api/v2/status.json 2>/dev/null | head -c 500
# Fallback se 404: https://status.stripe.com/
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" https://status.stripe.com/
# Dashboard reachability (no auth, solo TCP+TLS)
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" --max-time 5 https://dashboard.stripe.com/
```

Se Stripe status = `operational` AND dashboard HTTP 200 → procedi F1-F4. Altrimenti retry queue.

### Pre-flight S316 — Servizi iMac

```bash
ssh imac "lsof -iTCP:3001 -sTCP:LISTEN; tail -10 /tmp/fluxion-tauri-dev.log"
```

Expected: tauri-app listening. Se DOWN, riavvio:
```bash
ssh imac 'bash -lc "source ~/.nvm/nvm.sh && nvm use 20.11.0 >/dev/null && cd \"/Volumes/MacSSD - Dati/fluxion\" && nohup npm run tauri dev > /tmp/fluxion-tauri-dev.log 2>&1 & echo PID=\$!"'
```

### F1-F4 — Founder Stripe LIVE Payment Links (BLOCKING, retry post-outage)

1. Founder login `https://dashboard.stripe.com` → toggle **LIVE mode** (top-right)
2. Products → seleziona `fluxion-base` (€497) → "Create payment link" → copy URL `https://buy.stripe.com/<slug-LIVE-base>`
3. Products → seleziona `fluxion-pro` (€897) → "Create payment link" → copy URL `https://buy.stripe.com/<slug-LIVE-pro>`
4. Founder share 2 URL LIVE con CTO

### C1-C5 — CTO autonomous post-founder

1. Edit `landing/checkout-consent.html`:
   - Line 125 (chiave `base`): `stripeUrl: '<LIVE_BASE_URL>'`
   - Line 131 (chiave `pro`): `stripeUrl: '<LIVE_PRO_URL>'`
2. **CRITICO**: verify slug swap risolto. S314 evidence: slug attuali `00w28sdWL8BU0V9fYu24001` (su `base`) = PRO €897 + `bJe7sM19ZdWegU727E24000` (su `pro`) = BASE €497. Nuovi slug LIVE DEVONO matchare etichetta.
3. Cross-check via Stripe API LIVE:
   ```bash
   sk_live_key=$(...)  # founder provide o tramite ~/.claude/.env.fluxion-live
   for slug in <LIVE_BASE_SLUG> <LIVE_PRO_SLUG>; do
     curl -sS "https://api.stripe.com/v1/payment_links?limit=10" -u "$sk_live_key:" | jq '.data[] | select(.url | contains("'$slug'")) | {id, url, line_items: .line_items}'
   done
   ```
   Verify: `base` slug → product fluxion-base €497, `pro` slug → fluxion-pro €897.
4. `cd /Volumes/MontereyT7/FLUXION && npx wrangler pages deploy landing --project-name=fluxion-landing`
5. Curl verify prod:
   ```bash
   curl -sS https://fluxion-landing.pages.dev/checkout-consent.html?plan=base | grep -oE 'buy.stripe.com/[a-zA-Z0-9_]+' | head -1
   curl -sS https://fluxion-landing.pages.dev/checkout-consent.html?plan=pro | grep -oE 'buy.stripe.com/[a-zA-Z0-9_]+' | head -1
   ```
   Expected: rispettivamente LIVE_BASE_SLUG + LIVE_PRO_SLUG.

### Task E-4 — Stripe webhook LIVE verify (founder dashboard)

1. Founder `https://dashboard.stripe.com/webhooks` (LIVE mode)
2. Verifica endpoint = `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`
3. Eventi = `checkout.session.completed` minimo
4. SE manca: founder "Add endpoint" → CTO guida + `npx wrangler secret put STRIPE_WEBHOOK_SECRET --env production` con whsec_ LIVE

### Task D — META-VINCOLO REGOLA #18 (BLOCCANTE C-FLUXI-002)

**D-1 Smoke E2E LIVE (post-E-4 OK + post-C1-C5 OK)**:
1. Founder visita `https://fluxion-landing.pages.dev/checkout-consent.html?plan=base` → click consent → redirect LIVE plink €497
2. Founder paga con carta REALE (refund post-test)
3. CTO `npx wrangler tail fluxion-proxy --env production --format pretty` osserva: webhook 200 + Ed25519 sign + Resend send 200
4. /success render verify
5. Founder Gmail `fluxion.gestionale@gmail.com` check email `FLUXION <licenze@fluxion-app.com>` + screenshot recovery URL

**D-2 GUI activate**:
1. HTTP Bridge già UP (verifica con pre-flight); se DOWN avvio come sopra
2. Founder fisicamente all'iMac, wizard licenza → incolla email → "Attiva" → Ed25519 unlock + screenshot
3. Keychain GUI unlock risolve `User interaction is not allowed`

**D-3 Evidence**: `~/venture-os/state/s187-fase1-S316-production-validation.json` (tabella D-1/D-2 + Luke GO esplicito)

**STOP META-VINCOLO**: CTO NON dichiara `production_ready` senza D-1/D-2/D-3 letti da Luke.

### Task F — Closure C-FLUXI-002 post-D

```bash
cd /Volumes/MontereyT7/FLUXION
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002 --motivation "primo CLOSED_WON real S316 PASS D-1/D-2/D-3 evidence Luke GO + E-7 bug fixed"
python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
```

## EVIDENCE GATE S316 closure verde

- [ ] Stripe status `operational` + dashboard 200
- [ ] HTTP Bridge 3001 UP su iMac
- [ ] F1-F4: founder shared 2 LIVE Payment Link URLs
- [ ] C1-C5: landing fixed + deployed + curl verify slug LIVE match etichetta
- [ ] E-4: Stripe webhook LIVE endpoint verified + whsec_ LIVE put su worker prod
- [ ] D-1: pagamento reale LIVE + Resend email + inbox screenshot
- [ ] D-2: FLUXION app GUI activate PASS + Keychain unlock + screenshot
- [ ] D-3: S187 FASE 1 evidence + Luke GO esplicito
- [ ] F: VOS C-FLUXI-002 resolved + gate VERDE

## REGOLE ATTIVE S316

#4 critica strutturale · #12 Keychain GUI required · #14 CTO autonomous (C1-C5, F) · #15 NO A/B · #16 research-first · **#18 META-VINCOLO (D BLOCCANTE)** · #20 CF token · **#22 critique-then-ignore mitigation: Stripe API verify slug+product mandatory pre C1-C5 deploy**

## REGOLA #22 STRENGTHENED (post-S314, ribadita S316)

Pattern critique-then-ignore ricorrenza 5: **S296→S303→S305→S306→S313**. Mitigazione mandatory:
- Evidence gate PROD per URL Stripe MUST include Stripe API query (sk_live_) + slug match + line_items product+price match, NO HEAD 200 shortcut.
- Per ogni "anomalia" / "warning" flagged: STOP gate, NO closure verde fino a verdict deterministico.

## ARTEFATTI PRONTI

- Commit HEAD: aggiornato S315 (vedi `git log -1`)
- Worker prod version: `e18df659-bed2-4491-a8fe-9fef9e398b2e` (invariato S314)
- 13 secrets prod (incl. LICENSE_RECOVERY_SECRET)
- Resend domain `fluxion-app.com` id `6f986180-2eaf-41e2-8a40-53ebeefedbf0` verified
- Evidence S314: `~/venture-os/state/s314-finding-e7-bug.json`
- HTTP Bridge S315: tauri-app PID 19684 listening 3001 su iMac

## DECISIONI LUKE PENDENTI (escalate post primo CLOSED_WON)

1. `magazzino` scope v1.0 o post-launch?
2. `9 verticali` fonte canonica?
3. macOS code signing → firma o ad-hoc + Gatekeeper page?
4. Nuovo CF token `Zone DNS Edit` 90d TTL?
5. DMARC `p=none` → `p=quarantine` schedule?
6. `ED25519_KID` secret prod — investigate usage, add/remove?
7. Stripe LIVE sk_live_ in `~/.claude/.env.fluxion-live` per CTO autonomous LIVE ops?

## NOTE OPERATIVE

- **STRIPE_API_KEY in `~/.claude/.env`** = TEST mode (`sk_test_`, len=107). Per ops LIVE serve founder action o richiesta Luke per `sk_live_`.
- **CF token `FLUXION-CTO-Deploy-90d`** (`3856673a...`) valido per deploy + secret put PROD.
- **Stripe outage S315**: monitorare `https://status.stripe.com/` prima di F1-F4 retry.
