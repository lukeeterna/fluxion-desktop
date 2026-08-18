# SARA WORLD-CLASS PRODUCTION GATE v1

**Stato:** requisito di produzione FLUXION — da rendere GREEN prima di `U9 PRIMO CLIENTE PAGANTE`.

**Scopo:** trasformare la research interna sui migliori voice/AI assistant in criteri di accettazione falsificabili per Sara. Questo documento non sostituisce U1/U2/U3/U7/U8: li consolida e aggiunge i gap rimasti fuori dalla roadmap.

**Fonti interne principali:**
- `.claude/cache/agents/r2-world-class-benchmarks.md`
- ricerca F02/F02.1 su NLU e guardrail italiani
- ricerca interna su pattern conversazionali italiani e sub-verticali
- evidenze `STRESS-VERTICALI`, CERT-21 e test Sara già presenti nel repository

## 1. Principi non negoziabili

1. **FSM deterministica autorevole sui flussi transazionali.** Nome, cognome, telefono, servizio, data, ora, conferme, cancellazioni e spostamenti non devono dipendere da una generazione libera quando lo stato è già deterministico.
2. **LLM dove serve, non ovunque.** Il modello può interpretare linguaggio aperto, FAQ e richieste non strutturate; non deve duplicare o contraddire la state machine.
3. **Grounding verticale stretto.** Sara usa soltanto catalogo, KB, disponibilità, prezzi e regole del verticale/licenza attivi. Nessun dato di un altro verticale può contaminare la risposta.
4. **Mai inventare.** Nessun servizio, prezzo, durata, professionista, slot, policy, disponibilità o fatto aziendale può essere presentato come reale se non proviene da una fonte runtime/KB autorizzata.
5. **Fail closed sui booking.** In dubbio Sara chiarisce, propone una via sicura o passa il contesto al titolare; non conferma un appuntamento non dimostrato.
6. **Una conversazione, non un IVR.** Sara deve ricordare gli slot già raccolti, non ripetere domande inutili, accettare interruzioni e usare formulazioni naturali in italiano.
7. **Nessuna ottimizzazione di latenza può indebolire qualità o sicurezza.** Provider/model/timeout, guardrail e booking authority restano separati da questo gate salvo mandato esplicito.

## 2. Livelli di accettazione

### P0 — BLOCCANTE per U9

Un solo FAIL P0 mantiene `SARA-WORLD-CLASS-GATE=RED`.

- correttezza booking e assenza di conferme false;
- isolamento/grounding verticale;
- intenti critici e conferme implicite italiane;
- cancel/reschedule/special commands in qualunque stato attivo;
- disambiguazione senza loop;
- graceful degradation senza dead-end;
- barge-in/turn-taking;
- persistenza del contesto e handoff con contesto;
- fallback sicuro per servizi sconosciuti;
- latenza U3 senza regressioni;
- nessuna regressione della disclosure AI, escalation e guardrail esistenti.

### P1 — WORLD-CLASS QUALITY

Va implementato e misurato prima di U9; un risultato sotto target deve essere esplicitamente riportato nel dossier finale e non può essere nascosto da una media globale.

- riduzione dei turni per prenotazioni di clienti noti;
- proactive slot suggestion quando i dati sono verificati;
- naturalness e assenza di wording ridondante;
- qualità voce percepita e riduzione del dead-air;
- metriche per verticale, non solo aggregate.

## 3. Gate WC-01 — Grounding, isolamento verticale e anti-hallucination

### Requisiti

- Ogni sessione ha un solo verticale attivo e una sola KB/catalogo autorizzati.
- FAQ, servizi, prezzi, durate e policy devono essere risolti da fonti del verticale attivo.
- Un servizio appartenente a un altro verticale deve essere rifiutato o trattato come out-of-scope; non deve essere reinterpretato come servizio valido.
- Uno slot può essere proposto/confermato solo se prodotto dal checker di disponibilità o da una fonte equivalente autorizzata.
- Se la KB non contiene una risposta, Sara non improvvisa: dichiara il limite in modo naturale e offre raccolta nota/contatto.
- Nessun test può passare usando fixture di un verticale diverso da quello dichiarato.

