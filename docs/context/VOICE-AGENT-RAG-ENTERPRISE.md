# FLUXION Voice Agent RAG - Enterprise Production Specification v3.0

**Documento tecnico enterprise**: Implementazione conversazionale per prenotazioni appuntamenti
**Data**: Gennaio 2026
**Stack**: Tauri 2.x (Rust) + React 19 + Python 3.11 + SQLite + Groq API
**Versione**: 3.0 Enterprise Production-Ready
**GDPR Compliance**: Audit logging + data retention policies

---

## 1. ARCHITETTURA SISTEMA

### 1.1 Diagramma Flusso Completo

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19 + Tauri)                        │
│  ┌─────────────────┐  ┌───────────────┐  ┌─────────────────────────────┐ │
│  │ Voice Capture   │→ │ Groq Whisper  │→ │ HTTP POST to Python:3002   │ │
│  │ (Web Audio API) │  │ STT (cloud)   │  │ /api/voice/process         │ │
│  └─────────────────┘  └───────────────┘  └─────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ Text
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              VOICE AGENT PIPELINE (Python 3.11) - localhost:3002          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 1. SPECIAL COMMAND CHECK (annulla, indietro, aiuto)                │ │
│  │    - Se match → esegui comando, skip classification                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 2. CORRECTION DETECTION ("no, non X, volevo dire Y")               │ │
│  │    - Se match → aggiorna slot, conferma correzione                 │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 3. INTENT CLASSIFICATION (Groq Mixtral - 400ms)                    │ │
│  │    ├─ prenotazione (>= 0.7) → Booking Flow                         │ │
│  │    ├─ cancella (>= 0.7) → Cancellation Flow                        │ │
│  │    ├─ modifica (>= 0.7) → Modification Flow                        │ │
│  │    ├─ info (>= 0.7) → RAG Handler                                  │ │
│  │    ├─ conferma/nega → Continue current flow                        │ │
│  │    └─ < 0.5 confidence → Ask to repeat (max 3x → handoff)          │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 4. SESSION RECOVERY (SQLite persistence)                           │ │
│  │    ├─ Load session from voice_sessions table                       │ │
│  │    ├─ Check TTL (10 minutes)                                       │ │
│  │    └─ Restore conversation context                                 │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 5. SLOT FILLING (conversational)                                   │ │
│  │    ├─ cliente_id (disambiguazione se >1)                           │ │
│  │    ├─ servizi (array multi-servizio)                               │ │
│  │    ├─ data (validazione orari + festivi)                           │ │
│  │    ├─ ora (validazione pausa pranzo)                               │ │
│  │    └─ operatore_id (preferenza cliente)                            │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 6. CLIENT DISAMBIGUATION (if needed)                               │ │
│  │    ├─ Search: POST /api/clienti/search                             │ │
│  │    ├─ If count > 1: show list with data_nascita                    │ │
│  │    ├─ Accept: number, date, phone ending                           │ │
│  │    └─ If count = 0: offer registration                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 7. AVAILABILITY CHECK (MANDATORY)                                  │ │
│  │    ├─ Check: giorni_festivi table                                  │ │
│  │    ├─ Check: orari_lavoro (apertura/chiusura/pausa)                │ │
│  │    ├─ Check: MIN_ADVANCE = 60 minutes                              │ │
│  │    ├─ Check: MAX_ADVANCE = 90 days                                 │ │
│  │    ├─ Check: existing appointments (conflicts)                     │ │
│  │    ├─ If unavailable: propose 3 alternatives                       │ │
│  │    └─ If all refused: offer waitlist (VIP priority)                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 8. BOOKING CONFIRMATION                                            │ │
│  │    ├─ Recap: cliente, servizi, data, ora, operatore                │ │
│  │    ├─ Ask explicit confirmation                                    │ │
│  │    ├─ If yes: POST /api/appuntamenti/create                        │ │
│  │    └─ Send WhatsApp confirmation (async, non-blocking)             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 9. TTS GENERATION (Piper - offline)                                │ │
│  │    ├─ Model: it_IT-paola-medium                                    │ │
│  │    ├─ Speed: 1.1x                                                  │ │
│  │    └─ Fallback: text-only if TTS fails                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ 10. AUDIT LOGGING (GDPR)                                           │ │
│  │     ├─ Log: session_id, user_input, intent, response               │ │
│  │     ├─ Retention: 30 days, then anonymize                          │ │
│  │     └─ Stats: update voice_agent_stats                             │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│               BACKEND API (Rust/Tauri) - localhost:3001                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ ENDPOINTS:                                                          │ │
│  │  POST /api/clienti/search          POST /api/clienti/create        │ │
│  │  POST /api/appuntamenti/create     POST /api/appuntamenti/disponib │ │
│  │  PUT  /api/appuntamenti/{id}       DELETE /api/appuntamenti/{id}   │ │
│  │  POST /api/waitlist/add            GET /api/operatori/list         │ │
│  │  GET  /api/settings/nome_attivita  GET /api/settings/orari_lavoro  │ │
│  │  GET  /api/settings/giorni_festivi POST /api/whatsapp/send-template│ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ SQLite Database (fluxion.db)                                        │ │
│  │  clienti, appuntamenti, operatori, servizi, orari_lavoro,          │ │
│  │  giorni_festivi, voice_sessions, voice_audit_log, waitlist         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. INTENT CLASSIFICATION

