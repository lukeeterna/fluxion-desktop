-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: CENTRO ESTETICO (full restore)
-- Ripristina il verticale beauty dopo test altre verticali
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Centro Estetico Bellezza Pura'),
('categoria_attivita', 'beauty'),
('macro_categoria', 'beauty'),
('micro_categoria', 'estetista_viso'),
('indirizzo_completo', 'Via Nazionale 88, 80013 Casalnuovo (NA)'),
('orario_apertura', '09:00'),
('orario_chiusura', '19:30'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-pulizia-viso',      'Pulizia Viso',                'Pulizia profonda con vapore e massaggio',            50.00,  60, 10, 'viso',        '#f9a8d4', 1,  1),
('srv-antirughe',         'Trattamento Antirughe',       'Filler naturale + radiofrequenza viso',              70.00,  60, 10, 'viso',        '#f9a8d4', 1,  2),
('srv-peeling',           'Peeling Chimico',             'Esfoliazione acidi AHA/BHA professionale',           80.00,  45, 15, 'viso',        '#f9a8d4', 1,  3),
('srv-manicure-base',     'Manicure Classica',           'Lima, cuticole, massaggio mani e smalto',            20.00,  30,  5, 'unghie',      '#c084fc', 1,  4),
('srv-manicure-semi',     'Manicure Semipermanente',     'Applicazione semipermanente gel UV',                 35.00,  45,  5, 'unghie',      '#c084fc', 1,  5),
('srv-pedicure',          'Pedicure Curativa',           'Trattamento piedi + smalto',                         30.00,  45,  5, 'unghie',      '#c084fc', 1,  6),
('srv-ceretta-gambe',     'Ceretta Gambe',               'Ceretta intera gamba con cera liposolubile',         25.00,  30,  5, 'ceretta',     '#fb923c', 1,  7),
('srv-ceretta-inguine',   'Ceretta Inguine',             'Ceretta inguine brasiliana',                         20.00,  20,  5, 'ceretta',     '#fb923c', 1,  8),
('srv-ceretta-braccia',   'Ceretta Braccia',             'Ceretta completa braccia',                           15.00,  20,  5, 'ceretta',     '#fb923c', 1,  9),
('srv-ceretta-baffetti',  'Ceretta Baffetti',            'Depilazione zona labbro superiore',                   8.00,  10,  5, 'ceretta',     '#fb923c', 1, 10),
('srv-laser-zona',        'Epilazione Laser Zona',       'Epilazione laser diodo singola zona',                80.00,  30, 10, 'laser',       '#ef4444', 1, 11),
('srv-massaggio',         'Massaggio Rilassante',        'Massaggio corpo olio aromaterapia 50 min',           60.00,  50, 10, 'corpo',       '#34d399', 1, 12),
('srv-linfodrenaggio',    'Linfodrenaggio',              'Drenaggio manuale Vodder gambe e addome',            70.00,  60, 10, 'corpo',       '#34d399', 1, 13),
('srv-tonificante',       'Trattamento Corpo Tonificante','Pressoterapia + radiofrequenza corpo',              65.00,  60, 10, 'corpo',       '#34d399', 1, 14),
('srv-sopracciglia',      'Sopracciglia Design',         'Profilatura e definizione arco sopraccigliare',      12.00,  15,  5, 'occhi',       '#818cf8', 1, 15),
('srv-extension-ciglia',  'Extension Ciglia',            'Applicazione extension singole filo per filo',       80.00,  90, 10, 'occhi',       '#818cf8', 1, 16);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-francesca', 'Francesca', 'De Luca',  'admin',     '#f9a8d4', 1, '["trattamenti viso","peeling","laser","antirughe"]',  'Titolare, 12 anni esperienza estetica medica e avanzata'),
('op-carmela',   'Carmela',   'Esposito', 'operatore', '#c084fc', 1, '["manicure","pedicure","extension ciglia","sopracciglia"]', 'Nail artist specializzata, 8 anni esperienza unghie e ciglia'),
('op-rosa',      'Rosa',      'Ferrara',  'operatore', '#fb923c', 1, '["ceretta","linfodrenaggio","massaggio","corpo"]',    'Estetista corpo, esperta drenaggio e trattamenti tonificanti'),
('op-teresa',    'Teresa',    'Marino',   'operatore', '#34d399', 1, '["massaggio","pressoterapia","laser","ceretta"]',     'Specialista benessere e laser epilazione, 5 anni esperienza');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Francesca: lun-sab full (titolare)
-- Carmela:   lun-ven + sab mattina (unghie e ciglia)
-- Rosa:      mar,mer,gio,ven,sab (parte del lun libero)
-- Teresa:    lun-ven 10-19 (no sabato)

DELETE FROM orari_lavoro WHERE operatore_id IN ('op-francesca','op-carmela','op-rosa','op-teresa');

-- FRANCESCA (titolare) — Lun-Ven 09-13/14-19:30, Sab 09-13
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-fra-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-francesca'),
('ol-fra-lun-pa', 1, '13:00', '14:00', 'pausa',  'op-francesca'),
('ol-fra-lun-pm', 1, '14:00', '19:30', 'lavoro', 'op-francesca'),
('ol-fra-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-francesca'),
('ol-fra-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-francesca'),
('ol-fra-mar-pm', 2, '14:00', '19:30', 'lavoro', 'op-francesca'),
('ol-fra-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-francesca'),
('ol-fra-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-francesca'),
('ol-fra-mer-pm', 3, '14:00', '19:30', 'lavoro', 'op-francesca'),
('ol-fra-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-francesca'),
('ol-fra-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-francesca'),
('ol-fra-gio-pm', 4, '14:00', '19:30', 'lavoro', 'op-francesca'),
('ol-fra-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-francesca'),
('ol-fra-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-francesca'),
('ol-fra-ven-pm', 5, '14:00', '19:30', 'lavoro', 'op-francesca'),
('ol-fra-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-francesca');

-- CARMELA (unghie/ciglia) — Lun-Ven 09-13/14-19, Sab 09-13
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-car-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-carmela'),
('ol-car-lun-pa', 1, '13:00', '14:00', 'pausa',  'op-carmela'),
('ol-car-lun-pm', 1, '14:00', '19:00', 'lavoro', 'op-carmela'),
('ol-car-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-carmela'),
('ol-car-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-carmela'),
('ol-car-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-carmela'),
('ol-car-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-carmela'),
('ol-car-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-carmela'),
('ol-car-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-carmela'),
('ol-car-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-carmela'),
('ol-car-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-carmela'),
('ol-car-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-carmela'),
('ol-car-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-carmela'),
('ol-car-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-carmela'),
('ol-car-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-carmela'),
('ol-car-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-carmela');

-- ROSA (corpo/ceretta) — Mar-Sab 09-13/14-18 (lun libero)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-ros-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-rosa'),
('ol-ros-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-rosa'),
('ol-ros-mar-pm', 2, '14:00', '18:00', 'lavoro', 'op-rosa'),
('ol-ros-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-rosa'),
('ol-ros-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-rosa'),
('ol-ros-mer-pm', 3, '14:00', '18:00', 'lavoro', 'op-rosa'),
('ol-ros-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-rosa'),
('ol-ros-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-rosa'),
('ol-ros-gio-pm', 4, '14:00', '18:00', 'lavoro', 'op-rosa'),
('ol-ros-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-rosa'),
('ol-ros-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-rosa'),
('ol-ros-ven-pm', 5, '14:00', '18:00', 'lavoro', 'op-rosa'),
('ol-ros-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-rosa');

-- TERESA (laser/massaggio) — Lun-Ven 10-13/14-19 (no sabato)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-ter-lun-am', 1, '10:00', '13:00', 'lavoro', 'op-teresa'),
('ol-ter-lun-pa', 1, '13:00', '14:00', 'pausa',  'op-teresa'),
('ol-ter-lun-pm', 1, '14:00', '19:00', 'lavoro', 'op-teresa'),
('ol-ter-mar-am', 2, '10:00', '13:00', 'lavoro', 'op-teresa'),
('ol-ter-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-teresa'),
('ol-ter-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-teresa'),
('ol-ter-mer-am', 3, '10:00', '13:00', 'lavoro', 'op-teresa'),
('ol-ter-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-teresa'),
('ol-ter-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-teresa'),
('ol-ter-gio-am', 4, '10:00', '13:00', 'lavoro', 'op-teresa'),
('ol-ter-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-teresa'),
('ol-ter-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-teresa'),
('ol-ter-ven-am', 5, '10:00', '13:00', 'lavoro', 'op-teresa'),
('ol-ter-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-teresa'),
('ol-ter-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-teresa');

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-bea-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-bea-01', 'Maria',     'Esposito',   '3332221001', 'maria.e@email.it',     '1980-06-14', 1, 28, 1, 'Pelle mista tendente grassa. VIP da 4 anni. Allergia nichel → no cerette metalliche'),
('cli-bea-02', 'Giulia',    'Ruggiero',   '3332221002', 'giulia.r@email.it',    '1993-02-22', 1, 12, 0, 'Pelle secca sensibile. Peeling leggero. Laser ascelle e inguine ciclo attivo'),
('cli-bea-03', 'Concetta',  'Ferrara',    '3332221003', 'concetta.f@email.it',  '1975-09-08', 1, 35, 1, 'Pelle matura. Trattamento antirughe ogni 6 settimane. Nessuna controindicazione'),
('cli-bea-04', 'Valentina', 'Napolitano', '3332221004', 'vale.nap@email.it',    '1990-04-30', 1,  6, 0, 'Prima cliente. Extension ciglia. Pelle normale. Nessuna allergia dichiarata'),
('cli-bea-05', 'Angela',    'De Rosa',    '3332221005', 'angela.dr@email.it',   '1987-11-17', 1, 20, 0, 'Manicure semipermanente ogni 3 settimane. Pedicure mensile. Nessuna allergia'),
('cli-bea-06', 'Immacolata','Sorrentino', '3332221006', 'imma.s@email.it',      '1969-03-05', 0, 45, 1, 'Cliente storica, titolare di attività. Pulizia viso + linfodrenaggio mensile'),
('cli-bea-07', 'Sofia',     'Coppola',    '3332221007', 'sofia.c@email.it',     '1998-08-25', 1,  4, 0, 'Studentessa. Ceretta gambe + sopracciglia. Pelle tendente grassa con comedoni'),
('cli-bea-08', 'Rossella',  'D''Ambrosio','3332221008', 'rossella.d@email.it',  '1985-12-03', 1, 16, 0, 'Sposa maggio 2026. Pacchetto sposa attivo. Pelle normale, leggera iperpigmentazione');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- Giovedì 3 Aprile = giornata PIENA (test waitlist)
DELETE FROM appuntamenti WHERE id LIKE 'apt-bea-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-bea-001', 'cli-bea-01', 'srv-pulizia-viso',     'op-francesca', '2026-03-31T09:00:00', '2026-03-31T10:00:00',  60, 'confermato',  50.00,  50.00, 'Pulizia profonda mensile',              'whatsapp'),
('apt-bea-002', 'cli-bea-05', 'srv-manicure-semi',    'op-carmela',   '2026-03-31T09:30:00', '2026-03-31T10:15:00',  45, 'confermato',  35.00,  35.00, 'Rosa nude come di solito',              'whatsapp'),
('apt-bea-003', 'cli-bea-07', 'srv-sopracciglia',     'op-carmela',   '2026-03-31T10:30:00', '2026-03-31T10:45:00',  15, 'confermato',  12.00,  12.00, NULL,                                    'voice'),
('apt-bea-004', 'cli-bea-02', 'srv-laser-zona',       'op-teresa',    '2026-03-31T10:00:00', '2026-03-31T10:30:00',  30, 'confermato',  80.00,  80.00, 'Laser ascelle — seduta 4 di 6',         'voice'),
('apt-bea-005', 'cli-bea-06', 'srv-linfodrenaggio',   'op-rosa',      '2026-03-31T14:00:00', '2026-03-31T15:00:00',  60, 'confermato',  70.00,  70.00, 'Drenaggio mensile gambe',               'whatsapp'),
('apt-bea-006', 'cli-bea-03', 'srv-antirughe',        'op-francesca', '2026-03-31T14:00:00', '2026-03-31T15:00:00',  60, 'confermato',  70.00,  70.00, 'Trattamento zona contorno occhi',       'manuale'),
-- Martedì 1 Aprile
('apt-bea-007', 'cli-bea-08', 'srv-pulizia-viso',     'op-francesca', '2026-04-01T09:00:00', '2026-04-01T10:00:00',  60, 'confermato',  50.00,  50.00, 'Pre-matrimonio: pelle luminosa',        'whatsapp'),
('apt-bea-008', 'cli-bea-04', 'srv-extension-ciglia', 'op-carmela',   '2026-04-01T09:30:00', '2026-04-01T11:00:00',  90, 'confermato',  80.00,  80.00, 'Prima applicazione — effetto naturale', 'voice'),
('apt-bea-009', 'cli-bea-07', 'srv-ceretta-gambe',    'op-rosa',      '2026-04-01T10:00:00', '2026-04-01T10:30:00',  30, 'confermato',  25.00,  25.00, NULL,                                    'whatsapp'),
('apt-bea-010', 'cli-bea-02', 'srv-peeling',          'op-francesca', '2026-04-01T14:00:00', '2026-04-01T14:45:00',  45, 'confermato',  80.00,  80.00, 'Peeling AHA 20% pelle sensibile',       'whatsapp'),
('apt-bea-011', 'cli-bea-05', 'srv-pedicure',         'op-carmela',   '2026-04-01T14:30:00', '2026-04-01T15:15:00',  45, 'confermato',  30.00,  30.00, 'Pedicure mensile',                      'manuale'),
-- Mercoledì 2 Aprile
('apt-bea-012', 'cli-bea-01', 'srv-massaggio',        'op-teresa',    '2026-04-02T10:00:00', '2026-04-02T10:50:00',  50, 'confermato',  60.00,  60.00, 'Massaggio rilassante schiena',          'voice'),
('apt-bea-013', 'cli-bea-06', 'srv-pulizia-viso',     'op-francesca', '2026-04-02T09:00:00', '2026-04-02T10:00:00',  60, 'confermato',  50.00,  50.00, NULL,                                    'whatsapp'),
('apt-bea-014', 'cli-bea-05', 'srv-ceretta-baffetti', 'op-rosa',      '2026-04-02T11:00:00', '2026-04-02T11:10:00',  10, 'confermato',   8.00,   8.00, NULL,                                    'whatsapp'),
('apt-bea-015', 'cli-bea-03', 'srv-tonificante',      'op-rosa',      '2026-04-02T14:00:00', '2026-04-02T15:00:00',  60, 'confermato',  65.00,  65.00, 'Pressoterapia gambe',                   'manuale'),
-- Giovedì 3 Aprile (giornata PIENA — test waitlist)
('apt-bea-016', 'cli-bea-08', 'srv-antirughe',        'op-francesca', '2026-04-03T09:00:00', '2026-04-03T10:00:00',  60, 'confermato',  70.00,  70.00, 'Trattamento sposa — fronte e collo',    'whatsapp'),
('apt-bea-017', 'cli-bea-04', 'srv-manicure-semi',    'op-carmela',   '2026-04-03T09:00:00', '2026-04-03T09:45:00',  45, 'confermato',  35.00,  35.00, 'Gel rosa antico',                       'voice'),
('apt-bea-018', 'cli-bea-07', 'srv-ceretta-inguine',  'op-rosa',      '2026-04-03T09:30:00', '2026-04-03T09:50:00',  20, 'confermato',  20.00,  20.00, NULL,                                    'whatsapp'),
('apt-bea-019', 'cli-bea-02', 'srv-laser-zona',       'op-teresa',    '2026-04-03T10:00:00', '2026-04-03T10:30:00',  30, 'confermato',  80.00,  80.00, 'Laser inguine — seduta 3 di 6',         'voice'),
('apt-bea-020', 'cli-bea-01', 'srv-peeling',          'op-francesca', '2026-04-03T14:00:00', '2026-04-03T14:45:00',  45, 'confermato',  80.00,  80.00, 'Peeling viso pre-estate',               'whatsapp');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-bea-01', 'Pacchetto Sposa',     '3 pulizie viso + 2 trattamenti antirughe + extension ciglia (-15%)',   240.00, 280.00, 6, NULL,                 90, 1),
('pkg-bea-02', 'Pacchetto Relax',     '4 massaggi rilassanti al prezzo di 3',                                 180.00, 240.00, 4, 'srv-massaggio',     120, 1),
('pkg-bea-03', 'Pacchetto Anti-Age',  '6 trattamenti antirughe + 2 peeling chimici (-20%)',                   480.00, 600.00, 8, NULL,                180, 1);

