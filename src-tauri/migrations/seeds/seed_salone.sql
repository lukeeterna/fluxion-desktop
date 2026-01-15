-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Servizi Default
-- Verticale: SALONE PARRUCCHIERE
-- Generato: Gennaio 2026
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci servizi esistenti (opzionale, per reset)
-- DELETE FROM servizi;

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
('srv_sal_001', 'Taglio Donna', 'Taglio, shampoo e asciugatura', 35.00, 60, 'taglio', '#ec4899'),
('srv_sal_002', 'Taglio Uomo', 'Taglio classico maschile', 18.00, 30, 'taglio', '#3b82f6'),
('srv_sal_003', 'Piega', 'Messa in piega professionale', 20.00, 30, 'styling', '#8b5cf6'),
('srv_sal_004', 'Colore', 'Colorazione completa', 55.00, 90, 'colore', '#f59e0b'),
('srv_sal_005', 'Meches', 'Meches o colpi di sole', 65.00, 120, 'colore', '#f59e0b'),
('srv_sal_006', 'Balayage', 'Tecnica schiarente naturale', 85.00, 150, 'colore', '#f59e0b'),
('srv_sal_007', 'Trattamento Cheratina', 'Trattamento lisciante ristrutturante', 80.00, 120, 'trattamenti', '#10b981'),
('srv_sal_008', 'Barba', 'Taglio e rifinitura barba', 12.00, 20, 'uomo', '#3b82f6'),
('srv_sal_009', 'Taglio + Barba', 'Combo taglio e barba uomo', 28.00, 45, 'uomo', '#3b82f6'),
('srv_sal_010', 'Shampoo + Piega', 'Lavaggio e asciugatura', 25.00, 30, 'styling', '#8b5cf6'),
('srv_sal_011', 'Tinta Ricrescita', 'Ritocco radici', 40.00, 60, 'colore', '#f59e0b'),
('srv_sal_012', 'Permanente', 'Ondulazione permanente', 60.00, 120, 'trattamenti', '#10b981'),
('srv_sal_013', 'Extension', 'Applicazione extension capelli', 150.00, 180, 'speciali', '#ef4444'),
('srv_sal_014', 'Sposa', 'Acconciatura sposa (prova inclusa)', 120.00, 120, 'speciali', '#ef4444'),
('srv_sal_015', 'Taglio Bambino', 'Taglio bambino sotto 12 anni', 12.00, 20, 'taglio', '#ec4899');

-- Verifica
-- SELECT COUNT(*) FROM servizi;
-- Expected: 15
