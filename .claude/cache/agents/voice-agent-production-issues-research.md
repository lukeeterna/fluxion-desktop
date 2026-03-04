# Voice Agent Production Issues — Research File
> Generato: 2026-03-04 | Sessione 14 | Basato su analisi reale del codice sorgente
> File letti: tts.py, orchestrator.py (2300 righe), booking_state_machine.py (~3200 righe), whatsapp.py, vertical_loader.py, italian_regex.py, entity_extractor.py, main.py

---

## PROBLEMA 1 — TTS Phone Number Formatting

### Root Cause (file:linea)
Il template `confirm_phone_number` in `booking_state_machine.py:533` è:
```python
"confirm_phone_number": "Ho capito {phone}, è corretto?"
```
Il valore `{phone}` viene iniettato grezzo (es. `"3807769822"`). Il TTS engine (SystemTTS → macOS `say`, o Piper) interpreta il numero come valore numerico intero e lo vocalizza come "3 virgola 8 milioni..." o "3 miliardi 807 milioni...".

**Percorso completo**:
1. `booking_state_machine.py:3001-3006` — `_handle_registering_phone` → `CONFIRMING_PHONE` → template con `{phone}` grezzo
2. `booking_state_machine.py:3117` — fallback in `_handle_confirming_phone` → `f"...il numero è {self.context.client_phone or ''}..."` — stesso problema
3. `orchestrator.py:1338` — `await self.tts.synthesize(response)` — riceve il testo con numero grezzo
4. `tts.py` — **NESSUNA pre-elaborazione del testo** prima della sintesi

Il problema è assente per Chatterbox (che gestisce numeri come testo) ma presente per SystemTTS (macOS `say`) e Piper, che sono i motori effettivamente in uso (`main.py:549` usa `use_piper_tts=False` → SystemTTS).

### Fix Proposto
Aggiungere una funzione `preprocess_for_tts(text: str) -> str` in `tts.py` (o in un modulo dedicato `tts_normalizer.py`) che:
1. Intercetta numeri telefonici italiani (10 cifre con pattern `3[0-9]{9}` o `0[0-9]{8,9}`)
2. Li espande cifra per cifra separati da spazio: `"3807769822"` → `"3 8 0 7 7 6 9 8 2 2"`
3. Viene chiamata in `TTSCache.synthesize()` prima di delegare al motore sottostante

```python
# tts.py — aggiungere sopra la classe TTSCache
import re

_PHONE_RE = re.compile(r'\b((?:\+39|0039)?[3][0-9]{8,9}|0[0-9]{8,9})\b')

def preprocess_for_tts(text: str) -> str:
    """
    Pre-elabora testo prima della sintesi TTS.
    Espande numeri telefonici cifra per cifra per evitare
    che i motori TTS li leggano come numeri interi.
    """
    def expand_phone(m: re.Match) -> str:
        digits = re.sub(r'\D', '', m.group(0))
        return ' '.join(digits)
    return _PHONE_RE.sub(expand_phone, text)
```

Chiamarla in `TTSCache.synthesize()`:
```python
async def synthesize(self, text: str) -> bytes:
    key = text.strip()
    processed = preprocess_for_tts(key)  # <-- aggiungere
    if processed in self._cache:
        ...
    audio = await self._engine.synthesize(processed)  # usa testo processato
    self._cache[processed] = audio
    return audio
```

Oppure, più semplicemente, applicarla solo ai template che contengono numeri di telefono in `booking_state_machine.py:533`:
```python
"confirm_phone_number": "Ho capito il numero {phone}, è corretto?",
```
E nel handler:
```python
phone_spaced = ' '.join(self.context.client_phone)  # "3807769822" → "3 8 0 7 7 6 9 8 2 2"
response=TEMPLATES["confirm_phone_number"].format(phone=phone_spaced)
```

**Raccomandazione**: fix in `tts.py` è più robusto (copre tutti i casi futuri). Fix in `booking_state_machine.py:3004` è più rapido.

