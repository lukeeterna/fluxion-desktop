-- Migration 033: Add genere column to operatori table (GAP-P1-4)
-- Valori: 'M' (maschile), 'F' (femminile), NULL (non specificato)
-- Usato da Sara per filtro preferenza genere operatore ("vorrei un'operatrice")
ALTER TABLE operatori ADD COLUMN genere TEXT;
