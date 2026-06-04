# Prompt per giudice esterno (Claude.ai) — S337 escalation REGOLA #1c

> **Perché questo prompt esiste**: 2 cicli falliti sullo stesso ostacolo (S336 fix Python, S337 downgrade pjsip). Vincolo VOS #1c vieta un 3° ciclo autonomo → si chiede verdetto esterno PRIMA di agire. Incollare integralmente a Claude.ai e riportare il verdetto in `.claude/cache/agents/s337/claude-ai-response.md`.

---

## CONTESTO SISTEMA
- **Prodotto**: FLUXION, gestionale desktop per PMI italiane. Voice agent "Sara" risponde a chiamate telefoniche per prenotare appuntamenti.
- **Stack voce**: Python 3.9 (CommandLineTools), binding **pjsua2** (SWIG) su **iMac macOS 11 Big Sur** (no AVX2). Sara = `voip_pjsua2.py` + FSM 23 stati + RAG. STT Whisper / NLU Groq / TTS Piper.
- **Vincoli non negoziabili**: ZERO costi (no servizi paid, no hardware). NON rompere il path chiamate reali via provider SIP (EHIWEB/vivavox).
- **Perché serve il test loopback**: per validare Sara via audio in autonomia (il CTO guida il test parlando via TTS), senza dipendere da una chiamata telefonica reale. Harness `sara_audio_harness.py` = 2° endpoint pjsua2 locale che fa INVITE a Sara e streamma un WAV su RTP.

## IL PROBLEMA
Sara **crasha con SIGABRT** quando processa un INVITE SIP **loopback** (harness locale → Sara, entrambi su 127.0.0.1), durante il commit delle conference port. Crash confermato via faulthandler nel thread `_pjsua2_thread` dentro `libHandleEvents`, preceduto dai log C di pjsip:
```
conference.c  onCallMediaState  "Add port N queued"
os_core_unix.c                  "possibly re-registering existing thread"
```
Assertion che aborta: `grp_lock_unset_owner_thread` (lock.c). **Owner del group-lock SETTATO dal thread di callback `onCallMediaState`, UNSET da `_pjsua2_thread`** → mismatch → abort.

## DIAGNOSI ATTUALE (rivista S337)
Il bug è **strutturale e version-independent**: il conference port-add parte dal thread di callback `onCallMediaState`; pjsip 2.15+/2.16 usa una op-queue asincrona dove l'op effettiva e l'unset del group-lock avvengono su `_pjsua2_thread` in `libHandleEvents`. I due thread non coincidono → assertion.

## COSA È STATO PROVATO E FALSIFICATO (NON riproporre)
1. **S243 fix**: deferito `startTransmit` nel drainer `drain_pending_bridges`. → Insufficiente (lasciava `createPort` dentro `onCallMediaState`).
2. **S335 fix**: deferito ANCHE port creation (`ensure_port`+`getAudioMedia`) nel drainer. → Crash solo **spostato** da `Add port 2 (sara_bridge, la nostra)` a `Add port 1` = **la conference-port della call-leg, creata INTERNAMENTE da pjsip durante `answer()`, fuori dal controllo Python**. Conclusione: il bug colpisce anche porte che non gestiamo.
3. **S337 downgrade**: pjsip 2.16-dev → **2.15.1** (build da sorgente, verificato `libVersion().full == 2.15.1`). → **Stesso crash identico**. 2.15.1 ha la STESSA op-queue asincrona. **Ipotesi "2.15.1 è sincrona" FALSIFICATA.**

## FATTO CRITICO (potenziale game-changer)
**Le chiamate reali via provider (S244) FUNZIONAVANO live** (Sara rispondeva a una telefonata vera e prenotava). **Solo il loopback crasha sistematicamente.** Ipotesi interna: l'INVITE del provider arriva con media negoziato in un ordine/timing che evita la race; il loopback dispatcha `onCallMediaState` su un media-thread dedicato esponendola sempre. → **Possibile che il loopback test sia uno scenario artificiale più ostile della produzione, e che il bug non si manifesti su chiamate reali.**

## STATO ESTERNO
- Registrazione SIP provider attualmente bloccata: `reg_status:403` (EHIWEB/vivavox, policy lato provider, BLOCKED-ON azione del founder). Quindi una chiamata reale NON è testabile finché il 403 non è risolto.

## DOMANDE AL GIUDICE (decisione architetturale, conseguenze 30/60/90gg)

1. **È un bug nostro o uso scorretto di pjsua2?** Il warning `possibly re-registering existing thread` + l'assertion `grp_lock_unset_owner_thread` indicano un thread non registrato che chiama pjsua. **Esiste un idiom pjsua2 documentato per manipolare conference port da dentro un callback in modo thread-safe?** (`Endpoint.libRegisterThread`, posticipare l'op su `onTimer`/timer heap pjsip, usare `Endpoint.utilTimerSchedule`, o accodare l'op al thread worker pjsua?)

2. **OPZIONE 1 — fix threading (cheap, ~1-2h)**: eseguire il port-add nel contesto del thread worker/event di pjsua così che set e unset del group-lock avvengano sullo stesso thread. È tecnicamente corretto? Risolve ANCHE il crash su `Add port 1` (porta interna creata da pjsip in `answer()`, che NON chiamiamo noi)? Se la porta interna è il problema, il fix lato Python può bastare o è strutturalmente impossibile?

3. **OPZIONE 2 — Asterisk ARI (switch architetturale, ~4-8h)**: spostare SIP+media su Asterisk (gestisce conference/bridging in C testato in produzione mondiale), Sara diventa solo "cervello" via ARI (riceve audio, risponde audio). Elimina del tutto la conference bridge pjsua2 e questa classe di bug. È sproporzionato? Costo zero verificabile (Asterisk OSS)? Rischi su macOS 11 Big Sur?

4. **META-DOMANDA (la più importante)**: dato che **le chiamate provider reali funzionavano** e solo il loopback artificiale crasha — **vale la pena investire altro tempo a far funzionare il loopback, o il gate corretto è "validare Sara con una chiamata reale via provider" (una volta risolto il 403) e abbandonare il test loopback?** In altre parole: stiamo inseguendo un bug che esiste solo nel nostro harness di test e non in produzione?

## OUTPUT RICHIESTO
Verdetto secco: quale opzione (1 / 2 / abbandona-loopback-test-provider-reale), razionale con trade-off a 30/60/90gg, e — se opzione 1 — il pattern pjsua2 esatto da applicare con riferimento doc/API reale (non inventato). Se la meta-domanda 4 cambia tutto, dillo per primo.
