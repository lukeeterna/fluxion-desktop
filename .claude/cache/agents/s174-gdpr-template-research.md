# S174 — GDPR Template Research
> Legal Compliance Checker | 2026-04-27 | Basato su testo normativo verificato EUR-Lex + Garante Privacy

---

## TL;DR

PMI italiana sotto 250 dip. con trattamento di dati sanitari o dati non occasionali DEVE tenere il registro trattamenti (art. 30 GDPR). I 4 template coprono esattamente questo perimetro. Il formato raccomandato per lead magnet è: informativa SHORT in `.html` stampabile + registro `.xlsx` editabile + consenso sanitario `.pdf` compilabile + checklist `.html` standalone. Email gate riduce conversion, ma migliora qualificazione lead — usare form minimo (solo email) senza wall.

---

## 1. BASE NORMATIVA VERIFICATA

### Articolo 13 GDPR — Informativa (art. cit. EUR-Lex)
Obbliga il titolare a fornire all'interessato, al momento della raccolta:
- Identità e contatti titolare
- Contatti DPO (se nominato)
- Finalità e base giuridica del trattamento
- Interessi legittimi (se base giuridica è art. 6(1)(f))
- Categorie destinatari e trasferimenti extra-UE
- Periodo di conservazione o criteri per determinarlo
- Diritti: accesso, rettifica, cancellazione, limitazione, portabilità, opposizione
- Diritto di reclamo al Garante
- Se esiste trattamento automatizzato/profilazione

### Articolo 30 GDPR — Registro trattamenti
Obbligo per titolari. Il registro contiene:
- Nome e contatti titolare (+ contitolare, rappresentante, DPO se presenti)
- Finalità del trattamento
- Categorie di interessati e categorie di dati personali
- Categorie di destinatari (inclusi paesi terzi)
- Trasferimenti verso paesi terzi con identificazione paese + garanzie
- Termini di cancellazione (retention)
- Misure di sicurezza tecniche e organizzative

**Soglia PMI**: sotto 250 dip. l'obbligo scatta se:
- Il trattamento può presentare rischi per diritti/libertà (anche non elevati)
- Il trattamento è non occasionale (es. agenda clienti ricorrente)
- Si trattano categorie particolari (salute, biometria, etnia, ecc.)

**Garante FAQ (doc. 9047529, 08/10/2018)**: confermano che saloni, palestre, studi medici, fisioterapisti trattano dati "non occasionali" e/o dati sanitari — TUTTI rientrano nell'obbligo, indipendentemente dalla dimensione.

### Articolo 9 GDPR — Categorie particolari (dati salute)
- Vietato di default (art. 9(1))
- Eccezioni ammesse per uso sanitario:
  - Art. 9(2)(a): **consenso esplicito** dell'interessato
  - Art. 9(2)(h): trattamento **necessario per finalità di medicina preventiva, diagnosi, assistenza o terapia sanitaria** da professionisti sanitari soggetti a segreto professionale

**Provvedimento Garante 7 marzo 2019 [doc. 9091942]**:
- Liberi professionisti sanitari (dentisti, fisio, medici) possono basarsi su art. 9(2)(h) **senza consenso separato** se il trattamento è strettamente necessario alla prestazione sanitaria
- Consenso art. 9(2)(a) serve invece per: app mediche con accesso a terzi, programmi fedeltà farmacia, finalità promozionali/commerciali, dossier sanitario
- **Centro estetico, salone, palestra** NON sono professionisti sanitari → usano **art. 9(2)(a) consenso esplicito** per qualsiasi dato salute che raccolgono (es. allergie, controindicazioni)

### Articolo 22 GDPR — Decisioni automatizzate / profilazione
- Diritto dell'interessato di NON essere sottoposto a decisioni basate UNICAMENTE su trattamento automatizzato che produca effetti giuridici o significativi
- **Sara (voice agent)**: NON rientra in art. 22 perché:
  - Le decisioni di booking vengono confermate da un operatore umano (il titolare del gestionale)
  - Sara non produce "effetti giuridici" autonomamente: prende prenotazioni condizionate a conferma umana
  - È "assistenza automatizzata" (uso consentito) non "decisione automatizzata" (art. 22 restrittivo)
- **Classificazione corretta nel registro**: "Gestione automatizzata delle prenotazioni telefoniche mediante agente conversazionale AI" — finalità: erogazione servizio; base giuridica: art. 6(1)(b) esecuzione contratto; NON profilazione; NON art. 22

