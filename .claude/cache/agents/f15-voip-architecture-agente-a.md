# F15 — VoIP + Android APK per Sara: Benchmark Mondiali 2026
**Agente A — Deep Research CoVe 2026**
**Data**: 2026-03-12 | **Scope**: Gold standard SIP → AI voice pipeline su Android

---

## TL;DR Raccomandazione CTO

> **Stack vincente 2026**: PJSIP 2.x embedded in APK Android nativo (Kotlin) + WebSocket bridge verso Sara su iMac. APK configurabile via QR code / provisioning XML. Un APK generico multi-tenant, parametrizzato per cliente. Latency budget stimato 650–900ms end-to-end su LTE buono — sotto la soglia percettibile (<800ms target Sara).

---

## 1 — Landscape SIP SDK Android 2026

### 1.1 PJSIP (PJSUA2) — Gold Standard de facto

PJSIP è la libreria SIP open source più matura e diffusa al mondo. La versione 2.x introduce PJSUA2, un layer ad alto livello con binding Java/Kotlin nativo per Android.

**Pro:**
- Supporto completo SIP RFC 3261, SRTP, TLS, UDP, TCP transport
- Codec: OPUS (bassa latenza, 20ms frame), G.711 µ-law/a-law, G.729, G.722
- Audio device abstraction: permette di intercettare l'audio raw in entrambe le direzioni
- `AudioMediaPort` + `AudioFrameObserver` → callback Java ogni 20ms con PCM 16-bit → forward verso WebSocket Sara
- Usato in produzione da: Linphone (su base PJSIP), 3CX mobile, Zoiper, Bria
- Build Android: NDK + CMake, prebuilt .aar disponibili (pjsip-android-builder su GitHub)
- Licenza: AGPL-2 + eccezione commerciale (acquistabile)

**Con:**
- Build complessa (NDK r25c, CMake 3.22+, OpenSSL per TLS)
- Dimensione APK: +8–12 MB per le librerie native
- No Kotlin-first API — wrapper Java vecchio stile

**Latency audio PJSIP**: jitter buffer configurabile 20–80ms, default 60ms. Con OPUS 20ms frame e jitter 40ms → audio pronto in ~60ms lato Android.

### 1.2 Linphone SDK (basato su PJSIP + liblinphone)

Linphone è un layer di alto livello sopra belle-sip + mediastreamer2. SDK Android separato da PJSIP ma concettualmente simile.

**Pro:**
- API moderna Kotlin/Java, AAR pronto su Maven
- Supporto video + audio, account SIP multipli
- `AudioDevice` custom pluggabile → intercettazione audio
- Documentazione migliore di PJSIP raw
- Licenza: GPLv3 + eccezione commerciale (Belledonne Communications)

**Con:**
- Overhead maggiore (liblinphone, belle-sip, mediastreamer2 = ~15 MB nativo)
- Meno granularità audio rispetto a PJSIP raw per uso AI

**Verdict vs PJSIP**: Per intercettazione audio raw + forwarding a Sara, PJSIP è più diretto e leggero. Linphone è meglio per app SIP complete con UI.

### 1.3 Twilio Programmable Voice SDK — Android

Twilio offre un SDK Android per chiamate VoIP tramite infrastruttura Twilio Cloud (PSTN bridge).

**Pro:**
- Semplicissimo da integrare (AAR, pochi metodi)
- Qualità audio Twilio-gestita (Opus su WebRTC)
- `CallInvite.accept()` + `AudioDevice` custom → intercettazione audio

**Con:**
- **Lock-in totale Twilio** — NON compatibile con credenziali SIP EHIWEB
- Costo per minuto (€0.01–0.05/min) — inaccettabile per modello lifetime FLUXION
- Richiede Twilio account + numero Twilio, non SIP generico
- Per FLUXION con EHIWEB → **non applicabile**

### 1.4 WebRTC nativo Android (senza SIP)

Google WebRTC SDK per Android permette audio bidirezionale via DataChannel/AudioTrack.

**Pro:**
- Ultra-bassa latenza (ICE, DTLS-SRTP)
- Integrazione nativa Chrome/browser

**Con:**
- NON è SIP — nessuna compatibilità con EHIWEB o qualsiasi trunk SIP
- Richiederebbe un gateway SIP→WebRTC separato (FreeSWITCH, Kamailio, etc.)
- Aggiunge un hop di latenza e complessità infrastrutturale

