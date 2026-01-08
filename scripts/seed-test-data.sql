-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Script Seed Dati Test per iMac
-- Schema corretto basato su migrations 001-009
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- 1. IMPOSTAZIONI BASE + DATI AZIENDA REALI + SKIP WIZARD
-- ─────────────────────────────────────────────────────────────────

INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo) VALUES
-- Setup completato (SALTA IL WIZARD!)
('setup_completed', 'true', 'boolean'),
-- Dati azienda reali (da .env)
('nome_attivita', 'Automation Business', 'string'),
('partita_iva', '02159940762', 'string'),
('codice_fiscale', 'DSTMGN81S12L738L', 'string'),
('indirizzo', 'Via degli Ulivi 16', 'string'),
('cap', '85024', 'string'),
('citta', 'Lavello', 'string'),
('provincia', 'PZ', 'string'),
('telefono', '+393281536308', 'string'),
('email', 'gianlucanewtech@gmail.com', 'string'),
('regime_fiscale', 'RF19', 'string'),
('categoria_attivita', 'salone', 'string'),
-- NOTA: fluxion_ia_key viene inserita da seed-imac.sh (legge da .env)
-- Impostazioni operative
('orario_apertura', '09:00', 'string'),
('orario_chiusura', '19:00', 'string'),
('giorni_lavorativi', '["mar","mer","gio","ven","sab"]', 'json'),
('durata_slot_minuti', '30', 'number'),
('reminder_ore_prima', '24', 'number'),
('whatsapp_attivo', 'true', 'boolean'),
('voice_agent_attivo', 'false', 'boolean');

-- ─────────────────────────────────────────────────────────────────
-- 2. OPERATORI
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO operatori (id, nome, cognome, telefono, email, ruolo, colore, attivo) VALUES
('op-001', 'Mario', 'Rossi', '3331234567', 'mario.rossi@salone.it', 'admin', '#10b981', 1),
('op-002', 'Giulia', 'Bianchi', '3339876543', 'giulia.bianchi@salone.it', 'operatore', '#3b82f6', 1),
('op-003', 'Luca', 'Verdi', '3335551234', 'luca.verdi@salone.it', 'operatore', '#f59e0b', 1);

-- ─────────────────────────────────────────────────────────────────
-- 3. SERVIZI
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO servizi (id, nome, descrizione, durata_minuti, prezzo, categoria, attivo, colore) VALUES
('srv-001', 'Taglio Uomo', 'Taglio maschile classico', 30, 25.00, 'taglio', 1, '#22D3EE'),
('srv-002', 'Taglio Donna', 'Taglio femminile con styling', 45, 35.00, 'taglio', 1, '#22D3EE'),
('srv-003', 'Piega', 'Piega e styling', 30, 20.00, 'styling', 1, '#A78BFA'),
('srv-004', 'Colore Base', 'Colorazione mono-tono', 90, 50.00, 'colore', 1, '#F472B6'),
('srv-005', 'Meches', 'Meches classiche o moderne', 120, 70.00, 'colore', 1, '#F472B6'),
('srv-006', 'Balayage', 'Tecnica balayage', 150, 120.00, 'colore', 1, '#F472B6'),
('srv-007', 'Trattamento Cheratina', 'Lisciatura alla cheratina', 180, 150.00, 'trattamento', 1, '#34D399'),
('srv-008', 'Barba', 'Taglio e sistemazione barba', 20, 15.00, 'barba', 1, '#FB923C'),
('srv-009', 'Shampoo + Massaggio', 'Shampoo con massaggio rilassante', 15, 10.00, 'extra', 1, '#94A3B8'),
('srv-010', 'Taglio + Barba', 'Combo taglio uomo + barba', 45, 35.00, 'combo', 1, '#22D3EE');

