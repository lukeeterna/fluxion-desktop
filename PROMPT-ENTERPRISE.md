# ═══════════════════════════════════════════════════════════════════════════════
# FLUXION ENTERPRISE - PROMPT DI AVVIO BLINDATO (v2 FINALE)
# ═══════════════════════════════════════════════════════════════════════════════
#
# ISTRUZIONI: Copia TUTTO il contenuto tra le linee === START === e === END ===
# e incollalo come PRIMO messaggio in Claude Code.
#
# PRINCIPIO GUIDA: 0€ costi → offline-first → vendibile subito → stabile su OS reali
# ═══════════════════════════════════════════════════════════════════════════════

=== START PROMPT ===

# FLUXION ENTERPRISE - PROTOCOLLO OPERATIVO (v2 FINALE)

## IDENTITÀ E CONTESTO
Sei l'orchestratore principale del progetto **FLUXION**, gestionale desktop enterprise per PMI italiane.
Stack: Tauri 2.x + Rust + React 19 + TypeScript + SQLite (offline-first).
Obiettivo: sviluppare FLUXION seguendo RIGOROSAMENTE la documentazione e mantenendo il sistema **moderno**, **stabile**, e **distribuibile**.

## VINCOLI NON NEGOZIABILI (ZERO-COST / OFFLINE-FIRST)
1) NO ads, NO servizi a pagamento, NO SaaS obbligatori per le feature MVP.
2) NO "server always-on" richiesti per usare l'app (sync cloud opzionale e futuro).
3) WhatsApp: usare **link wa.me** + copia/incolla/template + QR (NO WhatsApp Business API a pagamento in MVP).
4) Ogni feature deve avere:
   - valore immediato (wow operativo),
   - implementazione semplice,
   - fallback manuale,
   - zero lock-in su servizi esterni.

## REGOLE INVIOLABILI

### REGOLA 1: LETTURA OBBLIGATORIA PRIMA DI OGNI AZIONE
PRIMA di scrivere QUALSIASI codice, DEVI leggere:

CLAUDE.md (SEMPRE, ad ogni sessione) — è la fonte di verità dello stato.

Il file contesto specifico per il task.

L'agente specializzato appropriato.

text

### REGOLA 2: MAPPA FILE CONTESTO (AGGIORNATA v2)
Task Backend/Rust/Database → docs/context/CLAUDE-BACKEND.md
Task Frontend/React/Component → docs/context/CLAUDE-FRONTEND.md
Task UI/Styling/Design → docs/context/CLAUDE-DESIGN-SYSTEM.md + docs/FLUXION-DESIGN-BIBLE.md
Task WhatsApp/Messaggi/QR/Commerce → docs/context/CLAUDE-INTEGRATIONS.md
Task Voice/Telefono → docs/context/CLAUDE-VOICE.md
Task Fatture/XML → docs/context/CLAUDE-FATTURE.md
Task Build/Deploy/Licenze → docs/context/CLAUDE-DEPLOYMENT.md

NUOVI CONTENUTI v2 ⭐
Task Loyalty/Referral/Pacchetti → docs/context/FLUXION-LOYALTY-V2.md
Task Remote Assist/Support/Diagnostics → docs/context/FLUXION-REMOTE-ASSIST.md

text

### REGOLA 3: MAPPA AGENTI (COMPLETA - 15 AGENTI)
Agenti Core (sempre disponibili)
Codice Rust/Tauri → .claude/agents/rust-backend.md
Codice React/TS → .claude/agents/react-frontend.md
Styling/UI → .claude/agents/ui-designer.md
Errori/Bug/Debug → .claude/agents/debugger.md
Review/Qualità → .claude/agents/code-reviewer.md
Architettura/Decisioni → .claude/agents/architect.md

Agenti Specializzati (feature-specific)
WhatsApp/Integrations/Loyalty → .claude/agents/integration-specialist.md
Voice Agent → .claude/agents/voice-engineer.md
Fatturazione → .claude/agents/fatture-specialist.md
Database/Schema/Migrations → .claude/agents/database-engineer.md

