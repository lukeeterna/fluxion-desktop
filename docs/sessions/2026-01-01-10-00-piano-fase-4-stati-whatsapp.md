# 📋 PIANO FASE 4 - Gestione Stati + WhatsApp Reminders

**Data**: 2026-01-01
**Fase**: 4
**Obiettivo**: Completare gestione stati appuntamenti + Sistema WhatsApp reminders

---

## 🎯 STATO ATTUALE (Fine Fase 3)

### ✅ GIÀ IMPLEMENTATO
- [x] CRUD appuntamenti completo (create, read, update)
- [x] Edit appuntamento (click su appuntamento → dialog apre in modalità edit)
- [x] Stati definiti: `bozza | confermato | completato | cancellato | no_show`
- [x] Calendario mensile con navigazione
- [x] Conflict detection per appuntamenti sovrapposti
- [x] Auto-fill prezzo/durata da servizio
- [x] Visualizzazione appuntamenti su griglia calendario
- [x] Legenda stati (Confermato/Completato/Cancellato) - SOLO visuale, non funzionale

### ❌ MANCANTE (Da implementare in Fase 4)
- [ ] Badge visuali stato su appuntamenti nel calendario
- [ ] Colori appuntamenti basati su STATO (attualmente solo servizio_colore)
- [ ] Filtro dropdown per stato (mostra solo confermati/completati/ecc.)
- [ ] Quick actions: bottoni cambio stato rapido ("Segna come completato")
- [ ] Delete appuntamento (soft delete con deleted_at)
- [ ] Conferma eliminazione + ripristino
- [ ] WhatsApp reminders automatici
- [ ] UI configurazione template reminder
- [ ] Log messaggi WhatsApp inviati

---

## 📐 ARCHITETTURA FASE 4

### Sub-Fasi

```
Fase 4.1: Visual Stati & Filtri (1 giorno)
    ├─ Badge stato su appuntamenti
    ├─ Colori per stato (cyan/green/red/orange/gray)
    ├─ Dropdown filtro stati nel calendario
    └─ Quick actions cambio stato

Fase 4.2: Delete & Soft Delete (0.5 giorno)
    ├─ Tauri command delete_appuntamento
    ├─ Dialog conferma eliminazione
    ├─ Soft delete con deleted_at
    └─ (Future: UI ripristino appuntamenti cancellati)

Fase 4.3: WhatsApp Reminders (1.5 giorni)
    ├─ Backend Rust: WhatsApp API client
    ├─ Tabella reminder_log (SQLite)
    ├─ Scheduling sistema (24h prima, 1h prima)
    ├─ Template messaggi configurabili
    └─ UI configurazione reminder per appuntamento
```

---

## 🚀 PIANO DETTAGLIATO

---

## **FASE 4.1 - VISUAL STATI & FILTRI** (PRIORITÀ ALTA)

### Obiettivo
Rendere lo stato appuntamento visibile e filtrabile nel calendario

### File da Modificare
1. `src/pages/Calendario.tsx` - Aggiungere filtro stati + colori stato
2. `src/components/calendario/AppuntamentoDialog.tsx` - Badge stato + quick actions
3. `src/types/appuntamento.ts` - Utility per colori stato

### Task

#### 1. Utility Colori Stato
**File**: `src/types/appuntamento.ts`

```typescript
// Aggiungi dopo la definizione di StatoAppuntamento
export const STATO_COLORS = {
  bozza: '#64748b',       // slate-500
  confermato: '#06b6d4',  // cyan-500 (FLUXION primary)
  completato: '#10b981',  // green-500
  cancellato: '#ef4444',  // red-500
  no_show: '#f97316',     // orange-500
} as const;

export const STATO_LABELS = {
  bozza: 'Bozza',
  confermato: 'Confermato',
  completato: 'Completato',
  cancellato: 'Cancellato',
  no_show: 'No Show',
} as const;

export function getStatoColor(stato: StatoAppuntamento): string {
  return STATO_COLORS[stato];
}

export function getStatoLabel(stato: StatoAppuntamento): string {
  return STATO_LABELS[stato];
}
```