-- ─────────────────────────────────────────────────────────────────
-- 4. CLIENTI CON SOPRANNOME (per identificazione WhatsApp)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO clienti (id, nome, cognome, soprannome, telefono, email, data_nascita, indirizzo, citta, cap, provincia, codice_fiscale, partita_iva, codice_sdi, pec, note, fonte, loyalty_visits, is_vip, referral_cliente_id, consenso_marketing, consenso_whatsapp) VALUES
-- Clienti abituali
('cli-001', 'Marco', 'Ferrari', 'Marco il biondo', '3281234567', 'marco.ferrari@email.it', '1985-03-15', 'Via Dante 10', 'Milano', '20121', 'MI', 'FRRMRC85C15F205X', NULL, NULL, NULL, 'Cliente abituale, preferisce taglio corto', 'passaparola', 12, 1, NULL, 1, 1),
('cli-002', 'Anna', 'Colombo', 'Anna occhi blu', '3287654321', 'anna.colombo@email.it', '1990-07-22', 'Corso Buenos Aires 50', 'Milano', '20124', 'MI', 'CLMNNA90L62F205Y', NULL, NULL, NULL, 'Ama il balayage, allergica a alcuni prodotti', 'instagram', 8, 0, 'cli-001', 1, 1),
('cli-003', 'Giuseppe', 'Russo', 'Beppe', '3291112233', 'giuseppe.russo@email.it', '1978-11-03', 'Via Torino 25', 'Milano', '20123', 'MI', 'RSSGPP78S03F205Z', NULL, NULL, NULL, 'Viene ogni 3 settimane', 'google', 15, 1, NULL, 1, 1),
('cli-004', 'Francesca', 'Esposito', 'Francy', '3294445566', 'francesca.esposito@email.it', '1995-02-28', 'Piazza Duomo 1', 'Milano', '20122', 'MI', 'SPSFNC95B68F205A', NULL, NULL, NULL, 'Studentessa, preferisce sconti', 'tiktok', 3, 0, 'cli-002', 1, 1),
('cli-005', 'Roberto', 'Romano', 'Rob barba lunga', '3297778899', 'roberto.romano@email.it', '1982-09-10', 'Via Montenapoleone 8', 'Milano', '20121', 'MI', 'RMNRRT82P10F205B', NULL, NULL, NULL, 'Manager, appuntamenti serali', 'linkedin', 6, 0, NULL, 0, 1),
-- Clienti B2B (con dati fatturazione)
('cli-006', 'Mario', 'Bianchi', NULL, '0212345678', 'fatture@aziendasrl.it', NULL, 'Via Industria 100', 'Milano', '20100', 'MI', NULL, '12345678901', 'ABC1234', 'aziendasrl@pec.it', 'Azienda cliente per fatture test', 'fiera', 2, 0, NULL, 1, 0),
('cli-007', 'Giovanni', 'Rossi', NULL, '0298765432', 'studio@legalrossi.it', NULL, 'Corso Vittorio 50', 'Milano', '20122', 'MI', NULL, '98765432109', '0000000', 'legalrossi@pec.it', 'Studio legale, fattura mensile', 'referral', 1, 0, NULL, 1, 0),
-- Clienti normali
('cli-008', 'Simone', 'Galli', 'Simo', '3201234567', 'simone.galli@email.it', '1988-05-20', NULL, 'Monza', '20900', 'MB', NULL, NULL, NULL, NULL, 'Nuovo cliente', 'walk-in', 1, 0, NULL, 1, 1),
('cli-009', 'Valentina', 'Moretti', 'Vale capelli rossi', '3209876543', 'valentina.moretti@email.it', '1992-12-01', NULL, 'Sesto San Giovanni', '20099', 'MI', NULL, NULL, NULL, NULL, 'Colore naturale rosso', 'instagram', 4, 0, 'cli-004', 1, 1),
('cli-010', 'Paolo', 'Ricci', NULL, '3205554433', 'paolo.ricci@email.it', '1975-08-14', 'Via Garibaldi 33', 'Milano', '20121', 'MI', 'RCCPLA75M14F205C', NULL, NULL, NULL, 'Cliente storico', 'passaparola', 25, 1, NULL, 1, 1);

-- ─────────────────────────────────────────────────────────────────
-- 5. APPUNTAMENTI (oggi e prossimi giorni)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO appuntamenti (id, cliente_id, operatore_id, servizio_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, note, fonte_prenotazione) VALUES
-- Oggi
('app-001', 'cli-001', 'op-001', 'srv-001',
 datetime('now', 'localtime', '+1 hour'),
 datetime('now', 'localtime', '+1 hour', '+30 minutes'),
 30, 'confermato', 25.00, 0, 25.00, 'Taglio come sempre', 'manuale'),
('app-002', 'cli-002', 'op-002', 'srv-006',
 datetime('now', 'localtime', '+2 hour'),
 datetime('now', 'localtime', '+2 hour', '+150 minutes'),
 150, 'confermato', 120.00, 0, 120.00, 'Balayage miele', 'whatsapp'),
