# CARRY S352 — IMPLEMENTARE FIX pjsua2 DA VERDETTO CLAUDE AI → CHIUDERE GATE SARA LAYER 2

> Il loop ~15 sessioni è rotto (S351: test ESEGUITO con output reale). Resta UN bug strutturale pjsua2.
> Per uscire dal loop: la prossima sessione NON ri-diagnostica e NON improvvisa — INGERISCE il verdetto di Claude AI e IMPLEMENTA.

## ⚠️ PRIMA AZIONE S352 (in quest'ordine, NON saltare)
1. **CHIEDI A LUKE l'output di Claude AI**: "Incolla qui la risposta di Claude AI al prompt diagnosi pjsua2 (prompt + addendum dati a S351)." Se Luke non l'ha ancora → STOP, attendi, NON improvvisare una fix a freddo.
2. Quando arriva l'output: leggilo, estrai il VERDETTO (domanda E del prompt) e i passi concreti. Verifica i claim tecnici contro la realtà del codice (`voip_pjsua2.py`) PRIMA di applicarli (REGOLA #1: API pjsua2 reali, non verosimili).
3. Pre-flight SIP: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → confermare `reg_status:200`. Se 403 → BLOCKED-ON Luke→EHIWEB (trial instabile), NON re-diagnosticare.
4. IMPLEMENTA la fix raccomandata (delega a `voice-engineer`, REGOLA #25, su iMac). Riavvia pipeline (CLAUDE.md regola 6).
5. VERIFICA E2E: ri-esegui il test harness (`voice-agent/scripts/sara_audio_harness.py`, WAV PCM16 8kHz mono già a `/tmp/book.wav`). DONE = Sara risponde PERTINENTE via audio reale, NESSUN SIGABRT, RTP scambiato, trascrizione catturata. (REGOLA #24: exit-0 ≠ verificato; serve la risposta audio reale.)

## ROOT CAUSE RAFFINATA S351 (evidenza grezza, NON ri-derivare)
- Crash: `EXC_CRASH/SIGABRT`, `__assert_rtn` su `grp_lock_release` ← `pjsip_dlg_dec_lock` ← `pjsip_inv_answer` ← `pjsua_call_answer2`, innescato DENTRO timer callback ICE-complete (`ice_init_complete_cb → on_incoming_call_med_tp_complete2`), sul worker `libHandleEvents` (`voip_pjsua2.py:806 _pjsua2_thread`).
- **SMOKING GUN**: log pjsip lvl5 → subito prima dell'abort `os_core_unix.c "possibly re-registering existing thread"` + il thread media passa da `thr0x700016b` a nome `onCallMediaS`. = thread del callback media (`onCallMediaState`, dove si fa l'add della conference port "sara_bridge") NON registrato pulito in PJLIB / tocca oggetti SIP fuori dal thread che possiede il group lock → assert owner.
- Ipotesi fix (da confermare con Claude AI): thread confinement/registration — NON eseguire API pjsua2 (conf port add / qualsiasi cosa prenda lock dialog) inline in `onCallMediaState` su thread esterno; registrare il thread (`pj_thread_register`/`registerThread`) o marshallare l'op sul thread `libHandleEvents`.
- Falsificato 4x (S336-S338+S351): transport-independent (loopback==LAN crashano identico). 4 crash report 09:41→09:50 stesso pattern = 100% riproducibile. Path provider reale (timing ICE diverso, S244 NON crashava) non testabile in autonomia: INVITE anonimo harness → 403 dal softswitch VivaVox; servirebbe 2° account EHIWEB autenticato.

## FORK (se il verdetto Claude AI dice "pjsua2 non affidabile")
Fallback = rework **Asterisk ARI** (OSS €0): Asterisk gestisce SIP+media battle-tested, Sara = solo brain STT→NLU→TTS. Elimina la race alla radice ma è più lavoro. Decisione founder.

## CONTESTO PRODOTTO
EHIWEB = carrier su cui OGNI futuro cliente italiano FLUXION ospiterà Sara (punta di diamante). Il path inbound-answer+media DEVE essere a prova di crash su scala. Gate vendita REGOLA #21.

## Stato lasciato S351
Pipeline Sara UP (riavviata post-crash, era DAVVERO down), SIP `reg_status:200` verde, `.env` intatto, harness invariato, WAV `/tmp/book.wav` pronto. Prompt diagnosi+addendum consegnati a Luke per Claude AI. 4 `.ips` in `~/Library/Logs/DiagnosticReports/` (iMac) + `/tmp/sara-pjsip-s244.log` + `/tmp/voice-pipeline.log` come evidenza.

## Carry residui (dopo gate Sara)
- **R2**: CI `release-full.yml` ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm). Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 sk_live (Stripe live key).