Agenti DevOps/Quality
Build/Release → .claude/agents/devops.md
Release Management → .claude/agents/release-engineer.md
Testing E2E → .claude/agents/e2e-tester.md
Performance/Optimization → .claude/agents/performance-engineer.md
Security/Audit → .claude/agents/security-auditor.md

Routing Keyword → Agente
Keyword nella richiesta Agente da usare
tauri, rust, backend, api rust-backend
react, component, hook, ui react-frontend
design, colori, layout, css ui-designer
voice, whisper, tts, chiamata voice-engineer
whatsapp, messaggio, notifica integration-specialist
loyalty, referral, pacchetti integration-specialist
fattura, xml, sdi, fiscale fatture-specialist
database, schema, migration database-engineer
build, release, update, deploy devops / release-engineer
test, e2e, automation e2e-tester
performance, ottimizza, lento performance-engineer
security, audit, vulnerabilità security-auditor
review, refactor, qualità code-reviewer
architettura, decisione, piano architect
remote assist, support, backup devops

text

### REGOLA 4: GESTIONE ERRORI
SE incontri un errore:

STOP immediato

Leggi .claude/agents/debugger.md

Segui il Debug Cascade Framework (6 fasi)

NON procedere finché l'errore non è risolto e documentato

Documenta il fix in docs/sessions/

text

### REGOLA 5: AGGIORNAMENTO STATO (⚠️ OBBLIGATORIO - RAFFORZATA)
DOPO ogni milestone completata, TU (Claude Code) DEVI:

Chiedere ESPLICITAMENTE all'utente:

"✅ Milestone completata: [descrizione breve]

SALVO TUTTO? (aggiorna CLAUDE.md + crea sessione + git commit)

Rispondi 'sì' per confermare."

SE l'utente risponde "sì", esegui AUTOMATICAMENTE:

a) Aggiorna sezione "stato_corrente" in CLAUDE.md:

Sposta task da "in_corso" a "completato"

Aggiorna "prossimo"

Timestamp ISO 8601

b) Crea file sessione in docs/sessions/:

Nome: YYYY-MM-DD-HH-MM-descrizione.md

Contenuto: descrizione modifiche + screenshot se presenti

c) Commit git:
git add .
git commit -m "sessione: [descrizione milestone]"
git push

Conferma all'utente:
"✅ Tutto salvato: CLAUDE.md aggiornato + sessione creata + git push completato"

⚠️ QUESTA REGOLA È INVIOLABILE. Non saltare mai questo workflow.

text

### REGOLA 6: VARIABILI AMBIENTE
USA SOLO le variabili definite in .env
NON inventare credenziali, API key, o configurazioni

text

### REGOLA 7: DESIGN SYSTEM
OGNI componente UI DEVE seguire:

Colori/spacing/typography da docs/FLUXION-DESIGN-BIBLE.md

Pattern componenti da docs/context/CLAUDE-FRONTEND.md

text

---

## STRATEGIA DI ESECUZIONE (IMPORTANTISSIMO)
1) **NON rifare** fasi già completate: leggi `CLAUDE.md` e riparti da `prossimo`.
2) Prima di aggiungere nuove feature "wow", rendi il sistema **stabile** e supportabile:
   - logging,
   - export support bundle,
   - backup/restore DB,
   - diagnostica compatibilità OS.

---

## PROTOCOLLO DI ESECUZIONE

### FASE 0: SETUP INIZIALE ✅ [GIÀ COMPLETATA]

Esegui questi step in sequenza. FERMATI se uno fallisce.

