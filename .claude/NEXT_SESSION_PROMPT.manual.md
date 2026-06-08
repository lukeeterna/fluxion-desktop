# CARRY S353 — DECISIONE FOUNDER: pjsip 2.15.1 downgrade (CTO-reco) vs Asterisk ARI → CHIUDERE GATE SARA LAYER 2

> S352 CHIUSO: verdetto Claude AI INGERITO + verificato. La sua fix (threadCnt=0+mainThreadOnly+marshalling+AudioMediaPort) era GIÀ tutta implementata (S243/S244). Esperimento NUOVO mai tentato (guard `libIsThreadRegistered`) ESEGUITO e FALLITO pulito → **verdetto strutturale CONFERMATO con evidenza grezza**.

## ESITO S352 (NON ri-derivare)
- Claude AI ha diagnosticato giusto (thread ownership group-lock) ma la sua fix raccomandata era già nel codice da S243/S244 → crashava lo stesso.
- Insight nuovo S352: il codice chiamava `libRegisterThread` in 7 siti SENZA `libIsThreadRegistered()` → double-register dei thread pjmedia-interni (`onCallMediaS`) = smoking gun `"possibly re-registering existing thread"`. Mai tentato prima.
- FIX S352 (guard conservativo `_register_thread_if_needed`, 7 siti, backup `voip_pjsua2.py.bak-PRE-S352-20260608-102756`): **FALLITA**. `"possibly re-registering existing thread"` ANCORA presente + `Assertion failed grp_lock_unset_owner_thread lock.c:279` + SIGABRT (HARNESS_EXIT=134, crash `Python-2026-06-08-103035.ips`). Bridge wiring si completa (`Added port harness_bridge transmitting`, RTP switched) POI crash. La re-registrazione avviene C-SIDE nel dispatch SWIG-director del media callback, FUORI dai siti Python → non intercettabile da Python.
- **5 fix thread-registration falliti**: S237-S244 (aggressivi) + S352 (conservativo). Race INTERNA al conference-bridge pjsua2, NON sanabile lato Python. Verdetto strutturale Claude AI confermato.
- Stato codice: il guard S352 è ancora nel file (iMac + repo locale, SHA identico). Benigno (più corretto dell'aggressivo) ma NON risolutivo. Decisione commit/revert rimandata alla direzione scelta.

## ⚠️ PRIMA AZIONE S353
1. Pre-flight SIP: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `reg_status:200`? Se 403 → BLOCKED-ON Luke→EHIWEB, NON re-diagnosticare.
2. **ATTENDI GO FOUNDER sulla direzione** (vedi FORK sotto). NON partire con rebuild/rework senza GO (REGOLA #18 validate-then-implement).

## FORK STRATEGICO (decisione founder — carry lo prevedeva)
**RACCOMANDAZIONE CTO (singola, REGOLA #3): pjsip 2.15.1 downgrade PRIMA, Asterisk ARI fallback.**
- **Perché 2.15.1**: evidenza S244 (commento codice righe 870-878) + log = il build attuale è **pjsip 2.16-dev**, il cui conference-bridge fu refactorato da SYNC (`Conf add port N`) ad ASYNC (`Add port N queued`) — ed è ESATTAMENTE il code-path async che innesca la race cross-thread. 2.15.1 ha il conf bridge SYNCRONO. Downgrade = intervento MINIMO che colpisce la causa strutturale CONFERMATA, **preserva tutta l'architettura + il modello di distribuzione** (1 cliente = 1 numero EHIWEB = 1 Sara, binario unico, zero-cost). Costo: rebuild pjproject 2.15.1 + bindings SWIG Python su iMac (meccanico, one-shot; attenzione macOS Big Sur + no-AVX2). VERIFICATO: `libIsThreadRegistered` esiste nel build attuale (non rilevante post-downgrade ma conferma toolchain SWIG ok).
- **Perché NON Asterisk ARI come prima scelta**: Claude AI stesso ha AVVERTITO che Asterisk ARI fa esplodere il bundling per il modello desktop PMI (infilare un PBX completo nell'installer cliente, config/porte su macchine eterogenee, 2° media-path AudioSocket da debuggare). Ha senso solo se si centralizza multi-tenant (rompe il modello per-cliente zero-cost). Resta FALLBACK se anche 2.15.1 crasha.
- **RIFIUTATO come fix: 2° account VivaVox** — Claude AI: darebbe FALSO VERDE (il timing rete reale maschera il bug latente, non lo elimina). Serve DOPO un fix vero, solo per stress-test concorrenza.

## DOPO IL FIX (gate verde)
VERIFICA E2E: harness `voice-agent/scripts/sara_audio_harness.py`, WAV PCM16 8kHz mono a `/tmp/book.wav`. DONE = Sara risponde PERTINENTE via audio reale, NESSUN SIGABRT, RTP scambiato, trascrizione catturata (REGOLA #24). Controlla `/tmp/sara-pjsip-s244.log`: sparito "re-registering", zero `lock.c:279`.

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
