-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Demo Screenshot: SALONE ELEGANCE (Sprint 1)
-- Dati demo perfetti per screenshot e video promozionali
-- Target: fatturato €4.850, 48 clienti, 9 oggi, VIP + pacchetti
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI ──────────────────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Salone Elegance di Giulia'),
('categoria_attivita', 'salone'),
('macro_categoria', 'hair'),
('micro_categoria', 'salone_parrucchiere'),
('indirizzo_completo', 'Via Roma 42, 20121 Milano'),
('orario_apertura', '09:00'),
('orario_chiusura', '19:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]'),
('telefono', '02 8734521'),
('email', 'info@saloneelegance.it'),
('partita_iva', '12345678901'),
('durata_slot_minuti', '30'),
('cassa_fondo_iniziale', '200');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-taglio-donna', 'Taglio Donna',          'Taglio, shampoo e asciugatura',        35.00,  45, 5, 'taglio',       '#ec4899', 1, 1),
('srv-taglio-uomo',  'Taglio Uomo',           'Taglio classico maschile',             18.00,  30, 5, 'taglio',       '#3b82f6', 1, 2),
('srv-taglio-bimbo', 'Taglio Bambino',        'Taglio bambino sotto 12 anni',         12.00,  20, 5, 'taglio',       '#ec4899', 1, 3),
('srv-piega',        'Piega',                 'Messa in piega professionale',          20.00,  30, 5, 'styling',      '#8b5cf6', 1, 4),
('srv-colore',       'Colore',                'Colorazione completa',                  55.00,  90, 5, 'colore',       '#f59e0b', 1, 5),
('srv-meches',       'Meches',                'Meches o colpi di sole',                65.00, 120, 5, 'colore',       '#f59e0b', 1, 6),
('srv-balayage',     'Balayage',              'Tecnica schiarente naturale',           85.00, 120, 5, 'colore',       '#f59e0b', 1, 7),
('srv-trattamento',  'Trattamento Cheratina', 'Trattamento lisciante ristrutturante', 80.00, 120, 5, 'trattamenti',  '#10b981', 1, 8),
('srv-barba',        'Barba',                 'Taglio e rifinitura barba',             12.00,  20, 5, 'uomo',         '#3b82f6', 1, 9),
('srv-combo',        'Taglio + Barba',        'Combo taglio e barba uomo',             28.00,  45, 5, 'uomo',         '#3b82f6', 1, 10),
('srv-ricrescita',   'Tinta Ricrescita',      'Ritocco radici',                        40.00,  60, 5, 'colore',       '#f59e0b', 1, 11),
('srv-permanente',   'Permanente',            'Ondulazione permanente',                60.00, 120, 5, 'trattamenti',  '#10b981', 1, 12),
('srv-extension',    'Extension',             'Applicazione extension capelli',       150.00, 180, 5, 'speciali',     '#ef4444', 1, 13),
('srv-sposa',        'Acconciatura Sposa',    'Acconciatura sposa (prova inclusa)',   120.00, 120, 5, 'speciali',     '#ef4444', 1, 14);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-giulia', 'Giulia',  'Colombo',  'admin',     '#ec4899', 1, '["colore","meches","balayage","trattamenti"]',  'Titolare, 15 anni esperienza colore e tecniche avanzate'),
('op-marco',  'Marco',   'Rossi',    'operatore', '#3b82f6', 1, '["taglio uomo","barba","fade"]',                'Barbiere specializzato, tagli moderni e classici'),
('op-laura',  'Laura',   'Bianchi',  'operatore', '#10b981', 1, '["trattamenti","extension","sposa"]',           'Specialista trattamenti e acconciature cerimonia'),
('op-luca',   'Luca',    'Ferrari',  'operatore', '#f59e0b', 1, '["taglio uomo","barba","styling"]',             'Giovane talento, esperto di tendenze'),
('op-paola',  'Paola',   'Verdi',    'operatore', '#8b5cf6', 1, '["piega","styling","taglio donna"]',            'Esperta piega e styling, 10 anni esperienza');

-- ── ORARI LAVORO ──────────────────────────────────────────────────
DELETE FROM orari_lavoro WHERE operatore_id IN ('op-giulia','op-marco','op-laura','op-luca','op-paola');

-- GIULIA (titolare) — Lun-Ven 09-13/14-19, Sab 09-13
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-giulia-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-giulia'),
('ol-giulia-lun-pa', 1, '13:00', '14:00', 'pausa', 'op-giulia'),
('ol-giulia-lun-pm', 1, '14:00', '19:00', 'lavoro', 'op-giulia'),
('ol-giulia-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-giulia'),
('ol-giulia-mar-pa', 2, '13:00', '14:00', 'pausa', 'op-giulia'),
('ol-giulia-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-giulia'),
('ol-giulia-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-giulia'),
('ol-giulia-mer-pa', 3, '13:00', '14:00', 'pausa', 'op-giulia'),
('ol-giulia-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-giulia'),
('ol-giulia-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-giulia'),
('ol-giulia-gio-pa', 4, '13:00', '14:00', 'pausa', 'op-giulia'),
('ol-giulia-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-giulia'),
('ol-giulia-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-giulia'),
('ol-giulia-ven-pa', 5, '13:00', '14:00', 'pausa', 'op-giulia'),
('ol-giulia-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-giulia'),
('ol-giulia-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-giulia');

-- MARCO (barbiere) — Mar-Sab 09-13/14-19
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-marco-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-marco'),
('ol-marco-mar-pa', 2, '13:00', '14:00', 'pausa', 'op-marco'),
('ol-marco-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-marco'),
('ol-marco-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-marco'),
('ol-marco-mer-pa', 3, '13:00', '14:00', 'pausa', 'op-marco'),
('ol-marco-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-marco'),
('ol-marco-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-marco'),
('ol-marco-gio-pa', 4, '13:00', '14:00', 'pausa', 'op-marco'),
('ol-marco-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-marco'),
('ol-marco-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-marco'),
('ol-marco-ven-pa', 5, '13:00', '14:00', 'pausa', 'op-marco'),
('ol-marco-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-marco'),
('ol-marco-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-marco'),
('ol-marco-sab-pa', 6, '13:00', '14:00', 'pausa', 'op-marco'),
('ol-marco-sab-pm', 6, '14:00', '19:00', 'lavoro', 'op-marco');

-- LAURA (part-time) — Lun,Mer,Ven 09-13/14-18, Sab 09-13
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-laura-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-laura'),
('ol-laura-lun-pa', 1, '13:00', '14:00', 'pausa', 'op-laura'),
('ol-laura-lun-pm', 1, '14:00', '18:00', 'lavoro', 'op-laura'),
('ol-laura-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-laura'),
('ol-laura-mer-pa', 3, '13:00', '14:00', 'pausa', 'op-laura'),
('ol-laura-mer-pm', 3, '14:00', '18:00', 'lavoro', 'op-laura'),
('ol-laura-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-laura'),
('ol-laura-ven-pa', 5, '13:00', '14:00', 'pausa', 'op-laura'),
('ol-laura-ven-pm', 5, '14:00', '18:00', 'lavoro', 'op-laura'),
('ol-laura-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-laura');

-- LUCA — Lun-Ven 10-13/14-20
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-luca-lun-am', 1, '10:00', '13:00', 'lavoro', 'op-luca'),
('ol-luca-lun-pa', 1, '13:00', '14:00', 'pausa', 'op-luca'),
('ol-luca-lun-pm', 1, '14:00', '20:00', 'lavoro', 'op-luca'),
('ol-luca-mar-am', 2, '10:00', '13:00', 'lavoro', 'op-luca'),
('ol-luca-mar-pa', 2, '13:00', '14:00', 'pausa', 'op-luca'),
('ol-luca-mar-pm', 2, '14:00', '20:00', 'lavoro', 'op-luca'),
('ol-luca-mer-am', 3, '10:00', '13:00', 'lavoro', 'op-luca'),
('ol-luca-mer-pa', 3, '13:00', '14:00', 'pausa', 'op-luca'),
('ol-luca-mer-pm', 3, '14:00', '20:00', 'lavoro', 'op-luca'),
('ol-luca-gio-am', 4, '10:00', '13:00', 'lavoro', 'op-luca'),
('ol-luca-gio-pa', 4, '13:00', '14:00', 'pausa', 'op-luca'),
('ol-luca-gio-pm', 4, '14:00', '20:00', 'lavoro', 'op-luca'),
('ol-luca-ven-am', 5, '10:00', '13:00', 'lavoro', 'op-luca'),
('ol-luca-ven-pa', 5, '13:00', '14:00', 'pausa', 'op-luca'),
('ol-luca-ven-pm', 5, '14:00', '20:00', 'lavoro', 'op-luca');

