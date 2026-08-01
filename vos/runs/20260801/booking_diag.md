# Diagnosi: loop FSM waiting_date — T-BOOKING-DIAG/#34v
Data: 2026-08-01

## Sintomo
Stato FSM `waiting_date`, booking in corso (service=taglio_uomo, date=None).
Input «martedì 8 settembre 2026» → risposta «Non ho trovato appuntamenti da spostare. Posso
aiutarla in altro modo?» → stato rimane `waiting_date` → loop 4x.

## Evidenza verbatim (scorecard v2, parrucchiere/barbiere — 2026-07-31)
```
USER: martedì 8 settembre 2026
SARA: Ok. Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?
FSM:  waiting_date
LAYER: L1_exact
LATENCY_MS: 256.7
BOOKING_ACTION: {state: waiting_date, service: taglio_uomo, date: None}
```

Caso confermato anche su Officina Auto:
```
USER: mercoledì 9 settembre 2026
SARA: Perfetto. Non ho trovato appuntamenti da spostare. Posso aiutarla in altro modo?
FSM:  waiting_date
LAYER: L1_exact
LATENCY_MS: 1634.6
```

## a) Classificazione in waiting_date
`orchestrator.py:1282–1308` — il LLM NLU (Groq, ~250ms) classifica «martedì 8 settembre 2026»
come `SaraIntent.SPOSTAMENTO` perché il prompt NLU (`nlu/schemas.py:141`) non include il contesto
FSM corrente: il modello vede solo la stringa e la interpreta come richiesta di spostamento data.
Il risultato popola `intent_result` (categoria `IntentCategory.SPOSTAMENTO`).
Il handler SPOSTAMENTO a `orchestrator.py:1521` scatta su questo valore.

## b) Il ramo spostamento verifica lo stato corrente?
NO. Condizione a `orchestrator.py:1521`:
```python
if response is None and intent_result.category == IntentCategory.SPOSTAMENTO:
```
Non c'è alcun guard su `booking_in_progress` né su `self.booking_sm.context.state`.
A confronto: il `skip_for_booking` definito a `orchestrator.py:1392` protegge SOLO
`IntentCategory.CONFERMA` e `IntentCategory.RIFIUTO`, non SPOSTAMENTO né CANCELLAZIONE.
Il handler si attiva incondizionatamente per qualsiasi stato FSM non-IDLE.

## c) Parser di date già esistente per il booking
Sì. `entity_extractor.py:263` — `extract_date()` — parser completo (relativo+assoluto, italiano).
Viene invocato da `booking_state_machine.py:946` via `_handle_waiting_date(user_input, extracted)`.
Questo codice NON viene mai raggiunto perché L1 intercetta la risposta prima che il booking SM
venga chiamato (`orchestrator.py:1765–1777` — `should_process_booking` è True ma viene saltato
perché `response` è già non-None dopo il handler SPOSTAMENTO).

## d) Stati FSM esposti alla stessa intercettazione
Tutti gli stati non-IDLE, perché il guard SPOSTAMENTO non usa `booking_in_progress`:
- `waiting_service`, `waiting_date`, `waiting_time`, `waiting_operator`
- `confirming`, `propose_registration`, `registering_phone`, `registering_surname`
- `asking_close_confirmation`, `asking_waitlist`, ecc.
Il fix è un guard singolo (`not booking_in_progress`) da aggiungere alla condizione SPOSTAMENTO
(e per coerenza anche a CANCELLAZIONE, che ha la stessa assenza di guard a `orchestrator.py:1457`).

## SUPERFICIE DEL FIX
- `voice-agent/src/orchestrator.py` — righe 1521 (SPOSTAMENTO guard) e 1457 (CANCELLAZIONE guard)