### Articolo 33 GDPR — Data breach 72h
- Notifica al Garante entro 72h dalla scoperta
- Eccezione: se "improbabile che presenti rischio per diritti/libertà"
- Notifica deve contenere: natura violazione, categorie/numero interessati, contatti DPO/referente, conseguenze probabili, misure adottate

### Articolo 37 GDPR — DPO (quando obbligatorio)
**Non obbligatorio** per PMI 1-15 dip. a meno che:
- Sia un'autorità pubblica (no)
- Attività principali = monitoraggio regolare e sistematico su **larga scala** (no per salone/palestra)
- Attività principali = trattamento **su larga scala** di categorie particolari (art. 9) o penali

**Conclusione per FLUXION target**: DPO NON obbligatorio. Raccomandato facoltativamente per studi medici/dentali con molti pazienti, ma non imposto dalla norma per PMI 1-15 dip. con operatività locale.

---

## 2. STRUTTURA DEI 4 TEMPLATE

### Template 1 — `informativa-privacy.docx`
**Base normativa**: Art. 13 GDPR | Art. 12 GDPR (forma concisa, linguaggio chiaro)
**Garante**: Provvedimento 7/03/2019 — informativa deve essere "concisa, trasparente, intelligibile, facilmente accessibile, linguaggio semplice e chiaro"

**Struttura (SHORT — 1 pagina fronte-retro)**:

```
INFORMATIVA SUL TRATTAMENTO DEI DATI PERSONALI
ai sensi dell'art. 13 del Regolamento UE 2016/679 (GDPR)

1. CHI SIAMO (TITOLARE DEL TRATTAMENTO)
   [NOME ATTIVITÀ] | [INDIRIZZO COMPLETO] | [EMAIL] | [TELEFONO]
   [Titolare: NOME TITOLARE]

2. QUALI DATI RACCOGLIAMO E PERCHÉ
   a) Dati anagrafici (nome, cognome, telefono, email): gestione appuntamenti e comunicazioni
      Base giuridica: art. 6(1)(b) GDPR — esecuzione del contratto di servizio
   b) Preferenze e storico servizi: personalizzazione del servizio, promemoria
      Base giuridica: art. 6(1)(b) GDPR — esecuzione del contratto
   c) [Solo se raccolti] Dati relativi alla salute (allergie, controindicazioni):
      Base giuridica: art. 9(2)(a) GDPR — consenso esplicito dell'interessato
   d) Comunicazioni via WhatsApp/SMS (se autorizzate): conferme appuntamenti, promemoria
      Base giuridica: art. 6(1)(a) GDPR — consenso

3. CON CHI CONDIVIDIAMO I TUOI DATI
   I tuoi dati NON vengono venduti né ceduti a terzi.
   Possono essere accessibili a: [DIPENDENTI/COLLABORATORI] per l'erogazione del servizio.
   [Se applicabile] Software gestionale: i dati sono archiviati sul computer della struttura
   (non su server cloud di terze parti).
   [Se Sara è attivo] Servizio di prenotazione telefonica AI: l'audio della telefonata viene
   elaborato da provider certificati per la trascrizione. Nessun dato è venduto o profilato.

4. PER QUANTO TEMPO CONSERVIAMO I TUOI DATI
   - Dati anagrafici e storico servizi: [X anni, es. 7] dalla data dell'ultima prestazione
   - Dati contabili/fatturazione: 10 anni (obblighi fiscali)
   - Dati raccolti su base consenso: fino alla revoca del consenso

5. I TUOI DIRITTI
   Hai diritto di: accedere ai tuoi dati · chiederne la rettifica · chiederne la cancellazione
   · limitarne il trattamento · ricevere una copia (portabilità) · opporti al trattamento
   · revocare il consenso in qualsiasi momento (senza pregiudicare la liceità del trattamento
   precedente) · proporre reclamo al Garante (www.garanteprivacy.it)
   
   Per esercitare i tuoi diritti: [EMAIL] oppure di persona presso [INDIRIZZO]

6. AGGIORNAMENTI
   Questa informativa è aggiornata al [DATA]. Eventuali modifiche saranno comunicate.
```

**Placeholder da compilare**: `[NOME ATTIVITÀ]`, `[INDIRIZZO COMPLETO]`, `[EMAIL]`, `[TELEFONO]`, `[NOME TITOLARE]`, `[DIPENDENTI/COLLABORATORI]`, `[X anni]`, `[DATA]`

