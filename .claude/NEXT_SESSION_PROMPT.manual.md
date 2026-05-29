# Prompt ripartenza S315 — Task E-7 fix BLOCKER + Task E-4 + Task D META-VINCOLO #18 (founder-bound) → Task F closure C-FLUXI-002

> **Generato S314 chiusura verde** (CTO autonomous research-first → E-7 bug critico identificato via Stripe API, pre-flight 4/4 PASS).
> **Critica strutturale S313 (REGOLA #4)**: evidence gate S313 ha marcato E-7 `PASS ⚠ anomalia` su base HEAD 200, MA Stripe serve pagina generica 200 per slug inesistenti → era FAIL. Pattern critique-then-ignore (REGOLA #22, 5x: S296/S303/S305/S306/S313).

## 🎯 DIRETTIVA LUKE (invariata)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con primo CLOSED_WON validato end-to-end.

## ✅ S314 OUTCOME — research finding (evidence: `~/venture-os/state/s314-finding-e7-bug.json`)

| Task | Status | Evidence |
|------|--------|----------|
| Pre-flight | ✅ 4/4 PASS | Worker prod /health 200, git clean, Stripe TEST key OK, CF token attivo |
| E-7-VERIFY | 🔴 BUG_CRITICAL | Stripe API TEST query → slug attuali landing puntano a slug TEST con prefisso `test_` MA codice usa NO prefisso. Stripe maschera con HTTP 200 generic page (stesso etag 7e6cf6ca... per entrambe le forme). + SLUG SWAP base↔pro in `landing/checkout-consent.html:125,131` |
| E-4 | ⏸ BLOCKED founder | Stripe LIVE webhook dashboard verify (Stripe TEST key non basta, serve LIVE key o founder dashboard) |
| D-1 | ⏸ BLOCKED founder | Pagamento reale LIVE €497 |
| D-2 | ⏸ BLOCKED founder | GUI activate FLUXION app |
| F | ⏸ post-D | VOS C-FLUXI-002 resolve |

### Mappa bug landing (Stripe API TEST verified)
| Slug attuale landing | Etichetta landing (sbagliata) | Vera identità Stripe |
|---|---|---|
| `00w28sdWL8BU0V9fYu24001` | base €497 | **PRO €897** (`plink_1TRrGrIW4bHDTsaH1KwXKrUJ`, TEST) |
| `bJe7sM19ZdWegU727E24000` | pro €897 | **BASE €497** (`plink_1TRrGqIW4bHDTsaHeX8g37gD`, TEST) |

Doppio bug: **(1) slug swap base↔pro + (2) missing LIVE URL (slug TEST inutili in PROD)**.

## SCOPE S315 (ordine esecuzione)

### S0 — Pre-flight servizi iMac (CTO autonomous, BLOCKING Task D-2)

Verificato S314: iMac UP 7gg+, load 3.96, MA HTTP Bridge (3001) + Voice Pipeline (3002) OFF (dev services manuali, NO LaunchAgent auto-start). Per S315:
- **HTTP Bridge (3001)** = OBBLIGATORIO per Task D-2 GUI activate. Avvio CTO autonomous:
  ```bash
  ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && nohup npm run tauri dev > /tmp/fluxion-tauri-dev.log 2>&1 &"
  sleep 30 && curl -sS http://192.168.1.2:3001/health -w "HTTP=%{http_code}\n"
  ```
- **Voice Pipeline (3002)** = NON necessario S315 (scope = €497 base, Sara is Pro €897 only). Skip.

Evidence S0: log `/tmp/fluxion-tauri-dev.log` su iMac + curl /health 200.

### F1-F4 — Founder Stripe LIVE Payment Links (BLOCKING)

1. Founder login `https://dashboard.stripe.com` → toggle **LIVE mode** (top-right)
2. Products → seleziona `fluxion-base` (€497) → "Create payment link" → copy URL (formato `https://buy.stripe.com/<slug-LIVE-base>`)
3. Products → seleziona `fluxion-pro` (€897) → "Create payment link" → copy URL `https://buy.stripe.com/<slug-LIVE-pro>`
4. Founder share 2 URL LIVE con CTO (incolla qui o channel)

### C1-C5 — CTO autonomous post-founder

1. Edit `landing/checkout-consent.html`:
   - Line 125: `base.stripeUrl = '<LIVE_BASE_URL>'`
   - Line 131: `pro.stripeUrl = '<LIVE_PRO_URL>'`
2. Verify slug swap risolto: `base.stripeUrl` punta a €497, `pro.stripeUrl` a €897
3. `cd /Volumes/MontereyT7/FLUXION && npx wrangler pages deploy landing --project-name=fluxion-landing`
4. Curl verify: `curl -s https://fluxion-landing.pages.dev/checkout-consent.html?plan=base | grep -oE 'buy.stripe.com/[a-zA-Z0-9_]+' | head -1` → match LIVE base slug
5. Curl Stripe API LIVE (richiede `sk_live_`, founder action) per double-check plinks attivi + linked al prodotto giusto

### Task E-4 — Stripe webhook LIVE verify (founder dashboard)

1. Founder `https://dashboard.stripe.com/webhooks` (LIVE mode)
2. Verifica endpoint = `https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/webhook/stripe`
3. Eventi = `checkout.session.completed` minimo
4. SE manca: founder "Add endpoint" → CTO guida + `npx wrangler secret put STRIPE_WEBHOOK_SECRET` con whsec_ LIVE

### Task D — META-VINCOLO REGOLA #18 (BLOCCANTE C-FLUXI-002)

**D-1 Smoke E2E LIVE (post-E-4 OK + post-C1-C5 OK)**:
1. Founder visita `https://fluxion-landing.pages.dev/checkout-consent.html?plan=base` → click consent → redirect LIVE plink €497
2. Founder paga con carta REALE (refund post-test)
3. CTO `wrangler tail fluxion-proxy --env production` osserva webhook 200 + Ed25519 sign + Resend send
4. /success render verify
5. Founder Gmail `fluxion.gestionale@gmail.com` check email `FLUXION <licenze@fluxion-app.com>` + screenshot recovery URL

**D-2 GUI activate**:
1. CTO `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run tauri dev"` background
2. Founder wizard licenza → incolla email → "Attiva" → Ed25519 unlock + screenshot

**D-3 Evidence**: `~/venture-os/state/s187-fase1-S315-production-validation.json` (tabella D-1/D-2 + Luke GO esplicito)

**STOP META-VINCOLO**: CTO NON dichiara `production_ready` senza D-1/D-2/D-3 letti da Luke.

### Task F — Closure C-FLUXI-002 post-D

```bash
cd /Volumes/MontereyT7/FLUXION
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002 --motivation "primo CLOSED_WON real S315 PASS D-1/D-2/D-3 evidence Luke GO + E-7 bug fixed"
python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
```

## EVIDENCE GATE S315 closure verde

- [ ] F1-F4: founder shared 2 LIVE Payment Link URLs
- [ ] C1-C5: landing fixed + deployed + curl verify slug LIVE
- [ ] E-4: Stripe webhook LIVE endpoint verified + whsec_ LIVE put su worker prod
- [ ] D-1: pagamento reale LIVE + Resend email + inbox screenshot
- [ ] D-2: FLUXION app GUI activate PASS + screenshot
- [ ] D-3: S187 FASE 1 evidence + Luke GO esplicito
- [ ] F: VOS C-FLUXI-002 resolved + gate VERDE

## REGOLE ATTIVE S315

#4 critica strutturale · #14 CTO autonomous (C1-C5, F) · #15 NO A/B · #16 research-first (Stripe API verify mandatory) · **#18 META-VINCOLO (D BLOCCANTE)** · #20 CF token · **#22 critique-then-ignore: gate evidence PROD = Stripe API verify per ogni URL, NO HEAD 200 shortcut**

## REGOLA #22 STRENGTHENED (post-S314)

Pattern critique-then-ignore ricorrenza 5: **S296→S303→S305→S306→S313**. Mitigazione mandatory:
- Evidence gate PROD per URL Stripe MUST include Stripe API query (sk_live_ o sk_test_) + slug match, NO HEAD 200 shortcut.
- Per ogni "anomalia" / "warning" flagged: STOP gate, NO closure verde fino a verdict deterministico.

## ARTEFATTI PRONTI

- Commit HEAD S313: `3d451fd`
- Worker prod version: `e18df659-bed2-4491-a8fe-9fef9e398b2e`
- 13 secrets prod (incl. LICENSE_RECOVERY_SECRET)
- Resend domain `fluxion-app.com` id `6f986180-2eaf-41e2-8a40-53ebeefedbf0` verified
- Evidence S314: `~/venture-os/state/s314-finding-e7-bug.json`
- Stripe TEST plinks attivi (per regression test): `plink_1TRrGqIW...` base, `plink_1TRrGrIW...` pro

## DECISIONI LUKE PENDENTI (escalate post primo CLOSED_WON)

1. `magazzino` scope v1.0 o post-launch?
2. `9 verticali` fonte canonica?
3. macOS code signing → firma o ad-hoc + Gatekeeper page?
4. Nuovo CF token `Zone DNS Edit` 90d TTL?
5. DMARC `p=none` → `p=quarantine` schedule?
6. `ED25519_KID` secret prod — investigate usage, add/remove?

## NOTE OPERATIVE

- **Anomalia E-7 risolta in bug**: HEAD 200 era false-positive. Stripe risponde 200 + pagina generica per slug inesistenti. Evidence: stesso etag `7e6cf6ca7e7a9bef5837abbebe50f675` per URL con e senza `test_` prefix.
- **CF token `FLUXION-CTO-Deploy-90d`** (`3856673a...`) valido per deploy + secret put PROD.
- **STRIPE_API_KEY in `~/.claude/.env`** = TEST mode (`sk_test_`, len=107). Per ops LIVE serve founder action o richiesta Luke per `sk_live_` (se vuole abilitare CTO autonomous LIVE ops).
