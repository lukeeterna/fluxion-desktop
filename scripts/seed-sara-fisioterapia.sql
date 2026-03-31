-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: STUDIO FISIOTERAPIA
-- Sotto-verticale: Fisioterapia (macro: medico)
-- Per test voce Sara su iMac — settimana 31 Mar - 5 Apr 2026
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita',      'Studio Fisioterapia Salus'),
('categoria_attivita', 'fisioterapia'),
('macro_categoria',    'medico'),
('micro_categoria',    'fisioterapia'),
('indirizzo_completo', 'Via Colombo 18, 20135 Milano'),
('orario_apertura',    '08:30'),
('orario_chiusura',    '19:00'),
('giorni_lavorativi',  '["lun","mar","mer","gio","ven","sab"]'),
('whatsapp_number',    '3456789012'),
('whatsapp_attivo',    'true');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-prima-visita',   'Prima Visita Fisioterapica',   'Valutazione funzionale completa con anamnesi e piano terapeutico',  60.00, 45, 10, 'visite',        '#6366f1', 1,  1),
('srv-fisio-45',       'Seduta Fisioterapia',          'Seduta riabilitativa individuale 45 minuti',                        50.00, 45,  5, 'riabilitazione','#3b82f6', 1,  2),
('srv-terapia-man',    'Terapia Manuale',              'Mobilizzazione articolare e tecniche manuali certificate',          55.00, 45,  5, 'riabilitazione','#3b82f6', 1,  3),
('srv-massoterapia',   'Massoterapia',                 'Massaggio terapeutico decontratturante e rilassante',               45.00, 40,  5, 'massaggi',      '#10b981', 1,  4),
('srv-tecar',          'Tecarterapia',                 'Terapia diatermia capacitiva e resistiva (TECAR)',                  40.00, 30,  5, 'strumentale',   '#f59e0b', 1,  5),
('srv-ultrasuoni',     'Ultrasuoni',                   'Terapia con ultrasuoni per infiammazioni e contratture',            30.00, 20,  5, 'strumentale',   '#f59e0b', 1,  6),
('srv-laser',          'Laser Terapia',                'Laserterapia antalgica e biostimolante',                            35.00, 20,  5, 'strumentale',   '#f59e0b', 1,  7),
('srv-onde-urto',      'Onde d''Urto',                 'Terapia con onde d''urto per tendinopatie e calcificazioni',        50.00, 30,  5, 'strumentale',   '#ef4444', 1,  8),
('srv-riabilitazione', 'Riabilitazione Post-Operatoria','Percorso riabilitativo post-chirurgico personalizzato',            60.00, 60, 10, 'riabilitazione','#ec4899', 1,  9),
('srv-posturale',      'Rieducazione Posturale',       'Correzione postura globale con tecniche RPG/Mézières',             55.00, 50,  5, 'postura',       '#8b5cf6', 1, 10),
('srv-kinesio',        'Kinesitaping',                 'Applicazione bendaggio funzionale kinesio tape',                    25.00, 15,  5, 'bendaggi',      '#10b981', 1, 11),
('srv-linfodren',      'Linfodrenaggio Manuale',       'Drenaggio linfatico manuale metodo Vodder',                        60.00, 50,  5, 'massaggi',      '#10b981', 1, 12),
('srv-elettro',        'Elettrostimolazione',          'TENS, interferenziale e correnti galvaniche antidolorifiche',       30.00, 20,  5, 'strumentale',   '#f59e0b', 1, 13),
('srv-val-posturale',  'Valutazione Posturale',        'Analisi posturale strumentale completa con refertazione',          70.00, 60, 10, 'visite',        '#6366f1', 1, 14);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva) VALUES
('op-martini',  'Dr.ssa Elena', 'Martini',  'admin',     '#6366f1', 1, '["fisioterapia","terapia manuale","riabilitazione post-operatoria","postura"]', 'Titolare, fisioterapista abilitata con 18 anni esperienza. Specializzata in riabilitazione ortopedica'),
('op-ferrari',  'Dr. Matteo',   'Ferrari',  'operatore', '#3b82f6', 1, '["fisioterapia","onde d urto","tecarterapia","ultrasuoni"]',                     'Fisioterapista specializzato in terapie strumentali e sport medicine'),
('op-conti',    'Dr.ssa Sara',  'Conti',    'operatore', '#10b981', 1, '["linfodrenaggio","massoterapia","kinesitaping","postura"]',                      'Fisioterapista esperta in linfodrenaggio Vodder e terapia manuale'),
('op-russo',    'Dr. Andrea',   'Russo',    'operatore', '#f59e0b', 1, '["riabilitazione","elettrostimolazione","laser","rieducazione posturale"]',       'Fisioterapista specializzato in riabilitazione neurologica e post-operatoria');

