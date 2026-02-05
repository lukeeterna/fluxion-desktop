-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Demo Database Seed V2 (Schema Reale)
-- Popola il database con dati completi per testing
-- ═══════════════════════════════════════════════════════════════════

-- ===================================================================
-- 1. IMPOSTAZIONI (Config base)
-- ===================================================================
INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo) VALUES
('setup_completato', 'true', 'boolean'),
('azienda_nome', 'Studio Dentistico Demo', 'string'),
('azienda_indirizzo', 'Via Roma 123, Milano', 'string'),
('macro_categoria', 'medico', 'string'),
('micro_categoria', 'odontoiatra', 'string'),
('license_tier', 'enterprise', 'string'),
('tema_colore', 'cyan', 'string');

-- ===================================================================
-- 2. OPERATORI (4 profili diversi)
-- ===================================================================
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, email, telefono, ruolo, colore, attivo, specializzazioni, descrizione_positiva, anni_esperienza) VALUES 
('op-001', 'Mario', 'Rossi', 'mario.rossi@studiodemo.it', '+39 333 1111111', 'admin', '#3B82F6', 1, '["Protesi", "Implantologia"]', 'Direttore sanitario, specialista in chirurgia implantare', 15),
('op-002', 'Anna', 'Bianchi', 'anna.bianchi@studiodemo.it', '+39 333 2222222', 'operatore', '#EC4899', 1, '["Igiene", "Sbiancamento"]', 'Igienista dentale, esperta in prevenzione', 8),
('op-003', 'Luca', 'Verdi', 'luca.verdi@studiodemo.it', '+39 333 3333333', 'operatore', '#10B981', 1, '["Ortodonzia"]', 'Specialista in ortodonzia invisibile', 10),
('op-004', 'Giulia', 'Neri', 'giulia.neri@studiodemo.it', '+39 333 4444444', 'reception', '#F59E0B', 1, '["Accoglienza"]', 'Responsabile accoglienza e amministrazione', 5);

-- ===================================================================
-- 3. SERVIZI (Categorie Odontoiatriche)
-- ===================================================================
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, durata_minuti, prezzo, categoria, colore, attivo, iva_percentuale) VALUES
-- Diagnostica
('srv-001', 'Visita di controllo', 'Controllo denti e gengive', 30, 50.00, 'diagnostica', '#3B82F6', 1, 22),
('srv-002', 'Panoramica dentale', 'Radiografia panoramica digitale', 15, 40.00, 'diagnostica', '#3B82F6', 1, 22),
('srv-003', 'Rx endorale', 'Radiografia endorale singolo elemento', 15, 25.00, 'diagnostica', '#3B82F6', 1, 22),

-- Igiene
('srv-101', 'Igiene professionale', 'Pulizia professionale denti', 45, 80.00, 'igiene', '#10B981', 1, 22),
('srv-102', 'Sbiancamento in studio', 'Sbiancamento professionale', 60, 250.00, 'igiene', '#10B981', 1, 22),

-- Conservativa
('srv-201', 'Otturazione composito', 'Otturazione estetica', 45, 120.00, 'conservativa', '#F59E0B', 1, 22),
('srv-202', 'Devitalizzazione', 'Devitalizzazione canale', 60, 280.00, 'conservativa', '#F59E0B', 1, 22),

-- Protesi
('srv-301', 'Corona ceramica-zirconio', 'Corona fisica zirconio', 60, 650.00, 'protesi', '#8B5CF6', 1, 22),
('srv-302', 'Ponte 3 elementi', 'Ponte fisso 3 corone', 90, 1500.00, 'protesi', '#8B5CF6', 1, 22),

-- Chirurgia
('srv-401', 'Estrazione semplice', 'Estrazione dente', 30, 100.00, 'chirurgia', '#EF4444', 1, 22),
('srv-402', 'Impianto dentale', 'Impianto singolo con chirurgia', 90, 1200.00, 'chirurgia', '#EF4444', 1, 22),

