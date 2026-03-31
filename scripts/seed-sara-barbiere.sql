-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: BARBIERE (full restore)
-- Sotto-verticale: barbiere / barber shop
-- Per test voce Sara su iMac — settimana 31 Mar - 5 Apr 2026
-- Giovedì 3 Aprile PIENO per test waitlist
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita',      'Barbershop Da Giovanni'),
('categoria_attivita', 'barbiere'),
('macro_categoria',    'hair'),
('micro_categoria',    'barbiere'),
('indirizzo_completo', 'Via Garibaldi 18, 10121 Torino'),
('orario_apertura',    '09:00'),
('orario_chiusura',    '19:30'),
('giorni_lavorativi',  '["mar","mer","gio","ven","sab"]');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-barba-taglio-uomo',    'Taglio Uomo',               'Taglio classico maschile con rifinitura',             18.00,  30, 5, 'taglio',      '#3b82f6', 1,  1),
('srv-barba-completa',       'Barba Completa',            'Taglio e modellatura barba con olio',                 15.00,  25, 5, 'barba',       '#1d4ed8', 1,  2),
('srv-barba-taglio-combo',   'Taglio + Barba',            'Combo taglio e barba — il classico da barbiere',      28.00,  45, 5, 'combo',       '#6366f1', 1,  3),
('srv-barba-rifinitura',     'Rifinitura Barba',          'Solo rifinitura e definizione barba',                 10.00,  15, 5, 'barba',       '#1d4ed8', 1,  4),
('srv-barba-rasatura-testa', 'Rasatura Testa',            'Rasatura completa testa con rasoio',                  20.00,  30, 5, 'taglio',      '#7c3aed', 1,  5),
('srv-barba-shampoo-taglio', 'Shampoo + Taglio',          'Shampoo professionale + taglio + asciugatura',        22.00,  35, 5, 'taglio',      '#3b82f6', 1,  6),
('srv-barba-colore',         'Colorazione Barba',         'Copertura grigio o cambio colore barba',              15.00,  20, 5, 'colore',      '#f59e0b', 1,  7),
('srv-barba-trattamento',    'Trattamento Viso Uomo',     'Maschera idratante + massaggio viso uomo',            25.00,  30, 5, 'trattamenti', '#10b981', 1,  8),
('srv-barba-black-mask',     'Black Mask',                'Maschera detergente nera per pori viso',              15.00,  20, 5, 'trattamenti', '#10b981', 1,  9),
('srv-barba-bambino',        'Taglio Bambino',            'Taglio bambino sotto 12 anni',                        12.00,  20, 5, 'taglio',      '#ec4899', 1, 10),
('srv-barba-fade',           'Fade',                      'Sfumatura fade / skin fade professionale',            22.00,  35, 5, 'taglio',      '#3b82f6', 1, 11),
('srv-barba-deluxe',         'Taglio + Barba Deluxe',     'Taglio + barba + hot towel + trattamento viso',       40.00,  60, 5, 'deluxe',      '#dc2626', 1, 12);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-giovanni', 'Giovanni', 'Ferretti', 'admin',     '#6366f1', 1, '["taglio uomo","barba","fade","trattamento viso","rasatura testa"]', 'Titolare, 20 anni esperienza. Specialista fade e rasatura tradizionale'),
('op-antonio',  'Antonio',  'Mancuso',  'operatore', '#3b82f6', 1, '["taglio uomo","barba","colorazione barba","shampoo"]',            'Barber classico, maestro della modellatura barba e colorazione'),
('op-diego',    'Diego',    'Ruggieri', 'operatore', '#10b981', 1, '["fade","skin fade","taglio bambino","trattamento viso"]',         'Specialista fade moderni, molto richiesto dai giovani'),
('op-luca-b',   'Luca',     'Bruno',    'operatore', '#f59e0b', 1, '["taglio uomo","barba","black mask","deluxe"]',                    'Barber tuttofare, esperto trattamenti deluxe e benessere uomo');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Giovanni (titolare): Mar-Sab 09-13/14-19:30
-- Antonio: Mar-Sab 09-13/14-19 (classico)
-- Diego: Mer-Sab 10-13/14-19:30 (no mar, entra tardi)
-- Luca B: Mar-Ven 09-13/14-19 (sab libero)
-- NB: Lunedì chiuso (classico barbiere)

