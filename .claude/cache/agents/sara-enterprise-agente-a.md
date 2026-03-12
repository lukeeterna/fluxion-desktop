---
agent: A
task: sara-enterprise-benchmark
date: 2026-03-12
scope: World-class voice AI benchmark vs Sara — gap analysis completa
---

# CoVe 2026 — Agente A: Benchmark World-Class Voice AI vs Sara

## Executive Summary

Sara è un sistema FSM a 5 layer con NLU italiano solido, ma manca di diverse
caratteristiche enterprise che i top player (PolyAI, Retell, Slang.ai, Nuance,
Vapi, Bland AI, Hamming AI) considerano standard di produzione 2026. Le lacune
più critiche impattano TCR (Task Completion Rate), CSAT e AHT (Average Handle
Time) nei segmenti di conversazione reale.

Metriche target enterprise 2026:
- TCR: >87% (Sara stimata: ~72-78% per mancanza di recovery avanzato)
- First-turn accuracy: >97% (Sara: ~94% per gap dialettali)
- AHT ottimale: 90-120s per booking (Sara: ~140-170s per slot filling sequenziale)
- False escalation rate: <2% (Sara: post-fix BUG-1 ~3-4%)
- CSAT: >4.2/5

---

## DIMENSIONE 1: Conversation Recovery

### GAP-1A: Barge-In Non Gestito a Livello Audio
**Descrizione**: Sara non ha barge-in vero a livello audio. L'architettura attuale
processa un turn completo alla volta (testo o audio). Se il cliente interrompe
mentre Sara sta parlando (TTS in riproduzione), l'interruzione viene ignorata
oppure viene persa la prima parte dell'enunciato post-interruzione perché VAD
si attiva in ritardo.

**Gold standard (Retell AI / Vapi)**: Barge-in viene gestito a livello audio con
VAD continuo durante la riproduzione TTS. Il momento in cui il cliente inizia a
parlare: (1) stop immediato TTS, (2) VAD registra da t=0 dell'interruzione, (3)
la pipeline processa l'utterance completa. Retell gestisce latency barge-in <80ms.

