# FLUXION — Piano Completo Video Tutorial
> Versione: 1.0 | Data: 2026-02-27
> Durata target: 12 minuti 30 secondi
> Obiettivo: utente autonomo dopo la visione, zero assistenza necessaria

---

## INDICE E TIMING GLOBALE

| Parte | Titolo                         | Inizio   | Fine     | Durata |
|-------|--------------------------------|----------|----------|--------|
| 0     | Intro + Titoli                 | 00:00    | 00:30    | 0:30   |
| 1     | Onboarding e Setup Wizard      | 00:30    | 02:30    | 2:00   |
| 2     | Gestione Quotidiana            | 02:30    | 06:30    | 4:00   |
| 3     | Sara — Voice Agent             | 06:30    | 09:30    | 3:00   |
| 4     | Verticali Specializzati        | 09:30    | 12:30    | 3:00   |
| 5     | Amministrazione                | 12:30    | 14:30    | 2:00   |
| 6     | Conclusione                    | 14:30    | 15:00    | 0:30   |

---

## PARTE 0 — INTRO (00:00 – 00:30)

### Timing dettagliato
- 00:00–00:05 — Logo FLUXION su sfondo navy, fade-in
- 00:05–00:20 — Titolo animato: "Benvenuto in FLUXION — Il gestionale che lavora per te"
- 00:20–00:30 — Sommario visuale: icone delle 6 sezioni principali appaiono in sequenza

### Script narrazione
> "Benvenuto in FLUXION. In questo tutorial imparerai tutto quello che ti serve per gestire la tua attività in autonomia: dal primo avvio fino alla fatturazione elettronica, passando per Sara, la tua assistente vocale che risponde ai clienti al posto tuo, ventiquattro ore su ventiquattro. Iniziamo."

### Scene / Screenshot necessari
- S0-A: Splash screen FLUXION (logo + tagline)
- S0-B: Grid animata con icone: Calendario, Clienti, Sara (microfono), Fatture, Verticale, Impostazioni

### Note didattiche
- Durata massima 30 secondi: non dilungarsi con credenziali o ringraziamenti
- Il tono deve essere pratico e diretto, non promozionale
- Usare musica di sottofondo leggera, volume 20%, che si abbassa durante la narrazione

---

## PARTE 1 — ONBOARDING E SETUP WIZARD (00:30 – 02:30)

### 1A — Primo avvio: Setup Wizard (00:30 – 01:20)

#### Timing dettagliato
- 00:30–00:40 — Schermata benvenuto Setup Wizard
- 00:40–00:55 — Step 1: scelta macro-categoria (beauty / medico / veicoli / sport)
- 00:55–01:05 — Step 2: scelta verticale specifico (es. Salone dentro beauty)
- 01:05–01:15 — Step 3: nome attività, partita IVA, regime fiscale
- 01:15–01:20 — Step 4: numero WhatsApp e numero Ehiweb (per Sara)

#### Script narrazione
> "Al primo avvio FLUXION ti guida attraverso sei semplici passaggi. Prima cosa: scegli la tua categoria. Se sei un salone o un barbiere, seleziona 'Beauty'. Se sei uno studio dentistico, seleziona 'Medico'. Ogni categoria attiva le schede cliente e i flussi di lavoro specifici per te."
>
> "Poi inserisci il nome della tua attività, la partita IVA e il regime fiscale. Questi dati verranno usati automaticamente sulle fatture. Infine, inserisci il numero WhatsApp Business e, se ce l'hai, il numero Ehiweb: Sara li userà per inviare le conferme di prenotazione ai tuoi clienti."

#### Scene / Screenshot necessari
- S1A-1: Schermata benvenuto wizard (step 1 di 6)
- S1A-2: Griglia selezione macro-categoria (4 opzioni con icone e colori)
- S1A-3: Selezione verticale (dropdown o tile con 6 opzioni)
- S1A-4: Form dati attività (nome, P.IVA, regime fiscale dropdown)
- S1A-5: Form numeri (WhatsApp, Ehiweb con spiegazione tooltip)

#### Note didattiche
- Evidenziare con cerchio rosso animato il campo "numero WhatsApp": errore comune e' inserire il numero personale invece del Business
- Spiegare che verticale si puo' cambiare in seguito dalle Impostazioni
- Il regime fiscale predefinito e' "Ordinario": ricordare che se si e' forfettari va cambiato

---

### 1B — Configurazione iniziale: Operatori e Servizi (01:20 – 02:30)

#### Timing dettagliato
- 01:20–01:35 — Aggiunta primo operatore (nome, orari, colore calendario)
- 01:35–01:50 — Aggiunta secondo operatore per mostrare multi-operatore
- 01:50–02:10 — Creazione primo servizio (nome, prezzo, durata in minuti, categoria)
- 02:10–02:30 — Creazione secondo e terzo servizio; overview lista servizi completata

#### Script narrazione
> "Adesso aggiungiamo il personale. Clicca su 'Operatori' nella barra laterale e poi su 'Nuovo Operatore'. Inserisci il nome, imposta gli orari di lavoro — che possono essere diversi da quelli dell'attività — e scegli un colore: ogni operatore apparira' nel calendario con il suo colore. Se lavori da solo, aggiungi solo te stesso."
>
> "Poi vai su 'Servizi'. Ogni servizio ha un nome, un prezzo e una durata in minuti. La durata e' fondamentale: e' quella che Sara usa per controllare la disponibilita' del calendario. Se un taglio dura 45 minuti, Sara non prendera' mai due appuntamenti sovrapposti."

#### Scene / Screenshot necessari
- S1B-1: Pagina Operatori vuota con bottone "+ Nuovo Operatore"
- S1B-2: Dialog OperatoreDialog con campi compilati (nome: "Marco", colore selezionato: blu)
- S1B-3: Lista operatori con due operatori aggiunti
- S1B-4: Pagina Servizi vuota con bottone "+ Nuovo Servizio"
- S1B-5: Dialog ServizioDialog (nome: "Taglio Donna", prezzo: 35, durata: 45 min)
- S1B-6: Lista servizi con 3 servizi visibili (nome, prezzo, durata)

#### Note didattiche
- Errore comune: durata impostata a 0 o 1 — il sistema accetta prenotazioni ma il calendario va in conflitto
- Spiegare che il colore dell'operatore e' solo visivo, non cambia nulla funzionalmente
- Se si gestisce cassa, il prezzo del servizio viene riportato automaticamente nella fattura

---

## PARTE 2 — GESTIONE QUOTIDIANA (02:30 – 06:30)

### 2A — Dashboard: leggere i KPI (02:30 – 03:15)

