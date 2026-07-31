[FLUXION] HANDOFF — 2026-07-31 sessione auto-close

## STATO CORRENTE
T-STRESS-VERTICALI v2 COMPLETATO — VERDETTO ROSSO (6/6 FAIL, nessun regresso driver).

## COMMIT SESSIONE
- Script v2 creato: `vos/runs/20260731/stress_verticali_v2.py` (baseline v1 fd32bc12)
- Report run 1: `vos/runs/20260731/stress_verticali_v2.md` (run iniziale, FAIL_DRIVER=2)
- Report run 2: stesso file aggiornato (post-patch `completed`, FAIL_DRIVER=0)
- Debug: `vos/runs/20260731/stress_verticali_v2_debug.md`

## RISULTATI STRESS TEST v2

### Scorecard finale (run 2, FAIL_DRIVER=0)
| Verticale               | Esito | Booking     | FAIL_SARA | FAIL_DRV | p95 ms |
|------------------------|-------|-------------|-----------|----------|--------|
| Parrucchiere / Barbiere | FAIL  | FAIL_SARA   | 2         | 0        | 1227   |
| Officina Auto           | FAIL  | FAIL_SARA   | 3         | 0        | 2332   |
| Studio Odontoiatrico    | FAIL  | FAIL_SARA   | 2         | 0        | 2348   |
| Studio di Fisioterapia  | FAIL  | FAIL_SARA   | 3         | 0        | 6844   |
| Palestra / Centro Fitness| FAIL | FAIL_SARA   | 3         | 0        | 9512   |
| Centro Estetico         | FAIL  | FAIL_SARA   | 2         | 0        | 4201   |

**Totali**: FAIL_SARA=15, FAIL_DRIVER=0, WARN=19
**Verticale più pronto**: Parrucchiere / Barbiere

### Root cause confermati (FAIL_SARA strutturali — non correggibili dal driver)

1. **Booking loop `waiting_date`** (4/6: Parrucchiere, Officina, Palestra, Estetica):
   - Sara riceve data valida (`martedì 8 settembre 2026` etc.) ma risponde
     "Non ho trovato appuntamenti da spostare" restando in `waiting_date`
   - booking_action.context mostra già una data `2093-06-11` preesistente — Sara
     interpreta la nuova data come richiesta di spostamento anziché nuova slot
   - Causa ipotizzata: L1_exact matcher intercetta "martedì X" come modifica
     di un appuntamento già in context, non come nuova data

2. **Booking `completed` senza `booking_created`** (Odontoiatra, Fisioterapia):
   - FSM arriva a `completed`, Sara dice "prenotazione confermata"
   - Ma booking_action.action = `booking_in_progress` (non `booking_created`)
   - Bug Sara: FSM e action non sincronizzati quando lo stato è `completed`
   - Classificato FAIL_SARA (driver v2 patch gestisce `completed` correttamente)

3. **Catalogo deviato nel booking** (Officina, Odontoiatra, Fisioterapia, Palestra):
   - "Quali servizi posso prenotare?" → Sara risponde "Come ti chiami?" (FSM: waiting_name)
   - La sessione eredita il context del booking precedente (reset non svuota FSM)

4. **Cross-contamination Fisioterapia** → "Siamo Officina Demo FLUXION" (FAIL_SARA)

5. **Latenza p95 > 5000ms** su Fisioterapia (6844ms), Palestra (9512ms) — FAIL_SARA

### Modifiche driver v2 vs v1
- Correzione principale: driver FSM-driven puro (no flag temporali) — falso FAIL risolto
- Aggiunto: FAIL_SARA vs FAIL_DRIVER distinzione
- Aggiunto: rilevamento loop FSM (≥3 ripetizioni consecutive)
- Aggiunto: gestione stato `completed` (run 2 patch) → FAIL_DRIVER=0
- Limite MAX_BOOKING_TURNS=20
- Preflight 12 condizioni

## DISCORDANZE APERTE
- Sara non emette `booking_created` action in stato `completed` (source: booking_state_machine.py)
- FSM `waiting_date` loop: L1_exact intercetta date come spostamento anziché nuova prenotazione
- Catalogo: reset sessione non svuota FSM context tra scenari diversi
- Latenza Fisioterapia/Palestra/Estetica strutturalmente > 5000ms (p95)

## PROSSIMA DIRETTIVA OPERATIVA
Incollare report `vos/runs/20260731/stress_verticali_v2.md` + debug a Sol con domanda:
"Fix 3 bug Sara: (a) booking_created action in stato completed, (b) waiting_date loop con
data preesistente in context, (c) reset sessione non svuota FSM booking context tra scenari.
Non toccare il driver."

Oppure: decidere di lavorare solo su Parrucchiere (verticale più pronto, p95=1227ms)
come verticale pilota per il lancio.
