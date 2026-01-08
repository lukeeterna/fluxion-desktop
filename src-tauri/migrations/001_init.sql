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
-- FATTURE (creata in migration 007 con schema completo FatturaPA)
-- ─────────────────────────────────────────────────────────────────
-- NOTA: La tabella fatture è definita in 007_fatturazione_elettronica.sql
-- con lo schema completo per la fatturazione elettronica italiana

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