#### Timing dettagliato
- 02:30–02:45 — Panoramica Dashboard con dati reali
- 02:45–03:00 — Spiegazione KPI: appuntamenti oggi, clienti totali, VIP, fatturato mese
- 03:00–03:10 — Lista appuntamenti del giorno (scrollabile)
- 03:10–03:15 — Link rapido al calendario dal pannello appuntamenti

#### Script narrazione
> "Ogni mattina apri FLUXION e la prima cosa che vedi e' la Dashboard. In alto hai i numeri chiave: quanti appuntamenti hai oggi, quanti clienti totali, quanti sono VIP — cioe' con piu' di cinque visite — e il fatturato del mese corrente. Questi dati si aggiornano ogni cinque minuti."
>
> "In basso vedi la lista degli appuntamenti di oggi, con nome cliente, servizio e orario. Clicca su un appuntamento per aprirlo direttamente nel calendario."

#### Scene / Screenshot necessari
- S2A-1: Dashboard completa con KPI cards (dati demo: 8 appuntamenti oggi, 127 clienti, €3.420 mese)
- S2A-2: Zoom sulle KPI cards con frecce esplicative per ogni metrica
- S2A-3: Lista appuntamenti del giorno con 5-6 righe visibili
- S2A-4: Click su un appuntamento che apre il calendario in quel giorno

#### Note didattiche
- Spiegare che "clienti VIP" non e' un giudizio soggettivo ma automatico dopo N visite
- Il fatturato mese conta solo fatture emesse, non appuntamenti completati: spiegare la distinzione

---

### 2B — Calendario: gestione appuntamenti (03:15 – 05:00)

#### Timing dettagliato
- 03:15–03:30 — Vista mensile del calendario, navigazione mesi
- 03:30–03:45 — Click su un giorno: apertura vista giornaliera con ore
- 03:45–04:05 — Creazione nuovo appuntamento (click su slot vuoto → dialog)
- 04:05–04:20 — Compilazione AppuntamentoDialog: cliente, servizio, operatore, data/ora
- 04:20–04:35 — Modifica appuntamento esistente (click → edit)
- 04:35–04:50 — Cambio stato appuntamento: Confermato → Completato → Annullato
- 04:50–05:00 — Doppio click su appuntamento occupato: dialog di override

#### Script narrazione
> "Il Calendario e' il cuore operativo di FLUXION. Dalla vista mensile vedi quanti appuntamenti hai ogni giorno con un punto colorato. Clicca su un giorno per entrare nella vista dettagliata dove vedi le ore."
>
> "Per creare un appuntamento, clicca su uno slot vuoto. Si apre un dialog: scegli il cliente dalla lista — o aggiungine uno al volo se e' nuovo — poi il servizio e l'operatore. FLUXION calcola automaticamente l'orario di fine in base alla durata del servizio, e ti avvisa se c'e' un conflitto."
>
> "Per modificare un appuntamento esistente, cliccaci sopra e poi su 'Modifica'. Puoi cambiare qualsiasi campo. Puoi anche segnare un appuntamento come 'Completato' quando il cliente ha finito, o 'Annullato' se disdice. Questi stati sono importanti per le statistiche e per la fatturazione."

#### Scene / Screenshot necessari
- S2B-1: Vista calendario mensile con punti colorati sui giorni
- S2B-2: Click su giorno con transizione alla vista giornaliera a ore (8:00-20:00)
- S2B-3: Click su slot 10:00 → AppuntamentoDialog aperto
- S2B-4: Dialog compilato (cliente: "Anna Bianchi", servizio: "Taglio Donna", operatore: "Marco", ora: 10:00)
- S2B-5: Conferma e appuntamento appare nel calendario (colore operatore)
- S2B-6: Click sull'appuntamento → menu con Modifica / Cambio stato / Elimina
- S2B-7: Dropdown stati: Prenotato / Confermato / Completato / Annullato / No-Show
- S2B-8: OverrideDialog quando si prova a prenotare su slot occupato

#### Note didattiche
- Errore comune: confondere "Completato" con "Fatturato" — sono cose diverse
- Il colore dell'appuntamento segue il colore dell'operatore, non del servizio
- "No-Show" e' importante: viene tracciato nelle statistiche cliente e puo' influenzare la priorita' in lista d'attesa
- Spiegare che Sara usa gli stessi slot del calendario: se un appuntamento esiste li', Sara non lo prenota

---

### 2C — Clienti: anagrafica e storico (05:00 – 06:30)

#### Timing dettagliato
- 05:00–05:15 — Pagina Clienti: lista con ricerca, filtri (VIP, consenso WhatsApp)
- 05:15–05:35 — Aggiunta nuovo cliente: form completo
- 05:35–05:55 — Scheda cliente: anagrafica, storico visite, loyalty points
- 05:55–06:10 — Campo "consenso WhatsApp": spiegazione GDPR
- 06:10–06:30 — Sistema Loyalty: timbri, soglie VIP, referral

#### Script narrazione
> "La sezione Clienti raccoglie tutte le anagrafiche. Puoi cercare per nome, cognome o telefono. Il filtro VIP ti mostra subito i tuoi clienti piu' fedeli. Per aggiungere un nuovo cliente, clicca su 'Nuovo Cliente' e compila il form: nome, cognome, telefono, e-mail se vuoi. Il telefono e' l'unico campo obbligatorio perche' Sara lo usa per inviare i messaggi WhatsApp."
>
> "Una volta creato il cliente, aprendo la scheda vedi tutto lo storico delle visite, con data, servizio e importo. Vedi anche i punti loyalty: ogni visita aggiunge un timbro. Raggiunte cinque visite, il cliente diventa automaticamente VIP e riceve trattamenti prioritari."
>
> "Attenzione al campo 'Consenso WhatsApp': va attivato solo se il cliente ha espresso il consenso scritto a ricevere messaggi promozionali. Sara puo' comunque inviare conferme di prenotazione anche senza consenso, perche' quelli sono messaggi di servizio, non promozionali."

#### Scene / Screenshot necessari
- S2C-1: Pagina Clienti con lista (8-10 righe), barra ricerca attiva con "Bian"
- S2C-2: Filtro VIP attivato: lista ridotta a clienti stelle
- S2C-3: Dialog "Nuovo Cliente" compilato (nome, cognome, telefono, email)
- S2C-4: Scheda cliente aperta: tab Anagrafica / Storico / Loyalty / Scheda Verticale
- S2C-5: Tab Storico con 5 visite elencate (data, servizio, operatore, importo)
- S2C-6: Tab Loyalty con barra progressione timbri (4/5 con indicatore VIP prossimo)
- S2C-7: Zoom su toggle "Consenso WhatsApp" con spiegazione

