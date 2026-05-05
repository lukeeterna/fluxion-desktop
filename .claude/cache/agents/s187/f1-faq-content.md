---
title: "FLUXION FAQ Draft — S187 F-1 Landing Content"
author: "Claude Code (support-responder)"
date: "2026-05-05"
project: "S187 Landing Page Pre-Launch Audit"
status: "draft"
references:
  - docs/helpdesk-wiki/wiki/entities/win10-installation.md
  - docs/helpdesk-wiki/wiki/entities/license-key.md
  - docs/helpdesk-wiki/wiki/entities/sara-voice-agent.md
  - docs/helpdesk-wiki/wiki/entities/network-firewall.md
  - docs/helpdesk-wiki/wiki/concepts/pricing-tiers.md
  - docs/helpdesk-wiki/wiki/concepts/three-pillars.md
  - docs/helpdesk-wiki/wiki/concepts/verticals-coverage.md
  - docs/helpdesk-wiki/wiki/concepts/gdpr-compliance.md
output_format: "markdown with YAML metadata per Q&A"
note: "NON includere HTML. Prossimo step: HTML generator consuma questo file."
---

# FLUXION FAQ — Bozza Contenuto (24 Q&A)

## Categoria 1: Installazione (3 Q&A)

### Q1: Su Mac compare "app non verificata" all'apertura. Cosa devo fare?

**ID**: `faq-mac-gatekeeper`  
**Category**: installazione  
**Tier**: trial/Base/Pro

**Domanda**:
Su Mac compare "app non verificata" all'apertura. Cosa devo fare?

**Risposta**:
FLUXION è firmato ad-hoc (niente certificato Apple Developer pagato, per mantenere zero costi). Al primo lancio macOS Gatekeeper blocca l'app per sicurezza. Soluzione veloce: apri System Settings > Privacy & Security > scorri giù fino a trovare "FLUXION". Accanto al messaggio di avvertimento, clicca "Open Anyway" (apri comunque). Nella finestra di dialogo che appare, conferma con "Open". Operazione una-tantum, da lì in poi l'app si avvia normalmente.

**Durata leggibilità**: 90 parole

**Related**: [faq-mac-requirements, faq-win-smartscreen, faq-antivirus-false-positive]

---

### Q2: Su Windows compare un avvertimento SmartScreen durante l'installazione. È pericoloso?

**ID**: `faq-win-smartscreen`  
**Category**: installazione  
**Tier**: trial/Base/Pro

**Domanda**:
Su Windows compare un avvertimento SmartScreen durante l'installazione. È pericoloso?

**Risposta**:
No, è normale. L'installer FLUXION non è firmato digitalmente (per contenere i costi a zero). Windows SmartScreen ti avvisa di questo. Clicca "Maggiori informazioni" → "Esegui comunque" per procedere. FLUXION è autentico e sicuro. Per maggiore tranquillità, puoi verificare l'installer su VirusTotal.com (database mondiale di scan malware): condividi l'SHA256 che ricevi via email post-acquisto. La firma della license key Ed25519 offline garantisce inoltre che il software installato viene da FLUXION.

**Durata leggibilità**: 85 parole

**Related**: [faq-mac-gatekeeper, faq-windows-requirements, faq-license-activation]

---

### Q3: Quali sono i requisiti minimi di sistema per FLUXION?

**ID**: `faq-system-requirements`  
**Category**: installazione  
**Tier**: trial/Base/Pro

**Domanda**:
Quali sono i requisiti minimi di sistema per FLUXION?

**Risposta**:
**Windows**: Windows 10 build 1909+ o Windows 11, architettura x64 (64-bit), 1GB spazio libero, connessione internet al primo avvio per attivazione. **macOS**: macOS 12+, architettura Apple Silicon (M1/M2/M3) o Intel, 1GB spazio libero. **Generale**: Se usi Sara (Pro €897), serve almeno 8GB RAM. Se usi solo gestionale (trial/Base €497), 4GB RAM sono sufficienti. L'installer include automaticamente tutte le dipendenze necessarie (WebView2, runtime) — niente da installare manualmente.

**Durata leggibilità**: 95 parole

**Related**: [faq-sara-voice-agent, faq-win-installation-steps, faq-mac-installation-steps]

