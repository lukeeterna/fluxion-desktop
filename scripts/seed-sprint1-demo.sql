-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Sprint 1: Seed Completo Demo (Marzo 2026)
-- Target dashboard: fatturato ~€4.850, 9 appuntamenti oggi, 48+ clienti
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- -------------------------------------------------------
-- APPUNTAMENTI OGGI 24 MARZO 2026 (Martedì — giornata piena)
-- -------------------------------------------------------
INSERT OR REPLACE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
('td-001', 'cli-anna',      'srv-colore',       'op-giulia', '2026-03-24T09:00:00', '2026-03-24T10:00:00', 60, 'completato', 45.00, 65.00, 'Ritocco radici castano 5N', 'whatsapp'),
('td-002', 'cli-paolo',     'srv-taglio-uomo',  'op-marco',  '2026-03-24T09:00:00', '2026-03-24T09:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('td-003', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-03-24T09:30:00', '2026-03-24T10:00:00', 30, 'completato', 18.00, 30.00, 'Fade + barba completa', 'voice'),
('td-004', 'cli-elena',     'srv-meches',       'op-giulia', '2026-03-24T10:30:00', '2026-03-24T12:00:00', 90, 'completato', 65.00, 85.00, 'Balayage miele estate', 'whatsapp'),
('td-005', 'cli-chiara',    'srv-trattamento',  'op-laura',  '2026-03-24T11:00:00', '2026-03-24T12:00:00', 60, 'completato', 30.00, 45.00, 'Keratina brasiliana', 'whatsapp'),
('td-006', 'cli-francesca', 'srv-piega',        'op-paola',  '2026-03-24T14:00:00', '2026-03-24T14:30:00', 30, 'confermato', 20.00, 25.00, 'Piega volume', 'voice'),
('td-007', 'cli-sara',      'srv-colore',       'op-giulia', '2026-03-24T14:30:00', '2026-03-24T15:30:00', 60, 'confermato', 45.00, 75.00, 'Biondo cenere Wella 12.1', 'whatsapp'),
('td-008', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-03-24T15:00:00', '2026-03-24T15:20:00', 20, 'confermato', 12.00, 12.00, NULL, 'voice'),
('td-009', 'cli-lucia',     'srv-meches',       'op-laura',  '2026-03-24T16:00:00', '2026-03-24T17:30:00', 90, 'confermato', 65.00, 95.00, 'Meches platino freddo', 'manuale');

-- -------------------------------------------------------
-- INCASSI OGGI (completati)
-- -------------------------------------------------------
INSERT OR REPLACE INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, descrizione, categoria, data_incasso, created_at) VALUES
('itd-001', 65.00, 'carta',     'cli-anna',    'td-001', 'Colore + piega',          'servizio', '2026-03-24T10:05:00', '2026-03-24T10:05:00'),
('itd-002', 18.00, 'contanti',  'cli-paolo',   'td-002', 'Taglio uomo',             'servizio', '2026-03-24T09:35:00', '2026-03-24T09:35:00'),
('itd-003', 30.00, 'satispay',  'cli-matteo',  'td-003', 'Fade + barba',            'servizio', '2026-03-24T10:05:00', '2026-03-24T10:05:00'),
('itd-004', 85.00, 'carta',     'cli-elena',   'td-004', 'Balayage miele',          'servizio', '2026-03-24T12:10:00', '2026-03-24T12:10:00'),
('itd-005', 45.00, 'carta',     'cli-chiara',  'td-005', 'Keratina brasiliana',     'servizio', '2026-03-24T12:05:00', '2026-03-24T12:05:00');