-- ── ORARI LAVORO PER OPERATORE ────────────────────────────────────
-- Studio medico: Lun-Ven 08:30-12:30 / 14:30-19:00, Sab mattina
-- Dr.ssa Martini (titolare): Lun-Ven full + Sab mattina
-- Dr. Ferrari: Lun-Ven (no Sab, strumentali richiedono attrezzatura dedicata)
-- Dr.ssa Conti: Lun,Mer,Ven,Sab (part-time specialista)
-- Dr. Andrea Russo: Mar-Sab (copre turno pomeridiano esteso)

DELETE FROM orari_lavoro WHERE operatore_id IN ('op-martini','op-ferrari','op-conti','op-russo');

-- DR.SSA MARTINI (titolare) — Lun-Ven 08:30-12:30 / 14:30-19:00, Sab 08:30-12:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-fis-martini-lun-am', 1, '08:30', '12:30', 'lavoro', 'op-martini'),
('ol-fis-martini-lun-pa', 1, '12:30', '14:30', 'pausa',  'op-martini'),
('ol-fis-martini-lun-pm', 1, '14:30', '19:00', 'lavoro', 'op-martini'),
('ol-fis-martini-mar-am', 2, '08:30', '12:30', 'lavoro', 'op-martini'),
('ol-fis-martini-mar-pa', 2, '12:30', '14:30', 'pausa',  'op-martini'),
('ol-fis-martini-mar-pm', 2, '14:30', '19:00', 'lavoro', 'op-martini'),
('ol-fis-martini-mer-am', 3, '08:30', '12:30', 'lavoro', 'op-martini'),
('ol-fis-martini-mer-pa', 3, '12:30', '14:30', 'pausa',  'op-martini'),
('ol-fis-martini-mer-pm', 3, '14:30', '19:00', 'lavoro', 'op-martini'),
('ol-fis-martini-gio-am', 4, '08:30', '12:30', 'lavoro', 'op-martini'),
('ol-fis-martini-gio-pa', 4, '12:30', '14:30', 'pausa',  'op-martini'),
('ol-fis-martini-gio-pm', 4, '14:30', '19:00', 'lavoro', 'op-martini'),
('ol-fis-martini-ven-am', 5, '08:30', '12:30', 'lavoro', 'op-martini'),
('ol-fis-martini-ven-pa', 5, '12:30', '14:30', 'pausa',  'op-martini'),
('ol-fis-martini-ven-pm', 5, '14:30', '19:00', 'lavoro', 'op-martini'),
('ol-fis-martini-sab-am', 6, '08:30', '12:30', 'lavoro', 'op-martini');

