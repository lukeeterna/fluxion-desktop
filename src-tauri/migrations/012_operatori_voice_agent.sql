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

-- ───────────────────────────────────────────────────────────────
-- STEP 2: Popola dati demo
-- ───────────────────────────────────────────────────────────────

-- Aggiorna operatori esistenti con dati demo
UPDATE operatori SET
    specializzazioni = '["taglio", "piega"]',
    descrizione_positiva = 'Esperta in tagli moderni e pieghe eleganti',
    anni_esperienza = 8
WHERE nome = 'Maria' OR nome LIKE '%Maria%';

UPDATE operatori SET
    specializzazioni = '["colore", "trattamenti"]',
    descrizione_positiva = 'Specialista colorazioni e trattamenti rigeneranti',
    anni_esperienza = 12
WHERE nome = 'Laura' OR nome LIKE '%Laura%';

UPDATE operatori SET
    specializzazioni = '["taglio", "barba"]',
    descrizione_positiva = 'Maestro del taglio classico e cura della barba',
    anni_esperienza = 15
WHERE nome = 'Marco' OR nome LIKE '%Marco%';

-- Se non ci sono operatori, creane alcuni demo
INSERT OR IGNORE INTO operatori (id, nome, cognome, specializzazioni, descrizione_positiva, anni_esperienza, attivo)
VALUES
    ('op-paola', 'Paola', 'Verdi', '["taglio", "colore", "piega"]', 'La titolare! Esperta in ogni tipo di trattamento', 20, 1),
    ('op-giulia', 'Giulia', 'Bianchi', '["colore", "extension"]', 'Artista del colore e delle extension', 5, 1);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT nome, specializzazioni, descrizione_positiva, anni_esperienza
-- FROM operatori WHERE attivo = 1;
-- ═══════════════════════════════════════════════════════════════
