-- ═══════════════════════════════════════════════════════════════
-- FLUXION - Mock Data per Testing/Demo
-- Migration 010: Clienti, Servizi, Operatori, Appuntamenti
-- ═══════════════════════════════════════════════════════════════

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
-- APPUNTAMENTI (settimana corrente + prossima)
-- Usiamo date dinamiche relative a 'now'
-- ─────────────────────────────────────────────────────────────────

-- Oggi
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-001', 'cli-anna', 'srv-colore', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+9 hours'),
     datetime('now', 'localtime', 'start of day', '+10 hours'),
     60, 'confermato', 45.00, 0, 45.00, 'whatsapp'),
    ('app-002', 'cli-paolo', 'srv-taglio-uomo', 'op-marco',
     datetime('now', 'localtime', 'start of day', '+10 hours'),
     datetime('now', 'localtime', 'start of day', '+10 hours', '+30 minutes'),
     30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-003', 'cli-sara', 'srv-piega', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+11 hours'),
     datetime('now', 'localtime', 'start of day', '+11 hours', '+30 minutes'),
     30, 'confermato', 20.00, 0, 20.00, 'manuale'),
    ('app-004', 'cli-marco', 'srv-barba', 'op-marco',
     datetime('now', 'localtime', 'start of day', '+14 hours'),
     datetime('now', 'localtime', 'start of day', '+14 hours', '+20 minutes'),
     20, 'confermato', 12.00, 0, 12.00, 'voice'),
    ('app-005', 'cli-elena', 'srv-meches', 'op-luca',
     datetime('now', 'localtime', 'start of day', '+15 hours'),
     datetime('now', 'localtime', 'start of day', '+16 hours', '+30 minutes'),
     90, 'confermato', 65.00, 10, 58.50, 'manuale');

-- Domani
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-006', 'cli-giuseppe', 'srv-taglio-uomo', 'op-marco',
     datetime('now', 'localtime', 'start of day', '+1 day', '+9 hours'),
     datetime('now', 'localtime', 'start of day', '+1 day', '+9 hours', '+30 minutes'),
     30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-007', 'cli-francesca', 'srv-taglio-donna', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+1 day', '+10 hours'),
     datetime('now', 'localtime', 'start of day', '+1 day', '+10 hours', '+45 minutes'),
     45, 'confermato', 35.00, 0, 35.00, 'whatsapp'),
    ('app-008', 'cli-andrea', 'srv-trattamento', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+1 day', '+14 hours'),
     datetime('now', 'localtime', 'start of day', '+1 day', '+14 hours', '+45 minutes'),
     45, 'confermato', 30.00, 0, 30.00, 'manuale');

-- Dopodomani
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-009', 'cli-anna', 'srv-piega', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+2 days', '+11 hours'),
     datetime('now', 'localtime', 'start of day', '+2 days', '+11 hours', '+30 minutes'),
     30, 'confermato', 20.00, 0, 20.00, 'manuale'),
    ('app-010', 'cli-paolo', 'srv-taglio-uomo', 'op-luca',
     datetime('now', 'localtime', 'start of day', '+2 days', '+16 hours'),
     datetime('now', 'localtime', 'start of day', '+2 days', '+16 hours', '+30 minutes'),
     30, 'confermato', 18.00, 0, 18.00, 'voice');

-- Fra 3 giorni
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-011', 'cli-sara', 'srv-colore', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+3 days', '+10 hours'),
     datetime('now', 'localtime', 'start of day', '+3 days', '+11 hours'),
     60, 'confermato', 45.00, 0, 45.00, 'whatsapp'),
    ('app-012', 'cli-elena', 'srv-piega', 'op-luca',
     datetime('now', 'localtime', 'start of day', '+3 days', '+15 hours'),
     datetime('now', 'localtime', 'start of day', '+3 days', '+15 hours', '+30 minutes'),
     30, 'bozza', 20.00, 0, 20.00, 'manuale');

-- Fra 4 giorni
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-013', 'cli-marco', 'srv-taglio-uomo', 'op-marco',
     datetime('now', 'localtime', 'start of day', '+4 days', '+9 hours'),
     datetime('now', 'localtime', 'start of day', '+4 days', '+9 hours', '+30 minutes'),
     30, 'confermato', 18.00, 0, 18.00, 'manuale'),
    ('app-014', 'cli-francesca', 'srv-meches', 'op-giulia',
     datetime('now', 'localtime', 'start of day', '+4 days', '+14 hours'),
     datetime('now', 'localtime', 'start of day', '+4 days', '+15 hours', '+30 minutes'),
     90, 'confermato', 65.00, 0, 65.00, 'manuale');

-- Fra 5 giorni
INSERT OR IGNORE INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, sconto_percentuale, prezzo_finale, fonte_prenotazione) VALUES
    ('app-015', 'cli-giuseppe', 'srv-barba', 'op-marco',
     datetime('now', 'localtime', 'start of day', '+5 days', '+11 hours'),
     datetime('now', 'localtime', 'start of day', '+5 days', '+11 hours', '+20 minutes'),
     20, 'confermato', 12.00, 0, 12.00, 'voice');
