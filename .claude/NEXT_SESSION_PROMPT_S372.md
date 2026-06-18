# FLUXION — NEXT SESSION PROMPT — S372 · CHIUSURA T2 (deploy+invio) + fix copy mail + T3/T4

> Continua da S371. Founder: produzione zero-compromessi. Regole: idempotente (verifica alla fonte, REGOLA #30 — i COMMIT battono i doc). Niente `git add -A` cieco. Done-condition ESTERNA per ogni task. Cred in `~/.claude/.env.fluxion-live`, mai in chat. WIP=1.

## ✅ T1 — CLEANUP S369 — **CHIUSO** (verificato alla fonte, NON riaprire)
Charge €1 bruciato su decisione founder. Tutti i fatti terminali verificati:
- **Refund**: `re_3Tiz7aIW4bHDTsaH0290VyrO` su charge `ch_3Tiz7aIW4bHDTsaH0hyVHVvJ` → `status:succeeded` (Stripe live API). NESSUNA attivazione anello-5 fatta (refund libero, autorizzato founder).
- **Payment link**: `plink_1TeCftIW4bHDTsaHJfwJNndD` → `active:false` (Stripe live API).
- **Landing**: rimosso blocco `test:{}` (piano €1, url `…24007`) da `landing/checkout-consent.html` → commit `9bbed91` → deploy Pages. **Verificato prod con `-L`** (308 redirect .html→/checkout-consent): `?plan=test` → `24007` **assente**, `24003` (base) e `24004` (pro) **presenti**. `?plan=test` ora cade nel guard `if(!plan)` → redirect `/#prezzi`.

## 🧑‍⚖️ VERDETTO GIUDICE S372 (license revoca + anti-crack) — INGERITO, da implementare
Prompt: `.claude/cache/PROMPT-GIUDICE-license-revoca-anticrack.md`. Verdetti secchi:
- **Q1** crack-proof su app desktop = ILLUSIONE (pubkey nel binario, branch verifica NOP-pabile). Obiettivo onesto = alzare costo sopra threat reale (cliente-rimborso + condivisione casuale PMI), NON il cracker esperto.
- **Q2** revoca onesta = solo dove c'è chokepoint online → **solo Sara** (già fingerprint-bound `auth.ts:52-55`). Gestionale offline-forever = deterrente, revoca zero.
- **Q3** check online solo-all'attivazione = TEATRO (pattern compra-usa-rimborsa: rimborso arriva DOPO). NO.
- **Q4** node-locking gestionale = SÌ ma **gated su via di re-bind testata** (primitiva da verificare a sorgente `src-tauri/src/commands/license_ed25519.rs:712-714`, NON darla per esistente). Senza escape-valve → lock-out clienti paganti (cambio PC/reinstall) = il danno che vuoi evitare.
- **Q5** togliere blob inline dall'email = SÌ. ✅ **FATTO QUESTA SESSIONE** (vedi sotto).
- **Q6 (mossa migliore)** **node-locking SERVER-SIDE al retrieve**: app chiama recovery endpoint inviando il PROPRIO fingerprint → Worker controlla rimborso → embedda fingerprint nel payload → ri-firma → restituisce. Binding applicato al chokepoint online che controlli, non client-side. Riusa recovery endpoint + chiave firma + logica fingerprint Sara, zero infra nuova. Vincolo: fingerprint mandato dall'APP, non dal browser che apre la mail.

### Architettura minima (ordine):
1. **ORA**: togli blob email (Q5) → ✅ fatto, type-check 0 err, da deploy+invio.
2. **ORA-DOPO**: node-lock server-side al retrieve (Q6), gated su re-bind testata. Senza re-bind → NON spedire.
3. **DETERRENTE ACCETTATO**: gestionale offline crackabile dall'esperto (§4+Q1) — a verbale, non spenderci.
4. **DEBITO FUTURO cond. revenue**: code signing reale (UX install, non anti-crack); watermark forense.

## 🟢 T2 — MAIL LICENZA — copy fix + BLOB RIMOSSO (Q5) — type-check OK, **NON deployata/spedita**
**Fatto S372**: in `fluxion-proxy/src/routes/stripe-webhook.ts` `buildEmailHtml` → rimosso il blocco "Attivazione manuale" col blob JSON + rimossa la riga hero "in fondo trovi il codice". L'unica via licenza = pulsante "Recupera il codice licenza" → `recoveryUrl` (link HMAC, rispetta 410-rimborso). `licensePayload/licenseSignature` non più nel corpo (restano in args per firma D1). `tsc --noEmit` EXIT=0.
**⚠️ Anteprima `.claude/cache/mail-licenza-preview.html` è STALE** (mostra ancora il blob unificato pre-rimozione) → rigenerare/ri-editare prima di mostrarla.
**CHIUSURA T2 (next session)**: `cd fluxion-proxy && npx wrangler deploy` (NB: non c'è script `npm run type-check`, usa `npx tsc --noEmit`) → invio reale a `gianlucadistasi81@gmail.com` → verifica Gmail (logo + copy + link recupero + incolla-attiva) = DONE esterna T2.

## 🗑️ (storico) T2 pre-verdetto — MAIL LICENZA BRANDIZZATA — bozza pronta, logo LIVE, **NON deployata, NON spedita**
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
