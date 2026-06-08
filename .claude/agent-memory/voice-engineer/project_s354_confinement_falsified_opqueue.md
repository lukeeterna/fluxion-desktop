---
name: S354 confinement falsified — conference op-queue drained by clock thread
description: S354 prova che il marshalling dell'attach sul loop NON evita lock.c:279; le conf op (Add/Connect port) sono eseguite C-side dal clock thread non-owner. Verdetto S353 falsificato.
type: project
---

S354 (2026-06-08): implementato il confinement PURO richiesto dal verdetto S353 (ESITO 1): `onCallMediaState` enqueue-only (solo `getInfo()` + push `_PendingBridge`), tutto il lavoro lock-taking (`ensure_port`/`getAudioMedia`/`startTransmit`) spostato in `drain_pending_bridges()` sul thread `_pjsua2_thread` (loop libHandleEvents). Stesso pattern applicato all'harness (`HarnessCall.drain_bridge()` chiamato dal loop run_harness). `_register_thread_if_needed` ri-abilitato con guard `libIsThreadRegistered()`.

**RISULTATO: crash IDENTICO, verdetto S353 FALSIFICATO.** EXIT=134 (SIGABRT) su entrambi i processi (Sara + harness), stesso stack su thread `clock`:
`clock_thread → clock_callback → get_frame(pjmedia_port*) → grp_lock_release → __assert_rtn (lock.c:279)`.

**Why (evidenza grezza dai log Sara /tmp/voice-pipeline.log run 11:28):**
- Il confinement S354 FUNZIONA: `Add port 2 (sara_bridge) queued` loggato su `thr0x70000df` (il drain loop thread), e log `S243 T1: Audio bridge established (deferred)` confermato nel run 11:24.
- MA: `Added port 2 (sara_bridge)` + `Port 1 transmitting to port 2` + `possibly re-registering existing thread` sono tutti eseguiti dal thread `clock`, NON dal loop thread.
- Smoking gun strutturale: pjmedia accoda le conference op (`Add port`/`Connect ports queued`) su una **op-queue processata dal CLOCK THREAD interno di pjmedia**. Confinare l'attach al loop thread NON cambia QUALE thread esegue davvero l'operazione: la drena il clock thread, che non è owner del group lock → assert lock.c:279.

**How to apply:** il marshalling Python-side (qualunque thread chiami startTransmit) NON può risolvere questo: il lavoro viene comunque migrato C-side al clock thread dall'op-queue async di pjmedia 2.16-dev. Le opzioni residue NON-Python:
1. Downgrade pjsip 2.15.1 — MA giudice Claude AI S353 sostenne che l'async conf bridge esiste già in 2.15.1 (da ri-verificare con questa nuova evidenza: in 2.15.1 le op potrebbero essere sincrone sul thread chiamante).
2. Rework Asterisk ARI: Asterisk gestisce SIP+media (conference bridge C maturo), Sara = solo brain via ARI. Elimina la race alla radice, gold-standard enterprise, zero-cost (Asterisk OSS).

Il bridge nel run 11:24 si è stabilito ("established (deferred)") prima che il clock thread crashasse → il path SIP/SDP/RTP fino al confirm è sano (200 OK, speex/16000 negoziato, RTP address switched). Il blocco è SOLO la race clock-thread/group-lock della conf bridge.

File modificati S354 (confinement corretto, da TENERE come base per qualunque fix futuro): `src/voip_pjsua2.py` (onCallMediaState enqueue-only + drain con ensure_port/getAudioMedia), `scripts/sara_audio_harness.py` (drain_bridge + guarded thread reg). Backup: `src/voip_pjsua2.py.bak-PRE-S354-20260608-111954`, `scripts/sara_audio_harness.py.bak-PRE-S354-20260608-112257`.
