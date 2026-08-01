# STATE — T-BOOKING-FIX/#34v

HEAD ATTESO: 1e6c628f
SESSIONE: 1cc622df-476a-4757-8f12-63cf16ebcc37
DATA: 2026-08-01

## Stato :3002
UP — pid=13067 — engine=go — SIP registered=True reg_status=200

## Fix confermati nel codice
- FIX-A: escalation_manager.py:97 (E6-FIX congedo senza collega)
- FIX-C: booking_state_machine.py:756 (Mi conferma il nome corretto?)
- AI Disclosure: session_manager.py:743 (EU AI Act art.50)

## Sessione 2026-08-01 — T-BOOKING-DIAG/#34v
MANDATO: diagnosi loop FSM waiting_date + merge vos/roadmap + ponte Sol.
GATE-0: merge vos/roadmap→master OK (2 file docs-only). iMac allineato. HANDOFF.md spostato archive/.
F1-F2: diagnosi completata e bancata su commit e0cfcc48.
  - Root cause: LLM NLU classifica data nuda → SPOSTAMENTO; handler L1 (orchestrator.py:1521) 
    scatta senza guard booking_in_progress; FSM _handle_waiting_date() mai raggiunto.
  - Superficie fix: orchestrator.py righe 1521 (SPOSTAMENTO) e 1457 (CANCELLAZIONE).
  - Referto: vos/runs/20260801/booking_diag.md
F3 PONTE: STOP-PONTE — browser autenticato non disponibile. Bozza manuale: incoming/SOL_MESSAGE_DRAFT.md
vos_check.sh: 6/1 (FAIL residuo: NEXT_SESSION_PROMPT.md presente) → risolto sessione corrente 7/7.
:3002: non toccato — UP.

## T-BOOKING-FIX (sessione 2026-08-01 pomeriggio)
PATCH SOL APPLICATA — commit 1e6c628f (master, pushato).
- File: voice-agent/src/orchestrator.py (5768→5773 righe, +5)
- Diff: 4 hunk chirurgici — CANCELLAZIONE+SPOSTAMENTO aggiunti a skip_for_booking + guard not skip_for_booking su handler L4
- Validazione: py_compile OK, diff ±40 righe, nessun refactor
- Pre-flight: backup .bak_pre_sol (5768 righe)
- test_cancel_reschedule.py: 22/22 PASS
- 30 FAIL pre-esistenti (BSM test su testo risposta stale, NON regressions del fix): confermato con git stash pre-Sol
- iMac: git pull OK, pipeline riavviata :3002 health=ok, orchestrator.py = 5773 righe

## Ultimo run T-STRESS-VERTICALI (#34v)
vos/runs/20260731/stress_verticali_v2.md — VERDETTO: ROSSO
Data: 2026-07-31 | Verticale pronto: Parrucchiere/Barbiere
FAIL principale: loop waiting_date → FIX APPLICATO (commit 1e6c628f)

## Unita' residue
→ docs/judge/ROADMAP-PRODUZIONE.md (sezione "Unita' residue, in ordine di dipendenza")
→ T-STRESS-VERTICALI re-run (verificare che loop waiting_date sia risolto in produzione)

## Prossima direttiva operativa
Re-run T-STRESS-VERTICALI con patch Sol attiva per verificare risoluzione loop waiting_date.
Valutare se i 30 FAIL BSM pre-esistenti vanno portati a Sol per sync aspettative test.
