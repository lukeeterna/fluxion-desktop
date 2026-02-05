-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Demo Database Seed
-- Popola il database con dati completi per testing
-- ═══════════════════════════════════════════════════════════════════

-- ===================================================================
-- 1. SETUP CONFIG (Wizard già completato)
-- ===================================================================
INSERT OR REPLACE INTO setup_config (id, azienda_nome, azienda_indirizzo, azienda_citta, azienda_cap, azienda_provincia, azienda_piva, azienda_telefono, azienda_email, macro_categoria, micro_categoria, license_tier, setup_completato, created_at, updated_at) 
VALUES (
  1, 
  'Studio Dentistico Demo', 
  'Via Roma 123', 
  'Milano', 
  '20121', 
  'MI', 
  '12345678901', 
  '+39 02 1234567', 
  'info@studiodemo.it',
  'medico',
  'odontoiatra',
  'enterprise',
  1,
  datetime('now'),
  datetime('now')
);

-- ===================================================================
-- 2. OPERATORI (4 profili diversi)
-- ===================================================================
DELETE FROM operatori;
INSERT INTO operatori (id, nome, email, telefono, colore, attivo, specializzazione, orario_lavoro) VALUES 
('op-001', 'Dott. Mario Rossi', 'mario.rossi@studiodemo.it', '+39 333 1111111', '#3B82F6', 1, 'Dentista - Protesi', '{"lunedi": "09:00-13:00,14:00-18:00", "martedi": "09:00-13:00,14:00-18:00", "mercoledi": "09:00-13:00,14:00-18:00", "giovedi": "09:00-13:00,14:00-18:00", "venerdi": "09:00-13:00,14:00-17:00"}'),
('op-002', 'Dott.ssa Anna Bianchi', 'anna.bianchi@studiodemo.it', '+39 333 2222222', '#EC4899', 1, 'Igienista Dentale', '{"lunedi": "08:30-12:30,14:00-17:00", "martedi": "08:30-12:30,14:00-17:00", "mercoledi": "08:30-12:30,14:00-17:00", "giovedi": "08:30-12:30,14:00-17:00", "venerdi": "08:30-12:30"}'),
('op-003', 'Dott. Luca Verdi', 'luca.verdi@studiodemo.it', '+39 333 3333333', '#10B981', 1, 'Ortodonzia', '{"lunedi": "10:00-13:00,15:00-19:00", "martedi": "10:00-13:00,15:00-19:00", "giovedi": "10:00-13:00,15:00-19:00", "venerdi": "10:00-13:00,15:00-18:00"}'),
('op-004', 'Sig.ra Giulia Neri', 'giulia.neri@studiodemo.it', '+39 333 4444444', '#F59E0B', 1, 'Receptionist / Amministrazione', '{"lunedi": "08:00-13:00,14:00-17:00", "martedi": "08:00-13:00,14:00-17:00", "mercoledi": "08:00-13:00,14:00-17:00", "giovedi": "08:00-13:00,14:00-17:00", "venerdi": "08:00-13:00,14:00-16:00"}');

-- ===================================================================
-- 3. SERVIZI (Categorie Odontoiatriche)
-- ===================================================================
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, durata_minuti, prezzo, categoria, colore, attivo, iva_percentuale) VALUES
-- Diagnostica
('srv-001', 'Visita di controllo', 'Controllo denti e gengive', 30, 50.00, 'diagnostica', '#3B82F6', 1, 22),
('srv-002', 'Panoramica dentale', 'Radiografia panoramica digitale', 15, 40.00, 'diagnostica', '#3B82F6', 1, 22),
('srv-003', 'Rx endorale', 'Radiografia endorale singolo elemento', 15, 25.00, 'diagnostica', '#3B82F6', 1, 22),
('srv-004', 'Cone Beam CT', 'Tac dentale 3D', 30, 120.00, 'diagnostica', '#3B82F6', 1, 22),

