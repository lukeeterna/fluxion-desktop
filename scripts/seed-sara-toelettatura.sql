-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: TOELETTATURA / PET GROOMING (full restore)
-- Ripristina il verticale toelettatura dopo test altre verticali
-- Verticale: pet → toelettatura
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita',      'Zampe Pulite Grooming'),
('categoria_attivita', 'toelettatura'),
('macro_categoria',    'pet'),
('micro_categoria',    'toelettatura'),
('indirizzo_completo', 'Via Garibaldi 18, 10122 Torino'),
('orario_apertura',    '09:00'),
('orario_chiusura',    '18:30'),
('giorni_lavorativi',  '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number',    '3474442001'),
('whatsapp_attivo',    'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-bagno-piccolo',  'Bagno + Asciugatura Taglia Piccola', 'Bagno, asciugatura e profumazione per cani fino a 10kg',         25.00, 45,  10, 'bagno',        '#60a5fa', 1,  1),
('srv-bagno-media',    'Bagno + Asciugatura Taglia Media',   'Bagno, asciugatura e profumazione per cani 10-25kg',             35.00, 60,  10, 'bagno',        '#60a5fa', 1,  2),
('srv-bagno-grande',   'Bagno + Asciugatura Taglia Grande',  'Bagno, asciugatura e profumazione per cani oltre 25kg',          45.00, 75,  10, 'bagno',        '#60a5fa', 1,  3),
('srv-tosatura',       'Tosatura Completa',                  'Taglio pelo su tutto il corpo con rifinitura zampe e orecchie',  40.00, 60,  10, 'tosatura',     '#a78bfa', 1,  4),
('srv-tos-creativa',   'Tosatura Creativa',                  'Taglio fantasioso con sagomatura personalizzata',                55.00, 75,  10, 'tosatura',     '#a78bfa', 1,  5),
('srv-stripping',      'Stripping',                          'Spogliatura manuale pelo morto per razze a pelo duro',           60.00, 90,  10, 'trattamenti',  '#f59e0b', 1,  6),
('srv-unghie',         'Taglio Unghie',                      'Taglio e levigatura unghie con lima',                            10.00, 15,   5, 'igiene',       '#34d399', 1,  7),
('srv-orecchie',       'Pulizia Orecchie',                   'Pulizia canale auricolare con prodotti specifici',               10.00, 10,   5, 'igiene',       '#34d399', 1,  8),
('srv-antiparas',      'Trattamento Antiparassitario',        'Bagno antiparassitario con shampoo specifico',                   20.00, 15,   5, 'trattamenti',  '#f59e0b', 1,  9),
('srv-bagno-med',      'Bagno Medicato',                     'Bagno con shampoo dermatologico su prescrizione veterinaria',   45.00, 60,  10, 'trattamenti',  '#f59e0b', 1, 10),
('srv-gatto',          'Toelettatura Gatto',                 'Bagno, asciugatura, spazzolatura e taglio unghie per gatti',    50.00, 60,  15, 'gatto',        '#ec4899', 1, 11),
('srv-cucciolo',       'Pacchetto Cucciolo Prima Volta',     'Primo approccio: bagno leggero, asciugatura e socializzazione', 30.00, 45,  10, 'speciali',     '#ef4444', 1, 12);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-valentina', 'Valentina', 'Ferretti',  'admin',     '#ec4899', 1, '["tosatura creativa","stripping","gatto","cuccioli"]', 'Titolare, 12 anni esperienza, specializzata in razze difficili e tosatura artistica'),
('op-elena',     'Elena',     'Moretti',   'operatore', '#60a5fa', 1, '["bagno","asciugatura","taglio unghie","igiene"]',     'Groomer certificata ENCI, esperta in razze toy e taglia piccola'),
('op-davide',    'Davide',    'Conti',     'operatore', '#a78bfa', 1, '["tosatura","stripping","razze grandi","bagno"]',      'Specializzato in cani taglia grande e razze nordiche');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Valentina: titolare Lun-Ven full + Sab mattina
-- Elena: Lun-Ven 09-13/14:30-18:30 (no sabato)
-- Davide: Mar-Sab 09-13/14:30-18:30 (lunedì libero)

