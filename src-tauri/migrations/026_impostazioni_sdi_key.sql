-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 026: Aggiunge fattura24_api_key a impostazioni_fatturazione
-- Task: W1-A — Fix SDI API Key security (rimuove window.prompt cleartext)
-- Data: 2026-03-02
-- ═══════════════════════════════════════════════════════════════

-- Aggiunge colonna per API key Fattura24 salvata localmente
-- Sostituisce il window.prompt() insicuro in Fatture.tsx
ALTER TABLE impostazioni_fatturazione ADD COLUMN fattura24_api_key TEXT;

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT id, fattura24_api_key FROM impostazioni_fatturazione WHERE id = 'default';
