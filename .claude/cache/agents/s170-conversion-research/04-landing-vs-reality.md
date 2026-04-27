# S170 — Audit Coerenza: Landing FLUXION vs Realtà del Prodotto

**Data:** 2026-04-27 · **Sessione:** S170 · **Autore:** subagente conversion-research
**Riferimento landing:** https://fluxion-landing.pages.dev/ → `landing/index.html` (2170 righe, S170 deploy live)

---

## 1. EXECUTIVE SUMMARY

### Voto coerenza globale: **C+** (sufficiente con riserva)

La landing è **emotivamente potente e ben scritta**, ma contiene **3 mismatch CRITICI** che possono generare reso, recensioni negative, segnalazioni AGCM e perdita di fiducia. Il prodotto sotto è solido (32 commands Tauri, 37 migrations, FSM 23 stati confermato), ma la landing **promette feature che esistono solo parzialmente o in tier diverso**. La separazione Base/Pro nel codice **non corrisponde** a quella mostrata sulla landing. La pagina ha anche un **terzo tier "Clinic" €1.497 che NON esiste nel codice né nello Stripe webhook** — letteralmente un'opzione di acquisto fantasma.

### I 3 mismatch più CRITICI

| # | Claim landing | Realtà codice | Impatto |
|---|---------------|---------------|---------|
| **1** | **Tier "Clinic" €1.497** con CTA Stripe | `stripe-webhook.ts:36` mappa SOLO `49700→base, 89700→pro`. Nessun `clinic`. CTA Clinic punta allo **stesso payment link Pro €897**. `LicenseTier` enum: `Trial/Base/Pro/Enterprise` — manca `Clinic`. | Cliente paga aspettandosi €1.497 di funzioni → riceve licenza Pro €897. **Frode involontaria + chargeback garantito.** |
| **2** | **Pro = "Tutti e 6 i settori"** (riga 1824) | `license_ed25519.rs:201` → `Pro: max_verticals: 3`. Solo Enterprise (€1.497, ma il tier non è venduto online) ha 6+ verticali. | Cliente sceglie Pro per coprire 2 attività diverse → ne può attivare massimo 3. Reso o downgrade emotivo. |
| **3** | **Programma fedeltà 4 livelli "Bronze/Silver/Gold/Platinum" basato su PUNTI** (€1=1 punto, +200 compleanno, +300 referral) | DB `clienti.loyalty_visits + loyalty_threshold` (riga 005:14-17): è una **tessera timbri per VISITE**, NON un punteggio per euro. Nessuna tabella `punti`, nessun trigger compleanno/referral automatico. Nessun tier Bronze/Silver/Gold/Platinum nel codice. | Promessa di sistema enterprise (à la Sephora) che non esiste. Onboarding cliente = scoperta di un counter visite stupido. **Reso settore beauty/wellness garantito.** |

---

## 2. TABELLA CLAIM-BY-CLAIM

