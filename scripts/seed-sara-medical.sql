-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: STUDIO MEDICO
-- Sotto-verticale: Poliambulatorio (odontoiatria + ortopedia + dermatologia + medicina generale)
-- Per test voce Sara su iMac
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Poliambulatorio Salus'),
('categoria_attivita', 'medical'),
('macro_categoria', 'medico'),
('micro_categoria', 'poliambulatorio'),
('indirizzo_completo', 'Via Garibaldi 78, 20121 Milano'),
('orario_apertura', '08:00'),
('orario_chiusura', '20:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number', '3289876543'),
('whatsapp_attivo', 'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
-- Medicina Generale
('srv-visita',        'Visita Medica Generale',  'Visita di base con anamnesi',           80.00, 30, 5, 'visite',       '#6366f1', 1, 1),
('srv-prima-visita',  'Prima Visita',            'Prima visita completa con anamnesi',   100.00, 45, 5, 'visite',       '#6366f1', 1, 2),
('srv-controllo',     'Controllo',               'Visita di follow-up',                   60.00, 20, 5, 'visite',       '#10b981', 1, 3),
-- Odontoiatria
('srv-pulizia-denti', 'Pulizia Denti',           'Igiene orale professionale',            70.00, 45, 10, 'odontoiatria', '#3b82f6', 1, 4),
('srv-otturazione',   'Otturazione',             'Riparazione carie',                     90.00, 30, 10, 'odontoiatria', '#3b82f6', 1, 5),
('srv-estrazione',    'Estrazione Dente',        'Estrazione semplice',                  120.00, 45, 15, 'odontoiatria', '#ef4444', 1, 6),
('srv-sbiancamento',  'Sbiancamento Denti',      'Sbiancamento professionale',           200.00, 60, 10, 'odontoiatria', '#f59e0b', 1, 7),
('srv-panoramica',    'Panoramica Dentale',       'Radiografia panoramica',                50.00, 15,  5, 'odontoiatria', '#8b5cf6', 1, 8),
-- Ortopedia
('srv-visita-orto',   'Visita Ortopedica',       'Visita specialistica ortopedica',      120.00, 30, 5, 'ortopedia',    '#ec4899', 1, 9),
('srv-infiltrazione', 'Infiltrazione',           'Infiltrazione cortisone/acido ialuronico', 80.00, 20, 10, 'ortopedia', '#ec4899', 1, 10),
-- Dermatologia
('srv-visita-derm',   'Visita Dermatologica',    'Visita dermatologica completa',        100.00, 30, 5, 'dermatologia', '#f59e0b', 1, 11),
('srv-mappatura-nei', 'Mappatura Nei',           'Mappatura completa videodermatoscopia', 120.00, 45, 5, 'dermatologia', '#f59e0b', 1, 12),
-- Diagnostica
('srv-ecg',           'Elettrocardiogramma',     'ECG a riposo',                          50.00, 20, 5, 'diagnostica',  '#ef4444', 1, 13),
('srv-eco-addome',    'Ecografia Addominale',    'Ecografia addome completo',             70.00, 30, 5, 'diagnostica',  '#3b82f6', 1, 14),
('srv-analisi-base',  'Analisi Sangue Base',     'Emocromo + glicemia + colesterolo',     35.00, 15, 0, 'analisi',      '#f59e0b', 1, 15),
-- Certificati
('srv-cert-medico',   'Certificato Medico',      'Certificato malattia/idoneità',         30.00, 15, 0, 'certificati',  '#8b5cf6', 1, 16),
('srv-cert-sportivo', 'Certificato Sportivo',    'Idoneità non agonistica + ECG',         50.00, 30, 5, 'certificati',  '#8b5cf6', 1, 17);

-- ── OPERATORI (medici) ────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva, genere) VALUES
('op-dott-rossi',   'Dott. Marco',  'Rossi',    'operatore', '#6366f1', 1, '["medicina generale","certificati","ecg"]',         'Medico di famiglia, 20 anni esperienza', 'M'),
('op-dott-bianchi', 'Dott.ssa Anna','Bianchi',  'operatore', '#ec4899', 1, '["odontoiatria","igiene dentale","estetica dentale"]','Odontoiatra specializzata in estetica del sorriso', 'F'),
('op-dott-verdi',   'Dott. Luca',   'Verdi',   'operatore', '#10b981', 1, '["ortopedia","fisioterapia","medicina sportiva"]',   'Ortopedico specializzato in ginocchio e spalla', 'M'),
('op-dott-neri',    'Dott.ssa Sara','Neri',     'operatore', '#f59e0b', 1, '["dermatologia","mappatura nei","laser"]',           'Dermatologa, esperta oncologia cutanea', 'F'),
('op-inf-giulia',   'Giulia',       'Conti',    'operatore', '#3b82f6', 1, '["prelievi","ecografie","assistenza"]',              'Infermiera professionale, ecografista', 'F');

