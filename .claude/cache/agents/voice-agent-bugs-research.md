# Voice Agent Sara — Bug Research (CoVe 2026)
> Generato: 2026-03-03
> Conversazione analizzata: Genoveffo, salone, flusso prenotazione con richiesta flessibilità date

---

## A. MAPPA ESATTA DEI BUG

---

### BUG-1: "scegli tu per me" → `escalation_frustration` (CRITICO)

**File**: `voice-agent/src/orchestrator.py` righe 575-581
**File secondario**: `voice-agent/src/sentiment.py` righe 97-109

**Trigger esatto**:
```
U: "no senti per me è la stessa cosa va bene scegli tu per me da domani tutti i giorni si può fare"
→ sentiment.analyze() viene chiamato PRIMA dell'intent classifier (L0c, riga 575-581)
→ La frase contiene "no" (WORD_BOUNDARY_KEYWORDS peso 1) + "ma" potenziale + storia conversazione
→ Più criticamente: il filler "senti" viene stripped da strip_fillers() DOPO il sentiment check
→ ma il sentiment check usa l'input RAW (con "senti" dentro)
```

**Analisi del percorso nel codice**:

1. orchestrator.py riga 575: `sentiment_result = self.sentiment.analyze(user_input)` — usa input RAW
2. sentiment.py riga 268-270: `_detect_frustration` fa substring match su FRUSTRATION_KEYWORDS
3. Il turno precedente ("vorrei parlare con l'operatore") ha già accumulato storia
4. `_conversation_history` mantiene i punteggi cumulativi (riga 241): storia turn precedente = score elevato
5. Turno "scegli tu per me": "no" (score 1) + storia accumulata → cumulative_frustration >= escalation_threshold (6)
6. Riga 374: `frustration_level == FrustrationLevel.HIGH and cumulative_score >= self.escalation_threshold` → `should_escalate = True`
7. orchestrator.py riga 578-581: `response = "Mi scusi per il disagio. La metto in contatto con un operatore."` + `intent = "escalation_frustration"`

**Problema strutturale**: Il SentimentAnalyzer NON resetta la storia quando l'utente cambia intenzione. Genoveffo ha chiesto l'operatore al turno 1 (score alto da "operatore" = 4 in FRUSTRATION_KEYWORDS riga 63), poi ha cambiato idea e ha chiesto di prenotare — ma la storia accumulata fa sembrare ogni turno successivo "frustrazione cumulativa".

**WORD_BOUNDARY_KEYWORDS problematici** (sentiment.py riga 103-109):
```python
"mai": 3,   # "mai stato" è nuovo cliente, non frustrazione!
"no": 1,    # Ogni negazione normale diventa frustrazione
"ma": 1,    # Connettivo naturale dell'italiano
"però": 1,  # Idem
```

---

### BUG-2: Il SentimentAnalyzer non differenzia "no aspetta voglio prenotare" da frustrazione

**File**: `voice-agent/src/sentiment.py` righe 97-109 (`WORD_BOUNDARY_KEYWORDS`)
**File**: `voice-agent/src/orchestrator.py` riga 575 (ordine di esecuzione)

**Sequenza della conversazione**:
```
Turno 1: "voglio parlare con l'operatore" → escalation → history score += 4 ("operatore")
Turno 2: "sento ma lo posso prendere..." → "no" in text → history score += 1 → cumulative = 5
Turno 3: "no senti per me è la stessa cosa scegli tu" → "no" → cumulative >= 6 → ESCALATE
Turno 4: "No, senti, pure domani..." → idem → loop infinito
```

**Perché non si rompe il loop**: dopo escalation il sentiment check non viene bypassato nei turni successivi. L'orchestrator imposta `should_escalate = True` e chiude la sessione (riga 1294-1307), ma se il client richiama, il SentimentAnalyzer ha la storia azzerata — ma il NUOVO turno viene comunque intercettato perché il sentiment accumula di nuovo se l'utente usa "no".

---

### BUG-3: Nessun handler per "disponibilità flessibile" (MANCANTE)

**File**: `voice-agent/src/booking_state_machine.py` — `_handle_waiting_date()` righe 1927-1980
**File**: `voice-agent/src/italian_regex.py` — nessun pattern per flexible scheduling

