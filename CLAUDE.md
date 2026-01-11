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

## PROTOCOLLO SVILUPPO AUTONOMO

> **Claude Code è l'ORCHESTRATORE**. Coordina agenti, sviluppa, testa e avanza autonomamente.

### Principi Fondamentali

1. **ORCHESTRATORE**: Coordino 16 agenti specializzati (vedi `.claude/agents/`)
2. **SVILUPPO AUTONOMO**: Sviluppo con agenti, senza attendere istruzioni step-by-step
3. **TEST SU iMAC**: Testo via SSH + MCP Server prima di far testare all'utente
4. **CI/CD OBBLIGATORIO**: Push + verifica GitHub Actions prima di ogni test utente
5. **SESSIONI SALVATE**: Ogni milestone → salvo sessione in `docs/sessions/`

### Infrastruttura Multi-Piattaforma

```yaml
# === MACCHINE DI TEST (Claude Code esegue test via SSH) ===

SSH iMac (macOS):
  host: imac (192.168.1.2)
  user: gianlucadistasi
  path: /Volumes/MacSSD - Dati/fluxion
  uso: Test macOS + Voice Agent

SSH Windows PC:
  host: 192.168.1.17
  user: gianluca
  path: C:\Users\gianluca\fluxion
  uso: Test Windows

# === PORTE SERVIZI ===
HTTP Bridge: porta 3001 (Axum, solo debug)
Voice Pipeline: porta 3002 (Python)
MCP Server: porta 5000 (TypeScript)

# === CI/CD ===
CI/CD: .github/workflows/ci.yml (macOS, Windows, Linux)
```

### Protocollo Test Automatico (SSH)

Claude Code DEVE eseguire test su ENTRAMBE le piattaforme:

```bash
# === TEST SU iMAC ===
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull && npm run tauri dev"

# === TEST SU WINDOWS ===
ssh gianluca@192.168.1.17 "cd C:\Users\gianluca\fluxion && git pull && npm run tauri dev"
```

**IMPORTANTE**: Dopo ogni implementazione significativa, Claude Code deve:
1. Push su GitHub
2. Attendere CI/CD
3. Test automatico su iMac via SSH
4. Test automatico su Windows via SSH
5. Verificare che entrambi funzionino prima di confermare all'utente

---

## CI/CD + LIVE TESTING

```bash
# 1. Commit + Push
git add . && git commit -m "feat: descrizione" && git push

# 2. Attendi CI/CD
gh run list --limit 1

# 3. Test su iMac
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull && npm run tauri dev"

# 4. MCP tools per test automatici
# take_screenshot(), executeScript(), etc.
```

---

## STATO CORRENTE

```yaml
fase: 7
nome_fase: "Voice Agent + WhatsApp + FLUXION IA"
ultimo_aggiornamento: 2026-01-11T16:00:00
ci_cd_run: "#153 SUCCESS"

completato:
  # >>> docs/context/COMPLETED-PHASES.md per dettagli <<<
  - Fase 0-6: Setup, Layout, CRM, Booking, Care, Loyalty, Fatturazione
  - Migrations: 001-013
  - Tauri Commands: 127+ totali (+7 voice)
  - HTTP Bridge: porta 3001 (15 endpoints)
  - Voice Pipeline: Python + 7 Tauri commands + RAG + Client Registration

in_corso: |
  Voice Agent Features (2026-01-11) - IN PROGRESS

  COMPLETATO OGGI:
  - ✅ RAG Fix: usa SEMPRE FAQ locale prima di Groq
  - ✅ TODO #5: Disambiguazione cliente con data_nascita
  - ✅ TODO #6: Registrazione nuovo cliente via conversazione
  - ✅ TODO #7: Preferenza operatore con alternative

  TESTATO OK:
  - FAQ: "quanto costa un taglio?" → "Uomo €18, Donna €35"
  - Estrazione data nascita (formato IT, slash, ISO)
  - Estrazione telefono, nome completo, cognome, email
  - Operatore preference con match nome/cognome

prossimo:
  - TODO #4: Waitlist con priorità VIP (endpoint esiste, logica da integrare)
  - Test end-to-end completo Voice Agent
  - Integrazione VoIP Ehiweb
  - WhatsApp QR scan

bug_da_fixare:
  - BUG-V2: ✅ RISOLTO (Stdio::null())
```

---

## VOICE AGENT ROADMAP

### Funzionalità Database Voice Agent

