# Prompt ripartenza — S230

**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Pipeline iMac**: venv 127.0.0.1:3002 PID 67425 ATTIVA — project DB.
**Stato S229**: ✅ CHIUSA investigation-only, NO product code touched.

## Contesto S229 (handoff sintetico)

Bug RIPRODOTTO deterministicamente in full 6-vert stress (137/13/0 vs S228 baseline dual-run 140/9 e 140/7). Pattern univoco: input T2 con `<modale> + "fare" + service` → fsm=idle, layer=L4_groq, cascade T3-T6 stuck waiting_service.

**Verticali falliti**:
- AUTO: "Devo fare la revisione" (NEW regression vs S228)
- BEAUTY: "Vorrei fare epilazione laser"
- PROFESSIONALE: "Devo fare la dichiarazione dei redditi"

**MEMORY S229 hypothesis SCARTATA** (S226-P1 verb blacklist): blacklist attiva solo 1-3 parole, frasi failing hanno 4+ → bypass completo. NON è la root cause.

**Bug STATE-DEPENDENT** confermato:
- BEAUTY isolato (`--vertical beauty`): 22/0/0 ✅
- Full 6-vert: BEAUTY 19/5/0 ❌
- SALONE-singola-conv → AUTO immediato: ✅ funziona

→ Serve accumulo SALONE FULL (3 booking + 3 FAQ L4_groq + 2 guardrail + 1 disambig + 1 cancel + 1 latency) prima che AUTO esponga regression.

**Root cause hypothesis attiva (S230)**: race condition `orchestrator.py:3382-3396` set_vertical() — `asyncio.ensure_future(self._load_business_context())` fire-and-forget. Comment "block until done" è errato (`ensure_future` ritorna immediato). Handler returns prima che DB load completi → next process() arriva con state intermedio.

## Plan S230 (deterministic)

### Step a: conferma race (NON invasivo, ~3 min)
```bash
ssh imac 'bash /tmp/race_test.sh'
```
Script già scritto su iMac: 3 scenari (SALONE-singola → AUTO immediate, AUTO immediate post-reset, AUTO con sleep 2s post set-vertical). Se sleep risolve → race confermata.

Test alternativo (più rappresentativo): script che simula stress completo SALONE (multiple conv + faq + guardrail) poi AUTO immediate con/senza sleep.

### Step b1: se race CONFERMATA
Fix in `voice-agent/src/orchestrator.py:3382-3396` set_vertical(): convertire metodo a `async def set_vertical` + `await self._load_business_context()` esplicito. Aggiornare callers:
- `voice-agent/main.py:625` set_vertical_handler — già async → aggiungere await
- `voice-agent/main.py:606` reset_handler vertical branch — già async → aggiungere await
- Verificare `voice-agent/src/vertical_integration.py:111` e altri callers sync (line 3349 chiamato da reset_handler async ✓, ma anche da contesti sync?)

### Step b2: se race FALSIFIED
Investigare alternative:
1. Cache state in `intent_classifier` / `entity_extractor` cross-vertical
2. `extract_all` state in italian_regex.py cross-vertical
3. `faq_manager.faqs` NON wiped on set_vertical (orchestrator.py:3406-3409 wipe condizionato HAS_VERTICAL_LOADER)
4. State accumulation in disambiguation_handler (reset chiamato ma verificare attributi residui)

### Step c: safety net intent classifier (indipendente da race)
Estendere `voice-agent/src/intent_classifier.py:387-410` PRENOTAZIONE patterns per matchare `<modale> fare <service>` indipendentemente dalla lista chiusa di service tokens. Esempio:
```python
r"(voglio|vorrei|posso|devo|dovrei)\s+fare\s+(?:un[oa]?\s+|l[ao'\u2019]?\s+)?(?:la\s+)?\w+",
```
Trade-off: troppo permissivo? Verificare con guardrail scenarios.

### Step d: extension `_has_booking_words` (orchestrator.py:1685-1692)
Aggiungere token chiave NON in regex: `revisione`, `epilazione`, `dichiarazione redditi`, `dichiarazione`, `redditi`. Oppure migrare a regex generato da `VERTICAL_SERVICES` keys (DRY).

### Step e: validation (lezione S228)
Min 2 run full 6-vert consecutivi per filtrare flake L4_groq cold path. Target: 145+ OK / 0 booking_keyword_miss / 0 FAIL su entrambi.

## File reference S229

- `voice-agent/src/orchestrator.py`:
  - 1670-1763 (should_process_booking logic)
  - 1685-1692 (`_has_booking_words` regex — incompleto)
  - 3015-3163 (`_load_business_context` async — DB services load)
  - 3349-3412 (`set_vertical` — RACE candidate line 3391)
  - 3857-3882 (`_find_vertical_db_path`)
- `voice-agent/src/booking_state_machine.py:1395-1430` (`_handle_idle` blacklist)
- `voice-agent/src/intent_classifier.py:387-410` (PRENOTAZIONE patterns — GAP "fare X")
- `voice-agent/src/italian_regex.py:281-382` (VERTICAL_SERVICES — service synonyms OK)
- `voice-agent/main.py:587-650` (reset_handler + set_vertical_handler)
- `voice-agent/tests/e2e/test_sara_stress_per_verticale.py` (test scenarios)
- `voice-agent/tests/e2e/baselines/sara-gate-s228-full6vert.json` (baseline S228)
- `/tmp/sara-stress-gate-report-1778755109.json` su iMac (gate report S229 full run)
- `/tmp/race_test.sh` su iMac (race confirmation script)
- `/tmp/repro_beauty.sh` su iMac (BEAUTY isolated repro — passa, conferma state-dependent)

## Pre-flight S230
1. Verifica pipeline iMac ancora UP: `ssh imac 'curl -s http://127.0.0.1:3002/health'`
2. Verifica git status pulito: `git status`
3. Verifica branch master + commit head = S229 closing commit

## Vincoli S230
- NO modifiche a file critici sopra 50% context (regola context-budget-gate.md)
- Double-run baseline OBBLIGATORIO (regola S228)
- Atomic commits per ogni patch chirurgico (regola CoVe 2026)
- Commit message senza `Co-Authored-By: Claude*/anthropic*` (regola #6 MEMORY)

## Tech debt deferred S230+
- PRIORITY 2: Streaming L4_groq→TTS chunked (P95 ~10s cold)
- PRIORITY 3: per-tenant facility config Setup Wizard
- PRIORITY 4-7 founder: auto-spawn Tauri sidecar, --port argparse, self-hosted runner, PSTN test, Win MSI, arm64 UB