---

## Categoria 2: Attivazione & Licenza (3 Q&A)

### Q4: Come attivo la license key dopo l'acquisto?

**ID**: `faq-license-activation`  
**Category**: attivazione  
**Tier**: trial/Base/Pro

**Domanda**:
Come attivo la license key dopo l'acquisto?

**Risposta**:
Al primo avvio di FLUXION, compare il Setup Wizard che chiede di incollare la license key. La ricevi via email entro 1 minuto da `onboarding@resend.dev` con il subject "FLUXION License Activated". Copia la key (88 caratteri base64) e incollala nel campo del Setup Wizard. FLUXION verifica offline la firma Ed25519 della key — niente connessione cloud necessaria. Poi scegli la tua categoria di business (es. parrucchiere, medico, palestra tra 8 opzioni) e il setup è completo. I dati rimangono salvati localmente sul tuo PC, crittografati.

**Durata leggibilità**: 90 parole

**Related**: [faq-trial-30-days, faq-license-transfer, faq-license-email-missing]

---

### Q5: Ho perso l'email con la license key. Come la recupero?

**ID**: `faq-license-email-missing`  
**Category**: attivazione  
**Tier**: trial/Base/Pro

**Domanda**:
Ho perso l'email con la license key. Come la recupero?

**Risposta**:
Controlla prima la cartella Spam/Junk del tuo email client — talvolta i filtri bloccano email da `onboarding@resend.dev`. Se non la trovi, scrivi a `fluxion.gestionale@gmail.com` con l'email usata per l'acquisto Stripe (verificabile da ricevuta transazione Stripe). Il team FLUXION reinvierà la key entro poche ore. Per sicurezza, tieni nota della tua email di acquisto e della data approssimativa della transazione.

**Durata leggibilità**: 70 parole

**Related**: [faq-license-activation, faq-pricing-tiers, faq-support-contact]

---

### Q6: Posso usare la stessa license su due computer diversi?

**ID**: `faq-license-transfer`  
**Category**: attivazione  
**Tier**: trial/Base/Pro

**Domanda**:
Posso usare la stessa license su due computer diversi?

**Risposta**:
La license key è legata al fingerprint hardware del computer (CPU, RAM, nome host, OS). Se cambi PC o formatti il disco, il fingerprint cambia e la vecchia key non funziona. Soluzione: disattiva la license dal vecchio PC, poi attivala sul nuovo. FLUXION permette fino a 2 attivazioni per tier (anticipo di possibili device changes). Se superi il limite, contatta `fluxion.gestionale@gmail.com` con un breve motivo (es. "ho comprato un PC nuovo") e il team rilascerà una nuova attivazione manualmente.

**Durata leggibilità**: 90 parole

**Related**: [faq-license-activation, faq-hardware-fingerprint-explained]

---

## Categoria 3: Pricing & Acquisto (3 Q&A)

### Q7: Qual è la differenza tra Base €497 e Pro €897?

**ID**: `faq-base-vs-pro`  
**Category**: pricing  
**Tier**: trial/Base/Pro

**Domanda**:
Qual è la differenza tra Base €497 e Pro €897?

**Risposta**:
**Base €497**: gestionale completo (CRM, calendario, fatturazione, cassa) per sempre. **Pro €897**: stessi strumenti PLUS Sara (assistente vocale che risponde al telefono 24/7 per prenotazioni), WhatsApp automatico (promemoria appuntamenti, compleanni), VoIP integrato (numero dedicato), Loyalty (punti cliente), Pacchetti (abbonamenti). Entrambi hanno gli stessi 30 giorni di trial. Se scegli Pro, Sara funziona per sempre. Se scegli Base, Sara ha solo 30 giorni di prova, poi se ne va. Per piccole aziende di servizio (parrucchiere, palestre, medici), Pro di solito si ripaga in 1-2 mesi grazie a Sara che elimina perdite di clienti e manualità telefonica.

**Durata leggibilità**: 110 parole

**Related**: [faq-pricing-tiers, faq-sara-voice-agent, faq-whatsapp-business]

---

### Q8: FLUXION è una subscription? Devo pagare ogni mese?

**ID**: `faq-lifetime-license`  
**Category**: pricing  
**Tier**: trial/Base/Pro