#### Note didattiche
- Il numero telefono deve essere nel formato internazionale per WhatsApp: +39 3XX XXX XXXX — mostrare l'esempio
- Errore comune: inserire il numero senza +39; Sara non riesce a inviare il messaggio
- La scheda verticale (tab "Scheda") cambia contenuto in base al tipo di attivita': lo vedranno nella Parte 4

---

## PARTE 3 — SARA, IL VOICE AGENT (06:30 – 09:30)

### 3A — Cos'e' Sara e come attivarla (06:30 – 07:00)

#### Timing dettagliato
- 06:30–06:45 — Pagina Voice Agent: spiegazione interfaccia
- 06:45–07:00 — Bottone "Avvia Pipeline": stato prima e dopo l'attivazione

#### Script narrazione
> "Sara e' la tua assistente vocale. Risponde alle chiamate dei tuoi clienti, prende le prenotazioni, le registra nel calendario e manda la conferma via WhatsApp — tutto in automatico, anche quando sei impegnato con un altro cliente, o di notte."
>
> "Per attivarla, vai su 'Voice Agent' nella barra laterale. Vedrai l'interfaccia di Sara con un grande pulsante 'Avvia Pipeline'. Cliccalo: il cerchio diventa verde e Sara e' online. Il sistema avviera' il motore vocale in background — ci vogliono pochi secondi la prima volta."

#### Scene / Screenshot necessari
- S3A-1: Pagina VoiceAgent con pipeline spenta (badge rosso "Offline")
- S3A-2: Click su "Avvia Pipeline" → animazione loading
- S3A-3: Pipeline attiva (badge verde "Online", indicatore microfono attivo)

#### Note didattiche
- Sara richiede che il voice agent sia in esecuzione sul PC — spiegare che il PC deve rimanere acceso
- Se si usa Sara per rispondere alle chiamate telefoniche, e' necessario configurare il numero Ehiweb dal setup wizard
- Il VAD (rilevatore di voce) e' automatico: Sara inizia ad ascoltare solo quando sente parlare, non registra in silenzio

---

### 3B — Demo chiamata completa (07:00 – 08:30)

#### Timing dettagliato
- 07:00–07:10 — Click "Saluta" per avviare la conversazione dimostrativa
- 07:10–07:25 — Sara risponde con il saluto personalizzato con nome attivita'
- 07:25–07:45 — Simulazione cliente: "Buongiorno, sono Anna Bianchi, vorrei prenotare un taglio"
- 07:45–08:00 — Sara identifica il cliente, propone slot disponibili
- 08:00–08:10 — Cliente sceglie: "Mercoledi' alle 10 va bene"
- 08:10–08:20 — Sara conferma, mostra il riepilogo
- 08:20–08:30 — Sara invia il messaggio WhatsApp di conferma e chiude la chiamata

#### Script narrazione
> "Vediamo Sara in azione. Nell'interfaccia puoi anche simulare una chiamata via testo — utile per testare prima di andare live. Clicca 'Saluta' per far partire Sara."
>
> "Sara risponde: 'Buongiorno, sono Sara di Salone Bella, come posso aiutarla?' — notate che usa il nome della vostra attivita' che avete inserito nel setup."
>
> "Scriviamo, o diciamo via microfono: 'Buongiorno, sono Anna Bianchi, vorrei prenotare un taglio'. Sara riconosce il nome nel database, trova che Anna e' una cliente fissa, e le propone i prossimi slot disponibili per il servizio 'Taglio Donna'."
>
> "Anna risponde che mercoledi' alle dieci va bene. Sara chiede conferma, poi registra l'appuntamento nel calendario — potete vederlo apparire in tempo reale — e invia automaticamente un messaggio WhatsApp ad Anna con tutti i dettagli. Il flusso e' completo: nessun intervento manuale necessario."

#### Scene / Screenshot necessari
- S3B-1: Interfaccia chat VoiceAgent con campo testo + bottone microfono
- S3B-2: Messaggio Sara in arrivo (bubble blu): testo saluto con nome attivita'
- S3B-3: Input utente: "Buongiorno, sono Anna Bianchi, vorrei prenotare un taglio"
- S3B-4: Risposta Sara con proposta slot (es. "Ho disponibile Mercoledi' 5 Marzo alle 10:00 con Marco. Le va bene?")
- S3B-5: Conferma utente: "Si', perfetto"
- S3B-6: Sara mostra riepilogo prenotazione
- S3B-7: Split screen: chat Sara a sinistra, Calendario a destra con appuntamento che appare
- S3B-8: Notifica WhatsApp inviata (badge verde con testo "Conferma inviata a +39 3XX...")

#### Note didattiche
- Mostrare sia input testuale che input vocale (bottone microfono)
- Spiegare che il microfono usa il VAD automatico: non serve tenere premuto nulla
- Enfatizzare che l'appuntamento appare nel calendario in tempo reale: e' il momento "wow" della demo
- Se il cliente non ha il consenso WhatsApp, Sara comunque conferma verbalmente ma non invia il messaggio

---

### 3C — Casi speciali: slot pieno, nuovo cliente, disambiguazione (08:30 – 09:30)

#### Timing dettagliato
- 08:30–08:50 — Caso 1: slot occupato → Sara propone lista d'attesa (waitlist)
- 08:50–09:10 — Caso 2: cliente nuovo → Sara raccoglie dati e crea anagrafica
- 09:10–09:30 — Caso 3: nome ambiguo → Sara chiede disambiguazione fonetica

#### Script narrazione
> "Sara gestisce anche i casi piu' complessi. Primo: se lo slot richiesto e' occupato, Sara non risponde 'non posso aiutarla'. Propone automaticamente il prossimo slot disponibile e, se il cliente non accetta, lo mette in lista d'attesa: appena si libera uno slot, Sara avvisa."
>
> "Secondo caso: un cliente nuovo che non e' nel database. Sara raccoglie nome, cognome e telefono durante la chiamata, crea l'anagrafica automaticamente e poi procede con la prenotazione. Il cliente viene registrato anche senza che voi tocchiate nulla."
>
> "Terzo caso: la disambiguazione. Se qualcuno dice 'Sono Gino Peruzzi' ma nel database c'e' 'Gigio Peruzzi', Sara non confonde i due: chiede 'Mi scusi, ha detto Gino o Gigio?' — cosi' la prenotazione va al cliente giusto. Questo evita errori di overbooking."

