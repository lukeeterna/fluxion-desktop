# NEXT SESSION PROMPT — T-STRESS-VERTICALI (#34v)
> Generato: 2026-07-31 09:39 UTC | Chiusa per context 60% (vincolo #7 + STEP -1 mandato)

## STATO
- Context: 60% — STOP obbligatorio
- GATE-0 NON eseguito (base 53a8ecdc confermata da log)
- STEP 0 NON eseguito: codice Sol non ancora ricevuto
- :3002 UP produzione go engine pid 13067, trunk EHIWEB

## PROSSIMA SESSIONE — ricomincia da zero

### Prima riga obbligatoria: ⛔ ACCEPT-EDITS: non ci faccio affidamento.

### STEP -1: verifica used_pct dal json più recente in /tmp/claude-ctx-*.json. STOP se ≥60%.

### STEP 0: founder incolla codice Sol → scrivi TAL QUALE in vos/runs/20260731/stress_verticali.py
Valida: wc -l · head -8 (3 righe dichiarazione Sol) · grep -c 'def ' · grep -n 'set-vertical|3002' | head -4
Se vuoto/tronco/no 3 righe → STOP VERDETTO: ROSSO

### GATE-0: git fetch; base attesa 53a8ecdc; ./bin/vos_check.sh → 7/7

### Poi F1 → F2 → F3 → CHIUSURA come mandato originale.

## CONTESTO INVARIANTE
- :3002 PRODUZIONE (go engine, trunk EHIWEB vivo). NON riavviare se non indispensabile.
- DB su :3002 è quello vivo del founder. Pulire dati fittizi dopo F2.
- Non toccare rig :3003.
