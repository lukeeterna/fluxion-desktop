# FLUXION — Handoff Sessione 55 → 56 (2026-03-12)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 12757b3
fix(eslint): risolve 5 errori pre-existing
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅
```

---

## ✅ COMPLETATO SESSIONE 55
| Commit | Descrizione |
|--------|-------------|
| `12757b3` | ESLint fix: localStorage/IntersectionObserver globals + VoiceAgent escape |

### F08 Test Live API T1-T5 ✅
- T1-T5 tutti PASS via SSH → Sara 597ms P50 (target <800ms ✅)
- Sara v2.1.0 attiva su iMac

### CoVe 2026 Deep Research Sara Enterprise Grade ✅
- 3 subagenti completati: benchmark mondiali + codebase audit + NLU italiano
- **116 pattern NLU analizzati**: 27% coperti · 31% parziali · **42% non coperti**
- **94 gap totali identificati**: 9 P0 · 13 P1 · 15+ P2
- Research files: `.claude/cache/agents/sara-enterprise-agente-[a|b|c].md`

---

## 🔴 SPRINT 1 — Sara Enterprise P0 (PROSSIMA SESSIONE S56)
> **Questo è il task della prossima sessione. NON deviare.**
> Skill: `fluxion-voice-agent` | Python su iMac via SSH

### 9 Fix P0 con file:riga precisi

#### FIX-1: TimeConstraint AFTER applicato solo se slot occupato
- **File**: `voice-agent/src/orchestrator.py:1023`
- **Bug**: `if time_constraint_type and time_constraint_anchor and not slot_available:` — constraint mai applicato se slot è libero
- **Fix**: Applicare constraint PRIMA del check disponibilità. Se `constraint_type=AFTER` e `proposed_time <= anchor`, scartare e cercare primo slot > anchor
- **Test**: "dopo le 17" → Sara propone 17:30 (non 17:00)

#### FIX-2: FSM loop in CONFIRMING su correzione orario
- **File**: `voice-agent/src/booking_state_machine.py` — stato CONFIRMING
- **Bug**: Quando utente dice "no, dopo le 17 non alle 17" in stato CONFIRMING, Sara risponde "Perfetto! ora → 17:00. Confermi ora?" in loop
- **Fix**: In `_handle_confirming()`, aggiungere detection correzione temporale → exit CONFIRMING → re-extract time → ri-cercare slot
- **Test**: Loop di Fabrizio Corona eliminato

#### FIX-3: Groq Too Many Requests mid-call
- **File**: `voice-agent/src/orchestrator.py` — Groq client
- **Bug**: Key rotation insufficiente, nessun backoff, risposta vuota al cliente
- **Fix**: Exponential backoff 3 tentativi · fallback response immediato ("Un momento...") · log silenzioso senza mostrare errore al cliente
- **Test**: Simulare rate limit → risposta graceful

#### FIX-4: Sentiment falso positivo "no/ma/senti"
- **File**: `voice-agent/src/sentiment.py:103` — `WORD_BOUNDARY_KEYWORDS`
- **Bug**: "no" (peso 1), "ma" (peso 1), "però" (peso 1) accumulano frustration score → escalation operatore su frasi normali
- **Fix**: Rimuovere "no/ma/però/senti" da WORD_BOUNDARY_KEYWORDS · aggiungere reset storia su cambio intent rilevato
- **Test**: Conversazione Fabrizio Corona: nessuna falsa escalation

#### FIX-5: TTS legge "13/03" → "tredici barra tre"
- **File**: `voice-agent/src/tts.py:37` — `preprocess_for_tts()`
- **Bug**: Funzione espande solo telefoni, non date. "13/03" → Piper/SystemTTS legge "tredici barra tre" o "tredici zero tre"
- **Fix**: Aggiungere `_expand_date_for_tts()`: `13/03` → `tredici marzo` · `13/03/2026` → `tredici marzo duemilaventisei`
- **Test**: Conferma prenotazione "giovedì 13 marzo" letta correttamente

#### FIX-6: Numero telefono loggato in chiaro (GDPR)
- **File**: `voice-agent/src/orchestrator.py:2204`
- **Bug**: `print(f"[DEBUG] Creating client: {payload}")` include nome/cognome/telefono in chiaro in `/tmp/voice-pipeline.log`
- **Fix**: Masking `_mask_pii(payload)`: `telefono → "33*****789"`, `cognome → "R***"` nei log DEBUG
- **Test**: Grep su log dopo conversazione → nessun dato PII in chiaro

#### FIX-7: Date in lettere "il tre/sette/ventidue" non estratte
- **File**: `voice-agent/src/entity_extractor.py:316`
- **Bug**: `it_numbers` dict non usato in `extract_date()`. Pattern `\bil\s+(\d{1,2})\b` cattura solo cifre, non parole
- **Fix**: Normalizzare testo PRIMA del pattern: `"il tre"` → `"il 3"` con dict 1-31 completo
- **Test**: "voglio venire il sette" → data estratta correttamente

#### FIX-8: "Il primo" del mese bloccato da NAME_BLACKLIST
- **File**: `voice-agent/src/entity_extractor.py:887`
- **Bug**: `"primo"` è in NAME_BLACKLIST (per evitare estrazione come nome). "Voglio venire il primo" → dead end
- **Fix**: Check speciale PRE-blacklist: `r"\bil\s+primo\b"` → giorno 1 del mese corrente/prossimo
- **Test**: "il primo del mese" → data 1° estratta

#### FIX-9: Range orari "tra le 3 e le 4" → 03:00-04:00 invece di 15:00-16:00
- **File**: `voice-agent/src/entity_extractor.py:692`
- **Bug**: `_disambiguate_hour_pm()` chiamata solo per ora singola (PHASE 5), mai per range (PHASE 3)
- **Fix**: Una riga: aggiungere `start_h = _disambiguate_hour_pm(start_h, text)` e `end_h = _disambiguate_hour_pm(end_h, text)` in PHASE 3
- **Test**: "tra le 3 e le 4 del pomeriggio" → RANGE 15:00-16:00

---

## 🟡 SPRINT 2 — Sara Enterprise P1 (sessione S57)
13 fix: multi-servizio · flexible scheduling · streaming LLM · fallback progressivo · slot waterfall · selezione ordinale slot · FAQ mid-booking resume · sessioni concorrenti · escalation context · anchors CONFERMA/RIFIUTO · "anzi" standalone · TIME_PRESSURE · constraint negativi

## 🟢 SPRINT 3 — Sara Enterprise P2 (post-prima vendita)
Dialetti · multi-persona booking · prenotazione ricorrente · storico cliente · FCR/AHT analytics · verticali palestra/medical/auto · Groq system prompt con dati aziendali reali

---

## 📦 CONTESTO F15 VoIP — SALVATO (non perdere)
- Architettura: pjsua2 Python su iMac → bridge SIP → Sara localhost
- EHIWEB: mail partnership inviata (Gianluca Di Stasi, fondatore FLUXION)
- Alternativa test: `sip.linphone.org` (gratuito)
- Research: `.claude/cache/agents/f15-voip-architecture-agente-a.md` + `f15-ehiweb-termux-agente-b.md`
- **Riprende dopo Sara Sprint 1+2 completati**

---

## TODO iMac (quando raggiungibile — non urgente)
1. Configurare evento `order_refunded` su dashboard LemonSqueezy (2min, manuale)
2. Catturare `fx_voice_agent.png` per landing page

---

## Checkout URLs LemonSqueezy (PERMANENTI)
- Base €497: `https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3`
- Pro €897: `https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702`
- Clinic €1.497: `https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023`

---

## PROMPT SESSIONE S56 — Sara Enterprise Sprint 1

```
TASK S56: "Sara Enterprise Grade Sprint 1 — 9 fix P0"