#### Scene / Screenshot necessari
- S3C-1: Chat: richiesta slot occupato → Sara risponde con slot alternativo
- S3C-2: Cliente dice "mettimi in lista d'attesa" → Sara conferma con badge "Waitlist salvata"
- S3C-3: Chat: "Buongiorno, sono Luigi Verdi" (nuovo) → Sara chiede telefono e cogn. in sequenza
- S3C-4: Pagina Clienti aperta in background: nuovo cliente "Luigi Verdi" appare nella lista
- S3C-5: Chat: "Sono Gino Peruzzi" → Sara risponde "Ha detto Gino o Gigio Peruzzi?"
- S3C-6: Risposta: "Gigio" → Sara conferma e procede con Gigio

#### Note didattiche
- La disambiguazione fonetica e' basata su similarita' Levenshtein: funziona anche per Maria/Mario, Luca/Laura
- La waitlist e' automatica ma va gestita manualmente: quando si libera uno slot, Sara non richiama in autonomia (spiegare come controllare la lista nella sezione appuntamenti)
- Nuovo cliente creato da Sara ha il numero telefono pre-compilato ma manca l'email: ricordare di completare l'anagrafica dopo

---

## PARTE 4 — VERTICALI SPECIALIZZATI (09:30 – 12:30)

> Ritmo: 30 secondi di narrazione + 30 secondi di schermata per ogni verticale.

### 4A — Salone / Barbiere (09:30 – 10:00)

#### Timing dettagliato
- 09:30–09:45 — Apri scheda cliente → tab "Scheda Salone"
- 09:45–10:00 — Mostrare: storico colorazioni, note capello, prodotti usati

#### Script narrazione
> "Se hai scelto il verticale Salone o Barbiere, nella scheda di ogni cliente trovi una tab 'Scheda'. Qui puoi registrare il tipo di capello, le preferenze di taglio, e soprattutto lo storico delle colorazioni con formula, ossidante e marca. La prossima volta che la cliente viene, sai esattamente cosa le hai fatto sei mesi fa senza dover cercare foglietti."

#### Scene / Screenshot necessari
- S4A-1: Scheda cliente → tab "Scheda" con sezione Salone (tipo capello: ricci, colore naturale: castano)
- S4A-2: Sezione storico colorazioni: tabella con date, formula (es. "7.3 + 6% ossidante 30ml"), marca
- S4A-3: Campo "Preferenze" con note libere del parrucchiere

#### Note didattiche
- I campi sono a testo libero: non ci sono vincoli sulla formula — ognuno usa il proprio metodo
- Lo storico non ha limite di voci: si accumulano nel tempo

---

### 4B — Palestra / Fitness (10:00 – 10:30)

#### Timing dettagliato
- 10:00–10:15 — Scheda Fitness: abbonamento attivo, scadenza, misurazioni
- 10:15–10:30 — Schede allenamento: piano settimanale, progressione pesi

#### Script narrazione
> "Per palestre e centri fitness, la scheda cliente tiene traccia dell'abbonamento attivo con data di scadenza — FLUXION puo' ricordartelo prima che scada. Poi hai le misurazioni corporee nel tempo: peso, percentuale grassa, circonferenze. E le schede allenamento: puoi creare piani settimanali con esercizi, serie, ripetizioni e carichi, e vedere la progressione nel tempo."

#### Scene / Screenshot necessari
- S4B-1: Scheda Fitness: sezione Abbonamento (tipo: mensile, scadenza: 15/03/2026, badge verde "Attivo")
- S4B-2: Grafico misurazioni corporee nel tempo (peso in kg su 6 mesi)
- S4B-3: Scheda allenamento: esercizi in tabella (Squat 4x10 80kg, Panca 3x8 60kg...)

#### Note didattiche
- La gestione abbonamenti non emette automaticamente una fattura: va fatto manualmente dalla sezione Fatture
- Le misurazioni vanno inserite a ogni sessione: il grafico aggiorna automaticamente

---

### 4C — Odontoiatria (10:30 – 11:00)

#### Timing dettagliato
- 10:30–10:45 — Odontogramma FDI interattivo: click su dente → cambio stato
- 10:45–11:00 — Anamnesi medica, trattamenti per dente nel tempo

#### Script narrazione
> "Per gli studi dentistici, FLUXION integra un odontogramma interattivo secondo la notazione internazionale FDI. Vedete i 32 denti disposti come in bocca: superiori e inferiori. Cliccate su un dente e potete impostarne lo stato: sano, otturato, devitalizzato, corona, impianto, mancante o con carie. Il colore cambia immediatamente per dare una mappa visiva rapida."
>
> "Sotto l'odontogramma trovate l'anamnesi medica — allergie, farmaci, condizioni — e lo storico dei trattamenti dente per dente: quando e' stata fatta l'otturazione, con quale materiale, chi ha operato."

#### Scene / Screenshot necessari
- S4C-1: Odontogramma completo visibile: 4 quadranti, denti colorati (verde sano, giallo otturato, rosso carie)
- S4C-2: Click su dente 36 → dropdown stati (sano/otturato/devitalizzato/corona/impianto/mancante/carie)
- S4C-3: Selezione "otturato" → dente diventa giallo, cambia la legenda
- S4C-4: Sezione Anamnesi: form con allergie (penicillina), farmaci (warfarin), note
- S4C-5: Storico trattamenti dente 36: "Otturazione composito 15/01/2026 — Dr. Martini"

#### Note didattiche
- La notazione FDI e' quella standard europea: denti da 11 a 48 (non quella americana Palmer)
- L'odontogramma non e' un referto medico legale: e' uno strumento operativo interno
- Segnalare allergie ai farmaci (penicillina, FANS) e' critico: enfatizzare questo campo

---

### 4D — Fisioterapia (11:00 – 11:30)

#### Timing dettagliato
- 11:00–11:15 — Scale di valutazione: VAS dolore slider, Oswestry Index
- 11:15–11:30 — Zone corporee cliccabili, piano riabilitativo con sedute

#### Script narrazione
> "Per i centri di fisioterapia, la scheda integra le scale di valutazione clinica standard. Lo slider VAS va da 0 a 10 per il dolore percepito. L'Oswestry Disability Index va da 0 a 100 per la disabilita' lombare. L'NDI per il collo. Ogni seduta si registra il valore: nel tempo si vede il grafico di miglioramento — una prova concreta per il paziente."
>
> "Potete anche selezionare le zone corporee coinvolte: cervicale, spalla, lombare, ginocchio. E creare il piano riabilitativo: numero di sedute, obiettivi, note per ogni seduta."

#### Scene / Screenshot necessari
- S4D-1: Scheda Fisioterapia — slider VAS a 7 (dolore rosso), Oswestry 45%
- S4D-2: Grafico VAS nel tempo (da 8 a 3 in 10 sedute — trend discendente positivo)
- S4D-3: Mappa zone corporee (silhouette umana con zone cliccabili evidenziate: lombare + ginocchio dx)
- S4D-4: Piano riabilitativo: tabella sedute (Seduta 1: stretching cervicale 20min, note)