#### 2. Badge Stato su Appuntamento (Calendario)
**File**: `src/pages/Calendario.tsx`

Modificare linee 254-280 (render appuntamento):

```tsx
<div
  key={app.id}
  className="text-xs p-1.5 rounded border-l-2 truncate cursor-pointer hover:opacity-80 transition-opacity"
  style={{
    // NUOVO: Usa colore STATO invece di servizio
    backgroundColor: `${getStatoColor(app.stato)}15`,
    borderLeftColor: getStatoColor(app.stato),
  }}
  onClick={(e) => {
    e.stopPropagation();
    setEditingAppuntamento(app);
    setAppuntamentoDialogOpen(true);
  }}
  title={`${app.servizio_nome} - ${app.cliente_nome} ${app.cliente_cognome} - ${getStatoLabel(app.stato)}`}
>
  {/* NUOVO: Badge stato */}
  <div className="flex items-center justify-between mb-0.5">
    <span className="font-medium text-white">{startTime}</span>
    <span
      className="text-[10px] px-1 py-0.5 rounded"
      style={{
        backgroundColor: getStatoColor(app.stato),
        color: '#fff'
      }}
    >
      {getStatoLabel(app.stato).substring(0, 3).toUpperCase()}
    </span>
  </div>
  <div className="text-slate-400 truncate">
    {app.cliente_nome} {app.cliente_cognome}
  </div>
  <div className="text-slate-500 text-[10px] truncate">
    {app.servizio_nome}
  </div>
</div>
```

#### 3. Filtro Dropdown Stati
**File**: `src/pages/Calendario.tsx`

Aggiungere state per filtro (dopo linea 77):

```tsx
const [statoFilter, setStatoFilter] = useState<StatoAppuntamento | 'tutti'>('tutti');
```

Aggiungere dropdown nel header (dopo "Oggi" button, linea 184):

```tsx
{/* Filtro Stati */}
<Select value={statoFilter} onValueChange={(value) => setStatoFilter(value as StatoAppuntamento | 'tutti')}>
  <SelectTrigger className="w-[180px] border-slate-700">
    <SelectValue placeholder="Tutti gli stati" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="tutti">Tutti gli stati</SelectItem>
    {Object.entries(STATO_LABELS).map(([key, label]) => (
      <SelectItem key={key} value={key}>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getStatoColor(key as StatoAppuntamento) }}
          />
          {label}
        </div>
      </SelectItem>
    ))}
  </SelectContent>
</Select>
```

Filtrare appuntamenti (modificare linea 100-112):

```tsx
const appointmentsByDate = useMemo(() => {
  if (!appuntamenti) return new Map();

  // NUOVO: Filtra per stato
  const filtered = statoFilter === 'tutti'
    ? appuntamenti
    : appuntamenti.filter(app => app.stato === statoFilter);

  const map = new Map<string, typeof appuntamenti>();
  filtered.forEach((app) => {
    const date = new Date(app.data_ora_inizio);
    const key = formatDateISO(date);
    const existing = map.get(key) || [];
    map.set(key, [...existing, app]);
  });

  return map;
}, [appuntamenti, statoFilter]); // Aggiungi statoFilter dependency
```

#### 4. Badge Stato in AppuntamentoDialog
**File**: `src/components/calendario/AppuntamentoDialog.tsx`

Aggiungere badge stato nel header del dialog (dopo DialogTitle):

```tsx
{isEditMode && editingAppuntamento && (
  <div
    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
    style={{
      backgroundColor: `${getStatoColor(editingAppuntamento.stato)}20`,
      color: getStatoColor(editingAppuntamento.stato),
      border: `1px solid ${getStatoColor(editingAppuntamento.stato)}40`
    }}
  >
    {getStatoLabel(editingAppuntamento.stato)}
  </div>
)}
```

#### 5. Quick Actions Cambio Stato
**File**: `src/components/calendario/AppuntamentoDialog.tsx`

Aggiungere bottoni quick action dopo il form (prima dei bottoni Salva/Annulla):

