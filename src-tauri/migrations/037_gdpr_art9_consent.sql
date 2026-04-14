-- Migration 037: GDPR Art.9 explicit consent tracking for health verticals
-- Required for: odontoiatra, fisioterapia, medico_generico, specialista, etc.
-- Art.9 GDPR: processing of special categories of personal data (health)

CREATE TABLE IF NOT EXISTS gdpr_consents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    consent_type  TEXT    NOT NULL CHECK(consent_type IN ('base_art6', 'health_art9')),
    granted_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    granted_by    TEXT    NOT NULL,          -- nome firmatario
    email         TEXT,                       -- email firmatario
    version       TEXT    NOT NULL DEFAULT '1.0',
    revoked_at    TEXT                        -- NULL = active, set = revoked
);

CREATE INDEX IF NOT EXISTS idx_gdpr_consents_type ON gdpr_consents(consent_type);
