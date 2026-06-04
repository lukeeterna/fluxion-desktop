---
name: SIP loopback INVITE crash — conference op-queue group-lock bug (NOT version-specific, NOT fixable via mainThreadOnly config)
description: Sara crashes (SIGABRT) on direct loopback INVITE during conference port-add. S337 DISPROVED the pjsip-version hypothesis. S338 FALSIFIED the mainThreadOnly/threadCnt config hypothesis: those 3 flags were ALREADY SET before the run, yet Sara crashed identically. Root cause is structural — pjmedia conference port-add from onCallMediaState callback still runs on a separate media thread despite mainThreadOnly=True. Python-level fix is impossible.
type: project
---

## S338 BINARY RUN (2026-06-04) — VERDETTO: FALSIFICATO

**Obiettivo**: verificare se `uaConfig.threadCnt=0` + `uaConfig.mainThreadOnly=True` + `libCreate`/`libHandleEvents` stesso thread risolvono il crash (ipotesi giudice S338).

**Stato config confermato su iMac (commit live, non da MacBook):**
- riga 879: `ep_cfg.uaConfig.threadCnt = 0`
- riga 880: `ep_cfg.uaConfig.mainThreadOnly = True`
- riga 824: `self._ep.libCreate()` dentro `_pjsua2_thread`
- riga 806: `self._ep.libHandleEvents(20)` dentro `_pjsua2_thread`
- riga 902: `self._ep.libInit(ep_cfg)` DOPO i flag (ordine corretto)
- Tutti e 3 i punti del giudice erano GIÀ implementati prima del run.

**Versione pjsua2**: `2.15.1` (confermato `ep.libVersion().full`)

**Esito harness run (singolo, loopback `127.0.0.1:5080`):**
- Harness: INVITE inviato, Sara risponde `100 Trying` — mai `200 OK`.
- Sara: pipeline DOWN dopo run (curl 3002 → connection refused).
- Log `sara-pjsip-s244.log` — ultime righe prima di abort:
  ```
  DEBUG conference.c thr0x700015d  ......Add port 1 (sip:harness@127.0.0.1) queued
  DEBUG pjsua_media.c thr0x700015d  ....Audio updated, stream #0: speex (sendrecv)
  DEBUG os_core_unix.c thr0x700015d  ...Info: possibly re-registering existing thread
  TRACE resample.c onCallMediaS !....resample created: high qualiy, large filter, in/out rate=8000/16000
  TRACE resample.c onCallMediaS  ....resample created: high qualiy, large filter, in/out rate=16000/8000
  DEBUG conference.c onCallMediaS  ....Add port 2 (sara_bridge) queued
  Fatal Python error: Aborted
  Current thread 0x0000700015db8000 (most recent call first):
    File ".../lib/pjsua2/pjsua2.py", line 7333 in libHandleEvents
    File ".../src/voip_pjsua2.py", line 806 in _pjsua2_thread
  ```

**VERDETTO: FALSIFICATO**

`mainThreadOnly=True` è attivo, eppure `onCallMediaState` gira su thread `onCallMediaS` (distinto da `_pjsua2_thread`). Il "queing" delle conference-port (`Add port 1`, `Add port 2 queued`) avviene su `onCallMediaS`, poi `libHandleEvents` su `_pjsua2_thread` processa l'op → group-lock owner mismatch → SIGABRT identico a S336/S337.

**IMPLICAZIONE**: `mainThreadOnly=True` in pjsua2 non equivale a "tutti i callback sul thread python che chiama libHandleEvents". Controlla i callback SIP/INV (onCallState, ecc.) ma NON i callback media interni C-side (`onCallMediaState`/resample/conferenza). L'ipotesi del giudice era sbagliata sull'implementazione reale di mainThreadOnly.

**NEXT (architetturale, NON Python fix):** Nessuna modifica Python può impedire che `onCallMediaState` venga chiamato su `onCallMediaS`. Opzioni strutturali:
1. Asterisk ARI come SIP/media layer, Sara solo come brain (rimuove pjsua2 conference bridge)
2. Sostituire pjsua2 con PJSIP C diretto (basso livello, controlla thread dispatch)
3. Accettare che il loopback test non funziona e usare provider SIP reale EHIWEB (quando 403 risolto) come unico test path per Layer 2



