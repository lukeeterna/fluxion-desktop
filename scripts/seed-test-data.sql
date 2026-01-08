-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Script Seed Dati Test per iMac
-- Eseguire dopo installazione per avere dati pronti per test
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- 1. IMPOSTAZIONI BASE + API GROQ
-- ─────────────────────────────────────────────────────────────────

INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Salone Test Fluxion'),
('indirizzo', 'Via Roma 123'),
('citta', 'Milano'),
('cap', '20100'),
('provincia', 'MI'),
('telefono', '0212345678'),
('email', 'info@salonetestfluxion.it'),
('partita_iva', '02159940762'),
('codice_fiscale', 'DSTMGN81S12L738L'),
('regime_fiscale', 'RF19'),
('fluxion_ia_key', '{{GROQ_API_KEY}}'), -- Sostituire con API key reale su iMac
('cassa_fondo_iniziale', '100.00'),
('setup_completed', '1');

-- ─────────────────────────────────────────────────────────────────
-- 2. OPERATORI
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO operatori (id, nome, cognome, telefono, email, ruolo, colore_calendario, attivo) VALUES
('op-001', 'Mario', 'Rossi', '3331234567', 'mario.rossi@salone.it', 'titolare', '#10b981', 1),
('op-002', 'Giulia', 'Bianchi', '3339876543', 'giulia.bianchi@salone.it', 'senior', '#3b82f6', 1),
('op-003', 'Luca', 'Verdi', '3335551234', 'luca.verdi@salone.it', 'junior', '#f59e0b', 1);

-- ─────────────────────────────────────────────────────────────────
-- 3. SERVIZI
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO servizi (id, nome, descrizione, durata_minuti, prezzo, categoria, attivo) VALUES
('srv-001', 'Taglio Uomo', 'Taglio maschile classico', 30, 25.00, 'taglio', 1),
('srv-002', 'Taglio Donna', 'Taglio femminile con styling', 45, 35.00, 'taglio', 1),
('srv-003', 'Piega', 'Piega e styling', 30, 20.00, 'styling', 1),
('srv-004', 'Colore Base', 'Colorazione mono-tono', 90, 50.00, 'colore', 1),
('srv-005', 'Meches', 'Meches classiche o moderne', 120, 70.00, 'colore', 1),
('srv-006', 'Balayage', 'Tecnica balayage', 150, 120.00, 'colore', 1),
('srv-007', 'Trattamento Cheratina', 'Lisciatura alla cheratina', 180, 150.00, 'trattamento', 1),
('srv-008', 'Barba', 'Taglio e sistemazione barba', 20, 15.00, 'barba', 1),
('srv-009', 'Shampoo + Massaggio', 'Shampoo con massaggio rilassante', 15, 10.00, 'extra', 1),
('srv-010', 'Taglio + Barba', 'Combo taglio uomo + barba', 45, 35.00, 'combo', 1);

-- ─────────────────────────────────────────────────────────────────
-- 4. CLIENTI CON SOPRANNOME (per identificazione WhatsApp)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO clienti (id, nome, cognome, soprannome, telefono, email, data_nascita, indirizzo, citta, cap, provincia, codice_fiscale, partita_iva, codice_sdi, pec, note, fonte, loyalty_visits, is_vip, referred_by, consenso_marketing, consenso_whatsapp) VALUES
-- Clienti abituali
('cli-001', 'Marco', 'Ferrari', 'Marco il biondo', '3281234567', 'marco.ferrari@email.it', '1985-03-15', 'Via Dante 10', 'Milano', '20121', 'MI', 'FRRMRC85C15F205X', NULL, NULL, NULL, 'Cliente abituale, preferisce taglio corto', 'passaparola', 12, 1, NULL, 1, 1),
('cli-002', 'Anna', 'Colombo', 'Anna occhi blu', '3287654321', 'anna.colombo@email.it', '1990-07-22', 'Corso Buenos Aires 50', 'Milano', '20124', 'MI', 'CLMNNA90L62F205Y', NULL, NULL, NULL, 'Ama il balayage, allergica a alcuni prodotti', 'instagram', 8, 0, 'cli-001', 1, 1),
('cli-003', 'Giuseppe', 'Russo', 'Beppe', '3291112233', 'giuseppe.russo@email.it', '1978-11-03', 'Via Torino 25', 'Milano', '20123', 'MI', 'RSSGPP78S03F205Z', NULL, NULL, NULL, 'Viene ogni 3 settimane', 'google', 15, 1, NULL, 1, 1),
('cli-004', 'Francesca', 'Esposito', 'Francy', '3294445566', 'francesca.esposito@email.it', '1995-02-28', 'Piazza Duomo 1', 'Milano', '20122', 'MI', 'SPSFNC95B68F205A', NULL, NULL, NULL, 'Studentessa, preferisce sconti', 'tiktok', 3, 0, 'cli-002', 1, 1),
('cli-005', 'Roberto', 'Romano', 'Rob barba lunga', '3297778899', 'roberto.romano@email.it', '1982-09-10', 'Via Montenapoleone 8', 'Milano', '20121', 'MI', 'RMNRRT82P10F205B', NULL, NULL, NULL, 'Manager, appuntamenti serali', 'linkedin', 6, 0, NULL, 0, 1),

