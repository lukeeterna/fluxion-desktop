# T-BOOKING-DIAG2/#34v — Perché il guard non scatta

**Data:** 2026-08-01  
**Base commit:** 348d459d  
**Processo riavviato:** PID 2703, VOICE_ENGINE=go, registered=true, reg_status=200

---

## F1 — Verifica processo stantio

**Situazione pre-riavvio:**
- PID 13067 avviato **Gio 31 lug 23:xx** (before fix Sol)
- Fix Sol (1e6c628f) committato e pullato su iMac oggi **01 ago 16:26**
- md5 orchestrator.py su disco = identico MacBook/iMac (c329aeae9d90fa09ba1ccb10ff8a34e1)
- **Ma il processo in memoria aveva il codice PRE-fix** (Python carica al boot, non rilegge il file)

**Dopo riavvio (VOICE_ENGINE=go):**
- Scenario Parrucchiere completo: servizio → nome → telefono → conferma → waiting_date → data
- Input "martedi 8 settembre" in stato waiting_date → layer `L2_slot`, FSM `waiting_date`
- Risposta: limite 60 giorni (gestione corretta della data) — **NON** "Non ho trovato appuntamenti da spostare"
- L1_exact SPOSTAMENTO **non intercetta** più la data in booking context

**Esito F1: RISOLTO** — il loop era prodotto dal processo stantio, non da un difetto nel codice corrente.

## F2 — Log strumentale

**Non eseguito** — F1 ha risolto il problema. Il guard `skip_for_booking` funziona correttamente con il codice aggiornato.

Riga di log verbatim: N/D (F1 risolto, F2 non attivato per protocollo)

## F3 — Igiene .bak

5 file rimossi dal tracking con `git rm --cached`:
- `voice-agent/src/orchestrator.py.bak-B3FIX1`
- `voice-agent/src/nlu/providers.py.bak-nlu-20260715_180406`
- `voice-agent/src/voip_goengine.py.bak-PRE-FIXBARGE-20260711-183353`
- `voice-agent/src/voip_goengine.py.bak-PRE-FIXBARGE2-20260711-190934`
- `voice-agent/src/voip_goengine.py.bak-PRE-MEDIASWAP-METRIC-20260708-000233`

Pattern `*.bak-*` aggiunto a `.gitignore` (globale, complementa `*.bak` già presente).

---

## CAUSA:

Il processo su :3002 era avviato il 31 luglio 23:xx, prima del fix Sol (1e6c628f, committato il 01 agosto 16:26). Python carica il sorgente al boot: il processo girava l'orchestrator.py PRE-fix in memoria, senza il guard `skip_for_booking`. La diagnosi "L1 non ha il guard" nel booking_fix.md precedente era basata su un processo stantio, non sul codice live di master. Dopo riavvio, il guard funziona: l'input data in stato waiting_date viene gestito da L2_slot, non intercettato da L1_exact SPOSTAMENTO.