DELETE FROM orari_lavoro WHERE operatore_id IN ('op-giovanni','op-antonio','op-diego','op-luca-b');

-- GIOVANNI (titolare) — Mar-Sab 09-13/14-19:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-gio-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-giovanni'),
('ol-gio-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-giovanni'),
('ol-gio-mar-pm', 2, '14:00', '19:30', 'lavoro', 'op-giovanni'),
('ol-gio-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-giovanni'),
('ol-gio-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-giovanni'),
('ol-gio-mer-pm', 3, '14:00', '19:30', 'lavoro', 'op-giovanni'),
('ol-gio-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-giovanni'),
('ol-gio-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-giovanni'),
('ol-gio-gio-pm', 4, '14:00', '19:30', 'lavoro', 'op-giovanni'),
('ol-gio-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-giovanni'),
('ol-gio-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-giovanni'),
('ol-gio-ven-pm', 5, '14:00', '19:30', 'lavoro', 'op-giovanni'),
('ol-gio-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-giovanni'),
('ol-gio-sab-pa', 6, '13:00', '14:00', 'pausa',  'op-giovanni'),
('ol-gio-sab-pm', 6, '14:00', '19:00', 'lavoro', 'op-giovanni');

-- ANTONIO — Mar-Sab 09-13/14-19
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-ant-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-antonio'),
('ol-ant-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-antonio'),
('ol-ant-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-antonio'),
('ol-ant-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-antonio'),
('ol-ant-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-antonio'),
('ol-ant-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-antonio'),
('ol-ant-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-antonio'),
('ol-ant-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-antonio'),
('ol-ant-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-antonio'),
('ol-ant-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-antonio'),
('ol-ant-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-antonio'),
('ol-ant-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-antonio'),
('ol-ant-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-antonio'),
('ol-ant-sab-pa', 6, '13:00', '14:00', 'pausa',  'op-antonio'),
('ol-ant-sab-pm', 6, '14:00', '19:00', 'lavoro', 'op-antonio');

-- DIEGO — Mer-Sab 10-13/14-19:30 (lunedì e martedì libero, entra tardi)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-die-mer-am', 3, '10:00', '13:00', 'lavoro', 'op-diego'),
('ol-die-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-diego'),
('ol-die-mer-pm', 3, '14:00', '19:30', 'lavoro', 'op-diego'),
('ol-die-gio-am', 4, '10:00', '13:00', 'lavoro', 'op-diego'),
('ol-die-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-diego'),
('ol-die-gio-pm', 4, '14:00', '19:30', 'lavoro', 'op-diego'),
('ol-die-ven-am', 5, '10:00', '13:00', 'lavoro', 'op-diego'),
('ol-die-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-diego'),
('ol-die-ven-pm', 5, '14:00', '19:30', 'lavoro', 'op-diego'),
('ol-die-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-diego'),
('ol-die-sab-pa', 6, '13:00', '14:00', 'pausa',  'op-diego'),
('ol-die-sab-pm', 6, '14:00', '19:00', 'lavoro', 'op-diego');

-- LUCA B — Mar-Ven 09-13/14-19 (sabato libero)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-luc-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-luca-b'),
('ol-luc-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-luca-b'),
('ol-luc-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-luca-b'),
('ol-luc-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-luca-b'),
('ol-luc-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-luca-b'),
('ol-luc-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-luca-b'),
('ol-luc-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-luca-b'),
('ol-luc-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-luca-b'),
('ol-luc-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-luca-b'),
('ol-luc-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-luca-b'),
('ol-luc-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-luca-b'),
('ol-luc-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-luca-b');

