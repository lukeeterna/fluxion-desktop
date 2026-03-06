-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Migration 030: Cliente Media (Foto/Video)
-- F06 Media Upload Sprint A
-- ═══════════════════════════════════════════════════════════════════

-- Tabella principale media per clienti
CREATE TABLE IF NOT EXISTS cliente_media (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id        INTEGER NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
  media_path        TEXT NOT NULL,
  thumb_path        TEXT,
  tipo              TEXT NOT NULL CHECK(tipo IN ('foto', 'video')),
  categoria         TEXT NOT NULL DEFAULT 'generale',
  appuntamento_id   INTEGER REFERENCES appuntamenti(id),
  operatore_id      INTEGER REFERENCES operatori(id),
  dimensione_bytes  INTEGER,
  larghezza_px      INTEGER,
  altezza_px        INTEGER,
  durata_sec        INTEGER,
  consenso_gdpr     INTEGER NOT NULL DEFAULT 0,
  visibilita        TEXT NOT NULL DEFAULT 'interno',
  watermark         INTEGER NOT NULL DEFAULT 0,
  note              TEXT,
  tag               TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cliente_media_cliente    ON cliente_media(cliente_id);
CREATE INDEX IF NOT EXISTS idx_cliente_media_categoria  ON cliente_media(categoria);
CREATE INDEX IF NOT EXISTS idx_cliente_media_appuntamento ON cliente_media(appuntamento_id);

-- Tabella trasformazioni before/after (coppia di media)
CREATE TABLE IF NOT EXISTS cliente_media_trasformazioni (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id      INTEGER NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
  media_prima_id  INTEGER NOT NULL REFERENCES cliente_media(id) ON DELETE CASCADE,
  media_dopo_id   INTEGER NOT NULL REFERENCES cliente_media(id) ON DELETE CASCADE,
  appuntamento_id INTEGER REFERENCES appuntamenti(id),
  servizio_tag    TEXT,
  consenso_social INTEGER NOT NULL DEFAULT 0,
  note            TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Consenso GDPR media per cliente (colonne aggiunte alla tabella clienti)
ALTER TABLE clienti ADD COLUMN media_consenso_interno INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_social  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_clinico INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_data    TEXT;
