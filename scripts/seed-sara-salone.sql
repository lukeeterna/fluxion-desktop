-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: SALONE PARRUCCHIERE (full restore)
-- Ripristina il verticale salone dopo test altre verticali
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Salone Demo FLUXION'),
('categoria_attivita', 'salone'),
('macro_categoria', 'hair'),
('micro_categoria', 'salone_parrucchiere'),
('indirizzo_completo', 'Via Roma 42, 20121 Milano'),
('orario_apertura', '09:00'),
('orario_chiusura', '19:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]');

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

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Giulia: lun-ven full + sab mattina (titolare)
-- Marco: mar-sab (lunedì libero, classico barbiere)
-- Laura: lun,mer,ven,sab (part-time)
-- Luca: lun-ven 10-20 (no sabato, entra tardi)
-- Paola: lun-sab full time

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

-- MARCO (barbiere) — Mar-Sab 09-13/14-19 (lun libero)
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

-- LUCA — Lun-Ven 10-13/14-20 (no sabato, entra dopo)
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

-- PAOLA (full time) — Lun-Sab 09-13/14-19
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

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-sal-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-sal-01', 'Anna',      'Colombo',   '3331111001', 'anna.c@email.it',     '1985-04-12', 1, 25, 1, 'Colore ogni 6 settimane. VIP da 3 anni'),
('cli-sal-02', 'Paolo',     'Esposito',  '3331111002', 'paolo.e@email.it',    '1978-09-05', 1, 15, 0, 'Taglio uomo + barba ogni 3 settimane'),
('cli-sal-03', 'Valentina', 'Ricci',     '3331111003', 'vale.r@email.it',     '1992-01-28', 1,  8, 0, 'Balayage biondo. Allergia ammoniaca → usare prodotti senza'),
('cli-sal-04', 'Marco',     'Ferretti',  '3331111004', 'marco.f@email.it',    '1990-06-15', 0,  5, 0, 'Taglio uomo classico'),
('cli-sal-05', 'Giulia',    'Romano',    '3331111005', 'giulia.rom@email.it', '1988-11-20', 1, 30, 1, 'Piega ogni settimana. Trattamento cheratina 2x/anno'),
('cli-sal-06', 'Andrea',    'Costa',     '3331111006', 'andrea.c@email.it',   '1995-03-08', 1,  3, 0, 'Nuovo cliente. Taglio + barba'),
('cli-sal-07', 'Chiara',    'Marchetti', '3331111007', 'chiara.m@email.it',   '1982-07-22', 1, 18, 1, 'Extension ogni 3 mesi. Sposa maggio 2026'),
('cli-sal-08', 'Luca',      'Bianchi',   '3331111008', 'luca.b@email.it',     '1998-12-30', 1,  2, 0, 'Studente. Solo taglio uomo base');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
DELETE FROM appuntamenti WHERE id LIKE 'apt-sal-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-sal-001', 'cli-sal-01', 'srv-colore',       'op-giulia', '2026-03-31T09:00:00', '2026-03-31T10:30:00', 90,  'confermato', 55.00, 55.00, 'Ritocco biondo caldo',       'voice'),
('apt-sal-002', 'cli-sal-02', 'srv-combo',         'op-marco',  '2026-03-31T09:30:00', '2026-03-31T10:15:00', 45,  'confermato', 28.00, 28.00, NULL,                          'whatsapp'),
('apt-sal-003', 'cli-sal-05', 'srv-piega',         'op-paola',  '2026-03-31T10:00:00', '2026-03-31T10:30:00', 30,  'confermato', 20.00, 20.00, 'Piega settimanale',           'whatsapp'),
('apt-sal-004', 'cli-sal-04', 'srv-taglio-uomo',   'op-luca',   '2026-03-31T11:00:00', '2026-03-31T11:30:00', 30,  'confermato', 18.00, 18.00, NULL,                          'manuale'),
('apt-sal-005', 'cli-sal-03', 'srv-balayage',      'op-giulia', '2026-03-31T14:00:00', '2026-03-31T16:00:00', 120, 'confermato', 85.00, 85.00, 'Balayage biondo freddo',      'voice'),
-- Martedì 1 Aprile
('apt-sal-006', 'cli-sal-06', 'srv-combo',         'op-marco',  '2026-04-01T09:00:00', '2026-04-01T09:45:00', 45,  'confermato', 28.00, 28.00, 'Primo appuntamento',          'voice'),
('apt-sal-007', 'cli-sal-01', 'srv-piega',         'op-paola',  '2026-04-01T10:00:00', '2026-04-01T10:30:00', 30,  'confermato', 20.00, 20.00, NULL,                          'whatsapp'),
('apt-sal-008', 'cli-sal-07', 'srv-trattamento',   'op-laura',  '2026-04-01T14:00:00', '2026-04-01T16:00:00', 120, 'confermato', 80.00, 80.00, 'Cheratina pre-matrimonio',    'whatsapp'),
-- Mercoledì 2 Aprile
('apt-sal-009', 'cli-sal-05', 'srv-taglio-donna',  'op-paola',  '2026-04-02T09:00:00', '2026-04-02T09:45:00', 45,  'confermato', 35.00, 35.00, 'Taglio + piega',              'voice'),
('apt-sal-010', 'cli-sal-02', 'srv-taglio-uomo',   'op-marco',  '2026-04-02T10:00:00', '2026-04-02T10:30:00', 30,  'confermato', 18.00, 18.00, NULL,                          'whatsapp'),
('apt-sal-011', 'cli-sal-08', 'srv-taglio-uomo',   'op-luca',   '2026-04-02T15:00:00', '2026-04-02T15:30:00', 30,  'confermato', 18.00, 18.00, NULL,                          'manuale'),
-- Giovedì 3 Aprile (giornata piena — test waitlist)
('apt-sal-012', 'cli-sal-01', 'srv-meches',        'op-giulia', '2026-04-03T09:00:00', '2026-04-03T11:00:00', 120, 'confermato', 65.00, 65.00, 'Colpi di sole estivi',        'whatsapp'),
('apt-sal-013', 'cli-sal-02', 'srv-combo',         'op-marco',  '2026-04-03T09:00:00', '2026-04-03T09:45:00', 45,  'confermato', 28.00, 28.00, NULL,                          'voice'),
('apt-sal-014', 'cli-sal-05', 'srv-piega',         'op-paola',  '2026-04-03T09:30:00', '2026-04-03T10:00:00', 30,  'confermato', 20.00, 20.00, NULL,                          'whatsapp'),
('apt-sal-015', 'cli-sal-04', 'srv-taglio-uomo',   'op-luca',   '2026-04-03T10:00:00', '2026-04-03T10:30:00', 30,  'confermato', 18.00, 18.00, NULL,                          'manuale'),
('apt-sal-016', 'cli-sal-03', 'srv-ricrescita',    'op-giulia', '2026-04-03T14:00:00', '2026-04-03T15:00:00', 60,  'confermato', 40.00, 40.00, 'Tinta ricrescita castano',    'whatsapp'),
('apt-sal-017', 'cli-sal-07', 'srv-extension',     'op-laura',  '2026-04-03T14:00:00', '2026-04-03T17:00:00', 180, 'confermato',150.00,150.00, 'Rinnovo extension',           'voice'),
-- Venerdì 4 Aprile
('apt-sal-018', 'cli-sal-06', 'srv-taglio-uomo',   'op-marco',  '2026-04-04T09:30:00', '2026-04-04T10:00:00', 30,  'confermato', 18.00, 18.00, NULL,                          'whatsapp'),
('apt-sal-019', 'cli-sal-01', 'srv-piega',         'op-paola',  '2026-04-04T10:00:00', '2026-04-04T10:30:00', 30,  'confermato', 20.00, 20.00, 'Piega venerdì',               'voice'),
('apt-sal-020', 'cli-sal-07', 'srv-sposa',         'op-laura',  '2026-04-04T14:00:00', '2026-04-04T16:00:00', 120, 'confermato',120.00,120.00, 'Prova acconciatura sposa',    'whatsapp');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-sal-01', 'Festa del Papà',    '3 tagli uomo + 1 barba omaggio',          48.00,  66.00, 4, 'srv-taglio-uomo', 60,  1),
('pkg-sal-02', 'Natale Glamour',    'Colore + Piega + Trattamento (-20%)',     120.00, 155.00, 3, NULL,              30,  1),
('pkg-sal-03', 'Pacchetto Estate',  '5 pieghe al prezzo di 4',                 80.00, 100.00, 5, 'srv-piega',       90,  1);

PRAGMA foreign_keys = ON;