### Test negativi minimi

- richiesta `gomme` su salone/parrucchiere;
- servizio estetica su officina e viceversa;
- FAQ non presente in KB;
- prezzo non presente;
- slot inesistente;
- cambio verticale tra due sessioni consecutive: zero leakage di catalogo/FAQ/cliente.

### Acceptance

- **Out-of-scope rejection >=95%** sul corpus congelato;
- **0 cross-vertical leakage** nei casi di isolamento;
- **0 servizi/prezzi/slot inventati** nei test P0.

## 4. Gate WC-02 — Intent routing italiano e NLU robusta

### Requisiti

- Intenti booking-critical: prenota, conferma, cancella, sposta, data, ora, servizio, nome/telefono.
- Verbi e forme flesse italiane devono essere coperti, non solo keyword nominali.
- Conferme implicite: `va bene`, `ok`, `perfetto`, `d'accordo`, `benissimo` e varianti equivalenti devono agire come conferma quando il contesto lo consente.
- Flexible scheduling: `la prima che avete`, `quando vi va`, `voi scegliete` e forme equivalenti non devono generare loop.
- Indirezione italiana: `magari un altro giorno` deve essere interpretata nel contesto corretto senza trasformarsi automaticamente in cancellazione.
- Ordine nome/cognome deve tollerare `Rossi, Marco`; nickname mapping già esistente non deve regredire.
- In stati FSM deterministici il primary LLM NLU non deve partire se il task è già posseduto dalla state machine; `IDLE` e `WAITING_SERVICE` mantengono il percorso LLM previsto dalla U3.

### Acceptance

- **Intent accuracy booking-critical >=98%** sul corpus congelato;
- **slot extraction data/ora >=98%**;
- **wrong booking confirmed <0.5%** sul corpus di errore/ambiguità;
- test specifici per `WAITING_DATE`, `CONFIRMING`, `REGISTERING_PHONE`, `IDLE`, `WAITING_SERVICE`, cancellazione e spostamento.

## 5. Gate WC-03 — Disambiguazione senza loop

### Requisiti

- Una ambiguità produce al massimo **una domanda di chiarimento specifica**.
- Sara non deve ripetere la stessa domanda in loop.
- Se il secondo tentativo resta incoerente, la FSM sceglie una delle sole uscite sicure: reset controllato del sottoflusso, domanda più semplice, oppure escalation/fallback.
- Slot già validi restano persistenti; non si riparte da zero salvo incoerenza reale.
- Correzioni esplicite dell'utente (`no, intendevo...`) sovrascrivono il valore precedente in modo deterministico.

### Test negativi minimi

- nome foneticamente ambiguo;
- servizio simile a due voci catalogo;
- data incoerente dopo correzione;
- due STT transcript consecutivi degradati;
- utente corregge nome/data/ora durante `CONFIRMING`.

### Acceptance

- **0 loop >1 chiarimento per la stessa ambiguità**;
- **0 ri-richieste di slot già confermati** senza causa esplicita.

## 6. Gate WC-04 — Graceful degradation e fallback

### Catena obbligatoria

1. primo errore/STT incerto: risposta naturale e specifica;
2. secondo errore: domanda semplificata, una sola informazione alla volta;
3. persistenza del problema: fallback sicuro con raccolta contatto/nota o canale WhatsApp previsto dal prodotto.

### Requisiti

- Mai chiudere con `non so`/dead-end quando è possibile prendere una nota o chiedere il recapito.
- Servizio sconosciuto: non inventare mapping; offrire nota al team/titolare.
- La degradazione non deve creare un booking parziale marcato come confermato.
- Il fallback conserva il contesto già raccolto per evitare che il cliente ripeta tutto.

### Acceptance

