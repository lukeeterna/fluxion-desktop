# REPORT — T-SARA-MEDIASWAP-GO · GATE 2 LIVE · 2026-07-08

## VERDETTO: 🔴 ROSSO — etichetta **TTS-TX** (egress audio verso il chiamante)
Chiamata reale del founder al `0972536918` con `VOICE_ENGINE=go`: Sara **risponde, sente e
trascrive** (RX ok) ma il chiamante sente **MUTO** (TX ok a livello di coda, nessun frame RTP
in uscita). Done-condition 5/5 NON raggiunta. Una sola iterazione diagnostica (#1c) → STOP →
tavolo giudice. Motore ripristinato al default `pjsua2`.

## SCORECARD (voce per voce, con prova)
1. **Greeting + disclosure udito** — 🔴 NON udito (TX muta). NB: la disclosure È nel codice
   deployato e verificata (`grep 'assistente virtuale'` = session_manager.py:3 righe,
   orchestrator.py:1) — semplicemente non è stata pronunciata udibilmente perché la TX è muta.
2. **Risposta nel merito** — 🔴 impossibile da valutare (TX muta).
3. **count `/api/metrics/latency` AUMENTA** — 🟢 **VERDE**: baseline PRE-CALL **4** → POST **11**
   (+7). Il wiring metrica di GATE 1 ha funzionato **su chiamata reale**: la pipeline RX ha
   processato 7 turni live (STT+NLU, provider groq ~160ms). Prova che RX + metrica sono reali.
4. **Barge-in ~0.5s** — ⚪ non testabile (nessun audio in uscita da coprire).
5. **Sara stabile pre/post** — 🟢 durante le 2 call il processo Go NON è crashato (nessun
   `.ips`, RX gestita); ⚠️ ma lo shutdown ha rivelato un leak (vedi DIFETTO B).

## PROVA GREZZA (log call durevole)
Copia: `/Volumes/MacSSD - Dati/fluxion/call_gate2_20260708.log` (iMac; `/tmp/sara.log` troncato dal restore).
Sequenza reale (2 chiamate, 16:57:48 e 16:58:21):
```
INBOUND INVITE from=79.98.45.133:5060 → ANSWERED → MEDIA negoziato payloadType=8 codec=PCMA
→ CALL_START emesso (media attivo) → [voip_goengine] CALL_START
→ [A2] Greeting pre-synthesis done 'Salone Demo FLUXION' → [voip_goengine] greeting in coda TX
→ (chiamante: MUTO)
→ RX: STT+NLU processano la voce del founder ('...', intent groq conf 0.80-1.00, ms ~160)
→ CALL_END
```
- `grep -niE 'audio_tx|tx_queue|drena|ratecv|level=.*(tx|rtp|send|write)'` = **zero righe**: la coda
  TX si riempie ma nessun frame risulta drenato/emesso verso RTP.

## ROOT-CAUSE CIRCOSCRITTA (una iterazione #1c)
Asimmetria netta del bridge mediaswap:
- **Bridge RX** (engine→Python AUDIO_RX→STT): **FUNZIONA** (count 4→11 lo prova).
- **Bridge TX** (Python `queue_tts_audio`→AUDIO_TX→engine→RTP-out): **NON DELIVERA**.
Perché il gospike sembrava verde e qui no: il gospike S368 (CGNAT, WAV 595KB, eco udita) provò la
**TX RTP in echo-loopback INTERNO al motore Go**, mai alimentata dal bridge Python. GATE 1 catturò
254 frame TX **in-process** (cattura al bridge, non egress RTP reale). → la superficie **egress TX
alimentata dal bridge** è NUOVA e mai testata live. Il collo è lì, NON nel SIP/media del motore.

## DIFETTI PER IL GIUDICE (2)
- **A — TTS-TX egress (bloccante GATE 2)**: greeting sintetizzato e messo `in coda TX` ma il
  chiamante sente muto; nessun AUDIO_TX/RTP-out nei log. Candidati: (a) il thread che drena
  `queue_tts_audio`→AUDIO_TX non gira / non invia; (b) l'engine riceve AUDIO_TX ma non li impagina
  in RTP; (c) RTP-TX indirizzato male (latching simmetrico non applicato in uscita). Diagnosi
  successiva: log esplicito lato adapter (frame drenati) + lato engine (frame RTP scritti + remote addr).
- **B — Leak processo engine su shutdown (bloccò il restore)**: killando il parent Python (57907)
  il binario spawnato `engine_darwin_amd64` è rimasto **orfano** (PID 58004, PPID 1), tenendo UDP
  `192.168.1.2:5080` + la registrazione sul trunk → pjsua2 NON riusciva a ri-registrarsi
  (`reg_status:0` per >70s). Fix: l'adapter deve terminare l'engine su shutdown (signal propagation /
  process-group kill / de-REGISTER pulito). Bonificato a mano (kill 58004) → pjsua2 `reg_status:200`.

## EDIT DISCLOSURE (VERDE, decisione founder = prodotto, NON adattamento al test)
Motivazione founder: differenziatore etico + EU AI Act art.50 (dal 2 agosto 2026). Sara nel piano
€497 = trial 30 giorni. Due edit, entrambi #1d (backup verificato prima):
- `session_manager.py:740/:743` — greeting: `"{business}, {saluto}! Sono Sara, l'assistente virtuale. Come posso aiutarla?"`
- `orchestrator.py:3543` — regola conversazione sostituita: «Sei Sara, un'assistente virtuale. Se ti
  chiedono se sei una persona vera o un robot, confermi con naturalezza di essere un'assistente
  virtuale e prosegui ad aiutare. Non ti fingi mai umana.» (rimossa «MAI dire IA — sei una persona»).
- Deploy iMac verificato (md5 MacBook==iMac). Backup: `src/{session_manager,orchestrator}.py.bak-PRE-DISCLOSURE-20260708-164136`.
- Non udibile in questa call causa TX muta; la coerenza in conversazione ("sei una persona vera?")
  entra nelle conferme d'orecchio del prossimo test quando la TX sarà riparata.

## STATO FINALE (coerente, DICHIARATO)
Sara ripristinata al **default `pjsua2`**: PID **59182**, health **200**, `engine:"pjsua2"`,
`registered:true`, `reg_status:200`, `rtp_active:false`. Engine orfano bonificato. DB `appuntamenti`=0,
`fonte='voce'`=0 (invariato: TX muta = nessuna prenotazione). `/api/metrics/latency` count=11
(4 baseline + 7 turni RX reali). Motore Go resta a disco come fallback flaggato (`VOICE_ENGINE=go`).

## PROSSIMO
Tavolo giudice sul DIFETTO A (egress TX bridge). Fix candidato + diagnosi (log adapter+engine sui
frame TX/RTP), poi ripetere GATE 2 con la stessa done-condition 5/5 (RX e metrica già provate verdi).
Includere nel fix il DIFETTO B (kill engine su shutdown). Restore invariato:
`ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && kill <pid>; sleep 1; nohup /usr/bin/python3 main.py --port 3002 >/tmp/sara.log 2>&1 &"`.
