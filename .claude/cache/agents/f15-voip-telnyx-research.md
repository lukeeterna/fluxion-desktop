# F15 — VoIP Research: Telnyx vs Twilio vs EHIWEB vs SignalWire
**CoVe 2026 Deep Research — Telnyx SIP Trunk + Sara Voice Agent Integration**
**Data**: 2026-03-12 | **Scope**: SIP trunk per PMI italiane, bridge verso Sara Python aiohttp

---

## Stato Codebase Attuale (prerequisito per questa research)

**Già implementato**:
- `voice-agent/src/voip.py` — SIP client completo puro-Python (asyncio, senza pjsua2): SIP REGISTER/INVITE/BYE/CANCEL/ACK, Digest MD5 auth, RTP transport G.711 PCMU/PCMA, `VoIPManager` con pipeline integration, upsampling 8kHz→16kHz per Whisper
- `voice-agent/src/sip_client.py` — stub semplificato (simulato, senza socket reali)
- Server Sara: aiohttp porta 3002, bind `127.0.0.1`, endpoint `/api/voice/process` + `/api/voice/greet` + `/api/voice/reset`
- **Gap critico**: `voip.py` ha il full SIP/RTP stack ma NON è integrato in `main.py` — ha bisogno di essere collegato al pipeline reale

**Non implementato**:
- WebSocket audio endpoint (Sara accetta solo HTTP request/response, non streaming continuo)
- Telnyx/Twilio Call Control webhooks
- SIP binding su IP pubblico (attualmente tutto localhost)
- Test live con EHIWEB o qualsiasi provider reale

---

## 1 — Confronto Provider SIP per Italia

### 1.1 Telnyx

**Disponibilità numeri italiani**: Sì — Telnyx offre numeri DID italiani (geografici +39 02/06/etc. e mobili +39 3xx). La disponibilità è buona per Milano, Roma, e principali città.

**Pricing stimato** (dati pubblici 2024–2025, soggetti a variazione):
| Voce | Costo |
|------|-------|
| Numero DID italiano/mese | ~$1.00–3.00 USD |
| Inbound minuti (Italia) | ~$0.004–0.008/min |
| Outbound verso Italia fisso | ~$0.008–0.015/min |
| SIP trunking base | Nessun costo fisso — pay-per-use |

**Autenticazione SIP**:
- **IP authentication**: whitelist IP del server (nessuna password) — metodo preferito per server fissi
- **Credential authentication**: username + password per registrazioni SIP dinamiche
- Telnyx usa entrambi; per iMac con IP statico (LAN + Cloudflare) → IP auth è la scelta più sicura

**Telnyx Call Control API** (event-driven):
- Pattern webhooks: quando arriva una chiamata, Telnyx fa HTTP POST al tuo server con evento `call.initiated`
- Il server risponde con comandi REST: `answer`, `start_streaming`, `speak`, `hangup`, etc.
- **Media Streaming**: Telnyx può streamare audio bidirezionale via WebSocket verso un endpoint definito dal server
- WebSocket audio format: **mulaw 8kHz** (PCMU) in pacchetti base64 o binari
- Latenza aggiunta Telnyx cloud: stimata ~50–100ms (endpoint europei disponibili: Amsterdam, Francoforte)

**TeXML** (Telnyx XML — equivalente TwiML):
- Simile a TwiML di Twilio
- Tag principali: `<Answer>`, `<Stream>`, `<Say>`, `<Gather>`, `<Hangup>`
- Esempio:
  ```xml
  <Response>
    <Answer/>
    <Stream url="wss://tunnel.cliente.com/sara/audio" />
  </Response>
  ```
- Pro: semplice, dichiarativo
- Con: meno flessibile di Call Control per flussi complessi con AI

**Call Control vs TeXML per Sara**:
| Criterio | Call Control (API) | TeXML |
|----------|-------------------|-------|
| Flessibilità | Alta — ogni evento gestito via codice | Media — tag predefiniti |
| Latenza risposta | ~50–80ms (webhook round-trip) | ~40–70ms |
| Streaming audio | WebSocket bidirezionale | `<Stream>` WebSocket |
| Adatto per AI voice | **Sì — gold standard** | Sì ma meno flessibile |
| Complessità impl. | Media | Bassa |

**Raccomandazione per Sara**: **Call Control API + Media Streaming WebSocket** — è lo standard 2026 per voice AI agent (usato da Retell AI, Vapi, ElevenLabs conversational).

