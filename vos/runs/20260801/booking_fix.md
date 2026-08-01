# T-BOOKING-PROVE/#34v — Verifica fix waiting_date

**Data:** 2026-08-01  
**Commit testato:** 1e6c628f (fix Sol, orchestrator.py 5773 righe)  
**Run ID stress:** stress-v2:20260801T165521:91681:f2c800a5

## F1 — Parrucchiere vs baseline 31/07

| Metrica | Baseline 31/07 | Oggi 01/08 | Delta |
|---------|---------------|------------|-------|
| BOOKING | FAIL (loop waiting_date) | FAIL (loop waiting_date) | invariato |
| KB | WARN | WARN | = |
| AVG ms | 357 | 332 | -25ms ✅ |
| P95 ms | 1227 | 632 | -595ms ✅ |
| FAIL_SARA tot | 15 | 17 | +2 (altri verticali) |

**BOOKING FAIL — root cause aggiornata**: il loop `waiting_date` persiste.
Evidence: `USER: martedì 8 settembre 2026` → `SARA: Non ho trovato appuntamenti da spostare` → `LAYER: L1_exact` → `FSM: waiting_date` ripetuto 4x.

Fix Sol (1e6c628f) aggiunge guard `not skip_for_booking` solo su **L4** (Groq LLM handler).
Il loop avviene a **L1_exact** (regex layer, prima di L4): L1 non ha il guard.
Fix **incompleto** — L1_exact SPOSTAMENTO handler mancante di `skip_for_booking` check.

## F2 — Regressione (sessione pulita, nessun booking attivo)

| Test | Risposta Sara | Esito |
|------|---------------|-------|
| a. spostamento | "Per spostare un appuntamento, mi può dire il suo nome?" | OK ✅ |
| b. cancellazione | "Per cancellare un appuntamento, mi può dire il suo nome?" | OK ✅ |

Nessuna regressione — guard L4 non rompe i percorsi normali.

## F3 — Pulizia DB

Script stress ha rimosso 6 fixture automaticamente. Nessun residuo.

## Stato :3002

PID vivo, engine=go, SIP registered=True, reg_status=200, health=ok.

## VERDETTO: ROSSO

Loop waiting_date non risolto. Fix richiede guard su L1_exact oltre a L4.
Non modificato codice in questa sessione — segnalare a Sol.