-- ── SUPPLIERS (fornitori cosmetici) ───────────────────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-bea-%';
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-bea-01', 'Sothys Italia Srl',      'ordini@sothys.it',        '0223451234', 'Via Montenapoleone 12', 'Milano',  '20121', '04512378901', 'active', '2026-01-10T09:00:00', '2026-03-01T09:00:00'),
('sup-bea-02', 'Perron Rigot Cera Pro',  'italy@perronrigot.com',   '0245671890', 'Via Savona 99',         'Milano',  '20144', '07891234560', 'active', '2026-01-15T09:00:00', '2026-02-20T09:00:00'),
('sup-bea-03', 'Biotec Apparecchiature', 'info@biotec-beauty.it',   '0811234567', 'Via Caracciolo 45',     'Napoli',  '80122', '05678901234', 'active', '2026-02-01T09:00:00', '2026-03-10T09:00:00');

-- ── FATTURE (con righe, IVA 22%) ──────────────────────────────────
DELETE FROM fatture WHERE id LIKE 'fat-bea-%';
INSERT INTO fatture (
    id, numero, anno, numero_completo, tipo_documento, data_emissione,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione,
    cliente_codice_sdi, cliente_pec,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato
) VALUES
('fat-bea-001', 1, 2026, 'FV001-2026', 'TD01', '2026-03-03',
 'cli-bea-06', 'Immacolata Sorrentino', NULL, 'SRRMLT69C45F839Z',
 'Via Toledo 88', '80132', 'Napoli', 'NA', 'IT',
 '0000000', NULL,
 172.13, 37.87, 210.00,
 'MP01', 'TP02', 'pagata'),
