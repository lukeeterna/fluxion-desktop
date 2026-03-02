-- ═══════════════════════════════════════════════════════════════════
-- Migration 025 — Operatori Commissioni (B5)
-- Struttura commissioni operatori: percentuale, fisso mensile, bonus soglia
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS operatori_commissioni (
    id              TEXT PRIMARY KEY,
    operatore_id    TEXT NOT NULL,
    tipo            TEXT NOT NULL CHECK(tipo IN (
                        'percentuale_servizio',
                        'percentuale_prodotti',
                        'fisso_mensile',
                        'soglia_bonus'
                    )),
    -- Campi per tipo percentuale_servizio / percentuale_prodotti
    percentuale     REAL,
    -- Campo per tipo fisso_mensile
    importo_fisso   REAL,
    -- Campi per tipo soglia_bonus
    soglia_fatturato REAL,
    bonus_importo   REAL,
    -- Validità
    valida_dal      TEXT NOT NULL,   -- YYYY-MM-DD
    valida_al       TEXT,            -- YYYY-MM-DD, NULL = senza scadenza
    -- Opzionale: commissione per servizio specifico
    servizio_id     TEXT,
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_operatori_commissioni_operatore
    ON operatori_commissioni(operatore_id);

CREATE INDEX IF NOT EXISTS idx_operatori_commissioni_valida
    ON operatori_commissioni(operatore_id, valida_dal);

-- View: commissioni attive oggi per dashboard
CREATE VIEW IF NOT EXISTS v_commissioni_attive AS
SELECT
    c.*,
    o.nome || ' ' || o.cognome AS nome_operatore
FROM operatori_commissioni c
JOIN operatori o ON o.id = c.operatore_id
WHERE c.valida_dal <= date('now')
  AND (c.valida_al IS NULL OR c.valida_al >= date('now'));
