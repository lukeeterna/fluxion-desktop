# RUN_REPORT — T-AUTORUN v1 (#34v) — 20260718

Stato catena: **COMPLETA**  ·  generato 2026-07-18T06:48:32Z

| Step | Verdetto | Commit |
|------|----------|--------|
| 2-FIX-A | VERDE | 219fbbf4 |
| 3-FIX-C | VERDE | 4b844f27 |
| 4-SUITE | VERDE | 31186a65 |

## Discordanze
- porcelain a fine catena:
```
 M tools/VectCutAPI
 M vos/runs/autorun_chain_20260718_082443.out
?? vos/runs/20260718/RUN_REPORT.md
```
- HEAD: 31186a65 ; origin/master: 4b844f27 (snapshot pre-commit RUN_REPORT auto)

## Addendum chiusura sessione (main CC) — 2026-07-18

**Esito catena: COMPLETA — 2/2/4 tutti VERDE.** F1 corretto e pushato (b55c51b0) prima dell'avvio.

**used_pct:** 8.4% (budget_state=SAFE, da /tmp/claude-ctx-<sid>.json). Gli warning hook VOS "55-57%" erano RAW gonfiati (REGOLA #27).

**Commit reali per step** (il lavoro c'è; l'attribuzione differisce dal messaggio runner):
- STEP 2 FIX-A → contenuto in `219fbbf4` (msg `auto-close session ...`): voip_goengine.py FSM-HANGUP GUARD + escalation_manager (rimossa falsa promessa "La passo subito a un collega") + orchestrator + booking_state_machine + report.md.
- STEP 3 FIX-C → contenuto in `4b844f27` (msg `auto-close session ...`): booking_state_machine.py name-gate (+66) + report.md, 4 PASS espliciti.
- STEP 4 SUITE → `31186a65` (feat proprio): run_suite.py (437) + suite_report.md + sample.wav.
- RUN_REPORT auto → `0b9ccf05`. HEAD==origin==0b9ccf05 dopo il push finale.

**Discordanza 1 (attribuzione commit):** STEP 2/3 sono stati committati dall'hook VOS SessionEnd (`git add -A` → messaggio `auto-close session`) PRIMA del commit `auto(N/#34v): VERDE` del runner → nel log manca il messaggio runner per gli step 2/3. Lavoro NON perso (verificato con `git show --stat`). Effetto collaterale: l'hook ha trascinato anche `vos/runs/autorun_chain_*.out` (log launcher). Bonifica: gitignorato + `git rm --cached` in questo commit.

**Discordanza 2 (E6/reprompt live vs suite):** SUITE STEP 4 = PASS 5/7. FAIL onesti su **SCN-04 (escalation E6→congedo)** e **SCN-05 (silenzio→reprompt)**. Causa: la Sara interrogata dalla suite risponde con comportamento PRE-FIX (garbage→`confirming_name`, vuoto→`stt_hallucination`), cioè NON ha caricato il codice FIX-A/FIX-C (nessun restart :3002, vietato dal mandato). STEP 2/3 provati su rig fresco = VERDE. STEP 4 VERDE legittimo per criterio PLAYBOOK ("suite gira + FAIL veri dichiarati").
→ **BLOCKED-ON (REGOLA 1b):** verifica live E6-exit + reprompt su Sara con codice nuovo caricato = richiede restart :3002 in finestra founder-presente. Terminal fact = suite SCN-04/SCN-05 PASS dopo restart.

**Porcelain a chiusura (post-bonifica):** solo `M tools/VectCutAPI` (tollerato).