-- -------------------------------------------------------
-- APPUNTAMENTI 23 MARZO (Lunedi) — settimana corrente
-- -------------------------------------------------------
INSERT OR REPLACE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
('w2-001', 'cli-simona',    'srv-colore',       'op-giulia', '2026-03-23T09:00:00', '2026-03-23T10:00:00', 60, 'completato', 45.00, 55.00, 'Castano cioccolato', 'whatsapp'),
('w2-002', 'cli-roberto',   'srv-taglio-uomo',  'op-marco',  '2026-03-23T09:30:00', '2026-03-23T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('w2-003', 'cli-valeria',   'srv-meches',       'op-giulia', '2026-03-23T10:30:00', '2026-03-23T12:00:00', 90, 'completato', 65.00, 80.00, 'Meches caramello', 'whatsapp'),
('w2-004', 'cli-davide',    'srv-taglio-uomo',  'op-luca',   '2026-03-23T10:00:00', '2026-03-23T10:30:00', 30, 'completato', 18.00, 22.00, 'Taglio + styling', 'voice'),
('w2-005', 'cli-martina',   'srv-piega',        'op-paola',  '2026-03-23T14:00:00', '2026-03-23T14:30:00', 30, 'completato', 20.00, 25.00, 'Piega morbida', 'whatsapp'),
('w2-006', 'cli-giuseppe',  'srv-taglio-uomo',  'op-marco',  '2026-03-23T14:30:00', '2026-03-23T15:00:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),
('w2-007', 'cli-alessia',   'srv-trattamento',  'op-laura',  '2026-03-23T15:00:00', '2026-03-23T16:00:00', 60, 'completato', 30.00, 40.00, 'Trattamento idratante Olaplex', 'manuale');

-- Incassi 23 marzo
INSERT OR REPLACE INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, descrizione, categoria, data_incasso, created_at) VALUES
('iw2-001', 55.00, 'carta',     'cli-simona',    'w2-001', 'Colore castano',       'servizio', '2026-03-23T10:10:00', '2026-03-23T10:10:00'),
('iw2-002', 18.00, 'contanti',  'cli-roberto',   'w2-002', 'Taglio uomo',          'servizio', '2026-03-23T10:05:00', '2026-03-23T10:05:00'),
('iw2-003', 80.00, 'carta',     'cli-valeria',   'w2-003', 'Meches caramello',     'servizio', '2026-03-23T12:15:00', '2026-03-23T12:15:00'),
('iw2-004', 22.00, 'satispay',  'cli-davide',    'w2-004', 'Taglio + styling',     'servizio', '2026-03-23T10:35:00', '2026-03-23T10:35:00'),
('iw2-005', 25.00, 'contanti',  'cli-martina',   'w2-005', 'Piega morbida',        'servizio', '2026-03-23T14:35:00', '2026-03-23T14:35:00'),
('iw2-006', 18.00, 'contanti',  'cli-giuseppe',  'w2-006', 'Taglio uomo',          'servizio', '2026-03-23T15:05:00', '2026-03-23T15:05:00'),
('iw2-007', 40.00, 'carta',     'cli-alessia',   'w2-007', 'Trattamento Olaplex',  'servizio', '2026-03-23T16:10:00', '2026-03-23T16:10:00');

-- -------------------------------------------------------
-- INCASSI STORICI MARZO (1-16 marzo) — per raggiungere ~€4.850
-- Mix realistico: contanti, carta, satispay
-- -------------------------------------------------------
INSERT OR REPLACE INTO incassi (id, importo, metodo_pagamento, cliente_id, descrizione, categoria, data_incasso, created_at) VALUES
-- Settimana 1-7 marzo (~€1.100)
('im-001', 65.00,  'carta',     'cli-anna',      'Colore + piega',                'servizio', '2026-03-01T10:00:00', '2026-03-01T10:00:00'),
('im-002', 18.00,  'contanti',  'cli-paolo',     'Taglio uomo',                   'servizio', '2026-03-01T10:30:00', '2026-03-01T10:30:00'),
('im-003', 85.00,  'carta',     'cli-chiara',    'Meches balayage',               'servizio', '2026-03-01T12:00:00', '2026-03-01T12:00:00'),
('im-004', 45.00,  'satispay',  'cli-francesca', 'Trattamento keratina',          'servizio', '2026-03-02T11:00:00', '2026-03-02T11:00:00'),
('im-005', 30.00,  'contanti',  'cli-matteo',    'Fade + barba',                  'servizio', '2026-03-02T10:00:00', '2026-03-02T10:00:00'),
('im-006', 75.00,  'carta',     'cli-sara',      'Colore biondo cenere',          'servizio', '2026-03-03T09:30:00', '2026-03-03T09:30:00'),
('im-007', 55.00,  'carta',     'cli-simona',    'Colore castano',                'servizio', '2026-03-03T14:00:00', '2026-03-03T14:00:00'),
('im-008', 25.00,  'contanti',  'cli-lucia',     'Piega volume',                  'servizio', '2026-03-04T09:00:00', '2026-03-04T09:00:00'),
('im-009', 18.00,  'contanti',  'cli-antonio',   'Taglio uomo',                   'servizio', '2026-03-04T10:00:00', '2026-03-04T10:00:00'),
('im-010', 95.00,  'carta',     'cli-valeria',   'Meches + trattamento',          'servizio', '2026-03-04T12:00:00', '2026-03-04T12:00:00'),
('im-011', 120.00, 'carta',     'cli-lucia',     'Look sposa prova',              'servizio', '2026-03-05T10:00:00', '2026-03-05T10:00:00'),
('im-012', 22.00,  'satispay',  'cli-davide',    'Taglio + styling',              'servizio', '2026-03-05T14:00:00', '2026-03-05T14:00:00'),
('im-013', 65.00,  'carta',     'cli-elena',     'Colore completo',               'servizio', '2026-03-06T09:00:00', '2026-03-06T09:00:00'),
('im-014', 18.00,  'contanti',  'cli-roberto',   'Taglio uomo',                   'servizio', '2026-03-06T10:00:00', '2026-03-06T10:00:00'),
('im-015', 40.00,  'carta',     'cli-alessia',   'Trattamento idratante',         'servizio', '2026-03-06T15:00:00', '2026-03-06T15:00:00'),
('im-016', 85.00,  'carta',     'cli-chiara',    'Meches platino',                'servizio', '2026-03-07T10:00:00', '2026-03-07T10:00:00'),
('im-017', 30.00,  'contanti',  'cli-andrea',    'Taglio + barba',                'servizio', '2026-03-07T11:00:00', '2026-03-07T11:00:00'),
('im-018', 25.00,  'satispay',  'cli-martina',   'Piega morbida',                 'servizio', '2026-03-07T14:00:00', '2026-03-07T14:00:00'),
-- Settimana 8-14 marzo (~€1.200)
('im-019', 75.00,  'carta',     'cli-sara',      'Colore + piega',                'servizio', '2026-03-08T09:00:00', '2026-03-08T09:00:00'),
('im-020', 18.00,  'contanti',  'cli-giuseppe',  'Taglio uomo',                   'servizio', '2026-03-08T10:00:00', '2026-03-08T10:00:00'),
('im-021', 55.00,  'carta',     'cli-anna',      'Colore copertura bianchi',      'servizio', '2026-03-08T11:00:00', '2026-03-08T11:00:00'),
('im-022', 85.00,  'carta',     'cli-elena',     'Balayage rame',                 'servizio', '2026-03-09T09:00:00', '2026-03-09T09:00:00'),
('im-023', 30.00,  'contanti',  'cli-matteo',    'Fade + design',                 'servizio', '2026-03-09T10:30:00', '2026-03-09T10:30:00'),
('im-024', 45.00,  'carta',     'cli-francesca', 'Trattamento lisciante',         'servizio', '2026-03-10T10:00:00', '2026-03-10T10:00:00'),
('im-025', 65.00,  'carta',     'cli-simona',    'Colore + trattamento',          'servizio', '2026-03-10T14:00:00', '2026-03-10T14:00:00'),
('im-026', 18.00,  'contanti',  'cli-paolo',     'Taglio uomo',                   'servizio', '2026-03-10T09:30:00', '2026-03-10T09:30:00'),
('im-027', 95.00,  'carta',     'cli-valeria',   'Meches biondo naturale',        'servizio', '2026-03-11T10:00:00', '2026-03-11T10:00:00'),
('im-028', 25.00,  'satispay',  'cli-lucia',     'Piega liscia',                  'servizio', '2026-03-11T14:00:00', '2026-03-11T14:00:00'),
('im-029', 22.00,  'contanti',  'cli-davide',    'Taglio businessman',            'servizio', '2026-03-11T15:00:00', '2026-03-11T15:00:00'),
('im-030', 12.00,  'contanti',  'cli-andrea',    'Barba',                         'servizio', '2026-03-12T09:00:00', '2026-03-12T09:00:00'),
('im-031', 80.00,  'carta',     'cli-chiara',    'Meches caramello',              'servizio', '2026-03-12T10:30:00', '2026-03-12T10:30:00'),
('im-032', 55.00,  'carta',     'cli-alessia',   'Colore ramato',                 'servizio', '2026-03-12T14:00:00', '2026-03-12T14:00:00'),
('im-033', 35.00,  'carta',     'cli-martina',   'Piega + trattamento',           'servizio', '2026-03-13T10:00:00', '2026-03-13T10:00:00'),
('im-034', 18.00,  'contanti',  'cli-antonio',   'Taglio uomo',                   'servizio', '2026-03-13T11:00:00', '2026-03-13T11:00:00'),
('im-035', 120.00, 'carta',     'cli-lucia',     'Prova acconciatura sposa',      'servizio', '2026-03-13T14:00:00', '2026-03-13T14:00:00'),
('im-036', 18.00,  'contanti',  'cli-marco',     'Taglio uomo',                   'servizio', '2026-03-14T09:00:00', '2026-03-14T09:00:00'),
('im-037', 65.00,  'carta',     'cli-anna',      'Colore + piega evento',         'servizio', '2026-03-14T10:00:00', '2026-03-14T10:00:00'),
('im-038', 30.00,  'satispay',  'cli-matteo',    'Fade + barba',                  'servizio', '2026-03-14T11:00:00', '2026-03-14T11:00:00'),
-- Settimana 15-16 marzo (~€400)
('im-039', 75.00,  'carta',     'cli-sara',      'Ritocco biondo cenere',         'servizio', '2026-03-15T09:00:00', '2026-03-15T09:00:00'),
('im-040', 85.00,  'carta',     'cli-elena',     'Meches primavera',              'servizio', '2026-03-15T10:30:00', '2026-03-15T10:30:00'),
('im-041', 18.00,  'contanti',  'cli-roberto',   'Taglio uomo',                   'servizio', '2026-03-15T14:00:00', '2026-03-15T14:00:00'),
('im-042', 45.00,  'satispay',  'cli-francesca', 'Trattamento anti-crespo',       'servizio', '2026-03-16T10:00:00', '2026-03-16T10:00:00'),
('im-043', 55.00,  'carta',     'cli-simona',    'Colore castano dorato',         'servizio', '2026-03-16T14:00:00', '2026-03-16T14:00:00'),
('im-044', 22.00,  'contanti',  'cli-giovanni',  'Taglio + styling',              'servizio', '2026-03-16T15:00:00', '2026-03-16T15:00:00'),
-- Vendita pacchetti (marzo)
('im-045', 99.00,  'carta',     'cli-chiara',    'Pacchetto Beauty Plus',         'pacchetto', '2026-03-05T12:00:00', '2026-03-05T12:00:00'),
('im-046', 55.00,  'satispay',  'cli-andrea',    'Pacchetto Barba Pro',           'pacchetto', '2026-03-10T10:00:00', '2026-03-10T10:00:00'),
('im-047', 175.00, 'carta',     'cli-lucia',     'Pacchetto Sposa da Sogno',      'pacchetto', '2026-03-13T15:00:00', '2026-03-13T15:00:00');

-- -------------------------------------------------------
-- CLIENTI_PACCHETTI — pacchetti venduti a clienti
-- -------------------------------------------------------
INSERT OR REPLACE INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato, note) VALUES
('cp-001', 'cli-chiara',  'pck-beauty-plus', 'attivo', 1, 4, '2026-03-04', '2026-03-05', '2027-03-05', 'carta', 1, 'Ha gia usato 1 colore. Prossimo: piega.'),
('cp-002', 'cli-andrea',  'pck-barba-pro',   'attivo', 2, 5, '2026-03-09', '2026-03-10', '2027-03-10', 'satispay', 1, 'Viene ogni 2 settimane per barba.'),
('cp-003', 'cli-lucia',   'pck-sposa',       'attivo', 2, 5, '2026-03-12', '2026-03-13', '2026-09-13', 'carta', 1, 'Matrimonio luglio. 2 prove fatte, prossima aprile.'),
('cp-004', 'cli-sara',    'pck-meches-vip',  'attivo', 1, 8, '2026-02-20', '2026-02-22', '2027-02-22', 'carta', 1, 'VIP annuale. Prima meches fatta a marzo.'),
('cp-005', 'cli-anna',    'pkg_vip_monthly',  'attivo', 3, 4, '2026-03-01', '2026-03-01', '2026-04-01', 'carta', 1, 'Abbonamento mensile. 3/4 servizi usati.');

PRAGMA foreign_keys = ON;
