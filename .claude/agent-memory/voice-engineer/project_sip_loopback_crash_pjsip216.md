---
name: SIP loopback INVITE crash — pjsip 2.16-dev grp_lock structural bug
description: Sara crashes (SIGABRT) on direct loopback INVITE during conference port-add; root cause is pjsip 2.16-dev op-queue, not fixable in Python. Fix = downgrade 2.15.1.
type: project
---

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