| # | Funzionalità | Endpoint | Status |
|---|--------------|----------|--------|
| 1 | Cerca clienti (nome, cognome, telefono, email, soprannome) | `/api/clienti/search` | ✅ |
| 2 | Crea appuntamenti | `/api/appuntamenti/create` | ✅ |
| 3 | Verifica disponibilità | `/api/appuntamenti/disponibilita` | ✅ |
| 4 | Lista d'attesa con priorità VIP | `/api/waitlist/add` | ⏳ Endpoint OK, integrazione pending |
| 5 | Fallback identificazione con data_nascita | `/api/clienti/search` + pipeline | ✅ |
| 6 | Registrazione nuovo cliente (Voice + WA) | `/api/clienti/create` + pipeline | ✅ |
| 7 | Preferenza operatore in prenotazione | `/api/operatori/list` + pipeline | ✅ |

### TODO #4: Waitlist con Priorità VIP

```yaml
Endpoint: POST /api/waitlist/add
Request:
  cliente_id: string
  servizio_id: string
  data_richiesta: string  # YYYY-MM-DD
  ora_richiesta: string   # HH:MM

Logica:
  1. Verifica se cliente è VIP (SELECT is_vip FROM clienti)
  2. Se VIP → priorita = 10
  3. Se non VIP → priorita = 1
  4. INSERT INTO waitlist con priorità

Response:
  success: bool
  posizione: int  # Posizione in lista
  vip_boost: bool
```

### TODO #5: Identificazione Cliente con Fallback

```yaml
Logica identificazione (in ordine):
  1. Cerca per NOME → se 1 match → OK
  2. Se >1 match → cerca per SOPRANNOME
  3. Se ancora >1 match → chiedi DATA NASCITA
  4. Voice Agent chiede: "Ho trovato più clienti con questo nome. Mi può dire la sua data di nascita?"

Upgrade endpoint /api/clienti/search:
  - Aggiungere campo data_nascita alla query
  - Nuovo parametro: ?by_birthdate=YYYY-MM-DD
  - Ritorna match_count per gestire ambiguità
```

### TODO #6: Registrazione Nuovo Cliente (Voice + WhatsApp)

```yaml
Skill: Aggiunta nuovo cliente tramite conversazione
Agenti: Voice Agent + WhatsApp Agent

Flow conversazionale:
  1. Cliente non trovato → "Non la trovo in archivio. Vuole registrarsi?"
  2. Se sì → chiedi in sequenza:
     - Nome
     - Cognome
     - Telefono (se Voice) / già noto (se WhatsApp)
     - Email (opzionale)
     - Data di nascita (per identificazione futura)
     - Soprannome (opzionale, "Come preferisce essere chiamato?")
  3. Riepilogo: "Ho registrato: Mario Rossi, tel 333..."
  4. Conferma → INSERT INTO clienti

Endpoint: POST /api/clienti/create
Request:
  nome: string
  cognome: string
  telefono: string
  email: string (optional)
  data_nascita: string (optional, YYYY-MM-DD)
  soprannome: string (optional)
  fonte: "voice" | "whatsapp" | "manual"

Response:
  success: bool
  cliente_id: string
  messaggio_conferma: string
```

### TODO #7: Preferenza Operatore in Prenotazione

```yaml
Skill: Gestione preferenza operatore per appuntamento
Agenti: Voice Agent + WhatsApp Agent

Flow conversazionale:
  1. Cliente chiede prenotazione
  2. Voice Agent chiede: "Ha un operatore preferito?"
  3. Se sì → cerca operatore per nome
  4. Verifica disponibilità CALENDARIO:
     a. Slot liberi nel giorno richiesto
     b. Operatore disponibile in quello slot
  5. Se operatore NON disponibile:
     - Cerca altri operatori disponibili per quel servizio
     - Propone alternativa con DOTI POSITIVE:
       "Mario non è disponibile martedì, ma c'è Laura che è
        specializzata in colorazioni ed ha molta esperienza!"
  6. Se nessun operatore disponibile → propone altri giorni

Endpoint: GET /api/operatori/list
Response:
  operatori: [{
    id, nome,
    specializzazioni: ["taglio", "colore"],
    descrizione_positiva: "Specialista colorazioni, 10 anni esperienza"
  }]

Endpoint: GET /api/operatori/disponibilita
Request:
  operatore_id: string
  data: string (YYYY-MM-DD)
  servizio_id: string
Response:
  disponibile: bool
  slots: ["09:00", "10:00", ...]

Endpoint: GET /api/calendario/verifica-slot
Request:
  data: string (YYYY-MM-DD)
  ora: string (HH:MM)
  operatore_id: string (optional)
  servizio_id: string
Response:
  disponibile: bool
  operatori_alternativi: [{id, nome, descrizione_positiva}]
  slot_alternativi: ["10:00", "11:00"]

Logica in pipeline.py:
  - Estrai nome operatore da testo ("con Mario", "da Paola")
  - Cerca in lista operatori
  - Verifica calendario per slot + operatore
  - Se non disponibile → proponi alternativa con descrizione positiva
```

