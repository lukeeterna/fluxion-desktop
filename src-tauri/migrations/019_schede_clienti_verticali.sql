-- ═══════════════════════════════════════════════════════════════════
-- MIGRATION 019: Schede Cliente Verticali
-- ═══════════════════════════════════════════════════════════════════
-- Data: 2026-02-04
-- Obiettivo: Aggiungere macro/micro categoria e schede specifiche per settore
-- NOTA: Non modifica tabelle esistenti, solo aggiunge nuove
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- STEP 1: Impostazioni Macro/Micro Categoria
-- ─────────────────────────────────────────────────────────────────────

-- Aggiungi impostazioni per categorie verticali (se non esistono)
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('macro_categoria', '', 'string'),  -- 'medico', 'auto', 'estetica', 'salone'
    ('micro_categoria', '', 'string');  -- 'odontoiatra', 'fisioterapia', 'meccanico', etc.

-- ─────────────────────────────────────────────────────────────────────
-- STEP 2: Tabelle Schede Cliente Verticali
-- ─────────────────────────────────────────────────────────────────────

-- =====================================================
-- SCHEDA MEDICA / ODONTOIATRICA
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_odontoiatriche (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    
    -- Odontogramma (JSON con stato denti)
    -- Esempio: {"11": {"stato": "sano", "trattamenti": []}, "12": {...}}
    odontogramma TEXT DEFAULT '{}',
    
    -- Storia clinica
    prima_visita DATE,
    ultima_visita DATE,
    frequenza_controlli TEXT, -- '6mesi', '1anno'
    
    -- Abitudini
    spazzolino TEXT, -- 'manuale', 'elettrico'
    filo_interdentale INTEGER DEFAULT 0,
    collutorio INTEGER DEFAULT 0,
    
    -- Allergie specifiche
    allergia_lattice INTEGER DEFAULT 0,
    allergia_anestesia INTEGER DEFAULT 0,
    allergie_altre TEXT,
    
    -- Storia trattamenti (JSON array)
    otturazioni TEXT DEFAULT '[]',
    estrazioni TEXT DEFAULT '[]',
    devitalizzazioni TEXT DEFAULT '[]',
    corone TEXT DEFAULT '[]',
    impianti TEXT DEFAULT '[]',
    
    -- Ortodonzia
    ortodonzia_in_corso INTEGER DEFAULT 0,
    tipo_apparecchio TEXT, -- 'fisso', 'invisibile'
    data_inizio_ortodonzia DATE,
    
    -- Note
    note_cliniche TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_odontoiatriche_cliente ON schede_odontoiatriche(cliente_id);

-- =====================================================
-- SCHEDA FISIOTERAPIA / RIABILITAZIONE
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_fisioterapia (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    
    -- Motivo accesso
    motivo_primo_accesso TEXT,
    data_inizio_terapia DATE,
    data_fine_terapia DATE,
    
    -- Diagnosi
    diagnosi_medica TEXT,
    diagnosi_fisioterapica TEXT,
    
    -- Zone trattate
    zona_principale TEXT, -- 'colonna_lombare', 'spalla_dx', 'ginocchio', etc.
    zone_secondarie TEXT, -- JSON array
    
    -- Valutazioni (JSON)
    valutazione_iniziale TEXT DEFAULT '{}', -- {vas_dolore: 7, rom: {...}}
    scale_valutazione TEXT DEFAULT '{}', -- {nrs: 7, oswestry: 45}
    
    -- Prescrizione medica
    numero_sedute_prescritte INTEGER,
    frequenza_settimanale TEXT, -- '2x', '3x'
    
    -- Storia sedute (JSON array)
    sedute_effettuate TEXT DEFAULT '[]',
    
    -- Esito
    esito_trattamento TEXT, -- 'miglioramento', 'stabile', 'peggioramento'
    
    -- Controindicazioni
    controindicazioni TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_fisioterapia_cliente ON schede_fisioterapia(cliente_id);

-- =====================================================
-- SCHEDA ESTETICA
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_estetica (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    
    -- Analisi pelle
    fototipo INTEGER CHECK (fototipo BETWEEN 1 AND 6), -- Scala Fitzpatrick
    tipo_pelle TEXT, -- 'secca', 'mista', 'grassa', 'sensibile'
    
    -- Allergie
    allergie_prodotti TEXT, -- JSON array
    allergie_profumi INTEGER DEFAULT 0,
    allergie_henne INTEGER DEFAULT 0,
    
    -- Trattamenti precedenti (JSON)
    trattamenti_precedenti TEXT DEFAULT '[]',
    
    -- Epilazione
    ultima_depilazione DATE,
    metodo_depilazione TEXT, -- 'ceretta', 'laser', 'filo'
    
    -- Unghie
    unghie_naturali INTEGER DEFAULT 1,
    problematiche_unghie TEXT,
    
    -- Viso
    problematiche_viso TEXT, -- JSON: ["acne", "macchie", "rughe"]
    routine_skincare TEXT,
    
    -- Corpo
    peso_attuale REAL,
    obiettivo TEXT, -- 'dimagrimento', 'tonificazione', 'rilassamento'
    
    -- Contraindicazioni
    gravidanza INTEGER DEFAULT 0,
    allattamento INTEGER DEFAULT 0,
    patologie_attive TEXT, -- JSON array
    
    -- Note
    note_trattamenti TEXT,
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_estetica_cliente ON schede_estetica(cliente_id);

-- =====================================================
-- SCHEDA PARRUCCHIERE
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_parrucchiere (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    
    -- Analisi capelli
    tipo_capello TEXT, -- 'fino', 'medio', 'spesso'
    porosita TEXT, -- 'bassa', 'media', 'alta'
    lunghezza_attuale TEXT, -- 'corto', 'medio', 'lungo'
    
    -- Storia colore
    base_naturale TEXT, -- livello 1-10
    colore_attuale TEXT,
    
    -- Storia chimica
    colorazioni_precedenti TEXT DEFAULT '[]', -- JSON con date
    decolorazioni INTEGER DEFAULT 0,
    permanente INTEGER DEFAULT 0,
    stirature_chimiche INTEGER DEFAULT 0,
    
    -- Allergie
    allergia_tinta INTEGER DEFAULT 0,
    allergia_ammoniaca INTEGER DEFAULT 0,
    test_pelle_eseguito INTEGER DEFAULT 0,
    data_test_pelle DATE,
    
    -- Preferenze
    servizi_abituali TEXT, -- JSON array
    frequenza_taglio TEXT,
    frequenza_colore TEXT,
    
    -- Prodotti
    prodotti_casa TEXT, -- JSON
    
    -- Preferenze
    preferenze_colore TEXT,
    non_vuole TEXT, -- JSON array ["rosso", "cortissimo"]
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_parrucchiere_cliente ON schede_parrucchiere(cliente_id);

-- =====================================================
-- SCHEDA AUTOMOTIVE (VEICOLI)
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_veicoli (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    
    -- Dati veicolo
    targa TEXT NOT NULL,
    marca TEXT,
    modello TEXT,
    anno INTEGER,
    alimentazione TEXT, -- 'benzina', 'diesel', 'gpl', 'metano', 'elettrico', 'ibrido'
    cilindrata TEXT,
    kw INTEGER,
    telaio TEXT, -- VIN
    
    -- Dati tecnici
    ultima_revisione DATE,
    scadenza_revisione DATE,
    km_attuali INTEGER,
    km_ultimo_tagliando INTEGER,
    
    -- Gomme
    misura_gomme TEXT,
    tipo_gomme TEXT, -- 'estive', 'invernali', 'allseason'
    
    -- Preferenze
    preferenza_ricambi TEXT, -- 'originali', 'compatibili'
    note_veicolo TEXT,
    
    -- Storico interventi (JSON)
    interventi TEXT DEFAULT '[]',
    
    is_default INTEGER DEFAULT 0, -- Veicolo principale
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_veicoli_cliente ON schede_veicoli(cliente_id);
CREATE INDEX IF NOT EXISTS idx_schede_veicoli_targa ON schede_veicoli(targa);

-- =====================================================
-- SCHEDA CARROZZERIA (Interventi)
-- =====================================================
CREATE TABLE IF NOT EXISTS schede_carrozzeria (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    veicolo_id TEXT REFERENCES schede_veicoli(id),
    
    -- Danno
    tipo_danno TEXT, -- 'ammaccatura', 'graffio', 'urto'
    posizione_danno TEXT, -- 'paraurti_ant', 'porta_dx', etc.
    entita_danno TEXT, -- 'lieve', 'media', 'grave'
    descrizione_danno TEXT,
    
    -- Foto (JSON array di URL)
    foto_pre TEXT DEFAULT '[]',
    foto_post TEXT DEFAULT '[]',
    
    -- Preventivo
    preventivo_numero TEXT,
    importo_preventivo REAL,
    approvato INTEGER DEFAULT 0,
    
    -- Intervento
    data_ingresso DATE,
    data_consegna_prevista DATE,
    data_consegna_effettiva DATE,
    
    -- Dettagli
    lavorazioni TEXT DEFAULT '[]', -- JSON
    verniciatura INTEGER DEFAULT 0,
    codice_colore TEXT,
    
    -- Assicurazione
    sinistro_assicurativo INTEGER DEFAULT 0,
    compagnia TEXT,
    numero_sinistro TEXT,
    
    -- Stato
    stato TEXT DEFAULT 'preventivo', -- 'preventivo', 'in_lavorazione', 'completato'
    
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_schede_carrozzeria_cliente ON schede_carrozzeria(cliente_id);

-- ═══════════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════════
-- SELECT 
--     (SELECT COUNT(*) FROM schede_odontoiatriche) as odontoiatria,
--     (SELECT COUNT(*) FROM schede_fisioterapia) as fisioterapia,
--     (SELECT COUNT(*) FROM schede_estetica) as estetica,
--     (SELECT COUNT(*) FROM schede_parrucchiere) as parrucchiere,
--     (SELECT COUNT(*) FROM schede_veicoli) as veicoli,
--     (SELECT COUNT(*) FROM schede_carrozzeria) as carrozzeria;
-- ═══════════════════════════════════════════════════════════════════
