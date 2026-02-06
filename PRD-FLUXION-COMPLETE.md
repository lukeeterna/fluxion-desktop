# FLUXION - Product Requirements Document (PRD)
## Versione 1.0 - Documento di Verità Unico
**Data**: 2026-02-06  
**Stato**: Implementazione Avanzata (~85% completata)  
**Prossima Milestone**: Completamento Schede Verticali + Testing E2E

---

# 1. VISIONE PRODOTTO

## 1.1 Cos'è Fluxion

Fluxion è un **gestionale desktop enterprise per PMI italiane** (1-15 dipendenti) che unisce:
- CRM con schede cliente verticalizzate per settore
- Calendario appuntamenti con workflow automatizzati
- Fatturazione elettronica XML (FatturaPA)
- Voice Agent AI "Sara" per prenotazioni telefoniche
- WhatsApp Business integration
- Sistema loyalty e pacchetti servizi

## 1.2 Target Market

| Segmento | Esempi | Dipendenti |
|----------|--------|------------|
| Beauty & Wellness | Saloni, centri estetici, SPA | 1-5 |
| Health | Studi dentistici, fisioterapia | 2-10 |
| Automotive | Meccanici, carrozzerie, gommisti | 2-8 |
| Fitness | Palestre, personal trainer | 1-5 |

## 1.3 Modello Business - Licenza LIFETIME

```
┌─────────────────────────────────────────────────────────────┐
│  FLUXION LICENSE SYSTEM - NO SaaS, NO Commissioni           │
├─────────────────────────────────────────────────────────────┤
│  🏅 BASE (€199)          │ 1 Verticale, CRM, Calendario      │
│  🥈 PRO (€399)           │ 3 Verticali, Marketing, Analytics │
│  🥇 ENTERPRISE (€799)    │ 6 Verticali, Voice, WhatsApp, API │
└─────────────────────────────────────────────────────────────┘
```

**Vantaggio competitivo**: Pagamento una tantum vs. SaaS mensile concorrenti (€30-100/mese).

---

# 2. STACK TECNOLOGICO

## 2.1 Architettura Completa

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FLUXION ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    HTTP/WebSocket    ┌─────────────────────────┐  │
│  │  Tauri Frontend │ ◄──────────────────► │   Voice Agent (Python)  │  │
│  │  React 19 + TS  │                      │   - FastAPI server        │  │
│  │  - Desktop UI   │                      │   - Silero VAD            │  │
│  │  - State mgmt   │                      │   - Groq LLM fallback     │  │
│  └────────┬────────┘                      │   - Piper TTS             │  │
│           │                               └─────────────────────────┘  │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Tauri Backend (Rust)                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │ Commands API │  │ Domain Layer │  │  Infrastructure      │   │   │
│  │  │ - 100+ cmds  │  │ - Entities   │  │  - SQLite (SQLx)     │   │   │
│  │  │ - Validation │  │ - Services   │  │  - File system       │   │   │
│  │  │ - Auth       │  │ - Repository │  │  - HTTP clients      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Database SQLite (Local)                                        │   │
│  │  - 25+ tabelle                                                  │   │
│  │  - Migrations SQLx                                              │   │
│  │  - Encryption AES-256-GCM per dati sensibili                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Tecnologie Dettagliate

| Layer | Tecnologia | Versione | Scopo |
|-------|------------|----------|-------|
| **Desktop Runtime** | Tauri | 2.x | App desktop cross-platform |
| **Frontend** | React | 19.x | UI component-based |
| **Frontend Lang** | TypeScript | 5.x | Type safety |
| **Styling** | Tailwind CSS | 3.4 | Utility-first CSS |
| **UI Components** | shadcn/ui | Latest | Pre-built accessible components |
| **State Mgmt** | TanStack Query | 5.x | Server state management |
| **Routing** | React Router | 7.x | Client-side routing |
| **Icons** | Lucide React | Latest | Icon library |
| **Charts** | Recharts | Latest | Data visualization |
| **Backend** | Rust | 1.75+ | Performance & safety |
| **DB Driver** | SQLx | 0.8 | Async SQL con compile-time checks |
| **DB** | SQLite | 3.x | Local embedded database |
| **Voice STT** | Whisper.cpp + Groq | - | Speech-to-text |
| **Voice TTS** | Piper | - | Text-to-speech italiano |
| **Voice NLU** | Custom + Groq | - | Intent classification |
| **Voice VAD** | Silero ONNX | - | Voice Activity Detection |

