-- ═══════════════════════════════════════════════════════════════════
-- MIGRATION 003: Orari Lavoro + Giorni Festivi
-- ═══════════════════════════════════════════════════════════════════
-- Sistema di gestione orari apertura/chiusura e festività italiane
-- per validazione automatica booking
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────
-- Tabella: orari_lavoro
-- ───────────────────────────────────────────────────────────────────
-- Gestisce fasce orarie lavorative e pause per ogni giorno settimana
-- Supporta orari globali o specifici per operatore

CREATE TABLE IF NOT EXISTS orari_lavoro (
  id TEXT PRIMARY KEY,
  giorno_settimana INTEGER NOT NULL CHECK(giorno_settimana BETWEEN 0 AND 6),
  -- 0=domenica, 1=lunedì, 2=martedì, 3=mercoledì, 4=giovedì, 5=venerdì, 6=sabato

  ora_inizio TEXT NOT NULL, -- Formato "HH:MM" (es. "09:00")
  ora_fine TEXT NOT NULL,   -- Formato "HH:MM" (es. "13:00")

  tipo TEXT NOT NULL CHECK(tipo IN ('lavoro', 'pausa')),
  -- 'lavoro' = fascia lavorativa
  -- 'pausa' = fascia non lavorativa (es. pranzo, riposo)

  operatore_id TEXT, -- NULL = vale per tutti, altrimenti specifico

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);

CREATE INDEX idx_orari_lavoro_giorno ON orari_lavoro(giorno_settimana);
CREATE INDEX idx_orari_lavoro_operatore ON orari_lavoro(operatore_id);

-- ───────────────────────────────────────────────────────────────────
-- Tabella: giorni_festivi
-- ───────────────────────────────────────────────────────────────────
-- Gestisce calendario festività italiane (giorni rossi)
-- Supporta festività fisse (ricorrenti) e mobili (specifiche anno)

