-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Mock Data per Test
-- Eseguire dopo la creazione del DB per popolare con dati demo
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci dati esistenti (in ordine inverso per foreign keys)
DELETE FROM fatture_pagamenti;
DELETE FROM fatture_righe;
DELETE FROM fatture_riepilogo_iva;
DELETE FROM fatture;
DELETE FROM appuntamenti;
DELETE FROM clienti_pacchetti;
DELETE FROM pacchetto_servizi;
DELETE FROM pacchetti;
DELETE FROM waitlist;
DELETE FROM servizi;
DELETE FROM operatori;
DELETE FROM clienti;
DELETE FROM impostazioni_fatturazione;

-- ───────────────────────────────────────────────────────────────────
-- CLIENTI (10 clienti mock)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO clienti (id, nome, cognome, email, telefono, note, loyalty_visits, loyalty_threshold, is_vip, referral_source, created_at, updated_at)
VALUES
  ('cli_001', 'Mario', 'Rossi', 'mario.rossi@email.it', '3331234567', 'Cliente abituale', 8, 10, 0, NULL, '2025-01-15 10:00:00', '2026-01-05 10:00:00'),
  ('cli_002', 'Giulia', 'Bianchi', 'giulia.bianchi@email.it', '3339876543', 'Preferisce mattina', 12, 10, 1, 'Passaparola', '2025-02-20 14:30:00', '2026-01-05 10:00:00'),
  ('cli_003', 'Luca', 'Verdi', 'luca.verdi@email.it', '3351112233', NULL, 3, 10, 0, 'Google', '2025-03-10 09:15:00', '2026-01-05 10:00:00'),
  ('cli_004', 'Anna', 'Ferrari', 'anna.ferrari@email.it', '3384445566', 'Allergica al nichel', 5, 10, 0, 'cli_002', '2025-04-05 16:00:00', '2026-01-05 10:00:00'),
  ('cli_005', 'Paolo', 'Romano', 'paolo.romano@email.it', '3397778899', 'VIP aziendale', 15, 10, 1, 'LinkedIn', '2025-05-12 11:30:00', '2026-01-05 10:00:00'),
  ('cli_006', 'Sara', 'Conti', 'sara.conti@email.it', '3401234567', NULL, 2, 10, 0, NULL, '2025-06-18 13:45:00', '2026-01-05 10:00:00'),
  ('cli_007', 'Marco', 'Galli', 'marco.galli@email.it', '3412345678', 'Paga sempre cash', 7, 10, 0, 'Facebook', '2025-07-22 10:00:00', '2026-01-05 10:00:00'),
  ('cli_008', 'Elena', 'Marino', 'elena.marino@email.it', '3423456789', NULL, 1, 10, 0, 'Instagram', '2025-08-30 15:20:00', '2026-01-05 10:00:00'),
  ('cli_009', 'Andrea', 'Costa', 'andrea.costa@email.it', '3434567890', 'Preferisce pomeriggio', 9, 10, 0, 'cli_005', '2025-09-14 09:00:00', '2026-01-05 10:00:00'),
  ('cli_010', 'Francesca', 'Rizzo', 'francesca.rizzo@email.it', '3445678901', 'Cliente premium', 20, 10, 1, 'Evento', '2025-10-25 17:00:00', '2026-01-05 10:00:00');

