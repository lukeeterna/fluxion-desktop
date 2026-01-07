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

## ⚠️ REGOLA IMPERATIVA: CI/CD PRIMA DEI TEST UTENTE

> **OBBLIGATORIO**: Dopo OGNI implementazione significativa, eseguire i test CI/CD PRIMA di far testare all'utente.

```bash
# Workflow OBBLIGATORIO prima di far testare all'utente:
1. git add . && git commit -m "descrizione"
2. git push origin master
3. Attendere esito GitHub Actions (CI/CD)
4. Solo se CI/CD PASSA → l'utente può testare
```

**Perché è imperativo:**
- Evita sprechi di tempo dell'utente su build rotte
- Identifica errori TypeScript, Rust, ESLint PRIMA
- Garantisce che il codice compili su tutti i 3 OS (macOS, Windows, Linux)
- Test automatizzati trovano bug prima dei test manuali

**Se CI/CD FALLISCE:**
1. NON far testare all'utente
2. Leggere i log di GitHub Actions
3. Fixare gli errori
4. Pushare e attendere nuovo esito
5. Solo quando VERDE → procedere con test utente

---

## STATO CORRENTE

```yaml
fase: 7
nome_fase: "Voice Agent + WhatsApp + FLUXION IA"
data_inizio: 2025-12-30
ultimo_aggiornamento: 2026-01-07T15:30:00
completato:
  # Fase 0 - Setup
  - Struttura directory
  - Design Bible + Documentazione contesto
  - Tauri 2.x inizializzato (React 19 + TypeScript)
  - Dipendenze Node + Rust installate
  - shadcn/ui configurato (18 componenti)
  - Schema database (9 tabelle)
  - Plugin Tauri backend (SQL, FS, Dialog, Store, Opener)
  - Git repository (GitHub: lukeeterna/fluxion-desktop)
  - Workflow multi-macchina (MacBook → GitHub → iMac)

  # Fase 1 - Layout + Navigation
  - main.rs configurato con SQLite (SQLx)
  - MainLayout + Sidebar + Header
  - React Router (6 routes)
  - Palette FLUXION custom (Navy/Cyan/Teal/Purple)
  - 6 pagine navigabili
  - Requisiti sistema documentati (macOS 12+, Windows 10+)

  # Fase 2 - CRM Clienti (100% COMPLETATO)
  - Tauri commands CRUD completi
  - TypeScript types + Zod schemas
  - TanStack Query hooks
  - ClientiPage + ClienteDialog con validazione
  - Soft delete implementato
  - Test CRUD completo su macOS Monterey

  # Fase 3 - Calendario + Booking (100% COMPLETATO)
  - Backend Rust completo (18 Tauri commands)
  - servizi.rs + operatori.rs + appuntamenti.rs
  - CalendarioPage con griglia mensile
  - AppuntamentoDialog con auto-fill
  - Conflict detection automatico
  - Workflow end-to-end: Cliente → Servizio → Operatore → Appuntamento → Calendario
  - File test completo (1139 righe, 20+ test, 31 screenshot)

  # Documentazione Loyalty & Marketing (ESPANSA)
  - FLUXION-LOYALTY-V3.md completo con 11 Quick Wins (0-10)
  - Quick Win #6: Hold Slot + Countdown Timer
  - Quick Win #7: Riprenota Uguale (1-Tap Rebooking)
  - Quick Win #8: QR Check-In + Micro-Reward
  - Quick Win #9: Smart Reminder con Bottoni
  - Quick Win #10: Mini-Sito "Mini-Program" via QR

  # Refactoring DDD Layer (FASE CRITICA COMPLETATA)
  - Backend: Service layer con Repository pattern
  - 8 nuovi Tauri commands DDD (appuntamenti_ddd.rs)
  - State machine workflow (8 stati: Bozza → Completato)
  - 3-layer validation system (hard blocks, warnings, suggestions)
  - Frontend: TypeScript types con Zod schemas
  - Frontend: 8 TanStack Query mutation hooks
  - Frontend: ValidationAlert component (color-coded)
  - Frontend: OverrideDialog component (audit trail)
  - Backward compatibility mantenuta con comandi legacy

  # GitHub Actions CI/CD Pipeline (COMPLETATO)
  - Workflow test.yml: 5 jobs paralleli (backend tests 3 OS, quality, frontend, build, status)
  - Workflow release.yml: Automated release multi-platform
  - Cargo config: Aliases TDD + build profiles ottimizzati
  - Feature flags: development, production, testing
  - README badges: Tests, Release, License
  - Tempo test ridotto 60%: ~8 min parallelo vs ~20 min locale sequenziale

  # Test di Integrazione Backend (COMPLETATO)
  - Integration tests per appuntamenti DDD layer (10 test completi)
  - Test helper module (common/mod.rs) con setup database reale
  - Test workflow completi: Happy path, override, rifiuto, cancellazione
  - Test validazioni: Hard blocks, modifiche, persistenza, soft delete
  - Test query: find_by_operatore_and_date_range
  - Moduli esposti pubblici in lib.rs (domain, services, infra)
  - Dev-dependencies configurate (sqlx macros, tokio-test)
  - Coverage obiettivo: 95%

  # CI/CD Fixes (2026-01-03)
  - Fix clippy: semicolon in build.rs
  - Fix ESLint: globals HTML + React
  - Fix test: ValidationResult per proponi()
  - CI workflow allentato (quality non-bloccante)
  - Fix export moduli DDD (getter methods, new() alias)
  - Fix integration tests (10 test corretti)
  - Aggiunto find_by_operatore_and_date_range al repository

  # Fix iMac Integration Tests (2026-01-04)
  - Fix SQLite connection: aggiunto ?mode=rwc (Read-Write-Create)
  - Cleanup unused imports in 5 file Rust
  - Fix unused variables in pattern matching (prefisso _)
  - Fix NagerHoliday struct: #[allow(dead_code)]
  - Fix CLAUDE.md: Tailwind CSS 4 → 3.4, luketerna → lukeeterna

  # Fase 4 - Fluxion Care (2026-01-04) ✅ COMPLETATO
  - Support Bundle Export: comando export_support_bundle (ZIP con diagnostics, DB, config)
  - Backup Database: comando backup_database (copia atomica con WAL checkpoint)
  - Restore Database: comando restore_database (verifica integrità + safety backup)
  - List Backups: comando list_backups
  - Delete Backup: comando delete_backup (ADMIN ONLY, doppia conferma)
  - Diagnostics Info: comando get_diagnostics_info (versioni, spazio disco, contatori)
  - Remote Assist v1: comando get_remote_assist_instructions (macOS/Windows native)
  - DiagnosticsPanel UI: componente React completo in Impostazioni
  - Dipendenze: zip 2.1, os_info 3
  - TypeScript types + TanStack Query hooks
  - Fix crash restore: exit() invece di relaunch() per evitare corruzione SQLite pool

  # Fase 5 - Quick Wins Loyalty (2026-01-04) ✅ COMPLETATO
  - Fix CI/CD: quotato `domain::` e `services::` in test.yml (9/9 jobs pass)
  - Agente github-cli-engineer.md (696 righe documentazione)
  - Migration 005: loyalty_visits, is_vip, referral_source, pacchetti, clienti_pacchetti, waitlist
  - Migration 006: pacchetto_servizi (many-to-many pacchetti ↔ servizi)
  - Backend: 18 Tauri commands Loyalty + Pacchetti (loyalty.rs)
  - 5 nuovi commands: delete_pacchetto, update_pacchetto, get_pacchetto_servizi, add_servizio_to_pacchetto, remove_servizio_from_pacchetto
  - Frontend: types/loyalty.ts (Zod schemas + PacchettoServizio + helpers)
  - Frontend: hooks/use-loyalty.ts (TanStack Query + 5 nuovi hooks)
  - Frontend: LoyaltyProgress.tsx (tessera timbri con progress bar)
  - Frontend: PacchettiList.tsx (workflow proposta/acquisto/uso + countdown scadenza)
  - UI: progress.tsx + tooltip.tsx (custom, no radix dependency)
  - CI/CD: Test Suite 9/9 SUCCESS su 3 OS (Run #46)
  - ClienteDialog: Tab system (Dati | Fedeltà | Pacchetti) in edit mode
  - ClientiTable: Colonna Fedeltà con VIP badge + progress bar mini
  - Cliente struct: aggiunto loyalty_visits, loyalty_threshold, is_vip, referral_source, referral_cliente_id (Rust + TypeScript)
  - PacchettiAdmin v3: Composizione servizi alla CREAZIONE + calcolo automatico prezzo da sconto %
  - PacchettiList: Countdown scadenza con colori (rosso <=7gg, giallo <=30gg)
  - WhatsApp QR Kit: 3 template (Prenota, Info, Sposta) + export PDF + personalizzazione messaggio
  - Dipendenze: qrcode.react, jspdf, html2canvas

  # Fase 6 - Fatturazione Elettronica (2026-01-04) ✅ COMPLETATO
  - Migration 007: Schema completo fatturazione elettronica (8 tabelle)
    - impostazioni_fatturazione (dati azienda, regime fiscale, IBAN)
    - fatture (header con stato workflow: bozza→emessa→pagata)
    - fatture_righe (linee con IVA, natura, sconto)
    - fatture_riepilogo_iva (aggregazione per aliquota)
    - fatture_pagamenti (tracking incassi)
    - numeratore_fatture (progressivo per anno)
    - codici_pagamento (lookup SDI: MP01-MP23)
    - codici_natura_iva (lookup SDI: N1-N7)
  - Backend Rust: 14 Tauri commands (fatture.rs, 700+ righe)
    - CRUD fatture + righe + pagamenti
    - Emissione con generazione XML FatturaPA 1.2.2
    - Calcolo automatico bollo virtuale (>€77.47 forfettario)
    - Numerazione progressiva per anno
  - XML FatturaPA compliant:
    - Header cedente/cessionario con regime fiscale
    - Linee documento con natura IVA per esenzioni
    - Riepilogo IVA aggregato
    - Dati pagamento con IBAN
    - Bollo virtuale automatico per forfettari
  - Frontend TypeScript:
    - types/fatture.ts: Zod schemas + helpers (validaPartitaIva, validaCodiceFiscale)
    - hooks/use-fatture.ts: 15+ TanStack Query hooks
    - pages/Fatture.tsx: Lista fatture con filtri + stats cards
    - FatturaDialog.tsx: Creazione bozza con cliente/tipo/date
    - FatturaDetail.tsx: Sheet con righe, pagamenti, download XML
    - ImpostazioniFatturazioneDialog.tsx: 3 tabs (Azienda/Fiscale/Banca)
  - Workflow completo: Bozza → Emessa (genera XML) → Pagata
  - Download XML per invio manuale a SDI

  # Build Fixes (2026-01-05)
  - Fix vite.config.ts: chunk splitting (vendor-react, vendor-tanstack, vendor-ui, vendor-utils, vendor-pdf)
  - Fix bundle identifier: com.fluxion.app → com.fluxion.desktop (evita conflitto macOS)
  - Fix Rust warnings: #[allow(dead_code)] su CreateFatturaInput structs
  - Fix WhatsApp QR Kit: ESLint errors (window.alert, window.URL)
  - Fix WhatsApp QR Kit: usa @tauri-apps/plugin-opener per aprire URL
  - scripts/mock_data.sql: 10 clienti, 8 servizi, 4 operatori, 3 pacchetti, 15 appuntamenti
  - data/faq_salone.md: FAQ placeholder per RAG system

  # Fase 7 - Voice Agent + WhatsApp (2026-01-06) 🔄 IN CORSO
  - Piper TTS integration: voice.rs con synthesize_speech command
  - WhatsApp Web.js: whatsapp.rs con automation locale (ZERO API costs)
  - Fix Rust ownership error: &self invece di self in synthesize_speech
  - Fix Puppeteer download: PUPPETEER_SKIP_DOWNLOAD=true in CI
  - CI/CD Run #20742842792: 9/9 jobs SUCCESS su 3 OS (ubuntu, macos, windows)
  - FAQ prompts: 5 categorie PMI (salone, palestra, studio_medico, carrozzeria, ristorante)

  # RAG con Groq LLM (2026-01-06) ✅ COMPLETATO
  - rag.rs: 5 Tauri commands (load_faqs, list_faq_categories, rag_answer, quick_faq_search, test_groq_connection)
  - Groq API integration: llama-3.1-8b-instant model (veloce, economico)
  - FAQ markdown parser: supporta formato salone/auto con sezioni e Q&A
  - Simple keyword retrieval: TF-IDF lite con scoring normalizzato
  - TypeScript types: rag.ts con Zod schemas
  - TanStack Query hooks: use-rag.ts con 6 hooks
  - Bundle config: data/* incluso come risorse Tauri
  - Fix Rust borrow checker: query_lower binding per lifetime
  - CI/CD Run #20743767261: 9/9 jobs SUCCESS su 3 OS

  # RagChat UI (2026-01-06) ✅ COMPLETATO
  - RagChat.tsx: Chat interface con cronologia messaggi
  - Category selector (salone, auto, wellness, medical)
  - Confidence badges colorati + sezione fonti espandibile
  - Test API button per verifica Groq
  - Aggiunto a pagina Impostazioni
  - CI/CD Run #20744155571: 9/9 jobs SUCCESS

  # Fix Environment Variables (2026-01-06) ✅ COMPLETATO
  - Aggiunto dotenvy 0.15 per caricare .env
  - Load .env all'avvio app in lib.rs
  - Messaggi errore migliorati per GROQ_API_KEY mancante

  # Setup Wizard (2026-01-06) ✅ COMPLETATO
  - Backend: setup.rs con 4 Tauri commands (get_setup_status, save_setup_config, get_setup_config, reset_setup)
  - Frontend: SetupWizard.tsx con 4 step (Dati Attività, Sede, Configurazione, Riepilogo)
  - Types: setup.ts con Zod schemas + REGIMI_FISCALI + CATEGORIE_ATTIVITA
  - Hooks: use-setup.ts con TanStack Query
  - App.tsx: Mostra wizard se setup_completed != true
  - Configurazione salvata in tabella impostazioni
  - Fix mock_data.sql: Schema adattato a migration 001 per fatture/fatture_righe
  - Test iMac: Setup Wizard completato con successo ("ALMA di Di Stasi Mario Gianluca")
  - Test iMac: mock_data.sql importato correttamente (10 clienti, 8 servizi, 6 operatori, 20 appuntamenti, 5 fatture)

  # FLUXION IA Branding (2026-01-06) ✅ COMPLETATO
  - Rinominato "Groq" → "FLUXION IA" in tutta l'interfaccia utente
  - groq_api_key → fluxion_ia_key nel Setup Wizard e backend
  - RAG module ora legge API key da: 1) DB (Setup Wizard) 2) .env fallback
  - L'utente può configurare FLUXION IA senza toccare .env
  - UI: "FLUXION IA Key (opzionale - per assistente intelligente)"
  - RagChat.tsx: "FLUXION IA - Assistente" invece di "RAG Chat - Test Groq LLM"
  - Messaggi errore user-friendly senza menzionare Groq
  - Commit: cbab635

  # WhatsApp Auto-Responder (2026-01-07) ✅ COMPLETATO
  - whatsapp-service.js: Servizio Node.js con whatsapp-web.js
  - Groq LLM integration per risposte intelligenti
  - FAQ-based context retrieval (faq_salone.md)
  - Rate limiting: max 60 risposte/ora per utente
  - WhatsAppAutoResponder.tsx: UI completa in Impostazioni
  - Status badge, QR code display, toggle on/off
  - Log messaggi ricevuti/inviati in tempo reale
  - 2 nuovi Tauri commands: get_whatsapp_config, update_whatsapp_config
  - CI/CD Run #20777817807: 9/9 jobs SUCCESS
  - Commit: d14ad65

  # FAQ Learning System (2026-01-07) ✅ COMPLETATO
  - Sistema apprendimento supervisionato "Learn from Operator"
  - Confidence threshold 50%: sotto questa soglia → passa a operatore
  - pending_questions.jsonl: Log domande senza risposta automatica
  - faq_custom.md: FAQ aggiunte dall'operatore (append-only)
  - Tracking automatico risposte operatore via WhatsApp
  - PendingQuestions.tsx: UI per operatore review + salvataggio FAQ
  - 6 nuovi Tauri commands:
    - get_pending_questions
    - update_pending_question_status
    - delete_pending_question
    - save_custom_faq
    - get_custom_faqs
    - get_pending_questions_count
  - Garanzia: Bot MAI improvvisa, solo dati verificati DB/FAQ
  - Fix chrono::Datelike import in dashboard.rs
  - Regola CI/CD imperativa aggiunta a CLAUDE.md
  - CI/CD Run #20777817807: 9/9 jobs SUCCESS su 3 OS
  - Commit: 3ced0c9

in_corso: |
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

  ## PROSSIMO:
  - Test CI/CD per verificare compilazione
  - FatturAE Bridge per fatture B2B occasionali
  - Test su iMac: Cassa + RAG locale

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

prossimo: |
  Fase 7 - Voice Agent
  - Voice Agent: Groq Whisper STT + Piper TTS
  - Integrazione VoIP Ehiweb
  - Waitlist con priorità VIP

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

Tabella Routing Agenti (16 AGENTI MAPPATI)
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
Lista Completa Agenti (.claude/agents/)
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
PROSSIME AZIONI
Fase 4 - Fluxion Care (PROSSIMA - PRIORITÀ MASSIMA)
Leggere prima di iniziare:

docs/context/FLUXION-REMOTE-ASSIST.md

docs/context/CLAUDE-DEPLOYMENT.md

.claude/agents/devops.md

Task:

Support Bundle Export (1 click → .zip con log/DB/diagnostics)

Comando Tauri: export_support_bundle

Contenuto: versioni app/OS, log (ultimi 500 righe), DB SQLite (opzionale), config/store, info diagnostica

Salva in cartella scelta dall'utente (tauri-plugin-dialog)

Backup/Restore DB (1 click → copia sicura SQLite)

Comando Tauri: backup_database (copia atomica: temp file + rename)

Comando Tauri: restore_database (conferma forte + test integrità)

Diagnostics Panel UI (Impostazioni → sezione "Diagnostica")

App version (da Cargo.toml)

OS version (Tauri API)

Path data directory

Stato DB (dimensione, numero tabelle, ultimo backup)

Spazio disco libero

Ultimi 10 errori/warning da log

Comando Tauri: get_diagnostics_info

Remote Assist v1 guidata (senza server, istruzioni native OS)

macOS: istruzioni Screen Sharing nativo (System Preferences → Sharing)

Windows: istruzioni Quick Assist (Win+Ctrl+Q)

Bottoni "Copia istruzioni" + "Apri Preferenze/Quick Assist"

NO WebRTC in MVP (pianificato per Fase 4B futuro)

Obiettivo: Ridurre drasticamente tempo di debug su PC clienti.

Criteri accettazione:

Export bundle funziona su macOS Monterey senza crash

Bundle contiene tutti i file richiesti

Backup/restore non corrompe DB (test con 50+ appuntamenti)

Diagnostics panel mostra info corrette

Istruzioni assistenza remota chiare per macOS + Windows

Nessuna dipendenza server esterni

Fase 5 - Quick Wins Zero-Cost (WhatsApp + Loyalty + Referral + Commerce v1)
Leggere prima:

docs/context/FLUXION-LOYALTY-V2.md ⭐

docs/context/CLAUDE-INTEGRATIONS.md

.claude/agents/integration-specialist.md

Principi (da Loyalty V2):

Automazione "warm" (non aggressiva, tono Sud Italia)

"Progress, not urgency" (no FOMO spam)

Gamification soft e privata (no leaderboard pubblica)

Frequenza bassa (1–2 msg/settimana max, MVP = manual copy)

Deliverable (ordine consigliato):

1) WhatsApp Template Library (v1):

10 template predefiniti:

Reminder appuntamento 24h prima

Follow-up post servizio

Birthday con sconto soft

Riattivazione cliente dormiente (30+ giorni)

Promozione stagionale soft

Referral request

Loyalty milestone

Conferma prenotazione

Cancellazione slot disponibile

Thank you post-acquisto pacchetto

Variabili: {{nome}}, {{data}}, {{servizio}}, {{benefit}}, {{scadenza_soft}}

UI: pagina "Marketing" → "Template WhatsApp"

Lista template con categoria

Preview + bottone "Copia"

Edit/crea custom template

Storage: SQLite tabella whatsapp_templates:

sql
CREATE TABLE whatsapp_templates (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  template_name TEXT NOT NULL,
  template_text TEXT NOT NULL,
  variables TEXT, -- JSON array
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
2) WhatsApp QR Kit (v1):

Genera QR per:

Prenota: wa.me/39NUMERO?text=Ciao!%20Vorrei%20prenotare%20un%20appuntamento

Info/Prezzi: wa.me/39NUMERO?text=Buongiorno,%20vorrei%20info%20su%20servizi%20e%20prezzi

Sposta appuntamento: wa.me/39NUMERO?text=Devo%20spostare%20appuntamento

UI: pagina "Marketing" → "QR WhatsApp"

3 QR preconfigurati

Opzione "Personalizza testo"

Export PDF stampabile (A4 con QR + testo + logo)

Tech: libreria qrcode (Rust crate) o JS (qrcode.react)

3) WhatsApp Commerce (v1 manuale):

"Pacchetti" vendibili (es. "5 Massaggi €180")

Tabella DB pacchetti:

sql
CREATE TABLE pacchetti (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  descrizione TEXT,
  prezzo REAL NOT NULL,
  servizi_inclusi INTEGER,
  validita_giorni INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clienti_pacchetti (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  pacchetto_id TEXT NOT NULL,
  stato TEXT NOT NULL, -- 'proposto' | 'venduto' | 'in_uso' | 'completato'
  servizi_usati INTEGER DEFAULT 0,
  data_acquisto TIMESTAMP,
  data_scadenza TIMESTAMP,
  FOREIGN KEY (cliente_id) REFERENCES clienti(id),
  FOREIGN KEY (pacchetto_id) REFERENCES pacchetti(id)
);
UI:

Pagina "Pacchetti" → crea/edit pacchetti

In scheda cliente → tab "Pacchetti"

Bottone "Invia proposta WhatsApp" (genera messaggio precompilato, copy manual)

Pagamento: offline (cash/bonifico/Satispay) → bottone "Segna come pagato"

4) Referral Tracking (manuale ma tracciato):

Aggiungi campo in tabella clienti: referral_source TEXT

Quando crei nuovo cliente: campo opzionale "Chi ti ha consigliato?"

UI:

Report "Top Referrer" (pagina Dashboard o Marketing)

Lista clienti + count referral portati

Alert quando un cliente porta 3+ amici (badge/notifica UI)

5) Loyalty "Tessera Timbri Digitale" (v1):

Aggiungi campi in tabella clienti:

sql
ALTER TABLE clienti ADD COLUMN loyalty_visits INTEGER DEFAULT 0;
ALTER TABLE clienti ADD COLUMN loyalty_threshold INTEGER DEFAULT 10;
Logic: increment automatico loyalty_visits ogni appuntamento completato (stato = 'completato')

UI scheda cliente:

Progress bar: "8/10 visite ⭐"

Testo: "Mancano 2 timbri per premio: Sconto 15%"

Badge visivo quando milestone raggiunta

Suggerimento template WhatsApp: "Complimenti {{nome}}! Hai raggiunto {{loyalty_threshold}} visite 💚"

Metafora: "Tessera Timbri" (nome friendly), non "Loyalty Program"

Criteri accettazione:

Template WhatsApp copy/paste funziona

QR generati scansionabili e aprono WhatsApp

Pacchetti creabili e assegnabili

Referral tracking funziona, report visibile

Loyalty progress bar aggiornamento automatico post-appuntamento

Tutto offline, zero API esterne obbligatorie

UI coerente con Design Bible

RIFERIMENTI RAPIDI
Risorsa	Path	Note
Design Bible	docs/FLUXION-DESIGN-BIBLE.md	Mockup completo
Design Tokens	docs/context/CLAUDE-DESIGN-SYSTEM.md	Colori/spacing
Schema DB	docs/context/CLAUDE-BACKEND.md	9 tabelle SQLite
API Reference	docs/context/CLAUDE-INTEGRATIONS.md	WhatsApp
Voice Agent	docs/context/CLAUDE-VOICE.md	Groq + Piper (voce Paola)
Loyalty/Referral	docs/context/FLUXION-LOYALTY-V2.md	⭐ Quick Wins
Remote Assist	docs/context/FLUXION-REMOTE-ASSIST.md	⭐ Support
Ultimo aggiornamento: 2026-01-01T17:45:00