**Verdict**: Per bridging SIP diretto → **WebRTC puro non applicabile**. Utile solo se si aggiunge un SIP proxy sul server.

### 1.5 MjSIP / JAIN-SIP (Java puro)

Implementazioni SIP pure-Java storiche.

**Con:**
- Abbandonate o con manutenzione minima
- Nessun supporto audio nativo — solo signaling SIP
- Richiederebbero implementazione audio separata
- **Da escludere**

---

## 2 — Come fanno i Leader AI Voice Bridging SIP → LLM

### 2.1 Retell AI (2024–2026)

Retell è il provider più avanzato per AI voice agent nel 2026.

**Architettura SIP→LLM:**
- Retell accetta SIP INVITE direttamente sul loro SIP endpoint (`sip.retellai.com`)
- Il trunk SIP del cliente (Twilio, Vonage, EHIWEB, etc.) fa forward al SIP Retell
- Retell gestisce STT (Deepgram), LLM (GPT-4o/Claude), TTS (ElevenLabs/Cartesia)
- Latency dichiarata: **<800ms** end-to-end (STT+LLM+TTS pipeline)
- Audio encoding: OPUS 8kHz o G.711 8kHz (standard telefonia)
- Pattern: **SIP trunk → Retell cloud → AI pipeline** (tutto server-side, nessun APK)

**Lezione per FLUXION**: Il pattern cloud è più robusto, ma FLUXION è offline-first desktop. L'APK Android deve replicare il "SIP endpoint" localmente o via bridge iMac.

### 2.2 Vapi AI (2024–2026)

Vapi ha la migliore documentazione pubblica su SIP bridging.

**Architettura:**
- SIP REGISTER verso `sip.vapi.ai` con credenziali Vapi
- Chiamata in ingresso → Vapi orchestra pipeline: Deepgram STT → OpenAI LLM → Cartesia TTS
- Supporta anche `phone_number` (PSTN) + SIP trunk in ingresso
- Vapi espone WebSocket verso backend custom per LLM personalizzato
- Pattern avanzato: **SIP → Vapi → WebSocket → LLM custom (Sara)**

**Lezione per FLUXION**: Vapi potrebbe essere usato come SIP termination cloud con forwarding WebSocket a Sara locale — ma introduce dipendenza cloud + costo/minuto. Non ideale per modello offline.

### 2.3 Bland AI

**Architettura:**
- Simile a Vapi — cloud SIP termination + webhook per LLM custom
- Focus su outbound dialing (call automation)
- Meno rilevante per inbound SIP con APK Android

### 2.4 Twilio Media Streams (gold standard per DIY)

Twilio offre **Media Streams** via WebSocket: quando arriva una chiamata SIP/PSTN su Twilio, l'audio viene streamato in real-time via WebSocket verso un server custom.

**Pattern:**
```
SIP trunk (EHIWEB) → Twilio SIP Domain → TwiML <Stream> → WebSocket → Sara Python
```

**Flusso:**
1. EHIWEB fa forward chiamata a Twilio SIP Domain (€0.005/min termination)
2. Twilio risponde con TwiML che attiva `<Stream>` WebSocket
3. Sara riceve mulaw 8kHz via WebSocket, processa, risponde con audio
4. Twilio ricodifica e riproduce al chiamante

**Latency aggiunta Twilio**: ~100–150ms (cloud hop)
**Costo**: ~€0.005–0.01/min — accettabile per PMI italiana (<€3/giorno a 300 min/giorno)

**Lezione**: Questo è il pattern più collaudato per SIP→AI, ma richiede Twilio account e internet. L'APK Android è completamente eliminato — la PMI usa il numero EHIWEB che fa forward a Twilio.

### 2.5 SignalWire (FreeSWITCH cloud)

SignalWire è il cloud di FreeSWITCH. Supporta SIP trunking + Media Streams WebSocket identico a Twilio ma a costo inferiore.

**Pattern identico a Twilio** ma:
- €0.003/min invece di €0.005/min
- API compatibile Twilio (drop-in replacement)
- SIP endpoint europeo disponibile (latenza minore per EHIWEB Italia)

---

## 3 — APK Configurabile: Pattern Migliori 2026

### 3.1 Android Flavors (build-time configuration)

