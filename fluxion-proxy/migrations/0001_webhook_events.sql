-- S291 — Webhook events dedup + license payload persistence
-- D1 schema: idempotency primary store (replaces KV-only FSAF-09 S286)
--
-- event_id PK = Stripe event id (evt_xxx) — UNIQUE guarantees INSERT OR IGNORE dedup
-- session_id = checkout.session.completed session id (cs_test_xxx)
-- license_id = sha256(session_id || product || customer_email) — deterministic
-- license_payload = JSON canonical (signed payload kid:v1)
-- license_signature = base64 64-byte Ed25519 signature
-- email_sent_at = unix epoch when Resend OK (NULL if not yet sent — replay re-send path)
-- created_at = unix epoch INSERT (replay never overwritten)
--
-- Replay logic (handler):
--   SELECT * WHERE event_id = ? -> if row exists AND email_sent_at IS NULL:
--     re-send email reading license_payload+license_signature -> UPDATE email_sent_at = unixepoch()
--   else: idempotent_replay true, no-op.

CREATE TABLE IF NOT EXISTS webhook_events (
  event_id          TEXT PRIMARY KEY NOT NULL,
  session_id        TEXT NOT NULL,
  license_id        TEXT NOT NULL,
  customer_email    TEXT NOT NULL,
  product           TEXT NOT NULL,
  license_payload   TEXT NOT NULL,
  license_signature TEXT NOT NULL,
  email_sent_at     INTEGER NULL,
  created_at        INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_webhook_events_session_id ON webhook_events(session_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_customer_email ON webhook_events(customer_email);
CREATE INDEX IF NOT EXISTS idx_webhook_events_email_sent_at ON webhook_events(email_sent_at);