-- ── CLIENTI ───────────────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-barb-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-barb-01', 'Mario',     'Conti',      '3451122001', 'mario.c@email.it',     '1978-03-14', 1, 35, 1, 'VIP. Taglio + barba ogni 2 settimane. Preferisce Giovanni'),
('cli-barb-02', 'Salvatore', 'Esposito',   '3451122002', 'salvo.e@email.it',     '1985-07-22', 1, 20, 0, 'Fade skin fade. Cliente fisso ogni 3 settimane'),
('cli-barb-03', 'Francesco', 'Lombardi',   '3451122003', 'fra.lombardi@email.it','1992-11-05', 1, 12, 0, 'Taglio + barba completa. Sposo aprile 2026'),
('cli-barb-04', 'Roberto',   'Greco',      '3451122004', 'rob.greco@email.it',   '1970-09-28', 0,  8, 0, 'Taglio uomo classico. Richiede rifinitura precisa'),
('cli-barb-05', 'Lorenzo',   'Marchetti',  '3451122005', 'lor.m@email.it',       '1998-06-15', 1, 18, 0, 'Giovane, ama le fade. Cliente di Diego'),
('cli-barb-06', 'Vincenzo',  'Ferrara',    '3451122006', 'vin.ferrara@email.it', '1965-02-08', 1, 45, 1, 'VIP. Deluxe ogni mese. Regala pacchetti ai colleghi'),
('cli-barb-07', 'Andrea',    'Ricci',      '3451122007', 'andrea.ricci@email.it','1988-04-19', 1,  5, 0, 'Nuovo cliente. Taglio bambino + taglio uomo assieme'),
('cli-barb-08', 'Giacomo',   'De Santis',  '3451122008', 'gia.des@email.it',     '2015-10-30', 1,  3, 0, 'Bambino 10 anni. Viene col papà Andrea (cli-barb-07)');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- NB: Il barbiere è chiuso il lunedì → prima data utile è martedì 1 Apr
-- Mercoledì 2 Apr è il martedì extra (31 Mar = lunedì CHIUSO, partiamo da Mar 1 Apr)
-- Giovedì 3 Aprile: PIENO su tutti gli operatori → test waitlist Sara
DELETE FROM appuntamenti WHERE id LIKE 'apt-barb-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES

-- Martedì 1 Aprile
('apt-barb-001', 'cli-barb-01', 'srv-barba-taglio-combo',   'op-giovanni', '2026-04-01T09:00:00', '2026-04-01T09:45:00', 45, 'confermato', 28.00, 28.00, 'Taglio + barba fisso settimanale',    'whatsapp'),
('apt-barb-002', 'cli-barb-02', 'srv-barba-fade',            'op-antonio',  '2026-04-01T09:30:00', '2026-04-01T10:05:00', 35, 'confermato', 22.00, 22.00, 'Skin fade — raccorciare ai lati',     'voice'),
('apt-barb-003', 'cli-barb-05', 'srv-barba-fade',            'op-luca-b',   '2026-04-01T10:00:00', '2026-04-01T10:35:00', 35, 'confermato', 22.00, 22.00, NULL,                                  'whatsapp'),
('apt-barb-004', 'cli-barb-04', 'srv-barba-taglio-uomo',     'op-antonio',  '2026-04-01T11:00:00', '2026-04-01T11:30:00', 30, 'confermato', 18.00, 18.00, 'Taglio classico corto',               'manuale'),
('apt-barb-005', 'cli-barb-06', 'srv-barba-deluxe',          'op-giovanni', '2026-04-01T14:00:00', '2026-04-01T15:00:00', 60, 'confermato', 40.00, 40.00, 'Mensile deluxe VIP',                  'whatsapp'),