### Dipendenze

- Tabella `waitlist` già esiste (migration 005)
- Campo `is_vip` già esiste su `clienti`
- Campo `data_nascita` già esiste su `clienti`
- Campo `soprannome` già esiste e cercato
- Tabella `clienti` già ha tutti i campi necessari
- Tabella `operatori` già esiste
- Tabella `operatori_servizi` già esiste

> **Cronologia sessioni**: `docs/context/SESSION-HISTORY.md`
> **Decisioni architetturali**: `docs/context/DECISIONS.md`

---

## FASI PROGETTO

| Fase | Nome | Status |
|------|------|--------|
| 0 | Setup Iniziale | ✅ |
| 1 | Layout + Navigation | ✅ |
| 2 | CRM Clienti | ✅ |
| 3 | Calendario + Booking | ✅ |
| 4 | Fluxion Care | ✅ |
| 5 | Quick Wins Loyalty | ✅ |
| 6 | Fatturazione Elettronica | ✅ |
| 7 | Voice Agent + WhatsApp | 📋 IN CORSO |
| 8 | Build + Licenze | 📋 TODO |
| 9 | Moduli Verticali | 📋 TODO |

---

## SISTEMA AGENTI

### Tabella Routing (24 agenti)

| Keyword | Agente | Contesto |
|---------|--------|----------|
| rust, tauri, sqlite | rust-backend | CLAUDE-BACKEND.md |
| react, hook, component | react-frontend | CLAUDE-FRONTEND.md |
| design, css, tailwind | ui-designer | CLAUDE-DESIGN-SYSTEM.md |
| voice, whisper, tts | voice-engineer | CLAUDE-VOICE.md |
| whatsapp, api | integration-specialist | CLAUDE-INTEGRATIONS.md |
| fattura, xml, sdi | fatture-specialist | CLAUDE-FATTURE.md |
| test, e2e | e2e-tester | docs/testing/e2e/ |
| build, deploy | devops | CLAUDE-DEPLOYMENT.md |
| security, audit | security-auditor | — |
| gh, github, ci | github-cli-engineer | CLAUDE-GITHUB-CLI.md |

> **Lista completa**: `.claude/agents/` (24 file)

### Invocazione

```
@agent:rust-backend Crea lo schema SQLite per la tabella clienti
```

---

## WORKFLOW SESSIONE

### Inizio
1. Leggi CLAUDE.md
2. Controlla `in_corso`
3. Seleziona agente appropriato

### Fine (OBBLIGATORIO)
```
✅ Milestone completata: [descrizione]
SALVO TUTTO? (aggiorna CLAUDE.md + crea sessione + git commit)
```

Se "sì":
1. Aggiorna CLAUDE.md
2. Crea `docs/sessions/YYYY-MM-DD-HH-MM-descrizione.md`
3. `git add . && git commit && git push`

---

## RIFERIMENTI RAPIDI

| Risorsa | Path |
|---------|------|
| Fasi Completate | docs/context/COMPLETED-PHASES.md |
| Cronologia Sessioni | docs/context/SESSION-HISTORY.md |
| Decisioni Architetturali | docs/context/DECISIONS.md |
| AI Live Testing | docs/AI-LIVE-TESTING.md |
| Design Bible | docs/FLUXION-DESIGN-BIBLE.md |
| Schema DB | docs/context/CLAUDE-BACKEND.md |
| Voice Agent | docs/context/CLAUDE-VOICE.md |

---

## VARIABILI AMBIENTE

```bash
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556
GITHUB_TOKEN=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
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it
TTS_VOICE_MODEL=it_IT-paola-medium
WHATSAPP_PHONE=393281536308
```

---

## REQUISITI SISTEMA

- **Windows**: 10 build 1809+ o Windows 11
- **macOS**: 12 Monterey o superiore

---

*Ultimo aggiornamento: 2026-01-11T10:00:00*
