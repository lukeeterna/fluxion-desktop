-- ═══════════════════════════════════════════════════════════════════
-- Migration 035: Scheda Pet (toelettatura, veterinario, pensione)
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS schede_pet (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,

    -- Dati animale
    nome_animale TEXT NOT NULL DEFAULT '',
    specie TEXT NOT NULL DEFAULT 'cane',           -- cane, gatto, coniglio, etc.
    razza TEXT DEFAULT '',
    colore_mantello TEXT DEFAULT '',
    data_nascita TEXT DEFAULT '',                    -- YYYY-MM-DD
    peso_kg REAL DEFAULT NULL,
    sesso TEXT DEFAULT '',                          -- M, F, castrato, sterilizzata
    microchip TEXT DEFAULT '',

    -- Salute
    vaccinazioni TEXT DEFAULT '[]',                  -- JSON: [{nome, data, scadenza}]
    allergie TEXT DEFAULT '',
    patologie TEXT DEFAULT '',
    farmaci TEXT DEFAULT '',
    veterinario_riferimento TEXT DEFAULT '',

    -- Toelettatura
    tipo_pelo TEXT DEFAULT '',                       -- corto, medio, lungo, riccio, liscio, duro
    problemi_pelo TEXT DEFAULT '',                   -- nodi frequenti, dermatite, etc.
    temperamento TEXT DEFAULT '',                    -- tranquillo, nervoso, aggressivo, pauroso
    note_comportamento TEXT DEFAULT '',              -- morde, teme asciugatore, etc.
    prodotti_preferiti TEXT DEFAULT '',
    ultima_toelettatura TEXT DEFAULT '',              -- YYYY-MM-DD
    frequenza_consigliata TEXT DEFAULT '',            -- ogni 4 settimane, etc.

    -- Storico trattamenti
    storico_trattamenti TEXT DEFAULT '[]',            -- JSON: [{data, tipo, note}]
    foto TEXT DEFAULT '[]',                           -- JSON: [url]

    note TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_pet_cliente ON schede_pet(cliente_id);
CREATE INDEX IF NOT EXISTS idx_schede_pet_microchip ON schede_pet(microchip);