-- ───────────────────────────────────────────────────────────────────
-- SERVIZI (8 servizi mock)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO servizi (id, nome, descrizione, durata_minuti, prezzo, colore, attivo, created_at, updated_at)
VALUES
  ('srv_001', 'Taglio Uomo', 'Taglio capelli classico uomo', 30, 18.00, '#3B82F6', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_002', 'Taglio Donna', 'Taglio capelli donna con piega', 60, 35.00, '#EC4899', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_003', 'Colore', 'Colorazione capelli completa', 90, 55.00, '#8B5CF6', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_004', 'Piega', 'Messa in piega', 30, 20.00, '#F59E0B', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_005', 'Trattamento Cheratina', 'Trattamento lisciante alla cheratina', 120, 80.00, '#10B981', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_006', 'Barba', 'Regolazione e styling barba', 20, 12.00, '#6366F1', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_007', 'Shampoo Massaggio', 'Shampoo con massaggio rilassante', 15, 8.00, '#14B8A6', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('srv_008', 'Consulenza Stile', 'Consulenza personalizzata look', 45, 25.00, '#F97316', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00');

-- ───────────────────────────────────────────────────────────────────
-- OPERATORI (6 operatori mock con ruoli diversi)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO operatori (id, nome, cognome, email, telefono, ruolo, colore, attivo, created_at, updated_at)
VALUES
  ('op_001', 'Giovanni', 'Esposito', 'giovanni@fluxion.it', '3501234567', 'admin', '#EF4444', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('op_002', 'Maria', 'De Luca', 'maria@fluxion.it', '3502345678', 'operatore', '#22C55E', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('op_003', 'Roberto', 'Santoro', 'roberto@fluxion.it', '3503456789', 'operatore', '#3B82F6', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('op_004', 'Chiara', 'Greco', 'chiara@fluxion.it', '3504567890', 'operatore', '#A855F7', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('op_005', 'Laura', 'Ferretti', 'laura@fluxion.it', '3505678901', 'reception', '#F59E0B', 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('op_006', 'Marco', 'Bianchi', 'marco@fluxion.it', '3506789012', 'operatore', '#06B6D4', 0, '2025-01-01 00:00:00', '2025-01-01 00:00:00');

-- Associazione operatori-servizi
INSERT INTO operatori_servizi (operatore_id, servizio_id) VALUES
  ('op_001', 'srv_001'), ('op_001', 'srv_006'), -- Giovanni: Taglio Uomo, Barba
  ('op_002', 'srv_002'), ('op_002', 'srv_003'), ('op_002', 'srv_004'), ('op_002', 'srv_005'), -- Maria: Donna, Colore, Piega, Cheratina
  ('op_003', 'srv_001'), ('op_003', 'srv_002'), ('op_003', 'srv_004'), -- Roberto: Taglio Uomo/Donna, Piega
  ('op_004', 'srv_003'), ('op_004', 'srv_005'), ('op_004', 'srv_008'); -- Chiara: Colore, Cheratina, Consulenza

-- ───────────────────────────────────────────────────────────────────
-- PACCHETTI (3 pacchetti mock)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO pacchetti (id, nome, descrizione, prezzo, servizi_inclusi, validita_giorni, sconto_percentuale, created_at, updated_at)
VALUES
  ('pac_001', 'Pacchetto Uomo 5x', '5 tagli uomo a prezzo scontato', 75.00, 5, 180, 17, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('pac_002', 'Pacchetto Donna Premium', '3 taglio + colore', 200.00, 3, 120, 20, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('pac_003', 'Pacchetto Benessere', '5 trattamenti cheratina', 320.00, 5, 365, 20, '2025-01-01 00:00:00', '2025-01-01 00:00:00');

-- ───────────────────────────────────────────────────────────────────
-- PACCHETTO_SERVIZI (associazioni pacchetto-servizio)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita, created_at)
VALUES
  ('ps_001', 'pac_001', 'srv_001', 5, '2025-01-01 00:00:00'),
  ('ps_002', 'pac_002', 'srv_002', 3, '2025-01-01 00:00:00'),
  ('ps_003', 'pac_002', 'srv_003', 3, '2025-01-01 00:00:00'),
  ('ps_004', 'pac_003', 'srv_005', 5, '2025-01-01 00:00:00');

-- ───────────────────────────────────────────────────────────────────
-- CLIENTI_PACCHETTI (assegnazioni pacchetti a clienti)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, data_acquisto, data_scadenza, created_at, updated_at)
VALUES
  ('cp_001', 'cli_001', 'pac_001', 'in_uso', 3, '2025-11-01 10:00:00', '2026-04-30 23:59:59', '2025-11-01 10:00:00', '2026-01-05 10:00:00'),
  ('cp_002', 'cli_002', 'pac_002', 'in_uso', 1, '2025-12-15 14:00:00', '2026-04-15 23:59:59', '2025-12-15 14:00:00', '2026-01-05 10:00:00'),
  ('cp_003', 'cli_005', 'pac_003', 'venduto', 0, '2026-01-03 11:00:00', '2027-01-03 23:59:59', '2026-01-03 11:00:00', '2026-01-05 10:00:00');

-- ───────────────────────────────────────────────────────────────────
-- APPUNTAMENTI (20 appuntamenti mock - mix di stati)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO appuntamenti (id, cliente_id, servizio_id, operatore_id, data_ora_inizio, data_ora_fine, durata_minuti, stato, prezzo, prezzo_finale, note, fonte_prenotazione, created_at, updated_at)
VALUES
  -- Appuntamenti completati (passato)
  ('app_001', 'cli_001', 'srv_001', 'op_001', '2026-01-03T09:00:00', '2026-01-03T09:30:00', 30, 'completato', 18.00, 18.00, 'Taglio standard', 'manuale', '2026-01-02 10:00:00', '2026-01-03 09:30:00'),
  ('app_002', 'cli_002', 'srv_002', 'op_002', '2026-01-03T10:00:00', '2026-01-03T11:00:00', 60, 'completato', 35.00, 35.00, NULL, 'whatsapp', '2026-01-02 11:00:00', '2026-01-03 11:00:00'),
  ('app_003', 'cli_003', 'srv_001', 'op_003', '2026-01-04T14:00:00', '2026-01-04T14:30:00', 30, 'completato', 18.00, 18.00, NULL, 'manuale', '2026-01-03 09:00:00', '2026-01-04 14:30:00'),
  ('app_016', 'cli_005', 'srv_003', 'op_002', '2026-01-04T15:00:00', '2026-01-04T16:30:00', 90, 'completato', 55.00, 55.00, 'Colore biondo', 'manuale', '2026-01-03 10:00:00', '2026-01-04 16:30:00'),
  ('app_017', 'cli_007', 'srv_006', 'op_001', '2026-01-05T09:00:00', '2026-01-05T09:20:00', 20, 'completato', 12.00, 12.00, 'Barba curata', 'whatsapp', '2026-01-04 08:00:00', '2026-01-05 09:20:00'),

  -- Appuntamenti confermati (oggi 6 gennaio)
  ('app_004', 'cli_004', 'srv_003', 'op_004', '2026-01-06T09:30:00', '2026-01-06T11:00:00', 90, 'confermato', 55.00, 55.00, 'Prima volta colore', 'manuale', '2026-01-04 15:00:00', '2026-01-04 15:00:00'),
  ('app_005', 'cli_005', 'srv_005', 'op_002', '2026-01-06T11:00:00', '2026-01-06T13:00:00', 120, 'confermato', 80.00, 80.00, 'Trattamento premium VIP', 'manuale', '2026-01-04 16:00:00', '2026-01-04 16:00:00'),
  ('app_006', 'cli_006', 'srv_004', 'op_004', '2026-01-06T14:00:00', '2026-01-06T14:30:00', 30, 'confermato', 20.00, 20.00, NULL, 'whatsapp', '2026-01-05 09:00:00', '2026-01-05 09:00:00'),
  ('app_007', 'cli_007', 'srv_001', 'op_001', '2026-01-06T15:00:00', '2026-01-06T15:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'manuale', '2026-01-05 10:00:00', '2026-01-05 10:00:00'),
  ('app_018', 'cli_009', 'srv_002', 'op_003', '2026-01-06T16:00:00', '2026-01-06T17:00:00', 60, 'confermato', 35.00, 35.00, 'Cliente abituale', 'voice', '2026-01-05 11:00:00', '2026-01-05 11:00:00'),

  -- Appuntamenti domani (7 gennaio)
  ('app_008', 'cli_008', 'srv_002', 'op_003', '2026-01-07T10:00:00', '2026-01-07T11:00:00', 60, 'confermato', 35.00, 35.00, 'Nuovo cliente', 'online', '2026-01-05 11:00:00', '2026-01-05 11:00:00'),
  ('app_009', 'cli_009', 'srv_006', 'op_001', '2026-01-07T16:00:00', '2026-01-07T16:20:00', 20, 'confermato', 12.00, 12.00, NULL, 'manuale', '2026-01-05 12:00:00', '2026-01-05 12:00:00'),
  ('app_019', 'cli_010', 'srv_005', 'op_002', '2026-01-07T09:00:00', '2026-01-07T11:00:00', 120, 'confermato', 80.00, 72.00, 'Sconto VIP 10%', 'manuale', '2026-01-05 14:00:00', '2026-01-05 14:00:00'),

  -- Appuntamenti in attesa conferma
  ('app_010', 'cli_010', 'srv_008', 'op_004', '2026-01-08T09:00:00', '2026-01-08T09:45:00', 45, 'bozza', 25.00, 25.00, 'Consulenza completa', 'whatsapp', '2026-01-05 13:00:00', '2026-01-05 13:00:00'),
  ('app_020', 'cli_001', 'srv_007', 'op_003', '2026-01-08T14:00:00', '2026-01-08T14:15:00', 15, 'bozza', 8.00, 8.00, 'Solo shampoo', 'manuale', '2026-01-06 08:00:00', '2026-01-06 08:00:00'),

  -- Appuntamenti futuri
  ('app_011', 'cli_001', 'srv_001', 'op_001', '2026-01-10T09:00:00', '2026-01-10T09:30:00', 30, 'confermato', 18.00, 18.00, NULL, 'manuale', '2026-01-05 14:00:00', '2026-01-05 14:00:00'),
  ('app_012', 'cli_002', 'srv_003', 'op_002', '2026-01-12T11:00:00', '2026-01-12T12:30:00', 90, 'confermato', 55.00, 55.00, NULL, 'whatsapp', '2026-01-05 15:00:00', '2026-01-05 15:00:00'),
  ('app_013', 'cli_003', 'srv_007', 'op_003', '2026-01-15T14:30:00', '2026-01-15T14:45:00', 15, 'bozza', 8.00, 8.00, NULL, 'manuale', '2026-01-05 16:00:00', '2026-01-05 16:00:00'),

  -- Appuntamento cancellato
  ('app_014', 'cli_004', 'srv_002', 'op_004', '2026-01-05T10:00:00', '2026-01-05T11:00:00', 60, 'cancellato', 35.00, 35.00, 'Cliente ha disdetto', 'manuale', '2026-01-03 10:00:00', '2026-01-04 18:00:00'),

  -- Appuntamento no-show
  ('app_015', 'cli_006', 'srv_001', 'op_003', '2026-01-02T15:00:00', '2026-01-02T15:30:00', 30, 'no_show', 18.00, 18.00, 'Non si è presentato', 'manuale', '2026-01-01 10:00:00', '2026-01-02 15:30:00');

-- ───────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI FATTURAZIONE
-- ───────────────────────────────────────────────────────────────────

INSERT INTO impostazioni_fatturazione (
  id, denominazione, partita_iva, codice_fiscale,
  indirizzo, cap, citta, provincia, nazione,
  regime_fiscale, telefono, email, pec,
  iban, banca, intestatario_conto,
  created_at, updated_at
)
VALUES (
  'imp_001',
  'Salone Fluxion Demo',
  '02159940762',
  'DSTMGN81S12L738L',
  'Via Roma 123',
  '85100',
  'Potenza',
  'PZ',
  'IT',
  'RF19',
  '0971123456',
  'info@fluxion-demo.it',
  'fluxion@pec.it',
  'IT60X0542811101000000123456',
  'Banca Demo',
  'Salone Fluxion Demo',
  '2025-01-01 00:00:00',
  '2025-01-01 00:00:00'
);

-- ───────────────────────────────────────────────────────────────────
-- FATTURE (5 fatture mock)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO fatture (
  id, numero, anno, data_emissione, data_scadenza,
  cliente_id, tipo_documento, stato,
  totale_imponibile, totale_iva, totale_documento,
  bollo_virtuale, importo_bollo,
  note, xml_content, created_at, updated_at
)
VALUES
  ('fat_001', 1, 2026, '2026-01-03', '2026-02-03', 'cli_001', 'TD01', 'pagata', 53.00, 11.66, 64.66, 0, 0.00, 'Fattura gennaio', NULL, '2026-01-03 10:00:00', '2026-01-03 10:00:00'),
  ('fat_002', 2, 2026, '2026-01-04', '2026-02-04', 'cli_002', 'TD01', 'pagata', 90.00, 19.80, 109.80, 0, 0.00, NULL, NULL, '2026-01-04 11:00:00', '2026-01-04 11:00:00'),
  ('fat_003', 3, 2026, '2026-01-05', '2026-02-05', 'cli_003', 'TD01', 'emessa', 35.00, 7.70, 42.70, 0, 0.00, 'In attesa pagamento', NULL, '2026-01-05 09:00:00', '2026-01-05 09:00:00'),
  ('fat_004', 4, 2026, '2026-01-06', '2026-02-06', 'cli_005', 'TD01', 'emessa', 80.00, 17.60, 97.60, 1, 2.00, 'Trattamento premium', NULL, '2026-01-06 10:00:00', '2026-01-06 10:00:00'),
  ('fat_005', 5, 2026, '2026-01-06', '2026-02-06', 'cli_004', 'TD01', 'bozza', 55.00, 12.10, 67.10, 0, 0.00, 'Da completare', NULL, '2026-01-06 11:00:00', '2026-01-06 11:00:00');

-- ───────────────────────────────────────────────────────────────────
-- FATTURE_RIGHE (righe per ogni fattura)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO fatture_righe (
  id, fattura_id, numero_linea, descrizione,
  quantita, prezzo_unitario, aliquota_iva,
  natura_iva, totale_linea, created_at
)
VALUES
  -- Fattura 1: Taglio + Piega
  ('riga_001', 'fat_001', 1, 'Taglio Uomo', 1, 18.00, 22, NULL, 18.00, '2026-01-03 10:00:00'),
  ('riga_002', 'fat_001', 2, 'Taglio Donna', 1, 35.00, 22, NULL, 35.00, '2026-01-03 10:00:00'),
  -- Fattura 2: Colore + Piega
  ('riga_003', 'fat_002', 1, 'Colore', 1, 55.00, 22, NULL, 55.00, '2026-01-04 11:00:00'),
  ('riga_004', 'fat_002', 2, 'Taglio Donna', 1, 35.00, 22, NULL, 35.00, '2026-01-04 11:00:00'),
  -- Fattura 3: Solo taglio
  ('riga_005', 'fat_003', 1, 'Taglio Donna', 1, 35.00, 22, NULL, 35.00, '2026-01-05 09:00:00'),
  -- Fattura 4: Trattamento
  ('riga_006', 'fat_004', 1, 'Trattamento Cheratina', 1, 80.00, 22, NULL, 80.00, '2026-01-06 10:00:00'),
  -- Fattura 5: Colore (bozza)
  ('riga_007', 'fat_005', 1, 'Colore', 1, 55.00, 22, NULL, 55.00, '2026-01-06 11:00:00');

-- ───────────────────────────────────────────────────────────────────
-- FATTURE_PAGAMENTI (pagamenti per fatture pagate)
-- ───────────────────────────────────────────────────────────────────

INSERT INTO fatture_pagamenti (
  id, fattura_id, data_pagamento, importo,
  metodo_pagamento, note, created_at
)
VALUES
  ('pag_001', 'fat_001', '2026-01-03', 64.66, 'MP01', 'Pagato in contanti', '2026-01-03 10:30:00'),
  ('pag_002', 'fat_002', '2026-01-04', 109.80, 'MP08', 'Pagato con carta', '2026-01-04 11:30:00');

-- ───────────────────────────────────────────────────────────────────
-- AGGIORNA NUMERATORE FATTURE
-- ───────────────────────────────────────────────────────────────────

INSERT OR REPLACE INTO numeratore_fatture (anno, ultimo_numero)
VALUES (2026, 5);

-- ───────────────────────────────────────────────────────────────────
-- FINE MOCK DATA
-- ───────────────────────────────────────────────────────────────────

-- Verifica conteggi
SELECT 'Clienti' as tabella, COUNT(*) as totale FROM clienti
UNION ALL SELECT 'Servizi', COUNT(*) FROM servizi
UNION ALL SELECT 'Operatori', COUNT(*) FROM operatori
UNION ALL SELECT 'Pacchetti', COUNT(*) FROM pacchetti
UNION ALL SELECT 'Appuntamenti', COUNT(*) FROM appuntamenti
UNION ALL SELECT 'Fatture', COUNT(*) FROM fatture
UNION ALL SELECT 'Impostazioni', COUNT(*) FROM impostazioni_fatturazione;
