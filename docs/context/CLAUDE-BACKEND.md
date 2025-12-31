# 🦀 FLUXION Backend - Rust + Tauri + SQLite

> Architettura backend: Tauri 2.x, Rust, SQLite, API commands

---

## 📋 Indice

1. [Stack Tecnologico](#stack-tecnologico)
2. [Schema Database SQLite](#schema-database-sqlite)
3. [Tauri Commands](#tauri-commands)
4. [Plugin Tauri](#plugin-tauri)
5. [Gestione Errori](#gestione-errori)
6. [Migrations](#migrations)

---

## Stack Tecnologico

| Componente | Versione | Uso |
|------------|----------|-----|
| **Tauri** | 2.x | Framework desktop |
| **Rust** | 1.75+ | Backend logic |
| **SQLite** | 3.x | Database locale |
| **SQLx** | 0.7+ | Query async + migrations |
| **Serde** | 1.0 | Serialization JSON |
| **tokio** | 1.0 | Async runtime |

### Cargo.toml Dipendenze

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "protocol-asset"] }
tauri-plugin-sql = { version = "2", features = ["sqlite"] }
tauri-plugin-fs = "2"
tauri-plugin-dialog = "2"
tauri-plugin-updater = "2"
tauri-plugin-store = "2"

serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.7", features = ["runtime-tokio", "sqlite"] }
tokio = { version = "1", features = ["full"] }
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1", features = ["v4", "serde"] }
thiserror = "1"
```

---

## Schema Database SQLite

### Tabelle Core

```sql
-- ═══════════════════════════════════════════════════════════════
-- FLUXION DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════

-- Attiva foreign keys
PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────────────────────────
-- CLIENTI
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clienti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    -- Anagrafica
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT,
    telefono TEXT NOT NULL,
    data_nascita TEXT,  -- ISO 8601: YYYY-MM-DD
    
    -- Indirizzo
    indirizzo TEXT,
    cap TEXT,
    citta TEXT,
    provincia TEXT,
    
    -- Fiscale (per fatturazione)
    codice_fiscale TEXT,
    partita_iva TEXT,
    codice_sdi TEXT DEFAULT '0000000',
    pec TEXT,
    
    -- Metadata
    note TEXT,
    tags TEXT,  -- JSON array: ["vip", "fedele"]
    fonte TEXT,  -- come ci ha conosciuto
    
    -- GDPR
    consenso_marketing INTEGER DEFAULT 0,
    consenso_whatsapp INTEGER DEFAULT 0,
    data_consenso TEXT,
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT  -- soft delete
);

CREATE INDEX idx_clienti_telefono ON clienti(telefono);
CREATE INDEX idx_clienti_email ON clienti(email);
CREATE INDEX idx_clienti_nome ON clienti(nome, cognome);

-- ─────────────────────────────────────────────────────────────────
-- SERVIZI
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS servizi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    nome TEXT NOT NULL,
    descrizione TEXT,
    categoria TEXT,  -- es: "Taglio", "Colore", "Trattamento"
    
    -- Pricing
    prezzo REAL NOT NULL,
    iva_percentuale REAL DEFAULT 22.0,
    
    -- Tempo
    durata_minuti INTEGER NOT NULL,
    buffer_minuti INTEGER DEFAULT 0,  -- pausa dopo servizio
    
    -- UI
    colore TEXT DEFAULT '#22D3EE',  -- per calendario
    icona TEXT,
    
    -- Status
    attivo INTEGER DEFAULT 1,
    ordine INTEGER DEFAULT 0,  -- per ordinamento lista
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────────
-- OPERATORI / STAFF
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS operatori (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    
    -- Ruolo
    ruolo TEXT DEFAULT 'operatore',  -- admin, operatore, reception
    
    -- UI
    colore TEXT DEFAULT '#C084FC',
    avatar_url TEXT,
    
    -- Status
    attivo INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Servizi che l'operatore può erogare
CREATE TABLE IF NOT EXISTS operatori_servizi (
    operatore_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    PRIMARY KEY (operatore_id, servizio_id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────────
-- APPUNTAMENTI
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appuntamenti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    -- Relazioni
    cliente_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    operatore_id TEXT,
    
    -- Timing
    data_ora_inizio TEXT NOT NULL,  -- ISO 8601: YYYY-MM-DDTHH:MM:SS
    data_ora_fine TEXT NOT NULL,
    durata_minuti INTEGER NOT NULL,
    
    -- Status
    stato TEXT DEFAULT 'confermato',  -- bozza, confermato, completato, cancellato, no_show
    
    -- Pricing
    prezzo REAL NOT NULL,
    sconto_percentuale REAL DEFAULT 0,
    prezzo_finale REAL NOT NULL,
    
    -- Note
    note TEXT,
    note_interne TEXT,  -- visibili solo staff
    
    -- Tracking
    fonte_prenotazione TEXT DEFAULT 'manuale',  -- manuale, whatsapp, voice, online
    reminder_inviato INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

CREATE INDEX idx_appuntamenti_data ON appuntamenti(data_ora_inizio);
CREATE INDEX idx_appuntamenti_cliente ON appuntamenti(cliente_id);
CREATE INDEX idx_appuntamenti_stato ON appuntamenti(stato);

-- ─────────────────────────────────────────────────────────────────
-- FATTURE
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fatture (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    -- Numerazione
    numero INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_completo TEXT NOT NULL,  -- es: "2025/001"
    
    -- Cliente
    cliente_id TEXT NOT NULL,
    
    -- Importi
    imponibile REAL NOT NULL,
    iva REAL NOT NULL,
    totale REAL NOT NULL,
    
    -- Status
    stato TEXT DEFAULT 'bozza',  -- bozza, emessa, inviata, pagata, annullata
    
    -- XML FatturaPA
    xml_generato INTEGER DEFAULT 0,
    xml_path TEXT,
    sdi_identificativo TEXT,
    sdi_stato TEXT,
    sdi_data_invio TEXT,
    
    -- Date
    data_emissione TEXT NOT NULL,
    data_scadenza TEXT,
    data_pagamento TEXT,
    
    -- Metodo pagamento
    metodo_pagamento TEXT,  -- contanti, carta, bonifico
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    UNIQUE(numero, anno)
);

-- Righe fattura
CREATE TABLE IF NOT EXISTS fatture_righe (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    fattura_id TEXT NOT NULL,
    
    descrizione TEXT NOT NULL,
    quantita REAL DEFAULT 1,
    prezzo_unitario REAL NOT NULL,
    iva_percentuale REAL DEFAULT 22.0,
    totale_riga REAL NOT NULL,
    
    -- Riferimento opzionale ad appuntamento
    appuntamento_id TEXT,
    
    ordine INTEGER DEFAULT 0,
    
    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE,
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

-- ─────────────────────────────────────────────────────────────────
-- MESSAGGI WHATSAPP
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messaggi_whatsapp (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    cliente_id TEXT,
    telefono TEXT NOT NULL,
    
    -- Contenuto
    direzione TEXT NOT NULL,  -- inbound, outbound
    tipo TEXT DEFAULT 'text',  -- text, image, document
    contenuto TEXT NOT NULL,
    
    -- Status
    stato TEXT DEFAULT 'pending',  -- pending, sent, delivered, read, failed
    errore TEXT,
    
    -- Template
    template_id TEXT,
    
    -- Timestamps
    data_invio TEXT DEFAULT (datetime('now')),
    data_consegna TEXT,
    data_lettura TEXT,
    
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);

CREATE INDEX idx_messaggi_telefono ON messaggi_whatsapp(telefono);
CREATE INDEX idx_messaggi_data ON messaggi_whatsapp(data_invio);

-- ─────────────────────────────────────────────────────────────────
-- CHIAMATE VOICE AGENT
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chiamate_voice (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    telefono TEXT NOT NULL,
    cliente_id TEXT,
    
    -- Call info
    direzione TEXT NOT NULL,  -- inbound, outbound
    durata_secondi INTEGER,
    
    -- Trascrizione
    trascrizione TEXT,
    intent_rilevato TEXT,  -- prenotazione, cancellazione, info, altro
    
    -- Esito
    esito TEXT,  -- successo, fallito, trasferito
    appuntamento_creato_id TEXT,
    
    -- Timestamps
    data_inizio TEXT DEFAULT (datetime('now')),
    data_fine TEXT,
    
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_creato_id) REFERENCES appuntamenti(id)
);

-- ─────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS impostazioni (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    tipo TEXT DEFAULT 'string',  -- string, number, boolean, json
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Valori default
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('nome_attivita', 'La Mia Attività', 'string'),
    ('orario_apertura', '09:00', 'string'),
    ('orario_chiusura', '19:00', 'string'),
    ('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]', 'json'),
    ('durata_slot_minuti', '30', 'number'),
    ('reminder_ore_prima', '24', 'number'),
    ('whatsapp_attivo', 'true', 'boolean'),
    ('voice_agent_attivo', 'false', 'boolean');
```

---

## Tauri Commands

### Struttura Base Command

```rust
// src-tauri/src/commands/mod.rs

use serde::{Deserialize, Serialize};
use tauri::State;
use sqlx::SqlitePool;

// Tipo risultato standard
pub type CmdResult<T> = Result<T, String>;

// Wrapper per errori
fn map_err<E: std::fmt::Display>(e: E) -> String {
    e.to_string()
}
```

### Commands Clienti

```rust
// src-tauri/src/commands/clienti.rs

use super::*;

#[derive(Debug, Serialize, Deserialize)]
pub struct Cliente {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub email: Option<String>,
    pub telefono: String,
    pub note: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct NuovoCliente {
    pub nome: String,
    pub cognome: String,
    pub email: Option<String>,
    pub telefono: String,
    pub note: Option<String>,
}

#[tauri::command]
pub async fn get_clienti(
    pool: State<'_, SqlitePool>
) -> CmdResult<Vec<Cliente>> {
    sqlx::query_as!(
        Cliente,
        r#"
        SELECT id, nome, cognome, email, telefono, note, created_at
        FROM clienti
        WHERE deleted_at IS NULL
        ORDER BY cognome, nome
        "#
    )
    .fetch_all(pool.inner())
    .await
    .map_err(map_err)
}

#[tauri::command]
pub async fn get_cliente(
    pool: State<'_, SqlitePool>,
    id: String
) -> CmdResult<Option<Cliente>> {
    sqlx::query_as!(
        Cliente,
        r#"
        SELECT id, nome, cognome, email, telefono, note, created_at
        FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
        id
    )
    .fetch_optional(pool.inner())
    .await
    .map_err(map_err)
}

#[tauri::command]
pub async fn crea_cliente(
    pool: State<'_, SqlitePool>,
    cliente: NuovoCliente
) -> CmdResult<Cliente> {
    let id = uuid::Uuid::new_v4().to_string();
    
    sqlx::query!(
        r#"
        INSERT INTO clienti (id, nome, cognome, email, telefono, note)
        VALUES (?, ?, ?, ?, ?, ?)
        "#,
        id,
        cliente.nome,
        cliente.cognome,
        cliente.email,
        cliente.telefono,
        cliente.note
    )
    .execute(pool.inner())
    .await
    .map_err(map_err)?;
    
    get_cliente(pool, id).await?.ok_or("Cliente non trovato".into())
}

#[tauri::command]
pub async fn cerca_clienti(
    pool: State<'_, SqlitePool>,
    query: String
) -> CmdResult<Vec<Cliente>> {
    let pattern = format!("%{}%", query);
    
    sqlx::query_as!(
        Cliente,
        r#"
        SELECT id, nome, cognome, email, telefono, note, created_at
        FROM clienti
        WHERE deleted_at IS NULL
          AND (nome LIKE ? OR cognome LIKE ? OR telefono LIKE ? OR email LIKE ?)
        ORDER BY cognome, nome
        LIMIT 50
        "#,
        pattern, pattern, pattern, pattern
    )
    .fetch_all(pool.inner())
    .await
    .map_err(map_err)
}
```

### Commands Appuntamenti

```rust
// src-tauri/src/commands/appuntamenti.rs

use super::*;
use chrono::{NaiveDateTime, Duration};

#[derive(Debug, Serialize, Deserialize)]
pub struct Appuntamento {
    pub id: String,
    pub cliente_id: String,
    pub cliente_nome: String,
    pub servizio_id: String,
    pub servizio_nome: String,
    pub operatore_id: Option<String>,
    pub data_ora_inizio: String,
    pub data_ora_fine: String,
    pub durata_minuti: i32,
    pub stato: String,
    pub prezzo_finale: f64,
    pub note: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct NuovoAppuntamento {
    pub cliente_id: String,
    pub servizio_id: String,
    pub operatore_id: Option<String>,
    pub data_ora_inizio: String,
    pub note: Option<String>,
}

#[tauri::command]
pub async fn get_appuntamenti_giorno(
    pool: State<'_, SqlitePool>,
    data: String  // YYYY-MM-DD
) -> CmdResult<Vec<Appuntamento>> {
    sqlx::query_as!(
        Appuntamento,
        r#"
        SELECT 
            a.id,
            a.cliente_id,
            c.nome || ' ' || c.cognome as cliente_nome,
            a.servizio_id,
            s.nome as servizio_nome,
            a.operatore_id,
            a.data_ora_inizio,
            a.data_ora_fine,
            a.durata_minuti,
            a.stato,
            a.prezzo_finale,
            a.note
        FROM appuntamenti a
        JOIN clienti c ON a.cliente_id = c.id
        JOIN servizi s ON a.servizio_id = s.id
        WHERE date(a.data_ora_inizio) = ?
          AND a.stato != 'cancellato'
        ORDER BY a.data_ora_inizio
        "#,
        data
    )
    .fetch_all(pool.inner())
    .await
    .map_err(map_err)
}

#[tauri::command]
pub async fn crea_appuntamento(
    pool: State<'_, SqlitePool>,
    app: NuovoAppuntamento
) -> CmdResult<Appuntamento> {
    // Recupera servizio per durata e prezzo
    let servizio = sqlx::query!(
        "SELECT durata_minuti, prezzo FROM servizi WHERE id = ?",
        app.servizio_id
    )
    .fetch_one(pool.inner())
    .await
    .map_err(map_err)?;
    
    let id = uuid::Uuid::new_v4().to_string();
    let inizio = NaiveDateTime::parse_from_str(&app.data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
        .map_err(|e| e.to_string())?;
    let fine = inizio + Duration::minutes(servizio.durata_minuti as i64);
    let fine_str = fine.format("%Y-%m-%dT%H:%M:%S").to_string();
    
    sqlx::query!(
        r#"
        INSERT INTO appuntamenti 
        (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, 
         durata_minuti, prezzo, prezzo_finale, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
        id,
        app.cliente_id,
        app.servizio_id,
        app.operatore_id,
        app.data_ora_inizio,
        fine_str,
        servizio.durata_minuti,
        servizio.prezzo,
        servizio.prezzo,
        app.note
    )
    .execute(pool.inner())
    .await
    .map_err(map_err)?;
    
    // Ritorna appuntamento completo
    get_appuntamento(pool, id).await
}
```

---

## Plugin Tauri

### Configurazione in main.rs

```rust
// src-tauri/src/main.rs

mod commands;

use tauri::Manager;
use sqlx::sqlite::SqlitePoolOptions;

#[tokio::main]
async fn main() {
    // Database connection
    let db_path = "sqlite:fluxion.db?mode=rwc";
    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(db_path)
        .await
        .expect("Failed to connect to database");
    
    // Run migrations
    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .expect("Failed to run migrations");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_sql::Builder::default().build())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_updater::Builder::default().build())
        .plugin(tauri_plugin_store::Builder::default().build())
        .manage(pool)
        .invoke_handler(tauri::generate_handler![
            // Clienti
            commands::clienti::get_clienti,
            commands::clienti::get_cliente,
            commands::clienti::crea_cliente,
            commands::clienti::cerca_clienti,
            // Appuntamenti
            commands::appuntamenti::get_appuntamenti_giorno,
            commands::appuntamenti::crea_appuntamento,
            // ... altri commands
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## Gestione Errori

```rust
// src-tauri/src/error.rs

use thiserror::Error;
use serde::Serialize;

#[derive(Error, Debug, Serialize)]
pub enum FluxionError {
    #[error("Database error: {0}")]
    Database(String),
    
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Validation error: {0}")]
    Validation(String),
    
    #[error("Conflict: {0}")]
    Conflict(String),
}

impl From<sqlx::Error> for FluxionError {
    fn from(e: sqlx::Error) -> Self {
        FluxionError::Database(e.to_string())
    }
}

// Per Tauri commands
impl From<FluxionError> for String {
    fn from(e: FluxionError) -> Self {
        e.to_string()
    }
}
```

---

## Migrations

### Struttura Directory

```
src-tauri/
├── migrations/
│   ├── 20251228_000001_init.sql
│   ├── 20251228_000002_seed_data.sql
│   └── ...
└── ...
```

### Migration Iniziale

```sql
-- migrations/20251228_000001_init.sql
-- Copia tutto lo schema SQL dalla sezione precedente
```

### Seed Data (Demo)

```sql
-- migrations/20251228_000002_seed_data.sql

-- Servizi demo
INSERT INTO servizi (id, nome, categoria, prezzo, durata_minuti, colore) VALUES
    ('srv-001', 'Taglio Donna', 'Taglio', 35.00, 45, '#22D3EE'),
    ('srv-002', 'Taglio Uomo', 'Taglio', 20.00, 30, '#3B82F6'),
    ('srv-003', 'Piega', 'Styling', 25.00, 30, '#8B5CF6'),
    ('srv-004', 'Colore', 'Colore', 50.00, 90, '#EC4899'),
    ('srv-005', 'Taglio + Piega', 'Combo', 55.00, 60, '#10B981');

-- Operatori demo
INSERT INTO operatori (id, nome, cognome, ruolo, colore) VALUES
    ('op-001', 'Maria', 'Rossi', 'admin', '#F59E0B'),
    ('op-002', 'Giuseppe', 'Verdi', 'operatore', '#10B981');

-- Clienti demo
INSERT INTO clienti (id, nome, cognome, telefono, email) VALUES
    ('cli-001', 'Anna', 'Bianchi', '+393331234567', 'anna.bianchi@email.it'),
    ('cli-002', 'Marco', 'Neri', '+393339876543', 'marco.neri@email.it');
```

---

## 🔗 File Correlati

- Frontend React: `CLAUDE-FRONTEND.md`
- Design System: `CLAUDE-DESIGN-SYSTEM.md`
- Deployment: `CLAUDE-DEPLOYMENT.md`

---

*Ultimo aggiornamento: 2025-12-28T18:00:00*
