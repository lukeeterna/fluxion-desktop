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

## 🟢🟢 T2 — MAIL LICENZA — DEPLOYATA + SPEDITA + LINK VERIFICATO (porzione autonoma CHIUSA)
**Fatto S372 (sessione precedente)**: in `fluxion-proxy/src/routes/stripe-webhook.ts` `buildEmailHtml` → rimosso blob JSON + riga hero. Unica via licenza = pulsante "Recupera il codice licenza" → `recoveryUrl` (link HMAC, rispetta 410-rimborso). Commit `872ed2a`. `tsc` EXIT=0.

**Fatto S373 (questa sessione) — porzione autonoma CHIUSA, evidenze E2E reali**:
- **DEPLOY**: `npx wrangler deploy` OK → Version `4ea8119b-af6e-4752-aa1d-9c180d7df90d` su `fluxion-proxy` (= `fluxion-app.com`).
- **INVIO REALE**: mail spedita a `gianlucadistasi81@gmail.com` via Resend (`RESEND_TEST_KEY`, from `licenze@fluxion-app.com`) → **Resend id `c06ba11c-0d5e-45df-a364-8e0afacacef4`, status 200**. HTML = output ESATTO di `buildEmailHtml` (bundle esbuild della funzione reale, zero-divergenza — `buildEmailHtml` ora `export`; harness `fluxion-proxy/scripts/send-test-confirmation.ts`).
- **GUARD AUTOMATICO**: nel corpo HTML zero `Payload firmato`/`Firma Ed25519`/`base64`/blob (assert nel harness) → Q5 confermato a runtime, non solo a sorgente.
- **BUG CATTURATO+FIX**: prima verifica recovery-link → **403 Invalid token** = `LICENSE_RECOVERY_SECRET` del Worker ≠ file `~/.claude/.env.s295-recovery-secret`. Fix: `wrangler secret put LICENSE_RECOVERY_SECRET` = valore file (64 hex) → worker ora self-consistent e allineato al file. **NB**: il 403 era artefatto del MIO token calcolato localmente; per i clienti veri il Worker costruisce E valida il link col PROPRIO secret (sempre self-consistent) → nessun cliente reale impattato. Tutte le purchase esistenti sono test rimborsate (410), zero clienti reali → rotazione sicura.
- **RECOVERY ENDPOINT VERIFICATO (3 esiti reali)**: token valido → (a) `gianluca…` non-acquirente = **404 No license**; (b) `fluxion.gestionale@…` / `ilcombeeretrasher@…` = **410 REFUNDED** → *prova che il gate-rimborso funziona* (motivo di sicurezza di Q5). Il path **200+licenza** richiede acquisto NON-rimborsato.
- **PREVIEW rigenerata** (non più stale): `.claude/cache/mail-licenza-preview.html` = render reale corrente.

**RESTA T2 (2 cose, entrambe esterne)**:
1. **Eyeball Gmail (founder, REGOLA #1b)**: aprire la mail `c06ba11c` in `gianlucadistasi81@gmail.com` → confermare logo visibile + copy + pulsante recupero. (Cliccando il pulsante: per gianluca = 404 perché non ha acquisto reale — atteso.)
2. **BLOCKED-ON prima vendita reale**: il path "incolla-attiva" 200-con-licenza si chiude col 1° acquisto vero non-rimborsato (NON fabbrico licenze, REGOLA S364).

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

## ✅ T3 — COPY-PONTE post-pagamento — CHIUSO (verificato comportamentalmente in prod)
**Fatto S373**: `checkout-success.ts:156` → `"Versione Windows in arrivo…"` sostituito con `"Compatibile con macOS 12+ (Intel e Apple Silicon)."`. Grep src worker = **0** occorrenze "in arrivo". Deploy Version `284e96bf-0285-4c3e-9624-cc6d3d878061`.
**VERIFICA E2E PROD** (session LIVE reale `cs_live_a152jM61…` → template completo renderizzato): `in arrivo`=**0**, `Compatibile con macOS 12`=**1**, `Passo 1`=1, title `FLUXION Base — Licenza pronta`. DONE esterna T3.

## 🚩 FINDING SICUREZZA S373 — success page bypassa il gate-rimborso (Q5-consistency) — DECISIONE founder/giudice
**Scoperto durante verifica T3** (NON toccato, fuori scope T3 per REGOLA #29):
- `/success/:session_id` (`checkout-success.ts:180-195`) renderizza **inline** `Payload firmato` + `Firma Ed25519 (base64)` + License ID — costruiti dalla Stripe session, **senza check rimborso**.
- Prova: session S317 = email `fluxion.gestionale@gmail.com`. Recovery endpoint per quella email = **410 REFUNDED** (gate ok), MA la success page **mostra ancora la licenza+blob** della stessa purchase rimborsata → **bypassa la leva di revoca**, identica natura del Q5 ma su superficie post-pagamento (transitoria, non inbox).
- **Raccomandazione CTO**: estendere logica Q5 alla success page (rimuovere blob inline lines 180-195, lasciare solo il link recupero del Passo 3 che rispetta il 410). Differenza dal Q5-email: la success page è transitoria (1 vista), ma un cliente può copiare il blob prima del rimborso → stesso rischio. Chiedere verdetto giudice sullo scope (come fu per l'email).

## T4 — WINDOWS DOWNLOAD (ARMATO) — parte SOLO se anelli 4-8 = PASS (founder #1)
Release `v1.0.1` `lukeeterna/fluxion-desktop` ha 0 asset (verificato S369) → se nessun installer → BLOCKED-ON build.

## 1 DOMANDA FOUNDER aperta
1. Anelli 4-8 (walkthrough nativo): PASS / non-fatti / bloccante? → sblocca T4.
2. ~~Licenza S369 attivata?~~ → RISOLTA: charge bruciato+refunded, nessuna attivazione.

## INVARIATI (hard-gate)
- Sara chiamata-reale TUTTI i verticali (verdetto giudice S365). R1 Sales Agent SOSPESO fino a onboarding VERDE. Magazzino+alert: GATE PASS S361.