-- Igiene
('srv-101', 'Igiene professionale', 'Pulizia professionale denti', 45, 80.00, 'igiene', '#10B981', 1, 22),
('srv-102', 'Sbiancamento in studio', 'Sbiancamento professionale', 60, 250.00, 'igiene', '#10B981', 1, 22),
('srv-103', 'Sbiancamento domiciliare', 'Kit sbiancamento casa', 20, 150.00, 'igiene', '#10B981', 1, 22),
('srv-104', 'Fluoroprofilassi', 'Trattamento fluoruro', 20, 35.00, 'igiene', '#10B981', 1, 22),

-- Conservativa
('srv-201', 'Otturazione composito', 'Otturazione estetica', 45, 120.00, 'conservativa', '#F59E0B', 1, 22),
('srv-202', 'Otturazione provvisoria', 'Otturazione temporanea', 20, 40.00, 'conservativa', '#F59E0B', 1, 22),
('srv-203', 'Devitalizzazione monoradicolare', 'Devitalizzazione canale singolo', 60, 280.00, 'conservativa', '#F59E0B', 1, 22),
('srv-204', 'Devitalizzazione pluriradicolare', 'Devitalizzazione canali multipli', 90, 380.00, 'conservativa', '#F59E0B', 1, 22),
('srv-205', 'Ricostruzione corona', 'Ricostruzione post-traumatica', 60, 200.00, 'conservativa', '#F59E0B', 1, 22),

-- Protesi
('srv-301', 'Corona ceramica-zirconio', 'Corona fisica zirconio', 60, 650.00, 'protesi', '#8B5CF6', 1, 22),
('srv-302', 'Corona ceramica-metallo', 'Corona fisica PFM', 60, 450.00, 'protesi', '#8B5CF6', 1, 22),
('srv-303', 'Ponte 3 elementi', 'Ponte fisso 3 corone', 90, 1500.00, 'protesi', '#8B5CF6', 1, 22),
('srv-304', 'Protesi rimovibile parziale', 'Scheletrato', 45, 800.00, 'protesi', '#8B5CF6', 1, 22),
('srv-305', 'Protesi totale', 'Protesi mobile completa', 60, 1200.00, 'protesi', '#8B5CF6', 1, 22),

-- Chirurgia
('srv-401', 'Estrazione semplice', 'Estrazione dente incluso', 30, 100.00, 'chirurgia', '#EF4444', 1, 22),
('srv-402', 'Estrazione chirurgica', 'Estrazione complessa/incluso', 60, 250.00, 'chirurgia', '#EF4444', 1, 22),
('srv-403', 'Impianto dentale', 'Impianto singolo con chirurgia', 90, 1200.00, 'chirurgia', '#EF4444', 1, 22),
('srv-404', 'Innesto osseo', 'Rigenerazione ossea', 60, 500.00, 'chirurgia', '#EF4444', 1, 22),
('srv-405', 'Alzamento seno', 'Alzamento pavimento sinusale', 90, 800.00, 'chirurgia', '#EF4444', 1, 22),

-- Ortodonzia
('srv-501', 'Apparecchio fisso', 'Ortodonzia fisso installazione', 90, 3500.00, 'ortodonzia', '#EC4899', 1, 22),
('srv-502', 'Apparecchio mobile', 'Ortodonzia mobile installazione', 45, 800.00, 'ortodonzia', '#EC4899', 1, 22),
('srv-503', 'Allineatore invisibile', 'Invisalign/similare', 60, 4500.00, 'ortodonzia', '#EC4899', 1, 22),
('srv-504', 'Controllo ortodontico', 'Controllo mensile apparecchio', 20, 50.00, 'ortodonzia', '#EC4899', 1, 22);

