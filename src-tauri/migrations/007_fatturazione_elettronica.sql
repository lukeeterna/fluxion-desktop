-- ═══════════════════════════════════════════════════════════════════
-- FLUXION Migration 007: Fatturazione Elettronica Italiana
-- FatturaPA XML + SDI + Gestione Pagamenti
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI FATTURAZIONE (Dati Azienda Emittente)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS impostazioni_fatturazione (
    id TEXT PRIMARY KEY DEFAULT 'default',

    -- Dati Azienda
    denominazione TEXT NOT NULL,
    partita_iva TEXT NOT NULL,
    codice_fiscale TEXT,

    -- Regime Fiscale (RF01=Ordinario, RF19=Forfettario)
    regime_fiscale TEXT NOT NULL DEFAULT 'RF19',

    -- Sede Legale
    indirizzo TEXT NOT NULL,
    cap TEXT NOT NULL,
    comune TEXT NOT NULL,
    provincia TEXT NOT NULL,
    nazione TEXT DEFAULT 'IT',

    -- Contatti
    telefono TEXT,
    email TEXT,
    pec TEXT,

    -- Numerazione Fatture
    prefisso_numerazione TEXT DEFAULT '',
    ultimo_numero INTEGER DEFAULT 0,
    anno_corrente INTEGER DEFAULT 2026,

    -- IVA Default
    aliquota_iva_default REAL DEFAULT 22.0,
    natura_iva_default TEXT, -- N1-N7 per esenzioni

    -- Banca per Pagamenti
    iban TEXT,
    bic TEXT,
    nome_banca TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────────────────────────
-- FATTURE (Documento Principale)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fatture (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),

    -- Numerazione
    numero INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_completo TEXT NOT NULL, -- es: "1/2026" o "FT-001/2026"

    -- Tipo Documento FatturaPA
    -- TD01=Fattura, TD04=Nota Credito, TD05=Nota Debito
    -- TD06=Parcella, TD24=Fattura Differita, TD25=Fattura Accompagnatoria
    tipo_documento TEXT NOT NULL DEFAULT 'TD01',

    -- Date
    data_emissione TEXT NOT NULL, -- ISO 8601
    data_scadenza TEXT,

    -- Cliente (Cessionario/Committente)
    cliente_id TEXT NOT NULL,
    -- Snapshot dati cliente al momento emissione
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

    -- Ritenuta d'acconto (se applicabile)
    ritenuta_tipo TEXT, -- RT01=Persone fisiche, RT02=Persone giuridiche
    ritenuta_percentuale REAL,
    ritenuta_importo REAL,
    ritenuta_causale TEXT, -- A-Z causale

    -- Bollo (se esente IVA > 77.47€)
    bollo_virtuale INTEGER DEFAULT 0, -- 1=SI, 0=NO
    bollo_importo REAL DEFAULT 2.00,

    -- Pagamento
    modalita_pagamento TEXT DEFAULT 'MP05', -- MP01=Contanti, MP05=Bonifico, MP08=Carta
    condizioni_pagamento TEXT DEFAULT 'TP02', -- TP01=Rate, TP02=Completo, TP03=Anticipo

    -- Stato Fattura
    -- bozza, emessa, inviata_sdi, accettata, rifiutata, scartata, pagata, annullata
    stato TEXT NOT NULL DEFAULT 'bozza',

    -- SDI
    sdi_id_trasmissione TEXT, -- ID assegnato da SDI
    sdi_data_invio TEXT,
    sdi_data_risposta TEXT,
    sdi_esito TEXT, -- RC=Ricevuta Consegna, NS=Notifica Scarto, MC=Mancata Consegna
    sdi_errori TEXT, -- JSON array errori

    -- File XML
    xml_filename TEXT,
    xml_content TEXT, -- XML completo FatturaPA

    -- Riferimenti
    appuntamento_id TEXT,
    ordine_id TEXT,
    fattura_origine_id TEXT, -- per note credito

    -- Note
    causale TEXT, -- max 200 char per blocco, può essere multipla
    note_interne TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT, -- soft delete

    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id),
    FOREIGN KEY (fattura_origine_id) REFERENCES fatture(id)
);

CREATE INDEX idx_fatture_numero ON fatture(numero, anno);
CREATE INDEX idx_fatture_cliente ON fatture(cliente_id);
CREATE INDEX idx_fatture_stato ON fatture(stato);
CREATE INDEX idx_fatture_data ON fatture(data_emissione);