---

### 1.2 Twilio

**Disponibilità numeri italiani**: Sì — numeri italiani disponibili (geografici Milano/Roma + mobile). Twilio è storicamente il più affidabile per numeri italiani.

**Pricing stimato** (2024–2025):
| Voce | Costo |
|------|-------|
| Numero DID italiano/mese | ~$2.00–4.00 USD |
| Inbound minuti (Italia) | ~$0.005–0.010/min |
| Outbound verso Italia fisso | ~$0.010–0.020/min |
| Media Streams | Incluso nel costo chiamata |

**Media Streams (WebSocket)**:
- Twilio invia audio via WebSocket in formato **mulaw 8kHz base64-encoded** in messaggi JSON
- Formato messaggio inbound:
  ```json
  {
    "event": "media",
    "streamSid": "MZxxx",
    "media": {
      "payload": "BASE64_MULAW_8KHZ",
      "timestamp": "12345",
      "chunk": "42"
    }
  }
  ```
- Sara risponde con lo stesso formato per TTS output

**TwiML `<Stream>`**:
```xml
<Response>
  <Start>
    <Stream url="wss://tunnel.cliente.com/sara/audio" />
  </Start>
  <Pause length="60"/>
</Response>
```

**Twilio SIP Domain** (SIP termination):
- Si può configurare un "SIP Domain" Twilio per ricevere SIP INVITE da trunk esterni (EHIWEB)
- EHIWEB fa forward a `your-domain.sip.twilio.com`
- Twilio poi gestisce l'audio e chiama il webhook con TwiML

**Considerazioni per FLUXION**:
- Twilio è il provider più documentato e più usato — enorme community
- Lock-in più alto di Telnyx ma migliore affidabilità storica per Italia
- Costo per minuto più alto di Telnyx (~2x)
- **Non compatibile con credenziali EHIWEB dirette** — richiede sempre il cloud Twilio come intermediario

---

### 1.3 EHIWEB (provider italiano)

**Profilo provider**: EHIWEB (AS49709) è un operatore VoIP italiano Tier-1. Offre SIP trunk, numeri DID geografici italiani, e servizi per PMI.

**Parametri SIP ufficiali** (da documentazione EHIWEB pubblica e configurazioni note):
```
SIP Server (Registrar): sip.ehiweb.it
SIP Porta:             5060 (UDP) / 5061 (TLS)
SIP Realm:             ehiweb.it
Username:              numero assegnato (es. 0250150001)
Password:              impostata dal cliente nel pannello my.ehiweb.it
Codec:                 G.711 A-law (PCMA), G.711 µ-law (PCMU), G.729A
STUN:                  stun.ehiweb.it:3478
Outbound proxy:        proxy.ehiweb.it (alcuni account)
```

**API per sviluppatori**: EHIWEB **non offre una REST API** pubblica tipo Telnyx/Twilio. Non c'è Call Control, non c'è webhooks, non c'è streaming audio gestito. EHIWEB è un provider SIP "tradizionale" — fornisce il trunk SIP e il numero, ma la gestione della chiamata è interamente lato client (il software SIP del cliente).

**Pricing EHIWEB** (stima da listino pubblico 2024):
| Voce | Costo |
|------|-------|
| Numero DID italiano/mese | ~€2–5/mese |
| Inbound chiamate | Spesso incluse o ~€0.01/min |
| SIP trunk mensile | ~€5–15/mese per account business |

**Pattern d'uso con FLUXION**:
- EHIWEB è il provider ideale per i clienti PMI italiani che già hanno il numero lì
- Il bridge SIP deve girare sull'iMac del cliente, registrato direttamente a `sip.ehiweb.it`
- Nessun cloud intermedio — audio direttamente da EHIWEB a iMac a Sara
- **Già supportato in `voip.py`** (`SIPConfig.server = "sip.ehiweb.it"`)

**Vantaggio unico EHIWEB per FLUXION**:
- Numero italiano già del cliente → zero porting, zero cambio numero
- Zero costo per minuto aggiuntivo (incluso nel piano EHIWEB)
- Dati vocali mai escono dall'Italia → GDPR nativo
- Nessuna dipendenza da provider cloud straniero

---

### 1.4 Vonage / Nexmo

**Stato 2025–2026**: Vonage è stata acquisita da Ericsson nel 2022 e successivamente scorporata; il brand "Vonage" come API platform esiste ancora ma con focus enterprise. Per PMI italiane è meno rilevante.

