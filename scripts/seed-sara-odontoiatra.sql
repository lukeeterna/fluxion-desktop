-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: STUDIO DENTISTICO ODONTOIATRA (full restore)
-- Ripristina il verticale odontoiatra dopo test altre verticali
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Studio Dentistico Dr. Marchetti'),
('categoria_attivita', 'odontoiatra'),
('macro_categoria', 'medico'),
('micro_categoria', 'odontoiatra'),
('indirizzo_completo', 'Via Manzoni 15, 20121 Milano'),
('orario_apertura', '08:30'),
('orario_chiusura', '19:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number', '3356789012'),
('whatsapp_attivo', 'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-visita-controllo',  'Visita di Controllo',    'Esame clinico completo con sondaggio',       50.00,  30, 10, 'visite',       '#6366f1', 1,  1),
('srv-igiene-dentale',    'Igiene Dentale',         'Detartrasi + lucidatura professionale',       80.00,  45, 10, 'igiene',       '#10b981', 1,  2),
('srv-otturazione',       'Otturazione',            'Ricostruzione composita per carie',          100.00,  45, 10, 'conservativa', '#3b82f6', 1,  3),
('srv-devitalizzazione',  'Devitalizzazione',       'Trattamento endodontico monoradicolare',     250.00,  90, 15, 'endodonzia',   '#ef4444', 1,  4),
('srv-estraz-semplice',   'Estrazione Semplice',    'Estrazione dente erotto senza complicanze',   80.00,  30, 15, 'chirurgia',    '#f59e0b', 1,  5),
('srv-estraz-complessa',  'Estrazione Complessa',   'Estrazione chirurgica + punti di sutura',    150.00,  60, 20, 'chirurgia',    '#f59e0b', 1,  6),
('srv-sbiancamento',      'Sbiancamento',           'Sbiancamento professionale in studio',       300.00,  60, 10, 'estetica',     '#ec4899', 1,  7),
('srv-corona',            'Corona',                 'Corona in ceramica su dente devitalizzato',  600.00,  60, 15, 'protesi',      '#8b5cf6', 1,  8),
('srv-impianto',          'Impianto',               'Impianto osteointegrato titanio + corona',  1500.00,  90, 20, 'implantologia','#ef4444', 1,  9),
('srv-panoramica',        'Panoramica',             'Radiografia panoramica digitale OPT',         40.00,  15,  5, 'diagnostica',  '#6366f1', 1, 10),
('srv-orto-consulto',     'Ortodonzia Consulto',    'Prima visita ortodontica + analisi morso',    80.00,  45, 10, 'ortodonzia',   '#f59e0b', 1, 11),
('srv-apparecchio',       'Apparecchio',            'Montaggio brackets fissi (seduta iniziale)', 3000.00,  60, 15, 'ortodonzia',   '#f59e0b', 1, 12),
('srv-protesi-mobile',    'Protesi Mobile',         'Protesi totale o parziale in resina',        800.00,  60, 15, 'protesi',      '#8b5cf6', 1, 13),
('srv-emergenza',         'Emergenza Dentale',      'Visita urgente + trattamento dolore',        100.00,  30, 10, 'urgenze',      '#ef4444', 1, 14);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-marchetti',  'Dott. Luca',       'Marchetti',  'admin',     '#6366f1', 1, '["conservativa","endodonzia","implantologia","chirurgia"]',  'Titolare, 20 anni esperienza. Specialista implantologia e devitalizzazioni'),
('op-igienista',  'Valentina',        'Conti',      'operatore', '#10b981', 1, '["igiene dentale","sbiancamento","prevenzione"]',             'Igienista dentale professionale, esperta in prevenzione e sbiancamento'),
('op-assistente', 'Giorgia',          'Ferretti',   'operatore', '#ec4899', 1, '["assistenza","accettazione","radiografie","panoramica"]',    'Assistente di studio, gestione radiografie e accettazione pazienti'),
('op-ortod',      'Dott.ssa Chiara',  'Romano',     'operatore', '#f59e0b', 1, '["ortodonzia","apparecchi fissi","allineatori","morso"]',     'Ortodontista, specializzata in trattamenti adulti e teen. Aligner expert');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Dr. Marchetti: Lun-Ven full + Sab mattina (titolare)
-- Igienista Valentina: Mar,Mer,Ven,Sab (part-time)
-- Assistente Giorgia: Lun-Sab full (reception + radiografie)
-- Dr.ssa Romano (ortodontista): Lun,Gio,Sab (ambulatorio ortodonzia)
-- Pausa pranzo medica: 13:00-14:30 (più lunga per disinfezione)

