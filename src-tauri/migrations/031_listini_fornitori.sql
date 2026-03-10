-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Migration 031: Listini Fornitori (Gap #5)
-- Import Excel/CSV listini prezzi da fornitori con storico variazioni
-- ═══════════════════════════════════════════════════════════════════

-- Tabella principale: testata listino importato
CREATE TABLE IF NOT EXISTS listini_fornitori (
  id              TEXT PRIMARY KEY,
  fornitore_id    TEXT NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
  nome_listino    TEXT NOT NULL,
  data_import     TEXT NOT NULL DEFAULT (datetime('now')),
  data_validita   TEXT,
  formato_fonte   TEXT NOT NULL CHECK(formato_fonte IN ('xlsx','xls','csv')),
  righe_totali    INTEGER NOT NULL DEFAULT 0,
  righe_inserite  INTEGER NOT NULL DEFAULT 0,
  righe_aggiornate INTEGER NOT NULL DEFAULT 0,
  note            TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tabella righe: ogni prodotto/servizio del listino
CREATE TABLE IF NOT EXISTS listino_righe (
  id              TEXT PRIMARY KEY,
  listino_id      TEXT NOT NULL REFERENCES listini_fornitori(id) ON DELETE CASCADE,
  codice_articolo TEXT,
  descrizione     TEXT NOT NULL,
  unita_misura    TEXT NOT NULL DEFAULT 'pz',
  prezzo_acquisto REAL NOT NULL,
  sconto_pct      REAL NOT NULL DEFAULT 0,
  prezzo_netto    REAL,
  iva_pct         REAL NOT NULL DEFAULT 22,
  categoria       TEXT,
  ean             TEXT,
  note            TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tabella variazioni: storico cambiamenti prezzi (differenziante vs competitor)
CREATE TABLE IF NOT EXISTS listino_variazioni (
  id               TEXT PRIMARY KEY,
  listino_riga_id  TEXT NOT NULL REFERENCES listino_righe(id) ON DELETE CASCADE,
  campo            TEXT NOT NULL,
  valore_precedente TEXT,
  valore_nuovo     TEXT NOT NULL,
  data_variazione  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_listini_fornitore   ON listini_fornitori(fornitore_id);
CREATE INDEX IF NOT EXISTS idx_listino_righe_listino ON listino_righe(listino_id);
CREATE INDEX IF NOT EXISTS idx_listino_righe_codice  ON listino_righe(codice_articolo);
CREATE INDEX IF NOT EXISTS idx_listino_variazioni_riga ON listino_variazioni(listino_riga_id);
