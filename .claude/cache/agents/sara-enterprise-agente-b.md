# Sara Voice Agent — CoVe 2026 Deep Codebase Audit (Agente B)
> Audit completo codebase `voice-agent/src/`. Gap NON già noti nei file di research esistenti.
> Data: 2026-03-12 | Agente: B | File letti: _INDEX.md, orchestrator.py, booking_state_machine.py,
> entity_extractor.py, italian_regex.py, sentiment.py, disambiguation_handler.py, tts.py, analytics.py

---

## A. STATO FSM — Stati mancanti / incompleti

### GAP-A1: `handle_timeout()` non differenzia per stato FSM
- **File:riga**: `booking_state_machine.py:2381`
- **Problema**: `handle_timeout()` ritorna sempre la stessa risposta generica ("Sei ancora lì?")
  indipendentemente dallo stato. In `REGISTERING_PHONE` un timeout diverso ("Le ho chiesto il
  numero di telefono, vuole continuare?") sarebbe UX migliore. In `CONFIRMING` si dovrebbe
  ricordare all'utente il riepilogo.
- **Fix proposto**: Dispatch per stato nel metodo `handle_timeout()` — risposta diversa per
  WAITING_NAME, REGISTERING_PHONE, CONFIRMING, WAITING_DATE, WAITING_TIME.
- **Priorità**: P1

### GAP-A2: Stato `SLOT_UNAVAILABLE` senza handler dedicato in `process_message()`
- **File:riga**: `booking_state_machine.py:750-815` (dispatch switch) + `_INDEX.md:32`
- **Problema**: `BookingState.SLOT_UNAVAILABLE`, `PROPOSING_WAITLIST`, `CONFIRMING_WAITLIST`,
  `WAITLIST_SAVED` sono elencati nell'enum (riga 32 dell'index) ma NON hanno handler dedicati
  nel `process_message()` dispatch switch (righe 750-815). Se la FSM atterra in questi stati
  e riceve input, cade nel fallback generico (`TEMPLATES["fallback_clarify"]`).
  `waiting_for_waitlist_confirm` viene gestito via flag bool in orchestrator (riga 739),
  non con stati FSM: architettura doppia inconsistente.
- **Fix proposto**: Aggiungere handler `_handle_slot_unavailable()`, `_handle_proposing_waitlist()`,
  `_handle_confirming_waitlist()` nel dispatch di `process_message()`.
- **Priorità**: P1

### GAP-A3: Nessun handler per torna indietro da `REGISTERING_PHONE` / `REGISTERING_SURNAME`
- **File:riga**: `orchestrator.py:1798` (`_handle_back`)
- **Problema**: `_handle_back()` gestisce solo WAITING_TIME→WAITING_DATE, WAITING_DATE→WAITING_SERVICE,
  CONFIRMING→WAITING_TIME. Non copre il percorso di registrazione nuovo cliente:
  - Da REGISTERING_PHONE → REGISTERING_SURNAME
  - Da REGISTERING_CONFIRM → REGISTERING_PHONE
  - Da PROPOSING_WAITLIST → WAITING_TIME
  Se l'utente dice "torna indietro" durante la registrazione, riceve "Mi dica pure cosa vuole
  cambiare." senza alcuna transizione di stato.
- **Fix proposto**: Aggiungere casi nel `_handle_back()` per tutti gli stati di registrazione.
- **Priorità**: P1

### GAP-A4: Stato `COMPLETED` emette risposta fissa senza `business_name`
- **File:riga**: `booking_state_machine.py:803`
- **Problema**: "L'appuntamento è già stato confermato. Arrivederci!" — risposta generica, non usa
  `self.context.service_display` o `booking_context.business_name`. Dopo una prenotazione
  completata, un secondo messaggio dell'utente nella stessa sessione riceve questa risposta
  decontestualizzata.
- **Fix proposto**: "Il suo appuntamento per {service} è confermato. A presto da {business_name}!"
- **Priorità**: P2

### GAP-A5: L'interruzione "reset" va sempre a `WAITING_SERVICE`, non al flusso corretto
- **File:riga**: `booking_state_machine.py:866-870`
- **Problema**: Il pattern `reset` in `_check_interruption()` porta sempre a `WAITING_SERVICE`
  con risposta TEMPLATES["reset_ack"]. Ma se il cliente non è ancora noto (WAITING_NAME),
  azzerare e tornare a WAITING_SERVICE è sbagliato — dovrebbe tornare a WAITING_NAME o IDLE.
  Caso concreto: cliente dice "ricominciamo" mentre Sara chiede il nome → Sara risponde
  "Quale servizio desidera?" senza aver raccolto il nome.