-- Mercoledì 2 Aprile
('apt-barb-006', 'cli-barb-03', 'srv-barba-taglio-combo',   'op-giovanni', '2026-04-02T09:00:00', '2026-04-02T09:45:00', 45, 'confermato', 28.00, 28.00, 'Pre-cerimonia nuziale',               'whatsapp'),
('apt-barb-007', 'cli-barb-01', 'srv-barba-completa',        'op-antonio',  '2026-04-02T10:00:00', '2026-04-02T10:25:00', 25, 'confermato', 15.00, 15.00, 'Solo barba infrasettimanale',         'whatsapp'),
('apt-barb-008', 'cli-barb-07', 'srv-barba-taglio-uomo',     'op-luca-b',   '2026-04-02T11:00:00', '2026-04-02T11:30:00', 30, 'confermato', 18.00, 18.00, 'Padre di Giacomo',                    'voice'),
('apt-barb-009', 'cli-barb-08', 'srv-barba-bambino',         'op-diego',    '2026-04-02T11:00:00', '2026-04-02T11:20:00', 20, 'confermato', 12.00, 12.00, 'Bambino 10 anni, molto tranquillo',   'voice'),
('apt-barb-010', 'cli-barb-05', 'srv-barba-trattamento',     'op-luca-b',   '2026-04-02T14:30:00', '2026-04-02T15:00:00', 30, 'confermato', 25.00, 25.00, 'Trattamento viso dopo fade',          'whatsapp'),

-- Giovedì 3 Aprile — PIENO (test waitlist Sara)
-- Giovanni pieno: 09:00-09:45 + 10:00-10:35 + 11:00-12:00 + 14:00-15:00 + 15:30-16:30
-- Antonio pieno:  09:00-09:30 + 09:45-10:45 + 11:00-11:25 + 14:00-14:45 + 15:00-15:35
-- Diego pieno:    10:00-10:35 + 11:00-11:30 + 14:00-14:25 + 15:00-16:00
-- Luca B pieno:   09:00-09:45 + 10:00-10:30 + 11:00-11:35 + 14:00-15:00
('apt-barb-011', 'cli-barb-06', 'srv-barba-taglio-combo',   'op-giovanni', '2026-04-03T09:00:00', '2026-04-03T09:45:00', 45, 'confermato', 28.00, 28.00, 'Appuntamento fisso giovedì',          'whatsapp'),
('apt-barb-012', 'cli-barb-02', 'srv-barba-fade',            'op-antonio',  '2026-04-03T09:00:00', '2026-04-03T09:35:00', 35, 'confermato', 22.00, 22.00, NULL,                                  'voice'),
('apt-barb-013', 'cli-barb-04', 'srv-barba-taglio-uomo',     'op-luca-b',   '2026-04-03T09:00:00', '2026-04-03T09:30:00', 30, 'confermato', 18.00, 18.00, NULL,                                  'manuale'),
('apt-barb-014', 'cli-barb-05', 'srv-barba-fade',            'op-diego',    '2026-04-03T10:00:00', '2026-04-03T10:35:00', 35, 'confermato', 22.00, 22.00, 'Fade mensile',                        'whatsapp'),
('apt-barb-015', 'cli-barb-01', 'srv-barba-shampoo-taglio',  'op-giovanni', '2026-04-03T10:00:00', '2026-04-03T10:35:00', 35, 'confermato', 22.00, 22.00, 'Shampoo + taglio pre-riunione',       'whatsapp'),
('apt-barb-016', 'cli-barb-03', 'srv-barba-colore',          'op-antonio',  '2026-04-03T09:45:00', '2026-04-03T10:05:00', 20, 'confermato', 15.00, 15.00, 'Copertura grigio pre-matrimonio',     'voice'),
('apt-barb-017', 'cli-barb-07', 'srv-barba-taglio-combo',   'op-luca-b',   '2026-04-03T10:00:00', '2026-04-03T10:45:00', 45, 'confermato', 28.00, 28.00, NULL,                                  'whatsapp'),
('apt-barb-018', 'cli-barb-06', 'srv-barba-trattamento',     'op-giovanni', '2026-04-03T11:00:00', '2026-04-03T11:30:00', 30, 'confermato', 25.00, 25.00, 'Trattamento viso post-taglio',        'whatsapp'),
('apt-barb-019', 'cli-barb-08', 'srv-barba-bambino',         'op-diego',    '2026-04-03T11:00:00', '2026-04-03T11:20:00', 20, 'confermato', 12.00, 12.00, 'Taglio bambino, viene col papà',      'voice'),
('apt-barb-020', 'cli-barb-04', 'srv-barba-completa',        'op-antonio',  '2026-04-03T11:00:00', '2026-04-03T11:25:00', 25, 'confermato', 15.00, 15.00, NULL,                                  'manuale'),

