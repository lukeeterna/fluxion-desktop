-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: VEICOLI / GOMMISTA
-- Sotto-verticale: Gommista (cambio gomme, equilibratura, convergenza)
-- Per test voce Sara su iMac
-- Settimana: 31 Mar - 5 Apr 2026 (ALTA STAGIONE cambio estive!)
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Gomme Express Di Paolo'),
('categoria_attivita', 'auto'),
('macro_categoria', 'auto'),
('micro_categoria', 'gommista'),
('indirizzo_completo', 'Via dell''Artigianato 7, 35010 Limena (PD)'),
('orario_apertura', '08:00'),
('orario_chiusura', '18:30'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number', '3486557890'),
('whatsapp_attivo', 'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
-- Cambio stagionale (core del gommista)
('srv-cambio-stagionale',   'Cambio Gomme Stagionale',      'Smontaggio + montaggio set 4 gomme (estive o invernali)',           60.00,  45, 10, 'cambio',      '#6366f1', 1,  1),
('srv-equilibratura',       'Equilibratura 4 Ruote',        'Bilanciatura dinamica delle 4 ruote',                               30.00,  20,  5, 'cambio',      '#6366f1', 1,  2),
('srv-convergenza',         'Convergenza',                  'Allineamento assetto geometrico assi anteriore e posteriore',       40.00,  30,  5, 'assetto',     '#8b5cf6', 1,  3),
-- Riparazioni
('srv-riparazione-foratura','Riparazione Foratura',         'Vulcanizzazione foratura tubeless (se riparabile)',                  20.00,  15,  5, 'riparazione', '#ef4444', 1,  4),
('srv-cambio-valvole',      'Cambio Valvole',               'Sostituzione valvole aria 4 ruote',                                 20.00,  15,  5, 'riparazione', '#ef4444', 1,  5),
('srv-sostituzione-tpms',   'Sostituzione TPMS',            'Sensori pressione pneumatici (1 pezzo)',                             80.00,  30,  5, 'riparazione', '#f59e0b', 1,  6),
-- Pneumatici
('srv-pneumatici-nuovi',    'Pneumatici Nuovi',             'Fornitura + montaggio set 4 pneumatici (prezzo montaggio)',        400.00,  60, 10, 'pneumatici',  '#10b981', 1,  7),
('srv-cerchi-lega',         'Cerchi in Lega Montaggio',     'Smontaggio + montaggio cerchi in lega (set 4)',                    120.00,  45, 10, 'pneumatici',  '#10b981', 1,  8),
-- Servizi complementari
('srv-stoccaggio',          'Stoccaggio Gomme Stagionale',  'Custodia pneumatici per stagione (set 4) in magazzino climatizzato', 50.00,  15,  0, 'stoccaggio',  '#3b82f6', 1,  9),
('srv-azoto',               'Gonfiaggio Azoto',             'Gonfiaggio con azoto puro 4 ruote (minor perdita pressione)',        15.00,  10,  0, 'servizi',     '#3b82f6', 1, 10),
('srv-assetto-completo',    'Assetto Ruote Completo',       'Convergenza + campanatura + equilibratura (full setup)',             80.00,  45, 10, 'assetto',     '#8b5cf6', 1, 11),
('srv-controllo-pneumatici','Controllo Pneumatici',         'Verifica usura, pressione e danni visivi (gratuito)',                 0.00,  10,  0, 'servizi',     '#6b7280', 1, 12);

-- ── OPERATORI (gommisti) ──────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-gom-paolo',   'Paolo',   'Di Stasio', 'admin',     '#6366f1', 1, '["cambio_gomme","convergenza","assetto","TPMS","cerchi_lega"]',  'Titolare, 20 anni esperienza pneumatici, certificato Michelin e Pirelli'),
('op-gom-marco',   'Marco',   'Silvestri', 'operatore', '#10b981', 1, '["cambio_gomme","equilibratura","riparazione_foratura","azoto"]', 'Gommista senior, specializzato bilanciatura e pneumatici run-flat'),
('op-gom-davide',  'Davide',  'Trevisan',  'operatore', '#f59e0b', 1, '["cambio_gomme","equilibratura","stoccaggio","valvole"]',        'Gommista, esperto stoccaggio e gestione magazzino pneumatici');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Officina aperta 08:00-18:30. Lun-Sab orario completo.
-- Alta stagione (Mar-Apr): turnazione potenziata per cambio estive
DELETE FROM orari_lavoro WHERE operatore_id IN ('op-gom-paolo','op-gom-marco','op-gom-davide');

-- PAOLO (titolare) — Lun-Ven 08:00-12:30 / 14:00-18:30, Sab 08:00-12:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-gom-paolo-lun-am', 1, '08:00', '12:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-lun-pa', 1, '12:30', '14:00', 'pausa',  'op-gom-paolo'),
('ol-gom-paolo-lun-pm', 1, '14:00', '18:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-mar-am', 2, '08:00', '12:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-mar-pa', 2, '12:30', '14:00', 'pausa',  'op-gom-paolo'),
('ol-gom-paolo-mar-pm', 2, '14:00', '18:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-mer-am', 3, '08:00', '12:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-mer-pa', 3, '12:30', '14:00', 'pausa',  'op-gom-paolo'),
('ol-gom-paolo-mer-pm', 3, '14:00', '18:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-gio-am', 4, '08:00', '12:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-gio-pa', 4, '12:30', '14:00', 'pausa',  'op-gom-paolo'),
('ol-gom-paolo-gio-pm', 4, '14:00', '18:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-ven-am', 5, '08:00', '12:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-ven-pa', 5, '12:30', '14:00', 'pausa',  'op-gom-paolo'),
('ol-gom-paolo-ven-pm', 5, '14:00', '18:30', 'lavoro', 'op-gom-paolo'),
('ol-gom-paolo-sab-am', 6, '08:00', '12:30', 'lavoro', 'op-gom-paolo');

-- MARCO (gommista senior) — Lun-Ven 08:00-12:30 / 14:00-18:30, Sab 08:00-12:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-gom-marco-lun-am', 1, '08:00', '12:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-lun-pa', 1, '12:30', '14:00', 'pausa',  'op-gom-marco'),
('ol-gom-marco-lun-pm', 1, '14:00', '18:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-mar-am', 2, '08:00', '12:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-mar-pa', 2, '12:30', '14:00', 'pausa',  'op-gom-marco'),
('ol-gom-marco-mar-pm', 2, '14:00', '18:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-mer-am', 3, '08:00', '12:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-mer-pa', 3, '12:30', '14:00', 'pausa',  'op-gom-marco'),
('ol-gom-marco-mer-pm', 3, '14:00', '18:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-gio-am', 4, '08:00', '12:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-gio-pa', 4, '12:30', '14:00', 'pausa',  'op-gom-marco'),
('ol-gom-marco-gio-pm', 4, '14:00', '18:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-ven-am', 5, '08:00', '12:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-ven-pa', 5, '12:30', '14:00', 'pausa',  'op-gom-marco'),
('ol-gom-marco-ven-pm', 5, '14:00', '18:30', 'lavoro', 'op-gom-marco'),
('ol-gom-marco-sab-am', 6, '08:00', '12:30', 'lavoro', 'op-gom-marco');

-- DAVIDE (gommista) — Lun-Ven 08:00-12:30 / 14:00-18:00, Sab 08:00-12:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-gom-davide-lun-am', 1, '08:00', '12:30', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-lun-pa', 1, '12:30', '14:00', 'pausa',  'op-gom-davide'),
('ol-gom-davide-lun-pm', 1, '14:00', '18:00', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-mar-am', 2, '08:00', '12:30', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-mar-pa', 2, '12:30', '14:00', 'pausa',  'op-gom-davide'),
('ol-gom-davide-mar-pm', 2, '14:00', '18:00', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-mer-am', 3, '08:00', '12:30', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-mer-pa', 3, '12:30', '14:00', 'pausa',  'op-gom-davide'),
('ol-gom-davide-mer-pm', 3, '14:00', '18:00', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-gio-am', 4, '08:00', '12:30', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-gio-pa', 4, '12:30', '14:00', 'pausa',  'op-gom-davide'),
('ol-gom-davide-gio-pm', 4, '14:00', '18:00', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-ven-am', 5, '08:00', '12:30', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-ven-pa', 5, '12:30', '14:00', 'pausa',  'op-gom-davide'),
('ol-gom-davide-ven-pm', 5, '14:00', '18:00', 'lavoro', 'op-gom-davide'),
('ol-gom-davide-sab-am', 6, '08:00', '12:00', 'lavoro', 'op-gom-davide');

-- ── CLIENTI ───────────────────────────────────────────────────────
-- note: veicolo + targa in Italian format (AA 000 AA o AB123CD transitorio)
DELETE FROM clienti WHERE id LIKE 'cli-gom-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-gom-01', 'Luca',       'Ferraretto',  '3471234001', 'luca.ferraretto@email.it',  '1985-03-18', 1, 14, 0, 'Volkswagen Golf VIII 2021, targa FV582JK. Cambio stagionale ogni anno. Preferisce Michelin.'),
('cli-gom-02', 'Giovanna',   'Manzoni',     '3471234002', 'giovanna.m@email.it',       '1979-07-22', 1,  6, 0, 'Fiat 500 2019, targa EL234RK. Pneumatici 185/65 R15. Note: stoccaggio gomme invernali in magazzino.'),
('cli-gom-03', 'Roberto',    'Carnevali',   '3471234003', 'rob.carnev@email.it',       '1972-11-05', 1, 28, 1, 'BMW X5 2022, targa GH491PW. VIP, flotta aziendale 2 veicoli. Pirelli P-Zero. Stoccaggio incluso.'),
('cli-gom-04', 'Silvia',     'Tonello',     '3471234004', 'silvia.tonello@email.it',   '1991-04-14', 1,  3, 0, 'Toyota Yaris Hybrid 2023, targa JM102YT. Prima volta, cambio invernali→estive.'),
('cli-gom-05', 'Emanuele',   'Bortot',      '3471234005', 'ema.bortot@email.it',       '1968-09-30', 1, 35, 1, 'Mercedes Classe C 2020, targa DK773SR. VIP storico, 8 anni cliente. TPMS installati da noi.'),
('cli-gom-06', 'Cristina',   'Righetto',    '3471234006', 'cristina.r@email.it',       '1988-01-27', 0,  8, 0, 'Renault Clio 2020, targa AP341BH. Cerchi in lega aftermarket 17''. Equilibratura critica.'),
('cli-gom-07', 'Matteo',     'Segato',      '3471234007', 'matteo.segato@email.it',    '1995-06-12', 1,  2, 0, 'Peugeot 208 2022, targa NZ890CV. Foratura sul fianco, verificare se riparabile.'),
('cli-gom-08', 'Patrizia',   'Zambon',      '3471234008', 'pat.zambon@email.it',       '1963-12-08', 1, 20, 0, 'Fiat Panda 4x4 2018, targa CW554MN. Gomme invernali in stoccaggio. Pronta per cambio estive.');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- GIOVEDI' 3 APRILE = PIENO (test waitlist Sara)
-- Alta stagione cambio gomme: tutti i tecnici sotto pressione
DELETE FROM appuntamenti WHERE id LIKE 'apt-gom-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-gom-001', 'cli-gom-01', 'srv-cambio-stagionale',    'op-gom-paolo',  '2026-03-31T08:00:00', '2026-03-31T08:45:00',  45, 'confermato',  60.00,  60.00, 'Golf VIII — invernali→estive. Michelin Primacy 4 225/45 R17', 'whatsapp'),
('apt-gom-002', 'cli-gom-02', 'srv-cambio-stagionale',    'op-gom-marco',  '2026-03-31T08:00:00', '2026-03-31T08:45:00',  45, 'confermato',  60.00,  60.00, 'Fiat 500 — ritiro gomme da stoccaggio + montaggio estive',    'voice'),
('apt-gom-003', 'cli-gom-08', 'srv-cambio-stagionale',    'op-gom-davide', '2026-03-31T08:00:00', '2026-03-31T08:45:00',  45, 'confermato',  60.00,  60.00, 'Panda 4x4 — invernali→estive, ritiro stoccaggio',            'telefono'),
('apt-gom-004', 'cli-gom-01', 'srv-equilibratura',        'op-gom-marco',  '2026-03-31T09:00:00', '2026-03-31T09:20:00',  20, 'confermato',  30.00,  30.00, 'Post cambio stagionale Golf VIII',                           'whatsapp'),
('apt-gom-005', 'cli-gom-04', 'srv-cambio-stagionale',    'op-gom-paolo',  '2026-03-31T09:30:00', '2026-03-31T10:15:00',  45, 'confermato',  60.00,  60.00, 'Yaris Hybrid — prima volta, cambio invernali→estive',         'voice'),
('apt-gom-006', 'cli-gom-06', 'srv-equilibratura',        'op-gom-davide', '2026-03-31T09:00:00', '2026-03-31T09:20:00',  20, 'confermato',  30.00,  30.00, 'Clio cerchi lega 17'' — equilibratura post inverno',          'whatsapp'),
('apt-gom-007', 'cli-gom-03', 'srv-convergenza',          'op-gom-paolo',  '2026-03-31T14:00:00', '2026-03-31T14:30:00',  30, 'confermato',  40.00,  40.00, 'BMW X5 — controllo assetto post cambio stagionale',          'manuale'),
-- Martedì 1 Aprile
('apt-gom-008', 'cli-gom-03', 'srv-cambio-stagionale',    'op-gom-paolo',  '2026-04-01T08:00:00', '2026-04-01T08:45:00',  45, 'confermato',  60.00,  60.00, 'BMW X5 (2° veicolo flotta) — Pirelli P-Zero 275/45 R20',     'whatsapp'),
('apt-gom-009', 'cli-gom-05', 'srv-sostituzione-tpms',    'op-gom-paolo',  '2026-04-01T09:00:00', '2026-04-01T09:30:00',  30, 'confermato',  80.00,  80.00, 'Mercedes C — sensore TPMS ant. sinistro difettoso (codice)',  'whatsapp'),
('apt-gom-010', 'cli-gom-07', 'srv-riparazione-foratura', 'op-gom-marco',  '2026-04-01T08:30:00', '2026-04-01T08:45:00',  15, 'confermato',  20.00,  20.00, 'Peugeot 208 — foratura laterale, verificare riparabilità',   'voice'),
('apt-gom-011', 'cli-gom-06', 'srv-convergenza',          'op-gom-davide', '2026-04-01T10:00:00', '2026-04-01T10:30:00',  30, 'confermato',  40.00,  40.00, 'Clio — post equilibratura, verifica assetto',                'whatsapp'),
('apt-gom-012', 'cli-gom-08', 'srv-stoccaggio',           'op-gom-davide', '2026-04-01T08:50:00', '2026-04-01T09:05:00',  15, 'confermato',  50.00,  50.00, 'Panda 4x4 — deposito invernali per stagione est.',           'telefono'),
-- Mercoledì 2 Aprile
('apt-gom-013', 'cli-gom-02', 'srv-stoccaggio',           'op-gom-davide', '2026-04-02T08:00:00', '2026-04-02T08:15:00',  15, 'confermato',  50.00,  50.00, 'Fiat 500 — stoccaggio invernali rimossi oggi',               'whatsapp'),
('apt-gom-014', 'cli-gom-05', 'srv-cambio-stagionale',    'op-gom-paolo',  '2026-04-02T08:00:00', '2026-04-02T08:45:00',  45, 'confermato',  60.00,  60.00, 'Mercedes C — cambio invernali→estive Continental PremiumC.', 'manuale'),
('apt-gom-015', 'cli-gom-04', 'srv-azoto',                'op-gom-marco',  '2026-04-02T09:00:00', '2026-04-02T09:10:00',  10, 'confermato',  15.00,  15.00, 'Yaris Hybrid — gonfiaggio azoto post cambio',                'voice'),
-- Giovedì 3 Aprile (PIENO — test waitlist Sara!)
('apt-gom-016', 'cli-gom-01', 'srv-assetto-completo',     'op-gom-paolo',  '2026-04-03T08:00:00', '2026-04-03T08:45:00',  45, 'confermato',  80.00,  80.00, 'Golf VIII — assetto completo post stagione',                 'whatsapp'),
('apt-gom-017', 'cli-gom-05', 'srv-assetto-completo',     'op-gom-paolo',  '2026-04-03T09:00:00', '2026-04-03T09:45:00',  45, 'confermato',  80.00,  80.00, 'Mercedes C — assetto completo post sostituzione TPMS',       'whatsapp'),
('apt-gom-018', 'cli-gom-03', 'srv-pneumatici-nuovi',     'op-gom-marco',  '2026-04-03T08:00:00', '2026-04-03T09:00:00',  60, 'confermato', 400.00, 400.00, 'BMW X5 — montaggio Pirelli P-Zero nuovi 275/45 R20 (x4)',    'manuale'),
('apt-gom-019', 'cli-gom-06', 'srv-cambio-valvole',       'op-gom-davide', '2026-04-03T08:00:00', '2026-04-03T08:15:00',  15, 'confermato',  20.00,  20.00, 'Clio — sostituzione 4 valvole in gomma usurate',             'telefono'),
('apt-gom-020', 'cli-gom-07', 'srv-cambio-stagionale',    'op-gom-davide', '2026-04-03T14:00:00', '2026-04-03T14:45:00',  45, 'confermato',  60.00,  60.00, 'Peugeot 208 — cambio stagionale + pneumatico nuovo ant. sx', 'voice');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-gom-01', 'Pacchetto Cambio Stagionale',         'Cambio 4 gomme + equilibratura 4 ruote + stoccaggio invernali (-15%)',         119.00, 140.00, 3, NULL, 180, 1),
('pkg-gom-02', 'Pacchetto Sicurezza Pneumatici',      'Convergenza + assetto completo + controllo TPMS + gonfiaggio azoto (-20%)',    105.00, 135.00, 4, NULL, 365, 1);

