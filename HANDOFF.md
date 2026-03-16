# FLUXION — Handoff Sessione 79 → 80 (2026-03-16)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> **SUPPORTO POST-VENDITA = ZERO MANUALE. Sara fa tutto.**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: c5851e8
fix(nlu): add all 6 verticals to NAME_BLACKLIST + more FSM re-prompts
type-check: 0 errori ✅
Tutti i file committati e pushati ✅
```

---

## COMPLETATO SESSIONE 79 (6 commit)

### 1. `95cb50a` — S78 fix batch ✅
- VAD: prefer webrtcvad over Silero ONNX (broken on iMac Intel)
- VAD: reduce sticky speaking (probs maxlen 30→8, silence 500→350ms)
- VAD HTTP: add resampling + debug logging
- FSM BUG-1: multi-service merge ("barba e capelli" = 2 services)
- FSM BUG-2: "quando è possibile" → flexible scheduling
- FSM BUG-3: referential context skip ("trattamenti che ti ho chiesto")
- FSM BUG-4: cortesia during booking → re-prompt after "Prego!"
- UI: greetingFiredRef prevents double greeting
- Logging: structured conversation logging in main.py

### 2. `a81c30c` — Code review findings + enterprise skill ✅
- HIGH FIX: logging crash risk (AttributeError on FSM state)
- Resampling: `audioop.ratecv()` anti-alias filter (was nearest-neighbor)
- Hex validation with HTTP 400
- `get_current_prompt()` in FSM (remove orchestrator duplication)
- Pre-compiled `_REFERENTIAL_PATTERNS` at module level
- `audioop.rms/max` for C-speed debug logging
- **NEW SKILL**: `fluxion-code-review` — 12 dimensions, A-F scoring, enterprise-grade
- **UPDATED AGENT**: `code-reviewer.md` — Uber uReview + DeepSource + Google Critique

### 3. `fc368ce` — Intent negazione fix ✅
- "non voglio cancellare" no longer triggers CANCELLAZIONE
- Negation guard in intent_classifier.py skips CANCELLAZIONE patterns
- Expanded `_NEGATED_CANCEL` regex in orchestrator

### 4. `1a861b8` — VAD sticky SPEAKING root cause fix ✅
- **Root cause**: silence_window_size calculated with Silero 32ms chunks, but webrtcvad probes are ~256ms
- 10 probes * 256ms = 2.5 SECONDS to detect silence (was masked as "sticky")
- Fix: recalculate windows in `_start_webrtc()` → silence_window=2 (~512ms)

### 5. `0ded136` — "tagliare" extracted as name fix ✅
- "tagliare" was missing from NAME_BLACKLIST (only "taglio" was listed)
- Added service verbs (tagliare, colorare, etc.) and body parts (capelli, unghie)

### 6. `c5851e8` — All 6 verticals in NAME_BLACKLIST ✅
- Systematic fix: hair, beauty, wellness, medical, auto, professional
- 70+ service words added to prevent STT capitalization → false name extraction
- Added REGISTERING_PHONE, DISAMBIGUATING_NAME, DISAMBIGUATING_BIRTH_DATE to get_current_prompt()

---

## ⚠️ PROBLEMI APERTI

### P1: TTS voce "Legacy System"
- La pipeline usa SystemTTS macOS (voce robotica, legge numeri male: "3.000.575")
- Serena/Qwen3-TTS non attiva (richiede Python 3.11 venv)
- **TODO**: Attivare Serena o piper-tts come fallback

### P2: VAD — da testare live con microfono
- Fix silence_window deployato (2.5s→512ms) ma NON ancora testato con microfono reale
- Serve test E2E audio su iMac

### P3: Sara Sales FSM — non ancora wired
- Research completa in `.claude/cache/agents/`
- Dataset pronto: sales_knowledge_base.json, support_knowledge_base.json
- TODO: creare sales_state_machine.py + wire in orchestrator

### P4: F15 VoIP EHIWEB — non ancora wired
- Credenziali pronte in `memory/reference_ehiweb_voip.md`
- voip.py esiste (1227 righe) — serve integrazione + port forward router

---

## AZIONE IMMEDIATA S80

### Priorità 1: Test VAD E2E su iMac
```
# Testare con microfono reale:
# - Turn gap < 1 secondo
# - No "sticky SPEAKING"
# - Conversazione fluida booking completo
```

### Priorità 2: Wire Sara Sales FSM
```
# Research completa in .claude/cache/agents/
# Creare: sales_state_machine.py + sales_kb_loader.py
# Nuovi endpoint: /api/sales/process
# Stati: SALES_QUALIFYING → PITCHING → OBJECTION → CLOSING
```

### Priorità 3: TTS fix numeri
```
# "3.000.575" letto cifra per cifra → correggere
# Attivare piper-tts o text preprocessing per numeri italiani
```

### Priorità 4: F15 VoIP EHIWEB
```
/gsd:plan-phase F15
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 80:
1. Testa VAD E2E su iMac con microfono — verifica turn gap < 1s
2. Wire Sara Sales FSM (research completa, dataset pronto)
3. Fix TTS numeri italiani ("3.000.575" letto correttamente)
4. F15 VoIP EHIWEB se tempo
```