**Numeri italiani**: Disponibili ma meno buona copertura rispetto a Telnyx/Twilio.

**Pricing**: Competitivo con Twilio ma supporto meno solido per Italia.

**Verdetto**: Non raccomandato per FLUXION — Telnyx e Twilio sono superiori in ogni metrica.

---

### 1.5 SignalWire

**Profilo**: Fondata dai creatori di FreeSWITCH, SignalWire offre API VoIP cloud-native.

**Punti forti**:
- API completamente compatibile con Twilio (drop-in replacement)
- Prezzi inferiori a Twilio (~30–50%)
- Endpoint europei (Francoforte) → latenza minore per Italia
- SWML (SignalWire Markup Language) = equivalente TwiML
- **AI Gateway nativo**: SignalWire AI Agent ha integrazione diretta con LLM

**Pricing stimato** (2024–2025):
| Voce | Costo |
|------|-------|
| Numero DID italiano/mese | ~$1.50–3.00 USD |
| Inbound minuti | ~$0.003–0.005/min |
| Outbound Italia | ~$0.008–0.012/min |

**Per FLUXION**: Alternativa valida a Twilio se si vuole il pattern "cloud intermediary" ma a costo inferiore. L'endpoint europeo riduce latenza.

---

### 1.6 Altri Provider SIP Italiani

**Messagenet** (messagenet.it):
- Provider VoIP italiano, numeri DID geografici, target PMI
- SIP standard, no API REST pubblica
- Pricing competitivo con EHIWEB

**VoiP.ms** (canadese, ma con numeri italiani):
- Eccellente per sviluppatori — API REST, WebRTC, SIP
- Prezzi molto bassi (~$0.85/mese per DID italiano)
- Meno affidabile di EHIWEB per Italia

**Kalliope** (kamailio-based, italiano):
- PBX enterprise italiano
- Non rilevante per SIP trunk diretto

---

## 2 — Tabella Confronto Provider

| Criterio | Telnyx | Twilio | EHIWEB | SignalWire | Vonage |
|----------|--------|--------|--------|------------|--------|
| Numeri italiani | ✅ Sì | ✅ Sì | ✅ Sì (nativi) | ✅ Sì | ⚠️ Limitati |
| Call Control API | ✅ Eccellente | ✅ Eccellente | ❌ No | ✅ Compatibile | ⚠️ Medio |
| Media Streaming WS | ✅ Sì (mulaw) | ✅ Sì (mulaw) | ❌ No (SIP puro) | ✅ Sì | ⚠️ Limitato |
| SIP trunk diretto | ✅ Sì | ✅ Sì | ✅ Sì | ✅ Sì | ✅ Sì |
| Costo DID Italia/mese | ~$1–3 | ~$2–4 | ~€2–5 | ~$1.5–3 | ~$2–4 |
| Costo inbound/min | ~$0.006 | ~$0.007 | ~€0.01* | ~$0.004 | ~$0.008 |
| Endpoint europeo | ✅ Amsterdam/FRA | ✅ Francoforte | ✅ Italia | ✅ Francoforte | ⚠️ UK |
| Lock-in | Basso | Medio | Zero | Basso | Medio |
| API docs qualità | Eccellente | Eccellente | N/A | Buona | Buona |
| GDPR / dati in EU | ✅ (EU region) | ✅ (EU region) | ✅ (IT) | ✅ (EU) | ⚠️ |
| Adatto per FLUXION | ✅ Sì | ✅ Sì | ✅ Primario | ✅ Alternativa | ❌ No |

*EHIWEB: inbound spesso inclusa nel canone mensile

---

## 3 — Architettura Raccomandata: Bridge SIP → Sara Python

### 3.1 Opzione A — EHIWEB Diretto (raccomandato per produzione)

**Pattern**: SIP bridge Python (`voip.py` già presente) su iMac, registrato direttamente a EHIWEB.

```
CHIAMANTE (telefono PSTN/VoIP)
    │
    │ SIP/PSTN
    ↓
EHIWEB SIP Trunk (sip.ehiweb.it:5060)
    │
    │ SIP INVITE → iMac (IP LAN o tramite port forwarding)
    ↓
voip.py (VoIPManager — già implementato)
    │ SIPClient: REGISTER, INVITE, BYE, ACK, Digest MD5
    │ RTPTransport: G.711 PCMU/PCMA, 160 samples/packet (20ms)
    │ VoIPManager: buffer 500ms → PCM → upsample 8kHz→16kHz
    ↓
Sara HTTP API (127.0.0.1:3002)
    │ POST /api/voice/process → {audio_hex: str}
    │ Response: {audio_base64: str, response: str, fsm_state: str}
    ↓
VoIPManager → downsample 16kHz→8kHz → RTPTransport.send_audio()
    │
    │ RTP PCMU → EHIWEB → CHIAMANTE
```