('fat-bea-002', 2, 2026, 'FV002-2026', 'TD01', '2026-03-10',
 'cli-bea-03', 'Concetta Ferrara', NULL, 'FRRCCT75P48F839A',
 'Via Duomo 14', '80138', 'Napoli', 'NA', 'IT',
 '0000000', NULL,
 114.75, 25.25, 140.00,
 'MP02', 'TP02', 'pagata'),
('fat-bea-003', 3, 2026, 'FV003-2026', 'TD01', '2026-03-17',
 'cli-bea-08', 'Rossella D''Ambrosio', NULL, 'DMBRSS85T43F839B',
 'Via Mergellina 5', '80122', 'Napoli', 'NA', 'IT',
 '0000000', NULL,
 204.92, 45.08, 250.00,
 'MP08', 'TP02', 'emessa'),
('fat-bea-004', 4, 2026, 'FV004-2026', 'TD01', '2026-03-24',
 'cli-bea-01', 'Maria Esposito', NULL, 'SPSMIR80H54F839C',
 'Via Roma 33', '80013', 'Casalnuovo', 'NA', 'IT',
 '0000000', NULL,
 122.95, 27.05, 150.00,
 'MP01', 'TP02', 'pagata'),
('fat-bea-005', 5, 2026, 'FV005-2026', 'TD01', '2026-03-28',
 'cli-bea-06', 'Immacolata Sorrentino', NULL, 'SRRMLT69C45F839Z',
 'Via Toledo 88', '80132', 'Napoli', 'NA', 'IT',
 '0000000', NULL,
 98.36, 21.64, 120.00,
 'MP01', 'TP02', 'bozza');

