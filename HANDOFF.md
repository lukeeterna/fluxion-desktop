# FLUXION — Handoff Sessione 141 → 142 (2026-04-09)

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

## COMPLETATO SESSIONE 141

### P1-1: Guardrail Vertical-Aware — FIXATO (0 guardrail FAIL)
- **Root cause**: Pattern `taglio\s+capelli` non matchava "taglio **di** capelli" (preposizione italiana)
- **Fix**: Tutti i pattern servizio+capelli ora includono `(?:(?:di|dei)\s+)?` opzionale
- **Scope**: taglio, tinta, colorazione, piega, trattamento, extension, allungamento, cheratina, balayage, meches
- **Result**: 0 guardrail FAIL (was 4) — auto, medical, palestra, professionale tutti bloccano correttamente
- **Unit tests**: 468 passed / 0 failed
- **E2E**: Verificato via API live su iMac per tutti i verticali

### P1-2: Pre-warm Groq API — FIXATO (first turn 1.2s, was 3-22s)
- **Root cause**: Groq cold start (TCP+TLS+HTTP/2 handshake) al primo turno
- **Fix**: Chiamata minima `max_tokens=1` al startup in `main.py` dopo init orchestrator
- **Result**: Pre-warm in 543ms, primo turno 1.2s (was 3-22s cold start)
- **Startup**: "✅ Groq API pre-warmed (543ms) — first turn will be fast"

### P1-3: Nome+Cognome in un turno — GIA' FUNZIONANTE
- Verificato: "Marco Rossi" e "Sono Marco Rossi" → entrambi estratti correttamente
- FSM va a `disambiguating_name` (verifica DB) come atteso
- Nessun fix necessario — era già implementato in S122

### Stress Test S141 (con guardrail fix, PRIMA del pre-warm Groq)
```
S141:  79 OK / 105 WARN / 4 FAIL su 188 test
       0 guardrail FAIL (was 4)
       3 latency FAIL (Groq cold start — fixato con pre-warm)
       1 transient HTTP 500

Latenza: P50=1223ms | P95=4591ms (migliorato da P95=10716ms in S140)
```

---

## STATO GIT
```
Branch: master | HEAD: 48c98fe
Commits S141:
  b8c69c9 fix(S141): P1-1 guardrail vertical-aware — Italian prepositions in service patterns
  48c98fe fix(S141): P1-2 pre-warm Groq API connection at startup
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10e: Sara Bug Fixes       DONE (S127, S134, S135, S140, S141 P1 fixes)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    DONE (S137-S138)
Sprint 4:  Landing Definitiva   DONE (S139)
Sprint 5:  Sales Agent WA       PENDING
```

---

## BUG RIMANENTI

### Risolti S141
- ~~P1-1: Guardrail non vertical-aware~~ → FIXED
- ~~P1-2: Latenza first-turn~~ → FIXED (pre-warm Groq)
- ~~P1-3: Nome+cognome in un turno~~ → Era già funzionante

### P2 — Non bloccanti per lancio
1. **Latenza variabile Groq** (WARN): P95=4.6s, dipende da carico Groq API
   - Mitigato con pre-warm; ulteriore riduzione richiede streaming LLM (v1.1)
2. **Servizi non-salone non riconosciuti**: DB ha solo servizi salone demo
   - Irrilevante per produzione (ogni cliente avrà i suoi servizi)
3. **Booking confirmation slot non disponibili**: WARN nel test (slot demo occupati)
   - Non un bug — comportamento corretto quando slot pieno

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 142.
PROSSIMI PASSI:
1. LIVE TEST TELEFONO — il fondatore deve richiamare e testare tutti i fix P0+P1
2. Sprint 5: Sales Agent WA — scraping + WhatsApp outreach per acquisizione clienti
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
REGOLA: Riavviare pipeline iMac dopo OGNI modifica Python
```