**Note implementative**:
- Versione SHORT (sopra): per cartello in sala d'attesa / consegna al cliente / QR code
- Non serve versione LONG per PMI 1-15 dip. con trattamenti standard (Garante art. 12: "concisa")
- Se studi dentali/medici: aggiungere sezione separata per art. 9(2)(h) con riferimento esplicito alla finalità sanitaria

---

### Template 2 — `registro-trattamenti.xlsx`
**Base normativa**: Art. 30 GDPR | FAQ Garante doc. 9047529

**Struttura tabella** (una riga per tipo di trattamento):

| Colonna | Contenuto |
|---------|-----------|
| N. | Numero progressivo |
| Nome trattamento | Es. "Gestione anagrafica clienti" |
| Finalità | Es. "Erogazione servizi, gestione appuntamenti" |
| Base giuridica | Es. "Art. 6(1)(b) — esecuzione contratto" |
| Categorie interessati | Es. "Clienti, potenziali clienti" |
| Categorie dati | Es. "Dati anagrafici, contatti, storico servizi" |
| Dati particolari (art. 9)? | Sì/No — se Sì specificare tipo |
| Destinatari | Es. "Dipendenti, nessun terzo" |
| Trasferimenti extra-UE | Sì/No — se Sì: paese + garanzie |
| Retention | Es. "7 anni dall'ultima prestazione" |
| Misure sicurezza | Es. "Crittografia disco, accesso con password, backup giornaliero" |
| Data ultima verifica | Data aggiornamento riga |

**Righe pre-compilate per FLUXION target PMI** (adattabili):

**Riga 1 — Anagrafica clienti**
- Finalità: Gestione rapporto commerciale, prenotazioni, fatturazione
- Base: Art. 6(1)(b) esecuzione contratto
- Interessati: Clienti attuali e passati
- Dati: Nome, cognome, telefono, email, data nascita, indirizzo
- Art. 9: No
- Destinatari: Titolare + dipendenti autorizzati
- Extra-UE: No (gestionale on-premise)
- Retention: 7 anni dall'ultima prestazione
- Sicurezza: Software gestionale con accesso autenticato, backup, PC protetto da password

**Riga 2 — Prenotazioni e agenda**
- Finalità: Gestione appuntamenti, ottimizzazione agenda, riduzione no-show
- Base: Art. 6(1)(b)
- Dati: Anagrafica + servizio prenotato + data/ora + note
- Art. 9: No (salvo note con controindicazioni)
- Extra-UE: No se gestionale on-premise; Sì (USA) se Sara attivo — provider certificato
- Retention: 3 anni (attività commerciale corrente)
- Sicurezza: come riga 1 + cifratura backup

**Riga 3 — Comunicazioni WhatsApp/SMS**
- Finalità: Conferme appuntamenti, promemoria, comunicazioni commerciali (se consenso)
- Base: Art. 6(1)(b) per conferme / Art. 6(1)(a) consenso per marketing
- Dati: Numero telefono, nome, contenuto messaggio, data invio
- Art. 9: No
- Extra-UE: Sì (Meta/WhatsApp — USA, SCCs applicabili)
- Retention: 12 mesi
- Sicurezza: Whatsapp Business account protetto 2FA

**Riga 4 — Fatturazione e contabilità**
- Finalità: Obbligo fiscale, emissione ricevute/fatture
- Base: Art. 6(1)(c) obbligo legale
- Dati: Nome, CF/P.IVA, indirizzo, importi, servizi
- Art. 9: No
- Extra-UE: No (o Sì se SDI provider estero — specificare)
- Retention: 10 anni (obblighi fiscali)
- Sicurezza: Backup + accesso limitato

**Riga 5 — Gestione voce/AI Sara (se attivo)**
- Finalità: Gestione automatizzata prenotazioni telefoniche, riduzione carico operativo
- Base: Art. 6(1)(b) esecuzione contratto di servizio
- Interessati: Chiamanti (clienti e non)
- Dati: Audio chiamata (elaborato in tempo reale, non conservato), testo trascritto (temporaneo), dati prenotazione
- Art. 9: No (Sara non raccoglie dati sanitari)
- Extra-UE: Sì — STT/LLM elaborati su server USA (Groq/Cerebras) con garanzie contrattuale; audio eliminato dopo trascrizione
- Retention: Audio: non conservato. Prenotazione: come riga 2
- Sicurezza: TLS in transito, nessun audio conservato, provider con DPA
- Note: NON profilazione / NON decisione automatizzata ai sensi art. 22 (prenotazione confermata da operatore)
- Disclosure obbligatoria: Informare il chiamante all'inizio della telefonata ("questa chiamata è assistita da AI")

