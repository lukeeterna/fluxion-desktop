-- ═══════════════════════════════════════════════════════════════
-- FLUXION - Mock Data per Testing/Demo
-- Migration 010: Clienti, Servizi, Operatori, Appuntamenti
-- ═══════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- SETUP COMPLETATO (skip wizard)
-- ─────────────────────────────────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo) VALUES
    ('setup_completed', 'true', 'boolean'),
    ('nome_attivita', 'Salone Demo FLUXION', 'string');

-- ─────────────────────────────────────────────────────────────────
-- SERVIZI (Salone esempio)
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO servizi (id, nome, descrizione, categoria, prezzo, durata_minuti, colore, attivo) VALUES
    ('srv-taglio-uomo', 'Taglio Uomo', 'Taglio classico maschile', 'Taglio', 18.00, 30, '#22D3EE', 1),
    ('srv-taglio-donna', 'Taglio Donna', 'Taglio femminile con styling', 'Taglio', 35.00, 45, '#F472B6', 1),
    ('srv-piega', 'Piega', 'Piega semplice', 'Styling', 20.00, 30, '#A78BFA', 1),
    ('srv-colore', 'Colore', 'Colorazione completa', 'Colore', 45.00, 60, '#FB923C', 1),
    ('srv-meches', 'Meches/Balayage', 'Schiariture e riflessi', 'Colore', 65.00, 90, '#FBBF24', 1),
    ('srv-trattamento', 'Trattamento Ristrutturante', 'Trattamento capelli danneggiati', 'Trattamento', 30.00, 45, '#34D399', 1),
    ('srv-barba', 'Barba', 'Rasatura e cura barba', 'Uomo', 12.00, 20, '#60A5FA', 1);

-- ─────────────────────────────────────────────────────────────────
-- OPERATORI
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO operatori (id, nome, cognome, email, telefono, ruolo, colore, attivo) VALUES
    ('op-marco', 'Marco', 'Rossi', 'marco@salone.it', '3331234567', 'operatore', '#22D3EE', 1),
    ('op-giulia', 'Giulia', 'Bianchi', 'giulia@salone.it', '3339876543', 'operatore', '#F472B6', 1),
    ('op-luca', 'Luca', 'Verdi', 'luca@salone.it', '3335551234', 'admin', '#A78BFA', 1);

-- Associazioni operatori-servizi
INSERT OR IGNORE INTO operatori_servizi (operatore_id, servizio_id) VALUES
    ('op-marco', 'srv-taglio-uomo'),
    ('op-marco', 'srv-barba'),
    ('op-giulia', 'srv-taglio-donna'),
    ('op-giulia', 'srv-piega'),
    ('op-giulia', 'srv-colore'),
    ('op-giulia', 'srv-meches'),
    ('op-giulia', 'srv-trattamento'),
    ('op-luca', 'srv-taglio-uomo'),
    ('op-luca', 'srv-taglio-donna'),
    ('op-luca', 'srv-piega'),
    ('op-luca', 'srv-colore');

-- ─────────────────────────────────────────────────────────────────
-- CLIENTI
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO clienti (id, nome, cognome, telefono, email, note, consenso_whatsapp) VALUES
    ('cli-anna', 'Anna', 'Ferrari', '3281234567', 'anna.ferrari@email.it', 'Cliente fedele, preferisce colori naturali', 1),
    ('cli-paolo', 'Paolo', 'Romano', '3289876543', 'paolo.romano@email.it', 'Taglio ogni 3 settimane', 1),
    ('cli-sara', 'Sara', 'Colombo', '3285551234', 'sara.colombo@email.it', 'Allergia a alcuni prodotti - chiedere sempre', 1),
    ('cli-marco', 'Marco', 'Ricci', '3281112233', 'marco.ricci@email.it', NULL, 0),
    ('cli-elena', 'Elena', 'Moretti', '3283334455', 'elena.moretti@email.it', 'VIP - cliente da 5 anni', 1),
    ('cli-giuseppe', 'Giuseppe', 'Esposito', '3286667788', NULL, 'Solo contanti', 0),
    ('cli-francesca', 'Francesca', 'Russo', '3288889900', 'francesca.russo@email.it', 'Porta sempre la figlia', 1),
    ('cli-andrea', 'Andrea', 'Conti', '3280001122', 'andrea.conti@email.it', NULL, 1);

-- ─────────────────────────────────────────────────────────────────
-- APPUNTAMENTI (date fisse Gennaio 2026)
-- Formato ISO 8601: YYYY-MM-DDTHH:MM:SS (con T, senza Z)
-- ─────────────────────────────────────────────────────────────────

-- 8 Gennaio 2026 (Oggi)
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-001', 'cli-anna', 'srv-colore', 'op-giulia', '2026-01-08T09:00:00', '2026-01-08T10:00:00', 60, 'confermato', 45.00, 0, 45.00, 'whatsapp'),
    ('app-002', 'cli-paolo', 'srv-taglio-uomo', 'op-marco', '2026-01-08T10:00:00', '2026-01-08T10:30:00', 30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-003', 'cli-sara', 'srv-piega', 'op-giulia', '2026-01-08T11:00:00', '2026-01-08T11:30:00', 30, 'confermato', 20.00, 0, 20.00, 'manuale'),
    ('app-004', 'cli-marco', 'srv-barba', 'op-marco', '2026-01-08T14:00:00', '2026-01-08T14:20:00', 20, 'confermato', 12.00, 0, 12.00, 'voice'),
    ('app-005', 'cli-elena', 'srv-meches', 'op-luca', '2026-01-08T15:00:00', '2026-01-08T16:30:00', 90, 'confermato', 65.00, 10, 58.50, 'manuale');

-- 9 Gennaio 2026
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-006', 'cli-giuseppe', 'srv-taglio-uomo', 'op-marco', '2026-01-09T09:00:00', '2026-01-09T09:30:00', 30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-007', 'cli-francesca', 'srv-taglio-donna', 'op-giulia', '2026-01-09T10:00:00', '2026-01-09T10:45:00', 45, 'confermato', 35.00, 0, 35.00, 'whatsapp'),
    ('app-008', 'cli-andrea', 'srv-trattamento', 'op-giulia', '2026-01-09T14:00:00', '2026-01-09T14:45:00', 45, 'confermato', 30.00, 0, 30.00, 'manuale');