-- ── SUPPLIERS (fornitori pneumatici) ──────────────────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-gom-%';
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-gom-01', 'Pirelli Tyre S.p.A.',         'ordini.nord@pirelli.com',       '026444001',  'Viale Sarca 222',           'Milano',  '20126', '00860640157', 'active', '2026-01-10T08:00:00', '2026-03-20T08:00:00'),
('sup-gom-02', 'Michelin Italia S.p.A.',       'distributori.it@michelin.com',  '024345111',  'Corso Sempione 55',         'Milano',  '20149', '00867780158', 'active', '2026-01-10T08:00:00', '2026-03-15T08:00:00'),
('sup-gom-03', 'Continental Italia S.r.l.',    'vendite@continental-italia.it', '026712900',  'Via Volturno 48',           'Segrate',  '20090', '01234560963', 'active', '2026-01-10T08:00:00', '2026-02-28T08:00:00'),
('sup-gom-04', 'Bridgestone Italia S.p.A.',    'dealer@bridgestone.it',         '0688681',    'Via Abbadesse 45',          'Roma',     '00141', '00452140585', 'active', '2026-01-10T08:00:00', '2026-03-10T08:00:00');

-- ── FATTURE ───────────────────────────────────────────────────────
-- 5 fatture con IVA 22% (ricambi e pneumatici sono imponibili IVA)
DELETE FROM fatture WHERE id LIKE 'fat-gom-%';
INSERT INTO fatture (
    id, numero, anno, numero_completo, tipo_documento, data_emissione,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione,
    cliente_codice_sdi, cliente_pec,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato
) VALUES
-- FV001/2026 — Roberto Carnevali (BMW flotta aziendale)
('fat-gom-001', 1, 2026, 'FV001/2026', 'TD01', '2026-03-10',
 'cli-gom-03', 'Carnevali Roberto',            NULL, 'CRNRRT72S05L736X',
 'Via Roma 44', '35010', 'Limena', 'PD', 'IT',
 '0000000', NULL,
 327.87, 72.13, 400.00,
 'MP05', 'TP02', 'pagata'),
