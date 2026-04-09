# FLUXION — Handoff Sessione 140 → 141 (2026-04-09)

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

## COMPLETATO SESSIONE 140

### P0 Bug Critici da Live Test Telefono — TUTTI FIXATI

#### P0-a: STT trascrive cognome come "Grazie"
- **Root cause**: Decoder language model bias — P("Grazie") >> P("Di Stasi") in Whisper training data
- **Fix 1**: Enhanced Whisper prompt: 800 char budget (was 400), names at END for decoder recency bias
- **Fix 2**: State-aware prompting: name-biased prompt during WAITING_NAME/IDLE, generic for other states
- **Fix 3**: Common-word rejection: "Grazie"/"Prego" etc. rejected deterministically when FSM expects a name → asks to repeat
- **Research**: `.claude/cache/agents/stt-italian-surnames-research.md` (375 righe)

#### P0-b: VAD parla sopra l'utente
- **Root cause**: silence_timeout 700ms troppo corto per italiano; min_speech 60ms triggera su eco/rumore
- **Fix 1**: silence_timeout 35→75 frames (700ms→1500ms) — matches Italian phone conventions (Google default 2000ms)
- **Fix 2**: min_speech 3→15 frames (60ms→300ms) — reject coughs/echo/noise
- **Fix 3**: speech_threshold 500→600 — reject phone line noise (200-400 RMS)
- **Fix 4**: Anti-echo grace 0.6s→0.8s — covers G.711 round-trip + phone reverb
- **Fix 5**: Audio quality gate: reject turns <300ms or RMS<400 before dispatching to STT
- **Research**: `.claude/cache/agents/vad-barge-in-research.md` (536 righe)

#### P0-c: Ricerca nome estrae "di" invece del cognome
- **Fix**: Added "di", "da", "dal", "dalla", "dallo", etc. to NAME_BLACKLIST
- **Fix**: New regex patterns for "X di nome Y di cognome" and "nome X cognome Y" format
- **Fix**: Multi-group match handling (2 capture groups → combined nome+cognome)

#### P0-d: NameCorrector DB schema rotto
- **Fix**: `a.data` → `a.data_ora_inizio` in name_corrector.py SQL query

#### P0-e: Prima chiamata si disconnette subito
- **Fix**: Send 180 Ringing before 200 OK, with 1s delay for ICE/STUN candidate gathering
- Separate thread for delayed answer to avoid blocking pjsua2 event loop

### Stress Test Results (MIGLIORATI)
```
BEFORE (S139): 87 OK / 80 WARN / 6 FAIL su 173 test
AFTER  (S140): 96 OK / 70 WARN / 5 FAIL su 171 test
                +9 OK  / -10 WARN / -1 FAIL

PER VERTICALE:
  SALONE:        25 OK /  8 WARN / 0 FAIL (was 1 FAIL - FIXED!)
  BEAUTY:        15 OK / 10 WARN / 0 FAIL (was 1 FAIL - FIXED!)
  AUTO:          19 OK / 18 WARN / 2 FAIL (guardrail + latency)
  MEDICAL:       12 OK / 11 WARN / 1 FAIL (guardrail)
  PALESTRA:      13 OK / 11 WARN / 1 FAIL (guardrail)
  PROFESSIONALE: 12 OK / 12 WARN / 1 FAIL (guardrail)

Latenza: P50=1014ms | P95=10716ms (warm-up Groq → P1 fix needed)
```

### Unit Tests
- 178 passed / 1 pre-existing fail (unrelated follow_up text assertion)

---

## STATO GIT
```
Branch: master | HEAD: c7e6a00
Commits S140:
  f9be590 fix(S140): P0-c/d/e — surname stop-words, NameCorrector DB, first call disconnect
  c7e6a00 fix(S140): P0-a/b — STT state-aware prompting + VAD turn-taking tuning
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10e: Sara Bug Fixes       DONE (S127, S134, S135, S140 P0 fixes)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    DONE (S137-S138)
Sprint 4:  Landing Definitiva   DONE (S139)
Sprint 5:  Sales Agent WA       PENDING
```

---

## BUG RIMANENTI (P1)

### P1 — Da fixare nella prossima sessione
1. **Guardrail non vertical-aware** (4 FAIL): "taglio capelli" accettato su auto/medical/palestra/professionale
   - Serve: lista servizi ammessi per verticale, blocco se servizio non nel verticale corrente
2. **Latenza first-turn**: 3-10s warm-up Groq (P95=10716ms)
   - Serve: pre-warm Groq API call all'avvio pipeline + keep-alive
3. **Nome+cognome in un turno**: se dico "Marco Rossi" in un turno, deve capire nome+cognome insieme
   - Serve: fix entity_extractor per estrarre nome+cognome da "sono Marco Rossi"
4. **Servizi non-salone non riconosciuti in booking flow**: DB ha solo servizi salone demo
   - Per produzione irrilevante (ogni cliente avrà i suoi servizi)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 141.
PROSSIMI PASSI:
1. P1 GUARDRAIL VERTICAL-AWARE — bloccare servizi non pertinenti per verticale
2. P1 LATENZA — pre-warm Groq API + keep-alive connection
3. P1 NOME+COGNOME — estrarre nome+cognome insieme da "sono Marco Rossi"
4. LIVE TEST TELEFONO — il fondatore deve richiamare e testare i fix P0
5. SOLO DOPO i P1: Sprint 5 Sales Agent WA
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
REGOLA: voice-engineer agent per implementazione, sara-nlu-trainer per NLU
REGOLA: Dopo OGNI fix → stress test + live test telefono
```