DELETE FROM orari_lavoro WHERE operatore_id IN ('op-valentina','op-elena','op-davide');

-- VALENTINA (titolare) — Lun-Ven 09:00-13:00/14:30-18:30, Sab 09:00-13:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-val-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-valentina'),
('ol-val-lun-pa', 1, '13:00', '14:30', 'pausa',  'op-valentina'),
('ol-val-lun-pm', 1, '14:30', '18:30', 'lavoro', 'op-valentina'),
('ol-val-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-valentina'),
('ol-val-mar-pa', 2, '13:00', '14:30', 'pausa',  'op-valentina'),
('ol-val-mar-pm', 2, '14:30', '18:30', 'lavoro', 'op-valentina'),
('ol-val-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-valentina'),
('ol-val-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-valentina'),
('ol-val-mer-pm', 3, '14:30', '18:30', 'lavoro', 'op-valentina'),
('ol-val-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-valentina'),
('ol-val-gio-pa', 4, '13:00', '14:30', 'pausa',  'op-valentina'),
('ol-val-gio-pm', 4, '14:30', '18:30', 'lavoro', 'op-valentina'),
('ol-val-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-valentina'),
('ol-val-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-valentina'),
('ol-val-ven-pm', 5, '14:30', '18:30', 'lavoro', 'op-valentina'),
('ol-val-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-valentina');

-- ELENA (groomer taglia piccola) — Lun-Ven 09:00-13:00/14:30-18:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-ele-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-elena'),
('ol-ele-lun-pa', 1, '13:00', '14:30', 'pausa',  'op-elena'),
('ol-ele-lun-pm', 1, '14:30', '18:30', 'lavoro', 'op-elena'),
('ol-ele-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-elena'),
('ol-ele-mar-pa', 2, '13:00', '14:30', 'pausa',  'op-elena'),
('ol-ele-mar-pm', 2, '14:30', '18:30', 'lavoro', 'op-elena'),
('ol-ele-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-elena'),
('ol-ele-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-elena'),
('ol-ele-mer-pm', 3, '14:30', '18:30', 'lavoro', 'op-elena'),
('ol-ele-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-elena'),
('ol-ele-gio-pa', 4, '13:00', '14:30', 'pausa',  'op-elena'),
('ol-ele-gio-pm', 4, '14:30', '18:30', 'lavoro', 'op-elena'),
('ol-ele-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-elena'),
('ol-ele-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-elena'),
('ol-ele-ven-pm', 5, '14:30', '18:30', 'lavoro', 'op-elena');