-- FV002/2026 — Emanuele Bortot (Mercedes VIP, TPMS + cambio)
('fat-gom-002', 2, 2026, 'FV002/2026', 'TD01', '2026-03-18',
 'cli-gom-05', 'Bortot Emanuele',              NULL, 'BRTEMN68P30B563W',
 'Via Trieste 8', '35030', 'Rubano', 'PD', 'IT',
 '0000000', NULL,
 114.75, 25.25, 140.00,
 'MP02', 'TP02', 'pagata'),
-- FV003/2026 — Luca Ferraretto (Golf stagionale + equilibratura)
('fat-gom-003', 3, 2026, 'FV003/2026', 'TD01', '2026-03-22',
 'cli-gom-01', 'Ferraretto Luca',              NULL, 'FRRLCU85C18L736K',
 'Via Padova 12', '35010', 'Vigodarzere', 'PD', 'IT',
 '0000000', NULL,
  73.77, 16.23,  90.00,
 'MP08', 'TP02', 'pagata'),
-- FV004/2026 — Cristina Righetto (equilibratura + convergenza)
('fat-gom-004', 4, 2026, 'FV004/2026', 'TD01', '2026-03-25',
 'cli-gom-06', 'Righetto Cristina',            NULL, 'RGHCST88A67L736T',
 'Via Manzoni 3', '35010', 'Cadoneghe', 'PD', 'IT',
 '0000000', NULL,
  57.38, 12.62,  70.00,
 'MP08', 'TP02', 'pagata'),