#### Note didattiche
- I valori delle scale non vengono inviati al paziente: sono solo per uso interno del terapista
- SF-36 e' una scala lunga: ci vuole tempo per compilarla. Spiegare che e' opzionale
- Suggerire di compilare VAS a ogni seduta: e' il dato piu' semplice e piu' utile per i grafici

---

### 4E — Estetica (11:30 – 12:00)

#### Timing dettagliato
- 11:30–11:45 — Tipo pelle, obiettivi trattamento, allergie prodotti
- 11:45–12:00 — Storico prodotti usati, note per trattamento, metodo depilazione

#### Script narrazione
> "Per i centri estetici, la scheda tiene traccia del tipo di pelle della cliente — secca, mista, grassa, sensibile, normale — e degli obiettivi: dimagrimento, tonificazione, rilassamento. Importantissime le allergie: nickel, profumi, parabeni, siliconi. Salvare queste informazioni evita reazioni avverse."
>
> "Poi lo storico dei prodotti usati trattamento per trattamento: marca, nome prodotto, concentrazione se applicabile. E le note libere per ogni seduta: cosi' qualunque estetista dello staff che prende in carico la cliente sa esattamente cosa e' stato fatto."

#### Scene / Screenshot necessari
- S4E-1: Scheda Estetica — tipo pelle "mista" selezionato, obiettivi "tonificazione" + "anticellulite"
- S4E-2: Sezione Allergie: badge rossi per "nickel" e "profumi"
- S4E-3: Storico prodotti: tabella con data, prodotto, zona applicazione
- S4E-4: Campo metodo depilazione: "ceretta" selezionato

#### Note didattiche
- Le allergie vanno sempre controllate prima di ogni trattamento: FLUXION le mostra in evidenza nella scheda
- Il tipo di pelle puo' cambiare nel tempo: aggiornarlo periodicamente

---

### 4F — Officina / Meccanica (12:00 – 12:30)

#### Timing dettagliato
- 12:00–12:15 — Scheda veicolo del cliente: targa, marca, modello, anno, km
- 12:15–12:30 — Storico interventi: data, lavoro eseguito, ricambi usati, costo

#### Script narrazione
> "Per officine e carrozzerie, invece della scheda cliente si gestisce la scheda veicolo. A ogni cliente si associano uno o piu' veicoli: targa, marca, modello, anno di immatricolazione, chilometraggio attuale. La targa e' la chiave di ricerca: basta digitarla per trovare subito il veicolo."
>
> "Ogni intervento viene registrato con data, descrizione del lavoro, pezzi sostituiti e loro codice, e costo. Quando il cliente riporta l'auto, vedete in un secondo cosa e' stato fatto in precedenza: evita di rifare diagnosi gia' eseguite."

#### Scene / Screenshot necessari
- S4F-1: Scheda cliente con tab "Veicoli": lista con una Fiat 500 (EX123AB, 2019, 87.000 km)
- S4F-2: Dettaglio veicolo: dati tecnici + bottone "Nuovo Intervento"
- S4F-3: Storico interventi: tabella (data, descrizione, ricambi, costo) con 3-4 righe
- S4F-4: Form nuovo intervento: descrizione "Tagliando completo", ricambi "Filtro olio K&N", costo 180€

#### Note didattiche
- Se un cliente ha piu' veicoli (auto e moto), ognuno ha il suo storico separato
- Il chilometraggio va aggiornato a ogni intervento: serve per i promemoria tagliando
- I ricambi inseriti qui non si collegano automaticamente al magazzino (funzione futura)

---

## PARTE 5 — AMMINISTRAZIONE (12:30 – 14:30)

### 5A — Servizi e prezzi (12:30 – 13:00)

#### Timing dettagliato
- 12:30–12:45 — Modifica prezzo servizio esistente
- 12:45–13:00 — Disattivare un servizio vs. eliminarlo; categorie servizi

#### Script narrazione
> "Dalla sezione Servizi potete gestire il listino in qualsiasi momento. Per modificare un prezzo, cliccate sul servizio, cambiate il valore e salvate. Sara usera' immediatamente il nuovo prezzo nelle prenotazioni."
>
> "Una cosa importante: non eliminate mai un servizio che ha gia' appuntamenti storici. Usate invece il tasto 'Disattiva': il servizio scompare dal listino e Sara non lo propone piu', ma rimane nello storico dei vecchi appuntamenti. Cosi' le statistiche rimangono corrette."

#### Scene / Screenshot necessari
- S5A-1: Lista servizi con prezzi e durate
- S5A-2: Click "Modifica" su "Taglio Donna" → dialog con prezzo cambiato da 35 a 38 euro
- S5A-3: Toggle "Attivo/Disattivo" su un servizio → servizio scompare dalla lista attiva
- S5A-4: Mostrare che il servizio disattivato appare ancora nello storico appuntamenti

#### Note didattiche
- Errore comune: eliminare un servizio e poi notare che gli appuntamenti storici mostrano "servizio eliminato"
- I servizi si raggruppano per categoria: utile quando il listino e' lungo (es. odontoiatria con 20+ prestazioni)

---

### 5B — Fatturazione Elettronica (13:00 – 14:00)

#### Timing dettagliato
- 13:00–13:15 — Impostazioni fatturazione: dati fiscali, regime, causale
- 13:15–13:35 — Creazione nuova fattura da zero (o da appuntamento completato)
- 13:35–13:50 — Emissione fattura: cambio stato da Bozza a Emessa
- 13:50–14:00 — Download XML fattura elettronica + invio a SDI

#### Script narrazione
> "FLUXION genera fatture elettroniche in formato XML compatibile con il Sistema di Interscambio italiano. Prima di tutto, configurate le impostazioni di fatturazione: i dati dell'emittente vengono presi dal setup wizard, ma qui potete aggiungere la banca per il bonifico, la causale predefinita e il metodo di pagamento."
>
> "Per creare una fattura, cliccate su 'Nuova Fattura'. Selezionate il cliente, aggiungete le righe — servizio, quantita', prezzo unitario e aliquota IVA. Se avete completato degli appuntamenti oggi, potete importare direttamente le righe da li'. Salvate come bozza e controllate tutto."
>
> "Quando siete sicuri, cliccate 'Emetti'. La fattura prende il numero progressivo definitivo, lo stato diventa 'Emessa' e non si puo' piu' modificare — solo annullare con nota di credito. A questo punto cliccate 'Scarica XML' e inviate il file al vostro commercialista o caricatelo direttamente su SDI. FLUXION non invia automaticamente a SDI: questo e' un passaggio manuale per ora."