-- DR. FERRARI — Lun-Ven 08:30-12:30 / 14:30-19:00 (no Sab)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-fis-ferrari-lun-am', 1, '08:30', '12:30', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-lun-pa', 1, '12:30', '14:30', 'pausa',  'op-ferrari'),
('ol-fis-ferrari-lun-pm', 1, '14:30', '19:00', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-mar-am', 2, '08:30', '12:30', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-mar-pa', 2, '12:30', '14:30', 'pausa',  'op-ferrari'),
('ol-fis-ferrari-mar-pm', 2, '14:30', '19:00', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-mer-am', 3, '08:30', '12:30', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-mer-pa', 3, '12:30', '14:30', 'pausa',  'op-ferrari'),
('ol-fis-ferrari-mer-pm', 3, '14:30', '19:00', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-gio-am', 4, '08:30', '12:30', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-gio-pa', 4, '12:30', '14:30', 'pausa',  'op-ferrari'),
('ol-fis-ferrari-gio-pm', 4, '14:30', '19:00', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-ven-am', 5, '08:30', '12:30', 'lavoro', 'op-ferrari'),
('ol-fis-ferrari-ven-pa', 5, '12:30', '14:30', 'pausa',  'op-ferrari'),
('ol-fis-ferrari-ven-pm', 5, '14:30', '19:00', 'lavoro', 'op-ferrari');

-- DR.SSA CONTI (part-time) — Lun,Mer,Ven 09:00-13:00 / 14:30-18:00, Sab 09:00-12:30
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-fis-conti-lun-am', 1, '09:00', '13:00', 'lavoro', 'op-conti'),
('ol-fis-conti-lun-pa', 1, '13:00', '14:30', 'pausa',  'op-conti'),
('ol-fis-conti-lun-pm', 1, '14:30', '18:00', 'lavoro', 'op-conti'),
('ol-fis-conti-mer-am', 3, '09:00', '13:00', 'lavoro', 'op-conti'),
('ol-fis-conti-mer-pa', 3, '13:00', '14:30', 'pausa',  'op-conti'),
('ol-fis-conti-mer-pm', 3, '14:30', '18:00', 'lavoro', 'op-conti'),
('ol-fis-conti-ven-am', 5, '09:00', '13:00', 'lavoro', 'op-conti'),
('ol-fis-conti-ven-pa', 5, '13:00', '14:30', 'pausa',  'op-conti'),
('ol-fis-conti-ven-pm', 5, '14:30', '18:00', 'lavoro', 'op-conti'),
('ol-fis-conti-sab-am', 6, '09:00', '12:30', 'lavoro', 'op-conti');

-- DR. RUSSO — Mar-Sab 08:30-12:30 / 14:30-19:00 (lun libero)
INSERT OR REPLACE INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id) VALUES
('ol-fis-russo-mar-am', 2, '08:30', '12:30', 'lavoro', 'op-russo'),
('ol-fis-russo-mar-pa', 2, '12:30', '14:30', 'pausa',  'op-russo'),
('ol-fis-russo-mar-pm', 2, '14:30', '19:00', 'lavoro', 'op-russo'),
('ol-fis-russo-mer-am', 3, '08:30', '12:30', 'lavoro', 'op-russo'),
('ol-fis-russo-mer-pa', 3, '12:30', '14:30', 'pausa',  'op-russo'),
('ol-fis-russo-mer-pm', 3, '14:30', '19:00', 'lavoro', 'op-russo'),
('ol-fis-russo-gio-am', 4, '08:30', '12:30', 'lavoro', 'op-russo'),
('ol-fis-russo-gio-pa', 4, '12:30', '14:30', 'pausa',  'op-russo'),
('ol-fis-russo-gio-pm', 4, '14:30', '19:00', 'lavoro', 'op-russo'),
('ol-fis-russo-ven-am', 5, '08:30', '12:30', 'lavoro', 'op-russo'),
('ol-fis-russo-ven-pa', 5, '12:30', '14:30', 'pausa',  'op-russo'),
('ol-fis-russo-ven-pm', 5, '14:30', '19:00', 'lavoro', 'op-russo'),
('ol-fis-russo-sab-am', 6, '08:30', '12:30', 'lavoro', 'op-russo');

