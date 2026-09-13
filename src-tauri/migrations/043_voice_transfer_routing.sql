-- Migration 043: Sara live-transfer routing policy
-- Personal operator phones remain encrypted in operatori.telefono.
-- These non-PII flags are explicit opt-in/reachability/routing metadata.

ALTER TABLE operatori ADD COLUMN voice_transfer_enabled INTEGER NOT NULL DEFAULT 0 CHECK(voice_transfer_enabled IN (0, 1));
ALTER TABLE operatori ADD COLUMN voice_transfer_reachable INTEGER NOT NULL DEFAULT 1 CHECK(voice_transfer_reachable IN (0, 1));
ALTER TABLE operatori ADD COLUMN voice_transfer_priority INTEGER NOT NULL DEFAULT 100 CHECK(voice_transfer_priority BETWEEN 0 AND 9999);

CREATE INDEX IF NOT EXISTS idx_operatori_voice_transfer
ON operatori(attivo, voice_transfer_enabled, voice_transfer_reachable, voice_transfer_priority);
