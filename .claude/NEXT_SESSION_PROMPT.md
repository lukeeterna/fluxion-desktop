# Prompt ripartenza — S376 🟢 PATH-200 CHIUSO (recovery 200 su charge vivo)

## 🟢🟢 RISULTATO S376 — PATH-200 RECOVERY PROVATO (autonomo CTO, fonte reale)
Acquisto €1 LIVE non-rimborsato con mail FRESCA `manueldx2014@gmail.com` (n=1 in D1, mai usata).
- **Session**: `cs_live_a1vYPgFHRrvfjS13I5KgusrysCK7vc0HH2qLGtjtOSW7Qq5MkIHH5wKN6K` · paid/complete · €1 · PI `pi_3TkMDOIW4bHDTsaH271C8e6o`.
- **C1 D1 ✅**: 1 riga, `license_id 38ce18393a33cfc2…`, payload=256, firma=88.
- **C3 RECOVERY 200 ✅ (FATTO CHIAVE)**: `GET fluxion-app.com/api/v1/license/manueldx2014@gmail.com?token=<HMAC>` → **HTTP 200**, body `{license_id 38ce18393a33cfc20b28 (=C1), tier, license_payload(256), license_signature(88), issued_at}`. Token = `hex(HMAC-SHA256(secret, email.lower().trim()))`, secret = riga unica `~/.claude/.env.s295-recovery-secret`. **Primo path-200 mai osservato.**
- ⚠️ NOTA config: il payment-link `plink_1TeCftIW4bHDTsaHJfwJNndD` ha `success_url: https://stripe.com` → NON redirige alla success-page FLUXION (founder non l'ha vista). La success-page Q5 (no-blob) NON è stata osservata visivamente in questo giro — ma è indipendente, già verificata via curl in S375.

## RESTA (founder-dipendente, NON simulare)
- **C2 mail**: founder apre inbox `manueldx2014@gmail.com` (account suo?) → eyeball template brandizzato (logo + zero blob). [esterno founder]
- **C4 attivazione app**: founder apre FLUXION (iMac/Win), carica la licenza (recovery-link o `.lic`) → CTO verifica `license_cache` popolata (SSH sqlite, delta id). Pipeline iMac DOWN ora.
- **C5 SOLO DOPO C4**: refund del charge `pi_3TkMDOIW…` → ri-chiama recovery stessa mail → atteso **410** (prova gate-rimborso su charge vivo). Refund: `curl -s -X POST https://api.stripe.com/v1/refunds -u "$KEY:" -d payment_intent=pi_3TkMDOIW4bHDTsaH271C8e6o`.
- ⚠️ Charge €1 `manueldx2014` è LIVE non-rimborsato: tenerlo finché C4 fatto, poi C5.

## Stato Stripe pulito (refund precedenti)
3 tentativi mail-non-fresca tutti rimborsati: gianlucadistasi81 ×2 (`pyr_1TkLnL…`,`pyr_1TkLqs…`), ilcombeeretrasher ×1 (`re_3TkLsD…`). Solo manueldx2014 resta vivo (voluto).

## Regole
- NON toccare: T2/T3/Q5 (verde), node-lock Q4/Q6 (post-CLOSED_WON).
- ⚠️ Hook PostToolUse rigenera questo file in boilerplate dopo ogni Bash → fonte = ultimo commit.