-- ── CLIENTI (pazienti) ────────────────────────────────────────────
-- Note contengono: diagnosi, zona trattamento, prescrizione medica
DELETE FROM clienti WHERE id LIKE 'cli-fis-%';
INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, consenso_whatsapp, loyalty_visits, is_vip, note) VALUES
('cli-fis-01', 'Roberto',   'Colombo',   '3381234101', 'r.colombo@email.it',   '1968-05-14', 1, 22, 1, 'Diagnosi: ernia L4-L5. Zona: lombare. Cicli fisioterapia 2x/anno. Prescrizione medico base. Evitare flessione brusca'),
('cli-fis-02', 'Francesca', 'Moretti',   '3381234102', 'fra.moretti@email.it', '1985-09-03', 1, 10, 0, 'Diagnosi: tendinite rotatoria spalla dx. Zona: spalla destra. Post-operatoria artroscopia gen 2026. Prescrizione ortopedico Dr. Bianchi'),
('cli-fis-03', 'Luca',      'Santoro',   '3381234103', 'luca.s@email.it',      '1978-11-22', 1, 15, 0, 'Diagnosi: cervicalgia cronica + protrusione C5-C6. Zona: cervicale. Farmaci: ibuprofene SOS. Controllo mensile neurologia'),
('cli-fis-04', 'Maria',     'Esposito',  '3381234104', 'maria.e@email.it',     '1992-02-08', 1,  6, 0, 'Diagnosi: distorsione caviglia grado II. Zona: caviglia sinistra. Infortunio calcio 15/03/2026. Atleta amatoriale. Obiettivo: riprendere attività sportiva'),
('cli-fis-05', 'Giorgio',   'Ferrara',   '3381234105', 'g.ferrara@email.it',   '1955-07-19', 1, 35, 1, 'Diagnosi: gonartrosi bilaterale grado III. Zona: ginocchia. Paziente storico VIP. Farmaci: paracetamolo 1g. In lista attesa protesi ginocchio sx'),
('cli-fis-06', 'Alessia',   'Romano',    '3381234106', 'ale.romano@email.it',  '1990-04-25', 1,  8, 0, 'Diagnosi: lombalgia acuta + sciatica dx (L5-S1). Zona: lombare e arto inferiore dx. Prima visita gen 2026. Professione: infermiera (lavoro in piedi)'),
('cli-fis-07', 'Tommaso',   'Ricci',     '3381234107', 't.ricci@email.it',     '1975-12-30', 1, 18, 0, 'Diagnosi: epicondilite laterale gomito dx (gomito del tennista). Zona: gomito destro. Giocatore tennis agonistico. Prescrizione: fisioterapia + onde d urto'),
('cli-fis-08', 'Valentina', 'Galli',     '3381234108', 'vale.galli@email.it',  '1988-08-15', 1,  4, 0, 'Diagnosi: scoliosi funzionale + ipercifosi dorsale. Zona: colonna vertebrale. Prescrizione ortopedica: rieducazione posturale RPG. Sedentaria, lavoro ufficio');

