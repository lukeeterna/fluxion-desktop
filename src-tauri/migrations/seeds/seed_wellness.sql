-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Servizi Default
-- Verticale: PALESTRA / CENTRO BENESSERE
-- Generato: Gennaio 2026
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci servizi esistenti (opzionale, per reset)
-- DELETE FROM servizi;

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
('srv_wel_001', 'Abbonamento Mensile', 'Accesso illimitato palestra', 45.00, 0, 'abbonamenti', '#6366f1'),
('srv_wel_002', 'Abbonamento Trimestrale', 'Accesso 3 mesi (risparmio 10%)', 120.00, 0, 'abbonamenti', '#6366f1'),
('srv_wel_003', 'Abbonamento Annuale', 'Accesso 12 mesi (risparmio 20%)', 400.00, 0, 'abbonamenti', '#6366f1'),
('srv_wel_004', 'Ingresso Singolo', 'Ingresso giornaliero', 10.00, 0, 'abbonamenti', '#8b5cf6'),
('srv_wel_005', 'Personal Training', 'Seduta individuale con trainer', 50.00, 60, 'personal', '#ec4899'),
('srv_wel_006', 'Pacchetto PT 10 sedute', 'Personal training (sconto 15%)', 425.00, 600, 'personal', '#ec4899'),
('srv_wel_007', 'Yoga', 'Lezione di gruppo yoga', 10.00, 60, 'corsi', '#10b981'),
('srv_wel_008', 'Pilates', 'Lezione di gruppo pilates', 10.00, 60, 'corsi', '#10b981'),
('srv_wel_009', 'Spinning', 'Lezione indoor cycling', 10.00, 45, 'corsi', '#f59e0b'),
('srv_wel_010', 'CrossFit', 'Allenamento funzionale intenso', 12.00, 60, 'corsi', '#ef4444'),
('srv_wel_011', 'Zumba', 'Fitness dance latino', 10.00, 60, 'corsi', '#f59e0b'),
('srv_wel_012', 'Acquagym', 'Ginnastica in acqua', 12.00, 45, 'corsi', '#3b82f6'),
('srv_wel_013', 'Valutazione Fitness', 'Analisi composizione corporea', 30.00, 45, 'valutazioni', '#8b5cf6'),
('srv_wel_014', 'Scheda Allenamento', 'Programma personalizzato', 25.00, 30, 'valutazioni', '#8b5cf6'),
('srv_wel_015', 'Massaggio Sportivo', 'Massaggio decontratturante', 50.00, 60, 'benessere', '#ec4899');

-- Verifica
-- SELECT COUNT(*) FROM servizi;
-- Expected: 15