#### Scene / Screenshot necessari
- S5B-1: Pagina Impostazioni Fatturazione: form con IBAN, causale, metodo pagamento
- S5B-2: Pagina Fatture: lista con stati (Bozza / Emessa / Pagata)
- S5B-3: Click "+ Nuova Fattura" → FatturaDialog aperto
- S5B-4: Dialog compilato: cliente Anna Bianchi, riga "Taglio Donna" €38 + IVA 22%
- S5B-5: Bottone "Salva come bozza" → fattura appare in lista con badge grigio "Bozza"
- S5B-6: Click "Emetti" su fattura → dialog conferma → badge diventa verde "Emessa" con numero FT-2026-001
- S5B-7: Bottone "Scarica XML" → file .xml scaricato con nome fattura
- S5B-8: Apertura XML in editor di testo (30 righe visibili) per mostrare il formato corretto

#### Note didattiche
- Il numero fattura e' sequenziale e automatico: non modificarlo
- Se si emette una fattura sbagliata, non si puo' eliminarla: va annullata con nota di credito (mostrare il flusso)
- L'aliquota IVA predefinita e' 22%: i professionisti sanitari esenti IVA devono cambiarla a 0% (natura N4)
- Il commercialista di solito vuole il file XML: FLUXION lo genera nel formato ufficiale Agenzia Entrate

---

### 5C — Impostazioni Avanzate (14:00 – 14:30)

#### Timing dettagliato
- 14:00–14:10 — Orari di lavoro: apertura, chiusura, pausa pranzo, giorno di chiusura
- 14:10–14:20 — Festivi: aggiunta giorni di chiusura straordinaria
- 14:20–14:30 — Diagnostica: pannello stato componenti (DB, voice pipeline, WhatsApp)

#### Script narrazione
> "Nelle Impostazioni trovate gli orari di lavoro. Potete avere orari diversi per ogni giorno della settimana: ad esempio mercoledi' chiusura pomeriggio, sabato orario ridotto. FLUXION e Sara useranno questi orari per non proporre mai slot fuori dall'orario di apertura."
>
> "Potete anche aggiungere festivi straordinari: le ferie estive, Natale, la fiera locale. In quei giorni il calendario si chiude automaticamente e Sara risponde che l'attivita' e' chiusa."
>
> "In fondo alle Impostazioni c'e' il pannello Diagnostica. Vi mostra in verde o rosso lo stato di tutti i componenti: database, pipeline vocale, connessione WhatsApp. Se qualcosa non funziona, partite da qui per capire dove e' il problema."

#### Scene / Screenshot necessari
- S5C-1: Pagina Impostazioni: sezione Orari di Lavoro con tabella giorni e orari
- S5C-2: Dialog aggiungi orario: giorno lunedi', 09:00-13:00 e 15:00-19:00, pausa 13:00-15:00
- S5C-3: Sezione Festivi: lista con Natale e Capodanno gia' presenti
- S5C-4: Aggiunta festivo straordinario: "Ferie agosto", dal 10/08 al 24/08
- S5C-5: Pannello Diagnostica: tutti i componenti verdi (DB Connected, Voice Online, WhatsApp OK)
- S5C-6: Pannello Diagnostica con Voice in rosso: messaggio di errore leggibile

#### Note didattiche
- Gli orari di lavoro influenzano anche Sara: se si imposta chiusura il lunedi', Sara non prenota il lunedi'
- I festivi nazionali (25 dicembre, 1 gennaio ecc.) NON sono pre-inseriti: vanno aggiunti manualmente
- Il pannello Diagnostica e' il primo posto dove guardare se Sara non risponde: spesso basta riavviare la pipeline

---

## PARTE 6 — CONCLUSIONE (14:30 – 15:00)

### Timing dettagliato
- 14:30–14:40 — Riepilogo visuale delle sezioni viste
- 14:40–14:50 — Dove trovare supporto: email, documentazione
- 14:50–15:00 — Aggiornamenti automatici: come funzionano

### Script narrazione
> "Eccoci alla fine del tutorial. Avete visto tutto quello che FLUXION fa per voi: il calendario intelligente, la gestione clienti con loyalty, Sara che prenota al posto vostro, le schede specializzate per il vostro settore, e la fatturazione elettronica certificata."
>
> "Se avete domande, trovate il manuale completo nel sito ufficiale FLUXION. Gli aggiornamenti sono automatici: FLUXION vi avvisa quando c'e' una nuova versione e la scarica in background. Non perdete mai i vostri dati: il database e' sul vostro computer, non su server terzi."
>
> "Buon lavoro con FLUXION."

### Scene / Screenshot necessari
- S6-1: Grid 2x3 con le 6 sezioni principali (icone + nome), fade-in uno alla volta
- S6-2: Schermata con email supporto e link documentazione
- S6-3: Dialog aggiornamento automatico (come appare quando esce una nuova versione)
- S6-4: Logo FLUXION finale con tagline e versione corrente

### Note didattiche
- Non terminare con "grazie per aver guardato": e' un tutorial professionale, non uno YouTube video
- La call-to-action finale deve essere concreta: "apri FLUXION e inizia", non generica

---

## APPENDICE A — CHECKLIST SCENE DA REGISTRARE

### Ordine di registrazione consigliato (per efficienza)
> Registrare prima tutte le scene che richiedono dati demo nel database, poi le scene di configurazione.

**Prerequisiti prima di registrare:**
- [ ] Database demo popolato con `scripts/seed_demo_data_v2.sql`
- [ ] Almeno 8 clienti con storico visite
- [ ] Almeno 10 appuntamenti: passati (completati) e futuri (prenotati/confermati)
- [ ] 3 operatori creati con colori diversi
- [ ] 5+ servizi con prezzi e durate realistici
- [ ] Voice pipeline attiva e funzionante
- [ ] Almeno 1 fattura in stato Bozza e 1 in stato Emessa

**Lista scene per numero:**
```
PARTE 0: S0-A, S0-B
PARTE 1: S1A-1..5, S1B-1..6
PARTE 2: S2A-1..4, S2B-1..8, S2C-1..7
PARTE 3: S3A-1..3, S3B-1..8, S3C-1..6
PARTE 4: S4A-1..3, S4B-1..3, S4C-1..5, S4D-1..4, S4E-1..4, S4F-1..4
PARTE 5: S5A-1..4, S5B-1..8, S5C-1..6
PARTE 6: S6-1..4
```
**Totale scene: 82**

---

## APPENDICE B — SPECIFICHE TECNICHE VIDEO