### 2.1 Definizione Intent

| Intent | Keywords | Confidence Min | Azione |
|--------|----------|----------------|--------|
| `prenotazione` | prenota, appuntamento, fissa, libro, slot, vorrei | 0.7 | Slot filling → booking |
| `cancella` | cancella, disdetta, annulla, elimina, tolgo | 0.7 | Search → confirm → delete |
| `modifica` | modifica, sposta, cambia, rinvia, posticipa | 0.7 | Search → edit → confirm |
| `info` | orari, prezzi, quanto, come, dove, cosa, servizi | 0.7 | RAG query |
| `saluto` | ciao, buongiorno, salve, buonasera | 0.8 | Greeting |
| `conferma` | sì, ok, va bene, confermo, esatto, certo | 0.8 | Confirm pending |
| `nega` | no, annulla, sbagliato, ricominciamo | 0.8 | Cancel/restart |
| `operatore` | operatore, persona, umano, parlo con | 0.8 | Handoff |

### 2.2 Synonym Normalization

```python
SYNONYMS = {
    "prenotazione": ["prenota", "prenotare", "fissa", "fissare", "libro", "prendo", "metti", "mettimi"],
    "cancella": ["cancella", "cancellare", "disdetta", "disdire", "annulla", "annullare", "tolgo", "togliere", "elimina"],
    "modifica": ["modifica", "modificare", "sposta", "spostare", "cambia", "cambiare", "rinvia", "posticipa", "anticipa"],
    "conferma": ["sì", "si", "ok", "okay", "va bene", "confermo", "esatto", "giusto", "certo", "perfetto"],
    "nega": ["no", "non", "sbagliato", "errore", "annulla", "ricominciamo", "stop", "basta"]
}
```

### 2.3 Confidence Handling

```
Confidence >= 0.8: Procedi direttamente
Confidence 0.5-0.8: "Ho capito che vuoi {intent}. È corretto?"
Confidence < 0.5: "Non ho capito bene. Puoi ripetere?"

Se 3 turni consecutivi < 0.5:
  "Mi sembra una richiesta complessa. Preferisci parlare con un operatore?"
```

---

## 3. SPECIAL COMMANDS

### 3.1 Comandi Mid-Flow

| Comando | Triggers | Azione |
|---------|----------|--------|
| `annulla` | "annulla", "ricominciamo", "stop", "basta", "lascia stare" | Reset sessione |
| `indietro` | "indietro", "torna", "precedente", "correggo" | Torna a slot precedente |
| `aiuto` | "aiuto", "help", "cosa puoi fare", "come funziona" | Mostra capabilities |
| `ripeti` | "ripeti", "non ho capito", "come?", "cosa hai detto" | Ripeti ultima risposta |
| `umano` | "operatore", "persona", "umano", "qualcuno vero" | Handoff |

### 3.2 Gestione Correzioni

Pattern riconosciuti:
- "No, non {X}, volevo dire {Y}"
- "Anzi, meglio {Y}"
- "Ho sbagliato, è {Y}"
- "Correggo: {Y}"

```python
CORRECTION_PATTERNS = [
    r"no,?\s*non\s+(.+?),?\s*(?:volevo dire|intendevo|è)\s+(.+)",
    r"anzi,?\s*(?:meglio|preferisco)\s+(.+)",
    r"(?:ho sbagliato|mi sono sbagliato),?\s*(?:è|volevo)\s+(.+)",
    r"correggo:?\s*(.+)"
]
```

