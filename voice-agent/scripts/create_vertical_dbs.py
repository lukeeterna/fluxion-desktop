#!/usr/bin/env python3
"""
FLUXION - Create Vertical Demo DBs for Sara Testing
====================================================
Creates 9 complete SQLite databases (one per vertical) with realistic
Italian business data: settings, services, operators, work hours,
FAQ settings, and sample clients.

Usage:
    python create_vertical_dbs.py [--output-dir PATH]

Default output: voice-agent/data/vertical_dbs/
"""

import os
import sys
import sqlite3
import uuid
import shutil
from datetime import datetime


# ========================================================================
# CONFIGURATION
# ========================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "vertical_dbs")

# Existing odontoiatra DB to copy
EXISTING_DB = os.path.join(PROJECT_ROOT, "src-tauri", "fluxion.db")


def gen_id():
    """Generate a hex ID matching Rust's lower(hex(randomblob(16)))."""
    return uuid.uuid4().hex


# ========================================================================
# FULL SCHEMA (from all 35 migrations)
# ========================================================================

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- 001: Core tables
CREATE TABLE IF NOT EXISTS clienti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT,
    telefono TEXT NOT NULL,
    data_nascita TEXT,
    indirizzo TEXT,
    cap TEXT,
    citta TEXT,
    provincia TEXT,
    codice_fiscale TEXT,
    partita_iva TEXT,
    codice_sdi TEXT DEFAULT '0000000',
    pec TEXT,
    note TEXT,
    tags TEXT,
    fonte TEXT,
    consenso_marketing INTEGER DEFAULT 0,
    consenso_whatsapp INTEGER DEFAULT 0,
    data_consenso TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT,
    -- 005: loyalty
    loyalty_visits INTEGER DEFAULT 0,
    loyalty_threshold INTEGER DEFAULT 10,
    is_vip INTEGER DEFAULT 0,
    referral_source TEXT,
    referral_cliente_id TEXT,
    -- 008: soprannome
    soprannome TEXT
);
CREATE INDEX IF NOT EXISTS idx_clienti_telefono ON clienti(telefono);
CREATE INDEX IF NOT EXISTS idx_clienti_email ON clienti(email);
CREATE INDEX IF NOT EXISTS idx_clienti_nome ON clienti(nome, cognome);
CREATE INDEX IF NOT EXISTS idx_clienti_soprannome ON clienti(soprannome);
CREATE INDEX IF NOT EXISTS idx_clienti_is_vip ON clienti(is_vip);

CREATE TABLE IF NOT EXISTS servizi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    descrizione TEXT,
    categoria TEXT,
    prezzo REAL NOT NULL,
    iva_percentuale REAL DEFAULT 22.0,
    durata_minuti INTEGER NOT NULL,
    buffer_minuti INTEGER DEFAULT 0,
    colore TEXT DEFAULT '#22D3EE',
    icona TEXT,
    attivo INTEGER DEFAULT 1,
    ordine INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS operatori (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    ruolo TEXT DEFAULT 'operatore',
    colore TEXT DEFAULT '#C084FC',
    avatar_url TEXT,
    attivo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    -- 012: voice agent
    specializzazioni TEXT DEFAULT '[]',
    descrizione_positiva TEXT,
    anni_esperienza INTEGER DEFAULT 0,
    -- 033: genere
    genere TEXT
);