CREATE TABLE IF NOT EXISTS giorni_festivi (
  id TEXT PRIMARY KEY,
  data TEXT NOT NULL UNIQUE, -- Formato "YYYY-MM-DD" (es. "2026-01-01")
  descrizione TEXT NOT NULL,  -- Es. "Capodanno", "Pasqua", "Ferragosto"
  ricorrente INTEGER DEFAULT 0 CHECK(ricorrente IN (0, 1)),
  -- 0 = festività mobile (es. Pasqua, varia ogni anno)
  -- 1 = festività fissa (es. 25/12, si ripete stesso giorno ogni anno)

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_giorni_festivi_data ON giorni_festivi(data);
CREATE INDEX idx_giorni_festivi_ricorrente ON giorni_festivi(ricorrente);

-- ═══════════════════════════════════════════════════════════════════
-- SEED: Orari Default
-- ═══════════════════════════════════════════════════════════════════
-- Orari standard PMI italiane: Lun-Ven 9-13, 14-20; Sab 9-13; Dom chiuso

-- LUNEDÌ (1)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_lun_mattina', 1, '09:00', '13:00', 'lavoro', NULL),
('orario_lun_pausa', 1, '13:00', '14:00', 'pausa', NULL),
('orario_lun_pomeriggio', 1, '14:00', '20:00', 'lavoro', NULL);

-- MARTEDÌ (2)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_mar_mattina', 2, '09:00', '13:00', 'lavoro', NULL),
('orario_mar_pausa', 2, '13:00', '14:00', 'pausa', NULL),
('orario_mar_pomeriggio', 2, '14:00', '20:00', 'lavoro', NULL);

-- MERCOLEDÌ (3)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_mer_mattina', 3, '09:00', '13:00', 'lavoro', NULL),
('orario_mer_pausa', 3, '13:00', '14:00', 'pausa', NULL),
('orario_mer_pomeriggio', 3, '14:00', '20:00', 'lavoro', NULL);

-- GIOVEDÌ (4)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_gio_mattina', 4, '09:00', '13:00', 'lavoro', NULL),
('orario_gio_pausa', 4, '13:00', '14:00', 'pausa', NULL),
('orario_gio_pomeriggio', 4, '14:00', '20:00', 'lavoro', NULL);

-- VENERDÌ (5)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_ven_mattina', 5, '09:00', '13:00', 'lavoro', NULL),
('orario_ven_pausa', 5, '13:00', '14:00', 'pausa', NULL),
('orario_ven_pomeriggio', 5, '14:00', '20:00', 'lavoro', NULL);

-- SABATO (6)
INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('orario_sab_mattina', 6, '09:00', '13:00', 'lavoro', NULL);

-- DOMENICA (0) - chiuso (nessun orario inserito)

-- ═══════════════════════════════════════════════════════════════════
-- SEED: Festività Italiane 2026
-- ═══════════════════════════════════════════════════════════════════

-- FESTIVITÀ FISSE (ricorrente = 1)
INSERT INTO giorni_festivi (id, data, descrizione, ricorrente) VALUES
('fest_2026_0101', '2026-01-01', 'Capodanno', 1),
('fest_2026_0106', '2026-01-06', 'Epifania', 1),
('fest_2026_0425', '2026-04-25', 'Festa della Liberazione', 1),
('fest_2026_0501', '2026-05-01', 'Festa dei Lavoratori', 1),
('fest_2026_0602', '2026-06-02', 'Festa della Repubblica', 1),
('fest_2026_0815', '2026-08-15', 'Ferragosto (Assunzione)', 1),
('fest_2026_1101', '2026-11-01', 'Tutti i Santi', 1),
('fest_2026_1208', '2026-12-08', 'Immacolata Concezione', 1),
('fest_2026_1225', '2026-12-25', 'Natale', 1),
('fest_2026_1226', '2026-12-26', 'Santo Stefano', 1);

-- FESTIVITÀ MOBILI 2026 (ricorrente = 0)
INSERT INTO giorni_festivi (id, data, descrizione, ricorrente) VALUES
('fest_2026_pasqua', '2026-04-05', 'Pasqua', 0),
('fest_2026_pasquetta', '2026-04-06', 'Lunedì dell''Angelo (Pasquetta)', 0);

-- ═══════════════════════════════════════════════════════════════════
-- SEED: Festività Italiane 2027 (BONUS - pianificazione futura)
-- ═══════════════════════════════════════════════════════════════════

-- FESTIVITÀ FISSE 2027
INSERT INTO giorni_festivi (id, data, descrizione, ricorrente) VALUES
('fest_2027_0101', '2027-01-01', 'Capodanno', 1),
('fest_2027_0106', '2027-01-06', 'Epifania', 1),
('fest_2027_0425', '2027-04-25', 'Festa della Liberazione', 1),
('fest_2027_0501', '2027-05-01', 'Festa dei Lavoratori', 1),
('fest_2027_0602', '2027-06-02', 'Festa della Repubblica', 1),
('fest_2027_0815', '2027-08-15', 'Ferragosto (Assunzione)', 1),
('fest_2027_1101', '2027-11-01', 'Tutti i Santi', 1),
('fest_2027_1208', '2027-12-08', 'Immacolata Concezione', 1),
('fest_2027_1225', '2027-12-25', 'Natale', 1),
('fest_2027_1226', '2027-12-26', 'Santo Stefano', 1);

-- FESTIVITÀ MOBILI 2027
INSERT INTO giorni_festivi (id, data, descrizione, ricorrente) VALUES
('fest_2027_pasqua', '2027-03-28', 'Pasqua', 0),
('fest_2027_pasquetta', '2027-03-29', 'Lunedì dell''Angelo (Pasquetta)', 0);

-- ═══════════════════════════════════════════════════════════════════
-- Fine Migration 003
-- ═══════════════════════════════════════════════════════════════════