```tsx
{/* Quick Actions - Solo in Edit Mode */}
{isEditMode && editingAppuntamento && (
  <div className="flex items-center gap-2 pt-4 border-t border-slate-700">
    <span className="text-sm text-slate-400">Azioni rapide:</span>

    {editingAppuntamento.stato === 'confermato' && (
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => {
          form.setValue('stato', 'completato');
          form.handleSubmit(onSubmit)();
        }}
        className="border-green-500/30 text-green-500 hover:bg-green-500/10"
      >
        Segna Completato
      </Button>
    )}

    {editingAppuntamento.stato === 'bozza' && (
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => {
          form.setValue('stato', 'confermato');
          form.handleSubmit(onSubmit)();
        }}
        className="border-cyan-500/30 text-cyan-500 hover:bg-cyan-500/10"
      >
        Conferma Appuntamento
      </Button>
    )}

    {editingAppuntamento.stato !== 'cancellato' && (
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => {
          if (confirm('Sei sicuro di voler cancellare questo appuntamento?')) {
            form.setValue('stato', 'cancellato');
            form.handleSubmit(onSubmit)();
          }
        }}
        className="border-red-500/30 text-red-500 hover:bg-red-500/10"
      >
        Cancella
      </Button>
    )}
  </div>
)}
```

### Test Fase 4.1
1. Aprire calendario
2. Creare appuntamento con stato "bozza" → Badge grigio
3. Creare appuntamento con stato "confermato" → Badge cyan
4. Filtrare solo "confermati" → Altri nascosti
5. Editare appuntamento → Click "Segna Completato" → Badge verde
6. Verificare colori corretti su calendario

---

## **FASE 4.2 - DELETE & SOFT DELETE** (PRIORITÀ MEDIA)

### Obiettivo
Permettere eliminazione appuntamenti con soft delete (deleted_at)

### File da Modificare
1. `src-tauri/src/commands/appuntamenti.rs` - Aggiungere delete command
2. `src/hooks/use-appuntamenti.ts` - Aggiungere useDeleteAppuntamento hook
3. `src/components/calendario/AppuntamentoDialog.tsx` - Bottone Delete

### Task

#### 1. Backend Delete Command
**File**: `src-tauri/src/commands/appuntamenti.rs`

```rust
#[tauri::command]
pub async fn delete_appuntamento(
    state: State<'_, DbConnection>,
    id: i64,
) -> Result<(), String> {
    let db = state.0.lock().await;

    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query!(
        "UPDATE appuntamenti SET deleted_at = ? WHERE id = ?",
        now,
        id
    )
    .execute(&*db)
    .await
    .map_err(|e| format!("Errore eliminazione appuntamento: {}", e))?;

    Ok(())
}
```

Aggiungere al builder in `main.rs`:

```rust
.invoke_handler(tauri::generate_handler![
    // ... existing commands ...
    delete_appuntamento,
])
```

#### 2. Hook useDeleteAppuntamento
**File**: `src/hooks/use-appuntamenti.ts`

```typescript
export function useDeleteAppuntamento() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await invoke('delete_appuntamento', { id });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appuntamenti'] });
    },
  });
}
```

#### 3. Bottone Delete in Dialog
**File**: `src/components/calendario/AppuntamentoDialog.tsx`

Aggiungere import:
```tsx
import { Trash2 } from 'lucide-react';
```

Aggiungere state per delete:
```tsx
const deleteMutation = useDeleteAppuntamento();
```

Aggiungere bottone Delete (in footer, prima di Annulla):

```tsx
{isEditMode && editingAppuntamento && (
  <Button
    type="button"
    variant="outline"
    onClick={() => {
      if (confirm('Sei sicuro di voler eliminare definitivamente questo appuntamento?')) {
        deleteMutation.mutate(editingAppuntamento.id, {
          onSuccess: () => {
            onSuccess();
          }
        });
      }
    }}
    disabled={deleteMutation.isPending}
    className="border-red-500/30 text-red-500 hover:bg-red-500/10"
  >
    <Trash2 className="w-4 h-4 mr-2" />
    Elimina
  </Button>
)}
```