-- Righe fatture
DELETE FROM fatture_righe WHERE id LIKE 'rfbea-%';
INSERT INTO fatture_righe (
    id, fattura_id, numero_linea, descrizione, quantita, unita_misura,
    prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, natura
) VALUES
-- fat-bea-001: pacchetto sposa + extension
('rfbea-001-1', 'fat-bea-001', 1, 'Pacchetto Sposa — 3 Pulizie Viso + 2 Antirughe',            1, 'PZ', 150.00, 0, 0, 150.00, 22.00, NULL),
('rfbea-001-2', 'fat-bea-001', 2, 'Extension Ciglia — applicazione completa',                   1, 'PZ',  80.00, 0, 0,  80.00, 22.00, NULL),
-- fat-bea-002: antirughe ciclo
('rfbea-002-1', 'fat-bea-002', 1, 'Trattamento Antirughe × 2 sedute',                           2, 'PZ',  70.00, 0, 0, 140.00, 22.00, NULL),
-- fat-bea-003: pacchetto relax sposa
('rfbea-003-1', 'fat-bea-003', 1, 'Pacchetto Sposa — servizi preparativi matrimonio',           1, 'PZ', 240.00, 0, 0, 240.00, 22.00, NULL),
('rfbea-003-2', 'fat-bea-003', 2, 'Peeling Chimico AHA — seduta preparatoria',                  1, 'PZ',  80.00, 0, 0,  80.00, 22.00, NULL),
-- fat-bea-004: pulizie + massaggio
('rfbea-004-1', 'fat-bea-004', 1, 'Pulizia Viso Profonda × 2 sedute mensili',                   2, 'PZ',  50.00, 0, 0, 100.00, 22.00, NULL),
('rfbea-004-2', 'fat-bea-004', 2, 'Massaggio Rilassante Aromaterapia',                          1, 'PZ',  60.00, 0, 0,  60.00, 22.00, NULL),
-- fat-bea-005: linfodrenaggio ciclo
('rfbea-005-1', 'fat-bea-005', 1, 'Linfodrenaggio Manuale × 2 sedute (ciclo mensile)',          2, 'PZ',  70.00, 0, 0, 140.00, 22.00, NULL);