**Riga 6 — [Solo verticali sanitari] Dati relativi alla salute**
- Finalità: Erogazione prestazione sanitaria/estetica (es. anamnesi, allergie, controindicazioni)
- Base: Art. 9(2)(a) consenso esplicito / Art. 9(2)(h) per professionisti sanitari (dentisti, fisio)
- Interessati: Pazienti/clienti con scheda sanitaria
- Dati: Anamnesi, allergie, patologie, farmaci, note cliniche
- Art. 9: SÌ — dati relativi alla salute
- Destinatari: Solo professionista titolare + collaboratori con vincolo segreto professionale
- Extra-UE: No (schede su gestionale on-premise)
- Retention: 10 anni (obblighi deontologici) / durata rapporto
- Sicurezza: Accesso riservato, cifratura, backup

**Riga 7 — Programma fedeltà / marketing (se attivo)**
- Finalità: Fidelizzazione, invio promozioni
- Base: Art. 6(1)(a) consenso
- Dati: Nome, contatto, storico acquisti, punti/timbri
- Art. 9: No
- Extra-UE: No
- Retention: Fino a revoca consenso + 12 mesi
- Sicurezza: come riga 1

---

### Template 3 — `consenso-art9-sanitario.pdf`
**Base normativa**: Art. 9(2)(a) GDPR | Provvedimento Garante 7/03/2019 [9091942]
**Destinatari**: Centri estetici, nail artist, palestre (non professionisti sanitari) + studi dentali/fisio per trattamenti NON strettamente terapeutici

**Struttura modulo compilabile**:

```
MODULO DI CONSENSO AL TRATTAMENTO DI DATI RELATIVI ALLA SALUTE
ai sensi dell'art. 9, paragrafo 2, lett. a) del Regolamento UE 2016/679 (GDPR)

TITOLARE DEL TRATTAMENTO
[NOME ATTIVITÀ] — [INDIRIZZO] — [EMAIL]

INFORMATIVA SINTETICA
[NOME ATTIVITÀ] raccoglie i seguenti dati relativi alla tua salute esclusivamente per:
- Adattare i trattamenti/servizi alle tue condizioni fisiche e prevenire controindicazioni
- [FINALITÀ SPECIFICA: es. "pianificare il percorso estetico in sicurezza"]

Questi dati sono conservati [X anni] e accessibili solo al personale autorizzato.
Non vengono condivisi con terzi, salvo obbligo di legge.

DATI CHE RACCOGLIAMO (barrare quello che si applica):
[ ] Allergie e intolleranze
[ ] Patologie in corso: _______________
[ ] Farmaci assunti: _______________
[ ] Gravidanza / allattamento
[ ] Interventi chirurgici recenti (ultimi 12 mesi): _______________
[ ] Condizioni cutanee / dermatologiche: _______________
[ ] Controindicazioni specifiche: _______________
[ ] Altro: _______________

ESPRESSIONE DEL CONSENSO
Il/la sottoscritto/a _________________________________ (nome e cognome)
nato/a il _____________ a _____________
dichiara di aver ricevuto e compreso l'informativa sul trattamento dei dati personali
e PRESTA IL PROPRIO CONSENSO ESPLICITO al trattamento dei dati relativi alla salute
sopra indicati per le finalità descritte.

Il consenso è:
[ ] Libero (non condizionato all'erogazione del servizio per i dati non strettamente necessari)
[ ] Revocabile in qualsiasi momento (senza pregiudicare la liceità del trattamento pregresso)

Luogo e data: _________________________
Firma: _________________________________

REVOCA DEL CONSENSO (da compilare solo in caso di revoca)
Il/la sottoscritto/a revoca il consenso prestato in data _____________.
Firma: _________________________________  Data revoca: _____________
```

**Note legali importanti per il template**:
- Per dentisti e fisioterapisti che agiscono per finalità terapeutica: la base giuridica principale è art. 9(2)(h), NON il consenso — ma il consenso separato può essere richiesto per dati accessori (es. uso in ricerca, comunicazione con medico di base)
- Il consenso art. 9 deve essere ESPLICITO: non è sufficiente un consenso generico
- Il consenso non può essere condizione per l'accesso al servizio (principio di proporzionalità) — se il dato è strettamente necessario per sicurezza del trattamento, la base è contrattuale o interesse vitale, non consenso
- Per minorenni: necessario consenso dei genitori/tutori