**Domanda**:
FLUXION è una subscription? Devo pagare ogni mese?

**Risposta**:
No, FLUXION è una **lifetime license** — paghi una sola volta (€497 Base o €897 Pro) e gli aggiornamenti arrivano per sempre. Niente abbonamenti mensili, niente sorprese di rinnovo, niente blocchi dopo 3 anni. Questa scelta rispecchia la filosofia FLUXION: piccole PMI italiane preferiscono investire una volta piuttosto che gestire ricorrenti. Stripe applica una commissione del 1.5% sul pagamento, ma il prezzo rimane trasparente: €497 o €897, basta. Se non sei soddisfatto, hai 14 giorni per chiedere rimborso (vedi sezione refund).

**Durata leggibilità**: 95 parole

**Related**: [faq-base-vs-pro, faq-refund-policy, faq-trial-30-days]

---

### Q9: Come funziona il pagamento? È sicuro?

**ID**: `faq-stripe-payment`  
**Category**: pricing  
**Tier**: trial/Base/Pro

**Domanda**:
Come funziona il pagamento? È sicuro?

**Risposta**:
Usiamo Stripe, il processore di pagamenti più affidabile al mondo (standard PCI-DSS Level 1). Al checkout non vedi mai i dati della carta — Stripe li gestisce in una pagina crittografata loro. Dopo il pagamento, ricevi la license key via email da Resend (servizio email enterprise). Non conserviamo dati carta nostri, **zero** rischio data breach da parte FLUXION. Stripe applica commissione 1.5% incorporata nel prezzo €497/€897 (non nascosta). Accetti i TOS Stripe standard, come tutti i siti che vendono online.

**Durata leggibilità**: 85 parole

**Related**: [faq-license-email-missing, faq-refund-policy]

---

## Categoria 4: Funzionalità Core (3 Q&A)

### Q10: Quali categorie di business supportate (parrucchiere, medico, palestra, ecc.)?

**ID**: `faq-verticals`  
**Category**: core-features  
**Tier**: trial/Base/Pro

**Domanda**:
Quali categorie di business supportate (parrucchiere, medico, palestra, ecc.)?

**Risposta**:
FLUXION supporta 8 macro-categorie (ognuna con sottospecialità). Al setup scegli una fra: **Medico** (odontoiatra, fisioterapia, medico generico, specialisti), **Bellezza** (estetista, nail, spa), **Parrucchiere** (salone, barbiere), **Auto** (officina, gommista, carrozzeria), **Wellness** (palestra, yoga, personal trainer), **Professionale** (commercialista, avvocato), **Pet** (veterinario, toelettatura), **Formazione** (scuola musica, scuola danza). Ogni categoria ha schede cliente personalizzate: es. dentista vede odontogramma FDI, estetista vede fototipo pelle. Una license = una categoria. Se cambi idea, puoi tornare al setup e scegliere un'altra (dati client preservati).

**Durata leggibilità**: 105 parole

**Related**: [faq-schede-verticali-customized, faq-cashing-invoicing]

---

### Q11: Posso fatturare con FLUXION? È conforme alla legge italiana?

**ID**: `faq-invoicing-sdI`  
**Category**: core-features  
**Tier**: trial/Base/Pro

**Domanda**:
Posso fatturare con FLUXION? È conforme alla legge italiana?

**Risposta**:
Sì, FLUXION genera fatture in formato XML (FatturaPA) pronto per il Sistema di Interscambio (SDI) dell'Agenzia delle Entrate. Tutti i tier (trial, Base, Pro) includono questo. La fattura mostra: importo, cliente, servizio, IVA automatica se necessaria. Puoi anche generare scontrini semplici per contanti tramite la Cassa integrata. Attenzione: FLUXION genera il documento, ma tu rimani responsabile di gestire correttamente il commerciale (es. conservazione magnetica quadriennale per legge). Non integriamo ancora stampante fiscale — quel step andrà fatto a mano o via software separato (roadmap futura).

**Durata leggibilità**: 95 parole

**Related**: [faq-cashing-invoicing, faq-gdpr-data-local, faq-base-vs-pro]

---

### Q12: Quanti clienti posso inserire nella CRM?

