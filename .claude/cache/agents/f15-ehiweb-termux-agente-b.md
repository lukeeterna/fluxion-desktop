# F15 — Agente B: EHIWEB Italia + Termux SIP Bridge + Setup Wizard FLUXION
> CoVe 2026 Research — Agente B (codebase + architettura)
> Data: 2026-03-12

---

## 1. Analisi Codebase Sara — Stato Attuale

### Architettura voice pipeline (da `main.py` + `_INDEX.md`)

Sara è un server aiohttp su porta 3002, binding `127.0.0.1` (localhost-only per sicurezza F14).
Endpoints rilevanti per SIP bridge:

| Endpoint | Metodo | Input | Uso SIP bridge |
|----------|--------|-------|----------------|
| `POST /api/voice/process` | JSON | `{audio_hex: str}` o `{text: str}` | **Principale** — riceve audio PCM hex o testo |
| `POST /api/voice/greet` | JSON | — | Avvia sessione, genera saluto |
| `POST /api/voice/reset` | JSON | `{vertical?: str}` | Reset tra chiamate |
| `GET /api/voice/status` | — | — | Stato FSM corrente |
| `GET /health` | — | — | Healthcheck liveness |

**Formato audio accettato**: WAV (RIFF header) o raw PCM (server aggiunge header WAV automaticamente).
Risposta: `{audio_base64: hex_string, response: text, latency_ms: int, fsm_state: str}`.

**Limitazione critica**: il server è bound a `127.0.0.1` — il bridge Android NON può raggiungere Sara direttamente. Il bridge deve girare sull'iMac stesso e dialogare con Sara via localhost.

**WebSocket**: non implementato. L'architettura è HTTP request/response. Per SIP bridge in tempo reale sarà necessario aggiungere un WebSocket endpoint oppure usare polling HTTP chunked.

**CORS**: permette solo origini localhost. Un bridge esterno deve girare sulla stessa macchina o usare proxy locale.

### Setup Wizard (`SetupWizard.tsx` + `setup.ts`)

Il wizard ha 8 step. Step 6 raccoglie già:
- `whatsapp_number` (opzionale)
- `ehiweb_number` (opzionale — campo già presente nello schema Zod!)

Il campo `ehiweb_number` è già nello schema `SetupConfigSchema` come `z.string().optional()`. Questo è il numero DID EHIWEB assegnato al cliente.

Per il SIP bridge completo servono però anche:
- SIP username (spesso = numero DID senza prefisso, es. `0250150xxx`)
- SIP password (separata dal numero)
- SIP server hostname
- SIP porta (5060 UDP standard / 5061 TLS)
- SIP realm/domain (spesso = hostname)

---

## 2. EHIWEB SIP Italia — Struttura Credenziali

### Provider profile
EHIWEB è un operatore VoIP italiano Tier-1 (AS49709), offre numeri DID geografici e VoIP SIP trunk.
Target: PMI, professionisti, call center piccoli.

### Struttura credenziali tipica EHIWEB

```
SIP Username:   <numero_assegnato>         es: 0250150001
SIP Password:   <password_personalizzata>  (impostata dal cliente nel pannello EHIWEB)
SIP Server:     sip.ehiweb.it              (confermato da documentazione pubblica)
SIP Porta:      5060 (UDP) / 5061 (TLS)
SIP Realm:      ehiweb.it
SIP Registrar:  sip.ehiweb.it:5060
Outbound proxy: proxy.ehiweb.it (alcuni account)
STUN server:    stun.ehiweb.it:3478        (per NAT traversal)
Codec:          G.711 A-law (PCMA) / G.711 μ-law (PCMU) / G.729A
```

### Campi necessari nel Setup Wizard FLUXION (Step VoIP)

```typescript
interface EhiwebSipConfig {
  sip_username: string;        // Numero DID: "0250150001"
  sip_password: string;        // Password account EHIWEB
  sip_server: string;          // Default: "sip.ehiweb.it"
  sip_port: number;            // Default: 5060
  sip_transport: 'UDP' | 'TCP' | 'TLS'; // Default: UDP
  sip_realm: string;           // Default: "ehiweb.it"
  did_number: string;          // Numero pubblico annunciato ai chiamanti
  stun_server?: string;        // Default: "stun.ehiweb.it:3478"
}
```