-- ── APPUNTAMENTI (settimana 31 Mar - 5 Apr 2026) ─────────────────
-- Giovedì 3 Aprile: giornata PIENA — per test waitlist Sara
DELETE FROM appuntamenti WHERE id LIKE 'apt-fis-%';
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- Lunedì 31 Marzo
('apt-fis-001', 'cli-fis-01', 'srv-fisio-45',     'op-martini', '2026-03-31T08:30:00', '2026-03-31T09:15:00', 45, 'confermato', 50.00, 50.00, 'Seduta lombare - ciclo 8/10',              'whatsapp'),
('apt-fis-002', 'cli-fis-03', 'srv-terapia-man',  'op-martini', '2026-03-31T09:30:00', '2026-03-31T10:15:00', 45, 'confermato', 55.00, 55.00, 'Mobilizzazione cervicale C5-C6',          'voice'),
('apt-fis-003', 'cli-fis-07', 'srv-onde-urto',    'op-ferrari', '2026-03-31T08:30:00', '2026-03-31T09:00:00', 30, 'confermato', 50.00, 50.00, 'Onde d urto gomito dx - seduta 3/5',      'whatsapp'),
('apt-fis-004', 'cli-fis-05', 'srv-tecar',        'op-ferrari', '2026-03-31T09:30:00', '2026-03-31T10:00:00', 30, 'confermato', 40.00, 40.00, 'Tecarterapia ginocchia bilaterale',       'manuale'),
('apt-fis-005', 'cli-fis-08', 'srv-posturale',    'op-conti',   '2026-03-31T09:00:00', '2026-03-31T09:50:00', 50, 'confermato', 55.00, 55.00, 'RPG seduta 2/8 - scoliosi + cifosi',      'voice'),
('apt-fis-006', 'cli-fis-01', 'srv-elettro',      'op-martini', '2026-03-31T14:30:00', '2026-03-31T14:50:00', 20, 'confermato', 30.00, 30.00, 'TENS antidolorifico post-seduta',         'whatsapp'),
-- Martedì 1 Aprile
('apt-fis-007', 'cli-fis-02', 'srv-riabilitazione','op-russo',  '2026-04-01T08:30:00', '2026-04-01T09:30:00', 60, 'confermato', 60.00, 60.00, 'Riab. post-artroscopia spalla dx - 5/12', 'whatsapp'),
('apt-fis-008', 'cli-fis-04', 'srv-fisio-45',     'op-russo',   '2026-04-01T09:45:00', '2026-04-01T10:30:00', 45, 'confermato', 50.00, 50.00, 'Riabilitazione caviglia - progressione',  'voice'),
('apt-fis-009', 'cli-fis-06', 'srv-prima-visita', 'op-martini', '2026-04-01T08:30:00', '2026-04-01T09:15:00', 45, 'confermato', 60.00, 60.00, 'Prima visita - lombalgia acuta sciatica', 'voice'),
('apt-fis-010', 'cli-fis-07', 'srv-ultrasuoni',   'op-ferrari', '2026-04-01T14:30:00', '2026-04-01T14:50:00', 20, 'confermato', 30.00, 30.00, 'Ultrasuoni gomito dx - antinfiammatorio', 'whatsapp'),
-- Mercoledì 2 Aprile
('apt-fis-011', 'cli-fis-03', 'srv-laser',        'op-ferrari', '2026-04-02T08:30:00', '2026-04-02T08:50:00', 20, 'confermato', 35.00, 35.00, 'Laser cervicale - biostimolazione',       'whatsapp'),
('apt-fis-012', 'cli-fis-05', 'srv-massoterapia', 'op-conti',   '2026-04-02T09:00:00', '2026-04-02T09:40:00', 40, 'confermato', 45.00, 45.00, 'Massoterapia arti inferiori pre-seduta',  'manuale'),
('apt-fis-013', 'cli-fis-08', 'srv-val-posturale','op-martini', '2026-04-02T08:30:00', '2026-04-02T09:30:00', 60, 'confermato', 70.00, 70.00, 'Rivalutazione posturale strumentale',     'whatsapp'),
('apt-fis-014', 'cli-fis-06', 'srv-fisio-45',     'op-russo',   '2026-04-02T14:30:00', '2026-04-02T15:15:00', 45, 'confermato', 50.00, 50.00, 'Fisioterapia lombo-sciatica - seduta 2',  'voice'),
-- Giovedì 3 Aprile (PIENO — test waitlist Sara)
('apt-fis-015', 'cli-fis-01', 'srv-fisio-45',     'op-martini', '2026-04-03T08:30:00', '2026-04-03T09:15:00', 45, 'confermato', 50.00, 50.00, 'Seduta lombare - ciclo 9/10',             'whatsapp'),
('apt-fis-016', 'cli-fis-02', 'srv-riabilitazione','op-russo',  '2026-04-03T08:30:00', '2026-04-03T09:30:00', 60, 'confermato', 60.00, 60.00, 'Riab. spalla - seduta 6/12',              'whatsapp'),
('apt-fis-017', 'cli-fis-07', 'srv-onde-urto',    'op-ferrari', '2026-04-03T08:30:00', '2026-04-03T09:00:00', 30, 'confermato', 50.00, 50.00, 'Onde d urto gomito - seduta 4/5',         'voice'),
('apt-fis-018', 'cli-fis-04', 'srv-kinesio',      'op-conti',   '2026-04-03T09:00:00', '2026-04-03T09:15:00', 15, 'confermato', 25.00, 25.00, 'Kinesitaping caviglia - supporto gara',   'whatsapp'),
('apt-fis-019', 'cli-fis-05', 'srv-tecar',        'op-ferrari', '2026-04-03T14:30:00', '2026-04-03T15:00:00', 30, 'confermato', 40.00, 40.00, 'Tecarterapia ginocchia - mantenimento',   'manuale'),
('apt-fis-020', 'cli-fis-03', 'srv-terapia-man',  'op-martini', '2026-04-03T14:30:00', '2026-04-03T15:15:00', 45, 'confermato', 55.00, 55.00, 'Terapia manuale cervicale - follow-up',   'voice');

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-fis-01', 'Ciclo 10 Sedute',          '10 sedute fisioterapia individuale al prezzo di 9 (-10%)',    450.00, 500.00, 10, 'srv-fisio-45',     90, 1),
('pkg-fis-02', 'Pacchetto Posturale',      'Prima visita + valutazione posturale + 6 sedute RPG (-15%)', 480.00, 565.00,  8, 'srv-posturale',   120, 1),
('pkg-fis-03', 'Percorso Riabilitativo',   'Prima visita + 8 sedute riab. post-op + 2 controlli',        530.00, 620.00, 11, 'srv-riabilitazione', 60, 1);

