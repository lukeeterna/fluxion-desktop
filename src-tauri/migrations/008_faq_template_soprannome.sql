-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 008: FAQ Template System + Soprannome Cliente
-- ═══════════════════════════════════════════════════════════════

-- Aggiunge campo soprannome per identificazione cliente WhatsApp
ALTER TABLE clienti ADD COLUMN soprannome TEXT;

-- Indice per ricerca per soprannome
CREATE INDEX IF NOT EXISTS idx_clienti_soprannome ON clienti(soprannome);

-- ─────────────────────────────────────────────────────────────────
-- FAQ_SETTINGS: Variabili per template FAQ
-- Chiave-valore per popolare {{variabile}} nei file FAQ
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faq_settings (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    categoria TEXT DEFAULT 'generale',  -- orari, prenotazioni, pagamenti, etc.
    descrizione TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────────
-- VALORI DEFAULT FAQ (Salone tipo)
-- ─────────────────────────────────────────────────────────────────

-- Orari
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('giorni_apertura', 'Martedì - Sabato', 'orari', 'Giorni di apertura'),
('orario_mattina', '9:00', 'orari', 'Orario apertura mattina'),
('orario_pomeriggio', '19:00', 'orari', 'Orario chiusura'),
('giorni_chiusura', 'Domenica e Lunedì', 'orari', 'Giorni di chiusura'),
('tempo_ultimo_appuntamento', '30', 'orari', 'Minuti prima della chiusura per ultimo appuntamento');

-- Prenotazioni
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('metodo_prenotazione_principale', 'Chiamata o WhatsApp', 'prenotazioni', 'Come prenotare'),
('metodo_urgenze', 'chiamaci direttamente', 'prenotazioni', 'Per urgenze'),
('canale_info', 'Instagram', 'prenotazioni', 'Canale solo info'),
('giorni_anticipo', '3-5', 'prenotazioni', 'Anticipo consigliato prenotazione'),
('quando_last_minute', 'il giorno stesso dalle 9:00', 'prenotazioni', 'Quando last minute'),
('ore_disdetta', '24', 'prenotazioni', 'Ore anticipo per disdetta gratuita'),
('numero_noshow', '2', 'prenotazioni', 'Numero no-show prima di richiedere anticipo'),
('percentuale_anticipo', '50', 'prenotazioni', 'Percentuale anticipo richiesto'),
('metodo_conferma', 'WhatsApp', 'prenotazioni', 'Come confermiamo appuntamento'),
('tempo_conferma', '24 ore', 'prenotazioni', 'Quando confermiamo'),
('contatto_modifiche', 'WhatsApp o telefono', 'prenotazioni', 'Come modificare appuntamento'),
('ore_modifica', '24', 'prenotazioni', 'Ore anticipo per modifica gratuita'),
('minuti_tolleranza', '10', 'prenotazioni', 'Minuti tolleranza ritardo');

-- Pagamenti
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('metodi_pagamento', 'Contanti, Carte, Satispay', 'pagamenti', 'Metodi di pagamento accettati'),
('sconto_pacchetti', '10', 'pagamenti', 'Sconto pacchetti prepagati'),
('disponibilita_carte_regalo', 'Sì, disponibili', 'pagamenti', 'Carte regalo'),
('modalita_fattura', 'su richiesta', 'pagamenti', 'Come richiedere fattura');

-- Consulenza
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('costo_consulenza', 'gratuita', 'consulenza', 'Costo consulenza');

-- Parcheggio
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('info_parcheggio', 'Parcheggio gratuito davanti al salone', 'logistica', 'Info parcheggio'),
('info_parcheggio_alternativo', 'Strisce blu a 50m', 'logistica', 'Parcheggio alternativo'),
('accesso_disabili', 'Sì, ingresso senza barriere', 'logistica', 'Accessibilità');

-- Prodotti
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('disponibilita_prodotti', 'Sì, disponibili in salone', 'prodotti', 'Vendita prodotti'),
('sconto_prodotti', '15', 'prodotti', 'Sconto prodotti clienti abituali'),
('marchi_prodotti', 'L''Oréal, Wella, Kérastase', 'prodotti', 'Marchi disponibili');

-- Durate servizi (in minuti)
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('durata_taglio_uomo', '30 min', 'servizi', 'Durata taglio uomo'),
('durata_taglio_donna', '45-60 min', 'servizi', 'Durata taglio donna'),
('durata_piega', '30-45 min', 'servizi', 'Durata piega'),
('durata_colore', '90-120 min', 'servizi', 'Durata colore'),
('durata_cheratina', '120-180 min', 'servizi', 'Durata trattamento cheratina'),
('durata_barba', '20 min', 'servizi', 'Durata barba'),
('durata_meches', '120-150 min', 'servizi', 'Durata meches'),
('durata_balayage', '150-180 min', 'servizi', 'Durata balayage'),
('durata_permanente', '90-120 min', 'servizi', 'Durata permanente'),
('durata_trattamento', '45-60 min', 'servizi', 'Durata trattamento ristrutturante'),
('durata_styling', '60-90 min', 'servizi', 'Durata styling eventi');

-- Frequenze consigliate
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('frequenza_taglio_uomo', '3-4 settimane', 'frequenze', 'Frequenza taglio uomo'),
('frequenza_taglio_donna', '6-8 settimane', 'frequenze', 'Frequenza taglio donna'),
('frequenza_ritocco_colore', '4-6 settimane', 'frequenze', 'Frequenza ritocco colore'),
('frequenza_colore_completo', '8-12 settimane', 'frequenze', 'Frequenza colore completo'),
('frequenza_balayage', '3-4 mesi', 'frequenze', 'Frequenza manutenzione balayage');

-- Post-trattamento
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('durata_piega_liscia', '2-3', 'post_trattamento', 'Durata piega liscia in giorni'),
('durata_piega_mossa', '1-2', 'post_trattamento', 'Durata piega mossa in giorni'),
('durata_risultati_cheratina', '3-4', 'post_trattamento', 'Durata risultati cheratina in mesi'),
('ore_post_cheratina', '72', 'post_trattamento', 'Ore senza lavare dopo cheratina'),
('giorni_post_cheratina', '3', 'post_trattamento', 'Giorni senza legare capelli'),
('tipo_prodotti_cheratina', 'senza solfati', 'post_trattamento', 'Tipo prodotti per cheratina'),
('settimane_post_cheratina', '2', 'post_trattamento', 'Settimane evitare cloro/mare'),
('ore_post_colore', '48', 'post_trattamento', 'Ore senza lavare dopo colore');

-- Cura capelli
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('frequenza_lavaggio_consigliata', '2-3 volte a settimana', 'cura', 'Frequenza lavaggio'),
('temperatura_styling', '180', 'cura', 'Temperatura max styling'),
('frequenza_maschere', '1 volta a settimana', 'cura', 'Frequenza maschere nutrienti');

-- FAQ varie
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('lavaggio_pre_appuntamento', 'Non necessario, laviamo noi in salone', 'faq', 'Lavaggio prima appuntamento'),
('politica_bambini', 'Sì, benvenuti! Abbiamo area giochi', 'faq', 'Politica bambini'),
('minuti_anticipo_arrivo', '5-10', 'faq', 'Minuti anticipo consigliato'),
('giorni_tra_trattamenti', '15-20', 'faq', 'Giorni tra trattamenti aggressivi'),
('numero_sedute_schiaritura', '2-3', 'faq', 'Sedute per schiaritura'),
('frequenza_trattamento_riparazione', '2-3 settimane', 'faq', 'Frequenza trattamento riparazione'),
('disponibilita_test_allergia', 'su richiesta', 'faq', 'Test allergia'),
('ore_test_allergia', '48', 'faq', 'Ore anticipo test allergia'),
('quando_obbligatorio_test', 'colorazioni e trattamenti chimici', 'faq', 'Quando obbligatorio test'),
('a_chi_comunicare', 'al tuo stilista', 'faq', 'A chi comunicare cambi'),
('politica_soddisfazione', 'La tua soddisfazione è la nostra priorità', 'faq', 'Politica soddisfazione'),
('giorni_ritocco_gratuito', '7', 'faq', 'Giorni per ritocco gratuito'),
('contatto_reclami', 'il responsabile del salone', 'faq', 'Contatto reclami'),
('lavaggio_incluso', 'Lavaggio incluso in tutti i servizi', 'faq', 'Lavaggio incluso');

-- Igiene e politiche
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('politica_asciugamani', 'Asciugamani monouso', 'igiene', 'Politica asciugamani'),
('frequenza_sanificazione', 'ogni 2 ore', 'igiene', 'Frequenza sanificazione');

-- Servizi extra
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('disponibilita_wifi', 'Sì', 'extra', 'WiFi gratuito'),
('disponibilita_bevande', 'Caffè, tè, acqua offerti', 'extra', 'Bevande'),
('descrizione_area_attesa', 'Comoda area con divani', 'extra', 'Area attesa'),
('disponibilita_intrattenimento', 'Riviste e TV', 'extra', 'Intrattenimento');

-- Contatti (da sovrascrivere con dati reali)
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('numero_telefono', '{{DA_CONFIGURARE}}', 'contatti', 'Telefono salone'),
('numero_whatsapp', '{{DA_CONFIGURARE}}', 'contatti', 'WhatsApp salone'),
('indirizzo_salone', '{{DA_CONFIGURARE}}', 'contatti', 'Indirizzo'),
('email_salone', '{{DA_CONFIGURARE}}', 'contatti', 'Email'),
('link_social', '{{DA_CONFIGURARE}}', 'contatti', 'Link social');

-- Promozioni
INSERT OR IGNORE INTO faq_settings (chiave, valore, categoria, descrizione) VALUES
('come_iscriversi_newsletter', 'Lascia la tua email in salone', 'promozioni', 'Iscrizione newsletter'),
('info_promozioni', 'Seguici su Instagram per le promo', 'promozioni', 'Info promozioni'),
('info_referral', 'Porta un amico, ottieni 10% di sconto', 'promozioni', 'Programma referral');