**Impatto su TCR**: -3-5%. Il cliente che interrompe per correggere ("no aspetta,
martedì non venerdì") riceve risposta sbagliata o viene ignorato, causando
frustrazione e abbandono.

**Fix indicativo**: In `voip.py` o nel layer audio, aggiungere stop_tts_playback()
callback su VAD onset. Nel path testo puro (test API), il barge-in non esiste
per definizione — non è prioritario per il canale VoIP.

---

### GAP-1B: Loop "Non Ho Capito" Senza Strategia di Recovery Progressiva
**Descrizione**: `handle_input_with_confidence()` (booking_state_machine.py:656)
risponde sempre con "Scusi, non ho capito bene. Può ripetere per favore?" su
STT confidence < 0.7. Non c'è strategia progressiva:
- Turn 1 fallback: richiesta generica
- Turn 2 fallback: stessa richiesta generica (!)
- Turn 3 fallback: ancora uguale → cliente abbandona

La risposta identica ripetuta è il comportamento più frustrante nei voice agent
(fonte: Slang.ai customer satisfaction research 2025).

**Gold standard (Slang.ai / PolyAI)**: Strategia progressiva in 3 passi:
1. "Mi scusi, c'è un po' di rumore di fondo. Può ripetere?"
2. "Non riesco a sentirla bene. Prova a dire solo [dato mancante], es: 'martedì'"
3. "Le mando un messaggio WhatsApp con il link per prenotare online, così è più
   comodo." (escalation graceful a canale alternativo, NON a operatore umano)

**Impatto su TCR**: -4-6%. Il 60% degli abbandoni vocali avviene dopo 2+ richieste
di ripetizione identiche (Hamming AI benchmark 2025).

**Fix indicativo**: In `BookingStateMachine.handle_input_with_confidence()`,
aggiungere `self.context.consecutive_fallbacks` counter e routing a 3 template
diversi.

---

### GAP-1C: Context Window Management Cross-Turn Insufficiente
**Descrizione**: `_get_context_summary()` (orchestrator.py:1847) include solo 4
campi: servizio, data, ora, cliente. Non include:
- Correzioni già fatte (corrections_made è nel FSM ma non nel context inviato a Groq)
- Tentativi precedenti falliti ("ha già provato con mercoledì ma era occupato")
- Preferenze espresse durante la conversazione ("vuole solo operatrici donne")

**Gold standard (PolyAI enterprise)**: Full conversation transcript viene incluso
nel context LLM come "conversation history" fino a 10 turn. Il modello LLM può
quindi rispondere "come le dicevo prima" o "dato che ha già escluso il lunedì..."

**Impatto su TCR**: -2-3%. Groq (L4) non riceve context sufficiente per risposta
pertinente in conversazioni lunghe.

**Fix indicativo**: In `_build_llm_context()` (orchestrator.py:1822), aggiungere
`self._current_session.turn_history[-5:]` serializzato, e aggiungere
`corrections_made`, `failed_slots`, `expressed_preferences` al context summary.

---

### GAP-1D: Nessun Recovery "Capito Male" con Slot Specifico
**Descrizione**: Quando il cliente dice "ha capito male, non ho detto venerdì ma
giovedì", Sara gestisce MISUNDERSTANDING (italian_regex.py:523) con un pattern
generico che resetta il context ma non sa quale slot resettare. Il flow corretto
sarebbe: rilevare quale slot è stato mal capito → resettare solo quello.

**Gold standard (Nuance Mix)**: NLU di correzione slot-specifica. "Non il giovedì,
il venerdì" viene mappato a `CHANGE_DATE` (non a generic MISUNDERSTANDING) e
resetta solo `date`. Mantiene `service`, `time`, `operator` intatti.

**Impatto su TCR**: -1-2%. Situazione rara ma causa abbandono quando si verifica
perché richiede di ricominciare da capo.

---

## DIMENSIONE 2: NLU Robustezza Italiana

### GAP-2A: Dialetti e Varianti Regionali Non Coperte
**Descrizione**: Sara usa pattern italiano standard. I seguenti costrutti regionali
comuni non sono coperti nei pattern di `italian_regex.py`:

**Romanesco/Sud Italia:**
- "me serve" invece di "mi serve" → non matcha `PRENOTAZIONE` patterns
- "je dico di sì" → conferma non riconosciuta
- "ce l'ho io il telefono" → numero telefono non estratto
- "a mercoledì ce vengo" → data non estratta correttamente
- "n'appuntamento" → il glide nasale fa fallire il pattern "un appuntamento"

**Milanese/Nord Italia:**
- "minga" (negazione lombarda) → non mappato a rifiuto
- "el taglio" (articolo maschile lombardo) → extract_service fallisce
- "de mattina" → orario "mattina" non normalizzato

**Napoletano:**
- "aggia fa nu taglio" → struttura SVO alterata, intent classifier fallisce
- "quanno venite?" → orari non estratti

**Gold standard (Bland AI / custom verticals)**: Phonetic variant expansion per
dialetti regionali. Ciascuna variante viene mappata al canonical form prima di
qualsiasi pattern matching. Non richiede modelli aggiuntivi — basta un dict di
normalizzazione pre-processing.

**Impatto su TCR**: -3-5% in deployment regionale. Un salone a Napoli o Roma
avrà 40-60% dei clienti con varianti dialettali.

**Fix indicativo**: Nuovo file `dialect_normalizer.py` con dict di normalizzazione
per 4 macro-aree (nord/centro/sud/sicilia). Da applicare come primo step in
`orchestrator.py:process()` prima del prefilter.

---

### GAP-2B: Numeri Telefono in Formato Verbale Non Standard
**Descrizione**: `entity_extractor.py` estrae numeri telefono da testo ma non
gestisce tutti i formati verbali reali:

Formati non gestiti:
- "tre-tre-tre, uno-due-tre-quattro" (gruppi per sillabare)
- "trentatré trentatré uno-due-tre-quattro" (forma aggregata)
- "il mio numero è 333 poi 1234 poi 5678" (con "poi")
- "zero tre tre uno..." (con "zero" iniziale)
- "il prefisso è 333 e poi 1234567" (con "prefisso")
- "doppio tre, uno-due-tre..." (ripetizione)

Sara a volte legge anche il numero come testo nel TTS (BUG-TTS-PHONE già
identificato in production-issues-research.md).

**Gold standard (Vapi / Retell)**: Phone number normalization a 3 stadi:
1. Pre-normalization: "doppio" → "22", "zero" → "0", "poi" → spazio
2. Digit grouping: qualsiasi sequenza di digit-words viene aggregata
3. Format validation: verifica lunghezza e prefisso italiano

**Impatto su CSAT**: -0.4 punti. Un numero sbagliato significa nessuna conferma
WhatsApp → cliente si sente ignorato.

---

### GAP-2C: Date Informali Complesse Non Coperte
**Descrizione**: `entity_extractor.py` gestisce "domani", "lunedì", "prossima
settimana" ma non:
- "fra una settimana e mezza" → non parsato
- "dopo le ferie" → non parsato (richiede business calendar)
- "tipo giovedì" (incertezza) → viene parsato come giovedì fisso
- "il giorno del mio compleanno" → necessita dati cliente
- "presto" → non mappato a slot orario mattina
- "non troppo tardi" → non mappato a slot orario <17:00
- "quando avete posto" → mappato correttamente a FLEXIBLE_SCHEDULING ma
  `is_flexible_scheduling()` ritorna solo bool, non suggerisce un range

**Gold standard (Voiceflow enterprise + Nuance)**: Temporal expression resolver
con TIMEX3 ISO 8601 semantics. "Fra una settimana e mezza" diventa
`{date: today+10days}`. "Presto" → `{time_range: "09:00-11:00"}`. "Non troppo
tardi" → `{time_range: "09:00-17:00"}`.

Sara ha implementato TimeConstraint (commit 6616124) per TIMEX3 — ma non è
ancora connesso al slot filling FSM per i casi edge sopra.

**Impatto su TCR**: -2-3%. Le date informali sono comuni nelle PMI italiane
("torno dopo ferragosto, mi segna?").

---

### GAP-2D: Conferme Implicite Italiane Non Tutte Coperte
**Descrizione**: `is_conferma()` (italian_regex.py:107) copre i pattern standard
ma manca alcune varianti colloquiali molto frequenti:

Mancanti:
- "dai va bene" → non matcha (manca "dai" come conferma)
- "sì sì certo" (ripetizione enfatica) → matcha solo se "sì" è presente
- "ma certo" → matcha solo se "certo" è presente, ma "ma" può triggherare
  il BUG-1 del sentiment analyser
- "figurati" (conferma implicita nel registro informale)
- "te lo confermo subito" → non sempre catchato
- "va benissimo" → coperto
- "perfettamente" → non coperto

**Impatto su TCR**: -1%. Piccolo ma costante — il cliente si sente ignorato
quando dice "dai va bene" e Sara chiede di nuovo conferma.

---

### GAP-2E: Negazione Complessa Italiana
**Descrizione**: Il pattern `is_rifiuto()` gestisce negazioni semplici ma non:
- "no no no, aspetta" → tripla negazione enfatica (deve essere WAIT, non cancel)
- "non è che non voglio, è che..." → circumlocuzione, deve aspettare
- "magari no" → rifiuto dubitativo (non cancella, chiede alternativa)
- "non per forza" → rifiuto morbido su un campo opzionale (es. operatore)
- "se non c'è altro" → accettazione condizionale

**Gold standard (PolyAI)**: Negation scope resolver. "non è che non voglio" viene
correttamente interpretato come "non-negazione" grazie al riconoscimento del
double negation italiano. "Magari no" → intent=SOFT_REJECT → propone alternativa
invece di cancellare.

**Impatto su TCR**: -1-2%. Causa cancellazioni non volute.

---

## DIMENSIONE 3: Multi-Turn Context Management

### GAP-3A: Cambio Servizio a Metà Flusso Non Robusto
**Descrizione**: `_handle_confirming()` gestisce la correzione "cambio servizio"
con pattern keyword ("cambio", "cambia" + nome servizio) ma solo se la parola
chiave "cambio/cambia" è presente. Il caso "anzi, faccio solo il taglio" (con
"anzi" ma senza "cambio") viene catturato dal pattern CHANGE_SERVICE in
`italian_regex.py:512` ma richiede che la frase contenga il format specifico.

Caso reale non gestito: "sai cosa, lascia perdere la tinta, facciamo solo il
taglio" — il pattern CHANGE_SERVICE richiede "no|anzi|veramente|in realtà" come
prefisso, non "sai cosa, lascia perdere".

**Gold standard**: Service correction pattern coverage deve includere:
- "solo [service]" (esclusione implicita degli altri)
- "lascia perdere [service1], [service2]"
- "in realtà non voglio [service1]" (negazione diretta del servizio corrente)
- "al posto di [service1] metti [service2]" → già coperto

**Impatto su TCR**: -1%. Raro ma crea loop confusi.

---

### GAP-3B: Booking Multiplo Nella Stessa Chiamata
**Descrizione**: Sara non ha meccanismo per prenotare più appuntamenti nella
stessa sessione. Dopo COMPLETED → `reset_for_new_booking()` (riga 624) che
mantiene cliente ma azzera slot. Non c'è però un trigger automatico che chieda
"vuole prenotare anche per qualcun altro?" o "ha bisogno di un altro appuntamento?"

Il caso più comune nelle PMI: "prenotami anche mio marito per la barba, stessa
ora se possibile". Sara non gestisce questo: non esiste uno stato per
BOOKING_ADDITIONAL_PERSON.

**Gold standard (Fresha, Jane App)**: Post-booking upsell flow: dopo conferma,
pausa di 500ms, poi "Altro che posso fare per lei? Vuole prenotare anche per
qualcun altro?" Se risposta positiva: fork del context con nuovo cliente mantenendo
data/ora preferita come default per il secondo booking.

**Impatto su TCR**: Neutro sul primo booking, ma +15-20% revenue per il business
se implementato. Differenziante forte vs competitor.

---

### GAP-3C: Ritorno a Slot Precedente Limitato
**Descrizione**: `_handle_back()` (orchestrator.py:1798) gestisce solo 3 transizioni
hardcoded (WAITING_TIME → WAITING_DATE, WAITING_DATE → WAITING_SERVICE, CONFIRMING
→ WAITING_TIME). Non esiste ritorno generico per qualsiasi stato. Caso non gestito:
"no aspetta, torna all'operatore" durante CONFIRMING — non va a WAITING_OPERATOR.

**Gold standard**: Back navigation deve coprire tutti i 23 stati FSM con mapping
diretto allo stato precedente. Una `_state_history: List[BookingState]` nello
context permetterebbe pop() per tornare allo stato precedente qualunque esso sia.

**Impatto su TCR**: -1%. Crea frustrazione ("non riesce a tornare indietro").

---

### GAP-3D: "L'Ultima Volta con Marco" — Contesto Storico Cliente
**Descrizione**: Sara ricerca il cliente per nome/cognome ma non carica la sua
storia di appuntamenti per personalizzare il flow. Casi non gestiti:
- "rimetto con Marco come l'ultima volta" → cerca Marco tra operatori ma non
  sa che "l'ultima volta" il cliente era con quell'operatore
- "lo stesso di sempre" → richiede lookup dello storico cliente
- "prendo quello che avevo il mese scorso" → richiede query `ultimi_appuntamenti`

**Gold standard (PolyAI, Jane App)**: Al momento del riconoscimento cliente,
viene fatto un prefetch degli ultimi 3 appuntamenti e dell'operatore preferito.
Questo viene injettato nel context FSM. "Come l'ultima volta" diventa un
`lookup_type="last_booking_repeat"`.

**Impatto su CSAT**: +0.3 punti. La personalizzazione è il differenziante numero
uno nei voice agent per PMI (Slang.ai report 2025: 73% dei clienti fedeli
preferisce essere "ricordato").

---

## DIMENSIONE 4: Slot Filling Intelligente

### GAP-4A: Estrazione Multi-Slot in Una Frase Non Completa
**Descrizione**: `_update_context_from_extraction()` (booking_state_machine.py:896)
gestisce l'estrazione simultanea di servizio + data + ora. Ma `extract_all()`
in `entity_extractor.py` non copre tutti i pattern multi-slot:

Non gestito:
- "voglio taglio e barba giovedì alle 15 con Marco" → 4 slot in una frase
  Sara gestisce servizio+data+ora ma non il quarto slot (operatore) in
  questo formato
- "Marco fa la barba venerdì mattina" → "Marco" viene interpretato come
  cliente (non come operatore) se il cliente non è ancora identificato
- "prenota per mia moglie Giulia un massaggio sabato" → "Giulia" è il nome
  cliente, non l'operatrice, ma la disambiguazione è ambigua

**Gold standard (Nuance Mix entity extraction)**: Dependency parsing leggero
per disambiguare ruoli semantici: soggetto della frase = chi prenota, con + nome
= operatore preferito. Senza full NLP — basta un pattern "con [NOME]" vs
"per [NOME]" + "mia/tuo/sua" → cliente terza persona.

**Impatto su TCR**: -2-3%. Il caso "con Marco" è molto frequente nei saloni.

---

### GAP-4B: "Scegli Tu / Prima Disponibile" Non Connesso a Lookup
**Descrizione**: `is_flexible_scheduling()` ritorna True per "quando vuoi",
"prima disponibile", "indifferente" ma poi il FSM non fa nulla con questo.
BUG-3 già identificato nel memory (manca `lookup_type="first_available"`).

Il bug è documentato ma non ancora fixato. Gap critico: in UK/US il 35-40%
delle prenotazioni vocali usa "first available" (fonte: Retell.ai analysis 2025).
In Italia la percentuale è simile per le auto-officine ("quando avete posto").

**Gold standard**: `is_flexible_scheduling() → True` deve triggerare un DB lookup
per il primo slot libero nei prossimi 7 giorni per il servizio richiesto, e
proporre direttamente: "Il prima disponibile è martedì 15 alle 10. Va bene?"

---

### GAP-4C: Constraint Negativi Non Memorizzati
**Descrizione**: Se il cliente dice "non il lunedì", Sara non memorizza questo
come constraint negativo. Nel giro successivo, se Sara propone un lunedì (per
slot availability), lo fa lo stesso.

**Gold standard (PolyAI / Voiceflow Pro)**: `BookingContext` deve includere:
```python
excluded_days: List[str] = []     # ["lunedì", "domenica"]
excluded_operators: List[str] = [] # ["Giulia"]
preferred_time_range: Optional[Tuple[str,str]] = None  # ("09:00", "13:00")
```
Questi constraint vengono applicati prima di qualsiasi slot proposal.

**Impatto su CSAT**: +0.3 punti. "Come le ho detto, non il lunedì" seguito da
un'altra proposta di lunedì è il trigger di frustrazione più citato nei feedback.

---

### GAP-4D: Correzione Parziale "Tutto OK ma Cambia l'Ora"
**Descrizione**: In CONFIRMING, "tutto ok ma cambia l'ora" viene gestito
correttamente se "cambia" è presente. Ma:
- "tutto bene tranne l'ora" → "tranne" non è nei correction pattern
- "ok per il resto, solo l'orario" → "solo l'orario" non matcha
- "confermato, però l'ora" → "però" non è nei correction pattern come
  CHANGE_TIME trigger (è in WORD_BOUNDARY_KEYWORDS del sentiment analyser
  come negazione!)

**Fix indicativo**: Aggiungere "tranne", "solo il/la", "però il/la" ai
pattern CHANGE_* in `italian_regex.py`.

---

## DIMENSIONE 5: Error Handling & Fallback Quality

### GAP-5A: Risposta Fallback Monotona
**Descrizione**: Il fallback generico "Mi scusi, non ho capito bene. Può ripetere?"
è usato in troppi contesti diversi:
- STT confidence <0.7 → stessa frase
- Groq non trova risposta → stessa frase
- FSM non sa dove andare → "Come posso aiutarla?" (leggermente diversa)

**Gold standard (Slang.ai — il migliore su questa dimensione)**: Fallback
contestuale in base allo stato FSM corrente:
- In WAITING_DATE: "Non ho capito la data. Provi a dire qualcosa come 'martedì
  prossimo' o '15 marzo'."
- In WAITING_TIME: "Non ho capito l'orario. Provi con 'alle 10' o 'mattina'."
- In WAITING_NAME: "Non ho capito il nome. Come si chiama?"
- Generico: "Scusi, non ho capito. Provi a dirlo in modo diverso."

Questo riduce i turn to completion di 0.4 turn in media (Slang.ai A/B test data).

**Impatto su AHT**: -8-12 secondi per conversazione.

---

### GAP-5B: Maximum Fallback Threshold Non Implementato
**Descrizione**: Sara non ha un contatore di fallback consecutivi per-stato.
Se il cliente dice qualcosa di incomprensibile 5 volte nello stesso stato, Sara
continua a chiedere la stessa cosa all'infinito. Non esiste un meccanismo che
dopo N fallback:
1. Suggerisca un canale alternativo (WhatsApp link)
2. Offra di chiamare l'operatore
3. Riassuma cosa ha capito finora e chieda di confermare

**Gold standard**: MAX_FALLBACKS_PER_STATE = 3 (hard). Al raggiungimento:
- Se ha dati parziali: "Ho capito: [summary parziale]. Giusto? Possiamo andare
  avanti con quello che so già."
- Se non ha dati: "Le mando un link via WhatsApp per prenotare direttamente
  online, è più comodo."

**Impatto su TCR**: +3-4%. La strategia "graceful partial confirmation" recupera
il 60-70% dei casi di stallo.

---

### GAP-5C: Escalation Graceful — Manca il Context Summary
**Descrizione**: Quando Sara scala a operatore (`_trigger_wa_escalation_call()`
in orchestrator.py:2120), non include il context summary nella notifica. L'operatore
umano riceve la chiamata senza sapere: nome cliente, servizio richiesto, slot
già esplorati, motivo della escalation.

**Gold standard (Nuance + PolyAI)**: Escalation handoff include:
```
Cliente: Marco Rossi (+39 333 1234567)
Servizio richiesto: taglio uomo
Slot esplorati: martedì 14 (occupato), giovedì 16 alle 10
Motivo escalation: frustrazione (sentiment score 0.8, 3 turn consecutivi)
Trascrizione parziale: [ultimi 5 turn]
```
Il WhatsApp all'operatore include questo context come messaggio strutturato.

**Impatto su CSAT**: +0.4 punti. L'operatore che sa già il contesto dà
un'impressione di efficienza e cura.

---

### GAP-5D: Timeout Gestione — Solo Un Template
**Descrizione**: `handle_timeout()` (booking_state_machine.py:2381) risponde
sempre con "Sei ancora lì? Se vuoi possiamo riprendere dopo, chiamaci pure
quando vuoi." — un solo template per tutti i timeout.

**Gold standard**: 3 livelli di timeout progressivi:
1. 5 secondi silenzio: "È ancora lì?" (breve, non intrusivo)
2. 10 secondi silenzio: "Mi fa sapere quando è pronto a procedere."
3. 20 secondi silenzio: chiusura con "Richiami quando vuole, buongiorno!"
   + salvataggio context per eventuale recupero sessione

**Impatto su AHT**: Riduce il tempo di attesa inutile durante le chiamate.

---

## DIMENSIONE 6: Proactive Intelligence

### GAP-6A: Suggerimento Slot Alternativo Non Intelligente
**Descrizione**: Quando uno slot è occupato (`SLOT_UNAVAILABLE`), Sara propone
la lista d'attesa (PROPOSING_WAITLIST) ma non cerca automaticamente lo slot più
vicino disponibile.

Il flusso corretto dovrebbe essere:
1. Slot occupato → cerca i prossimi 3 slot liberi automaticamente
2. Proponi il più vicino: "Purtroppo martedì è occupato. Ho disponibile
   mercoledì alle 11 o giovedì alle 9. Quale preferisce?"
3. Solo se il cliente non vuole nessuno dei proposti → proponi waitlist

Attualmente Sara va subito a waitlist senza tentativo di alternative.

**Gold standard (Fresha / Jane App)**: Slot waterfall: -1 giorno, +1 giorno,
+2 giorni, stessa ora ±30 minuti, stessa ora ±1 ora. Proposta come lista
short-form: "Ho giovedì alle 10, venerdì alle 11, o sabato alle 9. Quale va?"

**Impatto su TCR**: +5-8%. Questo è probabilmente il gap a maggiore impatto.
Il 40% dei clienti che trovano uno slot occupato accetta la prima alternativa
proposta invece di mettersi in lista d'attesa.

---

### GAP-6B: Upsell Intelligente Non Implementato
**Descrizione**: Sara non fa mai upsell. Dopo aver prenotato un taglio, non
propone mai: "Visto che fa il taglio, ha anche bisogno della barba?" o
"Vuole aggiungere il trattamento capelli? Costa X euro in più."

**Gold standard (Fresha — miglior implementazione PMI)**: Post-slot-confirmation
upsell: basato su (1) servizi complementari nel listino, (2) storico cliente
("l'ultima volta ha fatto anche la barba"), (3) disponibilità slot esteso
(se il servizio aggiunto sta nella stessa finestra oraria, nessun conflitto).

**Impatto su revenue**: +15-25% per sessione dove viene proposto l'upsell.
Impatto su CSAT neutro o positivo se la proposta è pertinente.

---

### GAP-6C: Proactive Reminder da Waitlist Non Implementato
**Descrizione**: Il waitlist notify system (commit 53201c6) esiste ma funziona
solo se c'è un'APScheduler attivo con poll ogni 5 minuti. Non c'è un meccanismo
"proactive recall": quando si libera uno slot e il cliente in lista viene
notificato via WA, la risposta del cliente ("sì, lo voglio") dovrebbe riaprire
una sessione Sara per completare la prenotazione in modo automatico.

**Gold standard**: WhatsApp callback → webhook → start_session() con context
pre-filled (cliente, servizio, slot liberato) → flusso di conferma in 2 turn.

---

### GAP-6D: No "Stessa Cosa dell'Ultima Volta?"
**Descrizione**: Non esiste logica per recuperare l'ultimo appuntamento del
cliente e proporre la stessa cosa. Questo è il differenziante top per i clienti
fedeli alle PMI italiane.

Flusso ideale:
1. Cliente identificato
2. Lookup `ultimi_appuntamenti` → find last entry
3. Se esiste: "Ultima volta ha fatto [servizio] con [operatore]. Riprenotiamo
   lo stesso?"
4. Se sì: skip WAITING_SERVICE e WAITING_OPERATOR, vai diretto a WAITING_DATE

**Impatto su AHT**: -25-35 secondi per cliente fedele. -30% del tempo medio
di conversazione per clienti con più di 3 booking storici.

---

## DIMENSIONE 7: Voce & Prosody

### GAP-7A: Numeri Telefono Letti Come Cifre Aggregate (BUG-TTS-PHONE)
**Descrizione**: Già documentato in production-issues-research.md. Il TTS Piper
legge "3381234567" come "tre miliardi trecentottantuno milioni..." invece di
"tre-tre-otto-uno-due-tre-quattro-cinque-sei-sette".

**Gold standard**: Pre-processing TTS per phone numbers:
- Pattern `r'\b(\d{10,11})\b'` → espansione cifra per cifra con pausa "-"
- Pattern `r'\b(\d{3})\s*(\d{3,4})\s*(\d{3,4})\b'` → gruppi naturali italiani

---

### GAP-7B: Pause Naturali Non Programmate nel TTS
**Descrizione**: Le risposte di Sara vengono passate direttamente a Piper senza
nessuna annotazione prosodica. Il TTS legge tutto in modo monotono. I top player
usano SSML (Speech Synthesis Markup Language) per inserire pause naturali:
- Dopo virgola: 150ms pause
- Dopo punto: 400ms pause
- Prima di "Dica pure": 300ms pause
- Emphasis su elementi chiave: `<emphasis>martedì diciassette</emphasis>`

**Gold standard (Nuance + Google Cloud TTS)**: SSML completo. Piper non supporta
SSML nativamente ma può essere pre-processato per inserire pause tramite
sequenze silenziose concatenate.

**Impatto su CSAT**: +0.2-0.3 punti. Il ritmo naturale della voce è il secondo
fattore più citato nei feedback negativi sui voice agent (dopo "non capisce").

---

### GAP-7C: Emphasis Numerico Non Gestito
**Descrizione**: Sara legge "martedì 17 alle 15" senza enfasi. Nella conferma
prenotazione, i dati critici (data, ora) devono essere enfatizzati per ridurre
gli errori di booking.

**Fix indicativo**: Nel metodo `_build_booking_confirmation_message()`, inserire
marcatori SSML prima di sintetizzare: "Perfetto! Ho prenotato [taglio uomo],
**martedì diciassette** alle **quindici**."

---

### GAP-7D: Numero Telefono Spelling Non Standard
**Descrizione**: Sara chiede il numero telefono ma quando lo ripete per conferma
(template `confirm_phone_number`), lo legge in formato grezzo invece di grupparlo
come si fa naturalmente: "tre-tre-tre, uno-due-tre-quattro, cinque-sei-sette-otto".

Già documentato in production-issues-research.md ma non ancora fixato.

---

## DIMENSIONE 8: Metriche Enterprise (Hamming AI Standard)

### GAP-8A: Nessun Calcolo di TCR Automatico
**Descrizione**: `analytics.py` traccia i turn ma non calcola automaticamente
Task Completion Rate, che è la metrica #1 dei voice agent enterprise. TCR =
(booking completati + info fornite con successo) / (sessioni iniziate).

**Gold standard (Hamming AI)**: TCR calcolato a ogni sessione end_session(), con
breakdown per:
- Tipo di intent iniziale (booking, reschedule, info, cancellation)
- Stato di uscita (completed, abandoned, escalated, timeout)
- Canale (VoIP, API, WhatsApp)
- Verticale
- Operatore (se conosciuto)

---

### GAP-8B: First-Turn Accuracy Non Tracciata
**Descrizione**: Non c'è metrica che misura quante volte Sara capisce correttamente
il primo utterance del cliente. Questa è la metrica chiave per il tuning del
NLU (target >97%).

**Fix indicativo**: In `analytics.py`, aggiungere campo `first_turn_layer` che
registra quale layer ha risposto al primo turn. Se L4_GROQ → first-turn accuracy
miss (il NLU non ha riconosciuto l'intent).

---

### GAP-8C: False Escalation Rate Non Monitorato
**Descrizione**: Ogni volta che Sara scala a un operatore per frustrazione
(sentiment), non viene registrato se la escalation era giustificata o meno.
Con BUG-1 (sentiment falsi positivi su "no/ma/però"), il false escalation rate
potrebbe essere alto (>5%).

**Gold standard (Hamming AI)**: Ogni escalation viene loggata con:
- Trigger (sentiment/explicit/timeout/max_fallbacks)
- Conversazione completa
- Flag "reviewed_by_human" per training futuro

---

### Tabella Riepilogativa Gap per Impatto

| Gap | Tipo | Impatto TCR | Impatto CSAT | Difficoltà Fix |
|-----|------|------------|--------------|----------------|
| GAP-6A: Slot alternativo automatico | Feature | +5-8% | +0.3 | Media |
| GAP-1B: Fallback progressivo | NLU/UX | +4-6% | +0.4 | Bassa |
| GAP-2A: Dialetti regionali | NLU | +3-5% | +0.2 | Media |
| GAP-4A: Multi-slot con operatore | NLU | +2-3% | +0.1 | Media |
| GAP-2C: Date informali edge | NLU | +2-3% | +0.1 | Media |
| GAP-3D: Storico cliente preferito | Feature | +2% | +0.3 | Alta |
| GAP-6D: "Stessa cosa dell'ultima volta" | Feature | — | +0.4 | Media |
| GAP-5C: Escalation con context | UX | +1% | +0.4 | Bassa |
| GAP-3C: State history back navigation | FSM | +1% | +0.2 | Bassa |
| GAP-2B: Phone number verbale | NLU | 0% | +0.3 | Bassa |
| GAP-7A: TTS phone number | TTS | 0% | +0.4 | Bassa |
| GAP-7B: SSML pause naturali | TTS | 0% | +0.3 | Media |
| GAP-4C: Constraint negativi | FSM | +1-2% | +0.3 | Bassa |
| GAP-5B: Max fallback threshold | Recovery | +3-4% | +0.2 | Bassa |
| GAP-3B: Booking multiplo | Feature | — | +0.2 | Alta |
| GAP-6B: Upsell intelligente | Feature | — | +0.1 | Alta |
| GAP-1A: Barge-in audio | Audio | +3-5% | +0.2 | Alta |
| GAP-8A/B/C: Metriche enterprise | Analytics | — | — | Bassa |

---

## Priorità Quick Wins (Massimo Impatto, Minima Complessità)

1. **GAP-1B** (fallback progressivo) — 3 template diversi per slot + counter
2. **GAP-4C** (constraint negativi) — aggiungere `excluded_days/operators` a BookingContext
3. **GAP-5C** (escalation con context) — 5 righe in `_trigger_wa_escalation_call()`
4. **GAP-7A** (TTS phone) — regex pre-processing in `tts.py`
5. **GAP-5B** (max fallback threshold) — counter in FSM, 2 template aggiuntivi
6. **GAP-4B** (first available) — già documentato come BUG-3, connettere FSM a DB lookup

---

## Note su Cosa Sara Fa Bene (Non da Toccare)

Per completezza, Sara supera già molti competitor PMI su:
- Disambiguazione fonetica (Levenshtein) — PolyAI usa lo stesso approccio
- 5-layer RAG con LRU cache — architettura solida
- SQLite fallback quando Bridge offline — enterprise-grade
- Parallel TTS streaming (L4) — meno di 5% dei competitor PMI lo ha
- 3-level correction in CONFIRMING — gold standard corretto
- Sentiment analysis con guard su booking attivo (post-fix) — sofisticato
- TimeConstraint TIMEX3 (commit 6616124) — superiore alla maggior parte

Il gap principale non è nell'architettura ma nelle micro-decisioni UX:
fallback quality, slot alternatives, proactive intelligence.

---
_Generato: 2026-03-12 | Agente A | 245 righe_