## S337 UPDATE (2026-06-04) — DOWNGRADE 2.15.1 DONE, DID NOT FIX. Hypothesis disproved.
- **Built pjsip 2.15.1 from source on iMac** (tag verified real), SWIG 4.4.1 binding for CommandLineTools Python 3.9, static-linked x86_64 (Big Sur). Installed in `lib/pjsua2/`, verified `ep.libVersion().full == 2.15.1`. STEP 1 = technically successful.
- **CRITICAL FINDING: 2.15.1 ALSO uses the async op-queue.** Sara pipeline log under 2.15.1 still shows `conference.c onCallMediaS "Add port 1 ... queued"` + `"Add port 2 (sara_bridge) queued"` + `os_core_unix.c "possibly re-registering existing thread"` — the EXACT same signature as 2.16-dev. **Sara crashed (SARA_DEAD, port 3002 down) on the loopback INVITE, never sent 200 OK** (harness saw only `100 Trying` then 30s timeout). The harness then aborted in its own teardown (`Assertion call_id>=0 ... pjsua_call_set_user_data pjsua_call.c:2592` = harness-side, not Sara).
- **CONCLUSION: the prior root-cause framing ("2.16-dev introduced an async op-queue, 2.15.1 is synchronous") was WRONG.** The op-queue / group-lock owner-thread mismatch is present in 2.15.1 too. The real root cause is STRUCTURAL: Sara calls conference port-add (`createPort`/`addPort`) from the `onCallMediaState` callback thread, but op processing + group-lock unset happens on `_pjsua2_thread` in `libHandleEvents`. Version downgrade does not touch this.
- **Build artifacts on iMac**: pjsip 2.15.1 source `/tmp/pjproject-2.15.1`, libs built, binding installed in `lib/pjsua2/`. Backup of original 2.16-dev binding = `lib/pjsua2.backup-PRE-S337-20260604-125255/` (verified 22MB, restore point). To revert to 2.16-dev: `cp lib/pjsua2.backup-PRE-S337-*/_pjsua2.cpython-39-darwin.so lib/pjsua2/` (but no reason to — neither version works for loopback).
- **NEXT (do NOT attempt a 3rd Python fix cycle, REGOLA #1c):** the structural fix must make ALL conference port-adds happen on the pjsip event thread, OR abandon pjsua2's conference bridge for the loopback path. Two real options from the dossier: (1) call `Endpoint.libRegisterThread()` / ensure port-add runs inside the pjsua worker thread context so the group-lock owner matches; (2) escalate to **Asterisk ARI (option N5)** as the SIP/media layer, using Sara only as the brain — removes pjsua2 conference bridge entirely. This is an architecture decision for the founder/main, not a quick patch.

---
## ORIGINAL (S336) DIAGNOSIS BELOW — partially superseded by S337 finding above

Sara (voip_pjsua2.py) crasha con SIGABRT su INVITE SIP diretto loopback (harness `scripts/sara_audio_harness.py`), durante il commit delle conference port.

**Why:** pjsip attivo = **2.16-dev** (verificato `ep.libVersion().full`; backup older build in `lib/pjsua2.backup-2.16dev-20260515`). Il refactor 2.16-dev di `pjmedia_conf` usa una op-queue ASINCRONA: `createPort` emette `Add port N queued` sul thread di callback-dispatch (`onCallMediaS`) ma l'op è processata dopo in `libHandleEvents` su `_pjsua2_thread` → grp_lock owner set/unset da thread diversi → `grp_lock_unset_owner_thread` assertion → abort. Crash thread confermato via faulthandler: `_pjsua2_thread` dentro `libHandleEvents` (voip_pjsua2.py:806/799).

**How to apply:**
- S243/S244 avevano già deferito `startTransmit` nel drainer, ma NON `createPort`. Fix S335 (2026-06-03, applicato al file iMac, NON committato, in attesa review main): spostato `ensure_port()`+`getAudioMedia()` da `onCallMediaState` dentro `drain_pending_bridges` (pending.call_audio=None, risolto nel drainer via media_index). py_compile OK.
- RISULTATO: il crash si è SPOSTATO da `Add port 2 (sara_bridge)` a `Add port 1` (la call-leg dell'INVITE, creata internamente da pjsip durante answer — FUORI dal controllo Python). Sara crasha ancora (health=FAIL). **Conferma struttturale: il bug colpisce anche porte che non tocchiamo → NON fixabile lato Python.**
- **NEXT (non tentato — REGOLA #1c stop a 2 cicli):** downgrade pjsip 2.15.1 (runbook in `.claude/NEXT_SESSION_PROMPT.manual.md` S244 path B1) OPPURE provare il backup `lib/pjsua2.backup-2.16dev-20260515` (potrebbe essere build pre-regressione). In 2.15.1 il conf usa `Conf add port N` SINCRONO (no op-queue) → niente owner mismatch.
- Perché le chiamate provider (S244 live OK) sembravano funzionare: timing diverso — il provider INVITE arriva con media già negoziato in un ordine che a volte evita la race; il loopback dispatcha onCallMediaState su un media-thread dedicato esponendola sistematicamente.

**Ambiente test (replica esatta launch main.py):**
- Launch faulthandler: `/tmp/sara_launch_fh.sh` (PYTHONFAULTHANDLER=1 + `-X faulthandler`, stderr→/tmp/sara-fh-stderr.log). pjsip C-log + abort → `/tmp/sara-pjsip-s244.log` (dup2 in `_pjsua2_thread`).
- Harness: `SARA_IP=127.0.0.1 SARA_SIP_PORT=5080 HARNESS_IP=127.0.0.1 HARNESS_SIP_PORT=5070 PYTHONPATH=lib/pjsua2 DYLD_LIBRARY_PATH=lib/pjsua2 /Library/Developer/CommandLineTools/usr/bin/python3 scripts/sara_audio_harness.py --wav /tmp/book.wav`
- WAV input: `say -o raw.aiff "..." && afconvert -f WAVE -d LEI16@8000 -c 1 raw.aiff book.wav` (PCM16 8kHz mono).
- Backup pre-fix: `/tmp/voip_pjsua2.py.bak-s335-1780518361`.
- `timeout` non esiste su macOS iMac — l'harness ha `--timeout` interno.