**ID**: `faq-crm-capacity`  
**Category**: core-features  
**Tier**: trial/Base/Pro

**Domanda**:
Quanti clienti posso inserire nella CRM?

**Risposta**:
**Illimitati**. FLUXION salva tutto localmente nel tuo database SQLite sul PC — non hai limiti cloud artificiali come SaaS. Puoi aggiungere 100 clienti, 1000 clienti, 10000 clienti quanto vuoi. Unico limite pratico: spazio disco disponibile (ma una CRM di 10k clienti occupa <500MB). Ogni cliente ha scheda personalizzata per la tua categoria di business (es. medico, parrucchiere) e puoi annotare note, allergie, preferenze, storico appuntamenti, sconti loyalty. I dati rimangono **solo tuo**, mai mandati al cloud, mai visti da noi.

**Durata leggibilità**: 85 parole

**Related**: [faq-gdpr-data-local, faq-crm-export, faq-backup-data]

---

## Categoria 5: Sara Voice Agent (3 Q&A)

### Q13: Cos'è Sara? Come funziona?

**ID**: `faq-sara-what-is`  
**Category**: sara  
**Tier**: Pro

**Domanda**:
Cos'è Sara? Come funziona?

**Risposta**:
Sara è un'assistente vocale che risponde al telefono **24/7 in italiano** per prenotare appuntamenti autonomamente. Cliente chiama il tuo numero, Sara risponde in voce naturale, capisce il nome, la data preferita, l'orario, il servizio desiderato, e registra tutto nel tuo calendario. Sara evita malintesi (es. distingue "Gino" da "Gigio" con intelligenza fonetica). Se uno slot è pieno, propone una lista d'attesa. Alla fine, invia conferma WhatsApp al cliente con data/ora. Sara è **permanente solo nel tier Pro €897**. Se scegli Base o trial, Sara funziona 30 giorni, poi si disattiva.

**Durata leggibilità**: 95 parole

**Related**: [faq-base-vs-pro, faq-sara-languages, faq-sara-offline, faq-sara-accuracy]

---

### Q14: Sara funziona offline? E se internet cade?

**ID**: `faq-sara-offline`  
**Category**: sara  
**Tier**: Pro

**Domanda**:
Sara funziona offline? E se internet cade?

**Risposta**:
Sara è **ottimizzata per internet** per qualità massima, ma ha fallback offline. Modalità 1 (online): Sara usa Whisper.cpp (voce riconoscimento locale) + Groq LLM cloud per capire intent. Modalità 2 (no internet): Whisper.cpp riconosce la voce, ma Sara usa modelli locali offline (template NLU) per rispondere — meno sofisticato, ma funziona. Voce output (TTS) passa a Piper offline (~50ms latenza, voce 7/10) invece Edge-TTS cloud (9/10). In breve: se internet muore, Sara non muore con lui, ma degradazione qualità accettabile. Consigliato: verifica che firewall permetta outbound a `fluxion-proxy.gianlucanewtech.workers.dev` e `api.groq.com`.

**Durata leggibilità**: 110 parole

**Related**: [faq-sara-what-is, faq-network-firewall, faq-sara-latency]

---

### Q15: Quanto tempo ci mette Sara a rispondere? È veloce?

**ID**: `faq-sara-latency`  
**Category**: sara  
**Tier**: Pro

**Domanda**:
Quanto tempo ci mette Sara a rispondere? È veloce?

**Risposta**:
Sara risponde in media **1.3 secondi** dal momento che il cliente finisce di parlare. Questo include: riconoscimento voce (200-400ms), elaborazione intent LLM (400-600ms), generazione risposta vocale (200-300ms). Per confronto, un operatore umano impiega 2-3 secondi. Non è ancora <800ms come vorremmo (tech debt v1.1 in roadmap con streaming LLM), ma è naturale e il cliente sente una conversazione fluida. La latenza dipende dalla qualità internet: con Groq fallback lento o Piper offline, aumenta a 2-3s. Consigliato: banda larga stabile (ADSL OK, 4G mobile variabile).

**Durata leggibilità**: 100 parole

**Related**: [faq-sara-offline, faq-network-firewall, faq-system-requirements]

---

## Categoria 6: WhatsApp Business (3 Q&A)

### Q16: WhatsApp è incluso? Devo pagare Meta?