- **Fix proposto**: Logica condizionale: se `client_id` è None → IDLE, altrimenti WAITING_SERVICE.
- **Priorità**: P1

### GAP-A6: `WAITING_OPERATOR` non ha logica "qualsiasi operatore" / "indifferente"
- **File:riga**: `booking_state_machine.py:2154` (`_handle_waiting_operator`)
- **Problema**: L'index indica che WAITING_OPERATOR ha un handler, ma dal codice letto il flusso
  non è noto gestire "indifferente", "chiunque", "non importa", "scegli tu". Il fallback
  documentato nei bug noti (BUG-3) descrive il problema per lookup_type="first_available" —
  confermato: nessun sinonimo di "indifferente" mappa a scelta automatica operatore.
- **Fix proposto**: In `_handle_waiting_operator`, se input matcha pattern indifferente →
  `operator_requested=False`, `operator_id=None`, transizione a CONFIRMING.
- **Priorità**: P1 (già noto parzialmente, ma riga esatta ora identificata)

---

## B. ENTITY EXTRACTOR — Casi non coperti

### GAP-B1: Data "il primo" / "l'uno" non riconosciuta come giorno 1
- **File:riga**: `entity_extractor.py:384` (pattern `\bil\s+(\d{1,2})\b`)
- **Problema**: Pattern cerca `\bil\s+(\d{1,2})\b` — cattura solo numeri arabi. Parole come
  "il primo", "l'uno del mese" non vengono parsate. `dateparser` può gestirle ma solo se
  installato (flaggato come opzionale con HAS_DATEPARSER=False fallback). Nei dizionari
  `giorni_scritti` in `disambiguation_handler.py` riga 469 esiste il mapping "primo"→1,
  ma questa funzione è solo per date di nascita, non per date di appuntamento.
- **Fix proposto**: Aggiungere alla `extract_date()` un pattern per numeri ordinali scritti
  ("primo", "l'uno", "il due") → giorno del mese.
- **Priorità**: P1

### GAP-B2: "Fra un mese" / "il mese prossimo" non gestito
- **File:riga**: `entity_extractor.py:314-357`
- **Problema**: Gestiti "fra X giorni" e "fra X settimane" ma non "fra un mese", "il mese prossimo",
  "fra due mesi". Il pattern `fra_pattern` cattura solo `giorn[oi]|settiman[ae]`, non `mes[ei]`.
  Chiamata comune: "Vorrei un appuntamento per il mese prossimo" → `extract_date()` ritorna None.
- **Fix proposto**: Aggiungere unità `mes[ei]` al pattern `fra_pattern` + aggiungere
  "mese prossimo"/"il prossimo mese" ai relativi.
- **Priorità**: P1

### GAP-B3: Orario "a ora di pranzo" risolve a 13:00 (PRANZO slot) ma non a TimeConstraint AROUND
- **File:riga**: `entity_extractor.py:208-223` (TIME_SLOTS) e `_SEMANTIC_ANCHORS:460-468`
- **Problema**: "ora di pranzo" è in TIME_SLOTS con mapping fisso `TimeSlot.PRANZO` = "13:00",
  restituisce `ExtractedTime(time=13:00, is_approximate=True)` senza `time_constraint`. Ma
  "ora di pranzo" semanticamente significa AROUND(13:00), non EXACT(13:00). Il slot "stasera"
  (19:00) è anch'esso approssimativo ma non ha TimeConstraint AROUND.
  "_SEMANTIC_ANCHORS" copre "dopo pranzo" ma non "a pranzo" / "durante il pranzo".
- **Fix proposto**: TIME_SLOTS dovrebbe creare `TimeConstraint(AROUND, anchor=time(H,M))` invece
  di exact time; oppure aggiungere a `_SEMANTIC_ANCHORS`.
- **Priorità**: P2

### GAP-B4: Numeri telefono in formato parlato non gestiti
- **File:riga**: `entity_extractor.py` (pattern telefono non letto completamente, ma confermato
  da tts.py:32 che gestisce solo formato numerico per la rilettura)
- **Problema**: Whisper può trascrivere "tre otto zero" invece di "380" per numeri dettati a voce.
  Il pattern telefono cerca sequenze numeriche (`\d{10,11}`). Se il numero viene dettato
  "separando le cifre" verbalmente, non viene estratto.
- **Fix proposto**: In `entity_extractor.py` aggiungere pre-processing che converte numero
  parlato a cifre prima dell'estrazione telefono, usando `_normalize_italian_numbers()` già
  esistente nell'estrattore.
- **Priorità**: P1