---

## 4. SLOT FILLING

### 4.1 Slots per Intent

**PRENOTAZIONE:**
| Slot | Tipo | Required | Validazione |
|------|------|----------|-------------|
| cliente_id | int | Sì | Esistente o nuovo |
| cliente_nome | string | Sì | Min 2 char |
| cliente_telefono | string | Sì | Pattern: 3XX XXX XXXX |
| servizi | array | Sì | [{servizio_id, nome, durata}] |
| data | date | Sì | YYYY-MM-DD, non passata, non festiva |
| ora | time | Sì | HH:MM, dentro orari, fuori pausa |
| operatore_id | int | No | Verifica disponibilità |
| note | string | No | Max 500 char |

**CANCELLAZIONE:**
| Slot | Tipo | Required |
|------|------|----------|
| appuntamento_id | int | Sì |
| conferma | bool | Sì |

**MODIFICA:**
| Slot | Tipo | Required |
|------|------|----------|
| appuntamento_id | int | Sì |
| nuova_data | date | No |
| nuova_ora | time | No |

### 4.2 Estrazione Data Italiana

```python
DATE_PATTERNS = {
    "oggi": lambda: date.today(),
    "domani": lambda: date.today() + timedelta(days=1),
    "dopodomani": lambda: date.today() + timedelta(days=2),
    "lunedì": lambda: next_weekday(0),
    "martedì": lambda: next_weekday(1),
    # ...
    r"(\d{1,2})\s*(gennaio|febbraio|marzo|...)": parse_italian_date,
    r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?": parse_numeric_date,
}
```

### 4.3 Estrazione Ora Italiana

```python
TIME_PATTERNS = {
    r"(\d{1,2}):(\d{2})": lambda m: f"{m[1].zfill(2)}:{m[2]}",
    r"le\s*(\d{1,2})(?:\s*e\s*(\d{2}))?": parse_italian_time,
    r"(\d{1,2})\s*(?:di|del)\s*(mattina|pomeriggio|sera)": parse_period_time,
    "mezzogiorno": lambda: "12:00",
    "mezzanotte": lambda: "00:00",
}
```

---

## 5. DISAMBIGUAZIONE CLIENTE

### 5.1 Flow

```
1. User: "Mi chiamo Marco Rossi"
2. System: POST /api/clienti/search {nome: "Marco Rossi"}
3. Response: count = 2

4. System: "Ho trovato 2 clienti con questo nome:
   1. Marco Rossi, nato il 15/03/1985 - 328 456 7890
   2. Marco Rossi, nato il 22/07/1990 - 328 123 4567

   Quale sei? Dimmi il numero o la tua data di nascita."

5. User: "Sono il primo" | "1985" | "15 marzo" | "...7890"

6. System: Match → cliente_id = X
```

### 5.2 Matching Logic

```python
def match_disambiguation_response(response: str, clients: List[Dict]) -> Optional[Dict]:
    response = response.lower().strip()

    # Try numeric (1, 2, 3...)
    if match := re.match(r"(\d+)", response):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(clients):
            return clients[idx]

    # Try ordinal ("primo", "secondo"...)
    ordinals = {"primo": 0, "secondo": 1, "terzo": 2, "quarto": 3}
    for word, idx in ordinals.items():
        if word in response and idx < len(clients):
            return clients[idx]

    # Try date of birth
    for client in clients:
        dob = client.get("data_nascita", "")
        if dob:
            # Match year (1985, 85)
            year = dob.split("-")[0]
            if year in response or year[-2:] in response:
                return client
            # Match formatted date
            if dob.replace("-", "/") in response:
                return client

    # Try phone ending
    for client in clients:
        phone = client.get("telefono", "")
        if phone and phone[-4:] in response:
            return client

    return None
```

---

## 6. VERIFICA DISPONIBILITÀ

### 6.1 Controlli Obbligatori

