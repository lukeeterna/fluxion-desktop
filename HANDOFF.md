<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-17 · Chiusura ordinata mandato #34v (B3-WINDOW-PREP, pre-flight finestra live B3).
> Restore point pre-overwrite = `git show HEAD:HANDOFF.md` (file tracked).

## STATO CORRENTE

**Mandato #34v — B3-WINDOW-PREP (pre-flight finestra live B3, taglia XS): 🟢 CHIUSO.**

- Commit: `920b7a35` (pushed) · HEAD==origin/master==`920b7a35` · residuo albero = SOLO `M tools/VectCutAPI`
  (gitlink embedded, pointer-only, pre-esistente; carve-out autorizzato).
- Report sessione = C4 in coda alla conversazione (diff-stat, discordanze, CONTEXT).

**F1 — Deploy verificato allineato (host che risponde = iMac):**
- md5 MacBook↔iMac IDENTICI: `orchestrator.py = aa4dcb0884e9160d066a7d209b712edf` ·
  `nlu/providers.py = 7993ce8cd283d5288a507fb1fce91dea`. Nessun scp necessario.
- NLU attivo deployato = `groq/llama-3.3-70b-versatile` (`voice-agent/src/nlu/providers.py:54-61`,
  priority=0, Cerebras rimosso).
- Runtime finestra: `b3_open.sh` killa la produzione (CHECKPOINT 3) e rilancia una Sara-go FRESCA da
  `$VA=$REPO/voice-agent` (CHECKPOINT 4) → la go-engine carica il codice 70B corrente. Nessun restart
  eseguito da me su :3002 (rispettato il divieto). Stato live a fine sessione = pjsua2 + reg 200.

**F2 — Runbook aggiornato** (`.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/RUNBOOK_B3.md`, edit strutturato):
- M5 criterio ratificato: «Sara pronuncia il congedo e chiude lei; BYE ≤2s dalla fine della goodbye-TTS»
  (rig 2026-07-16 misurò 0.6s → verde; fonte `rig/REPORT_B3-X2-PROVE_20260716.md:55`).
- M3 = PARZIALE-con-diagnosi accettabile per promozione (founder D4); fix pieno a BRAINSYNC.
- Nota NLU 70B: annotare latenza percepita per turno durante la chiamata.
- Invarianti: 1 chiamata (max 2) · check orfani post-close · pjsua2 ripristinato e verificato.

**F3 — Pre-call checklist founder** (`.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/PRECALL_CHECKLIST_B3.md`):
una pagina — cosa avviare, cosa osservare M1..M5, cosa raccogliere (WAV/log), come chiudere.

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **Commit `920b7a35` ha un 3° file non nel `git add` esplicito**: `vos-out/decisions.jsonl` (+1 riga,
   gate-pass) aggiunto da hook pre-commit VOS. Append-only lossless (escluso #1d), benigno. Segnalato per
   trasparenza — non richiede azione.
2. **Stale :3002 [NON-blocker]**: il processo produzione live (avviato prima del deploy 2026-07-15) ha in
   memoria la vecchia config `['groq','cerebras']` (log `sara_go.log`). Irrilevante alla finestra: `b3_open`
   lo killa e riavvia fresco → 70B. Anche `b3_close` ricarica fresco → produzione si auto-allinea a 70B.
3. **Doppia copia runbook**: canonica aggiornata = quella nel repo (`.claude/cache/.../B3_RUNBOOK/`); la copia
   effimera `/tmp/b3/RUNBOOK_B3.md` (iMac, 2026-07-14) è più vecchia e NON aggiornata (comandi comunque validi).
4. **M5 caveat interpretativo** (ereditato #34v B3-X2): ≤5s da fine-utterance caller = 8.6s vs ≤2s da
   fine-goodbye-TTS = 0.6s → risolto adottando il criterio ratificato dal giudice (fine-goodbye-TTS).

## PROSSIMA DIRETTIVA OPERATIVA

**La finestra live B3 la esegue il FOUNDER** (non CC). Pre-flight completo → tutto pronto.
1. Founder apre la finestra seguendo `PRECALL_CHECKLIST_B3.md` (DRY-RUN consigliato → poi chiamata reale a
   **0972536918**, 1 sola chiamata max 2). Compila scorecard M1..M5 + latenze percepite per turno (NLU 70B).
2. Founder chiude: `b3_close.sh` → verifica `engine=pjsua2` + reg 200 + niente orfani su :3002.
3. **Mandato CC successivo** = raccolta evidenza: estrarre WAV chiamata da
   `.claude/cache/T-SARA-TURNTAKING/calls/` + `sara_go.log` da `/tmp/b3/` su iMac → montare evidenza M1..M5
   per il giudice (REGOLA #32: WAV allegabile). Verifica orfani :3002 + pjsua2 ripristinato.

NB: la saga chiamata reale via trunk resta BLOCKED-ON (S244 falsificata CALL-1) — questa finestra usa il
path Sara-go/DID diretto del rig B3, non risolve la saga trunk/Asterisk-ARI.
