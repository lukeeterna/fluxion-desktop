# Prompt ripartenza S317 — Smoke E2E LIVE €1 simbolico + D-1/D-2/D-3 + F closure C-FLUXI-002

> **Generato S316 chiusura verde C-API-1..C-API-8 PASS** (Stripe LIVE Payment Links creati + landing deployed prod + worker secrets LIVE put).
> **Vincolo founder**: no €497 disponibili → smoke con €1 simbolico (path 100% identico produzione, refund 1-click post-test).

## 🎯 DIRETTIVA LUKE (invariata)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con primo CLOSED_WON validato end-to-end.

## ✅ S316 OUTCOME (CTO autonomous PASS)

| Task | Status | Evidence |
|------|--------|----------|
| C-API-1 inventory products LIVE | ✅ DONE | Base `prod_UBT1Dg0l0bYO4C` price `price_1TD65hIW4bHDTsaHFs3O3iMk` 49700 eur one_time / Pro `prod_UBT51LsziQDyYd` price `price_1TD68vIW4bHDTsaHLqGMGSCj` 89700 eur one_time |
| C-API-2 marketing copy | ✅ DONE | descriptions + 6 marketing_features ciascuno (Base+Pro), Pro feature #5 cosmetic `+` → space (low-priority fix) |
| C-API-3 Payment Link BASE LIVE | ✅ DONE | `plink_1TcpAkIW4bHDTsaH8boabwRX` → `https://buy.stripe.com/8x2aEYg4T8BUeLZcMi24003` |
| C-API-4 Payment Link PRO LIVE | ✅ DONE | `plink_1TcpAkIW4bHDTsaHfn8dioIo` → `https://buy.stripe.com/dRm4gA2e39FY47l13A24004` |
| C-API-5 Webhook LIVE | ✅ DONE | `we_1TcpBLIW4bHDTsaHIap86lRB` 3 eventi (checkout.session.completed + payment_intent.succeeded + charge.refunded) + duplicato `we_1TD6liIW4bHDTsaHr1LIrukH` deleted |
| C-API-6 Secrets prod LIVE | ✅ DONE | `STRIPE_WEBHOOK_SECRET` whsec_ LIVE + `STRIPE_SECRET_KEY` sk_live_ put su worker `fluxion-proxy` (root env = production) |
| C-API-7 Landing edit | ✅ DONE | `landing/checkout-consent.html` line 125+131 swap slug LIVE + REGOLA #22 Stripe API cross-check slug→product MATCH PASS |
| C-API-8 Deploy + verify | ✅ DONE | CF Pages branch=main deploy URL `260706e3.fluxion-landing.pages.dev` → prod `fluxion-landing.pages.dev/checkout-consent.html` verify 3× consecutive slug LIVE match |
| Worker prod health | ✅ DONE | `/health` HTTP 200 post-secrets-update |
| Evidence | ✅ DONE | `~/venture-os/state/s316-c-api-evidence.json` 1.7KB JSON completo |

**Bug E-7 S314 RISOLTO**: slug swap `base`↔`pro` + slug TEST→LIVE in unica operazione, cross-check API pre-deploy.

## SCOPE S317 (ordine esecuzione)

### Pre-flight S317 (CTO autonomous)

```bash
# 1. Stripe LIVE key + worker prod health
source ~/.claude/.env.fluxion-live
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" "https://api.stripe.com/v1/balance" -u "${STRIPE_LIVE_SECRET_KEY}:"
curl -sS -w "\nHTTP=%{http_code}\n" "https://fluxion-proxy.gianlucanewtech.workers.dev/health"

# 2. Landing prod slug LIVE still match
curl -sSL "https://fluxion-landing.pages.dev/checkout-consent.html?plan=base&_cb=$(date +%s)" | grep -oE "buy.stripe.com/[a-zA-Z0-9_]+"
# Expected: 8x2aEYg4T8BUeLZcMi24003 + dRm4gA2e39FY47l13A24004

# 3. HTTP Bridge iMac (per D-2)
ssh imac "lsof -iTCP:3001 -sTCP:LISTEN; tail -5 /tmp/fluxion-tauri-dev.log"
# Expected: tauri-app listening localhost:3001
# Se DOWN: ssh imac 'bash -lc "source ~/.nvm/nvm.sh && nvm use 20.11.0 && cd \"/Volumes/MacSSD - Dati/fluxion\" && nohup npm run tauri dev > /tmp/fluxion-tauri-dev.log 2>&1 & echo PID=\$!"'
```

