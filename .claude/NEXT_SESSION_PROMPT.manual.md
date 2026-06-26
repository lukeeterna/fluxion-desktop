# NEXT SESSION PROMPT (MANUALE) — FLUXION / Sales Agent (carry da S383, 2026-06-26)

## 🔴 TASK#2 S384 — SEO-programmatico Astro: BUILD LOCALE BLOCCATA su Big Sur (2026-06-27)
Eseguito su MacBook Big Sur 11.7.10, Node v22.14.0, scratch `/tmp/seo-test`. Repo testato: `masterkram/minted-directory-astro` (Astro 5.5.2). Repo #2 (15500 pagine) non identificato con certezza → testato solo #1 (come da istruzione).
- **GATE #1 = NO**: `npm install` fallisce con `dyld: Symbol not found: _SecTrustCopyCertificateChain` — il binario prebuilt **esbuild** (dep core Astro/Vite) è built per **macOS 12.0**, simbolo assente su Big Sur 11 → SIGABRT. **NON è Node** (v22 gira), è il muro Big Sur (stessa classe vincolo #8 paddlepaddle). Vale anche per iMac 2012 (anch'esso Big Sur). **Nessuna delle 2 macchine builda Astro localmente.**
- 5 pagine verticale×città create come sorgente markdown (slug=filename, bottone WhatsApp placeholder `wa.me/39xxx`), ma **0 HTML** (build non parte). Lighthouse non misurabile.
- **VERDETTO**: build locale **NO**. Canale SEO-programmatico **NON necessariamente bloccato** → **CF Pages builda da remoto su CI Linux**, aggirando il muro a zero-cost. **NEXT STEP DECISIVO (non-capex)**: push repo Astro minimo → CF Pages → confermare build remota = HTML 200 live. Solo se fallisse anche quella → fork Apple Silicon (rischio #1). `minted-directory-astro` = base consigliata se la build remota regge. Report: `/tmp/seo-test/REPORT_SEO_astro.md` + `install2.log`.


## 🟢 TASK#1 S384 — CHIUSO VERDE (2026-06-26): IG `web_profile_info` VERIFICATO empiricamente
Eseguito su MacBook Big Sur, curl_cffi **0.7.4** (venv `/tmp/scraper-test/venv`), `impersonate=chrome120` + HTTP/2, cookie-stripping, throttling 3s+jitter. **15 richieste, 0×403, 0×429, 0 blocchi.**
- **Profili validi-reali: 7/7 = 200 con dati pieni** (aldocoppola, compagniadellabellezza, calzedonia, intimissimi, eataly, diadora, originalmarines).
- **link-in-bio (external_url): SÌ** 7/7 — nota: spesso aggregatore (linktr.ee/clz.do/linkin.bio) → 1 hop extra per anchor booking. Nessun Booksy/Treatwell/Fresha/Calendly diretto nel campione.
- **recency (ultimo post): SÌ** 7/7 timestamp reale, 5/7 di oggi.
- **Fragilità reale = `200 {"status":"ok"}` vuoto** (lerbolario, riproducibile 2/2, ~12% degli handle validi). NON è un 403/ban → mitigazione = retry + fallback HTML pubblico. Doc_id rotation NON osservata.
- **Verdetto**: base affidabile su Big Sur + IP residenziale. Combinato con FB SSujitX (5/5) → segnali 1-5 abbastanza stabili per costruire il Sales Agent **SÌ**. Report completo: `/tmp/scraper-test/REPORT_IG_web_profile_info.md` + `ig_results{1,2,3}.json`.

## 📌 VOCE ROADMAP (NON ATTIVA ORA) — "Infrastruttura anti-ban a volume"
**Attivare SOLO post-primo-CLOSED_WON**, quando i volumi di scraping superano ciò che un singolo IP residenziale regge col throttling semplice (3s+jitter, pausa 60s/50). NON per la fase attuale (zero clienti) — costruirla ora = gold-plating documentato.
- **Rotazione IP residenziale via dongle USB LTE/5G** + comandi AT seriali (forza disconnessione/riconnessione cella → nuovo IP CGNAT pulito in pochi secondi, zero costo banda/proxy). Backoff esponenziale + riavvio interfaccia LTE al 3° fallimento. Motivazione: IP datacenter bloccati istantaneamente da Meta; IP mobili CGNAT italiani = reputazione massima. ✅ **Compatibile con hardware attuale** (hardware esterno + seriale), attivabile a regime senza cambio macchina.
- **Orchestrazione pipeline scraping via n8n (Community Edition).** ⚠️ **VINCOLO HARD**: "n8n in Docker" è **INCOMPATIBILE** con iMac 2012 no-AVX2 (NO DOCKER, vincolo VOS non-negoziabile). Questa parte è **SUBORDINATA** a UNA delle due: (a) n8n NATIVO (npm, senza Docker) sull'hardware esistente, OPPURE (b) migrazione ad Apple Silicon (già rischio strutturale #1 a verbale). **NON registrare "n8n in Docker" come fattibile sull'iMac attuale.**

---

## TASK#1 S384 — MANDATO ORIGINALE (archiviato, ESEGUITO sopra)
## ~~TASK#1 S384 — MANDATO~~: VERIFICA EMPIRICA endpoint Instagram `web_profile_info` con curl_cffi su 5 profili reali

MANDATO: VERIFICA EMPIRICA — testa l'endpoint Instagram web_profile_info con curl_cffi su 5 profili reali.
NON costruire l'integrazione. NON installare dongle/n8n/Docker (esplicitamente fuori scope — vedi sotto).
FASE 0: git status pulito. Lavoro in scratch /tmp/scraper-test (riusa l'esistente). Idempotente. NIENTE subagent (main).
Done = JSON reali estratti, non "i Deep Research dicono". Picuki/Imginn/mirror = SCARTATI (morti), non testare.

CONTESTO: due Deep Research convergono su web_profile_info come via gratuita robusta per IG (link-in-bio + recency),
da interrogare con curl_cffi su HTTP/2 per superare il TLS fingerprinting JA3/JA4. È RACCOMANDATO ma NON ANCORA
ESEGUITO sulla nostra macchina. Questo task lo verifica empiricamente, come abbiamo fatto smascherando Picuki.

ESEGUI su 5 attività italiane reali con IG pubblico (puoi riusare gli handle già noti o trovarne via Google
"parrucchiere Milano instagram"):
  Endpoint: https://i.instagram.com/api/v1/users/web_profile_info/?username={user}
  Tecnica (da entrambi i report):
   - usa curl_cffi (pin 0.7.4, lo stesso che carica su Big Sur) con impersonate Chrome, HTTP/2.
   - header: x-ig-app-id: 936619743392459 + User-Agent mobile + Accept-Language it-IT.
   - cookie-stripping: NON inviare cookie vuoti/malformati (causano 401 CSRF).
   - throttling: 3s + jitter casuale tra le richieste; backoff esponenziale su 403/429. NESSUN proxy, NESSUN dongle.

PER OGNI PROFILO, riporta cosa ESCE DAVVERO dal JSON:
  | attività | http | external_url (link-in-bio) | category_name | is_business | follower | n.post | timestamp ultimo post |
  Valore reale / VUOTO / ERRORE per ciascun campo. + per ognuno: che data ha l'ultimo post (recency reale)?

CONTROLLI:
  - tasso di successo: quanti dei 5 tornano 200 con dati vs quanti 403/429/blocco?
  - curl_cffi 0.7.4 supporta impersonate+HTTP2 su Big Sur, o dà errori? Riporta la versione che ha funzionato.
  - se l'external_url esce: contiene link Booksy/Treatwell/Fresha/Calendly per qualcuno dei 5? (= anchor booking reale)
  - quanto spesso scatta il 403 (la fragilità che i report attribuiscono alla doc_id rotation)?

PARERE TECNICO CC: da chi ha eseguito — web_profile_info è una base affidabile su Big Sur con IP residenziale,
o si blocca troppo? Verdetto secco: link-in-bio ottenibile SÌ/NO, recency ottenibile SÌ/NO. E: combinato con FB
SSujitX (già 5/5), copriamo i segnali 1-5 in modo abbastanza stabile da costruirci il Sales Agent SÌ/NO?

DONE (esterna): la tabella coi JSON reali dei 5 + tasso successo + verdetto SÌ/NO sui due segnali chiave.
Oppure FATTO che blocca (403 sistematico → quale, e se serve qualcosa che NON sia dongle/proxy a pagamento).

NON TOCCARE: ARGOS/FLUXION, nessun commit, nessuna build, NIENTE dongle LTE / n8n / Docker / rotazione IP
(sproporzionato a zero clienti = fuori scope ora; throttling semplice basta per questi volumi). Solo test scratch.
APRI OUTPUT IN TEXTEDIT.

---

## (parcheggiato S383) Verticali Sara — fonte risolta, NON è priorità ora
3 assi distinti, verificati alla fonte: A) prodotto/setup `src/types/setup.ts` = 8 macro; B) Sara vende `voice-agent/data/sales_knowledge_base.json` = 8 (parrucchiere/meccanico/gommista/carrozziere/estetista/palestra/clinica/studio_professionale); C) Sara booking FSM `.claude/rules/voice-agent.md` = 4 (salone/palestra/medical/auto). Per test live Sara → usare Asse C (4). Ripreso solo dopo TASK#1.

