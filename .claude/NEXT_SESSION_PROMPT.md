# Prompt ripartenza S319 — Post-CLOSED_WON validation, 9 decisioni Luke pendenti ordine ROI

> **Generato S318 chiusura verde**: Luke GO esplicito "GO C-FLUXI-002 no errori" → CTO S318-B autonomous: critique C-FLUXI-002 added (LUKE origin, era citata ma mancante in PLAN.md §CRITIQUE) + resolved + VOS gate VERDE ("nessuna CRITIQUE [OPEN]").
> **C-FLUXI-002 chiusura LOGICA**: production-ready validated end-to-end via €1 smoke S317 (D-1+D-2+D-3 PASS, refund €1 PASS). Primo CLOSED_WON real €497 = scope S319-1.

## ✅ S318 OUTCOME

| Step | Status | Evidence |
|------|--------|----------|
| S318-A Luke GO esplicito META-VINCOLO #18 | ✅ DONE | "GO C-FLUXI-002 no errori" 2026-05-30 ~20:31 UTC |
| S318-B-1 critique add C-FLUXI-002 origin LUKE | ✅ DONE | `critique_add ok` (fix gap PLAN.md §CRITIQUE) |
| S318-B-2 critique resolve C-FLUXI-002 | ✅ DONE | `critique_resolve ok` motivation chain S317 |
| S318-B-3 VOS gate verde | ✅ DONE | `GATE OK: nessuna CRITIQUE [OPEN]` |

## 🚦 SCOPE S319 — 9 decisioni Luke ordine ROI

### Priorità ALTA (revenue/legal blocker)

1. **Primo CLOSED_WON reale strategy** (revenue first sale)
   - A: self-purchase €497 founder → smoke production real, no refund. B: attendere primo cliente organic.
   - **Raccomandazione CTO**: A (€497 → P.IVA founder come business test cost, controllo timing, no esposizione bug residui su paying customer first time).
   - Trigger: Luke GO → CTO autonomous (Payment Link real €497 → /success → Resend → activate, NO refund, keep license).

2. **macOS code signing** (distribuzione blocker)
   - A: ad-hoc + Gatekeeper bypass page (€0). B: Apple Developer Account ($99/anno).
   - **Decisione richiesta Luke** (costo vs friction UX PMI italiane non-tech).

3. **9 verticali canonical source** (architettura scaling)
   - S308.audit-2: 3 fonti discordi (`src/types/setup.ts` 5 macro, `switch_vertical.sh` 9 verticali, CLAUDE.md "8 macro × 50 micro").
   - **Decisione richiesta Luke** → CTO autonomous riallinea multi-file.

### Priorità MEDIA (hardening pre-launch)

4. **Magazzino scope v1.0 o post-launch** (S308.audit-2 ASSENTE)
   - 0 command/migration/UI. Core per auto/gommista, opzionale altrove. Dipende da #3.

5. **Nuovo CF token Zone DNS Edit 90d TTL** (current Deploy-90d no zones)
   - Trigger: future DNS edit require founder UI manuale fino a token nuovo.

6. **DMARC `p=none` → `p=quarantine` schedule** post 100 email production sent
   - CTO autonomous monitor Resend counter + switch quando soglia + 0 fail rate.

### Priorità BASSA (cosmetic + tech debt)

7. **ED25519_KID secret prod** audit usage (grep codebase: populate o cleanup).
8. **Fix cosmetic Pro feature #5** (`+` → space encoding landing) 1-line edit.
9. **Hardening pre-action-check** REGOLA #16 strengthen: grep handler keyword pre script Stripe API (catch metadata key mismatch S317-type).

## ARTEFATTI PRODUCTION READY (post-S317+S318)

- Stripe LIVE Payment Links: Base `plink_1TcpAk...8boabwRX` €497, Pro `plink_1TcpAk...fn8dioIo` €897
- Webhook LIVE `we_1TcpBLIW...IIap86lRB` (3 eventi)
- Worker prod version `2a1b79bc-b7cd-49db-8ab8-5395b2c88c2e` (post detectTier fix S317)
- Landing prod `fluxion-landing.pages.dev/checkout-consent.html` (slug LIVE verified)
- Email domain `fluxion-app.com` verified Resend (DKIM+SPF+DMARC delivery confirmed)
- VOS gate VERDE (zero CRITIQUE [OPEN]) — S318 chiusura
- Evidence: `~/venture-os/state/s317-d1-evidence.json` + `~/venture-os/state/s187-fase1-S317-production-validation.json`

## REGOLE ATTIVE S319

- **#4** critica + autocritica 4 punti
- **#13** pre-action-check D-XX rif
- **#14** CTO autonomous (post-GO S319-1, +S319-3 follow-up, +S319-6/7/8/9)
- **#15** NO A/B (eccezione: S319-1, S319-2 scope/cost decisions richiedono Luke)
- **#16** research-first (S319-2 friction Gatekeeper PMI prima proposta)
- **#22** critique-then-ignore mitigation (gate VERDE conferma chiusura pattern S296→S317)

## QUICK START S319

```bash
cd /Volumes/MontereyT7/FLUXION
cat .claude/NEXT_SESSION_PROMPT.md
# Luke decide ordine #1..9. CTO autonomous esegue dove possibile.
# #1 self-purchase: CTO crea Payment Link + URL Luke + wrangler tail post-pay
# #2 signing: CTO deep-research friction Gatekeeper PMI prima proposta
# #3 verticali: Luke decide canonical → CTO multi-file realign
```

## CONTEXT BUDGET S318

- Chiusura ordinata a 63% (soglia 60% VOS mandate raggiunta).
- Files toccati S318: questo file (non-critico per slugs gate). Zero source-code modifications.
- S319 boot stimato ~18% → ~28% headroom safe per decisioni Luke.
