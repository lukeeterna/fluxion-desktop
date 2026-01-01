# 🆕 NUOVE FEATURE - Waitlist + WhatsApp Booking Automatico

**Data**: 2026-01-01 12:00
**Tipo**: Feature Request
**Fase Proposta**: 5 o 6
**Priorità**: ALTA (dopo Fase 4)

---

## 📋 REQUISITI FUNZIONALI

### 1. WAITLIST (Lista d'Attesa)

#### Scenario
Un cliente vuole prenotare uno slot già occupato → Si mette in **waitlist** per quello slot.

#### Workflow
```
1. Cliente richiede appuntamento (es: 2 gen ore 15:00, Taglio Capelli, Mario Barbiere)
2. Sistema verifica: Slot occupato ❌
3. Sistema propone: "Vuoi essere inserito in lista d'attesa?"
4. Cliente accetta → Inserito in waitlist

5. [EVENTO] Appuntamento originale viene cancellato
6. Sistema rileva: Slot 2 gen 15:00 si è liberato! ✅
7. Sistema invia WhatsApp al PRIMO in waitlist:
   "🔔 Buone notizie! Lo slot 2 gennaio ore 15:00 con Mario Barbiere si è liberato.
    Vuoi prenotarlo? Rispondi SI per confermare entro 15 minuti."

8a. Cliente risponde "SI" entro 15min → Appuntamento confermato ✅
8b. Cliente NON risponde → Passa al SECONDO in waitlist (ripeti step 7)
8c. Cliente risponde "NO" → Passa al SECONDO in waitlist
```

#### Database Schema

**Nuova Tabella**: `waitlist`

```sql
CREATE TABLE waitlist (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    operatore_id TEXT,
    data_desiderata TEXT NOT NULL,      -- "2026-01-02"
    ora_inizio_desiderata TEXT NOT NULL, -- "15:00"
    ora_fine_desiderata TEXT,            -- "16:00" (opzionale)
    durata_minuti INTEGER NOT NULL,
    priorita INTEGER NOT NULL DEFAULT 1, -- 1 = primo della lista, 2 = secondo, etc.
    stato TEXT NOT NULL CHECK(stato IN ('attivo', 'notificato', 'scaduto', 'convertito')) DEFAULT 'attivo',
    notificato_at TEXT,                  -- Timestamp invio WhatsApp
    scade_at TEXT,                       -- Timestamp scadenza risposta (notificato_at + 15min)
    convertito_appuntamento_id TEXT,     -- ID appuntamento se confermato
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id),
    FOREIGN KEY (convertito_appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX idx_waitlist_cliente ON waitlist(cliente_id);
CREATE INDEX idx_waitlist_data ON waitlist(data_desiderata);
CREATE INDEX idx_waitlist_stato ON waitlist(stato);
CREATE INDEX idx_waitlist_priorita ON waitlist(priorita);
```

#### Tauri Commands

```rust
// Get waitlist for a specific slot
#[tauri::command]
pub async fn get_waitlist(
    data_desiderata: String,
    ora_inizio: String,
    operatore_id: Option<String>,
) -> Result<Vec<WaitlistEntry>, String>

// Add cliente to waitlist
#[tauri::command]
pub async fn add_to_waitlist(
    cliente_id: String,
    servizio_id: String,
    operatore_id: Option<String>,
    data_desiderata: String,
    ora_inizio: String,
    durata_minuti: i64,
) -> Result<WaitlistEntry, String>

// Remove from waitlist
#[tauri::command]
pub async fn remove_from_waitlist(
    id: String
) -> Result<(), String>

// Notify next in waitlist (automatic trigger on appointment cancellation)
#[tauri::command]
pub async fn notify_waitlist_slot_available(
    appuntamento_id: String, // Appuntamento cancellato
) -> Result<(), String>
```

#### WhatsApp Integration

**Messaggio Notifica**:
```
🔔 Buone notizie!

Lo slot che desideravi si è liberato:
📅 Data: 2 gennaio 2026
🕐 Ora: 15:00
✂️ Servizio: Taglio Capelli
👤 Operatore: Mario Barbiere

Vuoi prenotarlo?
Rispondi SI per confermare entro 15 minuti.
```

**Gestione Risposta**:
- Risposta "SI" → Crea appuntamento automaticamente + Invia conferma
- Risposta "NO" → Marca waitlist come 'scaduto' + Notifica prossimo
- Nessuna risposta dopo 15min → Timeout + Notifica prossimo

#### UI Components