-- Clienti B2B (con dati fatturazione)
('cli-006', 'Azienda', 'Test SRL', NULL, '0212345678', 'fatture@aziendasrl.it', NULL, 'Via Industria 100', 'Milano', '20100', 'MI', NULL, '12345678901', 'ABC1234', 'aziendasrl@pec.it', 'Azienda cliente per fatture test', 'fiera', 2, 0, NULL, 1, 0),
('cli-007', 'Studio', 'Legale Rossi', NULL, '0298765432', 'studio@legalrossi.it', NULL, 'Corso Vittorio 50', 'Milano', '20122', 'MI', NULL, '98765432109', '0000000', 'legalrossi@pec.it', 'Studio legale, fattura mensile', 'referral', 1, 0, NULL, 1, 0),

-- Clienti normali
('cli-008', 'Simone', 'Galli', 'Simo', '3201234567', 'simone.galli@email.it', '1988-05-20', NULL, 'Monza', '20900', 'MB', NULL, NULL, NULL, NULL, 'Nuovo cliente', 'walk-in', 1, 0, NULL, 1, 1),
('cli-009', 'Valentina', 'Moretti', 'Vale capelli rossi', '3209876543', 'valentina.moretti@email.it', '1992-12-01', NULL, 'Sesto San Giovanni', '20099', 'MI', NULL, NULL, NULL, NULL, 'Colore naturale rosso', 'instagram', 4, 0, 'cli-004', 1, 1),
('cli-010', 'Paolo', 'Ricci', NULL, '3205554433', 'paolo.ricci@email.it', '1975-08-14', 'Via Garibaldi 33', 'Milano', '20121', 'MI', 'RCCPLA75M14F205C', NULL, NULL, NULL, 'Cliente storico', 'passaparola', 25, 1, NULL, 1, 1);

-- ─────────────────────────────────────────────────────────────────
-- 5. APPUNTAMENTI (oggi e prossimi giorni)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO appuntamenti (id, cliente_id, operatore_id, servizio_id, data_ora, durata_minuti, stato, note) VALUES
-- Oggi
('app-001', 'cli-001', 'op-001', 'srv-001', datetime('now', 'localtime', '+1 hour'), 30, 'confermato', 'Taglio come sempre'),
('app-002', 'cli-002', 'op-002', 'srv-006', datetime('now', 'localtime', '+2 hour'), 150, 'confermato', 'Balayage miele'),
('app-003', 'cli-003', 'op-001', 'srv-010', datetime('now', 'localtime', '+4 hour'), 45, 'proposto', 'Da confermare'),
-- Domani
('app-004', 'cli-004', 'op-003', 'srv-002', datetime('now', 'localtime', '+1 day', 'start of day', '+10 hours'), 45, 'confermato', NULL),
('app-005', 'cli-005', 'op-001', 'srv-001', datetime('now', 'localtime', '+1 day', 'start of day', '+18 hours'), 30, 'confermato', 'Orario serale'),
-- Dopodomani
('app-006', 'cli-009', 'op-002', 'srv-004', datetime('now', 'localtime', '+2 day', 'start of day', '+11 hours'), 90, 'confermato', 'Ritocco radici'),
('app-007', 'cli-010', 'op-001', 'srv-001', datetime('now', 'localtime', '+2 day', 'start of day', '+15 hours'), 30, 'proposto', NULL);

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
-- 8. FATTURE TEST
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO fatture (id, numero, anno, data_fattura, cliente_id, tipo_documento, stato, imponibile, iva, totale, pagata, data_pagamento, note) VALUES
('fat-001', 1, 2026, date('now', '-5 day'), 'cli-006', 'TD01', 'emessa', 150.00, 33.00, 183.00, 1, date('now', '-3 day'), 'Pacchetto servizi aziendale'),
('fat-002', 2, 2026, date('now', '-2 day'), 'cli-007', 'TD01', 'emessa', 100.00, 22.00, 122.00, 0, NULL, 'Servizi mensili'),
('fat-003', 3, 2026, date('now'), 'cli-006', 'TD01', 'bozza', 200.00, 44.00, 244.00, 0, NULL, 'Nuovi servizi');