---

# (carry precedente) NEXT SESSION PROMPT (MANUALE) — FLUXION (da S382, 2026-06-26)

> File MANUALE (non rigenerato dagli hook). All'apertura: incolla qui il VERDETTO DEL GIUDICE (prompt giudice consegnato a Luke in S382).
> Branch `master`. Worker prod `fluxion-proxy` Version a51ef6b4.

---

## STATO CHIUSO S382 — VERDE (2026-06-26)

1. **Mail conferma re-inviata** a `manueldx2014@gmail.com` → Resend **HTTP 200**, msg id `1ac98581-a9fe-40ab-bc87-9d50c6fcecc0`. Render via `buildEmailHtml` (vitest, import risolto) con guard PASS: logo apple=1, win=1, link dmg+exe, zero blob (Q5). NB: se i loghi non si vedono = Gmail blocca immagini esterne (icon PNG su pages.dev = 200).
2. **🟢 ATTIVAZIONE WINDOWS VERIFICATA ALLA FONTE**: Luke ha installato FLUXION da link e attivato. DB tirato Win→Mac (`.claude/cache/win_verify_20260626_185057.db`): `license_cache` = **base / active**, `is_ed25519=1`, `license_id=38ce1839…`, email `manueldx2014@gmail.com`, issued 2026-06-20, Sara trial 30gg (→2026-07-26). NON è `s317.lic` (quello = `3b6e97cb…`, schema vecchio): Luke ha usato un `.lic` legato alla SUA mail, passato `verify_strict` Ed25519 reale. `s317.lic` resta copiato su `Desktop\s317.lic` del Win (non usato).
3. **`/grazie` 404 = NON percorso pagante** (verificato): success_url Stripe → worker `checkout-success.ts` (dmg+exe entrambi 200) + email = sani. `/grazie` è pagina ORFANA (non linkata, 404 su dominio prod = worker). Fix link macOS `.pkg`→`.dmg` applicato+committato per igiene, non urgente.