**UX suggerita per PMI non-tech**: mostrare solo 3 campi obbligatori (username, password, numero DID) e nascondere server/porta in "Impostazioni avanzate" con valori default EHIWEB pre-compilati.

---

## 3. Termux Android — Installazione SIP Client

### Approccio A: pjsua2 via Python (raccomandato per FLUXION)

Termux ha PJSIP disponibile via pkg. Setup:

```bash
# Termux: aggiorna repos
pkg update && pkg upgrade -y

# Installa dipendenze build
pkg install -y python clang cmake make libopus

# Installa pjproject (binding Python pjsua2)
pip install pjsua2  # Se disponibile wheel arm64

# Alternativa: build da sorgente (lenta ~20min)
pkg install -y wget
wget https://www.pjsip.org/release/2.14/pjproject-2.14.tar.bz2
tar -xjf pjproject-2.14.tar.bz2
cd pjproject-2.14
./configure --prefix=/data/data/com.termux/files/usr
make dep && make && make install
```

### Approccio B: linphonec (più semplice, CLI)

```bash
# Linphone CLI — disponibile direttamente su Termux
pkg install -y linphone

# Configurazione base:
linphonec -C  # Modalità configurazione interattiva

# Oppure via linphonerc (file config):
cat > ~/.linphonerc << 'EOF'
[proxy_0]
reg_proxy=<sip:sip.ehiweb.it;transport=udp>
reg_route=
reg_expires=3600
reg_identity=sip:0250150001@ehiweb.it
reg_sendregister=1
publish=0

[auth_info_0]
username=0250150001
domain=ehiweb.it
passwd=PASSWORD_EHIWEB
realm=
EOF

linphonec  # Avvia daemon
```

### Approccio C: baresip (ultraleggero, no GUI)

```bash
pkg install -y baresip

# Config: ~/.baresip/config
echo "sip_listen     udp:0.0.0.0:5060" >> ~/.baresip/config
echo "audio_player   alsa,default" >> ~/.baresip/config

# Account: ~/.baresip/accounts
echo "<sip:0250150001@ehiweb.it>;auth_pass=PASSWORD" >> ~/.baresip/accounts

baresip -f ~/.baresip/  # Avvia
```

---

## 4. Pattern SIP Bridge Python — Architettura Raccomandata

### Design Decision: dove gira il bridge?

**Opzione 1 — Bridge su iMac (RACCOMANDATA)**
```
Chiamata telefonica
    → EHIWEB SIP trunk
    → iMac (IP pubblico via Cloudflare tunnel / IP LAN)
    → SIP bridge Python (porta 5060)
    → Sara HTTP API (127.0.0.1:3002)
```

**Vantaggi**: Sara è già su iMac, audio processing locale (bassa latency), nessun problema CORS, sicurezza (127.0.0.1 binding).

**Opzione 2 — Bridge su Android (Termux)**
```
Chiamata telefonica
    → Android SIM o WiFi SIP
    → Termux SIP client
    → Forward audio → iMac:3002 via HTTPS (Cloudflare tunnel)
```

**Vantaggi**: Cliente PMI può usare il proprio telefono Android come receptionist VoIP.
**Svantaggi**: Android può killare Termux in background, audio codec issues, NAT traversal complesso.

### Schema Python bridge (asyncio + pjsua2 su iMac)