### GAP-B5: Nome operatore estratto solo da `ExtractedOperator` — non da frasi embed
- **File:riga**: `entity_extractor.py` (classe `ExtractedOperator` riga 164)
- **Problema**: L'estrazione nome operatore cerca pattern come "con Mario", "dall'operatrice
  Laura" ma in WAITING_OPERATOR il cliente può rispondere solo con il nome ("Mario", "la Carla").
  Il campo `ExtractedOperator.name` cattura il nome, ma se l'utente dice "vorrei quello che
  viene il martedì" o "il ragazzo con i capelli" non c'è estrazione.
- **Fix proposto**: In `_handle_waiting_operator()` aggiungere fuzzy match sul nome contro
  lista operatori DB (già disponibile via `_search_operators()`).
- **Priorità**: P2

### GAP-B6: "Fine settimana" / "weekend" non normalizzato a sabato prossimo
- **File:riga**: `entity_extractor.py:290-302`
- **Problema**: `AMBIGUOUS_DATE_PATTERNS` in `italian_regex.py:582` rileva "fine settimana"
  come ambiguo, ma `extract_date()` in entity_extractor non ha logica per convertire "weekend" /
  "fine settimana" a una data concreta (sabato prossimo). Se non c'è match in patterns precedenti
  e `dateparser` è offline, ritorna None.
- **Fix proposto**: Aggiungere "fine settimana" / "weekend" ai pattern in `extract_date()` →
  sabato prossimo (`timedelta` calcolato come da "sabato").
- **Priorità**: P1

---

## C. TTS PREPROCESSING — Cosa viene letto male

### GAP-C1: Date in formato numerico "13/03" lette come "tredici barra tre"
- **File:riga**: `tts.py:37` (`preprocess_for_tts` — solo telefoni, non date)
- **Problema**: `preprocess_for_tts()` espande solo numeri di telefono. Le date in formato
  numerico come "13/03" o "15:30" passano al TTS senza preprocessing. Piper/Chatterbox leggono
  "13/03" come "tredici barra tre" invece di "tredici marzo". Il campo `date_display` di
  BookingContext viene già formato in italiano ("mercoledì 15 marzo") ma il TTS riceve
  il testo grezzo del template, non il display.
  **Verifica**: template `confirm_phone_number` in booking_state_machine.py riga 533 (già
  documentato parzialmente in BUG: TTS-PHONE nei bug noti).
- **Fix proposto**: Estendere `preprocess_for_tts()` per convertire pattern `\d{1,2}/\d{1,2}`
  in formato "GG mese_italiano". Anche "ore HH:MM" va bene, ma "HH:MM" bare può confondere.
- **Priorità**: P0

### GAP-C2: Acronimi IVA, SDI, WhatsApp letti male
- **File:riga**: `tts.py:37` (`preprocess_for_tts`)
- **Problema**: Acronimi comuni nelle risposte di Sara non vengono espansi prima del TTS.
  - "IVA" → Piper legge "i-va" o "iva" (accent sbagliato)
  - "SDI" → "s-di-i" o "èsdi"
  - "WhatsApp" → "uòtsapp" (Piper confonde W iniziale)
  - "SMS" → "smès" o "ès-em-ès"
  Il testo delle FAQ e dei template può contenere questi acronimi.
- **Fix proposto**: Aggiungere dizionario acronimi in `preprocess_for_tts()`:
  ```python
  ACRONYMS = {"IVA": "I-V-A", "SDI": "S-D-I", "WhatsApp": "Whatsapp", "SMS": "S-M-S"}
  ```
- **Priorità**: P2

### GAP-C3: Prezzi in euro "€20" o "20€" letti come "ventimilioni" o "venti euro"
- **File:riga**: `tts.py:37`
- **Problema**: Il simbolo `€` prima del numero porta certi TTS a leggere il numero come intero
  grande. "€20" può essere letto come "simbolo-euro venti" o "ventimilioni di euro" da Piper.
  Non c'è preprocessing per il simbolo euro.
- **Fix proposto**: `preprocess_for_tts()`: regex `€(\d+)` → "X euro", `(\d+)€` → "X euro".
- **Priorità**: P2

### GAP-C4: `warm_cache()` in TTSCache non pre-processa i testi prima del caching
- **File:riga**: `tts.py:534-551`
- **Problema**: `warm_cache()` chiama direttamente `self._engine.synthesize(t)` bypassando
  `preprocess_for_tts()`. Quindi i testi pre-warmati vengono sintetizzati senza espansione
  telefoni/date. Al contrario `synthesize()` della cache chiama `preprocess_for_tts(key)`.
  Se un testo pre-warmato contiene un numero di telefono, la versione cacchata non ha
  l'espansione, ma se richiesta via `synthesize()` la riceve — mismatch cache: hit ritorna
  audio senza espansione, miss ritorna audio con espansione.