DELETE FROM orari_lavoro WHERE operatore_id IN ('op-marchetti','op-igienista','op-assistente','op-ortod');

-- DR. MARCHETTI (titolare) — Lun-Ven 08:30-13:00/14:30-19:00, Sab 08:30-13:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-march-lun-am', 1, '08:30', '13:00', 'lavoro', 'op-marchetti'),
('ol-march-lun-pa', 1, '13:00', '14:30', 'pausa',  'op-marchetti'),
('ol-march-lun-pm', 1, '14:30', '19:00', 'lavoro', 'op-marchetti'),
('ol-march-mar-am', 2, '08:30', '13:00', 'lavoro', 'op-marchetti'),
('ol-march-mar-pa', 2, '13:00', '14:30', 'pausa',  'op-marchetti'),
('ol-march-mar-pm', 2, '14:30', '19:00', 'lavoro', 'op-marchetti'),
('ol-march-mer-am', 3, '08:30', '13:00', 'lavoro', 'op-marchetti'),
('ol-march-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-marchetti'),
('ol-march-mer-pm', 3, '14:30', '19:00', 'lavoro', 'op-marchetti'),
('ol-march-gio-am', 4, '08:30', '13:00', 'lavoro', 'op-marchetti'),
('ol-march-gio-pa', 4, '13:00', '14:30', 'pausa',  'op-marchetti'),
('ol-march-gio-pm', 4, '14:30', '19:00', 'lavoro', 'op-marchetti'),
('ol-march-ven-am', 5, '08:30', '13:00', 'lavoro', 'op-marchetti'),
('ol-march-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-marchetti'),
('ol-march-ven-pm', 5, '14:30', '19:00', 'lavoro', 'op-marchetti'),
('ol-march-sab-am', 6, '08:30', '13:00', 'lavoro', 'op-marchetti');

-- VALENTINA (igienista) — Mar,Mer,Ven 09:00-13:00/14:30-18:00, Sab 09:00-13:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-igien-mar-am', 2, '09:00', '13:00', 'lavoro', 'op-igienista'),
('ol-igien-mar-pa', 2, '13:00', '14:30', 'pausa',  'op-igienista'),
('ol-igien-mar-pm', 2, '14:30', '18:00', 'lavoro', 'op-igienista'),
('ol-igien-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-igienista'),
('ol-igien-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-igienista'),
('ol-igien-mer-pm', 3, '14:30', '18:00', 'lavoro', 'op-igienista'),
('ol-igien-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-igienista'),
('ol-igien-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-igienista'),
('ol-igien-ven-pm', 5, '14:30', '18:00', 'lavoro', 'op-igienista'),
('ol-igien-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-igienista');

