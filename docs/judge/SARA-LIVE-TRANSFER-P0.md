# SARA LIVE CALL TRANSFER — P0 PRODUCTION CONTRACT

**Stato:** BLOCCANTE per `U9 PRIMO CLIENTE PAGANTE`.

**Scopo:** quando Sara non riesce a risolvere in modo affidabile una chiamata, oppure il cliente chiede esplicitamente una persona, la chiamata telefonica in corso deve poter essere trasferita realmente e automaticamente alla persona reperibile configurata in FLUXION: operatore oppure titolare.

Questo documento integra `docs/judge/SARA-WORLD-CLASS-PRODUCTION-GATE.md` ed è parte normativa di `U8A SARA-WORLD-CLASS-GATE`.

## 1. Regola prodotto

Sara non deve limitarsi a dire "la ricontatteranno", inviare soltanto una notifica WhatsApp o terminare la sessione quando è disponibile un destinatario live valido.

Se il canale corrente è una chiamata VoIP e il trasferimento è consentito/configurato, Sara deve:

1. rilevare la necessità di escalation;
2. determinare il destinatario reperibile dalla configurazione FLUXION;
3. informare il chiamante in modo naturale che sta passando la chiamata;
4. trasferire la chiamata in corso al numero mobile configurato della persona selezionata;
5. conservare e registrare il contesto dell'escalation;
6. usare fallback sicuri soltanto se il trasferimento live non è possibile o non riesce.

## 2. Trigger di escalation

Il trasferimento live può essere attivato da almeno questi casi:

- richiesta esplicita: operatore, titolare, persona, essere umano, parlare con qualcuno;
- raggiungimento della soglia configurata `trasferisci_dopo_tentativi`;
- ripetuti fallimenti sullo stesso slot/stato senza progresso;
- frustrazione/escalation riconosciuta secondo le regole Sara;
- richiesta complessa o fuori perimetro che Sara non può risolvere senza inventare;
- errore operativo che impedisce di completare il task in sicurezza.

Una richiesta esplicita dell'utente non deve essere trattenuta artificialmente da tentativi aggiuntivi non necessari.

## 3. Routing dalla disponibilità configurata in FLUXION

La fonte di verità del destinatario non deve essere hardcoded nel voice agent.

FLUXION deve permettere di configurare, almeno:

- chi può ricevere escalation: `OPERATORE`, `TITOLARE`, oppure entrambi;
- numero di cellulare/reperibilità per ciascun destinatario abilitato;
- disponibilità/reperibilità della persona;
- priorità di routing quando più persone sono disponibili;
- soglia `trasferisci_dopo_tentativi`;
- numero di fallback generale (`numero_trasferimento`) quando previsto;
- comportamento fuori orario.

### Ordine di selezione richiesto

1. operatore marcato disponibile/reperibile per quella fascia, se abilitato al transfer;
2. altro operatore disponibile secondo priorità configurata;
3. titolare disponibile/reperibile;
4. `numero_trasferimento` generale configurato;
5. fallback asincrono solo se nessun destinatario live valido è disponibile.

La policy esatta può essere configurabile, ma la decisione runtime deve essere deterministica, auditabile e basata sui dati FLUXION correnti.

## 4. Configurazione software obbligatoria

Prima di U9 il gestionale deve esporre all'utente una UI chiara per configurare questa funzione. La sola presenza dei campi nel database non è sufficiente.

La UI deve consentire di vedere/modificare almeno:

- abilita/disabilita trasferimento automatico;
- numero cellulare di trasferimento/reperibilità;
- ruolo/destinatario (operatore o titolare);
- disponibilità/reperibilità;
- priorità se esistono più destinatari;
- numero tentativi prima del transfer automatico;
- fallback se nessuno risponde;
- comportamento fuori orario.

I campi già presenti `trasferisci_dopo_tentativi` e `numero_trasferimento` devono essere realmente utilizzati oppure sostituiti da una configurazione più strutturata con migrazione compatibile. Non devono restare dead configuration.

## 5. Trasferimento della chiamata