- ogni scenario degradato termina in `RECOVERED`, `SAFE_FALLBACK` o `ESCALATED_WITH_CONTEXT`;
- **0 dead-end** nei casi P0 previsti dal corpus.

## 7. Gate WC-05 — Handoff/escalation con contesto

### Requisiti

Quando Sara passa la richiesta al titolare/team deve produrre un payload strutturato minimo con:
- verticale;
- nome/telefono se verificati;
- servizio richiesto;
- data/ora richieste o slot già discussi;
- motivo dell'escalation;
- ultima intenzione dell'utente;
- stato booking (`non confermato`, `confermato`, `da richiamare`).

Il cliente non deve essere costretto a ricominciare da zero dopo l'handoff.

### Acceptance

- tutti i campi disponibili vengono preservati;
- nessun campo non verificato viene marcato come certo;
- nessun dato di un'altra sessione entra nel payload.

## 8. Gate WC-06 — Turn-taking e barge-in

### Requisiti

- VAD resta capace di rilevare l'utente durante l'output TTS secondo l'architettura certificata.
- Se l'utente interrompe per correggere o cambiare richiesta, TTS viene interrotto e il nuovo input viene processato.
- Nessuna risposta lunga deve impedire una correzione dell'utente.
- Reprompt, strike E6 e congedo onesto restano conformi a CERT-21.

### Acceptance

- test barge-in GREEN su almeno: correzione nome, correzione servizio, cancellazione durante proposta slot;
- **0 perdita del nuovo input** nei casi certificati;
- nessuna regressione di disclosure AI e chiusura chiamata.

## 9. Gate WC-07 — Minimo numero di turni e proactive slot suggestion

### Returning customer

Obiettivo world-class: **3-4 turni** quando identità, storico e servizio precedente sono verificati.

Pattern desiderato:
- identificazione cliente;
- conferma/riuso del servizio precedente solo se certo;
- proposta di 1-2 slot realmente disponibili;
- conferma finale.

### New customer

Obiettivo: **5-6 turni** nel percorso nominale, senza richiedere due volte lo stesso slot.

### Regole

- Proactive prefill mai basato su supposizioni: storico cliente e identità devono essere verificati.
- Se il cliente cambia servizio o preferenza, il percorso torna al punto minimo necessario, non al greeting.
- Una proposta di slot deve contenere solo disponibilità reale.

### Acceptance

- scenario nominale returning <=4 turni dopo identificazione verificata;
- scenario nominale new <=6 turni;
- nessuna riduzione dei turni ottenuta saltando conferme di sicurezza necessarie.

## 10. Gate WC-08 — Naturalness italiana

### Requisiti

- una domanda alla volta nei passaggi di raccolta dati;
- niente doppi prefissi empatici o formule ripetute meccanicamente;
- niente fraseologia da IVR (`premi`, menu numerici, istruzioni non naturali) nel dialogo vocale;
- mantenere il registro `Lei/tu` coerente con il verticale/configurazione senza rompersi se l'utente cambia registro;
- risposte brevi quando il task è deterministico; spiegazioni più estese solo per FAQ/consulenza;
- non rileggere l'intero riepilogo dopo ogni correzione: confermare soltanto il delta e riepilogare al momento corretto.

### Acceptance

- scorecard manuale/automatica senza: repetition loop, duplicate empathy, re-ask, robotic menu, cross-turn context loss;
- ogni FAIL deve riportare transcript e stato FSM.

## 11. Gate WC-09 — Latenza e fluidità

### Hard gate produzione

U3 resta autoritativa: **`FAIL=0 && P95<2000 ms`** sul test previsto dalla roadmap. Questo gate non può essere indebolito.

### Target world-class della research

- P50 end-to-end: target <700 ms, stretch ~500 ms;
- P95 end-to-end: target <1200 ms, world-class stretch <800 ms;
- evitare attese del full LLM response quando è tecnicamente sicuro usare streaming;
- connessioni persistenti/riuso client dove già supportato;
- TTS first-byte ottimizzato senza cambiare voce/prodotto senza mandato.

### Regole