-- 10 Gennaio 2026
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-009', 'cli-anna', 'srv-piega', 'op-giulia', '2026-01-10T11:00:00', '2026-01-10T11:30:00', 30, 'confermato', 20.00, 0, 20.00, 'manuale'),
    ('app-010', 'cli-paolo', 'srv-taglio-uomo', 'op-luca', '2026-01-10T16:00:00', '2026-01-10T16:30:00', 30, 'confermato', 18.00, 0, 18.00, 'voice');

-- 11 Gennaio 2026
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-011', 'cli-sara', 'srv-colore', 'op-giulia', '2026-01-11T10:00:00', '2026-01-11T11:00:00', 60, 'confermato', 45.00, 0, 45.00, 'whatsapp'),
    ('app-012', 'cli-elena', 'srv-piega', 'op-luca', '2026-01-11T15:00:00', '2026-01-11T15:30:00', 30, 'bozza', 20.00, 0, 20.00, 'manuale');

-- 12 Gennaio 2026
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-013', 'cli-marco', 'srv-taglio-uomo', 'op-marco', '2026-01-12T09:00:00', '2026-01-12T09:30:00', 30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-014', 'cli-francesca', 'srv-meches', 'op-giulia', '2026-01-12T14:00:00', '2026-01-12T15:30:00', 90, 'confermato', 65.00, 0, 65.00, 'manuale');

-- 13 Gennaio 2026
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-015', 'cli-giuseppe', 'srv-barba', 'op-marco', '2026-01-13T11:00:00', '2026-01-13T11:20:00', 20, 'confermato', 12.00, 0, 12.00, 'voice');

-- ─────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI FATTURAZIONE
-- ─────────────────────────────────────────────────────────────────
INSERT OR REPLACE INTO impostazioni_fatturazione (id, denominazione, partita_iva, codice_fiscale, regime_fiscale, indirizzo, cap, comune, provincia, telefono, email, ultimo_numero, anno_corrente) VALUES
    ('default', 'Salone Demo FLUXION', '02159940762', 'DSTMGN81S12L738L', 'RF19', 'Via degli Ulivi 16', '85024', 'Lavello', 'PZ', '3281536308', 'demo@fluxion.it', 3, 2026);

-- ─────────────────────────────────────────────────────────────────
-- FATTURE (Demo)
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO fatture (id, numero, anno, numero_completo, tipo_documento, data_emissione, cliente_id, cliente_denominazione, cliente_partita_iva, imponibile_totale, iva_totale, totale_documento, stato) VALUES
    ('fat-001', 1, 2026, '1/2026', 'TD01', '2026-01-02', 'cli-elena', 'Elena Moretti', NULL, 65.00, 0, 65.00, 'pagata'),
    ('fat-002', 2, 2026, '2/2026', 'TD01', '2026-01-05', 'cli-anna', 'Anna Ferrari', NULL, 45.00, 0, 45.00, 'emessa'),
    ('fat-003', 3, 2026, '3/2026', 'TD01', '2026-01-07', 'cli-francesca', 'Francesca Russo', NULL, 35.00, 0, 35.00, 'bozza');

-- ─────────────────────────────────────────────────────────────────
-- INCASSI (Ultimi giorni)
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO incassi (id, importo, metodo_pagamento, cliente_id, descrizione, categoria, operatore_id, data_incasso) VALUES
    ('inc-001', 65.00, 'carta', 'cli-elena', 'Meches/Balayage', 'servizio', 'op-giulia', '2026-01-06T16:30:00'),
    ('inc-002', 18.00, 'contanti', 'cli-paolo', 'Taglio Uomo', 'servizio', 'op-marco', '2026-01-06T10:30:00'),
    ('inc-003', 45.00, 'satispay', 'cli-anna', 'Colore', 'servizio', 'op-giulia', '2026-01-07T10:00:00'),
    ('inc-004', 35.00, 'carta', 'cli-francesca', 'Taglio Donna', 'servizio', 'op-giulia', '2026-01-07T11:00:00'),
    ('inc-005', 12.00, 'contanti', 'cli-giuseppe', 'Barba', 'servizio', 'op-marco', '2026-01-07T14:30:00'),
    ('inc-006', 20.00, 'contanti', 'cli-sara', 'Piega', 'servizio', 'op-luca', '2026-01-07T15:00:00');

-- ─────────────────────────────────────────────────────────────────
-- CHIUSURA CASSA (Ieri)
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO chiusure_cassa (id, data_chiusura, totale_contanti, totale_carte, totale_satispay, totale_giornata, numero_transazioni, fondo_cassa_iniziale, fondo_cassa_finale, operatore_id) VALUES
    ('chiu-001', '2026-01-07', 50.00, 100.00, 45.00, 195.00, 6, 100.00, 150.00, 'op-luca');