---

# 3. MODULI IMPLEMENTATI

## 3.1 Core System (100% Completato)

### Setup Wizard
- **File**: `SetupWizard.tsx`, `setup.rs`
- **Feature**:
  - 6 step guidati: Dati → Indirizzo → Macro → Micro → Licenza → Config
  - Selezione 6 macro-categorie (medico, beauty, hair, auto, wellness, professionale)
  - 40+ micro-categorie mappate
  - Configurazione FLUXION IA Key
  - **Campi Configurazione Comunicazione (Nuovi):**
    - `nome_attivita`: Nome visualizzato in QR code, Voice Agent greeting, WhatsApp
    - `whatsapp_number`: Numero WhatsApp Business per notifiche clienti
    - `ehiweb_number`: Numero linea fissa EhiWeb per Voice Agent (opzionale)
  - Salvataggio in tabella `impostazioni`

**Schema Configurazione Aggiornato:**
```sql
CREATE TABLE impostazioni (
  -- ... campi esistenti ...
  nome_attivita TEXT,
  whatsapp_number TEXT,
  ehiweb_number TEXT,  -- Opzionale
  -- Usato per:
  -- - QR Code: "Prenota ora su {nome_attivita}"
  -- - Voice Agent: "Buongiorno, sono Sara di {nome_attivita}"
  -- - WhatsApp: Template con nome attività
);
```

### Sistema Licenze Ed25519
- **File**: `license_ed25519.rs`, `LicenseManager.tsx`
- **Feature**:
  - Firma crittografica Ed25519 offline
  - Hardware fingerprint (hostname + CPU + RAM + OS)
  - 3 tier: Trial, Base (€199), Pro (€399), Enterprise (€799)
  - Verifica accesso a verticali e feature
  - Tool separato `fluxion-license-generator/` per generazione licenze

---

## 3.2 CRM Clienti (100% Completato)

### Gestione Clienti Base
- **File**: `clienti.rs`, `ClientiPage.tsx`, `ClienteDialog.tsx`
- **Feature**:
  - CRUD completo clienti
  - Soft delete con `deleted_at`
  - Ricerca full-text
  - Import/Export CSV
  - Validazione telefono, email, CF

### Schede Cliente Verticali - 3/8 Complete

| Scheda | Stato | Feature Principali |
|--------|-------|-------------------|
| **Odontoiatrica** | ✅ Completa | Odontogramma FDI interattivo (32 denti), anamnesi, allergie, trattamenti |
| **Fisioterapia** | ✅ Completa | Zone corpo, scale VAS/Oswestry/NDI, sedute con progresso |
| **Estetica** | ✅ Completa | Fototipo Fitzpatrick (1-6), tipo pelle, allergie, routine skincare |
| Parrucchiere | 📝 Placeholder | Colorazioni, formulazioni, tagli |
| Veicoli | 📝 Placeholder | Storico veicoli, tagliandi, gomme |
| Carrozzeria | 📝 Placeholder | Danni, foto, preventivi |
| Medica | 📝 Placeholder | Cartella clinica, prescrizioni |
| Fitness | 📝 Placeholder | Schede allenamento, misurazioni |

**Switching Dinamico**: Componente `SchedaClienteDynamic.tsx` mappa `micro_categoria` → componente scheda corretta.

**Roadmap Schede Mancanti (FASE 2):**
1. **Parrucchiere**: Colorazioni con formulazione chimica, storico tagli
2. **Veicoli**: Anagrafica veicoli, storico tagliandi, scadenze (assicurazione, bollo)
3. **Carrozzeria**: Foto danni, preventivi, stati lavorazione
4. **Medica**: Cartella clinica, prescrizioni, referti
5. **Fitness**: Schede allenamento, misurazioni antropometriche, progressi

