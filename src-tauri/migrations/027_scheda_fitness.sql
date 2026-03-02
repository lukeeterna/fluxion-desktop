-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 027: Scheda Fitness (W2-B)
-- Palestre, personal trainer, yoga, crossfit, piscine
-- Data: 2026-03-02
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS schede_fitness (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,

    -- Obiettivo e livello
    obiettivo TEXT, -- 'dimagrimento', 'tonificazione', 'massa', 'resistenza', 'salute', 'altro'
    livello TEXT,   -- 'principiante', 'intermedio', 'avanzato'
    frequenza_allenamento TEXT, -- '1x_settimana', '2x_settimana', ecc.

    -- Misurazioni corporee
    peso_kg REAL,
    altezza_cm REAL,
    percentuale_grasso REAL,
    circonferenza_vita REAL,
    circonferenza_fianchi REAL,

    -- Note mediche
    note_mediche TEXT,
    limitazioni_fisiche TEXT,
    cardiopatico INTEGER DEFAULT 0,
    iperteso INTEGER DEFAULT 0,
    diabetico INTEGER DEFAULT 0,

    -- Scheda e storico (JSON)
    scheda_allenamento TEXT DEFAULT '[]', -- [{giorno, esercizi: [string]}]
    storico_misurazioni TEXT DEFAULT '[]', -- [{id, data, peso, grasso, note}]

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_fitness_cliente ON schede_fitness(cliente_id);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT COUNT(*) FROM schede_fitness;