1. **WaitlistBadge** (nel calendario)
   - Badge arancione con numero di persone in waitlist per quello slot
   - Click → Apre WaitlistDialog

2. **WaitlistDialog**
   - Lista clienti in waitlist (ordinati per priorità)
   - Bottone "Aggiungi alla Lista"
   - Bottone "Rimuovi" (per ogni entry)
   - Stato (attivo/notificato/scaduto/convertito)

3. **AppuntamentoDialog - Add to Waitlist**
   - Quando slot occupato → Mostra bottone "Aggiungi alla Lista d'Attesa"
   - Click → Inserisce cliente in waitlist

---

### 2. WHATSAPP BOOKING AUTOMATICO (Gestione Predefinita)

#### Scenario
Gli appuntamenti vengono gestiti **principalmente tramite WhatsApp**, ma è possibile modificarli manualmente.

#### Workflow Booking via WhatsApp

```
1. Cliente invia WhatsApp: "Ciao, vorrei prenotare un taglio per domani alle 15"

2. [VOICE AGENT o NLP Parser]
   - Estrae intento: "prenotazione"
   - Estrae data: "domani" → 2026-01-02
   - Estrae ora: "15" → 15:00
   - Estrae servizio: "taglio" → ID servizio Taglio Capelli
   - Identifica cliente: numero WhatsApp → cerca in DB

3. Sistema verifica disponibilità:
   - get_appuntamenti(2026-01-02, operatore_id=auto)
   - check_conflicts(15:00, durata_servizio=30min)

4a. SLOT DISPONIBILE ✅
   → Crea appuntamento automaticamente
   → Invia conferma WhatsApp:
     "✅ Appuntamento confermato!
      📅 2 gennaio 2026, ore 15:00
      ✂️ Taglio Capelli (30min)
      👤 Operatore: Mario Barbiere
      💰 Prezzo: €25

      Ci vediamo!"

4b. SLOT OCCUPATO ❌
   → Invia WhatsApp:
     "❌ Mi dispiace, lo slot 2 gennaio ore 15:00 è già occupato.

      🕐 Slot disponibili per 2 gennaio:
      - 10:00
      - 12:30
      - 17:00

      Oppure vuoi essere inserito in lista d'attesa per le 15:00?
      Rispondi con l'orario desiderato o 'LISTA' per la lista d'attesa."

5. Cliente sceglie slot alternativo: "12:30"
   → Crea appuntamento per 12:30
   → Invia conferma
```

#### Parsing NLP (Natural Language Processing)

**Libreria Consigliata**: Groq Llama 3.3 70B (già disponibile in .env)

**Prompt Template**:
```
Estrai le informazioni di prenotazione dal seguente messaggio WhatsApp:

"{messaggio_cliente}"

Ritorna un JSON con:
{
  "intento": "prenotazione" | "modifica" | "cancellazione" | "info",
  "data": "YYYY-MM-DD",
  "ora": "HH:mm",
  "servizio": "nome_servizio",
  "note": "eventuali note"
}

Se l'informazione non è presente, usa null.
```

**Esempio**:
```
Input: "Ciao, vorrei prenotare un taglio per domani alle 15"
Output:
{
  "intento": "prenotazione",
  "data": "2026-01-02",
  "ora": "15:00",
  "servizio": "taglio",
  "note": null
}
```

#### Tauri Commands

```rust
// Parse WhatsApp message using LLM
#[tauri::command]
pub async fn parse_whatsapp_booking(
    message: String,
    cliente_phone: String,
) -> Result<BookingIntent, String>

// Auto-create appointment from WhatsApp
#[tauri::command]
pub async fn create_whatsapp_appointment(
    booking: BookingIntent,
) -> Result<Appuntamento, String>

// Send WhatsApp confirmation
#[tauri::command]
pub async fn send_whatsapp_booking_confirmation(
    appuntamento_id: String,
) -> Result<(), String>

// Get available slots for suggestion
#[tauri::command]
pub async fn get_available_slots(
    data: String,
    servizio_id: String,
    operatore_id: Option<String>,
) -> Result<Vec<String>, String> // ["10:00", "12:30", "17:00"]
```

#### WhatsApp Webhook Integration

**Provider**: Twilio WhatsApp Business API

**Webhook Endpoint** (Tauri backend può esporre endpoint locale):
```
POST http://localhost:3000/webhook/whatsapp
```

**Payload**:
```json
{
  "from": "whatsapp:+393281536308",
  "body": "Ciao, vorrei prenotare un taglio per domani alle 15",
  "timestamp": "2026-01-01T12:30:00Z"
}
```

