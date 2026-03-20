-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 012: Operatori Voice Agent Enhancement
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-11
-- Fase 7: Voice Agent
-- Obiettivo: Aggiungere campi per descrizione positiva operatori
--            usata dal Voice Agent per proporre alternative
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Campi Voice Agent per operatori
-- ───────────────────────────────────────────────────────────────

-- Specializzazioni (JSON array): ["taglio", "colore", "barba"]
ALTER TABLE operatori ADD COLUMN specializzazioni TEXT DEFAULT '[]';

-- Descrizione positiva per Voice Agent
-- Es: "Specialista in colorazioni creative, 10 anni di esperienza"
ALTER TABLE operatori ADD COLUMN descrizione_positiva TEXT;

-- Anni di esperienza (per costruire descrizioni automatiche)
ALTER TABLE operatori ADD COLUMN anni_esperienza INTEGER DEFAULT 0;

-- STEP 2: Demo data removed for production.
-- Operators are created by the user via Setup Wizard.

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT nome, specializzazioni, descrizione_positiva, anni_esperienza
-- FROM operatori WHERE attivo = 1;
-- ═══════════════════════════════════════════════════════════════
