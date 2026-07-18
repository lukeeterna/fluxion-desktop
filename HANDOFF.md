<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-18 · Chiusura ordinata.
> Restore point pre-overwrite = `HANDOFF.md.bak-20260718_091758` (size 3404, gitignored) + `git show HEAD:HANDOFF.md`.

## STATO CORRENTE

**Catena T-AUTORUN (#34v) ESEGUITA end-to-end: STEP 2→3→4 tutti VERDE. F1 applicato pre-catena. STEP 1 resta VERDE ratificato (`b5027ac8`), non toccato. HEAD==origin==`83df2e55`. Porcelain = solo `M tools/VectCutAPI`.**

### F1 — correzioni pre-catena — commit `b55c51b0` (pushato, pre-commit hook PASSED, 0 errori)
- **F1.1 VERDETTO-MARKER** (era il vero blocco): `vos/PLAYBOOK-1.md` REGOLE COMUNI + `vos/autorun.sh` allineati al contratto ESATTO. Runner ora determina l'esito con `grep -E '^VERDETTO: (VERDE|ROSSO)$'` sull'ultima riga match (`autorun.sh:115-127`); assenza marcatore esatto = ROSSO tecnico; timeout 30 min (`STEP_TIMEOUT=1800`). `bash -n` OK.
- **F1.2** `.gitignore vos/runs/**/audio/` = già presente (no-op verificato).
- **F1.3** `launch_rig.sh:57-60` export `SARA_TEST_CAPTURE=1` a sara3003 = già fatto in STEP 1 ratificato (`b5027ac8`), file tracked pulito (no-op verificato).

### F2 — catena autonoma (`autorun.sh 2 3 4`, headless fresh-CC per step, stop-on-red) — COMPLETA
| Step | Verdetto | Lavoro reale (commit) — verificato `git show --stat` |
|------|----------|------|
| 2-FIX-A E6-EXIT | VERDE | `219fbbf4`: `voip_goengine.py` FSM-HANGUP guard + `escalation_manager.py` (rimossa falsa promessa "La passo subito a un collega") + `orchestrator.py` + `booking_state_machine.py` + report 129 righe |
| 3-FIX-C NAME-GATE | VERDE | `4b844f27`: `booking_state_machine.py` +66 (name-gate); report con 4 PASS (Buonasera→None, bare-name→CONFIRMING_NAME, sì→Marco, no→cleared) |
| 4-SUITE v1 | VERDE | `31186a65`: `voice-agent/tools/suite/run_suite.py` (437) + `suite_report.md` (PASS 5/7) + `sample.wav` |

RUN_REPORT auto `0b9ccf05` → addendum+bonifica chiusura `83df2e55`. RUN_REPORT completo: `vos/runs/20260718/RUN_REPORT.md`.

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **[BLOCKED-ON — REGOLA 1b] E6/reprompt live NON verificati.** SUITE STEP 4 = PASS 5/7; FAIL onesti **SCN-04 (escalation E6→congedo)** e **SCN-05 (silenzio→reprompt)**: la Sara interrogata risponde PRE-FIX (garbage→`confirming_name`, vuoto→`stt_hallucination`) perché il codice FIX-A/FIX-C **non è caricato a runtime** — nessun restart :3002 (vietato dal mandato). STEP 2/3 provati su rig fresco = VERDE. STEP 4 VERDE legittimo per criterio PLAYBOOK ("suite gira + FAIL veri dichiarati"). Fonte: `vos/runs/20260718/4-SUITE/suite_report.md`. **Terminal fact = SCN-04/SCN-05 PASS dopo restart :3002 con codice nuovo.**
2. **Attribuzione commit STEP 2/3**: il lavoro è finito sotto messaggio `auto-close session …` (hook VOS SessionEnd `git add -A` prima del commit `auto(N/#34v)` del runner) → a log manca il msg runner per step 2/3. Lavoro NON perso (verificato). Effetto collaterale già bonificato: log launcher `vos/runs/autorun_chain_*.out` gitignorato + `git rm --cached` (commit `83df2e55`).
3. **git housekeeping**: warning `gc.log` + "too many unreachable loose objects" ad ogni commit → `git prune` consigliato (non bloccante, push riusciti).
4. **porcelain residuo**: solo `M tools/VectCutAPI` (carve-out atteso, mai toccato).
5. **Context**: `used_pct=8.4` (SAFE, da `/tmp/claude-ctx-<sid>.json`); gli warning hook RAW "55-64%" sono notoriamente gonfiati (MEMORY REGOLA #27).

## PROSSIMA DIRETTIVA OPERATIVA

**Chiudere il BLOCKED-ON E6/reprompt (discordanza #1):** in finestra founder-presente, restart della pipeline voce :3002 con il codice FIX-A/FIX-C caricato, poi rieseguire la SUITE per validare SCN-04/SCN-05:

```
# (founder-presente) restart :3002 con codice nuovo, poi:
python voice-agent/tools/suite/run_suite.py
```

- Terminal fact di chiusura: `SCN-04` (escalation E6→congedo onesto, BYE) e `SCN-05` (silenzio→reprompt) = **PASS**.
- Il restart :3002 è un atto founder-presente (era vietato al runner headless): richiede GO founder.
- Catena runner invariata: ogni step chiude con `^VERDETTO: (VERDE|ROSSO)$` (ultima riga) o è ROSSO; stop-on-red; commit+push per step; RUN_REPORT finale pushato.