CONTESTO:
- Fondatore: Gianluca Di Stasi | Landing: https://fluxion-landing.pages.dev
- Branch: master | HEAD: 12757b3 | iMac: 192.168.1.12 (voice pipeline 127.0.0.1:3002)
- Python su iMac (3.9) — NO Rust build

OBIETTIVO: Correggere i 9 bug P0 che rendono Sara non enterprise grade.
Verificato da conversazione reale (Fabrizio Corona) che ha mostrato:
  - "dopo le 17" → Sara propone 17:00 (sbagliato)
  - Loop infinito in CONFIRMING su correzione orario
  - Groq "Too Many Requests" mid-call
  - Falsa escalation operatore su frasi normali

RESEARCH COMPLETATA (NON rifare — leggere direttamente):
  .claude/cache/agents/sara-enterprise-agente-a.md (benchmark mondiali)
  .claude/cache/agents/sara-enterprise-agente-b.md (codebase audit 37 gap)
  .claude/cache/agents/sara-enterprise-agente-c.md (116 pattern NLU italiani)

I 9 FIX P0 con file:riga ESATTI (da HANDOFF.md):
  FIX-1: orchestrator.py:1023 — TimeConstraint AFTER pre-check
  FIX-2: booking_state_machine.py — CONFIRMING loop su correzione
  FIX-3: orchestrator.py — Groq backoff + graceful fallback
  FIX-4: sentiment.py:103 — rimuovi "no/ma/però" da WORD_BOUNDARY
  FIX-5: tts.py:37 — preprocess_for_tts() + date expansion
  FIX-6: orchestrator.py:2204 — mask PII nei log (GDPR)
  FIX-7: entity_extractor.py:316 — date in lettere "il tre/sette"
  FIX-8: entity_extractor.py:887 — "il primo" pre-blacklist check
  FIX-9: entity_extractor.py:692 — range orari PM disambiguation

WORKFLOW OBBLIGATORIO:
  1. Skill: fluxion-voice-agent (già identificata)
  2. Research: GIÀ FATTA — leggi i 3 file .md sopra, NON rilanciare agenti
  3. Per ogni fix: leggi il file esatto → implementa → test curl via SSH
  4. Test SSH: ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/process ..."
  5. Dopo ogni fix: pytest voice-agent/tests/ su iMac
  6. Commit atomico per ogni fix (9 commit separati)
  7. Fine: push + sync iMac + update HANDOFF + MEMORY

ACCEPTANCE CRITERIA (tutti verificati):
  AC1: "dopo le 17" → Sara propone slot >= 17:30 (mai 17:00)
  AC2: Correzione orario in CONFIRMING → exit loop, ri-proposta slot
  AC3: Groq rate limit → risposta graceful, conversazione prosegue
  AC4: "No, senti, voglio prenotare" → NESSUNA escalation operatore
  AC5: Conferma "giovedì 13 marzo" → letta correttamente da TTS
  AC6: grep /tmp/voice-pipeline.log → 0 risultati con telefono/cognome in chiaro
  AC7: "voglio venire il sette" → data estratta
  AC8: "voglio venire il primo" → giorno 1 estratto
  AC9: "tra le 3 e le 4 del pomeriggio" → RANGE 15:00-16:00

REGOLE FERME:
  - Python SOLO su iMac via SSH (non su MacBook)
  - MAI --no-verify
  - Riavvio pipeline dopo OGNI modifica .py su iMac
  - pytest su iMac dopo ogni fix
  - Conversazione Fabrizio Corona deve passare end-to-end senza errori
```