**Percorso atteso ma mancante**:
```
U: "scegli tu per me da domani tutti i giorni"
→ Dovrebbe: riconoscere FLEXIBLE_SCHEDULING → proporre prima disponibilità
→ Succede: nessun pattern lo intercetta → va a L4 Groq (UNKNOWN) → risposta generica
```

**`is_ambiguous_date()`** (italian_regex.py riga 570-588) copre:
```python
r"\b(?:prossima|questa)\s+settimana\b",
r"\b(?:uno\s+di\s+questi\s+giorni|appena\s+possibile|prima\s+possibile)\b",
```
Ma NON copre: "scegli tu", "decidi tu", "quando vuoi", "va bene tutto", "tutti i giorni".

**booking_state_machine.py `_handle_waiting_date()`** (riga 1927): controlla `is_ambiguous_date()` per "prossima settimana" ma non ha un branch per "utente indifferente alla data" che dovrebbe triggerare `lookup_type="first_available"`.

---

### BUG-4: L'escalation operatore NON fa nulla di concreto

**File**: `voice-agent/src/orchestrator.py` righe 511-518 e 1863-1890

**Cosa succede realmente**:
1. orchestrator.py riga 512: `response = "La metto in contatto con un operatore, un attimo..."`
2. riga 515: `should_escalate = True`
3. riga 518: `asyncio.ensure_future(self._trigger_wa_escalation_call(pre.escalation_type))` — fire-and-forget
4. `_trigger_wa_escalation_call()` (riga 1863): richiede `self._wa_client` non None AND `telefono_titolare` in config
5. Se `_wa_client` è None (WhatsApp non configurato) → riga 1868: `return` silenzioso
6. Se `telefono_titolare` non è configurato → riga 1877: log info + `return`

**Risultato pratico**: L'escalation manda (nel migliore dei casi) un messaggio WhatsApp al titolare dicendo "richiamare il cliente". NON c'è:
- Trasferimento di chiamata reale
- Notifica urgente con numero cliente
- Conferma che l'escalation è avvenuta
- Timeout o retry

**L'escalation chiude la sessione** (riga 1294-1307): `session_manager.close_session(sid, "escalated")` — dopo questa chiamata, la conversazione è terminata. Il cliente non viene MAI effettivamente connesso a un operatore.

---

### BUG-5: La conversazione non termina mai (loop infinito post-escalation)

**File**: `voice-agent/src/orchestrator.py` riga 1294-1307
**File**: `voice-agent/main.py` (endpoint `/api/voice/process`)

**Problema**: Quando `should_escalate = True`, la sessione viene chiusa lato Python (SQLite). Ma il **canale telefonico** (Twilio/SIP) non viene istruito a chiudere la chiamata. Il campo `should_exit` è impostato a `True` (riga 1295), ma dipende dal Rust client che legga e agisca su `should_exit` nel body della risposta JSON.

**Percorso Rust**: `src-tauri/src/commands/voice_pipeline.rs` — se il client Rust non processa `should_exit: true` correttamente, la chiamata rimane aperta e il cliente può continuare a parlare su una sessione "chiusa".

**Senza risposta dopo escalation**: se il caller parla ancora, ogni turno successivo trova una sessione non esistente (riga 459-467 in orchestrator.py) → viene creata una nuova sessione → nuovo greeting → loop confusionale per il cliente.

---

### BUG-6: Multi-servizio compound non catturato correttamente

**File**: `voice-agent/src/italian_regex.py` righe 296-298 (`_SERVICE_CONNECTORS`)
**File**: `voice-agent/src/booking_state_machine.py` riga 1856 (`extract_multi_services`)

**Frase analizzata**: "mi devo tagliare la barba e mi devo fare il taglio dei capelli e il colore dei capelli"

**`_SERVICE_CONNECTORS`** (riga 297):
```python
r"(?:\s+e\s+|\s*,\s*(?:e\s+)?|\s+(?:con|più|anche|poi(?:\s+anche)?)\s+)"
```
Copre "e", "," e "poi anche" ma NON "e mi devo fare" (con verbo interposto).

**`extract_multi_services()`** (riga 300-320): fa substring match sulle sinonimi — funziona su "barba", "taglio", "colore" come singole parole. MA se Groq restituisce la risposta generica senza estrarre i servizi ("La ringrazio per avermi informato..."), significa che Groq è stato chiamato al Layer 4, che NON popola `self.context.service`.

