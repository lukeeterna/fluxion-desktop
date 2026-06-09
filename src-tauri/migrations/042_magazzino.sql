-- 042_magazzino.sql
-- Magazzino: articoli + movimenti + alert sottoscorta automatici
-- Created: 2026-06-08
-- Additiva: NON tocca licenze, Sara, payload firmato, encryption. WIP=1 magazzino.
-- Convenzioni: PK TEXT uuid-default, FK opzionale verso suppliers(id),
-- soft-delete via colonna `attivo`, timestamp datetime('now').

-- Articoli di magazzino
CREATE TABLE IF NOT EXISTS articoli (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    categoria TEXT,
    giacenza INTEGER NOT NULL DEFAULT 0,
    soglia_minima INTEGER NOT NULL DEFAULT 0,
    prezzo_acquisto REAL,
    prezzo_vendita REAL,
    ean TEXT,
    -- FK opzionale verso suppliers (016_suppliers.sql, PK id TEXT).
    -- Nessun UNIQUE qui: la 040 ha tolto UNIQUE da suppliers per l'encryption,
    -- non introduciamo vincoli che possano confliggere.
    fornitore_id TEXT REFERENCES suppliers(id),
    -- alert_notificato: 1 = alert sottoscorta gia' scattato (anti-spam),
    -- 0 = sopra soglia / da riemettere se riscende.
    alert_notificato INTEGER NOT NULL DEFAULT 0,
    attivo INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Movimenti di magazzino (carico/scarico) — storico immutabile
CREATE TABLE IF NOT EXISTS movimenti_magazzino (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    articolo_id TEXT NOT NULL REFERENCES articoli(id),
    tipo TEXT NOT NULL,        -- 'carico' | 'scarico'
    quantita INTEGER NOT NULL, -- sempre > 0 (il segno e' dato dal tipo)
    causale TEXT,              -- 'vendita' | 'rettifica' | 'acquisto' | ...
    riferimento TEXT,          -- id esterno opzionale (es. id fattura/appuntamento)
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indici per WHERE/JOIN frequenti
CREATE INDEX IF NOT EXISTS idx_articoli_attivo ON articoli(attivo);
CREATE INDEX IF NOT EXISTS idx_movimenti_articolo ON movimenti_magazzino(articolo_id);