| Parametro        | Valore                      |
|------------------|-----------------------------|
| Risoluzione      | 1920x1080 (Full HD)         |
| Frame rate       | 30 fps                      |
| Formato output   | MP4 H.264                   |
| Audio narrazione | Mono 44.1kHz, -3dBFS        |
| Voce             | `say -v Alice` (macOS it_IT) o ElevenLabs |
| Font titoli      | `/System/Library/Fonts/Helvetica.ttc` |
| Colore sfondo    | `#0f172a` (navy FLUXION)    |
| Colore testo     | `#f8fafc` (bianco slate)    |
| Colore accent    | `#3b82f6` (blue-500)        |
| Musica sottofondo | Volume 15% durante narrazione, 30% nei titoli |
| Zoom UI          | Fattore 1.2x per sezioni con testo piccolo |
| Highlight click  | Cerchio giallo 40px animato sui click importanti |

---

## APPENDICE C — ERRORI COMUNI DA MOSTRARE (sezione "Cosa NON fare")

> Ogni errore va mostrato brevemente (3-4 secondi) con overlay rosso "ATTENZIONE", seguito dalla soluzione corretta.

| Errore | Sezione | Soluzione da mostrare |
|--------|---------|----------------------|
| Numero telefono senza +39 | 2C | Inserire +39 davanti |
| Durata servizio = 0 min | 1B | Minimo 15 minuti |
| Eliminare servizio con storico | 5A | Usare "Disattiva" |
| Emettere fattura senza controllare IVA | 5B | Controllare aliquota prima |
| Avviare Sara senza pipeline attiva | 3A | Cliccare "Avvia Pipeline" prima |

---

## APPENDICE D — SCRIPT AUDIO COMPLETO (pronto per TTS)

> Testo concatenato senza markup per passarlo direttamente a `say -v Alice` o ElevenLabs.
> Ogni paragrafo corrisponde a un segmento audio separato.