-- ===================================================================
-- 4. CLIENTI CON SCHEDE (30 clienti di esempio)
-- ===================================================================
DELETE FROM clienti;
INSERT INTO clienti (id, nome, cognome, email, telefono, data_nascita, indirizzo, citta, cap, codice_fiscale, note, data_creazione, data_modifica, newsletter) VALUES
-- Pazienti attivi con schede
('cli-001', 'Marco', 'Ferrari', 'marco.ferrari@email.it', '+39 340 1111111', '1985-03-15', 'Via Garibaldi 1', 'Milano', '20121', 'FRAMRC85C15F205Z', 'Paziente da 5 anni, paura del dentista', datetime('now'), datetime('now'), 1),
('cli-002', 'Laura', 'Colombo', 'laura.colombo@email.it', '+39 340 2222222', '1990-07-22', 'Via Dante 45', 'Milano', '20123', 'CLMLRA90L62F205Z', 'Gravidanza in corso - attenzione ai raggi X', datetime('now'), datetime('now'), 1),
('cli-003', 'Giuseppe', 'Ricci', 'giuseppe.ricci@email.it', '+39 340 3333333', '1978-11-08', 'Corso Buenos Aires 123', 'Milano', '20124', 'RCCGPP78S08F205Z', 'Iperteso, allergia al lattice', datetime('now'), datetime('now'), 0),
('cli-004', 'Francesca', 'Marino', 'francesca.marino@email.it', '+39 340 4444444', '1995-01-30', 'Piazza Duomo 5', 'Milano', '20121', 'MRNFNC95A70F205Z', 'Ortodonzia in corso', datetime('now'), datetime('now'), 1),
('cli-005', 'Antonio', 'Greco', 'antonio.greco@email.it', '+39 340 5555555', '1982-09-12', 'Viale Monza 78', 'Milano', '20127', 'GRCNTN82P12F205Z', 'Diabete tipo 2', datetime('now'), datetime('now'), 0),
('cli-006', 'Stefania', 'Conti', 'stefania.conti@email.it', '+39 340 6666666', '1988-05-18', 'Via Torino 234', 'Milano', '20123', 'CNTSFN88E58F205Z', 'Pacchetto igiene annuale', datetime('now'), datetime('now'), 1),
('cli-007', 'Roberto', 'Lombardi', 'roberto.lombardi@email.it', '+39 340 7777777', '1975-12-03', 'Corso Magenta 89', 'Milano', '20123', 'LMBRRT75T03F205Z', 'Paziente VIP, preferisce mattino', datetime('now'), datetime('now'), 1),
('cli-008', 'Patrizia', 'Serra', 'patrizia.serra@email.it', '+39 340 8888888', '1992-04-25', 'Via Brera 12', 'Milano', '20121', 'SRAPTZ92E65F205Z', 'Tessera fedeltà attiva', datetime('now'), datetime('now'), 1),
('cli-009', 'Davide', 'Cattaneo', 'davide.cattaneo@email.it', '+39 340 9999999', '1980-08-14', 'Viale Tunisia 56', 'Milano', '20124', 'CTTDVD80M14F205Z', 'Impianti in corso', datetime('now'), datetime('now'), 0),
('cli-010', 'Elena', 'Monti', 'elena.monti@email.it', '+39 341 0000000', '1987-02-28', 'Via Washington 67', 'Milano', '20146', 'MNTLNE87B68F205Z', 'Allergie multiple dichiarate', datetime('now'), datetime('now'), 1);

