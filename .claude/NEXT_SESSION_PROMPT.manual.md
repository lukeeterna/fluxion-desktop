# FLUXION — S336 resume — Sara Layer 2 audio. SCAFFOLD harness PRONTO. **SBLOCCO: INVITE diretto bypassa EHIWEB.**

> Scritto 2026-06-03 a chiusura S335. **FINDING CHIAVE**: l'harness audio può testare Sara via **INVITE SIP DIRETTO all'iMac** (peer-to-peer, porta 5080), **SENZA aspettare EHIWEB** (la registrazione 403 NON impedisce di ricevere un INVITE diretto). Il gate Sara Layer 2 è quindi sbloccabile SUBITO. Lo scaffold è scritto e validato (import/argparse), resta il live-run.

> ## >>> PRIMA AZIONE S336: live-run dell'harness con INVITE diretto. NON serve EHIWEB. <<<
> `ssh imac` → lanciare `voice-agent/scripts/sara_audio_harness.py` contro `sip:0972536918@<IP_iMac>:5080` con un WAV di test (PCM16 8kHz mono). Verificare i 4 `# TODO[SIP-LIVE]` (makeCall, instradamento INVITE IP-diretto, bridge wiring `onCallMediaState`, cattura RTP-in). Se l'INVITE diretto dà 404 → fallback: outbound proxy = IP iMac. Delegare il live-run + debug a voice-engineer (context isolato, REGOLA #25).

## STATO SIP / EHIWEB (NON più bloccante per il test audio)
- Pre-flight S335: `reg_status:403` PERSISTE anche dopo **restart pulito + fresh-register** (PID 99654, cseq=57505, 21:52:57 → `403 Forbidden` reale, non cache). Il reset binding che EHIWEB ha "garantito immediato" NON ha avuto effetto.
- **Ri-escalation EHIWEB pendente (azione Luke)**: dire all'operatore: *"Restart pulito → REGISTER fresco → ancora 403 sul peer 0972536918 (dopo 401+digest corretto). Il reset garantito immediato NON ha funzionato. Verificate: (a) reset realmente eseguito+propagato; (b) IP whitelist — IP pubblico attuale iMac `151.72.9.90`; (c) account/credito. Se rigenerate la password, datemela → aggiorno `voice-agent/.env` VOIP_SIP_PASS."*
- **MA**: il test audio Layer 2 NON dipende più da questo (vedi INVITE diretto sotto). La registrazione al provider serve solo per ricevere chiamate REALI dai clienti in produzione, non per il test CTO-guidato.

## S335 — COSA HO FATTO
### 1. Confermato SIP ancora 403 (restart pulito, non era cache)
Via voice-engineer: kill PID 69944 → restart pulito (PID 99654) → un solo fresh-register → server risponde `403 Forbidden` su cseq fresco. Falsificata l'ipotesi "403 vecchio in cache". Health Sara OK (v2.1.0). Root cause resta esterna EHIWEB (coerente S334).

### 2. FINDING: harness bypassa EHIWEB con INVITE diretto (via voice-engineer research)
- **Il runtime usa `src/voip_pjsua2.py` (pjsua2), NON `src/voip.py`** (quest'ultimo è client custom legacy NON usato — `main.py:1324` importa da `voip_pjsua2`). L'analisi S334 che citava `voip.py:1126/1438` era sul file sbagliato.
- **VERDETTO INVITE diretto = SÌ**: (1) processo pipeline in ascolto su `UDP *:5080` (lsof, tutte le interfacce); (2) `SaraAccount.onIncomingCall` (`voip_pjsua2.py:536`) accetta l'INVITE **senza gate sulla registrazione** (unico check: già-in-chiamata → 486 Busy, `:542-547`). Un INVITE `sip:0972536918@<IP_iMac>:5080` raggiunge Sara P2P senza toccare `sip.vivavox.it`.
- **Audio model pjsua2** (non `send_audio`): `SaraAudioPort.queue_tts_audio` (`:292`) parse WAV (`:303 wave.open` READ) → resample 8kHz (`:311 audioop.ratecv`) → chunk **320 byte = 20ms @ 8kHz mono 16bit** (`:313-320`) → tx_queue → `onFrameRequested` (`:265`). RTP-in: `onFrameReceived` (`:256`) → rx_queue → `get_caller_audio` (`:324`) → STT. Nessuna cattura su file dell'entrante (l'harness deve aggiungerla).

### 3. Scaffold creato (NON committato finché non leggi il diff — fatto in S335 commit)
- `voice-agent/scripts/sara_audio_harness.py` (407 righe). Endpoint pjsua2 separato (porta locale 5070), `HarnessAudioPort` (TX nostro WAV via `onFrameRequested` + cattura Sara via `onFrameReceived`→WAV), `HarnessCall.makeCall()` IP-diretto, `generate_wav_from_text()` ricetta S334 (`say -o raw.aiff` + `afconvert -f WAVE -d LEI16@8000 -c 1` → PCM16 8kHz mono).
- 4 `# TODO[SIP-LIVE]` (righe 36, 273, 345, 374): solo cose validabili con un run reale.
- **Verifiche offline OK**: pjsua2 importabile SOLO con `lib/pjsua2` su sys.path + interprete CommandLineTools 3.9 (NON bare python3/venv); porta SIP locale Sara = **5080**; WAV `afinfo` = `1 ch, 8000 Hz, Int16`; `--help` harness gira su iMac (subclass `pj.AudioMediaPort` reale OK).

## S336 — PIANO (CTO, REGOLA #15)
1. **Live-run harness con INVITE diretto** (sblocca il gate Sara SENZA EHIWEB). Delegare a voice-engineer: lanciare l'harness su iMac, INVITE a `sip:0972536918@<IP_iMac>:5080`, streammare un WAV "Buongiorno, vorrei prenotare", catturare la risposta RTP di Sara su WAV, trascriverla (whisper/groq) per verificare che Sara abbia capito+risposto. Debuggare i 4 TODO[SIP-LIVE]. Se 404 → fallback outbound proxy = iMac.
2. **Estendere a golden-path per verticale** (REGOLA #21: "soddisfa pienamente il cliente" su tutti). Gli scenari STT-sensitivi via audio; il resto Layer 1 testo già VERDE (S333, 50/3/0).
3. **In parallelo, indipendente da Luke**: EHIWEB resta utile per chiamate clienti reali in prod, ma NON blocca il gate vendita. Custom domain `fluxion-app.com` (~10 min) quando serve go-live brandizzato.

## BLOCKED-ON (Luke/esterno, NON blocca gate Sara)
- EHIWEB reset binding SIP (ri-escalation sopra) — serve solo per chiamate clienti reali in prod.
- Custom domain `fluxion-app.com`: NS su CF, no record A → attaccare a worker prod.
- Rami client-side license tsc-only (offline grace/clock-rollback/banner): GUI iMac Keychain (REGOLA #12).