-- GIORGIA (assistente/accettazione) — Lun-Ven 08:00-13:00/14:00-19:00, Sab 08:00-13:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-assis-lun-am', 1, '08:00', '13:00', 'lavoro', 'op-assistente'),
('ol-assis-lun-pa', 1, '13:00', '14:00', 'pausa',  'op-assistente'),
('ol-assis-lun-pm', 1, '14:00', '19:00', 'lavoro', 'op-assistente'),
('ol-assis-mar-am', 2, '08:00', '13:00', 'lavoro', 'op-assistente'),
('ol-assis-mar-pa', 2, '13:00', '14:00', 'pausa',  'op-assistente'),
('ol-assis-mar-pm', 2, '14:00', '19:00', 'lavoro', 'op-assistente'),
('ol-assis-mer-am', 3, '08:00', '13:00', 'lavoro', 'op-assistente'),
('ol-assis-mer-pa', 3, '13:00', '14:00', 'pausa',  'op-assistente'),
('ol-assis-mer-pm', 3, '14:00', '19:00', 'lavoro', 'op-assistente'),
('ol-assis-gio-am', 4, '08:00', '13:00', 'lavoro', 'op-assistente'),
('ol-assis-gio-pa', 4, '13:00', '14:00', 'pausa',  'op-assistente'),
('ol-assis-gio-pm', 4, '14:00', '19:00', 'lavoro', 'op-assistente'),
('ol-assis-ven-am', 5, '08:00', '13:00', 'lavoro', 'op-assistente'),
('ol-assis-ven-pa', 5, '13:00', '14:00', 'pausa',  'op-assistente'),
('ol-assis-ven-pm', 5, '14:00', '19:00', 'lavoro', 'op-assistente'),
('ol-assis-sab-am', 6, '08:00', '13:00', 'lavoro', 'op-assistente');

-- DR.SSA ROMANO (ortodontista) — Lun,Gio 09:00-13:00/14:30-18:00, Sab 09:00-13:00
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-ortod-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-ortod'),
('ol-ortod-lun-pa', 1, '13:00', '14:30', 'pausa',  'op-ortod'),
('ol-ortod-lun-pm', 1, '14:30', '18:00', 'lavoro', 'op-ortod'),
('ol-ortod-gio-am', 4, '09:00', '13:00', 'lavoro', 'op-ortod'),
('ol-ortod-gio-pa', 4, '13:00', '14:30', 'pausa',  'op-ortod'),
('ol-ortod-gio-pm', 4, '14:30', '18:00', 'lavoro', 'op-ortod'),
('ol-ortod-sab-am', 6, '09:00', '13:00', 'lavoro', 'op-ortod');