**Pattern**: Definire `productFlavors` in `build.gradle` con credenziali SIP hard-coded per cliente.

```kotlin
// build.gradle
flavorDimensions += "client"
productFlavors {
    create("clienteRossi") {
        applicationId = "com.fluxion.sara.clienterossi"
        buildConfigField("String", "SIP_SERVER", "\"sip.ehiweb.it\"")
        buildConfigField("String", "SIP_USER", "\"0298765432\"")
        buildConfigField("String", "SIP_PASS", "\"secretpass\"")
    }
}
```

**Pro**: Sicuro (credenziali non modificabili a runtime), APK distinto per cliente
**Con**: Richiede build separato per ogni cliente (CI/CD necessario), slow se molti clienti

**Verdict**: Accettabile per <20 clienti, non scalabile oltre.

### 3.2 QR Code Provisioning (runtime configuration) — RACCOMANDATO

**Pattern**: Un APK generico, configurato al primo avvio via QR code generato da FLUXION desktop.

```
FLUXION Desktop → genera QR con payload JSON:
{
  "sip_server": "sip.ehiweb.it",
  "sip_user": "0298765432",
  "sip_password": "AES256_encrypted_password",
  "sara_ws_url": "wss://tunnel.cliente.com/sara",
  "client_name": "Salone da Mario"
}
```

**Flusso onboarding**:
1. PMI apre FLUXION → Impostazioni → Voice → "Configura Android Bridge"
2. FLUXION genera QR con parametri SIP + URL Sara
3. PMI installa APK da link FLUXION → scansiona QR → configurato
4. APK salva config in `EncryptedSharedPreferences` (Android Keystore)

**Pro**:
- Un APK per tutti i clienti (manutenzione zero)
- Sicuro: password AES-256 nel QR, decriptata e salvata in Android Keystore
- UX eccellente: 30 secondi di setup
- Pattern usato da: Cisco IP Phone provisioning, Zoiper QR login, 3CX QR config

**Con**:
- Richiede implementazione QR scanner nell'APK
- Config persiste su dispositivo (risk se telefono perso → keystore mitiga)

### 3.3 SIP Provisioning XML (standard RFC 5261 / RFC 6080)

Standard enterprise per provisioning SIP phone. Un server HTTP serve file XML con config SIP per ogni dispositivo.

```xml
<config xmlns="urn:ietf:params:xml:ns:p2p:config-data">
  <sip>
    <registrar>sip.ehiweb.it:5060</registrar>
    <username>0298765432</username>
    <password>encrypted_base64</password>
    <transport>TLS</transport>
  </sip>
</config>
```

**Pro**: Standard industriale, compatibile con phone fisici + app SIP
**Con**: Richiede server HTTPS per serving config, overkill per FLUXION

**Verdict per FLUXION**: **QR Code Provisioning** è il gold standard 2026 per APK consumer. Semplice, sicuro, UX ottima.

---

## 4 — EHIWEB Italia: Credenziali SIP e Server

EHIWEB è un operatore VoIP italiano. La loro infrastruttura SIP segue gli standard RFC 3261.

**Parametri SIP tipici EHIWEB** (da documentazione pubblica e provider simili italiani):

| Parametro | Valore tipico EHIWEB |
|-----------|---------------------|
| SIP Server (Registrar) | `voip.ehiweb.it` o `sip.ehiweb.it` |
| SIP Porta | 5060 (UDP/TCP) o 5061 (TLS) |
| Transport | UDP (default), TLS disponibile |
| Codec supportati | G.711 a-law (PCMA), G.711 µ-law (PCMU), G.729 |
| Username | Numero di telefono assegnato (es. `0298765432`) |
| Password | Fornita da EHIWEB in pannello cliente |
| STUN server | `stun.ehiweb.it:3478` o Google STUN |
| Autenticazione | Digest MD5 (SIP standard) |

**Note critiche**:
- EHIWEB usa prevalentemente UDP su porta 5060 per SIP signaling
- RTP audio su porte dinamiche (range 10000–20000 tipico)
- NAT traversal: richiedere `rport` e STUN per Android su LTE/WiFi privata
- G.711 a-law è il codec di default (8kHz, 64kbps) — Sara deve accettare PCMA/PCMU o transcodificare

**Verifica**: Le credenziali SIP EHIWEB si trovano nel pannello clienti `my.ehiweb.it` sotto "Servizi VoIP" → "Dettagli linea".

