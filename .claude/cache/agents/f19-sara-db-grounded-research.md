# F19 — Sara DB-Grounded: Research Analysis

> Date: 2026-03-19 | Session: S95
> Goal: Make Sara read services, operators, and waitlist from SQLite DB instead of hardcoded constants

---

## 1. Services Loading in booking_state_machine.py

### Current State
- **File**: `voice-agent/src/booking_state_machine.py` lines 293-309
- `DEFAULT_SERVICES` is a hardcoded dict with 5 salone-only services (taglio, piega, colore, barba, trattamento)
- `VERTICAL_SERVICES` in `italian_regex.py` lines 229-299 has hardcoded service synonyms for 4 verticals (salone, palestra, medical, auto) — much richer, ~70 services total
- `BookingStateMachine.__init__()` (line 600): `self.services_config = services_config or DEFAULT_SERVICES`
- `VoiceOrchestrator.__init__()` (line 427-430): loads from `VERTICAL_SERVICES.get(verticale_id, {})` and passes to BSM
- On vertical switch (line 2274): `self.booking_sm.services_config = VERTICAL_SERVICES.get(vertical, {})`

### Problem
Services are **always hardcoded** from `italian_regex.py`. If a salone owner adds custom services in the DB (e.g., "trattamento botox premium", "extension ciglia"), Sara will never recognize them. She only knows the synonyms compiled into the Python source.

### DB Schema (migration 001)
```sql
servizi (id, nome, descrizione, categoria, prezzo, durata_minuti, buffer_minuti, attivo, ...)
```

### Recommended Fix
1. At session start (or on `/api/voice/process` first call), query SQLite:
   ```sql
   SELECT id, nome, categoria FROM servizi WHERE attivo = 1
   ```
2. Build a dynamic `services_config` dict: key = service `id`, value = `[nome, ...synonyms from VERTICAL_SERVICES if matching]`
3. Merge DB services with hardcoded synonyms (DB is primary, hardcoded is synonym expansion)
4. Method: `_load_services_from_db()` in orchestrator.py, called once per session, result cached
5. Pass merged config to `self.booking_sm.services_config`

### Code Locations to Modify
- `orchestrator.py` line 427-430: add `_load_services_from_db()` call
- `orchestrator.py` line 2274: replace hardcoded with DB + merge
- New method `_load_services_from_db()` in orchestrator.py (pattern: like `_check_slot_availability_sqlite_fallback`)
- `booking_state_machine.py` line 600: no change needed (already accepts config param)

---

## 2. Entity Extractor — extract_operator() Validation

### Current State
- **File**: `voice-agent/src/entity_extractor.py` lines 1145-1222
- Pure regex extraction: matches patterns like "con l'operatore Marco", "vorrei Laura", "con Marco Rossi"
- Has a blacklist of common Italian words to filter false positives (lines 1164-1181)
- Returns `ExtractedOperator(name, original_text, confidence)` — **name is whatever regex matched**
- **No validation against actual operators in DB** — if user says "con Roberto" and there's no Roberto, Sara accepts it anyway

### Problem
Sara will accept ANY capitalized name as operator, even if that person doesn't work at the business. This leads to bookings with non-existent operators.

### DB Schema (migration 001)
```sql
operatori (id, nome, cognome, email, telefono, ruolo, attivo, ...)
```

### Recommended Fix
1. Load operator list from DB at session start:
   ```sql
   SELECT id, nome, cognome FROM operatori WHERE attivo = 1
   ```
2. After `extract_operator()` returns a name, validate against DB list using fuzzy matching (Levenshtein, already in codebase via `disambiguation_handler.py`)
3. If exact match: set `operator_id` in context
4. If fuzzy match (>70%): confirm with user ("Intende Marco Rossi?")
5. If no match: inform user ("Non ho trovato un operatore con quel nome. I nostri operatori sono: Marco, Laura, Giulia")
6. Add `operator_names` parameter to `extract_operator()` for optional validation