---

## 3.3 Calendario & Booking (100% Completato)

### Backend (Rust)
- **File**: `appuntamenti.rs`, `appuntamenti_ddd.rs`
- **Commands**: 18 Tauri commands + 8 DDD commands
- **Feature**:
  - State Machine workflow (8 stati): Bozza → Confermato → InCorso → Completato
  - Validazione 3-layer: Hard Block + Warning + Suggerimento
  - Conflict detection automatico
  - Festività italiane (Nager.Date API)
  - Query per operatore e range date

### Frontend (React)
- **File**: `CalendarioPage.tsx`, `AppuntamentoDialog.tsx`
- **Feature**:
  - Vista mensile/settimanale/giornaliera
  - Drag & drop appuntamenti
  - Auto-fill da cliente/servizio selezionato
  - ValidazioneAlert component (color-coded)
  - OverrideDialog per audit trail

### Domain Model
```rust
// Stati Appuntamento
enum StatoAppuntamento {
    Bozza,
    Confermato,
    InArrivo,
    InAttesa,
    InCorso,
    Completato,
    Cancellato,
    NoShow,
}

// Validazione 3-layer
struct ValidationResult {
    blocks: Vec<ValidationIssue>,      // Hard blocks (no save)
    warnings: Vec<ValidationIssue>,    // Warning (can override)
    suggestions: Vec<ValidationIssue>, // Suggerimenti (info only)
}
```

---

## 3.4 Servizi & Operatori (100% Completato)

### Servizi
- **File**: `servizi.rs`
- **Commands**: 5 Tauri commands
- **Feature**:
  - CRUD servizi con durata e prezzo
  - Categorizzazione per verticale
  - Colori per calendario

### Operatori
- **File**: `operatori.rs`
- **Commands**: 5 Tauri commands
- **Feature**:
  - CRUD operatori/squadra
  - Assegnazione servizi
  - Orari di lavoro
  - Colori personali

---

## 3.5 Fatturazione Elettronica (100% Completato)

### Schema Database (8 tabelle)
- `impostazioni_fatturazione` - Dati azienda, regime fiscale, IBAN
- `fatture` - Header con stato workflow
- `fatture_righe` - Linee con IVA, natura, sconto
- `fatture_riepilogo_iva` - Aggregazione per aliquota
- `fatture_pagamenti` - Tracking incassi
- `numeratore_fatture` - Progressivo per anno
- `codici_pagamento` - Lookup SDI (MP01-MP23)
- `codici_natura_iva` - Lookup SDI (N1-N7)

### Backend (Rust)
- **File**: `fatture.rs` (700+ righe)
- **Commands**: 14 Tauri commands
- **Feature**:
  - CRUD fatture + righe + pagamenti
  - Emissione con generazione XML FatturaPA 1.2.2
  - Calcolo automatico bollo virtuale (>€77.47 forfettario)
  - Numerazione progressiva per anno
  - Workflow: Bozza → Emessa → Pagata

### XML FatturaPA Compliant
- Header cedente/cessionario con regime fiscale
- Linee documento con natura IVA per esenzioni
- Riepilogo IVA aggregato
- Dati pagamento con IBAN
- Bollo virtuale automatico per forfettari

### Frontend
- **File**: `Fatture.tsx`, `FatturaDialog.tsx`, `FatturaDetail.tsx`
- **Feature**:
  - Lista fatture con filtri
  - Stats cards (fatturato, da pagare, scadute)
  - Creazione bozza wizard
  - Download XML per invio SDI

---

## 3.6 Loyalty & Pacchetti (100% Completato)

### Schema Database
- `loyalty_visits` - Contatore visite per cliente
- `pacchetti` - Definizione pacchetti servizi
- `clienti_pacchetti` - Acquisti cliente
- `pacchetto_servizi` - Many-to-many pacchetti ↔ servizi

### Backend
- **File**: `loyalty.rs`
- **Commands**: 18 Tauri commands
- **Feature**:
  - Tracking visite con soglia VIP
  - Pacchetti con scadenza e countdown
  - Composizione servizi alla creazione
  - Calcolo automatico prezzo da sconto %

