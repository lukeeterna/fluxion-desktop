-- Migration 011: Voice Agent - Tabella chiamate
-- Storico chiamate voce per prenotazioni automatiche

CREATE TABLE IF NOT EXISTS chiamate_voice (
    id TEXT PRIMARY KEY,
    telefono TEXT NOT NULL,
    cliente_id TEXT REFERENCES clienti(id),
    direzione TEXT NOT NULL CHECK(direzione IN ('inbound', 'outbound')),
    durata_secondi INTEGER DEFAULT 0,
    trascrizione TEXT,
    intent_rilevato TEXT,
    esito TEXT CHECK(esito IN ('completata', 'abbandonata', 'errore', 'trasferita')),
    appuntamento_creato_id TEXT REFERENCES appuntamenti(id),
    sentiment TEXT CHECK(sentiment IN ('positivo', 'neutro', 'negativo')),
    note TEXT,
    data_inizio TEXT NOT NULL,
    data_fine TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT
);

-- Indici per query frequenti
CREATE INDEX IF NOT EXISTS idx_chiamate_voice_telefono ON chiamate_voice(telefono);
CREATE INDEX IF NOT EXISTS idx_chiamate_voice_cliente ON chiamate_voice(cliente_id);
CREATE INDEX IF NOT EXISTS idx_chiamate_voice_data ON chiamate_voice(data_inizio);
CREATE INDEX IF NOT EXISTS idx_chiamate_voice_esito ON chiamate_voice(esito);

-- Configurazione Voice Agent
CREATE TABLE IF NOT EXISTS voice_agent_config (
    id TEXT PRIMARY KEY DEFAULT 'default',
    attivo INTEGER DEFAULT 0,
    voce_modello TEXT DEFAULT 'it_IT-paola-medium',
    saluto_personalizzato TEXT,
    orario_attivo_da TEXT DEFAULT '09:00',
    orario_attivo_a TEXT DEFAULT '19:00',
    giorni_attivi TEXT DEFAULT '1,2,3,4,5,6', -- Lun-Sab
    max_chiamate_contemporanee INTEGER DEFAULT 2,
    timeout_risposta_secondi INTEGER DEFAULT 30,
    trasferisci_dopo_tentativi INTEGER DEFAULT 3,
    numero_trasferimento TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Inserisci config di default
INSERT OR IGNORE INTO voice_agent_config (id) VALUES ('default');

-- Statistiche giornaliere Voice Agent
CREATE TABLE IF NOT EXISTS voice_agent_stats (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    chiamate_totali INTEGER DEFAULT 0,
    chiamate_completate INTEGER DEFAULT 0,
    chiamate_abbandonate INTEGER DEFAULT 0,
    appuntamenti_creati INTEGER DEFAULT 0,
    durata_media_secondi REAL DEFAULT 0,
    sentiment_positivo INTEGER DEFAULT 0,
    sentiment_neutro INTEGER DEFAULT 0,
    sentiment_negativo INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_voice_stats_data ON voice_agent_stats(data);