-- Ortodonzia
('srv-501', 'Apparecchio fisso', 'Ortodonzia fisso installazione', 90, 3500.00, 'ortodonzia', '#EC4899', 1, 22),
('srv-502', 'Controllo ortodontico', 'Controllo mensile apparecchio', 20, 50.00, 'ortodonzia', '#EC4899', 1, 22);

-- Associazione operatori-servizi
DELETE FROM operatori_servizi;
INSERT INTO operatori_servizi (operatore_id, servizio_id) VALUES
('op-001', 'srv-001'), ('op-001', 'srv-002'), ('op-001', 'srv-003'), ('op-001', 'srv-201'), ('op-001', 'srv-202'), ('op-001', 'srv-301'), ('op-001', 'srv-302'), ('op-001', 'srv-401'), ('op-001', 'srv-402'),
('op-002', 'srv-001'), ('op-002', 'srv-101'), ('op-002', 'srv-102'),
('op-003', 'srv-001'), ('op-003', 'srv-501'), ('op-003', 'srv-502');

-- ===================================================================
-- 4. CLIENTI (10 clienti di esempio)
-- ===================================================================
DELETE FROM clienti;
INSERT INTO clienti (id, nome, cognome, email, telefono, data_nascita, indirizzo, citta, cap, provincia, codice_fiscale, note, tags, consenso_marketing, consenso_whatsapp) VALUES
('cli-001', 'Marco', 'Ferrari', 'marco.ferrari@email.it', '+39 340 1111111', '1985-03-15', 'Via Garibaldi 1', 'Milano', '20121', 'MI', 'FRAMRC85C15F205Z', 'Paziente da 5 anni, paura del dentista', '["fedele", "paura-dentista"]', 1, 1),
('cli-002', 'Laura', 'Colombo', 'laura.colombo@email.it', '+39 340 2222222', '1990-07-22', 'Via Dante 45', 'Milano', '20123', 'MI', 'CLMLRA90L62F205Z', 'Gravidanza in corso - attenzione ai raggi X', '["gravidanza"]', 1, 1),
('cli-003', 'Giuseppe', 'Ricci', 'giuseppe.ricci@email.it', '+39 340 3333333', '1978-11-08', 'Corso Buenos Aires 123', 'Milano', '20124', 'MI', 'RCCGPP78S08F205Z', 'Iperteso, allergia al lattice', '["allergie", "patologie"]', 0, 1),
('cli-004', 'Francesca', 'Marino', 'francesca.marino@email.it', '+39 340 4444444', '1995-01-30', 'Piazza Duomo 5', 'Milano', '20121', 'MI', 'MRNFNC95A70F205Z', 'Ortodonzia in corso', '["ortodonzia"]', 1, 1),
('cli-005', 'Antonio', 'Greco', 'antonio.greco@email.it', '+39 340 5555555', '1982-09-12', 'Viale Monza 78', 'Milano', '20127', 'MI', 'GRCNTN82P12F205Z', 'Diabete tipo 2', '["patologie"]', 0, 1),
('cli-006', 'Stefania', 'Conti', 'stefania.conti@email.it', '+39 340 6666666', '1988-05-18', 'Via Torino 234', 'Milano', '20123', 'MI', 'CNTSFN88E58F205Z', 'Pacchetto igiene annuale', '["pacchetto"]', 1, 1),
('cli-007', 'Roberto', 'Lombardi', 'roberto.lombardi@email.it', '+39 340 7777777', '1975-12-03', 'Corso Magenta 89', 'Milano', '20123', 'MI', 'LMBRRT75T03F205Z', 'Paziente VIP, preferisce mattino', '["vip", "mattino"]', 1, 1),
('cli-008', 'Patrizia', 'Serra', 'patrizia.serra@email.it', '+39 340 8888888', '1992-04-25', 'Via Brera 12', 'Milano', '20121', 'MI', 'SRAPTZ92E65F205Z', 'Tessera fedeltà attiva', '["fedelta"]', 1, 1),
('cli-009', 'Davide', 'Cattaneo', 'davide.cattaneo@email.it', '+39 340 9999999', '1980-08-14', 'Viale Tunisia 56', 'Milano', '20124', 'MI', 'CTTDVD80M14F205Z', 'Impianti in corso', '["implantologia"]', 0, 1),
('cli-010', 'Elena', 'Monti', 'elena.monti@email.it', '+39 341 0000000', '1987-02-28', 'Via Washington 67', 'Milano', '20146', 'MI', 'MNTLNE87B68F205Z', 'Allergie multiple dichiarate', '["allergie"]', 1, 1);

