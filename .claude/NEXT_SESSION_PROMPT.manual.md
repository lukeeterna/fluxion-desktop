# S238 — Prompt ripartenza (handoff S237 → S238)

**Generato**: 2026-05-15 ~10:05 (chiusura S237 ORANGE — F1 success status=506784 risolto, nuovo blocker pjmedia clock thread assertion)
**Branch**: master @ `cf243b2` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean

## TL;DR S237 outcome

- ✅ **F1 SUCCESS**: `setNullDev()` post `libStart()` ha sbloccato `pjsua_conf_connect` (era root cause S236 status=506784). Audio bridge ora si stabilisce **in 0ms** invece di fallire dopo 14.5s Core Audio open block.
- ✅ **Decode 506784 confermato**: OSStatus encoded nel gap errno 470000-519999 (no pjsua strerror mapping). Trace: `pjsua_aud.c:1085` non-mswitch branch implicitly chiama `pjsua_set_snd_dev` su prima `startTransmit` se `null_snd==NULL && snd_port==NULL && !no_snd`.
- ❌ **Nuovo blocker emerso post-F1** (era mascherato dal precedente): pjmedia clock master thread assertion → SIGABRT.
- ⚠️ F1-bis (registrare thread in `onFrame*` callbacks) NON sufficiente — l'assertion scatta PRIMA delle frame callback.

## Smoking gun S237 (`/tmp/sara-live-s237-f1bis.log` iMac)

```
09:58:11 Incoming call from: <sip:3281536308@79.98.45.133>
09:58:11 S236 DIAG H1/H2/H3: tutti OK (MRO, refcount=2, format match)
09:58:11 Audio bridge established: call(slot=1) ↔ Sara(slot=2) after 0ms  ← startTransmit SUCCESS
Assertion failed: (glock->owner == pj_thread_this()), function grp_lock_unset_owner_thread, file lock.c, line 279.
                                                                            ← SIGABRT immediatamente
```

Identico timing pre/post F1-bis (commit `cf243b2`). Le frame callback (`onFrameRequested`, `onFrameReceived`) **non sono mai invocate** prima dell'assertion. La registrazione thread nelle callback è quindi irrilevante per questo specifico assertion path.

## Root cause analysis S237 (post-F1)

Quando `setNullDev()` installa il null master port, `pjmedia_clock_create` spawna un **thread interno C-side** che chiama `clock_callback` per tickare il conf bridge ogni 20ms (driven da OS timer, non da pjsua2 event loop). Quel thread:

1. Tocca i `pj_grp_lock` interni del conf bridge per pull/push frames
2. NON è registrato con pjlib (`pj_thread_register` mai chiamato per quel thread)
3. `pj_thread_this()` ritorna NULL su quel thread
4. `grp_lock_unset_owner_thread` legge `glock->owner` (set da chi acquisì il lock, presumibilmente il main pjsua2 thread che ha chiamato `pjsua_conf_connect`) e confronta con `pj_thread_this()` → fallisce → assertion

`mainThreadOnly=True` + `threadCnt=0` (config voip_pjsua2.py:609-610) controllano solo i worker thread di pjsua2 lib, NON i thread pjmedia internal (clock, audio device handlers).

**Per evidence verifiable**: il timing 0ms `Audio bridge established` + assertion immediata significa che lo spawn del clock thread è sincrono con `startTransmit` (via `pjsua_conf_connect2` → `pjmedia_conf_add_port` setup → clock arm).

## Hypothesis nuove S238 (rank-ordered)

### **F2 (TOP) — setNoDev + custom SaraAudioPort come clock master**

Sostituire `setNullDev()` con `setNoDev()` (pjsua2.py L6313). `setNoDev` non installa null master clock. Il conf bridge è poi tickato da `SaraAudioPort` stesso che diventa master clock (pattern raccomandato pjsua2 docs per server SIP applications). `onFrameRequested` viene chiamato da pjlib internal driven dal RTP clock della call, e quel thread può essere registrato proattivamente prima di startTransmit.

**Risk**: medium — richiede capire come pjsua2 conf bridge sceglie il clock master. Possibile flag in `MediaFormatAudio` o flag su `createPort`.

### **F3 — Switch a built-in AudioMediaPlayer + AudioMediaRecorder**

Pjsua2 espone `AudioMediaPlayer` e `AudioMediaRecorder` built-in (no director pattern, no Python callback in audio thread). Replace `SaraAudioPort` con:
- `AudioMediaPlayer` per TTS → call (read da file WAV, ma può anche read da pipe)
- `AudioMediaRecorder` per call → STT (write a file, monitorato in poll)