-- ── CLIENTI (pazienti) ────────────────────────────────────────────
DELETE FROM clienti WHERE id LIKE 'cli-odo-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-odo-01', 'Roberto',   'Esposito',  '3351234801', 'rob.esposito@email.it',  '1972-03-18', 1, 28, 1, 'Paziente storico VIP. Impianto mandibola sx completato 2025. Controllo semestrale. Nessuna allergia'),
('cli-odo-02', 'Francesca', 'De Luca',   '3351234802', 'fra.deluca@email.it',    '1988-07-04', 1, 12, 0, 'In terapia ortodontica con Dr.ssa Romano. Bracket fissi applicati gen 2026. Allergia penicillina'),
('cli-odo-03', 'Matteo',    'Santoro',   '3351234803', 'matteo.s@email.it',      '1995-11-22', 1,  5, 0, 'Carie multiple premolari. Ansioso dal dentista → anestesia topica raccomandata prima dell''iniezione'),
('cli-odo-04', 'Luisa',     'Ferrara',   '3351234804', 'luisa.ferrara@email.it', '1960-05-30', 1, 35, 1, 'Protesi parziale superiore. VIP da 15 anni. Diabetica tipo 2 → guarigione più lenta post-estrazioni'),
('cli-odo-05', 'Simone',    'Greco',     '3351234805', 'simone.g@email.it',      '1985-09-14', 1,  8, 0, 'Sbiancamento completato feb 2026. Igiene ogni 6 mesi. Bruxismo → portatore di bite notturno'),
('cli-odo-06', 'Patrizia',  'Vitale',    '3351234806', 'pat.vitale@email.it',    '1978-01-25', 0,  3, 0, 'Prima visita mar 2026. Piano terapeutico: 2 otturazioni + igiene. In gravidanza (7° mese) → evitare rx'),
('cli-odo-07', 'Claudio',   'Russo',     '3351234807', 'claudio.russo@email.it', '1968-08-11', 1, 20, 1, 'Parodontite trattata 2024. VIP. In terapia con anticoagulanti (warfarin) → INR da verificare pre-estrazioni'),
('cli-odo-08', 'Elena',     'Lombardi',  '3351234808', 'elena.l@email.it',       '1992-04-03', 1,  6, 0, 'Consulto ortodonzia per diastema frontale. Interessata ad allineatori invisibili. Nessuna controindicazione');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- Giovedì 3 Aprile: giornata PIENA su Dr. Marchetti (test waitlist)
DELETE FROM appuntamenti WHERE id LIKE 'apt-odo-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-odo-001', 'cli-odo-01', 'srv-visita-controllo', 'op-marchetti',  '2026-03-31T08:30:00', '2026-03-31T09:00:00',  30, 'confermato',   50.00,   50.00, 'Controllo semestrale + sondaggio parodontale',           'whatsapp'),
('apt-odo-002', 'cli-odo-05', 'srv-igiene-dentale',   'op-igienista',  '2026-03-31T09:00:00', '2026-03-31T09:45:00',  45, 'confermato',   80.00,   80.00, 'Igiene semestrale. Rinforzo istruzioni bite notturno',   'voice'),
('apt-odo-003', 'cli-odo-08', 'srv-orto-consulto',    'op-ortod',      '2026-03-31T09:00:00', '2026-03-31T09:45:00',  45, 'confermato',   80.00,   80.00, 'Prima visita ortodontica. Valutazione allineatori',      'voice'),
('apt-odo-004', 'cli-odo-03', 'srv-otturazione',      'op-marchetti',  '2026-03-31T10:00:00', '2026-03-31T10:45:00',  45, 'confermato',  100.00,  100.00, 'Otturazione premolare inf sx. Anestesia topica prima',   'whatsapp'),
('apt-odo-005', 'cli-odo-07', 'srv-panoramica',       'op-assistente', '2026-03-31T11:00:00', '2026-03-31T11:15:00',  15, 'confermato',   40.00,   40.00, 'OPT di controllo post-parodontite',                      'manuale'),
('apt-odo-006', 'cli-odo-02', 'srv-visita-controllo', 'op-ortod',      '2026-03-31T14:30:00', '2026-03-31T15:00:00',  30, 'confermato',   50.00,   50.00, 'Controllo mensile apparecchio. Cambio elastici',          'whatsapp'),
-- Martedì 1 Aprile
('apt-odo-007', 'cli-odo-07', 'srv-visita-controllo', 'op-marchetti',  '2026-04-01T08:30:00', '2026-04-01T09:00:00',  30, 'confermato',   50.00,   50.00, 'Visita parodontale follow-up. Verificare INR pre-seduta', 'whatsapp'),
('apt-odo-008', 'cli-odo-04', 'srv-igiene-dentale',   'op-igienista',  '2026-04-01T09:00:00', '2026-04-01T09:45:00',  45, 'confermato',   80.00,   80.00, 'Igiene attorno protesi parziale. Attenzione gengive',    'voice'),
('apt-odo-009', 'cli-odo-01', 'srv-corona',           'op-marchetti',  '2026-04-01T10:00:00', '2026-04-01T11:00:00',  60, 'confermato',  600.00,  600.00, 'Cementazione corona ceramica premolare sx definitiva',   'manuale'),
('apt-odo-010', 'cli-odo-05', 'srv-visita-controllo', 'op-marchetti',  '2026-04-01T14:30:00', '2026-04-01T15:00:00',  30, 'confermato',   50.00,   50.00, 'Controllo post-sbiancamento + valutazione bite',          'whatsapp'),
-- Mercoledì 2 Aprile
('apt-odo-011', 'cli-odo-06', 'srv-igiene-dentale',   'op-igienista',  '2026-04-02T09:00:00', '2026-04-02T09:45:00',  45, 'confermato',   80.00,   80.00, 'Igiene paziente in gravidanza. No rx. Strumentazione manuale', 'voice'),
('apt-odo-012', 'cli-odo-03', 'srv-devitalizzazione', 'op-marchetti',  '2026-04-02T10:00:00', '2026-04-02T11:30:00',  90, 'confermato',  250.00,  250.00, 'Devitalizzazione molare inf dx. Seduta unica monoradicolare', 'whatsapp'),
('apt-odo-013', 'cli-odo-04', 'srv-protesi-mobile',   'op-marchetti',  '2026-04-02T14:30:00', '2026-04-02T15:30:00',  60, 'confermato',  800.00,  800.00, 'Prova protesi parziale superiore. Aggiustamento occlusione', 'manuale'),
-- Giovedì 3 Aprile (PIENO Dr. Marchetti — test waitlist)
('apt-odo-014', 'cli-odo-01', 'srv-impianto',         'op-marchetti',  '2026-04-03T08:30:00', '2026-04-03T10:00:00',  90, 'confermato', 1500.00, 1500.00, 'Inserimento impianto molare sup dx. Fase chirurgica',    'whatsapp'),
('apt-odo-015', 'cli-odo-07', 'srv-estraz-semplice',  'op-marchetti',  '2026-04-03T10:30:00', '2026-04-03T11:00:00',  30, 'confermato',   80.00,   80.00, 'Estrazione radice residua. INR 2.1 OK per procedura',    'telefono'),
('apt-odo-016', 'cli-odo-02', 'srv-visita-controllo', 'op-ortod',      '2026-04-03T09:00:00', '2026-04-03T09:30:00',  30, 'confermato',   50.00,   50.00, 'Controllo ortodontico mensile. Attivazione arco',        'whatsapp'),
('apt-odo-017', 'cli-odo-08', 'srv-orto-consulto',    'op-ortod',      '2026-04-03T10:00:00', '2026-04-03T10:45:00',  45, 'confermato',   80.00,   80.00, 'Secondo consulto: presentazione piano allineatori',      'voice'),
('apt-odo-018', 'cli-odo-05', 'srv-sbiancamento',     'op-igienista',  '2026-04-03T09:00:00', '2026-04-03T10:00:00',  60, 'confermato',  300.00,  300.00, 'Sbiancamento in studio con lampada LED. Denti asciutti', 'whatsapp'),
('apt-odo-019', 'cli-odo-06', 'srv-otturazione',      'op-marchetti',  '2026-04-03T14:30:00', '2026-04-03T15:15:00',  45, 'confermato',  100.00,  100.00, 'Otturazione incisivo lat sup dx. In gravidanza → no rx', 'whatsapp'),
-- Venerdì 4 Aprile
('apt-odo-020', 'cli-odo-04', 'srv-visita-controllo', 'op-marchetti',  '2026-04-04T08:30:00', '2026-04-04T09:00:00',  30, 'confermato',   50.00,   50.00, 'Consegna protesi definitiva + istruzioni igiene',        'manuale');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-odo-01', 'Check-Up Completo',        'Visita controllo + Panoramica + Igiene dentale (-10%)',     153.00, 170.00, 3, NULL,              60, 1),
('pkg-odo-02', 'Pacchetto Igiene Annuale', '2 igieni professionali + 2 visite controllo (-15%)',        221.00, 260.00, 4, 'srv-igiene-dentale', 365, 1);

