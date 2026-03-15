# FLUXION — Handoff Sessione 74 → 75 (2026-03-15)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 02d90f6
docs(audioworklet-01): complete AudioWorklet migration plan
type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1488 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 74

### audioworklet-vad-fix — FASE COMPLETA ✅
- Phone button (open-mic) approvato fisicamente su iMac da Gianluca
- SUMMARY + VERIFICATION scritti, STATE.md aggiornato
- Fase completamente chiusa

### F-SARA-NLU-PATTERNS — PIANIFICATA ✅
- Research completo (audit diretto codebase — HIGH confidence)
- 4 PLAN.md scritti + verificati (2 iterazioni checker, 4 blocker risolti)
- Struttura: 4 wave sequenziali (no parallel per evitare write conflict su file condivisi)
- Plans in: `.planning/phases/f-sara-nlu-patterns/`

---

## PROSSIMA SESSIONE S75 — AZIONE IMMEDIATA

### P1 — ESEGUIRE F-SARA-NLU-PATTERNS (PRIORITÀ ASSOLUTA)

```
/gsd:execute-phase f-sara-nlu-patterns
```

**Struttura esecuzione:**
| Wave | Plan | Cosa fa |
|------|------|---------|
| 1 | 01 | hair + beauty — 20+ gruppi servizi, guardrails, entity extraction, ≥60 test |
| 2 | 02 | wellness + medico — 15+ gruppi, _MEDICAL_SPECIALTIES esteso, ≥50 test |
| 3 | 03 | auto extended + professionale, DURATION_MAP, OPERATOR_ROLES, ≥50 test |
| 4 | 04 | orchestrator wiring + fix prod bug lines 673+685 + iMac pytest ≥1488 PASS |

**Perché è critico:**
- Oggi 4 verticali legacy con copertura parziale → dopo: 6 macro × 30+ micro
- BUG PRODUZIONE: lines 673+685 orchestrator passano raw verticale_id invece del key normalizzato → tutti i nuovi verticali silenziosamente ignorati (fix obbligatorio in Wave 4)
- Claude come fonte enciclopedica per generare pattern enterprise-grade per ogni verticale

### P2 — F-SARA-VOICE (dopo NLU)
```
/gsd:plan-phase F-SARA-VOICE
```
- FluxionTTS Adaptive: Qwen3-TTS 0.6B + Piper fallback
- Research completo: `memory/project_qwen3tts_sara.md`
- Prerequisito: AudioWorklet ✅ (SODDISFATTO)

### P3 — F17 Windows (dopo F-SARA-VOICE)
- Prerequisito: VAD Open-Mic ✅ (SODDISFATTO)

### P4 — F15 VoIP (bloccante su EHIWEB credentials)
- Quando arrivano: `/gsd:plan-phase F15`

---

## ARCHITETTURA NLU — NOTE CRITICHE PER S75

### File da NON toccare senza leggere _INDEX.md prima
- `voice-agent/src/italian_regex.py` (921 righe, 12 gruppi)
- `voice-agent/src/entity_extractor.py` (2064+ righe)
- `voice-agent/src/orchestrator.py` (2800+ righe)

### Key mapping mismatch (BUG ATTIVO — fix in Wave 4)
```
setup.ts value  →  runtime key oggi   →  status
hair            →  salone             →  MISMATCH (silenzioso)
beauty          →  (nessuno)          →  MISSING
wellness        →  palestra           →  MISMATCH
medico          →  medical            →  MISMATCH
auto            →  auto               →  OK
professionale   →  (nessuno)          →  MISSING
```
Wave 4 Plan 04 Task 1: fix `_extract_vertical_key()` + lines 673+685

### Legacy aliases OBBLIGATORI (40+ test dipendono da questi)
```python
VERTICAL_GUARDRAILS["salone"] = VERTICAL_GUARDRAILS["hair"]
VERTICAL_GUARDRAILS["palestra"] = VERTICAL_GUARDRAILS["wellness"]
VERTICAL_GUARDRAILS["medical"] = VERTICAL_GUARDRAILS["medico"]
```

---

## PROMEMORIA TECNICI
- **Riavvio pipeline iMac**: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && [python] main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"`
- **pytest iMac**: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && [python] -m pytest tests/ -v --tb=short 2>&1 | tail -20"`
- **type-check MacBook**: `npm run type-check`
- **Test microfono**: sempre fisicamente su iMac (pipeline bound 127.0.0.1)
- **Fluxion.app**: `src-tauri/target/release/bundle/macos/Fluxion.app`