-- ─────────────────────────────────────────────────────────────────
-- FATTURE RIGHE (Linee Dettaglio)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fatture_righe (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    -- Numerazione riga
    numero_linea INTEGER NOT NULL,

    -- Descrizione
    descrizione TEXT NOT NULL,
    codice_articolo TEXT, -- opzionale

    -- Quantità e Prezzo
    quantita REAL NOT NULL DEFAULT 1,
    unita_misura TEXT DEFAULT 'PZ', -- PZ, NR, KG, LT, M, MQ, MC, H
    prezzo_unitario REAL NOT NULL,

    -- Sconti
    sconto_percentuale REAL DEFAULT 0,
    sconto_importo REAL DEFAULT 0,

    -- Totale Riga
    prezzo_totale REAL NOT NULL, -- qty * prezzo - sconti

    -- IVA
    aliquota_iva REAL NOT NULL DEFAULT 22.0,
    natura TEXT, -- N1-N7 per operazioni esenti/non imponibili
    -- N1=Escluse art.15, N2=Non soggette, N2.1=Non soggette art.7
    -- N2.2=Non soggette altri casi, N3=Non imponibili
    -- N4=Esenti, N5=Regime margine, N6=Inversione contabile, N7=IVA altro stato

    -- Riferimenti
    servizio_id TEXT,
    appuntamento_id TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id)
);

CREATE INDEX idx_fatture_righe_fattura ON fatture_righe(fattura_id);

-- ─────────────────────────────────────────────────────────────────
-- FATTURE RIEPILOGO IVA (per aliquota)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fatture_riepilogo_iva (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    aliquota_iva REAL NOT NULL,
    natura TEXT, -- se aliquota = 0
    imponibile REAL NOT NULL,
    imposta REAL NOT NULL,
    esigibilita TEXT DEFAULT 'I', -- I=Immediata, D=Differita, S=Split payment

    -- Riferimento normativo per esenzioni
    riferimento_normativo TEXT,

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE
);

CREATE INDEX idx_fatture_riepilogo_fattura ON fatture_riepilogo_iva(fattura_id);

-- ─────────────────────────────────────────────────────────────────
-- PAGAMENTI FATTURE
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fatture_pagamenti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    fattura_id TEXT NOT NULL,

    -- Dettaglio Pagamento
    data_pagamento TEXT NOT NULL,
    importo REAL NOT NULL,
    metodo TEXT NOT NULL, -- contanti, bonifico, carta, satispay, assegno

    -- Riferimenti bancari
    iban TEXT,
    riferimento TEXT, -- CRO, numero assegno, etc.

    -- Note
    note TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (fattura_id) REFERENCES fatture(id) ON DELETE CASCADE
);

CREATE INDEX idx_pagamenti_fattura ON fatture_pagamenti(fattura_id);

-- ─────────────────────────────────────────────────────────────────
-- NUMERATORE FATTURE (per garantire univocità)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS numeratore_fatture (
    anno INTEGER PRIMARY KEY,
    ultimo_numero INTEGER NOT NULL DEFAULT 0
);

-- Inizializza anno corrente
INSERT OR IGNORE INTO numeratore_fatture (anno, ultimo_numero) VALUES (2026, 0);

-- ─────────────────────────────────────────────────────────────────
-- CODICI MODALITÀ PAGAMENTO FatturaPA
-- ─────────────────────────────────────────────────────────────────
-- Tabella di lookup per UI
CREATE TABLE IF NOT EXISTS codici_pagamento (
    codice TEXT PRIMARY KEY,
    descrizione TEXT NOT NULL
);

INSERT OR IGNORE INTO codici_pagamento (codice, descrizione) VALUES
    ('MP01', 'Contanti'),
    ('MP02', 'Assegno'),
    ('MP03', 'Assegno circolare'),
    ('MP04', 'Contanti presso Tesoreria'),
    ('MP05', 'Bonifico'),
    ('MP06', 'Vaglia cambiario'),
    ('MP07', 'Bollettino bancario'),
    ('MP08', 'Carta di pagamento'),
    ('MP09', 'RID'),
    ('MP10', 'RID utenze'),
    ('MP11', 'RID veloce'),
    ('MP12', 'RIBA'),
    ('MP13', 'MAV'),
    ('MP14', 'Quietanza erario'),
    ('MP15', 'Giroconto su conti di contabilità speciale'),
    ('MP16', 'Domiciliazione bancaria'),
    ('MP17', 'Domiciliazione postale'),
    ('MP18', 'Bollettino di c/c postale'),
    ('MP19', 'SEPA Direct Debit'),
    ('MP20', 'SEPA Direct Debit CORE'),
    ('MP21', 'SEPA Direct Debit B2B'),
    ('MP22', 'Trattenuta su somme già riscosse'),
    ('MP23', 'PagoPA');

