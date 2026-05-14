# PROMPT RIPARTENZA S231 — FLUXION

## Contesto
S230 chiusa pulito sotto context rot >50%. Commit `955e119` `fix(S230-P1)` applicato + pushed, **NON validato**. Pipeline iMac stopped + orchestrator.py reverted a clean state (no S230 marker locale iMac).

## Root cause S230 (verificata, NON race condition come ipotizzato S229)
Groq NLU HTTP 429 rate-limit durante stress burst → fallback regex `get_cached_intent` → `<modale> fare <X>` con X ∈ {revisione, epilazione, dichiarazione, barba} ritorna `category=UNKNOWN` → `_has_booking_words` regex backup (orchestrator.py:1685-1692) NON copre questi service tokens → tutte 6 condizioni `should_process_booking` False → routing L4_groq invece di booking flow → fsm=idle → `booking_keyword_miss` deterministico.

**Smoking gun**: `/tmp/voice-pipeline-s227b.log` linea 12:59:59 mostra esplicitamente HTTP 429 + confidence 0.00 + regex fallback. Direct intent_classifier test conferma "Devo fare la revisione" → unknown 0.000 mentre "Devo fare il tagliando" → prenotazione 0.451 (tagliando già in regex).

## Fix S230-P1 (committed `955e119`, deferred validation)
`voice-agent/src/orchestrator.py:1684-1694` — aggiunti 4 service token a `_has_booking_words` regex: `revisione|epilazione|dichiarazione|barba`.

## Step S231 (deterministico, ~15 min)

### a. Sync iMac + pipeline restart (~2 min)
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION" && git pull origin master && grep -c "S230-P1" voice-agent/src/orchestrator.py'
# Expected: count=1

ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline-s231.log 2>&1 &'
sleep 3
curl -s http://192.168.1.2:3002/health | python3 -m json.tool
```

### b. Double-run stress validation (lezione S228 mandatoria, ~10 min)
```bash
# Run 1
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && source venv/bin/activate && SARA_STRESS_GATE_REPORT=/tmp/sara-s231-run1.json python tests/e2e/test_sara_stress_per_verticale.py 2>&1 | tail -30'

# Run 2 (filtra flake L4 cold path)
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && source venv/bin/activate && SARA_STRESS_GATE_REPORT=/tmp/sara-s231-run2.json python tests/e2e/test_sara_stress_per_verticale.py 2>&1 | tail -30'
```

### c. Decision tree
- **Both runs ≥145 OK / 0 booking_keyword_miss / 0 FAIL** → S231 close green. Commit baseline `baselines/sara-gate-s231-full6vert.json` + update MEMORY/ROADMAP.
- **Regression (es. "dichiarazione" false positive cross-vert)** → `git revert 955e119`, Plan S231 alternativo: estendere `intent_classifier.py:387-410` PRENOTAZIONE patterns con `(devo|vorrei|voglio|dovrei|posso)\s+fare\s+\w+`. Più chirurgico di regex backup.
- **Flake L4 (1 green / 1 red WARN diversi)** → 3° run tiebreaker, se ancora flake → P2 streaming TTS chunking (MEMORY S228 tech debt).

### d. Edge case scan (parallel, ~3 min)
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && source venv/bin/activate && python3 -c "
from src.intent_classifier import IntentClassifier
ic = IntentClassifier()
for t in [
  \"La dichiarazione di guerra del 1940\",
  \"Sto facendo la barba al cane\",
  \"Non voglio fare la revisione\",
  \"Quanto costa la revisione?\",
]:
    r = ic.classify(t)
    print(f\"{t!r} → {r.category.name} {r.confidence:.3f}\")
"'
```

## File critici S231 (NON toccare sopra 50% context)
- `voice-agent/src/orchestrator.py` (5747 righe, già edited S230-P1)
- `voice-agent/src/intent_classifier.py` (ALTERNATIVA fix se regression)
- `voice-agent/src/booking_state_machine.py` (4459 righe)

## Stato repository
- **MacBook** `/Volumes/MontereyT7/FLUXION` master `955e119` (S230-P1 fix committed+pushed)
- **iMac** `/Volumes/MacSSD - Dati/FLUXION` master `2018f02` (PRE S230-P1, pull required)
- **Pipeline iMac**: STOPPED (clean state, restart on S231 step a)

## Tech debt S231+ deferred (da MEMORY S228+S229)
- **P2**: streaming L4_groq→TTS chunked per MEDICAL/BEAUTY P95 ~10s cold
- **P3**: per-tenant facility config Setup Wizard (sostituisce S227-P1b defaults)
- **P4**: auto-spawn sidecar Tauri su `.app` launch
- **P5**: `--port=N` argparse a `voice-agent/main.py` (15 min)
- **P6-9**: self-hosted runner, PSTN test, Win MSI, arm64 UB (founder/deferred)

## Vincoli S231 (CLAUDE.md + MEMORY)
- Double-run baseline OBBLIGATORIO (no single-run cherry-pick)
- Atomic commit con messaggio chiaro pre/post status
- NO Co-Authored-By Claude/anthropic trailer (MEMORY rule #6)
- File critici NO sopra 50% context (rule #5 CLAUDE.md)
- Honest CTO: se validation rossa, revert + bisect, no patch-on-patch
