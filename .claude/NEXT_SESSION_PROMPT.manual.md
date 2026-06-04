# FLUXION — S338 resume — Sara Layer 2 audio. **S337 DOWNGRADE 2.15.1 FATTO ma NON RISOLVE. Ipotesi versione FALSIFICATA.**

> ## >>> PRIMA AZIONE S338 (REGOLA #1c, OBBLIGATORIA): NON tentare un 3° fix autonomo. Incollare a Claude.ai il prompt giudice `.claude/cache/agents/s337/claude-ai-prompt-s337.md`, salvare il verdetto in `.claude/cache/agents/s337/claude-ai-response.md`, e SOLO POI eseguire l'opzione scelta. <<<
> ## Il prompt giudice include la META-DOMANDA chiave: le chiamate provider REALI (S244) funzionavano, solo il loopback artificiale crasha → forse il gate corretto è "chiamata reale via provider dopo fix 403", non far funzionare il loopback. Il giudice decide questo PER PRIMO.

> ## >>> S337 ESITO (2026-06-04, voice-engineer): pjsip downgrade 2.16-dev → 2.15.1 ESEGUITO e VERIFICATO (`libVersion().full == 2.15.1`, build da sorgente iMac, SWIG 4.4.1, static x86_64 Big Sur, installato in `lib/pjsua2/`). **MA Sara CRASHA ANCORA identico sull'INVITE loopback** (SARA_DEAD, mai 200 OK, harness solo `100 Trying`→timeout). **2.15.1 HA LA STESSA op-queue asincrona di 2.16-dev** — log Sara mostra ancora `conference.c onCallMediaS "Add port N queued"` + `possibly re-registering existing thread`. **L'ipotesi "2.15.1 è sincrona" era SBAGLIATA.** <<<
> ## ROOT CAUSE REALE (rivista): STRUTTURALE, non version-specific. Sara fa port-add conference da thread `onCallMediaState`; group-lock unset su `_pjsua2_thread` in `libHandleEvents` → mismatch owner → abort. Il downgrade non tocca questo.
> ## NEXT S338 (decisione architetturale founder/main, NO 3° fix Python — REGOLA #1c): opzione (1) forzare port-add nel contesto del thread pjsua worker (`libRegisterThread`/eseguire add dentro l'event thread così l'owner del group-lock combacia); opzione (2) ESCALATION Asterisk ARI (N5 dossier) come layer SIP/media, Sara solo cervello — elimina la conference bridge pjsua2. Dettaglio completo: `.claude/agent-memory/voice-engineer/project_sip_loopback_crash_pjsip216.md` (sezione S337 UPDATE).
> ## Stato lib iMac: pjsua2 2.15.1 installato in `lib/pjsua2/`; backup 2.16-dev = `lib/pjsua2.backup-PRE-S337-20260604-125255/` (22MB, restore point). Nessun motivo di revertire (nessuna delle 2 versioni funziona per loopback). Sara pipeline DOWN dopo l'ultimo crash harness — riavviarla all'inizio S338.

> --- HANDOFF S337 ORIGINALE (parzialmente superato) ---
# FLUXION — S337 resume — Sara Layer 2 audio. **ROOT CAUSE TROVATA: pjsip 2.16-dev. NEXT = downgrade pjsip 2.15.1.**

> Scritto 2026-06-03 a chiusura S336. **FINDING DECISIVO**: l'INVITE SIP diretto P2P all'iMac FUNZIONA (gate sbloccato lato routing), ma la pipeline Sara **crasha** processando l'INVITE per un bug di **pjsip 2.16-dev** (op-queue / group-lock owner-thread sul commit della conference port). Il crash NON è chiudibile lato Python. **Unica via: downgrade pjsip → 2.15.1** (conference sincrona, niente op-queue). Gate Sara Layer 2 NON raggiunto = handoff strutturato, non verde.