-- ===================================================================
-- 5. SCHEDE ODONTOIATRICHE
-- ===================================================================
DELETE FROM schede_odontoiatriche;
INSERT INTO schede_odontoiatriche (id, cliente_id, odontogramma, prima_visita, ultima_visita, frequenza_controlli, spazzolino, filo_interdentale, collutorio, allergia_lattice, allergia_anestesia, allergie_altre, ortodonzia_in_corso, tipo_apparecchio, data_inizio_ortodonzia, trattamenti, note_cliniche) VALUES
('sch-001', 'cli-001', 
  '{"18": {"stato": "sano"}, "17": {"stato": "sano"}, "16": {"stato": "otturato"}, "15": {"stato": "sano"}, "14": {"stato": "sano"}, "13": {"stato": "sano"}, "12": {"stato": "sano"}, "11": {"stato": "corona"}, "21": {"stato": "sano"}, "22": {"stato": "sano"}, "23": {"stato": "sano"}, "24": {"stato": "otturato"}, "25": {"stato": "sano"}, "26": {"stato": "sano"}, "27": {"stato": "sano"}, "28": {"stato": "estratt0"}}',
  '2020-03-15', '2025-01-20', '6_mesi', 'elettrico', 1, 1, 0, 0, NULL, 0, NULL, NULL,
  '[{"data": "2020-03-15", "tipo": "controllo", "descrizione": "Prima visita"}, {"data": "2020-04-10", "tipo": "otturazione", "descrizione": "Otturazione 1.6 composito"}, {"data": "2024-12-15", "tipo": "corona", "descrizione": "Corona zirconio 1.1"}]',
  'Paziente collaborativo, igiene orale buona'
),
('sch-002', 'cli-002',
  '{"18": {"stato": "sano"}, "17": {"stato": "sano"}, "16": {"stato": "sano"}, "15": {"stato": "sano"}, "14": {"stato": "sano"}, "13": {"stato": "sano"}, "12": {"stato": "sano"}, "11": {"stato": "sano"}, "21": {"stato": "sano"}, "22": {"stato": "sano"}, "23": {"stato": "sano"}, "24": {"stato": "sano"}, "25": {"stato": "sano"}, "26": {"stato": "sano"}, "27": {"stato": "sano"}, "28": {"stato": "sano"}}',
  '2023-06-10', '2025-01-15', '12_mesi', 'manuale', 1, 0, 0, 0, 'Gravidanza', 0, NULL, NULL,
  '[{"data": "2023-06-10", "tipo": "controllo", "descrizione": "Prima visita"}, {"data": "2024-01-20", "tipo": "igiene", "descrizione": "Igiene professionale"}]',
  'Gravidanza in corso - evitare raggi X'
),
('sch-003', 'cli-004',
  '{"18": {"stato": "sano"}, "17": {"stato": "sano"}, "16": {"stato": "sano"}, "15": {"stato": "sano"}, "14": {"stato": "sano"}, "13": {"stato": "sano"}, "12": {"stato": "sano"}, "11": {"stato": "sano"}, "21": {"stato": "sano"}, "22": {"stato": "sano"}, "23": {"stato": "sano"}, "24": {"stato": "sano"}, "25": {"stato": "sano"}, "26": {"stato": "sano"}, "27": {"stato": "sano"}, "28": {"stato": "sano"}, "31": {"stato": "in_ortodonzia"}, "32": {"stato": "in_ortodonzia"}, "33": {"stato": "in_ortodonzia"}, "34": {"stato": "in_ortodonzia"}, "35": {"stato": "in_ortodonzia"}, "36": {"stato": "in_ortodonzia"}, "37": {"stato": "in_ortodonzia"}, "38": {"stato": "in_ortodonzia"}}',
  '2022-09-01', '2025-01-10', '6_mesi', 'elettrico', 1, 1, 0, 0, NULL, 1, 'fisso_multibracket', '2022-09-15',
  '[{"data": "2022-09-01", "tipo": "controllo", "descrizione": "Prima visita ortodontica"}, {"data": "2022-09-15", "tipo": "ortodonzia", "descrizione": "Installazione apparecchio fisso"}, {"data": "2025-01-10", "tipo": "controllo", "descrizione": "Controllo ortodontico mensile"}]',
  'Ortodonzia in corso - prevista rimozione estate 2025'
);

