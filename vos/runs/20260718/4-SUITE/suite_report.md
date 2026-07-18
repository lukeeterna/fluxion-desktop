# SUITE v1 — Report
**Data:** 2026-07-18 08:45:16
**Target:** http://127.0.0.1:3003
**Totale:** 7 | PASS=5 | FAIL=2 | ND=0

## Tabella riepilogo

| ID | Nome | Verdict |
|---|---|---|
| SCN-01 | smoke — health + greeting | **PASS** |
| SCN-02 | congedo×2 — goodbye ripetuto (idempotenza) | **PASS** |
| SCN-03 | name-gate — «Buonasera» non committato come nome | **PASS** |
| SCN-04 | escalation E6 — 3 garbage → congedo onesto | **FAIL** |
| SCN-05 | silenzio→reprompt — input vuoto genera reprompt | **FAIL** |
| SCN-06 | barge-in — input rapido consecutivo | **PASS** |
| SCN-07 | dettatura numero — inject cifre pulite | **PASS** |

## Dettaglio scenari

### SCN-01 — smoke — health + greeting
**Verdict:** PASS

**[greeting]** INPUT: `'Buongiorno'`
  → HTTP 200 | intent=`greeting_first_turn_ack` | fsm=`idle`
  → RESPONSE: `Mi dica pure, come posso aiutarla?`

- health OK: 2.1.0 pipeline=4-layer RAG
- [PASS] Sara risponde al saluto: 'Mi dica pure, come posso aiutarla?'

### SCN-02 — congedo×2 — goodbye ripetuto (idempotenza)
**Verdict:** PASS

**[congedo_#1]** INPUT: `'Grazie, arrivederci'`
  → HTTP 200 | intent=`goodbye_standalone` | fsm=`idle`
  → RESPONSE: `Che bello! Prego! Arrivederci, buona giornata!`

**[congedo_#2]** INPUT: `'Grazie, arrivederci'`
  → HTTP 200 | intent=`goodbye_standalone` | fsm=`idle`
  → RESPONSE: `Che bello! Prego! Arrivederci, buona giornata!`

- attempt #1: should_exit=True intent=goodbye_standalone hit=True
- attempt #2: should_exit=True intent=goodbye_standalone hit=True
- [PASS] congedo riconosciuto entrambe le volte

### SCN-03 — name-gate — «Buonasera» non committato come nome
**Verdict:** PASS

**[saluto_buonasera]** INPUT: `'Buonasera'`
  → HTTP 200 | intent=`greeting_first_turn_ack` | fsm=`idle`
  → RESPONSE: `Mi dica pure, come posso aiutarla?`

- fsm_state=idle intent=greeting_first_turn_ack
- [PASS] 'Buonasera' trattato come saluto (fsm=idle), NON nome. Response: 'Mi dica pure, come posso aiutarla?'

### SCN-04 — escalation E6 — 3 garbage → congedo onesto
**Verdict:** FAIL

**[garbage_1]** INPUT: `'xkzqwmflpbt'`
  → HTTP 200 | intent=`booking_confirming_name` | fsm=`confirming_name`
  → RESPONSE: `La registro come Xkzqwmflpbt, corretto?`

**[garbage_2]** INPUT: `'aaaa bbbb cccc dddd eeee ffffzz'`
  → HTTP 200 | intent=`booking_waiting_name` | fsm=`waiting_name`
  → RESPONSE: `Benissimo. Come ti chiami?`

**[garbage_3]** INPUT: `'9999 0000 1234 zqzq asdf'`
  → HTTP 200 | intent=`booking_waiting_name` | fsm=`waiting_name`
  → RESPONSE: `Mi dice il nome, per cortesia?`

- [FAIL] E6 NON scattato dopo 3 garbage consecutivi

### SCN-05 — silenzio→reprompt — input vuoto genera reprompt
**Verdict:** FAIL

**[silenzio]** INPUT: `''`
  → HTTP 200 | intent=`stt_hallucination` | fsm=`idle`
  → RESPONSE: ``

- intent=stt_hallucination response=''
- [FAIL] Sara non genera nessuna risposta su input vuoto

### SCN-06 — barge-in — input rapido consecutivo
**Verdict:** PASS

**[turn1]** INPUT: `'Vorrei prenotare un appuntamento'`
  → HTTP 200 | intent=`booking_waiting_name` | fsm=`waiting_name`
  → RESPONSE: `Come ti chiami?`

**[bargein]** INPUT: `'Scusi ho cambiato idea'`
  → HTTP 200 | intent=`booking_idle` | fsm=`idle`
  → RESPONSE: `Nessun problema! Sono qui se cambia idea.`

- [PASS] Sara gestisce barge-in senza crash. turn1_fsm=waiting_name turn2_fsm=idle

### SCN-07 — dettatura numero — inject cifre pulite
**Verdict:** PASS

**[nome]** INPUT: `'Sono Marco Rossi, cliente nuovo'`
  → HTTP 200 | intent=`new_client_phone` | fsm=`registering_phone`
  → RESPONSE: `Non la trovo tra i nostri clienti, Marco. Mi dà un numero di telefono per registrarla?`

**[dettatura_numero]** INPUT: `'tre tre tre uno due tre quattro cinque sei'`
  → HTTP 200 | intent=`booking_confirming_phone` | fsm=`confirming_phone`
  → RESPONSE: `Ho capito 333123456, corretto?`

- fsm_state=confirming_phone intent=booking_confirming_phone
- response='Ho capito 333123456, corretto?'
- [PASS] dettatura numero processata senza crash (HTTP 200, fsm=confirming_phone)
