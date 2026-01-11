-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 013: Waitlist con Priorità VIP
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-11
-- Fase 7: Voice Agent
-- Obiettivo: Tabella lista d'attesa con sistema priorità
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Tabella Waitlist
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS waitlist (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clienti(id),
    servizio TEXT NOT NULL,
    data_preferita TEXT,           -- YYYY-MM-DD
    ora_preferita TEXT,            -- HH:MM
    operatore_preferito TEXT REFERENCES operatori(id),
    priorita TEXT DEFAULT 'normale', -- 'normale', 'vip', 'urgente'
    priorita_valore INTEGER DEFAULT 10, -- 10=normale, 50=vip, 100=urgente
    note TEXT,
    stato TEXT DEFAULT 'attesa',   -- 'attesa', 'contattato', 'prenotato', 'annullato'
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    contattato_at TEXT,            -- Quando è stato contattato
    prenotato_at TEXT              -- Quando ha prenotato
);

-- ───────────────────────────────────────────────────────────────
-- STEP 2: Indici per ordinamento priorità
-- ───────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_waitlist_priorita ON waitlist(priorita_valore DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_waitlist_stato ON waitlist(stato);
CREATE INDEX IF NOT EXISTS idx_waitlist_cliente ON waitlist(cliente_id);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT * FROM waitlist ORDER BY priorita_valore DESC, created_at ASC;
-- ═══════════════════════════════════════════════════════════════
