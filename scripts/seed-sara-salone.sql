-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Sara Test: SALONE PARRUCCHIERE (full restore)
-- Ripristina il verticale salone dopo test altre verticali
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- ── IMPOSTAZIONI (verticale) ──────────────────────────────────────
INSERT OR REPLACE INTO impostazioni (chiave, valore) VALUES
('nome_attivita', 'Salone Demo FLUXION'),
('categoria_attivita', 'salone'),
('macro_categoria', 'hair'),
('micro_categoria', 'salone_parrucchiere'),
('indirizzo_completo', 'Via Roma 42, 20121 Milano'),
('orario_apertura', '09:00'),
('orario_chiusura', '19:00'),
('giorni_lavorativi', '["lun","mar","mer","gio","ven","sab"]');

-- ── SERVIZI ───────────────────────────────────────────────────────
DELETE FROM servizi;
INSERT INTO servizi (id, nome, descrizione, prezzo, durata_minuti, buffer_minuti, categoria, colore, attivo, ordine) VALUES
('srv-taglio-donna', 'Taglio Donna',          'Taglio, shampoo e asciugatura',        35.00,  45, 5, 'taglio',       '#ec4899', 1, 1),
('srv-taglio-uomo',  'Taglio Uomo',           'Taglio classico maschile',             18.00,  30, 5, 'taglio',       '#3b82f6', 1, 2),
('srv-taglio-bimbo', 'Taglio Bambino',        'Taglio bambino sotto 12 anni',         12.00,  20, 5, 'taglio',       '#ec4899', 1, 3),
('srv-piega',        'Piega',                 'Messa in piega professionale',          20.00,  30, 5, 'styling',      '#8b5cf6', 1, 4),
('srv-colore',       'Colore',                'Colorazione completa',                  55.00,  90, 5, 'colore',       '#f59e0b', 1, 5),
('srv-meches',       'Meches',                'Meches o colpi di sole',                65.00, 120, 5, 'colore',       '#f59e0b', 1, 6),
('srv-balayage',     'Balayage',              'Tecnica schiarente naturale',           85.00, 120, 5, 'colore',       '#f59e0b', 1, 7),
('srv-trattamento',  'Trattamento Cheratina', 'Trattamento lisciante ristrutturante', 80.00, 120, 5, 'trattamenti',  '#10b981', 1, 8),
('srv-barba',        'Barba',                 'Taglio e rifinitura barba',             12.00,  20, 5, 'uomo',         '#3b82f6', 1, 9),
('srv-combo',        'Taglio + Barba',        'Combo taglio e barba uomo',             28.00,  45, 5, 'uomo',         '#3b82f6', 1, 10),
('srv-ricrescita',   'Tinta Ricrescita',      'Ritocco radici',                        40.00,  60, 5, 'colore',       '#f59e0b', 1, 11),
('srv-permanente',   'Permanente',            'Ondulazione permanente',                60.00, 120, 5, 'trattamenti',  '#10b981', 1, 12),
('srv-extension',    'Extension',             'Applicazione extension capelli',       150.00, 180, 5, 'speciali',     '#ef4444', 1, 13),
('srv-sposa',        'Acconciatura Sposa',    'Acconciatura sposa (prova inclusa)',   120.00, 120, 5, 'speciali',     '#ef4444', 1, 14);

-- ── OPERATORI ─────────────────────────────────────────────────────
DELETE FROM operatori;
INSERT INTO operatori (id, nome, cognome, ruolo, colore, attivo, specializzazioni, descrizione_positiva, genere) VALUES
('op-giulia', 'Giulia',  'Colombo',  'admin',     '#ec4899', 1, '["colore","meches","balayage","trattamenti"]',  'Titolare, 15 anni esperienza colore e tecniche avanzate', 'F'),
('op-marco',  'Marco',   'Rossi',    'operatore', '#3b82f6', 1, '["taglio uomo","barba","fade"]',                'Barbiere specializzato, tagli moderni e classici', 'M'),
('op-laura',  'Laura',   'Bianchi',  'operatore', '#10b981', 1, '["trattamenti","extension","sposa"]',           'Specialista trattamenti e acconciature cerimonia', 'F'),
('op-luca',   'Luca',    'Ferrari',  'operatore', '#f59e0b', 1, '["taglio uomo","barba","styling"]',             'Giovane talento, esperto di tendenze', 'M'),
('op-paola',  'Paola',   'Verdi',    'operatore', '#8b5cf6', 1, '["piega","styling","taglio donna"]',            'Esperta piega e styling, 10 anni esperienza', 'F');

-- ── CLIENTI ───────────────────────────────────────────────────────
-- Clienti salone sono quelli originali (cli-anna, cli-paolo, etc.)
-- Non toccarli se già presenti

-- ── PACCHETTI ─────────────────────────────────────────────────────
DELETE FROM pacchetti;
INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, servizio_tipo_id, validita_giorni, attivo) VALUES
('pkg-sal-01', 'Festa del Papà',    '3 tagli uomo + 1 barba omaggio',          48.00,  66.00, 4, 'srv-taglio-uomo', 60,  1),
('pkg-sal-02', 'Natale Glamour',    'Colore + Piega + Trattamento (-20%)',     120.00, 155.00, 3, NULL,              30,  1),
('pkg-sal-03', 'Pacchetto Estate',  '5 pieghe al prezzo di 4',                 80.00, 100.00, 5, 'srv-piega',       90,  1);

PRAGMA foreign_keys = ON;
