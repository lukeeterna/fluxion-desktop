-- ═══════════════════════════════════════════════════════════════════
-- FLUXION — Seed Pacchetti Stagionali + Dati Fedeltà
-- Per screenshot Pacchetti (22) e Fedeltà (23)
-- ═══════════════════════════════════════════════════════════════════

PRAGMA foreign_keys = OFF;

-- -------------------------------------------------------
-- PULIZIA pacchetti demo vecchi (dalla migration 005)
-- -------------------------------------------------------
DELETE FROM pacchetto_servizi WHERE pacchetto_id IN ('pkg_beauty_5', 'pkg_relax_10', 'pkg_vip_monthly');
DELETE FROM clienti_pacchetti WHERE pacchetto_id IN ('pkg_beauty_5', 'pkg_relax_10', 'pkg_vip_monthly');
DELETE FROM pacchetti WHERE id IN ('pkg_beauty_5', 'pkg_relax_10', 'pkg_vip_monthly');

-- -------------------------------------------------------
-- 3 PACCHETTI STAGIONALI
-- -------------------------------------------------------
INSERT OR REPLACE INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, validita_giorni, attivo, created_at, updated_at) VALUES
('pkg-festa-papa', 'Festa del Papà', 'Taglio uomo + barba + styling — regalo perfetto per la festa del papà', 89.00, 126.00, 3, 30, 1, '2026-03-01 09:00:00', '2026-03-01 09:00:00'),
('pkg-estate', 'Estate Brillante', 'Colore + meches + trattamento + piega + taglio — pronta per l''estate', 149.00, 210.00, 5, 90, 1, '2026-03-01 09:00:00', '2026-03-01 09:00:00'),
('pkg-natale', 'Natale Glamour', 'Piega + trattamento + colore + styling — splendi alle feste', 119.00, 165.00, 4, 45, 1, '2026-03-01 09:00:00', '2026-03-01 09:00:00');

-- -------------------------------------------------------
-- PACCHETTO-SERVIZI (many-to-many links)
-- -------------------------------------------------------
-- Festa del Papà: taglio uomo + barba + trattamento
INSERT OR REPLACE INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita, created_at) VALUES
('ps-fp-1', 'pkg-festa-papa', 'srv-taglio-uomo', 1, '2026-03-01 09:00:00'),
('ps-fp-2', 'pkg-festa-papa', 'srv-barba', 1, '2026-03-01 09:00:00'),
('ps-fp-3', 'pkg-festa-papa', 'srv-trattamento', 1, '2026-03-01 09:00:00');

-- Estate Brillante: colore + meches + trattamento + piega + taglio
INSERT OR REPLACE INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita, created_at) VALUES
('ps-es-1', 'pkg-estate', 'srv-colore', 1, '2026-03-01 09:00:00'),
('ps-es-2', 'pkg-estate', 'srv-meches', 1, '2026-03-01 09:00:00'),
('ps-es-3', 'pkg-estate', 'srv-trattamento', 1, '2026-03-01 09:00:00'),
('ps-es-4', 'pkg-estate', 'srv-piega', 1, '2026-03-01 09:00:00'),
('ps-es-5', 'pkg-estate', 'srv-taglio-uomo', 1, '2026-03-01 09:00:00');

-- Natale Glamour: piega + trattamento + colore + meches
INSERT OR REPLACE INTO pacchetto_servizi (id, pacchetto_id, servizio_id, quantita, created_at) VALUES
('ps-na-1', 'pkg-natale', 'srv-piega', 1, '2026-03-01 09:00:00'),
('ps-na-2', 'pkg-natale', 'srv-trattamento', 1, '2026-03-01 09:00:00'),
('ps-na-3', 'pkg-natale', 'srv-colore', 1, '2026-03-01 09:00:00'),
('ps-na-4', 'pkg-natale', 'srv-meches', 1, '2026-03-01 09:00:00');

-- -------------------------------------------------------
-- LOYALTY DATA — Update clienti esistenti
-- -------------------------------------------------------
-- Anna Ferrari: VIP, 8/10 timbri (quasi completa)
UPDATE clienti SET loyalty_visits = 8, loyalty_threshold = 10, is_vip = 1 WHERE id = 'cli-anna';

-- Chiara: 5/10 timbri (a metà strada)
UPDATE clienti SET loyalty_visits = 5, loyalty_threshold = 10, is_vip = 0 WHERE id = 'cli-chiara';

-- Elena Ricci: 10/10 timbri (completata! premio disponibile), VIP
UPDATE clienti SET loyalty_visits = 10, loyalty_threshold = 10, is_vip = 1 WHERE id = 'cli-elena';

-- -------------------------------------------------------
-- CLIENTI-PACCHETTI (acquisti)
-- -------------------------------------------------------
-- Anna ha comprato Estate Brillante (in uso, 2/5 servizi usati)
INSERT OR REPLACE INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato, created_at, updated_at) VALUES
('cp-anna-estate', 'cli-anna', 'pkg-estate', 'in_uso', 2, 5, '2026-02-28 10:00:00', '2026-03-01 10:00:00', '2026-05-30 23:59:59', 'carta', 1, '2026-03-01 10:00:00', '2026-03-15 14:00:00');

-- Chiara ha comprato Festa del Papà (venduto, non ancora iniziato)
INSERT OR REPLACE INTO clienti_pacchetti (id, cliente_id, pacchetto_id, stato, servizi_usati, servizi_totali, data_proposta, data_acquisto, data_scadenza, metodo_pagamento, pagato, created_at, updated_at) VALUES
('cp-chiara-papa', 'cli-chiara', 'pkg-festa-papa', 'venduto', 0, 3, '2026-03-10 11:00:00', '2026-03-15 11:00:00', '2026-04-14 23:59:59', 'contanti', 1, '2026-03-15 11:00:00', '2026-03-15 11:00:00');

PRAGMA foreign_keys = ON;
