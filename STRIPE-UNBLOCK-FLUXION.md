# Sblocco C-LIC-001 — Stripe production credentials FLUXION

> Generato da CC 2026-05-28. Azione richiesta: **Luke** (CC non può fare login per te).
> Tempo realistico: **20-40 min lato tuo + 1-3 giorni verifica Stripe** (account business review).

## Prerequisito reale che pochi dicono

Stripe Italia in modalità **live** richiede:
- **P.IVA attiva** (forfettaria va bene)
- **IBAN intestato a te / alla tua ditta individuale**
- **Documento identità** scansionato
- **Indirizzo verificabile** (la verifica può richiedere bolletta recente)

Se P.IVA non è ancora aperta → blocco hard, non procedere. Se aperta → vai.

## Passi concreti (in ordine)

### 1. Crea account business Stripe Italia
- URL: `https://dashboard.stripe.com/register`
- Email: usa la tua professionale (NON la personale se hai partita IVA distinta)
- Country: **Italy**
- Business type: **Individual / Sole Proprietor** (ditta individuale forfettaria)

### 2. Completa "Activate your account" (modalità live)
Dashboard → in alto a destra dovrebbe esserci un banner "Activate your account". Click.

Sezioni da compilare:
- Business details: nome attività (può essere il tuo nome), P.IVA, indirizzo
- Public details: nome che apparirà sul card statement del cliente — **importante**, scegli "FLUXION" o "Gianluca Di Stasi" coerente con cosa il cliente si aspetta dopo aver pagato
- Bank account: IBAN per i payout
- Identity verification: documento identità

**Verifica può richiedere 1-3 giorni** lavorativi. Riceverai email quando approvato.

### 3. Generazione chiavi LIVE (solo dopo verifica completata)
- Dashboard → Developers → API keys
- Vedrai due colonne: **Test mode** e **Live mode** (toggle in alto)
- Attiva **Live mode**
- Copia:
  - `Publishable key` (inizia con `pk_live_...`)
  - `Secret key` (inizia con `sk_live_...`) — **click "Reveal" UNA volta, poi non più mostrata**

### 4. Inserisci le chiavi in FLUXION
Dalla shell, NON da git:

```bash
cd /Volumes/MontereyT7/FLUXION
# se .env non esiste, copia da template
[ -f .env ] || cp .env.example .env
# aggiungi/aggiorna queste righe (sostituisci con i tuoi valori)
cat >> .env << 'STRIPE_EOF'

# Stripe LIVE (aggiunto manualmente da Luke 2026-XX-XX)
STRIPE_SECRET_KEY=sk_live_QUI_LA_TUA_CHIAVE
STRIPE_PUBLISHABLE_KEY=pk_live_QUI_LA_TUA_CHIAVE
STRIPE_EOF
# VERIFICA che .env sia in .gitignore (deve esserlo)
grep -q "^\.env$" .gitignore && echo "OK .env gitignored" || echo "ATTENZIONE: aggiungi .env a .gitignore PRIMA di committare"
```

### 5. Risolvi C-LIC-001 e ri-controlla maturity
```bash
python3 ~/.vos/vos_plan.py critique resolve /Volumes/MontereyT7/FLUXION C-LIC-001
python3 ~/.vos/vos_plan.py maturity /Volumes/MontereyT7/FLUXION
# DISTANZA dovrebbe scendere a 0 blocchi [ASSUMPTION] → primo sale possibile
```

### 6. Aggiorna PROSSIMA_AZIONE in PLAN.md
Dopo unblock, la PROSSIMA_AZIONE diventa:
> "Configurare webhook Stripe + endpoint license-delivery per primo sale test su account amico"

## Cosa NON fare

- **NON** committare le chiavi `sk_live_...` in git. Mai. Anche se cancelli il commit, GitHub le scansiona e Stripe le revoca automaticamente.
- **NON** usare le chiavi `sk_test_...` per onboarding reale: Stripe le rifiuta su carte vere.
- **NON** dare le chiavi a nessuno (incluso me in chat se rigenero questo dossier).

## Domande aperte (su cui CC può aiutarti dopo unblock)

- Webhook endpoint per `checkout.session.completed` → bind a license-delivery in FLUXION
- Test sandbox con carta `4242 4242 4242 4242` (anche post-live, mode test funziona ancora in parallelo)
- Refund flow (memoria research-stripe-refund già fatta in FLUXION/.claude/cache)