### Step S1 — CTO autonomous: crea NEW price €1 + Payment Link smoke

**Razionale €1 simbolico**: founder no €497 disponibili. €0 NO (Stripe LIVE minimum charge €0.50 hard-limit per `payment_intent` su carte). Path €1 = 100% identico €497 (webhook event, sign, resend, license).

```bash
source ~/.claude/.env.fluxion-live

# Create €1 price one_time su prod Base esistente
PRICE_SMOKE=$(curl -sS -X POST "https://api.stripe.com/v1/prices" \
  -u "${STRIPE_LIVE_SECRET_KEY}:" \
  -d "unit_amount=100" \
  -d "currency=eur" \
  -d "product=prod_UBT1Dg0l0bYO4C" \
  -d "nickname=S317 smoke €1" \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")
echo "PRICE_SMOKE=$PRICE_SMOKE"

# Create Payment Link smoke
PLINK_SMOKE=$(curl -sS -X POST "https://api.stripe.com/v1/payment_links" \
  -u "${STRIPE_LIVE_SECRET_KEY}:" \
  -d "line_items[0][price]=$PRICE_SMOKE" \
  -d "line_items[0][quantity]=1" \
  -d "after_completion[type]=redirect" \
  -d "after_completion[redirect][url]=https://fluxion-proxy.gianlucanewtech.workers.dev/success/{CHECKOUT_SESSION_ID}" \
  -d "metadata[plan]=base" \
  -d "metadata[fluxion_version]=v1" \
  -d "metadata[smoke_test]=S317" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['id'],d['url'])")
echo "PLINK_SMOKE=$PLINK_SMOKE"

# Persist for S317 cleanup post-smoke
echo "$PRICE_SMOKE" > ~/venture-os/state/s317-smoke-price-id.txt
echo "$PLINK_SMOKE" > ~/venture-os/state/s317-smoke-plink.txt
```

### Step S2 — Avvio wrangler tail real-time (CTO autonomous background)

```bash
cd /Volumes/MontereyT7/FLUXION/fluxion-proxy
npx wrangler tail fluxion-proxy --format pretty > /tmp/s317-tail.log 2>&1 &
TAIL_PID=$!
echo "TAIL_PID=$TAIL_PID, log /tmp/s317-tail.log"
```

### Step S3 — Founder pagamento €1 LIVE

1. Founder apre URL PLINK_SMOKE in browser
2. Pagamento con carta reale, email `fluxion.gestionale@gmail.com`
3. Stripe processa €1 LIVE → redirect a `/success/{session_id}`

### Step S4 — D-1 Evidence (CTO autonomous)

```bash
# Stop tail
kill $TAIL_PID 2>/dev/null

# Parse tail log: webhook event id + sign + resend + license
grep -E "(webhook|ed25519|resend|license|error)" /tmp/s317-tail.log | tail -30

# Verify Resend email delivered
RESEND_KEY=$(grep RESEND_API_KEY ~/.claude/.env | cut -d= -f2)
# (last 5 emails)
curl -sS "https://api.resend.com/emails" -H "Authorization: Bearer $RESEND_KEY" | python3 -m json.tool | head -50

# Verify D1 webhook_events log
# Verify KV purchase entry
# (requires CF API token con D1+KV scope)
```

### Step S5 — D-2 GUI activate iMac (founder)

1. Founder fisicamente all'iMac (HTTP Bridge già UP)
2. Apre FLUXION app → wizard licenza
3. Incolla email recovery URL ricevuto via Resend
4. Click "Attiva" → Ed25519 unlock + Keychain GUI consent (risolve `User interaction is not allowed`)
5. Screenshot conferma activation + nome licenza unlocked

### Step S6 — D-3 Evidence + Luke GO (CTO autonomous + founder)

CTO scrive `~/venture-os/state/s187-fase1-S317-production-validation.json` con D-1+D-2 evidence. **STOP META-VINCOLO REGOLA #18**: Luke legge → "GO" esplicito o "STOP" con motivo.

### Step S7 — Cleanup smoke + refund €1

