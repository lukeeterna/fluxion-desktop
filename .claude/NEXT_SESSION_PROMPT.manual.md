# Prompt ripartenza S318 — Luke GO esplicito META-VINCOLO + S8 VOS critique resolve C-FLUXI-002

> **Generato S317 chiusura verde con CTO autonomous fix bug FBUG-DETECT-TIER-METADATA-KEY-01 + D-1+D-2+D-3 PASS** (Stripe €1 LIVE → webhook → D1 → Ed25519 → /success → Resend delivered → founder GUI activate iMac → refund €1 + PL smoke deactivated).
> **Vincolo founder rispettato**: smoke €1 simbolico (refund 1-click PASS, founder no spesa). Path 100% identico €497 production.

## 🎯 DIRETTIVA LUKE (invariata)
"Segui la roadmap e vai dritto verso la produzione con parametri VOS".
Scope locked = chiusura `C-FLUXI-002` con primo CLOSED_WON validato end-to-end.

## ✅ S317 OUTCOME (CTO autonomous PASS)

| Step | Status | Evidence |
|------|--------|----------|
| Pre-flight 4/4 | ✅ DONE | Stripe LIVE balance 200, worker /health 200, landing slug LIVE match, HTTP Bridge iMac UP |
| S1 price €1 + PL smoke | ✅ DONE | `price_1TcsBsIW4bHDTsaHeLb8zaOn` + `plink_1TcsC6IW4bHDTsaHDDYHUExu` |
| S2 wrangler tail | ⚠️ INITIAL SKIP | output buffering opaco; tail3 attivato post-deploy con CF token = capture webhook redelivery PASS |
| S3 founder pagamento €1 LIVE | ✅ DONE | session `cs_live_a152jM61CLVrYaD8YAGf620jrx0xuyJy4oggMjkUD4gYvjYTshRt5vcnis` paid, payment_intent `pi_3TcsGUIW...` |
| **BUG FBUG-DETECT-TIER-METADATA-KEY-01** | ✅ FIXED | `detectTier()` accetta `metadata.tier ?? metadata.plan` — production hardening 1-line, NO impatto €497/€897 (AMOUNT_TO_TIER fallback) |
| Deploy fix worker prod | ✅ DONE | version `2a1b79bc-b7cd-49db-8ab8-5395b2c88c2e`, tsc 0 err + vitest 36/36 PASS |
| Founder Stripe dashboard webhook resend | ✅ DONE | event `evt_1TcsGXIW4bHDTsaHRkJF08tr` redelivered post-fix → 200 |
| S4 D-1 evidence | ✅ DONE | license_id `3b6e97cb0c6c0ef57c6503a263846b54c9788c1f1ff796021036887f0486c419`, Resend `edc52a92-4bbb-4620-a6d0-be3877a1febc` delivered from `licenze@fluxion-app.com`. JSON: `~/venture-os/state/s317-d1-evidence.json` |
| S5 D-2 GUI activate iMac | ✅ DONE | founder conferma "licenza attivata" ~20:23 UTC, Keychain GUI consent PASS (REGOLA #12) |
| S6 D-3 evidence + Luke GO | ⏳ PENDING META-VINCOLO #18 | `~/venture-os/state/s187-fase1-S317-production-validation.json` consolidato D-1+D-2 evidence. **Luke deve scrivere "GO C-FLUXI-002" esplicito S318** |
| S7 refund €1 + cleanup | ✅ DONE | `re_3TcsGUIW4bHDTsaH1G4siEJl` status=succeeded amount=100, PL smoke deactivated 200 |
| S8 VOS critique resolve | ⏳ PENDING | bloccato da Luke GO S6 |

## 🚦 SCOPE S318 (single blocking action + cleanup)

### Step S318-A — Luke esplicito GO META-VINCOLO REGOLA #18

CTO presenta evidence consolidato:
- `~/venture-os/state/s187-fase1-S317-production-validation.json` (D-1+D-2+D-3 verdict PASS)
- `~/venture-os/state/s317-d1-evidence.json` (chain end-to-end completa)

Luke legge **e scrive una di queste**:
- ✅ `"GO C-FLUXI-002"` → S318-B procede
- ⛔ `"STOP C-FLUXI-002 motivo: <X>"` → CTO opens follow-up task S319

### Step S318-B — VOS critique resolve + gate (CTO autonomous post-GO)

```bash
cd /Volumes/MontereyT7/FLUXION
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-FLUXI-002 \
  --motivation "primo CLOSED_WON real S317 smoke €1 LIVE PASS D-1 (Stripe→webhook→D1→Ed25519→Resend delivered) + D-2 GUI activate iMac PASS + D-3 refund+cleanup PASS + bug FBUG-DETECT-TIER-METADATA-KEY-01 fixed → production-hardening worker accetta metadata.tier OR metadata.plan, no impatto €497/€897 prod (AMOUNT_TO_TIER fallback)"

python3 ~/.vos/vos_plan.py gate /Volumes/MontereyT7/FLUXION
```

Expected: critique C-FLUXI-002 status `RESOLVED`, gate `VERDE`.

### Step S318-C — Decisioni Luke pendenti (post-CLOSED_WON, da affrontare ordine ROI)

1. **Primo CLOSED_WON reale strategy**: self-purchase €497 founder per smoke production-grade oppure attendere primo cliente organic via funnel?
2. **macOS code signing**: ad-hoc + Gatekeeper page OR Apple Developer Account ($99/anno)?
3. **Magazzino scope v1.0** o post-launch?
4. **9 verticali canonical source** (sync verticals across landing + app + voice)
5. **Nuovo CF token `Zone DNS Edit` 90d TTL** (current CTO-Deploy-90d no zones)
6. **DMARC `p=none` → `p=quarantine` schedule** post primo 100 email sent
7. **ED25519_KID secret prod** investigate usage, add/remove
8. **Fix cosmetic Pro feature #5** (`+` → space encoding) bassa priorità
9. **Hardening pre-action-check**: aggiungere step "grep handler keyword" su ogni script che invoca API Stripe (catch metadata key mismatch S317 type) — TODO REGOLA #16

## REGOLE ATTIVE S318

- **#4 critica strutturale** + autocritica 4 punti su REGOLA #16 fail S317 (NEXT_SESSION_PROMPT.manual.md S1 ha hardcoded `metadata[plan]` senza grep handler)
- **#12** Keychain GUI required (verificato S317 D-2)
- **#13** pre-action-check D-XX rif su decisioni S318 1-9
- **#14** CTO autonomous (S318-B post-GO)
- **#15** NO A/B
- **#16** research-first
- **#18 META-VINCOLO** (D-3 BLOCCANTE Luke GO esplicito = S318-A)
- **#22** critique-then-ignore mitigation (S317 evidence chain è esempio applicato)

## ARTEFATTI PRONTI S318

- **Production LIVE artifacts ready** (smoke validated, awaiting real €497):
  - Stripe LIVE Payment Link Base `https://buy.stripe.com/8x2aEYg4T8BUeLZcMi24003` (€497 one-time)
  - Stripe LIVE Payment Link Pro `https://buy.stripe.com/dRm4gA2e39FY47l13A24004` (€897 one-time)
  - Webhook LIVE `we_1TcpBLIW4bHDTsaHIap86lRB` (3 eventi)
  - Worker prod version `2a1b79bc-b7cd-49db-8ab8-5395b2c88c2e` (post-fix detectTier)
  - Landing prod `fluxion-landing.pages.dev/checkout-consent.html` (slug LIVE verified S316 + S317)
  - Email domain verified `fluxion-app.com` (Resend DKIM+SPF+DMARC, founder confirmed delivery)
- **Evidence files S317**:
  - `~/venture-os/state/s317-d1-evidence.json` (5-step chain end-to-end)
  - `~/venture-os/state/s187-fase1-S317-production-validation.json` (META-VINCOLO consolidato D-1+D-2+D-3)
- **Smoke artifacts** (refunded/deactivated):
  - `price_1TcsBsIW4bHDTsaHeLb8zaOn` €1 LIVE (dormant)
  - `plink_1TcsC6IW4bHDTsaHDDYHUExu` deactivated
  - Refund `re_3TcsGUIW4bHDTsaH1G4siEJl` succeeded

## NOTE OPERATIVE S318

- **Stripe webhook resend Live**: NO API REST disponibile, SOLO dashboard click founder. Pattern carry-over per future debug webhook prod (S317 step founder ~1-click @ `https://dashboard.stripe.com/webhooks/we_1TcpBLIW4bHDTsaHIap86lRB`).
- **wrangler tail su MacBook macOS 11**: prima invocazione no output (buffering), seconda invocazione con CF token env exportato funziona — workaround = avviare tail PRIMA di redelivery.
- **Token D1 query REST**: `CF_API_TOKEN` (id `3856673a...` FLUXION-CTO-Deploy-90d) HA permission `wrangler secret list` + `wrangler deploy` MA **NO D1 query** (error 7403). Per future query D1 prod: o creare nuovo token con D1 scope OR usare `/success/{session_id}` come probe indiretto (legge D1 + render).
- **REGOLA #16 candidata strengthening**: pre-action-check su script che invoca API Stripe DEVE includere `grep <metadata_key>` su `src/routes/stripe-webhook.ts` per catch key mismatch before script run.