- **Fix proposto**: In `warm_cache()`, applicare `preprocess_for_tts(t)` prima di sintetizzare
  e usare il testo preprocessato come chiave cache.
- **Priorità**: P1

### GAP-C5: Chatterbox TTS importa `torch` — viola regola Python 3.9 iMac
- **File:riga**: `tts.py:130` (`from chatterbox.tts import ChatterboxTTS`) + riga 176 (`import torchaudio`)
- **Problema**: `ChatterboxTTS._load_model()` chiama `from chatterbox.tts import CBModel` che
  richiede PyTorch. La factory `get_tts()` (riga 468) tenta `import torch` come guard, quindi
  fallisce silenziosamente a Piper se torch non è installato su iMac. Tuttavia il `ChatterboxTTS`
  è dichiarato come `DEFAULT_ENGINE` (riga 72) e `synthesize_to_file()` (riga 201) fa
  `import torchaudio as ta` senza guard. Se il codice path tenta direttamente
  `ChatterboxTTS().synthesize_to_file()` crasha invece di degradare.
- **Fix proposto**: Aggiungere guard `import torchaudio` in `try/except ImportError` in
  `synthesize_to_file()`. Documentare che su iMac production il default è sempre Piper.
- **Priorità**: P1

---

## D. ANALYTICS — Metriche mancanti

### GAP-D1: FCR (First Call Resolution) non tracciato
- **File:riga**: `analytics.py:77` (`AnalyticsMetrics` dataclass)
- **Problema**: `AnalyticsMetrics` traccia completion_rate, escalation_rate, groq_usage_percent,
  avg_satisfaction. Non traccia FCR = percentuale di conversazioni in cui il cliente ha ottenuto
  ciò che voleva **senza dover richiamare**. FCR è la metrica #1 dei call center enterprise
  (Gartner 2026: FCR target >70%). Senza FCR non si sa se Sara risolve davvero i problemi.
- **Fix proposto**: Aggiungere `first_call_resolution_rate: float` e un campo `conversation_id`
  per correlare chiamate dallo stesso numero in 24h (se outcome = NOT completed → FCR fallita).
- **Priorità**: P1

### GAP-D2: AHT (Average Handle Time) non correttamente calcolato
- **File:riga**: `analytics.py:620` (`get_metrics`)
- **Problema**: `avg_latency_ms` è latenza per turn, non AHT (tempo totale conversazione).
  `total_latency_ms / total_turns` = latenza media per risposta, non durata call. In un call
  center l'AHT include hold time + talk time. Il campo `ended_at - started_at` di
  `ConversationSession` darebbe AHT reale ma non viene calcolato nel `get_metrics()`.
- **Fix proposto**: In `get_metrics()` aggiungere query:
  ```sql
  AVG((julianday(ended_at) - julianday(started_at)) * 86400) as avg_handle_time_seconds
  ```
- **Priorità**: P1

### GAP-D3: Nessuna metrica per "dove si rompono le conversazioni"
- **File:riga**: `analytics.py:689` (`get_failed_queries`)
- **Problema**: `get_failed_queries()` ritorna query che hanno usato Groq o avuto frustrazione,
  ma non identifica in quale **stato FSM** la conversazione è abbandonata. Se l'utente abandona
  durante REGISTERING_PHONE, Sara ha bisogno di sapere che la registrazione è il collo di
  bottiglia. Non c'è colonna `fsm_state` in `conversation_turns`.
- **Fix proposto**: Aggiungere colonna `fsm_state TEXT` alla tabella `conversation_turns` nel
  SCHEMA. Loggare `self.booking_sm.context.state.value` in ogni turn log in orchestrator.py.
- **Priorità**: P0

### GAP-D4: `cleanup_old_data()` non viene mai chiamato automaticamente
- **File:riga**: `analytics.py:779`
- **Problema**: `cleanup_old_data()` è implementato (GDPR retention 90gg) ma non è schedulato.
  Nessun chiamante automatico visibile in main.py o orchestrator. I dati crescono senza limite
  finché non viene chiamato manualmente. Su un sistema con 100 chiamate/giorno, dopo 90 giorni
  = 9000 conversazioni accumulate senza pulizia automatica.
- **Fix proposto**: In `main.py` aggiungere job periodico (APScheduler già usato per reminder):
  `scheduler.add_job(logger.cleanup_old_data, 'cron', hour=3)`.
- **Priorità**: P1