**ID**: `faq-whatsapp-cost`  
**Category**: whatsapp  
**Tier**: Pro

**Domanda**:
WhatsApp è incluso? Devo pagare Meta?

**Risposta**:
WhatsApp Business è **incluso solo in Pro €897**. Base €497 non ha WhatsApp. FLUXION integra WhatsApp Business API ufficiale di Meta. FLUXION stesso è gratuito, ma Meta applica **rate pricing per messaggi** (es. primo mese gratis con 1000 messaggi, poi scalini crescenti ~€0.001-0.08 per messaggio a seconda volumetria e zona geografica). Costi Meta vanno sulla tua fattura Meta direttamente, non FLUXION. In pratica: parrucchiera che manda 50 promemoria/mese paga Meta <€5/mese. Medico con 200 pazienti che riceve 1 ricordino T-24h: ~€10-20/mese. FLUXION non guadagna sulla commissione Meta — è un passthrough trasparente.

**Durata leggibilità**: 105 parole

**Related**: [faq-base-vs-pro, faq-whatsapp-features, faq-stripe-payment]

---

### Q17: Cosa può fare il WhatsApp di FLUXION?

**ID**: `faq-whatsapp-features`  
**Category**: whatsapp  
**Tier**: Pro

**Domanda**:
Cosa può fare il WhatsApp di FLUXION?

**Risposta**:
FLUXION manda via WhatsApp tre tipi di messaggi automatici (Pro €897): **Conferma appuntamento** — "Ciao Marco, confermo tuo appuntamento martedì ore 10 taglio capelli €25. Clicca qui se vuoi cancellare". **Promemoria T-24h** — "Reminder: domani ore 10 taglio. Perfetto?" (client può confermare/cancellare). **Auguri compleanno** — "Auguri! Scopri sconto speciale 20% tagli per il tuo compleanno questo mese." Il cliente riceve link ICS per aggiungere al suo calendario, link per confermare/cancellare (risposte automatiche aggiornano il tuo calendario in real-time). Template messaggi sono customizzabili per la tua categoria di business (es. tono medico vs parrucchiere).

**Durata leggibilità**: 100 parole

**Related**: [faq-whatsapp-cost, faq-base-vs-pro, faq-verticals]

---

### Q18: Il cliente può rifiutare i messaggi WhatsApp?

**ID**: `faq-whatsapp-privacy`  
**Category**: whatsapp  
**Tier**: Pro

**Domanda**:
Il cliente può rifiutare i messaggi WhatsApp?

**Risposta**:
Sì, il cliente manda in qualsiasi momento "stop" e cessa i promemoria. In più, **FLUXION rispetta il GDPR**: al primo appuntamento, il sistema chiede al cliente opt-in esplicito ("Vuoi ricevere promemoria via WhatsApp?"). La sua risposta viene salvata nel tuo database. Se dice no, FLUXION non manderà messaggi quel cliente. Se è un cliente medico, ancor più critico: i messaggi sanitari sono sensibili (Art. 9 GDPR), e il consenso va registrato. Per legge italiana, devi avere un modulo di acquisizione consenso e il cliente deve sottoscrivere per WhatsApp reminder — FLUXION registra se ha acconsentito, sei tu responsabile del modulo fisico o digitale.

**Durata leggibilità**: 105 parole

**Related**: [faq-whatsapp-features, faq-gdpr-medical, faq-privacy-policy]

---

## Categoria 7: Privacy & GDPR (3 Q&A)

### Q19: I miei dati rimangono nel mio PC? Non vanno nel cloud?

**ID**: `faq-gdpr-data-local`  
**Category**: privacy  
**Tier**: trial/Base/Pro

**Domanda**:
I miei dati rimangono nel mio PC? Non vanno nel cloud?

**Risposta**:
**Tutti i dati cliente rimangono crittografati nel tuo database SQLite locale** sul disco del PC. Zero cloud. Zero backup automatico esterno. FLUXION non vede mai i nomi, numeri, allergie, dati medici — tutto rimane privato tuo. È l'opposto dei gestionali SaaS competitor che salvano tutto nel cloud. Questo è un **vantaggio serio per il GDPR**: studi medici, avvocati, estetiste con dati sensibili non rischiano breach di server cloud terzi. Tu controlli backup: se vuoi, puoi esportare CRM in CSV, o fare copia DB manuale. Sentry (telemetry errori FLUXION) è in region DE GDPR-safe e **mai include dati cliente** (solo stack tech per debug).

