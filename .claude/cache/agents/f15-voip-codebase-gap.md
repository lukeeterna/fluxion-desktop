# F15 VoIP — Codebase Gap Analysis
> Agente: Gap Analysis Codebase
> Data: 2026-03-12
> Basato su: lettura diretta di main.py, voip.py, sip_client.py, orchestrator.py, voice_calls.rs, VoiceAgentSettings.tsx, requirements.txt, migration 011

---

## 1. Stato Attuale Pipeline Audio

```
CHIAMATE ATTUALI (Tauri UI → Sara):
─────────────────────────────────────────────────────────────────────
Browser/Tauri        HTTP POST          Python Server
(audio WAV/PCM)  ──────────────────▶  /api/voice/process
                  {audio_hex: str}      porta 3002 (127.0.0.1)
                  {text: str}          │
                                       ▼
                                 GroqClient.transcribe_audio()
                                 [Groq Whisper large-v3, ~200ms]
                                       │
                                       ▼
                                 VoiceOrchestrator.process()
                                 [5-layer RAG pipeline]
                                       │
                                       ▼
                                 TTS.synthesize(response_text)
                                 [SystemTTS macOS say + TTSCache]
                                       │
                                       ▼
                  {audio_base64: hex}
Tauri   ◀─────────────────────────────┘
plays audio


CHIAMATE VoIP DESIDERATE (SIP trunk → Sara):
─────────────────────────────────────────────────────────────────────
PSTN/VoIP caller
       │ INVITE SIP RFC 3261
       ▼
sip.ehiweb.it:5060 (UDP)
       │
       ▼ [NAT traversal needed!]
voip.py SIPClient (iMac)   ◀──── attualmente: NON integrato in main.py
       │ G.711 RTP (PCMU/PCMA 8kHz)
       ▼
RTPTransport._decode_pcmu()  → PCM 16-bit 8kHz
       │
       ▼
VoIPManager._upsample_audio() → PCM 16-bit 16kHz
       │
       ▼ [MANCANTE: interfaccia pipeline]
?? pipeline.process_audio(audio_16k) ??  → nessun metodo `process_audio` in VoiceOrchestrator
       │
       ▼
STT (Groq transcribe_audio) → text
       │
       ▼
VoiceOrchestrator.process(text) → OrchestratorResult
       │
       ▼
TTS.synthesize(response_text) → WAV bytes (16kHz, 16-bit)
       │ [MANCANTE: conversione formato]
       ▼
?? downsample 16kHz→8kHz ?? → PCM 8kHz (presente in VoIPManager._downsample_audio)
       │
       ▼
RTPTransport.send_audio(pcm_8k) → G.711 RTP packets
       │
       ▼
Caller hears Sara
```

---

## 2. Cosa Esiste Già nel Codebase

### Python — Già Implementato

| File | Stato | Note |
|------|-------|-------|
| `voice-agent/src/voip.py` | IMPLEMENTATO (non integrato) | SIPClient UDP + SIP RFC 3261, RTPTransport G.711, VoIPManager, upsample/downsample audio |
| `voice-agent/src/sip_client.py` | DUPLICATO (più vecchio) | Versione stub — sovrascritta da `voip.py` completo |
| `voice-agent/src/orchestrator.py` | FUNZIONANTE | Non espone `process_audio()` — solo `process(user_input: str)` |
| `voice-agent/main.py` | FUNZIONANTE | Non avvia VoIPManager. Nessun endpoint `/api/voice/call`. CORS solo localhost. |

### Rust/Tauri — Già Implementato

| File | Stato | Note |
|------|-------|-------|
| `src-tauri/src/commands/voice_calls.rs` | IMPLEMENTATO | DB CRUD: chiamate_voice, voice_agent_config, stats. Comandi registrati in lib.rs |
| Migration `011_voice_agent.sql` | APPLICATA | Tabelle: chiamate_voice, voice_agent_config (no colonne SIP credentials) |

### Frontend — Stato

| File | Stato | Note |
|------|-------|-------|
| `VoiceAgentSettings.tsx` | PRESENTE | Solo campo Groq API key. Nessuna sezione VoIP/SIP. |
| `Impostazioni.tsx` | PRESENTE | Carica `<VoiceAgentSettings />` nella sezione Sara. |
| Setup Wizard | PARZIALE | Campo `ehiweb_number` già nello schema Zod (SetupConfigSchema) ma nessun campo SIP password/server. |

### Dipendenze Python — Stato

