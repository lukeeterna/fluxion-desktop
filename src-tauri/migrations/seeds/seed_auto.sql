-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Servizi Default
-- Verticale: OFFICINA / CARROZZERIA
-- Generato: Gennaio 2026
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci servizi esistenti (opzionale, per reset)
-- DELETE FROM servizi;

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
('srv_aut_001', 'Tagliando Base', 'Manutenzione ordinaria (prezzo indicativo)', 120.00, 120, 'manutenzione', '#6366f1'),
('srv_aut_002', 'Tagliando Completo', 'Tagliando con filtri e controlli', 180.00, 180, 'manutenzione', '#6366f1'),
('srv_aut_003', 'Revisione', 'Revisione ministeriale (tariffa fissa)', 66.88, 60, 'revisione', '#8b5cf6'),
('srv_aut_004', 'Diagnosi Computerizzata', 'Lettura centralina errori', 35.00, 30, 'diagnostica', '#3b82f6'),
('srv_aut_005', 'Cambio Olio', 'Sostituzione olio motore + filtro', 50.00, 45, 'manutenzione', '#f59e0b'),
('srv_aut_006', 'Cambio Gomme 4', 'Montaggio 4 pneumatici', 40.00, 60, 'gomme', '#10b981'),
('srv_aut_007', 'Equilibratura 4 Gomme', 'Equilibratura completa', 20.00, 30, 'gomme', '#10b981'),
('srv_aut_008', 'Cambio + Equilibratura', 'Cambio e equilibratura 4 gomme', 55.00, 75, 'gomme', '#10b981'),
('srv_aut_009', 'Pastiglie Freni Anteriori', 'Sostituzione pastiglie ant.', 80.00, 60, 'freni', '#ef4444'),
('srv_aut_010', 'Pastiglie Freni Posteriori', 'Sostituzione pastiglie post.', 70.00, 60, 'freni', '#ef4444'),
('srv_aut_011', 'Dischi + Pastiglie', 'Sostituzione dischi e pastiglie', 200.00, 120, 'freni', '#ef4444'),
('srv_aut_012', 'Sostituzione Batteria', 'Manodopera cambio batteria', 30.00, 30, 'elettrico', '#f59e0b'),
('srv_aut_013', 'Ricarica Clima', 'Ricarica climatizzatore + controllo', 60.00, 45, 'clima', '#3b82f6'),
('srv_aut_014', 'Controllo Pre-Vacanze', 'Check-up completo sicurezza', 25.00, 30, 'controlli', '#8b5cf6'),
('srv_aut_015', 'Convergenza', 'Allineamento ruote', 45.00, 45, 'gomme', '#10b981');

-- Verifica
-- SELECT COUNT(*) FROM servizi;
-- Expected: 15
