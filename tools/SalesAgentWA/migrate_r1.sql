-- migrate_r1.sql — eseguire una volta: sqlite3 leads.db < migrate_r1.sql
ALTER TABLE messages ADD COLUMN reply_intent TEXT;          -- hot|negative|risk|other
ALTER TABLE messages ADD COLUMN handoff_status TEXT DEFAULT 'none';  -- none|queued|claimed|closed
ALTER TABLE messages ADD COLUMN checkout_url TEXT;
ALTER TABLE messages ADD COLUMN converted_at TEXT;

ALTER TABLE leads ADD COLUMN do_not_contact INTEGER DEFAULT 0;  -- suppression list
ALTER TABLE leads ADD COLUMN outcome TEXT;                       -- won|lost|null

CREATE INDEX IF NOT EXISTS idx_messages_handoff ON messages(handoff_status);
CREATE INDEX IF NOT EXISTS idx_messages_intent  ON messages(reply_intent);
CREATE INDEX IF NOT EXISTS idx_leads_dnc        ON leads(do_not_contact);
