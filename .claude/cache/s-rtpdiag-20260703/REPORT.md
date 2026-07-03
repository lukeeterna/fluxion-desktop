# REPORT SESSIONE — T-SARA-AUTOCALL: diagnosi gap RTP (2026-07-03)

## Obiettivo
Chiudere il gap RTP che blocca S2-S5: in S1 la call connette ma Sara non processa turni
(`/api/metrics/latency count=0`, `sara_heard=false`, 0 booking). Autonomia, zero-code,
nessuna modifica a Sara/DB/repo iMac.

## Pre-flight (live, read-only)
- `:3002/health` = 200 · SIP **registered reg_status:200** (`0972536918`, sip.vivavox.it) · `rtp_active:false`
- **Sara PID 54563 stabile** (== baseline) · bridge `:3001` = 200
- `/api/metrics/latency` = `count:0` · voice bookings baseline = **3**

## Finding statico (ribalta lo smoke della sessione precedente)
- Sara suona un **SALUTO all'answer**: `voip_pjsua2.py:1074` (`target=self._send_greeting`) → `_send_greeting:1298` → `queue_tts_audio`.
- ⇒ gli "11.64s di risposta Sara" dello smoke (STEP 1) erano **con ogni probabilità il saluto, NON una risposta** all'harness. Lo smoke provava solo "Sara risponde e saluta", mai "Sara sente l'harness".
- Formati port **identici** L16 8k/mono: Sara `voip_pjsua2.py:258` == harness `sara_audio_harness.py:199` (`fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)`).

## Test live decisivo (delayed-speech, direct-INVITE 127.0.0.1:5080, guardia `perl alarm`)
WAV nostro = 13s silenzio + parlato ("prenotare un taglio giovedì") → il parlato arriva DOPO il
saluto ⇒ **falsifica l'ipotesi collisione-saluto**.

| Misura | Valore | Significato |
|---|---|---|
| TX nostro `TX_our_speech_padded.wav` | peak=22257, rms=2981 | audio SANO, >> soglia VAD 600 |
| RX da Sara `RX_sara_capture_SILENCE.wav` | 26.7s, **peak=0, rms=0** | **SILENZIO PURO** — Sara non ha trasmesso NULLA |
| `/api/metrics/latency count` (post) | **0** | Sara non ha processato alcun turno (anche col ritardo) |
| Sara PID | 54563 invariato | NO SIGABRT (NDEBUG regge) |
| SDP harness | offre `speex/16000` (pt 96) | port L16 8k → pjsua2 transcodifica |

## Root cause localizzata
Il gap **NON è**: (a) transport RTP (i frame fluiscono: harness riceve 26.7s di frame) ·
codec · collisione turno-1/saluto (ritardo → stesso `count=0`).

**È che la port audio di Sara (`SaraAudioPort ↔ call-audio`) NON viene wired sul conference-bridge
nel direct-INVITE.** Se lo fosse, `onFrameRequested` di Sara verrebbe pompato e il saluto già in coda
fluirebbe → l'harness lo catturerebbe (invece = zeri) → e specularmente `onFrameReceived` di Sara non
riceve → `rx_queue` vuota → VAD mai → `count=0`, `sara_heard=false`, call dropped.

Sospetto: lato Sara `onCallMediaState`/`drain_pending_bridges` (`voip_pjsua2.py:435-648`) — media non
raggiunge `PJSUA_CALL_MEDIA_ACTIVE`, o il bridge differito (S243) non drena su questo path, a differenza
dell'inbound-provider autenticato S244 (che wired-ava il media).

## Non verificato (limite budget context)
Dove scrive `logger.info` di Sara: `/tmp/sara_tsaraA_181742.log` (fd1w) e `/tmp/sara-pjsip-s244.log`
(fd2w) contengono solo pjsip-trace + apscheduler, NON "Audio processing loop started"/greeting/VAD.

## Prossima direttiva (in HANDOFF.md, sezione RESUME)
1. Trovare la sink del logger di Sara (`main.py`/config) → leggere il path `onCallMediaState`→`drain_pending_bridges`.
2. Confronto col path S244 (trunk, che wired-ava media): SDP speex/16000 vs G729? media index? SRTP? routing INVITE IP-to-IP a `SaraAccount`?
3. Fix mirato; criterio sblocco S2-S5 = 1 call con `latency count>0` E cattura `rms>0`. `logger.info` diagnostico in `onCallMediaState` ammesso a context basso (`voip_pjsua2.py` quasi-critico).
4. Escalation (#1c) se il wiring non si attiva sul direct-INVITE → passare al trunk EHIWEB (path S244), 2° account SIP.

## Artefatti durevoli (questa cartella)
- `TX_our_speech_padded.wav` — nostro TX (audio sano)
- `RX_sara_capture_SILENCE.wav` — cattura da Sara (silenzio puro = prova)
- `harness_evidence.txt` — righe SDP/media decisive dal log harness iMac

## Stato lasciato
Sara UP iMac pid 54563 reg 200 · DB non toccato (voice bookings 3) · nessun edit codice/commit al codice · nessun crash.