-- FV005/2026 — Roberto Carnevali (2° fattura — pneumatici nuovi X5)
('fat-gom-005', 5, 2026, 'FV005/2026', 'TD01', '2026-03-28',
 'cli-gom-03', 'Carnevali Roberto',            NULL, 'CRNRRT72S05L736X',
 'Via Roma 44', '35010', 'Limena', 'PD', 'IT',
 '0000000', NULL,
 360.66, 79.34, 440.00,
 'MP05', 'TP02', 'emessa');

-- Aggiorna numeratore fatture
INSERT OR REPLACE INTO numeratore_fatture (anno, ultimo_numero) VALUES (2026, 5);

-- ── RIGHE FATTURE ─────────────────────────────────────────────────
DELETE FROM fatture_righe WHERE id LIKE 'rf-gom-%';
INSERT INTO fatture_righe (
    id, fattura_id, numero_linea, descrizione, quantita, unita_misura,
    prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, natura
) VALUES
-- FV001/2026 — BMW X5 cambio stagionale + convergenza
('rf-gom-001-1', 'fat-gom-001', 1, 'Cambio Gomme Stagionale BMW X5 — Pirelli P-Zero 275/45 R20',       1, 'PZ',  60.00, 0, 0,  60.00, 22.00, NULL),
('rf-gom-001-2', 'fat-gom-001', 2, 'Fornitura + montaggio pneumatici Pirelli P-Zero 275/45 R20 (x4)',  1, 'PZ', 327.87, 0, 0, 327.87, 22.00, NULL),
-- FV002/2026 — Mercedes TPMS + cambio
('rf-gom-002-1', 'fat-gom-002', 1, 'Sostituzione sensore TPMS anteriore sinistro Mercedes C',          1, 'PZ',  80.00, 0, 0,  80.00, 22.00, NULL),
('rf-gom-002-2', 'fat-gom-002', 2, 'Cambio Gomme Stagionale Mercedes Classe C — Continental',          1, 'PZ',  60.00, 0, 0,  60.00, 22.00, NULL),
-- FV003/2026 — Golf stagionale + equilibratura
('rf-gom-003-1', 'fat-gom-003', 1, 'Cambio Gomme Stagionale VW Golf VIII — Michelin Primacy 4',        1, 'PZ',  60.00, 0, 0,  60.00, 22.00, NULL),
('rf-gom-003-2', 'fat-gom-003', 2, 'Equilibratura 4 Ruote VW Golf VIII',                               1, 'PZ',  30.00, 0, 0,  30.00, 22.00, NULL),
-- FV004/2026 — Clio equilibratura + convergenza
('rf-gom-004-1', 'fat-gom-004', 1, 'Equilibratura 4 Ruote Renault Clio cerchi 17''',                  1, 'PZ',  30.00, 0, 0,  30.00, 22.00, NULL),
('rf-gom-004-2', 'fat-gom-004', 2, 'Convergenza Renault Clio',                                         1, 'PZ',  40.00, 0, 0,  40.00, 22.00, NULL),
-- FV005/2026 — BMW X5 pneumatici nuovi (2° fattura)
('rf-gom-005-1', 'fat-gom-005', 1, 'Fornitura Pirelli P-Zero 275/45 R20 (set 4) — stagione est. 2026', 4, 'PZ',  90.16, 0, 0, 360.66, 22.00, NULL);