-- ── FORNITORI (suppliers) ─────────────────────────────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-odo-%';
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-odo-01', 'DentalPro Italia Srl',       'ordini@dentalpro.it',       '02 4521 8900', 'Via Buonarroti 28',     'Milano',  '20145', '07812340152', 'active', '2026-01-10 09:00:00', '2026-03-15 10:00:00'),
('sup-odo-02', 'TechnoLab Protesi Milano',   'commerciale@technolab.it',  '02 8734 5600', 'Via Padova 112',        'Milano',  '20127', '04523190963', 'active', '2026-01-10 09:00:00', '2026-03-01 09:00:00'),
('sup-odo-03', 'RadioDent Diagnostica Srl',  'info@radiodent.it',         '02 6609 1234', 'Via Washington 65',     'Milano',  '20146', '09871230154', 'active', '2026-02-01 10:00:00', '2026-03-20 11:30:00');

-- ── FATTURE + RIGHE ───────────────────────────────────────────────
-- 5 fatture emesse a pazienti (TD01, IVA 22%, stato pagata)
-- Numerazione FV001-2026 → FV005-2026
DELETE FROM fatture_righe WHERE fattura_id LIKE 'fatt-odo-%';
DELETE FROM fatture WHERE id LIKE 'fatt-odo-%';