('app-003', 'cli-003', 'op-001', 'srv-010',
 datetime('now', 'localtime', '+4 hour'),
 datetime('now', 'localtime', '+4 hour', '+45 minutes'),
 45, 'bozza', 35.00, 0, 35.00, 'Da confermare', 'manuale'),
-- Domani
('app-004', 'cli-004', 'op-003', 'srv-002',
 datetime('now', 'localtime', '+1 day', 'start of day', '+10 hours'),
 datetime('now', 'localtime', '+1 day', 'start of day', '+10 hours', '+45 minutes'),
 45, 'confermato', 35.00, 10, 31.50, NULL, 'manuale'),
('app-005', 'cli-005', 'op-001', 'srv-001',
 datetime('now', 'localtime', '+1 day', 'start of day', '+18 hours'),
 datetime('now', 'localtime', '+1 day', 'start of day', '+18 hours', '+30 minutes'),
 30, 'confermato', 25.00, 0, 25.00, 'Orario serale', 'whatsapp'),
-- Dopodomani
('app-006', 'cli-009', 'op-002', 'srv-004',
 datetime('now', 'localtime', '+2 day', 'start of day', '+11 hours'),
 datetime('now', 'localtime', '+2 day', 'start of day', '+11 hours', '+90 minutes'),
 90, 'confermato', 50.00, 0, 50.00, 'Ritocco radici', 'manuale'),
('app-007', 'cli-010', 'op-001', 'srv-001',
 datetime('now', 'localtime', '+2 day', 'start of day', '+15 hours'),
 datetime('now', 'localtime', '+2 day', 'start of day', '+15 hours', '+30 minutes'),
 30, 'bozza', 25.00, 0, 25.00, NULL, 'manuale');

-- ─────────────────────────────────────────────────────────────────
-- 6. INCASSI (ultimi giorni)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO incassi (id, importo, metodo_pagamento, cliente_id, descrizione, categoria, data_incasso) VALUES
-- Ieri
('inc-001', 25.00, 'contanti', 'cli-001', 'Taglio uomo', 'servizio', datetime('now', 'localtime', '-1 day', '+10 hours')),
('inc-002', 35.00, 'carta', 'cli-002', 'Taglio donna', 'servizio', datetime('now', 'localtime', '-1 day', '+11 hours')),
('inc-003', 70.00, 'satispay', 'cli-009', 'Meches', 'servizio', datetime('now', 'localtime', '-1 day', '+14 hours')),
('inc-004', 15.00, 'contanti', 'cli-003', 'Barba', 'servizio', datetime('now', 'localtime', '-1 day', '+16 hours')),
-- 2 giorni fa
('inc-005', 120.00, 'carta', 'cli-002', 'Balayage', 'servizio', datetime('now', 'localtime', '-2 day', '+10 hours')),
('inc-006', 50.00, 'contanti', 'cli-004', 'Colore base', 'servizio', datetime('now', 'localtime', '-2 day', '+12 hours')),
('inc-007', 35.00, 'carta', 'cli-005', 'Taglio + Barba', 'servizio', datetime('now', 'localtime', '-2 day', '+18 hours')),
-- 3 giorni fa
('inc-008', 150.00, 'bonifico', 'cli-006', 'Pacchetto aziendale', 'pacchetto', datetime('now', 'localtime', '-3 day', '+10 hours')),
('inc-009', 25.00, 'contanti', 'cli-008', 'Taglio uomo', 'servizio', datetime('now', 'localtime', '-3 day', '+11 hours')),
('inc-010', 20.00, 'satispay', 'cli-001', 'Piega', 'servizio', datetime('now', 'localtime', '-3 day', '+15 hours'));

-- ─────────────────────────────────────────────────────────────────
-- 7. CHIUSURE CASSA (giorni precedenti)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO chiusure_cassa (id, data_chiusura, totale_contanti, totale_carte, totale_satispay, totale_bonifici, totale_altro, totale_giornata, numero_transazioni, fondo_cassa_iniziale, fondo_cassa_finale, note) VALUES
('ch-001', date('now', '-1 day'), 40.00, 35.00, 70.00, 0.00, 0.00, 145.00, 4, 100.00, 140.00, 'Giornata normale'),
('ch-002', date('now', '-2 day'), 50.00, 155.00, 0.00, 0.00, 0.00, 205.00, 3, 100.00, 150.00, 'Buona giornata'),
('ch-003', date('now', '-3 day'), 45.00, 0.00, 20.00, 150.00, 0.00, 215.00, 3, 100.00, 145.00, 'Bonifico aziendale');