### Test Fase 4.2
1. Aprire appuntamento esistente
2. Click "Elimina" → Conferma
3. Verificare appuntamento rimosso dal calendario
4. Verificare in database: deleted_at è popolato (non NULL)

---

## **FASE 4.3 - WHATSAPP REMINDERS** (PRIORITÀ ALTA)

### Obiettivo
Sistema automatico reminder WhatsApp 24h e 1h prima appuntamento

### Architettura

```
┌─────────────────┐
│  Tauri App      │
│  (Frontend)     │
└────────┬────────┘
         │
         │ invoke('send_whatsapp_reminder')
         ▼
┌─────────────────┐
│  Rust Backend   │
│  whatsapp.rs    │
└────────┬────────┘
         │
         │ HTTP POST
         ▼
┌─────────────────┐      ┌──────────────┐
│  WhatsApp API   │──────│  WhatsApp    │
│  (Twilio/      │      │  Business    │
│   Cloud API)    │      │  Account     │
└─────────────────┘      └──────────────┘
```

### Database Schema

**Nuova Tabella**: `reminder_log`

```sql
CREATE TABLE reminder_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appuntamento_id INTEGER NOT NULL,
    tipo_reminder TEXT NOT NULL CHECK(tipo_reminder IN ('24h', '1h', 'manuale')),
    destinatario TEXT NOT NULL, -- numero telefono +393281536308
    messaggio TEXT NOT NULL,
    stato TEXT NOT NULL CHECK(stato IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    twilio_sid TEXT, -- SID messaggio Twilio (se usato)
    error_message TEXT,
    sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX idx_reminder_appuntamento ON reminder_log(appuntamento_id);
CREATE INDEX idx_reminder_stato ON reminder_log(stato);
CREATE INDEX idx_reminder_sent_at ON reminder_log(sent_at);
```

### File da Creare/Modificare

#### 1. Migration Database
**File**: `src-tauri/migrations/003_reminder_log.sql`

```sql
-- Tabella per logging reminder WhatsApp
CREATE TABLE IF NOT EXISTS reminder_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appuntamento_id INTEGER NOT NULL,
    tipo_reminder TEXT NOT NULL CHECK(tipo_reminder IN ('24h', '1h', 'manuale')),
    destinatario TEXT NOT NULL,
    messaggio TEXT NOT NULL,
    stato TEXT NOT NULL CHECK(stato IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    twilio_sid TEXT,
    error_message TEXT,
    sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX IF NOT EXISTS idx_reminder_appuntamento ON reminder_log(appuntamento_id);
CREATE INDEX IF NOT EXISTS idx_reminder_stato ON reminder_log(stato);
CREATE INDEX IF NOT EXISTS idx_reminder_sent_at ON reminder_log(sent_at);
```

#### 2. Backend WhatsApp Client
**File**: `src-tauri/src/whatsapp.rs`

```rust
use serde::{Deserialize, Serialize};
use reqwest::Client;

#[derive(Debug, Serialize)]
struct TwilioWhatsAppRequest {
    #[serde(rename = "From")]
    from: String,
    #[serde(rename = "To")]
    to: String,
    #[serde(rename = "Body")]
    body: String,
}

#[derive(Debug, Deserialize)]
struct TwilioWhatsAppResponse {
    sid: String,
    status: String,
    error_message: Option<String>,
}

pub async fn send_whatsapp_message(
    to: &str,           // +393281536308
    message: &str,
    account_sid: &str,  // Da .env TWILIO_ACCOUNT_SID
    auth_token: &str,   // Da .env TWILIO_AUTH_TOKEN
    from: &str,         // whatsapp:+14155238886 (Twilio sandbox)
) -> Result<String, String> {
    let client = Client::new();

    let url = format!(
        "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json",
        account_sid
    );

    let body = TwilioWhatsAppRequest {
        from: format!("whatsapp:{}", from),
        to: format!("whatsapp:{}", to),
        body: message.to_string(),
    };

    let response = client
        .post(&url)
        .basic_auth(account_sid, Some(auth_token))
        .form(&body)
        .send()
        .await
        .map_err(|e| format!("Errore invio WhatsApp: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("WhatsApp API error: {}", response.status()));
    }

    let result: TwilioWhatsAppResponse = response
        .json()
        .await
        .map_err(|e| format!("Errore parsing response: {}", e))?;

    Ok(result.sid)
}
```

