-- =============================================================================
-- S251 Cat 3 P0 #2 Step D — GDPR Encryption Migration State
-- =============================================================================
-- Marker table consulted by `data_migration::encrypt_clienti_pii` to make the
-- one-shot legacy-row re-encryption runner idempotent across app restarts.
--
-- Row contract (one row per migration_key):
--   migration_key    Logical name of the data migration (e.g.
--                    "encrypt_clienti_pii_v1"). The runner refuses to re-apply
--                    when the row is present.
--   applied_at       ISO 8601 timestamp set when the marker is inserted (i.e.
--                    after the runner has finished encrypting every plaintext
--                    row it found).
--   rows_processed   Number of rows the runner mutated (UPDATE clienti). 0 is
--                    legitimate on installs that never held plaintext PII.
--   backup_path      Absolute path of the `VACUUM INTO` backup snapshot taken
--                    BEFORE any UPDATE. Used by support/recovery tooling.
--
-- IMPORTANT: do NOT delete rows from this table. Removing the marker would
-- cause the runner to attempt re-encryption of already-Base64 ciphertext, and
-- the detection heuristic (decrypt_field → Ok = already encrypted) would
-- correctly skip every row, but a fresh backup would be taken unnecessarily.
-- =============================================================================

CREATE TABLE IF NOT EXISTS encryption_migration_state (
    migration_key   TEXT PRIMARY KEY,
    applied_at      TEXT NOT NULL DEFAULT (datetime('now')),
    rows_processed  INTEGER NOT NULL DEFAULT 0,
    backup_path     TEXT
);