```python
async def check_availability(
    data: date,
    ora: time,
    durata_minuti: int,
    operatore_id: Optional[int] = None
) -> AvailabilityResult:

    # 1. Giorno festivo?
    festivo = await db.fetchone(
        "SELECT nome FROM giorni_festivi WHERE data = ?", (data,)
    )
    if festivo:
        return Unavailable(f"Siamo chiusi per {festivo['nome']}")

    # 2. Giorno lavorativo?
    weekday = data.weekday()  # 0=lunedì
    orari = await get_orari_lavoro(weekday)
    if not orari or not orari.aperto:
        return Unavailable(f"Siamo chiusi il {GIORNI[weekday]}")

    # 3. Dentro orario apertura?
    ora_fine = (datetime.combine(data, ora) + timedelta(minutes=durata_minuti)).time()
    if ora < orari.apertura:
        return Unavailable(f"Apriamo alle {orari.apertura}")
    if ora_fine > orari.chiusura:
        return Unavailable(f"Chiudiamo alle {orari.chiusura}")

    # 4. Fuori pausa pranzo?
    if orari.pausa_inizio and orari.pausa_fine:
        if time_overlaps(ora, ora_fine, orari.pausa_inizio, orari.pausa_fine):
            return Unavailable(
                f"Quell'orario cade in pausa pranzo ({orari.pausa_inizio}-{orari.pausa_fine})"
            )

    # 5. Anticipo minimo (60 minuti)?
    now = datetime.now()
    booking_dt = datetime.combine(data, ora)
    if booking_dt < now + timedelta(minutes=60):
        return Unavailable("Serve almeno 1 ora di anticipo per prenotare")

    # 6. Anticipo massimo (90 giorni)?
    if data > date.today() + timedelta(days=90):
        return Unavailable("Puoi prenotare fino a 3 mesi in anticipo")

    # 7. Conflitti con altri appuntamenti?
    conflitti = await check_conflicts(data, ora, ora_fine, operatore_id)
    if conflitti:
        alternatives = await find_alternatives(data, durata_minuti, operatore_id, limit=3)
        return Unavailable(alternatives=alternatives)

    return Available(data=data, ora=ora, operatore_id=operatore_id)
```

### 6.2 Slot Alternativi

```python
async def find_alternatives(
    data: date,
    durata_minuti: int,
    operatore_id: Optional[int],
    limit: int = 3
) -> List[Dict]:
    alternatives = []

    # Try same day, different times
    for ora in generate_time_slots(data):
        if await is_slot_free(data, ora, durata_minuti, operatore_id):
            alternatives.append({"data": data, "ora": ora, "operatore_id": operatore_id})
            if len(alternatives) >= limit:
                return alternatives

    # Try next 7 days
    for days_ahead in range(1, 8):
        next_date = data + timedelta(days=days_ahead)
        if not await is_working_day(next_date):
            continue
        for ora in generate_time_slots(next_date):
            if await is_slot_free(next_date, ora, durata_minuti, operatore_id):
                alternatives.append({"data": next_date, "ora": ora, "operatore_id": operatore_id})
                if len(alternatives) >= limit:
                    return alternatives

    return alternatives
```

---

## 7. WAITLIST CON PRIORITÀ VIP

### 7.1 Schema

```sql
CREATE TABLE waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    servizio_id INTEGER NOT NULL,
    data_preferita DATE NOT NULL,
    ora_preferita TIME,
    operatore_preferito_id INTEGER,
    priorita TEXT DEFAULT 'NORMAL',  -- NORMAL, HIGH, VIP
    priorita_score INTEGER DEFAULT 0, -- VIP=100, HIGH=50, NORMAL=0
    status TEXT DEFAULT 'WAITING',    -- WAITING, NOTIFIED, BOOKED, EXPIRED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);
```

### 7.2 Priorità Automatica

```python
async def add_to_waitlist(
    cliente_id: int,
    servizio_id: int,
    data_preferita: date,
    ora_preferita: Optional[time] = None
) -> Dict:
    # Check if client is VIP
    cliente = await get_cliente(cliente_id)
    priorita = "VIP" if cliente.is_vip else "NORMAL"
    priorita_score = 100 if cliente.is_vip else 0

    result = await db.execute("""
        INSERT INTO waitlist (cliente_id, servizio_id, data_preferita, ora_preferita, priorita, priorita_score, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+30 days'))
    """, (cliente_id, servizio_id, data_preferita, ora_preferita, priorita, priorita_score))

    # Get position
    position = await db.fetchone("""
        SELECT COUNT(*) + 1 as pos FROM waitlist
        WHERE data_preferita = ? AND servizio_id = ?
        AND (priorita_score > ? OR (priorita_score = ? AND created_at < ?))
    """, (data_preferita, servizio_id, priorita_score, priorita_score, result.created_at))

    return {
        "waitlist_id": result.id,
        "position": position["pos"],
        "priorita": priorita
    }
```