-- ── INCASSI ───────────────────────────────────────────────────────
-- 10 incassi: mix contanti / carta / POS — tipico di un gommista
DELETE FROM incassi WHERE id LIKE 'inc-gom-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, descrizione, categoria, data_incasso) VALUES
-- Ultimi giorni (pre settimana seed)
('inc-gom-01',  60.00, 'carta',    'cli-gom-01', 'Cambio stagionale Golf VIII invernali→estive',           'servizio', datetime('now', 'localtime', '-5 day', '+9 hours')),
('inc-gom-02',  30.00, 'contanti', 'cli-gom-04', 'Equilibratura Yaris Hybrid post cambio',                 'servizio', datetime('now', 'localtime', '-5 day', '+10 hours')),
('inc-gom-03',  90.00, 'carta',    'cli-gom-01', 'Cambio stagionale + equilibratura Golf VIII',            'servizio', datetime('now', 'localtime', '-4 day', '+9 hours')),
('inc-gom-04', 140.00, 'pos',      'cli-gom-05', 'TPMS Mercedes C + cambio stagionale (acconto)',          'servizio', datetime('now', 'localtime', '-4 day', '+11 hours')),
('inc-gom-05',  60.00, 'contanti', 'cli-gom-08', 'Cambio stagionale Panda 4x4',                           'servizio', datetime('now', 'localtime', '-3 day', '+8 hours')),
('inc-gom-06',  50.00, 'carta',    'cli-gom-02', 'Stoccaggio invernali Fiat 500 — stagione',               'servizio', datetime('now', 'localtime', '-3 day', '+9 hours')),
('inc-gom-07',  20.00, 'contanti', 'cli-gom-07', 'Riparazione foratura Peugeot 208',                      'servizio', datetime('now', 'localtime', '-2 day', '+10 hours')),
('inc-gom-08', 400.00, 'bonifico', 'cli-gom-03', 'Pneumatici Pirelli P-Zero BMW X5 (x4) — flotta',        'prodotto', datetime('now', 'localtime', '-2 day', '+14 hours')),
('inc-gom-09',  70.00, 'pos',      'cli-gom-06', 'Equilibratura + convergenza Renault Clio',               'servizio', datetime('now', 'localtime', '-1 day', '+9 hours')),
('inc-gom-10',  80.00, 'carta',    'cli-gom-05', 'Assetto completo Mercedes Classe C',                     'servizio', datetime('now', 'localtime', '-1 day', '+11 hours'));

PRAGMA foreign_keys = ON;
