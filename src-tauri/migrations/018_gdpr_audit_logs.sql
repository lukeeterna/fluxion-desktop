-- ═══════════════════════════════════════════════════════════════════════════
-- FLUXION Migration 018: GDPR Audit Log System
-- Sistema di audit trail per conformità GDPR
-- ═══════════════════════════════════════════════════════════════════════════

-- Tabella audit_log principale - tracciamento completo operazioni su dati personali
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    user_id TEXT,                           -- session_id (voice) or operator_id
    user_type TEXT NOT NULL,                -- 'voice_session', 'operator', 'system'
    
    -- Azione eseguita
    action TEXT NOT NULL,                   -- 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT', 'ANONYMIZE'
    entity_type TEXT NOT NULL,              -- 'cliente', 'appuntamento', 'consenso', 'voice_session', 'operator'
    entity_id TEXT NOT NULL,                -- UUID dell'entità coinvolta
    
    -- Dati (JSON per flessibilità)
    data_before TEXT,                       -- JSON snapshot before (null per CREATE)
    data_after TEXT,                        -- JSON snapshot after (null per DELETE)
    changed_fields TEXT,                    -- JSON array di nomi campi modificati
    
    -- GDPR metadata - classificazione dati
    gdpr_category TEXT NOT NULL,            -- 'personal_data', 'consent', 'booking', 'voice_session', 'financial'
    source TEXT NOT NULL,                   -- 'voice', 'web', 'api', 'system', 'mobile'
    legal_basis TEXT,                       -- 'consent', 'contract', 'legitimate_interest', 'legal_obligation'
    
    -- Retention policy - gestione automatica
    retention_until TEXT NOT NULL,          -- Data purge automatica (calcolata da policy)
    anonymized_at TEXT,                     -- Timestamp anonimizzazione (se applicata)
    
    -- Metadata tecnico - audit trail completo
    ip_address TEXT,                        -- IP richiesta (se disponibile)
    user_agent TEXT,                        -- User agent client
    request_id TEXT,                        -- Correlazione log distribuiti
    
    -- Validazione constraint
    CHECK (user_type IN ('voice_session', 'operator', 'system', 'api')),
    CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT', 'ANONYMIZE', 'LOGIN', 'LOGOUT')),
    CHECK (gdpr_category IN ('personal_data', 'consent', 'booking', 'voice_session', 'financial', 'marketing')),
    CHECK (source IN ('voice', 'web', 'api', 'system', 'mobile', 'integration')),
    CHECK (legal_basis IS NULL OR legal_basis IN ('consent', 'contract', 'legitimate_interest', 'legal_obligation', 'vital_interests', 'public_task'))
);

-- Tabella configurazione GDPR - policy retention dinamiche
CREATE TABLE IF NOT EXISTS gdpr_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,                       -- Documentazione uso del setting
    updated_at TEXT DEFAULT (datetime('now')),
    updated_by TEXT                         -- Chi ha modificato l'impostazione
);

-- Inserisci default retention policy (in giorni)
INSERT OR IGNORE INTO gdpr_settings (key, value, description) VALUES
    ('retention_personal_data', '2555', 'Retention dati personali cliente (7 anni - art. 2940 c.c. prescrizione)'),
    ('retention_consent', '1825', 'Retention consensi GDPR (5 anni dopo revoca)'),
    ('retention_booking', '1095', 'Retention storico appuntamenti (3 anni)'),
    ('retention_voice_session', '365', 'Retention sessioni vocali (1 anno)'),
    ('retention_audit_log', '2555', 'Retention log audit (7 anni - obbligo legale)'),
    ('retention_financial', '3650', 'Retention dati fiscali (10 anni)'),
    ('auto_purge_enabled', 'true', 'Abilita purge automatica dati scaduti'),
    ('auto_anonymize_enabled', 'true', 'Abilita anonimizzazione automatica'),
    ('anonymize_after_days', '90', 'Giorni dopo cui anonimizzare dati inattivi'),
    ('encryption_at_rest', 'true', 'Crittografia dati sensibili a riposo');