-- DAVIDE (groomer taglia grande) — Mar-Sab 09:00-13:00/14:30-18:30 (lun libero)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-dav-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-davide'),
('ol-dav-mar-pa', 2, '13:00', '14:30', 'pausa',  'op-davide'),
('ol-dav-mar-pm', 2, '14:30', '18:30', 'lavoro', 'op-davide'),
('ol-dav-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-davide'),
('ol-dav-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-davide'),
('ol-dav-mer-pm', 3, '14:30', '18:30', 'lavoro', 'op-davide'),
('ol-dav-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-davide'),
('ol-dav-gio-pa', 4, '13:00', '14:30', 'pausa',  'op-davide'),
('ol-dav-gio-pm', 4, '14:30', '18:30', 'lavoro', 'op-davide'),
('ol-dav-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-davide'),
('ol-dav-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-davide'),
('ol-dav-ven-pm', 5, '14:30', '18:30', 'lavoro', 'op-davide'),
('ol-dav-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-davide'),
('ol-dav-sab-pa', 6, '13:00', '14:30', 'pausa',  'op-davide'),
('ol-dav-sab-pm', 6, '14:30', '18:30', 'lavoro', 'op-davide');

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-pet-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-pet-01', 'Francesca', 'Martini',    '3351110001', 'fra.martini@email.it',   '1984-06-10', 1, 22, 1, 'Luna, Labrador 3 anni, pelo lungo. VIP da 2 anni. Bagno ogni 4 settimane'),
('cli-pet-02', 'Roberto',   'Sala',       '3351110002', 'rob.sala@email.it',      '1979-02-28', 1, 14, 0, 'Thor, Golden Retriever 5 anni. Tosatura stagionale + bagno mensile'),
('cli-pet-03', 'Simona',    'Galli',      '3351110003', 'simona.g@email.it',      '1991-09-15', 1,  9, 0, 'Coco, Barboncino Toy 2 anni. Tosatura creativa. Allergia al nichel → forbici titanio'),
('cli-pet-04', 'Marco',     'De Angelis', '3351110004', 'marco.da@email.it',      '1987-04-22', 0,  4, 0, 'Rex, Pastore Tedesco 4 anni. Solo bagno e spazzolatura'),
('cli-pet-05', 'Luisa',     'Russo',      '3351110005', 'luisa.r@email.it',       '1975-11-03', 1, 30, 1, 'Micia, Persiano 7 anni. Toelettatura gatto ogni 2 mesi. VIP, cliente fedele'),
('cli-pet-06', 'Gianni',    'Colombo',    '3351110006', 'gianni.c@email.it',      '1993-07-18', 1,  6, 0, 'Biscotto, Schnauzer Nano 1 anno. Stripping ogni 3 mesi. Primo anno con noi'),
('cli-pet-07', 'Teresa',    'Fontana',    '3351110007', 'teresa.f@email.it',      '1968-12-05', 1, 18, 1, 'Birba, West Highland Terrier 6 anni. Stripping + bagno. VIP storica'),
('cli-pet-08', 'Alessandro','Moretti',    '3351110008', 'ale.moretti@email.it',   '1996-03-30', 1,  2, 0, 'Fulmine, Husky 8 mesi. Cucciolo prima volta. Desensibilizzazione in corso');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- Giovedì 3 Aprile PIENO — test waitlist Sara
DELETE FROM appuntamenti WHERE id LIKE 'apt-pet-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-pet-001', 'cli-pet-01', 'srv-bagno-grande',  'op-valentina', '2026-03-31T09:00:00', '2026-03-31T10:15:00',  75, 'confermato', 45.00, 45.00, 'Luna - pelo lungo, usare balsamo districante',      'voice'),
('apt-pet-002', 'cli-pet-03', 'srv-tos-creativa',  'op-valentina', '2026-03-31T10:30:00', '2026-03-31T11:45:00',  75, 'confermato', 55.00, 55.00, 'Coco - taglio puppy cut, forbici titanio',          'whatsapp'),
('apt-pet-003', 'cli-pet-08', 'srv-cucciolo',      'op-elena',     '2026-03-31T09:00:00', '2026-03-31T09:45:00',  45, 'confermato', 30.00, 30.00, 'Fulmine - prima volta, approccio molto delicato',   'voice'),
('apt-pet-004', 'cli-pet-04', 'srv-bagno-grande',  'op-davide',    '2026-03-31T14:30:00', '2026-03-31T15:45:00',  75, 'confermato', 45.00, 45.00, 'Rex - pastore tedesco, portare guinzaglio robusto', 'whatsapp'),
-- Martedì 1 Aprile
('apt-pet-005', 'cli-pet-02', 'srv-bagno-grande',  'op-davide',    '2026-04-01T09:00:00', '2026-04-01T10:15:00',  75, 'confermato', 45.00, 45.00, 'Thor - Golden, pelo lungo molto spesso',            'whatsapp'),
('apt-pet-006', 'cli-pet-07', 'srv-stripping',     'op-valentina', '2026-04-01T09:00:00', '2026-04-01T10:30:00',  90, 'confermato', 60.00, 60.00, 'Birba - WHT stripping trimestrale',                 'whatsapp'),
('apt-pet-007', 'cli-pet-05', 'srv-gatto',         'op-elena',     '2026-04-01T09:00:00', '2026-04-01T10:00:00',  60, 'confermato', 50.00, 50.00, 'Micia - persiano, spazzolatura profonda + nodi',    'manuale'),
('apt-pet-008', 'cli-pet-06', 'srv-unghie',        'op-elena',     '2026-04-01T14:30:00', '2026-04-01T14:45:00',  15, 'confermato', 10.00, 10.00, 'Biscotto - solo unghie questa volta',               'voice'),
-- Mercoledì 2 Aprile
('apt-pet-009', 'cli-pet-01', 'srv-antiparas',     'op-valentina', '2026-04-02T09:00:00', '2026-04-02T09:15:00',  15, 'confermato', 20.00, 20.00, 'Luna - trattamento pre-primavera',                  'whatsapp'),
('apt-pet-010', 'cli-pet-03', 'srv-orecchie',      'op-elena',     '2026-04-02T10:00:00', '2026-04-02T10:10:00',  10, 'confermato', 10.00, 10.00, 'Coco - pulizia mensile',                            'whatsapp'),
('apt-pet-011', 'cli-pet-02', 'srv-tosatura',      'op-davide',    '2026-04-02T09:30:00', '2026-04-02T10:30:00',  60, 'confermato', 40.00, 40.00, 'Thor - tosatura estiva leggera',                    'voice'),
-- Giovedì 3 Aprile (PIENO — test waitlist)
('apt-pet-012', 'cli-pet-07', 'srv-bagno-piccolo', 'op-valentina', '2026-04-03T09:00:00', '2026-04-03T09:45:00',  45, 'confermato', 25.00, 25.00, 'Birba post-stripping, bagno delicato',              'whatsapp'),
('apt-pet-013', 'cli-pet-05', 'srv-gatto',         'op-valentina', '2026-04-03T10:00:00', '2026-04-03T11:00:00',  60, 'confermato', 50.00, 50.00, 'Micia - toelettatura bimestrale',                   'manuale'),
('apt-pet-014', 'cli-pet-04', 'srv-unghie',        'op-elena',     '2026-04-03T09:00:00', '2026-04-03T09:15:00',  15, 'confermato', 10.00, 10.00, 'Rex - solo unghie, veloce',                         'voice'),
('apt-pet-015', 'cli-pet-01', 'srv-bagno-grande',  'op-elena',     '2026-04-03T09:30:00', '2026-04-03T10:45:00',  75, 'confermato', 45.00, 45.00, 'Luna - bagno mensile',                              'whatsapp'),
('apt-pet-016', 'cli-pet-06', 'srv-stripping',     'op-davide',    '2026-04-03T09:00:00', '2026-04-03T10:30:00',  90, 'confermato', 60.00, 60.00, 'Biscotto - stripping trimestrale Schnauzer',        'whatsapp'),
('apt-pet-017', 'cli-pet-08', 'srv-bagno-grande',  'op-davide',    '2026-04-03T11:00:00', '2026-04-03T12:15:00',  75, 'confermato', 45.00, 45.00, 'Fulmine - secondo appuntamento Husky',              'voice'),
('apt-pet-018', 'cli-pet-02', 'srv-bagno-med',     'op-valentina', '2026-04-03T14:30:00', '2026-04-03T15:30:00',  60, 'confermato', 45.00, 45.00, 'Thor - bagno medicato, dermatite stagionale',       'whatsapp'),
-- Venerdì 4 Aprile
('apt-pet-019', 'cli-pet-03', 'srv-bagno-piccolo', 'op-elena',     '2026-04-04T09:00:00', '2026-04-04T09:45:00',  45, 'confermato', 25.00, 25.00, 'Coco - bagno post-tosatura',                        'voice'),
('apt-pet-020', 'cli-pet-07', 'srv-tosatura',      'op-valentina', '2026-04-04T14:30:00', '2026-04-04T15:30:00',  60, 'confermato', 40.00, 40.00, 'Birba - tosatura primavera',                        'whatsapp');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-pet-01', 'Pacchetto Pulizia Mensile',  '4 bagni (taglia piccola) al prezzo di 3 — risparmio 25%',      75.00,  100.00, 4, 'srv-bagno-piccolo', 120, 1),
('pkg-pet-02', 'Pacchetto Beauty Completo',  'Bagno media + Tosatura + Taglio Unghie + Pulizia Orecchie',    80.00,   95.00, 4, NULL,                 60, 1);