INSERT INTO fatture (id, numero, anno, numero_completo, tipo_documento, data_emissione, data_scadenza,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione, cliente_codice_sdi,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato,
    causale, note_interne) VALUES
-- FV001/2026 — Roberto Esposito: corona
('fatt-odo-001', 1, 2026, 'FV001/2026', 'TD01', '2026-03-10', '2026-03-25',
    'cli-odo-01', 'Roberto Esposito', NULL, 'SPTRRT72C18F839K',
    'Via Monforte 8', '20122', 'Milano', 'MI', 'IT', '0000000',
    491.80, 108.20, 600.00,
    'MP05', 'TP02', 'pagata',
    'Prestazione odontoiatrica: Corona in ceramica premolare sx', NULL),
-- FV002/2026 — Simone Greco: sbiancamento
('fatt-odo-002', 2, 2026, 'FV002/2026', 'TD01', '2026-03-15', '2026-03-30',
    'cli-odo-05', 'Simone Greco', NULL, 'GRCSNE85P14L219Z',
    'Via Vigevano 34', '20144', 'Milano', 'MI', 'IT', '0000000',
    245.90, 54.10, 300.00,
    'MP08', 'TP02', 'pagata',
    'Prestazione odontoiatrica: Sbiancamento professionale in studio', NULL),
-- FV003/2026 — Luisa Ferrara: igiene + visita
('fatt-odo-003', 3, 2026, 'FV003/2026', 'TD01', '2026-03-18', '2026-04-02',
    'cli-odo-04', 'Luisa Ferrara', NULL, 'FRRLSU60E70F839N',
    'Corso Magenta 52', '20123', 'Milano', 'MI', 'IT', '0000000',
    106.56,  23.44, 130.00,
    'MP01', 'TP02', 'pagata',
    'Prestazione odontoiatrica: Igiene dentale + Visita controllo', NULL),
-- FV004/2026 — Matteo Santoro: devitalizzazione + otturazione
('fatt-odo-004', 4, 2026, 'FV004/2026', 'TD01', '2026-03-25', '2026-04-09',
    'cli-odo-03', 'Matteo Santoro', NULL, 'SNTMTT95S22L219P',
    'Via Cenisio 14', '20154', 'Milano', 'MI', 'IT', '0000000',
    286.89,  63.11, 350.00,
    'MP01', 'TP02', 'pagata',
    'Prestazione odontoiatrica: Devitalizzazione + Otturazione composita', NULL),
-- FV005/2026 — Claudio Russo: visita + panoramica
('fatt-odo-005', 5, 2026, 'FV005/2026', 'TD01', '2026-03-28', '2026-04-12',
    'cli-odo-07', 'Claudio Russo', NULL, 'RSSCLD68M11H501Y',
    'Via Porpora 91', '20131', 'Milano', 'MI', 'IT', '0000000',
     73.77,  16.23,  90.00,
    'MP05', 'TP02', 'pagata',
    'Prestazione odontoiatrica: Visita controllo parodontale + Panoramica OPT', NULL);

-- Righe fattura FV001/2026
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
('fr-odo-001-1', 'fatt-odo-001', 1, 'Corona in ceramica su premolare sx devitalizzato', 1.0, 'PZ', 491.80, 0, 0, 491.80, 22.0, 'srv-corona');

-- Righe fattura FV002/2026
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
('fr-odo-002-1', 'fatt-odo-002', 1, 'Sbiancamento professionale in studio con lampada LED', 1.0, 'PZ', 245.90, 0, 0, 245.90, 22.0, 'srv-sbiancamento');

-- Righe fattura FV003/2026
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
('fr-odo-003-1', 'fatt-odo-003', 1, 'Igiene dentale professionale — detartrasi + lucidatura', 1.0, 'PZ', 65.57, 0, 0, 65.57, 22.0, 'srv-igiene-dentale'),
('fr-odo-003-2', 'fatt-odo-003', 2, 'Visita di controllo con sondaggio parodontale',          1.0, 'PZ', 40.99, 0, 0, 40.99, 22.0, 'srv-visita-controllo');