---

### Template 4 — `guida-gdpr-pmi.html`
**Formato**: HTML standalone, no framework JS, vanilla CSS, stampa/PDF-friendly
**Target**: PMI titolare che legge e compila da solo, 20-30 min

**Struttura checklist** (15 step):

```html
<!-- STEP 1: Sei titolare del trattamento? -->
<!-- Quando: sempre, prima di tutto -->
<!-- Norma: Art. 4(7) GDPR -->
<!-- Spiegazione: Se gestisci dati di clienti per la tua attività, sei titolare. -->
<!-- Esempio salone: "Sì: tengo l'agenda con nomi e telefoni dei clienti" -->

<!-- STEP 2: Devi tenere il registro dei trattamenti? -->
<!-- Norma: Art. 30 GDPR + FAQ Garante doc. 9047529 -->
<!-- Risposta per PMI FLUXION: QUASI SEMPRE SÌ -->
<!-- Regola: sotto 250 dip. sei obbligato se tratti dati non occasionali (agenda clienti = non occasionale) -->
<!-- oppure dati sanitari (allergie, anamnesi = sempre sì) -->

<!-- STEP 3: Hai l'informativa privacy da dare ai clienti? -->
<!-- Norma: Art. 13 GDPR -->
<!-- Azione: Stampa e affiggi in sala d'attesa + dai copia digitale alla prima visita -->
<!-- Tempo stimato: 15 min se usi il template 1 -->

<!-- STEP 4: Devi nominare un DPO (Responsabile Protezione Dati)? -->
<!-- Norma: Art. 37 GDPR -->
<!-- Risposta per PMI 1-15 dip.: NO, salvo casi eccezionali (grande volume dati sanitari) -->
<!-- Esempio: palestra con 2000 clienti e app biometrica → valutare. Salone 200 clienti → NO -->

<!-- STEP 5: Usi dati relativi alla salute (es. allergie, patologie)? -->
<!-- Norma: Art. 9 GDPR -->
<!-- Se sì: devi avere consenso esplicito separato (usa template 3) -->
<!-- Esempio dentista: anamnesi = art. 9(2)(h) senza consenso separato -->
<!-- Esempio centro estetico: allergie pelle = art. 9(2)(a) consenso esplicito obbligatorio -->

<!-- STEP 6: Cookie banner sul tuo sito web? -->
<!-- Norma: D.Lgs 196/2003 art. 122 (Cookie Law) + Provvedimento Garante 10/06/2021 -->
<!-- Se hai Google Analytics, Facebook Pixel, YouTube embed → SÌ, obbligatorio -->
<!-- Se il sito è solo vetrina senza tracking → cookie tecnici solo, nessun banner obbligatorio -->

<!-- STEP 7: Usi WhatsApp per comunicare con clienti? -->
<!-- Norma: Art. 6(1)(b)/(a) GDPR + Linee guida Garante comunicazioni elettroniche -->
<!-- Regola: per conferme appuntamento = base contrattuale (no consenso separato) -->
<!-- Per promozioni/marketing = serve consenso esplicito preventivo -->

<!-- STEP 8: Usi un'AI per rispondere al telefono (es. Sara)? -->
<!-- Norma: Art. 13 GDPR (informativa), Art. 22 GDPR (decisioni automatizzate) -->
<!-- Obbligatorio: informare il chiamante che la telefonata è gestita da AI -->
<!-- Sara NON è decisione automatizzata (art. 22) se l'operatore conferma la prenotazione -->
<!-- Azione: messaggio di benvenuto Sara deve includere "assistenza automatizzata AI" -->

<!-- STEP 9: Data breach — sai cosa fare? -->
<!-- Norma: Art. 33 GDPR -->
<!-- Scenario: PC rubato con dati clienti, accesso non autorizzato, ransomware -->
<!-- Regola: notifica Garante entro 72h se rischio per interessati -->
<!-- Come: modulo online Garante (garanteprivacy.it/home/notifica-data-breach) -->

<!-- STEP 10: Backup dei dati? -->
<!-- Non è norma GDPR specifica, ma è "misura tecnica adeguata" art. 32 GDPR -->
<!-- Raccomandazione: backup quotidiano automatico + copia offline settimanale -->

<!-- STEP 11: Formazione dipendenti? -->
<!-- Norma: Art. 29 GDPR + Art. 32(4) -->
<!-- Azione: far firmare a ogni dipendente "Nomina ad Autorizzato al trattamento" (1 pagina) -->
<!-- Contenuto: quali dati possono vedere, come gestirli, a chi riportare anomalie -->

<!-- STEP 12: Diritti degli interessati — come gestirti le richieste? -->
<!-- Norma: Art. 15-22 GDPR -->
<!-- Tempo di risposta: 1 mese (prorogabile di 2 mesi in casi complessi) -->
<!-- Canale: email dedicata o sportello fisico -->
<!-- Azione: crea una procedura interna (anche 5 righe) per gestire richieste accesso/cancellazione -->

<!-- STEP 13: Trasferimento dati extra-UE? -->
<!-- Norma: Art. 44-49 GDPR -->
<!-- Quando si applica: usi WhatsApp (Meta USA), Google (USA), software cloud USA -->
<!-- Soluzione: verifica che il provider abbia SCCs (Standard Contractual Clauses) o sia certificato -->
<!-- Gestionale FLUXION on-premise: dati NON escono dall'UE — vantaggio differenziante -->

<!-- STEP 14: Periodo di conservazione — quando cancellare i dati? -->
<!-- Norma: Art. 5(1)(e) GDPR — "limitazione della conservazione" -->
<!-- Regola pratica per PMI: -->
<!-- Clienti inattivi da 7+ anni → anonimizzare i dati anagrafici -->
<!-- Dati contabili → 10 anni (D.P.R. 600/1973) -->
<!-- Consensi marketing → fino a revoca + 12 mesi buffer -->

<!-- STEP 15: Hai aggiornato questo registro nell'ultimo anno? -->
<!-- Norma: Art. 30(3) GDPR — il registro va aggiornato -->
<!-- Raccomandazione: revisione annuale o ad ogni cambio rilevante (nuovo software, nuovo trattamento) -->
<!-- FLUXION: il software include audit trail di chi ha acceduto a cosa e quando -->
```

