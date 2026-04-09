# FLUXION — Handoff Sessione 139 → 140 (2026-04-09)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 139

### 1. Sprint 4 — Landing con Video Embeddato
- Video landing multi-settore (12MB, 16:9) embeddato nella landing
- Sostituito vecchio `fluxion-demo.mp4` (4MB) con `landing_final_16x9.mp4` (12MB)
- HTML5 `<video>` tag con poster dashboard, controls, preload=metadata
- Caption aggiornata: "Guarda come FLUXION gestisce il tuo salone, palestra, clinica o officina"

### 2. VideoObject JSON-LD
- Schema.org markup per Google rich results
- `@type: VideoObject`, duration PT1M20S, lingua it, thumbnailUrl dashboard

### 3. CF Pages Deploy Fix
- **SCOPERTO**: `--branch=production` NON aggiorna il dominio principale
- **FIX**: `--branch=main` aggiorna fluxion-landing.pages.dev (produzione)
- MEMORY aggiornata con il comando corretto

### 4. Pulizia Assets
- 238MB di video promo inutilizzati spostati in `landing-assets-archive/`
- Landing deploy size: 35MB (da 270MB+)

### 5. Test E2E Landing (6/6 PASS)
- Landing HTTP 200 (128KB)
- Video serve HTTP 200 (video/mp4)
- Stripe CTA link presente
- /grazie HTTP 200
- /installa HTTP 200
- JSON-LD VideoObject presente

### 6. Skills Suite (34 nuove skill installate)
- Estratte da `claude_code_skills_suite.zip` in `.claude/skills/<nome>/SKILL.md`
- Categorie: engineering(6), marketing(7), design(5), testing(5), product(3), project-management(3), studio-operations(5)
- Totale: 47 skill (13 fluxion + 34 generiche + deep-research)

### 7. CLAUDE.md — Nuove Sezioni Integrate
- Regola Zero (Skill → Agent → Execute)
- Sistema Due Livelli (skills vs agents)
- Routing nuove categorie: PRODUCT, engineering extras, reddit
- Skill Trasversali, Protocollo per Task Tipo, Guardrails Permanenti
- Indice completo 47 skill installate
- **NULLA di esistente toccato/rimosso**

### 8. Stress Test Sara per Verticale
- 173 test point su 6 verticali (conversazioni multi-turn identiche al flusso telefono)
- File: `voice-agent/tests/e2e/test_sara_stress_per_verticale.py` (789 righe)
- 87 OK / 80 WARN / 6 FAIL — 5 bug identificati

---

## STATO GIT
```
Branch: master | HEAD: ab62df4 (uncommitted: landing, video, skills, CLAUDE.md, stress test)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10e: Sara Bug Fixes       DONE (S127, S134, S135)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    DONE (S137-S138)
Sprint 4:  Landing Definitiva   QUASI DONE (S139) — manca solo test responsive device reale
Sprint 5:  Sales Agent WA       PENDING
```

---

## STRESS TEST SARA — RISULTATI COMPLETI (tutti 6 verticali)
```
TOTALE: 87 OK / 80 WARN / 6 FAIL su 173 test point
P50 latenza: 488ms | Post warm-up: 350-900ms

PER VERTICALE:
  SALONE:        19 OK / 15 WARN / 1 FAIL (latenza)
  AUTO:          14 OK / 21 WARN / 1 FAIL (guardrail)
  MEDICAL:       13 OK / 11 WARN / 1 FAIL (guardrail)
  PALESTRA:      13 OK / 11 WARN / 1 FAIL (guardrail)
  BEAUTY:        15 OK / 12 WARN / 1 FAIL (latenza)
  PROFESSIONALE: 13 OK / 10 WARN / 1 FAIL (guardrail)
```
File: `voice-agent/tests/e2e/test_sara_stress_per_verticale.py` (789 righe)
Run: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && PYTHONUNBUFFERED=1 python tests/e2e/test_sara_stress_per_verticale.py"`

## BUG DA FIXARE (emersi dallo stress test)
1. **GUARDRAIL NON VERTICAL-AWARE** (4 FAIL): "taglio capelli" accettato su auto/medical/palestra/professionale
2. **LATENZA FIRST-TURN** (2 FAIL): 10-23s primo turno warm-up Groq → pre-warm o keep-alive
3. **SLOT DB VUOTO** (WARN): conferma booking fallisce su tutti i verticali — solo servizi salone nel DB demo
4. **set_vertical non stabile**: primo turn post-reset a volte risponde col verticale sbagliato
5. **Servizi non-salone non riconosciuti**: entity_extractor ha solo servizi salone nel DB

## BUG CRITICI DA LIVE TEST TELEFONO (S139 — fondatore ha chiamato)
> **SARA NON PUO' ANDARE LIVE COSI'. Ogni bug = cliente perso.**

### P0 — BLOCCANTI (fix PRIMA di tutto il resto)
1. **STT trascrive cognome come "Grazie"** — utente dice cognome, Groq STT sente "Grazie." (3 volte). Deep research: confronto STT models, post-processing, confidence threshold, retry logic
2. **VAD parla sopra l'utente** — turni troppo corti (920ms, 800ms), Sara interrompe. Deep research: VAD sensitivity, silence detection threshold, minimum turn length, barge-in prevention
3. **Ricerca nome estrae "di" invece del cognome** — "Marco di nome Galli di cognome" → cerca "di" nel DB. Il surname extractor non filtra stop-words italiane
4. **NameCorrector DB schema rotto** — `no such column: a.data` — crash silenzioso
5. **Prima chiamata si disconnette subito** — 0 pacchetti RX, call time 0s, poi richiamata funziona

### P1 — UX GRAVE
6. **Sara chiede cognome separatamente** — se dico "Marco Rossi" in un turno, deve capire nome+cognome insieme
7. **Guardrail non vertical-aware** (4 FAIL stress test): "taglio capelli" accettato su auto/medical/palestra
8. **Latenza first-turn** 10-23s warm-up Groq

### APPROCCIO RICHIESTO (fondatore)
- **Deep Research ESPLICITA** con `/deep-research` skill + `voice-engineer` agent per OGNI bug P0
- Usare le nuove skill (`/ai-engineer`, `/backend-architect`) + agent routing table
- Obiettivo: esperienza utente FANTASTICA, non "funziona"

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 140.
PROSSIMI PASSI:
1. P0 BUG CRITICI DA LIVE TEST — PRIORITA' ASSOLUTA:
   a. Deep research STT accuracy: perche' Groq trascrive male i cognomi italiani? Soluzioni?
   b. Deep research VAD: come evitare che Sara parli sopra? Threshold, min turn length, barge-in
   c. Fix surname extractor: filtrare stop-words italiane ("di", "del", "da", "nome", "cognome")
   d. Fix NameCorrector DB: column "a.data" non esiste
   e. Fix prima chiamata disconnessa
2. P1: nome+cognome in un turno, guardrail vertical-aware, latenza
3. Re-run stress test + LIVE TEST TELEFONO per verificare
4. SOLO DOPO: Sprint 5 Sales Agent
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
REGOLA: Deep Research OBBLIGATORIA per ogni fix P0 (usa /deep-research skill)
REGOLA: Usa Agent Routing Table + Skills in CLAUDE.md per OGNI task
REGOLA: voice-engineer agent per implementazione, sara-nlu-trainer per NLU, sara-fsm-architect per FSM
REGOLA: Dopo OGNI fix → stress test + live test telefono
```