### GAP-D5: Tabella `faq_effectiveness` non viene mai popolata
- **File:riga**: `analytics.py:854` (`log_faq_effectiveness`)
- **Problema**: `log_faq_effectiveness()` è implementato e la tabella esiste nello SCHEMA, ma
  nessuna parte del codebase chiama questo metodo (verificato: nessuna chiamata in orchestrator.py
  o faq_manager.py nell'index). La tabella è sempre vuota, rendendo inutile questa metrica.
- **Fix proposto**: In orchestrator.py layer L3 (FAQ retrieval, riga ~1365-1401), dopo aver
  risposto con una FAQ, chiamare `analytics.log_faq_effectiveness(faq_id, ...)`. Il feedback
  "è stato utile?" può essere inferito dalla prossima utterance (se l'utente ripete la domanda
  → `was_helpful=False`).
- **Priorità**: P2

### GAP-D6: `daily_metrics` non viene mai aggiornata automaticamente
- **File:riga**: `analytics.py:828` (`update_daily_metrics`)
- **Problema**: `update_daily_metrics()` è implementato ma nessuna parte del codice la chiama.
  La tabella `daily_metrics` (usata per il dashboard Tauri) è sempre vuota.
  Il dashboard Tauri che legge le metriche vocali probabilmente riceve dati vuoti.
- **Fix proposto**: Chiamare `update_daily_metrics(verticale_id)` in `end_session()` di
  `ConversationLogger`, oppure come job APScheduler ogni mezzanotte.
- **Priorità**: P1

---

## E. CONCORRENZA / RACE CONDITIONS

### GAP-E1: `_active_sessions` dict in `ConversationLogger` non thread-safe
- **File:riga**: `analytics.py:224` (`self._active_sessions: Dict[str, ConversationSession] = {}`)
- **Problema**: Il dict `_active_sessions` è un plain Python dict condiviso tra chiamate async.
  In Python asyncio questo è generalmente safe (GIL + single event loop), ma se il logger
  viene usato da thread separati (es. WhatsApp callback in un thread diverso) ci sono race
  conditions. La struttura `del self._active_sessions[session_id]` in `end_session()` riga 352
  può sollevare KeyError se chiamata due volte concorrentemente.
- **Fix proposto**: Wrappare le operazioni su `_active_sessions` in `asyncio.Lock` o usare
  `dict.pop(session_id, None)` per evitare KeyError.
- **Priorità**: P1

### GAP-E2: `ChatterboxTTS._model` (class variable) condiviso tra istanze senza lock
- **File:riga**: `tts.py:97` (`_model = None` class variable)
- **Problema**: `ChatterboxTTS._model` è una class variable condivisa. Se due richieste TTS
  arrivano simultaneamente e il modello non è ancora caricato, entrambe eseguono `_load_model()`.
  Non c'è lock, quindi due thread potrebbero caricare il modello due volte, sprecando 200MB di
  RAM e potenzialmente causando conflitti.
- **Fix proposto**: Aggiungere `_load_lock = asyncio.Lock()` come class variable e wrappare
  `_load_model()` con `async with ChatterboxTTS._load_lock:`.
- **Priorità**: P2 (su iMac non critico perché Chatterbox non è installato, fallisce a Piper)

### GAP-E3: Sessione orchestrator non isolata per chiamate concorrenti
- **File:riga**: `orchestrator.py:544-565`
- **Problema**: `self._current_session`, `self._pending_cancel`, `self._pending_reschedule`,
  `self._selected_appointment_id`, `self._last_booking_data` sono instance variables del
  `VoiceOrchestrator`. Se due richieste HTTP arrivano all'endpoint `/api/voice/process`
  in parallelo per sessioni diverse, condividono lo stesso orchestrator singleton e si
  sovrascrivono queste variabili. Il server in `main.py` usa un singolo orchestrator instance
  globale (confermato dalla factory `create_orchestrator()` usata una sola volta).
- **Fix proposto**: `_current_session` e le variabili di stato devono essere spostate in un
  context per-request (dict keyed by session_id) o l'orchestrator deve essere creato per-sessione.
- **Priorità**: P0 (critico per multi-tenant o chiamate parallele)

---

## F. SICUREZZA / GDPR

### GAP-F1: Numero di telefono loggato in chiaro in `print()` nel codice di produzione
- **File:riga**: `orchestrator.py:2098` + molteplici `print(f"[DEBUG]...")` con dati cliente
- **Problema**: `print(f"[DEBUG] SQLite fallback booking created: {booking_id} ({servizio_nome} {data} {ora})")`
  include dati di booking in testo. Peggio: riga ~2211: `print(f"[DEBUG] Creating client: {payload}")`
  dove `payload` contiene `telefono`, `nome`, `cognome` in chiaro. Questi print vanno a
  `/tmp/voice-pipeline.log` (iMac), file non protetto. Non è GDPR compliant se contiene PII.
- **Fix proposto**: Sostituire `print()` con `logger.debug()` condizionale a un flag DEBUG,
  e mascherare PII nei log: `nome[:2]**`, numero telefono `***XX`.
- **Priorità**: P0

### GAP-F2: `anonymize=False` come default in `ConversationLogger`
- **File:riga**: `analytics.py:204`
- **Problema**: Il costruttore di `ConversationLogger` ha `anonymize: bool = False` come default.
  Quindi PII (nomi, telefoni) vengono salvati in chiaro nel database analytics. La funzione
  `_anonymize_if_needed()` esiste ma non viene mai attivata di default. Per GDPR, il default
  dovrebbe essere `anonymize=True` oppure dovrebbe esserci una policy documentata.
- **Fix proposto**: Cambiare default a `anonymize=True`, o documentare esplicitamente che è
  scelta consapevole e che la DB è protetta con accesso limitato.
- **Priorità**: P1

### GAP-F3: Nessuna verifica data retention all'avvio — DB può contenere dati scaduti
- **File:riga**: `analytics.py:200-230` (`__init__`)
- **Problema**: `cleanup_old_data()` non viene chiamato in `__init__()`. Se il sistema si
  riavvia dopo un lungo downtime, il DB analytics potrebbe contenere dati oltre i 90gg (retention_days)
  senza che vengano mai purgati. GDPR Art. 5(e) richiede che i dati non vengano conservati
  oltre il necessario.
- **Fix proposto**: In `__init__()` aggiungere chiamata a `cleanup_old_data()` in background,
  o almeno loggare quanti record scaduti esistono.
- **Priorità**: P1

### GAP-F4: DB path in `_load_config_from_sqlite()` non validato contro path traversal
- **File:riga**: `orchestrator.py:1654`
- **Problema**: `db_path = os.environ.get("FLUXION_DB_PATH")` — se questa env var viene
  impostata da input esterno, potrebbe contenere un path traversal (`../../etc/passwd`).
  Non c'è validazione che il path sia una sottodirectory di `~/Library/Application Support`.
  Rischio basso in un contesto desktop locale, ma da notare per completezza enterprise.
- **Fix proposto**: Validare che `db_path` sia assoluto e contenuto in directory autorizzate.
- **Priorità**: P2

---

## G. VERTICALI — Gap specifici per verticale non-salone

### GAP-G1: `_get_next_required_slot()` per verticale "auto" non richiede ora
- **File:riga**: `booking_state_machine.py:2388-2408`
- **Problema**: In verticale "auto", `required_slots` esclude `("time", BookingState.WAITING_TIME)`.
  Quindi il flusso booking auto salta direttamente da WAITING_DATE a CONFIRMING senza chiedere
  l'ora. Questo ha senso per alcuni scenari (es. lasciare la macchina per la giornata), ma
  non per tutti (es. "cambio gomme veloce, ci voglio 20 minuti"). Nessuna configurazione
  per auto-officine che fanno appuntamenti orari.
- **Fix proposto**: Aggiungere configurazione per-verticale `requires_time: bool` caricata
  dal DB impostazioni, con default True per tutti tranne "auto_dropoff".
- **Priorità**: P2

### GAP-G2: Verticale "medical" non gestisce urgenza come slot dedicato
- **File:riga**: `orchestrator.py:627-639` (extra_entities)
- **Problema**: `urgency` viene estratto da `extract_vertical_entities()` e salvato in
  `context.extra_entities`. Ma non cambia il flusso FSM: un paziente che dice "ho un dolore
  acuto, è urgente" riceve lo stesso flusso di prenotazione standard. Non c'è stato
  WAITING_URGENCY o routing verso uno slot di urgenza / guardia medica.
- **Fix proposto**: In `_handle_waiting_service()` per verticale medical, se `urgency=True` →
  risposta specializzata "Per urgenze, le consiglio di chiamare il 118 o presentarsi
  direttamente. Vuole comunque prenotare una visita?" + flag per slot di urgenza.
- **Priorità**: P1

### GAP-G3: Verticale "palestra" non gestisce abbonamenti vs appuntamenti singoli
- **File:riga**: `italian_regex.py:247-259` (VERTICAL_SERVICES palestra)
- **Problema**: In palestra, "abbonamento", "iscrizione", "tessera" sono service synonyms ma
  non ha senso "prenotare un abbonamento" con data e ora. Il flusso FSM standard chiede data
  e ora anche per "voglio rinnovare l'abbonamento". Questo è un percorso completamente diverso
  (gestione commerciale, non calendar booking).
- **Fix proposto**: Aggiungere guardrail/branch in `_handle_waiting_service()` per palestra:
  se service matcha abbonamento → risposta "Per l'abbonamento la mettiamo in contatto con
  la segreteria" (escalation soft) senza continuare il booking flow.
- **Priorità**: P1

### GAP-G4: FAQ mancanti per scenari "auto" comuni non coperti da L1
- **File:riga**: `italian_regex.py:276-290` (VERTICAL_SERVICES auto)
- **Problema**: Il verticale "auto" ha sinonimi per servizi ma nessuna FAQ built-in per:
  - "Quanto costa il tagliando?" → risposta standard
  - "Accettate garanzia?" → risposta standard
  - "Fate conto alla rovescia Euro6?" → specifico Italy
  - "Fate ritiro a domicilio?" → comune per officine premium
  Questi finiscono a Groq (L4) aumentando latenza e costo API.
- **Fix proposto**: Aggiungere FAQ verticale "auto" in `vertical_faqs/auto_faqs.json` (se
  il file esiste) con le domande di cui sopra.
- **Priorità**: P2

### GAP-G5: Greeting non personalizzato per verticale
- **File:riga**: `orchestrator.py:1822-1845` (`_build_llm_context`)
- **Problema**: Il system prompt Groq non include il verticale: "Sei Sara, l'assistente vocale
  di {business_name}". Non c'è indicazione se è un salone, palestra, studio medico o officina.
  Groq potrebbe quindi rispondere in modo inadeguato per il contesto (es. "Le consiglio la
  nostra promozione abbronzatura" in un'officina). Anche il greeting iniziale non cambia per
  verticale.
- **Fix proposto**: In `_build_llm_context()` aggiungere riga:
  `"VERTICALE: {self.verticale_id} ({vertical_description})"` + lista servizi tipici del
  verticale + lista di argomenti OUT-OF-SCOPE per questo verticale.
- **Priorità**: P1

---

## H. ALTRI GAP TRASVERSALI

### GAP-H1: LRU cache intent condivisa tra sessioni può causare risposte errate
- **File:riga**: `orchestrator.py:101-103` + `start_session():483`
- **Problema**: `clear_intent_cache()` viene chiamato solo in `start_session()`. Ma la LRU cache
  è module-level (`@functools.lru_cache` o simile). Se due sessioni attive condividono un'utterance
  comune ("sì"), la seconda ottiene il risultato cacchato della prima (stesso testo → stesso
  intent result). Questo è quasi sempre corretto per intent puri, ma il `intent_result.response`
  cacheato potrebbe contenere il nome cliente della sessione precedente se i template erano
  personalizzati.
- **Fix proposto**: Verificare che `intent_result.response` non contenga dati session-specific.
  Se sì, non cachare la response, solo l'intent category + confidence.
- **Priorità**: P1

### GAP-H2: `_build_llm_context()` non include orari di apertura né lista operatori
- **File:riga**: `orchestrator.py:1822-1845`
- **Problema**: Il system prompt per Groq contiene solo personalità + CAPACITA' + contesto attuale
  (service/date/time/cliente). Non include:
  - Orari di apertura (se qualcuno chiede "siete aperti domenica?" a Groq, risponde inventando)
  - Lista operatori disponibili (Groq non può consigliare "Marco è disponibile")
  - Prezzi dei servizi (Groq risponde generico)
  Questi dati sono disponibili nel DB e già caricati in `db_config` a inizio sessione.
- **Fix proposto**: In `_build_llm_context()` aggiungere sezione con orari, operatori (nomi),
  e top-5 servizi più frequenti con prezzo — tutto da `db_config`.
- **Priorità**: P1

### GAP-H3: PHONETIC_VARIANTS ha duplicati e inconsistenze
- **File:riga**: `disambiguation_handler.py:118-132`
- **Problema**:
  - `"gigio": ["gino", "gigi", "gianni"]` e `"gino": ["gigio", "gino", "gianni"]` — "gino"
    appare come variante di sé stesso in "gino" entry.
  - `"anna": ["ana", "annamaria", "annamaria"]` — "annamaria" duplicata.
  - `"gigi": ["luigi", "gino", "gigio"]` e `"luigi": ["gigi", "luigia", "luisa"]` — "gigi"
    è sia base che variante, creando cicli nella logica di matching.
  - Il commento dice "Ordered to ensure deterministic matching" ma l'ordine non ha effetto
    poiché si usa `dict.items()` non ordered matching.
- **Fix proposto**: Deduplicare varianti, rimuovere self-references, normalizzare la struttura.
- **Priorità**: P2

### GAP-H4: `_check_special_command()` usa substring match su tutta la stringa
- **File:riga**: `orchestrator.py:1619-1632`
- **Problema**: Il loop `if cmd in text_lower` fa substring match. Se `SPECIAL_COMMANDS` contiene
  una chiave "no" (verificare), "aiuto", o "annulla", qualsiasi utterance che contiene
  queste parole come sottostringhe triggera il comando speciale. Esempio ipotetico: se esiste
  "si" come special command, "visita" contiene "si" e triggererebbe il match.
  La lista SPECIAL_COMMANDS non è stata letta integralmente, ma il pattern è pericoloso.
- **Fix proposto**: Usare word boundary matching `r'\b' + re.escape(cmd) + r'\b'` invece di
  substring `in`.
- **Priorità**: P1

### GAP-H5: `analyze_simple()` usa `Dict[str, any]` (lowercase `any`) — tipo non valido
- **File:riga**: `sentiment.py:411`
- **Problema**: `def analyze_simple(self, text: str) -> Dict[str, any]:` — `any` minuscolo
  non è un tipo Python valido in questo contesto. In Python 3.9 `any` è la funzione built-in,
  non un type hint. Dovrebbe essere `Dict[str, Any]` (importato da `typing`). In runtime non
  causa errori immediati ma viola TypeScript strict equivalente e potrebbe causare problemi
  con mypy/pyright se usati.
- **Fix proposto**: Cambiare `any` in `Any` (già importato in `sentiment.py:10`).
- **Priorità**: P2

### GAP-H6: Messaggio escalation non include dati cliente per l'operatore umano
- **File:riga**: `orchestrator.py:2178`
- **Problema**: Il messaggio di escalation WhatsApp al titolare è:
  `"Richiesta escalation ({escalation_type}) da cliente: {client_name}. Richiamarlo al più presto."`
  Non include: numero telefono cliente, servizio richiesto, motivo escalation verbatim,
  timestamp. Un operatore umano che riceve questo messaggio non sa a chi rispondere.
- **Fix proposto**: Arricchire il messaggio con `client_phone`, `service`, `escalation_context`
  (ultime 2-3 utterance dell'utente), `timestamp`.
- **Priorità**: P1

### GAP-H7: `process()` alias in BookingStateMachine sincronizza solo 5 campi al write-back
- **File:riga**: `booking_state_machine.py:843-854`
- **Problema**: Il write-back da SM context a external ctx copia solo: state, service, date, time,
  client_id, client_name, client_phone, operator_id, operator_name. Non copia:
  - `time_constraint_type` / `time_constraint_anchor` (per AFTER/BEFORE/AROUND semantics)
  - `urgency`
  - `notes`
  - `disambiguation_attempts`
  - `was_interrupted`
  Questi campi vengono persi se l'orchestrator usa il ctx esterno come fonte di verità.
- **Fix proposto**: Completare il write-back per includere tutti i campi non-identity rilevanti.
- **Priorità**: P1

---

## Riepilogo per Priorità

| Priorità | Count | Gap IDs |
|----------|-------|---------|
| P0 | 4 | GAP-C1, GAP-D3, GAP-E3, GAP-F1 |
| P1 | 21 | GAP-A1,A2,A3,A5,A6 · GAP-B1,B2,B4,B6 · GAP-C4,C5 · GAP-D1,D2,D4,D6 · GAP-E1 · GAP-F2,F3 · GAP-G2,G3,G5 · GAP-H1,H2,H4,H6,H7 |
| P2 | 11 | GAP-A4 · GAP-B3,B5 · GAP-C2,C3 · GAP-D5 · GAP-E2 · GAP-F4 · GAP-G1,G4 · GAP-H3,H5 |

---

## Top 5 Fix Immediati (P0)

1. **GAP-E3** `orchestrator.py` — Instance variables condivise tra sessioni parallele. Ogni
   sessione parallela sovrascrive `_current_session`, `_pending_cancel`, ecc. Su un sistema
   multi-chiamata questo causa booking attribuiti alla sessione sbagliata.

2. **GAP-F1** `orchestrator.py:2204` — PII (nome+telefono cliente) in `print()` → log file non
   protetto. Viola GDPR. Fix immediato: `logger.debug()` con PII mascherata.

3. **GAP-D3** `analytics.py` — Nessuna colonna `fsm_state` nei turn log. Impossibile sapere
   dove si rompono le conversazioni senza questo dato. Migration DB necessaria.

4. **GAP-C1** `tts.py:37` — Date numeriche "13/03" non preprocessate → Piper legge "tredici
   barra tre". Impatta ogni conferma di prenotazione.

5. **GAP-A2** `booking_state_machine.py` — SLOT_UNAVAILABLE, PROPOSING_WAITLIST,
   CONFIRMING_WAITLIST non hanno handler nel dispatch switch. Se la FSM atterra in questi
   stati, ogni utterance cade nel fallback generico.

---
_Audit completato: 2026-03-12. File letti: 9. Gap trovati: 37 (4 P0, 21 P1, 12 P2)._
_Non include gap già documentati in: voice-agent-bugs-research.md, voice-agent-production-issues-research.md, f02-nlu-ambiguity-research.md_
