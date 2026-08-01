# STATE — T-BOOKING-DIAG/#34v

HEAD ATTESO: e0cfcc48
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
vos_check.sh: 6/1 (FAIL residuo: NEXT_SESSION_PROMPT.md presente).
:3002: non toccato — UP.

## Ultimo run T-STRESS-VERTICALI (#34v)
vos/runs/20260731/stress_verticali_v2.md — VERDETTO: ROSSO
Data: 2026-07-31 | Verticale pronto: Parrucchiere/Barbiere
FAIL principale: loop waiting_date (→ ora diagnosticato, fix pending)

## Unita' residue
→ docs/judge/ROADMAP-PRODUZIONE.md (sezione "Unita' residue, in ordine di dipendenza")

## Prossima direttiva operativa
Inviare manualmente incoming/SOL_MESSAGE_DRAFT.md alla conversazione ChatGPT «fluxion 1».
Poi: sessione separata per applicare la patch Sol a orchestrator.py + re-run stress verticali.