-- ===================================================================
-- 5. APPUNTAMENTI (Distribuiti su vari giorni)
-- ===================================================================
DELETE FROM appuntamenti;
INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, prezzo, prezzo_finale, stato, note, fonte_prenotazione) VALUES
-- Oggi
('app-001', 'cli-001', 'srv-001', 'op-001', datetime('now', 'start of day', '+9 hours'), datetime('now', 'start of day', '+9 hours', '+30 minutes'), 30, 50.00, 50.00, 'confermato', 'Controllo semestrale', 'manuale'),
('app-002', 'cli-002', 'srv-101', 'op-002', datetime('now', 'start of day', '+10 hours'), datetime('now', 'start of day', '+10 hours', '+45 minutes'), 45, 80.00, 80.00, 'confermato', 'Igiene pre-parto', 'manuale'),
('app-003', 'cli-004', 'srv-502', 'op-003', datetime('now', 'start of day', '+11 hours'), datetime('now', 'start of day', '+11 hours', '+20 minutes'), 20, 50.00, 50.00, 'confermato', 'Controllo apparecchio', 'manuale'),
('app-004', 'cli-005', 'srv-402', 'op-001', datetime('now', 'start of day', '+14 hours'), datetime('now', 'start of day', '+15 hours', '+30 minutes'), 90, 1200.00, 1200.00, 'confermato', 'Impianto elemento 3.6', 'manuale'),
('app-005', 'cli-006', 'srv-101', 'op-002', datetime('now', 'start of day', '+15 hours', '+30 minutes'), datetime('now', 'start of day', '+16 hours', '+15 minutes'), 45, 80.00, 80.00, 'confermato', 'Igiene trimestrale', 'manuale'),

-- Domani
('app-006', 'cli-003', 'srv-001', 'op-001', datetime('now', '+1 day', 'start of day', '+9 hours'), datetime('now', '+1 day', 'start of day', '+9 hours', '+30 minutes'), 30, 50.00, 50.00, 'confermato', '', 'manuale'),
('app-007', 'cli-007', 'srv-102', 'op-002', datetime('now', '+1 day', 'start of day', '+10 hours'), datetime('now', '+1 day', 'start of day', '+11 hours'), 60, 250.00, 250.00, 'confermato', 'Sbiancamento', 'whatsapp'),
('app-008', 'cli-008', 'srv-001', 'op-001', datetime('now', '+1 day', 'start of day', '+11 hours'), datetime('now', '+1 day', 'start of day', '+11 hours', '+30 minutes'), 30, 50.00, 50.00, 'confermato', '', 'manuale'),
('app-009', 'cli-009', 'srv-402', 'op-001', datetime('now', '+1 day', 'start of day', '+14 hours'), datetime('now', '+1 day', 'start of day', '+15 hours', '+30 minutes'), 90, 1200.00, 1200.00, 'confermato', 'Secondo impianto', 'manuale'),
('app-010', 'cli-010', 'srv-101', 'op-002', datetime('now', '+1 day', 'start of day', '+16 hours'), datetime('now', '+1 day', 'start of day', '+16 hours', '+45 minutes'), 45, 80.00, 80.00, 'confermato', '', 'manuale'),