### Effort Stimato
- Fix puntuale in `booking_state_machine.py`: 15 minuti
- Fix sistematico in `tts.py`: 30 minuti + 2 test

### Acceptance Criteria
- `preprocess_for_tts("Ho capito 3807769822, è corretto?")` → `"Ho capito 3 8 0 7 7 6 9 8 2 2, è corretto?"`
- Il TTS vocalizza il numero cifra per cifra
- Test: `pytest tests/test_tts.py -k test_phone_formatting`

---

## PROBLEMA 2 — Cliente Non Riconosciuto Dopo Registrazione Stessa Sessione

### Root Cause (file:linea)
**Il `client_id` viene salvato correttamente nel context** (`orchestrator.py:1122`):
```python
self.booking_sm.context.client_id = create_result.get("id")
```
Tuttavia, il context `booking_sm.context` viene **resettato** quando il cliente dice cose che fanno tornare il flusso a L2 senza session_id corretto, oppure tra sessioni diverse.

Il problema reale è un **doppio percorso di reset inconsistente**:

1. **Percorso A (reset implicito)**: `orchestrator.py:457-477` — se `session_id` non è in `_sessions` dict, chiama `await self.start_session()` che a sua volta chiama `self.booking_sm.reset()` (`orchestrator.py:398`). Se la sessione torna con un session_id diverso da quello attivo, il booking_sm viene resettato e `client_id` viene perso.

2. **Percorso B (client_name vs client_id)**: Quando il cliente nella stessa sessione dice "avevamo già fatto la registrazione", il flusso torna a IDLE perché la FSM è in COMPLETED (o in un secondo giro in IDLE). `_handle_idle` non verifica se `client_id` è già nel context quando `client_name` è presente e `client_id` è assente. Questo causa un nuovo lookup DB.

3. **Reset parziale in booking_sm.reset()** (`booking_state_machine.py:596-612`): il `client_phone` viene preservato esplicitamente ma non viene documentato se `client_id` e `client_name` sopravvivono. Leggendo il codice:

```python
def reset(self, full_reset: bool = False) -> None:
    """Reset state machine to IDLE."""
    # ...
    client_phone = self.context.client_phone  # preserva telefono
    # self.context = BookingContext()  ← RESET COMPLETO: azzera client_id!
    self.context.client_phone = client_phone  # ripristina solo telefono
```

Quindi `client_id` viene **perso** ad ogni `booking_sm.reset()`.

4. La chiamata a `start_session()` chiama `self.booking_sm.reset()` → `client_id = None`. Se dopo la registrazione (fine primo booking) l'utente dice qualcosa che fa girare `process()` senza session_id, viene chiamata `start_session()` → `booking_sm.reset()` → `client_id` perso.

### Fix Proposto
In `orchestrator.py:start_session()` (riga ~398), **NON resettare il booking_sm se c'è già un client_id attivo**:

```python
# PRIMA DEL FIX (riga 398):
self.booking_sm.reset()

# DOPO IL FIX:
# Preserva client_id se stiamo solo riaprendo una sessione per lo stesso cliente
_saved_client_id = self.booking_sm.context.client_id
_saved_client_name = self.booking_sm.context.client_name
_saved_client_phone = self.booking_sm.context.client_phone
self.booking_sm.reset()
# Ripristina identità cliente se noto (per follow-up nella stessa chiamata)
if _saved_client_id:
    self.booking_sm.context.client_id = _saved_client_id
    self.booking_sm.context.client_name = _saved_client_name
    self.booking_sm.context.client_phone = _saved_client_phone
```

**Fix alternativo (più semplice)**: in `booking_state_machine.py:reset()`, preservare anche `client_id` e `client_name`:
```python
def reset(self, full_reset: bool = False) -> None:
    client_id = self.context.client_id
    client_name = self.context.client_name
    client_phone = self.context.client_phone
    client_surname = self.context.client_surname
    self.context = BookingContext()
    if not full_reset:
        self.context.client_id = client_id
        self.context.client_name = client_name
        self.context.client_phone = client_phone
        self.context.client_surname = client_surname
```