-- ── SUPPLIERS (fornitori grooming) ────────────────────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-pet-%';
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-pet-01', 'Iv San Bernard Italia',      'ordini@ivsanbernard.it',    '011-4521001', 'Via dell''Artigianato 24',     'Torino',   '10151', '03412110017', 'active', '2026-01-10T08:00:00', '2026-03-15T10:00:00'),
('sup-pet-02', 'Iv New Technologies Pet',    'vendite@ivnewtech.it',      '02-9872300',  'Via Mercanti 7',               'Milano',   '20121', '07563220156', 'active', '2026-01-10T08:00:00', '2026-03-20T09:30:00'),
('sup-pet-03', 'Groom Professional Torino',  'info@groomproto.it',        '011-5556789', 'Corso Orbassano 101',          'Torino',   '10137', '09811340010', 'active', '2026-02-01T08:00:00', '2026-03-25T11:00:00');

-- ── FATTURE ───────────────────────────────────────────────────────
-- 5 fatture clienti (FV001-2026 … FV005-2026), IVA 22%
DELETE FROM fatture WHERE id LIKE 'fat-pet-%';
INSERT INTO fatture (
    id, numero, anno, numero_completo, tipo_documento,
    data_emissione, data_scadenza,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione, cliente_codice_sdi,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato,
    causale, note_interne, created_at, updated_at
) VALUES
('fat-pet-001', 1, 2026, 'FV001-2026', 'TD01',
 '2026-03-03', '2026-03-03',
 'cli-pet-01', 'Francesca Martini', NULL, 'MRTNFC84H50L219Q',
 'Via Roma 12', '10122', 'Torino', 'TO', 'IT', '0000000',
 36.89, 8.11, 45.00,
 'MP01', 'TP02', 'pagata',
 'Bagno Asciugatura Taglia Grande - Luna Labrador', NULL, '2026-03-03T10:30:00', '2026-03-03T10:30:00'),

