# FLUXION - Deployment & Integration Guide

> **Version**: 1.0 | **Updated**: 15 Gennaio 2026
> **Source**: Perplexity AI + Claude Code collaboration

---

## Pre-Production Checklist

### Backend Services

- [ ] FastAPI voice-agent avviabile standalone con `uvicorn src.api:app --port 3002`
- [ ] HTTP Bridge Node.js avviabile con `npm start` (porta 3001)
- [ ] Entrambi rispondono a `/health` endpoint con status OK
- [ ] Logging configurato (file + stdout)
- [ ] Error handling per timeout/connection errors
- [ ] SQLite database migrations eseguite
- [ ] CORS configurato per Tauri IPC

### Frontend/Desktop

- [ ] Tauri app avviabile con `npm run tauri dev`
- [ ] React components render senza errori
- [ ] Tauri IPC commands functional (es: `invoke('check_available_slots')`)
- [ ] SQLite read/write funzionante da Rust backend
- [ ] Hot reload working during development

### Database

- [ ] SQLite file location: `~/Library/Application Support/fluxion/` (macOS)
- [ ] All migrations run successfully
- [ ] Seed data inserito per verticale selezionato
- [ ] Indexes creati per performance
- [ ] Backup strategy configurato (rsync nightly to ~/Backups/)

### External Integrations

- [ ] Groq API key valida e testata
- [ ] Groq rate limit: 30 req/min (free tier) - ACCEPTABLE
- [ ] n8n instance available (can be localhost)
- [ ] n8n webhook per WhatsApp configurato
- [ ] Webhook URL raggiungibile da n8n
- [ ] WhatsApp Business Account API token valido
- [ ] Piper TTS installato (locale o API key configurato)
- [ ] Whisper STT configurato (OpenAI API o local)

### MCP Server (Future)

- [ ] MCP server codebase pronto (ma non deployato)
- [ ] Tools: search_clienti, create_appuntamento, get_disponibilita, get_faq
- [ ] Resources: clienti, servizi, faq
- [ ] Test connection with Claude Code (quando pronto)

---

## Performance Benchmarks & Latency Targets

### L0-L4 Response Time SLA

**Definizione SLA:** "Utente dice comando -> riceve risposta audio" (end-to-end)

| Layer | Operation | Target | Current Est. | Status |
|-------|-----------|--------|--------------|--------|
| **L0** | Regex pattern match | <1ms | <0.5ms | OK |
| **L1** | Intent classification (spaCy) | <5ms | ~3ms | OK |
| **L2** | Slot filling NER | <10ms | ~5ms | OK |
| **L3** | FAISS semantic search (top-3) | <50ms | ~30-40ms | OK |
| **L4** | Groq Llama 3.1 completion | <500ms | ~200-300ms | OK |
| **L4+TTS** | Groq + TTS (Piper) | <1500ms | ~800-1000ms | Monitor |
| **TTS** | Piper audio generation | <200ms | ~100-150ms | OK |
| **STT** | Whisper transcription | <500ms | ~300-400ms | OK |
| **E2E** | Voice in -> Voice out | <2000ms | ~1500ms | ACCEPTABLE |

### Threshold Decisions

- **L3 score < 0.7** -> Skip FAQ, go to L4 (LLM fallback)
- **Response > 1s** -> Playback "Sto elaborando..." (UX feedback)
- **LLM timeout > 2s** -> Return cached FAQ or error message
- **STT timeout > 1s** -> Ask user to repeat

### Database Query Performance

| Query | Target | Est. | Status |
|-------|--------|------|--------|
| `SELECT * FROM clienti WHERE telefono = ?` | <5ms | <2ms | Indexed |
| `SELECT * FROM appuntamenti WHERE data = ? AND operatore_id = ?` | <10ms | ~5ms | Indexed |
| `SELECT * FROM faq_entries WHERE categoria_pmi = ? (LIMIT 100)` | <20ms | ~10ms | Indexed |
| `SELECT * FROM chat_history WHERE cliente_id = ? (LIMIT 50)` | <15ms | ~8ms | Indexed |
| Semantic search (FAISS) on 500 FAQs | <50ms | ~30ms | Acceptable |

### Infrastructure Requirements (macOS)