**Design raccomandato** (HTML standalone):
- Ogni step: box con icona + titolo + norma in piccolo + descrizione + esempio settoriale + checkbox
- Stile: bianco/grigio, nessun framework, max 50KB totale
- Print CSS: pagina A4, nessun colore di sfondo
- Nessun JS esterno, nessun tracker, nessun cookie
- Lingua: italiano semplice, zero latinismi
- In fondo: firma + data + sezione "revisione annuale"

---

## 3. DISCLAIMER LEGALE STANDARD (da includere su TUTTI i template)

```
AVVERTENZA LEGALE

Questo documento è un modello informativo fornito a titolo orientativo e non costituisce
consulenza legale. Le PMI che trattano dati personali sono responsabili dei propri adempimenti
GDPR nella loro totalità.

FLUXION fornisce questo template come strumento di supporto operativo. Per situazioni
complesse — in particolare studi medici, dentali, fisioterapici, o attività con trattamento
esteso di dati sanitari — si raccomanda la verifica da parte di un DPO o consulente
legale specializzato.

Riferimenti normativi: Regolamento UE 2016/679 (GDPR) | D.Lgs 196/2003 (Codice Privacy)
come modificato dal D.Lgs 101/2018 | Provvedimenti Garante Privacy (www.garanteprivacy.it)

Versione: [DATA]. Verificare eventuali aggiornamenti normativi sul sito del Garante.
```

---

## 4. EMAIL GATE — PRO/CONTRO

### Opzione A: Download diretto (no gate)
- Pro: frizione zero, massima conversion, genera goodwill
- Pro: la PMI NON si aspetta di "pagare con la mail" per materiale gratuito
- Contro: nessuna lista email, impossibile follow-up
- Contro: chi scarica senza convertire = lead perso

### Opzione B: Email gate (form minimo — solo email)
- Pro: qualificazione lead, lista email per follow-up automatico (es. "3 giorni dopo: come stai con il GDPR?")
- Pro: PMI che compila la mail è già più avanti nel funnel
- Contro: 30-50% drop (tipico per PDF lead magnet B2B Italia 2026)
- Contro: se il competitor offre lo stesso senza gate, perdi

### Raccomandazione FLUXION
**Opzione B con form minimo (solo email + nome attività)** — perché:
1. Il lead magnet GDPR è pre-acquisto, chi lo scarica è un potenziale cliente qualificato
2. L'email permette sequenza automatica: giorno 1 (template), giorno 4 (reminder GDPR), giorno 7 (offerta FLUXION)
3. Hosting CF Pages `/assets/gdpr/` con form → Cloudflare Workers → store email in KV (già infrastruttura esistente)
4. Alternativa zero-costo: Beehiiv o Mailchimp free tier per gestire la lista