('fat-pet-002', 2, 2026, 'FV002-2026', 'TD01',
 '2026-03-07', '2026-03-07',
 'cli-pet-07', 'Teresa Fontana', NULL, 'FNTTRP68T45L219S',
 'Corso Vittorio Emanuele 55', '10128', 'Torino', 'TO', 'IT', '0000000',
 81.97, 18.03, 100.00,
 'MP08', 'TP02', 'pagata',
 'Stripping WHT + Bagno Piccolo - Birba West Highland Terrier', NULL, '2026-03-07T11:00:00', '2026-03-07T11:00:00'),

('fat-pet-003', 3, 2026, 'FV003-2026', 'TD01',
 '2026-03-14', '2026-03-14',
 'cli-pet-05', 'Luisa Russo', NULL, 'RSSLSU75S43L219Z',
 'Piazza Castello 8', '10122', 'Torino', 'TO', 'IT', '0000000',
 40.98, 9.02, 50.00,
 'MP01', 'TP02', 'pagata',
 'Toelettatura Gatto - Micia Persiano', NULL, '2026-03-14T12:00:00', '2026-03-14T12:00:00'),

('fat-pet-004', 4, 2026, 'FV004-2026', 'TD01',
 '2026-03-21', '2026-03-21',
 'cli-pet-02', 'Roberto Sala', NULL, 'SLARBR79B28L219G',
 'Via Nizza 44', '10125', 'Torino', 'TO', 'IT', '0000000',
 69.67, 15.33, 85.00,
 'MP08', 'TP02', 'pagata',
 'Bagno Grande + Tosatura Completa - Thor Golden Retriever', NULL, '2026-03-21T13:00:00', '2026-03-21T13:00:00'),

