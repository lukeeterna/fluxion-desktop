# Sara Sprint 3 — Agente B: Gap Analysis GAP-A5 (FSM Cancel Mid-Flow)

> Generato: 2026-03-12 | Agente B: codebase analysis + fix proposto

---

## 1. Localizzazione precisa del bug

### Bug primario: `_check_interruption()` → riga 870

**File**: `voice-agent/src/booking_state_machine.py`

```
Righe 864-874:
    # Reset/cancel interruption
    for pattern in INTERRUPTION_PATTERNS["reset"]:
        if re.search(pattern, text_lower):
            self.context.previous_state = self.context.state.value
            self.context.was_interrupted = True
            self.reset()
            self.context.state = BookingState.WAITING_SERVICE   # ← BUG
            return StateMachineResult(
                next_state=BookingState.WAITING_SERVICE,         # ← BUG
                response=TEMPLATES["reset_ack"]
            )
```

**Pattern che scattano** (riga 314-317):
```python
INTERRUPTION_PATTERNS = {
    "reset": [
        r"\b(ricominciamo|ricomincia|da\s+capo|annulla\s+tutto)\b",
        r"\b(cancella|voglio\s+annullare)\b",
    ],
    ...
}
```

### Comportamento attuale (sbagliato)
Quando lo stato è `WAITING_NAME` e l'utente dice "no grazie" / "lascia perdere" / "annulla" / "annulla tutto":

1. `_check_interruption()` scatta (riga 865-874)
2. `self.reset()` viene chiamato — porta a `IDLE` internamente (riga 628)
3. Ma poi **immediatamente** si forza `self.context.state = BookingState.WAITING_SERVICE` (riga 870)
4. Sara risponde "D'accordo, ricominciamo. Come posso aiutarla?" e aspetta un servizio

Risultato: l'utente che vuole uscire dal flusso viene intrappolato nel flusso di booking.

### Comportamento corretto (atteso)
Se lo stato è `WAITING_NAME` (utente non ha ancora dato il nome), cancellare = voler uscire completamente. Sara deve tornare a `IDLE` e rispondere con qualcosa come "Certo, nessun problema. La chiamo se ha bisogno."

---

## 2. Analisi INTERRUPTION_PATTERNS["reset"] — frasi triggering

Le frasi che triggherano il reset "sbagliato" in WAITING_NAME sono:

| Frase utente | Pattern match | Comportamento attuale |
|---|---|---|
| "ricominciamo" | `ricominciamo` | → WAITING_SERVICE (sbagliato se in WAITING_NAME) |
| "annulla tutto" | `annulla\s+tutto` | → WAITING_SERVICE (sbagliato se in WAITING_NAME) |
| "cancella" | `cancella` | → WAITING_SERVICE (sbagliato se in WAITING_NAME) |
| "voglio annullare" | `voglio\s+annullare` | → WAITING_SERVICE (sbagliato se in WAITING_NAME) |
| "da capo" | `da\s+capo` | → WAITING_SERVICE (OK — l'utente vuole ricominciare) |

**Nota critica**: "da capo" / "ricominciamo" in WAITING_NAME sono ambigui — l'utente potrebbe voler ricominciare il booking (→ WAITING_SERVICE). Per "cancella" / "annulla" / "no grazie" il significato è univoco: vuole uscire.

Ma il GAP-A5 nella task description parla specificamente di:
- "no grazie"
- "lascia perdere"
- "annulla"

"no grazie" e "lascia perdere" NON sono in `INTERRUPTION_PATTERNS["reset"]`. Questi arrivano al fallback di `_handle_waiting_name()` (riga 1438-1442) che non ha nessun handling esplicito → restano in `WAITING_NAME`. Questo è il **secondo bug**.

---

## 3. Due bug distinti in GAP-A5

### Bug A: `_check_interruption` forza WAITING_SERVICE invece di IDLE (riga 870)

Affetta tutti gli stati **iniziali** dove non c'è ancora nulla di significativo raccolto:
- `WAITING_NAME` ← principale
- Potenzialmente `WAITING_SURNAME` se l'utente dice "annulla tutto" prima di dare il cognome

In stati avanzati (`WAITING_DATE`, `WAITING_TIME`, `CONFIRMING`) WAITING_SERVICE è il comportamento corretto: l'utente vuole ricominciare il booking, non uscire.

### Bug B: "no grazie" / "lascia perdere" in WAITING_NAME non gestiti

`_handle_waiting_name()` riga 1438-1442 (fallback finale):
```python
# Couldn't extract name
return StateMachineResult(
    next_state=BookingState.WAITING_NAME,
    response="Mi dice il nome, per cortesia?"
)
```

Quando l'utente dice "no grazie" o "lascia perdere":
- `_check_interruption()` non scatta (non sono in nessun pattern)
- Il fallback di `_handle_waiting_name()` tratta queste frasi come nome non riconosciuto
- Sara risponde "Mi dice il nome, per cortesia?" — ignorando il rifiuto esplicito

---

## 4. Analisi stati affetti

| Stato | Bug A (reset→WAITING_SERVICE) | Bug B (rifiuto non gestito) |
|-------|------|------|
| `WAITING_NAME` | Si — "annulla tutto" porta a WAITING_SERVICE | Si — "no grazie" ignorato |
| `WAITING_SURNAME` | Si — "annulla tutto" porta a WAITING_SERVICE | Si — "no grazie" trattato come cognome |
| `WAITING_SERVICE` | N/A (è già WAITING_SERVICE) | No |
| `WAITING_DATE` | No — reset a WAITING_SERVICE è corretto qui | No |
| `WAITING_TIME` | No — reset a WAITING_SERVICE è corretto qui | No |
| `CONFIRMING` | No — già gestito da handler dedicato | No — ha reject handling |
| `REGISTERING_SURNAME` | Si — "annulla tutto" durante registrazione nuovo cliente | Si |
| `REGISTERING_PHONE` | Borderline | Borderline |

**Riassunto**: stati "pre-identificazione" (WAITING_NAME, WAITING_SURNAME) hanno entrambi i bug. Stati "post-identificazione" hanno solo Bug A ma con comportamento meno grave (l'utente vuole ricominciare il booking, non uscire).

---

## 5. Benchmark — Best Practice FSM per voice booking

### Google Dialogflow CX
- Ogni intent "cancel" ha un handler esplicito per ogni stato della conversazione
- Comportamento: se l'utente cancella prima di completare l'identificazione → END_SESSION
- Se cancella durante il booking (post-identificazione) → confirma cancellazione → IDLE o END_SESSION
- Pattern: **"intent context-sensitivity"** — stesso intent, comportamento diverso per stato

### Retell AI / Vapi
- Approccio: "exit intents" definiti per l'intera conversazione, con override per stato
- Frasi come "no grazie", "basta", "lascia perdere" → sempre EXIT se prima dell'identificazione
- "Annulla tutto" dopo aver dato nome → chiede conferma prima di uscire

### Best practice FSM 2026
```
Pre-identification states (IDLE, WAITING_NAME, WAITING_SURNAME):
  cancel/no-thanks → IDLE (exit gracefully, no confirmation needed)

Mid-booking states (WAITING_SERVICE ... WAITING_TIME):
  cancel/annulla-tutto → WAITING_SERVICE (restart booking, don't exit)

Post-booking states (CONFIRMING):
  cancel/no → CANCELLED (with explicit confirmation)
```

La distinzione fondamentale è: **prima dell'identificazione = cancel = EXIT**, dopo l'identificazione = restart del booking.

---

## 6. Fix proposto — diff minimale

### Fix A: `_check_interruption()` — context-aware reset destination

**File**: `booking_state_machine.py`, righe 864-874

```python
# PRIMA (riga 864-874):
        # Reset/cancel interruption
        for pattern in INTERRUPTION_PATTERNS["reset"]:
            if re.search(pattern, text_lower):
                self.context.previous_state = self.context.state.value
                self.context.was_interrupted = True
                self.reset()
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=TEMPLATES["reset_ack"]
                )

# DOPO:
        # Reset/cancel interruption
        PRE_IDENTIFICATION_STATES = {
            BookingState.WAITING_NAME,
            BookingState.WAITING_SURNAME,
        }
        for pattern in INTERRUPTION_PATTERNS["reset"]:
            if re.search(pattern, text_lower):
                current_state = self.context.state
                self.context.previous_state = current_state.value
                self.context.was_interrupted = True
                self.reset()
                if current_state in PRE_IDENTIFICATION_STATES:
                    # User cancelled before identifying themselves — exit completely
                    self.context.state = BookingState.IDLE
                    return StateMachineResult(
                        next_state=BookingState.IDLE,
                        response="Certo, nessun problema. La aspettiamo quando vuole!"
                    )
                self.context.state = BookingState.WAITING_SERVICE
                return StateMachineResult(
                    next_state=BookingState.WAITING_SERVICE,
                    response=TEMPLATES["reset_ack"]
                )
```

### Fix B: `_handle_waiting_name()` — reject detection prima del fallback

**File**: `booking_state_machine.py`, righe 1438-1442 (fallback finale di `_handle_waiting_name`)

```python
# PRIMA (riga 1438-1442):
        # Couldn't extract name
        return StateMachineResult(
            next_state=BookingState.WAITING_NAME,
            response="Mi dice il nome, per cortesia?"
        )

# DOPO:
        # Check for explicit rejection before asking again
        REJECTION_PATTERNS = [
            r"\b(no\s+graz|lascia\s+perd|non\s+voglio|basta\s+così|ho\s+cambiato\s+idea)\b",
            r"^\s*(no|nope|nah|nein)\s*$",
        ]
        for pattern in REJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                self.context.state = BookingState.IDLE
                return StateMachineResult(
                    next_state=BookingState.IDLE,
                    response="Certo, nessun problema. La aspettiamo quando vuole!"
                )

        # Couldn't extract name
        return StateMachineResult(
            next_state=BookingState.WAITING_NAME,
            response="Mi dice il nome, per cortesia?"
        )
```

**Nota**: `is_rifiuto()` da `italian_regex.py` (riga 149) sarebbe il modulo corretto da usare invece dei pattern inline. Tuttavia, in `booking_state_machine.py` non è già importato — `is_flexible_scheduling` e `is_ambiguous_date` sono importati (riga 67-69), ma non `is_rifiuto`. Il fix minimale usa regex inline per non alterare gli import.

**Alternativa con `is_rifiuto`** (più robusto, richiede import):
```python
# In import block (riga 67-69), aggiungere is_rifiuto:
from .italian_regex import is_ambiguous_date, strip_fillers, extract_multi_services, is_flexible_scheduling, is_rifiuto

# In _handle_waiting_name() fallback:
        if HAS_ITALIAN_REGEX:
            is_reject, _ = is_rifiuto(text)
            if is_reject:
                self.context.state = BookingState.IDLE
                return StateMachineResult(
                    next_state=BookingState.IDLE,
                    response="Certo, nessun problema. La aspettiamo quando vuole!"
                )
```

---

## 7. Fix per `_handle_waiting_surname()` (Bug B secondario)

**File**: `booking_state_machine.py`, riga 1894-1898 (fallback di `_handle_waiting_surname`)

```python
# PRIMA:
        # Couldn't extract surname - re-ask
        return StateMachineResult(
            next_state=BookingState.WAITING_SURNAME,
            response="Mi ripete il cognome, per cortesia?"
        )

# DOPO:
        # Check for explicit rejection before asking again
        if HAS_ITALIAN_REGEX:
            is_reject, _ = is_rifiuto(text)
            if is_reject:
                self.context.state = BookingState.IDLE
                return StateMachineResult(
                    next_state=BookingState.IDLE,
                    response="Certo, nessun problema. La aspettiamo quando vuole!"
                )

        # Couldn't extract surname - re-ask
        return StateMachineResult(
            next_state=BookingState.WAITING_SURNAME,
            response="Mi ripete il cognome, per cortesia?"
        )
```

---

## 8. Test da aggiungere

### Test nuovi per GAP-A5 (file: `tests/test_booking_state_machine.py`)

```python
class TestCancelPreIdentification:
    """GAP-A5: Cancel during WAITING_NAME/WAITING_SURNAME must go to IDLE."""

    def test_annulla_in_waiting_name_goes_to_idle(self):
        """'annulla tutto' in WAITING_NAME → IDLE (not WAITING_SERVICE)."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("annulla tutto")
        assert result.next_state == BookingState.IDLE, (
            f"Expected IDLE, got {result.next_state}"
        )

    def test_cancella_in_waiting_name_goes_to_idle(self):
        """'cancella' in WAITING_NAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("cancella")
        assert result.next_state == BookingState.IDLE

    def test_no_grazie_in_waiting_name_goes_to_idle(self):
        """'no grazie' in WAITING_NAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("no grazie")
        assert result.next_state == BookingState.IDLE

    def test_lascia_perdere_in_waiting_name_goes_to_idle(self):
        """'lascia perdere' in WAITING_NAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("lascia perdere")
        assert result.next_state == BookingState.IDLE

    def test_annulla_in_waiting_surname_goes_to_idle(self):
        """'annulla tutto' in WAITING_SURNAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Marco"
        result = sm.process_message("annulla tutto")
        assert result.next_state == BookingState.IDLE

    def test_no_grazie_in_waiting_surname_goes_to_idle(self):
        """'no grazie' in WAITING_SURNAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_SURNAME
        sm.context.client_name = "Marco"
        result = sm.process_message("no grazie")
        assert result.next_state == BookingState.IDLE

    # --- Regression: reset in mid-booking must still go to WAITING_SERVICE ---

    def test_annulla_tutto_mid_booking_still_goes_to_waiting_service(self):
        """'annulla tutto' in WAITING_DATE → WAITING_SERVICE (regression guard)."""
        sm = create_state_machine()
        sm.start_booking_flow()
        sm.process_message("taglio")
        # Now in WAITING_DATE
        result = sm.process_message("annulla tutto")
        assert result.next_state == BookingState.WAITING_SERVICE, (
            f"Mid-booking reset should go to WAITING_SERVICE, got {result.next_state}"
        )

    def test_ricominciamo_in_waiting_name_goes_to_idle(self):
        """'ricominciamo' in WAITING_NAME → IDLE (utente non ha ancora dato nome)."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message("ricominciamo")
        assert result.next_state == BookingState.IDLE

    @pytest.mark.parametrize("phrase", [
        "no grazie",
        "lascia perdere",
        "non voglio",
        "basta così",
        "ho cambiato idea",
    ])
    def test_rejection_phrases_in_waiting_name(self, phrase):
        """Parametric: all rejection phrases in WAITING_NAME → IDLE."""
        sm = create_state_machine()
        sm.context.state = BookingState.WAITING_NAME
        result = sm.process_message(phrase)
        assert result.next_state == BookingState.IDLE, (
            f"'{phrase}' in WAITING_NAME should go to IDLE, got {result.next_state}"
        )
```

---

## 9. Acceptance Criteria misurabili

| AC | Verifica |
|---|---|
| AC-1: "annulla tutto" in WAITING_NAME → `next_state == IDLE` | `test_annulla_in_waiting_name_goes_to_idle` |
| AC-2: "cancella" in WAITING_NAME → `next_state == IDLE` | `test_cancella_in_waiting_name_goes_to_idle` |
| AC-3: "no grazie" in WAITING_NAME → `next_state == IDLE` | `test_no_grazie_in_waiting_name_goes_to_idle` |
| AC-4: "lascia perdere" in WAITING_NAME → `next_state == IDLE` | `test_lascia_perdere_in_waiting_name_goes_to_idle` |
| AC-5: "annulla tutto" in WAITING_SURNAME → `next_state == IDLE` | `test_annulla_in_waiting_surname_goes_to_idle` |
| AC-6: "no grazie" in WAITING_SURNAME → `next_state == IDLE` | `test_no_grazie_in_waiting_surname_goes_to_idle` |
| AC-7: "annulla tutto" in WAITING_DATE (mid-booking) → `next_state == WAITING_SERVICE` | `test_annulla_tutto_mid_booking_still_goes_to_waiting_service` — regression |
| AC-8: Response per tutti i casi di exit contiene parola "aspettiamo" o "problema" | assertion su `result.response` |
| AC-9: `pytest tests/ -v --tb=short` → tutti green (1334+ PASS, 0 FAIL) | pytest run |

---

## 10. Copertura test esistenti per WAITING_NAME

Dall'analisi del test file:

| Test | Cosa copre | GAP-A5 coperto? |
|---|---|---|
| `test_name_extraction` (riga 370) | Estrae "Laura Bianchi" da "mi chiamo Laura Bianchi" | No |
| `test_confirming_to_cancelled` (riga 187) | "no annulla" in CONFIRMING → CANCELLED | No (stato diverso) |
| `test_annulla_tutto_interruption` (riga 223) | "annulla tutto" in WAITING_DATE → WAITING_SERVICE | No (stato diverso) |
| `test_negative_responses` (riga 672) | "no grazie" in CONFIRMING → CANCELLED | No (stato diverso) |

**Conclusione**: 0 test coprono "annulla" / "no grazie" in WAITING_NAME o WAITING_SURNAME. Tutti i test esistenti testano questi comportamenti in stati avanzati.

---

## 11. Ordine di implementazione consigliato

1. **Fix A** (2 righe cambiate in `_check_interruption`) — impatto maggiore, più sicuro
2. **Fix B** (import `is_rifiuto` + 4 righe in `_handle_waiting_name` fallback)
3. **Fix B secundario** (`_handle_waiting_surname` fallback — pattern identico)
4. **Test** — 8 nuovi test in `TestCancelPreIdentification`
5. **pytest** → verifica 1334+ PASS

**Stima tempo**: 20-30 minuti totali (fix minimali + test).

---

## 12. Verifica impatto su test esistenti

Il test `test_annulla_tutto_interruption` (riga 223) verifica:
```python
sm.process_message("taglio domani alle 15")  # stato è WAITING_CONFIRMING/WAITING_DATE
result = sm.process_message("annulla tutto")
assert sm.context.state == BookingState.WAITING_SERVICE
```
Questo test NON sarà rotto dal Fix A perché:
- Dopo `sm.process_message("taglio domani alle 15")` lo stato è `WAITING_TIME` o `CONFIRMING`
- `WAITING_TIME` non è in `PRE_IDENTIFICATION_STATES`
- Quindi il fix lascia invariato il path → ancora WAITING_SERVICE

Il test `test_annulla_interruption` (riga 206-221) con "ricominciamo":
```python
sm.start_booking_flow()        # stato WAITING_SERVICE
sm.process_message("colore")   # stato WAITING_DATE
sm.process_message("domani")   # stato WAITING_TIME
result = sm.process_message("no aspetta, ricominciamo")
assert sm.context.state == BookingState.WAITING_SERVICE
```
Non rotto — stato è WAITING_TIME, non in PRE_IDENTIFICATION_STATES.