**Percorso reale**: la frase molto lunga non viene classificata da L1 (nessun exact match) → L2 regex PRENOTAZIONE (regex riga 389: `r"(voglio|vorrei|mi\s+serve|mi\s+servirebbe)\s+(un|una|il|la)?\s*(taglio|piega|colore|tinta|barba|trattamento)"`) → L4 Groq → risposta generica invece di transizione FSM.

---

## B. REGEX MANCANTI DA AGGIUNGERE IN `italian_regex.py`

### B1. Flessibilità date/orari (FLEXIBLE_SCHEDULING)

Da aggiungere come nuova sezione nel file, dopo la sezione 8 (riga 541 attuale):

```python
# =============================================================================
# 9. FLEXIBLE SCHEDULING PATTERNS
# =============================================================================
# User delegates date/time choice to the business.
# These should trigger lookup_type="first_available" in booking_state_machine.

FLEXIBLE_SCHEDULING_PATTERNS = [
    # Delega esplicita
    r"\b(?:scegli|decidi|scegliet[ei]|decidet[ei])\s+(?:tu|voi|lei)\b",
    r"\b(?:quando\s+vuoi|quando\s+volet[ei]|quando\s+(?:vi|le)\s+(?:fa|torna)\s+comod[oa])\b",
    r"\b(?:per\s+me\s+(?:va\s+bene\s+tutto|è\s+(?:lo\s+stesso|uguale|indifferente)))\b",
    r"\b(?:sono\s+)?indifferente\b",
    # Prima disponibilità
    r"\b(?:prima\s+(?:data\s+)?disponibile|prima\s+(?:cosa\s+)?che\s+(?:c'è|avete|trovate))\b",
    r"\b(?:il\s+prima\s+possibile|appena\s+(?:potete|potuto|c'è\s+posto))\b",
    r"\b(?:qualunque|qualsiasi)\s+(?:giorno|data|ora|orario)\b",
    # Tutti i giorni / libertà totale
    r"\b(?:tutti\s+i\s+giorni\s+(?:va\s+bene|sono\s+libero|sono\s+disponibile))\b",
    r"\b(?:va\s+bene\s+(?:tutto|qualunque\s+(?:giorno|ora|orario|cosa)))\b",
    r"\b(?:non\s+ho\s+preferenze?)\b",
    r"\b(?:fate\s+voi|fate\s+(?:pure\s+)?voi|organizzate\s+voi)\b",
    # Come preferisce l'altro
    r"\b(?:come\s+(?:preferisci|preferite|preferisce|ti|vi|le)\s+(?:fa\s+(?:più\s+)?comodo|conviene|torna\s+bene))\b",
    # "Da domani in poi" / range aperto
    r"\b(?:da\s+domani\s+in\s+poi|da\s+domani)\s+(?:qualsiasi|tutti|ogni|qualunque)\b",
    r"\b(?:da\s+(?:oggi|domani|dopodomani))\s+(?:in\s+poi)?\s*(?:va\s+bene|sono\s+disponibile|libero)\b",
]

_FLEXIBLE_SCHEDULING_COMPILED = [re.compile(p, re.IGNORECASE) for p in FLEXIBLE_SCHEDULING_PATTERNS]


def is_flexible_scheduling(text: str) -> Tuple[bool, float]:
    """
    Check if user is flexible on date/time (delegates choice to business).
    Returns (is_match, confidence).
    Triggers lookup_type="first_available" in booking_state_machine.
    """
    text_clean = text.strip()
    for pattern in _FLEXIBLE_SCHEDULING_COMPILED:
        if pattern.search(text_clean):
            return (True, 0.9)
    return (False, 0.0)
```

**Aggiunta in `prefilter()`** (riga 616-653): aggiungere campo `is_flexible_scheduling: bool = False` a `RegexPreFilterResult` e chiamata:
```python
# 7. Flexible scheduling
result.is_flexible_scheduling = is_flexible_scheduling(text)[0]
```

### B2. Multi-servizio compound (connettori con verbo interposto)

In `italian_regex.py`, `_SERVICE_CONNECTORS` (riga 297), aggiungere:

