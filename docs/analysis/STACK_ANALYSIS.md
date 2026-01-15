# Stack Fluxion - Analisi Completa

## Backend

| Componente | Tecnologia | Dettagli |
|------------|------------|----------|
| **Linguaggio** | Rust (Edition 2021) | Async/await con Tokio 1.48 |
| **Framework** | Tauri 2.x | Desktop cross-platform |
| **Database** | SQLite 3.x | Local-first, 15 migrazioni |
| **ORM** | SQLx 0.8.6 | Async, compile-time checked |
| **HTTP Bridge** | Axum 0.7 | Per MCP integration (porta 3001) |

### Dipendenze Core
```toml
tauri = "2.x"
sqlx = { version = "0.8.6", features = ["sqlite", "runtime-tokio"] }
tokio = { version = "1.48", features = ["full"] }
serde = "1.0"
chrono = "0.4.42"
uuid = "1.19"
reqwest = "0.11"
```

---

## Frontend

| Componente | Tecnologia | Versione |
|------------|------------|----------|
| **Framework** | React | 19.1.0 |
| **Linguaggio** | TypeScript | 5.8.3 |
| **Build Tool** | Vite | 5.4.11 |
| **Styling** | Tailwind CSS | 3.4.17 |
| **UI Components** | Radix UI | 1.x |
| **State** | Zustand | 4.5.7 |
| **Data Fetching** | TanStack Query | 5.90.15 |
| **Forms** | react-hook-form + Zod | 7.69 + 4.2 |

---

## Voice Agent (Python 3.10+)

### STT (Speech-to-Text)
| Provider | Model | Latenza |
|----------|-------|---------|
| **Groq API** | whisper-large-v3 | ~200ms |

### TTS (Text-to-Speech) - Voce: **Sara**
| Engine | Qualità | Latenza | Size | Ruolo |
|--------|---------|---------|------|-------|
| **Chatterbox Italian** | 9/10 | 100-150ms | 200MB | Primary |
| **Piper (paola-medium)** | 7.5/10 | 50ms | 60MB | Fallback |
| **macOS say** | 5/10 | 30ms | 0 | Last resort |

### NLU (4-Layer Pipeline) - ~100-120ms totali
| Layer | Tecnologia | Latenza | Scopo |
|-------|------------|---------|-------|
| **L1** | Regex patterns | ~1ms | Implicit intent (idiomi italiani) |
| **L2** | spaCy NER | ~20ms | Entity extraction |
| **L3** | UmBERTo | ~80ms | Intent classification |
| **L4** | Context Manager | ~5ms | Session state + slot filling |

### Dialogue Management
- **State Machine**: `booking_state_machine.py`
- **Orchestrator**: `orchestrator.py` (4-layer routing)
- **Session TTL**: 10 minuti
- **Disambiguazione**: data_nascita → soprannome fallback

### LLM Integration
| Provider | Model | Uso |
|----------|-------|-----|
| **Groq** | llama-3.3-70b-versatile | Fallback L4, FAQ complesse |

---

## Knowledge Base

### Architettura FAQ

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXION FAQ SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  SQLite DB  │───▶│  Variables  │───▶│  FAQ Text   │     │
│  │  (source)   │    │  {{...}}    │    │  (output)   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
│  Esempio:                                                   │
│  DB: servizi.nome = "Taglio Uomo", servizi.prezzo = 18     │
│  Template: "Il {{SERVIZIO}} costa {{PREZZO}}€"             │
│  Output: "Il Taglio Uomo costa 18€"                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Sistema Variabili DB

**IMPORTANTE**: Le FAQ NON sono statiche. Vengono generate dinamicamente usando variabili popolate dal database SQLite.

| Variabile | Tabella DB | Campo | Esempio |
|-----------|------------|-------|---------|
| `{{NOME_ATTIVITA}}` | `setup` | `business_name` | "Salone Maria" |
| `{{INDIRIZZO}}` | `setup` | `address` | "Via Roma 15, Milano" |
| `{{TELEFONO}}` | `setup` | `phone` | "02 1234567" |
| `{{LISTA_SERVIZI}}` | `servizi` | `nome, prezzo, durata` | "Taglio €18, Piega €20..." |
| `{{ORARI_APERTURA}}` | `orari` | `giorno, apertura, chiusura` | "Lun-Ven 9-19, Sab 9-13" |
| `{{LISTA_OPERATORI}}` | `operatori` | `nome, specializzazione` | "Marco (colorista), Sara..." |
| `{{POLITICA_DISDETTA}}` | `setup` | `cancellation_policy` | "Gratuita entro 24h" |

### Retrieval Strategy
1. **Keyword Match** (<5ms) - Pattern predefiniti
2. **Semantic Search** (~50ms) - FAISS + Sentence-Transformers
3. **Groq Fallback** (~500ms) - Per query complesse

### Storage
- **Format**: SQLite (`faq_template` table) + JSON/MD files
- **Vector DB**: FAISS (in-memory)
- **Embeddings**: sentence-transformers 2.2.2

---

## Infrastructure

### Deployment Target
| Platform | Bundle | Status |
|----------|--------|--------|
| **macOS** | .dmg, .app | ✅ Primary |
| **Windows** | .msi, .exe | ✅ Supported |
| **Linux** | .deb, .AppImage | ✅ Supported |

### Porte Locali
| Servizio | Porta | Scopo |
|----------|-------|-------|
| Vite Dev | 1420 | Frontend development |
| HTTP Bridge | 3001 | MCP/Claude Code integration |
| Voice Pipeline | 3002 | Python voice agent |

### Auto-Update
- **Provider**: GitHub Releases
- **Plugin**: tauri-plugin-updater 2.0
- **Signing**: Preparato per notarization macOS

---

## Testing

| Tipo | Framework | Coverage |
|------|-----------|----------|
| **E2E** | Playwright | 8/8 smoke tests |
| **E2E** | WebdriverIO | Windows/Linux |
| **Unit** | cargo test | Rust backend |
| **Unit** | pytest | Voice agent |
| **CI/CD** | GitHub Actions | release-full.yml |

---

## Fasi Progetto

| Fase | Nome | Status | Stack Impact |
|------|------|--------|--------------|
| 0-4 | Core CRM + Booking | ✅ | Tauri + React + SQLite |
| 5 | Loyalty + Packages | ✅ | State machine |
| 6 | E-Invoicing | ✅ | XML FatturaPA |
| 7 | Voice Agent + WhatsApp | ✅ | Python + Groq + Chatterbox |
| 8 | Build + Licenze | 📋 | Keygen.sh |
| 9 | Moduli Verticali | 📋 | Domain extensions |

---

*Generato: 2026-01-15*