- nessun tuning può cambiare provider/model/timeout o indebolire guardrail per ottenere un numero migliore senza task separato;
- metriche devono essere riportate per verticale e percentile, non solo media;
- ogni nuova capability WC deve dimostrare di non far regredire il P95 oltre la soglia U3.

## 12. Gate WC-10 — Copertura di tutti i verticali spediti

Il gate vale per **ogni verticale abilitato al primo rilascio commerciale**, non solo per il verticale usato durante lo sviluppo.

Per ogni verticale shipping devono esistere almeno:
- catalogo/KB caricabile;
- booking nominale;
- FAQ grounded;
- out-of-scope guardrail;
- servizio sconosciuto;
- cancellazione;
- spostamento;
- conferma implicita;
- ambiguous name/service;
- degraded STT/fallback;
- barge-in;
- latenza per percentile.

Qualunque verticale che non passa il gate deve essere **disabilitato dal packaging/licenza di produzione** oppure corretto prima di U9. Non può essere dichiarato supportato sulla base di test di un altro verticale.

## 13. Gate WC-11 — Evidenze e osservabilità di certificazione

Il dossier finale deve contenere almeno:
- commit esatto;
- elenco verticali shipping;
- corpus/versione test;
- scorecard per WC-01..WC-10;
- conteggi PASS/FAIL/WARN;
- intent accuracy e slot accuracy;
- wrong-confirmation rate;
- out-of-scope rejection rate;
- turn count returning/new;
- P50/P95 per verticale;
- transcript dei FAIL e degli edge-case principali;
- conferma che provider/model/timeouts, disclosure, escalation e wording protetto non siano stati cambiati fuori mandato;
- rollback per ogni mutazione di codice.

**WARN non può mascherare un P0 FAIL.**

## 14. Test matrix minima

Ogni verticale shipping deve eseguire almeno questi archetipi:

1. nuovo cliente — booking nominale;
2. cliente noto — booking come ultima volta;
3. conferma implicita (`va bene`/`perfetto`);
4. flexible scheduling;
5. cancellazione in stato attivo;
6. spostamento in stato attivo;
7. correzione nome;
8. correzione data/ora;
9. servizio sconosciuto;
10. richiesta out-of-scope;
11. FAQ presente;
12. FAQ assente;
13. STT degradato due volte;
14. barge-in durante TTS;
15. cross-vertical isolation;
16. slot non disponibile;
17. nessuna disponibilità;
18. escalation con contesto.

Il corpus deve usare formulazioni italiane variate, non una sola frase canonica per intent.

## 15. Ordine operativo rispetto alla roadmap

- **U1** continua a certificare contenuto verticale e diventa fonte primaria per WC-01/WC-10.
- **U2** resta autoritativa per comportamento live, barge-in, reprompt/E6 e congedo.
- **U3** resta autoritativa per hard gate latenza.
- **U4-U8** procedono nell'ordine già stabilito.
- **U8A SARA-WORLD-CLASS-GATE** esegue la certificazione completa WC-01..WC-11 e applica solo i fix necessari a chiudere i gap.
- **U9 PRIMO CLIENTE PAGANTE** è vietata se `SARA-WORLD-CLASS-GATE != GREEN`.

## 16. Cosa non fare

- non riaprire bug già falsificati senza nuova evidenza;
- non introdurre un nuovo intent classifier se esiste già un percorso autorevole;
- non usare il LLM per sostituire disponibilità/catalogo/booking state;
- non cambiare provider/model/timeout come scorciatoia;
- non dichiarare un verticale supportato se non è nel dossier GREEN;
- non trasformare P0 in post-lancio per rispettare una data;
- non confondere `CI green` con `Sara production-ready`: serve il dossier completo.

## 17. Verdetto

Il solo verdetto ammesso prima di U9 è:

`SARA-WORLD-CLASS-GATE=GREEN`

con **P0 FAIL=0**, evidenze complete e U3 ancora conforme a `FAIL=0 && P95<2000 ms`.
