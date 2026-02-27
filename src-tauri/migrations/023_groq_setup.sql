-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 023: Groq API Key per Voice Agent
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-02-27
-- Obiettivo: Archiviare la Groq API key configurata durante il wizard
--            Evita di richiedere .env manuale all'utente
-- ═══════════════════════════════════════════════════════════════

INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('groq_api_key', '', 'string');

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- SELECT chiave, valore FROM impostazioni WHERE chiave = 'groq_api_key';
-- ═══════════════════════════════════════════════════════════════