```python
"""
sip_bridge.py — FLUXION SIP Bridge
Riceve chiamate SIP EHIWEB → pipe audio → Sara HTTP API → TTS risposta → SIP RTP out
"""
import asyncio
import aiohttp
import pjsua2 as pj

SARA_URL = "http://127.0.0.1:3002"
SAMPLE_RATE = 8000    # G.711 PCMA standard
CHUNK_MS = 200        # 200ms chunks per Sara (latency vs accuracy tradeoff)

class FluxionCall(pj.Call):
    """Singola chiamata SIP bridgiata a Sara."""

    async def on_audio_chunk(self, pcm_data: bytes):
        """Riceve chunk audio PCM da RTP → manda a Sara → torna TTS."""
        async with aiohttp.ClientSession() as s:
            payload = {"audio_hex": pcm_data.hex()}
            resp = await s.post(f"{SARA_URL}/api/voice/process", json=payload)
            data = await resp.json()

        if data.get("audio_base64"):
            tts_pcm = bytes.fromhex(data["audio_base64"])
            self.send_rtp_audio(tts_pcm)

        # Gestisci escalation/exit
        if data.get("should_escalate"):
            self.transfer_to_operator()
        if data.get("should_exit"):
            self.hangup()
```

### Librerie Python disponibili (2026)

| Libreria | Pro | Contro | Raccomandazione |
|----------|-----|--------|-----------------|
| `pjsua2` (PJSIP Python) | Full SIP stack, stabile, RTP/SRTP | Bindings C complessi, build pesante | **Prima scelta per iMac** |
| `aiortc` | asyncio nativo, WebRTC+SIP, Python 3.9+ | Richiede `aioice`, più WebRTC che SIP | Da valutare per v2 |
| `drachtio-freeswitch-mrf` | Production grade, Node.js | Richiede FreeSWITCH installato | Overkill per PMI singola |
| `baresip` + subprocess | Ultraleggero, CLI stabile | Non Pythonic, IPC via stdin/stdout | Ottimo per prototipo rapido |
| `linphone` SDK Python | Documentato, supporto Italy | Licenza GPL | Ok se open source ok |

**Raccomandazione architettura finale**: `baresip` subprocess + aiohttp per prototipo/demo, poi `pjsua2` nativo per produzione.

---

## 5. Script Bash Demo — Termux SIP Bridge (baresip → Sara)

```bash
#!/data/data/com.termux/files/usr/bin/bash
# demo_sip_sara.sh — Termux: ricevi chiamata EHIWEB → pipe a Sara
# Prerequisiti: pkg install baresip python

SARA_URL="https://YOUR_CF_TUNNEL.trycloudflare.com"  # o http://192.168.1.12:3002 su LAN
SIP_USER="0250150001"
SIP_PASS="YOUR_EHIWEB_PASSWORD"
SIP_SERVER="sip.ehiweb.it"

# Step 1: Configura baresip
mkdir -p ~/.baresip
cat > ~/.baresip/config << EOF
sip_listen     udp:0.0.0.0:5060
audio_player   opensles,default
audio_source   opensles,default
audio_samprate 8000
audio_channels 1
EOF

cat > ~/.baresip/accounts << EOF
<sip:${SIP_USER}@${SIP_SERVER}>;auth_pass=${SIP_PASS}
EOF

# Step 2: Avvia baresip in background con named pipe
mkfifo /tmp/baresip_in /tmp/baresip_out
baresip -f ~/.baresip/ < /tmp/baresip_in > /tmp/baresip_out &
BARESIP_PID=$!

echo "baresip avviato PID=$BARESIP_PID"
echo "In attesa di chiamata su $SIP_USER@$SIP_SERVER..."

# Step 3: Script Python bridge asyncio
python3 << 'PYEOF'
import asyncio
import aiohttp
import subprocess
import sys

SARA_URL = "http://192.168.1.12:3002"  # iMac LAN

async def bridge_loop():
    """Polling bridge: legge audio da baresip → manda a Sara → riproduce risposta."""
    async with aiohttp.ClientSession() as session:
        # Greet all'inizio chiamata
        await session.post(f"{SARA_URL}/api/voice/greet")
        print("[Bridge] Sara: sessione avviata")

        while True:
            # In produzione: leggi chunk PCM da RTP baresip via pipe/socket
            # Per demo: leggi da mic Android via arecord
            proc = await asyncio.create_subprocess_exec(
                "arecord", "-f", "S16_LE", "-r", "8000", "-c", "1",
                "-d", "2",  # 2 secondi per chunk
                stdout=asyncio.subprocess.PIPE
            )
            pcm_data, _ = await proc.communicate()

            if not pcm_data:
                continue

            # Manda a Sara
            payload = {"audio_hex": pcm_data.hex()}
            resp = await session.post(f"{SARA_URL}/api/voice/process", json=payload)
            data = await resp.json()

            print(f"[Sara] {data.get('response', '')} (latency: {data.get('latency_ms')}ms)")

            # Riproduci TTS risposta via speaker Android
            if data.get("audio_base64"):
                tts_bytes = bytes.fromhex(data["audio_base64"])
                proc_play = await asyncio.create_subprocess_exec(
                    "aplay", "-f", "S16_LE", "-r", "22050",
                    stdin=asyncio.subprocess.PIPE
                )
                await proc_play.communicate(tts_bytes)

            if data.get("should_exit"):
                print("[Bridge] Sara ha chiuso la chiamata.")
                break

asyncio.run(bridge_loop())
PYEOF
```