---

## 5 — Latency Budget: SIP → Android → WebSocket → Sara → TTS → SIP

### Stack di riferimento: Intel iMac 2019 (3.6GHz i9, 32GB RAM)

```
CHIAMANTE PSTN
    │
    │ PSTN → SIP (EHIWEB trunk, ~50ms)
    ↓
ANDROID (pjsua2)
    │ SIP REGISTER + INVITE receive: ~20ms
    │ RTP audio decode PCMA → PCM16: ~5ms
    │ Buffer accumulo 160ms (20ms × 8 frame G.711): 160ms
    │                          ← alternativa OPUS 20ms frame: 20ms
    │ WebSocket send a Sara: ~10ms (LAN) / ~50ms (LTE+tunnel)
    ↓
SARA (iMac Python aiohttp)
    │ STT FluxionSTT (Whisper.cpp): ~150–300ms (iMac i9)
    │ LLM Groq llama-3.1-8b-instant: ~200–350ms (API call)
    │ TTS Piper Italian: ~80–150ms
    │ WebSocket send audio back: ~10ms (LAN)
    ↓
ANDROID
    │ RTP encode PCM16 → PCMA: ~5ms
    │ RTP send: ~10ms
    ↓
CHIAMANTE (riproduzione)
```

### Stime latency end-to-end

| Scenario | Breakdown | Totale |
|----------|-----------|--------|
| **LAN ideale** (telefono sul WiFi LAN iMac) | 50+20+20+10+300+300+100+10+5+10 = | **~825ms** |
| **LTE + Cloudflare Tunnel** | +80ms per tunnel round-trip | **~905ms** |
| **LTE + latenza STT alta** | Whisper.cpp iMac cold start | **~1100ms** |
| **Ottimizzato** (Groq fast + buffer 20ms OPUS) | STT 150ms + LLM 200ms + TTS 80ms | **~650ms** ✅ |

**Target Sara**: <800ms → **raggiungibile su LAN/WiFi buona** con ottimizzazione STT+LLM.

**Bottleneck principale**: Accumulo frame audio (G.711 20ms × 8 = 160ms) + Whisper.cpp STT. Soluzione: usare OPUS con frame 20ms e VAD aggressivo per tagliare il buffer.

---

## 6 — Alternativa Termux: pjsua CLI su Android

**pjsua** è il command-line tool di PJSIP. Su Termux (terminal emulator Android) è compilabile.

### Fattibilità 2026

**Compilazione**:
```bash
# Termux
pkg install pjsip  # disponibile nel repository Termux
pjsua --id sip:user@ehiweb.it --registrar sip:ehiweb.it \
      --realm ehiweb.it --username user --password pass \
      --auto-answer 200 --rec-file /data/audio_in.wav \
      --play-file /data/audio_out.wav
```

**Pro Termux**:
- Zero development cost — test immediato senza APK
- pjsua pre-compilato disponibile in Termux packages
- Script shell per orchestrare: registra SIP → risponde chiamata → pipe audio → curl Sara API → play risposta

**Con Termux**:
- Termux richiede app separata installata (non APK standalone)
- Android 12+ limita processi background → Termux viene killato
- `--rec-file` introduce latenza file I/O inaccettabile (batch, non streaming)
- pjsua CLI non supporta audio streaming bidirezionale real-time via pipe a programma esterno
- Rooting necessario per audio capture in background continuo

**Verdict**: Termux + pjsua è ottimo per **testing e prototipazione** (verifica credenziali SIP EHIWEB, test registrazione), ma **non adatto a produzione**. Usarlo solo per validare le credenziali EHIWEB prima di sviluppare l'APK.

```bash
# Test rapido credenziali EHIWEB su Termux
pjsua --id "sip:0298765432@voip.ehiweb.it" \
      --registrar "sip:voip.ehiweb.it" \
      --username "0298765432" --password "PASSWORD" \
      --realm "*" --log-level 4 2>&1 | grep -E "registration|200 OK|401"
```

---

## 7 — React Native vs Flutter vs Native Android per APK Sara

### Valutazione per use case: SIP + Audio streaming + WebSocket