-- Righe fattura
INSERT OR IGNORE INTO righe_fattura (id, fattura_id, descrizione, quantita, prezzo_unitario, aliquota_iva, importo) VALUES
('rf-001', 'fat-001', 'Pacchetto 10 tagli uomo', 1, 150.00, 22.00, 150.00),
('rf-002', 'fat-002', 'Servizi parrucchiere mese gennaio', 1, 100.00, 22.00, 100.00),
('rf-003', 'fat-003', 'Pacchetto colore + trattamento x5', 1, 200.00, 22.00, 200.00);

-- ─────────────────────────────────────────────────────────────────
-- 9. PACCHETTI CLIENTE
-- ─────────────────────────────────────────────────────────────────

-- Prima aggiungo pacchetti se non esistono
INSERT OR IGNORE INTO pacchetti (id, nome, descrizione, prezzo, servizi_inclusi, validita_giorni, attivo) VALUES
('pkg-001', 'Pacchetto 10 Tagli', '10 tagli uomo con sconto 20%', 200.00, 10, 365, 1),
('pkg-002', 'Abbonamento Colore', '4 colorazioni base', 180.00, 4, 180, 1),
('pkg-003', 'VIP Card', 'Accesso prioritario + sconto 15%', 99.00, 0, 365, 1);

-- Acquisti pacchetti
INSERT OR IGNORE INTO cliente_pacchetti (id, cliente_id, pacchetto_id, data_acquisto, data_scadenza, servizi_usati, servizi_totali, stato, prezzo_pagato) VALUES
('cp-001', 'cli-001', 'pkg-001', date('now', '-30 day'), date('now', '+335 day'), 3, 10, 'attivo', 200.00),
('cp-002', 'cli-002', 'pkg-002', date('now', '-60 day'), date('now', '+120 day'), 2, 4, 'attivo', 180.00),
('cp-003', 'cli-010', 'pkg-003', date('now', '-15 day'), date('now', '+350 day'), 0, 0, 'attivo', 99.00);

-- ─────────────────────────────────────────────────────────────────
-- 10. TEMPLATE WHATSAPP
-- ─────────────────────────────────────────────────────────────────

INSERT OR REPLACE INTO whatsapp_templates (id, nome, categoria, corpo, variabili, attivo) VALUES
('tpl-001', 'Promemoria Appuntamento', 'reminder', 'Ciao {{nome}}! Ti ricordiamo il tuo appuntamento per {{servizio}} il {{data}} alle {{ora}}. A presto!', '["nome", "servizio", "data", "ora"]', 1),
('tpl-002', 'Conferma Prenotazione', 'booking', 'Grazie {{nome}}! La tua prenotazione per {{servizio}} il {{data}} alle {{ora}} e'' confermata. Ti aspettiamo!', '["nome", "servizio", "data", "ora"]', 1),
('tpl-003', 'Auguri Compleanno', 'birthday', 'Tanti auguri {{nome}}! Per festeggiarti, ti regaliamo uno sconto del 20% sul prossimo servizio. Valido per 7 giorni!', '["nome"]', 1);

-- ─────────────────────────────────────────────────────────────────
-- 11. FAQ CUSTOM (apprese dal sistema)
-- ─────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO custom_faqs (id, domanda, risposta, categoria, created_at) VALUES
('cfaq-001', 'Fate anche extension?', 'Si, offriamo servizi di extension con capelli naturali. Prenota una consulenza gratuita per valutare insieme la soluzione migliore.', 'servizi', datetime('now', '-10 day')),
('cfaq-002', 'Avete parcheggio?', 'Si, abbiamo un parcheggio gratuito proprio davanti al salone. In alternativa ci sono strisce blu a 50 metri.', 'logistica', datetime('now', '-5 day')),
('cfaq-003', 'Posso portare il cane?', 'Certo! I piccoli amici a 4 zampe sono benvenuti, purche'' al guinzaglio e tranquilli.', 'politiche', datetime('now', '-3 day'));

-- ─────────────────────────────────────────────────────────────────
-- 12. AGGIORNA FAQ SETTINGS CON DATI REALI
-- ─────────────────────────────────────────────────────────────────

UPDATE faq_settings SET valore = '0212345678' WHERE chiave = 'numero_telefono';
UPDATE faq_settings SET valore = '3281536308' WHERE chiave = 'numero_whatsapp';
UPDATE faq_settings SET valore = 'Via Roma 123, 20100 Milano' WHERE chiave = 'indirizzo_salone';
UPDATE faq_settings SET valore = 'info@salonetestfluxion.it' WHERE chiave = 'email_salone';
UPDATE faq_settings SET valore = '@salonetestfluxion' WHERE chiave = 'link_social';

-- ═══════════════════════════════════════════════════════════════════
-- FINE SEED - Dati pronti per test su iMac
-- ═══════════════════════════════════════════════════════════════════