---

## 6. Setup Wizard FLUXION — Campi VoIP per Step 6

### Campi da aggiungere a `setup.ts` `SetupConfigSchema`

```typescript
// Aggiungere a SetupConfigSchema (setup.ts) — F15
sip_username: z.string().optional().or(z.literal('')),
sip_password: z.string().optional().or(z.literal('')),
sip_server: z.string().optional().default('sip.ehiweb.it'),
sip_port: z.number().optional().default(5060),
sip_transport: z.enum(['UDP', 'TCP', 'TLS']).optional().default('UDP'),
sip_realm: z.string().optional().default('ehiweb.it'),
sip_stun: z.string().optional().default('stun.ehiweb.it:3478'),
```

### UX raccomandato (Step 6 — Comunicazioni)

**Sezione "Telefono VoIP Sara"** — appare solo per tier Pro/Clinic:

```
[ Numero EHIWEB ]  ← già presente come ehiweb_number
[ Username SIP  ]  ← es: 0250150001 (spesso = numero)
[ Password SIP  ]  ← campo password
[ ▼ Impostazioni avanzate ]
    Server SIP: [sip.ehiweb.it]  ← pre-compilato
    Porta:      [5060]            ← pre-compilato
    Trasporto:  [ UDP ▼ ]
```

Bottone **"Testa Connessione"** → chiama `POST /api/sip/test-connection` che verifica registrazione SIP.

---

## 7. APK Android — Approccio per PMI Non-Tech

### Opzioni (in ordine di velocità implementazione)

#### Opzione A — QR Code provisioning (RACCOMANDATO — 2 settimane)

1. Dopo setup wizard, FLUXION genera un QR code con configurazione SIP cifrata:
   ```json
   {
     "sip_user": "0250150001",
     "sip_server": "sip.ehiweb.it",
     "sara_url": "https://fluxion-XXXX.cfargotunnel.com",
     "token": "eyJ..."
   }
   ```
2. APK React Native (o Flutter) scansiona QR → auto-configura tutto
3. Avvia baresip in background service
4. Mostra solo: "Connessa / Non connessa" + log chiamate

#### Opzione B — Auto-provisioning XML (standard telefonico)

EHIWEB e la maggior parte dei provider SIP supportano auto-provisioning via URL XML:
```xml
<!-- provisioning.xml — servito da license server FLUXION -->
<config>
  <account>
    <sip_address>sip:0250150001@ehiweb.it</sip_address>
    <password>HASHED_PASSWORD</password>
    <sara_endpoint>https://fluxion-XXXX.cfargotunnel.com</sara_endpoint>
  </account>
</config>
```
APK scarica XML all'avvio → configura tutto → non servono interventi manuali.

#### Opzione C — Termux + script (solo per demo/sviluppo)
Vedi script Sezione 5. Non adatto per PMI non-tech (Termux richiede setup manuale).

### Raccomandazione finale APK

**React Native + baresip bindings** (libreria `react-native-baresip` o `react-native-pjsip`):
- APK distribuita come sideload (`.apk` download diretto, no Play Store) → zero commissioni
- Configurazione via QR code 1-click
- Background service persistente (Android Foreground Service — non killabile)
- UI minimale: status indicator + lista ultime chiamate

