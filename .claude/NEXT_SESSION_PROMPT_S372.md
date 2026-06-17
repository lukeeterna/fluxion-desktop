# FLUXION — NEXT SESSION PROMPT — S372 · CHIUSURA T2 (deploy+invio) + fix copy mail + T3/T4

> Continua da S371. Founder: produzione zero-compromessi. Regole: idempotente (verifica alla fonte, REGOLA #30 — i COMMIT battono i doc). Niente `git add -A` cieco. Done-condition ESTERNA per ogni task. Cred in `~/.claude/.env.fluxion-live`, mai in chat. WIP=1.

## ✅ T1 — CLEANUP S369 — **CHIUSO** (verificato alla fonte, NON riaprire)
Charge €1 bruciato su decisione founder. Tutti i fatti terminali verificati:
- **Refund**: `re_3Tiz7aIW4bHDTsaH0290VyrO` su charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` → `status:succeeded` (Stripe live API). NESSUNA attivazione anello-5 fatta (refund libero, autorizzato founder).
- **Payment link**: `plink_1TeCftIW4bHDTsaHJfwJNndD` → `active:false` (Stripe live API).
- **Landing**: rimosso blocco `test:{}` (piano €1, url `…24007`) da `landing/checkout-consent.html` → commit `9bbed91` → deploy Pages. **Verificato prod con `-L`** (308 redirect .html→/checkout-consent): `?plan=test` → `24007` **assente**, `24003` (base) e `24004` (pro) **presenti**. `?plan=test` ora cade nel guard `if(!plan)` → redirect `/#prezzi`.

## 🟡 T2 — MAIL LICENZA BRANDIZZATA — bozza pronta, logo LIVE, **NON deployata, NON spedita**
Funzione `buildEmailHtml` in `fluxion-proxy/src/routes/stripe-webhook.ts`. Anteprima: `.claude/cache/mail-licenza-preview.html` (`open`).
- **Logo = quello VERO** (icona app `src-tauri/icons/icon.png` → `landing/assets/fluxion-icon.png`). **LIVE verificato**: `curl -sI https://fluxion-landing.pages.dev/assets/fluxion-icon.png` → 200 image/png. `logoUrl` nel template OK.
- Copy mail **veritiera verificata alla fonte** (REGOLA #30): HEAD ha **0 "in arrivo"**, 0 download Windows. La riga copy "in arrivo" fu rimossa dal commit **`86e6cd1`** (pickaxe: HEAD=0, `86e6cd1^`=1). `dmgUrl` assegnato a `:307` ma **NON** è negli args destrutturati da `buildEmailHtml` (`:74`) → non nel corpo. **1 passo unico = attivazione licenza**.

### ⚠️ FIX COPY MAIL — APERTO founder (customer-facing, serve OK)
La mail mostra **DUE campi separati** ("Payload firmato:" JSON + "Firma Ed25519 (base64):"). **L'app NON li vuole separati.** Verificato in `src/components/license/LicenseManager.tsx`:
- UN solo `Textarea` "Codice Licenza" (`:361`), placeholder "Incolla qui il codice licenza JSON…" (`:365`).
- `handleActivate`: `JSON.parse(raw)` poi `parsed.license_payload || parsed.payload` (`:427-428`) → vuole **UN blob JSON intero**.
- **RACCOMANDAZIONE**: sostituire i due blocchi crypto con UN blocco "Codice licenza" = il blob JSON intero (quello firmato dal Worker), rimuovere il gergo "Ed25519"/"base64". Il cliente incolla 1 cosa sola, identica al campo app. **Edit NON fatto (attesa OK founder su copy cliente).**

### CHIUSURA T2 (quando founder OK su render+copy)
1. (opz) applica fix copy un-singolo-JSON sopra.
2. `cd fluxion-proxy && npm run type-check` (0 err) → `npx wrangler deploy`.
3. **Invio reale** a `gianlucadistasi81@gmail.com` → verifica Gmail: logo visibile + copy + render + incolla-attiva funziona. = DONE esterna T2.

## T3 — COPY-PONTE post-pagamento (`checkout-success.ts:156`)
Stessa logica T2: veritiero, niente download Windows. Redeploy worker. DONE: `curl` prod = zero "in arrivo".

## T4 — WINDOWS DOWNLOAD (ARMATO) — parte SOLO se anelli 4-8 = PASS (founder #1)
Release `v1.0.1` `lukeeterna/fluxion-desktop` ha 0 asset (verificato S369) → se nessun installer → BLOCKED-ON build.

## 1 DOMANDA FOUNDER aperta
1. Anelli 4-8 (walkthrough nativo): PASS / non-fatti / bloccante? → sblocca T4.
2. ~~Licenza S369 attivata?~~ → RISOLTA: charge bruciato+refunded, nessuna attivazione.

## INVARIATI (hard-gate)
- Sara chiamata-reale TUTTI i verticali (verdetto giudice S365). R1 Sales Agent SOSPESO fino a onboarding VERDE. Magazzino+alert: GATE PASS S361.
