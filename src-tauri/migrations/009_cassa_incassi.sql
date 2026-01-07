-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 009: Sistema Cassa/Incassi
-- FLUXION = Gestionale puro, RT separato per scontrini
-- ═══════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- INCASSI: Registro pagamenti giornalieri
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS incassi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Importo
    importo REAL NOT NULL,
    metodo_pagamento TEXT NOT NULL DEFAULT 'contanti',  -- contanti, carta, satispay, bonifico, altro

    -- Collegamenti (opzionali)
    cliente_id TEXT,
    appuntamento_id TEXT,
    fattura_id TEXT,

    -- Descrizione
    descrizione TEXT,
    categoria TEXT DEFAULT 'servizio',  -- servizio, prodotto, pacchetto, altro

    -- Operatore che ha registrato
    operatore_id TEXT,

    -- Timestamps
    data_incasso TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),

    -- Foreign keys
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id),
    FOREIGN KEY (fattura_id) REFERENCES fatture(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

-- Indici per query frequenti
CREATE INDEX IF NOT EXISTS idx_incassi_data ON incassi(data_incasso);
CREATE INDEX IF NOT EXISTS idx_incassi_cliente ON incassi(cliente_id);
CREATE INDEX IF NOT EXISTS idx_incassi_metodo ON incassi(metodo_pagamento);

-- ─────────────────────────────────────────────────────────────────
-- CHIUSURE_CASSA: Riepilogo fine giornata
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chiusure_cassa (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Data chiusura
    data_chiusura TEXT NOT NULL,

    -- Totali per metodo
    totale_contanti REAL DEFAULT 0,
    totale_carte REAL DEFAULT 0,
    totale_satispay REAL DEFAULT 0,
    totale_bonifici REAL DEFAULT 0,
    totale_altro REAL DEFAULT 0,

    -- Totale generale
    totale_giornata REAL DEFAULT 0,
    numero_transazioni INTEGER DEFAULT 0,

    -- Fondo cassa
    fondo_cassa_iniziale REAL DEFAULT 0,
    fondo_cassa_finale REAL DEFAULT 0,

    -- Note
    note TEXT,

    -- Chi ha chiuso
    operatore_id TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

CREATE INDEX IF NOT EXISTS idx_chiusure_data ON chiusure_cassa(data_chiusura);

-- ─────────────────────────────────────────────────────────────────
-- METODI_PAGAMENTO: Lookup table
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS metodi_pagamento (
    codice TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    icona TEXT,
    attivo INTEGER DEFAULT 1,
    ordine INTEGER DEFAULT 0
);

-- Metodi di pagamento default
INSERT OR IGNORE INTO metodi_pagamento (codice, nome, icona, ordine) VALUES
('contanti', 'Contanti', '💵', 1),
('carta', 'Carta di Credito/Debito', '💳', 2),
('satispay', 'Satispay', '📱', 3),
('bonifico', 'Bonifico', '🏦', 4),
('assegno', 'Assegno', '📝', 5),
('buono', 'Buono/Voucher', '🎁', 6),
('pacchetto', 'Da Pacchetto Prepagato', '📦', 7),
('altro', 'Altro', '💰', 99);

-- ─────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI CASSA
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO impostazioni (chiave, valore) VALUES
('cassa_fondo_iniziale', '100.00'),
('cassa_arrotondamento', '0.01'),
('cassa_stampa_riepilogo', 'false');