-- Righe fattura FV004/2026
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
('fr-odo-004-1', 'fatt-odo-004', 1, 'Devitalizzazione molare inf dx — trattamento endodontico',  1.0, 'PZ', 204.92, 0, 0, 204.92, 22.0, 'srv-devitalizzazione'),
('fr-odo-004-2', 'fatt-odo-004', 2, 'Otturazione in composita premolare inf sx',                 1.0, 'PZ',  81.97, 0, 0,  81.97, 22.0, 'srv-otturazione');

-- Righe fattura FV005/2026
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
('fr-odo-005-1', 'fatt-odo-005', 1, 'Visita parodontale di controllo follow-up',  1.0, 'PZ', 40.98, 0, 0, 40.98, 22.0, 'srv-visita-controllo'),
('fr-odo-005-2', 'fatt-odo-005', 2, 'Radiografia panoramica digitale OPT',        1.0, 'PZ', 32.79, 0, 0, 32.79, 22.0, 'srv-panoramica');

-- ── INCASSI (10 — mix contanti/carta/bonifico) ────────────────────
DELETE FROM incassi WHERE id LIKE 'inc-odo-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, fattura_id, descrizione, categoria, operatore_id, data_incasso) VALUES
-- Incassi fatturati (collegati a fatture)
('inc-odo-001',  600.00, 'bonifico',  'cli-odo-01', NULL,          'fatt-odo-001', 'Saldo corona ceramica premolare sx (preparazione mar 10)',  'servizio', 'op-assistente', '2026-03-10 18:00:00'),
('inc-odo-002',  300.00, 'carta',     'cli-odo-05', NULL,          'fatt-odo-002', 'Saldo sbiancamento in studio',                          'servizio', 'op-assistente', '2026-03-15 17:30:00'),
('inc-odo-003',  130.00, 'contanti',  'cli-odo-04', 'apt-odo-008', 'fatt-odo-003', 'Igiene semestrale + visita controllo',                  'servizio', 'op-assistente', '2026-03-18 13:00:00'),
('inc-odo-004',  350.00, 'contanti',  'cli-odo-03', 'apt-odo-012', 'fatt-odo-004', 'Devitalizzazione + otturazione composita',              'servizio', 'op-marchetti',  '2026-03-25 18:30:00'),
('inc-odo-005',   90.00, 'bonifico',  'cli-odo-07', 'apt-odo-007', 'fatt-odo-005', 'Visita parodontale + OPT di controllo',                 'servizio', 'op-assistente', '2026-03-28 12:30:00'),
-- Incassi da appuntamenti della settimana (non ancora fatturati)
('inc-odo-006',   50.00, 'contanti',  'cli-odo-01', 'apt-odo-001', NULL,           'Visita controllo semestrale con sondaggio',             'servizio', 'op-assistente', '2026-03-31 09:00:00'),
('inc-odo-007',   80.00, 'carta',     'cli-odo-05', 'apt-odo-002', NULL,           'Igiene dentale semestrale',                             'servizio', 'op-igienista',  '2026-03-31 09:50:00'),
('inc-odo-008',   80.00, 'carta',     'cli-odo-08', 'apt-odo-003', NULL,           'Consulto ortodontico primo accesso',                    'servizio', 'op-ortod',      '2026-03-31 09:50:00'),
('inc-odo-009',  100.00, 'contanti',  'cli-odo-03', 'apt-odo-004', NULL,           'Otturazione composita premolare inf sx',                'servizio', 'op-marchetti',  '2026-03-31 10:50:00'),
('inc-odo-010',  600.00, 'bonifico',  'cli-odo-01', 'apt-odo-009', NULL,           'Acconto impianto mandibola — seduta chirurgica apr 3', 'servizio', 'op-assistente', '2026-04-01 09:00:00');

PRAGMA foreign_keys = ON;
