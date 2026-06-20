# Prompt ripartenza — S376 🟢 PILA-1 E2E VERDE + verdetto giudice 3 review

## 🟢 S376 — PILA-1 PROVATA E2E (charge reale fresco manueldx2014, costo €0)
C1 D1 ✅ · C3 recovery **200** ✅ (path-200) · C4 app **active** su Windows ✅ · C5 refund→**410** ✅. Dettaglio in commit `3b662d4`. Tutti i charge rimborsati.

## VERDETTO GIUDICE (3 review) — ordine di lavoro
Prompt giudice: `.claude/cache/s376-review-giudice.md`. Risposta ricevuta, sintesi:
1. **success_url** (Punto 3) = blocker condizionato, **sondare per primo** (ignoto-letale). → **VERIFICATO S376, vedi sotto**.
2. **Re-prompt licenza in Impostazioni** = blocker fiducia, fix localizzato: la pagina Impostazioni deve **rileggere `license_cache` al mount** invece di assumere "non attivata". (persistenza OK, status=active → è display, non dati).
3. **Wording "licenza del tuo mac"** = NON blocker ma fix obbligatorio 1-stringa: dicitura neutra ("Licenza attiva"/"La tua licenza FLUXION") finché node-lock Q6 non popola `machine_id`. **NON implementare node-lock** (scope chiuso post-CLOSED_WON); `machine_id` vuoto è atteso/corretto.

## 🟢 PUNTO 3 — CHIUSO (S377, verificato alla fonte Stripe LIVE API)
**Risposta**: la landing pubblica (`landing/checkout-consent.html`) usa già i link BUONI:
- Base €497 → `…8boabwRX` (short `…24003`) → success-page ✅ (active=True)
- Pro €897 → `…fn8dioIo` (short `…24004`) → success-page ✅ (active=True)

**Root cause scoperto (REGOLA #11)**: non un singolo link vagante, ma URL checkout pre-S104 stale su più superfici prodotto, tutti →`/grazie`:
- `…24000` (Base zombie ATTIVO) e `…24001` (Pro zombie INATTIVO) erano ancora in: `src/types/license-ed25519.ts`, `voice-agent/data/sales_knowledge_base.json` (Sara sales KB), `fluxion-proxy/src/routes/nlu-proxy.ts`, `src/components/license/SaraTrialBanner.tsx`, + 3 agent docs.
**Fix S377**: tutte ripuntate a `…24003`(Base)/`…24004`(Pro). Zombie attivo `plink_1TD6Dp…D2Hii4hA` → `active=false` via API. Ora NESSUN link attivo punta a `/grazie`. Residui solo in `_clinic_disabled.html` (pagina disabilitata) e `.claude/cache/` (research storica) — non live.

## Ordine prossima sessione
1. Fix Punto 1 (Impostazioni rilegge license_cache al mount).
2. Fix Punto 2 (stringa wording neutra).
Tutti zero-cost, nessun codice nuovo significativo, nessuno tocca node-lock.

## NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6.
⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