#### 3. Tauri Command Send Reminder
**File**: `src-tauri/src/commands/reminders.rs`

```rust
use tauri::State;
use crate::DbConnection;
use crate::whatsapp::send_whatsapp_message;

#[tauri::command]
pub async fn send_whatsapp_reminder(
    state: State<'_, DbConnection>,
    appuntamento_id: i64,
    tipo_reminder: String, // "24h" | "1h" | "manuale"
) -> Result<(), String> {
    let db = state.0.lock().await;

    // 1. Fetch appuntamento details con JOIN
    let app = sqlx::query!(
        r#"
        SELECT
            a.id,
            a.data_ora_inizio,
            c.nome as cliente_nome,
            c.cognome as cliente_cognome,
            c.telefono as cliente_telefono,
            s.nome as servizio_nome,
            o.nome as operatore_nome
        FROM appuntamenti a
        JOIN clienti c ON a.cliente_id = c.id
        JOIN servizi s ON a.servizio_id = s.id
        JOIN operatori o ON a.operatore_id = o.id
        WHERE a.id = ? AND a.deleted_at IS NULL
        "#,
        appuntamento_id
    )
    .fetch_one(&*db)
    .await
    .map_err(|e| format!("Appuntamento non trovato: {}", e))?;

    // 2. Build message template
    let data_ora = chrono::DateTime::parse_from_rfc3339(&app.data_ora_inizio)
        .map_err(|e| format!("Errore parsing data: {}", e))?;

    let data_formattata = data_ora.format("%d/%m/%Y alle %H:%M").to_string();

    let message = format!(
        "🔔 Promemoria Appuntamento\n\n\
        Gentile {nome} {cognome},\n\
        le ricordiamo il suo appuntamento per *{servizio}* \
        con {operatore} il giorno *{data}*.\n\n\
        Ci vediamo presto!\n\
        - Fluxion Team",
        nome = app.cliente_nome,
        cognome = app.cliente_cognome,
        servizio = app.servizio_nome,
        operatore = app.operatore_nome,
        data = data_formattata
    );

    // 3. Validate phone number
    let phone = app.cliente_telefono
        .ok_or("Cliente senza numero di telefono")?;

    if !phone.starts_with("+") {
        return Err("Numero telefono deve iniziare con + (es: +393281536308)".to_string());
    }

    // 4. Send WhatsApp via Twilio
    let twilio_account_sid = std::env::var("TWILIO_ACCOUNT_SID")
        .map_err(|_| "TWILIO_ACCOUNT_SID non configurato")?;
    let twilio_auth_token = std::env::var("TWILIO_AUTH_TOKEN")
        .map_err(|_| "TWILIO_AUTH_TOKEN non configurato")?;
    let twilio_from = std::env::var("TWILIO_WHATSAPP_FROM")
        .unwrap_or("+14155238886".to_string()); // Twilio sandbox default

    let sid = send_whatsapp_message(
        &phone,
        &message,
        &twilio_account_sid,
        &twilio_auth_token,
        &twilio_from,
    )
    .await?;

    // 5. Log reminder in database
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query!(
        r#"
        INSERT INTO reminder_log
        (appuntamento_id, tipo_reminder, destinatario, messaggio, stato, twilio_sid, sent_at)
        VALUES (?, ?, ?, ?, 'sent', ?, ?)
        "#,
        appuntamento_id,
        tipo_reminder,
        phone,
        message,
        sid,
        now
    )
    .execute(&*db)
    .await
    .map_err(|e| format!("Errore log reminder: {}", e))?;

    Ok(())
}
```