| Package | In requirements.txt | Installato su iMac | Note |
|---------|---------------------|-------------------|------|
| `websockets>=12.0` | SÌ | DA VERIFICARE | Per WebSocket bridge |
| `aiortc>=1.6.0` | SÌ | DA VERIFICARE | Non necessario per approccio SIP diretto |
| `pipecat-ai>=0.0.30` | SÌ | DA VERIFICARE | Non necessario per approccio SIP diretto |
| `av>=12.0.0` | SÌ | DA VERIFICARE | Potrebbe servire per codec avanzati |
| `sounddevice>=0.4.6` | SÌ | DA VERIFICARE | Non serve per SIP (no soundcard) |
| `pjsip` / `pjsua2` | NO | NO | Non nel requirements — l'approccio custom voip.py lo evita |

---

## 3. Gap Critici da Colmare

### GAP-1 (CRITICO): VoIPManager non integrato in main.py

**Problema**: `voip.py` esiste e implementa SIP+RTP completo, ma `main.py` non lo avvia mai. Il codice è morto.

**Dove**: `main.py` → funzione `main()` (riga 657)

**Cosa aggiungere**:
```python
# In main(), dopo start HTTP server (riga 781):
if groq_api_key and os.getenv("VOIP_SIP_USER"):
    from src.voip import VoIPManager, SIPConfig
    voip_config = SIPConfig.from_env()
    voip_manager = VoIPManager(voip_config)
    voip_manager.set_pipeline(orchestrator)  # vedi GAP-2
    if await voip_manager.start():
        print("✅ VoIP service started (SIP registered)")
    else:
        print("⚠️  VoIP service not started (no SIP credentials)")
```

**Stima**: 30 min (dipende da GAP-2)

---

### GAP-2 (CRITICO): Nessun metodo `process_audio()` su VoiceOrchestrator

**Problema**: `VoIPManager._process_audio()` chiama `self.pipeline.process_audio(audio_16k)` (riga 1124 di voip.py) — questo metodo NON esiste su `VoiceOrchestrator`. Esiste solo `VoiceOrchestrator.process(user_input: str)`.

**Dove**: `voice-agent/src/orchestrator.py`

**Cosa aggiungere** (nuovo metodo su VoiceOrchestrator):
```python
async def process_audio(self, audio_bytes: bytes) -> dict:
    """
    Processo audio PCM → STT → pipeline → TTS → PCM output.
    Usato da VoIPManager per chiamate SIP.

    Args:
        audio_bytes: PCM 16-bit 16kHz mono

    Returns:
        {"audio_response": bytes_pcm_16k, "text": str, "should_exit": bool}
    """
    from src.vad_http_handler import add_wav_header
    wav_data = add_wav_header(audio_bytes)

    # STT
    transcription = await self.groq_client.transcribe_audio(wav_data)
    if not transcription or not transcription.strip():
        return {"audio_response": None, "text": "", "should_exit": False}

    # Orchestrator pipeline
    result = await self.process(user_input=transcription)

    # TTS
    audio_out = await self.tts.synthesize(result.response)

    return {
        "audio_response": audio_out,
        "text": result.response,
        "should_exit": result.should_exit,
        "transcription": transcription,
        "latency_ms": result.latency_ms,
    }
```

**Stima**: 1 ora (includendo testing con audio 8kHz upsampled)

---

### GAP-3 (CRITICO): NAT Traversal — binding 127.0.0.1 per SIP

**Problema**: `voip.py` `SIPClient._create_socket()` bind a `local_ip` (riga 256). Il server voice (`main.py`) è bound a `127.0.0.1` per sicurezza F14. Per SIP il binding deve essere sull'IP LAN (192.168.1.12) altrimenti il trunk EHIWEB non può raggiungere la macchina.

**Dettaglio**: `SIPConfig.local_ip` è vuoto per default → `_get_local_ip()` fa auto-detect via UDP connect a sip.ehiweb.it → dovrebbe restituire 192.168.1.12 se il router DHCP è configurato. **Non garantito**.

**Soluzione**: Impostare `VOIP_LOCAL_IP=192.168.1.12` in config.env iMac. Verificare che il router (IP fisso DHCP per MAC `a8:20:66:4e:0e:2d`) restituisca sempre questo IP.

**Dove**: `config.env` iMac (già citato in MEMORY.md come "su iMac, NON in git")

