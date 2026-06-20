# Prompt ripartenza — S376 🟢 PILA-1 E2E VERDE + verdetto giudice 3 review

## 🟢 S376 — PILA-1 PROVATA E2E (charge reale fresco manueldx2014, costo €0)
C1 D1 ✅ · C3 recovery **200** ✅ (path-200) · C4 app **active** su Windows ✅ · C5 refund→**410** ✅. Dettaglio in commit `3b662d4`. Tutti i charge rimborsati.

## VERDETTO GIUDICE (3 review) — ordine di lavoro
Prompt giudice: `.claude/cache/s376-review-giudice.md`. Risposta ricevuta, sintesi:
1. **success_url** (Punto 3) = blocker condizionato, **sondare per primo** (ignoto-letale). → **VERIFICATO S376, vedi sotto**.
2. **Re-prompt licenza in Impostazioni** = blocker fiducia, fix localizzato: la pagina Impostazioni deve **rileggere `license_cache` al mount** invece di assumere "non attivata". (persistenza OK, status=active → è display, non dati).
3. **Wording "licenza del tuo mac"** = NON blocker ma fix obbligatorio 1-stringa: dicitura neutra ("Licenza attiva"/"La tua licenza FLUXION") finché node-lock Q6 non popola `machine_id`. **NON implementare node-lock** (scope chiuso post-CLOSED_WON); `machine_id` vuoto è atteso/corretto.

## ⚠️ PUNTO 3 — VERIFICATO ALLA FONTE (Stripe API), NON pulito
Payment-link ATTIVI con prezzo:
- `plink_1TcpAkIW4bHDTsaHfn8dioIo` €897 Pro → ✅ `…/success/{CHECKOUT_SESSION_ID}` (success-page).
- `plink_1TcpAkIW4bHDTsaH8boabwRX` €497 Base → ✅ `…/success/{CHECKOUT_SESSION_ID}`.
- `plink_1TD6DpIW4bHDTsaHD2Hii4hA` €497 Base (**2° link Base attivo!**) → ⚠️ `fluxion-landing.pages.dev/grazie` (pagina generica, NO recovery/attivazione).
- `plink_1TeCftIW4bHDTsaHJfwJNndD` €1 test → hosted_confirmation (resta Stripe, atteso).
**OPEN**: capire QUALE link Base usa la landing/checkout pubblico. Se è `…D2Hii4hA` (→/grazie) = BLOCKER reale (Base paga e finisce al muro) → disattivarlo e puntare a `…8boabwRX`. Se la landing usa già `…8boabwRX` = `…D2Hii4hA` è zombie da disattivare comunque.
→ Prossimo step: grep nel codice landing/checkout per il payment-link/URL Base usato (`grep -rn "plink_1TD6Dp\|plink_1TcpAk\|buy.stripe" landing/ fluxion-proxy/`), e/o leggere `landing/*checkout*`. Poi disattivare lo zombie via `POST /v1/payment_links/<id> active=false`.

## Ordine prossima sessione
1. Chiudi Punto 3 (grep link Base pubblico → disattiva zombie se serve).
2. Fix Punto 1 (Impostazioni rilegge license_cache al mount).
3. Fix Punto 2 (stringa wording neutra).
Tutti zero-cost, nessun codice nuovo significativo, nessuno tocca node-lock.

## NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6.
⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