#### 4. Frontend Hook
**File**: `src/hooks/use-reminders.ts`

```typescript
import { invoke } from '@tauri-apps/api/core';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useSendWhatsAppReminder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      appuntamentoId,
      tipoReminder
    }: {
      appuntamentoId: number;
      tipoReminder: '24h' | '1h' | 'manuale'
    }) => {
      await invoke('send_whatsapp_reminder', {
        appuntamentoId,
        tipoReminder,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminder-log'] });
    },
  });
}
```

#### 5. UI Bottone Invia Reminder
**File**: `src/components/calendario/AppuntamentoDialog.tsx`

Aggiungere import:
```tsx
import { MessageCircle } from 'lucide-react';
import { useSendWhatsAppReminder } from '@/hooks/use-reminders';
```

Aggiungere mutation:
```tsx
const sendReminderMutation = useSendWhatsAppReminder();
```

Aggiungere bottone (in footer, dopo quick actions):

```tsx
{isEditMode && editingAppuntamento && editingAppuntamento.stato === 'confermato' && (
  <Button
    type="button"
    variant="outline"
    size="sm"
    onClick={() => {
      sendReminderMutation.mutate({
        appuntamentoId: editingAppuntamento.id,
        tipoReminder: 'manuale',
      }, {
        onSuccess: () => {
          alert('Reminder WhatsApp inviato!');
        },
        onError: (error) => {
          alert(`Errore invio reminder: ${error}`);
        }
      });
    }}
    disabled={sendReminderMutation.isPending}
    className="border-green-500/30 text-green-500 hover:bg-green-500/10"
  >
    <MessageCircle className="w-4 h-4 mr-2" />
    {sendReminderMutation.isPending ? 'Invio...' : 'Invia Reminder WhatsApp'}
  </Button>
)}
```

### Configurazione Twilio WhatsApp

#### Step 1: Crea Account Twilio
1. Vai su https://www.twilio.com/
2. Sign up gratuito (trial account $15 credit)
3. Verifica email e telefono

#### Step 2: Attiva WhatsApp Sandbox
1. Console Twilio → Messaging → Try it out → WhatsApp
2. Segui istruzioni: invia "join [codice]" al numero Twilio WhatsApp
3. Copia numero WhatsApp sandbox (es: +14155238886)

#### Step 3: Configura .env
```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=+14155238886
```

#### Step 4: Test
```bash
# In Rust
cargo test test_send_whatsapp_message

# O via UI
1. Crea appuntamento con cliente con telefono +393281536308
2. Apri appuntamento
3. Click "Invia Reminder WhatsApp"
4. Verifica messaggio ricevuto su WhatsApp
```

### Scheduling Automatico (Future Enhancement)

Per reminder automatici 24h/1h prima:

**Opzione A**: Background task Tauri (sidecar process)
**Opzione B**: Cron job esterno che chiama Tauri command
**Opzione C**: Sistema trigger SQLite con webhook

**NOTA**: Per MVP, implementare solo **invio manuale**. Scheduling automatico sarà Fase 5.

### Test Fase 4.3
1. ✅ Configurare Twilio account + sandbox WhatsApp
2. ✅ Creare cliente con telefono +393281536308 (tuo numero test)
3. ✅ Creare appuntamento confermato per domani
4. ✅ Aprire appuntamento → Click "Invia Reminder WhatsApp"
5. ✅ Verificare messaggio ricevuto su WhatsApp
6. ✅ Verificare log in tabella reminder_log (stato='sent', twilio_sid popolato)

---

## 📊 CRITERI DI COMPLETAMENTO FASE 4

### Fase 4.1 - Visual Stati & Filtri
- [ ] Badge stato visibile su ogni appuntamento (calendario)
- [ ] Colori corretti per stato (cyan/green/red/orange/gray)
- [ ] Dropdown filtro stati funzionante
- [ ] Quick actions cambio stato funzionanti
- [ ] Badge stato in AppuntamentoDialog
- [ ] Legenda stati aggiornata (rimuovere placeholder, usare veri stati)