**Cosa aggiungere**: Riga in config.env:
```
VOIP_SIP_SERVER=sip.ehiweb.it
VOIP_SIP_PORT=5060
VOIP_SIP_USER=<numero_DID_ehiweb>
VOIP_SIP_PASSWORD=<password_ehiweb>
VOIP_LOCAL_IP=192.168.1.12
```

**Stima**: 15 min (config) + test SIP registration

---

### GAP-4 (IMPORTANTE): Nessuna sezione VoIP in Impostazioni UI

**Problema**: `VoiceAgentSettings.tsx` contiene solo la chiave Groq API. Non c'è nessun posto nell'UI per configurare le credenziali SIP (server, username, password, numero DID).

**Dove**: `src/components/impostazioni/VoiceAgentSettings.tsx` (riga 18 onward)

**Cosa aggiungere**: Nuovo pannello "Telefono VoIP (EHIWEB)" dentro `VoiceAgentSettings.tsx` o come componente separato `VoipSettings.tsx` caricato da `Impostazioni.tsx`.

**Campi UI necessari**:
- Numero DID EHIWEB (es. `0250150001`)
- Password SIP
- Server SIP (default `sip.ehiweb.it`, editabile)
- Toggle "Abilita ricezione chiamate"
- Stato connessione SIP (badge: Registrato / Non registrato / Errore)

**Stima**: 2 ore (componente React + hook + salvataggio in DB)

---

### GAP-5 (IMPORTANTE): DB manca colonne SIP credentials in voice_agent_config

**Problema**: La tabella `voice_agent_config` (migration 011) non ha le colonne per le credenziali SIP. Attualmente il `SetupConfigSchema` ha solo `ehiweb_number` (numero DID) ma manca `sip_password`, `sip_server`, `sip_port`.

**Dove**: `src-tauri/migrations/011_voice_agent.sql` (già applicata) — serve nuova migration

**Nuova migration da aggiungere** (es. `035_voip_sip_credentials.sql`):
```sql
-- Migration 035: VoIP SIP credentials in voice_agent_config
ALTER TABLE voice_agent_config ADD COLUMN sip_username TEXT;
ALTER TABLE voice_agent_config ADD COLUMN sip_password TEXT;
ALTER TABLE voice_agent_config ADD COLUMN sip_server TEXT DEFAULT 'sip.ehiweb.it';
ALTER TABLE voice_agent_config ADD COLUMN sip_port INTEGER DEFAULT 5060;
ALTER TABLE voice_agent_config ADD COLUMN voip_attivo INTEGER DEFAULT 0;
```

**Stima**: 30 min (migration + update Rust structs + update `get_voice_config` / `update_voice_config` in voice_calls.rs)

---

### GAP-6 (IMPORTANTE): Nessun Rust command per leggere/scrivere SIP credentials

**Problema**: `voice_calls.rs` ha `get_voice_config` / `update_voice_config` ma i tipi `VoiceAgentConfig` e il relativo `UPDATE` SQL non includono le nuove colonne SIP (dipende da GAP-5).

**Dove**: `src-tauri/src/commands/voice_calls.rs`

**Modifiche necessarie**:
1. Aggiungere campi a `VoiceAgentConfig` struct (riga 32):
```rust
pub sip_username: Option<String>,
pub sip_password: Option<String>,
pub sip_server: Option<String>,
pub sip_port: Option<i32>,
pub voip_attivo: i32,
```
2. Aggiornare la query `UPDATE voice_agent_config SET ...` per includere i nuovi campi.
3. Aggiungere comando `get_voip_status` che interroga porta 3002 `/api/voice/voip/status` (da aggiungere in Python — vedi GAP-7).

**Stima**: 1 ora

---

### GAP-7 (IMPORTANTE): Nessun endpoint HTTP per stato/controllo VoIP in main.py

**Problema**: Tauri UI non può sapere se SIP è registrato o quale chiamata è attiva. Nessun endpoint `/api/voice/voip/status` o `/api/voice/voip/hangup`.

**Dove**: `main.py` → `VoiceAgentHTTPServer._setup_routes()` (riga 239)

**Endpoint da aggiungere**:

```python
# In _setup_routes():
self.app.router.add_get("/api/voice/voip/status", self.voip_status_handler)
self.app.router.add_post("/api/voice/voip/hangup", self.voip_hangup_handler)
self.app.router.add_post("/api/voice/voip/call", self.voip_call_handler)  # outbound
```

