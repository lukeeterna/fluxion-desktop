# Prompt ripartenza — S376 🟢🟢🟢 PILA-1 E2E COMPLETA su charge reale fresco

## 🟢 RISULTATO S376 — catena acquisto→licenza→recovery→attivazione→gate-rimborso PROVATA
Charge €1 reale, mail FRESCA `manueldx2014@gmail.com` (n=1 D1), session `cs_live_a1vYPgFHRrvfjS13I5KgusrysCK7vc0HH2qLGtjtOSW7Qq5MkIHH5wKN6K`, PI `pi_3TkMDOIW4bHDTsaH271C8e6o`.
- **C1 D1 ✅**: license_id `38ce18393a33cfc2`, payload=256, firma=88.
- **C3 recovery 200 ✅** (FATTO CHIAVE, primo path-200): GET `fluxion-app.com/api/v1/license/<mail>?token=hmac` → 200 + licenza (license_id = C1). Token = `hex(HMAC-SHA256(secret, mail.lower().trim()))`, secret = riga unica `~/.claude/.env.s295-recovery-secret`.
- **C4 app active ✅**: founder attivato su **Windows** (`ssh fluxion-win`, DB `C:\Users\gianluca\AppData\Roaming\com.fluxion.desktop\fluxion.db`, dati nel WAL→copiati su Mac). `license_cache` id=1, license_id `38ce18393a33cfc2`, tier=base, **status=active**, manueldx2014@gmail.com, ed25519=1.
- **C5 refund→410 ✅**: refund `re_3TkMDOIW…` → recovery stessa mail → **HTTP 410** `{"code":"REFUNDED"}`. Gate-rimborso provato su charge vivo. €1 riaccreditato.
- C2 mail eyeball = founder (secondario, non load-bearing).
- Stripe pulito: tutti i charge rimborsati (3 mail-sbagliate + manueldx2014). Costo netto €0.

## ⚠️ DA RIVEDERE (raccolti S376, prompt giudice in `.claude/cache/s376-review-giudice.md`)
1. **Re-prompt licenza in Impostazioni**: wizard accetta licenza → Impostazioni la richiede di nuovo, NONOSTANTE `license_cache.status=active`. = bug display/refresh, NON perdita dati (persistenza verificata).
2. **Node-lock**: campo Impostazioni mostra "questa è la licenza del tuo mac" MA `license_cache.machine_id` è **vuoto** nel DB. Coerenza wording↔binding da chiarire (node-lock Q4/Q6 = post-CLOSED_WON).
3. **success_url plink** = `https://stripe.com` (non success-page FLUXION) → cliente non vede la pagina post-acquisto. Il plink €1 è solo test, ma verificare che i link Base/Pro pubblici abbiano success_url corretto.

## NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6 (post-CLOSED_WON).
⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