-- Venerdì 4 Aprile
('apt-barb-021', 'cli-barb-01', 'srv-barba-rifinitura',      'op-giovanni', '2026-04-04T09:30:00', '2026-04-04T09:45:00', 15, 'confermato', 10.00, 10.00, 'Solo rifinitura barba venerdì',       'whatsapp'),
('apt-barb-022', 'cli-barb-03', 'srv-barba-deluxe',          'op-giovanni', '2026-04-04T14:00:00', '2026-04-04T15:00:00', 60, 'confermato', 40.00, 40.00, 'Deluxe sposo — sabato si sposa',      'whatsapp'),
('apt-barb-023', 'cli-barb-02', 'srv-barba-taglio-uomo',     'op-diego',    '2026-04-04T15:00:00', '2026-04-04T15:30:00', 30, 'confermato', 18.00, 18.00, NULL,                                  'voice');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-barb-01', 'Pacchetto Barba Settimanale', '4 rifiniture barba al prezzo di 3',                          30.00,  40.00, 4, 'srv-barba-rifinitura', 30,  1),
('pkg-barb-02', 'Pacchetto Sposo',             'Taglio + Barba Deluxe sposo + 1 trattamento viso omaggio',   55.00,  80.00, 2, NULL,                   30,  1),
('pkg-barb-03', 'Pacchetto Padre-Figlio',      'Taglio uomo + Taglio bambino — sconto 15%',                  25.00,  30.00, 2, NULL,                   60,  1);

-- ── SUPPLIERS ─────────────────────────────────────────────────────
DELETE FROM suppliers WHERE id IN ('sup-barb-01','sup-barb-02','sup-barb-03');
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-barb-01', 'Barbertools Italia',         'ordini@barbertools.it',    '0112345678', 'Via Po 22',          'Torino',  '10100', '01234560014', 'active', '2026-01-10T08:00:00', '2026-03-01T10:00:00'),
('sup-barb-02', 'Lame & Rasoio Professional', 'info@lamepro.it',          '0298765432', 'Corso Sempione 88',  'Milano',  '20100', '09876540015', 'active', '2026-01-15T09:00:00', '2026-02-20T11:30:00'),
('sup-barb-03', 'Cosmetici Uomo Premium',     'vendite@cosmeticuomo.it',  '0647889900', 'Via Tuscolana 145',  'Roma',    '00181', '04567890016', 'active', '2026-02-01T10:00:00', '2026-03-15T09:00:00');

-- ── FATTURE (FV001-2026 … FV005-2026) ────────────────────────────
DELETE FROM fatture WHERE id IN ('fat-barb-01','fat-barb-02','fat-barb-03','fat-barb-04','fat-barb-05');
INSERT INTO fatture (
    id, numero, anno, numero_completo, tipo_documento,
    data_emissione, data_scadenza,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato,
    appuntamento_id, causale,
    created_at, updated_at
) VALUES
('fat-barb-01', 1, 2026, 'FV001/2026', 'TD01',
 '2026-04-01', '2026-04-01',
 'cli-barb-01', 'Mario Conti',          NULL, 'CNTMRA78C14L219Z',
 'Via Milano 5', '10100', 'Torino', 'TO', 'IT',
 22.95, 5.05, 28.00,
 'MP01', 'TP02', 'pagata',
 'apt-barb-001', 'Taglio + Barba — 01/04/2026',
 '2026-04-01T09:50:00', '2026-04-01T09:50:00'),