### Frontend
- **Componenti**: `LoyaltyProgress.tsx`, `PacchettiList.tsx`
- **Feature**:
  - Tessera timbri con progress bar
  - Badge VIP in tabella clienti
  - Workflow proposta/acquisto/uso pacchetti
  - Countdown scadenza (rosso ≤7gg, giallo ≤30gg)

### Invio Pacchetti via WhatsApp Selettivo (Nuovo)
L'operatore può inviare pacchetti promozionali via WhatsApp con filtri avanzati:

```typescript
interface WhatsAppPacchettiFilter {
  target: 'tutti' | 'vip' | 'vip_3_stelle' | 'vip_custom';
  minLoyaltyVisits?: number;  // Per vip_custom (es: >= 3)
  pacchettoId: string;
  messaggioPersonalizzato?: string;
}
```

**Filtri disponibili:**
- **Tutti i clienti**: Invia a tutto il database
- **Solo VIP**: `is_vip = 1`
- **VIP 3+ stelle**: `is_vip = 1 AND loyalty_visits >= 3`
- **VIP custom**: `is_vip = 1 AND loyalty_visits >= {soglia}`

**UI**: `WhatsAppPacchettiSender.tsx`
- Selezione pacchetto da catalogo
- Selezione filtro destinatari
- Preview messaggio con nome attività
- Invio progressivo (rate limiting 60 msg/ora)
- Report invio (consegnati, falliti, aperti)

---

## 3.7 Cassa (100% Completato)

### Schema Database
- `incassi` - Movimenti di cassa
- `chiusure_cassa` - Chiusure giornaliere
- `metodi_pagamento` - Contanti, Carta, Bonifico, etc.

### Feature
- Registrazione incassi da appuntamenti
- Chiusura cassa giornaliera
- Report incassi per periodo
- Metodi di pagamento personalizzabili

---

## 3.8 Voice Agent "Sara" (95% Completato)

### Architettura 5-Layer Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│                    SARA VOICE PIPELINE                         │
├────────────────────────────────────────────────────────────────┤
│ L0: Sentiment Analysis      (<5ms)    Frustrazione detection   │
│ L1: Exact Match             (<1ms)    Cortesia, conferme       │
│ L2: Intent Classifier       (<20ms)   Pattern matching         │
│ L3: FAQ Retrieval           (<50ms)   Keyword + semantic       │
│ L4: Groq LLM Fallback       (500ms+)  Complex cases            │
└────────────────────────────────────────────────────────────────┘
```

### Componenti Implementati

| Componente | Tecnologia | Stato |
|------------|------------|-------|
| STT Engine | Whisper.cpp + Groq fallback | ✅ |
| Intent Classifier | Pattern + TF-IDF semantic | ✅ |
| Entity Extractor | Regex + Groq fallback | ✅ |
| State Machine | Custom Python FSM | ✅ |
| TTS | Piper (italiano) | ✅ |
| VAD | Silero ONNX (32ms chunks) | ✅ |
| Disambiguation | Cognome-based strategy | ✅ |
| FAQ Manager | Hybrid keyword + semantic | ✅ |
| Analytics | SQLite logging | ✅ |

### Intents Supportati
- `PRENOTAZIONE` - Nuova prenotazione
- `CANCELLAZIONE` - Annulla appuntamento
- `SPOSTAMENTO` - Modifica data/ora
- `WAITLIST` - Richiesta lista d'attesa quando slot occupati
- `INFO_ORARI` - Chiede orari apertura
- `INFO_SERVIZI` - Chiede servizi disponibili
- `INFO_PREZZI` - Chiede prezzi
- `CORREZIONE` - Corregge input precedente
- `CONFERMA` - Conferma azione
- `RIFIUTO` - Rifiuta/annulla

#### Flusso WAITLIST (Nuovo)
Quando il cliente richiede uno slot occupato:

```
Cliente: "Vorrei prenotare domani alle 15:00"
Agente:  [Verifica slot occupati]
Agente:  "Mi dispiace, lo slot delle 15:00 è occupato. Posso proporle:
          - 14:30 (libero)
          - 16:00 (libero)
          Oppure vuole che la metta in lista d'attesa? 
          Le invieremo un WhatsApp appena si libera uno slot."