-- PAOLA — Lun-Sab 09-13/14-19
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-paola-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-lun-pa', 1, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-lun-pm', 1, '14:00', '19:00', 'lavoro', 'op-paola'),
('ol-paola-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-mar-pa', 2, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-paola'),
('ol-paola-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-mer-pa', 3, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-paola'),
('ol-paola-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-gio-pa', 4, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-paola'),
('ol-paola-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-ven-pa', 5, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-paola'),
('ol-paola-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-paola'),
('ol-paola-sab-pa', 6, '13:00', '14:00', 'pausa', 'op-paola'),
('ol-paola-sab-pm', 6, '14:00', '19:00', 'lavoro', 'op-paola');

-- ── CLIENTI (48 totali, 5 VIP) ────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-demo-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, loyalty_threshold, is_vip, note, fonte) VALUES
-- VIP clients (is_vip=1, high loyalty)
('cli-demo-01', 'Valeria',    'Moretti',    '3391001001', 'valeria.moretti@email.it',   '1984-06-15', 1, 14, 10, 1, 'Cliente storica. Colore ogni 5 settimane. Preferisce Giulia',      'passaparola'),
('cli-demo-02', 'Francesca',  'Marino',     '3391001002', 'francesca.m@email.it',       '1979-11-22', 1, 18, 10, 1, 'Trattamento cheratina trimestrale. Meches bionde',                'Google'),
('cli-demo-03', 'Silvia',     'De Luca',    '3391001003', 'silvia.dl@email.it',         '1987-03-30', 1, 22, 10, 1, 'VIP da 4 anni. Piega settimanale. Referral: 5 clienti portati',   'referral'),
('cli-demo-04', 'Roberto',    'Galli',      '3391001004', 'roberto.g@email.it',         '1975-08-19', 1, 12, 10, 1, 'Taglio + barba ogni 2 settimane. Vuole sempre Marco',             'passaparola'),
('cli-demo-05', 'Alessandra', 'Ricci',      '3391001005', 'ale.ricci@email.it',         '1991-01-07', 1, 16, 10, 1, 'Balayage esperta. Extension ogni 4 mesi',                         'Instagram'),
-- Regular clients (varied loyalty)
('cli-demo-06', 'Giuseppe',   'Esposito',   '3391001006', 'giuseppe.e@email.it',        '1982-04-03', 1,  3, 10, 0, 'Taglio uomo classico. Nuovo da gennaio',                          'Google'),
('cli-demo-07', 'Anna',       'Colombo',    '3391001007', 'anna.colombo@email.it',      '1985-04-12', 1,  8, 10, 0, 'Colore castano ogni 6 settimane',                                 'passaparola'),
('cli-demo-08', 'Luca',       'Bianchi',    '3391001008', 'luca.b@email.it',            '1998-12-30', 1,  2, 10, 0, 'Studente. Solo taglio base',                                      'amico'),
('cli-demo-09', 'Chiara',     'Marchetti',  '3391001009', 'chiara.march@email.it',      '1990-07-18', 1,  7, 10, 0, 'Piega per eventi. Sposa giugno 2026',                             'Instagram'),
('cli-demo-10', 'Paolo',      'Ferrari',    '3391001010', 'paolo.ferr@email.it',        '1978-09-05', 1,  9, 10, 0, 'Taglio + barba ogni 3 settimane',                                 'passaparola'),
('cli-demo-11', 'Maria',      'Romano',     '3391001011', 'maria.rom@email.it',         '1965-02-14', 1,  6, 10, 0, 'Piega settimanale sabato. Tinta ricrescita mensile',              'vicina'),
('cli-demo-12', 'Andrea',     'Costa',      '3391001012', 'andrea.costa@email.it',      '1995-03-08', 1,  4, 10, 0, 'Taglio moderno. Fade laterale',                                   'Google'),
('cli-demo-13', 'Elena',      'Fontana',    '3391001013', 'elena.f@email.it',           '1988-10-25', 1,  5, 10, 0, 'Balayage ogni 3 mesi',                                            'Instagram'),
('cli-demo-14', 'Davide',     'Conti',      '3391001014', 'davide.c@email.it',          '1993-05-12', 0,  1, 10, 0, 'Primo taglio gennaio. Combo taglio+barba',                        'Google'),
('cli-demo-15', 'Sara',       'Giordano',   '3391001015', 'sara.g@email.it',            '1996-08-30', 1,  3, 10, 0, 'Colore fantasia. Creativa',                                       'Instagram'),
('cli-demo-16', 'Marco',      'Mancini',    '3391001016', 'marco.manc@email.it',        '1989-12-01', 1,  6, 10, 0, 'Taglio uomo business. Sempre puntuale',                           'LinkedIn'),
('cli-demo-17', 'Laura',      'Barbieri',   '3391001017', 'laura.barb@email.it',        '1983-06-22', 1,  4, 10, 0, 'Taglio + colore trimestrale',                                     'passaparola'),
('cli-demo-18', 'Stefano',    'Pellegrini', '3391001018', 'stefano.p@email.it',         '1970-01-15', 1,  7, 10, 0, 'Taglio classico. Porta il figlio per taglio bambino',             'vicino'),
('cli-demo-19', 'Claudia',    'Vitale',     '3391001019', 'claudia.v@email.it',         '1992-09-08', 1,  2, 10, 0, 'Permanente 2x anno',                                              'Google'),
('cli-demo-20', 'Matteo',     'Serra',      '3391001020', 'matteo.s@email.it',          '1997-04-17', 0,  1, 10, 0, 'Taglio trend. Prima visita febbraio',                             'TikTok'),
('cli-demo-21', 'Paola',      'Lombardi',   '3391001021', 'paola.l@email.it',           '1981-11-03', 1,  5, 10, 0, 'Meches ogni 2 mesi',                                              'passaparola'),
('cli-demo-22', 'Antonio',    'Monti',      '3391001022', 'antonio.m@email.it',         '1974-07-29', 1,  8, 10, 0, 'Combo taglio+barba. Vuole Luca',                                  'amico'),
('cli-demo-23', 'Federica',   'Valentini',  '3391001023', 'federica.v@email.it',        '1994-02-20', 1,  3, 10, 0, 'Colore rame. Trattamento idratante',                              'Instagram'),
('cli-demo-24', 'Giovanni',   'Rinaldi',    '3391001024', 'giovanni.r@email.it',        '1986-05-11', 1,  4, 10, 0, 'Taglio uomo ogni mese',                                           'Google'),
('cli-demo-25', 'Beatrice',   'Fabbri',     '3391001025', 'beatrice.f@email.it',        '1999-08-06', 1,  2, 10, 0, 'Studentessa. Piega per feste',                                    'amico'),
('cli-demo-26', 'Simone',     'Grassi',     '3391001026', 'simone.g@email.it',          '1991-03-14', 0,  1, 10, 0, 'Primo appuntamento marzo',                                        'Google'),
('cli-demo-27', 'Giulia',     'Santoro',    '3391001027', 'giulia.sant@email.it',       '1987-10-09', 1,  6, 10, 0, 'Extension semipermanenti',                                        'Instagram'),
('cli-demo-28', 'Fabio',      'Mazza',      '3391001028', 'fabio.mazza@email.it',       '1980-01-25', 1,  5, 10, 0, 'Taglio + barba classico',                                         'passaparola'),
('cli-demo-29', 'Michela',    'Ruggiero',   '3391001029', 'michela.r@email.it',         '1993-12-18', 1,  3, 10, 0, 'Taglio corto donna. Styling moderno',                             'Google'),
('cli-demo-30', 'Enrico',     'Cattaneo',   '3391001030', 'enrico.c@email.it',          '1976-06-07', 1,  7, 10, 0, 'Taglio business. Sempre venerdì',                                 'referral'),
('cli-demo-31', 'Roberta',    'Pagano',     '3391001031', 'roberta.p@email.it',         '1989-09-23', 1,  4, 10, 0, 'Balayage castano dorato',                                         'Instagram'),
('cli-demo-32', 'Massimo',    'Villa',      '3391001032', 'massimo.v@email.it',         '1972-03-16', 0,  2, 10, 0, 'Taglio classico conservativo',                                    'vicino'),
('cli-demo-33', 'Teresa',     'Ferraro',    '3391001033', 'teresa.f@email.it',          '1968-07-04', 1,  9, 10, 0, 'Piega bisettimanale. Tinta ricrescita',                           'passaparola'),
('cli-demo-34', 'Lorenzo',    'Bruno',      '3391001034', 'lorenzo.b@email.it',         '1995-11-28', 1,  1, 10, 0, 'Fade moderno',                                                    'TikTok'),
('cli-demo-35', 'Elisa',      'Caruso',     '3391001035', 'elisa.c@email.it',           '1990-04-01', 1,  5, 10, 0, 'Colore biondo cenere',                                            'passaparola'),
('cli-demo-36', 'Nicola',     'Sorrentino', '3391001036', 'nicola.s@email.it',          '1988-08-13', 1,  3, 10, 0, 'Combo rapido in pausa pranzo',                                    'Google'),
('cli-demo-37', 'Cristina',   'Greco',      '3391001037', 'cristina.g@email.it',        '1985-02-26', 1,  6, 10, 0, 'Meches chiare. Trattamento ogni 3 mesi',                          'passaparola'),
('cli-demo-38', 'Vincenzo',   'Leone',      '3391001038', 'vincenzo.l@email.it',        '1977-10-31', 0,  4, 10, 0, 'Taglio + barba tradizionale',                                     'amico'),
('cli-demo-39', 'Marta',      'Marini',     '3391001039', 'marta.mar@email.it',         '1994-06-19', 1,  2, 10, 0, 'Taglio lungo scalato',                                            'Instagram'),
('cli-demo-40', 'Pietro',     'Bianco',     '3391001040', 'pietro.b@email.it',          '1983-12-08', 1,  5, 10, 0, 'Taglio uomo ogni 4 settimane',                                    'Google'),
('cli-demo-41', 'Sofia',      'Testa',      '3391001041', 'sofia.t@email.it',           '1997-01-20', 1,  3, 10, 0, 'Colore pastello. Social influencer',                              'Instagram'),
('cli-demo-42', 'Riccardo',   'Amato',      '3391001042', 'riccardo.a@email.it',        '1992-05-04', 0,  1, 10, 0, 'Prima visita marzo',                                              'Google'),
('cli-demo-43', 'Ilaria',     'Orlando',    '3391001043', 'ilaria.o@email.it',          '1986-08-17', 1,  7, 10, 0, 'Piega e taglio donna',                                            'passaparola'),
('cli-demo-44', 'Daniele',    'Piras',      '3391001044', 'daniele.p@email.it',         '1990-03-22', 1,  4, 10, 0, 'Taglio uomo texture',                                             'referral'),
('cli-demo-45', 'Caterina',   'Ferretti',   '3391001045', 'caterina.f@email.it',        '1982-09-06', 1,  8, 10, 0, 'Extension e colore. Budget alto',                                 'passaparola'),
('cli-demo-46', 'Filippo',    'Gentile',    '3391001046', 'filippo.g@email.it',         '1996-11-14', 1,  2, 10, 0, 'Taglio hipster',                                                  'TikTok'),
('cli-demo-47', 'Giada',      'Marchesi',   '3391001047', 'giada.m@email.it',           '1993-07-02', 1,  5, 10, 0, 'Trattamento lisciante annuale',                                   'passaparola'),
('cli-demo-48', 'Alberto',    'Sala',       '3391001048', 'alberto.s@email.it',         '1981-04-28', 0,  3, 10, 0, 'Combo classico mensile',                                          'vicino');

-- ── APPUNTAMENTI OGGI 31 MARZO (9 confermati) ─────────────────────
DELETE FROM appuntamenti WHERE id LIKE 'apt-demo-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
('apt-demo-t01', 'cli-demo-01', 'srv-colore',       'op-giulia', '2026-03-31T09:00:00', '2026-03-31T10:30:00', 90,  'confermato', 55.00, 55.00, 'Ritocco biondo caldo',        'voice'),
('apt-demo-t02', 'cli-demo-04', 'srv-combo',         'op-marco',  '2026-03-31T09:00:00', '2026-03-31T09:45:00', 45,  'confermato', 28.00, 28.00, 'Taglio + barba come sempre',  'whatsapp'),
('apt-demo-t03', 'cli-demo-03', 'srv-piega',         'op-paola',  '2026-03-31T09:30:00', '2026-03-31T10:00:00', 30,  'confermato', 20.00, 20.00, 'Piega settimanale',           'whatsapp'),
('apt-demo-t04', 'cli-demo-12', 'srv-taglio-uomo',   'op-luca',   '2026-03-31T10:00:00', '2026-03-31T10:30:00', 30,  'confermato', 18.00, 18.00, 'Fade laterale',               'manuale'),
('apt-demo-t05', 'cli-demo-05', 'srv-balayage',      'op-giulia', '2026-03-31T14:00:00', '2026-03-31T16:00:00', 120, 'confermato', 85.00, 85.00, 'Balayage biondo freddo',      'voice'),
('apt-demo-t06', 'cli-demo-09', 'srv-trattamento',   'op-laura',  '2026-03-31T14:00:00', '2026-03-31T16:00:00', 120, 'confermato', 80.00, 80.00, 'Cheratina pre-matrimonio',    'whatsapp'),
('apt-demo-t07', 'cli-demo-10', 'srv-taglio-uomo',   'op-marco',  '2026-03-31T14:30:00', '2026-03-31T15:00:00', 30,  'confermato', 18.00, 18.00, NULL,                          'voice'),
('apt-demo-t08', 'cli-demo-33', 'srv-ricrescita',    'op-paola',  '2026-03-31T15:00:00', '2026-03-31T16:00:00', 60,  'confermato', 40.00, 40.00, 'Tinta ricrescita castano',    'whatsapp'),
('apt-demo-t09', 'cli-demo-22', 'srv-combo',         'op-luca',   '2026-03-31T16:00:00', '2026-03-31T16:45:00', 45,  'confermato', 28.00, 28.00, 'Combo con styling',           'manuale'),

-- ── APPUNTAMENTI SETTIMANA (1-5 Apr, ~16 additional) ──────────────
-- Mercoledi 1 Aprile
('apt-demo-w01', 'cli-demo-02', 'srv-meches',        'op-giulia', '2026-04-01T09:00:00', '2026-04-01T11:00:00', 120, 'confermato', 65.00, 65.00, 'Meches estate',               'whatsapp'),
('apt-demo-w02', 'cli-demo-06', 'srv-combo',         'op-marco',  '2026-04-01T09:00:00', '2026-04-01T09:45:00', 45,  'confermato', 28.00, 28.00, NULL,                          'voice'),
('apt-demo-w03', 'cli-demo-11', 'srv-piega',         'op-paola',  '2026-04-01T10:00:00', '2026-04-01T10:30:00', 30,  'confermato', 20.00, 20.00, 'Piega sabato',                'whatsapp'),
('apt-demo-w04', 'cli-demo-20', 'srv-taglio-uomo',   'op-luca',   '2026-04-01T11:00:00', '2026-04-01T11:30:00', 30,  'confermato', 18.00, 18.00, NULL,                          'manuale'),
-- Giovedi 2 Aprile
('apt-demo-w05', 'cli-demo-07', 'srv-colore',        'op-giulia', '2026-04-02T09:00:00', '2026-04-02T10:30:00', 90,  'confermato', 55.00, 55.00, 'Colore castano cioccolato',   'whatsapp'),
('apt-demo-w06', 'cli-demo-16', 'srv-taglio-uomo',   'op-marco',  '2026-04-02T10:00:00', '2026-04-02T10:30:00', 30,  'confermato', 18.00, 18.00, 'Taglio business',             'voice'),
('apt-demo-w07', 'cli-demo-45', 'srv-extension',     'op-laura',  '2026-04-02T14:00:00', '2026-04-02T17:00:00', 180, 'confermato',150.00,150.00, 'Rinnovo extension',           'whatsapp'),
('apt-demo-w08', 'cli-demo-25', 'srv-piega',         'op-paola',  '2026-04-02T15:00:00', '2026-04-02T15:30:00', 30,  'confermato', 20.00, 20.00, 'Piega per festa',             'manuale'),
-- Venerdi 3 Aprile
('apt-demo-w09', 'cli-demo-37', 'srv-meches',        'op-giulia', '2026-04-03T09:00:00', '2026-04-03T11:00:00', 120, 'confermato', 65.00, 65.00, NULL,                          'whatsapp'),
('apt-demo-w10', 'cli-demo-30', 'srv-taglio-uomo',   'op-marco',  '2026-04-03T09:30:00', '2026-04-03T10:00:00', 30,  'confermato', 18.00, 18.00, 'Taglio venerdì fisso',        'voice'),
('apt-demo-w11', 'cli-demo-43', 'srv-taglio-donna',  'op-paola',  '2026-04-03T10:00:00', '2026-04-03T10:45:00', 45,  'confermato', 35.00, 35.00, 'Taglio + piega',              'whatsapp'),
('apt-demo-w12', 'cli-demo-34', 'srv-taglio-uomo',   'op-luca',   '2026-04-03T14:00:00', '2026-04-03T14:30:00', 30,  'confermato', 18.00, 18.00, 'Fade moderno',                'manuale'),
-- Sabato 4 Aprile
('apt-demo-w13', 'cli-demo-01', 'srv-piega',         'op-giulia', '2026-04-04T09:00:00', '2026-04-04T09:30:00', 30,  'confermato', 20.00, 20.00, NULL,                          'whatsapp'),
('apt-demo-w14', 'cli-demo-28', 'srv-combo',         'op-marco',  '2026-04-04T09:00:00', '2026-04-04T09:45:00', 45,  'confermato', 28.00, 28.00, NULL,                          'voice'),
('apt-demo-w15', 'cli-demo-11', 'srv-ricrescita',    'op-paola',  '2026-04-04T09:30:00', '2026-04-04T10:30:00', 60,  'confermato', 40.00, 40.00, 'Tinta mensile',               'whatsapp'),
('apt-demo-w16', 'cli-demo-09', 'srv-sposa',         'op-laura',  '2026-04-04T10:00:00', '2026-04-04T12:00:00', 120, 'confermato',120.00,120.00, 'Prova acconciatura sposa',    'whatsapp'),

-- ── APPUNTAMENTI MARZO COMPLETATI (~€4.850 fatturato) ─────────────
-- Settimana 2-7 Marzo (~€1.200)
('apt-demo-m01', 'cli-demo-01', 'srv-colore',       'op-giulia', '2026-03-02T09:00:00', '2026-03-02T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-m02', 'cli-demo-04', 'srv-combo',        'op-marco',  '2026-03-02T09:30:00', '2026-03-02T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-m03', 'cli-demo-03', 'srv-piega',        'op-paola',  '2026-03-02T10:00:00', '2026-03-02T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m04', 'cli-demo-08', 'srv-taglio-uomo',  'op-luca',   '2026-03-02T11:00:00', '2026-03-02T11:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m05', 'cli-demo-02', 'srv-trattamento',  'op-laura',  '2026-03-03T09:00:00', '2026-03-03T11:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
('apt-demo-m06', 'cli-demo-10', 'srv-combo',        'op-marco',  '2026-03-03T10:00:00', '2026-03-03T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m07', 'cli-demo-13', 'srv-balayage',     'op-giulia', '2026-03-04T09:00:00', '2026-03-04T11:00:00', 120, 'completato', 85.00, 85.00, NULL, 'voice'),
('apt-demo-m08', 'cli-demo-16', 'srv-taglio-uomo',  'op-marco',  '2026-03-04T09:30:00', '2026-03-04T10:00:00', 30,  'completato', 18.00, 18.00, NULL, 'whatsapp'),
('apt-demo-m09', 'cli-demo-21', 'srv-meches',       'op-giulia', '2026-03-05T14:00:00', '2026-03-05T16:00:00', 120, 'completato', 65.00, 65.00, NULL, 'whatsapp'),
('apt-demo-m10', 'cli-demo-22', 'srv-combo',        'op-luca',   '2026-03-05T10:00:00', '2026-03-05T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'manuale'),
('apt-demo-m11', 'cli-demo-11', 'srv-piega',        'op-paola',  '2026-03-06T09:00:00', '2026-03-06T09:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m12', 'cli-demo-18', 'srv-taglio-uomo',  'op-marco',  '2026-03-06T10:00:00', '2026-03-06T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-m13', 'cli-demo-24', 'srv-taglio-uomo',  'op-luca',   '2026-03-06T11:00:00', '2026-03-06T11:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m14', 'cli-demo-05', 'srv-extension',    'op-laura',  '2026-03-07T09:00:00', '2026-03-07T12:00:00', 180, 'completato',150.00,150.00, NULL, 'whatsapp'),
('apt-demo-m15', 'cli-demo-33', 'srv-ricrescita',   'op-paola',  '2026-03-07T10:00:00', '2026-03-07T11:00:00', 60,  'completato', 40.00, 40.00, NULL, 'whatsapp'),
('apt-demo-m16', 'cli-demo-28', 'srv-combo',        'op-marco',  '2026-03-07T09:30:00', '2026-03-07T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
-- Settimana 9-14 Marzo (~€1.250)
('apt-demo-m17', 'cli-demo-07', 'srv-colore',       'op-giulia', '2026-03-09T09:00:00', '2026-03-09T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'whatsapp'),
('apt-demo-m18', 'cli-demo-06', 'srv-combo',        'op-marco',  '2026-03-09T10:00:00', '2026-03-09T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m19', 'cli-demo-15', 'srv-colore',       'op-giulia', '2026-03-10T09:00:00', '2026-03-10T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-m20', 'cli-demo-36', 'srv-combo',        'op-luca',   '2026-03-10T12:00:00', '2026-03-10T12:45:00', 45,  'completato', 28.00, 28.00, NULL, 'manuale'),
('apt-demo-m21', 'cli-demo-37', 'srv-meches',       'op-giulia', '2026-03-11T09:00:00', '2026-03-11T11:00:00', 120, 'completato', 65.00, 65.00, NULL, 'whatsapp'),
('apt-demo-m22', 'cli-demo-30', 'srv-taglio-uomo',  'op-marco',  '2026-03-11T10:00:00', '2026-03-11T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-m23', 'cli-demo-43', 'srv-taglio-donna', 'op-paola',  '2026-03-11T10:30:00', '2026-03-11T11:15:00', 45,  'completato', 35.00, 35.00, NULL, 'whatsapp'),
('apt-demo-m24', 'cli-demo-19', 'srv-permanente',   'op-laura',  '2026-03-12T09:00:00', '2026-03-12T11:00:00', 120, 'completato', 60.00, 60.00, NULL, 'whatsapp'),
('apt-demo-m25', 'cli-demo-40', 'srv-taglio-uomo',  'op-marco',  '2026-03-12T09:30:00', '2026-03-12T10:00:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m26', 'cli-demo-03', 'srv-piega',        'op-paola',  '2026-03-12T10:00:00', '2026-03-12T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m27', 'cli-demo-31', 'srv-balayage',     'op-giulia', '2026-03-13T14:00:00', '2026-03-13T16:00:00', 120, 'completato', 85.00, 85.00, NULL, 'voice'),
('apt-demo-m28', 'cli-demo-44', 'srv-taglio-uomo',  'op-luca',   '2026-03-13T10:00:00', '2026-03-13T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m29', 'cli-demo-38', 'srv-combo',        'op-marco',  '2026-03-13T11:00:00', '2026-03-13T11:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m30', 'cli-demo-11', 'srv-ricrescita',   'op-paola',  '2026-03-14T09:00:00', '2026-03-14T10:00:00', 60,  'completato', 40.00, 40.00, NULL, 'whatsapp'),
('apt-demo-m31', 'cli-demo-01', 'srv-piega',        'op-giulia', '2026-03-14T10:00:00', '2026-03-14T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m32', 'cli-demo-46', 'srv-taglio-uomo',  'op-luca',   '2026-03-14T11:00:00', '2026-03-14T11:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
-- Settimana 16-21 Marzo (~€1.300)
('apt-demo-m33', 'cli-demo-02', 'srv-meches',       'op-giulia', '2026-03-16T09:00:00', '2026-03-16T11:00:00', 120, 'completato', 65.00, 65.00, NULL, 'whatsapp'),
('apt-demo-m34', 'cli-demo-04', 'srv-combo',        'op-marco',  '2026-03-16T09:30:00', '2026-03-16T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-m35', 'cli-demo-25', 'srv-piega',        'op-paola',  '2026-03-16T10:00:00', '2026-03-16T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'manuale'),
('apt-demo-m36', 'cli-demo-14', 'srv-combo',        'op-luca',   '2026-03-16T11:00:00', '2026-03-16T11:45:00', 45,  'completato', 28.00, 28.00, NULL, 'Google'),
('apt-demo-m37', 'cli-demo-45', 'srv-trattamento',  'op-laura',  '2026-03-17T09:00:00', '2026-03-17T11:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
('apt-demo-m38', 'cli-demo-12', 'srv-taglio-uomo',  'op-luca',   '2026-03-17T10:00:00', '2026-03-17T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-m39', 'cli-demo-23', 'srv-colore',       'op-giulia', '2026-03-18T09:00:00', '2026-03-18T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-m40', 'cli-demo-10', 'srv-combo',        'op-marco',  '2026-03-18T10:00:00', '2026-03-18T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-m41', 'cli-demo-03', 'srv-piega',        'op-paola',  '2026-03-18T10:30:00', '2026-03-18T11:00:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m42', 'cli-demo-35', 'srv-colore',       'op-giulia', '2026-03-19T09:00:00', '2026-03-19T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'Instagram'),
('apt-demo-m43', 'cli-demo-48', 'srv-combo',        'op-marco',  '2026-03-19T10:00:00', '2026-03-19T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m44', 'cli-demo-29', 'srv-taglio-donna', 'op-paola',  '2026-03-19T11:00:00', '2026-03-19T11:45:00', 45,  'completato', 35.00, 35.00, NULL, 'whatsapp'),
('apt-demo-m45', 'cli-demo-47', 'srv-trattamento',  'op-laura',  '2026-03-19T14:00:00', '2026-03-19T16:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
('apt-demo-m46', 'cli-demo-27', 'srv-extension',    'op-laura',  '2026-03-20T09:00:00', '2026-03-20T12:00:00', 180, 'completato',150.00,150.00, NULL, 'whatsapp'),
('apt-demo-m47', 'cli-demo-17', 'srv-taglio-donna', 'op-paola',  '2026-03-20T10:00:00', '2026-03-20T10:45:00', 45,  'completato', 35.00, 35.00, NULL, 'voice'),
('apt-demo-m48', 'cli-demo-26', 'srv-taglio-uomo',  'op-luca',   '2026-03-20T10:00:00', '2026-03-20T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m49', 'cli-demo-11', 'srv-piega',        'op-paola',  '2026-03-21T09:00:00', '2026-03-21T09:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m50', 'cli-demo-32', 'srv-taglio-uomo',  'op-marco',  '2026-03-21T10:00:00', '2026-03-21T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
-- Settimana 23-28 Marzo (~€1.100)
('apt-demo-m51', 'cli-demo-01', 'srv-colore',       'op-giulia', '2026-03-23T09:00:00', '2026-03-23T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-m52', 'cli-demo-22', 'srv-combo',        'op-marco',  '2026-03-23T09:30:00', '2026-03-23T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-m53', 'cli-demo-39', 'srv-taglio-donna', 'op-paola',  '2026-03-23T10:00:00', '2026-03-23T10:45:00', 45,  'completato', 35.00, 35.00, NULL, 'manuale'),
('apt-demo-m54', 'cli-demo-34', 'srv-taglio-uomo',  'op-luca',   '2026-03-23T11:00:00', '2026-03-23T11:30:00', 30,  'completato', 18.00, 18.00, NULL, 'TikTok'),
('apt-demo-m55', 'cli-demo-13', 'srv-balayage',     'op-giulia', '2026-03-24T09:00:00', '2026-03-24T11:00:00', 120, 'completato', 85.00, 85.00, NULL, 'voice'),
('apt-demo-m56', 'cli-demo-06', 'srv-combo',        'op-marco',  '2026-03-24T10:00:00', '2026-03-24T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m57', 'cli-demo-41', 'srv-colore',       'op-giulia', '2026-03-25T09:00:00', '2026-03-25T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'Instagram'),
('apt-demo-m58', 'cli-demo-24', 'srv-taglio-uomo',  'op-luca',   '2026-03-25T10:00:00', '2026-03-25T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m59', 'cli-demo-03', 'srv-piega',        'op-paola',  '2026-03-25T10:30:00', '2026-03-25T11:00:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-m60', 'cli-demo-09', 'srv-taglio-donna', 'op-paola',  '2026-03-26T09:00:00', '2026-03-26T09:45:00', 45,  'completato', 35.00, 35.00, NULL, 'whatsapp'),
('apt-demo-m61', 'cli-demo-16', 'srv-taglio-uomo',  'op-marco',  '2026-03-26T09:30:00', '2026-03-26T10:00:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-m62', 'cli-demo-42', 'srv-taglio-uomo',  'op-luca',   '2026-03-26T10:00:00', '2026-03-26T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'Google'),
('apt-demo-m63', 'cli-demo-33', 'srv-ricrescita',   'op-giulia', '2026-03-27T09:00:00', '2026-03-27T10:00:00', 60,  'completato', 40.00, 40.00, NULL, 'whatsapp'),
('apt-demo-m64', 'cli-demo-28', 'srv-combo',        'op-marco',  '2026-03-27T10:00:00', '2026-03-27T10:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-m65', 'cli-demo-18', 'srv-taglio-bimbo', 'op-paola',  '2026-03-27T10:00:00', '2026-03-27T10:20:00', 20,  'completato', 12.00, 12.00, 'Figlio di Stefano', 'manuale'),
('apt-demo-m66', 'cli-demo-21', 'srv-meches',       'op-giulia', '2026-03-28T09:00:00', '2026-03-28T11:00:00', 120, 'completato', 65.00, 65.00, NULL, 'whatsapp'),
('apt-demo-m67', 'cli-demo-40', 'srv-taglio-uomo',  'op-luca',   '2026-03-28T10:00:00', '2026-03-28T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-m68', 'cli-demo-11', 'srv-piega',        'op-paola',  '2026-03-28T09:30:00', '2026-03-28T10:00:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
-- Extra completati per raggiungere €4.850 (sabati + giorni extra)
-- Sabato 1 Marzo
('apt-demo-e01', 'cli-demo-04', 'srv-combo',        'op-marco',  '2026-03-01T09:00:00', '2026-03-01T09:45:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-e02', 'cli-demo-01', 'srv-piega',        'op-giulia', '2026-03-01T09:00:00', '2026-03-01T09:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e03', 'cli-demo-11', 'srv-piega',        'op-paola',  '2026-03-01T10:00:00', '2026-03-01T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
-- Sabato 8 Marzo
('apt-demo-e04', 'cli-demo-02', 'srv-colore',       'op-giulia', '2026-03-08T09:00:00', '2026-03-08T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-e05', 'cli-demo-10', 'srv-combo',        'op-marco',  '2026-03-08T09:30:00', '2026-03-08T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-e06', 'cli-demo-03', 'srv-piega',        'op-paola',  '2026-03-08T10:00:00', '2026-03-08T10:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e07', 'cli-demo-18', 'srv-taglio-uomo',  'op-luca',   '2026-03-08T10:00:00', '2026-03-08T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-e08', 'cli-demo-45', 'srv-balayage',     'op-giulia', '2026-03-08T11:00:00', '2026-03-08T13:00:00', 120, 'completato', 85.00, 85.00, NULL, 'whatsapp'),
-- Sabato 15 Marzo
('apt-demo-e09', 'cli-demo-01', 'srv-piega',        'op-giulia', '2026-03-15T09:00:00', '2026-03-15T09:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e10', 'cli-demo-22', 'srv-combo',        'op-marco',  '2026-03-15T09:00:00', '2026-03-15T09:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-e11', 'cli-demo-33', 'srv-piega',        'op-paola',  '2026-03-15T09:30:00', '2026-03-15T10:00:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e12', 'cli-demo-09', 'srv-trattamento',  'op-laura',  '2026-03-15T09:00:00', '2026-03-15T11:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
-- Sabato 22 Marzo
('apt-demo-e13', 'cli-demo-07', 'srv-colore',       'op-giulia', '2026-03-22T09:00:00', '2026-03-22T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-e14', 'cli-demo-04', 'srv-combo',        'op-marco',  '2026-03-22T09:00:00', '2026-03-22T09:45:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-e15', 'cli-demo-11', 'srv-piega',        'op-paola',  '2026-03-22T09:30:00', '2026-03-22T10:00:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e16', 'cli-demo-27', 'srv-trattamento',  'op-laura',  '2026-03-22T09:00:00', '2026-03-22T11:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
-- Sabato 29 Marzo
('apt-demo-e17', 'cli-demo-05', 'srv-colore',       'op-giulia', '2026-03-29T09:00:00', '2026-03-29T10:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-e18', 'cli-demo-28', 'srv-combo',        'op-marco',  '2026-03-29T09:00:00', '2026-03-29T09:45:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-e19', 'cli-demo-43', 'srv-taglio-donna', 'op-paola',  '2026-03-29T09:00:00', '2026-03-29T09:45:00', 45,  'completato', 35.00, 35.00, NULL, 'whatsapp'),
('apt-demo-e20', 'cli-demo-46', 'srv-taglio-uomo',  'op-luca',   '2026-03-29T10:00:00', '2026-03-29T10:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
-- Extra weekdays Marzo (fill gaps)
('apt-demo-e21', 'cli-demo-35', 'srv-meches',       'op-giulia', '2026-03-02T14:00:00', '2026-03-02T16:00:00', 120, 'completato', 65.00, 65.00, NULL, 'voice'),
('apt-demo-e22', 'cli-demo-17', 'srv-taglio-donna', 'op-paola',  '2026-03-03T14:00:00', '2026-03-03T14:45:00', 45,  'completato', 35.00, 35.00, NULL, 'whatsapp'),
('apt-demo-e23', 'cli-demo-44', 'srv-taglio-uomo',  'op-luca',   '2026-03-03T14:00:00', '2026-03-03T14:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-e24', 'cli-demo-41', 'srv-colore',       'op-giulia', '2026-03-04T14:00:00', '2026-03-04T15:30:00', 90,  'completato', 55.00, 55.00, NULL, 'Instagram'),
('apt-demo-e25', 'cli-demo-30', 'srv-taglio-uomo',  'op-marco',  '2026-03-04T14:00:00', '2026-03-04T14:30:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-e26', 'cli-demo-15', 'srv-ricrescita',   'op-giulia', '2026-03-05T09:00:00', '2026-03-05T10:00:00', 60,  'completato', 40.00, 40.00, NULL, 'whatsapp'),
('apt-demo-e27', 'cli-demo-36', 'srv-combo',        'op-marco',  '2026-03-05T09:30:00', '2026-03-05T10:15:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-e28', 'cli-demo-23', 'srv-colore',       'op-giulia', '2026-03-09T14:00:00', '2026-03-09T15:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-e29', 'cli-demo-38', 'srv-combo',        'op-luca',   '2026-03-10T14:00:00', '2026-03-10T14:45:00', 45,  'completato', 28.00, 28.00, NULL, 'manuale'),
('apt-demo-e30', 'cli-demo-47', 'srv-permanente',   'op-laura',  '2026-03-10T09:00:00', '2026-03-10T11:00:00', 120, 'completato', 60.00, 60.00, NULL, 'whatsapp'),
('apt-demo-e31', 'cli-demo-29', 'srv-taglio-donna', 'op-paola',  '2026-03-12T14:00:00', '2026-03-12T14:45:00', 45,  'completato', 35.00, 35.00, NULL, 'voice'),
('apt-demo-e32', 'cli-demo-48', 'srv-combo',        'op-marco',  '2026-03-12T14:00:00', '2026-03-12T14:45:00', 45,  'completato', 28.00, 28.00, NULL, 'whatsapp'),
('apt-demo-e33', 'cli-demo-31', 'srv-colore',       'op-giulia', '2026-03-17T14:00:00', '2026-03-17T15:30:00', 90,  'completato', 55.00, 55.00, NULL, 'voice'),
('apt-demo-e34', 'cli-demo-39', 'srv-piega',        'op-paola',  '2026-03-17T14:00:00', '2026-03-17T14:30:00', 30,  'completato', 20.00, 20.00, NULL, 'manuale'),
('apt-demo-e35', 'cli-demo-40', 'srv-combo',        'op-luca',   '2026-03-18T14:00:00', '2026-03-18T14:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-e36', 'cli-demo-07', 'srv-ricrescita',   'op-giulia', '2026-03-24T14:00:00', '2026-03-24T15:00:00', 60,  'completato', 40.00, 40.00, NULL, 'whatsapp'),
('apt-demo-e37', 'cli-demo-20', 'srv-taglio-uomo',  'op-luca',   '2026-03-24T14:00:00', '2026-03-24T14:30:00', 30,  'completato', 18.00, 18.00, NULL, 'manuale'),
('apt-demo-e38', 'cli-demo-14', 'srv-combo',        'op-marco',  '2026-03-25T14:00:00', '2026-03-25T14:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
('apt-demo-e39', 'cli-demo-25', 'srv-piega',        'op-paola',  '2026-03-26T14:00:00', '2026-03-26T14:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e40', 'cli-demo-37', 'srv-trattamento',  'op-laura',  '2026-03-26T14:00:00', '2026-03-26T16:00:00', 120, 'completato', 80.00, 80.00, NULL, 'whatsapp'),
('apt-demo-e41', 'cli-demo-02', 'srv-piega',        'op-giulia', '2026-03-27T14:00:00', '2026-03-27T14:30:00', 30,  'completato', 20.00, 20.00, NULL, 'whatsapp'),
('apt-demo-e42', 'cli-demo-12', 'srv-taglio-uomo',  'op-marco',  '2026-03-27T14:00:00', '2026-03-27T14:30:00', 30,  'completato', 18.00, 18.00, NULL, 'voice'),
('apt-demo-e43', 'cli-demo-19', 'srv-taglio-donna', 'op-paola',  '2026-03-28T14:00:00', '2026-03-28T14:45:00', 45,  'completato', 35.00, 35.00, NULL, 'manuale'),
('apt-demo-e44', 'cli-demo-46', 'srv-combo',        'op-luca',   '2026-03-28T14:00:00', '2026-03-28T14:45:00', 45,  'completato', 28.00, 28.00, NULL, 'voice'),
-- No-show (2)
('apt-demo-ns1', 'cli-demo-20', 'srv-taglio-uomo',  'op-marco',  '2026-03-10T16:00:00', '2026-03-10T16:30:00', 30,  'no_show',    18.00, 18.00, 'Non si è presentato', 'manuale'),
('apt-demo-ns2', 'cli-demo-42', 'srv-taglio-uomo',  'op-luca',   '2026-03-19T16:00:00', '2026-03-19T16:30:00', 30,  'no_show',    18.00, 18.00, 'Non risponde al telefono', 'voice');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-festa-papa', 'Festa del Papà',    'Taglio uomo + barba + styling — regalo perfetto per papà',   49.00,  58.00, 3, NULL,             30,  1),
('pkg-estate',     'Pacchetto Estate',  '5 pieghe al prezzo di 4 — pronta per l''estate',             80.00, 100.00, 5, 'srv-piega',       90,  1),
('pkg-natale',     'Promo Natale',      'Colore + piega + trattamento cheratina — look completo',    130.00, 155.00, 3, NULL,              60,  1);

-- ── PACCHETTO_SERVIZI ─────────────────────────────────────────────
DELETE FROM pacchetto_servizi;
INSERT INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita) VALUES
('ps-fp-1', 'pkg-festa-papa', 'srv-taglio-uomo', 1),
('ps-fp-2', 'pkg-festa-papa', 'srv-barba', 1),
('ps-fp-3', 'pkg-festa-papa', 'srv-piega', 1),
('ps-es-1', 'pkg-estate', 'srv-piega', 5),
('ps-na-1', 'pkg-natale', 'srv-colore', 1),
('ps-na-2', 'pkg-natale', 'srv-piega', 1),
('ps-na-3', 'pkg-natale', 'srv-trattamento', 1);

-- ── CLIENTI_PACCHETTI ─────────────────────────────────────────────
DELETE FROM clienti_pacchetti;
INSERT INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_acquisto, data_scadenza, metodo_pagamento, pagato) VALUES
('cp-01', 'cli-demo-10', 'pkg-festa-papa', 'venduto',   0, 3, '2026-03-15 10:30:00', '2026-04-14 23:59:59', 'carta',    1),
('cp-02', 'cli-demo-03', 'pkg-estate',     'in_uso',    2, 5, '2026-03-01 11:00:00', '2026-05-30 23:59:59', 'contanti', 1),
('cp-03', 'cli-demo-01', 'pkg-estate',     'in_uso',    3, 5, '2026-02-20 09:45:00', '2026-05-21 23:59:59', 'carta',    1),
('cp-04', 'cli-demo-37', 'pkg-natale',     'completato',3, 3, '2026-01-10 14:00:00', '2026-03-11 23:59:59', 'satispay', 1),
('cp-05', 'cli-demo-22', 'pkg-festa-papa', 'in_uso',    1, 3, '2026-03-20 16:00:00', '2026-04-19 23:59:59', 'contanti', 1);

-- ── INCASSI (match fatturato completati) ──────────────────────────
DELETE FROM incassi WHERE id LIKE 'inc-demo-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, descrizione, categoria, operatore_id, data_incasso) VALUES
-- Settimana 1 (2-7 Marzo)
('inc-demo-01', 55.00,  'carta',    'cli-demo-01', 'apt-demo-m01', 'Colore',              'servizio', 'op-giulia', '2026-03-02 10:30:00'),
('inc-demo-02', 28.00,  'contanti', 'cli-demo-04', 'apt-demo-m02', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-02 10:15:00'),
('inc-demo-03', 20.00,  'satispay', 'cli-demo-03', 'apt-demo-m03', 'Piega',               'servizio', 'op-paola',  '2026-03-02 10:30:00'),
('inc-demo-04', 18.00,  'contanti', 'cli-demo-08', 'apt-demo-m04', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-02 11:30:00'),
('inc-demo-05', 80.00,  'carta',    'cli-demo-02', 'apt-demo-m05', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-03 11:00:00'),
('inc-demo-06', 28.00,  'contanti', 'cli-demo-10', 'apt-demo-m06', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-03 10:45:00'),
('inc-demo-07', 85.00,  'carta',    'cli-demo-13', 'apt-demo-m07', 'Balayage',            'servizio', 'op-giulia', '2026-03-04 11:00:00'),
('inc-demo-08', 18.00,  'contanti', 'cli-demo-16', 'apt-demo-m08', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-04 10:00:00'),
('inc-demo-09', 65.00,  'carta',    'cli-demo-21', 'apt-demo-m09', 'Meches',              'servizio', 'op-giulia', '2026-03-05 16:00:00'),
('inc-demo-10', 28.00,  'satispay', 'cli-demo-22', 'apt-demo-m10', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-05 10:45:00'),
('inc-demo-11', 20.00,  'contanti', 'cli-demo-11', 'apt-demo-m11', 'Piega',               'servizio', 'op-paola',  '2026-03-06 09:30:00'),
('inc-demo-12', 18.00,  'contanti', 'cli-demo-18', 'apt-demo-m12', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-06 10:30:00'),
('inc-demo-13', 18.00,  'carta',    'cli-demo-24', 'apt-demo-m13', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-06 11:30:00'),
('inc-demo-14',150.00,  'carta',    'cli-demo-05', 'apt-demo-m14', 'Extension',           'servizio', 'op-laura',  '2026-03-07 12:00:00'),
('inc-demo-15', 40.00,  'contanti', 'cli-demo-33', 'apt-demo-m15', 'Tinta Ricrescita',    'servizio', 'op-paola',  '2026-03-07 11:00:00'),
('inc-demo-16', 28.00,  'satispay', 'cli-demo-28', 'apt-demo-m16', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-07 10:15:00'),
-- Settimana 2 (9-14 Marzo)
('inc-demo-17', 55.00,  'carta',    'cli-demo-07', 'apt-demo-m17', 'Colore',              'servizio', 'op-giulia', '2026-03-09 10:30:00'),
('inc-demo-18', 28.00,  'contanti', 'cli-demo-06', 'apt-demo-m18', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-09 10:45:00'),
('inc-demo-19', 55.00,  'carta',    'cli-demo-15', 'apt-demo-m19', 'Colore',              'servizio', 'op-giulia', '2026-03-10 10:30:00'),
('inc-demo-20', 28.00,  'contanti', 'cli-demo-36', 'apt-demo-m20', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-10 12:45:00'),
('inc-demo-21', 65.00,  'carta',    'cli-demo-37', 'apt-demo-m21', 'Meches',              'servizio', 'op-giulia', '2026-03-11 11:00:00'),
('inc-demo-22', 18.00,  'contanti', 'cli-demo-30', 'apt-demo-m22', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-11 10:30:00'),
('inc-demo-23', 35.00,  'satispay', 'cli-demo-43', 'apt-demo-m23', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-11 11:15:00'),
('inc-demo-24', 60.00,  'carta',    'cli-demo-19', 'apt-demo-m24', 'Permanente',          'servizio', 'op-laura',  '2026-03-12 11:00:00'),
('inc-demo-25', 18.00,  'contanti', 'cli-demo-40', 'apt-demo-m25', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-12 10:00:00'),
('inc-demo-26', 20.00,  'contanti', 'cli-demo-03', 'apt-demo-m26', 'Piega',               'servizio', 'op-paola',  '2026-03-12 10:30:00'),
('inc-demo-27', 85.00,  'carta',    'cli-demo-31', 'apt-demo-m27', 'Balayage',            'servizio', 'op-giulia', '2026-03-13 16:00:00'),
('inc-demo-28', 18.00,  'satispay', 'cli-demo-44', 'apt-demo-m28', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-13 10:30:00'),
('inc-demo-29', 28.00,  'contanti', 'cli-demo-38', 'apt-demo-m29', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-13 11:45:00'),
('inc-demo-30', 40.00,  'carta',    'cli-demo-11', 'apt-demo-m30', 'Tinta Ricrescita',    'servizio', 'op-paola',  '2026-03-14 10:00:00'),
('inc-demo-31', 20.00,  'contanti', 'cli-demo-01', 'apt-demo-m31', 'Piega',               'servizio', 'op-giulia', '2026-03-14 10:30:00'),
('inc-demo-32', 18.00,  'contanti', 'cli-demo-46', 'apt-demo-m32', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-14 11:30:00'),
-- Settimana 3 (16-21 Marzo)
('inc-demo-33', 65.00,  'carta',    'cli-demo-02', 'apt-demo-m33', 'Meches',              'servizio', 'op-giulia', '2026-03-16 11:00:00'),
('inc-demo-34', 28.00,  'contanti', 'cli-demo-04', 'apt-demo-m34', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-16 10:15:00'),
('inc-demo-35', 20.00,  'satispay', 'cli-demo-25', 'apt-demo-m35', 'Piega',               'servizio', 'op-paola',  '2026-03-16 10:30:00'),
('inc-demo-36', 28.00,  'contanti', 'cli-demo-14', 'apt-demo-m36', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-16 11:45:00'),
('inc-demo-37', 80.00,  'carta',    'cli-demo-45', 'apt-demo-m37', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-17 11:00:00'),
('inc-demo-38', 18.00,  'contanti', 'cli-demo-12', 'apt-demo-m38', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-17 10:30:00'),
('inc-demo-39', 55.00,  'carta',    'cli-demo-23', 'apt-demo-m39', 'Colore',              'servizio', 'op-giulia', '2026-03-18 10:30:00'),
('inc-demo-40', 28.00,  'satispay', 'cli-demo-10', 'apt-demo-m40', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-18 10:45:00'),
('inc-demo-41', 20.00,  'contanti', 'cli-demo-03', 'apt-demo-m41', 'Piega',               'servizio', 'op-paola',  '2026-03-18 11:00:00'),
('inc-demo-42', 55.00,  'carta',    'cli-demo-35', 'apt-demo-m42', 'Colore',              'servizio', 'op-giulia', '2026-03-19 10:30:00'),
('inc-demo-43', 28.00,  'contanti', 'cli-demo-48', 'apt-demo-m43', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-19 10:45:00'),
('inc-demo-44', 35.00,  'satispay', 'cli-demo-29', 'apt-demo-m44', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-19 11:45:00'),
('inc-demo-45', 80.00,  'carta',    'cli-demo-47', 'apt-demo-m45', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-19 16:00:00'),
('inc-demo-46',150.00,  'carta',    'cli-demo-27', 'apt-demo-m46', 'Extension',           'servizio', 'op-laura',  '2026-03-20 12:00:00'),
('inc-demo-47', 35.00,  'contanti', 'cli-demo-17', 'apt-demo-m47', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-20 10:45:00'),
('inc-demo-48', 18.00,  'contanti', 'cli-demo-26', 'apt-demo-m48', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-20 10:30:00'),
('inc-demo-49', 20.00,  'satispay', 'cli-demo-11', 'apt-demo-m49', 'Piega',               'servizio', 'op-paola',  '2026-03-21 09:30:00'),
('inc-demo-50', 18.00,  'contanti', 'cli-demo-32', 'apt-demo-m50', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-21 10:30:00'),
-- Settimana 4 (23-28 Marzo)
('inc-demo-51', 55.00,  'carta',    'cli-demo-01', 'apt-demo-m51', 'Colore',              'servizio', 'op-giulia', '2026-03-23 10:30:00'),
('inc-demo-52', 28.00,  'contanti', 'cli-demo-22', 'apt-demo-m52', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-23 10:15:00'),
('inc-demo-53', 35.00,  'satispay', 'cli-demo-39', 'apt-demo-m53', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-23 10:45:00'),
('inc-demo-54', 18.00,  'contanti', 'cli-demo-34', 'apt-demo-m54', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-23 11:30:00'),
('inc-demo-55', 85.00,  'carta',    'cli-demo-13', 'apt-demo-m55', 'Balayage',            'servizio', 'op-giulia', '2026-03-24 11:00:00'),
('inc-demo-56', 28.00,  'contanti', 'cli-demo-06', 'apt-demo-m56', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-24 10:45:00'),
('inc-demo-57', 55.00,  'carta',    'cli-demo-41', 'apt-demo-m57', 'Colore',              'servizio', 'op-giulia', '2026-03-25 10:30:00'),
('inc-demo-58', 18.00,  'contanti', 'cli-demo-24', 'apt-demo-m58', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-25 10:30:00'),
('inc-demo-59', 20.00,  'satispay', 'cli-demo-03', 'apt-demo-m59', 'Piega',               'servizio', 'op-paola',  '2026-03-25 11:00:00'),
('inc-demo-60', 35.00,  'carta',    'cli-demo-09', 'apt-demo-m60', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-26 09:45:00'),
('inc-demo-61', 18.00,  'contanti', 'cli-demo-16', 'apt-demo-m61', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-26 10:00:00'),
('inc-demo-62', 18.00,  'contanti', 'cli-demo-42', 'apt-demo-m62', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-26 10:30:00'),
('inc-demo-63', 40.00,  'carta',    'cli-demo-33', 'apt-demo-m63', 'Tinta Ricrescita',    'servizio', 'op-giulia', '2026-03-27 10:00:00'),
('inc-demo-64', 28.00,  'satispay', 'cli-demo-28', 'apt-demo-m64', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-27 10:45:00'),
('inc-demo-65', 12.00,  'contanti', 'cli-demo-18', 'apt-demo-m65', 'Taglio Bambino',      'servizio', 'op-paola',  '2026-03-27 10:20:00'),
('inc-demo-66', 65.00,  'carta',    'cli-demo-21', 'apt-demo-m66', 'Meches',              'servizio', 'op-giulia', '2026-03-28 11:00:00'),
('inc-demo-67', 18.00,  'contanti', 'cli-demo-40', 'apt-demo-m67', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-28 10:30:00'),
('inc-demo-68', 20.00,  'contanti', 'cli-demo-11', 'apt-demo-m68', 'Piega',               'servizio', 'op-paola',  '2026-03-28 10:00:00'),
-- Extra incassi (match extra completati)
('inc-demo-e01', 28.00,  'contanti', 'cli-demo-04', 'apt-demo-e01', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-01 09:45:00'),
('inc-demo-e02', 20.00,  'carta',    'cli-demo-01', 'apt-demo-e02', 'Piega',               'servizio', 'op-giulia', '2026-03-01 09:30:00'),
('inc-demo-e03', 20.00,  'contanti', 'cli-demo-11', 'apt-demo-e03', 'Piega',               'servizio', 'op-paola',  '2026-03-01 10:30:00'),
('inc-demo-e04', 55.00,  'carta',    'cli-demo-02', 'apt-demo-e04', 'Colore',              'servizio', 'op-giulia', '2026-03-08 10:30:00'),
('inc-demo-e05', 28.00,  'satispay', 'cli-demo-10', 'apt-demo-e05', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-08 10:15:00'),
('inc-demo-e06', 20.00,  'contanti', 'cli-demo-03', 'apt-demo-e06', 'Piega',               'servizio', 'op-paola',  '2026-03-08 10:30:00'),
('inc-demo-e07', 18.00,  'contanti', 'cli-demo-18', 'apt-demo-e07', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-08 10:30:00'),
('inc-demo-e08', 85.00,  'carta',    'cli-demo-45', 'apt-demo-e08', 'Balayage',            'servizio', 'op-giulia', '2026-03-08 13:00:00'),
('inc-demo-e09', 20.00,  'contanti', 'cli-demo-01', 'apt-demo-e09', 'Piega',               'servizio', 'op-giulia', '2026-03-15 09:30:00'),
('inc-demo-e10', 28.00,  'satispay', 'cli-demo-22', 'apt-demo-e10', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-15 09:45:00'),
('inc-demo-e11', 20.00,  'contanti', 'cli-demo-33', 'apt-demo-e11', 'Piega',               'servizio', 'op-paola',  '2026-03-15 10:00:00'),
('inc-demo-e12', 80.00,  'carta',    'cli-demo-09', 'apt-demo-e12', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-15 11:00:00'),
('inc-demo-e13', 55.00,  'carta',    'cli-demo-07', 'apt-demo-e13', 'Colore',              'servizio', 'op-giulia', '2026-03-22 10:30:00'),
('inc-demo-e14', 28.00,  'contanti', 'cli-demo-04', 'apt-demo-e14', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-22 09:45:00'),
('inc-demo-e15', 20.00,  'satispay', 'cli-demo-11', 'apt-demo-e15', 'Piega',               'servizio', 'op-paola',  '2026-03-22 10:00:00'),
('inc-demo-e16', 80.00,  'carta',    'cli-demo-27', 'apt-demo-e16', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-22 11:00:00'),
('inc-demo-e17', 55.00,  'carta',    'cli-demo-05', 'apt-demo-e17', 'Colore',              'servizio', 'op-giulia', '2026-03-29 10:30:00'),
('inc-demo-e18', 28.00,  'contanti', 'cli-demo-28', 'apt-demo-e18', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-29 09:45:00'),
('inc-demo-e19', 35.00,  'satispay', 'cli-demo-43', 'apt-demo-e19', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-29 09:45:00'),
('inc-demo-e20', 18.00,  'contanti', 'cli-demo-46', 'apt-demo-e20', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-29 10:30:00'),
('inc-demo-e21', 65.00,  'carta',    'cli-demo-35', 'apt-demo-e21', 'Meches',              'servizio', 'op-giulia', '2026-03-02 16:00:00'),
('inc-demo-e22', 35.00,  'contanti', 'cli-demo-17', 'apt-demo-e22', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-03 14:45:00'),
('inc-demo-e23', 18.00,  'contanti', 'cli-demo-44', 'apt-demo-e23', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-03 14:30:00'),
('inc-demo-e24', 55.00,  'carta',    'cli-demo-41', 'apt-demo-e24', 'Colore',              'servizio', 'op-giulia', '2026-03-04 15:30:00'),
('inc-demo-e25', 18.00,  'contanti', 'cli-demo-30', 'apt-demo-e25', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-04 14:30:00'),
('inc-demo-e26', 40.00,  'carta',    'cli-demo-15', 'apt-demo-e26', 'Tinta Ricrescita',    'servizio', 'op-giulia', '2026-03-05 10:00:00'),
('inc-demo-e27', 28.00,  'satispay', 'cli-demo-36', 'apt-demo-e27', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-05 10:15:00'),
('inc-demo-e28', 55.00,  'carta',    'cli-demo-23', 'apt-demo-e28', 'Colore',              'servizio', 'op-giulia', '2026-03-09 15:30:00'),
('inc-demo-e29', 28.00,  'contanti', 'cli-demo-38', 'apt-demo-e29', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-10 14:45:00'),
('inc-demo-e30', 60.00,  'carta',    'cli-demo-47', 'apt-demo-e30', 'Permanente',          'servizio', 'op-laura',  '2026-03-10 11:00:00'),
('inc-demo-e31', 35.00,  'satispay', 'cli-demo-29', 'apt-demo-e31', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-12 14:45:00'),
('inc-demo-e32', 28.00,  'contanti', 'cli-demo-48', 'apt-demo-e32', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-12 14:45:00'),
('inc-demo-e33', 55.00,  'carta',    'cli-demo-31', 'apt-demo-e33', 'Colore',              'servizio', 'op-giulia', '2026-03-17 15:30:00'),
('inc-demo-e34', 20.00,  'contanti', 'cli-demo-39', 'apt-demo-e34', 'Piega',               'servizio', 'op-paola',  '2026-03-17 14:30:00'),
('inc-demo-e35', 28.00,  'satispay', 'cli-demo-40', 'apt-demo-e35', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-18 14:45:00'),
('inc-demo-e36', 40.00,  'carta',    'cli-demo-07', 'apt-demo-e36', 'Tinta Ricrescita',    'servizio', 'op-giulia', '2026-03-24 15:00:00'),
('inc-demo-e37', 18.00,  'contanti', 'cli-demo-20', 'apt-demo-e37', 'Taglio Uomo',         'servizio', 'op-luca',   '2026-03-24 14:30:00'),
('inc-demo-e38', 28.00,  'contanti', 'cli-demo-14', 'apt-demo-e38', 'Taglio + Barba',      'servizio', 'op-marco',  '2026-03-25 14:45:00'),
('inc-demo-e39', 20.00,  'satispay', 'cli-demo-25', 'apt-demo-e39', 'Piega',               'servizio', 'op-paola',  '2026-03-26 14:30:00'),
('inc-demo-e40', 80.00,  'carta',    'cli-demo-37', 'apt-demo-e40', 'Trattamento Cheratina','servizio', 'op-laura',  '2026-03-26 16:00:00'),
('inc-demo-e41', 20.00,  'contanti', 'cli-demo-02', 'apt-demo-e41', 'Piega',               'servizio', 'op-giulia', '2026-03-27 14:30:00'),
('inc-demo-e42', 18.00,  'contanti', 'cli-demo-12', 'apt-demo-e42', 'Taglio Uomo',         'servizio', 'op-marco',  '2026-03-27 14:30:00'),
('inc-demo-e43', 35.00,  'carta',    'cli-demo-19', 'apt-demo-e43', 'Taglio Donna',        'servizio', 'op-paola',  '2026-03-28 14:45:00'),
('inc-demo-e44', 28.00,  'satispay', 'cli-demo-46', 'apt-demo-e44', 'Taglio + Barba',      'servizio', 'op-luca',   '2026-03-28 14:45:00'),
-- Pacchetti venduti (non collegati ad appuntamenti)
('inc-demo-p1', 80.00,  'carta',    'cli-demo-03', NULL,            'Pacchetto Estate',    'pacchetto','op-giulia', '2026-03-01 11:00:00'),
('inc-demo-p2', 49.00,  'contanti', 'cli-demo-10', NULL,            'Festa del Papà',      'pacchetto','op-marco',  '2026-03-15 10:30:00'),
('inc-demo-p3', 49.00,  'contanti', 'cli-demo-22', NULL,            'Festa del Papà',      'pacchetto','op-luca',   '2026-03-20 16:00:00'),
-- Vendita prodotti (shampoo, maschere, oli — margine extra)
('inc-demo-pr1', 28.00, 'carta',    'cli-demo-01', NULL,            'Shampoo L''Oréal Absolut Repair', 'prodotto', 'op-giulia', '2026-03-05 11:00:00'),
('inc-demo-pr2', 35.00, 'carta',    'cli-demo-05', NULL,            'Maschera Davines OI',              'prodotto', 'op-giulia', '2026-03-08 13:30:00'),
('inc-demo-pr3', 22.00, 'contanti', 'cli-demo-02', NULL,            'Olio Wella Oil Reflections',       'prodotto', 'op-laura',  '2026-03-12 11:30:00'),
('inc-demo-pr4', 45.00, 'carta',    'cli-demo-45', NULL,            'Kit Extension Care (shampoo+maschera)','prodotto','op-laura','2026-03-20 12:30:00'),
('inc-demo-pr5', 18.00, 'satispay', 'cli-demo-37', NULL,            'Spray protettivo calore',          'prodotto', 'op-paola',  '2026-03-11 11:30:00'),
('inc-demo-pr6', 32.00, 'carta',    'cli-demo-03', NULL,            'Balsamo Davines Love Curl',        'prodotto', 'op-giulia', '2026-03-18 11:30:00'),
('inc-demo-pr7', 24.00, 'contanti', 'cli-demo-22', NULL,            'Cera styling Wella EIMI',          'prodotto', 'op-marco',  '2026-03-23 10:30:00'),
('inc-demo-pr8', 42.00, 'carta',    'cli-demo-09', NULL,            'Set regalo Festa del Papà',        'prodotto', 'op-paola',  '2026-03-14 15:00:00'),
('inc-demo-pr9', 38.00, 'satispay', 'cli-demo-33', NULL,            'Trattamento Olaplex take-home',    'prodotto', 'op-giulia', '2026-03-28 10:30:00'),
('inc-demo-p10', 125.00,'carta',    'cli-demo-01', NULL,            'Piastra GHD Gold',                 'prodotto', 'op-giulia', '2026-03-15 10:00:00');

-- ── SUPPLIERS (per completare pagina fornitori) ───────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-demo-%';
INSERT OR REPLACE INTO suppliers (id, nome, telefono, email, indirizzo, citta, created_at, updated_at) VALUES
('sup-demo-01', 'L''Oréal Professionnel',  '800 123456', 'ordini@loreal-pro.it',    'Via Priula 21',    'Milano', '2026-01-01T00:00:00', '2026-01-01T00:00:00'),
('sup-demo-02', 'Wella Professionals',      '02 4567890', 'vendite@wella.it',        'Via Tortona 33',   'Milano', '2026-01-01T00:00:00', '2026-01-01T00:00:00'),
('sup-demo-03', 'Ricambi Salone SRL',       '02 3456789', 'info@ricambisalone.it',   'Via Mecenate 76',  'Milano', '2026-01-01T00:00:00', '2026-01-01T00:00:00'),
('sup-demo-04', 'Davines',                  '0521 965611','ordini@davines.com',      'Via Ravasini 9/A', 'Parma',  '2026-01-01T00:00:00', '2026-01-01T00:00:00');

PRAGMA foreign_keys = ON;

-- ═══════════════════════════════════════════════════════════════════
-- VERIFICA TOTALI (112 completati + 3 pacchetti + 2 no-show)
-- Fatturato marzo: ~€4.250 appuntamenti + €178 pacchetti = ~€4.428
-- 48 clienti, 5 VIP, 9 appuntamenti oggi, ~25 settimana
-- ═══════════════════════════════════════════════════════════════════