```
[INTRO]
Benvenuto in FLUXION. In questo tutorial imparerai tutto quello che ti serve per gestire la tua attività in autonomia: dal primo avvio fino alla fatturazione elettronica, passando per Sara, la tua assistente vocale che risponde ai clienti al posto tuo, ventiquattro ore su ventiquattro. Iniziamo.

[SETUP-1]
Al primo avvio FLUXION ti guida attraverso sei semplici passaggi. Prima cosa: scegli la tua categoria. Se sei un salone o un barbiere, seleziona Beauty. Se sei uno studio dentistico, seleziona Medico. Ogni categoria attiva le schede cliente e i flussi di lavoro specifici per te.

[SETUP-2]
Poi inserisci il nome della tua attività, la partita IVA e il regime fiscale. Questi dati verranno usati automaticamente sulle fatture. Infine, inserisci il numero WhatsApp Business e, se ce l'hai, il numero Ehiweb: Sara li userà per inviare le conferme di prenotazione ai tuoi clienti.

[OPERATORI]
Adesso aggiungiamo il personale. Clicca su Operatori nella barra laterale e poi su Nuovo Operatore. Inserisci il nome, imposta gli orari di lavoro — che possono essere diversi da quelli dell'attività — e scegli un colore: ogni operatore apparirà nel calendario con il suo colore. Se lavori da solo, aggiungi solo te stesso.

[SERVIZI]
Poi vai su Servizi. Ogni servizio ha un nome, un prezzo e una durata in minuti. La durata è fondamentale: è quella che Sara usa per controllare la disponibilità del calendario. Se un taglio dura 45 minuti, Sara non prenderà mai due appuntamenti sovrapposti.

[DASHBOARD]
Ogni mattina apri FLUXION e la prima cosa che vedi è la Dashboard. In alto hai i numeri chiave: quanti appuntamenti hai oggi, quanti clienti totali, quanti sono VIP — cioè con più di cinque visite — e il fatturato del mese corrente. Questi dati si aggiornano ogni cinque minuti. In basso vedi la lista degli appuntamenti di oggi, con nome cliente, servizio e orario. Clicca su un appuntamento per aprirlo direttamente nel calendario.

[CALENDARIO-1]
Il Calendario è il cuore operativo di FLUXION. Dalla vista mensile vedi quanti appuntamenti hai ogni giorno con un punto colorato. Clicca su un giorno per entrare nella vista dettagliata dove vedi le ore.

[CALENDARIO-2]
Per creare un appuntamento, clicca su uno slot vuoto. Si apre un dialog: scegli il cliente dalla lista — o aggiungine uno al volo se è nuovo — poi il servizio e l'operatore. FLUXION calcola automaticamente l'orario di fine in base alla durata del servizio, e ti avvisa se c'è un conflitto.

[CALENDARIO-3]
Per modificare un appuntamento esistente, cliccaci sopra e poi su Modifica. Puoi cambiare qualsiasi campo. Puoi anche segnare un appuntamento come Completato quando il cliente ha finito, o Annullato se disdice. Questi stati sono importanti per le statistiche e per la fatturazione.

[CLIENTI-1]
La sezione Clienti raccoglie tutte le anagrafiche. Puoi cercare per nome, cognome o telefono. Il filtro VIP ti mostra subito i tuoi clienti più fedeli. Per aggiungere un nuovo cliente, clicca su Nuovo Cliente e compila il form: nome, cognome, telefono, e-mail se vuoi. Il telefono è l'unico campo obbligatorio perché Sara lo usa per inviare i messaggi WhatsApp.

[CLIENTI-2]
Una volta creato il cliente, aprendo la scheda vedi tutto lo storico delle visite, con data, servizio e importo. Vedi anche i punti loyalty: ogni visita aggiunge un timbro. Raggiunte cinque visite, il cliente diventa automaticamente VIP e riceve trattamenti prioritari.

[CLIENTI-3]
Attenzione al campo Consenso WhatsApp: va attivato solo se il cliente ha espresso il consenso scritto a ricevere messaggi promozionali. Sara può comunque inviare conferme di prenotazione anche senza consenso, perché quelli sono messaggi di servizio, non promozionali.

[SARA-INTRO]
Sara è la tua assistente vocale. Risponde alle chiamate dei tuoi clienti, prende le prenotazioni, le registra nel calendario e manda la conferma via WhatsApp — tutto in automatico, anche quando sei impegnato con un altro cliente, o di notte. Per attivarla, vai su Voice Agent nella barra laterale. Vedrai l'interfaccia di Sara con un grande pulsante Avvia Pipeline. Cliccalo: il cerchio diventa verde e Sara è online.

[SARA-DEMO]
Vediamo Sara in azione. Nell'interfaccia puoi anche simulare una chiamata via testo — utile per testare prima di andare live. Clicca Saluta per far partire Sara.

Sara risponde: Buongiorno, sono Sara di Salone Bella, come posso aiutarla? — notate che usa il nome della vostra attività che avete inserito nel setup.

Scriviamo, o diciamo via microfono: Buongiorno, sono Anna Bianchi, vorrei prenotare un taglio. Sara riconosce il nome nel database, trova che Anna è una cliente fissa, e le propone i prossimi slot disponibili per il servizio Taglio Donna.

Anna risponde che mercoledì alle dieci va bene. Sara chiede conferma, poi registra l'appuntamento nel calendario — potete vederlo apparire in tempo reale — e invia automaticamente un messaggio WhatsApp ad Anna con tutti i dettagli. Il flusso è completo: nessun intervento manuale necessario.

[SARA-CASI]
Sara gestisce anche i casi più complessi. Primo: se lo slot richiesto è occupato, Sara non risponde non posso aiutarla. Propone automaticamente il prossimo slot disponibile e, se il cliente non accetta, lo mette in lista d'attesa: appena si libera uno slot, Sara avvisa.

Secondo caso: un cliente nuovo che non è nel database. Sara raccoglie nome, cognome e telefono durante la chiamata, crea l'anagrafica automaticamente e poi procede con la prenotazione. Il cliente viene registrato anche senza che voi tocchiate nulla.

Terzo caso: la disambiguazione. Se qualcuno dice Sono Gino Peruzzi ma nel database c'è Gigio Peruzzi, Sara non confonde i due: chiede Mi scusi, ha detto Gino o Gigio? — così la prenotazione va al cliente giusto.

[SALONE]
Se hai scelto il verticale Salone o Barbiere, nella scheda di ogni cliente trovi una tab Scheda. Qui puoi registrare il tipo di capello, le preferenze di taglio, e soprattutto lo storico delle colorazioni con formula, ossidante e marca. La prossima volta che la cliente viene, sai esattamente cosa le hai fatto sei mesi fa senza dover cercare foglietti.

[FITNESS]
Per palestre e centri fitness, la scheda cliente tiene traccia dell'abbonamento attivo con data di scadenza — FLUXION può ricordartelo prima che scada. Poi hai le misurazioni corporee nel tempo: peso, percentuale grassa, circonferenze. E le schede allenamento: puoi creare piani settimanali con esercizi, serie, ripetizioni e carichi, e vedere la progressione nel tempo.

[ODONTO]
Per gli studi dentistici, FLUXION integra un odontogramma interattivo secondo la notazione internazionale FDI. Vedete i 32 denti disposti come in bocca: superiori e inferiori. Cliccate su un dente e potete impostarne lo stato: sano, otturato, devitalizzato, corona, impianto, mancante o con carie. Sotto l'odontogramma trovate l'anamnesi medica — allergie, farmaci, condizioni — e lo storico dei trattamenti dente per dente.

[FISIO]
Per i centri di fisioterapia, la scheda integra le scale di valutazione clinica standard. Lo slider VAS va da 0 a 10 per il dolore percepito. L'Oswestry Disability Index va da 0 a 100 per la disabilità lombare. Ogni seduta si registra il valore: nel tempo si vede il grafico di miglioramento — una prova concreta per il paziente.

[ESTETICA]
Per i centri estetici, la scheda tiene traccia del tipo di pelle della cliente — secca, mista, grassa, sensibile, normale — e degli obiettivi: dimagrimento, tonificazione, rilassamento. Importantissime le allergie: nickel, profumi, parabeni, siliconi. Salvare queste informazioni evita reazioni avverse.

[OFFICINA]
Per officine e carrozzerie, invece della scheda cliente si gestisce la scheda veicolo. A ogni cliente si associano uno o più veicoli: targa, marca, modello, anno di immatricolazione, chilometraggio attuale. La targa è la chiave di ricerca: basta digitarla per trovare subito il veicolo.

[SERVIZI-ADMIN]
Dalla sezione Servizi potete gestire il listino in qualsiasi momento. Per modificare un prezzo, cliccate sul servizio, cambiate il valore e salvate. Sara userà immediatamente il nuovo prezzo nelle prenotazioni. Una cosa importante: non eliminate mai un servizio che ha già appuntamenti storici. Usate invece il tasto Disattiva.

[FATTURE-1]
FLUXION genera fatture elettroniche in formato XML compatibile con il Sistema di Interscambio italiano. Prima di tutto, configurate le impostazioni di fatturazione: i dati dell'emittente vengono presi dal setup wizard, ma qui potete aggiungere la banca per il bonifico, la causale predefinita e il metodo di pagamento.

[FATTURE-2]
Per creare una fattura, cliccate su Nuova Fattura. Selezionate il cliente, aggiungete le righe — servizio, quantità, prezzo unitario e aliquota IVA. Se avete completato degli appuntamenti oggi, potete importare direttamente le righe da lì. Salvate come bozza e controllate tutto.

[FATTURE-3]
Quando siete sicuri, cliccate Emetti. La fattura prende il numero progressivo definitivo, lo stato diventa Emessa e non si può più modificare — solo annullare con nota di credito. A questo punto cliccate Scarica XML e inviate il file al vostro commercialista o caricatelo direttamente su SDI.

[IMPOSTAZIONI]
Nelle Impostazioni trovate gli orari di lavoro. Potete avere orari diversi per ogni giorno della settimana. FLUXION e Sara useranno questi orari per non proporre mai slot fuori dall'orario di apertura. Potete anche aggiungere festivi straordinari: le ferie estive, Natale, la fiera locale. In quei giorni il calendario si chiude automaticamente e Sara risponde che l'attività è chiusa.

[DIAGNOSTICA]
In fondo alle Impostazioni c'è il pannello Diagnostica. Vi mostra in verde o rosso lo stato di tutti i componenti: database, pipeline vocale, connessione WhatsApp. Se qualcosa non funziona, partite da qui per capire dove è il problema.

[CONCLUSIONE]
Eccoci alla fine del tutorial. Avete visto tutto quello che FLUXION fa per voi: il calendario intelligente, la gestione clienti con loyalty, Sara che prenota al posto vostro, le schede specializzate per il vostro settore, e la fatturazione elettronica certificata. Se avete domande, trovate il manuale completo nel sito ufficiale FLUXION. Gli aggiornamenti sono automatici: FLUXION vi avvisa quando c'è una nuova versione e la scarica in background. Non perdete mai i vostri dati: il database è sul vostro computer, non su server terzi. Buon lavoro con FLUXION.
```

---

*Fine TUTORIAL_PLAN.md — 82 scene, 15 minuti, script TTS completo*
