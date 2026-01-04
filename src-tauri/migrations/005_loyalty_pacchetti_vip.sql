-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 005: Loyalty + VIP + Referral + Pacchetti
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-01-04
-- Fase 5: Quick Wins Zero-Cost
-- Obiettivo: Tessera timbri digitale, VIP manual, referral tracking, pacchetti
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- STEP 1: Aggiungi campi Loyalty a tabella clienti
-- ───────────────────────────────────────────────────────────────

-- Campo: loyalty_visits (contatore visite completate)
ALTER TABLE clienti ADD COLUMN loyalty_visits INTEGER DEFAULT 0;

-- Campo: loyalty_threshold (soglia per premio, configurabile per cliente)
ALTER TABLE clienti ADD COLUMN loyalty_threshold INTEGER DEFAULT 10;

-- Campo: is_vip (VIP manuale, toggle esercente)
ALTER TABLE clienti ADD COLUMN is_vip INTEGER DEFAULT 0;

-- Campo: referral_source (chi ti ha consigliato)
ALTER TABLE clienti ADD COLUMN referral_source TEXT;

-- Campo: referral_cliente_id (link al cliente che ha riferito)
ALTER TABLE clienti ADD COLUMN referral_cliente_id TEXT;

-- ───────────────────────────────────────────────────────────────
-- STEP 2: Indici per query loyalty/referral
-- ───────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_clienti_is_vip ON clienti(is_vip);
CREATE INDEX IF NOT EXISTS idx_clienti_loyalty ON clienti(loyalty_visits, loyalty_threshold);
CREATE INDEX IF NOT EXISTS idx_clienti_referral ON clienti(referral_cliente_id);

-- ───────────────────────────────────────────────────────────────
-- STEP 3: Tabella Pacchetti (Commerce v1)
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS pacchetti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    nome TEXT NOT NULL,
    descrizione TEXT,

    -- Pricing
    prezzo REAL NOT NULL,
    prezzo_originale REAL,  -- Prezzo senza sconto (per mostrare risparmio)

    -- Contenuto
    servizi_inclusi INTEGER NOT NULL,  -- Numero servizi nel pacchetto
    servizio_tipo_id TEXT,  -- Se specifico per un tipo servizio (nullable = qualsiasi)

    -- Validità
    validita_giorni INTEGER DEFAULT 365,  -- Giorni validità dopo acquisto

    -- Status
    attivo INTEGER DEFAULT 1,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (servizio_tipo_id) REFERENCES servizi(id)
);

CREATE INDEX IF NOT EXISTS idx_pacchetti_attivo ON pacchetti(attivo);

-- ───────────────────────────────────────────────────────────────
-- STEP 4: Tabella Acquisti Pacchetti (clienti_pacchetti)
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS clienti_pacchetti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    cliente_id TEXT NOT NULL,
    pacchetto_id TEXT NOT NULL,

    -- Stato workflow
    stato TEXT NOT NULL DEFAULT 'proposto',
    -- 'proposto' = offerto al cliente
    -- 'venduto' = pagato
    -- 'in_uso' = almeno 1 servizio usato
    -- 'completato' = tutti i servizi usati
    -- 'scaduto' = scadenza passata
    -- 'annullato' = rimborso/cancellazione

    -- Utilizzo
    servizi_usati INTEGER DEFAULT 0,
    servizi_totali INTEGER NOT NULL,

    -- Date
    data_proposta TEXT DEFAULT (datetime('now')),
    data_acquisto TEXT,
    data_scadenza TEXT,

    -- Pagamento (offline)
    metodo_pagamento TEXT,  -- 'contanti', 'carta', 'bonifico', 'satispay'
    pagato INTEGER DEFAULT 0,

    -- Note
    note TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id)
);

CREATE INDEX IF NOT EXISTS idx_clienti_pacchetti_cliente ON clienti_pacchetti(cliente_id);
CREATE INDEX IF NOT EXISTS idx_clienti_pacchetti_stato ON clienti_pacchetti(stato);
CREATE INDEX IF NOT EXISTS idx_clienti_pacchetti_scadenza ON clienti_pacchetti(data_scadenza);

-- ───────────────────────────────────────────────────────────────
-- STEP 5: Tabella Waitlist (Lista attesa slot)
-- ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS waitlist (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    cliente_id TEXT NOT NULL,
    operatore_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,

    -- Slot richiesto
    data_richiesta TEXT NOT NULL,  -- YYYY-MM-DD
    ora_richiesta TEXT NOT NULL,    -- HH:MM

    -- Priorità FIFO
    priorita INTEGER DEFAULT 1,

    -- Stato
    stato TEXT DEFAULT 'attivo',
    -- 'attivo' = in attesa
    -- 'notificato' = cliente avvisato di slot libero
    -- 'confermato' = cliente ha prenotato
    -- 'scaduto' = timeout risposta
    -- 'cancellato' = rimosso da lista

    -- Timestamps
    creato_il TEXT DEFAULT (datetime('now')),
    notificato_il TEXT,
    scadenza_risposta TEXT,  -- 2h dopo notifica

    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id),
    FOREIGN KEY (servizio_id) REFERENCES servizi(id)
);

CREATE INDEX IF NOT EXISTS idx_waitlist_slot ON waitlist(data_richiesta, ora_richiesta, operatore_id);
CREATE INDEX IF NOT EXISTS idx_waitlist_stato ON waitlist(stato);
CREATE INDEX IF NOT EXISTS idx_waitlist_cliente ON waitlist(cliente_id);

-- ───────────────────────────────────────────────────────────────
-- STEP 6: Seed Pacchetti Demo
-- ───────────────────────────────────────────────────────────────

INSERT INTO pacchetti (id, nome, descrizione, prezzo, prezzo_originale, servizi_inclusi, validita_giorni, attivo) VALUES
('pkg_beauty_5', 'Pacchetto Beauty 5', '5 servizi a scelta', 175.00, 200.00, 5, 180, 1),
('pkg_relax_10', 'Pacchetto Relax 10', '10 massaggi relax', 350.00, 450.00, 10, 365, 1),
('pkg_vip_monthly', 'Abbonamento VIP Mensile', '4 servizi premium al mese', 120.00, 160.00, 4, 30, 1);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE POST-MIGRATION
-- ═══════════════════════════════════════════════════════════════
-- Verifica nuove colonne:
--
-- SELECT loyalty_visits, loyalty_threshold, is_vip, referral_source
-- FROM clienti LIMIT 1;
--
-- Verifica tabelle create:
--
-- SELECT name FROM sqlite_master WHERE type='table'
-- AND name IN ('pacchetti', 'clienti_pacchetti', 'waitlist');
--
-- ═══════════════════════════════════════════════════════════════
-- Fine Migration 005
-- ═══════════════════════════════════════════════════════════════
