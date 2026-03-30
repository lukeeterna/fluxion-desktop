-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: OFFICINA / AUTOFFICINA
-- Sotto-verticale: Officina meccanica + gommista + elettrauto
-- Per test voce Sara su iMac
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Autofficina Rossi & Figli'),
('categoria_attivita', 'auto'),
('macro_categoria', 'auto'),
('micro_categoria', 'officina_meccanica'),
('indirizzo_completo', 'Via Industriale 12, 40127 Bologna'),
('orario_apertura', '08:00'),
('orario_chiusura', '18:30'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number', '3475551234'),
('whatsapp_attivo', 'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
-- Manutenzione
('srv-tagliando-base', 'Tagliando Base',         'Cambio olio + filtro olio + controlli',       120.00, 120, 15, 'manutenzione', '#6366f1', 1, 1),
('srv-tagliando-full', 'Tagliando Completo',     'Tutti i filtri + candele + liquidi',           220.00, 180, 15, 'manutenzione', '#6366f1', 1, 2),
('srv-cambio-olio',    'Cambio Olio',            'Olio motore + filtro olio',                     55.00,  45, 10, 'manutenzione', '#f59e0b', 1, 3),
-- Revisione
('srv-revisione',      'Revisione Ministeriale', 'Revisione obbligatoria (tariffa fissa)',        79.00,  60,  0, 'revisione',    '#8b5cf6', 1, 4),
-- Freni
('srv-past-ant',       'Pastiglie Freni Ant.',   'Sostituzione pastiglie anteriori',              85.00,  60, 10, 'freni',        '#ef4444', 1, 5),
('srv-past-post',      'Pastiglie Freni Post.',  'Sostituzione pastiglie posteriori',             75.00,  60, 10, 'freni',        '#ef4444', 1, 6),
('srv-dischi-past',    'Dischi + Pastiglie',     'Sostituzione dischi e pastiglie (1 asse)',      220.00, 120, 10, 'freni',        '#ef4444', 1, 7),
-- Gomme
('srv-cambio-gomme',   'Cambio Gomme 4 Ruote',  'Smontaggio + montaggio + equilibratura',        50.00,  60, 10, 'gomme',        '#10b981', 1, 8),
('srv-equilibratura',  'Equilibratura 4 Ruote', 'Bilanciatura gomme',                             25.00,  30,  5, 'gomme',        '#10b981', 1, 9),
('srv-convergenza',    'Convergenza',            'Allineamento ruote assetto geometria',           50.00,  45, 10, 'gomme',        '#10b981', 1, 10),
-- Elettrico / Clima
('srv-batteria',       'Sostituzione Batteria',  'Test + sostituzione batteria',                   35.00,  30,  5, 'elettrico',    '#f59e0b', 1, 11),
('srv-diagnosi',       'Diagnosi Computerizzata','Lettura centralina errori OBD',                  40.00,  30,  5, 'diagnostica',  '#3b82f6', 1, 12),
('srv-ricarica-ac',    'Ricarica Climatizzatore','Ricarica gas + controllo impianto A/C',          65.00,  45, 10, 'clima',        '#3b82f6', 1, 13),
-- Controlli
('srv-check-vacanze',  'Controllo Pre-Vacanze',  'Check-up completo sicurezza viaggio',            30.00,  30,  5, 'controlli',    '#8b5cf6', 1, 14),
('srv-check-usato',    'Controllo Auto Usata',   'Ispezione pre-acquisto 50 punti',                60.00,  60, 10, 'controlli',    '#8b5cf6', 1, 15);

-- ── OPERATORI (meccanici) ─────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-giuseppe', 'Giuseppe', 'Rossi',    'admin',     '#6366f1', 1, '["motori","diagnosi","iniezione elettronica"]',   'Titolare, 30 anni esperienza motori diesel e benzina'),
('op-andrea',   'Andrea',   'Rossi',    'operatore', '#3b82f6', 1, '["freni","sospensioni","sterzo"]',               'Meccanico specializzato telaio e impianto frenante'),
('op-paolo',    'Paolo',    'Marchetti','operatore', '#10b981', 1, '["gomme","equilibratura","convergenza"]',        'Gommista certificato, 15 anni esperienza'),
('op-daniele',  'Daniele',  'Conti',    'operatore', '#f59e0b', 1, '["elettronica auto","diagnosi OBD","clima"]',    'Elettrauto, specializzato centraline e impianti A/C'),
('op-marta',    'Marta',    'Bianchi',  'operatore', '#ec4899', 1, '["reception","preventivi","ricambi"]',           'Accettazione, gestione ordini ricambi');

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-auto-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-auto-01', 'Massimo',   'Ferrara',   '3381234001', 'mass.ferrara@email.it',  '1978-06-15', 1, 20, 1, 'Fiat Ducato 2019 furgone. Tagliando ogni 15.000km'),
('cli-auto-02', 'Claudia',   'Lombardi',  '3381234002', 'claudia.l@email.it',     '1990-03-22', 1,  8, 0, 'VW Golf 8 2022. Cambio gomme stagionale'),
('cli-auto-03', 'Stefano',   'Rizzo',     '3381234003', 'stef.rizzo@email.it',    '1985-11-08', 1, 12, 0, 'BMW Serie 3 2020. Freni + sospensioni'),
('cli-auto-04', 'Patrizia',  'Costa',     '3381234004', 'pat.costa@email.it',     '1972-04-30', 1, 30, 1, 'Fiat 500X 2018. Cliente fedele, sempre tagliando qui'),
('cli-auto-05', 'Luca',      'Santoro',   '3381234005', 'luca.s@email.it',        '1995-01-14', 0,  4, 0, 'Renault Clio 2021. Revisione scaduta'),
('cli-auto-06', 'Angela',    'De Luca',   '3381234006', 'angela.dl@email.it',     '1988-09-25', 1,  6, 0, 'Toyota Yaris Hybrid 2023. Solo tagliandi'),
('cli-auto-07', 'Roberto',   'Greco',     '3381234007', 'rob.greco@email.it',     '1968-12-03', 1, 45, 1, 'Alfa Romeo Giulia 2019. VIP, flotta aziendale 3 auto'),
('cli-auto-08', 'Sara',      'Marino',    '3381234008', 'sara.m@email.it',        '1998-08-18', 1,  2, 0, 'Smart ForTwo 2020. Prima volta, spia motore accesa');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
DELETE FROM appuntamenti WHERE id LIKE 'apt-auto-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-auto-001', 'cli-auto-01', 'srv-tagliando-full','op-giuseppe','2026-03-31T08:00:00', '2026-03-31T11:00:00', 180, 'confermato', 220.00, 220.00, 'Ducato 180.000km - tagliando completo', 'whatsapp'),
('apt-auto-002', 'cli-auto-02', 'srv-cambio-gomme',  'op-paolo',   '2026-03-31T09:00:00', '2026-03-31T10:00:00',  60, 'confermato',  50.00,  50.00, 'Cambio invernali→estive + deposito', 'voice'),
('apt-auto-003', 'cli-auto-08', 'srv-diagnosi',      'op-daniele', '2026-03-31T10:00:00', '2026-03-31T10:30:00',  30, 'confermato',  40.00,  40.00, 'Spia motore accesa da 2 settimane', 'whatsapp'),
('apt-auto-004', 'cli-auto-04', 'srv-revisione',     'op-giuseppe','2026-03-31T14:00:00', '2026-03-31T15:00:00',  60, 'confermato',  79.00,  79.00, 'Revisione biennale', 'telefono'),
-- Martedì 1 Aprile
('apt-auto-005', 'cli-auto-03', 'srv-dischi-past',   'op-andrea',  '2026-04-01T08:00:00', '2026-04-01T10:00:00', 120, 'confermato', 220.00, 220.00, 'Dischi + pastiglie anteriori BMW', 'whatsapp'),
('apt-auto-006', 'cli-auto-05', 'srv-revisione',     'op-giuseppe','2026-04-01T09:00:00', '2026-04-01T10:00:00',  60, 'confermato',  79.00,  79.00, 'Revisione scaduta da 2 mesi', 'voice'),
('apt-auto-007', 'cli-auto-06', 'srv-tagliando-base','op-giuseppe','2026-04-01T10:30:00', '2026-04-01T12:30:00', 120, 'confermato', 120.00, 120.00, 'Yaris 40.000km', 'whatsapp'),
('apt-auto-008', 'cli-auto-07', 'srv-ricarica-ac',   'op-daniele', '2026-04-01T14:00:00', '2026-04-01T14:45:00',  45, 'confermato',  65.00,  65.00, 'Giulia - A/C debole', 'manuale'),
-- Mercoledì 2 Aprile
('apt-auto-009', 'cli-auto-01', 'srv-cambio-olio',   'op-giuseppe','2026-04-02T08:00:00', '2026-04-02T08:45:00',  45, 'confermato',  55.00,  55.00, 'Secondo mezzo aziendale', 'whatsapp'),
('apt-auto-010', 'cli-auto-02', 'srv-convergenza',   'op-paolo',   '2026-04-02T09:00:00', '2026-04-02T09:45:00',  45, 'confermato',  50.00,  50.00, 'Post cambio gomme', 'voice'),
('apt-auto-011', 'cli-auto-04', 'srv-cambio-olio',   'op-andrea',  '2026-04-02T10:00:00', '2026-04-02T10:45:00',  45, 'confermato',  55.00,  55.00, NULL, 'whatsapp'),
-- Giovedì 3 Aprile (PIENO — test waitlist)
('apt-auto-012', 'cli-auto-07', 'srv-tagliando-full','op-giuseppe','2026-04-03T08:00:00', '2026-04-03T11:00:00', 180, 'confermato', 220.00, 220.00, 'Giulia 60.000km', 'whatsapp'),
('apt-auto-013', 'cli-auto-03', 'srv-past-ant',      'op-andrea',  '2026-04-03T08:00:00', '2026-04-03T09:00:00',  60, 'confermato',  85.00,  85.00, NULL, 'voice'),
('apt-auto-014', 'cli-auto-01', 'srv-cambio-gomme',  'op-paolo',   '2026-04-03T08:00:00', '2026-04-03T09:00:00',  60, 'confermato',  50.00,  50.00, 'Ducato cambio estive', 'whatsapp'),
('apt-auto-015', 'cli-auto-05', 'srv-batteria',      'op-daniele', '2026-04-03T09:00:00', '2026-04-03T09:30:00',  30, 'confermato',  35.00,  35.00, 'Batteria scarica', 'manuale'),
('apt-auto-016', 'cli-auto-06', 'srv-check-vacanze', 'op-andrea',  '2026-04-03T10:00:00', '2026-04-03T10:30:00',  30, 'confermato',  30.00,  30.00, 'Check pre-Pasqua', 'whatsapp'),
('apt-auto-017', 'cli-auto-04', 'srv-past-post',     'op-andrea',  '2026-04-03T11:00:00', '2026-04-03T12:00:00',  60, 'confermato',  75.00,  75.00, NULL, 'telefono'),
('apt-auto-018', 'cli-auto-02', 'srv-equilibratura', 'op-paolo',   '2026-04-03T14:00:00', '2026-04-03T14:30:00',  30, 'confermato',  25.00,  25.00, NULL, 'voice'),
-- Venerdì 4 Aprile
('apt-auto-019', 'cli-auto-08', 'srv-tagliando-base','op-giuseppe','2026-04-04T08:00:00', '2026-04-04T10:00:00', 120, 'confermato', 120.00, 120.00, 'Smart primo tagliando', 'whatsapp'),
('apt-auto-020', 'cli-auto-07', 'srv-check-usato',   'op-giuseppe','2026-04-04T14:00:00', '2026-04-04T15:00:00',  60, 'confermato',  60.00,  60.00, 'Perizia Audi A4 per acquisto', 'manuale');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-auto-01', 'Pacchetto Manutenzione Annuale', 'Tagliando completo + revisione + cambio gomme',  310.00, 349.00, 3, NULL,             365, 1),
('pkg-auto-02', 'Pacchetto Freni Completo',       'Dischi + pastiglie ant. e post. (-15%)',          360.00, 440.00, 2, NULL,              60, 1),
('pkg-auto-03', 'Pacchetto Estate Sicura',         'Check pre-vacanze + ricarica A/C + equilibratura', 100.00, 120.00, 3, NULL,             30, 1),
('pkg-auto-04', 'Pacchetto Flotta 3 Auto',         'Tagliando base × 3 auto (-20%)',                  288.00, 360.00, 3, 'srv-tagliando-base', 90, 1);

PRAGMA foreign_keys = ON;