Cliente: "Mettetemi in lista d'attesa"
Agente:  [Salva in tabella waitlist con stato 'attesa']
Agente:  "Perfetto! La abbiamo messa in lista d'attesa per domani 
          dalle 15:00. Riceverà un WhatsApp non appena si libera uno slot."
```

**Implementazione WAITLIST:**
- Intent: `WAITLIST` / `RICHIESTA_LISTA_ATTESA`
- State: `PROPOSING_WAITLIST` → `CONFIRMING_WAITLIST` → `WAITLIST_SAVED`
- Tabella: `waitlist` (Migration 013)
- Trigger: SlotChecker rileva occupazione → proposta automatica
- Notifica: WhatsApp automatico quando slot si libera
- Template WhatsApp: "Ciao {nome}, si è liberato uno slot per {servizio} 
  il {data} alle {ora}. Rispondi SI per prenotare o NO per declinare."

### State Machine States
```python
class BookingStateMachine:
    states = [
        "IDLE",
        "GREETING",
        "REGISTERING_SURNAME",
        "REGISTERING_PHONE",
        "SELECTING_SERVICE",
        "SELECTING_DATE",
        "SELECTING_TIME",
        "SELECTING_OPERATOR",
        "CONFIRMING",
        "CANCELLING",
        "RESCHEDULING",
        "CLOSING",
        # WAITLIST States (Nuovi)
        "CHECKING_AVAILABILITY",
        "SLOT_UNAVAILABLE",
        "PROPOSING_WAITLIST",
        "CONFIRMING_WAITLIST",
        "WAITLIST_SAVED",
    ]
