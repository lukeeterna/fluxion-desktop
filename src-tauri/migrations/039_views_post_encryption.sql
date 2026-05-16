-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 039: Views Post-Encryption Refactor (S255 P1.a)
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-05-16
-- Task: S255 — GDPR encryption operatori PII
--
-- CONTESTO:
-- Migration 024 ha creato `v_kpi_operatori` con `o.nome || ' ' || o.cognome
-- AS nome_completo`. Quando operatori PII viene cifrato (S255 P1.b/c),
-- la view restituirebbe `Base64Nome ' ' Base64Cognome` — illeggibile lato
-- frontend e impossibile da decifrare in-Rust (single field concat).
--
-- FIX:
-- DROP la view e ricreala restituendo `nome` e `cognome` SEPARATI come
-- colonne distinte. Il comando Rust (`get_kpi_operatore_storico` /
-- `get_top_operatori_mese`) decifra entrambi i campi e compone
-- `nome_completo = "{nome} {cognome}"` lato applicazione.
--
-- `v_operatori_assenti_oggi` (definita migration 024 step 3) NON viene
-- toccata: nessun consumer attivo (grep src/ src-tauri/ → 0 match) e
-- la prossima sessione che la userà saprà che restituisce Base64.
-- Se servisse, refactor analogo in migration successiva.
-- ═══════════════════════════════════════════════════════════════

-- STEP 1: DROP view legacy (concat-based)
DROP VIEW IF EXISTS v_kpi_operatori;

-- STEP 2: CREATE view nuova (nome + cognome separati)
CREATE VIEW v_kpi_operatori AS
SELECT
    o.id,
    o.nome,
    o.cognome,
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

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT id, nome, cognome, mese FROM v_kpi_operatori
--   WHERE mese = strftime('%Y-%m', 'now') LIMIT 5;
-- Atteso post-S255: nome+cognome Base64 ciphertext.
-- ═══════════════════════════════════════════════════════════════
