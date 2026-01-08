-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Mock Data per Test
-- ESEGUIRE DOPO che l'app ha creato le tabelle (npm run tauri dev)
-- sqlite3 ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db < scripts/mock_data.sql
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────
-- SETUP WIZARD (PERMANENTE - salta wizard all'avvio)
-- ───────────────────────────────────────────────────────────────────

-- Dati azienda
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
  ('setup_completed', 'true'),
  ('azienda_nome', 'Automation Business'),
  ('azienda_partita_iva', '02159940762'),
  ('azienda_codice_fiscale', 'DSTMGN81S12L738L'),
  ('azienda_indirizzo', 'Via Roma 1'),
  ('azienda_cap', '85100'),
  ('azienda_citta', 'Potenza'),
  ('azienda_provincia', 'PZ'),
  ('azienda_telefono', '3281536308'),
  ('azienda_email', 'test@fluxion.local'),
  ('regime_fiscale', 'RF19'),
  ('categoria_attivita', 'salone'),
  ('fluxion_ia_key', 'gsk_your_groq_api_key_here');

-- ───────────────────────────────────────────────────────────────────
-- FAQ SETTINGS (Variabili per RAG locale)
-- ───────────────────────────────────────────────────────────────────

INSERT OR REPLACE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
  -- Orari
  ('giorni_apertura', 'Lunedì - Sabato', 'orari', 'Giorni di apertura'),
  ('orario_mattina', '09:00 - 13:00', 'orari', 'Orario mattina'),
  ('orario_pomeriggio', '15:00 - 19:30', 'orari', 'Orario pomeriggio'),
  ('giorni_chiusura', 'Domenica', 'orari', 'Giorni di chiusura'),
  ('tempo_ultimo_appuntamento', '30', 'orari', 'Minuti prima chiusura'),
  -- Prenotazioni
  ('metodo_prenotazione_principale', 'Telefono o WhatsApp', 'prenotazioni', 'Come prenotare'),
  ('metodo_urgenze', 'Chiama direttamente', 'prenotazioni', 'Per urgenze'),
  ('canale_info', 'WhatsApp', 'prenotazioni', 'Canale info'),
  ('giorni_anticipo', '3-7', 'prenotazioni', 'Anticipo consigliato'),
  ('quando_last_minute', 'chiamando la mattina stessa', 'prenotazioni', 'Last minute'),
  ('ore_disdetta', '24', 'prenotazioni', 'Ore disdetta gratuita'),
  ('numero_noshow', '2', 'prenotazioni', 'No-show tollerati'),
  ('percentuale_anticipo', '50', 'prenotazioni', 'Percentuale anticipo'),
  ('metodo_conferma', 'WhatsApp', 'prenotazioni', 'Metodo conferma'),
  ('tempo_conferma', '24 ore', 'prenotazioni', 'Tempo conferma'),
  ('contatto_modifiche', 'WhatsApp o telefono', 'prenotazioni', 'Per modifiche'),
  ('ore_modifica', '12', 'prenotazioni', 'Ore modifica gratuita'),
  ('minuti_tolleranza', '10', 'prenotazioni', 'Tolleranza ritardo'),
  -- Servizi (durate)
  ('durata_taglio_uomo', '30 min', 'servizi', 'Durata taglio uomo'),
  ('durata_taglio_donna', '60 min', 'servizi', 'Durata taglio donna'),
  ('durata_piega', '30 min', 'servizi', 'Durata piega'),
  ('durata_colore', '90 min', 'servizi', 'Durata colore'),
  ('durata_cheratina', '120 min', 'servizi', 'Durata cheratina'),
  ('durata_barba', '20 min', 'servizi', 'Durata barba'),
  ('durata_meches', '90 min', 'servizi', 'Durata meches'),
  ('durata_balayage', '120 min', 'servizi', 'Durata balayage'),
  ('durata_permanente', '120 min', 'servizi', 'Durata permanente'),
  ('durata_trattamento', '45 min', 'servizi', 'Durata trattamento'),
  ('durata_styling', '60 min', 'servizi', 'Durata styling eventi'),
  -- Pagamenti
  ('metodi_pagamento', 'Contanti, Carta, Satispay, Bonifico', 'pagamenti', 'Metodi accettati'),
  ('sconto_pacchetti', '15', 'pagamenti', 'Sconto pacchetti prepagati'),
  ('disponibilita_carte_regalo', 'Sì, da €25 a €200', 'pagamenti', 'Carte regalo'),
  ('modalita_fattura', 'Su richiesta', 'pagamenti', 'Modalità fattura'),
  -- Contatti
  ('numero_telefono', '328 153 6308', 'contatti', 'Telefono'),
  ('numero_whatsapp', '328 153 6308', 'contatti', 'WhatsApp'),
  ('indirizzo_salone', 'Via Roma 1, 85100 Potenza (PZ)', 'contatti', 'Indirizzo'),
  ('email_salone', 'test@fluxion.local', 'contatti', 'Email'),
  ('link_social', '@automationbusiness', 'contatti', 'Social media'),
  -- Consulenza
  ('costo_consulenza', 'gratuita', 'consulenza', 'Costo consulenza'),
  -- Parcheggio
  ('info_parcheggio', 'Parcheggio gratuito davanti al salone', 'logistica', 'Info parcheggio'),
  ('info_parcheggio_alternativo', 'Parcheggio comunale a 50m', 'logistica', 'Alternativa'),
  ('accesso_disabili', 'Sì, ingresso accessibile', 'logistica', 'Accesso disabili'),
  -- Prodotti
  ('disponibilita_prodotti', 'Sì, linea professionale', 'prodotti', 'Prodotti vendita'),
  ('sconto_prodotti', '10', 'prodotti', 'Sconto clienti'),
  ('marchi_prodotti', 'Kérastase, Olaplex, Wella', 'prodotti', 'Marchi'),
  -- Manutenzione
  ('frequenza_taglio_uomo', '3-4 settimane', 'manutenzione', 'Frequenza taglio uomo'),
  ('frequenza_taglio_donna', '6-8 settimane', 'manutenzione', 'Frequenza taglio donna'),
  ('frequenza_ritocco_colore', '3-4 settimane', 'manutenzione', 'Frequenza ritocco'),
  ('frequenza_colore_completo', '6-8 settimane', 'manutenzione', 'Frequenza colore completo'),
  ('durata_piega_liscia', '2-3', 'manutenzione', 'Giorni piega liscia'),
  ('durata_piega_mossa', '1-2', 'manutenzione', 'Giorni piega mossa'),
  ('durata_risultati_cheratina', '3-5', 'manutenzione', 'Mesi cheratina'),
  ('ore_post_cheratina', '72', 'manutenzione', 'Ore no lavaggio cheratina'),
  ('frequenza_balayage', '3-4 mesi', 'manutenzione', 'Frequenza balayage'),
  -- Cura post
  ('ore_post_colore', '48', 'cura', 'Ore no lavaggio colore'),
  ('giorni_post_cheratina', '3', 'cura', 'Giorni no legare capelli'),
  ('tipo_prodotti_cheratina', 'senza solfati', 'cura', 'Prodotti post cheratina'),
  ('settimane_post_cheratina', '2', 'cura', 'Settimane no cloro/mare'),
  ('frequenza_lavaggio_consigliata', '2-3 volte a settimana', 'cura', 'Frequenza lavaggio'),
  ('temperatura_styling', '180', 'cura', 'Temperatura max styling'),
  ('frequenza_maschere', '1 volta a settimana', 'cura', 'Frequenza maschere'),
  -- FAQ comuni
  ('lavaggio_pre_appuntamento', 'Non necessario, laviamo noi i capelli', 'faq', 'Lavaggio prima'),
  ('politica_bambini', 'Sì, benvenuti con supervisione genitori', 'faq', 'Bambini'),
  ('minuti_anticipo_arrivo', '5-10', 'faq', 'Anticipo arrivo'),
  ('giorni_tra_trattamenti', '15', 'faq', 'Giorni tra trattamenti'),
  ('numero_sedute_schiaritura', '2-3', 'faq', 'Sedute schiaritura'),
  ('frequenza_trattamento_riparazione', '2-3 settimane', 'faq', 'Frequenza riparazione'),
  ('disponibilita_test_allergia', 'su richiesta', 'faq', 'Test allergia'),
  ('ore_test_allergia', '48', 'faq', 'Ore prima test'),
  ('quando_obbligatorio_test', 'colorazioni permanenti', 'faq', 'Quando obbligatorio'),
  ('a_chi_comunicare', 'al tuo parrucchiere', 'faq', 'A chi comunicare'),
  ('politica_soddisfazione', 'Garantiamo soddisfazione o ritocco gratuito', 'faq', 'Soddisfazione'),
  ('giorni_ritocco_gratuito', '7', 'faq', 'Giorni ritocco'),
  ('contatto_reclami', 'il titolare', 'faq', 'Contatto reclami'),
  ('lavaggio_incluso', 'Lavaggio sempre incluso nel servizio', 'faq', 'Lavaggio incluso'),
  -- Politiche
  ('politica_asciugamani', 'Asciugamani monouso', 'politiche', 'Asciugamani'),
  ('frequenza_sanificazione', 'dopo ogni cliente', 'politiche', 'Sanificazione'),
  ('disponibilita_wifi', 'Sì, password disponibile', 'politiche', 'WiFi'),
  ('disponibilita_bevande', 'Caffè, tè, acqua', 'politiche', 'Bevande'),
  ('descrizione_area_attesa', 'Comoda area relax', 'politiche', 'Area attesa'),
  ('disponibilita_intrattenimento', 'Riviste, TV', 'politiche', 'Intrattenimento'),
  -- Promozioni
  ('come_iscriversi_newsletter', 'Chiedi alla reception', 'promozioni', 'Newsletter'),
  ('info_promozioni', 'Seguici sui social', 'promozioni', 'Info promozioni'),
  ('info_referral', 'Porta un amico, 10% sconto per entrambi', 'promozioni', 'Referral');

-- Pulisci dati esistenti (in ordine inverso per foreign keys)
DELETE FROM fatture_righe WHERE id LIKE 'riga_%';
DELETE FROM fatture WHERE id LIKE 'fat_%';
DELETE FROM appuntamenti WHERE id LIKE 'app_%';
DELETE FROM clienti_pacchetti WHERE id LIKE 'cp_%';
DELETE FROM pacchetto_servizi WHERE id LIKE 'ps_%';
DELETE FROM pacchetti WHERE id LIKE 'pac_%';
DELETE FROM waitlist WHERE id LIKE 'wl_%';
DELETE FROM operatori_servizi WHERE operatore_id LIKE 'op_%';
DELETE FROM servizi WHERE id LIKE 'srv_%';
DELETE FROM operatori WHERE id LIKE 'op_%';
DELETE FROM clienti WHERE id LIKE 'cli_%';

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
  ('op_001', 'srv_001'), ('op_001', 'srv_006'),
  ('op_002', 'srv_002'), ('op_002', 'srv_003'), ('op_002', 'srv_004'), ('op_002', 'srv_005'),
  ('op_003', 'srv_001'), ('op_003', 'srv_002'), ('op_003', 'srv_004'),
  ('op_004', 'srv_003'), ('op_004', 'srv_005'), ('op_004', 'srv_008');

-- ───────────────────────────────────────────────────────────────────
-- PACCHETTI (3 pacchetti mock)
-- Schema: id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo, created_at, updated_at
-- ───────────────────────────────────────────────────────────────────

INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo, created_at, updated_at)
VALUES
  ('pac_001', 'Pacchetto Uomo 5x', '5 tagli uomo a prezzo scontato', 75.00, 90.00, 5, 'srv_001', 180, 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('pac_002', 'Pacchetto Donna Premium', '3 taglio + colore', 200.00, 250.00, 3, NULL, 120, 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00'),
  ('pac_003', 'Pacchetto Benessere', '5 trattamenti cheratina', 320.00, 400.00, 5, 'srv_005', 365, 1, '2025-01-01 00:00:00', '2025-01-01 00:00:00');

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
-- CLIENTI_PACCHETTI
-- Schema: id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato, note, created_at, updated_at
-- ───────────────────────────────────────────────────────────────────

INSERT INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato, note, created_at, updated_at)
VALUES
  ('cp_001', 'cli_001', 'pac_001', 'in_uso', 3, 5, '2025-10-15 10:00:00', '2025-11-01 10:00:00', '2026-04-30 23:59:59', 'contanti', 1, NULL, '2025-11-01 10:00:00', '2026-01-05 10:00:00'),
  ('cp_002', 'cli_002', 'pac_002', 'in_uso', 1, 3, '2025-12-10 14:00:00', '2025-12-15 14:00:00', '2026-04-15 23:59:59', 'carta', 1, NULL, '2025-12-15 14:00:00', '2026-01-05 10:00:00'),
  ('cp_003', 'cli_005', 'pac_003', 'venduto', 0, 5, '2026-01-02 11:00:00', '2026-01-03 11:00:00', '2027-01-03 23:59:59', 'bonifico', 1, 'Cliente VIP', '2026-01-03 11:00:00', '2026-01-05 10:00:00');

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
-- FATTURE (5 fatture mock) - Schema MIGRATION 007
-- ───────────────────────────────────────────────────────────────────

-- Aggiorna numeratore fatture
UPDATE numeratore_fatture SET ultimo_numero = 5 WHERE anno = 2026;

INSERT INTO fatture (
  id, numero, anno, numero_completo, tipo_documento,
  data_emissione, data_scadenza,
  cliente_id, cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale,
  cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_nazione, cliente_codice_sdi,
  imponibile_totale, iva_totale, totale_documento,
  modalita_pagamento, condizioni_pagamento,
  stato, created_at, updated_at
)
VALUES
  -- Fattura 1: Pagata (Mario Rossi)
  ('fat_001', 1, 2026, '1/2026', 'TD01',
   '2026-01-03', '2026-02-03',
   'cli_001', 'Mario Rossi', NULL, NULL,
   'Via Roma 10', '85100', 'Potenza', 'PZ', 'IT', '0000000',
   53.00, 0.00, 53.00,
   'MP01', 'TP02',
   'pagata', '2026-01-03 10:00:00', '2026-01-03 10:00:00'),

  -- Fattura 2: Pagata (Giulia Bianchi)
  ('fat_002', 2, 2026, '2/2026', 'TD01',
   '2026-01-04', '2026-02-04',
   'cli_002', 'Giulia Bianchi', NULL, NULL,
   'Via Napoli 20', '85100', 'Potenza', 'PZ', 'IT', '0000000',
   90.00, 0.00, 90.00,
   'MP08', 'TP02',
   'pagata', '2026-01-04 11:00:00', '2026-01-04 11:00:00'),

  -- Fattura 3: Emessa (Luca Verdi)
  ('fat_003', 3, 2026, '3/2026', 'TD01',
   '2026-01-05', '2026-02-05',
   'cli_003', 'Luca Verdi', NULL, NULL,
   'Via Milano 30', '85100', 'Potenza', 'PZ', 'IT', '0000000',
   35.00, 0.00, 35.00,
   'MP05', 'TP02',
   'emessa', '2026-01-05 09:00:00', '2026-01-05 09:00:00'),

  -- Fattura 4: Emessa (Paolo Romano - VIP)
  ('fat_004', 4, 2026, '4/2026', 'TD01',
   '2026-01-06', '2026-02-06',
   'cli_005', 'Paolo Romano', NULL, NULL,
   'Via Torino 50', '85100', 'Potenza', 'PZ', 'IT', '0000000',
   80.00, 0.00, 80.00,
   'MP05', 'TP02',
   'emessa', '2026-01-06 10:00:00', '2026-01-06 10:00:00'),

  -- Fattura 5: Bozza (Anna Ferrari)
  ('fat_005', 5, 2026, '5/2026', 'TD01',
   '2026-01-06', '2026-02-06',
   'cli_004', 'Anna Ferrari', NULL, NULL,
   'Via Bari 40', '85100', 'Potenza', 'PZ', 'IT', '0000000',
   55.00, 0.00, 55.00,
   'MP01', 'TP02',
   'bozza', '2026-01-06 11:00:00', '2026-01-06 11:00:00');

-- ───────────────────────────────────────────────────────────────────
-- FATTURE_RIGHE - Schema MIGRATION 007
-- ───────────────────────────────────────────────────────────────────

INSERT INTO fatture_righe (
  id, fattura_id, numero_linea, descrizione,
  quantita, unita_misura, prezzo_unitario,
  sconto_percentuale, sconto_importo, prezzo_totale,
  aliquota_iva, natura
)
VALUES
  -- Fattura 1: Taglio Uomo + Taglio Donna
  ('riga_001', 'fat_001', 1, 'Taglio Uomo', 1, 'PZ', 18.00, 0, 0, 18.00, 0.00, 'N2.2'),
  ('riga_002', 'fat_001', 2, 'Taglio Donna', 1, 'PZ', 35.00, 0, 0, 35.00, 0.00, 'N2.2'),
  -- Fattura 2: Colore + Taglio Donna
  ('riga_003', 'fat_002', 1, 'Colore', 1, 'PZ', 55.00, 0, 0, 55.00, 0.00, 'N2.2'),
  ('riga_004', 'fat_002', 2, 'Taglio Donna', 1, 'PZ', 35.00, 0, 0, 35.00, 0.00, 'N2.2'),
  -- Fattura 3: Solo taglio
  ('riga_005', 'fat_003', 1, 'Taglio Donna', 1, 'PZ', 35.00, 0, 0, 35.00, 0.00, 'N2.2'),
  -- Fattura 4: Trattamento
  ('riga_006', 'fat_004', 1, 'Trattamento Cheratina', 1, 'PZ', 80.00, 0, 0, 80.00, 0.00, 'N2.2'),
  -- Fattura 5: Colore (bozza)
  ('riga_007', 'fat_005', 1, 'Colore', 1, 'PZ', 55.00, 0, 0, 55.00, 0.00, 'N2.2');

-- ───────────────────────────────────────────────────────────────────
-- METODI_PAGAMENTO (seed iniziale)
-- ───────────────────────────────────────────────────────────────────

INSERT OR IGNORE INTO metodi_pagamento (codice, nome, icona, attivo, ordine)
VALUES
  ('contanti', 'Contanti', '💵', 1, 1),
  ('carta', 'Carta di Credito/Debito', '💳', 1, 2),
  ('satispay', 'Satispay', '📱', 1, 3),
  ('bonifico', 'Bonifico Bancario', '🏦', 1, 4),
  ('assegno', 'Assegno', '📝', 0, 5);

-- ───────────────────────────────────────────────────────────────────
-- INCASSI (15 incassi mock - ultimi giorni)
-- ───────────────────────────────────────────────────────────────────

DELETE FROM incassi WHERE id LIKE 'inc_%';

INSERT INTO incassi (id, importo, metodo_pagamento, cliente_id, appuntamento_id, fattura_id, descrizione, categoria, operatore_id, data_incasso, created_at)
VALUES
  -- Incassi 3 gennaio (giornata chiusa)
  ('inc_001', 18.00, 'contanti', 'cli_001', 'app_001', NULL, 'Taglio uomo', 'servizio', 'op_001', '2026-01-03 09:35:00', '2026-01-03 09:35:00'),
  ('inc_002', 35.00, 'carta', 'cli_002', 'app_002', NULL, 'Taglio donna', 'servizio', 'op_002', '2026-01-03 11:05:00', '2026-01-03 11:05:00'),

  -- Incassi 4 gennaio (giornata chiusa)
  ('inc_003', 18.00, 'contanti', 'cli_003', 'app_003', NULL, 'Taglio uomo', 'servizio', 'op_003', '2026-01-04 14:35:00', '2026-01-04 14:35:00'),
  ('inc_004', 55.00, 'carta', 'cli_005', 'app_016', NULL, 'Colore completo', 'servizio', 'op_002', '2026-01-04 16:35:00', '2026-01-04 16:35:00'),
  ('inc_005', 200.00, 'bonifico', 'cli_005', NULL, NULL, 'Pacchetto Donna Premium', 'pacchetto', 'op_001', '2026-01-04 17:00:00', '2026-01-04 17:00:00'),

  -- Incassi 5 gennaio (giornata chiusa)
  ('inc_006', 12.00, 'contanti', 'cli_007', 'app_017', NULL, 'Barba', 'servizio', 'op_001', '2026-01-05 09:25:00', '2026-01-05 09:25:00'),
  ('inc_007', 35.00, 'satispay', 'cli_008', NULL, NULL, 'Taglio donna walk-in', 'servizio', 'op_003', '2026-01-05 11:00:00', '2026-01-05 11:00:00'),
  ('inc_008', 8.00, 'contanti', 'cli_006', NULL, NULL, 'Shampoo massaggio', 'servizio', 'op_002', '2026-01-05 15:00:00', '2026-01-05 15:00:00'),

  -- Incassi 6 gennaio (oggi - NON chiusa)
  ('inc_009', 55.00, 'carta', 'cli_004', 'app_004', NULL, 'Colore prima volta', 'servizio', 'op_004', '2026-01-06 11:05:00', '2026-01-06 11:05:00'),
  ('inc_010', 80.00, 'carta', 'cli_005', 'app_005', NULL, 'Trattamento cheratina VIP', 'servizio', 'op_002', '2026-01-06 13:05:00', '2026-01-06 13:05:00'),
  ('inc_011', 20.00, 'satispay', 'cli_006', 'app_006', NULL, 'Piega', 'servizio', 'op_004', '2026-01-06 14:35:00', '2026-01-06 14:35:00'),
  ('inc_012', 18.00, 'contanti', 'cli_007', 'app_007', NULL, 'Taglio uomo', 'servizio', 'op_001', '2026-01-06 15:35:00', '2026-01-06 15:35:00'),

  -- Incassi 7 gennaio (oggi - data sistema)
  ('inc_013', 80.00, 'carta', 'cli_010', 'app_019', NULL, 'Trattamento cheratina sconto VIP', 'servizio', 'op_002', '2026-01-07 11:05:00', '2026-01-07 11:05:00'),
  ('inc_014', 35.00, 'contanti', 'cli_008', 'app_008', NULL, 'Taglio donna', 'servizio', 'op_003', '2026-01-07 11:10:00', '2026-01-07 11:10:00'),
  ('inc_015', 25.00, 'satispay', NULL, NULL, NULL, 'Prodotto vendita (shampoo)', 'prodotto', 'op_005', '2026-01-07 12:00:00', '2026-01-07 12:00:00');

-- ───────────────────────────────────────────────────────────────────
-- CHIUSURE_CASSA (3 chiusure - giorni passati)
-- ───────────────────────────────────────────────────────────────────

DELETE FROM chiusure_cassa WHERE id LIKE 'cc_%';

INSERT INTO chiusure_cassa (id, data_chiusura, totale_contanti, totale_carte, totale_satispay, totale_bonifici, totale_altro, totale_giornata, numero_transazioni, fondo_cassa_iniziale, fondo_cassa_finale, note, operatore_id, created_at)
VALUES
  ('cc_001', '2026-01-03', 18.00, 35.00, 0.00, 0.00, 0.00, 53.00, 2, 100.00, 118.00, 'Prima giornata test', 'op_001', '2026-01-03 19:00:00'),
  ('cc_002', '2026-01-04', 18.00, 55.00, 0.00, 200.00, 0.00, 273.00, 3, 100.00, 118.00, 'Venduto pacchetto premium', 'op_001', '2026-01-04 19:30:00'),
  ('cc_003', '2026-01-05', 20.00, 0.00, 35.00, 0.00, 0.00, 55.00, 3, 100.00, 120.00, NULL, 'op_001', '2026-01-05 18:45:00');

-- ───────────────────────────────────────────────────────────────────
-- FINE MOCK DATA
-- ───────────────────────────────────────────────────────────────────

-- Verifica conteggi
SELECT 'Clienti' as tabella, COUNT(*) as totale FROM clienti WHERE id LIKE 'cli_%'
UNION ALL SELECT 'Servizi', COUNT(*) FROM servizi WHERE id LIKE 'srv_%'
UNION ALL SELECT 'Operatori', COUNT(*) FROM operatori WHERE id LIKE 'op_%'
UNION ALL SELECT 'Pacchetti', COUNT(*) FROM pacchetti WHERE id LIKE 'pac_%'
UNION ALL SELECT 'ClientiPacchetti', COUNT(*) FROM clienti_pacchetti WHERE id LIKE 'cp_%'
UNION ALL SELECT 'Appuntamenti', COUNT(*) FROM appuntamenti WHERE id LIKE 'app_%'
UNION ALL SELECT 'Fatture', COUNT(*) FROM fatture WHERE id LIKE 'fat_%'
UNION ALL SELECT 'FattureRighe', COUNT(*) FROM fatture_righe WHERE id LIKE 'riga_%'
UNION ALL SELECT 'Incassi', COUNT(*) FROM incassi WHERE id LIKE 'inc_%'
UNION ALL SELECT 'ChiusureCassa', COUNT(*) FROM chiusure_cassa WHERE id LIKE 'cc_%'
UNION ALL SELECT 'MetodiPagamento', COUNT(*) FROM metodi_pagamento;
