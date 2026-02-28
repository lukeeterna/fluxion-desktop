-- =======================================================
-- FLUXION — Seed Data Credibili (Salone Parrucchiera)
-- Schema-verified 2026-02-28
-- =======================================================

PRAGMA foreign_keys = OFF;

-- -------------------------------------------------------
-- CLIENTI — 20 clienti italiani credibili
-- Schema: id, nome, cognome, email, telefono, note, tags(JSON),
--         fonte, is_vip, soprannome, loyalty_visits, consenso_*
-- -------------------------------------------------------
INSERT OR IGNORE INTO clienti (id, nome, cognome, telefono, email, note, tags, fonte, is_vip, soprannome, loyalty_visits, consenso_marketing, consenso_whatsapp, created_at, updated_at) VALUES
('cli-anna',      'Anna',      'Ferrari',    '3471234567', 'anna.ferrari@email.it',    'Cliente storica, preferisce Giulia', '["vip","fedele"]',   'passaparola', 1, 'Annina', 28, 1, 1, '2024-01-15 09:00:00', '2026-02-20 14:30:00'),
('cli-paolo',     'Paolo',     'Rossi',      '3389876543', 'p.rossi@libero.it',         'Taglio classico ogni 3 settimane', '[]',                  'passaparola', 0, NULL,     12, 1, 0, '2024-03-10 11:00:00', '2026-02-18 10:00:00'),
('cli-sara',      'Sara',      'Colombo',    '3661112233', 'sara.colombo@gmail.com',    'VIP — colore biondo cenere Wella', '["vip","colore"]',   'instagram',   1, 'Saretta', 42, 1, 1, '2023-11-05 15:00:00', '2026-02-25 16:00:00'),
('cli-marco',     'Marco',     'Bianchi',    '3334455667', 'm.bianchi@hotmail.it',      'Allergia fragranze forti', '[]',                          'passaparola', 0, NULL,     8,  1, 0, '2024-06-20 10:30:00', '2026-02-10 09:00:00'),
('cli-elena',     'Elena',     'Ricci',      '3481234321', 'elena.ricci@icloud.com',    'Colore ogni 6 settimane, meches', '["vip","meches"]',   'passaparola', 1, 'Ele',     35, 1, 1, '2023-09-12 14:00:00', '2026-02-22 11:30:00'),
('cli-giuseppe',  'Giuseppe',  'Marino',     '3205556789', 'g.marino@email.it',         'Pensionato, mattine libere', '[]',                         'walk-in',     0, 'Peppe',  19, 0, 0, '2024-02-08 09:30:00', '2026-02-17 10:00:00'),
('cli-francesca', 'Francesca', 'Conti',      '3476543210', 'francy.conti@gmail.com',    'Trattamento cheratina mensile', '["vip","keratina"]',  'instagram',   1, 'Francy',  31, 1, 1, '2023-12-01 16:00:00', '2026-02-24 15:00:00'),
('cli-andrea',    'Andrea',    'Romano',     '3351239876', 'andrea.romano@outlook.it',  'Barba settimanale + taglio mensile', '["barba"]',         'passaparola', 0, NULL,     16, 1, 1, '2024-04-15 11:00:00', '2026-02-19 09:30:00'),
('cli-lucia',     'Lucia',     'Gallo',      '3487654321', 'lucia.gallo@email.it',      'Sposa maggio 2026 — look wedding', '["vip","sposa"]',   'passaparola', 1, 'Lucy',    22, 1, 1, '2024-07-03 14:30:00', '2026-02-26 17:00:00'),
('cli-roberto',   'Roberto',   'Costa',      '3281234500', 'r.costa@libero.it',         'Capelli fini, prodotti volumizzanti', '[]',               'walk-in',     0, NULL,     6,  1, 0, '2025-01-20 10:00:00', '2026-02-14 10:00:00'),
('cli-chiara',    'Chiara',    'Esposito',   '3661234567', 'chiara.expo@gmail.com',     'VIP — abbonamento pacchetto Beauty Plus', '["vip","fedele"]', 'instagram', 1, 'Chia',  48, 1, 1, '2023-06-15 09:00:00', '2026-02-27 13:00:00'),
('cli-matteo',    'Matteo',    'Lombardi',   '3339988776', 'matteo.lmb@email.it',       'Fade + barba, studente universitario', '["barba"]',       'instagram',   0, NULL,     9,  1, 1, '2025-03-10 16:00:00', '2026-02-21 12:00:00'),
('cli-valeria',   'Valeria',   'Barbieri',   '3477654321', 'v.barbieri@icloud.com',     'Colorazione ogni 2 mesi, riflessi dorati', '["colore"]',  'passaparola', 0, NULL,     14, 1, 0, '2024-09-05 11:30:00', '2026-02-16 14:00:00'),
('cli-antonio',   'Antonio',   'Fontana',    '3205432167', 'antonio.f@hotmail.it',      'Titolare Bar Roma, ogni 2 settimane', '["fedele"]',       'passaparola', 0, NULL,     24, 1, 0, '2024-01-30 09:00:00', '2026-02-23 09:00:00'),
('cli-simona',    'Simona',    'Moretti',    '3481234123', 'simona.moretti@email.it',   'Trattamento anti-crespo, capelli ricci', '["vip"]',       'instagram',   1, 'Simo',   18, 1, 1, '2024-08-12 15:00:00', '2026-02-20 16:00:00'),
('cli-luca-p',    'Luca',      'Pellegrino', '3355432198', 'luca.pelleg@gmail.com',     'Frequenta la palestra di fianco', '[]',                  'walk-in',     0, NULL,     5,  1, 1, '2025-05-20 17:00:00', '2026-02-13 11:00:00'),
('cli-martina',   'Martina',   'Leone',      '3471122334', 'martina.leone@email.it',    'Mamma, preferisce sabato pomeriggio', '[]',               'passaparola', 0, NULL,     11, 1, 1, '2024-11-10 10:00:00', '2026-02-15 14:30:00'),
('cli-davide',    'Davide',    'Ferarri',    '3289876123', 'davide.f@libero.it',         'Imprenditore, look curato', '[]',                        'instagram',   0, NULL,     7,  1, 0, '2025-02-14 12:00:00', '2026-02-12 12:00:00'),
('cli-alessia',   'Alessia',   'Gentile',    '3667788990', 'alessia.g@gmail.com',       'Tinta castano cioccolato, regolare', '["colore"]',       'passaparola', 0, NULL,     13, 1, 1, '2024-10-08 14:00:00', '2026-02-11 09:00:00'),
('cli-giovanni',  'Giovanni',  'Marini',     '3341122334', 'giovanni.m@email.it',       'Anziano, capelli bianchi, taglio classico', '["fedele"]', 'walk-in',    0, 'Nonno Gianni', 32, 0, 0, '2023-07-20 09:00:00', '2026-02-28 09:30:00');