Il trasferimento deve essere un trasferimento della sessione telefonica corrente, non una semplice notifica.

Requisiti:

- la chiamata cliente resta attiva fino all'avvio del transfer;
- Sara riproduce una frase breve, ad esempio "Le passo subito Marco" oppure "La metto in contatto con il titolare";
- il motore VoIP esegue il meccanismo di transfer supportato dal trunk/stack in uso;
- il numero personale non viene letto al cliente salvo configurazione esplicita di fallback;
- il transfer non deve esporre credenziali SIP o dati privati nel transcript/log pubblico;
- in caso di fallimento tecnico la chiamata non deve cadere senza spiegazione.

## 6. Preservazione del contesto

Ogni escalation deve generare un record/payload con almeno:

- call/session id;
- timestamp;
- verticale;
- cliente e telefono se verificati;
- servizio;
- data/ora richieste;
- slot discussi;
- stato FSM;
- ultima intenzione;
- motivo escalation;
- numero/identità logica del destinatario selezionato;
- esito transfer: `CONNECTED`, `NO_ANSWER`, `BUSY`, `FAILED`, `NO_ROUTE`;
- booking status: confermato/non confermato/da richiamare.

Il destinatario deve poter ricevere il contesto senza costringere il cliente a ricominciare dall'inizio, per quanto consentito dall'interfaccia disponibile.

## 7. Fallback chain

Se il transfer live non riesce:

1. provare il successivo destinatario disponibile configurato, se previsto;
2. se nessun altro destinatario live è disponibile, Sara informa il cliente senza mentire;
3. creare callback/escalation con contesto;
4. inviare la notifica configurata (es. WhatsApp) al titolare/operatore;
5. soltanto se configurato, fornire il numero diretto pubblico.

Non è consentito chiudere la chiamata con una falsa affermazione tipo "la passo" se non è iniziato alcun transfer.

## 8. Privacy e sicurezza

- i numeri personali di reperibilità non devono comparire in UI non autorizzate, log pubblici o messaggi al cliente per default;
- il chiamante non può scegliere arbitrariamente un numero di destinazione;
- Sara può chiamare/trasferire solo verso destinatari salvati e abilitati in FLUXION;
- nessun numero proveniente dal testo pronunciato dall'utente può diventare destinazione del transfer;
- configurazione e modifica dei numeri seguono i permessi del gestionale;
- log e dossier devono mascherare il numero personale quando non necessario.

## 9. Acceptance test P0

Devono essere GREEN almeno questi casi:

1. richiesta esplicita "mi passi un operatore" → operatore disponibile → transfer effettuato;
2. richiesta esplicita "mi passi il titolare" → titolare disponibile → transfer effettuato;
3. raggiunti N tentativi configurati → auto-transfer al destinatario reperibile;
4. operatore A non disponibile, operatore B disponibile → B selezionato;
5. nessun operatore disponibile, titolare disponibile → titolare selezionato;
6. nessuno disponibile → nessun falso transfer, fallback con contesto;
7. destinatario BUSY → successivo route/fallback corretto;
8. destinatario NO_ANSWER → successivo route/fallback corretto;
9. transfer tecnico FAILED → Sara informa e conserva la chiamata abbastanza da offrire fallback;
10. fuori orario → routing conforme alla configurazione;
11. cambio disponibilità in FLUXION → la chiamata successiva usa la nuova configurazione senza hardcode;
12. numero personale non esposto al chiamante nei flussi normali;
13. input utente contenente un numero telefonico arbitrario non modifica il destinatario;
14. audit record contiene motivo, route ed esito senza secret SIP;
15. nessuna regressione di CERT-21, barge-in, disclosure AI e U3 latency gate.

## 10. Verdetto

Un prodotto in cui Sara "escalation" significa soltanto WhatsApp/callback non soddisfa questo requisito quando il live transfer è abilitato.

Prima di U9 deve essere dimostrato:

`SARA-LIVE-TRANSFER=GREEN`

con **P0 FAIL=0** sui casi sopra e con configurazione realmente accessibile dal software FLUXION.
