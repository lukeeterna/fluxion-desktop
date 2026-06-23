C # NEXT SESSION PROMPT — FLUXION (carry da S381, 2026-06-23)

> Documento per VALUTAZIONE GIUDICE (Claude AI esterno) + ripartenza prossima sessione.
> Branch `master`. Repo `/Volumes/MontereyT7/FLUXION`. Worker prod `fluxion-proxy` deployato Version f08f29b9.

---

## STATO CHIUSO QUESTA SESSIONE (S381) — VERDE

**Task giudice**: mail di conferma acquisto doveva contenere LICENZA **E** DOWNLOAD (prima solo recovery+attivazione → cliente che chiude la success-page restava senza software).

- **FIX** (`fluxion-proxy/src/routes/stripe-webhook.ts`, commit 4fe9bda, +32/-5): aggiunto STEP 1 "Scarica" con 2 bottoni — macOS (`${dmgUrl}` = `env.DMG_DOWNLOAD_URL_MACOS` = `v1.0.0/Fluxion_1.0.0_x64.dmg`, **200**) + Windows (`releases/latest/download/Fluxion_1.0.1_x64-setup.exe`, **200**). "Attiva" rinumerato STEP 2. Q5 INTATTO (blob licenza mai nel corpo, solo in args/D1).
- **PROVA runtime**: render della funzione esportata `buildEmailHtml` (1 def `:73`, 1 call-site `:290` → zero divergenza render/send) con blob passato di proposito negli args → blob nel corpo = **0**, link win=1, link mac=1, recovery preservata. Entrambi i link → **200** post-deploy.
- **DEPLOY**: `wrangler deploy` → Version f08f29b9 (GO delegato da Luke).
- **SEND REALE**: mail con i bottoni inviata a `manueldx2014@gmail.com` via Resend (`RESEND_TEST_KEY`, stesso path validato S342) → **HTTP 200**, msg id `8a0dc5a1-3def-4794-82a7-37c57bc76168`. NESSUN refund (metodo A = render+send diretto, zero addebito).
- Report completo: `.claude/REPORT_SESSIONE_2026-06-23_S381.md`.

---

## NUOVE RICHIESTE FOUNDER (mid-sessione S381) → TASK PROSSIMA SESSIONE

Luke ha scaricato l'`.exe` dalla mail (funziona) e ha chiesto 2 cose. **Verifiche fatte** (REGOLA #1):
- Repo `lukeeterna/fluxion-desktop` = **PUBBLICO** (`gh repo view` → `visibility:PUBLIC`).
- Worker = **nessuna** route download-gated con token (route esistenti: stripe-webhook, checkout-success, gdpr-download, lead-magnet).

### TASK 1 — "Mascherare il link download" (non replicabile)
**Verdetto onesto CTO (REGOLA #9)**: valore anti-pirateria **BASSO**. Il vero paywall è la **licenza Ed25519** — chi scarica l'`.exe` gratis ha un installer **inutile senza licenza pagata** (app non si attiva, Sara/funzioni gated). Condividere il link **non è un buco revenue**.

Mascheramento *vero* (solo se Luke lo vuole per controllo brand / evitare circolazione installer, NON per revenue) richiede 2 cose **insieme**:
1. binario NON fetchabile dall'URL pubblico → release **privata** OPPURE spostato su **Cloudflare R2** (free 10GB, REGOLA #5 zero-cost);
2. worker route `GET /api/v1/download?token=HMAC...` con token **per-acquisto, monouso, scadente** → il cliente vede solo `fluxion-app.com/...`, mai l'URL GitHub.

Mascherare *solo* nell'email lasciando la release pubblica = **teatro** (tasto destro → copia indirizzo lo rivela). Lavoro strutturale security → research+plan+validate-then-implement (REGOLA #18) PRIMA di toccare.

**Priorità raccomandata: BASSA** (licenza già gating). Aprire solo se Luke conferma che vuole il controllo brand.

### TASK 2 — Loghi mac/win sui bottoni
Attualmente i bottoni hanno solo `&#9660;` (freccia giù). Luke vuole i loghi piattaforma.
**Vincolo tecnico verificato**: i client email (Gmail/Apple Mail/Outlook) **strippano SVG** → niente loghi vettoriali inline. Unica via robusta = **PNG hostati** via `<img src="https://fluxion-app.com/...">`.
- Serve hostare 2 PNG (zero-cost: asset Cloudflare Pages della landing, o worker static).
- **Nota legale**: logo Apple/Windows sono trademark. "Scarica per Mac" con mela è uso comune ma regolato (Apple Marketing Guidelines). Alternativa safe = icona generica (mela/finestra stilizzata) o emoji. **Decisione scope per Luke** prima di implementare.
- Task piccolo (~30min) ma **dipende dagli asset PNG hostati**.

**Raccomandazione (REGOLA #3)**: fare TASK 2 (polish veloce, alto valore percepito) e valutare TASK 1 solo dopo conferma scope. Entrambe toccano email+download UX.

---

## DOMANDE PER IL GIUDICE
1. Il verdetto "mascherare il link ha valore basso perché la licenza Ed25519 è il vero paywall" è corretto, o sottovaluto un vettore (es. installer trojanizzato ridistribuito, telemetria, brand)?
2. Per TASK 2 loghi: meglio PNG trademark reali (Apple/Windows) con rischio legale, o icone generiche safe? Qual è lo standard 2026 per email transazionali B2B?
3. Priorità: TASK 2 prima (polish) o TASK 1 (security) prima? O nessuna delle due (è freelancing fuori roadmap, REGOLA #29)?

---

## RESIDUO PRE-ESISTENTE (non percorso pagante)
`landing/grazie/index.html:467` → `Fluxion_1.0.0_macOS.pkg` = **404**. È la landing pubblica, non la mail. Fix = repoint a `v1.0.0/Fluxion_1.0.0_x64.dmg` (già 200).

## COME RIPRENDERE
1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`.
2. ASPETTA l'output validation del giudice (incollato da Luke) PRIMA di toccare codice (gate post-compact VOS).
3. Se giudice OK → esegui il task scelto. Se FAIL → riapri investigazione.