Poi usare `booking_sm.reset(full_reset=True)` solo in `/api/voice/reset` e `full_reset=False` dopo booking completato.

### Effort Stimato
30-45 minuti + test

### Acceptance Criteria
- Dopo `create_client`, il `client_id` rimane in context per tutta la durata della chiamata
- Secondo booking nella stessa sessione → "Bentornato Flavio!" (non "Mi dice il suo nome?")
- `pytest tests/test_booking_state_machine.py -k test_returning_client_same_session`

---

## PROBLEMA 3 — Registrazione Duplicata con Numero Diverso

### Root Cause (file:linea)
`orchestrator.py:1962-1999` — `_create_client()` chiama `POST /api/clienti/create` o il fallback SQLite. **Non esiste nessun controllo di deduplication per nome+telefono** nel voice agent.

Il fallback SQLite (`orchestrator.py:2001-2037`) esegue direttamente:
```python
conn.execute(
    """INSERT INTO clienti (id, nome, cognome, telefono, ...)
       VALUES (?, ?, ?, ?, ...)""",
    (client_id, nome, cognome, telefono, ...)
)
```
Nessun `INSERT OR IGNORE`, nessun `SELECT` preventivo.

Il problema riportato ("registrato con numero diverso ma DB mostra ancora il numero originale") suggerisce uno di questi scenari:
1. Il cliente esiste già nel DB → viene creato un duplicato con il nuovo numero → l'UI mostra il record originale (più vecchio)
2. Il `client_id` nel context è quello del vecchio record (trovato in fase di search) → il nuovo numero non viene mai scritto sul vecchio record

**Scenario più probabile**: dopo `_search_client` trova il cliente con `id=X`, il `client_id` viene salvato. Ma poi il flusso va a `REGISTERING_PHONE` (come se fosse nuovo cliente) e al `REGISTERING_CONFIRM` viene inviato `create_client` → crea **duplicato con ID nuovo** → ma `booking_sm.context.client_id` era già stato settato a `X` → il booking viene creato su `X`, mentre il duplicato con il nuovo numero rimane orfano.

### Fix Proposto
In `_create_client_sqlite_fallback()` e nell'endpoint HTTP Bridge, aggiungere upsert per nome+cognome:

```python
# Prima di INSERT, cerca se esiste già
cursor = conn.execute(
    "SELECT id FROM clienti WHERE LOWER(nome)=LOWER(?) AND LOWER(cognome)=LOWER(?) AND deleted_at IS NULL LIMIT 1",
    (nome, cognome)
)
existing = cursor.fetchone()
if existing:
    # Aggiorna telefono se fornito e diverso
    if telefono:
        conn.execute(
            "UPDATE clienti SET telefono=?, updated_at=? WHERE id=?",
            (telefono, now, existing[0])
        )
    return {"success": True, "id": existing[0], "updated": True}
# Altrimenti procedi con INSERT
```

Questo richiede anche di toccare l'HTTP Bridge (Rust). Per il voice agent, il fix al SQLite fallback è indipendente.

### Effort Stimato
45 minuti (solo SQLite fallback) / 2 ore (anche endpoint HTTP Bridge in Rust)

### Acceptance Criteria
- Se Flavio Rossi esiste nel DB, `create_client({nome:"Flavio", cognome:"Rossi", telefono:"3801234567"})` aggiorna il telefono invece di creare duplicato
- DB ha un solo record `Flavio Rossi` dopo la chiamata
- `pytest tests/test_booking_state_machine.py -k test_no_duplicate_client`

---

## PROBLEMA 4 — WhatsApp Conferma Non Arriva

### Root Cause (file:linea)
Il problema ha **due strati indipendenti**:

#### Strato 1 — Trigger condizionale al booking completion
`orchestrator.py:1357-1364`:
```python
if should_exit and not should_escalate:
    if (self.booking_sm.context.state == BookingState.COMPLETED or
        hasattr(self.booking_sm.context, 'state') and
        self._last_booking_data and not self._whatsapp_sent):
        await self._send_wa_booking_confirmation(self._last_booking_data)
```
Il WA viene inviato solo quando `should_exit=True` (fine chiamata). Se la chiamata non si chiude formalmente (utente non dice "grazie arrivederci" → `ASKING_CLOSE_CONFIRMATION` non viene triggerata), il WA non parte.

#### Strato 2 — WhatsApp client bloccato su `is_connected()` check
`whatsapp.py:534-540`:
```python
if not self.is_connected():
    return {
        "success": False,
        "error": "WhatsApp not connected",
    }
```
`is_connected()` legge `~/.whatsapp-session/status.json`. Se `whatsapp-service.cjs` non è in esecuzione (processo Node non avviato, o QR non scannerizzato), il file non esiste o contiene `"status": "disconnected"` → tutti gli invii falliscono silenziosamente.

`_send_wa_booking_confirmation` (`orchestrator.py:1889-1929`) non ha nessun log visibile in caso di `is_connected() == False` perché `send_message_async` → `send_message` ritorna `{"success": False, "error": "WhatsApp not connected"}` ma `_send_wa_booking_confirmation` controlla solo `result.get("success")` e logga un WARNING, non un errore visibile in produzione.

#### Strato 3 — `client_phone` può essere None per clienti nuovi
`orchestrator.py:1897-1900`:
```python
phone = self.booking_sm.context.client_phone
if not phone:
    logger.info("[WA] No phone number for client, skipping WA confirmation")
    return
```
Se il cliente è nuovo e il telefono viene salvato nel DB ma non nel context (per via del problema 2), il WA non viene mai inviato.

#### Strato 4 — `_last_booking_data` non include `client_name` e `client_phone`
`orchestrator.py:916`:
```python
self._last_booking_data = sm_result.booking
```
`sm_result.booking` è il dict prodotto dalla FSM e non include `client_name` o `client_phone` dal context. `_send_wa_booking_confirmation` usa `booking.get("client_name", "")` che sarà sempre vuoto.

### Fix Proposto
1. **Fix Strato 1**: Inviare WA subito dopo `booking_result.get("success")` (riga 913), non aspettare `should_exit`:
```python
if booking_result.get("success"):
    self._last_booking_data = sm_result.booking
    # Invia WA subito (fire-and-forget), non aspettare chiusura chiamata
    asyncio.ensure_future(self._send_wa_booking_confirmation(sm_result.booking))
    self._whatsapp_sent = True
```

2. **Fix Strato 4**: Arricchire `_last_booking_data` con dati dal context:
```python
self._last_booking_data = {
    **sm_result.booking,
    "client_name": self.booking_sm.context.client_name or "",
    "client_phone": self.booking_sm.context.client_phone or "",
}
```

3. **Fix Strato 2 (diagnostico)**: Aggiungere log esplicito se `whatsapp-service.cjs` non è running:
```python
# In _send_wa_booking_confirmation, prima del try:
if not self._wa_client.is_connected():
    logger.warning("[WA] WhatsApp non connesso — conferma NON inviata. Avviare whatsapp-service.cjs e scansionare QR.")
    return
```

### Effort Stimato
30 minuti (fix strati 1+4) / 1 ora con log migliorati

### Acceptance Criteria
- Dopo conferma booking, log mostra `[WA] Booking confirmation sent to 39XXXXXXXXX`
- Se WA non connesso, log mostra warning esplicito (non silenzio)
- `pytest tests/test_whatsapp.py -k test_booking_confirmation_sent`

---

## PROBLEMA 5 — Vertical Context Enforcement Mancante

### Root Cause (file:linea)
**Il sistema verticale è parzialmente implementato** — carica le FAQ ma NON fa enforcement dei servizi.