---

## 8. MULTI-SERVIZIO

### 8.1 Parsing

```python
async def parse_services(text: str) -> List[Dict]:
    """Parse multi-service request like 'taglio, colore e piega'"""

    # Normalize separators
    text = text.lower()
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\s+e\s+", ", ", text)
    text = re.sub(r"\s+più\s+", ", ", text)

    service_names = [s.strip() for s in text.split(",") if s.strip()]

    services = []
    for name in service_names:
        service = await find_service_by_name(name)
        if service:
            services.append({
                "servizio_id": service["id"],
                "nome": service["nome"],
                "durata_minuti": service["durata_minuti"]
            })

    return services

def calculate_total_duration(services: List[Dict]) -> int:
    return sum(s.get("durata_minuti", 0) for s in services)
```

---

## 9. REGISTRAZIONE NUOVO CLIENTE

### 9.1 Flow Conversazionale

```
System: "Non ho trovato nessun cliente con questo nome. Vuoi registrarti?"
User: "Sì"

System: "Perfetto! Qual è il tuo cognome?"
User: "Bianchi"
→ slots["cognome"] = "Bianchi"

System: "E il tuo numero di telefono?"
User: "328 456 7890"
→ slots["telefono"] = "3284567890" (normalized)

System: "Grazie! Vuoi dirmi anche la tua data di nascita? È opzionale."
User: "20 giugno 1995" | "No, preferisco non dirla"
→ slots["data_nascita"] = "1995-06-20" | None

System: "Perfetto, Alessia Bianchi! Ti ho registrato.
        Per utilizzare l'assistente vocale, accetti il trattamento dei dati secondo GDPR?"
User: "Sì"
→ voice_consent = True

→ POST /api/clienti/create
→ Continua con prenotazione
```

---

## 10. CONFERMA WHATSAPP

### 10.1 Post-Booking

```python
async def send_booking_confirmation(appuntamento: Dict):
    """Send WhatsApp confirmation after successful booking (non-blocking)"""
    try:
        await whatsapp_client.send_template(
            to=appuntamento["cliente_telefono"],
            template="booking_confirmation",
            params={
                "nome": appuntamento["cliente_nome"],
                "data": format_date_italian(appuntamento["data"]),
                "ora": appuntamento["ora"],
                "servizio": ", ".join(s["nome"] for s in appuntamento["servizi"]),
                "operatore": appuntamento.get("operatore_nome", ""),
                "codice": appuntamento["confirmation_code"]
            }
        )
        logger.info(f"WhatsApp confirmation sent for appointment {appuntamento['id']}")

        # Update appointment
        await db.execute(
            "UPDATE appuntamenti SET whatsapp_confirmed = 1, whatsapp_confirmed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (appuntamento["id"],)
        )
    except Exception as e:
        # Non-blocking: log warning but don't fail booking
        logger.warning(f"WhatsApp send failed for appointment {appuntamento['id']}: {e}")
```

---

## 11. SESSION MANAGEMENT

### 11.1 Schema

```sql
CREATE TABLE voice_sessions (
    id TEXT PRIMARY KEY,                    -- UUID
    cliente_id INTEGER,
    current_intent TEXT,
    current_step TEXT,
    slots JSON DEFAULT '{}',
    pending_disambiguation JSON,
    pending_alternatives JSON,
    history JSON DEFAULT '[]',
    failed_understanding_count INTEGER DEFAULT 0,
    total_turns INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    handoff_requested BOOLEAN DEFAULT FALSE,
    completed BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);

CREATE INDEX idx_sessions_expires ON voice_sessions(expires_at);
```

### 11.2 Session Lifecycle