-- ─────────────────────────────────────────────────────────────────
-- CODICI NATURA IVA (per esenzioni)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS codici_natura_iva (
    codice TEXT PRIMARY KEY,
    descrizione TEXT NOT NULL,
    riferimento_normativo TEXT
);

INSERT OR IGNORE INTO codici_natura_iva (codice, descrizione, riferimento_normativo) VALUES
    ('N1', 'Escluse ex art. 15 DPR 633/72', 'Art. 15 DPR 633/72'),
    ('N2', 'Non soggette', NULL),
    ('N2.1', 'Non soggette ad IVA - artt. da 7 a 7-septies DPR 633/72', 'Artt. 7-7septies DPR 633/72'),
    ('N2.2', 'Non soggette - altri casi', NULL),
    ('N3', 'Non imponibili', NULL),
    ('N3.1', 'Non imponibili - esportazioni', 'Art. 8 c.1 lett.a-b DPR 633/72'),
    ('N3.2', 'Non imponibili - cessioni intracomunitarie', 'Art. 41 DL 331/93'),
    ('N3.3', 'Non imponibili - cessioni verso San Marino', 'DM 24/12/1993'),
    ('N3.4', 'Non imponibili - operazioni assimilate cessioni export', 'Art. 8-bis DPR 633/72'),
    ('N3.5', 'Non imponibili - dichiarazione intento', 'Art. 8 c.1 lett.c DPR 633/72'),
    ('N3.6', 'Non imponibili - altre operazioni', NULL),
    ('N4', 'Esenti', 'Art. 10 DPR 633/72'),
    ('N5', 'Regime del margine / IVA non esposta', 'Art. 36 DL 41/95'),
    ('N6', 'Inversione contabile (reverse charge)', NULL),
    ('N6.1', 'Inversione contabile - cessione rottami', 'Art. 74 c.7-8 DPR 633/72'),
    ('N6.2', 'Inversione contabile - cessione oro/argento', 'Art. 17 c.5 DPR 633/72'),
    ('N6.3', 'Inversione contabile - subappalto edilizia', 'Art. 17 c.6 lett.a DPR 633/72'),
    ('N6.4', 'Inversione contabile - cessione fabbricati', 'Art. 17 c.6 lett.a-bis DPR 633/72'),
    ('N6.5', 'Inversione contabile - cessione telefoni', 'Art. 17 c.6 lett.b DPR 633/72'),
    ('N6.6', 'Inversione contabile - cessione prodotti elettronici', 'Art. 17 c.6 lett.c DPR 633/72'),
    ('N6.7', 'Inversione contabile - prestazioni comparto edile', 'Art. 17 c.6 lett.a-ter DPR 633/72'),
    ('N6.8', 'Inversione contabile - settore energetico', 'Art. 17 c.6 lett.d-bis/ter/quater DPR 633/72'),
    ('N6.9', 'Inversione contabile - altri casi', NULL),
    ('N7', 'IVA assolta in altro stato UE', 'Regolamento UE 282/2011');

-- ─────────────────────────────────────────────────────────────────
-- IMPOSTAZIONI DEFAULT (Regime Forfettario)
-- ─────────────────────────────────────────────────────────────────
INSERT OR IGNORE INTO impostazioni_fatturazione (
    id,
    denominazione,
    partita_iva,
    codice_fiscale,
    regime_fiscale,
    indirizzo,
    cap,
    comune,
    provincia,
    nazione,
    aliquota_iva_default,
    natura_iva_default
) VALUES (
    'default',
    'Automation Business',
    '02159940762',
    'DSTMGN81S12L738L',
    'RF19',
    'Via Roma 1',
    '85100',
    'Potenza',
    'PZ',
    'IT',
    0.0,
    'N2.2'  -- Regime forfettario = operazioni non soggette
);