-- Prossima settimana
('app-011', 'cli-001', 'srv-201', 'op-001', datetime('now', '+3 days', 'start of day', '+9 hours', '+30 minutes'), datetime('now', '+3 days', 'start of day', '+10 hours', '+15 minutes'), 45, 120.00, 120.00, 'confermato', 'Otturazione 2.4', 'manuale'),
('app-012', 'cli-003', 'srv-202', 'op-001', datetime('now', '+5 days', 'start of day', '+10 hours'), datetime('now', '+5 days', 'start of day', '+11 hours'), 60, 280.00, 280.00, 'confermato', 'Devitalizzazione 1.6', 'manuale'),
('app-013', 'cli-005', 'srv-401', 'op-001', datetime('now', '+7 days', 'start of day', '+14 hours'), datetime('now', '+7 days', 'start of day', '+14 hours', '+30 minutes'), 30, 100.00, 100.00, 'confermato', 'Estrazione 3.8', 'manuale'),
('app-014', 'cli-007', 'srv-301', 'op-001', datetime('now', '+7 days', 'start of day', '+15 hours'), datetime('now', '+7 days', 'start of day', '+16 hours'), 60, 650.00, 650.00, 'confermato', 'Corona 2.1', 'manuale'),
('app-015', 'cli-002', 'srv-001', 'op-001', datetime('now', '+10 days', 'start of day', '+9 hours'), datetime('now', '+10 days', 'start of day', '+9 hours', '+30 minutes'), 30, 50.00, 50.00, 'confermato', 'Controllo post-partum', 'whatsapp');

-- ===================================================================
-- 6. WHATSAPP TEMPLATES
-- ===================================================================
DELETE FROM whatsapp_templates;
INSERT INTO whatsapp_templates (id, nome, categoria, descrizione, template_text, variabili) VALUES
('tpl-001', 'Promemoria Appuntamento', 'reminder', 'Promemoria automatico', 'Ciao {{nome}}, ti ricordiamo l''appuntamento fissato per {{data}} alle {{ora}}. Per disdire rispondi ANNULLA.', 'nome,data,ora'),
('tpl-002', 'Conferma Appuntamento', 'conferma', 'Conferma prenotazione', 'Ciao {{nome}}, confermiamo il tuo appuntamento per {{data}} alle {{ora}}. A presto!', 'nome,data,ora'),
('tpl-003', 'Richiesta Recensione', 'followup', 'Follow-up post-visita', 'Ciao {{nome}}, speriamo sia andato tutto bene! Lasciaci una recensione su Google. Grazie!', 'nome');

-- ===================================================================
-- 7. CHIAMATE VOICE (Esempi)
-- ===================================================================
DELETE FROM chiamate_voice;
INSERT INTO chiamate_voice (id, telefono, cliente_id, direzione, durata_secondi, trascrizione, intent_rilevato, esito) VALUES
('call-001', '+39 340 1111111', 'cli-001', 'inbound', 180, 'Buongiorno, vorrei prenotare una visita di controllo per la prossima settimana. Sono il dottor Rossi? No sono il paziente Ferrari. Ah ok, vedo che ha già un appuntamento...', 'prenotazione', 'successo'),
('call-002', '+39 340 2222222', 'cli-002', 'outbound', 45, 'Buongiorno, le confermiamo l''appuntamento di domani alle 10. Perfetto, arrivederci.', 'conferma', 'successo');

-- ===================================================================
-- 8. MESSAGGI WHATSAPP
-- ===================================================================
DELETE FROM messaggi_whatsapp;
INSERT INTO messaggi_whatsapp (id, cliente_id, telefono, direzione, tipo, contenuto, stato, template_id) VALUES
('msg-001', 'cli-001', '+39 340 1111111', 'outbound', 'text', 'Ciao Marco, ti ricordiamo l''appuntamento fissato per domani alle 09:00.', 'sent', 'tpl-001'),
('msg-002', 'cli-002', '+39 340 2222222', 'outbound', 'text', 'Ciao Laura, confermiamo il tuo appuntamento per domani alle 10:00. A presto!', 'delivered', 'tpl-002'),
('msg-003', 'cli-007', '+39 340 7777777', 'inbound', 'text', 'Posso spostare l''appuntamento di venerdì alla stessa ora ma il giorno dopo?', 'pending', NULL);

-- Fine seed