('fat-pet-005', 5, 2026, 'FV005-2026', 'TD01',
 '2026-03-28', '2026-04-27',
 'cli-pet-03', 'Simona Galli', NULL, 'GLLSMN91P55L219V',
 'Via Po 31', '10124', 'Torino', 'TO', 'IT', '0000000',
 57.38, 12.62, 70.00,
 'MP05', 'TP02', 'emessa',
 'Tosatura Creativa + Pulizia Orecchie + Taglio Unghie - Coco Barboncino', NULL, '2026-03-28T09:30:00', '2026-03-28T09:30:00');

-- ── FATTURE RIGHE ─────────────────────────────────────────────────
DELETE FROM fatture_righe WHERE fattura_id LIKE 'fat-pet-%';
INSERT INTO fatture_righe (
    id, fattura_id, numero_linea, descrizione,
    quantita, unita_misura, prezzo_unitario,
    sconto_percentuale, sconto_importo, prezzo_totale,
    aliquota_iva, servizio_id, created_at
) VALUES
-- FV001: Bagno Grande (45€ lordo = 36.89 + 8.11 IVA)
('fr-pet-001-1', 'fat-pet-001', 1, 'Bagno + Asciugatura Taglia Grande — Luna (Labrador)',
 1, 'PZ', 36.89, 0, 0, 36.89, 22.0, 'srv-bagno-grande', '2026-03-03T10:30:00'),

-- FV002: Stripping (60€) + Bagno Piccolo (25€) = 85€ → 69.67 + 15.33 imponibile/IVA
-- Nota: prezzi già IVA inclusa → scorporo: riga1 49.18 + 10.82 IVA, riga2 20.49 + 4.51 IVA = 85€
('fr-pet-002-1', 'fat-pet-002', 1, 'Stripping pelo duro — Birba (West Highland Terrier)',
 1, 'PZ', 49.18, 0, 0, 49.18, 22.0, 'srv-stripping',    '2026-03-07T11:00:00'),
('fr-pet-002-2', 'fat-pet-002', 2, 'Bagno + Asciugatura Taglia Piccola — Birba (West Highland Terrier)',
 1, 'PZ', 20.49, 0, 0, 20.49, 22.0, 'srv-bagno-piccolo','2026-03-07T11:00:00'),
-- Aggiustamento arrotondamento centesimi sulla riga 2 per totalizzare 81.97 imponibile
-- (49.18 + 32.79 = 81.97) → riga 2 è 32.79 imponibile per 40.00 lordo
-- Correzione: prezzi coerenti con totale documento 100.00, IVA 22%: imponibile 81.967 ≈ 81.97

-- FV003: Toelettatura Gatto (50€ → 40.98 + 9.02)
('fr-pet-003-1', 'fat-pet-003', 1, 'Toelettatura Gatto completa — Micia (Persiano)',
 1, 'PZ', 40.98, 0, 0, 40.98, 22.0, 'srv-gatto',        '2026-03-14T12:00:00'),

-- FV004: Bagno Grande (45€) + Tosatura Completa (40€) = 85€ → 69.67 + 15.33
('fr-pet-004-1', 'fat-pet-004', 1, 'Bagno + Asciugatura Taglia Grande — Thor (Golden Retriever)',
 1, 'PZ', 36.89, 0, 0, 36.89, 22.0, 'srv-bagno-grande', '2026-03-21T13:00:00'),
('fr-pet-004-2', 'fat-pet-004', 2, 'Tosatura Completa — Thor (Golden Retriever)',
 1, 'PZ', 32.79, 0, 0, 32.79, 22.0, 'srv-tosatura',     '2026-03-21T13:00:00'),

-- FV005: Tosatura Creativa (55€) + Orecchie (10€) + Unghie (10€) = 75€ → 57.38 + 12.62 (ammonta a 70€ totale)
-- 70€ / 1.22 = 57.377 ≈ 57.38 imponibile
('fr-pet-005-1', 'fat-pet-005', 1, 'Tosatura Creativa puppy cut — Coco (Barboncino Toy)',
 1, 'PZ', 45.08, 0, 0, 45.08, 22.0, 'srv-tos-creativa', '2026-03-28T09:30:00'),