**GDPR sul lead magnet stesso**: raccogliere email richiede informativa + checkbox consenso marketing. Usare testo: "Accetto di ricevere comunicazioni commerciali da FLUXION. Puoi annullare l'iscrizione in qualsiasi momento."

---

## 5. HOSTING E DIMENSIONI

### CF Pages `/assets/gdpr/`
- `informativa-privacy.docx`: ~50-80 KB (solo testo + placeholder)
- `registro-trattamenti.xlsx`: ~80-120 KB (tabella pre-compilata)
- `consenso-art9-sanitario.pdf`: ~150-200 KB (PDF compilabile)
- `guida-gdpr-pmi.html`: ~30-50 KB (HTML standalone)
- **Totale**: ~400-500 KB — ampiamente nel budget CF Pages (500MB free)

### Alternativa formato
- `.docx` vs `.odt`: .docx è standard de facto in Italia per PMI (Office prevalente)
- `.pdf` compilabile per il consenso: usa Adobe standard field, funziona su Preview/Adobe Reader
- `.xlsx` vs `.ods`: .xlsx preferito (Google Sheets lo apre, LibreOffice anche)
- `.html` standalone: nessun download aggiuntivo, apribile in browser, stampabile

### Generazione file senza costi
- `.docx`: python-docx (Python, gratis, generabile da script)
- `.xlsx`: openpyxl (Python, gratis)
- `.pdf` compilabile: reportlab (Python) o LibreOffice CLI con template ODT
- `.html`: scritto a mano — nessuna dipendenza

---

## 6. SARA (VOICE AGENT) — COME DICHIARARE NEL REGISTRO

