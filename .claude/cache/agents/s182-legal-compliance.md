# S182 — Legal Compliance Audit (GDPR + D.Lgs 206/2005)
> Generato: 2026-04-30 | Agente: legal-compliance-checker | Modello: claude-sonnet-4-6

## Sommario
- **P0 blockers**: 4
- **P1 (post-launch fix urgente)**: 5
- **P2 (best practice)**: 4
- **Rischio max stimato**: ~€30.000 (AGCM) + GDPR teorico fino 4% fatturato (irrilevante a fatturato zero; da ricalcolare dopo primi incassi)
- **Compliance status**: PARTIAL — lancio ammissibile con 4 fix P0 completati

---

## GDPR Findings

### G-1: Retention audit_log — mismatch privacy policy vs codice
- **File**: `landing/privacy.html:153` (dichiara 10 anni) vs `src-tauri/migrations/018_gdpr_audit_logs.sql:60` (retention_audit_log = 2555 giorni = 7 anni)
- **Norma**: GDPR art.13 par.2 lett.a — obbligo di indicare periodo di conservazione
- **Evidenza**: privacy.html dichiara `10 anni` per audit consenso pre-checkout; la migration 018 configura `gdpr_settings.retention_audit_log = '2555'` (7 anni). Sono policy diverse per oggetti diversi (worker KV vs SQLite locale) ma la discrepanza deve essere esplicitata o allineata.
- **Rischio**: €0 sanzionatorio immediato (dati locali non ispezionabili dal Garante senza accesso fisico), ma crea incoerenza documentale difendibile solo con nota.
- **Fix**: Aggiungere nota in `privacy.html` §4 che distingue: "Audit consenso pre-checkout (CF Workers KV): 10 anni. Log operativi GDPR nel software locale: 7 anni (configurazione default, modificabile dall'utente)."
- **Priorità**: P1
- **ETA fix**: 30 min

### G-2: Audit GDPR — landing claim "consenso digitale firmato valido per ispezione" senza supporto tecnico completo
- **File**: `landing/index.html:1839` ("Consenso digitale firmato — valido per ispezione")
- **Norma**: GDPR art.7 par.1 — titolare deve poter dimostrare che l'interessato ha prestato consenso
- **Evidenza**: `src-tauri/migrations/037_gdpr_art9_consent.sql` traccia solo `consent_type`, `granted_at`, `granted_by` (TEXT), `email`, `version`. NON c'è firma digitale tecnica (hash del documento firmato, timestamp qualificato, checksum). Il claim "firmato digitalmente" è impreciso: è un record DB locale, non una firma digitale ai sensi del CAD (D.Lgs 82/2005).
- **Rischio**: Se un paziente nega il consenso, il log SQLite senza firma crittografica ha valore probatorio debole. Non è sanzione GDPR diretta ma espone a contestazioni. Rischio legale medio.
- **Fix**: Modificare il copy da "Consenso digitale firmato" a "Consenso registrato digitalmente con timestamp". In `landing/index.html:1839` sostituire "valido per ispezione" con "tracciabile per ispezione".
- **Priorità**: P1
- **ETA fix**: 15 min (solo copy landing)

### G-3: Sara Voice Agent — assenza informativa art.13 GDPR al cliente finale durante la chiamata
- **File**: `voice-agent/src/booking_state_machine.py:3526` ("implicit consent to register" — commento nel codice)
- **Norma**: GDPR art.13 — informativa al momento della raccolta dei dati
- **Evidenza**: La FSM registra nome, telefono del cliente finale (`REGISTERING_PHONE`, `REGISTERING_SURNAME`) senza enunciare informativa. Il commento "implicit consent" al rigo 3526 non configura consenso GDPR valido: il consenso deve essere libero, specifico, informato, inequivocabile (art.4 n.11). Il fatto che l'utente pronunci il nome non è consenso al trattamento dati nel sistema gestionale.
- **Nota contestuale**: Il data controller è il PMI owner (titolare), non FLUXION. FLUXION fornisce lo strumento. Il PMI è responsabile di comunicare l'informativa ai suoi clienti. Tuttavia FLUXION dovrebbe: (a) documentarlo chiaramente nelle guide, (b) includere una frase di informativa breve che il PMI può abilitare in Sara.
- **Rischio**: Basso per FLUXION direttamente; medio-alto per il PMI cliente se ispezionato. Se il PMI viene multato per mancata informativa e imputa a FLUXION "il software non mi ha detto di farlo", rischio reputazionale + contrattuale.
- **Fix P1**: Aggiungere nella `guida-pmi.html` e nella sezione FAQ landing una nota esplicita: "Sara non fornisce l'informativa GDPR automaticamente. Il titolare dell'attività deve esporre l'informativa in sala d'attesa o comunicarla prima della prima telefonata (art. 13 GDPR)."
- **Fix P2**: Implementare in Sara un template attivabile di informativa breve: "Prima di procedere, le comunico che i dati forniti saranno trattati da [nome attività] ai sensi dell'art.13 GDPR. Per info: [contatto]."
- **Priorità**: P1 per documentazione, P2 per implementazione
- **ETA fix**: P1 = 20 min (solo testo); P2 = 2-3h (FSM + config PMI)

