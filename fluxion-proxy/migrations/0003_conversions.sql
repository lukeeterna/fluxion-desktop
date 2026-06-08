-- S346 — R1 Sales Agent: attribuzione conversione (§6.7 FACTORY_MASTER).
-- Mappa una checkout.session.completed Stripe al lead WA d'origine, via
-- client_reference_id = "lead_<id>" inviato dal payment link (checkout.py).
--
-- session_id UNIQUE -> INSERT OR IGNORE idempotente sui retry webhook Stripe.
-- amount = session.amount_total (centesimi). email = customer email.
-- at = ISO timestamp lato worker.
-- Loop chiuso lato Mac: `python3 agent.py won --lead <id>` (il leads.db locale
-- non e' raggiungibile dal Worker; D1 e' la sorgente d'attribuzione).

CREATE TABLE IF NOT EXISTS conversions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id     TEXT NOT NULL,
  session_id  TEXT NOT NULL UNIQUE,
  amount      INTEGER,
  email       TEXT,
  at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversions_lead_id ON conversions(lead_id);