('fat-barb-02', 2, 2026, 'FV002/2026', 'TD01',
 '2026-04-01', '2026-04-01',
 'cli-barb-06', 'Vincenzo Ferrara',     NULL, 'FRRVCN65B08F205K',
 'Via Veneto 33', '10100', 'Torino', 'TO', 'IT',
 32.79, 7.21, 40.00,
 'MP08', 'TP02', 'pagata',
 'apt-barb-005', 'Taglio + Barba Deluxe — 01/04/2026',
 '2026-04-01T15:05:00', '2026-04-01T15:05:00'),

('fat-barb-03', 3, 2026, 'FV003/2026', 'TD01',
 '2026-04-02', '2026-04-02',
 'cli-barb-07', 'Andrea Ricci',         NULL, 'RCCNDR88D19H501P',
 'Corso Re Umberto 12', '10100', 'Torino', 'TO', 'IT',
 14.75, 3.25, 18.00,
 'MP01', 'TP02', 'pagata',
 'apt-barb-008', 'Taglio Uomo — 02/04/2026',
 '2026-04-02T11:35:00', '2026-04-02T11:35:00'),

('fat-barb-04', 4, 2026, 'FV004/2026', 'TD01',
 '2026-04-03', '2026-04-03',
 'cli-barb-06', 'Vincenzo Ferrara',     NULL, 'FRRVCN65B08F205K',
 'Via Veneto 33', '10100', 'Torino', 'TO', 'IT',
 20.49, 4.51, 25.00,
 'MP08', 'TP02', 'pagata',
 'apt-barb-018', 'Trattamento Viso Uomo — 03/04/2026',
 '2026-04-03T11:35:00', '2026-04-03T11:35:00'),

('fat-barb-05', 5, 2026, 'FV005/2026', 'TD01',
 '2026-04-04', '2026-04-04',
 'cli-barb-03', 'Francesco Lombardi',   NULL, 'LMBFNC92S05F205R',
 'Via Garibaldi 7', '10100', 'Torino', 'TO', 'IT',
 32.79, 7.21, 40.00,
 'MP01', 'TP02', 'pagata',
 'apt-barb-022', 'Taglio + Barba Deluxe sposo — 04/04/2026',
 '2026-04-04T15:05:00', '2026-04-04T15:05:00');

-- ── FATTURE RIGHE ─────────────────────────────────────────────────
DELETE FROM fatture_righe WHERE fattura_id IN ('fat-barb-01','fat-barb-02','fat-barb-03','fat-barb-04','fat-barb-05');
INSERT INTO fatture_righe (
    id, fattura_id, numero_linea, descrizione,
    quantita, unita_misura, prezzo_unitario,
    sconto_percentuale, sconto_importo, prezzo_totale,
    aliquota_iva, servizio_id, appuntamento_id,
    created_at
) VALUES
-- FV001: Taglio + Barba €28
('fr-barb-01-01', 'fat-barb-01', 1, 'Taglio Uomo',   1, 'PZ', 18.00, 0, 0, 18.00, 22.0, 'srv-barba-taglio-uomo',  'apt-barb-001', '2026-04-01T09:50:00'),
('fr-barb-01-02', 'fat-barb-01', 2, 'Barba Completa',1, 'PZ', 10.00, 0, 0, 10.00, 22.0, 'srv-barba-completa',      'apt-barb-001', '2026-04-01T09:50:00'),

-- FV002: Taglio + Barba Deluxe €40
('fr-barb-02-01', 'fat-barb-02', 1, 'Taglio + Barba Deluxe', 1, 'PZ', 40.00, 0, 0, 40.00, 22.0, 'srv-barba-deluxe', 'apt-barb-005', '2026-04-01T15:05:00'),