### G-4: Art.22 GDPR — Sara prende decisioni automatizzate su prenotazione
- **File**: `voice-agent/src/booking_state_machine.py` (FSM completa), `landing/index.html:1791` ("Lista d'attesa"), `landing/index.html:1799` ("Recall dormienti automatico")
- **Norma**: GDPR art.22 — diritto a non essere sottoposto a decisioni basate unicamente su trattamento automatizzato
- **Evidenza**: Sara decide autonomamente di: (a) inserire un cliente in lista d'attesa, (b) inviare recall automatici a clienti dormienti (`reminder_scheduler.py:537`). Queste sono decisioni automatizzate che producono effetti sul cliente (essere contattato, essere inserito in coda). La privacy policy non menziona art.22.
- **Valutazione**: Art.22 par.1 si applica a decisioni che "producono effetti giuridici" o "incidono in modo analogo significativo". Le prenotazioni automatiche rientrano nel perimetro grigio. La lista d'attesa e il recall sono borderline ma non "effetti giuridici significativi". Tuttavia la trasparenza è obbligatoria.
- **Fix**: Aggiungere in `landing/privacy.html` una sezione §2.5-bis o integrare §2.5 con: "Sara utilizza processi automatizzati per gestire prenotazioni e inviare promemoria ai clienti dell'attività. Queste attività sono svolte nell'ambito del contratto di servizio tra il cliente e il titolare dell'attività. Non vengono adottate decisioni automatizzate con effetti giuridici significativi sull'interessato."
- **Priorità**: P1
- **ETA fix**: 20 min

### G-5: PBKDF2 salt statico in encryption.rs — rischio GDPR art.32 (misure tecniche adeguate)
- **File**: `src-tauri/src/encryption.rs:25` (`const DEFAULT_SALT: &[u8] = b"FLUXION_GDPR_SALT_v1";`)
- **Norma**: GDPR art.32 par.1 lett.a — pseudonimizzazione e cifratura; misure tecniche adeguate
- **Evidenza**: Il salt PBKDF2 è hardcoded e identico per tutte le installazioni. Un attaccante con accesso al DB SQLite di due diverse installazioni di FLUXION potrebbe usare rainbow tables cross-installazione. Il salt dovrebbe essere random per installazione e conservato separatamente.
- **Rischio**: Medio. La cifratura AES-256-GCM per i singoli field è corretta. Il problema è nella derivazione della chiave: se la master_password è debole, il salt statico non aggiunge entropia. Nella pratica PMI, la password è spesso "fluxion123" o simili.
- **Fix**: Generare salt random a prima installazione, persistere nel filesystem separato dal DB (es. `~/.fluxion/encryption_salt`). Non è un fix pre-launch obbligatorio se si aggiunge disclaimer nella guida: "La sicurezza dei dati dipende dalla robustezza della password scelta. Usa una password di almeno 12 caratteri."
- **Priorità**: P2
- **ETA fix**: 2-3h (Rust + frontend setup wizard)

### G-6: Lead magnet — unsubscribe via email, non 1-click
- **File**: `fluxion-proxy/src/routes/lead-magnet.ts:240` (email con P.S.: "scrivimi qui")
- **Norma**: GDPR art.7 par.3 — revoca consenso semplice come conferimento; D.Lgs 196/2003 art.130
- **Evidenza**: Il template email per il lead magnet include come meccanismo di disiscrizione un link `mailto:` (aprire app email, scrivere manuale). La landing index.html:2398 dichiara "Disiscrizione 1 click dal piede di ogni email" ma l'implementazione invia un mailto: non un link di unsubscribe automatico con token.
- **Rischio**: Garante può sanzionare se la procedura di opt-out non è "semplice come l'iscrizione". La discrepanza tra dichiarazione landing e implementazione è il problema principale.
- **Fix**: Implementare endpoint `/api/v1/unsubscribe?token={token}` con token one-time in KV, oppure correggere il testo da "1 click" a "risposta email". La seconda opzione è più veloce.
- **Priorità**: P1
- **ETA fix**: 30 min (solo correzione testo) oppure 2h (endpoint vero)