### Code Locations to Modify
- `orchestrator.py`: new `_load_operators_from_db()` method (SQLite direct, like `_find_db_path()` pattern)
- `orchestrator.py` line 2992-3004: `_search_operators()` — add SQLite fallback (see point 4 below)
- `entity_extractor.py` line 1145: add optional `known_operators: List[str] = None` param
- `booking_state_machine.py`: pass operator list to extraction calls

---

## 3. _handle_confirming() — Rejection Handling (PHASE 5)

### Current State
- **File**: `voice-agent/src/booking_state_machine.py` lines 2742-2764
- PHASE 5 (line 2748): calls `_detect_correction_or_rejection_signal(text_lower)` to detect "no"
- If `corrections_made == 0`: **cancels entire booking** (state -> CANCELLED, should_exit=True)
- If `corrections_made > 0`: asks "cosa desidera cambiare?" (stays in CONFIRMING)
- Hard limit at line 2627: after 3+ corrections -> resets to IDLE

### Problem
When user says "no" on first confirmation (corrections_made == 0), the booking is **cancelled and session exits**. This is too aggressive. User might just want to correct one slot, not cancel everything.

### Recommended Fix
Option A (conservative): Instead of CANCELLED + should_exit, transition to a "what do you want to change?" state:
```python
if has_rejection:
    if self.context.corrections_made == 0:
        # DON'T cancel — ask what to change
        return StateMachineResult(
            next_state=BookingState.CONFIRMING,
            response="Capisco. Cosa desidera cambiare? Il servizio, la data o l'orario?",
        )
```

Option B (with explicit cancel): Add a two-step cancellation:
```python
if has_rejection and self.context.corrections_made == 0:
    self.context.state = BookingState.ASKING_CANCEL_CONFIRMATION
    return StateMachineResult(
        next_state=BookingState.ASKING_CANCEL_CONFIRMATION,
        response="Vuole annullare la prenotazione o modificare qualcosa?",
    )
```

### Code Location
- `booking_state_machine.py` lines 2748-2764: modify PHASE 5 logic

---

## 4. _search_operators() — SQLite Fallback

### Current State
- **File**: `voice-agent/src/orchestrator.py` lines 2992-3004
- HTTP-only: calls `GET {bridge_url}/api/operatori/list`
- On any error (Bridge offline): returns `{"operatori": []}` — **empty list, no fallback**
- Pattern mismatch: `_check_slot_availability()` has SQLite fallback (line 2882), but `_search_operators()` does NOT

### Problem
Bridge (port 3001) is often offline (documented in system prompt). When offline, Sara cannot list operators and cannot validate operator names. This makes operator-based booking impossible.

### DB Schema
```sql
operatori (id, nome, cognome, attivo)
operatori_servizi (operatore_id, servizio_id)  -- which operator does which service
```

### Recommended Fix
Add `_search_operators_sqlite_fallback()` following the exact pattern of `_check_slot_availability_sqlite_fallback()`:

```python
async def _search_operators_sqlite_fallback(self) -> Dict[str, Any]:
    import sqlite3
    db_path = self._find_db_path()
    if not db_path:
        return {"operatori": []}
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, nome, cognome FROM operatori WHERE attivo = 1"
        ).fetchall()
        conn.close()
        return {"operatori": [dict(r) for r in rows]}
    except sqlite3.Error:
        return {"operatori": []}
```

Then in `_search_operators()`:
```python
# After the except blocks:
return await self._search_operators_sqlite_fallback()
```

### Code Locations to Modify
- `orchestrator.py` line 3004: change `return {"operatori": []}` to `return await self._search_operators_sqlite_fallback()`
- Add new method `_search_operators_sqlite_fallback()` near line 3004

---

## 5. _add_to_waitlist() — SQLite Fallback + VIP Priority