| Component | Min Requirement | Recommended | Notes |
|-----------|-----------------|-------------|-------|
| Python | 3.11 | 3.12 | LTS version |
| Node.js | 18 LTS | 20 LTS | Latest stable |
| Rust | latest stable | MSRV 1.70 | For Tauri |
| RAM | 2GB | 4GB+ | Python ML models take ~1.5GB |
| Disk | 500MB | 1GB | FAISS indexes + models cache |
| macOS | Big Sur | Monterey+ | Tauri requirement |

---

## Groq Rate Limiting Strategy

**Groq Free Tier Limits:**
- 30 richieste/minuto
- 500 token max per request
- Response time: ~200-400ms tipico
- Durante picco: max 1-2s

**Strategy (exponential backoff):**

```python
# voice-agent/src/groq_client.py
from tenacity import retry, stop_after_attempt, wait_exponential

class GroqClient:

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete(self, system_prompt: str, user_message: str, max_tokens: int = 150):
        """Riprova con backoff esponenziale se rate limited"""
        try:
            response = await self.client.chat.completions.create(...)
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.warning(f"Groq rate limited: {e}, retrying...")
            raise
        except Exception as e:
            return "Mi scusi, non riesco a elaborare la richiesta."
```

---

## TTS/STT Latency Optimization

### Piper TTS (Local)

```bash
piper --model it_IT-riccardo-x_low.onnx \
      --output_file cache/risposte.wav
```

### Whisper STT Comparison

| Method | Latency | Quality | Offline | Cost |
|--------|---------|---------|---------|------|
| Whisper Local (small) | ~300ms | 90% | Yes | Free |
| Whisper API (OpenAI) | ~800ms | 95% | No | $0.02/min |
| **Recommendation** | - | - | - | **Local small** |

---

## Monitoring Dashboard Template

```
FLUXION Health Dashboard
+-- Service Status
|   +-- Python Voice: [*] Online (3002)
|   +-- HTTP Bridge: [*] Online (3001)
|   +-- SQLite: [*] Healthy (5ms avg query)
|   +-- Groq: [*] Online (rate: 5/30 min)
+-- Performance
|   +-- Avg response time (L0-L4): 156ms
|   +-- FAQ hit rate: 76% (L3)
|   +-- LLM fallback rate: 24% (L4)
|   +-- Error rate: 0.2%
+-- Database
|   +-- Size: 45MB
|   +-- Backups: Last 24h
|   +-- Queries/min: 42
|   +-- Slow queries (>50ms): 0
+-- Integrations
    +-- WhatsApp: [*] Active (15 msg/hr)
    +-- n8n: [*] Active (5 workflows)
    +-- Piper TTS: [*] Online (avg 120ms)
```

---

## WhatsApp Integration (n8n Workflow)

### Step 1: Setup WhatsApp Business Account

```
[ ] Register WhatsApp Business Account (go.fb.com/waba)
[ ] Set up Meta App (developers.facebook.com)
[ ] Get WABA ID + Phone Number ID + Access Token
[ ] Verify domain (if using custom webhook)
[ ] Subscribe to message_template webhooks
```

**Credentials in SQLite `integrations` table:**

```json
{
  "integration_type": "whatsapp",
  "config": {
    "waba_id": "119923456...",
    "phone_number_id": "119923456...",
    "access_token": "EAA123...",
    "webhook_verify_token": "my_verify_token_123",
    "webhook_url": "https://yourdomain.com/webhooks/whatsapp"
  },
  "status": "active"
}
```

### Step 2: n8n Workflow - WhatsApp Voice Bridge

**Workflow Logic:**

```
[Webhook WhatsApp Message]
    |
    v
[Extract client phone + message text]
    |
    v
[POST to HTTP Bridge /api/voice/query]
    |
    v
[Generate TTS audio from response]
    |
    v
[Send WhatsApp audio + text]
    |
    v
[Log to SQLite chat_history]
```

### Step 3: Webhook Configuration

**In Meta App Dashboard:**

```
Settings -> Webhooks -> Edit
+-- Callback URL: https://yourdomain.com/webhooks/whatsapp
+-- Verify Token: my_verify_token_123
+-- Subscribe to events: [x] messages
```

### Step 4: Test Flow

```bash
# Send test message to managed number
"Ciao, quanto costa un tagliando?"

# Expected flow:
# 1. Webhook receives payload
# 2. n8n extracts message text
# 3. HTTP Bridge called
# 4. Voice pipeline processes (L0->L4)
# 5. Response sent back on WhatsApp

# Result: Client receives answer text + audio
```

---

## Ehiweb SIP/VoIP Integration (Post-MVP)

### Architecture

