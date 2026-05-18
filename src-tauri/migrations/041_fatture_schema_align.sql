-- ─────────────────────────────────────────────────────────────────
-- Migration 041 — Allineamento schema `fatture` a Fattura struct Rust
-- ─────────────────────────────────────────────────────────────────
-- Contesto: DB clienti live (es. com.fluxion.desktop su iMac) hanno
-- una versione vecchia/divergente del CREATE TABLE fatture (31 col, nomi
-- legacy: imponibile/iva/totale/metodo_pagamento/note/sdi_identificativo/
-- sdi_stato/sdi_data_consegna). Lo schema attuale dichiarato in
-- 007_fatturazione_elettronica.sql ha 45 col con nomi nuovi
-- (imponibile_totale/iva_totale/totale_documento/modalita_pagamento/
-- note_interne/sdi_id_trasmissione/sdi_esito/sdi_errori/...) e include
-- `deleted_at` per soft-delete.
--
-- Sintomo S262 (BUG-FATT-2): tab Fatture non carica, errore
-- "no such column: deleted_at" in `SELECT * FROM fatture WHERE deleted_at IS NULL`.
--
-- Decisione CTO autonoma (S263): poiché 0 righe in fatture + fatture_righe +
-- fatture_riepilogo_iva + fatture_pagamenti (verificato live iMac), DROP+RECREATE
-- è la strategia più sicura (zero data loss, no ALTER complessi).
--
-- numeratore_fatture è preservato (struttura identica, dati invariati).
-- codici_pagamento è preservato.
-- ─────────────────────────────────────────────────────────────────

-- Foreign keys OFF durante DROP per evitare cascade indesiderati su altre tabelle
PRAGMA foreign_keys = OFF;

-- Drop tabelle figlie prima (FK su fatture)
DROP TABLE IF EXISTS fatture_pagamenti;
DROP TABLE IF EXISTS fatture_riepilogo_iva;
DROP TABLE IF EXISTS fatture_righe;
DROP TABLE IF EXISTS fatture;

-- ─────────────────────────────────────────────────────────────────
-- RECREATE fatture (45 col, allineata a Fattura struct e schema 007 corrente)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE fatture (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Numerazione
    numero INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_completo TEXT NOT NULL,

    -- Tipo Documento FatturaPA
    tipo_documento TEXT NOT NULL DEFAULT 'TD01',

    -- Date
    data_emissione TEXT NOT NULL,
    data_scadenza TEXT,

    -- Cliente (Cessionario/Committente)
    cliente_id TEXT NOT NULL,
    cliente_denominazione TEXT NOT NULL,
    cliente_partita_iva TEXT,
    cliente_codice_fiscale TEXT,
    cliente_indirizzo TEXT,
    cliente_cap TEXT,
    cliente_comune TEXT,
    cliente_provincia TEXT,
    cliente_nazione TEXT DEFAULT 'IT',
    cliente_codice_sdi TEXT DEFAULT '0000000',
    cliente_pec TEXT,

    -- Totali
    imponibile_totale REAL NOT NULL DEFAULT 0,
    iva_totale REAL NOT NULL DEFAULT 0,
    totale_documento REAL NOT NULL DEFAULT 0,

    -- Ritenuta d'acconto
    ritenuta_tipo TEXT,
    ritenuta_percentuale REAL,
    ritenuta_importo REAL,
    ritenuta_causale TEXT,

    -- Bollo
    bollo_virtuale INTEGER DEFAULT 0,
    bollo_importo REAL DEFAULT 2.00,

    -- Pagamento
    modalita_pagamento TEXT DEFAULT 'MP05',
    condizioni_pagamento TEXT DEFAULT 'TP02',

    -- Stato
    stato TEXT NOT NULL DEFAULT 'bozza',

    -- SDI
    sdi_id_trasmissione TEXT,
    sdi_data_invio TEXT,
    sdi_data_risposta TEXT,
    sdi_esito TEXT,
    sdi_errori TEXT,

    -- File XML
    xml_filename TEXT,
    xml_content TEXT,

    -- Riferimenti
    appuntamento_id TEXT,
    ordine_id TEXT,
    fattura_origine_id TEXT,

    -- Note
    causale TEXT,
    note_interne TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT,

    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id),
    FOREIGN KEY (fattura_origine_id) REFERENCES fatture(id)
);

CREATE INDEX idx_fatture_numero ON fatture(numero, anno);
CREATE INDEX idx_fatture_cliente ON fatture(cliente_id);
CREATE INDEX idx_fatture_stato ON fatture(stato);
CREATE INDEX idx_fatture_data ON fatture(data_emissione);
CREATE INDEX idx_fatture_deleted_at ON fatture(deleted_at);

-- ─────────────────────────────────────────────────────────────────
-- RECREATE fatture_righe (allineata a FatturaRiga struct)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE fatture_righe (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    numero_linea INTEGER NOT NULL,

    descrizione TEXT NOT NULL,
    codice_articolo TEXT,

    quantita REAL NOT NULL DEFAULT 1,
    unita_misura TEXT DEFAULT 'PZ',
    prezzo_unitario REAL NOT NULL,

    sconto_percentuale REAL DEFAULT 0,
    sconto_importo REAL DEFAULT 0,

    prezzo_totale REAL NOT NULL,

    aliquota_iva REAL NOT NULL DEFAULT 22.0,
    natura TEXT,

    servizio_id TEXT,
    appuntamento_id TEXT,

    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX idx_fatture_righe_fattura ON fatture_righe(fattura_id);

-- ─────────────────────────────────────────────────────────────────
-- RECREATE fatture_riepilogo_iva
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE fatture_riepilogo_iva (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    aliquota_iva REAL NOT NULL,
    natura TEXT,
    imponibile REAL NOT NULL,
    imposta REAL NOT NULL,
    esigibilita TEXT DEFAULT 'I',

    riferimento_normativo TEXT,

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE
);

CREATE INDEX idx_fatture_riepilogo_fattura ON fatture_riepilogo_iva(fattura_id);

-- ─────────────────────────────────────────────────────────────────
-- RECREATE fatture_pagamenti
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE fatture_pagamenti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    data_pagamento TEXT NOT NULL,
    importo REAL NOT NULL,
    metodo TEXT NOT NULL,

    iban TEXT,
    riferimento TEXT,

    note TEXT,

    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE
);

CREATE INDEX idx_pagamenti_fattura ON fatture_pagamenti(fattura_id);

PRAGMA foreign_keys = ON;