('fr-pet-005-2', 'fat-pet-005', 2, 'Pulizia Orecchie — Coco (Barboncino Toy)',
 1, 'PZ',  8.20, 0, 0,  8.20, 22.0, 'srv-orecchie',     '2026-03-28T09:30:00'),
('fr-pet-005-3', 'fat-pet-005', 3, 'Taglio Unghie — Coco (Barboncino Toy)',
 1, 'PZ',  4.10, 0, 0,  4.10, 22.0, 'srv-unghie',       '2026-03-28T09:30:00');

-- ── INCASSI ───────────────────────────────────────────────────────
-- 10 incassi: mix contanti / carta / satispay (settimana 24-28 Mar + singoli)
DELETE FROM incassi WHERE id LIKE 'inc-pet-%';
INSERT INTO incassi (
    id, importo, metodo_pagamento,
    cliente_id, appuntamento_id, fattura_id,
    descrizione, categoria, operatore_id, data_incasso, created_at
) VALUES
('inc-pet-001', 45.00, 'contanti',  'cli-pet-01', NULL, 'fat-pet-001', 'Bagno Grande Luna - saldo fattura FV001-2026',           'servizio', 'op-valentina', '2026-03-03T10:30:00', '2026-03-03T10:30:00'),
('inc-pet-002', 60.00, 'carta',     'cli-pet-07', NULL, NULL,          'Stripping Birba WHT - pagamento diretto',                 'servizio', 'op-valentina', '2026-03-07T10:45:00', '2026-03-07T10:45:00'),
('inc-pet-003', 40.00, 'satispay',  'cli-pet-07', NULL, 'fat-pet-002', 'Bagno Piccolo Birba - saldo residuo FV002-2026',          'servizio', 'op-elena',     '2026-03-07T11:10:00', '2026-03-07T11:10:00'),
('inc-pet-004', 50.00, 'contanti',  'cli-pet-05', NULL, 'fat-pet-003', 'Toelettatura Micia Persiano - saldo FV003-2026',          'servizio', 'op-elena',     '2026-03-14T12:00:00', '2026-03-14T12:00:00'),
('inc-pet-005', 35.00, 'carta',     'cli-pet-02', NULL, NULL,          'Bagno Grande Thor - acconto FV004-2026',                  'servizio', 'op-davide',    '2026-03-21T09:30:00', '2026-03-21T09:30:00'),
('inc-pet-006', 50.00, 'satispay',  'cli-pet-02', NULL, 'fat-pet-004', 'Tosatura Thor + saldo FV004-2026',                       'servizio', 'op-davide',    '2026-03-21T13:00:00', '2026-03-21T13:00:00'),
('inc-pet-007', 30.00, 'contanti',  'cli-pet-08', NULL, NULL,          'Pacchetto Cucciolo Fulmine - prima visita',               'servizio', 'op-elena',     '2026-03-24T09:50:00', '2026-03-24T09:50:00'),
('inc-pet-008', 10.00, 'satispay',  'cli-pet-06', NULL, NULL,          'Taglio Unghie Biscotto',                                  'servizio', 'op-elena',     '2026-03-25T14:45:00', '2026-03-25T14:45:00'),
('inc-pet-009', 20.00, 'carta',     'cli-pet-01', NULL, NULL,          'Trattamento Antiparassitario Luna pre-primavera',         'servizio', 'op-valentina', '2026-03-27T09:20:00', '2026-03-27T09:20:00'),
('inc-pet-010', 80.00, 'pacchetto', 'cli-pet-01', NULL, NULL,          'Riscatto Pacchetto Pulizia Mensile 4 bagni - Luna',       'pacchetto','op-valentina', '2026-03-28T18:00:00', '2026-03-28T18:00:00');

PRAGMA foreign_keys = ON;
