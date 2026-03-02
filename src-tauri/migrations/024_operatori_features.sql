-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 024: Operatori Features (B2/B3)
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-03-02
-- Task: B2 — UI Servizi Abilitati per Operatore
-- Task: B3 — UI Orari/Turni per Operatore (tabella già esiste)
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Aggiunge colonna priorita a operatori_servizi
-- ───────────────────────────────────────────────────────────────
-- Permette di ordinare i servizi per operatore (es. il taglio è il primario)

ALTER TABLE operatori_servizi ADD COLUMN priorita INTEGER DEFAULT 0;

-- ───────────────────────────────────────────────────────────────
-- STEP 2: View KPI operatori (usata da dashboard e statistiche)
-- ───────────────────────────────────────────────────────────────
-- Aggregazione mensile per operatore: completati, fatturato, no-show

CREATE VIEW IF NOT EXISTS v_kpi_operatori AS
SELECT
    o.id,
    o.nome || ' ' || o.cognome AS nome_completo,
    strftime('%Y-%m', a.data_ora_inizio) AS mese,
    COUNT(CASE WHEN a.stato = 'completato' THEN 1 END)  AS appuntamenti_completati,
    COUNT(CASE WHEN a.stato = 'no_show' THEN 1 END)     AS no_show,
    COUNT(DISTINCT a.cliente_id)                          AS clienti_unici,
    COALESCE(SUM(CASE WHEN a.stato = 'completato' THEN a.prezzo_finale END), 0.0) AS fatturato_generato,
    ROUND(AVG(CASE WHEN a.stato = 'completato' THEN a.prezzo_finale END), 2)      AS ticket_medio
FROM operatori o
LEFT JOIN appuntamenti a ON a.operatore_id = o.id
WHERE o.attivo = 1
GROUP BY o.id, strftime('%Y-%m', a.data_ora_inizio);

-- ───────────────────────────────────────────────────────────────
-- STEP 3: Tabella assenze operatori (ferie, malattia, infortuni)
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS operatori_assenze (
    id          TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL,
    data_inizio  TEXT NOT NULL,  -- YYYY-MM-DD
    data_fine    TEXT NOT NULL,  -- YYYY-MM-DD
    tipo         TEXT NOT NULL CHECK(tipo IN (
                    'ferie', 'malattia', 'infortunio',
                    'permesso', 'formazione', 'maternita', 'altro'
                 )),
    note         TEXT,
    approvata    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assenze_operatore ON operatori_assenze(operatore_id);
CREATE INDEX IF NOT EXISTS idx_assenze_date ON operatori_assenze(data_inizio, data_fine);

-- View usata da Sara e dalla dashboard: operatori assenti oggi
CREATE VIEW IF NOT EXISTS v_operatori_assenti_oggi AS
SELECT
    o.id,
    o.nome,
    o.cognome,
    o.colore,
    a.tipo,
    a.data_inizio,
    a.data_fine,
    a.note
FROM operatori_assenze a
JOIN operatori o ON o.id = a.operatore_id
WHERE date('now') BETWEEN a.data_inizio AND a.data_fine
  AND a.approvata = 1;

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT * FROM v_kpi_operatori WHERE mese = strftime('%Y-%m', 'now') LIMIT 10;
-- SELECT operatore_id, servizio_id, priorita FROM operatori_servizi LIMIT 10;
-- SELECT * FROM v_operatori_assenti_oggi;
-- ═══════════════════════════════════════════════════════════════
