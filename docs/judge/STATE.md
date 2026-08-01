# STATE — T-BOOKING-PROVE/#34v

HEAD ATTESO: 48b46b11
SESSIONE: 51a48468-4bc1-4fa7-83ab-f9f5de824604
DATA: 2026-08-01

## Stato :3002
UP — engine=go — SIP registered=True — reg_status=200 — health=ok

## Fix confermati nel codice
- FIX-A: escalation_manager.py:97 (E6-FIX congedo senza collega)
- FIX-C: booking_state_machine.py:756 (Mi conferma il nome corretto?)
- AI Disclosure: session_manager.py:743 (EU AI Act art.50)
- FIX-SOL (1e6c628f): orchestrator.py — skip_for_booking L4 guard CANCELLAZIONE+SPOSTAMENTO

## T-BOOKING-PROVE — 2026-08-01

VERDETTO: **ROSSO**

Loop waiting_date NON risolto dal fix Sol (1e6c628f).

Root cause: LAYER L1_exact gestisce SPOSTAMENTO senza guard booking_in_progress.
Sol aveva fixato L4 (Groq handler). L1_exact = layer regex, scatta PRIMA di L4, non ha `not skip_for_booking`.

Evidenza (vos/runs/20260801/booking_fix.md):
- Parrucchiere BOOKING: FAIL — loop 4x — "Non ho trovato appuntamenti da spostare" da L1_exact
- F2 regressione: OK (spostamento/cancellazione fuori booking: nessuna regressione)
- AVG 332ms (-25 vs baseline), P95 632ms (-595 vs baseline 1227ms) — latenza migliorata
- Cleanup: OK (6 fixture rimosse dallo script)

## Confronto baseline 31/07 vs 01/08 (Parrucchiere)
- BOOKING: FAIL → FAIL (invariato)
- AVG: 357ms → 332ms
- P95: 1227ms → 632ms

## Prossima direttiva operativa
Segnalare a Sol: fix L1_exact mancante.
In orchestrator.py, la gestione L1_exact SPOSTAMENTO (e analoga CANCELLAZIONE) deve aggiungere
guard `if booking_in_progress` identico a quello applicato a L4.
Superfice: cercare handler L1_exact SPOSTAMENTO prima di riga 1391.
