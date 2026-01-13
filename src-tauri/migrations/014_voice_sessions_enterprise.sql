-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 014: Voice Sessions Enterprise + GDPR Audit Log
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-13
-- Fase 7: Voice Agent Enterprise RAG
-- Obiettivo: Sessioni persistenti e audit logging GDPR-compliant
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Voice Sessions Table
-- Stores conversation sessions for persistence and analytics
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS voice_sessions (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL DEFAULT 'voice' CHECK(channel IN ('voice', 'whatsapp', 'web')),
    state TEXT NOT NULL DEFAULT 'active' CHECK(state IN ('active', 'idle', 'completed', 'escalated', 'timeout')),
    verticale_id TEXT NOT NULL,
    business_name TEXT NOT NULL,

    -- Client info (nullable until identified)
    cliente_id TEXT REFERENCES clienti(id),
    cliente_nome TEXT,
    phone_number TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,

    -- Outcome
    outcome TEXT CHECK(outcome IN ('booking_created', 'info_provided', 'escalated', 'timeout', 'cancelled', 'unknown')),
    booking_id TEXT REFERENCES appuntamenti(id),
    escalation_reason TEXT,

    -- Metrics
    total_turns INTEGER DEFAULT 0,
    avg_latency_ms REAL DEFAULT 0,
    groq_calls INTEGER DEFAULT 0,

    -- Context JSON (booking state, entities, etc.)
    context_json TEXT DEFAULT '{}'
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_voice_sessions_state ON voice_sessions(state);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_cliente ON voice_sessions(cliente_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_created ON voice_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_outcome ON voice_sessions(outcome);

-- ───────────────────────────────────────────────────────────────
-- STEP 2: Voice Session Turns Table
-- Stores individual conversation turns
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS voice_session_turns (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES voice_sessions(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,

    -- Content (anonymized after retention period)
    user_input TEXT NOT NULL,
    intent TEXT,
    response TEXT NOT NULL,

    -- Metrics
    latency_ms REAL DEFAULT 0,
    layer_used TEXT CHECK(layer_used IN ('L0_special', 'L1_exact', 'L2_slot', 'L3_faq', 'L4_groq')),

    -- Analysis
    sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')),
    frustration_level INTEGER DEFAULT 0,
    intent_confidence REAL DEFAULT 0,

    -- Entities extracted (JSON)
    entities_json TEXT DEFAULT '{}',

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),

    -- GDPR: retention marker
    anonymized_at TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_voice_turns_session ON voice_session_turns(session_id);
CREATE INDEX IF NOT EXISTS idx_voice_turns_intent ON voice_session_turns(intent);
CREATE INDEX IF NOT EXISTS idx_voice_turns_layer ON voice_session_turns(layer_used);

-- ───────────────────────────────────────────────────────────────
-- STEP 3: GDPR Audit Log
-- Tracks all voice agent actions for compliance
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS voice_audit_log (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now')),

    -- Details (anonymized after retention period)
    details_json TEXT DEFAULT '{}',

    -- GDPR compliance
    retention_until TEXT NOT NULL,
    anonymized_at TEXT,

    -- Actor
    actor_type TEXT DEFAULT 'voice_agent' CHECK(actor_type IN ('voice_agent', 'operator', 'system')),
    actor_id TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_voice_audit_session ON voice_audit_log(session_id);
CREATE INDEX IF NOT EXISTS idx_voice_audit_action ON voice_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_voice_audit_retention ON voice_audit_log(retention_until);
CREATE INDEX IF NOT EXISTS idx_voice_audit_timestamp ON voice_audit_log(timestamp);

-- ───────────────────────────────────────────────────────────────
-- STEP 4: Voice Agent Business Config Extension
-- Additional config for enterprise features
-- ───────────────────────────────────────────────────────────────

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    min_advance_hours INTEGER DEFAULT 2;

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    max_advance_days INTEGER DEFAULT 60;

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    lunch_break_start TEXT DEFAULT '13:00';

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    lunch_break_end TEXT DEFAULT '14:00';

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    gdpr_retention_days INTEGER DEFAULT 30;

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    enable_waitlist INTEGER DEFAULT 1;

ALTER TABLE voice_agent_config ADD COLUMN IF NOT EXISTS
    enable_operator_preference INTEGER DEFAULT 1;

-- ───────────────────────────────────────────────────────────────
-- STEP 5: GDPR Anonymization Job Marker
-- Trigger-based anonymization after retention period
-- ───────────────────────────────────────────────────────────────

-- View for pending anonymization
CREATE VIEW IF NOT EXISTS v_voice_pending_anonymization AS
SELECT
    'voice_session_turns' AS table_name,
    id,
    session_id,
    created_at
FROM voice_session_turns
WHERE anonymized_at IS NULL
  AND created_at < datetime('now', '-30 days')

UNION ALL

SELECT
    'voice_audit_log' AS table_name,
    id,
    session_id,
    timestamp AS created_at
FROM voice_audit_log
WHERE anonymized_at IS NULL
  AND retention_until < datetime('now');

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'voice%';
-- SELECT * FROM v_voice_pending_anonymization LIMIT 10;
-- ═══════════════════════════════════════════════════════════════
