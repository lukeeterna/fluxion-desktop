<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

> Aggiornato: 2026-07-16 · Chiusura ordinata mandato #34v (B3-X2-PROVE).
> Restore point pre-overwrite = `git show HEAD:HANDOFF.md` (file tracked, era pulito).

## STATO CORRENTE

**Mandato #34v — B3-X2-PROVE (prova esterna congedo M5 su rig multi-inject): 🟢 con caveat. CHIUSO.**

- Commit: `0822510f` (pushed) · HEAD==origin/master==`0822510f` · residuo albero = SOLO `M tools/VectCutAPI`
  (gitlink embedded, pointer-only, pre-esistente; carve-out autorizzato dal giudice, opzione 3).
- Report completo: `.claude/cache/T-SARA-TURNTAKING/rig/REPORT_B3-X2-PROVE_20260716.md`.

**Esito provato (run2 valido, log `.../capture_B3X2_20260716/run2_valid/sara_fsm_transitions.log`):**
- Turno 1 `'Marco Rossi'` → `[S142] Bare name in IDLE → name=Marco,surname=Rossi` = FSM avanzata OLTRE ask_name
  (fonte: sara3003.log 22:52:31).
- Turno 2 `'e arrivederci'` → `intent=CHIUSURA conf=0.80` → `[S142] Standalone goodbye detected → exit=True`
  (22:52:41) → `HANGUP ricevuto da Python → CALL_END` (22:52:48.592). Harness chiuso dal BYE a ~31s (no dur-max).
- Path M5 congedo→BYE FUNZIONA end-to-end sul rig high-port loopback. Fix M5 in HEAD confermato:
  `orchestrator.py:1341` (`intent=goodbye_standalone`) + `:5643` (BYE su congedo), commit `99daeeda`.

**Rig (spento a fine sessione):** launcher `.claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh` (idempotente,
SOLO high-port, guard che aborta su :3002/trunk/Traccar con confronto esatto per-porta). Ricetta:
regstub `127.0.0.1:15062` + `main.py --port 3003` engine=go, env `VOIP_SIP_SERVER=127.0.0.1:15062
VOIP_BRIDGE_PORT=8399 VOIP_LOCAL_PORT=15090`. :3002 baseline pjsua2 INTATTO tutta la sessione.

## DISCORDANZE / CONTRADDIZIONI APERTE

1. **Criterio "≤5s dal fine-utterance turno2"**: literal = **8.6s** (fine-utterance caller 22:52:40 → BYE
   22:52:48.592); MA l'eccedenza è INTERAMENTE la goodbye-TTS che Sara pronuncia prima di riagganciare
   (`'Ha ragione. Arrivederci, buona giornata.'`, SPEAKING :43→:47, ~5s) = design S142 "hangup dopo goodbye TTS".
   Da fine-goodbye-TTS (LISTENING :48) a BYE = **0.6s**. → DECISIONE GIUDICE: la finestra ≤5s va misurata
   dal fine-utterance caller (8.6s = miss) o dal fine-goodbye-TTS (0.6s = pass)? Le condizioni ROSSE del
   mandato ("no BYE / transizione assente") sono entrambe ASSENTI → run NON rosso.

2. **run1 scartato per timing** (non difetto M5): greeting reale ~8s (non ~3s presunti) → `injectat=4000`
   metteva turno1 dentro il greeting → perso. Corretto a `injectat=11000` (turno1 post-greeting). Solo timing
   harness, zero modifiche codice. Capture conservata in `run1_invalid_timing/`.

3. **`*.log` è gitignored** (`.gitignore:39`): l'estratto log evidenza è stato force-added (`-f`) e le righe
   citate sono anche inline nel REPORT. Attenzione: futuri raw-log capture richiedono `git add -f`.

## PROSSIMA DIRETTIVA OPERATIVA

Palla al GIUDICE per due decisioni prima di dichiarare M5 definitivamente verde-secco:

A. **Interpretare il criterio ≤5s** (discordanza #1): se "fine-utterance caller" allora serve valutare se
   la goodbye-TTS di Sara (~5s) è accettabile prima del BYE, o se il BYE deve precedere/accorciare la frase
   di congedo. NB: accorciare la goodbye-TTS = modifica prodotto (UX), NON un bug del path M5.

B. **Contesto residuo**: la saga trunk/telefono reale resta BLOCKED-ON EHIWEB/Asterisk-ARI (S244 falsificata
   CALL-1, MEMORY). Questo mandato NON la tocca: prova SOLO su rig loopback. La chiamata reale DID resta
   gate separato (REGOLA #32: WAV per giudice).

Riavvio rig quando serve: `ssh imac 'bash -s' < .claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh`.