**Risk**: high — ristruttura intero audio path. Aggiunge latency I/O file. NON ideale per real-time bridge.

### **F4 — ctypes pj_thread_register dal main pre-startTransmit**

Workaround: pre-registrare proattivamente i thread che SAPPIAMO essere creati internamente. Difficile perché:
- pjmedia clock thread è anonimo (no name, no enumeration API)
- `pj_thread_register` richiede `pj_thread_desc` allocato per thread, ma noi non controlliamo lo spawn

**Risk**: very high — fragile, dipende da internals pjsip.

### **F5 — Switch engine SIP (last resort)**

- `python-pjsip` (legacy v1): stabile per custom audio, ma deprecato e Big Sur compat sconosciuto
- Asterisk/FreeSWITCH esterno + Sara come AGI/WebSocket client: più affidabile, costo zero (Asterisk OSS), ma ristruttura architettura

**Risk**: very high, settimane di lavoro.

## Plan S238

### Pre-flight
1. `ssh imac "lsof -ti:3002 || echo PIPELINE_DOWN_OK"` → verifica DOWN
2. Verificare commit `cf243b2` MacBook + iMac sync

### Step 1 — Subagent voice-engineer: clock master in pjsua2 (15 min)
Research domande:
- Cosa fa `setNullDev` vs `setNoDev` esattamente in `pjsua_aud.c`?
- Pjsua2 docs/examples: pattern raccomandato per server SIP applications senza local audio
- Esiste API per registrare custom port come clock master del conf bridge?
- WebFetch sources pjmedia/conf.c per capire come viene scelto il clock driver
- Output: `.claude/cache/agents/s238/pjsua2-clock-master-pattern.md`

### Step 2 — F2 prototype (se feasible da analisi)
Sostituire `setNullDev()` con `setNoDev()` + verificare se conf bridge clock è driven dalla call RTP stream (l'audio flow IN/OUT via SIP fornisce il clock). Se sì, no spawn di clock thread interno → no assertion.

### Step 3 — Test live discriminate
Founder chiama 0972536918, parla "Buongiorno". Discriminante:
- Sente greeting entro 3s → S238 chiude GREEN
- Silenzio → log mostra cosa è cambiato (new error path) → iterate

### Step 4 — Se F2 fallisce
Considerare F3 (AudioMediaPlayer/Recorder built-in) — richiede sessione dedicata, ristrutturazione audio path.

## File modificati S237 (mantenuti)

- `voice-agent/src/voip_pjsua2.py` L613-624: F1 `setNullDev()` post `libStart()` (commit `685d44c`)
- `voice-agent/src/voip_pjsua2.py` L104-138 + L135 + L143: F1-bis `_ensure_thread_registered` + chiamata in onFrame* (commit `cf243b2`)
- `.claude/cache/agents/s237/pjmedia-vs-pjsua-bridge-namespace.md`: report voice-engineer S237 (N2 falsified + root cause F1)

**Nota**: F1 e F1-bis sono **MANTENUTI** in master. F1 ha risolto status=506784 (progresso reale). F1-bis è defensive (zero overhead post-prima-call, sicuro anche se non sufficiente per il blocker S238).

## Cronologia bug onesta (per chi legge dopo)

| Sessione | Stato live SIP | Audio Sara erogato? |
|----------|----------------|---------------------|
| S232 | Solo test text-based 147/0/0 | NO (NON era live SIP) |
| S233 | call 1 OK 10s (founder hung up), call 2 startTransmit fail | NO (mai erogato greeting) |
| S234 | Primo INVITE startTransmit fail | NO |
| S235 | Fix B+A applicato, startTransmit ancora fail | NO |
| S236 | Diagnostic landed, status=506784 isolato | NO |
| S237 | F1 fix: startTransmit SUCCESS 0ms. Nuovo blocker assertion lock | NO ma progresso reale |

Pipeline FLUXION non ha **mai** erogato audio Sara in produzione SIP live. F1 è il primo passo concreto in avanti.

## Comando one-liner ripartenza S238

```
Sessione S238 FLUXION. Leggi MEMORY.md "Stato Corrente S237" + .claude/NEXT_SESSION_PROMPT.manual.md. F1 (setNullDev) ha risolto status=506784 — audio bridge ora si stabilisce in 0ms. Nuovo blocker: pjmedia clock master thread assertion `grp_lock_unset_owner_thread lock.c:279` SIGABRT subito dopo startTransmit. F1-bis (libRegisterThread in onFrame*) insufficiente — assertion scatta prima delle frame callback. Plan S238: subagent voice-engineer ricerca pattern clock master pjsua2 server SIP headless → F2 (setNoDev + custom port as clock master) → test live.
```
