# CARRY S355 — FORK STRATEGICO pjsip (decisione founder + giudice). Confinement S354 FALSIFICATO con dati. NIENTE 7° ciclo Python autonomo.

> S354: il confinement (verdetto S353/ESITO 1) è stato applicato CORRETTAMENTE eppure **Sara crasha lo stesso**. Root cause raffinata = il **clock thread di pjmedia drena la op-queue del conference bridge** senza possedere il group lock → `lock.c:279` SIGABRT. C-side, **irraggiungibile da Python**. 6 fix Python-side falliti. → STOP autonomo (REGOLA #1c, #18), serve GO founder + giudice.

## ⚠️ PRIMA AZIONE S355
1. Pre-flight SIP: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `reg_status:200`? (era 200 a S354; se 403 → BLOCKED-ON EHIWEB, non re-diagnosticare).
2. **ATTENDI GO FOUNDER + verdetto giudice Claude AI sul FORK** (sotto). NON partire con downgrade/rework senza GO (REGOLA #18 validate-then-implement). Niente 7° ciclo Python-side (REGOLA #1c).

## ESITO S354 (evidenza grezza, VERIFICATA dal main, NON ri-derivare)
- Confinement PURO applicato: `onCallMediaState` enqueue-only (solo `getInfo` + `_pending_bridges.append(_PendingBridge(media_index=i))`); `ensure_port`+`getAudioMedia`+`startTransmit` tutti spostati in `drain_pending_bridges` (thread loop `_pjsua2_thread`, owner del group lock). `_register_thread_if_needed` ri-abilitato con guard `libIsThreadRegistered()`.
- Chiamata SIP reale Sara↔harness → **DUE crash simultanei** 11:28:18: Sara pid 40786 (`Python-2026-06-08-112818.000.ips`) + harness pid 40989 (`Python-2026-06-08-112818.ips`). EXIT=134.
- Stack IDENTICO entrambi, thread `clock`: `clock_callback → get_frame(pjmedia_port*) → grp_lock_release → __assert_rtn (lock.c:279)`. Verificato dal main: 2 `.ips` esistono coi pid; `triggered:true`+`clock_callback`+`grp_lock_release` nel `.000.ips` (Sara).
- **S353 FALSIFICATO**: il baseline empty-callback non crashava Sara solo perché NON montava conference port. Appena Sara monta una conf port (anche marshallata sul loop), il clock thread la drena dalla op-queue e crasha. Non era "solo l'harness".
- ROOT CAUSE: pjmedia 2.16-dev → conference op (`Add port N queued`, `Connect port`) accodate su op-queue **drenata dal clock thread** che non possiede il group lock. Marshallare l'attach sul loop NON basta: il loop accoda, il clock C-side esegue. **Nessun fix Python sposta quel lavoro.**
- Storico 6 fix pjsip falliti: S237-S244 (thread-reg aggressiva) + S352 (guard conservativo) + S354 (confinement puro).

## FORK STRATEGICO (decisione founder, da sottoporre a giudice Claude AI con la NUOVA evidenza)
**RACCOMANDAZIONE CTO (singola, REGOLA #3): sottoporre al giudice Claude AI la nuova evidenza op-queue/clock-thread e chiedere verdetto binario tra A e B. CTO lean verso B (Asterisk ARI) SE il giudice non garantisce che 2.15.1 elimini il clock-drain.**
- **A) pjsip 2.15.1 downgrade**: ipotesi = in 2.15.1 le conf op sono sincrone sul thread chiamante (che possiede il lock), non drenate dal clock thread. ⚠️ Il giudice a S353 aveva DUBITATO che 2.15.1 fosse sincrono (`Add port N queued` non sarebbe novità 2.16-dev). La NUOVA evidenza (crash è SPECIFICAMENTE nel clock-drain della op-queue, non nell'add) va sottoposta per ruling aggiornato. Pro: preserva architettura + modello distribuzione (1 cliente=1 numero EHIWEB=1 Sara, binario unico, zero-cost). Contro: rebuild pjproject 2.15.1 + SWIG bindings su iMac Big Sur no-AVX2, e potrebbe NON risolvere se il giudice ha ragione.
- **B) rework Asterisk ARI** (OSS €0): Asterisk gestisce SIP+media battle-tested, Sara = solo brain STT→NLU→TTS via AudioSocket/ARI. Elimina la race alla radice. Contro (avvertenza giudice S352): fa esplodere il bundling per il modello desktop PMI (PBX nell'installer, porte/config su macchine eterogenee). Ha senso pieno solo se si valuta centralizzazione multi-tenant.
- **NON come fix: 2° account VivaVox** — darebbe FALSO VERDE (timing rete maschera il bug). Solo per stress-test DOPO un fix vero.

## PROMPT PER GIUDICE CLAUDE AI (consegnare a Luke)
"pjsip 2.16-dev su macOS 12, Python pjsua2 SWIG. Confinement applicato: il media callback `onCallMediaState` fa SOLO enqueue dell'indice media; `ensure_port`(createPort)/`getAudioMedia`/`startTransmit` eseguiti sul thread del loop `libHandleEvents` (che possiede il group lock). Nonostante ciò SIGABRT `lock.c:279` (`grp_lock_unset_owner_thread`) su thread `clock`: stack `clock_callback → get_frame → grp_lock_release → __assert_rtn`. Crashano SIA il processo Sara SIA l'harness chiamante, stack identico. Interpretazione: pjmedia 2.16-dev accoda le conference op su una op-queue drenata dal CLOCK THREAD del bridge, che non possiede il group lock. Domande: (1) È corretta questa lettura? (2) pjproject 2.15.1 esegue le conf op (`add port`/`connect`) SINCRONAMENTE sul thread chiamante (owner del lock), eliminando il clock-drain? Cita il codice/changelog pjmedia conf bridge tra 2.15.1 e 2.16-dev. (3) Se 2.15.1 NON risolve, qual è il fix minimo non-Python che lo fa senza passare a un PBX esterno?"

## DOPO IL FIX (gate verde)
VERIFICA E2E: harness `voice-agent/scripts/sara_audio_harness.py` (già patchato confinement S354), WAV PCM16 8kHz mono `/tmp/book.wav`. DONE = Sara risponde PERTINENTE via audio reale, NESSUN SIGABRT su NESSUN pid, RTP scambiato, `S243 T1: Audio bridge established`, zero `lock.c:279`/`re-registering` (REGOLA #24).

## STATO CODICE / FILE (NON ri-derivare)
- `voip_pjsua2.py` su iMac: confinement S354 IN PLACE = base corretta architettonicamente, TIENILA. Backup `voip_pjsua2.py.bak-PRE-S354-20260608-111954` (58322B). Repo locale MacBook divergente (S352-guard), va allineato/committato DOPO il fix scelto.
- `sara_audio_harness.py` su iMac: patchato confinement (enqueue-only + `drain_bridge`). Backup `.bak-PRE-S354-20260608-112257` (17749B).
- Pre-flight S354: `reg_status:200`, account `0972536918`@`sip.vivavox.it`, EHIWEB UP.

## CONTESTO PRODOTTO
EHIWEB/VivaVox = carrier su cui OGNI futuro cliente FLUXION ospiterà Sara. Il path inbound-answer+media DEVE essere crash-proof su scala. Gate vendita REGOLA #21.

## Carry residui (dopo gate Sara)
- **R2**: CI `release-full.yml` ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm). Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 sk_live (Stripe live key).
