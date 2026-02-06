-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 022: WhatsApp Invii Pacchetti Tracking
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-02-06
-- Obiettivo: Tabella tracking invio pacchetti via WhatsApp marketing
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Crea tabella tracking invii WhatsApp
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS whatsapp_invii (
    id TEXT PRIMARY KEY,
    pacchetto_id TEXT NOT NULL,
    filtro TEXT NOT NULL, -- 'tutti' | 'vip' | 'vip_3_plus'
    totale_clienti INTEGER NOT NULL DEFAULT 0,
    inviati INTEGER NOT NULL DEFAULT 0,
    falliti INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id)
);

-- Index per performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_invii_pacchetto 
    ON whatsapp_invii(pacchetto_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_invii_created 
    ON whatsapp_invii(created_at);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT * FROM whatsapp_invii ORDER BY created_at DESC LIMIT 5;
-- ═══════════════════════════════════════════════════════════════