-- Aggiorna numeratore fatture
INSERT OR REPLACE INTO numeratore_fatture (anno, ultimo_numero) VALUES (2026, 5);

-- ── INCASSI ───────────────────────────────────────────────────────
DELETE FROM incassi WHERE id LIKE 'inc-bea-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, descrizione, categoria, data_incasso) VALUES
('inc-bea-01', 50.00, 'contanti',  'cli-bea-01', 'Pulizia Viso',                           'servizio',  '2026-03-24T10:30:00'),
('inc-bea-02', 35.00, 'carta',     'cli-bea-05', 'Manicure Semipermanente',                 'servizio',  '2026-03-24T11:00:00'),
('inc-bea-03', 80.00, 'satispay',  'cli-bea-02', 'Laser Ascelle — seduta 3',               'servizio',  '2026-03-24T12:00:00'),
('inc-bea-04', 70.00, 'carta',     'cli-bea-06', 'Linfodrenaggio Gambe',                    'servizio',  '2026-03-25T09:30:00'),
('inc-bea-05', 12.00, 'contanti',  'cli-bea-07', 'Sopracciglia Design',                     'servizio',  '2026-03-25T10:00:00'),
('inc-bea-06',140.00, 'carta',     'cli-bea-03', 'Trattamento Antirughe × 2',               'fattura',   '2026-03-25T14:30:00'),
('inc-bea-07', 80.00, 'satispay',  'cli-bea-08', 'Extension Ciglia — prima applicazione',   'servizio',  '2026-03-26T09:30:00'),
('inc-bea-08', 25.00, 'contanti',  'cli-bea-07', 'Ceretta Gambe',                           'servizio',  '2026-03-26T10:30:00'),
('inc-bea-09',240.00, 'carta',     'cli-bea-08', 'Pacchetto Sposa — acconto 50%',           'pacchetto', '2026-03-27T11:00:00'),
('inc-bea-10', 65.00, 'satispay',  'cli-bea-03', 'Trattamento Corpo Tonificante',           'servizio',  '2026-03-27T15:00:00');

PRAGMA foreign_keys = ON;