```

### Integrazione WhatsApp Business
- **File**: `whatsapp-service.js`
- **Feature**:
  - Auto-responder con Groq LLM
  - FAQ-based context retrieval
  - Rate limiting (60 risposte/ora per utente)
  - Learn from Operator system
  - QR Kit generazione (Prenota, Info, Sposta)

---

## 3.9 FLUXION IA / RAG (100% Completato)

### Backend
- **File**: `rag.rs`
- **Commands**: 5 Tauri commands
- **Feature**:
  - Load FAQs from markdown
  - Category selector (5 verticali)
  - Simple keyword retrieval (TF-IDF lite)
  - Groq API integration (llama-3.1-8b-instant)
  - Confidence scoring

### Frontend
- **File**: `RagChat.tsx`
- **Feature**:
  - Chat interface con cronologia
  - Confidence badges colorati
  - Sezione fonti espandibili
  - Test API button

---

## 3.10 Diagnostics & Support (100% Completato)

### Feature
- **Support Bundle Export**: ZIP con diagnostics, DB, config
- **Backup Database**: Copia atomica con WAL checkpoint
- **Restore Database**: Verifica integrità + safety backup
- **Diagnostics Info**: Versioni, spazio disco, contatori
- **Remote Assist**: Istruzioni macOS/Windows native

---

## 3.11 CI/CD & Testing (100% Completato)

### GitHub Actions
- **test.yml**: 5 jobs paralleli (backend tests 3 OS, quality, frontend, build)
- **release.yml**: Automated release multi-platform
- **Status**: 9/9 jobs SUCCESS su Ubuntu, macOS, Windows

### Test Suite
- **Backend Rust**: 100+ tests
- **Voice Agent Python**: 955+ tests
- **E2E Playwright**: Setup completato
- **Coverage target**: 95%

---

# 4. DATABASE SCHEMA

## 4.1 Schema Completo (25+ tabelle)

### Core
```sql
-- Clienti
CREATE TABLE clienti (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  cognome TEXT NOT NULL,
  telefono TEXT,
  email TEXT,
  codice_fiscale TEXT,
  data_nascita TEXT,
  indirizzo TEXT,
  citta TEXT,
  cap TEXT,
  note TEXT,
  -- Loyalty fields
  loyalty_visits INTEGER DEFAULT 0,
  loyalty_threshold INTEGER DEFAULT 10,
  is_vip INTEGER DEFAULT 0,
  referral_source TEXT,
  referral_cliente_id TEXT,
  -- Vertical
  vertical_type TEXT,
  -- Soft delete
  deleted_at TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Servizi
CREATE TABLE servizi (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  descrizione TEXT,
  durata_minuti INTEGER NOT NULL,
  prezzo REAL NOT NULL,
  colore TEXT,
  categoria TEXT,
  attivo INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Operatori
CREATE TABLE operatori (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  cognome TEXT NOT NULL,
  telefono TEXT,
  email TEXT,
  colore TEXT,
  attivo INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Appuntamenti
CREATE TABLE appuntamenti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  servizio_id TEXT NOT NULL,
  operatore_id TEXT,
  data TEXT NOT NULL,
  ora_inizio TEXT NOT NULL,
  ora_fine TEXT NOT NULL,
  stato TEXT DEFAULT 'bozza',
  note TEXT,
  prezzo_finale REAL,
  sconto_applicato REAL,
  motivo_sconto TEXT,
  -- Waitlist
  waitlist_priority INTEGER DEFAULT 0,
  -- Audit
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT
);
```

### Fatturazione
```sql
CREATE TABLE fatture (
  id TEXT PRIMARY KEY,
  numero TEXT NOT NULL UNIQUE,
  anno INTEGER NOT NULL,
  data_emissione TEXT NOT NULL,
  cliente_id TEXT NOT NULL,
  stato TEXT DEFAULT 'bozza', -- bozza, emessa, pagata, annullata
  tipo_documento TEXT DEFAULT 'fattura',
  -- Totals
  imponibile_totale REAL DEFAULT 0,
  iva_totale REAL DEFAULT 0,
  bollo_virtuale REAL DEFAULT 0,
  totale_documento REAL DEFAULT 0,
  -- XML
  xml_content TEXT,
  -- Metadata
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE fatture_righe (
  id TEXT PRIMARY KEY,
  fattura_id TEXT NOT NULL,
  numero_linea INTEGER NOT NULL,
  descrizione TEXT NOT NULL,
  quantita REAL DEFAULT 1,
  prezzo_unitario REAL NOT NULL,
  sconto_percentuale REAL DEFAULT 0,
  -- IVA
  aliquota_iva REAL DEFAULT 22,
  natura_iva TEXT, -- N1-N7 per esenzioni
  -- Totals
  prezzo_totale REAL NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
```

### Loyalty
```sql
CREATE TABLE pacchetti (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  descrizione TEXT,
  prezzo_listino REAL NOT NULL,
  prezzo_scontato REAL NOT NULL,
  sconto_percentuale REAL,
  durata_giorni INTEGER,
  numero_servizi INTEGER,
  attivo INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE clienti_pacchetti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  pacchetto_id TEXT NOT NULL,
  data_acquisto TEXT NOT NULL,
  data_scadenza TEXT,
  prezzo_pagato REAL,
  servizi_totali INTEGER,
  servizi_usati INTEGER DEFAULT 0,
  stato TEXT DEFAULT 'attivo', -- attivo, completato, scaduto, rimborsato
  created_at TEXT DEFAULT (datetime('now'))
);
```

### Schede Verticali (Odontoiatrica - Esempio)
```sql
CREATE TABLE schede_odontoiatriche (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL UNIQUE,
  -- Anamnesi
  allergie TEXT, -- JSON array
  patologie TEXT, -- JSON array
  farmaci TEXT, -- JSON array
  fumatore INTEGER,
  -- Odontogramma
  odontogramma TEXT, -- JSON array 32 denti FDI
  -- Metadata
  note_generali TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT
);

CREATE TABLE odontogramma_trattamenti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  dente_numero INTEGER NOT NULL, -- 11-48 FDI
  data TEXT NOT NULL,
  tipo_trattamento TEXT,
  stato TEXT, -- pianificato, in_corso, completato
  costo_previsto REAL,
  costo_finale REAL,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

# 5. API TAURI COMMANDS

## 5.1 Riepilogo per Modulo

| Modulo | Commands | File |
|--------|----------|------|
| Clienti | 5 | `clienti.rs` |
| Servizi | 5 | `servizi.rs` |
| Operatori | 5 | `operatori.rs` |
| Appuntamenti | 26 | `appuntamenti.rs`, `appuntamenti_ddd.rs` |
| Loyalty | 18 | `loyalty.rs` |
| Fatture | 14 | `fatture.rs` |
| Setup | 4 | `setup.rs` |
| Diagnostics | 6 | `diagnostics.rs` |
| RAG | 5 | `rag.rs` |
| WhatsApp | 2 | `whatsapp.rs` |
| Voice | 1 | `voice.rs` |
| FAQ Template | 3 | `faq_template.rs` |
| Cassa | 8 | `cassa.rs` |
| Licenze | 7 | `license_ed25519.rs` |
| Schede Cliente | 12 | `schede_cliente.rs` |
| **TOTALE** | **~121** | |

---

# 6. DESIGN SYSTEM

## 6.1 Color Palette FLUXION

```css
:root {
  --primary: #22D3EE;        /* Cyan - Azioni principali */
  --secondary: #0891B2;      /* Teal - Azioni secondarie */
  --accent: #C084FC;         /* Purple - Highlights */
  --background: #1E293B;     /* Navy - Background */
  --background-dark: #0F172A;/* Navy Dark - Deep background */
  --foreground: #F1F5F9;     /* Slate 50 - Text */
  --muted: #64748B;          /* Slate 500 - Secondary text */
  --border: #334155;         /* Slate 700 - Borders */
  --destructive: #EF4444;    /* Red 500 - Error */
  --success: #10B981;        /* Emerald 500 - Success */
}
```

## 6.2 Typography

| Size | Value | Use Case |
|------|-------|----------|
| xs | 11px | Labels, badges |
| sm | 12px | Form labels |
| base | 14px | Body text |
| lg | 16px | Inputs, headers |
| xl | 18px | Section titles |
| 2xl | 20px | Page titles |
| 3xl | 24px | Dashboard titles |
| 4xl | 32px | KPI numbers |

## 6.3 Spacing

Base unit: 4px
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 20px
- 2xl: 24px
- 3xl: 32px

## 6.4 Componenti Base

### Sidebar
- Width: 60px (collapsed) → 240px (expanded)
- Transition: 200ms cubic-bezier(0.4, 0, 0.2, 1)
- Background: bg-slate-900
- Active state: bg-teal-500/20 + text-teal-400

### Header
- Height: 56px
- Background: bg-slate-900/50
- Shadow: shadow-sm

### Cards
- Border-radius: 12px
- Background: bg-slate-800/50
- Border: 1px solid border-slate-700
- Shadow: shadow-md
- Hover: scale 1.02 + shadow-lg

### Buttons
| Variant | Background | Text |
|---------|------------|------|
| Primary | bg-teal-500 | white |
| Secondary | bg-slate-800 | text-slate-200 |
| Ghost | transparent | text-slate-300 |
| Destructive | bg-red-600 | white |

Height: 40px, Border-radius: 8px, Padding: 8px 12px

---

# 7. ROADMAP FUTURA

## 7.1 Priorità Alta (Prossime 2 settimane)

### Voice Agent WAITLIST (In Corso)
- [x] Database schema `waitlist` (Migration 013) - ✅ Completo
- [ ] Intent `WAITLIST` in classifier - 🔴 Da implementare
- [ ] Stati state machine `SLOT_UNAVAILABLE` → `PROPOSING_WAITLIST` - 🔴 Da implementare
- [ ] Logica "slot occupati → proposta waitlist" - 🔴 Da implementare
- [ ] Integrazione WhatsApp notifica slot libero - 🔴 Da implementare
- [ ] Test E2E flusso completo - 🔴 Da eseguire

### Loyalty WhatsApp Selettivo
- [ ] UI `WhatsAppPacchettiSender.tsx` - 🔴 Da implementare
- [ ] Filtri: tutti | VIP | VIP 3+ stelle | custom - 🔴 Da implementare
- [ ] Rate limiting 60 msg/ora - 🔴 Da implementare
- [ ] Report invio - 🔴 Da implementare

### Setup Wizard Configurazione
- [ ] Campo `nome_attivita` - 🔴 Da implementare
- [ ] Campo `whatsapp_number` - 🔴 Da implementare
- [ ] Campo `ehiweb_number` (opzionale) - 🔴 Da implementare
- [ ] Integrazione Voice Agent greeting dinamico - 🔴 Da implementare

### MCP CI/CD Monitoraggio
- [ ] Setup MCP server per monitoraggio test - 🔴 Da implementare
- [ ] Integrazione GitHub Actions webhook - 🔴 Da implementare
- [ ] Dashboard stato CI/CD - 🔴 Da implementare

### Completamento Schede Verticali
- [ ] Scheda Parrucchiere completa (colorazioni, formulazioni)
- [ ] Scheda Veicoli completa (storico tagliandi)
- [ ] Scheda Carrozzeria completa (danni, foto)
- [ ] Scheda Medica completa (cartella clinica)
- [ ] Scheda Fitness completa (schede allenamento)

### Testing & QA
- [ ] E2E tests completi (Playwright)
- [ ] Voice Agent live testing
- [ ] Performance profiling
- [ ] Security audit

## 7.2 Priorità Media (1-2 mesi)

### Voice Agent Production
- [ ] VoIP Integration completa (SIP/RTP Ehiweb)
- [ ] Multi-vertical voice handlers
- [ ] Training data collection
- [ ] Analytics dashboard

### Marketing & Growth
- [ ] Landing page website
- [ ] Demo video
- [ ] Documentazione utente
- [ ] Onboarding guide

### Feature Aggiuntive
- [ ] Multi-location support
- [ ] White label customization
- [ ] API access per integrazioni
- [ ] Mobile companion app (PWA)

## 7.3 Priorità Bassa (3-6 mesi)

### Enterprise Features
- [ ] Team collaboration
- [ ] Advanced analytics
- [ ] Custom reports builder
- [ ] Zapier/Make integrations

### Expansion
- [ ] Traduzione multi-lingua
- [ ] Mercati EU (formati fatturazione)
- [ ] App mobile native

---

# 8. CONVENZIONI SVILUPPO

## 8.1 Rust Backend
- Formattazione: `cargo fmt`
- Lint: `cargo clippy`
- Preferire `unwrap_or_else()` a `unwrap_or()` per String
- Error handling con `Result<T, Error>`
- Async/await per tutte le operazioni I/O

## 8.2 TypeScript/React
- Strict mode abilitato
- No `any` impliciti
- Componenti: `PascalCase`
- Hooks: `camelCase` con prefisso `use`
- Types: `PascalCase` con suffisso `Type` o `Props`

## 8.3 Database
- Migrations numerate sequenzialmente (001, 002, ...)
- Soft delete con `deleted_at` campo
- Timestamps: `created_at`, `updated_at`
- JSON fields per dati flessibili

## 8.4 Git Workflow
- Branch: `feat/nome-feature`, `fix/nome-bug`
- Commit convenzionali: `feat:`, `fix:`, `docs:`, `refactor:`
- PR con template completo
- CI/CD must pass before merge

---

# 9. APPENDICI

## 9.1 Glossario

| Termine | Significato |
|---------|-------------|
| VAD | Voice Activity Detection |
| STT | Speech-to-Text |
| TTS | Text-to-Speech |
| NLU | Natural Language Understanding |
| RAG | Retrieval-Augmented Generation |
| FSM | Finite State Machine |
| DDD | Domain-Driven Design |
| FDI | Federazione Dentaria Internazionale (sistema numerazione denti) |

## 9.2 Riferimenti

- [Tauri Docs](https://tauri.app)
- [React Docs](https://react.dev)
- [Rust Book](https://doc.rust-lang.org/book/)
- [SQLx Docs](https://docs.rs/sqlx)
- [FatturaPA Specifiche](https://www.fatturapa.gov.it)

---

*Documento PRD - Versione 1.0*  
*Ultimo aggiornamento: 2026-02-06*  
*Prodotto da: Automation Business*