```python
# ATTUALE:
_SERVICE_CONNECTORS = r"(?:\s+e\s+|\s*,\s*(?:e\s+)?|\s+(?:con|più|anche|poi(?:\s+anche)?)\s+)"

# NUOVO — aggiungere connettori con verbo interposto:
_SERVICE_CONNECTORS = r"(?:\s+e\s+(?:mi\s+(?:devo\s+fare|devo\s+(?:fare\s+)?(?:anche\s+)?|vorrei\s+anche\s+))?|\s*,\s*(?:e\s+)?|\s+(?:con|più|anche|poi(?:\s+anche)?|oltre\s+a(?:l|la|i|lle)?|in\s+più)\s+)"
```

### B3. Terminazione conversazione (pattern più robusti)

In `CORTESIA_EXACT` di `intent_classifier.py` (riga 183-195), aggiungere:

```python
# === TERMINAZIONE COLLOQUIALE ===
"ok basta cosi": ("goodbye_done", IntentCategory.CORTESIA, "Perfetto, grazie! Arrivederci!"),
"ok basta così": ("goodbye_done_acc", IntentCategory.CORTESIA, "Perfetto, grazie! Arrivederci!"),
"ci sentiamo": ("goodbye_talk_later", IntentCategory.CORTESIA, "A presto!"),
"ci risentiamo": ("goodbye_talk_later2", IntentCategory.CORTESIA, "Certo, a presto!"),
"a dopo": ("goodbye_later", IntentCategory.CORTESIA, "A dopo!"),
"a domani": ("goodbye_tomorrow", IntentCategory.CORTESIA, "A domani!"),
"per oggi basta": ("goodbye_today_done", IntentCategory.CORTESIA, "Va bene, buona giornata!"),
"non ho altro": ("goodbye_nothing_else", IntentCategory.CORTESIA, "Perfetto, buona giornata!"),
"è tutto": ("goodbye_thats_all", IntentCategory.CORTESIA, "Perfetto! Arrivederci!"),
"e tutto": ("goodbye_thats_all2", IntentCategory.CORTESIA, "Perfetto! Arrivederci!"),
```

### B4. Operatore "persona vera" (varianti fonetiche)

In `CORTESIA_EXACT` di `intent_classifier.py` (riga 197-215), aggiungere:

```python
"non voglio parlare con un robot": ("op_no_robot", IntentCategory.OPERATORE, "Capisco, la connetto con un operatore."),
"non voglio il robot": ("op_no_robot2", IntentCategory.OPERATORE, "Certo, la connetto subito."),
"voglio parlare con una persona vera": ("op_real_person", IntentCategory.OPERATORE, "La connetto con un operatore."),
"mi passi qualcuno": ("op_someone", IntentCategory.OPERATORE, "Subito, un attimo..."),
"c e qualcuno": ("op_anyone", IntentCategory.OPERATORE, "La connetto con un operatore."),
```

### B5. Cambio decisione mid-flow

In `CORRECTION_PATTERNS` di `italian_regex.py` (sezione 8, riga 489), aggiungere a `CorrectionType.GENERIC_CHANGE`:

```python
# Cambio decisione improvviso
r"(?:no\s+aspetta|anzi\s+(?:sai\s+(?:cosa|che)|aspetta))",
r"(?:ci\s+ho\s+ripensato|ho\s+cambiato\s+idea)",
r"(?:sai\s+cosa|sai\s+che)\s*[,\?]?\s*(?:meglio|preferisco|facciamo)",
r"(?:aspetta|fermati)\s+(?:un\s+attimo)?\s*,?\s*(?:ho\s+cambiato|ci\s+ho\s+ripensato)",
```

---

## C. FIX SPECIFICI PROPOSTI (file:line:fix)

---

### FIX-1: Resettare storia SentimentAnalyzer quando l'utente cambia intenzione

**File**: `voice-agent/src/sentiment.py`
**Riga**: 404-412 (metodo `reset_history`)
**Fix**: Chiamare `reset_history()` nell'orchestrator quando si rileva un intent di booking dopo un operatore.

**File**: `voice-agent/src/orchestrator.py`
**Riga**: 596 (dopo `intent_result = classify_intent(user_input)`)
**Fix minimo** (5 righe):
```python
# AGGIUNGERE dopo riga 596:
# Reset sentiment history se l'utente torna a prenotare dopo aver chiesto operatore
if (self.sentiment and
    intent_result.category == IntentCategory.PRENOTAZIONE and
    self.sentiment.get_cumulative_frustration() > 3):
    self.sentiment.reset_history()
    logger.info("[SENTIMENT] Reset history: user returned to booking after operator request")
```

