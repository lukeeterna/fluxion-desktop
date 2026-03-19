-- Migration 034: Blocchi orario operatore (pausa pranzo, fasce non prenotabili)
-- P0-2: Sara deve verificare blocchi PRIMA di proporre slot

CREATE TABLE IF NOT EXISTS blocchi_orario (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL REFERENCES operatori(id) ON DELETE CASCADE,
    giorno_settimana INTEGER,  -- 0=Lun, 1=Mar, ..., 6=Dom (NULL = tutti i giorni)
    data_specifica TEXT,       -- YYYY-MM-DD per blocco one-shot (NULL = ricorrente)
    ora_inizio TEXT NOT NULL,  -- HH:MM
    ora_fine TEXT NOT NULL,    -- HH:MM
    motivo TEXT DEFAULT 'pausa',  -- 'pausa_pranzo', 'permesso', 'chiusura_anticipata', etc.
    ricorrente INTEGER DEFAULT 1, -- 1=ogni settimana, 0=una tantum
    attivo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Index for fast lookup by operator + day
CREATE INDEX IF NOT EXISTS idx_blocchi_orario_operatore
    ON blocchi_orario(operatore_id, giorno_settimana, attivo);

CREATE INDEX IF NOT EXISTS idx_blocchi_orario_data
    ON blocchi_orario(operatore_id, data_specifica, attivo);
