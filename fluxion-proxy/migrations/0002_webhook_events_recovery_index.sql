-- S298 — Recovery query composite index optimization
-- Optimizes recovery path: WHERE customer_email = ? ORDER BY created_at DESC LIMIT 1
-- (fluxion-proxy/src/routes/license-recovery.ts:117)
--
-- Pre: single-column idx(customer_email) → SQLite reads N matching rows + runtime sort
-- Post: composite idx(customer_email, created_at DESC) → ordered index seek, zero sort
--
-- Impact: O(log N) ordered lookup for clients with multiple purchases (recurring/upgrade).
-- Safe: CREATE INDEX IF NOT EXISTS — idempotent across replays. Old single-column index
-- retained (CREATE INDEX IF NOT EXISTS in 0001) — minimal storage overhead, useful for
-- non-ordered customer_email matches (none currently, but future-safe).

CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email_created_desc
  ON webhook_events(customer_email, created_at DESC);