**Implementazione `voip_status_handler`**:
```python
async def voip_status_handler(self, request):
    if hasattr(self, 'voip_manager') and self.voip_manager:
        return web.json_response(self.voip_manager.get_status())
    return web.json_response({"running": False, "sip": {"registered": False}})
```

**Stima**: 1 ora (3 handlers + wiring voip_manager in server instance)

---

### GAP-8 (MINORE): TTS output formato non garantito per VoIP

**Problema**: `TTS.synthesize()` restituisce bytes WAV o PCM grezzo (dipende dall'engine). `VoIPManager._send_audio()` si aspetta PCM 16-bit 16kHz raw (non WAV header). Se SystemTTS (macOS `say`) restituisce WAV con header RIFF, `_downsample_audio()` decoderà i bytes dell'header come audio → distorsione.

**Dove**: `voice-agent/src/voip.py` → `VoIPManager._on_call_connected()` (riga 1072), `VoIPManager._send_audio()` (riga 1151)

**Fix necessario** in `VoIPManager._send_audio()`:
```python
async def _send_audio(self, audio_data: bytes):
    # Strip WAV header if present
    if audio_data[:4] == b'RIFF':
        import wave, io
        with wave.open(io.BytesIO(audio_data)) as wf:
            raw_pcm = wf.readframes(wf.getnframes())
            # Resample if needed
            if wf.getframerate() != 8000:
                audio_data = raw_pcm  # then downsample below
            else:
                audio_data = raw_pcm
    # ... rest of existing _send_audio logic
```

**Stima**: 1 ora (incluso test con SystemTTS output)

---

### GAP-9 (MINORE): CORS blocca VoIP manager se serve WebSocket futuro

**Problema**: Il middleware CORS in `main.py` (riga 54) permette solo origini localhost. Se in futuro si aggiunge un WebSocket endpoint per streaming audio in tempo reale (latency ottimizzata), il bridge dovrà girare sull'iMac stesso (stessa macchina = no CORS issue). Non è un problema oggi con HTTP polling, ma da tenere presente.

**Dove**: `main.py` riga 36–49 (`_ALLOWED_ORIGINS`)

**Nota**: Per ora non cambiare — il design con bridge sulla stessa macchina è corretto per sicurezza.

---

### GAP-10 (FUTURO): Mancanza WebSocket per streaming real-time

**Problema**: L'architettura attuale è HTTP request/response (1 POST per utterance). Per SIP real-time con VAD in-call, serve WebSocket bidirezionale: audio chunks in ingresso → VAD → quando silence → flush a STT → risposta audio in uscita.

**Dove**: `main.py` (nuovo endpoint), `voip.py` (nuovo handler)

**Dipendenze già nel requirements.txt**: `websockets>=12.0` — già incluso.

**Stima**: 3–4 ore (WebSocket handler + VAD integration per SIP stream)

**Priorità**: BASSA per MVP — HTTP polling ogni ~500ms di silenzio è sufficiente per demo.

---

## 4. Schema Rust Commands per VoIP Settings

Riepilogo comandi Rust da aggiornare/aggiungere in `voice_calls.rs`:

```rust
// ESISTENTI — da aggiornare con nuovi campi SIP:
#[tauri::command] pub async fn get_voice_config(pool) -> Result<VoiceAgentConfig, String>
#[tauri::command] pub async fn update_voice_config(pool, config: VoiceAgentConfig) -> Result<VoiceAgentConfig, String>
#[tauri::command] pub async fn toggle_voice_agent(pool, attivo: bool) -> Result<VoiceAgentConfig, String>

// NUOVI — da aggiungere:
#[tauri::command] pub async fn get_voip_status() -> Result<VoipStatus, String>
  // Chiama GET http://127.0.0.1:3002/api/voice/voip/status
  // Returns: { running: bool, registered: bool, active_call: Option<CallInfo> }

#[tauri::command] pub async fn toggle_voip_attivo(pool, attivo: bool) -> Result<VoiceAgentConfig, String>
  // Salva voip_attivo in DB + notifica Python via HTTP POST /api/voice/voip/toggle
  // (Python riavvia VoIPManager se attivo, lo stoppa se non attivo)
```

**Struct aggiornata** (dopo migration 035):
```rust
#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct VoiceAgentConfig {
    // ... campi esistenti ...
    pub sip_username: Option<String>,
    pub sip_password: Option<String>,  // ATTENZIONE: non loggare mai
    pub sip_server: Option<String>,
    pub sip_port: Option<i32>,
    pub voip_attivo: i32,
}
```

---

## 5. Dipendenze Python da Aggiungere/Verificare

| Package | Necessario per | Già in requirements.txt | Azione |
|---------|---------------|------------------------|--------|
| Nessun nuovo package per MVP | voip.py usa stdlib: socket, asyncio, struct, uuid | N/A | Solo verificare `soundfile` per WAV parsing |
| `soundfile>=0.12.1` | WAV header stripping in TTS output | SÌ | Verificare installazione su iMac |
| `websockets>=12.0` | WebSocket streaming (futuro) | SÌ | Già incluso |

**Nota importante**: `voip.py` usa SOLO stdlib Python (socket, asyncio, struct, uuid, hashlib). Zero dipendenze esterne per il core SIP+RTP. Nessun `pipecat-ai`, `aiortc`, `pjsip` necessario per l'approccio implementato. I pacchetti VoIP nel requirements.txt (`pipecat-ai`, `aiortc`, `aioice`, `av`) sono stati pianificati ma non sono necessari dato l'implementazione custom in `voip.py`.

---

## 6. Stima Ore di Implementazione

| GAP | Componente | Ore |
|-----|-----------|-----|
| GAP-1 | Wiring VoIPManager in main.py | 0.5h |
| GAP-2 | process_audio() in VoiceOrchestrator | 1.0h |
| GAP-3 | Config.env + NAT setup + SIP registration test | 0.5h |
| GAP-4 | UI VoipSettings.tsx (React) | 2.0h |
| GAP-5 | Migration 035 SIP credentials | 0.5h |
| GAP-6 | Rust struct + commands update | 1.0h |
| GAP-7 | Endpoint HTTP /voip/status+hangup+call | 1.0h |
| GAP-8 | WAV header stripping in _send_audio | 1.0h |
| **TOTALE MVP** | | **7.5h** |
| GAP-10 (futuro) | WebSocket streaming | 3-4h |

---

## 7. Ordine di Implementazione Consigliato

**Fase A — Backend Python** (iMac, ~3h):
1. GAP-2: Aggiungere `process_audio()` a `VoiceOrchestrator`
2. GAP-8: Correggere WAV stripping in `VoIPManager._send_audio()`
3. GAP-7: Aggiungere endpoint `/api/voice/voip/*` a main.py
4. GAP-1: Integrare `VoIPManager` in `main()` con guard `if VOIP_SIP_USER`
5. GAP-3: Impostare config.env + test `python -c "from src.voip import VoIPManager; ..."`

**Fase B — Backend Rust** (iMac build, ~2h):
6. GAP-5: Migration 035
7. GAP-6: Aggiornare `VoiceAgentConfig` struct + queries + nuovo `get_voip_status`
8. Registrare nuovi comandi in `lib.rs`

**Fase C — Frontend React** (MacBook, ~2.5h):
9. GAP-4: Componente `VoipSettings.tsx` + sezione in `VoiceAgentSettings.tsx`
10. TypeScript type-check + `npm run type-check`

---

## 8. Rischi e Note Critiche

**RISCHIO-1 — SIP port 5060 sul router**: Il router di casa/ufficio potrebbe bloccare le connessioni SIP in ingresso (porta 5060 UDP). EHIWEB usa un trunk SIP — la chiamata parte da EHIWEB verso l'iMac. Serve port forwarding 5060→192.168.1.12 nel router. Alternativa: usare SIP over TCP/TLS su porta non standard.

**RISCHIO-2 — NAT SIP (SIP ALG)**: Molti router residenziali hanno "SIP ALG" che trasforma i pacchetti SIP → corrompe i header. Va disabilitato nel router. Da testare con `sngrep` su iMac.

**RISCHIO-3 — Concurrent calls**: `VoIPManager` gestisce una sola `active_call`. Per chiamate concorrenti (max_chiamate_contemporanee nella config = 2) serve refactoring con `dict[call_id, CallSession]`.

**RISCHIO-4 — Python 3.9 su iMac**: `voip.py` usa `asyncio.get_event_loop()` (deprecato in 3.10+) ma compatibile con 3.9. OK per iMac.

**NOTA — sip_client.py**: Il file `voice-agent/src/sip_client.py` è una versione stub più vecchia di `voip.py`. Non usarlo. Tutto il lavoro va su `voip.py`.

**NOTA — voice_pipeline.rs.backup**: Esiste un backup `voice_pipeline.rs.backup.20260218_135028`. Non toccare.

---

_Generato da codebase gap analysis agent — 2026-03-12_