| # | Claim landing (verbatim) | Realtà prodotto | Gap | Severità | Fix proposto |
|---|--------------------------|-----------------|-----|----------|--------------|
| C01 | "FLUXION — Gestionale con AI per PMI italiane. Sara prenota per te 24/7" (title, riga 6) | ✅ FSM 23 stati confermati `booking_state_machine.py` (4342 righe). Endpoint `/api/voice/process` attivo `main.py:312` | Nessuno se VoIP attivo | OK | — |
| C02 | "Sara gestisce appuntamenti, invia WhatsApp automatici e riconosce i clienti — 24 ore su 24" (meta description) | ✅ riconoscimento cliente `disambiguation_handler.py`. WA via `whatsapp.rs:577` (`send_booking_confirm_wa`). 24/7 richiede VoIP+SIP attivo (`voip_pjsua2.py`, credenziali EHIWEB necessarie). | Manca asterisco "richiede linea VoIP/SIP separata, non inclusa nel prezzo" | **ALTO** | Aggiungere nota "Sara 24/7 richiede una linea VoIP separata (es. EHIWEB ~€5/mese) — non inclusa nel prezzo" |
| C03 | "Paghi una volta sola" / "Licenza una tantum — nessun canone mensile" (riga 256, 2103) | ✅ `LicenseTier::Base/Pro` Lifetime confermato `license_ed25519.rs:10`, Ed25519 offline | Nessuno | OK | — |
| C04 | "I dati restano sul tuo computer" (riga 231, 360, 425, 1001-1006, 2007) | ⚠️ VERO per CRM/Calendario/Fatture (SQLite locale, `lib.rs:125 fluxion.db`), MA: <br>• Sara usa **Groq cloud** per LLM (`orchestrator.py:55`)<br>• Sara usa **Edge-TTS Microsoft cloud** per TTS quality tier (`architecture-distribution.md:5`)<br>• NLU passa per **CF Worker proxy** (`fluxion-proxy/src/routes/nlu-proxy.ts`)<br>• Stripe Checkout (US) per pagamenti<br>• Resend (US) per email post-acquisto | Claim "non escono mai dalla tua rete" è **falso quando Sara è attiva**. Il payload audio→testo→risposta passa per Groq (Stati Uniti) e Microsoft (Edge-TTS). | **CRITICO** | Modificare in: "Anagrafica clienti, calendario, fatture e schede restano in locale. Sara usa servizi AI esterni (Groq, Microsoft Edge-TTS) per capire il parlato e generare la voce — solo il testo della conversazione viene processato, non si conservano dati." Aggiungere DPA / privacy policy aggiornata. |
| C05 | "Funziona anche senza internet per calendario e schede clienti" (riga 426) + FAQ "Funziona senza internet? Sì." (riga 1962) | ✅ VERO: SQLite locale, Tauri app desktop. Sara richiede internet (Groq+Edge-TTS+CF Worker). FAQ è onesta: "Sara ha bisogno di internet" | Nessuno (FAQ ben fatto) | OK | — |
| C06 | "Sara risponde in meno di 1 secondo" (badge riga 517) + mockup "Sara AI · 680ms" (riga 555) | ❌ FALSO: `voice-agent-details.md:28` dice "attuale ~1330ms vs target <800ms". `PRD-FLUXION-COMPLETE.md:445` conferma "TOTALE ~1330ms" + "FIX v1.1". | La latenza reale è **~1.3s**, mai sotto 1s. Il mockup 680ms è promozionale, non realistico. | **ALTO** | Modificare in "Risponde in 1-2 secondi" oppure rimuovere il claim numerico. Mockup 680ms → 1.2s. |
| C07 | "Testato su 58 scenari reali" (badge riga 520) | ⚠️ PRD `PRD-FLUXION-COMPLETE.md:13` dice "Voice Agent Test Suite: 58/58 test passati" — sono test **Python unit**, non scenari live audio. `voice-agent-details.md:30` dice "Test Live Audio — ancora da fare". | I 58 sono test sintetici, non sessioni vocali reali. | MEDIO | Cambiare in "58 scenari di test automatici" oppure rimuovere |
| C08 | "Capisce accenti regionali (testato con accenti veneto, romano e siciliano)" FAQ riga 1998 | NON VERIFICATO. Nessun file di test con accenti regionali nel repo (`grep -r "veneto\|siciliano" voice-agent/tests` = 0). STT è Whisper.cpp Italian + Groq fallback. | Claim non supportato da test documentati. | MEDIO | Rimuovere "(testato con accenti...)" o aggiungere "su Whisper italiano standard" |
| C09 | **"€497 — €1.497 una volta"** (tabella confronto, riga 981) + 3 prezzi mostrati: **Base €497, Pro €897, Clinic €1.497** (righe 1759, 1803, 1844) | 🔴 `stripe-webhook.ts:35-37`: `49700→base`, `89700→pro`. **NESSUN €1.497**. CTA "Acquista Clinic" (riga 1872) usa `buy.stripe.com/00w28sdWL8BU0V9fYu24001` = stesso link di Pro. | Cliente paga €897 credendo di acquistare Clinic €1.497 → riceve Pro. Oppure si aspetta funzioni Clinic (multi-sede, supporto email, "Sara con nome custom") che non esistono nel codice. | **CRITICO** | (a) Rimuovere completamente il tier Clinic dalla landing finché non esiste (Stripe link + LicenseTier::Clinic + features mappate); OPPURE (b) creare il payment link Stripe €1.497 + tier `clinic` nel webhook + branch nel codice license. **Non lasciare il pulsante fantasma.** |
| C10 | "BASE €497 ... Calendario, clienti, fatture, 1 settore. Sara AI (solo Pro), WhatsApp automatico (solo Pro)" (riga 1755-1789) | ✅ Allineato con `license_ed25519.rs:186-194` Base: `voice_agent: false, whatsapp_ai: false, max_verticals: 1`. | Nessuno (anzi, ben chiaro) | OK | — |
| C11 | "PRO €897 ... Tutti e 6 i settori" (riga 1824) | ❌ `license_ed25519.rs:201` → `Pro: max_verticals: 3`. Per 6 verticali serve `Enterprise: max_verticals: 99` (€1.497 nel codice). | Cliente Pro che vuole 6 settori → bloccato a 3. | **CRITICO** | Allineare codice → 6 (`max_verticals: 6` per Pro), oppure correggere landing → "fino a 3 settori specializzati" |
| C12 | "Conferme WhatsApp automatiche" (riga 1820 + win-item riga 351) | ✅ `whatsapp.rs:577 send_booking_confirm_wa` + `reminder_scheduler.py` (24h+1h reminders). Auto-start `whatsapp.rs:108`. | Richiede Node.js installato sulla macchina cliente (`whatsapp.rs:120`). Se manca → WA disabilitato silenziosamente. | MEDIO | Aggiungere requisito "Node.js installato" oppure bundlare Node con installer |
| C13 | "Programma punti per i clienti fedeli" + 4 livelli VIP **Bronze/Silver/Gold/Platinum** con punteggio per euro speso, +200 compleanno, +300 referral (sezione fedeltà righe 1346-1485) | ❌ `005_loyalty_pacchetti_vip.sql:14-17` → DB ha solo `loyalty_visits` (counter visite), `loyalty_threshold`, `is_vip` (booleano). NESSUN tier Bronze/Silver/Gold/Platinum. NESSUN punteggio per euro. NESSUN bonus compleanno automatico (esiste `get_clienti_compleanno_settimana` solo come query, non assegna punti). NESSUN trigger referral automatico (campo `referral_cliente_id` esiste ma nessun bonus). | La promessa è di un sistema **Sephora-grade**. Realtà: **tessera timbri "10 visite = premio"**. | **CRITICO** | (a) Implementare davvero (4-tier punti per euro, +bonus compleanno via cron, referral auto) — 2-3 settimane lavoro; OPPURE (b) riscrivere sezione: "Tessera timbri digitale: 10 visite = 1 premio. Marca i clienti VIP. Storico fedeltà. Bonus compleanno via WhatsApp manuale." |
| C14 | "Sara con il nome che vuoi tu (es. 'Lucia')" — Clinic feature (riga 1861) | NON VERIFICATO: il nome "Sara" è hardcoded in greeting templates `voice-agent/main.py` e in `system_prompt`. Esiste `nome_attivita` configurabile (PRD riga 156) ma il nome **dell'assistente** stesso non risulta parametrizzato in modo evidente. | Feature unica del tier Clinic (che non esiste nel webhook) → doppia bugia. | **ALTO** | Verificare se il rename è davvero plug-and-play (PRD non lo conferma). Se no: rimuovere claim. |
| C15 | "Configurazione guidata da noi" — Clinic (riga 1869) | NON VERIFICATO. CLAUDE.md `feedback_zero_support.md` dice "Supporto post-vendita ZERO manuale". Nessun ticket system, nessun pagamento per onboarding manuale documentato. | Promessa di servizio umano in contraddizione con strategia "zero supporto manuale". | MEDIO | Allineare: o si vende davvero un setup assistito (con un costo reale), o si rimuove |
| C16 | "Supporto diretto via email (risposta entro 24h)" — Clinic (riga 1865) | NON VERIFICATO. Nessun SLA scritto in nessun file. Email `fluxion.gestionale@gmail.com` (footer riga 2116) — gestione manuale fondatore. | OK come policy commerciale ma serve onestà su capacità. | BASSO | Aggiungere "lun-ven, no SLA contrattuale" |
| C17 | "Gestione più sedi dallo stesso programma" — Clinic (riga 1857) | ❌ NON IMPLEMENTATO. `lib.rs:125` → DB unico `fluxion.db` per app data dir. Nessun concetto di "sede" nelle migrations 001-037. Ogni installazione = 1 attività. | Multi-sede non esiste a livello schema. | **CRITICO** se venduto | Rimuovere claim oppure costruire multi-tenant (settimane di lavoro) |
| C18 | "Fatturazione elettronica XML (SDI)" Base (riga 1776) | ✅ `007_fatturazione_elettronica.sql` schema completo + `fatture.rs:1145` genera XML FatturaPA 1.2.2 + invio multi-provider (`029_sdi_multi_provider.sql`: fattura24/aruba/openapi). `LicenseFeatures` Base: `fatturazione_pa: true`. | OK con sfumatura: l'invio SDI **richiede API key di provider terzi a pagamento** (Aruba, Fattura24, OpenAPI) che il cliente deve sottoscrivere separatamente. Il file XML può essere generato e scaricato gratis. | **ALTO** | Aggiungere "Generazione XML inclusa. Invio diretto SDI richiede account presso provider terzo (Aruba/Fattura24, da ~€4/mese)" |
| C19 | "Pacchetti prepagati" — 6 settori dimostrati (sezione righe 1042-1342) | ✅ `005_loyalty_pacchetti_vip.sql:40-114` schema `pacchetti` + `clienti_pacchetti` esiste. `loyalty.rs:613-624` commands `create_pacchetto, proponi_pacchetto, conferma_acquisto_pacchetto, usa_servizio_pacchetto`. | OK ma: **i pacchetti mostrati sono esempi, non preconfigurati**. Cliente deve crearli da zero. | BASSO | Aggiungere "Pacchetti di esempio precaricati al primo avvio" oppure seedare migration con questi |
| C20 | "Sara prenota dal pacchetto. Il cliente chiede 'voglio il pacchetto Beauty Day' e Sara lo prenota scalando automaticamente" (riga 1321) | NON VERIFICATO. FSM `booking_state_machine.py` ha 23 stati core booking. NON risulta uno stato `WAITING_PACKAGE` o handler `consume_pacchetto` nel flow. La logica `usa_servizio_pacchetto` esiste ma è command Tauri (manuale dall'UI), non integrata nella conversazione vocale Sara. | Sara NON sa dei pacchetti del cliente. | **ALTO** | Implementare integrazione pacchetti↔Sara (FSM + RAG context) o rimuovere claim |
| C21 | "Sara conosce i tuoi VIP. Riconosce il numero dal primo squillo" (riga 1461) | ⚠️ PARZIALE: con VoIP attivo e Caller ID, `voip_pjsua2.py` ha info chiamante. `disambiguation_handler.py` matcha cliente per nome dichiarato. Ma riconoscimento "dal primo squillo" by phone number → richiede lookup DB su Caller ID, non documentato esplicitamente. | Funziona se VoIP è attivo. Con Sara via app/altro canale, no Caller ID = no riconoscimento immediato. | MEDIO | "Riconosce il numero dal primo squillo (con linea VoIP collegata)" |
| C22 | "Risparmio rispetto a Mindbody su 3 anni: €24.703" (riga 1035) | NON VERIFICABILE: numero esempio. Mindbody ha tier €0-700/mese (range), Treatwell commissione 25% varia per booking. | Calcolo cherry-picked sul tier Mindbody Premium. Onesto se reso esplicito ("scenario Mindbody Premium"). | BASSO | Aggiungere "scenario stimato — Mindbody piano enterprise" |
| C23 | "Garanzia 30 giorni" (riga 1880, 2103) | ❌ NON VERIFICATO nel codice. `stripe-webhook.ts` non implementa logica refund. Nessun cron scaduti. Nessuna policy scritta in `landing/privacy.html` (file da verificare). Nessun handler `/api/v1/refund`. | "Garanzia" è solo policy commerciale gestita manualmente dal fondatore via Stripe dashboard. Cliente che chiede rimborso al 29° giorno → solo via email manuale. | **ALTO** | (a) Implementare cron / pulsante "richiedi rimborso entro 30gg" che usa Stripe Refund API; OPPURE (b) chiarire "rimborso a richiesta via email entro 30 giorni dall'acquisto" + procedura |
| C24 | "Sei in regola con la legge sulla privacy (GDPR)" (riga 361, 2007) | ⚠️ PARZIALE: dati locali OK. Ma: <br>• Trasferimento dati a Groq (USA) per Sara → richiede DPA + base giuridica (legittimo interesse o consenso)<br>• Edge-TTS Microsoft (USA) → idem<br>• Stripe (US/Irlanda) per pagamenti → DPA Stripe presente di default ma cliente deve menzionarlo nel suo registro trattamenti<br>• Resend (US) per email<br>• `037_gdpr_art9_consent.sql` + `018_gdpr_audit_logs.sql` esistono → struttura GDPR c'è | "Sei in regola SENZA FARE NULLA DI SPECIALE" è **ottimistico**. Cliente sanitario (Art. 9 dati salute) deve raccogliere consenso esplicito, mantenere registro trattamenti, fornire informativa. | **ALTO** | Modificare: "Fluxion include strumenti per gestire la conformità GDPR (consenso, audit, anonimizzazione). Per essere in regola devi: (1) compilare il registro trattamenti, (2) consegnare informativa ai clienti. Forniamo template." Mai dire "automaticamente in regola". |
| C25 | "Aggiornamenti inclusi" (riga 438, 1751, 1972) | NON VERIFICATO: nessun cron auto-update documentato. `phone-home.ts` esiste ma scopo è trial countdown, non update push. Nessun mention di GitHub Releases auto-pull. | Ambiguo: "aggiornamenti inclusi" = il cliente può scaricarli gratis dal sito, ma deve farlo manualmente? | MEDIO | "Aggiornamenti gratuiti — scaricabili dal nostro sito quando rilasciati" |
| C26 | "macOS 11 Big Sur o successivo" (riga 1980) | ⚠️ `architecture-distribution.md:30` dice "macOS 12+". CLAUDE.md dice "macOS 12+". Discrepanza. | Cliente macOS 11 acquista, scopre incompatibilità. | MEDIO | Allineare landing → macOS 12+, oppure testare su macOS 11 e confermare |
| C27 | "Una cliente mi ha detto 'la tua segretaria è così gentile'" (testimonial Giulia M., riga 1913) | NON VERIFICATO: nessun customer database, nessun caso studio in `customers/` o nel repo. **Probabilmente testimonial fittizia di lancio.** | Possibile pratica commerciale scorretta (D.Lgs. 206/2005 art. 23). | **ALTO** | (a) Sostituire con testimonial reali raccolte post-lancio; OPPURE (b) etichettare "Esempio illustrativo basato su feedback raccolti durante beta" |
| C28 | "1 settore (salone, officina, ecc.)" Base (riga 1780) | ✅ Coerente con `Base: max_verticals: 1` (`license_ed25519.rs:194`) e `MICRO_CATEGORIE` (43 sotto-verticali su 6 macro) | OK | OK | — |
| C29 | "Conferma WhatsApp entro 30 secondi dalla prenotazione" (riga 497) | ✅ Plausibile: `send_booking_confirm_wa` chiamato a `COMPLETED` state in `booking_state_machine.py`, poi WA service queue | OK | OK | — |
| C30 | "Capisce accenti, gestisce nomi simili (es. 'Gino' o 'Gigio?')" (riga 414) | ✅ `disambiguation_handler.py` + `PHONETIC_VARIANTS` dict + Levenshtein ≥70% (`voice-agent-details.md:14`) | OK | OK | — |

---

## 3. MISMATCH CRITICI (sezione dedicata)

### 3.1 🔴 Tier "Clinic" €1.497 fantasma (C09, C14, C15, C17)
**Severità:** CRITICA — può causare denuncia AGCM e chargeback Stripe.

**Evidenza:**
- Landing riga 1844: `<div class="text-4xl font-extrabold text-white mb-1">&euro;1.497</div>` con CTA "Acquista Clinic"
- CTA punta a `https://buy.stripe.com/00w28sdWL8BU0V9fYu24001` (riga 1872) = identico link di Pro €897
- `fluxion-proxy/src/routes/stripe-webhook.ts:35-37`: solo `49700→base, 89700→pro`. Pagamento di €1.497 non esiste come opzione Stripe → fisicamente impossibile
- `LicenseTier` enum (`license_ed25519.rs:87-89`): `Trial, Base, Pro, Enterprise`. Il prezzo Enterprise nel codice è €1.497 (`license_ed25519.rs:116`) ma **non viene mai venduto** sul sito (Stripe non lo mappa)
- Feature Clinic promesse non implementate: multi-sede (no schema), Sara-rename (non parametrizzato), supporto email SLA (no ticketing)

**Fix obbligatorio:** RIMUOVERE il tier Clinic dalla landing entro 24 ore, oppure costruirlo davvero (3 settimane).

### 3.2 🔴 Pro = "Tutti e 6 i settori" ma codice limita a 3 (C11)
**Severità:** CRITICA — consumer ottiene meno di quanto pagato.

**Evidenza:**
- Landing riga 1824: `<li>... Tutti e 6 i settori</li>` (Pro €897)
- `license_ed25519.rs:201`: `Pro: max_verticals: 3`
- Cliente con palestra + centro estetico + officina → bloccato. Deve comprare Enterprise (che però non esiste su Stripe).

**Fix:** allineare il codice a `max_verticals: 6` per Pro, oppure correggere landing → "fino a 3 settori".

### 3.3 🔴 Programma fedeltà 4 livelli a punti = pure marketing (C13)
**Severità:** CRITICA — feature flagship inesistente.

**Evidenza:**
- Landing righe 1346-1485: sezione completa con Bronze/Silver/Gold/Platinum, sconti %, "1 punto per euro", "+200 compleanno", "+300 referral"
- DB schema `005_loyalty_pacchetti_vip.sql:14-17`: `loyalty_visits INTEGER, loyalty_threshold INTEGER DEFAULT 10, is_vip INTEGER DEFAULT 0`. **NESSUN punteggio, NESSUN tier.**
- `loyalty.rs:108 increment_loyalty_visits`: `SET loyalty_visits = loyalty_visits + 1` — incrementa di 1 visita, non di N punti
- Nessuna funzione `add_loyalty_points`, nessun trigger SQL su compleanno, nessun bonus referral automatico

**Fix:** entrambe le opzioni richiedono lavoro:
- (A) Implementare il sistema punti (2-3 settimane: schema + commands + UI + trigger compleanno via reminder_scheduler)
- (B) Riscrivere sezione: "Tessera timbri digitale + marca clienti VIP + storico visite. Pacchetti prepagati per fidelizzare." Onesto, meno sexy.

---

## 4. UNDERPROMISE — feature reali NON sulla landing

| Feature | Esiste nel codice | Perché mostrarla |
|---------|-------------------|------------------|
| **Lista d'attesa intelligente (Waitlist)** | `005_loyalty_pacchetti_vip.sql:120-150` + FSM stati `PROPOSING_WAITLIST → WAITLIST_SAVED` (`booking_state_machine.py`) | "Slot occupato? Sara mette il cliente in lista e lo richiama appena si libera." Killer feature unico |
| **Recall clienti dormienti automatico** | `reminder_scheduler.py:627 check_and_recall_dormant` — dopo 60gg senza booking, WA automatico (max 1/mese, max 10/giorno) | "Sara recupera i clienti che non vedi da 60 giorni — automaticamente, mai spam" |
| **Schede verticali dettagliate** | Odontogramma FDI 32 denti (`scheda_odontoiatrica`), scale dolore VAS/Oswestry/NDI (`scheda_fisioterapia`), fototipo Fitzpatrick (`scheda_estetica`), schede pet/fitness/medica/veicoli/carrozzeria/parrucchiere — 19 migrations dedicate | Landing dice "schede clienti" generico. Nascondi un odontogramma interattivo professionale, mostralo! |
| **Audit trail GDPR completo** | `018_gdpr_audit_logs.sql` + `037_gdpr_art9_consent.sql` + `audit_service.rs` | Per cliente sanitario è killer feature. Landing tace |
| **Backup automatico giornaliero** | `lib.rs:466-478 run_auto_backup_if_needed` (F13) | "Backup automatici giornalieri locali" — sicurezza vendibile |
| **Encryption at rest AES-256-GCM** | `encryption.rs gdpr_encrypt/gdpr_decrypt` per dati sensibili | "Dati cifrati anche a computer spento" |
| **Multi-provider SDI** | `029_sdi_multi_provider.sql`: Aruba/Fattura24/OpenAPI | "Compatibile con tutti i provider fatturazione elettronica italiani" |
| **5 cron scheduler attivi** (reminders 15min, waitlist 5min, birthday 9:00, recall 10:00, learning Sun 6:00) | da MEMORY.md + `reminder_scheduler.py` | "Tutto si auto-programma: promemoria, recall, compleanni" |
| **Listini fornitori con tracking variazioni prezzo** | `031_listini_fornitori.sql` + `listini.rs` | "Importa listino fornitore da Excel, traccia ogni variazione prezzo nel tempo" |

---

## 5. SFUMATURE MANCANTI (asterischi necessari)

Da aggiungere come note "Cosa serve per usare Sara" o nelle FAQ:

1. **"Sara richiede un numero VoIP/SIP separato"** — non incluso, ~€5/mese per linea EHIWEB. Senza VoIP, Sara funziona solo come bot WhatsApp/test interno
2. **"Limite 200 chiamate NLU/giorno"** — `architecture-distribution.md:15`. Sopra → Sara temporaneamente non risponde. Per attività con 200+ telefonate/giorno serve upgrade (non documentato come acquistabile)
3. **"Richiede macOS 12+ / Windows 10+ 64bit"** — landing dice macOS 11 (incoerenza)
4. **"Per Sara servono 16GB RAM consigliati"** — già presente, OK
5. **"L'invio diretto a SDI richiede account presso provider (Aruba ~€4/mese, Fattura24, OpenAPI)"** — la generazione XML è gratis, l'invio no
6. **"Node.js deve essere installato per WhatsApp"** — silenzio del codice, ma `whatsapp.rs:120` lo richiede
7. **"WhatsApp usa whatsapp-web.js — non l'API ufficiale Meta"** — implica rischio ban account WA se utilizzato in modo aggressivo (Meta TOS)
8. **"Dati conversazione Sara passano per Groq (USA) e Microsoft Edge-TTS (USA)"** — incompatibile col claim "i dati restano sul tuo computer" senza chiarimento
9. **"Garanzia 30 giorni = rimborso a richiesta via email, non automatico"**
10. **"Aggiornamenti = scaricabili manualmente dal sito"** (no auto-update push documentato)

---

## 6. PRICING CHIARO?

### Cosa CAMBIA davvero tra Base (€497) e Pro (€897) nel codice

| Feature | Base | Pro | Coerente landing? |
|---------|------|-----|-------------------|
| Sara Voice Agent | ❌ | ✅ | ✅ SÌ |
| WhatsApp AI (auto-reply) | ❌ | ✅ | ⚠️ ambiguo: landing differenzia "WhatsApp di conferma" (Base?) vs "AI" (Pro). Codice blocca tutto WA AI per Base |
| RAG Chat | ❌ | ✅ | Non menzionato in landing |
| Fatturazione PA | ✅ | ✅ | ✅ |
| Loyalty Advanced | ❌ | ✅ | ⚠️ landing presenta loyalty come unico (tier-less) — implica Pro? |
| API Access | ❌ | ❌ | OK (solo Enterprise, non venduto) |
| Max verticali | 1 | **3** | 🔴 LANDING DICE 6 |

**Verdict pricing:** confuso e **disallineato con codice**. Il cliente Pro paga €897 aspettandosi 6 settori e ne ottiene 3. La differenza Base→Pro va resa esplicita e ONESTA: Sara + WhatsApp AI automatico + Loyalty avanzato + 3 settori. Il "Tutti e 6 i settori" va corretto o il codice va aggiornato.

### Tier Clinic €1.497 — non esiste
Vedi sezione 3.1. Va rimosso o costruito.

---

## 7. GDPR CHECK — claim privacy verificati contro architettura reale

| Claim landing | Realtà | Verdict |
|---------------|--------|---------|
| "Dati restano sul tuo computer" (riga 231, 425, 1001) | SQLite locale `fluxion.db` ✅ | OK per CRM/Calendario/Fatture. **FALSO durante uso Sara** (Groq+Edge-TTS) |
| "Nomi e numeri non escono mai dalla tua rete" (riga 425) | Vero per UI gestionale. Falso per Sara (LLM cloud sente i nomi pronunciati). **Ed è falso anche per WhatsApp** (whatsapp-web.js usa server WA Meta, ovvio ma non chiarito) | **PARZIALMENTE FALSO** |
| "In regola con la legge sulla privacy (GDPR) senza fare nulla di speciale" (riga 361, 2007) | Schema GDPR esiste (`018, 037`), audit trail OK. MA cliente sanitario deve comunque: registro trattamenti, informativa, consenso Art. 9 esplicito. Trasferimento USA (Groq/Microsoft) richiede DPA e clausole contrattuali standard | **OTTIMISTICO E PERICOLOSO** — un dentista che si fida di questo claim e poi ha controllo Garante Privacy paga multa, e poi causa Fluxion |
| "Nessun trasferimento di dati a terzi" (riga 2007) | Falso quando Sara è attiva: voce → Groq (US), risposta → Edge-TTS (US). Email post-acquisto → Resend (US). Pagamenti → Stripe (Irlanda+US) | **FALSO** |

**Fix obbligatori GDPR:**
1. Privacy policy aggiornata con elenco trasferimenti extra-UE (Groq, Microsoft, Stripe, Resend, CF Workers)
2. DPA scaricabili per cliente
3. Modificare claim landing: "I tuoi dati gestionali (clienti, appuntamenti, fatture) restano sul tuo computer in formato cifrato. Sara usa servizi AI cloud (Groq, Microsoft) per processare la voce: il testo della conversazione è elaborato in tempo reale, non conservato."
4. Per settore sanitario: aggiungere modulo consenso Art. 9 stampabile + informativa template (esiste lo schema, mancano i template)

---

## 8. VERDICT FINALE

### La landing è onesta?
**Parzialmente.** Le sezioni "il problema" (Treatwell vs Fluxion), confronto competitor, requisiti minimi e FAQ funzionano sono ben scritti e onesti. Le sezioni **Pricing** (tier Clinic fantasma, Pro 6 settori), **Loyalty** (4 livelli a punti), **Sara** (latenza, riconoscimento dal numero) e **GDPR** (dati locali "sempre") **non riflettono lo stato reale del codice**.

### Quanto % dei claim sono verificabili?

Su 30 claim analizzati:
- ✅ **OK / verificati**: 11 (37%)
- 🟡 **Sfumature/asterischi mancanti**: 9 (30%)
- 🔴 **Mismatch critici da fixare prima del lancio**: 6 (20%) — C04 dati locali, C09 tier Clinic, C11 6 settori, C13 punti VIP, C17 multi-sede, C23 garanzia 30gg
- ⚠️ **Non verificabili dal codice (testimonial, accenti)**: 4 (13%)

### Raccomandazione operativa per il fondatore

**STOP IMMEDIATO al traffic Sales Agent finché non sono fixati C09 e C11**: stai vendendo un tier €1.497 fantasma e prometti 6 settori che il codice limita a 3. Ogni acquisto Pro che ne richiede 4+ → reso garantito + recensione negativa.

**Priorità di fix (24-48h):**
1. **Rimuovere card Clinic** dalla sezione Prezzi (commenta in HTML) finché non costruita
2. **Allineare Pro a 6 settori** (1 riga in `license_ed25519.rs:201` → `max_verticals: 6`) + rebuild iMac
3. **Riscrivere sezione fedeltà** con realtà attuale (tessera timbri) — 30 minuti di copy honest
4. **Rivedere sezione GDPR/Privacy** in landing per non promettere "automaticamente in regola"
5. **Aggiungere asterisco "Sara richiede VoIP separato"** — eviti reso da chi compra aspettandosi numero magico incluso

**Priorità di fix (settimane):**
- Implementare davvero il sistema punti VIP 4-tier (se vuoi vendere come fa la landing)
- Oppure pivot copy a "tessera timbri + VIP marker + pacchetti" — più piccolo, più vero
- Costruire tier Clinic davvero (multi-sede schema, supporto email tracked, branding Sara)
- Implementare meccanismo refund automatico per garanzia 30gg

### Frase chiave per il fondatore
> "Tutto si può fare. Basta solo trovare il modo." — ma non si può vendere prima di averlo fatto.
> Il prodotto sotto è solido. La landing oggi promette il 130% di quello che esiste. Riportala al 95% e venderai uguale ma senza chargeback.

---

**File chiave di riferimento (assoluti):**
- `/Volumes/MontereyT7/FLUXION/landing/index.html` (claims)
- `/Volumes/MontereyT7/FLUXION/src-tauri/src/commands/license_ed25519.rs:175-210` (tier features reali)
- `/Volumes/MontereyT7/FLUXION/fluxion-proxy/src/routes/stripe-webhook.ts:35-37` (mapping prezzi reali)
- `/Volumes/MontereyT7/FLUXION/src-tauri/migrations/005_loyalty_pacchetti_vip.sql:14-17` (loyalty schema reale)
- `/Volumes/MontereyT7/FLUXION/voice-agent/main.py:310-341` (endpoint Sara reali)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/booking_state_machine.py` (FSM 23 stati confermato)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/reminder_scheduler.py` (cron WA reali)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/voip.py` (VoIP/SIP requisiti)
- `/Volumes/MontereyT7/FLUXION/.claude/rules/architecture-distribution.md:15` (200 NLU/giorno limite)
- `/Volumes/MontereyT7/FLUXION/PRD-FLUXION-COMPLETE.md:445` (latenza reale ~1330ms)