```python
class SessionManager:
    TTL_MINUTES = 10

    async def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=self.TTL_MINUTES)

        await db.execute("""
            INSERT INTO voice_sessions (id, slots, history, expires_at)
            VALUES (?, '{}', '[]', ?)
        """, (session_id, expires_at))

        return session_id

    async def load_session(self, session_id: str) -> Optional[Dict]:
        row = await db.fetchone(
            "SELECT * FROM voice_sessions WHERE id = ?", (session_id,)
        )

        if not row:
            return None

        # Check expiration
        if row["expires_at"] and datetime.fromisoformat(row["expires_at"]) < datetime.now():
            await self.delete_session(session_id)
            return None

        return {
            "id": row["id"],
            "cliente_id": row["cliente_id"],
            "intent": row["current_intent"],
            "step": row["current_step"],
            "slots": json.loads(row["slots"] or "{}"),
            "history": json.loads(row["history"] or "[]"),
            "failed_count": row["failed_understanding_count"]
        }

    async def update_session(self, session_id: str, **updates):
        set_clauses = []
        values = []

        for key, value in updates.items():
            if key in ("slots", "history", "pending_disambiguation", "pending_alternatives"):
                set_clauses.append(f"{key} = ?")
                values.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(session_id)

        await db.execute(
            f"UPDATE voice_sessions SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
```

---

## 12. AUDIT LOGGING (GDPR)

### 12.1 Schema

```sql
CREATE TABLE voice_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT,
    user_input_hash TEXT,
    detected_intent TEXT,
    intent_confidence REAL,
    special_command TEXT,
    slots_extracted JSON,
    system_response TEXT,
    action_taken TEXT,
    action_result TEXT,
    error_message TEXT,
    latency_ms INTEGER,
    ip_address TEXT,

    FOREIGN KEY (session_id) REFERENCES voice_sessions(id)
);

CREATE INDEX idx_audit_session ON voice_audit_log(session_id);
CREATE INDEX idx_audit_timestamp ON voice_audit_log(timestamp);
```

### 12.2 Anonymization

```python
async def anonymize_old_logs(days: int = 30):
    """GDPR: Anonymize PII after retention period"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    result = await db.execute("""
        UPDATE voice_audit_log
        SET
            user_input = '[REDACTED]',
            system_response = '[REDACTED]',
            ip_address = '[REDACTED]'
        WHERE timestamp < ? AND user_input != '[REDACTED]'
    """, (cutoff,))

    logger.info(f"Anonymized {result.rowcount} audit log entries")
```

---

## 13. RAG HANDLER

### 13.1 FAQ Loading

```python
class RAGHandler:
    def __init__(self, config: Dict):
        self.embedding_model = SentenceTransformer(config.get("embedding_model", "all-MiniLM-L6-v2"))
        self.faq_documents = []
        self.index = None
        self.faq_mtime = None

    async def load_faq(self, faq_path: str = "data/faq_auto.md"):
        """Load FAQ with caching based on file mtime"""
        current_mtime = os.path.getmtime(faq_path)

        if self.faq_mtime == current_mtime:
            return  # Already loaded

        with open(faq_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse Q&A pairs
        pattern = r'###\s*(.+?)\n(.*?)(?=###|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        self.faq_documents = [
            {"question": q.strip(), "answer": a.strip()}
            for q, a in matches
        ]

        # Build FAISS index
        if self.faq_documents:
            embeddings = self.embedding_model.encode(
                [doc["question"] for doc in self.faq_documents],
                convert_to_numpy=True
            ).astype('float32')

            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)

        self.faq_mtime = current_mtime
        logger.info(f"Loaded {len(self.faq_documents)} FAQ entries")
```

### 13.2 Query

```python
async def answer_query(self, query: str, top_k: int = 3) -> str:
    if not self.index:
        return "Non ho informazioni disponibili su questo argomento."

    # Embed query
    query_embedding = self.embedding_model.encode(
        [query], convert_to_numpy=True
    ).astype('float32')

    # Search
    distances, indices = self.index.search(query_embedding, top_k)

    # Build context
    context_docs = [self.faq_documents[int(i)] for i in indices[0]]
    context = "\n\n".join([
        f"D: {doc['question']}\nR: {doc['answer']}"
        for doc in context_docs
    ])

    # Generate response
    response = await groq_client.chat(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Rispondi alla domanda usando il contesto. Sii breve e naturale."},
            {"role": "user", "content": f"CONTESTO:\n{context}\n\nDOMANDA: {query}"}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
```

---

## 14. TTS SERVICE

### 14.1 Piper Configuration