> ## >>> PRIMA AZIONE S337: downgrade pjsip 2.16-dev → 2.15.1 sull'iMac, poi ri-run harness. <<<
> Delegare a voice-engineer (REGOLA #25, foreground per SSH/Bash). Runbook = "S244 path B1". Dopo il downgrade: ri-lanciare `voice-agent/scripts/sara_audio_harness.py` con INVITE diretto e validare il flusso audio E2E. Memory dettagliata dell'agent: `.claude/agent-memory/voice-engineer/project_sip_loopback_crash_pjsip216.md`.

## STATO — cosa è SOLIDO (non rifare)
- ✅ **INVITE diretto FUNZIONA** (chiude TODO[SIP-LIVE] ~36/~345). URI vincente: `sip:0972536918@127.0.0.1:5080` (harness su `127.0.0.1:5070`). Sara risponde `100 Trying` + `Answering call 0: code=200`, codec speex negoziato, bridge `sara_bridge` creato. La registrazione EHIWEB 403 è IRRILEVANTE per il test loopback (confermato).
- ✅ Harness `voice-agent/scripts/sara_audio_harness.py` (committato 196b491) = CORRETTO, non modificarlo. WAV TX gen OK (PCM16 8kHz mono, ricetta `say -o raw.aiff` + `afconvert -f WAVE -d LEI16@8000 -c 1`).
- ✅ Layer 1 testo VERDE (S333: 50 OK / 3 WARN / 0 FAIL su 12 verticali) — path HTTP `/api/voice/process`, NON tocca SIP, NON impattato dal bug.

## ROOT CAUSE (pjsip 2.16-dev) — diagnosi S336 completa
- Crash via `faulthandler`: `Fatal Python error: Aborted (SIGABRT)` nel thread `_pjsua2_thread` dentro `libHandleEvents` (`voip_pjsua2.py:806`), preceduto da pjsip C-log `conference.c onCallMediaS "Add port N queued"` + `os_core_unix.c "possibly re-registering existing thread"`. È l'assertion `grp_lock_unset_owner_thread` (lock.c): owner del group-lock settato dal thread di callback `onCallMediaState`, unset da `_pjsua2_thread`.
- pjsip attivo = **2.16-dev** (`libVersion` verificato). L'INVITE loopback dispatcha `onCallMediaState` su un media-thread dedicato → espone la race che le chiamate provider (S244) evitavano per timing.
- **Fix S243 esistente** (deferiva `startTransmit` nel drainer `drain_pending_bridges`) = INSUFFICIENTE: lasciava `createPort` dentro `onCallMediaState`.
- **Fix S335 tentato** (deferiva ANCHE la port creation `ensure_port`+`getAudioMedia` nel drainer): ha solo SPOSTATO il crash da `Add port 2 (sara_bridge)` → `Add port 1` (conference-port della call-leg, creata INTERNAMENTE da pjsip durante `answer()`, fuori dal controllo Python). **Conclusione: il bug op-queue 2.16-dev colpisce porte che non gestiamo → NON chiudibile lato Python.**

## S337 — PIANO (CTO, REGOLA #15)
1. **Downgrade pjsip 2.16-dev → 2.15.1** (iMac, runbook S244 path B1). NB: 2.15.1 ha conference API SINCRONA (`Conf add port N` immediato, niente op-queue) → niente owner-thread mismatch. Verificare che il path chiamate provider (S244) resti funzionante. Delegare a voice-engineer.
   - NON usare il backup `lib/pjsua2.backup-2.16dev-20260515` (è ancora 2.16-dev, stesso bug). Serve build/lib 2.15.1 reale.
2. **Ri-run harness** con INVITE diretto `sip:0972536918@127.0.0.1:5080`, WAV "Buongiorno, vorrei prenotare un appuntamento" → Sara NON crasha → 200 OK trasmesso → bridge attivo → cattura risposta RTP di Sara su WAV (durata >0) → trascrivi (whisper.cpp/Groq) → verifica Sara ha CAPITO+risposto pertinente. Chiude TODO[SIP-LIVE] ~273 (bridge wiring) e ~374 (cattura RTP).
3. **Estendere a golden-path per verticale via audio** (REGOLA #21: "soddisfa pienamente il cliente"). Scenari STT-sensitivi via audio; il resto già VERDE Layer 1 testo.

## STATO iMac (per ripartenza pulita)
- Branch iMac = `fix/license-interop-r01-s327` (preesistente da R-01, NON master). Tree pulito.
- **Fix S335 STASHATO** (recuperabile): `git stash list` → `stash@{0}` "s335-sip-loopback-fix-pjsip216-deferred-port". Backup pre-fix: `/tmp/voip_pjsua2.py.bak-s335-1780518361` (volatile, /tmp). **Probabilmente reso SUPERFLUO dal downgrade 2.15.1** (niente op-queue → niente deferral necessario). Recuperare solo se 2.15.1 mostrasse ancora una race.
- Pipeline Sara: UP+healthy (era PID 3410; il processo in memoria aveva il fix S335 caricato, il disco è ora a HEAD post-stash — il downgrade comporterà comunque restart, stato si normalizza).

## BLOCKED-ON (Luke/esterno, NON blocca gate Sara Layer 2)
- EHIWEB reset binding SIP (`reg_status:403` persistente): serve SOLO per chiamate clienti reali in prod, NON per il test CTO-guidato loopback. Ri-escalation operatore: reset garantito non ha funzionato; verificare reset propagato + IP whitelist (IP pubblico iMac `151.72.9.90`) + account/credito; se password rigenerata → aggiornare `voice-agent/.env` VOIP_SIP_PASS.
- Custom domain `fluxion-app.com`: NS su CF, no record A → attaccare a worker prod per go-live brandizzato.
- Rami client-side license tsc-only (offline grace/clock-rollback/banner): GUI iMac Keychain (REGOLA #12).