```bash
source ~/.claude/.env.fluxion-live

# Refund €1
SESSION_ID=$(...)  # parse from /tmp/s317-tail.log
PI=$(curl -sS "https://api.stripe.com/v1/checkout/sessions/$SESSION_ID" -u "${STRIPE_LIVE_SECRET_KEY}:" | python3 -c "import json,sys;print(json.load(sys.stdin)['payment_intent'])")
curl -sS -X POST "https://api.stripe.com/v1/refunds" -u "${STRIPE_LIVE_SECRET_KEY}:" -d "payment_intent=$PI" -d "reason=requested_by_customer"

# Deactivate smoke Payment Link
PLINK_SMOKE_ID=$(awk '{print $1}' ~/venture-os/state/s317-smoke-plink.txt)
curl -sS -X POST "https://api.stripe.com/v1/payment_links/$PLINK_SMOKE_ID" -u "${STRIPE_LIVE_SECRET_KEY}:" -d "active=false"
```

### Step S8 — F closure C-FLUXI-002 (post-D-3 Luke GO)

```bash
cd /Volumes/MontereyT7/FLUXION
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002 --motivation "primo CLOSED_WON real S317 smoke €1 LIVE PASS D-1+D-2+D-3 evidence Luke GO + E-7 fix S316"
python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
```

## EVIDENCE GATE S317 closure verde

- [ ] Pre-flight Stripe LIVE + worker prod + landing slug + HTTP Bridge iMac
- [ ] S1: price €1 + Payment Link smoke creato
- [ ] S2: wrangler tail started background
- [ ] S3: founder pagamento €1 PASS LIVE
- [ ] S4: D-1 evidence parsed (webhook 200, Ed25519 sign, Resend ID, license generated)
- [ ] S5: D-2 GUI activate iMac PASS + screenshot
- [ ] S6: D-3 JSON evidence + Luke GO esplicito
- [ ] S7: refund €1 PASS + Payment Link smoke deactivated
- [ ] S8: VOS C-FLUXI-002 resolved + gate VERDE

## REGOLE ATTIVE S317

#4 critica strutturale · #12 Keychain GUI required · #14 CTO autonomous (S1+S2+S4+S7+S8) · #15 NO A/B · #16 research-first · **#18 META-VINCOLO (D-3 BLOCCANTE)** · #19 persist secret · #20 CF token · **#22 critique-then-ignore mitigation: pre-action API verify mandatory**

## ARTEFATTI PRONTI S317

- Stripe LIVE Payment Links Base + Pro (`https://buy.stripe.com/8x2aEYg4T8BUeLZcMi24003` + `dRm4gA2e39FY47l13A24004`) creati S316 — NON usati in S317 smoke (riservati primo CLOSED_WON reale post-D-3 GO)
- Worker prod secrets LIVE updated S316 (whsec_ LIVE + sk_live_)
- Landing prod fluxion-landing.pages.dev slug LIVE match verified S316
- Evidence S316: `~/venture-os/state/s316-c-api-evidence.json`
- Stripe LIVE key persisted `~/.claude/.env.fluxion-live` mode 600 (107 char sk_live_, 107 char pk_live_)
- HTTP Bridge iMac PID 19684 listening 3001 (verificare pre-flight S317)

## DECISIONI LUKE PENDENTI (post primo CLOSED_WON)

1. `magazzino` scope v1.0 o post-launch?
2. `9 verticali` fonte canonica?
3. macOS code signing → firma o ad-hoc + Gatekeeper page?
4. Nuovo CF token `Zone DNS Edit` 90d TTL?
5. DMARC `p=none` → `p=quarantine` schedule?
6. `ED25519_KID` secret prod — investigate usage, add/remove?
7. Fix cosmetic Pro feature #5 (`+` → space encoding) — bassa priorità
8. Strategia primo CLOSED_WON reale (post-smoke): self-purchase €497 founder oppure attendere primo cliente acquisito via funnel?

## NOTE OPERATIVE S317

- **STRIPE_LIVE_SECRET_KEY** in `~/.claude/.env.fluxion-live` mode 600 (S316 persist).
- **CF token `FLUXION-CTO-Deploy-90d`** (`3856673a...`) valido per deploy + secret put PROD.
- **Branch CF Pages production = `main`** (NOT `master`). Sempre `--branch=main` per produzione.
- **Production worker env**: root (no `--env` flag). Test env: `--env test`.
- **Refund window Stripe**: 180 giorni — €1 smoke refund senza vincoli temporali.