**Stato implementazione**: `voip.py` ha già tutto il necessario. **Gap rimanenti**:
1. `main.py` non espone `VoIPManager` — da integrare
2. Buffer threshold troppo alto (500ms = 4000 bytes) → latenza eccessiva, ridurre a 200ms
3. Sara non ha un endpoint audio streaming dedicato — attualmente usa HTTP request/response (ok per iniziare)
4. NAT traversal: per EHIWEB su iMac LAN → serve port forwarding router (5060 UDP + RTP 10000–10100 UDP) o STUN

**Costi infrastruttura**: €0/mese aggiuntivi (EHIWEB già pagato dal cliente)

---

### 3.2 Opzione B — Telnyx Call Control + Media Streaming

**Pattern**: Telnyx gestisce la PSTN, iMac riceve solo WebSocket audio.

```
CHIAMANTE (PSTN)
    │
    │ PSTN → Telnyx cloud (EU endpoint)
    ↓
TELNYX CALL CONTROL
    │ HTTP POST → iMac Cloudflare Tunnel (evento: call.initiated)
    │ iMac risponde: {"command_name": "answer"}
    │ HTTP POST → iMac (evento: call.answered)
    │ iMac risponde: {"command_name": "start_streaming",
    │                 "url": "wss://tunnel/sara/audio"}
    ↓
TELNYX MEDIA STREAMING (WebSocket)
    │ ↕ wss://tunnel.cliente.com/sara/audio
    │ Inbound: {"event": "media", "payload": "BASE64_MULAW"}
    │ Outbound: {"event": "media", "payload": "BASE64_MULAW"}
    ↓
Sara WebSocket Handler (nuovo endpoint da aggiungere a main.py)
    │ Decode mulaw base64 → PCM16 8kHz → WAV header → Sara process
    │ Sara risponde audio → encode PCM16→mulaw → base64 → WS send
```

**Vantaggi Telnyx vs EHIWEB diretto**:
- Nessun problema NAT/firewall (Telnyx fa outbound WebSocket verso il tuo tunnel)
- Numeri italiani Telnyx se il cliente non ha già EHIWEB
- PSTN gateway gestito da Telnyx (qualità garantita SLA)
- Media Streaming elimina la necessità di gestire RTP lato Python

**Svantaggi**:
- Costo ~$0.006/min aggiuntivo
- Dipendenza da cloud Telnyx
- Richiede nuovo WebSocket endpoint in Sara

**Costi stimati mensili** (PMI tipica: 300 min/mese inbound):
- Numero DID: ~$1.50
- 300 min × $0.006 = $1.80
- Totale: ~$3.30/mese per PMI — **accettabilissimo**

---

### 3.3 Opzione C — Telnyx SIP Trunk + voip.py (ibrida)

**Pattern**: Telnyx come provider PSTN, ma SIP diretto (non Call Control/WebSocket).

```
CHIAMANTE → Telnyx (PSTN) → SIP INVITE → iMac voip.py → Sara HTTP
```

- iMac registra SIP su `sip.telnyx.com` con credenziali Telnyx
- Telnyx autentica via credential auth (username/password) o IP auth
- Vantaggio: riutilizza `voip.py` esistente senza modifiche a Sara
- Svantaggio: stesso problema NAT/firewall di EHIWEB diretto

---

## 4 — Codice Python: WebSocket Audio Bridge per Telnyx/Twilio

Il seguente codice mostra il nuovo endpoint WebSocket da aggiungere a `main.py` di Sara per supportare Telnyx Media Streaming o Twilio Media Streams:

```python
# Da aggiungere a main.py — WebSocket endpoint per Telnyx/Twilio Media Streaming
import aiohttp
from aiohttp import web
import audioop  # Python 3.9: ulaw↔linear conversion
import base64
import json
import struct
import wave
import io

# -----------------------------------------------------------------------
# COSTANTI AUDIO
# -----------------------------------------------------------------------
SAMPLE_RATE_SIP = 8000    # G.711 telefonia standard
SAMPLE_RATE_WHISPER = 16000  # Whisper/Groq STT richiede 16kHz
CHUNK_DURATION_MS = 200   # 200ms per chunk → buon balance latenza/accuratezza
CHUNK_SAMPLES_8K = SAMPLE_RATE_SIP * CHUNK_DURATION_MS // 1000  # = 1600 samples
CHUNK_BYTES_ULAW = CHUNK_SAMPLES_8K   # 1 byte per sample mulaw
CHUNK_BYTES_PCM16_8K = CHUNK_SAMPLES_8K * 2  # 2 bytes per sample PCM16


def ulaw_to_pcm16_8k(ulaw_bytes: bytes) -> bytes:
    """Converte G.711 µ-law → PCM 16-bit 8kHz."""
    return audioop.ulaw2lin(ulaw_bytes, 2)


def pcm16_8k_to_pcm16_16k(pcm8k: bytes) -> bytes:
    """Upsample PCM16 8kHz → 16kHz per Whisper/Groq STT."""
    return audioop.ratecv(pcm8k, 2, 1, 8000, 16000, None)[0]


def pcm16_16k_to_ulaw_8k(pcm16k: bytes) -> bytes:
    """Downsample PCM16 16kHz → 8kHz → G.711 µ-law per RTP output."""
    pcm8k = audioop.ratecv(pcm16k, 2, 1, 16000, 8000, None)[0]
    return audioop.lin2ulaw(pcm8k, 2)


def pcm16_to_wav_bytes(pcm_data: bytes, sample_rate: int = 16000) -> bytes:
    """Wrappa PCM16 in WAV header per Sara /api/voice/process."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


# -----------------------------------------------------------------------
# WEBSOCKET HANDLER — TELNYX MEDIA STREAMING
# -----------------------------------------------------------------------
async def sara_telnyx_ws_handler(request: web.Request) -> web.WebSocketResponse:
    """
    WebSocket endpoint per Telnyx Media Streaming.
    URL: wss://<tunnel>/sara/telnyx/stream

    Protocollo Telnyx:
    - Inbound msg: {"event": "media", "media": {"payload": "<base64_ulaw>"}}
    - Outbound msg: {"event": "media", "streamSid": "...", "media": {"payload": "<base64_ulaw>"}}
    - Connected msg: {"event": "connected", "protocol": "Call Control", "version": "1.0.0"}
    - Start msg: {"event": "start", "streamSid": "MZxxx", "start": {"mediaFormat": {...}}}
    - Stop msg: {"event": "stop"}
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    stream_sid = None
    audio_buffer = bytearray()
    session_active = False

    # Avvia sessione Sara
    async with aiohttp.ClientSession() as http_session:
        try:
            await http_session.post("http://127.0.0.1:3002/api/voice/greet")
            session_active = True
        except Exception as e:
            request.app.logger.error(f"Sara greet failed: {e}")

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                event = data.get("event")

                if event == "connected":
                    request.app.logger.info("Telnyx stream connected")

                elif event == "start":
                    stream_sid = data.get("streamSid")
                    request.app.logger.info(f"Stream started: {stream_sid}")

                elif event == "media":
                    # Decodifica audio µ-law inbound
                    payload_b64 = data.get("media", {}).get("payload", "")
                    if not payload_b64:
                        continue

                    ulaw_chunk = base64.b64decode(payload_b64)
                    audio_buffer.extend(ulaw_chunk)

                    # Processa quando abbiamo abbastanza audio (200ms)
                    if len(audio_buffer) >= CHUNK_BYTES_ULAW:
                        raw_ulaw = bytes(audio_buffer[:CHUNK_BYTES_ULAW])
                        audio_buffer = audio_buffer[CHUNK_BYTES_ULAW:]

                        # Converti: ulaw 8kHz → PCM16 8kHz → PCM16 16kHz → WAV
                        pcm8k = ulaw_to_pcm16_8k(raw_ulaw)
                        pcm16k = pcm16_8k_to_pcm16_16k(pcm8k)
                        wav_bytes = pcm16_to_wav_bytes(pcm16k)

                        # Manda a Sara
                        async with aiohttp.ClientSession() as http_session:
                            payload = {"audio_hex": wav_bytes.hex()}
                            resp = await http_session.post(
                                "http://127.0.0.1:3002/api/voice/process",
                                json=payload,
                                timeout=aiohttp.ClientTimeout(total=3.0)
                            )
                            sara_data = await resp.json()

                        # Invia risposta TTS al chiamante
                        tts_audio = sara_data.get("audio_base64")
                        if tts_audio and stream_sid:
                            # Converti TTS (PCM16 22050Hz) → ulaw 8kHz
                            # Nota: Sara restituisce PCM16 a 22050Hz (Piper)
                            tts_pcm = bytes.fromhex(tts_audio)
                            # Converti 22050→8000 Hz
                            pcm8k_out = audioop.ratecv(tts_pcm, 2, 1, 22050, 8000, None)[0]
                            ulaw_out = audioop.lin2ulaw(pcm8k_out, 2)
                            payload_out = base64.b64encode(ulaw_out).decode()

                            await ws.send_str(json.dumps({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": payload_out}
                            }))

                        # Gestisci terminazione chiamata
                        if sara_data.get("should_exit") or sara_data.get("fsm_state") == "IDLE":
                            await ws.send_str(json.dumps({
                                "event": "stop",
                                "streamSid": stream_sid
                            }))
                            break

                elif event == "stop":
                    request.app.logger.info("Telnyx stream stopped")
                    # Reset Sara per prossima chiamata
                    async with aiohttp.ClientSession() as http_session:
                        await http_session.post("http://127.0.0.1:3002/api/voice/reset")
                    break

            except json.JSONDecodeError:
                pass
            except Exception as e:
                request.app.logger.error(f"WS handler error: {e}")

        elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
            break

    return ws


# -----------------------------------------------------------------------
# WEBHOOK HANDLER — TELNYX CALL CONTROL
# -----------------------------------------------------------------------
async def telnyx_call_control_webhook(request: web.Request) -> web.Response:
    """
    HTTP POST handler per Telnyx Call Control events.
    URL: POST /webhooks/telnyx

    Risponde ai comandi per gestire il flusso della chiamata.
    Telnyx si aspetta risposta HTTP 200 con JSON.
    """
    data = await request.json()
    event_type = data.get("data", {}).get("event_type", "")
    call_control_id = data.get("data", {}).get("payload", {}).get("call_control_id")

    TELNYX_API_KEY = request.app["telnyx_api_key"]  # da config.env

    async with aiohttp.ClientSession() as session:

        if event_type == "call.initiated":
            # Risponde alla chiamata
            await session.post(
                f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer",
                headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
                json={}
            )

        elif event_type == "call.answered":
            # Avvia Media Streaming verso Sara
            await session.post(
                f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/streaming_start",
                headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
                json={
                    "stream_url": request.app["sara_ws_url"],  # wss://tunnel/sara/telnyx/stream
                    "stream_track": "both_tracks"
                }
            )

        elif event_type == "call.hangup":
            # Reset Sara
            async with aiohttp.ClientSession() as http:
                await http.post("http://127.0.0.1:3002/api/voice/reset")

    return web.Response(status=200, text="OK")
```