### FIX-2: Escludere connettivi naturali da WORD_BOUNDARY_KEYWORDS

**File**: `voice-agent/src/sentiment.py`
**Riga**: 103-109
**Fix**: Rimuovere "no", "ma", "però" dai WORD_BOUNDARY_KEYWORDS — sono connettivi normali dell'italiano, non indicatori di frustrazione in contesti di prenotazione.

```python
# PRIMA (riga 103-109):
WORD_BOUNDARY_KEYWORDS: Dict[str, int] = {
    "mai": 3,
    "scusi": 2,
    "no": 1,
    "ma": 1,
    "però": 1,
}

# DOPO:
WORD_BOUNDARY_KEYWORDS: Dict[str, int] = {
    "mai": 2,  # ridotto da 3: "mai stato" = nuovo cliente
    "scusi": 1,  # ridotto da 2: normale cortesia
    # RIMOSSI: "no", "ma", "però" — connettivi naturali italiani
}
```

### FIX-3: Aggiungere branch FLEXIBLE_SCHEDULING in `_handle_waiting_date()`

**File**: `voice-agent/src/booking_state_machine.py`
**Riga**: 1927 (inizio `_handle_waiting_date`, dopo il check `if self.context.date:`)
**Fix**: Aggiungere check per flexible scheduling PRIMA della ricerca data normale:

```python
# AGGIUNGERE prima del blocco "Check for ambiguous dates" (riga 1927):
# Check per disponibilità flessibile — utente delega la scelta
if HAS_ITALIAN_REGEX:
    try:
        from .italian_regex import is_flexible_scheduling
    except ImportError:
        from italian_regex import is_flexible_scheduling

    is_flex, flex_conf = is_flexible_scheduling(text)
    if is_flex:
        # Utente non ha preferenze — cerca prima disponibilità
        return StateMachineResult(
            next_state=BookingState.WAITING_DATE,
            response="",  # orchestrator sostituisce con slot reali
            needs_db_lookup=True,
            lookup_type="first_available",
            lookup_params={
                "service": self.context.service,
                "preferred_time": "afternoon",  # estrarre da context se disponibile
                "days_ahead": 7
            }
        )
```

### FIX-4: Aggiungere risposta per WAITING_TIME con orario preferenziale flessibile

**File**: `voice-agent/src/booking_state_machine.py`
**Riga**: 1987 (inizio `_handle_waiting_time`)
**Fix**: Prima di `extract_time()`, controllare se l'utente esprime fascia oraria generica:

```python
# AGGIUNGERE all'inizio di _handle_waiting_time, dopo "text_lower = text.lower()":
# Fascia oraria preferenziale (non ora specifica)
_TIME_PREFERENCE_PATTERNS = [
    (r"\b(?:pomeriggio|dopo\s+(?:le\s+)?(?:pranzo|12|13|14))\b", "14:00", "pomeriggio"),
    (r"\b(?:mattina|mattino|prima\s+(?:di\s+)?(?:pranzo|12|13))\b", "10:00", "mattina"),
    (r"\b(?:sera|tardi|dopo\s+(?:le\s+)?(?:17|18|19))\b", "18:00", "sera"),
    (r"\b(?:dopo\s+(?:le\s+)?)(\d{1,2})\b", None, "dopo_ora"),  # "dopo le 17"
]
for pattern, default_time, label in _TIME_PREFERENCE_PATTERNS:
    m = re.search(pattern, text_lower)
    if m:
        if label == "dopo_ora" and m.group(1):
            hour = int(m.group(1))
            self.context.time = f"{hour:02d}:00"
            self.context.time_is_approximate = True
        elif default_time:
            self.context.time = default_time
            self.context.time_is_approximate = True
        if self.context.time:
            self.context.time_display = f"intorno alle {self.context.time}"
            # Vai a conferma con orario approssimativo
            self.context.state = BookingState.CONFIRMING
            return StateMachineResult(
                next_state=BookingState.CONFIRMING,
                response=TEMPLATES["confirm_booking"].format(summary=self.context.get_summary())
            )
```