CREATE TABLE IF NOT EXISTS operatori_servizi (
    operatore_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    priorita INTEGER DEFAULT 0,
    PRIMARY KEY (operatore_id, servizio_id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appuntamenti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    operatore_id TEXT,
    data_ora_inizio TEXT NOT NULL,
    data_ora_fine TEXT NOT NULL,
    durata_minuti INTEGER NOT NULL,
    stato TEXT DEFAULT 'Confermato',
    prezzo REAL NOT NULL,
    sconto_percentuale REAL DEFAULT 0,
    prezzo_finale REAL NOT NULL,
    note TEXT,
    note_interne TEXT,
    fonte_prenotazione TEXT DEFAULT 'manuale',
    reminder_inviato INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    override_info TEXT,
    deleted_at TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (servizio_id) REFERENCES servizi(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);
CREATE INDEX IF NOT EXISTS idx_appuntamenti_data ON appuntamenti(data_ora_inizio);
CREATE INDEX IF NOT EXISTS idx_appuntamenti_cliente ON appuntamenti(cliente_id);
CREATE INDEX IF NOT EXISTS idx_appuntamenti_stato ON appuntamenti(stato);

CREATE TABLE IF NOT EXISTS messaggi_whatsapp (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT,
    telefono TEXT NOT NULL,
    direzione TEXT NOT NULL,
    tipo TEXT DEFAULT 'text',
    contenuto TEXT NOT NULL,
    stato TEXT DEFAULT 'pending',
    errore TEXT,
    template_id TEXT,
    data_invio TEXT DEFAULT (datetime('now')),
    data_consegna TEXT,
    data_lettura TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);

CREATE TABLE IF NOT EXISTS chiamate_voice (
    id TEXT PRIMARY KEY,
    telefono TEXT NOT NULL,
    cliente_id TEXT REFERENCES clienti(id),
    direzione TEXT NOT NULL CHECK(direzione IN ('inbound', 'outbound')),
    durata_secondi INTEGER DEFAULT 0,
    trascrizione TEXT,
    intent_rilevato TEXT,
    esito TEXT CHECK(esito IN ('completata', 'abbandonata', 'errore', 'trasferita')),
    appuntamento_creato_id TEXT REFERENCES appuntamenti(id),
    sentiment TEXT CHECK(sentiment IN ('positivo', 'neutro', 'negativo')),
    note TEXT,
    data_inizio TEXT NOT NULL,
    data_fine TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS impostazioni (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    tipo TEXT DEFAULT 'string',
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 002: WhatsApp templates
CREATE TABLE IF NOT EXISTS whatsapp_templates (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    descrizione TEXT,
    template_text TEXT NOT NULL,
    variabili TEXT,
    predefinito INTEGER DEFAULT 0,
    attivo INTEGER DEFAULT 1,
    uso_count INTEGER DEFAULT 0,
    ultimo_uso TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 003: orari + festivi
CREATE TABLE IF NOT EXISTS orari_lavoro (
    id TEXT PRIMARY KEY,
    giorno_settimana INTEGER NOT NULL CHECK(giorno_settimana BETWEEN 0 AND 6),
    ora_inizio TEXT NOT NULL,
    ora_fine TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('lavoro', 'pausa')),
    operatore_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_orari_lavoro_giorno ON orari_lavoro(giorno_settimana);

CREATE TABLE IF NOT EXISTS giorni_festivi (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL UNIQUE,
    descrizione TEXT NOT NULL,
    ricorrente INTEGER DEFAULT 0 CHECK(ricorrente IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 005: loyalty / pacchetti / waitlist
CREATE TABLE IF NOT EXISTS pacchetti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    descrizione TEXT,
    prezzo REAL NOT NULL,
    prezzo_originale REAL,
    servizi_inclusi INTEGER NOT NULL,
    servizio_tipo_id TEXT,
    validita_giorni INTEGER DEFAULT 365,
    attivo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (servizio_tipo_id) REFERENCES servizi(id)
);

CREATE TABLE IF NOT EXISTS clienti_pacchetti (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL,
    pacchetto_id TEXT NOT NULL,
    stato TEXT NOT NULL DEFAULT 'proposto',
    servizi_usati INTEGER DEFAULT 0,
    servizi_totali INTEGER NOT NULL,
    data_proposta TEXT DEFAULT (datetime('now')),
    data_acquisto TEXT,
    data_scadenza TEXT,
    metodo_pagamento TEXT,
    pagato INTEGER DEFAULT 0,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id)
);

CREATE TABLE IF NOT EXISTS waitlist (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clienti(id),
    servizio TEXT NOT NULL,
    data_preferita TEXT,
    ora_preferita TEXT,
    operatore_preferito TEXT REFERENCES operatori(id),
    priorita TEXT DEFAULT 'normale',
    stato TEXT DEFAULT 'attivo',
    note TEXT,
    creato_il TEXT DEFAULT (datetime('now')),
    notificato_il TEXT,
    scadenza_risposta TEXT
);

-- 006: pacchetto_servizi
CREATE TABLE IF NOT EXISTS pacchetto_servizi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    pacchetto_id TEXT NOT NULL,
    servizio_id TEXT NOT NULL,
    quantita INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id) ON DELETE CASCADE,
    FOREIGN KEY (servizio_id) REFERENCES servizi(id) ON DELETE CASCADE
);

-- 007: fatturazione
CREATE TABLE IF NOT EXISTS impostazioni_fatturazione (
    id TEXT PRIMARY KEY DEFAULT 'default',
    denominazione TEXT NOT NULL DEFAULT '',
    partita_iva TEXT NOT NULL DEFAULT '',
    codice_fiscale TEXT,
    regime_fiscale TEXT NOT NULL DEFAULT 'RF19',
    indirizzo TEXT NOT NULL DEFAULT '',
    cap TEXT NOT NULL DEFAULT '',
    comune TEXT NOT NULL DEFAULT '',
    provincia TEXT NOT NULL DEFAULT '',
    nazione TEXT DEFAULT 'IT',
    telefono TEXT,
    email TEXT,
    pec TEXT,
    prefisso_numerazione TEXT DEFAULT '',
    ultimo_numero INTEGER DEFAULT 0,
    anno_corrente INTEGER DEFAULT 2026,
    aliquota_iva_default REAL DEFAULT 22.0,
    natura_iva_default TEXT,
    iban TEXT,
    bic TEXT,
    nome_banca TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    fattura24_api_key TEXT,
    sdi_provider TEXT NOT NULL DEFAULT 'fattura24',
    aruba_api_key TEXT,
    openapi_api_key TEXT
);

CREATE TABLE IF NOT EXISTS fatture (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    numero INTEGER NOT NULL,
    anno INTEGER NOT NULL,
    numero_completo TEXT NOT NULL,
    tipo_documento TEXT NOT NULL DEFAULT 'TD01',
    data_emissione TEXT NOT NULL,
    data_scadenza TEXT,
    cliente_id TEXT NOT NULL,
    cliente_denominazione TEXT NOT NULL,
    cliente_partita_iva TEXT,
    cliente_codice_fiscale TEXT,
    cliente_indirizzo TEXT,
    cliente_cap TEXT,
    cliente_comune TEXT,
    cliente_provincia TEXT,
    cliente_codice_sdi TEXT DEFAULT '0000000',
    cliente_pec TEXT,
    imponibile REAL NOT NULL DEFAULT 0,
    iva REAL NOT NULL DEFAULT 0,
    totale REAL NOT NULL DEFAULT 0,
    stato TEXT NOT NULL DEFAULT 'bozza',
    metodo_pagamento TEXT DEFAULT 'MP05',
    xml_content TEXT,
    xml_filename TEXT,
    sdi_identificativo TEXT,
    sdi_stato TEXT,
    sdi_data_invio TEXT,
    sdi_data_consegna TEXT,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 008: faq_settings
CREATE TABLE IF NOT EXISTS faq_settings (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    categoria TEXT DEFAULT 'generale',
    descrizione TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 009: cassa/incassi
CREATE TABLE IF NOT EXISTS incassi (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    importo REAL NOT NULL,
    metodo_pagamento TEXT NOT NULL DEFAULT 'contanti',
    cliente_id TEXT,
    appuntamento_id TEXT,
    fattura_id TEXT,
    descrizione TEXT,
    categoria TEXT DEFAULT 'servizio',
    operatore_id TEXT,
    data_incasso TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clienti(id),
    FOREIGN KEY (appuntamento_id) REFERENCES appuntamenti(id),
    FOREIGN KEY (fattura_id) REFERENCES fatture(id),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

CREATE TABLE IF NOT EXISTS chiusure_cassa (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    data_chiusura TEXT NOT NULL,
    totale_contanti REAL DEFAULT 0,
    totale_carte REAL DEFAULT 0,
    totale_satispay REAL DEFAULT 0,
    totale_bonifici REAL DEFAULT 0,
    totale_altro REAL DEFAULT 0,
    totale_giornata REAL DEFAULT 0,
    numero_transazioni INTEGER DEFAULT 0,
    fondo_cassa_iniziale REAL DEFAULT 0,
    fondo_cassa_finale REAL DEFAULT 0,
    note TEXT,
    operatore_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id)
);

-- 011: voice agent
CREATE TABLE IF NOT EXISTS voice_agent_config (
    id TEXT PRIMARY KEY DEFAULT 'default',
    attivo INTEGER DEFAULT 0,
    voce_modello TEXT DEFAULT 'it_IT-paola-medium',
    saluto_personalizzato TEXT,
    orario_attivo_da TEXT DEFAULT '09:00',
    orario_attivo_a TEXT DEFAULT '19:00',
    giorni_attivi TEXT DEFAULT '1,2,3,4,5,6',
    max_chiamate_contemporanee INTEGER DEFAULT 2,
    timeout_risposta_secondi INTEGER DEFAULT 30,
    trasferisci_dopo_tentativi INTEGER DEFAULT 3,
    numero_trasferimento TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    sip_username TEXT,
    sip_password TEXT,
    sip_server TEXT DEFAULT 'sip.ehiweb.it',
    sip_port INTEGER DEFAULT 5060,
    voip_attivo INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS voice_agent_stats (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    chiamate_totali INTEGER DEFAULT 0,
    chiamate_completate INTEGER DEFAULT 0,
    chiamate_abbandonate INTEGER DEFAULT 0,
    appuntamenti_creati INTEGER DEFAULT 0,
    durata_media_secondi REAL DEFAULT 0,
    sentiment_positivo INTEGER DEFAULT 0,
    sentiment_neutro INTEGER DEFAULT 0,
    sentiment_negativo INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 014: voice sessions
CREATE TABLE IF NOT EXISTS voice_sessions (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL DEFAULT 'voice',
    state TEXT NOT NULL DEFAULT 'active',
    verticale_id TEXT NOT NULL DEFAULT '',
    business_name TEXT NOT NULL DEFAULT '',
    caller_number TEXT,
    caller_name TEXT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at TEXT,
    total_turns INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 015: license cache
CREATE TABLE IF NOT EXISTS license_cache (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    license_key TEXT,
    license_id TEXT,
    machine_id TEXT,
    fingerprint TEXT NOT NULL DEFAULT '',
    tier TEXT DEFAULT 'trial',
    status TEXT DEFAULT 'trial',
    trial_started_at TEXT,
    trial_ends_at TEXT,
    expiry_date TEXT,
    last_validated_at TEXT,
    validation_response TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    license_data TEXT,
    license_signature TEXT,
    licensee_name TEXT,
    licensee_email TEXT,
    enabled_verticals TEXT DEFAULT '[]',
    features TEXT DEFAULT '{}',
    issued_at TEXT
);

-- 016: suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(20),
    indirizzo VARCHAR(500),
    citta VARCHAR(100),
    cap VARCHAR(10),
    partita_iva VARCHAR(20) UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(nome)
);

-- 018: audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    user_id TEXT,
    user_type TEXT NOT NULL DEFAULT 'system',
    action TEXT NOT NULL DEFAULT '',
    entity_type TEXT NOT NULL DEFAULT '',
    entity_id TEXT NOT NULL DEFAULT '',
    data_before TEXT,
    data_after TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 022: whatsapp invii
CREATE TABLE IF NOT EXISTS whatsapp_invii (
    id TEXT PRIMARY KEY,
    pacchetto_id TEXT NOT NULL,
    filtro TEXT NOT NULL,
    totale_clienti INTEGER NOT NULL DEFAULT 0,
    inviati INTEGER NOT NULL DEFAULT 0,
    falliti INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id)
);

-- 024: operatori assenze
CREATE TABLE IF NOT EXISTS operatori_assenze (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL,
    data_inizio TEXT NOT NULL,
    data_fine TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'ferie',
    note TEXT,
    approvata INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);

-- 025: operatori commissioni
CREATE TABLE IF NOT EXISTS operatori_commissioni (
    id TEXT PRIMARY KEY,
    operatore_id TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'percentuale_servizio',
    percentuale REAL,
    importo_fisso REAL,
    soglia_fatturato REAL,
    bonus_importo REAL,
    valida_dal TEXT NOT NULL DEFAULT (date('now')),
    valida_al TEXT,
    servizio_id TEXT,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (operatore_id) REFERENCES operatori(id) ON DELETE CASCADE
);

-- 027: schede fitness
CREATE TABLE IF NOT EXISTS schede_fitness (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    obiettivo TEXT,
    livello TEXT,
    frequenza_allenamento TEXT,
    peso_kg REAL,
    altezza_cm REAL,
    percentuale_grasso REAL,
    circonferenza_vita REAL,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 028: schede mediche
CREATE TABLE IF NOT EXISTS schede_mediche (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    motivo_accesso TEXT,
    data_prima_visita TEXT,
    data_ultima_visita TEXT,
    medico_curante TEXT,
    inviato_da TEXT,
    gruppo_sanguigno TEXT,
    peso_kg REAL,
    altezza_cm REAL,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 030: cliente media
CREATE TABLE IF NOT EXISTS cliente_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    media_path TEXT NOT NULL,
    thumb_path TEXT,
    tipo TEXT NOT NULL DEFAULT 'foto',
    categoria TEXT NOT NULL DEFAULT 'generale',
    appuntamento_id TEXT REFERENCES appuntamenti(id),
    operatore_id TEXT REFERENCES operatori(id),
    dimensione_bytes INTEGER,
    larghezza_px INTEGER,
    altezza_px INTEGER,
    durata_sec INTEGER,
    consenso_gdpr INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 031: listini fornitori
CREATE TABLE IF NOT EXISTS listini_fornitori (
    id TEXT PRIMARY KEY,
    fornitore_id TEXT NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    nome_listino TEXT NOT NULL,
    data_import TEXT NOT NULL DEFAULT (datetime('now')),
    data_validita TEXT,
    formato_fonte TEXT NOT NULL DEFAULT 'csv',
    righe_totali INTEGER NOT NULL DEFAULT 0,
    righe_inserite INTEGER NOT NULL DEFAULT 0,
    righe_aggiornate INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 034: blocchi orario
CREATE TABLE IF NOT EXISTS blocchi_orario (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL REFERENCES operatori(id) ON DELETE CASCADE,
    giorno_settimana INTEGER,
    data_specifica TEXT,
    ora_inizio TEXT NOT NULL,
    ora_fine TEXT NOT NULL,
    motivo TEXT DEFAULT 'pausa',
    ricorrente INTEGER DEFAULT 1,
    attivo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 035: schede pet
CREATE TABLE IF NOT EXISTS schede_pet (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    cliente_id TEXT NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
    nome_animale TEXT NOT NULL DEFAULT '',
    specie TEXT NOT NULL DEFAULT 'cane',
    razza TEXT DEFAULT '',
    colore_mantello TEXT DEFAULT '',
    data_nascita TEXT DEFAULT '',
    peso_kg REAL DEFAULT NULL,
    sesso TEXT DEFAULT '',
    microchip TEXT DEFAULT '',
    vaccinazioni TEXT DEFAULT '[]',
    allergie TEXT DEFAULT '[]',
    note TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
"""


# ========================================================================
# FESTIVITY SEED (shared across all verticals)
# ========================================================================

FESTIVITA_2026 = [
    ("fest_2026_0101", "2026-01-01", "Capodanno", 1),
    ("fest_2026_0106", "2026-01-06", "Epifania", 1),
    ("fest_2026_pasqua", "2026-04-05", "Pasqua", 0),
    ("fest_2026_pasquetta", "2026-04-06", "Lunedi dell'Angelo", 0),
    ("fest_2026_0425", "2026-04-25", "Festa della Liberazione", 1),
    ("fest_2026_0501", "2026-05-01", "Festa dei Lavoratori", 1),
    ("fest_2026_0602", "2026-06-02", "Festa della Repubblica", 1),
    ("fest_2026_0815", "2026-08-15", "Ferragosto", 1),
    ("fest_2026_1101", "2026-11-01", "Tutti i Santi", 1),
    ("fest_2026_1208", "2026-12-08", "Immacolata Concezione", 1),
    ("fest_2026_1225", "2026-12-25", "Natale", 1),
    ("fest_2026_1226", "2026-12-26", "Santo Stefano", 1),
]


# ========================================================================
# VERTICAL DATA DEFINITIONS
# ========================================================================

VERTICALS = {
    "salone": {
        "impostazioni": {
            "nome_attivita": "Salone Bellissima",
            "macro_categoria": "hair",
            "micro_categoria": "salone",
            "indirizzo": "Via Roma 42, 20121 Milano (MI)",
            "telefono": "02 1234567",
            "email": "info@salonebellissima.it",
        },
        "servizi": [
            ("Taglio uomo", "Taglio classico maschile con lavaggio", "Taglio", 18.0, 30, "#3B82F6", 0),
            ("Taglio donna", "Taglio femminile con lavaggio e asciugatura", "Taglio", 25.0, 45, "#EC4899", 1),
            ("Piega", "Piega con lavaggio", "Piega", 20.0, 30, "#8B5CF6", 2),
            ("Colore", "Colorazione completa con lavaggio e piega", "Colore", 45.0, 90, "#F59E0B", 3),
            ("Meches", "Meches con stagnola e piega finale", "Colore", 60.0, 120, "#F97316", 4),
            ("Barba", "Regolazione e rifinitura barba", "Barba", 12.0, 20, "#6366F1", 5),
            ("Trattamento cheratina", "Trattamento lisciante alla cheratina", "Trattamento", 80.0, 60, "#14B8A6", 6),
            ("Extension", "Applicazione extension capelli naturali", "Extension", 120.0, 180, "#D946EF", 7),
        ],
        "operatori": [
            ("Marco", "Bianchi", "marco@salonebellissima.it", "333 1111111", "stilista", "#3B82F6", '["taglio uomo","taglio donna","piega","barba"]', "Stilista senior con 15 anni di esperienza", 15, "M"),
            ("Elena", "Rossi", "elena@salonebellissima.it", "333 2222222", "operatore", "#EC4899", '["colore","meches","piega","taglio donna","trattamento cheratina","extension"]', "Colorista esperta specializzata in balayage e meches", 10, "F"),
            ("Giada", "Conti", "giada@salonebellissima.it", "333 3333333", "operatore", "#8B5CF6", '["taglio donna","piega","barba","taglio uomo"]', "Assistente stilista, bravissima con le pieghe", 3, "F"),
        ],
        # (giorno_settimana: 0=dom, 1=lun, 2=mar, ..., 6=sab)
        # Mar-Sab 9:00-13:00, 14:00-19:00
        "orari": [
            # Martedi (2)
            (2, "09:00", "13:00", "lavoro"),
            (2, "13:00", "14:00", "pausa"),
            (2, "14:00", "19:00", "lavoro"),
            # Mercoledi (3)
            (3, "09:00", "13:00", "lavoro"),
            (3, "13:00", "14:00", "pausa"),
            (3, "14:00", "19:00", "lavoro"),
            # Giovedi (4)
            (4, "09:00", "13:00", "lavoro"),
            (4, "13:00", "14:00", "pausa"),
            (4, "14:00", "19:00", "lavoro"),
            # Venerdi (5)
            (5, "09:00", "13:00", "lavoro"),
            (5, "13:00", "14:00", "pausa"),
            (5, "14:00", "19:00", "lavoro"),
            # Sabato (6)
            (6, "09:00", "13:00", "lavoro"),
            (6, "13:00", "14:00", "pausa"),
            (6, "14:00", "19:00", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Martedi - Sabato",
            "orario_mattina": "9:00",
            "orario_pomeriggio": "19:00",
            "giorni_chiusura": "Domenica e Lunedi",
            "tempo_ultimo_appuntamento": "30",
            "metodi_pagamento": "Contanti, Carte, Satispay",
            "info_parcheggio": "Parcheggio gratuito davanti al salone",
            "numero_telefono": "02 1234567",
            "indirizzo_salone": "Via Roma 42, 20121 Milano",
        },
        "clienti": [
            ("Maria", "Verdi", "3391234567", "maria.verdi@email.it", "1985-03-15", "Cliente fidelizzata, preferisce Elena per il colore"),
            ("Luca", "Ferrara", "3387654321", "luca.ferrara@email.it", "1990-07-22", "Taglio ogni 3 settimane"),
            ("Anna", "Colombo", "3401122334", "anna.colombo@email.it", "1978-11-30", "Allergia a prodotti con ammoniaca"),
            ("Giuseppe", "Esposito", "3339988776", "giuseppe.esposito@email.it", "1995-01-10", "Barba e taglio sempre insieme"),
            ("Francesca", "Romano", "3476655443", "francesca.romano@email.it", "1982-06-25", "VIP - trattamento cheratina ogni 3 mesi"),
        ],
    },

    "barbiere": {
        "impostazioni": {
            "nome_attivita": "Barbiere da Tony",
            "macro_categoria": "hair",
            "micro_categoria": "barbiere",
            "indirizzo": "Corso Italia 15, 80138 Napoli (NA)",
            "telefono": "081 9876543",
            "email": "info@barbieretony.it",
        },
        "servizi": [
            ("Taglio uomo", "Taglio classico maschile", "Taglio", 15.0, 25, "#3B82F6", 0),
            ("Taglio e barba", "Taglio capelli + regolazione barba completa", "Taglio", 22.0, 40, "#6366F1", 1),
            ("Rasatura", "Rasatura completa con panno caldo", "Barba", 10.0, 15, "#14B8A6", 2),
            ("Barba stilizzata", "Modellatura barba con rasoio e forbici", "Barba", 18.0, 30, "#F59E0B", 3),
            ("Shampoo e massaggio", "Shampoo rilassante con massaggio cuoio capelluto", "Trattamento", 12.0, 15, "#8B5CF6", 4),
            ("Colorazione uomo", "Colorazione tono su tono per uomo", "Colore", 30.0, 45, "#EC4899", 5),
        ],
        "operatori": [
            ("Tony", "Napolitano", "tony@barbieretony.it", "333 4444444", "admin", "#3B82F6", '["taglio uomo","taglio e barba","rasatura","barba stilizzata","shampoo e massaggio","colorazione uomo"]', "Master barber con 20 anni di esperienza, specialista rasatura tradizionale", 20, "M"),
            ("Sandro", "De Luca", "sandro@barbieretony.it", "333 5555555", "operatore", "#14B8A6", '["taglio uomo","taglio e barba","rasatura","barba stilizzata","shampoo e massaggio"]', "Barber giovane e creativo, esperto in tagli moderni", 5, "M"),
        ],
        # Lun-Sab 8:30-12:30, 14:00-19:30
        "orari": [
            # Lunedi (1)
            (1, "08:30", "12:30", "lavoro"),
            (1, "12:30", "14:00", "pausa"),
            (1, "14:00", "19:30", "lavoro"),
            # Martedi (2)
            (2, "08:30", "12:30", "lavoro"),
            (2, "12:30", "14:00", "pausa"),
            (2, "14:00", "19:30", "lavoro"),
            # Mercoledi (3)
            (3, "08:30", "12:30", "lavoro"),
            (3, "12:30", "14:00", "pausa"),
            (3, "14:00", "19:30", "lavoro"),
            # Giovedi (4)
            (4, "08:30", "12:30", "lavoro"),
            (4, "12:30", "14:00", "pausa"),
            (4, "14:00", "19:30", "lavoro"),
            # Venerdi (5)
            (5, "08:30", "12:30", "lavoro"),
            (5, "12:30", "14:00", "pausa"),
            (5, "14:00", "19:30", "lavoro"),
            # Sabato (6)
            (6, "08:30", "12:30", "lavoro"),
            (6, "12:30", "14:00", "pausa"),
            (6, "14:00", "19:30", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Sabato",
            "orario_mattina": "8:30",
            "orario_pomeriggio": "19:30",
            "giorni_chiusura": "Domenica",
            "tempo_ultimo_appuntamento": "25",
            "metodi_pagamento": "Contanti, Carte",
            "info_parcheggio": "Strisce blu a 30 metri",
            "numero_telefono": "081 9876543",
            "indirizzo_salone": "Corso Italia 15, Napoli",
        },
        "clienti": [
            ("Marco", "Russo", "3391112233", "marco.russo@email.it", "1988-04-12", "Taglio classico ogni 2 settimane"),
            ("Antonio", "Gallo", "3384455667", "antonio.gallo@email.it", "1975-09-08", "Barba stilizzata, cliente storico"),
            ("Vincenzo", "Marino", "3407788990", "vincenzo.marino@email.it", "1992-12-03", "Preferisce Tony"),
            ("Roberto", "Caruso", "3336677889", "roberto.caruso@email.it", "1980-02-28", "Colorazione ogni 5 settimane"),
            ("Salvatore", "Giordano", "3479900112", "salvatore.giordano@email.it", "1998-08-17", "Taglio e barba sempre insieme"),
        ],
    },

    "beauty": {
        "impostazioni": {
            "nome_attivita": "Centro Estetico Aurora",
            "macro_categoria": "beauty",
            "micro_categoria": "centro_estetico",
            "indirizzo": "Via Garibaldi 88, 10122 Torino (TO)",
            "telefono": "011 5554433",
            "email": "info@centroaurora.it",
        },
        "servizi": [
            ("Pulizia viso", "Pulizia viso profonda con vapore e maschera", "Viso", 50.0, 60, "#EC4899", 0),
            ("Trattamento anti-age", "Trattamento anti-eta con acido ialuronico", "Viso", 80.0, 90, "#D946EF", 1),
            ("Massaggio rilassante", "Massaggio corpo rilassante con oli essenziali", "Corpo", 60.0, 60, "#8B5CF6", 2),
            ("Ceretta gambe", "Ceretta gambe intere con cera a caldo", "Epilazione", 30.0, 30, "#F59E0B", 3),
            ("Manicure", "Manicure completa con smalto", "Mani e Piedi", 25.0, 45, "#F97316", 4),
            ("Pedicure", "Pedicure estetica con trattamento piedi", "Mani e Piedi", 30.0, 45, "#14B8A6", 5),
            ("Epilazione laser", "Epilazione laser diodo zona a scelta", "Epilazione", 90.0, 30, "#EF4444", 6),
            ("Trattamento corpo", "Trattamento corpo rassodante e drenante", "Corpo", 70.0, 90, "#6366F1", 7),
        ],
        "operatori": [
            ("Francesca", "Moretti", "francesca@centroaurora.it", "333 6666666", "admin", "#EC4899", '["pulizia viso","trattamento anti-age","epilazione laser","ceretta gambe","trattamento corpo"]', "Estetista senior con 12 anni di esperienza, specializzata in trattamenti viso", 12, "F"),
            ("Laura", "Fontana", "laura@centroaurora.it", "333 7777777", "operatore", "#F97316", '["manicure","pedicure","ceretta gambe"]', "Nail artist creativa, specializzata in ricostruzione unghie", 6, "F"),
            ("Sara", "Marchetti", "sara@centroaurora.it", "333 8888888", "operatore", "#8B5CF6", '["massaggio rilassante","trattamento corpo","trattamento anti-age"]', "Massaggiatrice certificata, esperta in tecniche orientali", 8, "F"),
        ],
        # Lun-Ven 9:00-13:00, 14:30-19:30; Sab 9:00-13:00
        "orari": [
            (1, "09:00", "13:00", "lavoro"), (1, "13:00", "14:30", "pausa"), (1, "14:30", "19:30", "lavoro"),
            (2, "09:00", "13:00", "lavoro"), (2, "13:00", "14:30", "pausa"), (2, "14:30", "19:30", "lavoro"),
            (3, "09:00", "13:00", "lavoro"), (3, "13:00", "14:30", "pausa"), (3, "14:30", "19:30", "lavoro"),
            (4, "09:00", "13:00", "lavoro"), (4, "13:00", "14:30", "pausa"), (4, "14:30", "19:30", "lavoro"),
            (5, "09:00", "13:00", "lavoro"), (5, "13:00", "14:30", "pausa"), (5, "14:30", "19:30", "lavoro"),
            (6, "09:00", "13:00", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Sabato",
            "orario_mattina": "9:00",
            "orario_pomeriggio": "19:30",
            "giorni_chiusura": "Domenica",
            "tempo_ultimo_appuntamento": "45",
            "metodi_pagamento": "Contanti, Carte, Satispay, Bonifico",
            "info_parcheggio": "Parcheggio convenzionato a 50 metri",
            "numero_telefono": "011 5554433",
            "indirizzo_salone": "Via Garibaldi 88, Torino",
        },
        "clienti": [
            ("Giulia", "Rinaldi", "3391234000", "giulia.rinaldi@email.it", "1983-05-20", "Pulizia viso mensile + massaggio"),
            ("Valentina", "Costa", "3387654000", "valentina.costa@email.it", "1991-09-14", "Epilazione laser ciclo completo"),
            ("Chiara", "Ricci", "3401122000", "chiara.ricci@email.it", "1986-01-07", "Manicure settimanale, cliente VIP"),
            ("Simona", "Gatti", "3339988000", "simona.gatti@email.it", "1979-11-22", "Trattamento anti-age ogni 2 settimane"),
            ("Paola", "Lombardi", "3476655000", "paola.lombardi@email.it", "1994-03-18", "Ceretta e pedicure ogni mese"),
        ],
    },

    "fisioterapia": {
        "impostazioni": {
            "nome_attivita": "Centro Fisioterapia Salute",
            "macro_categoria": "medico",
            "micro_categoria": "fisioterapia",
            "indirizzo": "Via della Salute 12, 40136 Bologna (BO)",
            "telefono": "051 3344556",
            "email": "info@fisioterapiasalute.it",
        },
        "servizi": [
            ("Prima visita", "Prima visita fisioterapica con valutazione", "Visite", 60.0, 45, "#3B82F6", 0),
            ("Seduta fisioterapia", "Seduta standard di fisioterapia", "Terapia", 50.0, 45, "#14B8A6", 1),
            ("Massoterapia", "Massaggio terapeutico decontratturante", "Terapia", 45.0, 30, "#8B5CF6", 2),
            ("Rieducazione posturale", "Ginnastica posturale individuale", "Riabilitazione", 55.0, 60, "#F59E0B", 3),
            ("Terapia manuale", "Terapia manuale osteopatica", "Terapia", 50.0, 45, "#EC4899", 4),
            ("Elettroterapia", "Trattamento con elettrostimolazione", "Strumentale", 35.0, 30, "#6366F1", 5),
            ("Ultrasuoni", "Terapia a ultrasuoni per infiammazioni", "Strumentale", 30.0, 20, "#F97316", 6),
            ("Riabilitazione post-operatoria", "Programma riabilitativo post-chirurgico", "Riabilitazione", 60.0, 60, "#EF4444", 7),
        ],
        "operatori": [
            ("Dott.", "Bianchi", "bianchi@fisioterapiasalute.it", "333 9999111", "admin", "#3B82F6", '["prima visita","seduta fisioterapia","terapia manuale","rieducazione posturale","riabilitazione post-operatoria"]', "Fisioterapista con 18 anni di esperienza, specializzato in riabilitazione sportiva", 18, "M"),
            ("Dott.ssa", "Verdi", "verdi@fisioterapiasalute.it", "333 9999222", "operatore", "#EC4899", '["prima visita","terapia manuale","rieducazione posturale","seduta fisioterapia"]', "Osteopata certificata, specializzata in posturologia", 10, "F"),
            ("Matteo", "Greco", "matteo@fisioterapiasalute.it", "333 9999333", "operatore", "#14B8A6", '["massoterapia","elettroterapia","ultrasuoni","seduta fisioterapia"]', "Massoterapista qualificato con competenze in terapia strumentale", 6, "M"),
        ],
        # Lun-Ven 8:00-13:00, 14:00-19:00
        "orari": [
            (1, "08:00", "13:00", "lavoro"), (1, "13:00", "14:00", "pausa"), (1, "14:00", "19:00", "lavoro"),
            (2, "08:00", "13:00", "lavoro"), (2, "13:00", "14:00", "pausa"), (2, "14:00", "19:00", "lavoro"),
            (3, "08:00", "13:00", "lavoro"), (3, "13:00", "14:00", "pausa"), (3, "14:00", "19:00", "lavoro"),
            (4, "08:00", "13:00", "lavoro"), (4, "13:00", "14:00", "pausa"), (4, "14:00", "19:00", "lavoro"),
            (5, "08:00", "13:00", "lavoro"), (5, "13:00", "14:00", "pausa"), (5, "14:00", "19:00", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Venerdi",
            "orario_mattina": "8:00",
            "orario_pomeriggio": "19:00",
            "giorni_chiusura": "Sabato e Domenica",
            "tempo_ultimo_appuntamento": "45",
            "metodi_pagamento": "Contanti, Carte, Bonifico",
            "info_parcheggio": "Parcheggio riservato nel cortile interno",
            "numero_telefono": "051 3344556",
            "indirizzo_salone": "Via della Salute 12, Bologna",
        },
        "clienti": [
            ("Paolo", "Santini", "3391234111", "paolo.santini@email.it", "1970-08-15", "Cervicale cronica, sedute settimanali"),
            ("Marta", "Benedetti", "3387654111", "marta.benedetti@email.it", "1985-04-22", "Riabilitazione ginocchio post-intervento"),
            ("Giovanni", "Fabbri", "3401122111", "giovanni.fabbri@email.it", "1965-12-01", "Lombosciatalgia, terapia manuale"),
            ("Teresa", "Martini", "3339988111", "teresa.martini@email.it", "1992-06-30", "Rieducazione posturale, lavoro ufficio"),
            ("Andrea", "Pellegrini", "3476655111", "andrea.pellegrini@email.it", "1988-02-14", "Sportivo, massoterapia regolare"),
        ],
    },

    "gommista": {
        "impostazioni": {
            "nome_attivita": "Gomme Express di Paolo",
            "macro_categoria": "auto",
            "micro_categoria": "gommista",
            "indirizzo": "Via dell'Industria 5, 00071 Pomezia (RM)",
            "telefono": "06 9112233",
            "email": "info@gommeexpress.it",
        },
        "servizi": [
            ("Cambio gomme stagionale", "Sostituzione 4 gomme invernali/estive", "Pneumatici", 40.0, 60, "#3B82F6", 0),
            ("Equilibratura", "Equilibratura 4 ruote", "Manutenzione", 20.0, 30, "#14B8A6", 1),
            ("Convergenza", "Regolazione convergenza assetto ruote", "Manutenzione", 35.0, 45, "#F59E0B", 2),
            ("Riparazione foratura", "Riparazione pneumatico forato", "Riparazione", 15.0, 20, "#EF4444", 3),
            ("Deposito stagionale", "Deposito 4 gomme con custodia", "Deposito", 40.0, 10, "#8B5CF6", 4),
            ("Controllo pressione", "Controllo e regolazione pressione gomme", "Controllo", 0.0, 10, "#6366F1", 5),
            ("Sostituzione valvole", "Sostituzione valvole pneumatici", "Riparazione", 10.0, 15, "#F97316", 6),
            ("TPMS reset", "Reset sensori pressione pneumatici", "Elettronica", 25.0, 20, "#D946EF", 7),
        ],
        "operatori": [
            ("Paolo", "Marini", "paolo@gommeexpress.it", "333 1010101", "admin", "#3B82F6", '["cambio gomme stagionale","equilibratura","convergenza","riparazione foratura","deposito stagionale","controllo pressione","sostituzione valvole","tpms reset"]', "Titolare con 25 anni di esperienza, esperto in tutte le marche", 25, "M"),
            ("Marco", "Testa", "marco@gommeexpress.it", "333 2020202", "operatore", "#14B8A6", '["cambio gomme stagionale","equilibratura","riparazione foratura","controllo pressione","sostituzione valvole"]', "Tecnico specializzato in pneumatici sportivi e SUV", 8, "M"),
        ],
        # Lun-Ven 8:00-12:30, 14:00-18:30; Sab 8:00-12:30
        "orari": [
            (1, "08:00", "12:30", "lavoro"), (1, "12:30", "14:00", "pausa"), (1, "14:00", "18:30", "lavoro"),
            (2, "08:00", "12:30", "lavoro"), (2, "12:30", "14:00", "pausa"), (2, "14:00", "18:30", "lavoro"),
            (3, "08:00", "12:30", "lavoro"), (3, "12:30", "14:00", "pausa"), (3, "14:00", "18:30", "lavoro"),
            (4, "08:00", "12:30", "lavoro"), (4, "12:30", "14:00", "pausa"), (4, "14:00", "18:30", "lavoro"),
            (5, "08:00", "12:30", "lavoro"), (5, "12:30", "14:00", "pausa"), (5, "14:00", "18:30", "lavoro"),
            (6, "08:00", "12:30", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Sabato",
            "orario_mattina": "8:00",
            "orario_pomeriggio": "18:30",
            "giorni_chiusura": "Domenica",
            "tempo_ultimo_appuntamento": "60",
            "metodi_pagamento": "Contanti, Carte, Bonifico",
            "info_parcheggio": "Ampio piazzale con parcheggio gratuito",
            "numero_telefono": "06 9112233",
            "indirizzo_salone": "Via dell'Industria 5, Pomezia (RM)",
        },
        "clienti": [
            ("Stefano", "Rizzo", "3391234222", "stefano.rizzo@email.it", "1976-03-10", "Cambio gomme ogni stagione, BMW Serie 3"),
            ("Alessandro", "Conti", "3387654222", "alessandro.conti@email.it", "1983-11-25", "Deposito stagionale incluso"),
            ("Massimo", "Marchetti", "3401122222", "massimo.marchetti@email.it", "1990-07-18", "Furgone aziendale, equilibratura frequente"),
            ("Fabio", "Orlando", "3339988222", "fabio.orlando@email.it", "1968-09-05", "Cliente storico, auto d'epoca"),
            ("Claudio", "Serra", "3476655222", "claudio.serra@email.it", "1995-01-30", "Gomme sportive, TPMS reset frequente"),
        ],
    },

    "toelettatura": {
        "impostazioni": {
            "nome_attivita": "Zampe Felici Toelettatura",
            "macro_categoria": "pet",
            "micro_categoria": "toelettatura",
            "indirizzo": "Via dei Fiori 22, 50132 Firenze (FI)",
            "telefono": "055 7788990",
            "email": "info@zampefelici.it",
        },
        "servizi": [
            ("Bagno taglia piccola", "Bagno completo per cani fino a 10kg", "Bagno", 25.0, 45, "#3B82F6", 0),
            ("Bagno taglia media", "Bagno completo per cani 10-25kg", "Bagno", 35.0, 60, "#14B8A6", 1),
            ("Bagno taglia grande", "Bagno completo per cani oltre 25kg", "Bagno", 45.0, 75, "#6366F1", 2),
            ("Tosatura completa", "Tosatura con macchina e rifinitura", "Toelettatura", 40.0, 60, "#F59E0B", 3),
            ("Taglio forbici", "Taglio di precisione con forbici professionali", "Toelettatura", 50.0, 90, "#EC4899", 4),
            ("Stripping", "Stripping manuale per razze a pelo duro", "Toelettatura", 55.0, 90, "#D946EF", 5),
            ("Trattamento antiparassitario", "Bagno antiparassitario con prodotti specifici", "Trattamento", 20.0, 15, "#EF4444", 6),
            ("Pulizia orecchie", "Pulizia e igienizzazione orecchie", "Igiene", 10.0, 10, "#F97316", 7),
        ],
        "operatori": [
            ("Valentina", "Bernardi", "valentina@zampefelici.it", "333 3030303", "admin", "#EC4899", '["bagno taglia piccola","bagno taglia media","bagno taglia grande","tosatura completa","taglio forbici","stripping","trattamento antiparassitario","pulizia orecchie"]', "Toelettatrice senior certificata ANCF, 10 anni di esperienza", 10, "F"),
            ("Chiara", "Pellegrini", "chiara@zampefelici.it", "333 4040404", "operatore", "#14B8A6", '["bagno taglia piccola","bagno taglia media","bagno taglia grande","tosatura completa","trattamento antiparassitario","pulizia orecchie"]', "Toelettatrice specializzata in razze a pelo lungo", 4, "F"),
        ],
        # Lun-Sab 9:00-13:00, 14:30-18:30
        "orari": [
            (1, "09:00", "13:00", "lavoro"), (1, "13:00", "14:30", "pausa"), (1, "14:30", "18:30", "lavoro"),
            (2, "09:00", "13:00", "lavoro"), (2, "13:00", "14:30", "pausa"), (2, "14:30", "18:30", "lavoro"),
            (3, "09:00", "13:00", "lavoro"), (3, "13:00", "14:30", "pausa"), (3, "14:30", "18:30", "lavoro"),
            (4, "09:00", "13:00", "lavoro"), (4, "13:00", "14:30", "pausa"), (4, "14:30", "18:30", "lavoro"),
            (5, "09:00", "13:00", "lavoro"), (5, "13:00", "14:30", "pausa"), (5, "14:30", "18:30", "lavoro"),
            (6, "09:00", "13:00", "lavoro"), (6, "13:00", "14:30", "pausa"), (6, "14:30", "18:30", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Sabato",
            "orario_mattina": "9:00",
            "orario_pomeriggio": "18:30",
            "giorni_chiusura": "Domenica",
            "tempo_ultimo_appuntamento": "60",
            "metodi_pagamento": "Contanti, Carte, Satispay",
            "info_parcheggio": "Parcheggio gratuito davanti al negozio",
            "numero_telefono": "055 7788990",
            "indirizzo_salone": "Via dei Fiori 22, Firenze",
        },
        "clienti": [
            ("Silvia", "Morandi", "3391234333", "silvia.morandi@email.it", "1987-07-12", "Labrador 'Luna', bagno mensile"),
            ("Federico", "Vitale", "3387654333", "federico.vitale@email.it", "1979-02-28", "Barboncino 'Fifi', tosatura ogni 6 settimane"),
            ("Elisa", "Cattaneo", "3401122333", "elisa.cattaneo@email.it", "1993-10-05", "Golden Retriever 'Rex', stripping stagionale"),
            ("Davide", "Santoro", "3339988333", "davide.santoro@email.it", "1985-04-17", "Chihuahua 'Milo', bagno taglia piccola"),
            ("Irene", "Mancini", "3476655333", "irene.mancini@email.it", "1990-12-22", "Pastore Tedesco 'Thor', antiparassitario regolare"),
        ],
    },

    "palestra": {
        "impostazioni": {
            "nome_attivita": "FitZone Palestra",
            "macro_categoria": "wellness",
            "micro_categoria": "palestra",
            "indirizzo": "Viale dello Sport 100, 37138 Verona (VR)",
            "telefono": "045 6677889",
            "email": "info@fitzonepalestra.it",
        },
        "servizi": [
            ("Lezione pilates", "Lezione di pilates matwork in gruppo", "Corso", 15.0, 60, "#EC4899", 0),
            ("Lezione yoga", "Lezione di yoga vinyasa", "Corso", 15.0, 60, "#8B5CF6", 1),
            ("Personal training", "Sessione individuale con personal trainer", "Personal", 40.0, 60, "#3B82F6", 2),
            ("Lezione spinning", "Lezione di indoor cycling ad alta intensita", "Corso", 12.0, 45, "#F59E0B", 3),
            ("Lezione zumba", "Lezione di zumba fitness", "Corso", 10.0, 45, "#14B8A6", 4),
            ("Valutazione fisica", "Test e valutazione composizione corporea", "Valutazione", 30.0, 45, "#6366F1", 5),
            ("Massaggio sportivo", "Massaggio decontratturante post-allenamento", "Benessere", 50.0, 60, "#EF4444", 6),
            ("Lezione crossfit", "Lezione di functional training crossfit", "Corso", 15.0, 60, "#F97316", 7),
        ],
        "operatori": [
            ("Andrea", "Ferrari", "andrea@fitzonepalestra.it", "333 5050505", "admin", "#3B82F6", '["personal training","valutazione fisica","lezione crossfit","lezione spinning"]', "Personal trainer certificato ISSA, 12 anni di esperienza", 12, "M"),
            ("Marta", "Colombo", "marta@fitzonepalestra.it", "333 6060606", "operatore", "#EC4899", '["lezione pilates","lezione yoga","valutazione fisica"]', "Istruttrice yoga e pilates certificata, esperta in postura", 8, "F"),
            ("Luca", "Barbieri", "luca@fitzonepalestra.it", "333 7070707", "operatore", "#F97316", '["lezione crossfit","lezione spinning","lezione zumba","massaggio sportivo"]', "Istruttore CrossFit L2, massaggiatore sportivo", 6, "M"),
        ],
        # Lun-Ven 7:00-13:00, 15:00-22:00; Sab 8:00-13:00
        "orari": [
            (1, "07:00", "13:00", "lavoro"), (1, "13:00", "15:00", "pausa"), (1, "15:00", "22:00", "lavoro"),
            (2, "07:00", "13:00", "lavoro"), (2, "13:00", "15:00", "pausa"), (2, "15:00", "22:00", "lavoro"),
            (3, "07:00", "13:00", "lavoro"), (3, "13:00", "15:00", "pausa"), (3, "15:00", "22:00", "lavoro"),
            (4, "07:00", "13:00", "lavoro"), (4, "13:00", "15:00", "pausa"), (4, "15:00", "22:00", "lavoro"),
            (5, "07:00", "13:00", "lavoro"), (5, "13:00", "15:00", "pausa"), (5, "15:00", "22:00", "lavoro"),
            (6, "08:00", "13:00", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Sabato",
            "orario_mattina": "7:00",
            "orario_pomeriggio": "22:00",
            "giorni_chiusura": "Domenica",
            "tempo_ultimo_appuntamento": "60",
            "metodi_pagamento": "Contanti, Carte, Bonifico, Satispay",
            "info_parcheggio": "Ampio parcheggio gratuito",
            "numero_telefono": "045 6677889",
            "indirizzo_salone": "Viale dello Sport 100, Verona",
        },
        "clienti": [
            ("Matteo", "Rizzo", "3391234444", "matteo.rizzo@email.it", "1991-03-08", "Personal training 3x settimana, obiettivo massa"),
            ("Sara", "Monti", "3387654444", "sara.monti@email.it", "1988-11-15", "Yoga e pilates, 4 lezioni settimana"),
            ("Lorenzo", "Bianchi", "3401122444", "lorenzo.bianchi@email.it", "1996-06-20", "CrossFit appassionato, gare regionali"),
            ("Eleonora", "Neri", "3339988444", "eleonora.neri@email.it", "1984-09-02", "Spinning e zumba, fitness generale"),
            ("Daniele", "Parisi", "3476655444", "daniele.parisi@email.it", "1975-01-25", "Massaggio sportivo post-maratona"),
        ],
    },

    "medical": {
        "impostazioni": {
            "nome_attivita": "Studio Medico Dr. Colombo",
            "macro_categoria": "medico",
            "micro_categoria": "medico_generico",
            "indirizzo": "Piazza della Repubblica 8, 16121 Genova (GE)",
            "telefono": "010 4455667",
            "email": "info@studiocolombo.it",
        },
        "servizi": [
            ("Visita generale", "Visita medica generale con anamnesi", "Visite", 80.0, 30, "#3B82F6", 0),
            ("Visita specialistica", "Visita medica specialistica approfondita", "Visite", 120.0, 45, "#6366F1", 1),
            ("Ecografia", "Ecografia addominale o muscolo-scheletrica", "Diagnostica", 100.0, 30, "#14B8A6", 2),
            ("Elettrocardiogramma", "ECG a riposo con refertazione", "Diagnostica", 50.0, 20, "#F59E0B", 3),
            ("Analisi del sangue", "Prelievo ematico per analisi laboratorio", "Analisi", 30.0, 15, "#EF4444", 4),
            ("Certificato medico", "Certificato medico sportivo o lavorativo", "Certificati", 40.0, 15, "#8B5CF6", 5),
            ("Vaccino", "Somministrazione vaccino con registrazione", "Vaccini", 25.0, 15, "#EC4899", 6),
            ("Medicazione", "Medicazione ferite e post-operatoria", "Procedure", 20.0, 15, "#F97316", 7),
        ],
        "operatori": [
            ("Dr.", "Colombo", "colombo@studiocolombo.it", "333 8080808", "admin", "#3B82F6", '["visita generale","visita specialistica","ecografia","elettrocardiogramma","certificato medico","vaccino"]', "Medico generico con 22 anni di esperienza, specializzato in medicina interna", 22, "M"),
            ("Dott.ssa", "Ferraro", "ferraro@studiocolombo.it", "333 9090909", "operatore", "#EC4899", '["visita specialistica","ecografia","elettrocardiogramma","analisi del sangue"]', "Specialista in cardiologia e diagnostica per immagini", 15, "F"),
            ("Inf.", "Russo", "russo@studiocolombo.it", "333 1212121", "operatore", "#14B8A6", '["analisi del sangue","vaccino","medicazione","elettrocardiogramma"]', "Infermiera professionale con 10 anni di esperienza ospedaliera", 10, "F"),
        ],
        # Lun-Ven 8:30-13:00, 14:30-18:30
        "orari": [
            (1, "08:30", "13:00", "lavoro"), (1, "13:00", "14:30", "pausa"), (1, "14:30", "18:30", "lavoro"),
            (2, "08:30", "13:00", "lavoro"), (2, "13:00", "14:30", "pausa"), (2, "14:30", "18:30", "lavoro"),
            (3, "08:30", "13:00", "lavoro"), (3, "13:00", "14:30", "pausa"), (3, "14:30", "18:30", "lavoro"),
            (4, "08:30", "13:00", "lavoro"), (4, "13:00", "14:30", "pausa"), (4, "14:30", "18:30", "lavoro"),
            (5, "08:30", "13:00", "lavoro"), (5, "13:00", "14:30", "pausa"), (5, "14:30", "18:30", "lavoro"),
        ],
        "faq_settings": {
            "giorni_apertura": "Lunedi - Venerdi",
            "orario_mattina": "8:30",
            "orario_pomeriggio": "18:30",
            "giorni_chiusura": "Sabato e Domenica",
            "tempo_ultimo_appuntamento": "30",
            "metodi_pagamento": "Contanti, Carte, Bonifico",
            "info_parcheggio": "Parcheggio a pagamento in piazza",
            "numero_telefono": "010 4455667",
            "indirizzo_salone": "Piazza della Repubblica 8, Genova",
        },
        "clienti": [
            ("Carlo", "De Angelis", "3391234555", "carlo.deangelis@email.it", "1958-05-10", "Paziente cardiopatico, ECG trimestrale"),
            ("Rosa", "Pagano", "3387654555", "rosa.pagano@email.it", "1972-08-23", "Visite generali periodiche"),
            ("Emanuele", "Vitali", "3401122555", "emanuele.vitali@email.it", "1995-02-14", "Certificato medico sportivo annuale"),
            ("Lucia", "Ferretti", "3339988555", "lucia.ferretti@email.it", "1980-11-07", "Ecografie follow-up, paziente oncologica"),
            ("Alberto", "Zanetti", "3476655555", "alberto.zanetti@email.it", "1963-04-19", "Analisi sangue trimestrali, diabetico"),
        ],
    },
}


# ========================================================================
# DB CREATION FUNCTIONS
# ========================================================================

def create_schema(conn):
    """Create all tables from schema SQL."""
    # Split and execute statements individually to handle errors gracefully
    statements = []
    current = ""
    paren_depth = 0

    for line in SCHEMA_SQL.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue

        paren_depth += line.count("(") - line.count(")")
        current += line + "\n"

        if stripped.endswith(";") and paren_depth <= 0:
            statements.append(current.strip())
            current = ""
            paren_depth = 0

    if current.strip():
        statements.append(current.strip())

    for stmt in statements:
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e):
                print(f"  WARN: {e}")


def insert_default_impostazioni(conn):
    """Insert default impostazioni values."""
    defaults = [
        ("orario_apertura", "09:00", "string"),
        ("orario_chiusura", "19:00", "string"),
        ("giorni_lavorativi", '["lun","mar","mer","gio","ven","sab"]', "json"),
        ("durata_slot_minuti", "30", "number"),
        ("reminder_ore_prima", "24", "number"),
        ("whatsapp_attivo", "true", "boolean"),
        ("voice_agent_attivo", "true", "boolean"),
        ("whatsapp_number", "", "string"),
        ("ehiweb_number", "", "string"),
        ("indirizzo_completo", "", "string"),
        ("sito_web", "", "string"),
        ("groq_api_key", "", "string"),
        ("smtp_host", "smtp.gmail.com", "string"),
        ("smtp_port", "587", "number"),
        ("smtp_email_from", "", "string"),
        ("smtp_password", "", "string"),
        ("smtp_enabled", "false", "boolean"),
    ]
    for chiave, valore, tipo in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES (?, ?, ?)",
            (chiave, valore, tipo),
        )


def insert_voice_agent_config(conn):
    """Insert default voice agent config."""
    conn.execute("INSERT OR IGNORE INTO voice_agent_config (id) VALUES ('default')")


def insert_festivita(conn):
    """Insert Italian holidays for 2026."""
    for fid, data, desc, ric in FESTIVITA_2026:
        conn.execute(
            "INSERT OR IGNORE INTO giorni_festivi (id, data, descrizione, ricorrente) VALUES (?, ?, ?, ?)",
            (fid, data, desc, ric),
        )


def populate_vertical(conn, vertical_name, data):
    """Populate a vertical DB with business-specific data."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # 1. Impostazioni
    for chiave, valore in data["impostazioni"].items():
        conn.execute(
            "INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo, updated_at) VALUES (?, ?, 'string', ?)",
            (chiave, valore, now),
        )

    # 2. Servizi
    service_ids = []
    for nome, desc, cat, prezzo, durata, colore, ordine in data["servizi"]:
        sid = gen_id()
        service_ids.append((nome.lower(), sid))
        conn.execute(
            """INSERT INTO servizi (id, nome, descrizione, categoria, prezzo, durata_minuti, colore, ordine, attivo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (sid, nome, desc, cat, prezzo, durata, colore, ordine, now, now),
        )

    # 3. Operatori
    operator_ids = []
    for nome, cognome, email, tel, ruolo, colore, spec, desc_pos, anni, genere in data["operatori"]:
        oid = gen_id()
        operator_ids.append(oid)
        conn.execute(
            """INSERT INTO operatori (id, nome, cognome, email, telefono, ruolo, colore, attivo, specializzazioni, descrizione_positiva, anni_esperienza, genere, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)""",
            (oid, nome, cognome, email, tel, ruolo, colore, spec, desc_pos, anni, genere, now, now),
        )

    # 4. operatori_servizi — link operators to their services based on specializzazioni
    import json
    for i, op_data in enumerate(data["operatori"]):
        oid = operator_ids[i]
        spec_list = json.loads(op_data[6])  # specializzazioni JSON
        for spec_name in spec_list:
            spec_lower = spec_name.lower().strip()
            for svc_name, sid in service_ids:
                if svc_name == spec_lower:
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO operatori_servizi (operatore_id, servizio_id, priorita) VALUES (?, ?, 0)",
                            (oid, sid),
                        )
                    except sqlite3.IntegrityError:
                        pass
                    break

    # 5. Orari lavoro
    for giorno, ora_inizio, ora_fine, tipo in data["orari"]:
        oid_orario = gen_id()
        conn.execute(
            """INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id)
               VALUES (?, ?, ?, ?, ?, NULL)""",
            (oid_orario, giorno, ora_inizio, ora_fine, tipo),
        )

    # 6. FAQ settings
    for chiave, valore in data["faq_settings"].items():
        conn.execute(
            "INSERT OR REPLACE INTO faq_settings (chiave, valore, categoria, descrizione, created_at, updated_at) VALUES (?, ?, 'generale', ?, ?, ?)",
            (chiave, valore, chiave.replace("_", " ").title(), now, now),
        )

    # 7. Clienti
    for nome, cognome, tel, email, nascita, note in data["clienti"]:
        cid = gen_id()
        conn.execute(
            """INSERT INTO clienti (id, nome, cognome, telefono, email, data_nascita, note, consenso_whatsapp, consenso_marketing, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)""",
            (cid, nome, cognome, tel, email, nascita, note, now, now),
        )

    print(f"  Populated: {len(data['servizi'])} servizi, {len(data['operatori'])} operatori, "
          f"{len(data['orari'])} fasce orarie, {len(data['faq_settings'])} FAQ, {len(data['clienti'])} clienti")


def create_vertical_db(output_dir, vertical_name, data):
    """Create a complete SQLite DB for one vertical."""
    db_path = os.path.join(output_dir, f"{vertical_name}.db")

    # Remove existing
    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"\n--- Creating {vertical_name}.db ---")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        create_schema(conn)
        insert_default_impostazioni(conn)
        insert_voice_agent_config(conn)
        insert_festivita(conn)
        populate_vertical(conn, vertical_name, data)
        conn.commit()
        print(f"  OK: {db_path}")
    except Exception as e:
        print(f"  ERROR: {e}")
        raise
    finally:
        conn.close()

    return db_path


def copy_odontoiatra_db(output_dir, source_db):
    """Copy existing odontoiatra DB."""
    dest = os.path.join(output_dir, "odontoiatra.db")
    print(f"\n--- Copying odontoiatra.db ---")

    if os.path.exists(source_db):
        shutil.copy2(source_db, dest)
        print(f"  OK: Copied from {source_db}")
    else:
        # Create a fresh one with odontoiatra data if source doesn't exist
        print(f"  WARN: Source DB not found at {source_db}")
        print(f"  Creating fresh odontoiatra DB...")

        odontoiatra_data = {
            "impostazioni": {
                "nome_attivita": "Studio Dentistico Dr. Rossi",
                "macro_categoria": "medico",
                "micro_categoria": "odontoiatra",
                "indirizzo": "Via dei Mille 33, 00185 Roma (RM)",
                "telefono": "06 7788990",
                "email": "info@studiorossi.it",
            },
            "servizi": [
                ("Visita odontoiatrica", "Prima visita con panoramica", "Visite", 80.0, 30, "#3B82F6", 0),
                ("Pulizia dentale", "Igiene orale professionale con ultrasuoni", "Igiene", 60.0, 45, "#14B8A6", 1),
                ("Otturazione", "Otturazione in composito estetico", "Conservativa", 90.0, 45, "#F59E0B", 2),
                ("Devitalizzazione", "Trattamento endodontico canalare", "Endodonzia", 200.0, 90, "#EF4444", 3),
                ("Estrazione", "Estrazione dentale semplice", "Chirurgia", 100.0, 45, "#8B5CF6", 4),
                ("Sbiancamento", "Sbiancamento professionale LED", "Estetica", 250.0, 60, "#EC4899", 5),
                ("Impronta per protesi", "Impronta di precisione per corona/ponte", "Protesi", 50.0, 30, "#6366F1", 6),
                ("Controllo ortodontico", "Visita di controllo apparecchio", "Ortodonzia", 40.0, 20, "#F97316", 7),
            ],
            "operatori": [
                ("Dr.", "Rossi", "rossi@studiorossi.it", "333 1313131", "admin", "#3B82F6", '["visita odontoiatrica","otturazione","devitalizzazione","estrazione","sbiancamento","impronta per protesi","controllo ortodontico"]', "Odontoiatra con 20 anni di esperienza, specializzato in implantologia", 20, "M"),
                ("Dott.ssa", "Neri", "neri@studiorossi.it", "333 1414141", "operatore", "#EC4899", '["visita odontoiatrica","otturazione","sbiancamento","controllo ortodontico"]', "Odontoiatra specializzata in ortodonzia e estetica dentale", 12, "F"),
                ("Igienista", "Galli", "galli@studiorossi.it", "333 1515151", "operatore", "#14B8A6", '["pulizia dentale","visita odontoiatrica"]', "Igienista dentale certificata, esperta in prevenzione", 7, "F"),
            ],
            # Lun-Ven 9:00-13:00, 14:30-19:00
            "orari": [
                (1, "09:00", "13:00", "lavoro"), (1, "13:00", "14:30", "pausa"), (1, "14:30", "19:00", "lavoro"),
                (2, "09:00", "13:00", "lavoro"), (2, "13:00", "14:30", "pausa"), (2, "14:30", "19:00", "lavoro"),
                (3, "09:00", "13:00", "lavoro"), (3, "13:00", "14:30", "pausa"), (3, "14:30", "19:00", "lavoro"),
                (4, "09:00", "13:00", "lavoro"), (4, "13:00", "14:30", "pausa"), (4, "14:30", "19:00", "lavoro"),
                (5, "09:00", "13:00", "lavoro"), (5, "13:00", "14:30", "pausa"), (5, "14:30", "19:00", "lavoro"),
            ],
            "faq_settings": {
                "giorni_apertura": "Lunedi - Venerdi",
                "orario_mattina": "9:00",
                "orario_pomeriggio": "19:00",
                "giorni_chiusura": "Sabato e Domenica",
                "tempo_ultimo_appuntamento": "30",
                "metodi_pagamento": "Contanti, Carte, Bonifico",
                "info_parcheggio": "Parcheggio a pagamento nelle vicinanze",
                "numero_telefono": "06 7788990",
                "indirizzo_salone": "Via dei Mille 33, Roma",
            },
            "clienti": [
                ("Mario", "Bianchi", "3391234666", "mario.bianchi@email.it", "1975-06-15", "Pulizia semestrale, paziente puntuale"),
                ("Giovanna", "Santi", "3387654666", "giovanna.santi@email.it", "1982-03-22", "Trattamento ortodontico in corso"),
                ("Franco", "Moretti", "3401122666", "franco.moretti@email.it", "1960-11-08", "Protesi parziale, controlli trimestrali"),
                ("Alessia", "Bruno", "3339988666", "alessia.bruno@email.it", "1998-07-30", "Sbiancamento recente, pulizia regolare"),
                ("Enzo", "Carbone", "3476655666", "enzo.carbone@email.it", "1970-01-12", "Devitalizzazione in corso, 3 sedute"),
            ],
        }
        create_vertical_db(output_dir, "odontoiatra", odontoiatra_data)
        return

    return dest


def verify_db(db_path, vertical_name):
    """Verify a vertical DB has correct data."""
    conn = sqlite3.connect(db_path)
    try:
        counts = {}
        for table in ["servizi", "operatori", "orari_lavoro", "faq_settings", "clienti", "operatori_servizi"]:
            try:
                row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                counts[table] = row[0] if row else 0
            except sqlite3.OperationalError:
                counts[table] = -1

        nome = conn.execute("SELECT valore FROM impostazioni WHERE chiave='nome_attivita'").fetchone()
        macro = conn.execute("SELECT valore FROM impostazioni WHERE chiave='macro_categoria'").fetchone()

        print(f"  Verify {vertical_name}: nome={nome[0] if nome else '?'}, macro={macro[0] if macro else '?'}")
        print(f"    servizi={counts['servizi']}, operatori={counts['operatori']}, "
              f"orari={counts['orari_lavoro']}, faq={counts['faq_settings']}, "
              f"clienti={counts['clienti']}, op_servizi={counts['operatori_servizi']}")

        # Verify WAL mode
        journal = conn.execute("PRAGMA journal_mode").fetchone()
        print(f"    journal_mode={journal[0] if journal else '?'}")

        return all(v > 0 for v in counts.values())
    finally:
        conn.close()


# ========================================================================
# MAIN
# ========================================================================

def main():
    output_dir = DEFAULT_OUTPUT_DIR
    if len(sys.argv) > 1 and sys.argv[1] == "--output-dir":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR

    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("FLUXION - Creating Vertical Demo DBs")
    print(f"Output: {output_dir}")
    print("=" * 60)

    # Create 8 verticals from data definitions
    created = []
    for vname, vdata in VERTICALS.items():
        db_path = create_vertical_db(output_dir, vname, vdata)
        created.append((vname, db_path))

    # Copy or create odontoiatra
    copy_odontoiatra_db(output_dir, EXISTING_DB)
    created.append(("odontoiatra", os.path.join(output_dir, "odontoiatra.db")))

    # Verify all
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    all_ok = True
    for vname, db_path in created:
        if os.path.exists(db_path):
            ok = verify_db(db_path, vname)
            if not ok:
                all_ok = False
                print(f"  FAIL: {vname}")
        else:
            print(f"  FAIL: {vname} — file not found")
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("ALL 9 VERTICAL DBs CREATED SUCCESSFULLY")
    else:
        print("SOME VERTICALS HAD ISSUES — check output above")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    # List files
    print("\nFiles created:")
    for f in sorted(os.listdir(output_dir)):
        if f.endswith(".db"):
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"  {f:30s} {size:>10,d} bytes")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
