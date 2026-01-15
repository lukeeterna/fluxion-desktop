-- Migration 015: License System
-- FLUXION Phase 8: Build + Licenze
-- Keygen.sh integration with 30-day trial, offline caching

-- License cache table for offline validation (singleton)
CREATE TABLE IF NOT EXISTS license_cache (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    license_key TEXT,                       -- User's license key (nullable for trial)
    license_id TEXT,                        -- Keygen license ID
    machine_id TEXT,                        -- Keygen machine ID for this device
    fingerprint TEXT NOT NULL,              -- Hardware fingerprint (SHA-256)
    tier TEXT DEFAULT 'trial',              -- 'trial', 'base', 'ia'
    status TEXT DEFAULT 'trial',            -- 'trial', 'active', 'expired', 'suspended'
    trial_started_at TEXT,                  -- When trial began (ISO 8601)
    trial_ends_at TEXT,                     -- Trial expiry date
    expiry_date TEXT,                       -- License expiry (ISO 8601)
    last_validated_at TEXT,                 -- Last successful online validation
    validation_response TEXT,               -- Cached JSON response from Keygen
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- License event history (audit trail)
CREATE TABLE IF NOT EXISTS license_history (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    event_type TEXT NOT NULL,               -- 'trial_started', 'activated', 'validated',
                                            -- 'expired', 'deactivated', 'validation_failed'
    license_key TEXT,                       -- Masked key for privacy (XXXX-XXXX-...-1234)
    fingerprint TEXT,
    tier TEXT,
    response_code TEXT,                     -- Keygen validation code
    response_detail TEXT,                   -- Additional info
    created_at TEXT DEFAULT (datetime('now'))
);

-- Index for history queries
CREATE INDEX IF NOT EXISTS idx_license_history_date ON license_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_license_history_type ON license_history(event_type);

-- Initialize with trial mode on first app launch
-- This is handled in Rust code, not here