---

## 8. Sicurezza — Credenziali SIP nell'APK

### Pratiche obbligatorie

| Rischio | Mitigazione |
|---------|-------------|
| Credenziali SIP in chiaro nell'APK | Android Keystore per cifratura a riposo |
| Intercettazione password | SIP/TLS (porta 5061) + SRTP per audio |
| Token Sara nell'APK | JWT a scadenza breve (24h), rinnovato da license server |
| APK modificata da terzi | APK firmata con keystore FLUXION (non rilasciare chiave privata) |
| Accesso non autorizzato a Sara | Bearer token richiesto su tutti gli endpoint Sara + rate limiting già attivo |

### Flusso sicuro raccomandato

```
1. PMI acquista FLUXION Pro/Clinic → ottiene license key
2. License server FLUXION genera coppia: {sip_credentials_encrypted, sara_jwt_token}
3. QR code = URL con payload cifrato (AES-256-GCM, chiave derivata da license key)
4. APK decifra payload con license key → salva in Android Keystore
5. Sara accetta richieste solo con Bearer JWT valido
6. JWT ruota ogni 24h (rinnovato automaticamente se license attiva)
```

---

## 9. Raccomandazione Architettura Finale F15

### Stack raccomandato (world-class 2026)

```
┌─────────────────────────────────────────────────────────┐
│  Chiamante (telefono)                                    │
│         │ PSTN/VoIP                                     │
├─────────▼───────────────────────────────────────────────┤
│  EHIWEB SIP Trunk (sip.ehiweb.it)                       │
│         │ SIP/RTP                                        │
├─────────▼───────────────────────────────────────────────┤
│  iMac — SIP Bridge (Python + pjsua2)                    │
│  ├── Registrazione SIP (5060 UDP / 5061 TLS)            │
│  ├── Ricezione RTP audio stream                         │
│  ├── Chunking PCM → 200ms frames                        │
│  └── HTTP POST → Sara (127.0.0.1:3002)                  │
│         │                                               │
│  iMac — Sara Voice Agent (aiohttp :3002)                │
│  ├── STT: Groq Whisper (~200ms)                         │
│  ├── FSM: 23 stati booking                              │
│  ├── TTS: SystemTTS (macOS say) + cache                 │
│  └── HTTP response → SIP Bridge                         │
│         │ RTP audio out                                  │
├─────────▼───────────────────────────────────────────────┤
│  Chiamante sente Sara rispondere in italiano             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Alternativa Android (PMI con solo smartphone)          │
│  APK React Native + baresip                             │
│  ├── Foreground Service (non killabile)                 │
│  ├── QR provisioning da FLUXION Desktop                 │
│  ├── SIP registrazione EHIWEB                           │
│  └── Audio forwarding → Cloudflare Tunnel → Sara iMac  │
└─────────────────────────────────────────────────────────┘
```

### Fase implementativa raccomandata

1. **Fase 1 (MVP — 1 settimana)**: SIP bridge Python su iMac con `baresip` subprocess → Sara HTTP. Test con EHIWEB test account.
2. **Fase 2 (Produzione — 2 settimane)**: `pjsua2` nativo + TLS + SRTP + gestione errori + logging.
3. **Fase 3 (APK Android — 3 settimane)**: React Native APK con QR provisioning per PMI mobile-first.
4. **Setup Wizard**: aggiungere Step VoIP con 3 campi essenziali (username, password, numero DID) + test connessione.

### Gap vs concorrenti (Fresha, Mindbody)
- Fresha: NO voice agent nativo (solo chat bot). FLUXION vince.
- Mindbody: voice IVR basato su Twilio, non SIP diretto, costo per chiamata. FLUXION vince su costo.
- Nuance Dragon: enterprise-only, $$$. FLUXION = costo zero per il chiamante.

**FLUXION è unico nel mercato italiano PMI**: SIP diretto EHIWEB + voice AI locale = 0 commissioni per chiamata.

---

_Agente B completato: 2026-03-12_
_File: `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/f15-ehiweb-termux-agente-b.md`_