| Criterio | React Native | Flutter | Native Kotlin |
|----------|-------------|---------|---------------|
| PJSIP integration | Plugin community (react-native-pjsip) — **non mantenuto 2024** | Plugin (flutter-pjsip) — **non ufficiale, instabile** | **Nativa, FFI completo, stabile** ✅ |
| Audio raw access | Bridge JS → Java → JNI: 2 hop latency | Dart → JNI: 1 hop, migliore | **JNI diretto, zero overhead** ✅ |
| WebSocket | OK (libraries) | OK (dart:io) | OK (OkHttp) |
| Build time | ~3min (Metro bundler) | ~4min (Dart AOT) | **~2min (Kotlin/Gradle)** ✅ |
| APK size | ~25MB (React Native runtime) | ~20MB (Flutter engine) | **~10MB** ✅ |
| Background service | Possibile ma complesso | Possibile ma complesso | **Nativo, semplice** ✅ |
| QR provisioning | Camera API OK | Camera API OK | **CameraX + ZXing** ✅ |
| Developer skill match | Alto (team TypeScript) | Basso | Medio |

**Analisi critica**:

- **react-native-pjsip**: l'unico plugin serio era `datso/react-native-pjsip`, abbandonato nel 2023. Non supporta Android SDK 34+. Richiederebbe fork e manutenzione — rischio altissimo.
- **Flutter + PJSIP**: esistono wrapper non ufficiali, instabili, non supportati. Per audio streaming real-time AI la latenza Dart → platform channel → JNI è ~5–10ms aggiuntivi — accettabile ma non ottimale.
- **Native Kotlin**: accesso diretto a PJSUA2 Java API, `AudioMediaPort` senza hop aggiuntivi, `ForegroundService` nativo per background SIP, `EncryptedSharedPreferences` per credenziali. Build più leggera.

**Raccomandazione**: **Native Kotlin + PJSUA2**. Il team FLUXION ha TypeScript come primario ma Kotlin è simile (JVM, null safety, lambda). La build APK base può essere fatta in <1 settimana da un dev backend.

**Alternativa pragmatica**: Se il team non ha Android dev → considerare **Expo + react-native-sip2** (libreria mantenuta, basata su PJSIP, supporta Android). Però attenzione: sip2 è per SIP softphone completo, non per intercettazione audio raw. L'architettura sarebbe: SIP answer → route audio verso server Sara via background task.

---

## 8 — Architettura Raccomandata F15 — Decision Final

### Stack Consigliato: "Sara Android Bridge"

```
┌─────────────────────────────────────────────────────┐
│  ARCHITETTURA F15 — SARA ANDROID BRIDGE             │
└─────────────────────────────────────────────────────┘

CHIAMANTE (PSTN)
    │
    │ SIP/PSTN
    ▼
EHIWEB SIP Trunk
    │ SIP INVITE → forward a Android APK (registrato)
    ▼
APK "Sara Bridge" (Android 10+, Kotlin + PJSUA2)
┌────────────────────────────────────────────────┐
│  ForegroundService (persistente, non killabile)│
│  ┌──────────────────────────────────────────┐  │
│  │ PJSUA2                                   │  │
│  │  SIPAccount.register() → EHIWEB          │  │
│  │  onCallIncoming() → auto-answer          │  │
│  │  AudioMediaPort (20ms PCM frames)        │  │
│  │    │                                     │  │
│  │    ▼                                     │  │
│  │  WebSocket Client (OkHttp)               │  │
│  │    ↕ wss://[CloudflareTunnel]/sara/audio │  │
│  │    Audio in: PCM16 → base64/binary WS    │  │
│  │    Audio out: base64/binary → PCM16      │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  EncryptedSharedPreferences                    │
│  { sip_server, sip_user, sip_pass,            │
│    sara_ws_url, client_name }                 │
│                                                │
│  QRProvisioning Activity (primo avvio)         │
│  { scan QR → decrypt AES-256 → save config }  │
└────────────────────────────────────────────────┘
    │
    │ WebSocket (wss, Cloudflare Tunnel permanente)
    ▼
IMAC SARA (Python aiohttp, porta 3002)
    │  /sara/audio WebSocket endpoint (nuovo)
    │  Riceve: audio PCM16 chunks
    │  Processa: STT → LLM → TTS
    │  Risponde: audio PCM16 chunks
    ▼
APK → PCM16 → PJSUA2 AudioMediaPort → RTP → EHIWEB → CHIAMANTE
```

