<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-17 · Chiusura ordinata sessione `6fdbb8f1`.
> Restore point pre-overwrite = `git show HEAD:HANDOFF.md` (file tracked).

## STATO CORRENTE

**Sessione = 2 blocchi: (A) mandato B3-RACCOLTA v2 (#34v) CHIUSO VERDE; (B) addendum B3-FIX-OBS ricevuto SENZA corpo mandato → BLOCKED-ON input giudice/founder. Nessun codice modificato in questa sessione.**

### Blocco A — B3-RACCOLTA v2 (#34v) — 🟢 CHIUSO
- Consegna: dossier taratura chiamata reale finestra 17-07 (21:50:16→21:54:30, engine go) + salvage volatili. READ-ONLY + commit artefatti.
- Commit: `c3ab2467` (`test(B3-RACCOLTA/#34v): dossier taratura finestra 17-07 + salvage volatili`) — **pushato su origin/master**.
- Artefatti (repo, committati):
  - `.claude/cache/T-SARA-TURNTAKING/REPORT_B3-RACCOLTA_20260717.md` (report + scorecard M1..M5 + 7 root-cause + 4 discordanze).
  - `.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/scripts/` (b3_open/close/status.sh, restore.sh, RUNBOOK_B3.md salvati).
  - `.claude/cache/T-SARA-TURNTAKING/B3_LIVE_20260717/` (sara_go.log 224KB, sara_restore.tail2000.log, TURNS.md, TRANSCRIPT.md, CONFIG_SNAPSHOT.md, TEMPLATES_FIRED.md).
- Scorecard sintetica (dal log, `REPORT §3`): M1=ND (disclosure troncata a 40char), M2=FAIL/parziale, M3=FAIL (S142 bare-name «Dbeat»→nome), M4=parziale/ND, M5=ND.
- Root-cause strutturali (`REPORT §4`): RC#1 = euristica `[S142]` bare-name-in-IDLE accetta token singolo come nome senza gate conferma; RC#4 = `[E6]` 3-strike annuncia «la passo a un collega» ma HANGUP soppresso da FSM-guard → loop reprompt.

### Blocco B — addendum B3-FIX-OBS — 🟡 BLOCKED-ON corpo mandato
- Ricevuto SOLO un **addendum a F1** di un mandato `B3-FIX-OBS`; il **corpo (GATE, F1/F2/F3, vincoli, done-condition, chiusura) NON è nel contesto** (compaction ha coperto B3-RACCOLTA, non B3-FIX-OBS).
- Non ricostruito a memoria: nome «FIX» implica write su codice/config observability (per-effetto lossy #1d) → richiede scope esplicito, non sintesi verosimile (#10, #31).
- Addendum registrato (da applicare all'arrivo del mandato):
  1. **Trappola SARA_TEST_CAPTURE=1**: va esportata SIA all'harness SIA al processo Sara. Storia giu/lug: solo all'harness → nessun WAV. `b3_open.sh:60` la setta → F1 deve verificare a QUALE pid arriva davvero (env del processo `sara-go`).
  2. **Non toccare**: `.claude/SARA_STRESS_TEST_PATTERNS.md` e scenari in `cache calls/` (servono alla suite).

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **Corpo B3-FIX-OBS assente**: ricevuto solo addendum a F1. Impossibile eseguire senza scope autorizzato (quali file un mandato FIX abilita a modificare). BLOCKED-ON incollaggio mandato.
2. **HEAD locale ahead di origin al momento della chiusura**: `7e796a8a` (auto-close session hook, non pushato) vs origin `c3ab2467`. `vos-close.sh` gestisce il push finale.
3. **WAV assente finestra 17-07** (`REPORT §8 punto 2`): nonostante `SARA_TEST_CAPTURE=1` a `b3_open.sh:60`, nessun `.wav` post-21:00 → REGOLA #32 non soddisfatta. L'addendum B3-FIX-OBS punta esattamente a questa root-cause (env var non propagata al processo Sara).
4. **sara_restore.log 39KB ≠ 13,8MB** dichiarato (`REPORT §8 punto 1`): `restore.sh` usa `>` (tronca) ad ogni restore → i 13,8MB erano di un restore precedente azzerato.
5. **conversation_turns non persistito** (`REPORT §8 punto 3`): HTTP Bridge offline (`sara_go.log:810`) → turni ricostruiti dal log, DB autorevole = ND.
6. **Context**: hook RAW gonfiato (MEMORY REGOLA #27); json sessione = 9,6% used_pct (autorevole). Operato sotto soglia.

## PROSSIMA DIRETTIVA OPERATIVA

**BLOCKED-ON (giudice/founder): incollare il corpo del mandato `B3-FIX-OBS`** (GATE-0/0bis, definizione F1/F2/F3, vincoli, done-condition, procedura chiusura).

Appena disponibile il corpo, **prima azione F1** (da addendum): `ssh imac 'ps eww <pid-sara-go>'` per leggere l'environment REALE del processo Sara e confermare se `SARA_TEST_CAPTURE` ci arriva o si ferma all'harness — è la root-cause candidata del WAV mancante (discordanza #3, REGOLA #32).

NB: il dossier B3-RACCOLTA (`REPORT_B3-RACCOLTA_20260717.md`) è la base dati verificata da cui B3-FIX-OBS deve partire; non ri-raccogliere, riusare.