-- ===================================================================
-- 6. APPUNTAMENTI (Distribuiti su 30 giorni)
-- ===================================================================
DELETE FROM appuntamenti;
INSERT INTO appuntamenti (id, cliente_id, data, ora_inizio, ora_fine, servizi, note, stato, operatore_id, durata_minuti, prezzo_totale, created_at) VALUES
-- Oggi
('app-001', 'cli-001', date('now'), '09:00', '09:30', '["srv-001"]', 'Controllo semestrale', 'confermato', 'op-001', 30, 50.00, datetime('now')),
('app-002', 'cli-002', date('now'), '10:00', '10:45', '["srv-101"]', 'Igiene pre-parto', 'confermato', 'op-002', 45, 80.00, datetime('now')),
('app-003', 'cli-004', date('now'), '11:00', '11:20', '["srv-504"]', 'Controllo apparecchio', 'confermato', 'op-003', 20, 50.00, datetime('now')),
('app-004', 'cli-005', date('now'), '14:00', '15:00', '["srv-403"]', 'Impianto elemento 3.6', 'confermato', 'op-001', 60, 1200.00, datetime('now')),
('app-005', 'cli-006', date('now'), '15:30', '16:15', '["srv-101"]', 'Igiene trimestrale', 'confermato', 'op-002', 45, 80.00, datetime('now')),

-- Domani
('app-006', 'cli-003', date('now', '+1 day'), '09:00', '09:30', '["srv-001"]', '', 'confermato', 'op-001', 30, 50.00, datetime('now')),
('app-007', 'cli-007', date('now', '+1 day'), '10:00', '10:45', '["srv-102"]', 'Sbiancamento', 'confermato', 'op-002', 45, 250.00, datetime('now')),
('app-008', 'cli-008', date('now', '+1 day'), '11:00', '11:30', '["srv-001"]', '', 'confermato', 'op-001', 30, 50.00, datetime('now')),
('app-009', 'cli-009', date('now', '+1 day'), '14:00', '15:30', '["srv-403"]', 'Secondo impianto', 'confermato', 'op-001', 90, 1200.00, datetime('now')),
('app-010', 'cli-010', date('now', '+1 day'), '16:00', '16:45', '["srv-101"]', '', 'confermato', 'op-002', 45, 80.00, datetime('now')),

-- Prossima settimana
('app-011', 'cli-001', date('now', '+3 days'), '09:30', '10:15', '["srv-201"]', 'Otturazione 2.4', 'confermato', 'op-001', 45, 120.00, datetime('now')),
('app-012', 'cli-003', date('now', '+5 days'), '10:00', '11:00', '["srv-203"]', 'Devitalizzazione 1.6', 'confermato', 'op-001', 60, 280.00, datetime('now')),
('app-013', 'cli-005', date('now', '+7 days'), '14:00', '14:30', '["srv-401"]', 'Estrazione 3.8', 'confermato', 'op-001', 30, 100.00, datetime('now')),
('app-014', 'cli-007', date('now', '+7 days'), '15:00', '16:00', '["srv-301"]', 'Corona 2.1', 'confermato', 'op-001', 60, 650.00, datetime('now')),
('app-015', 'cli-002', date('now', '+10 days'), '09:00', '09:30', '["srv-001"]', 'Controllo post-partum', 'confermato', 'op-001', 30, 50.00, datetime('now'));

-- ===================================================================
-- 7. FATTURE (Elettroniche di test)
-- ===================================================================
DELETE FROM fatture;
INSERT INTO fatture (id, numero, data_emissione, cliente_id, totale_imponibile, totale_iva, totale_fattura, stato, tipo, note, data_scadenza, pagata, data_pagamento) VALUES
('fat-001', 'FAT/2025/001', '2025-01-15', 'cli-001', 409.84, 90.16, 500.00, 'emessa', 'fattura', 'Corona zirconio + controllo', '2025-02-15', 1, '2025-01-20'),
('fat-002', 'FAT/2025/002', '2025-01-18', 'cli-002', 65.57, 14.43, 80.00, 'emessa', 'fattura', 'Igiene professionale', '2025-02-18', 0, NULL),
('fat-003', 'FAT/2025/003', '2025-01-20', 'cli-003', 229.51, 50.49, 280.00, 'emessa', 'fattura', 'Devitalizzazione', '2025-02-20', 1, '2025-01-25'),
('fat-004', 'FAT/2025/004', '2025-01-22', 'cli-004', 532.79, 117.21, 650.00, 'emessa', 'fattura', 'Quota apparecchio ortodontico', '2025-02-22', 0, NULL),
('fat-005', 'FAT/2025/005', '2025-01-25', 'cli-005', 983.61, 216.39, 1200.00, 'emessa', 'fattura', 'Impianto dentale', '2025-02-25', 0, NULL);

