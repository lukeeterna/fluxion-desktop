# S232 — Prompt ripartenza (handoff S231 → S232)

**Generato**: 2026-05-14 (chiusura S231)
**Branch**: master @ `1e09412f` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED (clean state, PID 86858 terminato)
**Target S232**: 147/0/0 ideale, 145+/0/0 acceptable, 2 run consecutivi

## TL;DR S231 outcome
- ✅ S230-P1 fix VALIDATO net-positive (PROFESSIONALE Dichiarazione 3 miss → 0)
- ✅ Double-run deterministic 141/6/0 + 141/6/0 (strict improvement vs S228 140/7-9/0)
- ❌ Target 145+/0 NON raggiunto: 6 booking_keyword_miss residui AUTO Revisione + BEAUTY Epilazione, Turn 4-6 'Sabato'/'Alle X'/'Confermo' su fsm=waiting_date stuck
- 🎯 Root cause LINE-LEVEL identificato: `orchestrator.py:1653` S220-P2 guard troppo stretto

## Smoking gun (verificato in codice)
File `voice-agent/src/orchestrator.py:1635-1657`:

```python
_is_info = intent_result.category == IntentCategory.INFO
# S220-P2: gate this override by FSM state — when mid-booking
# (state != IDLE) AND LLM gave high-confidence PRENOTAZIONE,
# do NOT let the semantic TF-IDF override the LLM.
# Reason: bare day-of-week tokens like "Sabato" get classified as
# info_orari by TF-IDF (conf ~0.48), spuriously blocking L2 slot filling.
_state_in_booking_flow = self.booking_sm.context.state not in [
    BookingState.IDLE, BookingState.COMPLETED, BookingState.CANCELLED
]
_llm_high_conf_book = bool(
    _llm_nlu_result
    and _llm_nlu_result.confidence >= 0.9
    and intent_result.category == IntentCategory.PRENOTAZIONE
)
if not _is_info and not (_state_in_booking_flow and _llm_high_conf_book):  # <-- LINE 1653
    _regex_check = get_cached_intent(user_input)
    if _regex_check.category == IntentCategory.INFO:
        _is_info = True
        intent_result = _regex_check
```

**Bug**: condizione `not (_state_in_booking_flow and _llm_high_conf_book)` — quando Groq NLU rate-limited (429 cascade documentato S230 `/tmp/voice-pipeline-s227b.log`) → `_llm_high_conf_book=False` → guard non protegge → 'Sabato' viene classificato `info_orari` da TF-IDF semantic_classifier → `_is_info=True` → `should_process_booking=False` (line 1757-1767) → routing L3_faq → FSM bypass → fsm stuck `waiting_date`.

**Docstring S220-P2 ammette esplicitamente**: *"bare day-of-week tokens like 'Sabato' get classified as info_orari by TF-IDF (conf ~0.48), spuriously blocking L2 slot filling"*. Il fix S220 originale era partial — copre solo path `_llm_high_conf_book=True`, lasciando scoperto il path `_llm_high_conf_book=False` (Groq down/rate-limited).

## Fix S232-P1 (1 riga, surgical)

`voice-agent/src/orchestrator.py:1653`:
```diff
-            if not _is_info and not (_state_in_booking_flow and _llm_high_conf_book):
+            if not _is_info and not _state_in_booking_flow:
```

**Razionale**: quando FSM è mid-booking (state != IDLE/COMPLETED/CANCELLED), la FSM è source of truth per i token che riceve. Bare date tokens ('Sabato'), time tokens ('Alle dieci'), confirm tokens ('Confermo') devono SEMPRE andare a FSM continue, indipendentemente da LLM conf. Legitimate INFO mid-booking (utente chiede "Quanto costa?" durante prenotazione) è già protetto da S127 explicit keyword guard (line 1664, regex `\b(orari[o]?|prezz[oi]|cost[oai]|...)\b`) che fires regardless of state.