```
Ehiweb SIP Provider
    | [SIP/RTP]
    v
Voice Agent SIP Endpoint (port 5060)
    | [HTTP]
    v
Orchestrator (L0-L4 pipeline)
    | [SQLite]
    v
Clienti database + context
    | [HTTP]
    v
Tauri Desktop (show caller info)
```

**Status:** Post-MVP Priority 2
- SIP endpoint: python-sip library
- Call context: Lookup by caller ID
- Recording: Transcribe with Whisper

---

## n8n Workflow Support Matrix

| Vertical | Workflow | Trigger | Action | Phase |
|----------|----------|---------|--------|-------|
| SALONE | Appointment Reminder | Scheduler (24h) | SMS | Phase 4 |
| SALONE | WhatsApp Chatbot | Message received | Voice pipeline | Phase 2 |
| SALONE | Loyalty Update | Booking created | Points increment | Phase 4 |
| WELLNESS | Booking Reminder | Scheduler (24h before) | SMS + Email | Phase 2 |
| WELLNESS | WhatsApp Chatbot | Message received | Voice pipeline | Phase 2 |
| MEDICAL | Appointment Reminder | Scheduler (24h) | SMS | Phase 5+ |
| MEDICAL | Prescription Alert | Data received | SMS reminder | Phase 5+ |
| AUTO | Booking Reminder | Scheduler (24h before) | SMS + Email | Phase 2 |
| AUTO | Invoice Generator | Appointment completed | PDF generation | Phase 2 |
| AUTO | WhatsApp Chatbot | Message received | Voice pipeline | Phase 2 |

---

## Security & Data Privacy

### GDPR Compliance

- [ ] Data retention: Chat history max 90 days
- [ ] Encryption at rest: SQLite encryption optional
- [ ] Encryption in transit: HTTPS for all calls
- [ ] Consent: Store user consent for voice recording
- [ ] Right to deletion: Implement GDPR delete endpoint
- [ ] Data portability: Export user data as JSON

### API Security

- [ ] HTTP Bridge on localhost only
- [ ] Voice pipeline on 127.0.0.1 (no remote binding)
- [ ] Groq API key in .env (never in code)
- [ ] n8n webhooks validated with token
- [ ] SQLite file permissions: 600 (user only)

### Backup & Disaster Recovery

- [ ] Daily SQLite backup to `~/Backups/fluxion-[date].db`
- [ ] Retention: 7 giorni
- [ ] Test restore monthly
- [ ] n8n workflows export weekly (JSON)

---

## macOS LaunchAgent Setup

**File:** `~/Library/LaunchAgents/com.fluxion.voice.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fluxion.voice</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/fluxion/venv/bin/uvicorn</string>
        <string>src.api:app</string>
        <string>--port</string>
        <string>3002</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/fluxion/voice-agent</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**Installation:**

```bash
cp deploy/macos/com.fluxion.voice.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.fluxion.voice.plist
```

---

## Linux Systemd Services

**File:** `/etc/systemd/system/fluxion-voice.service`

```ini
[Unit]
Description=FLUXION Voice Pipeline
After=network.target

[Service]
Type=simple
User=fluxion
WorkingDirectory=/opt/fluxion/voice-agent
ExecStart=/opt/fluxion/venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 3002
Restart=always
RestartSec=10
Environment=GROQ_API_KEY=gsk_***

[Install]
WantedBy=multi-user.target
```

**Installation:**

```bash
sudo cp deploy/linux/fluxion-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fluxion-voice
sudo systemctl start fluxion-voice
```

---

## Development Start Script

**File:** `scripts/start-dev.sh`

```bash
#!/bin/bash
set -e

echo "Starting FLUXION Development Environment..."

# 1. Start HTTP Bridge (Node.js)
echo "Starting HTTP Bridge (port 3001)..."
cd http-bridge
npm run dev &
HTTP_PID=$!

# 2. Start Voice Pipeline (Python)
echo "Starting Voice Pipeline (port 3002)..."
cd ../voice-agent
source venv/bin/activate
python -m uvicorn src.api:app --port 3002 --reload &
VOICE_PID=$!

# 3. Start Tauri Dev
echo "Starting Tauri Desktop (dev)..."
cd ..
npm run tauri dev

# Cleanup on exit
trap "echo 'Stopping services...'; kill $HTTP_PID $VOICE_PID; exit" EXIT
```

---

*Last Updated: 15 Gennaio 2026*
*Maintained by: Claude Code + Perplexity AI*
