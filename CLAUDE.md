# FLUXION ENTERPRISE - Master Orchestrator v2

**LEGGIMI SEMPRE PER PRIMO**

Sono il cervello del progetto. Coordino agenti, gestisco stato, ottimizzo token.

---

## PROGETTO IN BREVE

**FLUXION**: Gestionale desktop enterprise per PMI italiane

- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Tailwind CSS 4
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Modello**: Licenza annuale desktop (NO SaaS, NO commissioni)

---

## STATO CORRENTE

```yaml
fase: 3
nome_fase: "Calendario + Booking (100% COMPLETATO)"
data_inizio: 2025-12-30
ultimo_aggiornamento: 2026-01-03T19:15:00
completato:
  # Fase 0 - Setup
  - Struttura directory
  - Design Bible + Documentazione contesto
  - Tauri 2.x inizializzato (React 19 + TypeScript)
  - Dipendenze Node + Rust installate
  - shadcn/ui configurato (18 componenti)
  - Schema database (9 tabelle)
  - Plugin Tauri backend (SQL, FS, Dialog, Store, Opener)
  - Git repository (GitHub: luketerna/fluxion-desktop)
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
  - TODO: Fix export moduli in lib.rs (su iMac)

in_corso: "Fix export moduli lib.rs per integration tests"
prossimo: |
  Fase 4 - Fluxion Care (PRIORITÀ MASSIMA)
  - Support Bundle Export (1 click)
  - Backup/Restore DB (1 click)
  - Diagnostics Panel UI
  - Remote Assist v1 guidata (Screen Sharing macOS / Quick Assist Windows)

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
4	Fluxion Care (Stabilità)	⏳ PROSSIMA	2 giorni	Support + Diagnostics
5	Quick Wins (WhatsApp + Loyalty)	📋 TODO	3 giorni	Template + QR + Pacchetti
6	Fatturazione Elettronica	📋 TODO	3 giorni	XML + SDI
7	Voice Agent	📋 TODO	3 giorni	Groq + Piper + Ehiweb
8	Build + Licenze	📋 TODO	2 giorni	Release + Keygen
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

Repository: https://github.com/luketerna/fluxion-desktop (privato)

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

Tabella Routing Agenti (15 AGENTI MAPPATI)
Keyword Richiesta	Agente	File Contesto	Quando Usare
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