### Fase 4.2 - Delete & Soft Delete
- [ ] Tauri command delete_appuntamento implementato
- [ ] Soft delete con deleted_at funzionante
- [ ] Bottone "Elimina" in AppuntamentoDialog
- [ ] Conferma eliminazione
- [ ] Appuntamento rimosso da calendario dopo delete
- [ ] Database: deleted_at popolato

### Fase 4.3 - WhatsApp Reminders
- [ ] Migration 003_reminder_log.sql eseguita
- [ ] Tabella reminder_log creata
- [ ] Backend whatsapp.rs implementato
- [ ] Tauri command send_whatsapp_reminder funzionante
- [ ] Hook useSendWhatsAppReminder implementato
- [ ] Bottone "Invia Reminder WhatsApp" in dialog
- [ ] Twilio account configurato
- [ ] Test invio manuale WhatsApp RIUSCITO
- [ ] Log reminder salvato in database

---

## 🎯 ORDINE DI ESECUZIONE

```
1. FASE 4.1 - Visual Stati & Filtri (INIZIA QUI)
   ├─ 1.1 Utility colori stato (types/appuntamento.ts)
   ├─ 1.2 Badge stato su calendario (Calendario.tsx)
   ├─ 1.3 Dropdown filtro stati (Calendario.tsx)
   ├─ 1.4 Badge in dialog (AppuntamentoDialog.tsx)
   └─ 1.5 Quick actions (AppuntamentoDialog.tsx)

2. FASE 4.2 - Delete & Soft Delete
   ├─ 2.1 Backend delete command (appuntamenti.rs)
   ├─ 2.2 Hook useDeleteAppuntamento (use-appuntamenti.ts)
   └─ 2.3 Bottone Delete in dialog (AppuntamentoDialog.tsx)

3. FASE 4.3 - WhatsApp Reminders
   ├─ 3.1 Migration database (003_reminder_log.sql)
   ├─ 3.2 Backend WhatsApp client (whatsapp.rs)
   ├─ 3.3 Tauri command (commands/reminders.rs)
   ├─ 3.4 Hook useSendWhatsAppReminder (use-reminders.ts)
   ├─ 3.5 UI bottone reminder (AppuntamentoDialog.tsx)
   └─ 3.6 Twilio setup + test
```

**IMPORTANTE**:
- Ogni sub-fase DEVE essere testata prima di passare alla successiva
- Creare commit Git dopo ogni sub-fase completata
- Aggiornare CLAUDE.md dopo ogni milestone

---

## 📝 FILE DI TEST DA CREARE

Dopo completamento Fase 4, creare:

```
testedebug/fase4/
├── TEST-FASE-4-1-STATI.txt      # Test visual stati + filtri
├── TEST-FASE-4-2-DELETE.txt     # Test soft delete
└── TEST-FASE-4-3-WHATSAPP.txt   # Test WhatsApp reminders
```

Ogni file deve contenere:
- Procedure test step-by-step
- Screenshot (30+ per fase)
- Query SQL per verifiche database
- Console output (Rust + Browser)
- Errori riscontrati + fix applicati

---

## 🔄 PROSSIMA FASE (Fase 5 - Preview)

Dopo Fase 4, le feature mancanti saranno:

**Fase 5 - Fatturazione Elettronica**
- Generazione XML FatturaPA
- Invio SDI (Sistema Di Interscambio)
- Gestione stati fattura (bozza, emessa, pagata, annullata)
- Note di credito
- Integrazione con appuntamenti (crea fattura da appuntamento completato)

**Fase 6 - Voice Agent**
- STT (Speech-to-Text) con Whisper
- TTS (Text-to-Speech) con ElevenLabs
- LLM orchestration (Groq Llama 3.3 70B)
- VoIP integration (Ehiweb SIP)
- Booking vocale ("Prenota appuntamento per domani alle 15")

---

*Piano creato: 2026-01-01*
*Durata stimata Fase 4: 3 giorni (4.1: 1gg, 4.2: 0.5gg, 4.3: 1.5gg)*
*Target completamento: 2026-01-04*