**Critica strutturale (CLAUDE.md rule #4)**:
1. Assumption nascosta: utente mai legitimately INFO mid-booking. → S127 explicit regex catch genuine queries (orari/prezzi/costo).
2. Cosa rompe a 30/60/90gg: scenari TF-IDF override durante booking. → Solo path narrow rimosso, S127 + line 1635 (LLM INFO classification) intatti.
3. Pattern errore noti: identico a S220-P2 partial-fix. → Estensione completa il fix.
4. Sovradimensiono: no, 1 riga deletion in condizione esistente.

## Step S232 deterministici

### a. Restart pipeline iMac (~2 min, no pull, repo già sync 1e09412f)
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && lsof -ti:3002 | xargs kill 2>/dev/null; rm -f /tmp/voice-pipeline-s232.log && nohup venv/bin/python main.py > /tmp/voice-pipeline-s232.log 2>&1 & echo "PID: $!"'
sleep 6
ssh imac 'curl -s --max-time 5 http://127.0.0.1:3002/health'
```

### b. Apply fix + commit + push + sync iMac (~3 min)
Edit `voice-agent/src/orchestrator.py:1653` su MacBook (vedi fix S232-P1 sopra).

```bash
cd /Volumes/MontereyT7/FLUXION
git diff voice-agent/src/orchestrator.py  # verify single-line
git add voice-agent/src/orchestrator.py
git commit -m "fix(S232-P1): extend S220-P2 guard to all mid-booking states

Bare date tokens ('Sabato') and time tokens ('Alle X') were routed to
L3_faq via TF-IDF info_orari classification when Groq NLU rate-limited
(429 cascade). FSM was bypassed → fsm stuck waiting_date.

S220-P2 guard original: protected only _llm_high_conf_book=True path.
Fix: remove _llm_high_conf_book conjunct — when FSM mid-booking, FSM is
source of truth regardless of LLM conf. S127 explicit keyword guard
(orari|prezzi|costo) remains active for legitimate INFO mid-booking.

Validated S231 double-run baselines:
- voice-agent/tests/e2e/baselines/sara-gate-s231-run1-141-6-0.json
- voice-agent/tests/e2e/baselines/sara-gate-s231-run2-141-6-0.json"
git push origin master
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION" && git pull origin master && cd voice-agent && lsof -ti:3002 | xargs kill 2>/dev/null; sleep 2 && nohup venv/bin/python main.py > /tmp/voice-pipeline-s232.log 2>&1 & echo "PID: $!"'
sleep 6
ssh imac 'curl -s --max-time 5 http://127.0.0.1:3002/health'
```

### c. Double-run stress validation (~12 min, mandatoria lezione S228)
```bash
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && SARA_STRESS_GATE_REPORT=/tmp/sara-s232-run1.json venv/bin/python tests/e2e/test_sara_stress_per_verticale.py 2>&1 | tail -25'
ssh imac 'cd "/Volumes/MacSSD - Dati/FLUXION/voice-agent" && SARA_STRESS_GATE_REPORT=/tmp/sara-s232-run2.json venv/bin/python tests/e2e/test_sara_stress_per_verticale.py 2>&1 | tail -25'
```

Aspettativa: 147 OK / 0 WARN / 0 FAIL su entrambi run. Accettabile: 145+/0/0.

### d. Decision tree
- **Both green ≥145/0/0**: close S232 verde, commit baselines `sara-gate-s232-run{1,2}-147-0-0.json`, aggiorna MEMORY + HANDOFF.
- **Regression (booking_keyword_miss > 0 stesso pattern)**: falsificate ipotesi root cause — investigate `intent_classifier.py` TF-IDF `info_orari` patterns OR `nlu/semantic_classifier.py` weekday tokens classification.
- **Flake (differente tra run1 e run2)**: 3° run + analizza pattern Groq rate limit timing. Considera P2 streaming tech debt.

### e. Edge case scan post-fix (smoke test ~5 min)
```bash
# Legitimate FAQ during idle (deve essere INFO routed)
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/reset'
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d "{\"text\":\"Sabato siete aperti?\"}"'
# Expected: layer=L3_faq o L4_groq, response about Saturday hours

# Mid-booking date answer (deve essere FSM continue)
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/reset'
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d "{\"text\":\"Vorrei prenotare un taglio\"}"'
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d "{\"text\":\"Marco Rossi\"}"'
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d "{\"text\":\"Sabato\"}"'
# Expected: fsm=waiting_time, response asks for time

# S127 explicit keyword catch mid-booking (legitimate INFO)
ssh imac 'curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d "{\"text\":\"Quanto costa?\"}"'
# Expected: _is_info=True via S127, response about pricing
```

## Vincoli S232 (CLAUDE.md)
- NO `Co-Authored-By: Claude*/anthropic*` trailer in commit (MEMORY rule #6)
- Atomic commits (1 fix = 1 commit)
- File critici (orchestrator.py routing) NO edit sopra 50% context (rule #7)
- Double-run mandatoria (lezione S228)
- Honest CTO assessment: closing green o handoff strutturato S233 (no PARTIAL)

## Tech debt residuo (deferred S233+)
- **P2 streaming L4_groq→TTS chunked** per MEDICAL/BEAUTY P95 ~10s cold L4 (S231 P95 5265-5383ms)
- **P3 per-tenant facility config Setup Wizard** (sostituisce hardcoded S227-P1b defaults piscina/parcheggio)
- **P4 auto-spawn sidecar Tauri** (voice pipeline launch from app)
- **P5 `--port=N` argparse main.py** (multi-instance support)
- **P6-9 founder-deferred**: self-hosted runner, PSTN test, Win MSI, arm64 UB

## File rilevanti S232
- `voice-agent/src/orchestrator.py:1635-1700` (routing precedence L1/L2/L3 gate)
- `voice-agent/src/intent_classifier.py:387-410` (PRENOTAZIONE regex patterns)
- `voice-agent/src/nlu/semantic_classifier.py` (TF-IDF `info_orari` classification)
- `voice-agent/tests/e2e/test_sara_stress_per_verticale.py` (stress test entry)
- `voice-agent/tests/e2e/baselines/sara-gate-s231-run{1,2}-141-6-0.json` (S231 baseline)
