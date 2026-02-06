-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 021: Setup Wizard Configuration Fields
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-02-06
-- Obiettivo: Aggiungere campi configurazione business per WhatsApp e Voice
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Aggiungi campi configurazione mancanti
-- ───────────────────────────────────────────────────────────────

-- Numero WhatsApp Business per notifiche clienti
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('whatsapp_number', '', 'string');

-- Numero linea fissa EhiWeb per Voice Agent (opzionale)
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('ehiweb_number', '', 'string');

-- Indirizzo completo per QR code e documenti
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('indirizzo_completo', '', 'string');

-- URL sito web (opzionale)
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('sito_web', '', 'string');

-- ───────────────────────────────────────────────────────────────
-- STEP 2: Update nome_attivita se ha valore default
-- ───────────────────────────────────────────────────────────────

UPDATE impostazioni 
SET valore = '' 
WHERE chiave = 'nome_attivita' 
AND valore = 'La Mia Attività';

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT chiave, valore FROM impostazioni 
-- WHERE chiave IN ('nome_attivita', 'whatsapp_number', 'ehiweb_number', 'indirizzo_completo', 'sito_web');
-- ═══════════════════════════════════════════════════════════════