-- FV003: Taglio Uomo €18
('fr-barb-03-01', 'fat-barb-03', 1, 'Taglio Uomo',   1, 'PZ', 18.00, 0, 0, 18.00, 22.0, 'srv-barba-taglio-uomo',  'apt-barb-008', '2026-04-02T11:35:00'),

-- FV004: Trattamento Viso Uomo €25
('fr-barb-04-01', 'fat-barb-04', 1, 'Trattamento Viso Uomo', 1, 'PZ', 25.00, 0, 0, 25.00, 22.0, 'srv-barba-trattamento', 'apt-barb-018', '2026-04-03T11:35:00'),

-- FV005: Taglio + Barba Deluxe sposo €40
('fr-barb-05-01', 'fat-barb-05', 1, 'Taglio + Barba Deluxe (sposo)', 1, 'PZ', 40.00, 0, 0, 40.00, 22.0, 'srv-barba-deluxe', 'apt-barb-022', '2026-04-04T15:05:00');

-- ── INCASSI ───────────────────────────────────────────────────────
DELETE FROM incassi WHERE id LIKE 'inc-barb-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, fattura_id, descrizione, categoria, operatore_id, data_incasso) VALUES
-- 1 Apr
('inc-barb-01', 28.00, 'contanti',  'cli-barb-01', 'apt-barb-001', 'fat-barb-01', 'Taglio + Barba — Mario Conti',           'servizio', 'op-giovanni', '2026-04-01T09:50:00'),
('inc-barb-02', 22.00, 'satispay',  'cli-barb-02', 'apt-barb-002', NULL,          'Fade — Salvatore Esposito',              'servizio', 'op-antonio',  '2026-04-01T10:10:00'),
('inc-barb-03', 22.00, 'carta',     'cli-barb-05', 'apt-barb-003', NULL,          'Fade — Lorenzo Marchetti',               'servizio', 'op-luca-b',   '2026-04-01T10:40:00'),
('inc-barb-04', 18.00, 'contanti',  'cli-barb-04', 'apt-barb-004', NULL,          'Taglio Uomo — Roberto Greco',            'servizio', 'op-antonio',  '2026-04-01T11:35:00'),
('inc-barb-05', 40.00, 'carta',     'cli-barb-06', 'apt-barb-005', 'fat-barb-02', 'Deluxe — Vincenzo Ferrara',              'servizio', 'op-giovanni', '2026-04-01T15:05:00'),
-- 2 Apr
('inc-barb-06', 28.00, 'contanti',  'cli-barb-03', 'apt-barb-006', NULL,          'Taglio + Barba — Francesco Lombardi',    'servizio', 'op-giovanni', '2026-04-02T09:50:00'),
('inc-barb-07', 15.00, 'satispay',  'cli-barb-01', 'apt-barb-007', NULL,          'Barba — Mario Conti',                   'servizio', 'op-antonio',  '2026-04-02T10:30:00'),
('inc-barb-08', 18.00, 'carta',     'cli-barb-07', 'apt-barb-008', 'fat-barb-03', 'Taglio Uomo — Andrea Ricci',             'servizio', 'op-luca-b',   '2026-04-02T11:35:00'),
('inc-barb-09', 12.00, 'contanti',  'cli-barb-07', 'apt-barb-009', NULL,          'Taglio Bambino — Giacomo (figl. Ricci)', 'servizio', 'op-diego',    '2026-04-02T11:25:00'),
-- 3 Apr (giovedì pieno)
('inc-barb-10', 28.00, 'satispay',  'cli-barb-06', 'apt-barb-011', NULL,          'Taglio + Barba — Vincenzo Ferrara',      'servizio', 'op-giovanni', '2026-04-03T09:50:00');

PRAGMA foreign_keys = ON;