**Verità #2a (Pila-1 revenue) ora ha DOPPIA prova**: s317.lic (S365) + licenza manueldx2014 (S382). Catena acquisto→email→recovery→`.lic`→verify_strict Rust→active = chiusa per 2 email diverse.

---

## STATO CHIUSO S381 — VERDE

**Task giudice**: mail conferma acquisto doveva contenere LICENZA **E** DOWNLOAD (prima solo recovery → cliente che chiude la success-page restava senza software).

- **FIX** (`fluxion-proxy/src/routes/stripe-webhook.ts`, commit 4fe9bda, +32/-5): STEP 1 "Scarica" con 2 bottoni — macOS (`${dmgUrl}`=`env.DMG_DOWNLOAD_URL_MACOS`=`v1.0.0/Fluxion_1.0.0_x64.dmg`, **200**) + Windows (`releases/latest/download/Fluxion_1.0.1_x64-setup.exe`, **200**). "Attiva" → STEP 2. Q5 INTATTO (blob mai nel corpo, solo args/D1).
- **PROVA runtime**: render `buildEmailHtml` (1 def `:73`, 1 call-site `:290` → zero divergenza) con blob passato negli args → blob nel corpo=0, win=1, mac=1, recovery preservata. Link → 200 post-deploy.
- **DEPLOY**: `wrangler deploy` → Version f08f29b9.
- **SEND REALE**: mail con bottoni → `manueldx2014@gmail.com` via Resend (`RESEND_TEST_KEY`, path S342) → **HTTP 200**, msg id `8a0dc5a1-3def-4794-82a7-37c57bc76168`. NESSUN refund (metodo A = render+send, zero addebito).
- Report: `.claude/REPORT_SESSIONE_2026-06-23_S381.md`. Carry git: commit `5001269`.

