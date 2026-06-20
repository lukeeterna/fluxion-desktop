# Prompt ripartenza — S376 IN CORSO (acquisto €1 / path-200)

## 🟡 STATO LIVE — ARM FATTO, ATTESA ACQUISTO MAIL-FRESCA + VERIFICA C (autonoma)

### Fatti già verificati (fonte Stripe live)
- **ARM A1/A2 ✅**: plink `plink_1TeCftIW4bHDTsaHJfwJNndD` → `active:true`. **URL diretto €1** = `https://buy.stripe.com/bJe6oIg4T19s1ZddQm24007`. Landing NON toccata, Base/Pro intatti.
- **2 tentativi ANNULLATI** (founder ha pagato 2× con mail NON fresca `gianlucadistasi81@`, entrambi rimborsati):
  - #1 session `cs_live_a1zar1…` → refund `pyr_1TkLnLIW4bHDTsaHXhye1Evc` (succeeded).
  - #2 session `cs_live_a1j45GVsup1I2sdzPHrESQXRJWrPuB5bf9kPe9yuLVt0WaYlU4M975oeWm` PI `pi_3TkLo0IW4bHDTsaH1mzjE5dr` → refund `pyr_1TkLqsIW4bHDTsaHGsMGHUro` (succeeded).
- ⚠️ MAIL VIETATE (già/forse in D1): `fluxion.gestionale@`, `gianlucadistasi81@`, `ilcombeeretrasher@`. **Usare alias FRESCO** es. `gianlucadistasi81+fluxtest@gmail.com` (consigliato al founder a fine S376).
- **Problema UX**: Stripe ripropila in automatico l'email precedente → founder deve cancellare il campo e digitare l'alias.

### PROSSIMO STEP — VERIFICA C (autonoma CTO, charge vivo, ordine OBBLIGATO)
0. Trova session paid + email reale: `curl -s "https://api.stripe.com/v1/checkout/sessions?limit=3" -u "$KEY:"` (KEY = `source ~/.claude/.env.fluxion-live` → `STRIPE_LIVE_SECRET_KEY`). Usa la mail EFFETTIVAMENTE pagata (verifica alla fonte, NON assumere quale alias).
1. **C1 D1**: `cd fluxion-proxy && npx wrangler d1 execute fluxion-webhook-events --remote --command "SELECT session_id,license_id,customer_email,length(license_payload) lp,length(license_signature) ls,created_at FROM webhook_events WHERE customer_email='<mail-reale>' ORDER BY created_at DESC LIMIT 1"` → riga nuova, `license_id` non-null, `lp>0 ls>0`.
2. **C2 mail** brandizzata (eyeball founder) — logo live + zero blob.
3. **C3 RECOVERY 200** (FATTO CHIAVE mai osservato): `token=hex(HMAC-SHA256(LICENSE_RECOVERY_SECRET, mail.toLowerCase().trim()))` (secret = `~/.claude/.env.s295-recovery-secret`) → `curl "https://fluxion-app.com/api/v1/license/<mail>?token=$token"` → **200 + licenza**.
4. **C4 attivazione app** (founder) → `license_cache` popolata (SSH sqlite, delta id).
5. **C5 SOLO DOPO 1-4 verdi** → refund → recovery stessa mail → **410**.

### Regole
- Se al ritorno NON risulta un charge €1 paid con mail fresca → l'acquisto non è stato completato: ridare URL plink al founder (riattivare plink se `active:false`).
- Step irraggiungibile → BLOCKED-ON, NON simulare.
- NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6.
- ⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → la fonte è l'ultimo commit.
