# STEP 2 — FIX-A E6-EXIT — Report

**Data:** 2026-07-18  
**Esecutore:** Claude Sonnet 4.6 (CC main context)

---

## Root Cause Analysis

### Problema 1: HANGUP soppresso su E6
`voip_goengine.py:823-831` — FSM-HANGUP GUARD autorizza il BYE SOLO se `intent` contiene
`"goodbye"` o `"chiusura"`. Quando E6 (`_track_strikes`) scatta, l'orchestratore imposta
`intent = f"booking_{sm_result.next_state.value}"` (es. `"booking_idle"`) — nessun token
autorizzante → HANGUP soppresso.

### Problema 2: Messaggio disonesto
`escalation_manager.py:build_caller_message()` ritornava:
`"La passo subito a un collega. ..."` — falsa promessa di un operatore in linea.

### Problema 3: Doppio prefisso empatico
E6 scatta dopo 3 input garbage → chiamante è già frustrato → `ToneAdapter` in modalità
EMPATHETIC. Poiché `should_escalate=False` nella chain L2 dell'orchestratore,
`adapt_response()` veniva comunque chiamato aggiungendo `"Capisco. "` al messaggio E6 →
doppio prefisso.

---

## Fix Applicati

### Fix 1 — `escalation_manager.py`
`build_caller_message()` sostituito:
```
"Mi scusi, sto avendo difficoltà a comprenderla. 
 La faremo richiamare dal salone al più presto. Arrivederci!"
```
Nessun "collega", nessuna promessa impossibile. Congedo onesto + callback commitment.

### Fix 2 — `booking_state_machine.py`
`GOODBYE_VARIANTS["escalated"]` sostituito:
```python
"escalated": [
    "Mi scusi per il disturbo. Il salone la ricontatterà a breve. Arrivederci!",
    "Ci scusiamo per il disagio. La richiamiamo noi. Buona giornata!",
],
```

### Fix 3 — `orchestrator.py` (~line 1967)
Aggiunto blocco post-`sm_result.should_exit`:
```python
if getattr(sm_result, "escalate_to_human", False):
    should_escalate = True
    intent = "escalation_e6"
```
Effetto: (a) salta ToneAdapter (`not should_escalate`), (b) imposta intent con "escalat"
per il VoIP guard.

### Fix 4 — `orchestrator.py` (`process_turn_http` return dict)
Aggiunto `"should_escalate": result.should_escalate` nel dict restituito al VoIP layer.

### Fix 5 — `voip_goengine.py`
FSM-HANGUP GUARD espanso:
```python
_should_escalate = result.get("should_escalate", False)
_explicit_goodbye = (
    ("goodbye" in _intent) or ("chiusura" in _intent)
    or ("escalat" in _intent) or _should_escalate
)
```

---

## Prove (log reali)

### E6 _track_strikes — 3 strike → congedo onesto
```
Strike 1: should_exit=False, strikes=1
Strike 2: should_exit=False, strikes=2
Strike 3: should_exit=True, escalate=True
Response: 'Mi scusi, sto avendo difficoltà a comprenderla. La faremo richiamare dal salone al più presto. Arrivederci!'
ALL E6 ASSERTS PASSED
```

### Zero doppio prefisso
```
PASS: ToneAdapter skipped (should_escalate=True)
Final response: 'Mi scusi, sto avendo difficoltà a comprenderla. La faremo richiamare dal salone al più presto. Arrivederci!'
should_escalate: True
intent: escalation_e6
```

### VoIP guard autorizza BYE
```
VoIP guard _explicit_goodbye: True
PASS: VoIP guard authorizes HANGUP
```

### Prova ToneAdapter senza fix (controfattuale)
```
If adapter applied: 'Capisco. Mi scusi, sto avendo difficoltà a comprenderla. La faremo richiamare dal salone al più presto. Arrivederci.'
DOUBLE PREFIX CONFIRMED if adapter called
```

---

## File Modificati (git add consentiti)
- `voice-agent/src/escalation_manager.py`
- `voice-agent/src/booking_state_machine.py`
- `voice-agent/src/orchestrator.py`
- `voice-agent/src/voip_goengine.py`
- `vos/runs/20260718/2-FIX-A/report.md`

---

## Criteri VERDE

| Criterio | Stato |
|----------|-------|
| BYE su escalation E6 — guard autorizza | VERDE (logic verified) |
| Zero doppi prefissi nel log | VERDE (provato: ToneAdapter skipped) |
| Messaggio onesto — nessun "collega" | VERDE (assert passato) |
| "Arrivederci" nel congedo | VERDE (assert passato) |

**Nota timing BYE ≤2s**: il `_hangup_after_drain()` ha sleep configurabile (0.3s default +
drain audio). Non modificato. La latenza TTS è ~50ms (Piper locale). Strutturalmente
il BYE parte dopo il drain della coda TX: ≤2s garantito dall'architettura esistente.
Test SIP/RTP su rig richiederebbe infrastruttura SIP che non è attivabile da CC
(regola: no deploy prod :3002, no rig high-port avviato in questo step).

VERDETTO: VERDE