-- ── SUPPLIERS (fornitori) ─────────────────────────────────────────
DELETE FROM suppliers WHERE id LIKE 'sup-fis-%';
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at) VALUES
('sup-fis-01', 'BTL Italia Srl',            'ordini@btl-italia.it',        '0240703700', 'Via Fantoli 26/10',          'Milano',  '20138', '03445670967', 'active', '2026-01-10T09:00:00', '2026-03-15T10:00:00'),
('sup-fis-02', 'Medi-Store Materiale Medico','info@medistore.it',           '0556541230', 'Via Pratese 140',            'Firenze', '50145', '04123880487', 'active', '2026-01-10T09:00:00', '2026-03-20T11:00:00'),
('sup-fis-03', 'Enraf-Nonius Italia',        'commerciale@enrafnonius.it',  '0248008411', 'Viale Certosa 222',          'Milano',  '20156', '01876540123', 'active', '2026-02-01T09:00:00', '2026-03-25T09:00:00');

-- ── FATTURE (5 fatture con righe, IVA 22%) ────────────────────────
-- Nota: fisioterapia privata soggetta a IVA al 22% (non esente)
-- I servizi in regime SSN sarebbero esenti N4 art.10 DPR 633/72
DELETE FROM fatture WHERE numero_completo LIKE 'FV%/2026' AND numero <= 5;
INSERT INTO fatture (id, numero, anno, numero_completo, tipo_documento, data_emissione, data_scadenza, cliente_id, cliente_denominazione, cliente_codice_fiscale, cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione, cliente_codice_sdi, imponibile_totale, iva_totale, totale_documento, modalita_pagamento, condizioni_pagamento, stato, causale, note_interne) VALUES
('fat-fis-001', 1, 2026, 'FV001/2026', 'TD01', '2026-03-24', '2026-03-24', 'cli-fis-01', 'Roberto Colombo',   'CLMRRT68E14F205X', 'Via Dante 5',        '20121', 'Milano',  'MI', 'IT', '0000000',  81.97, 18.03, 100.00, 'MP01', 'TP02', 'pagata',  'Prestazioni fisioterapiche marzo 2026', NULL),
('fat-fis-002', 2, 2026, 'FV002/2026', 'TD01', '2026-03-25', '2026-04-04', 'cli-fis-05', 'Giorgio Ferrara',   'FRRGRG55L19D969W', 'Piazza Duca 12',     '20129', 'Milano',  'MI', 'IT', '0000000', 106.56, 23.44, 130.00, 'MP08', 'TP02', 'pagata',  'Ciclo tecarterapia + massoterapia',     NULL),
('fat-fis-003', 3, 2026, 'FV003/2026', 'TD01', '2026-03-26', '2026-04-25', 'cli-fis-02', 'Francesca Moretti', 'MRTFNC85P43F205R', 'Via Monti 33',       '20145', 'Milano',  'MI', 'IT', '0000000', 122.95, 27.05, 150.00, 'MP05', 'TP02', 'emessa',  'Riabilitazione post-operatoria spalla', NULL),
('fat-fis-004', 4, 2026, 'FV004/2026', 'TD01', '2026-03-27', '2026-03-27', 'cli-fis-07', 'Tommaso Ricci',     'RCCTMS75T30H501K', 'Via Torino 8',       '20123', 'Milano',  'MI', 'IT', '0000000',  81.97, 18.03, 100.00, 'MP01', 'TP02', 'pagata',  'Onde d urto + ultrasuoni gomito dx',   NULL),
('fat-fis-005', 5, 2026, 'FV005/2026', 'TD01', '2026-03-28', '2026-04-27', 'cli-fis-08', 'Valentina Galli',   'GLLVNT88M55D969Z', 'Via Garibaldi 21',   '20121', 'Milano',  'MI', 'IT', '0000000', 102.46, 22.54, 125.00, 'MP08', 'TP02', 'emessa',  'Rieducazione posturale RPG sedute 1-2', NULL);

