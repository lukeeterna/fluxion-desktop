# FLUXION ENTERPRISE - Master Orchestrator v2

**LEGGIMI SEMPRE PER PRIMO**

Sono il cervello del progetto. Coordino agenti, gestisco stato, ottimizzo token.

---

## PROGETTO IN BREVE

**FLUXION**: Gestionale desktop enterprise per PMI italiane

- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Tailwind CSS 3.4
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Modello**: Licenza annuale desktop (NO SaaS, NO commissioni)

---

## 🤖 PROTOCOLLO SVILUPPO AUTONOMO (PERMANENTE)

> **Claude Code è l'ORCHESTRATORE**. Coordina agenti, sviluppa, testa e avanza autonomamente.

### Principi Fondamentali

1. **ORCHESTRATORE**: Coordino 16 agenti specializzati (vedi `.claude/agents/`)
2. **SVILUPPO AUTONOMO**: Sviluppo con agenti, senza attendere istruzioni step-by-step
3. **TEST SU iMAC**: Testo via SSH + MCP Server prima di far testare all'utente
4. **CI/CD OBBLIGATORIO**: Push + verifica GitHub Actions prima di ogni test utente
5. **SESSIONI SALVATE**: Ogni milestone → salvo sessione in `docs/sessions/`
6. **CLAUDE.MD AGGIORNATO**: Aggiorno questo file ad ogni avanzamento significativo

### Infrastruttura Autonoma

```yaml
SSH iMac:
  host: imac (192.168.1.2)
  user: gianlucadistasi
  key: ~/.ssh/id_ed25519
  uso: git pull + npm run tauri dev + MCP server

MCP Server:
  path: mcp-server-ts/
  porta: 5000
  tools: take_screenshot, get_dom_content, execute_script, mouse_click, type_text, key_press, ping, get_app_info
  agent: SystemManagementAgent (health checks, auto-recovery, metrics)

HTTP Bridge (MCP ↔ Tauri):
  file: src-tauri/src/http_bridge.rs
  porta: 3001
  endpoints: 12 REST (/health, /api/mcp/*)
  sicurezza: solo debug builds (#[cfg(debug_assertions)])
  dipendenze: axum 0.7, tower-http 0.5
  flusso: MCP(5000) → HTTP Bridge(3001) → window.eval() → WebView

CI/CD GitHub Actions:
  workflow: .github/workflows/ci.yml
  os: macOS, Windows, Linux
  controllo: build, lint, type-check
```

### Workflow Autonomo

```bash
# 1. Sviluppo con agente appropriato
@agent:rust-backend "Implementa feature X"

# 2. Commit + Push
git add . && git commit -m "feat: descrizione" && git push

# 3. Attendi CI/CD (leggi log se fallisce)
gh run list --limit 1

# 4. Test su iMac via SSH
ssh imac "cd /Volumes/MacSSD\ -\ Dati/fluxion && git pull"
# MCP tools per test automatici

# 5. Salva sessione
docs/sessions/YYYY-MM-DD-HH-MM-descrizione.md

# 6. Aggiorna CLAUDE.md
```

### Quando Coinvolgere l'Utente

- **Decisioni architetturali** che cambiano direzione progetto
- **Errori CI/CD irrisolvibili** dopo 3 tentativi
- **Test manuali richiesti** (interazione fisica, dispositivi esterni)
- **Conferma milestone** prima di procedere a fase successiva

---

## ⚠️ REGOLA IMPERATIVA: CI/CD + LIVE TESTING

> **OBBLIGATORIO**: Dopo OGNI implementazione significativa, seguire questo workflow PRIMA di far testare all'utente.

### FASE 1: CI/CD (Compilazione Automatizzata)

```bash
# Workflow OBBLIGATORIO:
1. git add . && git commit -m "descrizione"
2. git push origin master
3. Attendere esito GitHub Actions (CI/CD)
4. Solo se CI/CD PASSA → procedere a Fase 2
```

**Se CI/CD FALLISCE:**
1. NON far testare all'utente
2. Leggere i log di GitHub Actions
3. Fixare gli errori
4. Pushare e attendere nuovo esito

### FASE 2: AI Live Testing (Test Funzionali via MCP)

> **Documentazione completa:** `docs/AI-LIVE-TESTING.md`

```bash
# Su iMac (macchina di test):
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull
npm install
npm run tauri dev

# Claude Code esegue test automatici via MCP:
# - take_screenshot() → Verifica UI
# - executeScript() → Test funzionali
# - Documenta errori automaticamente
```

**Test da eseguire (Claude Code):**
1. **Visual**: Screenshot di ogni pagina principale
2. **Funzionali**: User flow completi (CRUD, prenotazioni, cassa)
3. **Errori**: Input invalidi, edge case
4. **Performance**: Tempi di risposta < 1s

**Output:**
- `test-reports/error_YYYYMMDD_HHMMSS.json` per ogni errore
- `test-reports/summary_YYYYMMDD.html` report finale

### Perché questo workflow è imperativo:
- CI/CD → Garantisce compilazione su tutti i 3 OS
- Live Testing → Trova bug funzionali che CI/CD non vede
- Documentazione automatica → Nessun bug sfugge
- L'utente testa SOLO codice verificato

---

## STATO CORRENTE