-- -------------------------------------------------------
-- OPERATORI aggiuntivi
-- -------------------------------------------------------
INSERT OR IGNORE INTO operatori (id, nome, colore, attivo, created_at) VALUES
('op-paola', 'Paola', '#F59E0B', 1, '2024-01-01 00:00:00'),
('op-laura', 'Laura', '#EC4899', 1, '2024-06-01 00:00:00');

-- -------------------------------------------------------
-- APPUNTAMENTI — Feb/Mar 2026
-- Schema: id, cliente_id, servizio_id, operatore_id,
--         data_ora_inizio, data_ora_fine, durata_minuti,
--         stato, prezzo, prezzo_finale, note, fonte_prenotazione
-- -------------------------------------------------------
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 16 Feb
('app-001', 'cli-anna',      'srv-colore',       'op-giulia', '2026-02-16T09:00:00', '2026-02-16T10:00:00', 60, 'completato', 45.00, 65.00, 'Ritocco radici + piega', 'whatsapp'),
('app-002', 'cli-paolo',     'srv-taglio-uomo',  'op-marco',  '2026-02-16T09:30:00', '2026-02-16T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-003', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-02-16T10:00:00', '2026-02-16T10:30:00', 30, 'completato', 18.00, 30.00, 'Fade laterale + barba', 'whatsapp'),
('app-004', 'cli-elena',     'srv-meches',       'op-giulia', '2026-02-16T10:30:00', '2026-02-16T12:00:00', 90, 'completato', 65.00, 85.00, 'Meches balayage + piega', 'manuale'),
('app-005', 'cli-giuseppe',  'srv-taglio-uomo',  'op-marco',  '2026-02-16T11:00:00', '2026-02-16T11:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-006', 'cli-chiara',    'srv-trattamento',  'op-laura',  '2026-02-16T14:00:00', '2026-02-16T15:00:00', 60, 'completato', 30.00, 45.00, 'Trattamento keratina', 'whatsapp'),
('app-007', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-02-16T14:30:00', '2026-02-16T15:00:00', 20, 'completato', 12.00, 12.00, 'Rifintura barba lunga', 'walk-in'),
('app-008', 'cli-lucia',     'srv-piega',        'op-paola',  '2026-02-16T15:00:00', '2026-02-16T15:30:00', 30, 'completato', 20.00, 30.00, 'Prova acconciatura sposa', 'telefono'),
-- Martedì 17 Feb
('app-009', 'cli-francesca', 'srv-colore',       'op-giulia', '2026-02-17T09:00:00', '2026-02-17T10:00:00', 60, 'completato', 45.00, 45.00, 'Tinta castano scuro', 'whatsapp'),
('app-010', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-02-17T09:30:00', '2026-02-17T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-011', 'cli-simona',    'srv-trattamento',  'op-paola',  '2026-02-17T10:00:00', '2026-02-17T11:00:00', 60, 'completato', 30.00, 35.00, 'Maschera anti-crespo intensiva', 'manuale'),
('app-012', 'cli-valeria',   'srv-meches',       'op-giulia', '2026-02-17T11:00:00', '2026-02-17T12:30:00', 90, 'completato', 65.00, 75.00, 'Riflessi dorati schiarenti', 'whatsapp'),
('app-013', 'cli-roberto',   'srv-taglio-uomo',  'op-luca',   '2026-02-17T14:00:00', '2026-02-17T14:30:00', 30, 'completato', 18.00, 18.00, 'Taglio scalato capelli fini', 'walk-in'),
('app-014', 'cli-davide',    'srv-taglio-uomo',  'op-marco',  '2026-02-17T15:00:00', '2026-02-17T15:30:00', 30, 'completato', 18.00, 20.00, 'Taglio businessman', 'manuale'),
-- Mercoledì 18 Feb
('app-015', 'cli-alessia',   'srv-colore',       'op-giulia', '2026-02-18T09:00:00', '2026-02-18T10:00:00', 60, 'completato', 45.00, 55.00, 'Tinta + piega', 'telefono'),
('app-016', 'cli-giovanni',  'srv-taglio-uomo',  'op-marco',  '2026-02-18T09:30:00', '2026-02-18T10:00:00', 30, 'completato', 18.00, 18.00, 'Taglio classico + sfumatura', 'telefono'),
('app-017', 'cli-martina',   'srv-piega',        'op-laura',  '2026-02-18T10:00:00', '2026-02-18T10:30:00', 30, 'completato', 20.00, 25.00, 'Piega con volume', 'whatsapp'),
('app-018', 'cli-anna',      'srv-piega',        'op-giulia', '2026-02-18T11:00:00', '2026-02-18T11:30:00', 30, 'completato', 20.00, 25.00, 'Piega in-between', 'whatsapp'),
('app-019', 'cli-luca-p',    'srv-taglio-uomo',  'op-luca',   '2026-02-18T14:00:00', '2026-02-18T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),
('app-020', 'cli-chiara',    'srv-piega',        'op-paola',  '2026-02-18T15:00:00', '2026-02-18T15:30:00', 30, 'completato', 20.00, 25.00, NULL, 'manuale'),
-- Giovedì 19 Feb
('app-021', 'cli-sara',      'srv-colore',       'op-giulia', '2026-02-19T09:00:00', '2026-02-19T10:30:00', 90, 'completato', 45.00, 75.00, 'Biondo cenere Wella 12.1 + piega', 'whatsapp'),
('app-022', 'cli-marco',     'srv-taglio-uomo',  'op-luca',   '2026-02-19T10:00:00', '2026-02-19T10:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-023', 'cli-elena',     'srv-trattamento',  'op-paola',  '2026-02-19T10:30:00', '2026-02-19T11:30:00', 60, 'completato', 30.00, 35.00, 'Trattamento idratante intensivo', 'manuale'),
('app-024', 'cli-andrea',    'srv-barba',        'op-marco',  '2026-02-19T14:00:00', '2026-02-19T14:20:00', 20, 'completato', 12.00, 12.00, NULL, 'whatsapp'),
('app-025', 'cli-francesca', 'srv-piega',        'op-laura',  '2026-02-19T15:00:00', '2026-02-19T15:30:00', 30, 'completato', 20.00, 25.00, 'Piega liscia effetto seta', 'manuale'),
-- Venerdì 20 Feb
('app-026', 'cli-lucia',     'srv-meches',       'op-giulia', '2026-02-20T09:00:00', '2026-02-20T11:00:00', 120,'completato', 65.00, 85.00, 'Prova colore matrimonio — meches sabbia', 'telefono'),
('app-027', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-02-20T10:00:00', '2026-02-20T10:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-028', 'cli-simona',    'srv-colore',       'op-paola',  '2026-02-20T10:30:00', '2026-02-20T11:30:00', 60, 'completato', 45.00, 50.00, 'Castano ramato caldo', 'whatsapp'),
('app-029', 'cli-chiara',    'srv-meches',       'op-giulia', '2026-02-20T14:00:00', '2026-02-20T15:30:00', 90, 'completato', 65.00, 95.00, 'Balayage + piega blow-dry', 'manuale'),
('app-030', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-02-20T14:30:00', '2026-02-20T15:00:00', 30, 'completato', 18.00, 18.00, NULL, 'whatsapp'),
-- Sabato 21 Feb (piena)
('app-031', 'cli-anna',      'srv-colore',       'op-giulia', '2026-02-21T09:00:00', '2026-02-21T10:00:00', 60, 'completato', 45.00, 60.00, 'Ritocco + trattamento', 'whatsapp'),
('app-032', 'cli-paolo',     'srv-taglio-uomo',  'op-marco',  '2026-02-21T09:00:00', '2026-02-21T09:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-033', 'cli-martina',   'srv-taglio-donna', 'op-laura',  '2026-02-21T09:00:00', '2026-02-21T09:45:00', 45, 'completato', 35.00, 40.00, 'Taglio con scalatura', 'manuale'),
('app-034', 'cli-valeria',   'srv-piega',        'op-paola',  '2026-02-21T10:00:00', '2026-02-21T10:30:00', 30, 'completato', 20.00, 25.00, NULL, 'whatsapp'),
('app-035', 'cli-davide',    'srv-taglio-uomo',  'op-marco',  '2026-02-21T10:00:00', '2026-02-21T10:30:00', 30, 'completato', 18.00, 20.00, NULL, 'manuale'),
('app-036', 'cli-elena',     'srv-piega',        'op-giulia', '2026-02-21T10:30:00', '2026-02-21T11:00:00', 30, 'completato', 20.00, 25.00, 'Piega morbida', 'whatsapp'),
('app-037', 'cli-alessia',   'srv-colore',       'op-paola',  '2026-02-21T11:00:00', '2026-02-21T12:00:00', 60, 'completato', 45.00, 50.00, 'Tinta cioccolato', 'manuale'),
('app-038', 'cli-giovanni',  'srv-taglio-uomo',  'op-marco',  '2026-02-21T11:00:00', '2026-02-21T11:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-039', 'cli-roberto',   'srv-taglio-uomo',  'op-luca',   '2026-02-21T14:00:00', '2026-02-21T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),
('app-040', 'cli-sara',      'srv-piega',        'op-giulia', '2026-02-21T14:30:00', '2026-02-21T15:00:00', 30, 'completato', 20.00, 25.00, 'Piega per cena', 'whatsapp'),
('app-041', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-02-21T15:00:00', '2026-02-21T15:20:00', 20, 'completato', 12.00, 12.00, NULL, 'whatsapp'),
-- Lunedì 23 Feb
('app-042', 'cli-chiara',    'srv-trattamento',  'op-giulia', '2026-02-23T09:00:00', '2026-02-23T10:00:00', 60, 'completato', 30.00, 40.00, 'Trattamento ristrutturante mensile', 'manuale'),
('app-043', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-02-23T09:30:00', '2026-02-23T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-044', 'cli-francesca', 'srv-trattamento',  'op-paola',  '2026-02-23T10:00:00', '2026-02-23T11:30:00', 90, 'completato', 30.00, 65.00, 'Cheratina lisciante professionale', 'manuale'),
('app-045', 'cli-marco',     'srv-taglio-uomo',  'op-luca',   '2026-02-23T14:00:00', '2026-02-23T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
-- Mar 24 Feb
('app-046', 'cli-simona',    'srv-colore',       'op-giulia', '2026-02-24T10:00:00', '2026-02-24T11:00:00', 60, 'completato', 45.00, 55.00, 'Ritocco + piega', 'whatsapp'),
('app-047', 'cli-lucia',     'srv-taglio-donna', 'op-laura',  '2026-02-24T11:00:00', '2026-02-24T11:45:00', 45, 'completato', 35.00, 38.00, 'Taglio spalla con scalatura leggera', 'telefono'),
('app-048', 'cli-giovanni',  'srv-taglio-uomo',  'op-marco',  '2026-02-24T14:00:00', '2026-02-24T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
-- Mer 25 Feb
('app-049', 'cli-anna',      'srv-colore',       'op-giulia', '2026-02-25T09:00:00', '2026-02-25T10:30:00', 90, 'completato', 45.00, 80.00, 'Colore completo + meches mento', 'whatsapp'),
('app-050', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-02-25T10:00:00', '2026-02-25T10:30:00', 30, 'completato', 18.00, 30.00, 'Fade + barba', 'whatsapp'),
('app-051', 'cli-chiara',    'srv-piega',        'op-paola',  '2026-02-25T14:00:00', '2026-02-25T14:30:00', 30, 'completato', 20.00, 25.00, NULL, 'manuale'),
-- Gio 26 Feb
('app-052', 'cli-sara',      'srv-trattamento',  'op-giulia', '2026-02-26T09:00:00', '2026-02-26T10:00:00', 60, 'completato', 30.00, 40.00, 'Trattamento luminosità', 'manuale'),
('app-053', 'cli-valeria',   'srv-colore',       'op-laura',  '2026-02-26T10:00:00', '2026-02-26T11:00:00', 60, 'completato', 45.00, 55.00, 'Riflessi rame + piega', 'whatsapp'),
('app-054', 'cli-andrea',    'srv-barba',        'op-marco',  '2026-02-26T11:00:00', '2026-02-26T11:20:00', 20, 'completato', 12.00, 12.00, NULL, 'whatsapp'),
('app-055', 'cli-roberto',   'srv-taglio-uomo',  'op-luca',   '2026-02-26T14:00:00', '2026-02-26T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),
-- Ven 27 Feb
('app-056', 'cli-elena',     'srv-meches',       'op-giulia', '2026-02-27T09:00:00', '2026-02-27T11:00:00', 120,'completato', 65.00, 90.00, 'Balayage completo', 'manuale'),
('app-057', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-02-27T09:30:00', '2026-02-27T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('app-058', 'cli-francesca', 'srv-piega',        'op-paola',  '2026-02-27T10:00:00', '2026-02-27T10:30:00', 30, 'completato', 20.00, 28.00, 'Piega evento cena aziendale', 'manuale'),
-- Sab 28 Feb (oggi)
('app-059', 'cli-davide',    'srv-taglio-uomo',  'op-marco',  '2026-02-28T09:00:00', '2026-02-28T09:30:00', 30, 'completato', 18.00, 20.00, NULL, 'manuale'),
('app-060', 'cli-anna',      'srv-piega',        'op-giulia', '2026-02-28T09:30:00', '2026-02-28T10:00:00', 30, 'confermato', 20.00, 25.00, 'Piega prima evento', 'whatsapp'),
('app-061', 'cli-chiara',    'srv-colore',       'op-laura',  '2026-02-28T10:00:00', '2026-02-28T11:00:00', 60, 'confermato', 45.00, 55.00, 'Ritocco + piega', 'manuale'),
('app-062', 'cli-giovanni',  'srv-taglio-uomo',  'op-marco',  '2026-02-28T10:30:00', '2026-02-28T11:00:00', 30, 'confermato', 18.00, 18.00, NULL, 'telefono'),
('app-063', 'cli-lucia',     'srv-piega',        'op-paola',  '2026-02-28T14:00:00', '2026-02-28T14:30:00', 30, 'confermato', 20.00, 35.00, 'Prova acconciatura matrimonio', 'telefono'),
('app-064', 'cli-sara',      'srv-meches',       'op-giulia', '2026-02-28T14:30:00', '2026-02-28T16:00:00', 90, 'confermato', 65.00, 75.00, 'Ritocco biondo cenere', 'whatsapp'),
-- Marzo (futuri)
('app-065', 'cli-marco',     'srv-taglio-uomo',  'op-luca',   '2026-03-02T09:00:00', '2026-03-02T09:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'whatsapp'),
('app-066', 'cli-simona',    'srv-trattamento',  'op-paola',  '2026-03-02T10:00:00', '2026-03-02T11:00:00', 60, 'confermato', 30.00, 35.00, 'Mensile anti-crespo', 'manuale'),
('app-067', 'cli-elena',     'srv-colore',       'op-giulia', '2026-03-03T09:00:00', '2026-03-03T10:30:00', 90, 'confermato', 45.00, 80.00, 'Radici + meches', 'manuale'),
('app-068', 'cli-andrea',    'srv-barba',        'op-marco',  '2026-03-03T10:00:00', '2026-03-03T10:20:00', 20, 'confermato', 12.00, 12.00, NULL, 'whatsapp'),
('app-069', 'cli-lucia',     'srv-taglio-donna', 'op-giulia', '2026-03-07T09:00:00', '2026-03-07T10:00:00', 60, 'confermato', 35.00, 45.00, 'Taglio pre-matrimonio', 'telefono'),
('app-070', 'cli-chiara',    'srv-trattamento',  'op-laura',  '2026-03-07T10:00:00', '2026-03-07T11:00:00', 60, 'confermato', 30.00, 40.00, 'Trattamento mensile', 'manuale');

-- -------------------------------------------------------
-- INCASSI — 55+ transazioni Feb 2026
-- Schema: id, importo, metodo_pagamento, cliente_id,
--         appuntamento_id, descrizione, categoria, operatore_id, data_incasso
-- -------------------------------------------------------
INSERT OR IGNORE INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, descrizione, categoria, operatore_id, data_incasso) VALUES
('inc-001', 65.00, 'carta',     'cli-anna',      'app-001', 'Colore + piega 16/02',         'servizio', 'op-giulia', '2026-02-16T10:05:00'),
('inc-002', 18.00, 'contanti',  'cli-paolo',     'app-002', 'Taglio 16/02',                 'servizio', 'op-marco',  '2026-02-16T10:05:00'),
('inc-003', 30.00, 'contanti',  'cli-matteo',    'app-003', 'Taglio fade + barba 16/02',    'servizio', 'op-luca',   '2026-02-16T10:35:00'),
('inc-004', 85.00, 'carta',     'cli-elena',     'app-004', 'Meches balayage 16/02',        'servizio', 'op-giulia', '2026-02-16T12:05:00'),
('inc-005', 18.00, 'contanti',  'cli-giuseppe',  'app-005', 'Taglio 16/02',                 'servizio', 'op-marco',  '2026-02-16T11:35:00'),
('inc-006', 45.00, 'satispay',  'cli-chiara',    'app-006', 'Keratina 16/02',               'servizio', 'op-laura',  '2026-02-16T15:05:00'),
('inc-007', 12.00, 'contanti',  'cli-andrea',    'app-007', 'Barba 16/02',                  'servizio', 'op-luca',   '2026-02-16T15:05:00'),
('inc-008', 30.00, 'satispay',  'cli-lucia',     'app-008', 'Prova sposa 16/02',            'servizio', 'op-paola',  '2026-02-16T15:35:00'),
('inc-009', 45.00, 'carta',     'cli-francesca', 'app-009', 'Tinta 17/02',                  'servizio', 'op-giulia', '2026-02-17T10:05:00'),
('inc-010', 18.00, 'contanti',  'cli-antonio',   'app-010', 'Taglio 17/02',                 'servizio', 'op-marco',  '2026-02-17T10:05:00'),
('inc-011', 35.00, 'satispay',  'cli-simona',    'app-011', 'Maschera anti-crespo 17/02',   'servizio', 'op-paola',  '2026-02-17T11:05:00'),
('inc-012', 75.00, 'carta',     'cli-valeria',   'app-012', 'Meches dorati 17/02',          'servizio', 'op-giulia', '2026-02-17T12:35:00'),
('inc-013', 18.00, 'contanti',  'cli-roberto',   'app-013', 'Taglio 17/02',                 'servizio', 'op-luca',   '2026-02-17T14:35:00'),
('inc-014', 20.00, 'satispay',  'cli-davide',    'app-014', 'Taglio businessman 17/02',     'servizio', 'op-marco',  '2026-02-17T15:35:00'),
('inc-015', 55.00, 'carta',     'cli-alessia',   'app-015', 'Tinta + piega 18/02',          'servizio', 'op-giulia', '2026-02-18T10:05:00'),
('inc-016', 18.00, 'contanti',  'cli-giovanni',  'app-016', 'Taglio classico 18/02',        'servizio', 'op-marco',  '2026-02-18T10:05:00'),
('inc-017', 25.00, 'satispay',  'cli-martina',   'app-017', 'Piega 18/02',                  'servizio', 'op-laura',  '2026-02-18T10:35:00'),
('inc-018', 25.00, 'satispay',  'cli-anna',      'app-018', 'Piega in-between 18/02',       'servizio', 'op-giulia', '2026-02-18T11:35:00'),
('inc-019', 18.00, 'contanti',  'cli-luca-p',    'app-019', 'Taglio 18/02',                 'servizio', 'op-luca',   '2026-02-18T14:35:00'),
('inc-020', 25.00, 'carta',     'cli-chiara',    'app-020', 'Piega 18/02',                  'servizio', 'op-paola',  '2026-02-18T15:35:00'),
('inc-021', 75.00, 'carta',     'cli-sara',      'app-021', 'Biondo cenere + piega 19/02',  'servizio', 'op-giulia', '2026-02-19T10:35:00'),
('inc-022', 18.00, 'contanti',  'cli-marco',     'app-022', 'Taglio 19/02',                 'servizio', 'op-luca',   '2026-02-19T10:35:00'),
('inc-023', 35.00, 'satispay',  'cli-elena',     'app-023', 'Trattamento idratante 19/02',  'servizio', 'op-paola',  '2026-02-19T11:35:00'),
('inc-024', 12.00, 'contanti',  'cli-andrea',    'app-024', 'Barba 19/02',                  'servizio', 'op-marco',  '2026-02-19T14:25:00'),
('inc-025', 25.00, 'satispay',  'cli-francesca', 'app-025', 'Piega liscia 19/02',           'servizio', 'op-laura',  '2026-02-19T15:35:00'),
('inc-026', 85.00, 'carta',     'cli-lucia',     'app-026', 'Meches sposa 20/02',           'servizio', 'op-giulia', '2026-02-20T11:05:00'),
('inc-027', 18.00, 'contanti',  'cli-antonio',   'app-027', 'Taglio 20/02',                 'servizio', 'op-marco',  '2026-02-20T10:35:00'),
('inc-028', 50.00, 'satispay',  'cli-simona',    'app-028', 'Castano ramato 20/02',         'servizio', 'op-paola',  '2026-02-20T11:35:00'),
('inc-029', 95.00, 'carta',     'cli-chiara',    'app-029', 'Balayage + blow-dry 20/02',    'servizio', 'op-giulia', '2026-02-20T15:35:00'),
('inc-030', 18.00, 'contanti',  'cli-matteo',    'app-030', 'Taglio 20/02',                 'servizio', 'op-luca',   '2026-02-20T15:05:00'),
('inc-031', 60.00, 'carta',     'cli-anna',      'app-031', 'Colore + trattamento 21/02',   'servizio', 'op-giulia', '2026-02-21T10:05:00'),
('inc-032', 18.00, 'contanti',  'cli-paolo',     'app-032', 'Taglio 21/02',                 'servizio', 'op-marco',  '2026-02-21T09:35:00'),
('inc-033', 40.00, 'satispay',  'cli-martina',   'app-033', 'Taglio scalato 21/02',         'servizio', 'op-laura',  '2026-02-21T09:50:00'),
('inc-034', 25.00, 'carta',     'cli-valeria',   'app-034', 'Piega 21/02',                  'servizio', 'op-paola',  '2026-02-21T10:35:00'),
('inc-035', 20.00, 'satispay',  'cli-davide',    'app-035', 'Taglio businessman 21/02',     'servizio', 'op-marco',  '2026-02-21T10:35:00'),
('inc-036', 25.00, 'satispay',  'cli-elena',     'app-036', 'Piega morbida 21/02',          'servizio', 'op-giulia', '2026-02-21T11:05:00'),
('inc-037', 50.00, 'carta',     'cli-alessia',   'app-037', 'Tinta cioccolato 21/02',       'servizio', 'op-paola',  '2026-02-21T12:05:00'),
('inc-038', 18.00, 'contanti',  'cli-giovanni',  'app-038', 'Taglio 21/02',                 'servizio', 'op-marco',  '2026-02-21T11:35:00'),
('inc-039', 18.00, 'contanti',  'cli-roberto',   'app-039', 'Taglio walk-in 21/02',         'servizio', 'op-luca',   '2026-02-21T14:35:00'),
('inc-040', 25.00, 'carta',     'cli-sara',      'app-040', 'Piega per cena 21/02',         'servizio', 'op-giulia', '2026-02-21T15:05:00'),
('inc-041', 12.00, 'satispay',  'cli-andrea',    'app-041', 'Barba 21/02',                  'servizio', 'op-luca',   '2026-02-21T15:25:00'),
('inc-042', 40.00, 'carta',     'cli-chiara',    'app-042', 'Trattamento mensile 23/02',    'servizio', 'op-giulia', '2026-02-23T10:05:00'),
('inc-043', 18.00, 'contanti',  'cli-antonio',   'app-043', 'Taglio 23/02',                 'servizio', 'op-marco',  '2026-02-23T10:05:00'),
('inc-044', 65.00, 'carta',     'cli-francesca', 'app-044', 'Cheratina 23/02',              'servizio', 'op-paola',  '2026-02-23T11:35:00'),
('inc-045', 18.00, 'contanti',  'cli-marco',     'app-045', 'Taglio 23/02',                 'servizio', 'op-luca',   '2026-02-23T14:35:00'),
('inc-046', 55.00, 'satispay',  'cli-simona',    'app-046', 'Ritocco + piega 24/02',        'servizio', 'op-giulia', '2026-02-24T11:05:00'),
('inc-047', 38.00, 'carta',     'cli-lucia',     'app-047', 'Taglio spalla 24/02',          'servizio', 'op-laura',  '2026-02-24T11:50:00'),
('inc-048', 18.00, 'contanti',  'cli-giovanni',  'app-048', 'Taglio 24/02',                 'servizio', 'op-marco',  '2026-02-24T14:35:00'),
('inc-049', 80.00, 'carta',     'cli-anna',      'app-049', 'Colore + meches 25/02',        'servizio', 'op-giulia', '2026-02-25T10:35:00'),
('inc-050', 30.00, 'satispay',  'cli-matteo',    'app-050', 'Fade + barba 25/02',           'servizio', 'op-luca',   '2026-02-25T10:35:00'),
('inc-051', 25.00, 'satispay',  'cli-chiara',    'app-051', 'Piega 25/02',                  'servizio', 'op-paola',  '2026-02-25T14:35:00'),
('inc-052', 40.00, 'carta',     'cli-sara',      'app-052', 'Trattamento luminosità 26/02', 'servizio', 'op-giulia', '2026-02-26T10:05:00'),
('inc-053', 55.00, 'satispay',  'cli-valeria',   'app-053', 'Riflessi rame 26/02',          'servizio', 'op-laura',  '2026-02-26T11:05:00'),
('inc-054', 12.00, 'contanti',  'cli-andrea',    'app-054', 'Barba 26/02',                  'servizio', 'op-marco',  '2026-02-26T11:25:00'),
('inc-055', 18.00, 'contanti',  'cli-roberto',   'app-055', 'Taglio walk-in 26/02',         'servizio', 'op-luca',   '2026-02-26T14:35:00'),
('inc-056', 90.00, 'carta',     'cli-elena',     'app-056', 'Balayage completo 27/02',      'servizio', 'op-giulia', '2026-02-27T11:05:00'),
('inc-057', 18.00, 'contanti',  'cli-antonio',   'app-057', 'Taglio 27/02',                 'servizio', 'op-marco',  '2026-02-27T10:05:00'),
('inc-058', 28.00, 'satispay',  'cli-francesca', 'app-058', 'Piega evento 27/02',           'servizio', 'op-paola',  '2026-02-27T10:35:00'),
('inc-059', 20.00, 'satispay',  'cli-davide',    'app-059', 'Taglio 28/02',                 'servizio', 'op-marco',  '2026-02-28T09:35:00');

-- -------------------------------------------------------
-- FORNITORI — 5 brand professionali
-- Schema: id, nome, email, telefono, indirizzo, citta, cap,
--         partita_iva, status, created_at, updated_at
-- -------------------------------------------------------
INSERT OR IGNORE INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-loreal',  "L'Oréal Professionnel",  'ordini@loreal-pro.it',    '0285741000', 'Via Monte Rosa 91',     'Milano', '20149', '01234567890', 'active', '2024-01-15T10:00:00', '2026-02-01T10:00:00'),
('sup-wella',   'Wella Professionals',    'm.bini@wella.com',        '0233456789', 'Via Varesina 162',      'Milano', '20156', '09876543210', 'active', '2024-02-10T10:00:00', '2026-01-15T10:00:00'),
('sup-keune',   'Keune Italia',           'info@keune.it',           '0518080200', 'Via Lame 75',           'Bologna','40122', '11223344556', 'active', '2024-03-05T10:00:00', '2026-02-10T10:00:00'),
('sup-revlon',  'Revlon Professional',    'pro@revlon.it',           '0612345678', 'Via Tiburtina 1020',    'Roma',   '00156', '55667788990', 'active', '2024-05-20T10:00:00', '2025-12-01T10:00:00'),
('sup-framesi', 'Framesi SpA',            'vendite@framesi.it',      '0248202001', 'Via Tcaikovsky 4',      'Milano', '20144', '77889900112', 'active', '2023-11-10T10:00:00', '2026-01-20T10:00:00');

-- -------------------------------------------------------
-- ORDINI FORNITORI
-- Schema: id, supplier_id, ordine_numero, data_ordine,
--         data_consegna_prevista, importo_totale, status, items(JSON), notes, created_at
-- -------------------------------------------------------
INSERT OR IGNORE INTO supplier_orders (id, supplier_id, ordine_numero, data_ordine, data_consegna_prevista, importo_totale, status, items, notes, created_at) VALUES
('ord-001', 'sup-loreal',
 'ORD-2026-001', '2026-02-03', '2026-02-07', 149.00, 'delivered',
 '[{"prodotto":"Majirel 4.0 Castano Naturale","qty":6,"prezzo_unit":8.50},{"prodotto":"Majirel 7.1 Biondo Cenere","qty":4,"prezzo_unit":8.50},{"prodotto":"Série Expert Vitamino Color Shampoo 1.5L","qty":3,"prezzo_unit":22.00},{"prodotto":"Oxidant 30vol 1L","qty":4,"prezzo_unit":7.50}]',
 'Ordine mensile standard', '2026-02-03T10:00:00'),
('ord-002', 'sup-wella',
 'ORD-2026-002', '2026-02-10', '2026-02-13', 248.50, 'delivered',
 '[{"prodotto":"Koleston Perfect 10/81 Biondo Chiarissimo Perla","qty":5,"prezzo_unit":9.20},{"prodotto":"Illumina Color 8/ Biondo Chiaro","qty":3,"prezzo_unit":10.50},{"prodotto":"EIMI Thermal Image Spray","qty":10,"prezzo_unit":12.80},{"prodotto":"NutriEnrich Shampoo 1L","qty":4,"prezzo_unit":18.50}]',
 'Richiesta urgente per colori Sara', '2026-02-10T09:00:00'),
('ord-003', 'sup-keune',
 'ORD-2026-003', '2026-01-25', '2026-01-29', 166.50, 'delivered',
 '[{"prodotto":"Keune 5.35 Castano Dorato Acajou","qty":4,"prezzo_unit":7.80},{"prodotto":"So Pure Moisturizing Shampoo 1L","qty":6,"prezzo_unit":14.20},{"prodotto":"Color Treatment Mask 500ml","qty":3,"prezzo_unit":22.50}]',
 NULL, '2026-01-25T11:00:00'),
('ord-004', 'sup-framesi',
 'ORD-2026-004', '2026-02-24', '2026-03-02', 180.20, 'shipped',
 '[{"prodotto":"Framcolor 2001 5.0 Castano Chiaro Naturale","qty":8,"prezzo_unit":6.90},{"prodotto":"Framesi Shampoo Color Protect 1L","qty":4,"prezzo_unit":13.50},{"prodotto":"Decolor B Meches Kit 500g","qty":2,"prezzo_unit":35.00}]',
 'Merce in arrivo lunedì 2 marzo', '2026-02-24T14:00:00'),
('ord-005', 'sup-loreal',
 'ORD-2026-005', '2026-02-27', '2026-03-03', 222.80, 'draft',
 '[{"prodotto":"Majirel Glow 6/23 Rosé Gold","qty":5,"prezzo_unit":9.00},{"prodotto":"Majirel High Lift Biondo Cenere","qty":3,"prezzo_unit":11.00},{"prodotto":"DiaRichesse 9.01 Naturale Cenere","qty":4,"prezzo_unit":8.20},{"prodotto":"Oxidant 20vol 1L","qty":6,"prezzo_unit":7.50}]',
 'Nuovo ordine mensile marzo', '2026-02-27T16:00:00');

-- -------------------------------------------------------
-- PACCHETTI — servizi_inclusi è INTEGER (count)
-- Schema: id, nome, descrizione, prezzo, prezzo_originale,
--         servizi_inclusi(INT), servizio_tipo_id, validita_giorni, attivo
-- -------------------------------------------------------
INSERT OR IGNORE INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo, created_at, updated_at) VALUES
('pck-beauty-plus',    'Beauty Plus',         'Colore + 2 pieghe + trattamento — tutto a prezzo scontato',        99.00,  135.00, 4, NULL,          90,  1, '2025-06-01T00:00:00', '2025-06-01T00:00:00'),
('pck-barba-pro',      'Barba Pro',           '4 rifinture barba + 1 taglio uomo incluso',                        55.00,   72.00, 5, 'srv-barba',   60,  1, '2025-08-01T00:00:00', '2025-08-01T00:00:00'),
('pck-keratina-3x',   'Keratina Trio',       '3 trattamenti keratina al prezzo di 2 — lisciatura progressiva',   75.00,  105.00, 3, 'srv-trattamento', 180, 1, '2025-09-15T00:00:00', '2025-09-15T00:00:00'),
('pck-sposa',          'Sposa da Sogno',      '2 prove acconciatura + taglio + colore + trattamento',            175.00,  230.00, 5, NULL,          120, 1, '2025-10-01T00:00:00', '2025-10-01T00:00:00'),
('pck-meches-vip',     'Meches VIP Annual',   '4 balayage/meches + 4 pieghe — abbonamento annuale risparmio',   299.00,  420.00, 8, 'srv-meches',  365, 1, '2025-11-01T00:00:00', '2025-11-01T00:00:00');

-- -------------------------------------------------------
-- CLIENTI PACCHETTI
-- Schema: id, cliente_id, pacchetto_id, stato, servizi_usati,
--         servizi_totali, data_acquisto, data_scadenza, metodo_pagamento, pagato, note
-- -------------------------------------------------------
INSERT OR IGNORE INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_acquisto, data_scadenza, metodo_pagamento, pagato, note) VALUES
('cp-001', 'cli-chiara',    'pck-beauty-plus',  'attivo',     2, 4, '2025-12-15T11:00:00', '2026-03-15', 'carta',    1, 'Rinnovo automatico previsto aprile'),
('cp-002', 'cli-sara',      'pck-meches-vip',   'attivo',     1, 8, '2026-01-10T15:00:00', '2027-01-10', 'carta',    1, NULL),
('cp-003', 'cli-andrea',    'pck-barba-pro',    'attivo',     3, 5, '2026-01-20T11:00:00', '2026-03-21', 'contanti', 1, '2 rifinture rimanenti'),
('cp-004', 'cli-lucia',     'pck-sposa',        'attivo',     2, 5, '2025-11-20T14:00:00', '2026-05-20', 'carta',    1, 'Matrimonio 16 maggio 2026'),
('cp-005', 'cli-francesca', 'pck-keratina-3x',  'attivo',     1, 3, '2026-02-05T16:00:00', '2026-08-05', 'satispay', 1, '2 keratine rimanenti'),
('cp-006', 'cli-anna',      'pck-beauty-plus',  'completato', 4, 4, '2025-10-01T09:00:00', '2025-12-30', 'carta',    1, 'Ciclo completato — riacquistato'),
('cp-007', 'cli-elena',     'pck-meches-vip',   'attivo',     2, 8, '2026-02-01T10:00:00', '2027-02-01', 'carta',    1, NULL);

-- -------------------------------------------------------
-- FATTURE — schema completo FatturaPA-compatible
-- Campi obbligatori: numero, anno, numero_completo, tipo_documento,
--   data_emissione, cliente_id, cliente_denominazione,
--   imponibile_totale, iva_totale, totale_documento, stato_sdi
-- -------------------------------------------------------
INSERT OR IGNORE INTO fatture (id, numero, anno, numero_completo, tipo_documento, data_emissione, data_scadenza,
  cliente_id, cliente_denominazione, cliente_codice_fiscale, cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione, cliente_codice_sdi,
  imponibile_totale, iva_totale, totale_documento, modalita_pagamento, condizioni_pagamento, created_at, updated_at) VALUES
('fat-001', 1, 2026, 'FT-001/2026', 'TD01', '2026-01-31', '2026-02-28',
  'cli-chiara', 'Chiara Esposito', NULL, 'Via Roma 12', '20121', 'Milano', 'MI', 'IT', '0000000',
  81.15, 17.85, 99.00, 'MP05', 'TP02', '2026-01-31T18:00:00', '2026-02-02T09:00:00'),
('fat-002', 2, 2026, 'FT-002/2026', 'TD01', '2026-01-31', '2026-02-28',
  'cli-sara', 'Sara Colombo', NULL, 'Via Nazionale 45', '00184', 'Roma', 'RM', 'IT', '0000000',
  245.08, 53.92, 299.00, 'MP05', 'TP02', '2026-01-31T18:00:00', '2026-01-31T18:30:00'),
('fat-003', 3, 2026, 'FT-003/2026', 'TD01', '2026-02-01', '2026-03-01',
  'cli-lucia', 'Lucia Gallo', NULL, 'Via Garibaldi 8', '40121', 'Bologna', 'BO', 'IT', '0000000',
  143.44, 31.56, 175.00, 'MP08', 'TP02', '2026-02-01T10:00:00', '2026-02-01T10:30:00'),
('fat-004', 4, 2026, 'FT-004/2026', 'TD01', '2026-02-05', '2026-03-05',
  'cli-francesca', 'Francesca Conti', NULL, 'Corso Italia 22', '10121', 'Torino', 'TO', 'IT', '0000000',
  61.48, 13.52, 75.00, 'MP08', 'TP02', '2026-02-05T16:30:00', '2026-02-05T17:00:00'),
('fat-005', 5, 2026, 'FT-005/2026', 'TD01', '2026-02-28', '2026-03-28',
  'cli-anna', 'Anna Ferrari', NULL, 'Via Verdi 5', '20121', 'Milano', 'MI', 'IT', '0000000',
  81.15, 17.85, 99.00, 'MP05', 'TP02', '2026-02-28T12:00:00', '2026-02-28T12:00:00'),
('fat-006', 6, 2026, 'FT-006/2026', 'TD01', '2026-02-28', '2026-03-28',
  'cli-elena', 'Elena Ricci', NULL, 'Via Manzoni 3', '20121', 'Milano', 'MI', 'IT', '0000000',
  245.08, 53.92, 299.00, 'MP05', 'TP02', '2026-02-28T12:30:00', '2026-02-28T12:30:00'),
('fat-007', 7, 2026, 'FT-007/2026', 'TD01', '2026-02-28', '2026-03-28',
  'cli-andrea', 'Andrea Romano', NULL, 'Via Dante 15', '20121', 'Milano', 'MI', 'IT', '0000000',
  45.08, 9.92, 55.00, 'MP01', 'TP02', '2026-02-28T13:00:00', '2026-02-28T13:00:00');

PRAGMA foreign_keys = ON;
