-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 029: SDI Multi-Provider
-- Aggiunge supporto Aruba FE (primario) + OpenAPI.com (secondario)
-- Mantiene Fattura24 per retrocompatibilità
-- Data: 2026-03-03
-- ═══════════════════════════════════════════════════════════════

-- Provider SDI attivo (default: fattura24 per retrocompat)
ALTER TABLE impostazioni_fatturazione ADD COLUMN sdi_provider TEXT NOT NULL DEFAULT 'fattura24';

-- API key Aruba Fatturazione Elettronica
-- Ottenibile da: fatturazioneelettronica.aruba.it → Account → API
ALTER TABLE impostazioni_fatturazione ADD COLUMN aruba_api_key TEXT;

-- API key OpenAPI.com SDI
-- Ottenibile da: console.openapi.com → API Keys
ALTER TABLE impostazioni_fatturazione ADD COLUMN openapi_api_key TEXT;

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT id, sdi_provider, aruba_api_key, openapi_api_key
-- FROM impostazioni_fatturazione WHERE id = 'default';
-- Expected: sdi_provider = 'fattura24', api keys = NULL