-- ===================================================================
-- 8. LICENSE CACHE (Licenza Demo Attiva)
-- ===================================================================
DELETE FROM license_cache;
INSERT INTO license_cache (id, fingerprint, tier, status, trial_started_at, trial_ends_at, license_id, license_data, license_signature, licensee_name, licensee_email, enabled_verticals, features, is_ed25519, updated_at) VALUES (
  1,
  '93c4a3ab6fd31b9bb97a6f89aea59bf2',
  'enterprise',
  'active',
  datetime('now'),
  datetime('now', '+30 days'),
  'FLX-ENTERPRISE-CLG2TNL6',
  '{"version": "1.0", "license_id": "FLX-ENTERPRISE-CLG2TNL6", "tier": "enterprise", "issued_at": "2026-02-05T09:03:54.383509+00:00", "expires_at": null, "hardware_fingerprint": "93c4a3ab6fd31b9bb97a6f89aea59bf2", "licensee_name": "Studio Demo Srl", "licensee_email": "demo@fluxion.it", "enabled_verticals": ["odontoiatrica", "fisioterapia", "estetica", "parrucchiere", "veicoli", "carrozzeria", "medica", "fitness"], "max_operators": 0, "features": {"voice_agent": true, "whatsapp_ai": true, "rag_chat": true, "fatturazione_pa": true, "loyalty_advanced": true, "api_access": true, "max_verticals": 0}}',
  'DvLqtn1spS2aukP0fXHOCmWXdHJzfdI8FiCXmzFo9MsLyYSYluoqoIrc5Iv/Ze89HxkTiagom1hC3UygcEMjBw==',
  'Studio Demo Srl',
  'demo@fluxion.it',
  '["odontoiatrica", "fisioterapia", "estetica", "parrucchiere", "veicoli", "carrozzeria", "medica", "fitness"]',
  '{"voice_agent": true, "whatsapp_ai": true, "rag_chat": true, "fatturazione_pa": true, "loyalty_advanced": true, "api_access": true, "max_verticals": 0}',
  1,
  datetime('now')
);

-- ===================================================================
-- 9. PACCHETTI FEDELTA
-- ===================================================================
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, num_timbri, durata_giorni, sconto_percentuale, attivo, servizi_inclusi) VALUES
('pacc-001', 'Pacchetto Igiene Annuale', '4 igiene professionali + 4 controlli', 8, 365, 20, 1, '["srv-001", "srv-101"]'),
('pacc-002', 'Pacchetto Famiglia', 'Sconto famiglia fino a 4 membri', 12, 365, 15, 1, '["srv-001", "srv-101", "srv-201"]'),
('pacc-003', 'Pacchetto Sbiancamento', 'Sbiancamento in studio + kit casa', 2, 180, 25, 1, '["srv-102", "srv-103"]');

-- ===================================================================
-- 10. WHATSAPP TEMPLATES (Default)
-- ===================================================================
DELETE FROM whatsapp_templates;
INSERT INTO whatsapp_templates (id, nome, categoria, template, variabili, attivo) VALUES
('tpl-001', 'Promemoria Appuntamento', 'promemoria', 'Ciao {{nome}}, ti ricordiamo l''appuntamento fissato per {{data}} alle {{ora}}. Servizi: {{servizi}}. Per disdire rispondi ANNULLA.', '["nome", "data", "ora", "servizi"]', 1),
('tpl-002', 'Conferma Appuntamento', 'conferma', 'Ciao {{nome}}, confermiamo il tuo appuntamento per {{data}} alle {{ora}}. A presto!', '["nome", "data", "ora"]', 1),
('tpl-003', 'Richiesta Recensione', 'followup', 'Ciao {{nome}}, speriamo sia andato tutto bene! Lasciaci una recensione su Google: https://g.page/r/...', '["nome"]', 1);

-- Fine seed
