<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-18 · Chiusura ordinata.
> Restore point pre-overwrite = `HANDOFF.md.bak-20260718_080506` (size 4285, gitignored) + `git show HEAD:HANDOFF.md`.

## STATO CORRENTE

**Ripresa catena T-AUTORUN (#34v). Applicate le 3 correzioni pre-catena richieste dal giudice a runner/PLAYBOOK/gitignore/launch_rig e committate. La catena STEP 2→3→4 NON è stata lanciata: founder ha dato `chiudi` prima del lancio. STEP 1 resta VERDE ratificato (`b5027ac8`), non toccato.**

### Correzioni applicate — commit `0c0a5e28` (pushato, pre-commit hook PASSED, 0 errori)
1. **WAITER marcatore `VERDETTO`** — `vos/autorun.sh`:
   - COMMON_RULES: output step deve chiudere con ULTIMA riga `VERDETTO: VERDE` | `VERDETTO: ROSSO <motivo>` (era `VERDICT:`).
   - Verdetto letto dall'**ultima** riga `^VERDETTO: ` dello stdout (`autorun.sh:114-127`, `grep … | tail -n1`), non più primo match. Timeout 30 min già presente (`STEP_TIMEOUT=1800`).
   - `vos/PLAYBOOK-1.md` REGOLE COMUNI: aggiunta la regola «chiudi SEMPRE con la riga VERDETTO…».
   - Zero occorrenze `VERDICT` residue (verificato); `bash -n` OK.
2. **WAV di suite** — `.gitignore`: aggiunto `vos/runs/**/audio/` (WAV volatili STEP 4 restano locali). `PLAYBOOK-1.md` STEP 4: scenari `.wav` in `vos/runs/<data>/4-SUITE/audio/`, commit SOLO 1 wav campione (STEPDIR root) + report testuali. WAV reali in `calls/` restano tracciati.
3. **Rig capture completa** — `.claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh:57`: aggiunto `SARA_TEST_CAPTURE=1` all'export che raggiunge `sara3003` (nohup python main.py, riga 62). Aggiunta minimale (commenti guard preservati), NON copia wholesale di `launch_rig_fixed.sh` (che stripava i commenti). Chiude la discordanza #3 del report STEP 1.

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **Catena STEP 2→4 non eseguita**: interrotta da `chiudi` prima del lancio. Le correzioni sono in place ma NON validate end-to-end su una run reale (nessuno step le ha ancora esercitate).
2. **Fix launch_rig NON ancora provato su rig**: la propagazione `SARA_TEST_CAPTURE=1` a `sara3003` è corretta a lettura codice (`voip_goengine.py:188` legge `os.getenv`), ma la PROVA WAV lato-Sara su rig avverrà solo quando gira STEP 4 (o un rilancio rig su iMac). [non verificato a runtime in questa sessione]
3. **git housekeeping**: warning `gc.log` + "too many unreachable loose objects" ad ogni commit → `git prune` consigliato (non bloccante, push riusciti).
4. **porcelain residuo**: solo `M tools/VectCutAPI` (carve-out atteso, mai toccato).
5. **Context**: `used_pct=55` (json sessione); hook RAW notoriamente gonfiato (MEMORY #27). Chiuso a soglia.

## PROSSIMA DIRETTIVA OPERATIVA

**Lanciare la catena riprendendo da STEP 2** (STEP 1 già VERDE ratificato — non rieseguirlo):

```
bash vos/autorun.sh 2 3 4
```

- Stop-on-red attivo, timeout 30 min/step, commit+push per step, `RUN_REPORT.md` finale pushato (logica invariata nel runner).
- Ogni step ora DEVE chiudere con `VERDETTO: VERDE|ROSSO` (ultima riga) o è ROSSO.
- STEP 4 scrive i `.wav` volatili in `vos/runs/<data>/4-SUITE/audio/` (gitignorata) e committa solo il wav campione + report.
- Capitolati STEP 2/3/4 invariati in `vos/PLAYBOOK-1.md`.

NB: `vos/autorun.sh` (senza argomenti) rilancerebbe anche STEP 1 — idempotente ma inutile; preferire `2 3 4`.