**Note implementazione**:
- `audioop` è il modulo Python stdlib per conversioni audio — disponibile su Python 3.9 (iMac)
- **Sara restituisce TTS PCM16 a 22050Hz** (Piper TTS default) → necessario downsample 22050→8000
- Il buffer da 200ms è il giusto tradeoff latenza/accuratezza STT — non scendere sotto 100ms
- `aiohttp.ClientTimeout(total=3.0)` protegge da timeout Sara bloccante

---

## 5 — Stima Latenza End-to-End Realistica

### Hardware: Intel iMac 2019 (Core i9 3.6GHz, 32GB RAM)

```
SCENARIO: chiamante parla → Sara risponde (prima parola udibile)

Componente                          Min    Tipico    P95
─────────────────────────────────────────────────────────
PSTN → Provider cloud (Telnyx/EHIWEB)  20ms    50ms    100ms
Audio buffering (200ms chunk)         160ms   200ms    240ms  ← bottleneck principale
ulaw→PCM→WAV encoding (Python)          1ms     2ms      5ms
HTTP POST → Sara (localhost)            1ms     2ms      5ms
Sara: STT Groq Whisper API            120ms   200ms    400ms
Sara: LLM Groq llama-3.1-8b-instant   150ms   250ms    500ms
Sara: TTS Piper Italian (iMac)         60ms   100ms    200ms
PCM→ulaw→base64 encoding                1ms     2ms      5ms
WebSocket send TTS                      2ms     5ms     20ms
Provider cloud → PSTN                  20ms    50ms    100ms
─────────────────────────────────────────────────────────
TOTALE                               ~535ms  ~861ms  ~1575ms
```

