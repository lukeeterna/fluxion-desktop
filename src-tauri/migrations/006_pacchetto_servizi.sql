-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 006: Pacchetto Servizi (Many-to-Many)
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-04
-- Obiettivo: Collegare pacchetti a servizi specifici
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Tabella di collegamento Pacchetto <-> Servizi
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS pacchetto_servizi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    pacchetto_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,

    -- Quantità di questo servizio nel pacchetto
    quantita INTEGER DEFAULT 1,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),

    -- Un servizio può essere aggiunto una sola volta per pacchetto
    UNIQUE(pacchetto_id, servizio_id)
);

CREATE INDEX IF NOT EXISTS idx_pacchetto_servizi_pacchetto ON pacchetto_servizi(pacchetto_id);
CREATE INDEX IF NOT EXISTS idx_pacchetto_servizi_servizio ON pacchetto_servizi(servizio_id);

-- ═══════════════════════════════════════════════════════════════
-- Fine Migration 006
-- ═══════════════════════════════════════════════════════════════