---

## NUOVE RICHIESTE FOUNDER (mid-S381) → TASK PROSSIMA SESSIONE

Verifiche fatte (REGOLA #1): repo `lukeeterna/fluxion-desktop` = **PUBBLICO**; worker = **nessuna** route download-gated con token.

### TASK 1 — "Mascherare il link download" (non replicabile)
Verdetto CTO (REGOLA #9): valore anti-pirateria **BASSO** — il paywall vero è la **licenza Ed25519** (`.exe` senza licenza = inutile). Condividere il link NON è buco revenue.
Mascheramento vero richiede 2 cose insieme: (1) binario NON fetchabile dall'URL pubblico → release privata o **Cloudflare R2** (free 10GB); (2) worker route `GET /api/v1/download?token=HMAC...` per-acquisto/monouso/scadente. Mascherare solo nell'email = teatro. Lavoro strutturale → research+plan (REGOLA #18). **Priorità BASSA.**

### TASK 2 — Loghi mac/win sui bottoni → ✅ FATTO (post-S381, 2026-06-23)
- PNG generati con Pillow: Apple = glifo reale  rasterizzato da `/System/Library/Fonts/SFNS.ttf` (Apple Symbols dava tofu — verificato visivamente); Windows = 4 quadrati bianchi. Bianco su trasparente, verificati su bg #111827.
- Hostati su `fluxion-landing.pages.dev/assets/icon-apple.png` + `icon-windows.png` (Pages deploy, entrambi **200**).
- `stripe-webhook.ts`: aggiunte const `appleIconUrl`/`winIconUrl`, sostituito `&#9660;` con `<img width=14/15 vertical-align:middle>` nei 2 bottoni. Render verificato: img apple=1, img win=1, vecchia freccia=0, Q5 blob=0, recovery intatto (HMAC x2). Worker redeploy **Version a51ef6b4**.
- Re-send reale a `manueldx2014@gmail.com` → HTTP 200, msg id `a355e5f4-58e0-44f6-b6c9-506efadc1d6d`.

**RESTA per il giudice** = solo TASK 1 (mascheramento link, valore basso).

---

## DOMANDE PER IL GIUDICE
1. "Mascherare il link ha valore basso perché la licenza Ed25519 è il vero paywall" — corretto, o sottovaluto un vettore (installer trojanizzato ridistribuito, telemetria, brand)?
2. Loghi: PNG trademark reali (rischio legale) vs icone generiche safe? Standard 2026 per email transazionali B2B?
3. Priorità: TASK 2 prima, TASK 1 prima, o nessuna (freelancing fuori roadmap, REGOLA #29)?

---

## RESIDUO PRE-ESISTENTE (non percorso pagante)
`landing/grazie/index.html:467` → `Fluxion_1.0.0_macOS.pkg` = **404**. Fix = repoint a `v1.0.0/Fluxion_1.0.0_x64.dmg` (già 200).

## COME RIPRENDERE
1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`.
2. Incolla il VERDETTO DEL GIUDICE + una riga di contesto ("verdetto giudice S381 mail download").
3. ASPETTA che io lo ingerisca PRIMA di toccare codice (gate post-compact VOS). Se OK → eseguo il task scelto; se FAIL → riapro investigazione.
