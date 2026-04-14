-- Migration 036: Add missing indexes identified in S154 Production Readiness Audit
-- Performance: clienti.deleted_at used in ~40 queries with WHERE deleted_at IS NULL

CREATE INDEX IF NOT EXISTS idx_clienti_deleted_at ON clienti(deleted_at);
CREATE INDEX IF NOT EXISTS idx_appuntamenti_deleted_at ON appuntamenti(deleted_at);
CREATE INDEX IF NOT EXISTS idx_fatture_deleted_at ON fatture(deleted_at);
CREATE INDEX IF NOT EXISTS idx_incassi_deleted_at ON incassi(deleted_at);
CREATE INDEX IF NOT EXISTS idx_chiamate_voice_deleted_at ON chiamate_voice(deleted_at);
