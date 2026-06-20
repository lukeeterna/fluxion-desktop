# Prompt ripartenza — S376 IN CORSO (acquisto €1 / path-200)

## 🟡 STATO LIVE — ARM FATTO, ATTESA ACQUISTO MAIL-FRESCA + VERIFICA C

### Fatti già verificati (fonte Stripe live)
- **ARM A1 ✅**: plink `plink_1TeCftIW4bHDTsaHJfwJNndD` → riattivato `active:true` (era false). **URL diretto €1** = `https://buy.stripe.com/bJe6oIg4T19s1ZddQm24007`.
- **A2 ✅**: usato URL diretto plink (NO landing toccata, Base/Pro €497/€897 intatti).
- **Tentativo #1 ANNULLATO**: founder ha pagato €1 con mail **NON fresca** `gianlucadistasi81@gmail.com` (in lista vietata/già-in-D1) → session `cs_live_a1zar1jwuThP8SHz0OojeWLIxAbd3UYAm4jEjrOsZTCQOTLgwK1vkk43sP` → **REFUND fatto** `pyr_1TkLnLIW4bHDTsaHXhye1Evc` (succeeded, €1). PI `pi_3TkLgRIW4bHDTsaH1h7p4RCT`.
- ⚠️ MAIL VIETATE (già in D1, NON usare): `fluxion.gestionale@`, `gianlucadistasi81@`, `ilcombeeretrasher@`. **Serve mail MAI usata** (es. alias `gianlucadistasi81+testN@gmail.com`).

### PROSSIMO STEP — VERIFICA C (charge vivo, ordine OBBLIGATO, non invertire)
Appena founder paga €1 con **mail fresca** (NON rimborsare):
0. Ricava session+email reale: `curl -s "https://api.stripe.com/v1/checkout/sessions?limit=3" -u "$KEY:"` (KEY = `source ~/.claude/.env.fluxion-live` → `STRIPE_LIVE_SECRET_KEY`). Trova la `paid` con la mail fresca.
1. **C1 D1**: `cd fluxion-proxy && npx wrangler d1 execute fluxion-webhook-events --remote --command "SELECT session_id,license_id,customer_email,length(license_payload) lp,length(license_signature) ls,created_at FROM webhook_events WHERE customer_email='<mail-fresca>' ORDER BY created_at DESC LIMIT 1"` → riga nuova, `license_id` non-null, `lp>0 ls>0`.
2. **C2 mail** brandizzata (eyeball founder) — logo live + zero blob.
3. **C3 RECOVERY 200** (FATTO CHIAVE, mai osservato): `token=hex(HMAC-SHA256(LICENSE_RECOVERY_SECRET, mail.toLowerCase().trim()))` (secret = `~/.claude/.env.s295-recovery-secret`) → `curl "https://fluxion-app.com/api/v1/license/<mail>?token=$token"` → **200 + licenza**.
4. **C4 attivazione app** (founder) → `license_cache` popolata (SSH sqlite, delta id).
5. **C5 SOLO DOPO 1-4 verdi** → refund → recovery stessa mail → **410** (prova gate-rimborso su charge vivo).

### Regole
- Step irraggiungibile in-sessione → BLOCKED-ON, NON simulare.
- NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6 (post-CLOSED_WON).
- ⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → la fonte è l'ultimo commit.
