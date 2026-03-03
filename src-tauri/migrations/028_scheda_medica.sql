-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 028: Scheda Medica Generica
-- Medici generici, specialisti, psicologi, nutrizionisti
-- Data: 2026-03-03
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS schede_mediche (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,

    -- Anamnesi
    motivo_accesso TEXT,
    data_prima_visita DATE,
    data_ultima_visita DATE,
    medico_curante TEXT,
    inviato_da TEXT,           -- medico/struttura che ha inviato il paziente

    -- Dati clinici base
    gruppo_sanguigno TEXT,     -- 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'
    peso_kg REAL,
    altezza_cm REAL,
    pressione_sistolica INTEGER,
    pressione_diastolica INTEGER,
    frequenza_cardiaca INTEGER,

    -- Allergie e intolleranze (JSON array di stringhe)
    allergie_farmaci TEXT DEFAULT '[]',
    allergie_alimenti TEXT DEFAULT '[]',
    allergie_altro TEXT DEFAULT '[]',

    -- Patologie e condizioni (JSON array)
    patologie_croniche TEXT DEFAULT '[]',   -- ["diabete tipo 2", "ipertensione", ...]
    patologie_pregresse TEXT DEFAULT '[]',  -- ["appendicectomia 2015", ...]
    interventi_chirurgici TEXT DEFAULT '[]',

    -- Farmaci attuali (JSON array di oggetti)
    -- [{nome, dosaggio, frequenza, dal}]
    farmaci_attuali TEXT DEFAULT '[]',

    -- Abitudini
    fumatore INTEGER DEFAULT 0,
    ex_fumatore INTEGER DEFAULT 0,
    consumo_alcol TEXT,        -- 'no', 'occasionale', 'moderato', 'frequente'
    attivita_fisica TEXT,      -- 'sedentario', 'leggera', 'moderata', 'intensa'

    -- Anamnesi familiare
    familiari_cardiopatie INTEGER DEFAULT 0,
    familiari_diabete INTEGER DEFAULT 0,
    familiari_tumori INTEGER DEFAULT 0,
    anamnesi_familiare_note TEXT,

    -- Donne
    gravidanza INTEGER DEFAULT 0,
    allattamento INTEGER DEFAULT 0,
    menopausa INTEGER DEFAULT 0,

    -- Storico visite (JSON array)
    -- [{id, data, diagnosi, terapia, note, prossima_visita}]
    visite TEXT DEFAULT '[]',

    -- Esami e referti (JSON array)
    -- [{id, data, tipo, risultato, allegato_nome}]
    esami TEXT DEFAULT '[]',

    -- Note libere
    note_cliniche TEXT,
    note_private TEXT,          -- note visibili solo al professionista

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_mediche_cliente ON schede_mediche(cliente_id);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT COUNT(*) FROM schede_mediche;