-- ── FATTURE RIGHE ────────────────────────────────────────────────
DELETE FROM fatture_righe WHERE fattura_id IN ('fat-fis-001','fat-fis-002','fat-fis-003','fat-fis-004','fat-fis-005');
INSERT INTO fatture_righe (id, fattura_id, numero_linea, descrizione, quantita, unita_misura, prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, servizio_id) VALUES
-- FV001/2026 — Roberto Colombo: 2 sedute fisioterapia (€50×2 = €100 IVA inclusa)
('fr-fis-001-1', 'fat-fis-001', 1, 'Seduta Fisioterapia individuale 45 min',            2.0, 'NR', 40.98, 0, 0, 81.97, 22.0, 'srv-fisio-45'),
-- FV002/2026 — Giorgio Ferrara: 2 tecar + 1 massoterapia (€40×2 + €45 = €125 → €130 ivata)
('fr-fis-002-1', 'fat-fis-002', 1, 'Tecarterapia bilaterale ginocchia 30 min',          2.0, 'NR', 32.79, 0, 0,  65.57, 22.0, 'srv-tecar'),
('fr-fis-002-2', 'fat-fis-002', 2, 'Massoterapia decontratturante arti inferiori 40 min',1.0,'NR', 36.89, 0, 0,  36.89, 22.0, 'srv-massoterapia'),
-- FV003/2026 — Francesca Moretti: 2 sedute riabilitazione post-op (€60×2 = €120 + €30 laser)
('fr-fis-003-1', 'fat-fis-003', 1, 'Riabilitazione Post-Operatoria spalla dx 60 min',  2.0, 'NR', 49.18, 0, 0,  98.36, 22.0, 'srv-riabilitazione'),
('fr-fis-003-2', 'fat-fis-003', 2, 'Laser terapia antalgica spalla 20 min',             1.0, 'NR', 28.69, 0, 0,  28.69, 22.0, 'srv-laser'),
-- FV004/2026 — Tommaso Ricci: 2 onde d'urto + 1 ultrasuoni (€50×2 + €30 = €130 → €100 ivata nota: 2 onde = €100 ivate)
('fr-fis-004-1', 'fat-fis-004', 1, 'Terapia con Onde d''Urto gomito dx 30 min',         2.0, 'NR', 40.98, 0, 0,  81.97, 22.0, 'srv-onde-urto'),
-- FV005/2026 — Valentina Galli: valutazione posturale + prima seduta RPG
('fr-fis-005-1', 'fat-fis-005', 1, 'Valutazione Posturale strumentale con referto 60 min',1.0,'NR',57.38, 0, 0,  57.38, 22.0, 'srv-val-posturale'),
('fr-fis-005-2', 'fat-fis-005', 2, 'Rieducazione Posturale RPG 50 min',                 1.0, 'NR', 45.08, 0, 0,  45.08, 22.0, 'srv-posturale');

