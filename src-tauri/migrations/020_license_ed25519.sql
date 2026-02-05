-- ═══════════════════════════════════════════════════════════════════
-- MIGRATION 020: License System Ed25519 (Offline)
-- FLUXION Phase 8.5: Sistema licenze completamente offline
-- 
-- Aggiunge supporto per licenze Ed25519 firmate offline
-- mantenendo compatibilità con sistema Keygen esistente
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- AGGIORNA TABELLA LICENSE_CACHE
-- ─────────────────────────────────────────────────────────────────────

-- Aggiungi campi per sistema Ed25519 (se non esistono già)
ALTER TABLE license_cache ADD COLUMN license_data TEXT;
ALTER TABLE license_cache ADD COLUMN license_signature TEXT;
ALTER TABLE license_cache ADD COLUMN licensee_name TEXT;
ALTER TABLE license_cache ADD COLUMN licensee_email TEXT;
ALTER TABLE license_cache ADD COLUMN enabled_verticals TEXT DEFAULT '[]';
ALTER TABLE license_cache ADD COLUMN features TEXT DEFAULT '{}';
ALTER TABLE license_cache ADD COLUMN issued_at TEXT;
ALTER TABLE license_cache ADD COLUMN is_ed25519 INTEGER DEFAULT 0;

-- Aggiorna tier values per includere 'pro' oltre a 'base', 'ia', 'trial'
-- Nota: i tier validi sono ora: trial, base, pro, enterprise

-- ═══════════════════════════════════════════════════════════════════
-- NOTE IMPLEMENTAZIONE
-- ═══════════════════════════════════════════════════════════════════

/*
Il sistema Ed25519 usa:
- license_data: JSON della licenza (FluxionLicense)
- license_signature: Firma Ed25519 in base64
- enabled_verticals: JSON array di verticali abilitate ["odontoiatrica", "estetica", ...]
- features: JSON con funzionalità abilitate {voice_agent: true, ...}
- is_ed25519: 1 se licenza Ed25519, 0 se Keygen legacy

Tier supportati:
- trial: Prova 30 giorni, tutte le funzioni
- base: €199, 1 verticale, base functions
- pro: €399, 3 verticali, voice, AI
- enterprise: €799, tutte le verticali, API access

Compatibilità:
- Le licenze Keygen esistenti continuano a funzionare (is_ed25519 = 0)
- Il nuovo sistema è preferito quando is_ed25519 = 1
*/
