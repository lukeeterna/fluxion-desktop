<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-18 · Chiusura ROSSO — sessione interrotta STEP -1 context gate.
> Sessione precedente: 73fc23d (rettifica giudice, F0 chiuso).

## STATO CORRENTE

**T-SUITE-v1.1-r6 (#34v): sessione interrotta a STEP -1 per used_pct=66% (≥40% → ROSSO). NESSUN lavoro eseguito. Rig mai avviato. :3002 iMac intatto. Base auditata: 73fc23d. Porcelain MacBook = solo `M tools/VectCutAPI`.**

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

**NESSUNA azione su :3002 in questa fase.** Founder-input 2026-07-18: il restart :3002 per validare la suite è **RESPINTO** (inutile per la suite + deploy prod non ratificato). **:3002 si tocca SOLO a B3-PROMOTE, con GO esplicito del founder.**

- Il BLOCKED-ON #1 (E6/reprompt live SCN-04/SCN-05) resta parcheggiato e **NON va risolto via restart :3002**: la sua validazione live è subordinata a B3-PROMOTE. Non riproporlo come "prossima azione".
- Catena T-AUTORUN #34v = CHIUSA e VERDE (2/3/4). Codice FIX-A/FIX-C committato e pushato; verifica live differita a B3-PROMOTE.
- Catena runner invariata (per riferimento futuro): ogni step chiude con `^VERDETTO: (VERDE|ROSSO)$` (ultima riga) o è ROSSO; stop-on-red; commit+push per step; RUN_REPORT finale pushato.

## Rettifica del giudice — 2026-07-18
La CAUSA dell'item BLOCKED-ON #1 è falsificata: il codice FIX-A/FIX-C ERA caricato nella Sara della suite (:3003, boot fresco post-copia); i FAIL SCN-04/05 sono limiti del path testo. L'item non richiede alcuna validazione «con codice caricato»: la copertura E6/silenzio si chiude con SCN-08/09 su rig (T-SUITE-v1.1-r5); il live resta solo alla chiamata di certificazione per-verticale (REGOLA #21), dopo B3-PROMOTE. Dettaglio: vos/runs/20260718/RUN_REPORT.md, «Rettifica del giudice».
