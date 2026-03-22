-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Dati Video Demo (Settimana 17-22 Marzo 2026)
-- Calendario PIENO + Schede Verticali compilate
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- -------------------------------------------------------
-- PULIZIA appuntamenti vecchi (mantieni clienti/servizi/operatori)
-- -------------------------------------------------------
DELETE FROM appuntamenti WHERE data_ora_inizio >= '2026-03-17T00:00:00';

-- -------------------------------------------------------
-- APPUNTAMENTI SETTIMANA 17-22 MARZO 2026 (PIENA)
-- 6-8 appuntamenti/giorno, mix stati
-- -------------------------------------------------------
INSERT OR REPLACE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione) VALUES
-- LUNEDI 17 MARZO
('vd-001', 'cli-anna',      'srv-colore',       'op-giulia', '2026-03-17T09:00:00', '2026-03-17T10:00:00', 60, 'completato', 45.00, 65.00, 'Ritocco radici castano 5N', 'whatsapp'),
('vd-002', 'cli-paolo',     'srv-taglio-uomo',  'op-marco',  '2026-03-17T09:30:00', '2026-03-17T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-003', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-03-17T10:00:00', '2026-03-17T10:30:00', 30, 'completato', 18.00, 30.00, 'Fade + barba', 'voice'),
('vd-004', 'cli-elena',     'srv-meches',       'op-giulia', '2026-03-17T10:30:00', '2026-03-17T12:00:00', 90, 'completato', 65.00, 85.00, 'Balayage miele', 'whatsapp'),
('vd-005', 'cli-giuseppe',  'srv-taglio-uomo',  'op-marco',  '2026-03-17T11:00:00', '2026-03-17T11:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-006', 'cli-chiara',    'srv-trattamento',  'op-laura',  '2026-03-17T14:00:00', '2026-03-17T15:00:00', 60, 'completato', 30.00, 45.00, 'Keratina brasiliana', 'whatsapp'),
('vd-007', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-03-17T14:30:00', '2026-03-17T15:00:00', 20, 'completato', 12.00, 12.00, NULL, 'voice'),
('vd-008', 'cli-lucia',     'srv-piega',        'op-paola',  '2026-03-17T15:00:00', '2026-03-17T15:30:00', 30, 'completato', 20.00, 30.00, 'Prova acconciatura sposa', 'manuale'),

-- MARTEDI 18 MARZO
('vd-009', 'cli-francesca', 'srv-colore',       'op-giulia', '2026-03-18T09:00:00', '2026-03-18T10:00:00', 60, 'completato', 45.00, 55.00, 'Castano cioccolato 4.3', 'whatsapp'),
('vd-010', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-03-18T09:30:00', '2026-03-18T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-011', 'cli-simona',    'srv-trattamento',  'op-paola',  '2026-03-18T10:00:00', '2026-03-18T11:00:00', 60, 'completato', 30.00, 35.00, 'Maschera anti-crespo', 'voice'),
('vd-012', 'cli-valeria',   'srv-meches',       'op-giulia', '2026-03-18T11:00:00', '2026-03-18T12:30:00', 90, 'completato', 65.00, 75.00, 'Highlights biondo naturale', 'whatsapp'),
('vd-013', 'cli-roberto',   'srv-taglio-uomo',  'op-luca',   '2026-03-18T14:00:00', '2026-03-18T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),
('vd-014', 'cli-davide',    'srv-taglio-uomo',  'op-marco',  '2026-03-18T15:00:00', '2026-03-18T15:30:00', 30, 'completato', 18.00, 20.00, 'Taglio businessman', 'manuale'),
('vd-015', 'cli-martina',   'srv-piega',        'op-laura',  '2026-03-18T16:00:00', '2026-03-18T16:30:00', 30, 'completato', 20.00, 25.00, 'Piega volume', 'whatsapp'),

-- MERCOLEDI 19 MARZO
('vd-016', 'cli-sara',      'srv-colore',       'op-giulia', '2026-03-19T09:00:00', '2026-03-19T10:30:00', 90, 'completato', 45.00, 75.00, 'Biondo cenere 12.1 Wella', 'whatsapp'),
('vd-017', 'cli-marco',     'srv-taglio-uomo',  'op-luca',   '2026-03-19T09:30:00', '2026-03-19T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-018', 'cli-chiara',    'srv-meches',       'op-giulia', '2026-03-19T11:00:00', '2026-03-19T12:30:00', 90, 'completato', 65.00, 95.00, 'Balayage caramello', 'manuale'),
('vd-019', 'cli-giovanni',  'srv-taglio-uomo',  'op-marco',  '2026-03-19T10:00:00', '2026-03-19T10:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-020', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-03-19T14:00:00', '2026-03-19T14:20:00', 20, 'completato', 12.00, 12.00, NULL, 'voice'),
('vd-021', 'cli-francesca', 'srv-piega',        'op-paola',  '2026-03-19T15:00:00', '2026-03-19T15:30:00', 30, 'completato', 20.00, 25.00, NULL, 'whatsapp'),
('vd-022', 'cli-alessia',   'srv-colore',       'op-laura',  '2026-03-19T15:30:00', '2026-03-19T16:30:00', 60, 'completato', 45.00, 55.00, 'Tinta castano ramato', 'manuale'),

-- GIOVEDI 20 MARZO
('vd-023', 'cli-lucia',     'srv-meches',       'op-giulia', '2026-03-20T09:00:00', '2026-03-20T11:00:00', 120,'completato', 65.00, 120.00,'Look sposa — colore + acconciatura', 'manuale'),
('vd-024', 'cli-paolo',     'srv-taglio-uomo',  'op-marco',  '2026-03-20T09:30:00', '2026-03-20T10:00:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-025', 'cli-simona',    'srv-colore',       'op-paola',  '2026-03-20T10:00:00', '2026-03-20T11:00:00', 60, 'completato', 45.00, 50.00, 'Castano ramato', 'whatsapp'),
('vd-026', 'cli-matteo',    'srv-taglio-uomo',  'op-luca',   '2026-03-20T10:30:00', '2026-03-20T11:00:00', 30, 'completato', 18.00, 30.00, 'Fade + design', 'voice'),
('vd-027', 'cli-anna',      'srv-piega',        'op-giulia', '2026-03-20T14:00:00', '2026-03-20T14:30:00', 30, 'completato', 20.00, 25.00, 'Piega morbida', 'whatsapp'),
('vd-028', 'cli-valeria',   'srv-trattamento',  'op-laura',  '2026-03-20T14:30:00', '2026-03-20T15:30:00', 60, 'completato', 30.00, 40.00, 'Trattamento idratante', 'manuale'),
('vd-029', 'cli-luca-p',    'srv-taglio-uomo',  'op-marco',  '2026-03-20T16:00:00', '2026-03-20T16:30:00', 30, 'completato', 18.00, 18.00, NULL, 'walk-in'),

-- VENERDI 21 MARZO (OGGI — misto completato/confermato/in_attesa)
('vd-030', 'cli-elena',     'srv-colore',       'op-giulia', '2026-03-21T09:00:00', '2026-03-21T10:00:00', 60, 'completato', 45.00, 65.00, 'Colore completo + piega', 'whatsapp'),
('vd-031', 'cli-antonio',   'srv-taglio-uomo',  'op-marco',  '2026-03-21T09:00:00', '2026-03-21T09:30:00', 30, 'completato', 18.00, 18.00, NULL, 'telefono'),
('vd-032', 'cli-chiara',    'srv-meches',       'op-giulia', '2026-03-21T10:30:00', '2026-03-21T12:00:00', 90, 'completato', 65.00, 85.00, 'Meches fredde platino', 'whatsapp'),
('vd-033', 'cli-davide',    'srv-taglio-uomo',  'op-luca',   '2026-03-21T10:00:00', '2026-03-21T10:30:00', 30, 'completato', 18.00, 22.00, 'Taglio + styling', 'voice'),
('vd-034', 'cli-francesca', 'srv-trattamento',  'op-paola',  '2026-03-21T11:00:00', '2026-03-21T12:30:00', 90, 'confermato', 30.00, 65.00, 'Cheratina lisciante', 'whatsapp'),
('vd-035', 'cli-sara',      'srv-piega',        'op-laura',  '2026-03-21T14:00:00', '2026-03-21T14:30:00', 30, 'confermato', 20.00, 25.00, 'Piega onde morbide', 'manuale'),
('vd-036', 'cli-martina',   'srv-colore',       'op-giulia', '2026-03-21T14:30:00', '2026-03-21T15:30:00', 60, 'confermato', 45.00, 55.00, 'Tinta biondo scuro', 'whatsapp'),
('vd-037', 'cli-andrea',    'srv-barba',        'op-luca',   '2026-03-21T15:00:00', '2026-03-21T15:20:00', 20, 'confermato', 12.00, 12.00, NULL, 'voice'),
('vd-038', 'cli-roberto',   'srv-taglio-uomo',  'op-marco',  '2026-03-21T16:00:00', '2026-03-21T16:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'walk-in'),

-- SABATO 22 MARZO (piena — giorno top)
('vd-039', 'cli-anna',      'srv-colore',       'op-giulia', '2026-03-22T09:00:00', '2026-03-22T10:00:00', 60, 'confermato', 45.00, 60.00, 'Ritocco + trattamento', 'whatsapp'),
('vd-040', 'cli-giuseppe',  'srv-taglio-uomo',  'op-marco',  '2026-03-22T09:00:00', '2026-03-22T09:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'telefono'),
('vd-041', 'cli-lucia',     'srv-piega',        'op-laura',  '2026-03-22T09:30:00', '2026-03-22T10:00:00', 30, 'confermato', 20.00, 35.00, 'Piega prova sposa', 'manuale'),
('vd-042', 'cli-chiara',    'srv-trattamento',  'op-paola',  '2026-03-22T10:00:00', '2026-03-22T11:00:00', 60, 'confermato', 30.00, 45.00, 'Olaplex ristrutturante', 'whatsapp'),
('vd-043', 'cli-simona',    'srv-meches',       'op-giulia', '2026-03-22T10:30:00', '2026-03-22T12:00:00', 90, 'confermato', 65.00, 80.00, 'Meches caramello', 'voice'),
('vd-044', 'cli-marco',     'srv-taglio-uomo',  'op-luca',   '2026-03-22T11:00:00', '2026-03-22T11:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'walk-in'),
('vd-045', 'cli-valeria',   'srv-colore',       'op-paola',  '2026-03-22T14:00:00', '2026-03-22T15:00:00', 60, 'confermato', 45.00, 55.00, 'Riflessi dorati', 'whatsapp'),
('vd-046', 'cli-matteo',    'srv-taglio-uomo',  'op-marco',  '2026-03-22T14:30:00', '2026-03-22T15:00:00', 30, 'confermato', 18.00, 30.00, 'Fade + barba', 'whatsapp'),
('vd-047', 'cli-alessia',   'srv-piega',        'op-laura',  '2026-03-22T15:00:00', '2026-03-22T15:30:00', 30, 'confermato', 20.00, 25.00, 'Piega per cena', 'manuale');

-- -------------------------------------------------------
-- SCHEDA PARRUCCHIERE — Sara Colombo (VIP, biondo cenere)
-- -------------------------------------------------------
INSERT OR REPLACE INTO schede_parrucchiere (id, cliente_id, tipo_capello, porosita, lunghezza_attuale, base_naturale, colore_attuale, colorazioni_precedenti, decolorazioni, permanente, stirature_chimiche, allergia_tinta, allergia_ammoniaca, test_pelle_eseguito, data_test_pelle, servizi_abituali, frequenza_taglio, frequenza_colore, prodotti_casa, preferenze_colore, non_vuole, created_at, updated_at) VALUES (
    'sp-sara', 'cli-sara',
    'medio', 'media', 'lungo',
    '6', 'Biondo cenere 12.1 Wella Koleston',
    '[{"id":"c1","data":"2026-01-15","colore":"Biondo cenere 12.1","tipo":"tinta"},{"id":"c2","data":"2025-11-20","colore":"Biondo platino 12.0","tipo":"decolorazione"},{"id":"c3","data":"2025-09-10","colore":"Biondo miele 9.3","tipo":"highlights"},{"id":"c4","data":"2025-07-05","colore":"Castano chiaro 5N","tipo":"tinta"}]',
    1, 0, 0,
    0, 0, 1, '2026-01-10',
    '["Colore","Piega","Trattamento","Taglio"]',
    '2mesi', 'mensile',
    '{"Shampoo":"Olaplex No.4","Balsamo":"Olaplex No.5","Maschera":"Kerastase Blond Absolu","Olio":"Moroccanoil"}',
    'Preferisce toni freddi, cenere. Mai toni caldi o ramati. Vuole mantenere il biondo cenere luminoso.',
    '["rosso","ramato","rame","caldo"]',
    '2024-01-15 09:00:00', '2026-03-19 16:00:00'
);

-- SCHEDA PARRUCCHIERE — Anna Ferrari (VIP, cliente storica)
INSERT OR REPLACE INTO schede_parrucchiere (id, cliente_id, tipo_capello, porosita, lunghezza_attuale, base_naturale, colore_attuale, colorazioni_precedenti, decolorazioni, permanente, stirature_chimiche, allergia_tinta, allergia_ammoniaca, test_pelle_eseguito, data_test_pelle, servizi_abituali, frequenza_taglio, frequenza_colore, prodotti_casa, preferenze_colore, non_vuole, created_at, updated_at) VALUES (
    'sp-anna', 'cli-anna',
    'fino', 'alta', 'medio',
    '5', 'Castano medio 5N con riflessi',
    '[{"id":"c5","data":"2026-03-17","colore":"Castano 5N + riflessi","tipo":"tinta"},{"id":"c6","data":"2026-02-16","colore":"Castano 5N","tipo":"tinta"},{"id":"c7","data":"2026-01-12","colore":"Castano scuro 4N","tipo":"tinta"}]',
    0, 0, 0,
    1, 0, 1, '2025-12-20',
    '["Colore","Piega","Taglio"]',
    '3mesi', 'mensile',
    '{"Shampoo":"L''Oreal Elvive","Balsamo":"Pantene"}',
    'Toni naturali, copertura bianchi totale. Niente highlights.',
    '["biondo","highlights"]',
    '2024-01-15 09:00:00', '2026-03-17 10:00:00'
);

-- -------------------------------------------------------
-- SCHEDA VEICOLI — Marco Bianchi (officina)
-- -------------------------------------------------------
INSERT OR REPLACE INTO schede_veicoli (id, cliente_id, targa, marca, modello, anno, alimentazione, cilindrata, kw, telaio, ultima_revisione, scadenza_revisione, km_attuali, km_ultimo_tagliando, misura_gomme, tipo_gomme, preferenza_ricambi, note_veicolo, interventi, is_default, created_at, updated_at) VALUES (
    'sv-marco', 'cli-marco',
    'FT 892 XK', 'Volkswagen', 'Golf 1.6 TDI', 2019, 'diesel', '1598cc', 85,
    'WVWZZZ1JZKW386752',
    '2025-10-15', '2026-10-15',
    87500, 75000,
    '205/55 R16', 'invernali',
    'originali',
    'Olio 5W40 sintetico. Frizione leggera usura. Prossimo cambio distribuzione a 90.000 km.',
    '[{"id":"i1","data":"2026-02-10","km":85000,"tipo":"Cambio olio","descrizione":"Cambio olio + filtro olio + filtro aria","costo":89.90},{"id":"i2","data":"2025-10-15","km":80000,"tipo":"Revisione","descrizione":"Revisione periodica - SUPERATA","costo":79.00},{"id":"i3","data":"2025-06-20","km":75000,"tipo":"Tagliando","descrizione":"Tagliando completo 75.000km: olio, filtri, candele, liquido freni","costo":320.00},{"id":"i4","data":"2025-03-10","km":72000,"tipo":"Cambio gomme","descrizione":"Montaggio gomme invernali 205/55 R16 Michelin Alpin 6","costo":45.00},{"id":"i5","data":"2024-11-05","km":68000,"tipo":"Freni","descrizione":"Sostituzione pastiglie freno anteriori","costo":145.00}]',
    1,
    '2024-06-20 10:00:00', '2026-03-18 14:00:00'
);

-- Secondo veicolo per Marco
INSERT OR REPLACE INTO schede_veicoli (id, cliente_id, targa, marca, modello, anno, alimentazione, cilindrata, kw, ultima_revisione, scadenza_revisione, km_attuali, km_ultimo_tagliando, misura_gomme, tipo_gomme, note_veicolo, interventi, is_default, created_at, updated_at) VALUES (
    'sv-marco2', 'cli-marco',
    'GH 123 AB', 'Fiat', 'Panda 1.2', 2016, 'benzina', '1242cc', 51,
    '2025-09-20', '2026-09-20',
    112000, 105000,
    '175/65 R14', 'allseason',
    'Auto della moglie. Cambio frizione previsto entro 120.000 km.',
    '[{"id":"i6","data":"2025-09-20","km":108000,"tipo":"Revisione","descrizione":"Revisione - SUPERATA con riserva (usura freni)","costo":79.00}]',
    0,
    '2024-06-20 10:00:00', '2026-01-15 09:00:00'
);

-- -------------------------------------------------------
-- SCHEDA ODONTOIATRICA — Elena Ricci
-- -------------------------------------------------------
INSERT OR REPLACE INTO schede_odontoiatriche (id, cliente_id, odontogramma, prima_visita, ultima_visita, frequenza_controlli, spazzolino, filo_interdentale, collutorio, allergia_lattice, allergia_anestesia, allergie_altre, ortodonzia_in_corso, note_cliniche, created_at, updated_at) VALUES (
    'so-elena', 'cli-elena',
    '{"11":{"stato":"sano"},"12":{"stato":"otturato"},"13":{"stato":"sano"},"14":{"stato":"sano"},"15":{"stato":"corona"},"16":{"stato":"otturato"},"17":{"stato":"sano"},"18":{"stato":"mancante"},"21":{"stato":"sano"},"22":{"stato":"sano"},"23":{"stato":"sano"},"24":{"stato":"otturato"},"25":{"stato":"sano"},"26":{"stato":"devitalizzato"},"27":{"stato":"sano"},"28":{"stato":"mancante"},"31":{"stato":"sano"},"32":{"stato":"sano"},"33":{"stato":"sano"},"34":{"stato":"sano"},"35":{"stato":"otturato"},"36":{"stato":"corona"},"37":{"stato":"sano"},"38":{"stato":"mancante"},"41":{"stato":"sano"},"42":{"stato":"sano"},"43":{"stato":"sano"},"44":{"stato":"sano"},"45":{"stato":"sano"},"46":{"stato":"carie"},"47":{"stato":"otturato"},"48":{"stato":"mancante"}}',
    '2020-03-15', '2026-03-10',
    '6mesi', 'elettrico', 1, 1,
    0, 0, NULL,
    0,
    'Paziente collaborante. Igiene orale buona. Prossimo controllo settembre 2026. Carie 46 da trattare prossima seduta.',
    '2020-03-15 09:00:00', '2026-03-10 11:00:00'
);

-- Trattamenti odontoiatrici (colonna dedicata in migration 030)
-- I trattamenti sono gestiti via JSON nel componente React

-- -------------------------------------------------------
-- SCHEDA ESTETICA — Francesca Conti
-- -------------------------------------------------------
INSERT OR REPLACE INTO schede_estetica (id, cliente_id, fototipo, tipo_pelle, allergie_prodotti, allergie_profumi, allergie_henne, trattamenti_precedenti, ultima_depilazione, metodo_depilazione, unghie_naturali, problematiche_unghie, problematiche_viso, routine_skincare, peso_attuale, obiettivo, gravidanza, allattamento, patologie_attive, note_trattamenti, created_at, updated_at) VALUES (
    'se-francesca', 'cli-francesca',
    3, 'mista',
    '["nickel","parabeni"]',
    1, 0,
    '[{"tipo":"Pulizia viso profonda","data":"2026-03-05","note":"Estrazione comedoni zona T"},{"tipo":"Peeling glicolico","data":"2026-02-10","note":"30% concentrazione, 5 minuti"},{"tipo":"Massaggio linfodrenante","data":"2026-01-20","note":"Gambe + addome"},{"tipo":"Ceretta integrale","data":"2026-03-01"}]',
    '2026-03-01', 'ceretta',
    1, NULL,
    '["pori_dilatati","macchie","pelle_opaca"]',
    'Mattina: detergente delicato Avene + crema idratante Bioderma. Sera: struccante bifasico + siero vitamina C + crema notte La Roche-Posay.',
    62.5, 'tonificazione',
    0, 0,
    '[]',
    'Cliente regolare. Pelle reattiva zona guance. Evitare prodotti con profumi forti. Risultati ottimi con peeling glicolico a bassa concentrazione.',
    '2024-12-01 16:00:00', '2026-03-05 15:00:00'
);

-- -------------------------------------------------------
-- SCHEDA FITNESS — Luca Pellegrino
-- -------------------------------------------------------
INSERT OR REPLACE INTO schede_fitness (id, cliente_id, obiettivo, livello, frequenza_allenamento, peso_kg, altezza_cm, percentuale_grasso, circonferenza_vita, cardiopatico, iperteso, diabetico, note_mediche, limitazioni_fisiche, scheda_allenamento, storico_misurazioni, created_at, updated_at) VALUES (
    'sf-luca', 'cli-luca-p',
    'tonificazione', 'intermedio', '3x_settimana',
    78.5, 178, 18.2, 84.0,
    0, 0, 0,
    'Nessuna patologia nota. Certificato medico sportivo valido fino a settembre 2026.',
    'Leggera lombalgia da postura — evitare deadlift pesante, preferire trap bar.',
    '[{"giorno":"Lunedì","esercizi":["Squat 4x8 @80kg","Leg press 3x12 @120kg","Affondi bulgari 3x10","Leg curl 3x12","Calf raises 4x15","Plank 3x45s"]},{"giorno":"Mercoledì","esercizi":["Panca piana 4x8 @70kg","Croci ai cavi 3x12","Military press 3x10 @40kg","Alzate laterali 3x15","Tricipiti pushdown 3x12","Curl bilanciere 3x10"]},{"giorno":"Venerdì","esercizi":["Trap bar deadlift 4x6 @90kg","Rematore bilanciere 4x8 @60kg","Lat pulldown 3x12","Face pull 3x15","Hyperextension 3x12","Ab wheel 3x10"]}]',
    '[{"id":"m1","data":"2026-03-15","peso":78.5,"grasso":18.2,"note":"Post 3 mesi di scheda"},{"id":"m2","data":"2026-02-15","peso":79.8,"grasso":19.1,"note":"Leggero miglioramento"},{"id":"m3","data":"2026-01-10","peso":81.2,"grasso":20.5,"note":"Inizio programma"},{"id":"m4","data":"2025-12-01","peso":82.0,"grasso":21.0,"note":"Prima misurazione"}]',
    '2025-12-01 10:00:00', '2026-03-15 17:00:00'
);

-- -------------------------------------------------------
-- INCASSI per oggi (21 marzo) — tabella reale: incassi
-- -------------------------------------------------------
INSERT OR REPLACE INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, descrizione, categoria, data_incasso, created_at) VALUES
('cx-001', 65.00, 'carta',     'cli-elena',     'vd-030', 'Colore completo + piega',    'servizio', '2026-03-21T10:05:00', '2026-03-21T10:05:00'),
('cx-002', 18.00, 'contanti',  'cli-antonio',   'vd-031', 'Taglio uomo',                'servizio', '2026-03-21T09:35:00', '2026-03-21T09:35:00'),
('cx-003', 85.00, 'carta',     'cli-chiara',    'vd-032', 'Meches platino',             'servizio', '2026-03-21T12:10:00', '2026-03-21T12:10:00'),
('cx-004', 22.00, 'contanti',  'cli-davide',    'vd-033', 'Taglio + styling',           'servizio', '2026-03-21T10:35:00', '2026-03-21T10:35:00'),
('cx-005', 32.00, 'satispay',  'cli-matteo',    NULL,     'Taglio + barba (walk-in)',    'servizio', '2026-03-21T11:00:00', '2026-03-21T11:00:00');

PRAGMA foreign_keys = ON;
