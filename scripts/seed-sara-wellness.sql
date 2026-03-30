-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: PALESTRA / CENTRO FITNESS
-- Sotto-verticale: Palestra con sala pesi, corsi, piscina, PT
-- Per test voce Sara su iMac
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'FitClub Roma'),
('categoria_attivita', 'wellness'),
('macro_categoria', 'wellness'),
('micro_categoria', 'palestra'),
('indirizzo_completo', 'Via Tuscolana 245, 00182 Roma'),
('orario_apertura', '06:00'),
('orario_chiusura', '22:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab","dom"]'),
('whatsapp_number', '3281234567'),
('whatsapp_attivo', 'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
-- Abbonamenti
('srv-abb-mensile',    'Abbonamento Mensile',      'Accesso illimitato palestra + corsi',  49.00, 0,  0, 'abbonamenti', '#6366f1', 1, 1),
('srv-abb-trimestre',  'Abbonamento Trimestrale',   'Accesso 3 mesi (-10%)',               129.00, 0, 0, 'abbonamenti', '#6366f1', 1, 2),
('srv-abb-annuale',    'Abbonamento Annuale',       'Accesso 12 mesi (-20%)',              449.00, 0, 0, 'abbonamenti', '#6366f1', 1, 3),
('srv-ingresso',       'Ingresso Singolo',          'Giornata intera',                      12.00, 0, 0, 'abbonamenti', '#8b5cf6', 1, 4),
-- Personal Training
('srv-pt-singola',     'Personal Training',         'Seduta individuale 60 min',            45.00, 60, 5, 'personal',    '#ec4899', 1, 5),
('srv-pt-coppia',      'PT di Coppia',              'Allenamento in coppia 60 min',         70.00, 60, 5, 'personal',    '#ec4899', 1, 6),
('srv-valutazione',    'Valutazione Fitness',       'Test composizione corporea + scheda',   35.00, 45, 5, 'personal',    '#8b5cf6', 1, 7),
-- Corsi di gruppo
('srv-yoga',           'Yoga',                      'Hatha yoga 60 min',                    10.00, 60, 5, 'corsi',       '#10b981', 1, 8),
('srv-pilates',        'Pilates',                   'Pilates matwork 60 min',               10.00, 60, 5, 'corsi',       '#10b981', 1, 9),
('srv-spinning',       'Spinning',                  'Indoor cycling 45 min',                10.00, 45, 5, 'corsi',       '#f59e0b', 1, 10),
('srv-crossfit',       'CrossFit',                  'WOD allenamento funzionale',           12.00, 60, 5, 'corsi',       '#ef4444', 1, 11),
('srv-zumba',          'Zumba',                     'Dance fitness 60 min',                 10.00, 60, 5, 'corsi',       '#f59e0b', 1, 12),
('srv-acquagym',       'Acquagym',                  'Ginnastica in acqua 45 min',           12.00, 45, 5, 'corsi',       '#3b82f6', 1, 13),
('srv-nuoto',          'Corso Nuoto Adulti',        'Lezione nuoto 45 min',                 15.00, 45, 5, 'corsi',       '#3b82f6', 1, 14),
-- Benessere
('srv-massaggio',      'Massaggio Sportivo',        'Decontratturante 60 min',              50.00, 60, 10,'benessere',   '#ec4899', 1, 15),
('srv-sauna',          'Circuito Sauna + Bagno Turco', 'Area relax 90 min',                 15.00, 90, 0, 'benessere',   '#f59e0b', 1, 16);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-marco',   'Marco',   'Ferretti',  'operatore', '#3b82f6', 1, '["personal training","sala pesi","crossfit"]',    'PT certificato, esperto bodybuilding e preparazione atletica'),
('op-elena',   'Elena',   'Conti',     'operatore', '#ec4899', 1, '["yoga","pilates","stretching"]',                 'Istruttrice yoga certificata RYT-500, specializzata in posturale'),
('op-davide',  'Davide',  'Russo',     'operatore', '#10b981', 1, '["spinning","crossfit","functional training"]',   'Atleta crossfit, coach motivazionale'),
('op-sara',    'Sara',    'Moretti',   'operatore', '#f59e0b', 1, '["nuoto","acquagym","baby nuoto"]',               'Istruttrice FIN, esperta recupero funzionale in acqua'),
('op-luca',    'Luca',    'Bianchi',   'admin',     '#8b5cf6', 1, '["gestione","reception","valutazioni"]',          'Direttore tecnico, laurea Scienze Motorie');

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-fit-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-fit-01', 'Alessandro', 'Rossi',    '3331234501', 'ale.rossi@email.it',    '1990-05-15', 1, 45, 1, 'Obiettivo: massa muscolare. PT 3x/settimana'),
('cli-fit-02', 'Giulia',     'Bianchi',  '3331234502', 'giulia.b@email.it',     '1988-03-22', 1, 30, 1, 'Frequenta yoga+pilates. VIP da 2 anni'),
('cli-fit-03', 'Federico',   'Marchetti','3331234503', 'fede.march@email.it',   '1995-11-08', 1, 12, 0, 'CrossFit 4x/settimana. Preparazione gara'),
('cli-fit-04', 'Valentina',  'Romano',   '3331234504', 'vale.romano@email.it',  '1992-07-30', 1, 20, 0, 'Spinning + sala pesi. Obiettivo tonificazione'),
('cli-fit-05', 'Roberto',    'Greco',    '3331234505', 'rob.greco@email.it',    '1985-01-14', 1,  8, 0, 'Nuoto libero 2x/settimana'),
('cli-fit-06', 'Martina',    'Ferrari',  '3331234506', 'martina.f@email.it',    '1998-09-25', 0,  3, 0, 'Nuova iscritta. Prova gratuita spinning'),
('cli-fit-07', 'Simone',     'Costa',    '3331234507', 'simone.c@email.it',     '1982-12-03', 1, 50, 1, 'Membro fondatore. PT + sauna. VIP gold'),
('cli-fit-08', 'Chiara',     'Lombardi', '3331234508', 'chiara.l@email.it',     '1993-06-18', 1, 15, 0, 'Zumba + acquagym. Obiettivo dimagrimento');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
DELETE FROM appuntamenti WHERE id LIKE 'apt-fit-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-fit-001', 'cli-fit-01', 'srv-pt-singola', 'op-marco',  '2026-03-31T07:00:00', '2026-03-31T08:00:00', 60, 'confermato', 45.00, 45.00, 'Scheda forza - settimana 12', 'whatsapp'),
('apt-fit-002', 'cli-fit-02', 'srv-yoga',       'op-elena',  '2026-03-31T09:00:00', '2026-03-31T10:00:00', 60, 'confermato', 10.00, 10.00, 'Hatha yoga mattina', 'voice'),
('apt-fit-003', 'cli-fit-03', 'srv-crossfit',   'op-davide', '2026-03-31T10:00:00', '2026-03-31T11:00:00', 60, 'confermato', 12.00, 12.00, 'WOD giorno gambe', 'manuale'),
('apt-fit-004', 'cli-fit-04', 'srv-spinning',   'op-davide', '2026-03-31T18:00:00', '2026-03-31T18:45:00', 45, 'confermato', 10.00, 10.00, NULL, 'whatsapp'),
('apt-fit-005', 'cli-fit-07', 'srv-pt-singola', 'op-marco',  '2026-03-31T19:00:00', '2026-03-31T20:00:00', 60, 'confermato', 45.00, 45.00, 'Upper body + core', 'voice'),
-- Martedì 1 Aprile
('apt-fit-006', 'cli-fit-05', 'srv-nuoto',      'op-sara',   '2026-04-01T07:30:00', '2026-04-01T08:15:00', 45, 'confermato', 15.00, 15.00, 'Corsia 3', 'manuale'),
('apt-fit-007', 'cli-fit-02', 'srv-pilates',    'op-elena',  '2026-04-01T10:00:00', '2026-04-01T11:00:00', 60, 'confermato', 10.00, 10.00, NULL, 'whatsapp'),
('apt-fit-008', 'cli-fit-08', 'srv-acquagym',   'op-sara',   '2026-04-01T11:00:00', '2026-04-01T11:45:00', 45, 'confermato', 12.00, 12.00, NULL, 'voice'),
('apt-fit-009', 'cli-fit-01', 'srv-pt-singola', 'op-marco',  '2026-04-01T18:00:00', '2026-04-01T19:00:00', 60, 'confermato', 45.00, 45.00, 'Scheda forza - giorno push', 'whatsapp'),
('apt-fit-010', 'cli-fit-06', 'srv-spinning',   'op-davide', '2026-04-01T19:00:00', '2026-04-01T19:45:00', 45, 'confermato', 10.00,  0.00, 'Prova gratuita', 'manuale'),
-- Mercoledì 2 Aprile
('apt-fit-011', 'cli-fit-03', 'srv-crossfit',   'op-davide', '2026-04-02T07:00:00', '2026-04-02T08:00:00', 60, 'confermato', 12.00, 12.00, 'Open gym + WOD', 'whatsapp'),
('apt-fit-012', 'cli-fit-02', 'srv-yoga',       'op-elena',  '2026-04-02T09:00:00', '2026-04-02T10:00:00', 60, 'confermato', 10.00, 10.00, 'Yin yoga', 'voice'),
('apt-fit-013', 'cli-fit-07', 'srv-massaggio',  'op-marco',  '2026-04-02T14:00:00', '2026-04-02T15:00:00', 60, 'confermato', 50.00, 50.00, 'Decontratturante schiena', 'whatsapp'),
('apt-fit-014', 'cli-fit-08', 'srv-zumba',      'op-elena',  '2026-04-02T18:00:00', '2026-04-02T19:00:00', 60, 'confermato', 10.00, 10.00, NULL, 'manuale'),
-- Giovedì 3 Aprile
('apt-fit-015', 'cli-fit-01', 'srv-pt-singola', 'op-marco',  '2026-04-03T07:00:00', '2026-04-03T08:00:00', 60, 'confermato', 45.00, 45.00, 'Leg day', 'whatsapp'),
('apt-fit-016', 'cli-fit-05', 'srv-nuoto',      'op-sara',   '2026-04-03T08:00:00', '2026-04-03T08:45:00', 45, 'confermato', 15.00, 15.00, NULL, 'voice'),
('apt-fit-017', 'cli-fit-04', 'srv-pt-coppia',  'op-marco',  '2026-04-03T18:00:00', '2026-04-03T19:00:00', 60, 'confermato', 70.00, 70.00, 'Con amica - full body', 'whatsapp'),
-- Venerdì 4 Aprile (slot pieni per test waitlist)
('apt-fit-018', 'cli-fit-01', 'srv-pt-singola', 'op-marco',  '2026-04-04T07:00:00', '2026-04-04T08:00:00', 60, 'confermato', 45.00, 45.00, NULL, 'whatsapp'),
('apt-fit-019', 'cli-fit-07', 'srv-pt-singola', 'op-marco',  '2026-04-04T08:00:00', '2026-04-04T09:00:00', 60, 'confermato', 45.00, 45.00, NULL, 'voice'),
('apt-fit-020', 'cli-fit-03', 'srv-pt-singola', 'op-marco',  '2026-04-04T09:00:00', '2026-04-04T10:00:00', 60, 'confermato', 45.00, 45.00, NULL, 'whatsapp'),
('apt-fit-021', 'cli-fit-04', 'srv-pt-singola', 'op-marco',  '2026-04-04T10:00:00', '2026-04-04T11:00:00', 60, 'confermato', 45.00, 45.00, NULL, 'manuale'),
('apt-fit-022', 'cli-fit-02', 'srv-yoga',       'op-elena',  '2026-04-04T09:00:00', '2026-04-04T10:00:00', 60, 'confermato', 10.00, 10.00, NULL, 'voice'),
('apt-fit-023', 'cli-fit-08', 'srv-spinning',   'op-davide', '2026-04-04T18:00:00', '2026-04-04T18:45:00', 45, 'confermato', 10.00, 10.00, NULL, 'whatsapp');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-fit-01', 'Pacchetto PT 10 Sedute',      '10 sessioni Personal Training (-15%)',      380.00, 450.00, 10, 'srv-pt-singola', 90,  1),
('pkg-fit-02', 'Estate in Forma',              '3 mesi illimitato + 5 PT + body check',    299.00, 420.00,  8, NULL,             120, 1),
('pkg-fit-03', 'Prova Tutto - 1 Settimana',    '7 giorni accesso totale + 1 PT gratis',     25.00,  57.00,  8, NULL,              7, 1),
('pkg-fit-04', 'Pacchetto Coppia PT',          '10 sessioni PT in coppia (-20%)',           560.00, 700.00, 10, 'srv-pt-coppia',  90,  1);

PRAGMA foreign_keys = ON;