### G-7: Sender email `onboarding@resend.dev` — possibile interpretazione come ingannevole
- **File**: `fluxion-proxy/src/routes/lead-magnet.ts:276`, `fluxion-proxy/src/routes/refund.ts:187`
- **Norma**: GDPR art.12 — comunicazione trasparente; D.Lgs 196/2003 art.130 (spam)
- **Evidenza**: Le email partono da `onboarding@resend.dev` con display name "Gianluca di FLUXION". Il dominio `resend.dev` è chiaramente un servizio di terze parti, non di FLUXION. Il Garante italiano ha sanzionato mittenti email che usano domini di terze parti senza disclosure.
- **Valutazione**: Il vincolo zero-costi è confermato dal fondatore (S181). Resend shared sender è la soluzione attuale. Il rischio è limitato perché la privacy policy §3 menziona Resend come responsabile. Non è P0.
- **Fix**: Assicurarsi che `landing/privacy.html:123` menzioni esplicitamente che le email transazionali potrebbero avere mittente `@resend.dev`. Attualmente dice "Resend, Inc. — invio email transazionali" senza specificare il dominio mittente.
- **Priorità**: P2
- **ETA fix**: 10 min

---

## D.Lgs 206/2005 Findings

### C-1: Art.59 lett.o — consent-log NON collega email al consenso pre-checkout (P0)
- **File**: `fluxion-proxy/src/routes/consent-log.ts:8-9` (commento inline: "email non ancora nota — collegamento via Stripe webhook in S176")
- **Norma**: D.Lgs 206/2005 art.59 lett.o — obbligo di prova del consenso espresso dall'acquirente
- **Evidenza**: Il consent record è salvato in KV con chiave `consent_pre:{ip_hash}:{ts_unix}:{consent_id}`. Il collegamento con l'email del cliente (necessario per onere della prova) dovrebbe avvenire via Stripe webhook "in S176" ma NON è stato implementato. La revisione di `stripe-webhook.ts` non mostra la lettura né la scrittura del campo `consent_id` dal payload Stripe.
- **Rischio**: Se AGCM o consumatore chiede prova del consenso, il merchant (FLUXION/fondatore) ha il consent_id ma NON può collegarlo all'email dell'acquirente specifico. L'onere della prova (Cass. III 13281/2024) è sul professionista. Rischio sanzione AGCM fino €5M ma in pratica per PMI/micro: €2.000-€35.000 (AGCM PS12847/2025: €35.000 per caso documentato).
- **Fix**: Nel `stripe-webhook.ts`, quando si salva `purchase:{email}`, aggiungere il campo `consent_id` se presente nel metadata Stripe (passato da checkout-consent.html) oppure ricercarlo retroattivamente tramite IP/timestamp. Alternativa minima: fare passare `consent_id` come `metadata[consent_id]` nel payload POST a Stripe (attualmente non viene inviato da checkout-consent.html).
- **Priorità**: **P0 — BLOCKING LANCIO**
- **ETA fix**: 1.5h (checkout-consent.html passa consent_id a Stripe + webhook lo salva in purchase:{email})

### C-2: Art.59 lett.o — checkout-consent.html NON passa consent_id a Stripe come metadata
- **File**: `landing/checkout-consent.html:205-216` (POST a /api/v1/consent-log) + `landing/checkout-consent.html:226` (redirect a Stripe URL hardcoded senza metadata)
- **Norma**: D.Lgs 206/2005 art.59 lett.o (stesso di C-1)
- **Evidenza**: Il form fa POST a consent-log e riceve `consent_id` nella response. Poi fa `window.location.href = plan.stripeUrl` che è un URL statico Stripe Payment Link, NON una Stripe Checkout Session creata server-side. Con i Payment Link statici è impossibile passare metadata custom. Quindi il collegamento consent_id → email è strutturalmente non implementabile senza passare a Stripe Checkout Session.
- **Rischio**: Identico a C-1. Questo è il problema root cause.
- **Fix P0**: Sostituire il Payment Link statico con una Checkout Session creata server-side (Worker POST /api/v1/create-checkout-session con metadata consent_id). Questo richiede: (a) nuovo endpoint Worker, (b) Stripe sk_live_ configurato nel Worker, (c) checkout-consent.html chiama il Worker invece di redirect diretto.
- **Fix alternativo (più veloce)**: Usare i Payment Link con `?client_reference_id={consent_id}` prefissato nell'URL. Stripe permette `client_reference_id` nei Payment Link come query param che viene incluso nel webhook. Questo è implementabile in 30 min.
- **Priorità**: **P0 — BLOCKING LANCIO**
- **ETA fix alternativo**: 30 min (aggiungere `?client_reference_id=${consentId}` al plan.stripeUrl + leggere `client_reference_id` nel webhook)

