-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: SALONE PARRUCCHIERE (restore default)
-- Ripristina il verticale salone dopo test altre verticali
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Salone Demo FLUXION'),
('categoria_attivita', 'salone'),
('macro_categoria', 'hair'),
('micro_categoria', 'salone_parrucchiere');

-- Servizi, operatori, clienti già presenti dal seed originale
-- Basta ripristinare la categoria_attivita

PRAGMA foreign_keys = ON;
