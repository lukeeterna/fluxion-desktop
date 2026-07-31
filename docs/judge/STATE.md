# STATE — T-B3-PROMOTE-r2

HEAD ATTESO: 22446998
SESSIONE: 0d30c66d-1dd6-4283-b6c9-31c5b2843a62
DATA: 2026-07-30

## Stato :3002
UP — pid=13067 — engine=go — SIP registered=True reg_status=200

## Fix confermati nel codice
- FIX-A: escalation_manager.py:97 (E6-FIX congedo senza collega)
- FIX-C: booking_state_machine.py:756 (Mi conferma il nome corretto?)
- AI Disclosure: session_manager.py:743 (EU AI Act art.50)

## Ultimo run T-STRESS-VERTICALI (#34v)
vos/runs/20260731/stress_verticali.md — VERDETTO: ROSSO
Data: 2026-07-31 | Durata: 155.8s | Verticali: 6/6 FAIL
FAIL universale BOOKING (booking_created mai osservata — FSM resta in waiting_date dopo conferma)
FAIL CATALOGO 4/6 (Sara risponde FAQ su come prenotare invece di listare servizi)
FAIL ARGOMENTAZIONI 3/6 (risposta non pertinente o contaminata)
FAIL RISPOSTE 1/6 (fisioterapia: "Siamo l'Officina Demo FLUXION" — cross-contamination verticale auto)
LATENZA: p95 OK per parrucchiere(1820ms)/officina(2553ms)/dentista(2042ms); FAIL per fisioterapia(9501ms)/palestra(10190ms)/estetica(10630ms)
CLEANUP DB: OK — 6 fixture rimosse
:3002: UP pid=13067 registered=True salone ripristinato
Verticale PIÙ PRONTO: Parrucchiere / Barbiere