**Handler**:
1. Ricevi messaggio WhatsApp
2. Parse con LLM (Groq)
3. Identifica cliente dal numero
4. Verifica disponibilità
5. Crea appuntamento o proponi alternative
6. Invia conferma WhatsApp

**NOTA**: Tauri desktop app NON può esporre endpoint HTTP pubblici.
**SOLUZIONE**: Usare **Tauri Plugin HTTP Server** (locale) + **Ngrok tunnel** per webhook development, oppure **Cloud Function** (Firebase/Vercel) come proxy.

---

### 3. MODIFICA MANUALE (UI Desktop)

#### Scenario
Anche se gli appuntamenti sono gestiti via WhatsApp, l'operatore può modificarli manualmente dall'UI desktop.

#### Features UI
1. **Badge "WhatsApp"** su appuntamenti creati via WA
   - Icona WhatsApp verde accanto all'orario
   - Hover → "Prenotato via WhatsApp"

2. **Log Chat WhatsApp**
   - Bottone "Visualizza Chat" nell'AppuntamentoDialog
   - Mostra conversazione WhatsApp relativa a quell'appuntamento
   - Read-only (per ora)

3. **Sync Bidirezionale**
   - Modifica manuale → Invia notifica WhatsApp:
     "⚠️ Il tuo appuntamento è stato modificato:
      Nuova data: 3 gennaio 2026, ore 16:00"
   - Cancellazione manuale → Invia notifica:
     "❌ Il tuo appuntamento del 2 gennaio ore 15:00 è stato cancellato.
      Contattaci per riprogrammare."

---

## 📊 DATABASE SCHEMA COMPLETO (Fasi 4-6)

```sql
-- Fase 4: Reminder Log
CREATE TABLE reminder_log (...); -- Già pianificato

-- Fase 5: Waitlist
CREATE TABLE waitlist (...);     -- Nuovo

-- Fase 6: WhatsApp Messages Log
CREATE TABLE whatsapp_messages (
    id TEXT PRIMARY KEY,
    cliente_id TEXT,
    appuntamento_id TEXT,
    twilio_sid TEXT,
    direction TEXT NOT NULL CHECK(direction IN ('inbound', 'outbound')),
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('sent', 'delivered', 'read', 'failed')),
    error_message TEXT,
    sent_at TEXT NOT NULL,
    delivered_at TEXT,
    read_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX idx_whatsapp_cliente ON whatsapp_messages(cliente_id);
CREATE INDEX idx_whatsapp_appuntamento ON whatsapp_messages(appuntamento_id);
CREATE INDEX idx_whatsapp_sent_at ON whatsapp_messages(sent_at);
```

---

## 🎯 PRIORITÀ IMPLEMENTAZIONE

### Fase 4 (IN CORSO)
- Stati appuntamenti + Filtri ✅
- Delete appuntamenti ✅
- Reminder WhatsApp manuali ✅

### Fase 5 (DOPO Fase 4)
- Waitlist completa
- Notifiche automatiche slot liberati
- Gestione priorità waitlist

### Fase 6 (DOPO Fase 5)
- WhatsApp Booking automatico (NLP parser)
- Webhook integration
- Log messaggi WhatsApp
- Sync bidirezionale UI ↔ WhatsApp

---

## 🔧 TECNOLOGIE RICHIESTE

### Backend (Rust)
- `reqwest` - HTTP client per Twilio API
- `serde_json` - JSON parsing
- `tokio` - Async runtime
- `chrono` - Date/time handling

### Frontend (React)
- TanStack Query - Data fetching
- Zod - Schema validation
- React Hook Form - Form handling

### External Services
- **Twilio WhatsApp Business API** (già in .env)
- **Groq Llama 3.3 70B** (per NLP parsing, già in .env)
- **Ngrok** (per webhook development, opzionale)

### Opzionale (Cloud)
- **Firebase Cloud Functions** - Webhook proxy
- **Vercel Serverless Functions** - Alternative proxy

---

## 📝 PROSSIMI STEP

1. **Completare Fase 4** (Stati + Delete + Reminder manuali)
2. **Test Fase 4** su iMac
3. **Pianificare Fase 5** dettagliata (Waitlist)
4. **Pianificare Fase 6** dettagliata (WhatsApp Booking Auto)
5. **Setup Twilio WhatsApp Sandbox** (già fatto in Fase 4.3)
6. **Test Groq LLM** per NLP parsing

---

*Feature request: 2026-01-01 12:00*
*Target implementazione: Fase 5-6 (dopo Fase 4)*
*Durata stimata: 5-7 giorni*
