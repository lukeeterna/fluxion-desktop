-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Servizi Default
-- Verticale: STUDIO MEDICO
-- Generato: Gennaio 2026
-- ═══════════════════════════════════════════════════════════════════

-- Pulisci servizi esistenti (opzionale, per reset)
-- DELETE FROM servizi;

INSERT INTO servizi (id, nome, descrizione, prezzo, durata, categoria, colore) VALUES
('srv_med_001', 'Visita Generale', 'Visita medica di base', 80.00, 30, 'visite', '#6366f1'),
('srv_med_002', 'Visita Specialistica', 'Visita con specialista', 120.00, 45, 'visite', '#8b5cf6'),
('srv_med_003', 'Prima Visita', 'Prima visita con anamnesi completa', 100.00, 45, 'visite', '#6366f1'),
('srv_med_004', 'Controllo', 'Visita di follow-up', 60.00, 20, 'visite', '#10b981'),
('srv_med_005', 'Ecografia Addominale', 'Ecografia addome completo', 70.00, 30, 'diagnostica', '#3b82f6'),
('srv_med_006', 'Ecografia Tiroidea', 'Ecografia tiroide', 60.00, 20, 'diagnostica', '#3b82f6'),
('srv_med_007', 'Ecografia Pelvica', 'Ecografia pelvi', 70.00, 30, 'diagnostica', '#3b82f6'),
('srv_med_008', 'ECG', 'Elettrocardiogramma', 50.00, 20, 'diagnostica', '#ef4444'),
('srv_med_009', 'Analisi Sangue Base', 'Emocromo + glicemia + colesterolo', 35.00, 15, 'analisi', '#f59e0b'),
('srv_med_010', 'Analisi Sangue Completo', 'Pannello metabolico completo', 60.00, 15, 'analisi', '#f59e0b'),
('srv_med_011', 'Certificato Medico', 'Certificato malattia/idoneita', 30.00, 15, 'certificati', '#8b5cf6'),
('srv_med_012', 'Certificato Sportivo', 'Cert. attivita non agonistica + ECG', 50.00, 30, 'certificati', '#8b5cf6'),
('srv_med_013', 'Visita + ECG', 'Visita cardiologica con ECG', 120.00, 45, 'visite', '#ef4444'),
('srv_med_014', 'Vaccino Antinfluenzale', 'Vaccinazione stagionale', 30.00, 15, 'vaccini', '#10b981'),
('srv_med_015', 'Holter ECG 24h', 'Monitoraggio cardiaco 24 ore', 100.00, 30, 'diagnostica', '#ef4444');

-- Verifica
-- SELECT COUNT(*) FROM servizi;
-- Expected: 15