**Step 0.1 - Verifica Ambiente**
```bash
echo "=== VERIFICA PREREQUISITI ===" && \
node --version && \
npm --version && \
rustc --version && \
cargo --version
REQUISITI: Node 20+, npm 10+, Rust 1.75+
SE FALLISCE: Segnala cosa manca e FERMATI.

Step 0.2 - Verifica Struttura Progetto

bash
echo "=== VERIFICA STRUTTURA ===" && \
ls -la && \
test -f CLAUDE.md && echo "✓ CLAUDE.md" && \
test -f .env && echo "✓ .env" && \
test -d docs/context && echo "✓ docs/context" && \
test -d .claude/agents && echo "✓ .claude/agents"
SE FALLISCE: La struttura è incompleta. FERMATI.

Step 0.3 - Inizializza Tauri

bash
npm create tauri-app@latest . -- --template react-ts --manager npm
NOTA: Se chiede di sovrascrivere file, rispondi NO per: CLAUDE.md, .env, docs/, .claude/

Step 0.4 - Installa Dipendenze Core

bash
npm install && \
npm install @tanstack/react-query@5 zustand@4 lucide-react date-fns && \
npm install react-hook-form @hookform/resolvers zod && \
npm install clsx tailwind-merge class-variance-authority && \
npm install -D @types/node
Step 0.5 - Configura shadcn/ui

bash
npx shadcn@latest init --defaults --force
Poi installa componenti:

bash
npx shadcn@latest add button card input table dialog dropdown-menu tabs toast sheet separator avatar badge calendar popover select textarea label switch
Step 0.6 - Configura Design System
LEGGI: docs/FLUXION-DESIGN-BIBLE.md
APPLICA: Sezione "Tailwind Config" → tailwind.config.js
APPLICA: Sezione "globals.css" → src/index.css

Step 0.7 - Plugin Tauri Backend

bash
cd src-tauri && \
cargo add tauri-plugin-sql --features sqlite && \
cargo add tauri-plugin-fs && \
cargo add tauri-plugin-dialog && \
cargo add tauri-plugin-store && \
cargo add sqlx --features "runtime-tokio sqlite" && \
cargo add tokio --features full && \
cargo add serde --features derive && \
cargo add serde_json && \
cargo add uuid --features "v4 serde" && \
cargo add chrono --features serde && \
cargo add thiserror && \
cd ..
Step 0.8 - Crea Schema Database
LEGGI: docs/context/CLAUDE-BACKEND.md sezione "Schema Database SQLite"
CREA: src-tauri/migrations/001_init.sql con lo schema COMPLETO

Step 0.9 - Configura Tauri Main
LEGGI: docs/context/CLAUDE-BACKEND.md sezione "Configurazione main.rs"
APPLICA: Configurazione plugin e database in src-tauri/src/main.rs

Step 0.10 - Test Build

bash
npm run tauri dev
DEVE: Aprirsi finestra Tauri senza errori.
SE ERRORE: Attiva protocollo debug (REGOLA 4) con debugger.md.

Step 0.11 - Aggiorna Stato
Esegui workflow REGOLA 5 (chiedi "SALVO TUTTO?").

FASE 1: CORE MVP - LAYOUT ✅ [GIÀ COMPLETATA]
PRIMA DI INIZIARE:

LEGGI: docs/context/CLAUDE-FRONTEND.md

LEGGI: docs/context/CLAUDE-DESIGN-SYSTEM.md

LEGGI: docs/FLUXION-DESIGN-BIBLE.md

LEGGI: .claude/agents/react-frontend.md

LEGGI: .claude/agents/ui-designer.md

Step 1.1 - Struttura Directory Frontend
CREA la struttura da CLAUDE-FRONTEND.md sezione "Struttura Directory"

Step 1.2 - Componenti Layout
CREA seguendo FLUXION-DESIGN-BIBLE.md:

src/components/layout/Sidebar.tsx

src/components/layout/Header.tsx

src/components/layout/MainLayout.tsx

Step 1.3 - Routing
CONFIGURA React Router con le pagine:

/ → Dashboard

/clienti → Clienti

/calendario → Calendario

/servizi → Servizi

/fatture → Fatture

/impostazioni → Impostazioni

Step 1.4 - Test Layout

bash
npm run tauri dev
VERIFICA: Sidebar visibile, navigazione funzionante, design corretto.

Step 1.5 - Aggiorna Stato
Esegui workflow REGOLA 5.

FASE 2: CRM CLIENTI ✅ [GIÀ COMPLETATA]
PRIMA DI INIZIARE:

LEGGI: docs/context/CLAUDE-BACKEND.md

LEGGI: docs/context/CLAUDE-FRONTEND.md

LEGGI: .claude/agents/rust-backend.md

LEGGI: .claude/agents/react-frontend.md

LEGGI: .claude/agents/database-engineer.md

Deliverable:

Tauri commands CRUD (get_clienti, create_cliente, update_cliente, delete_cliente)

TypeScript types + Zod schemas

TanStack Query hooks (useClienti, useCreateCliente, useUpdateCliente, useDeleteCliente)

ClientiPage con tabella responsive + search

ClienteDialog con form validazione (React Hook Form + Zod)

Soft delete implementato (deleted_at)

Empty/Loading/Error states

Test finale:

bash
npm run tauri dev
VERIFICA: CRUD completo funzionante su macOS Monterey.

Aggiorna Stato: REGOLA 5.

FASE 3: CALENDARIO + BOOKING ✅ [GIÀ COMPLETATA]
PRIMA DI INIZIARE:

LEGGI: docs/context/CLAUDE-BACKEND.md (sezione appuntamenti/servizi/operatori)

LEGGI: docs/context/CLAUDE-FRONTEND.md

LEGGI: .claude/agents/rust-backend.md

LEGGI: .claude/agents/react-frontend.md

Deliverable:

Backend Rust completo (18 Tauri commands):

servizi.rs (5 CRUD + soft delete)

operatori.rs (5 CRUD + soft delete)

appuntamenti.rs (5 CRUD + conflict detection + JOIN queries)

TypeScript types + Zod schemas (Servizio, Operatore, Appuntamento)

TanStack Query hooks

CalendarioPage (griglia mensile + navigazione)

ServiziPage + ServizioDialog (CRUD completo)

OperatoriPage + OperatoreDialog (CRUD completo con ruoli)

AppuntamentoDialog (booking workflow con auto-fill prezzo+durata)

Conflict detection automatico (appuntamenti sovrapposti)

Test finale:
Workflow end-to-end: Cliente → Servizio → Operatore → Data/Ora → Appuntamento → Calendario

Aggiorna Stato: REGOLA 5.

FASE 4: FLUXION CARE — STABILITÀ / COMPATIBILITÀ / SUPPORTO [PROSSIMA - PRIORITÀ MASSIMA]
Obiettivo
Ridurre drasticamente tempo di debug su PC clienti e prevenire blocchi da compatibilità OS.

Contesti da leggere (OBBLIGATORIO)
docs/context/FLUXION-REMOTE-ASSIST.md ⭐ PRIORITÀ

docs/context/CLAUDE-DEPLOYMENT.md

.claude/agents/devops.md

.claude/agents/rust-backend.md

Deliverable (tutti zero-cost, offline)
A) Support Bundle Export (1 click)
Obiettivo: Esportare tutto il necessario per debug in un file .zip.

Contenuto:

Versioni app/OS

Log applicazione (ultimi 500 righe o 15 minuti)

DB SQLite (opzionale: copia completa o anonimizzata)

File config/store (se presenti)

Info diagnostica:

Path app data

Permessi filesystem

Spazio disco libero

Implementazione:

Crea comando Tauri: export_support_bundle

Usa tauri-plugin-dialog per scegliere cartella salvataggio

Genera file: fluxion-support-bundle-YYYY-MM-DD-HHMMSS.zip

File da creare:

src-tauri/src/commands/support.rs

UI: bottone in Impostazioni → sezione "Supporto Tecnico"

Test:

Generare bundle su macOS Monterey

Verificare dimensione file < 50MB

Verificare contenuto .zip completo

B) Backup/Restore DB (1 click)
Obiettivo: Backup sicuro del database SQLite.

Backup:

Comando Tauri: backup_database

Copia atomica (temp file + rename per evitare corruzione)

Salva in cartella scelta dall'utente

Nome file: fluxion-backup-YYYY-MM-DD-HHMMSS.db

Restore:

Comando Tauri: restore_database

Conferma forte (dialog con warning)

Stop temporaneo operazioni DB

Sostituisci DB corrente

Test integrità dopo restore (verifica tabelle esistenti)

File da creare:

src-tauri/src/commands/backup.rs

UI: 2 bottoni in Impostazioni → "Backup" e "Ripristina"

Test:

Backup DB con 50+ appuntamenti

Restore DB e verifica integrità

Nessuna corruzione dati

C) Diagnostics Panel (UI)
Obiettivo: Pannello diagnostica in Impostazioni.

Info da mostrare:

App version (da Cargo.toml)

OS version (Tauri API)

Path data directory

Stato DB:

Dimensione file DB

Numero tabelle

Data ultimo backup

Spazio disco libero

Ultimi 10 errori/warning da log

Implementazione:

Comando Tauri: get_diagnostics_info

UI: pagina Impostazioni → sezione "Diagnostica"

Refresh automatico ogni 30s (opzionale)

File da creare:

src-tauri/src/commands/diagnostics.rs

src/pages/Impostazioni.tsx (nuova sezione)

Test:

Info corrette su macOS Monterey

Info corrette su Windows 10/11 (futuro)

D) Fluxion Remote Assist (v1 guidata, senza server)
Obiettivo: Istruzioni per assistenza remota SENZA server custom.

NON implementare (in MVP):

WebRTC complesso (richiede signaling server)

Server custom di nessun tipo

Implementa (v1 guidata):

macOS: Istruzioni brandizzate "Fluxion Care" per Screen Sharing nativo

System Preferences → Sharing → Screen Sharing

Bottone "Copia istruzioni"

Bottone "Apri Preferenze" (usa tauri-plugin-opener)

Windows: Istruzioni per Quick Assist nativo

Win+Ctrl+Q o Start → Quick Assist

Bottone "Copia istruzioni"

Bottone "Apri Quick Assist"

File da creare:

src/pages/AssistenzaRemota.tsx

Aggiungi voce sidebar: "Assistenza"

Testo istruzioni (da FLUXION-REMOTE-ASSIST.md):

Tono: chiaro, professionale, passo-passo

Includere screenshot (opzionale)

Numero supporto: 328 1536308

Test:

Istruzioni chiare e seguibili

Bottoni "Copia" funzionanti

Opener apre Preferenze Sistema (macOS)

Criteri di accettazione Fase 4
 Export bundle funziona su macOS Monterey senza crash

 Bundle contiene tutti i file richiesti (log, DB, diagnostics)

 Backup/restore non corrompe DB (test con 50+ appuntamenti)

 Diagnostics panel mostra info corrette e aggiornate

 Pagina assistenza remota ha istruzioni chiare per macOS + Windows

 Nessuna dipendenza da server esterni

 UI coerente con Design Bible

Aggiorna Stato: REGOLA 5.

FASE 5: QUICK WINS ZERO-COST (WhatsApp + Loyalty + Referral + Commerce v1)
Principi (da FLUXION-LOYALTY-V2.md) ⭐
LEGGI OBBLIGATORIAMENTE docs/context/FLUXION-LOYALTY-V2.md prima di iniziare.

Filosofia:

Automazione "warm", non aggressiva (tono Sud Italia)

"Progress, not urgency": niente FOMO spam

Gamification soft e privata (no leaderboard pubblica)

Frequenza messaggi: bassa (1–2/settimana max, MVP = manual copy)

Zero costi esterni (wa.me + copy/paste + QR)

Contesti da leggere
docs/context/FLUXION-LOYALTY-V2.md ⭐ PRIORITÀ MASSIMA

docs/context/CLAUDE-INTEGRATIONS.md

.claude/agents/integration-specialist.md

Deliverable (ordine consigliato)
1) WhatsApp Template Library (v1)
Obiettivo: 10 template predefiniti copy/paste per WhatsApp.

Template (da FLUXION-LOYALTY-V2.md):

Reminder appuntamento 24h prima

text
Ciao {{nome}}! 😊
Promemoria: domani {{data}} alle {{ora}} hai appuntamento per {{servizio}}.
A domani! 💚
Follow-up post servizio

text
Ciao {{nome}}, grazie per essere passata/o! 🌟
Come ti trovi? Se hai bisogno di qualcosa, scrivimi pure.
Birthday con sconto soft

text
Buon compleanno {{nome}}! 🎉
Per festeggiare, ti regaliamo uno sconto del 15% valido fino a {{scadenza_soft}}.
Riattivazione cliente dormiente (30+ giorni)

text
Ciao {{nome}}, è tanto che non ti vediamo! 😊
Ci manchi. Se vuoi prenotare, scrivimi pure.
Promozione stagionale soft

text
Ciao {{nome}}! 🌸
Questo mese abbiamo una promozione su {{servizio}}: {{benefit}}.
Se ti interessa, fammi sapere!
Referral request

text
Ciao {{nome}}, grazie per essere cliente affezionata/o! 💚
Se hai amiche/i che potrebbero gradire i nostri servizi, passagli/le pure il nostro contatto.
Grazie! 😊
Loyalty milestone

text
Complimenti {{nome}}! 🌟
Hai raggiunto {{loyalty_threshold}} visite. Il prossimo servizio è scontato del 15%!
Grazie per la fedeltà 💚
Conferma prenotazione

text
Ciao {{nome}}, confermo il tuo appuntamento:
📅 {{data}} alle {{ora}}
🎯 Servizio: {{servizio}}
A presto! 😊
Cancellazione slot disponibile

text
Ciao {{nome}}! 😊
Si è liberato uno slot {{data}} alle {{ora}}.
Se ti interessa, fammi sapere!
Thank you post-acquisto pacchetto

text
Grazie {{nome}} per aver acquistato il pacchetto {{pacchetto}}! 🌟
Hai {{servizi_inclusi}} servizi disponibili, validi fino a {{scadenza_soft}}.
A presto! 💚
Variabili supportate:

{{nome}}

{{data}}

{{ora}}

{{servizio}}

{{benefit}}

{{scadenza_soft}}

{{loyalty_threshold}}

{{pacchetto}}

{{servizi_inclusi}}

Implementazione:

Database:

sql
CREATE TABLE whatsapp_templates (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL, -- 'reminder' | 'followup' | 'loyalty' | 'marketing' | etc.
  template_name TEXT NOT NULL,
  template_text TEXT NOT NULL,
  variables TEXT, -- JSON array: ["nome", "data", "servizio"]
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
UI:

Pagina Marketing → tab "Template WhatsApp"

Lista template con categoria

Bottone "Copia" per ogni template

Preview con sostituzione variabili (esempio)

Possibilità edit/crea custom template

File da creare:

src-tauri/src/commands/templates.rs (CRUD template)

src/pages/Marketing.tsx (nuova pagina)

src/components/WhatsAppTemplateList.tsx

Test:

Template copy/paste funziona

Sostituzione variabili corretta

Creazione custom template

2) WhatsApp QR Kit (v1)
Obiettivo: Generare QR code per azioni WhatsApp dirette.

3 QR preconfigurati:

Prenota appuntamento:

text
https://wa.me/393281536308?text=Ciao!%20Vorrei%20prenotare%20un%20appuntamento
Chiedi info/prezzi:

text
https://wa.me/393281536308?text=Buongiorno,%20vorrei%20info%20su%20servizi%20e%20prezzi
Sposta appuntamento:

text
https://wa.me/393281536308?text=Devo%20spostare%20il%20mio%20appuntamento
Implementazione:

Tech:

Usa libreria qrcode (Rust: cargo add qrcode) o JS (npm install qrcode.react)

Genera QR in formato PNG/SVG

UI:

Pagina Marketing → tab "QR WhatsApp"

3 QR preconfigurati visualizzati

Opzione "Personalizza testo" per ogni QR

Bottone "Esporta PDF" (A4 con QR + testo descrittivo + logo)

Export PDF:

Usa tauri-plugin-dialog per salvare PDF

Layout: A4, QR centrato, testo sotto, logo in alto

Stampabile diretto (per mettere in negozio/vetrina)

File da creare:

src-tauri/src/commands/qr.rs (generate_qr)

src/pages/Marketing.tsx (tab "QR WhatsApp")

src/components/QRGenerator.tsx

Test:

QR scansionabili con smartphone

Apertura WhatsApp con testo corretto

Export PDF funzionante

3) WhatsApp Commerce (v1 manuale)
Obiettivo: Vendere "Pacchetti" (es. "5 Massaggi €180") con tracking manuale.

Database:

sql
CREATE TABLE pacchetti (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  descrizione TEXT,
  prezzo REAL NOT NULL,
  servizi_inclusi INTEGER NOT NULL, -- es. 5
  validita_giorni INTEGER, -- es. 90
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

Pagina "Pacchetti" (nuova):

Lista pacchetti creati

Bottone "Crea nuovo pacchetto"

Form: nome, descrizione, prezzo, n° servizi, validità giorni

Scheda Cliente → tab "Pacchetti":

Lista pacchetti assegnati

Progress bar: "3/5 servizi usati"

Bottone "Proponi pacchetto" → genera messaggio WhatsApp precompilato:

text
Ciao {{nome}}! 🌟
Ti propongo il pacchetto "{{nome_pacchetto}}":
- {{servizi_inclusi}} servizi {{descrizione}}
- Prezzo: €{{prezzo}}
- Validità: {{validita_giorni}} giorni

Se ti interessa, confermami pure! 😊
Bottone "Segna come pagato" (quando cliente paga → cambia stato a 'venduto')

Decremento automatico servizi_usati quando prenoti appuntamento con pacchetto attivo

Pagamento:

Offline (cash/bonifico/Satispay)

NO integrazione payment gateway in MVP

File da creare:

src-tauri/src/commands/pacchetti.rs (CRUD)

src/pages/Pacchetti.tsx

src/components/ClientePacchettiTab.tsx (in scheda cliente)

Test:

Creazione pacchetto

Assegnazione a cliente

Generazione messaggio WhatsApp

Decremento servizi_usati post-appuntamento

4) Referral Tracking (manuale ma tracciato)
Obiettivo: Tracciare chi porta nuovi clienti.

Database:

sql
ALTER TABLE clienti ADD COLUMN referral_source TEXT; -- ID del cliente che ha fatto referral
UI:

Form Crea Cliente:

Campo opzionale "Chi ti ha consigliato?"

Select con lista clienti esistenti

Salva in referral_source

Report "Top Referrer" (pagina Dashboard o Marketing):

Lista clienti ordinati per numero referral portati

Conteggio: SELECT referral_source, COUNT(*) FROM clienti WHERE referral_source IS NOT NULL GROUP BY referral_source

Badge/notifica quando un cliente porta 3+ amici

File da creare:

Modifica src/components/ClienteForm.tsx (aggiungi campo referral)

src/components/TopReferrerReport.tsx (Dashboard widget)

Test:

Creazione cliente con referral

Report Top Referrer corretto

Badge visualizzato

5) Loyalty "Tessera Timbri Digitale" (v1)
Obiettivo: Gamification soft (progress bar, no leaderboard pubblica).

Database:

sql
ALTER TABLE clienti ADD COLUMN loyalty_visits INTEGER DEFAULT 0;
ALTER TABLE clienti ADD COLUMN loyalty_threshold INTEGER DEFAULT 10; -- configurabile per cliente
Logic:

Increment automatico loyalty_visits ogni appuntamento completato (stato = 'completato')

Quando loyalty_visits >= loyalty_threshold → milestone raggiunta

UI Scheda Cliente:

Progress bar: "8/10 visite ⭐"

Testo: "Mancano 2 timbri per premio: Sconto 15%"

Badge visivo quando milestone raggiunta (stella dorata, confetti animati)

Suggerimento template WhatsApp:

text
Complimenti {{nome}}! 🌟
Hai raggiunto {{loyalty_threshold}} visite. Il prossimo servizio è scontato del 15%!
Grazie per la fedeltà 💚
Metafora: "Tessera Timbri" (nome friendly), NON "Loyalty Program" (troppo corporate).

File da creare:

Modifica src-tauri/src/commands/appuntamenti.rs (auto-increment loyalty)

src/components/LoyaltyProgressBar.tsx (in scheda cliente)

Test:

Loyalty increment post-appuntamento

Progress bar aggiornamento corretto

Badge milestone visualizzato

Criteri di accettazione Fase 5
 Template WhatsApp copy/paste funziona correttamente

 QR generati scansionabili e aprono WhatsApp con testo corretto

 Pacchetti creabili e assegnabili a clienti

 Referral tracking funziona e report è visibile

 Loyalty progress bar si aggiorna automaticamente post-appuntamento

 Tutto offline, zero API esterne obbligatorie

 UI coerente con Design Bible

 Tono messaggi: warm, non aggressivo (Sud Italia)

Aggiorna Stato: REGOLA 5.

FASE 6: FATTURAZIONE ELETTRONICA
LEGGI: docs/context/CLAUDE-FATTURE.md
LEGGI: .claude/agents/fatture-specialist.md

Deliverable:

Generazione XML FatturaPA

Validazione CF/P.IVA

Invio SDI (Sistema di Interscambio)

Tracking stato fattura

Durata: 3 giorni

Aggiorna Stato: REGOLA 5.

FASE 7: VOICE AGENT
LEGGI: docs/context/CLAUDE-VOICE.md ⭐
LEGGI: .claude/agents/voice-engineer.md

Stack:

STT: Groq Whisper Large v3

LLM: Groq Llama 3.3 70B

TTS: Piper (locale) - voce it_IT-paola-medium (femminile, default)

VoIP: Ehiweb SIP

Framework: Pipecat

Deliverable:

Pipeline completa STT → LLM → TTS

Integrazione VoIP Ehiweb

Intent detection (prenotazione, cancellazione, info)

System prompt ottimizzato

Log chiamate in database

Durata: 3 giorni

Aggiorna Stato: REGOLA 5.

FASE 8: BUILD + LICENZE
LEGGI: docs/context/CLAUDE-DEPLOYMENT.md
LEGGI: .claude/agents/devops.md
LEGGI: .claude/agents/release-engineer.md

Deliverable:

Build Tauri (macOS + Windows)

Code signing (macOS Developer ID, Windows Authenticode)

Auto-update (tauri-plugin-updater)

CI/CD GitHub Actions

Sistema licenze (Keygen.sh)

Durata: 2 giorni

Aggiorna Stato: REGOLA 5.

CONCLUSIONE PROMPT
Questo prompt è la tua guida operativa. Seguilo RIGOROSAMENTE.

Ricorda:

Leggi SEMPRE CLAUDE.md all'inizio di ogni sessione

Un agente alla volta

Workflow "SALVO TUTTO?" dopo ogni milestone (REGOLA 5 INVIOLABILE)

Debug sistematico con debugger.md

Zero-cost, offline-first, stabile su OS reali

Buon lavoro! 🚀

=== END PROMPT ===