```yaml
fase: 7
nome_fase: "Voice Agent + WhatsApp + FLUXION IA"
data_inizio: 2025-12-30
ultimo_aggiornamento: 2026-01-09T22:30:00
ci_cd_run: "#150 SUCCESS (8/8 jobs)"
completato:
  # >>> DETTAGLIO COMPLETO: docs/context/COMPLETED-PHASES.md <<<

  # Sommario Fasi (0-7)
  - Fase 0: Setup (Tauri 2.x, shadcn/ui, SQLite, Git)
  - Fase 1: Layout + Navigation (6 routes, Sidebar, Header)
  - Fase 2: CRM Clienti (CRUD, Zod, TanStack Query)
  - Fase 3: Calendario + Booking (18 commands, conflict detection)
  - Fase 4: Fluxion Care (Support Bundle, Backup/Restore, Diagnostics)
  - Fase 5: Quick Wins Loyalty (18 commands, Pacchetti, WhatsApp QR Kit)
  - Fase 6: Fatturazione Elettronica (14 commands, FatturaPA XML)
  - Fase 7: WhatsApp + RAG + FLUXION IA (in corso)

  # Migrations: 001-011 (vedi COMPLETED-PHASES.md per dettagli)
  # Tauri Commands: 127+ totali (+7 voice_pipeline)
  # CI/CD: Run #150 SUCCESS su 3 OS (2026-01-09)
  # HTTP Bridge: implementato (porta 3001)
  # Voice Pipeline: Python + 7 Tauri commands (porta 3002)

in_corso: |
  # E2E Testing Setup (2026-01-09)

  ## COMPLETATO:
  - 33 data-testid aggiunti in 9 componenti React
  - 5 WebDriverIO spec files (booking, crm, invoice, cashier, voice)
  - wdio.conf.ts configurato per Tauri
  - tauri-plugin-automation installato (feature e2e)

  ## BLOCCATO:
  - CrabNebula 403 "Unauthorized organization"
  - macOS WebDriver richiede subscription CrabNebula

  ## SOLUZIONE (domani):
  - File: MACOS-E2E-FINAL.md (in Downloads)
  - Approccio: tauri-driver nativo (NO CrabNebula)
  - `cargo install tauri-driver`
  - GitHub Actions macos-12
  - Zero costi, ~20-25 min per run

  ---

  # Voice Pipeline Implementation (2026-01-09)

  ## COMPLETATO OGGI:

  ### 1. Python Voice Agent (`voice-agent/`)
  - `src/groq_client.py`: STT (Whisper) + LLM (Llama 3.3 70B)
  - `src/tts.py`: Piper TTS + macOS fallback
  - `src/pipeline.py`: Orchestrazione STT → LLM → TTS
  - `main.py`: HTTP Server porta 3002
  - Persona italiana "Sara" con system prompt
  - Intent detection (prenotazione, cancellazione, etc.)

  ### 2. Rust Commands (`voice_pipeline.rs`)
  7 Tauri commands per gestire Python server:
  - start_voice_pipeline, stop_voice_pipeline
  - get_voice_pipeline_status, voice_process_text
  - voice_greet, voice_say, voice_reset_conversation

  ### 3. Test su iMac (TUTTI PASS)
  - Groq LLM: ✅ Risposte in italiano
  - TTS macOS: ✅ Audio generato
  - HTTP endpoints: ✅ /health, /greet, /process, /say
  - CI/CD Run #137, #138: ✅ SUCCESS

  ### 4. Architettura Voice
  ```
  Tauri App ──HTTP──▶ Python Voice Server (3002)
                            │
                            ├──▶ Groq Whisper (STT)
                            ├──▶ Groq Llama 3.3 70B (LLM)
                            └──▶ Piper TTS / macOS say
  ```

  ---

  # HTTP Bridge + Voice Agent (2026-01-08)

  ### HTTP Bridge per MCP Integration
  - File: `src-tauri/src/http_bridge.rs`
  - Server Axum su porta 3001
  - 12 REST endpoints per collegare MCP ↔ Tauri
  - Solo in debug builds (#[cfg(debug_assertions)])

  ---

  # RAG Locale + Workflow WhatsApp + Fatturazione SDI (2026-01-07)

  ## DECISIONI PRESE (da NON perdere):

  ### 1. FAQ con Variabili Template
  - File: data/faq_salone_variabili.md
  - Sintassi: {{variabile}} → sostituita con dati da DB
  - Variabili popolate da: tabella impostazioni, servizi, orari
  - Obiettivo: 90% risposte SENZA LLM, solo template matching

  ### 2. RAG Locale Leggero (NO Groq per FAQ standard)
  - Parser file FAQ → estrae Q&A
  - Template engine: sostituisce {{var}} con valori DB
  - Keyword matching per trovare risposta giusta
  - LLM (Groq) SOLO per domande complesse fuori FAQ

  ### 3. Identificazione Cliente WhatsApp
  - Priorità ricerca: nome → soprannome → data_nascita (fallback)
  - Campo soprannome: da aggiungere a tabella clienti
  - Se ambiguo dopo nome+soprannome → chiede data nascita
  - Lookup per numero telefono se già in rubrica

  ### 4. Workflow Conversazionali (già in data/workflows/)
  - intents.json: rilevamento intento
  - identificazione.json: lookup cliente
  - prenotazione.json: flow booking
  - modifica.json: modifica appuntamento
  - disdetta.json: cancellazione

  ### 5. Fiscalità Italiana - CORRISPETTIVI + FATTURE (2026-01-07)

  #### ⚠️ IMPORTANTE: PMI target emettono SCONTRINI, non fatture!
  - Saloni, palestre, cliniche → Registratore Telematico (RT) per scontrini
  - Fatture solo per clienti B2B che le richiedono (raro)

  #### API UFFICIALE AGENZIA ENTRATE (100% GRATIS)
  - **Endpoint**: https://api.corrispettivi.agenziaentrate.gov.it/v1
  - **Spec OpenAPI**: github.com/teamdigitale/api-openapi-samples
  - **Schema XML**: CorrispettiviType_1.0.xsd
  - **Auth**: Certificato digitale + firma XML (PKCS#7)
  - **Costo**: €0 (solo certificato €30/anno)

  #### LIBRERIE OPEN SOURCE
  - **scontrino-digitale** (Python/Node): github.com/Tudor44/scontrino-digitale
  - **fatturazione-elettronica** (topic): github.com/topics/fatturazione-elettronica

  #### SOFTWARE GRATUITI AGENZIA ENTRATE
  1. **FatturAE**: Crea/invia fatture XML a SDI (Java, multipiattaforma)
  2. **Desktop Telematico**: F24, INPS, INAIL (Java standalone)
  3. **F24 Web**: Solo browser, no installazione

  #### DECISIONE FLUXION (POLITICA FREE)

  **SCENARIO REALE PMI**:
  ```
  ┌─────────────────────────────────────────────────────────────────┐
  │                    FLUSSO QUOTIDIANO PMI                        │
  ├─────────────────────────────────────────────────────────────────┤
  │                                                                 │
  │  CLIENTE PAGA                                                   │
  │       │                                                         │
  │       ▼                                                         │
  │  ┌─────────────┐     ┌─────────────────┐     ┌───────────────┐ │
  │  │   FLUXION   │────▶│  RT (Esistente) │────▶│ AdE Corrispet.│ │
  │  │  Gestionale │     │  o RT Virtuale  │     │   Automatico  │ │
  │  └─────────────┘     └─────────────────┘     └───────────────┘ │
  │       │                                                         │
  │       ▼                                                         │
  │  Registra incasso                                               │
  │  + dati cliente                                                 │
  │  + servizio                                                     │
  │                                                                 │
  │  FINE GIORNATA:                                                 │
  │  - RT invia automaticamente corrispettivi a AdE                 │
  │  - FLUXION mostra report incassi/statistiche                    │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
  ```

  **OPZIONI IMPLEMENTAZIONE**:

  | Opzione | Descrizione | Costo | Complessità |
  |---------|-------------|-------|-------------|
  | A | FLUXION = solo gestionale, RT separato | €0 | ✅ Bassa |
  | B | FLUXION + RT Cloud (Effatta, etc.) | €20/mese | 🟡 Media |
  | C | FLUXION = RT virtuale (certificazione AdE) | €0 ma 6+ mesi | 🔴 Altissima |

  **RACCOMANDAZIONE MVP**: Opzione A
  - FLUXION gestisce: clienti, appuntamenti, incassi, statistiche
  - RT esistente (o da acquistare) gestisce: scontrini → AdE
  - Fatture B2B (rare): genera XML + FatturAE Bridge gratuito

  #### FatturAE BRIDGE (per fatture B2B occasionali)
  - Integrato nell'installer FLUXION
  - Rileva OS (Windows/macOS/Linux)
  - Scarica FatturAE se non presente
  - FLUXION genera XML → apre FatturAE → utente clicca Invia
  - 100% GRATUITO

  #### DECISIONE FINALE RT (2026-01-07)
  **CONFERMATA OPZIONE A**: FLUXION = Gestionale puro, RT separato

  Analisi repo scontrino-digitale (github.com/Tudor44/scontrino-digitale):
  - È solo generatore XML corrispettivi, NON controlla RT fisici
  - NON risolve il problema driver hardware

  Motivazioni Opzione A:
  - 50+ modelli RT con driver diversi = incubo compatibilità
  - Installazione fisica NON gestibile da remoto
  - RT Cloud costa €20-30/mese (contro policy FREE)
  - PMI hanno GIÀ RT funzionante → non serve sostituirlo

  **FLUXION MVP**:
  - Registra incassi per statistiche/CRM ✅
  - RT esistente cliente gestisce scontrini → AdE (separato)
  - Nessuna integrazione hardware RT

  **FUTURO (post-MVP, se richiesto)**:
  - Valutare RT Cloud API per clienti che vogliono "tutto in uno"
  - Costo aggiuntivo per il cliente

  ## TODO COMPLETATO (2026-01-07):
  1. ✅ Salvato faq_salone_variabili.md in data/
  2. ✅ Creato sistema template {{var}} → DB (migration 008 + faq_template.rs)
  3. ✅ Aggiunto campo soprannome a clienti (migration + Rust + TypeScript)
  4. ✅ Implementata identificazione cliente WhatsApp (nome→soprannome→data_nascita)
  5. ✅ Ricerca SDI/PEC completata (vedi sopra)
  6. ✅ **DECISIONE FISCALE**: Opzione A - FLUXION = Gestionale puro, RT separato
  7. ✅ Migration 009: tabella incassi + chiusure_cassa + metodi_pagamento
  8. ✅ cassa.rs: 8 Tauri commands (registra_incasso, get_incassi_oggi, chiudi_cassa, etc.)
  9. ✅ CassaPage: UI completa registrazione incassi + chiusura giornata
  10. ✅ Route /cassa + voce sidebar

  ## TODO COMPLETATO (2026-01-08):
  11. ✅ Fix DatePicker: min="1900-01-01" per permettere anni come 1945
  12. ✅ Fix Input numerico: value=0 → stringa vuota (no leading zero "010")
  13. ✅ Fix Chiusura Cassa: aggiunto window.alert per feedback utente
  14. ✅ Fix Invalid UUID: Zod schema da .uuid() a .min(1) per mock data
  15. ✅ Migration 010: mock_data.sql con clienti, servizi, operatori, appuntamenti

  ### 8. Architettura Servizi e Licenze (2026-01-08)

  #### FLUXION IA (Groq) - OPZIONE LICENZA
  - **Campo API Key**: SOLO nel Setup Wizard (Step 3), NON nelle Impostazioni
  - **Motivo**: È un'opzione della licenza, il cliente la sceglie all'acquisto
  - **Variabile DB**: `fluxion_ia_key` nella tabella `impostazioni`
  - **Fallback**: Se non presente, legge da .env `GROQ_API_KEY`

  #### WhatsApp - AUTO-START CON FLUXION
  - **Obiettivo**: WhatsApp DEVE partire automaticamente con l'app
  - **Servizio Node.js**: `scripts/whatsapp-service.cjs` (whatsapp-web.js)
  - **Dipendenze**: Devono essere installate con `npm install` durante setup
  - **Configurazione utente**:
    - Numero WhatsApp: inserito nel Setup Wizard
    - Scansione QR: una tantum, sessione persistente in `.whatsapp-session/`
  - **Auto-start TODO**: Tauri spawn child process Node.js all'avvio

  #### Variabili Configurabili (Setup Wizard)
  | Variabile | Step | Descrizione |
  |-----------|------|-------------|
  | nome_attivita | 1 | Nome salone/attività |
  | partita_iva | 1 | P.IVA (opzionale) |
  | telefono | 1 | Telefono (per WhatsApp) |
  | fluxion_ia_key | 3 | API Key per FLUXION IA (opzione licenza) |

  ## PROSSIMO:
  - WhatsApp auto-start: Tauri spawn child process Node.js
  - FatturAE Bridge per fatture B2B occasionali
  - Voice Agent: Groq Whisper STT + Piper TTS

  ### 6. Sistema Fornitori + Comunicazione (2026-01-07)

  #### Obiettivo
  Gestione ordini a fornitori con comunicazione automatizzata via Email e WhatsApp.

  #### Database Schema
  ```sql
  -- Provider email preconfigurati
  CREATE TABLE email_providers (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,           -- Gmail, Libero, Outlook, Aruba, Custom
    smtp_host TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    use_tls INTEGER DEFAULT 1,
    note TEXT
  );

  -- Configurazione email utente
  CREATE TABLE email_config (
    id TEXT PRIMARY KEY,
    provider_id TEXT REFERENCES email_providers(id),
    email TEXT NOT NULL,
    password_encrypted TEXT,      -- Crittografata con key locale
    attivo INTEGER DEFAULT 0,
    testato INTEGER DEFAULT 0,    -- Flag dopo test invio
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- Fornitori
  CREATE TABLE fornitori (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    telefono TEXT,                -- Per WhatsApp
    whatsapp_preferito INTEGER DEFAULT 0,
    categoria TEXT,               -- Prodotti, Attrezzature, Consumabili
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
  );

  -- Template ordini
  CREATE TABLE ordini_template (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    oggetto TEXT,                 -- Subject email
    corpo TEXT NOT NULL,          -- Body con {{variabili}}
    tipo TEXT NOT NULL,           -- 'email' | 'whatsapp'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

  #### Provider Email Preconfigurati (seed)
  | Provider | SMTP Host | Porta | TLS |
  |----------|-----------|-------|-----|
  | Gmail | smtp.gmail.com | 587 | Si |
  | Libero | smtp.libero.it | 465 | Si (SSL) |
  | Outlook/Hotmail | smtp-mail.outlook.com | 587 | Si |
  | Aruba | smtps.aruba.it | 465 | Si (SSL) |
  | Yahoo | smtp.mail.yahoo.com | 587 | Si |
  | Custom | - | - | - |

  #### UI Setup Wizard (Step Email)
  1. Select provider da dropdown
  2. Auto-compila SMTP host/porta
  3. Inserisci email + password
  4. Bottone "Testa Connessione"
  5. Se OK → flag testato = 1

  #### Flow Ordine Fornitore
  1. Seleziona fornitore
  2. Componi ordine (template o manuale)
  3. Scegli canale: Email o WhatsApp
  4. Preview messaggio
  5. Invia (o copia per WhatsApp manuale)

  #### Rust Crate
  - `lettre` per invio SMTP
  - Password crittografata con `ring` o `aes-gcm`

  ### 7. Remote Assistance System (2026-01-07)

  #### Decisione Architetturale
  **MVP**: Tailscale + SSH (Zero-cost, P2P, crittografato)
  **Enterprise**: RustDesk self-hosted (GUI, cross-platform)

  #### Perché Tailscale + SSH
  - **Costo**: $0 (fino 100 device)
  - **Setup**: 1 comando per macchina
  - **Sicurezza**: WireGuard encryption, no port forwarding
  - **Latenza**: P2P diretto, <50ms tipico
  - **NAT traversal**: Automatico, funziona dietro qualsiasi firewall

  #### Flusso MVP
  ```
  CLIENTE                           SUPPORTO (NOI)
  ────────                          ─────────────
  1. Installa Tailscale             1. Già ha Tailscale
  2. Si autentica                   2. Vede device nella rete
  3. Accetta invito team            3. SSH verso cliente
  4. [opzionale] Condivide          4. Accesso terminale
     schermo via Meet/Zoom             + trasferimento file
  ```

  #### Setup Cliente (1 minuto)
  ```bash
  # macOS
  brew install tailscale
  tailscale up --authkey=tskey-xxx --accept-routes

  # Windows (installer)
  # Download da tailscale.com, login con link fornito
  ```

  #### Comandi Supporto
  ```bash
  # Connetti a cliente
  ssh cliente@100.x.y.z

  # Trasferisci file
  scp fix.sh cliente@100.x.y.z:~/Desktop/

  # Vedi tutti i device
  tailscale status
  ```

  #### Tabella Comparativa Soluzioni
  | Soluzione | Costo | Setup | GUI | Note |
  |-----------|-------|-------|-----|------|
  | Tailscale+SSH | Free | 1 min | No | MVP perfetto |
  | RustDesk | Free | 5 min | Si | Self-hosted |
  | TeamViewer | $$$ | 2 min | Si | Costoso per business |
  | AnyDesk | $$ | 2 min | Si | Medio costo |
  | Parsec | Free | 3 min | Si | Gaming-focused |

  #### Roadmap Remote Assist
  - **MVP (Fase 8)**: Tailscale + SSH, istruzioni in-app
  - **v1.1**: RustDesk integration per GUI
  - **v2.0**: WebRTC P2P nativo (se necessario)

  #### UI in FLUXION (Impostazioni → Assistenza Remota)
  - Stato Tailscale: Connesso/Disconnesso
  - Device ID: 100.x.y.z
  - Bottone "Richiedi Assistenza" → genera ticket + notifica supporto
  - Log sessioni assistenza

  #### MCP Server per Assistenza Avanzata (2026-01-08)

  **Obiettivo**: Server MCP integrato in FLUXION che permette al supporto di:
  1. **Visualizzare l'app** - Screenshot automatici della UI
  2. **Interagire con l'app** - Click, input, navigazione remota
  3. **Identificare errori** - Cattura errori frontend/backend in tempo reale
  4. **Log locale** - Salva log dettagliati sul PC cliente
  5. **Prelievo log** - Trasferisce log al supporto per analisi
  6. **Debug remoto** - Ispeziona stato app, database, configurazioni

  **Architettura**:
  ```
  ┌─────────────────────────────────────────────────────────────────┐
  │                    PC CLIENTE                                   │
  ├─────────────────────────────────────────────────────────────────┤
  │  FLUXION App                                                    │
  │       │                                                         │
  │       ▼                                                         │
  │  ┌─────────────┐     ┌─────────────────┐     ┌───────────────┐ │
  │  │ MCP Server  │◄───▶│  Log Collector  │────▶│ logs/local/   │ │
  │  │ (localhost) │     │  + Screenshot   │     │ YYYY-MM-DD/   │ │
  │  └─────────────┘     └─────────────────┘     └───────────────┘ │
  │       │                                                         │
  │       │ Tailscale VPN (P2P encrypted)                          │
  │       ▼                                                         │
  └───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                    PC SUPPORTO                                  │
  ├─────────────────────────────────────────────────────────────────┤
  │  Claude Code + MCP Client                                       │
  │       │                                                         │
  │       ▼                                                         │
  │  - mcp_screenshot() → visualizza UI cliente                     │
  │  - mcp_click(x, y) → interagisce con app                        │
  │  - mcp_get_logs() → preleva log per analisi                     │
  │  - mcp_get_db_state() → ispeziona database                      │
  │  - mcp_run_diagnostic() → esegue diagnostica completa           │
  └─────────────────────────────────────────────────────────────────┘
  ```

  **Tools MCP da implementare**:
  | Tool | Descrizione |
  |------|-------------|
  | `screenshot` | Cattura screenshot UI corrente |
  | `click` | Simula click su coordinate/elemento |
  | `type` | Inserisce testo in input |
  | `navigate` | Naviga a route specifica |
  | `get_logs` | Recupera log applicazione |
  | `get_errors` | Lista errori recenti |
  | `get_db_query` | Esegue query SQL read-only |
  | `get_config` | Legge configurazione app |
  | `run_diagnostic` | Esegue suite diagnostica completa |

  **Sicurezza**:
  - MCP server attivo SOLO durante sessione assistenza
  - Autenticazione via token temporaneo
  - Tutte le operazioni loggate
  - Query DB solo SELECT (no modifiche)
  - Utente deve approvare connessione

  **Implementazione**: PRIORITÀ ALTA - Necessario per debug remoto

  #### Bug Irrisolto: Dropdown z-index in Dialog (2026-01-08)

  **Problema**: I menu Select dentro Dialog si sovrappongono al contenuto invece di apparire sopra.

  **Tentativi falliti**:
  | Tentativo | Approccio | Risultato |
  |-----------|-----------|-----------|
  | 1 | z-index: z-[100] su SelectContent | ❌ Non funziona |
  | 2 | z-index: z-[9999] su SelectContent | ❌ Non funziona |
  | 3 | position="popper" + CSS !important | ❌ Non funziona |
  | 4 | Rimozione Portal (render inline) | ❌ Non funziona |

  **Analisi**: Il problema sembra essere legato al WebView di Tauri su macOS Monterey.
  Il CSS stacking context non si comporta come in un browser standard.

  **Decisione**: Implementare MCP Server per debug remoto visivo per risolvere
  questo e futuri problemi UI.

prossimo: |
  Fase 7 - Voice Agent
  - Voice Agent: Groq Whisper STT + Piper TTS
  - Integrazione VoIP Ehiweb
  - Waitlist con priorità VIP

bug_da_fixare: |
  ## BUG IDENTIFICATI DA SCREENSHOT (2026-01-09)

  ### CRITICI (Bloccano release)
  - [ ] BUG-V2: Voice Agent conversazione non si avvia (spinner infinito)

  ### ALTI (Fix prima di release)
  - [ ] BUG-V1: Nome assistente "Sara" → cambiare in "Paola" (voce italiana)
  - [ ] BUG-V3: LLM mostra "Groq Llama 3.3 70B" → mostrare "FLUXION AI"

  ### MEDI (Miglioramenti UX)
  - [ ] BUG-F1: Icone header (campana, profilo, menu) non funzionali
  - [ ] BUG-F3: Utente footer sidebar non collegato a profilo/impostazioni

  ### Screenshot riferimento
  - /tmp/re12_extract/Schermata 2026-01-09 alle 18.27.48.png (Fatturazione)
  - /tmp/re12_extract/Schermata 2026-01-09 alle 18.30.10.png (Voice Agent)

requisiti_sistema:
  windows: "Windows 10 build 1809+ o Windows 11"
  macos: "macOS 12 Monterey o superiore (NO Big Sur)"
  nota: "Tauri 2.x richiede WebKit API moderne"
FASI PROGETTO
Fase	Nome	Status	Durata	Note
0	Setup Iniziale	✅ COMPLETATO	1 sett	Tauri + shadcn + DB
1	Layout + Navigation	✅ COMPLETATO	1 giorno	Sidebar + Router
2	CRM Clienti	✅ COMPLETATO	1 giorno	CRUD completo
3	Calendario + Booking	✅ COMPLETATO	1 giorno	Conflict detection
4	Fluxion Care (Stabilità)	✅ COMPLETATO	1 giorno	Support + Diagnostics
5	Quick Wins (Loyalty + Pacchetti)	✅ COMPLETATO	1 giorno	18 commands + UI + QR Kit
6	Fatturazione Elettronica	✅ COMPLETATO	1 giorno	14 commands + FatturaPA XML
7	WhatsApp + Voice Agent	📋 TODO	3 giorni	whatsapp-web.js + RAG + Groq + Piper
8	Build + Licenze + Feature Flags	📋 TODO	3 giorni	Release + Keygen + Feature Flags per categorie
9	Ricerca Mercato + Moduli Verticali	📋 TODO	-	Vedi dettaglio sotto

## FASE 9 - MODULI VERTICALI (POST-RELEASE BASE)

**⚠️ PREREQUISITO OBBLIGATORIO**: Prima di implementare i moduli verticali, effettuare ricerca di mercato con GPT 5.2 (o modello più recente disponibile) per identificare:
- Esigenze specifiche di ogni categoria
- Funzionalità loyalty adatte per settore
- Campi/dati specifici necessari
- Workflow operativi tipici

### Categorie Target (NECESSITA PRIMA RICERCA QUESTI SONO INDICATIVI)
| Codice | Categoria | Modulo | Campi Specifici |
|--------|-----------|--------|-----------------|
| BEAUTY | Parrucchieri, Estetisti | FLUXION-BEAUTY | Prodotti, Trattamenti |
| AUTO | Meccanici, Elettrauto, Carrozzieri | FLUXION-AUTO | Targa, Telaio, Km, Modello, Ricambi |
| WELLNESS | Palestre, Fisioterapisti, SPA | FLUXION-WELLNESS | Abbonamenti, Schede allenamento |
| MEDICAL | Studi medici, Dentisti | FLUXION-MEDICAL | Cartella clinica, Anamnesi |

### Sistema Feature Flags
```rust
// Esempio struttura licenza
struct License {
    business_type: BusinessType,  // BEAUTY, AUTO, WELLNESS, etc.
    modules: Vec<Module>,         // Moduli abilitati
    features: Vec<FeatureFlag>,   // Feature specifiche
    expires_at: DateTime,
}

enum FeatureFlag {
    Magazzino,
    SchedaVeicolo,
    Abbonamenti,
    CartellaCLlinica,
    FatturazioneElettronica,
    VoiceAgent,
    WhatsAppIntegration,
}
```

### Ricerca da Effettuare (GPT 5.2)
1. **BEAUTY**: Quali loyalty program funzionano meglio nei saloni? Tessera timbri, sconti compleanno, referral?
2. **AUTO**: Come gestiscono i promemoria tagliando/revisione? Quali dati veicolo sono essenziali?
3. **WELLNESS**: Abbonamenti mensili vs pacchetti? Come tracciare presenze?
4. **MEDICAL**: Requisiti GDPR sanitario, conservazione dati, consensi specifici?

> **NOTA**: FOOD (ristoranti/bar) ESCLUSO dal target - troppi competitor SaaS nel settore (TheFork, Quandoo, etc.)
WORKFLOW SVILUPPO
Ambiente Multi-Macchina
text
macbook_sviluppo:
  ruolo: "Sviluppo + Debug"
  attività:
    - Scrittura codice Rust/React/TypeScript
    - Debug e review
    - Git operations
    - Installazione dipendenze
  nota: "NON può eseguire npm run tauri dev (macOS 12 Monterey)"

imac_monterey:
  ruolo: "Testing + Run"
  attività:
    - Esecuzione npm run tauri dev
    - Test funzionalità UI
    - Verifiche integrazione
    - Screenshot e feedback
  requisiti: "macOS 12 Monterey o superiore"
Workflow Tipico
MacBook: Scrivi/modifica codice

Sync: git push (automatico MacBook → GitHub → iMac)

iMac: git pull + npm run tauri dev

Feedback: Riporta errori/bug

Loop: Torna a step 1

GIT WORKFLOW (SEMPRE DOPO MODIFICHE)
⚠️ REGOLA FONDAMENTALE
Dopo OGNI modifica al codice:

bash
git add .
git commit -m "descrizione modifiche"
git push
Perché obbligatorio:

Sincronizza MacBook → GitHub → iMac

Backup continuo cloud

Tracciabilità completa

Zero rischio perdita lavoro

Repository: https://github.com/lukeeterna/fluxion-desktop (privato)

Su iMac per sincronizzare:

bash
cd /Volumes/MacSSD\ -\ Dati/fluxion
git pull
npm run tauri dev
SISTEMA AGENTI (15 AGENTI COMPLETI) + PARLANT

## Regola d'Oro
**UN SOLO AGENTE** alla volta. MAI confusione.

## Parlant Integration (v1.0 - 2026-01-03)
**Coerenza cross-session e guidelines enforcement**

Struttura:
- `.parlant/config.json` - Configurazione CEO + agenti specializzati
- `.parlant/decision-log.md` - ADR (Architecture Decision Records)
- `.parlant/agent-guidelines.md` - Linee guida per ogni agente

**CEO Agent** (Master Orchestrator):
- Coordina tutti gli agenti specializzati
- Mantiene coerenza architetturale tra sessioni
- Acquisisce log CI/CD autonomamente (GitHub API)
- Registra decisioni critiche in decision-log
- Evita loop infiniti (max 3 tentativi)

**Coherence Rules**:
1. Architectural decisions → Documentate in ADR
2. Breaking changes → Review architect + code-reviewer
3. CI/CD failures → Auto-acquire logs + max 3 fix attempts
4. Cross-agent handoff → Preserve context via session logs

Come Funziona
Tu chiedi qualcosa

Orchestrator (CEO) analizza

Seleziona agente corretto (consulta `.parlant/config.json`)

Agente lavora con SUO contesto + guidelines (`.parlant/agent-guidelines.md`)

Claude Code DEVE chiedere: "✅ SALVO TUTTO?"

Tu rispondi "sì" → aggiorna CLAUDE.md + sessione + decision log + git push

Tabella Routing Agenti (24 AGENTI MAPPATI)
Keyword Richiesta	Agente	File Contesto	Quando Usare
gh, github cli, gh pr, gh issue, workflow, actions	github-cli-engineer	CLAUDE-GITHUB-CLI.md	GitHub CLI, CI/CD, PR automation
tauri, rust, backend, api, sqlite	rust-backend	CLAUDE-BACKEND.md	Tauri commands, SQLite, migrations
react, component, hook, state, frontend	react-frontend	CLAUDE-FRONTEND.md	Componenti React, hooks, TanStack Query
design, colori, layout, css, tailwind	ui-designer	CLAUDE-DESIGN-SYSTEM.md + FLUXION-DESIGN-BIBLE.md	Styling, palette, spacing
voice, whisper, tts, chiamata, pipecat	voice-engineer	CLAUDE-VOICE.md	Voice Agent, Groq, Piper TTS
whatsapp, messaggio, notifica, template, qr	integration-specialist	CLAUDE-INTEGRATIONS.md	WhatsApp, API esterne
fattura, xml, sdi, partita iva, fiscale	fatture-specialist	CLAUDE-FATTURE.md	Fatturazione elettronica
database, schema, migration, sql, tabelle	database-engineer	CLAUDE-BACKEND.md	Schema DB, migrations, query
build, release, deploy, update, licenza	devops / release-engineer	CLAUDE-DEPLOYMENT.md	Build, CI/CD, deploy
test, e2e, automation, playwright, tauri-driver	e2e-tester	docs/testing/e2e/	Test automation end-to-end
performance, ottimizza, lento, latency, memory	performance-engineer	—	Ottimizzazione performance
security, audit, xss, sql injection, vulnerabilità	security-auditor	—	Security audit, penetration test
review, refactor, code quality, bug, lint	code-reviewer	tutti i file	Code review, refactoring
architettura, decisione, struttura, piano, roadmap	architect	CLAUDE-INDEX.md	Decisioni architetturali
loyalty, fidelizzazione, referral, pacchetti, tessera	integration-specialist	FLUXION-LOYALTY-V2.md	Loyalty program, referral
remote assist, support, diagnostics, backup, log	devops	FLUXION-REMOTE-ASSIST.md	Support bundle, diagnostics
migration, schema version, refinery, alter table	migration-specialist	migration-specialist.md	SQLite migrations, schema evolution
ipc, invoke, specta, type mismatch, camelCase	tauri-ipc-specialist	tauri-ipc-specialist.md	Type-safe IPC, specta bindings
z-index, dropdown, portal, stacking, webview	tauri-webview-specialist	tauri-webview-specialist.md	WebView CSS issues, z-index fix
esm, commonjs, require, import error, bundle	module-bundler-specialist	module-bundler-specialist.md	ESM/CJS resolution, Vite config
screenshot, visual test, pixel diff, regression	visual-debugger	visual-debugger.md	Visual testing, screenshot comparison
seed, fixture, mock data, italian names, test db	test-data-manager	test-data-manager.md	Seed data, fixtures, fake Italian data
hot reload, hmr, cargo watch, slow build	dev-environment-specialist	dev-environment-specialist.md	Dev server, incremental builds
mcp, remote debug, claude tool, socket server	mcp-engineer	mcp-engineer.md	MCP Server, remote debugging
Lista Completa Agenti (.claude/agents/) - 24 TOTALI
architect.md - Decisioni architetturali e roadmap

code-reviewer.md - Code review e quality assurance

database-engineer.md - Schema DB, migrations, query optimization

debugger.md - Debug sistematico (Debug Cascade Framework)

devops.md - Infra, CI/CD, deployment

github-cli-engineer.md - GitHub CLI automation, CI/CD, PR/Issue management

e2e-tester.md - Test automation end-to-end

fatture-specialist.md - Fatturazione elettronica XML/SDI

integration-specialist.md - WhatsApp, API, Loyalty, Referral

performance-engineer.md - Ottimizzazione performance

react-frontend.md - React, TypeScript, TanStack Query

release-engineer.md - Release management, versioning

rust-backend.md - Rust, Tauri, SQLite

security-auditor.md - Security audit e penetration testing

ui-designer.md - Design system, palette, componenti

voice-engineer.md - Voice Agent, STT, TTS, VoIP

migration-specialist.md - SQLite migrations, schema versioning, refinery pattern

tauri-ipc-specialist.md - Type-safe IPC, specta, snake_case/camelCase

tauri-webview-specialist.md - WebView z-index, portal issues, stacking context

module-bundler-specialist.md - ESM/CJS resolution, Vite build config

visual-debugger.md - Screenshot capture, pixel diff, visual regression

test-data-manager.md - Seed data, Italian fixtures, factory pattern

dev-environment-specialist.md - Hot reload, cargo-watch, HMR optimization

mcp-engineer.md - MCP Server, remote debugging, Claude/Cursor integration

Invocazione Agente
text
@agent:<nome-agente> Descrizione task
Esempio:

text
@agent:rust-backend Crea lo schema SQLite per la tabella clienti
STRUTTURA FILE (AGGIORNATA v2)
text
FLUXION/
├── CLAUDE.md                      ← SEI QUI (leggi sempre primo)
├── PROMPT-ENTERPRISE.md           ← Prompt avvio Claude Code
├── .env                           ← Variabili ambiente
├── QUICKSTART.md                  ← Guida avvio rapido
├── docs/
│   ├── context/                   ← Contesto per agenti (11 file)
│   │   ├── CLAUDE-INDEX.md        ← Mappa navigazione
│   │   ├── CLAUDE-BACKEND.md      ← Rust + Tauri + SQLite
│   │   ├── CLAUDE-FRONTEND.md     ← React + TypeScript
│   │   ├── CLAUDE-DESIGN-SYSTEM.md ← Design tokens
│   │   ├── CLAUDE-INTEGRATIONS.md ← WhatsApp + API
│   │   ├── CLAUDE-VOICE.md        ← Voice Agent (voce Paola)
│   │   ├── CLAUDE-FATTURE.md      ← Fatturazione elettronica
│   │   ├── CLAUDE-DEPLOYMENT.md   ← Build + Release
│   │   ├── FLUXION-LOYALTY-V2.md  ← Loyalty/Referral/Pacchetti ⭐ NUOVO
│   │   └── FLUXION-REMOTE-ASSIST.md ← Remote Assist/Support ⭐ NUOVO
│   ├── sessions/                  ← Log sessioni (auto-generati)
│   │   └── YYYY-MM-DD-HH-MM-descrizione.md
│   ├── testing/e2e/               ← E2E test automation docs
│   └── FLUXION-DESIGN-BIBLE.md    ← Bibbia visiva completa
├── .claude/
│   ├── agents/                    ← 15 Agenti specializzati ⭐
│   │   ├── architect.md
│   │   ├── code-reviewer.md
│   │   ├── database-engineer.md   ⭐ NUOVO
│   │   ├── debugger.md
│   │   ├── devops.md
│   │   ├── e2e-tester.md          ⭐ NUOVO
│   │   ├── fatture-specialist.md
│   │   ├── integration-specialist.md
│   │   ├── performance-engineer.md ⭐ NUOVO
│   │   ├── react-frontend.md
│   │   ├── release-engineer.md    ⭐ NUOVO
│   │   ├── rust-backend.md
│   │   ├── security-auditor.md    ⭐ NUOVO
│   │   ├── ui-designer.md
│   │   └── voice-engineer.md
│   └── mcp_config.json            ← MCP servers config
├── .github/
│   └── workflows/
│       └── auto-save-context.yml  ← GitHub Actions (auto-save) ⭐ NUOVO
└── src/                           ← Codice sorgente
WORKFLOW SESSIONE (⚠️ RAFFORZATO)
Inizio Sessione
Leggi CLAUDE.md

Controlla stato_corrente

Identifica task da completare

Seleziona agente appropriato

Carica contesto minimo

Durante Sessione
Un agente alla volta

Test incrementali

Debug con debugger.md se errori

Fine Sessione (⚠️ OBBLIGATORIO - WORKFLOW AUTOMATIZZATO)
Claude Code DEVE chiedere ESPLICITAMENTE:

text
✅ Milestone completata: [descrizione breve]

SALVO TUTTO? (aggiorna CLAUDE.md + crea sessione + git commit)

Rispondi 'sì' per confermare.
SE ricevi "sì", esegui AUTOMATICAMENTE:

Aggiorna CLAUDE.md (sezione stato_corrente):

Sposta task da in_corso a completato

Aggiorna prossimo

Timestamp ISO 8601

Crea file sessione in docs/sessions/:

text
docs/sessions/2026-01-01-17-45-descrizione-milestone.md
Contenuto:

text
# Sessione: [descrizione milestone]

**Data**: 2026-01-01T17:45:00
**Fase**: 3
**Agente**: rust-backend

## Modifiche
- [lista modifiche]

## Test
- [risultati test]

## Screenshot
- [path screenshot se presenti]
Git commit automatico:

bash
git add .
git commit -m "sessione: [descrizione milestone]"
git push
Conferma all'utente:

text
✅ Tutto salvato:
- CLAUDE.md aggiornato
- Sessione creata: docs/sessions/2026-01-01-17-45-descrizione.md
- Git push completato
⚠️ QUESTA REGOLA È INVIOLABILE. Non saltare mai questo workflow.

OTTIMIZZAZIONE TOKEN
Regole
NON leggere tutto - Solo file necessari

Usa MCP filesystem - Accesso diretto

Agenti specializzati - Dominio specifico

State in YAML - Compatto

Sessioni separate - Non accumulare storia

Cosa Leggere per Task
Task	File da leggere
Setup progetto	CLAUDE.md + QUICKSTART.md
Backend/Database	CLAUDE-BACKEND.md
Componente React	CLAUDE-FRONTEND.md + CLAUDE-DESIGN-SYSTEM.md
Stile/Layout	CLAUDE-DESIGN-SYSTEM.md + FLUXION-DESIGN-BIBLE.md
Voice Agent	CLAUDE-VOICE.md
WhatsApp/Template/QR	CLAUDE-INTEGRATIONS.md
Loyalty/Referral/Pacchetti	FLUXION-LOYALTY-V2.md ⭐
Remote Assist/Support	FLUXION-REMOTE-ASSIST.md ⭐
Fatture	CLAUDE-FATTURE.md
Build/Deploy	CLAUDE-DEPLOYMENT.md
VARIABILI AMBIENTE
bash
# AI/LLM
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556

# GitHub
GITHUB_TOKEN=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
GITHUB_REPO=fluxion-desktop

# Licenze
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae

# VoIP
VOIP_PROVIDER=ehiweb
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it

# TTS Voice
TTS_VOICE_MODEL=it_IT-paola-medium  # Voce femminile (default)

# WhatsApp
WHATSAPP_PHONE=393281536308

# Azienda (test)
AZIENDA_NOME=Automation Business
AZIENDA_PARTITA_IVA=02159940762
AZIENDA_CF=DSTMGN81S12L738L
REGIME_FISCALE=RF19
RIFERIMENTI RAPIDI
Risorsa	Path	Note
**Fasi Completate**	docs/context/COMPLETED-PHASES.md	Storico dettagliato Fase 0-7
**AI Live Testing**	docs/AI-LIVE-TESTING.md	⚠️ OBBLIGATORIO - Test via MCP
Design Bible	docs/FLUXION-DESIGN-BIBLE.md	Mockup completo
Design Tokens	docs/context/CLAUDE-DESIGN-SYSTEM.md	Colori/spacing
Schema DB	docs/context/CLAUDE-BACKEND.md	9 tabelle SQLite
API Reference	docs/context/CLAUDE-INTEGRATIONS.md	WhatsApp
Voice Agent	docs/context/CLAUDE-VOICE.md	Groq + Piper (voce Paola)
Loyalty/Referral	docs/context/FLUXION-LOYALTY-V2.md	⭐ Quick Wins
Remote Assist	docs/context/FLUXION-REMOTE-ASSIST.md	⭐ Support
Ultimo aggiornamento: 2026-01-08T15:00:00