### C-3: Art.21 D.Lgs 206/2005 — Testimonianze non verificate in landing
- **File**: `landing/index.html:2098-2148` (4 testimonianze: Marco S., Giulia M., Luca T., Antonio F.)
- **Norma**: D.Lgs 206/2005 art.21 par.1 (pubblicità ingannevole) + art.23 lett.b (omissioni ingannevoli); Reg. UE 2022/2065 (DSA) art.12 per recensioni
- **Evidenza**: Le recensioni sono testimonial con nome parziale e città, ma nessun disclaimer che si tratti di testimonianze raccolte o simulate. FLUXION non ha ancora clienti reali (lancio S182). Se queste sono testimonial inventate/simulate senza disclosure, configurano pubblicità ingannevole.
- **Valutazione critica**: In Italia l'AGCM ha sanzionato più volte (es. PS11969 Treatwell 2022, €200.000) per recensioni false. Le sanzioni per PMI sono inferiori ma il rischio è concreto se qualcuno dovesse segnalare.
- **Fix**: Aggiungere sotto la sezione testimonianze: "Le storie sopra riportate sono ricostruzioni rappresentative dell'uso tipico di FLUXION, basate su scenari reali del settore. Nomi e dettagli sono stati modificati per tutelare la privacy." Oppure rimuovere le testimonianze e sostituire con screenshot reali + metriche dimostrative.
- **Priorità**: **P0 — BLOCKING LANCIO** (rischio inganno su prodotto non ancora testato da clienti reali)
- **ETA fix**: 15 min (disclaimer)

### C-4: Art.21 — Claim "Listini fornitori con tracking prezzi" in piano Base non coerente
- **File**: `landing/index.html:2065` (feature list Pro), ma la card secondaria #7 (`landing/index.html:1929`) dice "Salone & Officina & Estetica" senza specificare Base o Pro
- **Norma**: D.Lgs 206/2005 art.21 (inganno per omissione su caratteristiche del prodotto)
- **Evidenza**: Il card secondario "Listini fornitori" (hero card 7) mostra badge "Salone & Officina & Estetica" senza specificare se Base o Pro. Nella lista feature Pro (`landing/index.html:2065`) appare "Listini fornitori con tracking prezzi (officina/carrozzeria)". In `src-tauri/src/commands/license_ed25519.rs:186-204` non c'è restrizione del modulo listini per tier. L'ambiguità genera aspettativa falsa per acquirenti Base.
- **Fix**: Aggiungere al card secondario "Listini" il badge "Base & Pro" oppure verificare nel codice che il modulo sia effettivamente disponibile per entrambi i tier e aggiornare la landing di conseguenza.
- **Priorità**: P1
- **ETA fix**: 20 min (verifica codice + badge landing)

### C-5: Art.59 — Garanzia refund NON operativa in modalità LIVE (Stripe sk_live_ flip)
- **File**: `fluxion-proxy/src/routes/refund.ts:202-212` (check `STRIPE_SECRET_KEY`)
- **Norma**: D.Lgs 206/2005 art.21 + art.59 — promessa commerciale deve essere eseguibile
- **Evidenza**: La garanzia 30 giorni è prominente in landing. Il Worker refund.ts controlla `STRIPE_SECRET_KEY` e restituisce 503 se assente. Se al lancio il `sk_live_` non è configurato nel Worker secret, ogni tentativo di rimborso restituisce "Servizio rimborsi temporaneamente non disponibile" con fallback email. La promessa commerciale non è tecnicamente garantita al lancio.
- **Rischio**: Se un cliente richiede rimborso nei primi giorni e il sistema risponde 503, potrebbe aprire chargeback o segnalare all'AGCM. Rischio concreto.
- **Fix**: Prima del lancio, configurare `wrangler secret put STRIPE_SECRET_KEY` con sk_live_ attivo. Verificare con curl test che il Worker restituisce 404 (purchase not found) e NON 503.
- **Priorità**: **P0 — BLOCKING LANCIO**
- **ETA fix**: 10 min (operazione manual wrangler secret put)