### Current State
- **File**: `voice-agent/src/orchestrator.py` lines 3087-3111
- HTTP-only: `POST {bridge_url}/api/waitlist/add` with payload `{cliente_id, servizio, data_preferita, priorita: "normale"}`
- On error: returns `{"success": False, "error": "Bridge not available"}`
- **Priority is always hardcoded to "normale"** — never checks if client is VIP
- `booking_manager.py` lines 348-373 has VIP-aware logic (checks `customer.tier`) but it's unused by the voice pipeline
- `vertical_schemas.py` has full `WaitlistEntry` + `WaitlistManager` with priority scoring — also unused

### DB Schema (migration 013)
```sql
waitlist (id, cliente_id, servizio, data_preferita, ora_preferita,
          operatore_preferito, priorita, priorita_valore, note,
          stato, created_at, ...)
```
- `priorita`: 'normale', 'vip', 'urgente'
- `priorita_valore`: 10=normale, 50=vip, 100=urgente
- Client VIP flag: `clienti.is_vip` (migration 005)

### Recommended Fix

**A. SQLite fallback:**
```python
async def _add_to_waitlist_sqlite_fallback(
    self, client_id: str, service: str, preferred_date: str = None
) -> Dict[str, Any]:
    import sqlite3, uuid
    db_path = self._find_db_path()
    if not db_path:
        return {"success": False, "error": "DB not found"}
    try:
        conn = sqlite3.connect(db_path, timeout=5)

        # Check VIP status
        is_vip = conn.execute(
            "SELECT is_vip FROM clienti WHERE id = ?", (client_id,)
        ).fetchone()
        vip = is_vip and is_vip[0] == 1
        priorita = "vip" if vip else "normale"
        priorita_valore = 50 if vip else 10

        wl_id = str(uuid.uuid4())[:32]
        conn.execute(
            """INSERT INTO waitlist (id, cliente_id, servizio, data_preferita,
               priorita, priorita_valore, stato)
               VALUES (?, ?, ?, ?, ?, ?, 'attesa')""",
            (wl_id, client_id, service, preferred_date, priorita, priorita_valore)
        )
        conn.commit()
        conn.close()
        return {"success": True, "waitlist_id": wl_id, "priorita": priorita}
    except sqlite3.Error as e:
        return {"success": False, "error": str(e)}
```

**B. VIP priority in HTTP path too:**
Before the HTTP call, lookup `is_vip` from SQLite and set `priorita` accordingly instead of hardcoding `"normale"`.

### Code Locations to Modify
- `orchestrator.py` line 3096: change `"priorita": "normale"` to dynamic VIP lookup
- `orchestrator.py` line 3111: change `return {"success": False, ...}` to `return await self._add_to_waitlist_sqlite_fallback(...)`
- Add new method `_add_to_waitlist_sqlite_fallback()` near line 3111

---

## Summary: Implementation Priority

| # | Area | Effort | Impact | Priority |
|---|------|--------|--------|----------|
| 4 | _search_operators SQLite fallback | S | HIGH | P0 — without this, operator booking fails when Bridge offline |
| 1 | Services from DB | M | HIGH | P0 — custom services invisible to Sara |
| 2 | Operator name validation | M | HIGH | P1 — prevents phantom operator bookings |
| 5 | Waitlist SQLite + VIP | S | MED | P1 — waitlist broken when Bridge offline |
| 3 | Confirming rejection logic | S | MED | P2 — UX improvement, not data integrity |

### Shared Pattern
All SQLite fallbacks follow the same pattern already established by `_check_slot_availability_sqlite_fallback()`:
1. Call `self._find_db_path()` (already exists, line 2521)
2. `sqlite3.connect(db_path, timeout=5)`
3. Execute query
4. Return structured dict
5. Catch `sqlite3.Error`

### Key Principle
**DB is source of truth. Hardcoded lists are synonym expansion only.**
- `VERTICAL_SERVICES` stays as synonym/alias dictionary for NLU fuzzy matching
- DB `servizi` table provides the actual service catalog (names, IDs, durations, prices)
- Merge strategy: DB services + hardcoded synonyms for each matching service