-- Tabella per richieste GDPR (accesso, retifica, cancellazione, portabilità)
CREATE TABLE IF NOT EXISTS gdpr_requests (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    request_type TEXT NOT NULL,             -- 'access', 'rectification', 'erasure', 'portability', 'restriction'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'rejected'
    
    -- Identificazione soggetto
    cliente_id TEXT,                        -- Riferimento cliente (se noto)
    email_richiedente TEXT NOT NULL,        -- Email per comunicazioni
    nome_richiedente TEXT,                  -- Nome completo richiedente
    
    -- Dettagli richiesta
    descrizione TEXT,                       -- Descrizione dettagliata richiesta
    allegati TEXT,                          -- JSON array di documenti allegati
    
    -- Timeline
    created_at TEXT DEFAULT (datetime('now')),
    deadline_at TEXT NOT NULL,              -- Scadenza 30 giorni GDPR
    completed_at TEXT,                      -- Completamento effettivo
    
    -- Assegnazione e risoluzione
    assigned_to TEXT,                       -- Operatore assegnato
    resolution_notes TEXT,                  -- Note risoluzione
    rejection_reason TEXT,                  -- Motivo rifiuto (se applicabile)
    
    -- Audit
    audit_log_ids TEXT,                     -- JSON array di ID audit_log correlati
    
    CHECK (request_type IN ('access', 'rectification', 'erasure', 'portability', 'restriction', 'objection')),
    CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected', 'cancelled'))
);

-- ═══════════════════════════════════════════════════════════════════════════
-- INDEXES - Ottimizzazione performance query comuni
-- ═══════════════════════════════════════════════════════════════════════════

-- Ricerche temporali (report, purge)
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp_desc ON audit_log(timestamp DESC);

-- Ricerche per entità (storia completa di un record)
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity_time ON audit_log(entity_type, entity_id, timestamp DESC);

-- Ricerche per utente (chi ha fatto cosa)
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id, user_type);
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON audit_log(user_id, timestamp DESC);

-- Retention management - purge efficiente
CREATE INDEX IF NOT EXISTS idx_audit_retention ON audit_log(retention_until) WHERE anonymized_at IS NULL;

-- Report GDPR per categoria e sorgente
CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_log(gdpr_category, source);
CREATE INDEX IF NOT EXISTS idx_audit_category_time ON audit_log(gdpr_category, timestamp);

-- Ricerche specifiche azione/entità
CREATE INDEX IF NOT EXISTS idx_audit_action_entity ON audit_log(action, entity_type);

-- Correlazione richieste
CREATE INDEX IF NOT EXISTS idx_audit_request_id ON audit_log(request_id) WHERE request_id IS NOT NULL;

-- GDPR requests indexes
CREATE INDEX IF NOT EXISTS idx_gdpr_req_status ON gdpr_requests(status);
CREATE INDEX IF NOT EXISTS idx_gdpr_req_deadline ON gdpr_requests(deadline_at) WHERE status IN ('pending', 'in_progress');
CREATE INDEX IF NOT EXISTS idx_gdpr_req_cliente ON gdpr_requests(cliente_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS - Reportistica comune
-- ═══════════════════════════════════════════════════════════════════════════

-- View: operazioni recenti per dashboard
CREATE VIEW IF NOT EXISTS v_audit_recent AS
SELECT 
    a.id,
    a.timestamp,
    a.user_type,
    a.action,
    a.entity_type,
    a.gdpr_category,
    a.source,
    CASE 
        WHEN a.user_type = 'operator' THEN (SELECT nome FROM operatori WHERE id = a.user_id)
        WHEN a.user_type = 'voice_session' THEN 'Voice: ' || substr(a.user_id, 1, 8)
        ELSE a.user_type
    END as user_display
FROM audit_log a
ORDER BY a.timestamp DESC
LIMIT 1000;

-- View: statistiche per categoria GDPR
CREATE VIEW IF NOT EXISTS v_audit_stats_by_category AS
SELECT 
    gdpr_category,
    source,
    action,
    count(*) as operation_count,
    min(timestamp) as first_operation,
    max(timestamp) as last_operation
FROM audit_log
GROUP BY gdpr_category, source, action;

-- View: richieste GDPR in scadenza
CREATE VIEW IF NOT EXISTS v_gdpr_requests_due AS
SELECT 
    *,
    julianday(deadline_at) - julianday('now') as days_remaining
FROM gdpr_requests
WHERE status IN ('pending', 'in_progress')
ORDER BY deadline_at ASC;

-- Log migration
SELECT '✓ [018] GDPR Audit Log System ready - Tables: audit_log, gdpr_settings, gdpr_requests' AS status;