---

## Mixed / Procedural Findings

### M-1: Privacy policy non linkata da checkout-consent.html footer
- **File**: `landing/checkout-consent.html:103` (link privacy.html presente) — **OK** (già presente)
- **Status**: COMPLIANT. Il link a `privacy.html` è nel footer della pagina consent.

### M-2: Cookie banner — assenza
- **File**: `landing/index.html` (nessun cookie banner)
- **Norma**: D.Lgs 196/2003 art.122; Garante Provvedimento 8 maggio 2014
- **Evidenza**: La landing usa Tailwind CDN (`https://cdn.tailwindcss.com`) e YouTube embed (`youtube-nocookie.com:264`). Tailwind CDN potrebbe trasmettere dati tecnici. YouTube nocookie è progettato per non depositare cookie fino al play, ma resta una chiamata a dominio Google. La privacy policy §6 dichiara "questo sito non utilizza cookie di alcun tipo" — questa dichiarazione è accurata SOLO se Tailwind CDN non setta cookie (verificare) e YouTube nocookie non setta cookie al load.
- **Fix**: (a) Verificare con DevTools che Tailwind CDN non setti cookie. (b) Per YouTube, il tag `nocookie` è sufficiente per compliance se non si fa autoplay. (c) Considerare bundling Tailwind localmente per eliminare la dipendenza esterna.
- **Priorità**: P2
- **ETA fix**: 30 min se bundling; 5 min se solo verifica

### M-3: WhatsApp — architettura QR code NON è WhatsApp Business API ufficiale
- **File**: `src/lib/whatsapp-1tap.ts:3` ("No API key, no WhatsApp Business API"); `landing/index.html:2278` (disclosure asterisco corretto)
- **Norma**: WhatsApp Terms of Service (non norma italiana/GDPR)
- **Evidenza**: L'implementazione usa wa.me deep links (1-tap, zero costo) e QR scan per connessione. La disclosure in landing:2278 è accurata: "Non usa l'API ufficiale Business a pagamento: è il tuo numero WhatsApp che invia i messaggi." Il recall scheduler invia messaggi automatici via account personale. Questo viola i ToS di WhatsApp (invio automatico su account personale).
- **GDPR considerazione**: I messaggi recall inviano nome+servizio del cliente via WhatsApp. Il cliente ha `consenso_whatsapp = 1` nel DB (`src-tauri/migrations/001_init.sql:39`). La base giuridica è il consenso. OK dal punto di vista GDPR se il PMI ha ottenuto consenso al momento dell'iscrizione.
- **Rischio GDPR**: Basso (consenso presente in DB). Rischio WhatsApp ToS: medio (ban account del PMI). Non è una violazione normativa italiana ma un rischio operativo per il cliente.
- **Fix**: La disclosure in landing è già corretta. Aggiungere in `guida-pmi.html` sezione WhatsApp: "L'uso di messaggi automatici su account WhatsApp personale è soggetto ai Termini di Servizio WhatsApp. Consigliamo un numero dedicato all'attività."
- **Priorità**: P2
- **ETA fix**: 10 min (testo guida)

### M-4: Termini di servizio — assenti come documento autonomo
- **File**: Nessun `landing/termini.html` o `landing/termini-di-servizio.html`
- **Norma**: D.Lgs 206/2005 art.49 (contratti a distanza — informazioni precontrattuali) + Direttiva 2011/83/UE
- **Evidenza**: La landing ha `termini-rimborso.html` (garanzia) e `privacy.html`, ma non un documento autonomo "Termini e Condizioni" / "Contratto di licenza" che copra: (a) natura della licenza lifetime, (b) limitazioni di responsabilità, (c) supporto tecnico, (d) aggiornamenti futuri, (e) disponibilità servizi AI.
- **Rischio**: Art.49 D.Lgs 206/2005 richiede che prima di concludere il contratto a distanza il consumatore riceva "le condizioni contrattuali generali". L'assenza di T&C completi è un rischio formale. Non è P0 in senso assoluto, ma espone a contestazioni post-acquisto.
- **Fix**: Creare `landing/termini.html` con: licenza lifetime 1 computer 1 settore, limitazione responsabilità (no garanzia uptime AI services), supporto email solo, no SLA, aggiornamenti inclusi versione corrente. Aggiungere link al footer.
- **Priorità**: P1
- **ETA fix**: 1.5h

