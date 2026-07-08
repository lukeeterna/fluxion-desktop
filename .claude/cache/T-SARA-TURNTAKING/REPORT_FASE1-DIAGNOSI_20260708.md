# REPORT T-SARA-TURNTAKING — FASE 1 (DIAGNOSI ECO) + spec FASE 2/3/4

Data: 2026-07-08 · Gate label (#1c): **GATING/diagnosi eco** · Verdetto: 🟢 DIAGNOSI CHIUSA (read-only) · Mutazioni: **ZERO**

## 1. VERDETTO FASE 1 — nessun self-loop software; eco = leg reale (trunk PCMA)
Prova (read-only, `voice-agent/engine/main.go`):
- `main.go:271` — RX di produzione = solo `RTP(G.711)→PCM16 → AUDIO_RX` letto dal socket RTP reale.
- `main.go:352-392` — TX (`txBuf`/`pushTX`/`popTX`) scrive verso RTP-out, cap `txCapFrames=10` (200ms). Nessuna copia TX→RX.
- `main.go:74,523,539,556` — l'UNICO punto che ri-emette gli `AUDIO_TX` come `AUDIO_RX` (echo) è sotto flag `-selftest` (`fSelftest`), **mai attivo in chiamata reale**.
- CONCLUSIONE: in chiamata vera l'engine NON fonde TX→RX. La spazzatura STT del GATE B (`'Vessamiteevi, buonaseraamigliorea'`, log `sara_gateB_20260708.log:391-394`, con frammenti del greeting di Sara) proviene da **eco acustica/hairpin del leg telefonico PCMA**, non dal software.
- IMPLICAZIONE: il fix è **gating half-duplex + grace period nell'adapter** (`voip_goengine.py`), come da mandato FASE 2. Nessun rebuild engine necessario per l'eco. Coerente col divieto AEC.
- NB: l'echo-probe live (harness→engine silenzio-durante-greeting) resta il conferma-empirico; la diagnosi statica è già decisiva sul punto "dove va il fix". Eseguire l'echo-probe in FASE 3 come primo scenario dell'harness esteso.

## 2. DISCORDANZE (contratto)
- **DISCORDANZA #1** | premessa mandato «POLICY FILLER (prosody_injector.py:96 e banco frasi)» | fatto: `prosody_injector.py` NON contiene banco filler né cortesia — è solo iniezione pause/virgole/ellissi; riga 96 = `_add_thinking_pause`. | correzione (vince il disco): banco filler reale = `orchestrator.py:462-464` `["Un momento...", "Vediamo...", "Un attimo che controllo..."]`; cortesia escalation operatore = `orchestrator.py:294` `"...un attimo..."`. FASE 2.4 va applicata lì, non in prosody_injector.
- **DISCORDANZA #2 (host)** | premessa vari `.claude/rules` citano `192.168.1.12` | fatto: iMac reale = `192.168.1.2` (ssh alias `imac`, user `gianlucadistasi`), health 3002 ok da localhost iMac; da MacBook curl diretto a `192.168.1.2:3002` NON risponde (usare tunnel/ssh, non curl LAN). Pipeline live PID **69142** pjsua2.

## 3. STATO ADATTATORE (diagnosi statica del difetto, `voip_goengine.py`)
- `sara_speaking` (riga 594) = `(not _tx_queue.empty()) or _current_tx_rms>0`. **Difetti**:
  1. **Nessuna grace period** dopo fine TX: l'engine emette ancora audio Sara su RTP fino a 200ms dopo che la coda Python è vuota → la sua eco rientra su RX mentre Python crede che Sara abbia smesso → STT su audio sporco.
  2. `_current_tx_rms` NON viene azzerato quando la coda si svuota (solo in `clear_tx`) → stato-turno implicito e fragile, dipende dal barge-in per resettarsi.
  3. Barge-in a soglia FISSA (`BARGE_IN_MARGIN=500`, `ECHO_ATTENUATION=0.5`), non adattiva all'eco reale misurata.
  4. Sul barge-in (riga 603-607) si estende `speech` col SOLO frame-trigger: le prime ~250-300ms dell'utente (pre-soglia) si perdono.

## 4. SPEC ESECUTIVA FASE 2 (mutazioni, #1d su ogni file) — per sessione fresca
Applicare su iMac `/Volumes/MacSSD - Dati/fluxion/voice-agent` (codice live) + mirror git MacBook.
- **2.1 Stato-turno esplicito** in `voip_goengine.py`: enum/flag `SPEAKING|LISTENING` unica autorità. SPEAKING sse (TX in corso O `_tx_queue` non vuota). In SPEAKING: RX NON entra in `rx_queue`→STT (già `continue` a 608/611) MA aggiungere **grace ~150-200ms** dopo l'ultimo frame TX prima di riaprire RX→STT. Azzerare `_current_tx_rms=0` quando la coda si svuota nel `_tx_pump` idle-branch (riga 547-554).
- **2.2 Barge-in adattivo**: `echo_floor` = RMS medio della RX misurato DURANTE TX (media mobile); trigger = `rms > max(soglia_base, k·echo_floor)` sostenuto ≥250-300ms (≥13-15 frame). Sul trigger: `clear_tx()` + stop invio + **inoltra a STT il buffer dei ~300ms di trigger** (ring-buffer degli ultimi N frame RX, non solo il frame corrente) + stato→LISTENING.
- **2.3 FSM-HANGUP GUARD** (`booking_state_machine.py`): dal log GATE B il path è `[S142] Bare name in IDLE` su garbage → avanzamento → `HANGUP ricevuto da Python`. Hangup lecito SOLO su intento congedo esplicito o timeout silenzio. Confusione/bassa confidenza → reprompt "scusi, non ho capito, può ripetere?" max 2, poi offerta richiamo umano. Edit minimo, non refactor. (Verificare dove nasce il `should_exit` che innesca `_hangup_after_drain`, `voip_goengine.py:650-652`.)
- **2.4 Policy filler** (`orchestrator.py:462-464` + `:294`): (a) separare FILLER (vuoti) da CORTESIA ("grazie"/"prego"); (b) filler SOLO dopo turno utente completato E latenza attesa >~1s, max 1/turno, mai in SPEAKING utente, mai su silenzio, rotazione; (c) grazie/prego condizionati allo stato FSM (grazie←dato ricevuto; prego←grazie ricevuto); (d) verificare soglia fine-turno VAD ≥600ms — attuale `VAD_SILENCE_TIMEOUT=50` frame ×20ms = 1000ms (già ≥600ms, OK; annotare).

## 5. SPEC FASE 3 — GATE A3 (autonomo, il test che resta)
Estendere harness `voice-agent/tools/gospike/uac.go` con `-echo <dB>` (mix del ricevuto attenuato ~-15dB nel proprio TX) + iniezione utterance a T sopra il parlato di Sara. Scenario = GATE B in laboratorio → **committare come regressione permanente**. Done-condition A3(1-4): STT senza frammenti Sara; barge-in scatta sull'utterance vera (TX flush + log + prime parole NON perse); filler solo secondo policy; Sara non riaggancia mai per prima. Prova = WAV+trascrizioni+contatori committati in `.claude/cache/T-SARA-TURNTAKING/calls/<ts>_A3/` (rx.wav, tx.wav, mix.wav stereo, transcript.md). ADDENDUM W: cattura sotto flag `SARA_TEST_CAPTURE=1` (default OFF, verificare a fine sessione).

## 6. SPEC FASE 4 — GATE B3 (founder, una chiamata, solo su VERDE-A3, context ≤50%)
Switch `VOICE_ENGINE=go` + verifica tripla (health / engine:"go" reg 200 / no doppia REGISTER) → founder chiama `0972536918`: greeting+disclosure; prenotazione; parlarle sopra a metà; "sei una persona vera?"; UNA pausa lunga (Sara non la riempie né riaggancia); riaggancia il founder. Scorecard 5/5 ereditata + 2 orecchie (grazie/prego solo naturali; mai riagganciato lei). Cattura WAV mix per giudice (REGOLA #32). VERDE→go DEFAULT (#1d config) + soak; ROSSO→ripristino pjsua2 + etichetta + STOP.

## 7. STATO LASCIATO
- Sessione **read-only + diagnosi**: ZERO mutazioni al codice. Sara **default pjsua2 PID 69142**, health ok, `reg_status:200` (invariato dal boot). Nessun restore necessario.
- Backup #1d HANDOFF: `HANDOFF.md.bak-PRE-TURNTAKING-20260708-185353` (57829B).
- Chiusura anticipata guidata dal gate budget VOS (vincolo #7, %RAW possibilmente gonfiata per REGOLA #27 ma senza contro-misura questo turno). GATE B3 richiede comunque founder → nessuna perdita: la sessione fresca parte da qui con headroom pieno ed esegue FASE 2→3→4.