Percorso verticale attuale:
1. `main.py:487-492` — `verticale_id = config.get("verticale_id", "default")` — letto dal DB
2. `orchestrator.py:285,309` — `self._faq_vertical = self._extract_vertical_key(verticale_id)` — estratto da prefisso (es. `"salone_bella_vita"` → `"salone"`)
3. `orchestrator.py:1530-1540` — `load_faqs_for_vertical()` carica FAQ specifiche per verticale
4. `orchestrator.py:1551-1577` — `set_vertical()` permette di cambiare verticale a runtime

**Cosa MANCA**:
- **Nessun service guard**: il context vertice non filtra i servizi accettabili. `booking_state_machine.py` accetta qualsiasi stringa come servizio (`_handle_waiting_service` non ha whitelist). Un cliente che chiede "cambio olio" in un salone riceve risposta come se fosse un servizio valido.
- **Nessuna risposta "non siamo..."**: Il prompt LLM in `_build_llm_context()` (`orchestrator.py:1603-1626`) include `CAPACITA'` generiche ma non menziona "NON FACCIAMO cambio olio". Il sistema LLM potrebbe rispondere con "certamente!" se il modello non sa che il verticale è salone.
- **`DEFAULT_CONFIG["services"]`** (`main.py:65`) è `["Taglio", "Piega", "Colore", "Trattamenti"]` ma non viene mai usato per filtrare le richieste entranti.

**Risposta FAQ "siete un'officina?"**: va a L3 (FAQ) o L4 (Groq). Le FAQ del verticale `salone` non contengono questa domanda → va a L4 Groq. Il prompt LLM (`_build_llm_context`) non istruisce il modello su cosa il salone NON offre, quindi il Groq risponde ambiguamente.

### Fix Proposto
**Fase 1 — Service guard in booking_state_machine**:
Aggiungere `allowed_services: Optional[List[str]]` al context e validare in `_handle_waiting_service`:
```python
# In BookingContext (booking_state_machine.py):
allowed_services: Optional[List[str]] = None  # None = accetta tutto

# In _handle_waiting_service:
if self.context.allowed_services and extracted_service not in self.context.allowed_services:
    return StateMachineResult(
        next_state=BookingState.WAITING_SERVICE,
        response=f"Mi dispiace, non offriamo quel servizio. I nostri servizi sono: {', '.join(self.context.allowed_services[:5])}."
    )
```

**Fase 2 — Arricchire prompt LLM**:
In `_build_llm_context()`:
```python
if self._faq_vertical == "salone":
    context += "\nSEI: Un salone di parrucchiere. NON offri servizi di officina, medicina, palestra."
```

**Fase 3 — FAQ "chi siete" per verticale**:
Aggiungere nel FAQ JSON di ogni verticale una entry:
```json
{"question": "Cosa fate? Che tipo di attività siete?", "answer": "Siamo {{NOME_ATTIVITA}}, un salone di parrucchiere."}
```

### Effort Stimato
- Service guard: 1 ora
- FAQ verticale: 30 minuti per verticale (4 verticali = 2 ore)
- Prompt LLM enrichment: 30 minuti

### Acceptance Criteria
- "cambio olio" in un salone → "Mi dispiace, non offriamo quel servizio. I nostri servizi sono: Taglio, Piega, Colore..."
- "siete un'officina?" → risposta corretta che identifica il tipo di attività
- Test: `pytest tests/test_vertical_guard.py`

---

## PROBLEMA 6 — Content Filtering "Pompini"

### Root Cause (file:linea)
`italian_regex.py:416`:
```python
r"\b(?:scopare?|trombare?|pompa|pompino|sesso)\b",
```
La parola "pompini" (plurale) è inclusa nella lista `_SEVERE_PATTERNS`. Tuttavia, il pattern è `\bpompino\b` (singolare con `r"pompino"`), non `\bpompini\b`.

Verifica: il pattern usa `pompino` (singolare). Il plurale `pompini` NON è catturato dalla word boundary `\b` se il pattern non include il plurale.