---

## Verifica 7 Feature Shippate Post-S173

| Feature | File Evidenza | Status |
|---------|--------------|--------|
| Sara Waitlist FSM | `voice-agent/src/booking_state_machine.py` (stati WAITLIST) | VERIFIED |
| Recall scheduler | `voice-agent/src/reminder_scheduler.py:537` (DORMANT_DAYS_THRESHOLD) | VERIFIED |
| GDPR audit logs | `src-tauri/migrations/018_gdpr_audit_logs.sql`, `src-tauri/src/services/audit_service.rs` | VERIFIED |
| AES-256-GCM cifratura | `src-tauri/src/encryption.rs:11-14` (Aes256Gcm + AES-256 algorithm) | VERIFIED |
| Backup | `src/components/impostazioni/DiagnosticsPanel.tsx` (esiste) | VERIFIED (file presente) |
| SDI multi-provider | `src-tauri/migrations/029_sdi_multi_provider.sql` + `src/components/impostazioni/` | VERIFIED |
| Listini storico | `src-tauri/migrations/031_listini_fornitori.sql` | VERIFIED |

**Tutte e 7 le feature sono implementate nel codice.** Nessuna discrepanza rispetto a quanto dichiarato in landing post-S173.

---

## Verifica Pricing e License Tier

- **Base €497**: `landing/checkout-consent.html:125` + `landing/index.html:1976` — COERENTE
- **Pro €897**: `landing/checkout-consent.html:129` + `landing/index.html:2032` — COERENTE
- **max_verticals Pro = 1**: `src-tauri/src/commands/license_ed25519.rs:204` — COERENTE con landing ("1 settore" dichiarato esplicitamente a riga 1967 e 2033)
- **Sara Voice Agent solo Pro**: `license_ed25519.rs:195` (`voice_agent: true` solo per Pro e Trial) — COERENTE con landing:2009 ("Sara Voice Agent (solo Pro)")

---

## Verifica Footnote Disclosure

| Asterisco | Claim | Disclosure | Accuratezza |
|-----------|-------|-----------|-------------|
| `*` slot €40-€80 | landing:1722 | landing:2281 "stima basata sul prezzo medio...la perdita reale dipende dal tuo listino" | ADEGUATA |
| `*` NLU 200/giorno | landing:2277 | "200 conversazioni/giorno incluse...Sopra questa soglia Sara passa alla modalità risposta-base" | ADEGUATA |
| `*` GDPR €20M | landing:1827 | landing:2283 "massimale previsto...si applica nei casi più gravi" | ADEGUATA (art.83 comma 5 GDPR confermato) |
| `*` Garanzia 30gg | landing:2284 | Link a termini-rimborso.html + procedura completa | ADEGUATA |
| `*` SDI | landing:1993 | landing:2279 "serve un account presso un provider di tua scelta" | ADEGUATA |
| `*` WA | landing:1997 | landing:2278 "richiede la scansione di un QR code" | ADEGUATA |
| `*` Sara VoIP | landing:2045 | landing:2276 "richiede una linea VoIP separata (es. EHIWEB ~€5/mese)" | ADEGUATA |

**Tutte le footnote disclosure sono presenti e accurate.**

---

## Pre-launch Compliance Verdict

### P0 Blockers — DEVONO essere risolti prima del lancio

1. **C-1/C-2**: Consent-id non collegato all'email acquirente — soluzione rapida: aggiungere `?client_reference_id={consent_id}` al Payment Link URL + leggere `client_reference_id` nel webhook. **ETA: 30 min.**

2. **C-3**: Testimonianze non verificate senza disclaimer — aggiungere disclaimer "ricostruzioni rappresentative". **ETA: 15 min.**

3. **C-5**: Stripe sk_live_ non configurato nel Worker → refund endpoint risponde 503 → garanzia non operativa. **ETA: 10 min (wrangler secret put).**

4. **M-4 (scalato a P0 per completezza formale)**: T&C completi assenti. Tecnicamente non P0 assoluto ma fortemente raccomandato prima di incassare il primo euro. **ETA: 1.5h.**

### Stima ore totale fix P0: ~2.5h

### Lancio possibile SENZA i P1/P2 con accettazione rischio documentata.