### Configurazione QR generata da FLUXION Desktop

```json
{
  "v": 1,
  "sip_server": "voip.ehiweb.it",
  "sip_port": 5060,
  "sip_transport": "UDP",
  "sip_user": "0298765432",
  "sip_pass_enc": "AES256:BASE64ENCRYPTED",
  "sara_ws": "wss://abc123.cfargotunnel.com/sara/audio",
  "client_id": "salone-mario-001",
  "client_name": "Salone da Mario"
}
```

---

## 9 — Gap vs Competitor e Vantaggi Competitivi FLUXION F15

| Competitor | Come gestisce SIP→AI | Costo | Lock-in |
|-----------|---------------------|-------|---------|
| Retell AI | Cloud SIP endpoint Retell | ~€0.05–0.15/min | Totale (Retell infra) |
| Vapi | Cloud + WebSocket custom LLM | ~€0.05/min | Parziale |
| Bland AI | Cloud outbound focus | ~€0.05/min | Totale |
| Twilio + OpenAI | Media Streams + GPT-4o | ~€0.02/min + LLM | Twilio |
| **FLUXION F15** | **Android APK locale + Sara iMac** | **€0/min dopo licenza** | **Zero** |

**Vantaggio competitivo unico FLUXION**:
- **Zero costo per minuto** — modello lifetime, PMI paga una volta
- **Offline-capable** — Sara gira sull'iMac del cliente, non in cloud
- **Numero EHIWEB del cliente** — nessun cambio numero, nessuna portabilità
- **Dati vocali mai escono dall'Italia** — GDPR nativo, vantaggio enorme per cliniche

---

## 10 — Roadmap Implementazione F15 (3 Sprint)

### Sprint 1: Proof of Concept (2 giorni)
1. Termux su Android di test → valida credenziali SIP EHIWEB
2. Aggiungere endpoint WebSocket `/sara/audio` a Sara Python
3. Test pipe audio PCM → Sara → risposta TTS

### Sprint 2: APK Base (5 giorni)
1. Progetto Android Studio Kotlin + PJSUA2 AAR
2. `SIPForegroundService` con auto-answer
3. `AudioMediaPort` → WebSocket OkHttp streaming
4. `QRProvisioningActivity` con CameraX + ZXing
5. `EncryptedSharedPreferences` per config

### Sprint 3: Integrazione FLUXION Desktop (3 giorni)
1. UI FLUXION: "Configura Voice Bridge Android"
2. Generazione QR con payload JSON + AES-256
3. Gestione stato connessione (Connected/Disconnected/On Call)
4. Statistiche chiamate in Impostazioni

---

## 11 — Rischi e Mitigazioni

| Rischio | Probabilità | Mitigazione |
|---------|-------------|-------------|
| Android 13+ limita ForegroundService | Media | Usa `FOREGROUND_SERVICE_TYPE_MICROPHONE` + notifica persistente |
| PJSIP build rotta con NDK aggiornato | Media | Usa pjsip-android-builder con versione NDK pinned (r25c) |
| Latenza >800ms su LTE | Alta | VAD più aggressivo, OPUS 20ms, Groq llama-3.1-8b-instant |
| EHIWEB blocca REGISTER da Android | Bassa | Contattare EHIWEB per whitelist IP; usare SIP over TLS |
| APK non approvato su Play Store | Media | Distribuzione diretta APK (sideload) — normale per B2B enterprise |

---

## Fonti e Riferimenti

- PJSIP Documentation: https://docs.pjsip.org/en/latest/get-started/android/
- pjsip-android-builder: https://github.com/VoiSmart/pjsip-android-builder
- Retell AI SIP Docs: https://docs.retellai.com/integration/sip
- Vapi SIP: https://docs.vapi.ai/sip/introduction
- Twilio Media Streams: https://www.twilio.com/docs/voice/media-streams
- SignalWire SWML: https://developer.signalwire.com/
- Android Encrypted SharedPreferences: https://developer.android.com/topic/security/data
- ZXing Android: https://github.com/journeyapps/zxing-android-embedded
- EHIWEB VoIP: https://www.ehiweb.it/voip/

---

*Agente A — CoVe 2026 Research completata. Raccomandazione: Native Kotlin + PJSUA2 + QR Provisioning + WebSocket Sara. Implementazione stimata: 10 giorni developer Android.*