**Percorso del problema**:
1. Utente dice "pompini" → `prefilter(user_input)` in `orchestrator.py:493` chiama `check_content(text)` in `italian_regex.py:431`
2. `check_content` controlla `_SEVERE_COMPILED` — il pattern `pompino` NON matcha `pompini`
3. `content.severity == CLEAN` → nessun blocco
4. Il testo arriva alla FSM in stato `WAITING_SERVICE`
5. `_handle_waiting_service` tenta di matchare "pompini" come servizio — l'entity extractor cerca il servizio più simile → trova "Trattamenti" (fallback generico)

**Verifica pattern regex**:
```python
import re
pattern = re.compile(r"\b(?:scopare?|trombare?|pompa|pompino|sesso)\b", re.IGNORECASE)
pattern.search("pompini")  # → None (non matcha!)
pattern.search("pompino")  # → Match
```
`pompino` senza `s?` o `i?` alla fine non cattura il plurale.

### Fix Proposto
In `italian_regex.py`, correggere il pattern per catturare singolare e plurale:
```python
# PRIMA:
r"\b(?:scopare?|trombare?|pompa|pompino|sesso)\b"

# DOPO:
r"\b(?:scopare?|trombare?|pompa|pompin[oi]|sesso)\b"
```
O più esplicitamente:
```python
r"\b(?:scopare?|trombare?|pompa|pompini?|sesso)\b"
```

Dove `pompini?` matcha sia `pompino` che `pompini`.

Andrebbe anche aggiunto un test:
```python
def test_severe_content_plural():
    result = check_content("vorrei dei pompini")
    assert result.severity == ContentSeverity.SEVERE
```

### Effort Stimato
5 minuti (fix) + 10 minuti (test) = 15 minuti totali

### Acceptance Criteria
- `check_content("vorrei dei pompini").severity == ContentSeverity.SEVERE`
- `check_content("un pompino").severity == ContentSeverity.SEVERE`
- La sessione termina con "non posso continuare con questo tipo di linguaggio"
- `pytest tests/test_italian_regex.py -k test_content_filter_severe`

---

## DOMANDA STRATEGICA — Vertical Knowledge Base da Licenza

### Stato Attuale dell'Implementazione

Il sistema verticale è **parzialmente implementato**. Ecco lo stato end-to-end:

#### Cosa è implementato
1. **Verticale ID dalla licenza/DB**: `main.py:487-492` legge `verticale_id` dal DB (via HTTP Bridge o config file). Se il Bridge è offline, cade su `"default"`.
2. **FAQ loader per verticale**: `vertical_loader.py` — 5 verticali: `salone`, `wellness`, `medical`, `auto`, `altro`. File JSON in `voice-agent/data/`.
3. **Variable substitution nelle FAQ**: `{{NOME_ATTIVITA}}`, `{{ORARI_APERTURA}}` ecc. vengono sostituiti con valori dal DB.
4. **Switch verticale a runtime**: `orchestrator.set_vertical(vertical)` cambia verticale e ricarica FAQ. Usato nei test via `POST /api/voice/reset {"vertical": "medical"}`.
5. **Mappa verticale**: `_extract_vertical_key()` mappa `"salone_bella_vita"` → `"salone"`, ma usa SOLO il prefisso — nessun mapping da licenza tier.

#### Cosa NON è implementato
1. **Service guard basato su verticale**: ASSENTE (vedi Problema 5)
2. **Ora di apertura/chiusura dal DB per verticale**: Parzialmente — caricato in config ma non usato per bloccare prenotazioni fuori orario
3. **Operatori per verticale**: Non caricati dinamicamente — solo la FSM li cerca via HTTP Bridge
4. **Greeting personalizzato per verticale**: Il greeting usa `business_name` ma non include varianti verticale-specifiche ("sono Sara del Salone..." vs "sono Sara dello Studio Medico...")
5. **Licenza → verticale**: NON collegato. La licenza Ed25519 verifica solo tier (Base/Pro/Enterprise), non il verticale. Il verticale viene letto dalla tabella `impostazioni` del DB (`categoria_attivita`), NON dalla licenza. Quindi una licenza Base per un salone potrebbe tecnicamente essere usata per un'officina senza vincoli software.

