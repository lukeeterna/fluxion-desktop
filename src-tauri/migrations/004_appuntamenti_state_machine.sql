-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 004: Appuntamenti State Machine + Override Info
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-03
-- Obiettivo: Aggiungere colonna `stato` con enum esplicito + `override_info` JSON
--
-- Note:
-- - SQLite non supporta ALTER COLUMN, quindi usiamo strategia:
--   1. Aggiungi colonna `override_info`
--   2. Migra dati esistenti (tutti → 'Confermato')
--   3. Note per future cleanup (rimuovere vecchia colonna se necessario)
-- ═══════════════════════════════════════════════════════════════

-- STEP 1: Aggiungi colonna override_info (JSON nullable)
ALTER TABLE appuntamenti ADD COLUMN override_info TEXT;

-- STEP 2: Aggiungi colonna deleted_at se non esiste (soft delete)
-- (potrebbe già esistere, ignora errore se già presente)
ALTER TABLE appuntamenti ADD COLUMN deleted_at TEXT;

-- STEP 3: Migra valori stato esistenti
-- Converte vecchi stati a nuovi stati della state machine:
-- - 'confermato' → 'Confermato'
-- - 'bozza' → 'Bozza'
-- - 'completato' → 'Completato'
-- - 'cancellato' → 'Cancellato'
-- - 'no_show' → 'Rifiutato' (mapping best-effort)

UPDATE appuntamenti
SET stato = CASE stato
    WHEN 'confermato' THEN 'Confermato'
    WHEN 'bozza' THEN 'Bozza'
    WHEN 'completato' THEN 'Completato'
    WHEN 'cancellato' THEN 'Cancellato'
    WHEN 'no_show' THEN 'Rifiutato'
    ELSE 'Confermato'  -- Default fallback
END
WHERE stato IN ('confermato', 'bozza', 'completato', 'cancellato', 'no_show');

-- STEP 4: Crea index su nuova colonna stato
CREATE INDEX IF NOT EXISTS idx_appuntamenti_stato_new ON appuntamenti(stato);

-- STEP 5: Crea index su deleted_at per soft delete queries
CREATE INDEX IF NOT EXISTS idx_appuntamenti_deleted_at ON appuntamenti(deleted_at);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE POST-MIGRATION
-- ═══════════════════════════════════════════════════════════════
-- Verifica che tutti gli appuntamenti abbiano stato valido:
--
-- SELECT stato, COUNT(*) as count
-- FROM appuntamenti
-- WHERE stato NOT IN ('Bozza', 'Proposta', 'InAttesaOperatore', 'Confermato', 'ConfermatoConOverride', 'Rifiutato', 'Completato', 'Cancellato')
-- GROUP BY stato;
--
-- Risultato atteso: 0 rows (tutti gli stati sono validi)
-- ═══════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════
-- NOTE FUTURE CLEANUP (OPZIONALE)
-- ═══════════════════════════════════════════════════════════════
-- Se vuoi applicare CHECK constraint esplicito (richiede ricreare tabella):
--
-- 1. Crea tabella nuova con constraint:
-- CREATE TABLE appuntamenti_new (
--     id TEXT PRIMARY KEY,
--     ...
--     stato TEXT NOT NULL CHECK(stato IN ('Bozza', 'Proposta', 'InAttesaOperatore', 'Confermato', 'ConfermatoConOverride', 'Rifiutato', 'Completato', 'Cancellato')),
--     override_info TEXT,
--     ...
-- );
--
-- 2. Copia dati:
-- INSERT INTO appuntamenti_new SELECT * FROM appuntamenti;
--
-- 3. Drop vecchia tabella:
-- DROP TABLE appuntamenti;
--
-- 4. Rinomina:
-- ALTER TABLE appuntamenti_new RENAME TO appuntamenti;
--
-- ⚠️ ATTENZIONE: Questo rompe foreign keys! Fare solo se necessario.
-- ═══════════════════════════════════════════════════════════════