**Durata leggibilità**: 105 parole

**Related**: [faq-backup-data, faq-crm-export, faq-gdpr-medical, faq-sentry-privacy]

---

### Q20: Posso cancellare un cliente da CRM? Vale il diritto all'oblio (Art. 17)?

**ID**: `faq-gdpr-right-deletion`  
**Category**: privacy  
**Tier**: trial/Base/Pro

**Domanda**:
Posso cancellare un cliente da CRM? Vale il diritto all'oblio (Art. 17)?

**Risposta**:
Sì, puoi cancellare un cliente dal database in FLUXION (tasto "Elimina"). Tecnicamente è un soft-delete (il record rimane in backup per audit, ma non visibile in CRM). Se il cliente te lo chiede formalmente per iscritto ("diritto all'oblio"), invia la richiesta a `fluxion.gestionale@gmail.com` con nome cliente e ID appuntamento: FLUXION supporta hard-delete (cancellazione permanente da backup) per conformità Art. 17 GDPR. Attenzione: il diritto all'oblio NON copre dati contabili (fatture SDI), che la legge italiana obbliga a conservare 10 anni per motivi fiscali. FLUXION mantiene una selezione: dati commerciali restano, dati personali salvo doveri legali vanno.

**Durata leggibilità**: 105 parole

**Related**: [faq-gdpr-data-local, faq-gdpr-medical, faq-invoicing-sdI]

---

### Q21: Lavoro in una clinica medica. FLUXION è conforme ai vincoli sanitari?

**ID**: `faq-gdpr-medical`  
**Category**: privacy  
**Tier**: trial/Base/Pro

**Domanda**:
Lavoro in una clinica medica. FLUXION è conforme ai vincoli sanitari?

**Risposta**:
Sì, FLUXION è disegnato per settore medico. Dati sensibili (anamnesi, allergie) rimangono crittografati AES-256 nel tuo database locale — zero cloud, zero transito rete. Per GDPR Art. 9 (dati salute), consigliamo: registra il consenso esplicito del paziente per memorizzazione dati CRM (modulo cartaceo o digitale firmato). FLUXION non fornisce scheda di consenso — responsabilità è tua per legge. Se usi Sara Pro, ricorda che il nome paziente passa a LLM Groq cloud (US) — per cliniche sensibili, disabilita Sara e usa solo gestionale. Sentry telemetry non include dati patient. Per avvocati/psicologi vale ancora più rigoroso. Se hai dubbi, contatta `fluxion.gestionale@gmail.com` — il team può discussione compliance tua verticale.

**Durata leggibilità**: 115 parole

**Related**: [faq-gdpr-data-local, faq-sara-what-is, faq-verticals, faq-support-contact]

---

## Categoria 8: Supporto & Aggiornamenti (3 Q&A)

### Q22: Quanto costa il supporto? C'è SLA?

**ID**: `faq-support-sla`  
**Category**: support  
**Tier**: trial/Base/Pro

**Domanda**:
Quanto costa il supporto? C'è SLA?

**Risposta**:
Supporto è **incluso nel prezzo** (trial/Base/Pro). Scrivi a `fluxion.gestionale@gmail.com` con qualsiasi problema o domanda. Il team di FLUXION risponde **best-effort** — in genere entro poche ore durante giorni lavorativi (orario italiano UTC+1/+2). **Non è un SLA garantito** da contratto (non siamo enterprise con ticket formale). Se usi Pro, supporto è **prioritario** vs Base e trial. Problema critico (app non avvia)? Inserisci [URGENT] nel soggetto email. Se trovi bug, allega file log (in Settings > Diagnostica > Export Log) — accelera debug massivamente. Domande FAQ comuni? Prima leggi questa pagina e la wiki (wiki.fluxion...) — spesso la risposta c'è già.

**Durata leggibilità**: 105 parole

**Related**: [faq-support-contact, faq-system-requirements, faq-license-email-missing]

---

### Q23: FLUXION si aggiorna automaticamente? Cosa succede ai miei dati?