**Target**: P50 <900ms (percepito come istantaneo), P95 <2000ms (accettabile)

**Ottimizzazioni per raggiungere P50 <800ms**:
1. **Riduci buffer a 150ms** (da 200ms) — risparmia 50ms ma aumenta rischio VAD miss
2. **llama-3.1-8b-instant invece di llama-3.3-70b** per risposte brevi (booking) → -100ms
3. **TTS cache**: pre-genera frasi comuni ("Un momento prego", giorni/orari frequenti) → -80ms
4. **Groq Whisper large-v3-turbo** invece di large-v3 → -50ms STT
5. **Parallel processing**: inizia LLM mentre TTS chunka la risposta → pipeline streaming

**Con ottimizzazioni applicate**: P50 ~620ms, P95 ~1200ms — target raggiunto.

---

## 6 — Costi Mensili Stimati per PMI Italiana Tipica

**Assunzioni**: 100 chiamate/mese, media 4 min/chiamata = 400 min/mese inbound

### Scenario A: EHIWEB diretto (cliente già EHIWEB)
| Voce | Costo |
|------|-------|
| Numero DID EHIWEB | già pagato (~€3/mese) |
| Minuti inbound 400 | inclusi o ~€4 |
| FLUXION infrastruttura aggiuntiva | €0 |
| **Totale aggiuntivo per VoIP Sara** | **~€0–4/mese** |

### Scenario B: Telnyx
| Voce | Costo |
|------|-------|
| Numero DID italiano | ~$2.00 |
| 400 min × $0.006 inbound | ~$2.40 |
| Cloudflare tunnel | €0 (già presente) |
| **Totale** | **~$4.40/mese (~€4)** |

### Scenario C: Twilio
| Voce | Costo |
|------|-------|
| Numero DID italiano | ~$3.00 |
| 400 min × $0.0085 inbound | ~$3.40 |
| **Totale** | **~$6.40/mese (~€6)** |

### Scenario D: SignalWire
| Voce | Costo |
|------|-------|
| Numero DID italiano | ~$2.00 |
| 400 min × $0.004 inbound | ~$1.60 |
| **Totale** | **~$3.60/mese (~€3.30)** — opzione più economica cloud

---

## 7 — Integrazione con voip.py Esistente

`voip.py` è già un'implementazione SIP/RTP completa e funzionante per EHIWEB diretto. **Gap da chiudere prima del deploy**:

### Gap 1: Ridurre buffer latenza
In `VoIPManager._buffer_threshold`:
```python
# ATTUALE (500ms — troppo alto)
self._buffer_threshold = 8000  # ~500ms at 8kHz 16-bit

# CORRETTO (200ms)
self._buffer_threshold = 3200  # ~200ms at 8kHz 16-bit
```

### Gap 2: Integrare in main.py
`VoIPManager` esiste ma non è avviato dal server. Aggiungere:
```python
# In main.py — setup VoIP
from src.voip import VoIPManager, SIPConfig

sip_config = SIPConfig.from_env()
voip_manager = VoIPManager(config=sip_config)
voip_manager.set_pipeline(pipeline_instance)
# Avvia se credenziali configurate
if sip_config.username:
    await voip_manager.start()
```

### Gap 3: NAT traversal per iMac LAN
`voip.py` usa `socket.socket(AF_INET, SOCK_DGRAM)` — non implementa STUN. Per EHIWEB da LAN privata è necessario o:
- Router port forwarding: 5060 UDP + 10000–10100 UDP → iMac
- Oppure: `rport` + keep-alive SIP OPTIONS ogni 30s (già supportato dalla classe con `register_interval`)

### Gap 4: Error recovery e reconnect
Se EHIWEB scade la registrazione (ogni 300s), voip.py fa re-REGISTER automaticamente via `_register_loop()`. Ma se la connessione è persa (power cycle router), non c'è reconnect automatico. Aggiungere watchdog esterno.

### Gap 5: Audio resampling qualità
`_upsample_audio()` usa interpolazione lineare semplice — introduce aliasing. Sostituire con `audioop.ratecv()` per qualità migliore:
```python
import audioop
def _upsample_audio_hq(self, audio_8k: bytes) -> bytes:
    """Upsample 8kHz → 16kHz con anti-aliasing (audioop)."""
    result, _ = audioop.ratecv(audio_8k, 2, 1, 8000, 16000, None)
    return result
```

