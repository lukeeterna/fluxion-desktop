# REPORT SESSIONE — T-STRESS-VERTICALI (#34v)
Data: 2026-07-31 | Modello: Sonnet 4.6 | Session: 3830a8ae

## Mandato originale
Certificare il contenuto di Sara voice agent su 6 verticali PMI italiani eseguendo
lo script di stress test scritto da Sol TAL QUALE (zero modifiche logiche), produrre
scorecard per verticale, verificare cleanup DB, committare + pushare su GitHub.

## Cosa è stato fatto

### STEP -1 — GATE-0 (vos_check.sh 7/7)
- Commit e5555a9f mancante su origin → git push
- NEXT_SESSION_PROMPT presente (gitignored) → git rm -f
- Dirty working tree → git add + commit a60e4f19
- Finale: 7/7 PASS ✓

### F1 — Script Sol scritto in repo
File: `vos/runs/20260731/stress_verticali.py` (2203 righe)
Commit: a60e4f19
Script Sol copiato verbatim con 3 righe dichiarazione in testa:
```
# DECISIONE: ADATTO voice-agent/tests/e2e/test_sara_stress_per_verticale.py
# RIUSO: conversazioni booking, FAQ, guardrail e soglia 5000 ms
# MODIFICHE: sei verticali, catalogo DB-grounded, fixture uniche e cleanup
```

### F2 — Esecuzione su iMac (:3002, pid 13067, go engine)
- Eseguito via SSH su iMac (192.168.1.2), :3002 bound 127.0.0.1
- Attesa completamento con `until grep EXIT:` (timeout 1260s)
- Durata effettiva: 155.8s
- Cleanup DB: 6 fixture rimosse ✓
- Vertical restaurato: salone ✓

### F3 — Scorecard + STATE.md + push
Commit fd32bc12 (pushato origin/master):
- `vos/runs/20260731/stress_verticali.md` (189 righe, scorecard completa)
- `docs/judge/STATE.md` (sezione "Ultimo run T-STRESS-VERTICALI" aggiunta)

## VERDETTO FINALE: ROSSO — 6/6 verticali FAIL

| Verticale    | Booking | FAQ | Guardrail | Catalogo | Argomenti | p95 lat |
|-------------|---------|-----|-----------|----------|-----------|---------|
| Parrucchiere | FAIL    | OK  | OK        | OK       | OK        | 1820ms ✓ |
| Officina     | FAIL    | OK  | OK        | FAIL     | FAIL      | 2553ms ✓ |
| Dentista     | FAIL    | OK  | OK        | OK       | FAIL      | 2042ms ✓ |
| Fisioterapia | FAIL    | OK  | OK        | FAIL     | FAIL      | 9501ms ✗ |
| Palestra     | FAIL    | OK  | OK        | FAIL     | FAIL      | 10190ms ✗|
| Estetica     | FAIL    | OK  | OK        | OK       | FAIL      | 10630ms ✗|

### Root cause FAIL identificate
1. **BOOKING universale (6/6)**: FSM resta in `waiting_date` dopo "Sì, confermo" — `booking_created` action mai osservata. Driver automatico non replica il comportamento di un utente reale che fornisce nome già in DB.
2. **CATALOGO 4/6**: Sara risponde FAQ "come prenotare" invece di listare servizi. I DB verticali (`voice-agent/data/vertical_dbs/*.db`) non sono collegati al layer L1/L2 RAG per la query catalogo.
3. **CROSS-CONTAMINATION fisioterapia→auto**: "Chi siete?" restituisce "Siamo l'Officina Demo FLUXION" (L4_groq, 7944ms). KB fisioterapia punta al profilo auto nella demo.
4. **LATENZA alta (fisioterapia/palestra/estetica)**: p95 > 9000ms — L4_groq fallback senza match layer precedenti.

### Verticale più pronto
**Parrucchiere / Barbiere** — solo FAIL su booking, tutti gli altri check OK, latenza p95 1820ms.

## Fix necessari (NON eseguiti in questa sessione — mandato era solo misura)
- FSM: transizione da `confirming` → `booking_created` con driver automatico
- RAG: collegare `vertical_dbs/*.db` al layer catalogo
- KB: fixare cross-contamination fisioterapia
- Latenza: ottimizzare path L4_groq per verticali senza match

## Artefatti in repo (origin/master)
- `vos/runs/20260731/stress_verticali.py` — script Sol (a60e4f19)
- `vos/runs/20260731/stress_verticali.md` — scorecard (fd32bc12)
- `docs/judge/STATE.md` — stato aggiornato (fd32bc12)
- `voice-agent/tests/e2e/test_sara_stress_per_verticale.py` — asset 14/05 riusato
- `voice-agent/data/vertical_dbs/*.db` — DB verticali (tabella servizi.nome)
