# FLUXION — Handoff Sessione 58 → 59 (2026-03-12)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 3ef64d8
fix(sara): F02 — fix urgency type (str not bool) + pronto soccorso via visit_type
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1334 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 58 — F02 Vertical Guardrail + Live Audio Tests

### F02 Vertical Guardrail Fixes (2 fix, commit `0afdae7` + `3ef64d8`)

| Fix | File | Descrizione | Stato |
|-----|------|-------------|-------|
| GAP-G3 | booking_state_machine.py | Palestra abbonamento → soft escalation segreteria | ✅ |
| GAP-G2 | orchestrator.py | Medical urgency → 118 advisory (urgency="urgente" OR visit_type="urgenza") | ✅ |

**New tests**: `tests/test_f02_vertical_fixes.py` — 11 test, 11 PASS
**pytest iMac S58**: 1334 PASS / 0 FAIL ✅ (+11 rispetto a S57)

### Live Audio Tests T1-T5

| Test | Scenario | Risultato |
|------|----------|-----------|
| T1 | Gino vs Gigio disambiguazione fonetica | ✅ PHONETIC_VARIANTS gino↔gigio verificati |
| T2 | Gigi → Gigio soprannome canonico | ✅ PHONETIC_VARIANTS gigi↔gigio verificati |
| T3 | Chiusura graceful ASKING_CLOSE_CONFIRMATION→completed | ✅ FSM completato, WA response inviata |
| T4 | Flusso perfetto nuovo cliente → booking → WA close | ✅ Registrazione + booking + confirmed |
| T5 | Slot occupato → waterfall alternative (P1-5) | ✅ slot_unavailable_alternatives intent |
| T5b | WAITLIST pura (PROPOSING_WAITLIST→WAITLIST_SAVED) | ⚠️ Demo limitation: richiede calendario pieno |

---

## PROSSIMA SESSIONE S59

> **Skill**: `fluxion-tauri-architecture` (P1.0) | `fluxion-voice-agent` (F15/GAPs)
> **NOTA**: F03 Latency e F04 Schede già ✅ in ROADMAP_REMAINING.md

### Priorità S59 (in ordine):
1. **P1.0 Impostazioni Redesign** — sidebar verticale Linear-style, 8 rename plain language
   - `Impostazioni.tsx`: sidebar 240px + scroll-spy + badge stato sezioni
   - `useImpostazioniStatus` hook: query DB per ogni sezione
   - Quick setup banner in Dashboard.tsx
   - Research: già completa in ROADMAP_REMAINING.md (decisioni già prese)
2. **F15 VoIP** — era in pausa, riprende ora che F02 è done
   - Prerequisiti: F03 ✅ (latency < 800ms) + F02 ✅ (vertical guardrail)
   - Telnyx SIP trunk + EHIWEB numero italiano + bridge WebSocket
3. **Sara Enterprise Sprint 3** — GAP backlog da agente-b.md:
   - GAP-B2: "fra un mese" / "il mese prossimo" in entity_extractor
   - GAP-B6: "fine settimana" / "weekend" → sabato prossimo
   - GAP-A5: reset da WAITING_NAME → IDLE, non WAITING_SERVICE

---

## Riavvio pipeline iMac:
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
