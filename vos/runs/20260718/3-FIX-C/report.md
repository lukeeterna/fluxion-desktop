# STEP 3 — FIX-C NAME-GATE — Report

**Data:** 2026-07-18  
**Esecutore:** Claude Sonnet 4.6 (CC main context)

---

## Problema

In `_handle_idle` (S142 bare-name path), una parola come "Marco Rossi" pronunciata come
primo turno veniva immediatamente committa su `context.client_name` senza alcuna conferma
esplicita da parte del chiamante. Un saluto ambiguo ("ciao" → filtered dalla blacklist)
poteva passare se non fosse in `_not_name`, e qualsiasi nome unico non in blacklist veniva
registrato silenziosamente.

---

## Fix Applicati — `voice-agent/src/booking_state_machine.py`

### 1. Nuovo stato `CONFIRMING_NAME` (enum BookingState, riga ~116)
```python
CONFIRMING_NAME = "confirming_name"
```

### 2. Campi temporanei `_pending_name` / `_pending_surname` (BookingContext, riga ~195)
```python
_pending_name: Optional[str] = field(default=None, repr=False)
_pending_surname: Optional[str] = field(default=None, repr=False)
```

### 3. Template `confirm_name_gate` (TEMPLATES dict)
```python
"confirm_name_gate": "La registro come {name}, corretto?",
```

### 4. `_handle_idle` bare-name path — NON commette più `client_name`
Prima:
```python
self.context.client_name = parts[0]    # COMMIT immediato
self.context.client_surname = ...
```
Dopo:
```python
self.context._pending_name = parts[0]  # solo PENDING
self.context._pending_surname = ...
self.context.state = BookingState.CONFIRMING_NAME
return StateMachineResult(
    next_state=BookingState.CONFIRMING_NAME,
    response=TEMPLATES["confirm_name_gate"].format(name=display)
)
```

### 5. Dispatch table — nuovo branch `CONFIRMING_NAME`
```python
elif state == BookingState.CONFIRMING_NAME:
    result = self._handle_confirming_name(user_input, extracted)
```

### 6. Nuovo metodo `_handle_confirming_name`
- Affermazione (`sì`, `ok`, `certo`, `va bene`, `perfetto`, …) → commit `_pending_name`
  → `client_name` settato, pending azzerato, chain a `_handle_waiting_name`
- Negazione (`no`, `sbagliato`, `non sono`, …) → discard pending → `ask_name`

---

## Prove (log reali, rig FSM diretto — niente HTTP, niente :3002, niente SIP)

```
=== PROOF 1: greeting word → should NOT become client_name ===
  Input: 'Buonasera'
  state  = BookingState.WAITING_NAME
  client_name  = None
  _pending_name = None
  response = 'Come ti chiami?'
  PASS: 'Buonasera' → client_name=None, state=WAITING_NAME

=== PROOF 2: bare name → confirmation → registered ===
  Turn 1 Input: 'Marco Rossi'
  state         = BookingState.CONFIRMING_NAME
  client_name   = None  (must be None before confirm)
  _pending_name = 'Marco'
  response      = 'La registro come Marco Rossi, corretto?'
  PASS: bare name captured as pending, state=CONFIRMING_NAME, confirmation asked
  Turn 2 Input: 'Sì'
  client_name  = 'Marco'  (must be set after confirm)
  state        = BookingState.DISAMBIGUATING_NAME
  PASS: confirmed → client_name='Marco', pending cleared

=== PROOF 3: bare name → denial → ask_name ===
  Turn 2 Input: 'No'
  client_name  = None
  state        = BookingState.WAITING_NAME
  response     = 'Come ti chiami?'
  PASS: denied → client_name=None, state=WAITING_NAME, pending cleared

ALL NAME-GATE ASSERTS PASSED
```

---

## Criteri VERDE

| Criterio | Stato |
|----------|-------|
| "Buonasera" non diventa client_name | VERDE (PROOF 1 passato) |
| "Marco Rossi" → conferma richiesta → registrato | VERDE (PROOF 2 passato) |
| "Marco Rossi" → diniego → ask_name | VERDE (PROOF 3 passato) |
| Nessun deploy prod :3002 / niente SIP/trunk | RISPETTATO |
| tools/VectCutAPI non toccato | RISPETTATO |

VERDETTO: VERDE
