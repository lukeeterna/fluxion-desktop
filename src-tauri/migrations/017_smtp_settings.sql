-- ═══════════════════════════════════════════════════════════════════════════
-- FLUXION Migration 017: SMTP Email Settings
-- Configurazione email per invio ordini fornitori
-- ═══════════════════════════════════════════════════════════════════════════

-- Impostazioni SMTP (configurabili via UI in Impostazioni)
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('smtp_host', 'smtp.gmail.com', 'string'),
    ('smtp_port', '587', 'number'),
    ('smtp_email_from', '', 'string'),
    ('smtp_password', '', 'string'),
    ('smtp_enabled', 'false', 'boolean');

-- Log migration
SELECT '✓ [017] SMTP Settings ready' AS status;