-- ── INCASSI (10 incassi mix metodi pagamento) ─────────────────────
DELETE FROM incassi WHERE id LIKE 'inc-fis-%';
INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, fattura_id, descrizione, categoria, operatore_id, data_incasso) VALUES
('inc-fis-001', 100.00, 'contanti', 'cli-fis-01', 'apt-fis-001', 'fat-fis-001', 'Saldo FV001/2026 - 2 sedute fisioterapia',               'servizio', 'op-martini', '2026-03-24T09:30:00'),
('inc-fis-002',  50.00, 'carta',    'cli-fis-05', 'apt-fis-004', NULL,           'Tecarterapia ginocchia bilaterale',                       'servizio', 'op-ferrari', '2026-03-31T10:15:00'),
('inc-fis-003',  55.00, 'carta',    'cli-fis-03', 'apt-fis-002', NULL,           'Terapia manuale cervicale',                               'servizio', 'op-martini', '2026-03-31T10:30:00'),
('inc-fis-004', 130.00, 'carta',    'cli-fis-05', NULL,          'fat-fis-002', 'Saldo FV002/2026 - ciclo tecar + massoterapia',            'pacchetto','op-martini', '2026-03-25T11:00:00'),
('inc-fis-005',  60.00, 'bonifico', 'cli-fis-02', 'apt-fis-007', NULL,           'Riabilitazione post-op spalla - acconto percorso',        'servizio', 'op-russo',   '2026-04-01T09:45:00'),
('inc-fis-006',  60.00, 'contanti', 'cli-fis-06', 'apt-fis-009', NULL,           'Prima visita fisioterapica lombalgia sciatica',           'servizio', 'op-martini', '2026-04-01T09:30:00'),
('inc-fis-007',  50.00, 'carta',    'cli-fis-07', 'apt-fis-003', 'fat-fis-004', 'Onde d urto gomito dx - seduta 3',                        'servizio', 'op-ferrari', '2026-03-31T09:15:00'),
('inc-fis-008',  55.00, 'contanti', 'cli-fis-08', 'apt-fis-005', NULL,           'Rieducazione posturale RPG - seduta 2',                   'servizio', 'op-conti',   '2026-03-31T10:05:00'),
('inc-fis-009', 480.00, 'bonifico', 'cli-fis-08', NULL,          NULL,           'Acquisto Pacchetto Posturale completo (pkg-fis-02)',       'pacchetto','op-martini', '2026-03-28T10:00:00'),
('inc-fis-010',  50.00, 'carta',    'cli-fis-04', 'apt-fis-008', NULL,           'Fisioterapia caviglia - progressione post-distorsione',   'servizio', 'op-russo',   '2026-04-01T10:45:00');

PRAGMA foreign_keys = ON;