```python
class TTSService:
    def __init__(self):
        self.model = "it_IT-paola-medium"
        self.speed = 1.1
        self.sample_rate = 22050
        self.output_dir = "audio_output"
        os.makedirs(self.output_dir, exist_ok=True)

    async def synthesize(self, text: str) -> Optional[str]:
        """Generate speech with Piper TTS"""
        try:
            filename = f"{uuid.uuid4()}.wav"
            filepath = os.path.join(self.output_dir, filename)

            process = await asyncio.create_subprocess_exec(
                "piper",
                "--model", self.model,
                "--output_file", filepath,
                "--length_scale", str(1 / self.speed),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.communicate(input=text.encode('utf-8'))

            if process.returncode == 0:
                return filename
            else:
                logger.warning(f"Piper TTS failed with code {process.returncode}")
                return None

        except FileNotFoundError:
            logger.warning("Piper not found, TTS unavailable")
            return None
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
```

---

## 15. BUSINESS CONFIG

### 15.1 Dynamic Greeting

```python
async def get_greeting() -> str:
    """Get dynamic greeting with business name"""
    settings = await backend_client.get("/api/settings/nome_attivita")
    nome = settings.get("nome_attivita", "FLUXION")

    hour = datetime.now().hour
    if 5 <= hour < 12:
        saluto = "Buongiorno"
    elif 12 <= hour < 18:
        saluto = "Buon pomeriggio"
    else:
        saluto = "Buonasera"

    return f"{saluto}, sono Paola, l'assistente vocale di {nome}. Come posso aiutarla?"
```

---

## 16. ERROR HANDLING

### 16.1 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Service temporarily unavailable")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
```

### 16.2 Graceful Degradation

```python
FALLBACK_RESPONSES = {
    "groq_down": "Il servizio vocale è temporaneamente non disponibile. Puoi contattarci al {telefono}.",
    "backend_down": "Stiamo riscontrando un problema tecnico. Riprova tra qualche minuto.",
    "tts_down": None,  # Return text-only
    "db_down": "Non riesco ad accedere ai dati. Contatta il negozio direttamente."
}
```

---

## 17. HEALTH CHECK

```python
@app.get("/health")
async def health_check():
    checks = {}

    # Groq API
    try:
        await groq_client.models.list()
        checks["groq_api"] = "ok"
    except:
        checks["groq_api"] = "error"

    # Backend API
    try:
        await backend_client.get("/health")
        checks["backend_api"] = "ok"
    except:
        checks["backend_api"] = "error"

    # Database
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except:
        checks["database"] = "error"

    # Piper TTS
    try:
        result = await asyncio.create_subprocess_exec(
            "piper", "--help",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await result.communicate()
        checks["piper_tts"] = "ok" if result.returncode == 0 else "warning"
    except:
        checks["piper_tts"] = "warning"

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "components": checks,
        "timestamp": datetime.now().isoformat()
    }
```

---

## 18. PERFORMANCE TARGETS

| Metrica | Target | Critico |
|---------|--------|---------|
| Intent classification | < 500ms | < 800ms |
| Slot extraction | < 300ms | < 500ms |
| RAG query | < 1.5s | < 2.5s |
| API call | < 200ms | < 500ms |
| TTS generation | < 1s | < 2s |
| End-to-end (no TTS) | < 3s | < 5s |
| End-to-end (with TTS) | < 4s | < 6s |

---

## 19. TESTING CHECKLIST

### Unit Tests
- [ ] Intent classification accuracy >= 95%
- [ ] Slot extraction accuracy >= 90%
- [ ] Italian date parsing
- [ ] Italian phone validation
- [ ] Synonym normalization
- [ ] Correction pattern matching
- [ ] Special command detection

### Integration Tests
- [ ] Full booking flow (happy path)
- [ ] Booking with disambiguation
- [ ] Booking with alternatives
- [ ] Booking with waitlist
- [ ] New client registration
- [ ] Cancellation flow
- [ ] Modification flow
- [ ] RAG queries
- [ ] Session persistence
- [ ] WhatsApp notification

### Performance Tests
- [ ] Latency targets met
- [ ] 100 concurrent sessions
- [ ] Memory stability
- [ ] No connection leaks

### Security Tests
- [ ] Input sanitization
- [ ] Rate limiting
- [ ] GDPR anonymization

---

*Documento v3.0 - Enterprise Production Ready*
*Ultimo aggiornamento: Gennaio 2026*