### Classificazione corretta
**NON è**: profilazione (art. 4(4) GDPR — analisi sistematica per valutare aspetti personali)
**NON è**: decisione automatizzata con effetti giuridici (art. 22 — la prenotazione è confermata dall'operatore)
**È**: trattamento automatizzato strumentale all'erogazione del servizio

### Voce nel registro
```
Nome: Gestione prenotazioni telefoniche con assistente AI
Finalità: Ricezione e registrazione prenotazioni via telefono in assenza dell'operatore
Base giuridica: Art. 6(1)(b) — esecuzione del contratto di servizio con il cliente
Dati trattati: Audio chiamata (elaborazione real-time, non conservato) + testo prenotazione
                (nome, servizio, data, ora) conservato come prenotazione normale
Dati particolari (art. 9): No (Sara non raccoglie dati sanitari)
Destinatari: Nessuno — elaborazione locale/proxy; provider STT/LLM accedono a audio anonimizzato
             temporaneamente (Groq/Cerebras, USA, contratto con garanzie SCCs)
Extra-UE: Sì (provider STT/LLM USA) — solo per elaborazione, nessuna conservazione
Retention audio: Non conservato — eliminato dopo trascrizione (< 30 secondi)
Retention prenotazione: Come riga "Prenotazioni" (3 anni)
Misure sicurezza: TLS in transito, nessun dato biometrico, provider certificati
Disclosure: Il chiamante viene informato all'inizio della telefonata che la chiamata è
            gestita da un assistente AI (obbligo art. 13 GDPR)
Art. 22: NON applicabile — l'AI non prende decisioni definitive; la prenotazione entra in
         agenda e l'operatore ha pieno controllo
```

### Gestionale on-premise — impatto sul registro
- Tutti i dati a riposo: sul PC del titolare (no cloud)
- Cambia il rischio nella sezione sicurezza: "furto fisico del PC" è la minaccia principale
- Misure adeguate: cifratura disco (FileVault macOS / BitLocker Windows), password BIOS, backup criptato
- NON ci sono trasferimenti extra-UE per i dati a riposo
- Il registro deve esplicitare: "Software gestionale installato localmente sul PC della struttura"

---

## 7. CINQUE ERRORI GDPR COMUNI PMI ITALIANA 2026

**Errore 1 — Nessun registro trattamenti "tanto siamo piccoli"**
- Mito: solo le grandi aziende devono tenere il registro
- Realtà: qualsiasi attività con clienti ricorrenti e/o dati sanitari ha l'obbligo (Garante FAQ 9047529)
- Rischio: sanzione fino a €10M o 2% fatturato (art. 83(4) GDPR)

**Errore 2 — Consenso generico per tutto ("acconsento al trattamento dei miei dati")**
- Mito: un consenso jolly copre tutto
- Realtà: il consenso deve essere specifico per finalità, informato, inequivocabile; per dati sanitari deve essere ESPLICITO (art. 9(2)(a))
- Rischio: il consenso generico è nullo — tutti i trattamenti basati su di esso sono illeciti

**Errore 3 — WhatsApp per marketing senza consenso**
- Mito: posso mandare promozioni su WhatsApp perché il cliente mi ha dato il numero
- Realtà: il numero dato per prenotare NON autorizza comunicazioni commerciali — serve consenso separato e specifico
- Rischio: segnalazione Garante, sanzione, danni reputazionali

**Errore 4 — Nessuna procedura per data breach**
- Mito: "non mi capiterà mai" / "non so cosa fare quindi aspetto"
- Realtà: PC rubato, ransomware, dipendente che accede ai dati di un ex — sono data breach. Notifica Garante entro 72h è obbligatoria (art. 33)
- Rischio: la mancata notifica è sanzionata separatamente dal breach stesso

**Errore 5 — Conservare dati dei clienti per sempre "per sicurezza"**
- Mito: meglio tenere tutto, non si sa mai
- Realtà: il principio di "limitazione della conservazione" (art. 5(1)(e)) vieta di conservare dati oltre il necessario
- Realtà pratica: dopo 7 anni dall'ultima prestazione, l'anagrafica del cliente va anonimizzata
- Rischio: in caso di ispezione, avere dati di clienti del 2010 senza giustificazione è una violazione

---

## 8. FONTI UFFICIALI VERIFICATE

### Normativa primaria
- **GDPR completo in italiano**: https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:32016R0679
  - Art. 9 (categorie particolari), Art. 13 (informativa), Art. 22 (decisioni automatizzate), Art. 30 (registro), Art. 33 (data breach), Art. 37 (DPO)
- **D.Lgs 196/2003 come modificato da D.Lgs 101/2018 (Codice Privacy)**: https://www.garanteprivacy.it/codice-privacy

### Provvedimenti Garante rilevanti
- **FAQ Registro attività di trattamento** (doc. 9047529, 08/10/2018): conferma obbligo PMI con dati non occasionali
  URL: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9047529
- **Chiarimenti trattamento dati sanitari** (doc. 9091942, 07/03/2019): distinzione art. 9(2)(a) vs 9(2)(h), quando serve consenso esplicito
  URL: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9091942
- **Provvedimento cookie** (10/06/2021, doc. 9677876): requisiti cookie banner per siti web
- **Garante FAQ generali GDPR**: https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9081847

### Per DPA sub-processori FLUXION
- **Groq Privacy/DPA**: https://groq.com/privacy-policy/ (verifica SCCs per trasferimento USA)
- **Meta/WhatsApp DPA**: https://www.whatsapp.com/legal/business-data-processing-terms/it/
- **Cloudflare DPA**: https://www.cloudflare.com/cloudflare-customer-dpa/ (già GDPR compliant)
- **Stripe DPA**: https://stripe.com/it/legal/dpa

---

## 9. NOTE IMPLEMENTATIVE FLUXION

### Priorità di produzione
1. `guida-gdpr-pmi.html` — più valore percepito, nessun software necessario, si fa in 4h
2. `informativa-privacy.docx` — template più cercato, 2h
3. `registro-trattamenti.xlsx` — 3h con tutte le righe pre-compilate
4. `consenso-art9-sanitario.pdf` — solo per verticali sanitari, 2h

### Claim landing coerente con i template
Attuale: "30 minuti di compilazione e sei in regola" — MANTIENI ma aggiungi:
"Per attività standard senza dati sanitari. Per studi medici/dentali: consulta un DPO."
(Questo è già coperto dal footnote corrente — coerente.)

### Integrazione con FLUXION audit trail
Il template 2 (registro) può fare riferimento esplicito a FLUXION come misura tecnica:
"FLUXION gestionale registra automaticamente accessi, modifiche e cancellazioni dati (audit log)
conforme art. 30 GDPR — disponibile su richiesta del Garante."
Questo è un differenziatore di prodotto concreto.

### Cosa NON promettere
- NON "questi template ti rendono GDPR compliant" — la compliance richiede adempimenti comportamentali
- NON "sostituiscono un DPO" — per studi sanitari il DPO è fortemente raccomandato
- SÌ "riducono il tempo di adeguamento da settimane a 30 minuti per PMI standard"