-- ─────────────────────────────────────────────────────────────────
-- 8. FATTURE TEST (schema corretto da migration 007)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO fatture (
    id, numero, anno, numero_completo, tipo_documento, data_emissione,
    cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
    cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione,
    cliente_codice_sdi, cliente_pec,
    imponibile_totale, iva_totale, totale_documento,
    modalita_pagamento, condizioni_pagamento, stato
) VALUES
('fat-001', 1, 2026, '1/2026', 'TD01', date('now', '-5 day'),
 'cli-006', 'Mario Bianchi', '12345678901', NULL,
 'Via Industria 100', '20100', 'Milano', 'MI', 'IT',
 'ABC1234', 'aziendasrl@pec.it',
 150.00, 0.00, 150.00,
 'MP05', 'TP02', 'pagata'),
('fat-002', 2, 2026, '2/2026', 'TD01', date('now', '-2 day'),
 'cli-007', 'Giovanni Rossi', '98765432109', NULL,
 'Corso Vittorio 50', '20122', 'Milano', 'MI', 'IT',
 '0000000', 'legalrossi@pec.it',
 100.00, 0.00, 100.00,
 'MP05', 'TP02', 'emessa'),
('fat-003', 3, 2026, '3/2026', 'TD01', date('now'),
 'cli-006', 'Mario Bianchi', '12345678901', NULL,
 'Via Industria 100', '20100', 'Milano', 'MI', 'IT',
 'ABC1234', 'aziendasrl@pec.it',
 200.00, 0.00, 200.00,
 'MP05', 'TP02', 'bozza');

-- Aggiorna numeratore fatture
INSERT OR REPLACE INTO numeratore_fatture (anno, ultimo_numero) VALUES (2026, 3);

-- Righe fattura (schema corretto)
INSERT OR IGNORE INTO fatture_righe (
    id, fattura_id, numero_linea, descrizione, quantita, unita_misura,
    prezzo_unitario, sconto_percentuale, sconto_importo, prezzo_totale, aliquota_iva, natura
) VALUES
('rf-001', 'fat-001', 1, 'Pacchetto 10 tagli uomo', 1, 'PZ', 150.00, 0, 0, 150.00, 0.00, 'N2.2'),
('rf-002', 'fat-002', 1, 'Servizi parrucchiere mese gennaio', 1, 'PZ', 100.00, 0, 0, 100.00, 0.00, 'N2.2'),
('rf-003', 'fat-003', 1, 'Pacchetto colore + trattamento x5', 1, 'PZ', 200.00, 0, 0, 200.00, 0.00, 'N2.2');

-- ─────────────────────────────────────────────────────────────────
-- 9. PACCHETTI CLIENTE
-- ─────────────────────────────────────────────────────────────────

-- Acquisti pacchetti (usa pacchetti creati da migration 005)
INSERT OR IGNORE INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato) VALUES
('cp-001', 'cli-001', 'pkg_beauty_5', 'in_uso', 2, 5, date('now', '-30 day'), date('now', '-30 day'), date('now', '+150 day'), 'carta', 1),
('cp-002', 'cli-002', 'pkg_relax_10', 'venduto', 0, 10, date('now', '-10 day'), date('now', '-10 day'), date('now', '+355 day'), 'contanti', 1),
('cp-003', 'cli-010', 'pkg_vip_monthly', 'proposto', 0, 4, date('now'), NULL, NULL, NULL, 0);

-- ─────────────────────────────────────────────────────────────────
-- 10. AGGIORNA FAQ SETTINGS CON DATI REALI
-- ─────────────────────────────────────────────────────────────────

UPDATE faq_settings SET valore = '+393281536308' WHERE chiave = 'numero_telefono';
UPDATE faq_settings SET valore = '3281536308' WHERE chiave = 'numero_whatsapp';
UPDATE faq_settings SET valore = 'Via degli Ulivi 16, 85024 Lavello (PZ)' WHERE chiave = 'indirizzo_salone';
UPDATE faq_settings SET valore = 'gianlucanewtech@gmail.com' WHERE chiave = 'email_salone';
UPDATE faq_settings SET valore = '@automationbusiness' WHERE chiave = 'link_social';

-- ═══════════════════════════════════════════════════════════════════
-- FINE SEED - Dati pronti per test su iMac
-- ═══════════════════════════════════════════════════════════════════