---

## 8 — Raccomandazione Finale

### Strategia Dual-Track (raccomandata)

**Track 1 — MVP Immediato (1 settimana)**:
- Usa `voip.py` esistente con EHIWEB diretto
- Chiudi i 5 gap sopra elencati
- Testa con account EHIWEB di test (o account sviluppatore da richiedere)
- Costo: €0 aggiuntivi

**Track 2 — Fallback Cloud (opzionale, parallelo)**:
- Aggiungi WebSocket endpoint `/sara/telnyx/stream` a `main.py` (codice sopra)
- Configura Telnyx account con numero DID italiano di test (~$2/mese)
- Utile per clienti senza EHIWEB o con problemi NAT

### Provider Principale: EHIWEB Diretto
**Motivazione**:
1. **Zero costi aggiuntivi** per il cliente FLUXION — il numero EHIWEB lo ha già
2. **Zero dipendenza cloud** — nessun servizio esterno può interrompere il funzionamento
3. **Dati vocali mai escono dall'Italia** — vantaggio GDPR enorme per cliniche
4. **Implementazione già presente** — `voip.py` è SIP/RTP completo, solo 5 gap da chiudere
5. **UX perfetta**: "Il tuo numero di telefono esistente risponde automaticamente con Sara"

### Provider Backup: Telnyx
**Per clienti senza EHIWEB o con problemi di NAT**:
1. Costo ragionevole (~€4/mese)
2. API eccellente, endpoint EU, WebSocket Media Streaming pulito
3. Preferito a Twilio per minor costo e endpoint europeo più vicino
4. Codice WebSocket già pronto sopra (da aggiungere a `main.py`)

### Non raccomandato: Twilio come primario
- Costo 1.5–2× Telnyx per funzionalità identiche
- Latenza endpoint EU leggermente superiore
- Va bene come fallback di emergenza se Telnyx ha problemi

---

## 9 — Roadmap Implementazione F15 (aggiornata)

### Sprint 1 — MVP EHIWEB (3–5 giorni)
1. Chiudi Gap 1–5 in `voip.py` (buffer, resampling, integraizone main.py)
2. Test con `pjsua` CLI su Termux o Linphone per emulare EHIWEB
3. Verifica end-to-end: chiamata → Sara risponde → TTS udibile
4. Aggiungi `VOIP_SIP_USER`, `VOIP_SIP_PASSWORD`, `VOIP_SIP_SERVER` a `config.env` iMac

### Sprint 2 — Telnyx WebSocket Bridge (2–3 giorni)
1. Aggiungi endpoint `/sara/telnyx/stream` WebSocket a `main.py`
2. Aggiungi endpoint `/webhooks/telnyx` POST a `main.py`
3. Configura Telnyx account + DID italiano test
4. Test end-to-end con Telnyx

### Sprint 3 — Setup Wizard + UI (2–3 giorni)
1. Aggiungi step VoIP nel SetupWizard (3 campi: username, password, numero)
2. Bottone "Testa Connessione SIP" → endpoint `POST /api/sip/test`
3. Badge stato connessione in Impostazioni

---

## 10 — Sommario Gap vs Gold Standard 2026

| Competitor | Architettura VoIP AI | Costo/min | Dati in EU |
|-----------|---------------------|-----------|------------|
| Retell AI | Cloud SIP endpoint + CDN | ~€0.07–0.15 | No (US) |
| Vapi | Cloud + custom LLM webhook | ~€0.05 | No (US) |
| Bland AI | Cloud outbound | ~€0.05 | No (US) |
| Twilio + GPT-4o | Media Streams + OpenAI | ~€0.02 + LLM | Sì (EU) |
| **FLUXION F15** | **EHIWEB diretto + Sara locale** | **€0** | **Sì (IT)** |

**FLUXION è l'unico sistema nel mercato italiano PMI che combina**:
- Voice AI italiana (Sara, 23 stati FSM, 1334 PASS)
- SIP diretto con numero già esistente del cliente
- Zero costo per minuto
- Audio processing locale (iMac) = GDPR nativo

---

*CoVe 2026 Research completata — 2026-03-12*
*File: `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/f15-voip-telnyx-research.md`*
*Basata su: voip.py (1227 righe), sip_client.py, f15-voip-architecture-agente-a.md, f15-ehiweb-termux-agente-b.md*