#### Tabella `setup_config` nel DB
Non esiste `setup_config` come tabella separata — i dati sono nella tabella `impostazioni` (chiave/valore). Il voice agent legge da `impostazioni`:
- `nome_attivita` → business_name
- `whatsapp_number` → per conferme WA
- `telefono` → per escalation
- `email`
- `categoria_attivita` → verticale_id

Il `verticale_id` per le FAQ viene costruito da `categoria_attivita` tramite `_extract_vertical_key()`.

---

## GAP ASSESSMENT — Enterprise Level

| Feature | Stato | Gap |
|---------|-------|-----|
| TTS phone formatting | MANCANTE | Ogni numero di telefono viene letto male |
| Client persistence in-session | PARZIALE | `client_id` perso dopo reset booking |
| Deduplication cliente | ASSENTE | Crea duplicati senza controllo |
| WhatsApp send trigger | DIFETTOSO | Non inviato se chiamata non chiusa formalmente |
| Service guard per verticale | ASSENTE | Accetta servizi OOV qualsiasi |
| Content filter plurali | BUG | `pompini` non bloccato (solo `pompino`) |
| Verticale da licenza | DISACCOPPIATO | Non collegato alla licenza Ed25519 |
| Greeter verticale-specific | ASSENTE | Sara si presenta uguale per tutti i verticali |

---

## PRIORITA' IMPLEMENTAZIONE

| Priorità | Problema | Severity | Effort | Impact |
|----------|----------|----------|--------|--------|
| P1 | Problema 6: Content filter | CRITICO | 15 min | Evita contenuto inappropriato in produzione |
| P2 | Problema 1: TTS phone | ALTO | 30 min | UX ogni registrazione cliente |
| P3 | Problema 4: WA non inviato (strati 1+4) | ALTO | 30 min | Feature promessa non funziona |
| P4 | Problema 2: Client_id perso | MEDIO | 45 min | Confusione utente in chiamata |
| P5 | Problema 3: Duplicati cliente | MEDIO | 1 ora | Integrità DB |
| P6 | Problema 5: Vertical guard | BASSO-MEDIO | 3 ore | Enterprise credibility |

**Ordine di sessione raccomandato**:
1. Fix P1+P2+P4 (content filter + TTS phone + client_id) → 90 minuti totali, unico commit
2. Fix P3 (WA trigger) → 30 minuti, commit separato
3. Fix P5 (dedup) → 1 ora, va anche nel Rust HTTP Bridge
4. P6 (vertical guard) → sessione dedicata, impatta 4 file JSON + FSM

---

## Note Implementative

### File da modificare per ogni fix
| Fix | File | Riga approssimativa |
|-----|------|---------------------|
| P6: content filter | `src/italian_regex.py` | 416 |
| P1: TTS phone | `src/tts.py` | ~487 (TTSCache.synthesize) |
| P4a: WA trigger immediato | `src/orchestrator.py` | 913 |
| P4b: _last_booking_data arricchito | `src/orchestrator.py` | 916 |
| P2: client_id reset | `src/booking_state_machine.py` | ~596 (reset method) |
| P3: dedup | `src/orchestrator.py` | ~2001 (_create_client_sqlite_fallback) |
| P5: service guard | `src/booking_state_machine.py` | BookingContext + _handle_waiting_service |

### Test da aggiungere
- `tests/test_tts.py` → `test_phone_number_formatting`
- `tests/test_italian_regex.py` → `test_severe_content_plural`
- `tests/test_booking_state_machine.py` → `test_client_id_persists_after_booking`
- `tests/test_booking_state_machine.py` → `test_no_duplicate_client_creation`
- `tests/test_orchestrator.py` → `test_whatsapp_sent_after_booking`