### FIX-5: Aggiungere guard nel SentimentAnalyzer per non escalare durante booking attivo

**File**: `voice-agent/src/orchestrator.py`
**Riga**: 575 (layer 0c sentiment check)
**Fix**: Bypassare il sentiment escalation se il booking è in corso (l'utente sta rispondendo a domande della FSM — la sua "frustrazione" sono solo risposte ai prompt):

```python
# PRIMA (riga 575-581):
if response is None and self.sentiment:
    sentiment_result = self.sentiment.analyze(user_input)
    if sentiment_result.should_escalate:
        response = "Mi scusi per il disagio. La metto in contatto con un operatore."
        intent = "escalation_frustration"
        layer = ProcessingLayer.L0_SPECIAL
        should_escalate = True

# DOPO:
if response is None and self.sentiment:
    # NON escalare per sentiment durante un booking flow attivo
    # (l'utente sta rispondendo a domande - "no" / "ma" sono risposta, non frustrazione)
    is_booking_active = self.booking_sm.context.state not in [
        BookingState.IDLE, BookingState.COMPLETED, BookingState.CANCELLED
    ]
    sentiment_result = self.sentiment.analyze(user_input)
    if sentiment_result.should_escalate and not is_booking_active:
        response = "Mi scusi per il disagio. La metto in contatto con un operatore."
        intent = "escalation_frustration"
        layer = ProcessingLayer.L0_SPECIAL
        should_escalate = True
    elif sentiment_result.should_escalate and is_booking_active:
        # Log ma non escalare
        logger.info(f"[SENTIMENT] Escalation suppressed during active booking (state={self.booking_sm.context.state})")
```

### FIX-6: Reset sentiment history all'inizio di ogni nuova sessione

**File**: `voice-agent/src/orchestrator.py`
**Riga**: 396 (in `start_session()`, dopo `self.booking_sm.reset()`)
**Fix**:
```python
# AGGIUNGERE dopo "self.booking_sm.reset()" (riga 396):
if self.sentiment:
    self.sentiment.reset_history()
```

---

## D. ACCEPTANCE CRITERIA MISURABILI

I seguenti test case DEVONO passare dopo i fix. Formato: input → intent atteso → risposta attesa (parziale).

### D1. Flessibilità totale date (BUG-3 fix)
```
Input: "scegli tu per me da domani tutti i giorni"
Stato FSM attivo: WAITING_DATE, service="barba"
Intent atteso: L2_slot / flexible_scheduling (NON escalation_frustration)
Risposta attesa: contiene "disponibilità" o "prima data" o lista slot
should_escalate: False
```

### D2. Flessibilità parziale — pomeriggio (FIX-4)
```
Input: "il pomeriggio dopo le 17 va bene tutti i giorni"
Stato FSM attivo: WAITING_TIME, date="domani"
Intent atteso: L2_slot
Risposta attesa: contiene riepilogo con orario "17:00" o "pomeriggio"
should_escalate: False
```

### D3. Reset sentiment dopo operatore → booking (FIX-1 + FIX-5)
```
Turn 1: "voglio parlare con l'operatore" → intent: escalation_operator, should_escalate: True
[nuova sessione]
Turn 1: "vorrei prenotare taglio e barba" → intent: prenotazione, should_escalate: False
Turn 2: "no per me va bene qualsiasi giorno" → intent: flexible_scheduling, should_escalate: False
Turn 3: "scegli tu" → intent: flexible_scheduling, should_escalate: False
Sentiment escalation: NEVER durante booking attivo
```

### D4. Multi-servizio nella stessa frase (BUG-6 fix)
```
Input: "mi devo tagliare la barba e fare il taglio dei capelli e il colore"
Stato FSM attivo: WAITING_SERVICE
Risultato atteso: self.context.services = ["barba", "taglio", "colore"]
Risposta attesa: conferma tutti e tre i servizi
Layer atteso: L2_slot (NON L4_groq)
```

### D5. "Scegliet voi" pomeriggio con vincolo orario (D1 + D2 combinato)
```
Input: "no per me è uguale, scegliet voi, però nel pomeriggio se possibile"
Stato FSM: WAITING_DATE (service="taglio e barba")
Intent: L2_slot / flexible_scheduling
Context dopo: time_is_approximate=True, time="14:00", lookup_type="first_available"
should_escalate: False
```

### D6. Connettivo "no" non triggerizza frustrazione
```
Input: "no aspetta non ho detto quello, volevo il martedì non il lunedì"
Stato FSM: WAITING_DATE
Sentiment should_escalate: False
Intent: SPOSTAMENTO o correction (CHANGE_DATE)
```

### D7. Loop conversazione termina correttamente
```
Input: "grazie arrivederci"
Stato FSM: qualunque
Intent: CORTESIA / goodbye_thanks (exact match CORTESIA_EXACT)
should_exit: True (OPPURE should_escalate: False, ma sessione chiusa)
Risposta: "Prego! Arrivederci, buona giornata!"
```

### D8. "Prima disponibile" → lookup first_available
```
Input: "mi metta al primo posto che ha libero"
Stato FSM: WAITING_DATE
lookup_type restituito: "first_available"
Risposta: propone slot concreto (da DB) oppure "il prima disponibile è [data]"
should_escalate: False
```

---

## E. SOMMARIO PRIORITÀ FIX

| # | Fix | File | Riga | Impatto | Effort |
|---|-----|------|------|---------|--------|
| 1 | Guard sentiment durante booking attivo | orchestrator.py | 575 | CRITICO — elimina falsi escalation | 5 min |
| 2 | Rimuovere "no"/"ma"/"però" da WORD_BOUNDARY | sentiment.py | 103 | ALTO — riduce score erronei | 2 min |
| 3 | Reset sentiment su start_session | orchestrator.py | 396 | ALTO — storia non si accumula tra sessioni | 2 min |
| 4 | Aggiungere FLEXIBLE_SCHEDULING_PATTERNS | italian_regex.py | 541+ | ALTO — nuovo feature + fix bug | 20 min |
| 5 | Branch flexible in _handle_waiting_date | booking_state_machine.py | 1927 | ALTO — richiede lookup DB | 15 min |
| 6 | Fascia oraria approssimativa in _handle_waiting_time | booking_state_machine.py | 1987 | MEDIO | 15 min |
| 7 | Reset sentiment history su booking intent | orchestrator.py | 596 | MEDIO | 5 min |
| 8 | _SERVICE_CONNECTORS con verbo interposto | italian_regex.py | 297 | MEDIO | 5 min |

**Fix bloccanti (da fare PRIMA degli altri)**: Fix-1 + Fix-2 + Fix-3 — eliminano i falsi positivi di escalation che rendono il bot inutilizzabile nella conversazione analizzata.

---

## F. NOTE ARCHITETTURALI

### L'escalation operatore è "decorativa" allo stato attuale

`_trigger_wa_escalation_call()` dipende da:
1. `self._wa_client` non None (WhatsApp configurato)
2. `telefono_titolare` o `telefono` nella config DB

Se entrambi presenti, manda un messaggio WhatsApp al titolare tipo "richiamare cliente Genoveffo". Non è un trasferimento di chiamata reale. Per un salone, questo è sufficiente (il titolare può richiamare), ma l'UX cliente è interrotta.

**Miglioramento futuro (non critico ora)**: aggiungere SMS fallback via Twilio se WhatsApp non disponibile.

### Il SentimentAnalyzer è troppo sensibile per contesti booking

Il sistema è stato progettato per conversazioni WhatsApp lunghe dove la frustrazione si accumula naturalmente. In una telefonata di prenotazione, ogni "no" è una risposta legittima a una domanda chiusa — non un indicatore di disagio. L'integrazione del SentimentAnalyzer nell'orchestrator (Layer 0c) è concettualmente sbagliata per questo contesto: la sentiment analysis dovrebbe essere informativa (per i log analytics) ma NON dovrebbe triggerare escalation durante un flusso di prenotazione attivo.

### Conversazione che "non termina mai" — causa reale

La conversazione nella trascrizione non termina perché:
1. Ogni turn di Genoveffo viene intercettato da sentiment → `escalation_frustration`
2. La sessione viene chiusa (Python side)
3. Il turn successivo di Genoveffo crea una NUOVA sessione → nuovo greeting
4. Genoveffo parla ancora → altra sessione → loop
Il "silenzio" finale in trascrizione è probabilmente Genoveffo che ha abbandonato.