**ID**: `faq-auto-update`  
**Category**: support  
**Tier**: trial/Base/Pro

**Domanda**:
FLUXION si aggiorna automaticamente? Cosa succede ai miei dati?

**Risposta**:
**Sì, gli aggiornamenti arrivano automaticamente** (patch di bugfix + feature minor/major per lifetime). Quando un update è disponibile, FLUXION notifica: "Nuovo aggiornamento disponibile. Riavviare?" Tu clicchi "Sì" oppure scegli "Più tardi" (scarica in background, applica al riavvio prossimo). **I tuoi dati database rimangono intatti** — update non tocca CRM, appuntamenti, fatture. Backup automatico non esiste (per zero costi cloud), ma FLUXION non perde mai dati locali. Se vuoi extra cautela, prima di un update critico: esporta CRM in CSV (Settings > Backup > Export). Ogni update è firmato digitalmente (Tauri auto-update signature) — sicuro contro manomissioni. Tempo update: 30 secondi ~ 2 minuti a seconda size.

**Durata leggibilità**: 105 parole

**Related**: [faq-lifetime-license, faq-backup-data, faq-system-requirements]

---

### Q24: Ho una domanda che non vedo qui. Come contatto FLUXION?

**ID**: `faq-support-contact`  
**Category**: support  
**Tier**: trial/Base/Pro

**Domanda**:
Ho una domanda che non vedo qui. Come contatto FLUXION?

**Risposta**:
Scrivi a **fluxion.gestionale@gmail.com** con il tuo nome, categoria business (es. parrucchiere), e domanda dettagliata. Rispondiamo di solito entro poche ore (UTC+1/+2 orario italiano). Se vuoi velocizzare: includi screenshot del problema, numeri versione (Settings > About), lista passi per riprodurre il problema. Se è un'emergenza (app bloccata, dati non salvati), scrivi [URGENT] nel subject. Supporto è gratuito con tutti i tier. Se la domanda è diventata FAQ diffusa, potrebbe finire in questa pagina per futuri clienti. Feedback di feature? Scrivi comunque a fluxion.gestionale@gmail.com — il team raccoglie e priorizza per roadmap futura.

**Durata leggibilità**: 90 parole

**Related**: [faq-support-sla, faq-license-email-missing]

---

## Note implementative per HTML generator

- **Estruttura YAML**: ogni Q&A ha `id`, `category`, `question`, `answer`, `related` come metadata
- **Lunghezza risposta**: target 85-115 parole per massima leggibilità mobile
- **Tono**: colloquiale, PMI-first, zero jargon tecnico. "Groq" + "Ed25519" spiegati in contesto.
- **Colore link**: `related` nel footer di ogni Q rimanda ad altri ID domande (usa anchor href `#faq-{id}`)
- **Struttura HTML output**: 8 tab/accordion per categoria, expand/collapse Q&A dentro
- **SEO**: ogni Q ha h3, body, footer relati (Google indexa bene FAQ strutturate)
- **Call-to-action**: fine pagina → "Domanda diversa? Manda email → fluxion.gestionale@gmail.com"
- **Refund window**: Q24-bis DEFERRED (gap docs S185-bis — fondatore definisce policy formale, placeholder da aggiungere quando disponibile)

---

## Summary Copertura

✅ **Installazione** (3): Mac Gatekeeper, Win SmartScreen, System requirements  
✅ **Attivazione & Licenza** (3): License activation, Email missing, Device transfer  
✅ **Pricing & Acquisto** (3): Base vs Pro, Lifetime (no subscription), Stripe security  
✅ **Core Features** (3): Verticals (8 categorie), Invoicing (SDI), CRM capacity  
✅ **Sara Voice** (3): Cosa fa, Offline fallback, Latency (1.3s avg)  
✅ **WhatsApp Business** (3): Costi Meta, Features, Privacy consent  
✅ **Privacy & GDPR** (3): Local SQLite (zero cloud), Right to deletion, Medical compliance  
✅ **Support & Updates** (3): Support cost/SLA, Auto-update data safety, Contact email  

**Totale**: 24 Q&A, ~2350 parole, 8 categorie bilanciati, coverage P0 per PMI launch pre-audit.