-- ── CLIENTI (pazienti) ────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-med-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-med-01', 'Giorgio',   'Colombo',   '3351234001', 'g.colombo@email.it',   '1975-03-10', 1, 15, 1, 'Paziente storico. Diabetico tipo 2. Controlli trimestrali'),
('cli-med-02', 'Laura',     'Ferrari',   '3351234002', 'laura.f@email.it',     '1988-08-22', 1,  8, 0, 'Pulizia denti semestrale. Nessuna allergia'),
('cli-med-03', 'Antonio',   'Esposito',  '3351234003', 'a.esposito@email.it',  '1965-11-05', 1, 20, 1, 'Protesi ginocchio dx 2024. Follow-up ortopedico'),
('cli-med-04', 'Francesca', 'Ricci',     '3351234004', 'fra.ricci@email.it',   '1992-04-15', 1,  5, 0, 'Mappatura nei annuale. Fototipo II'),
('cli-med-05', 'Marco',     'Moretti',   '3351234005', 'marco.m@email.it',     '1980-07-28', 0, 10, 0, 'Certificato sportivo annuale. Nessuna patologia'),
('cli-med-06', 'Silvia',    'Russo',     '3351234006', 'silvia.r@email.it',    '1995-02-14', 1,  3, 0, 'Prima visita dermatologica. Acne'),
('cli-med-07', 'Giovanni',  'Romano',    '3351234007', 'gio.romano@email.it',  '1958-09-30', 1, 25, 1, 'Cardiopatico. ECG + Holter semestrali'),
('cli-med-08', 'Elena',     'Galli',     '3351234008', 'elena.g@email.it',     '1990-12-20', 1,  6, 0, 'Sbiancamento completato gen 2026. Prossimo controllo');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
DELETE FROM appuntamenti WHERE id LIKE 'apt-med-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-med-001', 'cli-med-01', 'srv-controllo',     'op-dott-rossi',  '2026-03-31T08:30:00', '2026-03-31T08:50:00', 20, 'confermato',  60.00,  60.00, 'Controllo glicemia trimestrale', 'whatsapp'),
('apt-med-002', 'cli-med-02', 'srv-pulizia-denti', 'op-dott-bianchi','2026-03-31T09:00:00', '2026-03-31T09:45:00', 45, 'confermato',  70.00,  70.00, 'Igiene semestrale', 'voice'),
('apt-med-003', 'cli-med-03', 'srv-visita-orto',   'op-dott-verdi',  '2026-03-31T10:00:00', '2026-03-31T10:30:00', 30, 'confermato', 120.00, 120.00, 'Follow-up ginocchio protesizzato', 'whatsapp'),
('apt-med-004', 'cli-med-07', 'srv-ecg',           'op-dott-rossi',  '2026-03-31T11:00:00', '2026-03-31T11:20:00', 20, 'confermato',  50.00,  50.00, 'ECG controllo semestrale', 'telefono'),
('apt-med-005', 'cli-med-05', 'srv-analisi-base',  'op-inf-giulia',  '2026-03-31T08:00:00', '2026-03-31T08:15:00', 15, 'confermato',  35.00,  35.00, 'Prelievo a digiuno', 'manuale'),
-- Martedì 1 Aprile
('apt-med-006', 'cli-med-04', 'srv-mappatura-nei', 'op-dott-neri',   '2026-04-01T09:00:00', '2026-04-01T09:45:00', 45, 'confermato', 120.00, 120.00, 'Mappatura annuale', 'whatsapp'),
('apt-med-007', 'cli-med-06', 'srv-visita-derm',   'op-dott-neri',   '2026-04-01T10:00:00', '2026-04-01T10:30:00', 30, 'confermato', 100.00, 100.00, 'Prima visita acne', 'voice'),
('apt-med-008', 'cli-med-01', 'srv-eco-addome',    'op-inf-giulia',  '2026-04-01T11:00:00', '2026-04-01T11:30:00', 30, 'confermato',  70.00,  70.00, 'Ecografia di controllo', 'whatsapp'),
('apt-med-009', 'cli-med-08', 'srv-pulizia-denti', 'op-dott-bianchi','2026-04-01T14:00:00', '2026-04-01T14:45:00', 45, 'confermato',  70.00,  70.00, 'Post-sbiancamento check', 'manuale'),
-- Mercoledì 2 Aprile
('apt-med-010', 'cli-med-05', 'srv-cert-sportivo', 'op-dott-rossi',  '2026-04-02T09:00:00', '2026-04-02T09:30:00', 30, 'confermato',  50.00,  50.00, 'Rinnovo certificato calcetto', 'whatsapp'),
('apt-med-011', 'cli-med-03', 'srv-infiltrazione', 'op-dott-verdi',  '2026-04-02T10:00:00', '2026-04-02T10:20:00', 20, 'confermato',  80.00,  80.00, 'Infiltrazione ginocchio sx', 'voice'),
('apt-med-012', 'cli-med-02', 'srv-sbiancamento',  'op-dott-bianchi','2026-04-02T14:00:00', '2026-04-02T15:00:00', 60, 'confermato', 200.00, 200.00, NULL, 'whatsapp'),
-- Giovedì 3 Aprile (PIENO — per test waitlist)
('apt-med-013', 'cli-med-01', 'srv-visita',        'op-dott-rossi',  '2026-04-03T08:30:00', '2026-04-03T09:00:00', 30, 'confermato',  80.00,  80.00, NULL, 'whatsapp'),
('apt-med-014', 'cli-med-07', 'srv-visita',        'op-dott-rossi',  '2026-04-03T09:00:00', '2026-04-03T09:30:00', 30, 'confermato',  80.00,  80.00, 'Visita cardiologica', 'telefono'),
('apt-med-015', 'cli-med-04', 'srv-visita-derm',   'op-dott-neri',   '2026-04-03T09:00:00', '2026-04-03T09:30:00', 30, 'confermato', 100.00, 100.00, NULL, 'voice'),
('apt-med-016', 'cli-med-06', 'srv-visita-derm',   'op-dott-neri',   '2026-04-03T09:30:00', '2026-04-03T10:00:00', 30, 'confermato', 100.00, 100.00, 'Controllo acne', 'whatsapp'),
('apt-med-017', 'cli-med-03', 'srv-visita-orto',   'op-dott-verdi',  '2026-04-03T10:00:00', '2026-04-03T10:30:00', 30, 'confermato', 120.00, 120.00, NULL, 'manuale'),
('apt-med-018', 'cli-med-02', 'srv-otturazione',   'op-dott-bianchi','2026-04-03T10:00:00', '2026-04-03T10:30:00', 30, 'confermato',  90.00,  90.00, 'Carie premolare sup dx', 'whatsapp'),
-- Venerdì 4 Aprile
('apt-med-019', 'cli-med-05', 'srv-visita',        'op-dott-rossi',  '2026-04-04T09:00:00', '2026-04-04T09:30:00', 30, 'confermato',  80.00,  80.00, NULL, 'voice'),
('apt-med-020', 'cli-med-08', 'srv-otturazione',   'op-dott-bianchi','2026-04-04T10:00:00', '2026-04-04T10:30:00', 30, 'confermato',  90.00,  90.00, NULL, 'whatsapp');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-med-01', 'Check-Up Completo',         'Visita + ECG + Analisi sangue completo',       150.00, 190.00, 3, NULL,              30, 1),
('pkg-med-02', 'Pacchetto Igiene Annuale',  '2 pulizie denti + 1 panoramica (-20%)',        150.00, 190.00, 3, 'srv-pulizia-denti', 365, 1),
('pkg-med-03', 'Screening Dermatologico',   'Visita derm + Mappatura nei completa',         180.00, 220.00, 2, NULL,              60, 1),
('pkg-med-04', 'Pacchetto Sportivo',        'Cert. sportivo + ECG + Visita ortopedica',     200.00, 220.00, 3, NULL,              30, 1);

PRAGMA foreign_keys = ON;
