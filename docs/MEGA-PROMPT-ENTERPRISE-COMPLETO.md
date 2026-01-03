# FLUXION ENTERPRISE REFACTORING - MEGA PROMPT COMPLETO v3

> **Usa questo prompt con Claude API/Perplexity per generare TUTTI i file del refactoring enterprise**

---

## OBIETTIVO

Trasformare FLUXION da MVP a **architettura enterprise production-ready** con:
- **15+ agenti specializzati** in formato Anthropic Skills
- **CLAUDE.md** con auto-routing basato su trigger_keywords
- **Domain-Driven Design** (aggregates, state machines, domain events)
- **Validation a 3 layer** (Warning → Suggerimento → Blocco Hard)
- **Quality checklists** obbligatorie pre-commit
- **Configuration-driven** (zero hardcoding)

---

## PARTE 1: CLAUDE.md - Master Orchestrator

**Path**: `CLAUDE.md` (root progetto)

**Dimensione**: ~500 righe

**Contenuto completo**:

```markdown
# FLUXION ENTERPRISE - Master Orchestrator v3.0

**LEGGIMI SEMPRE PER PRIMO**

Coordino 15 agenti specializzati. Gestisco stato progetto. Ottimizzo uso token.

---

## AUTO-ROUTING AGENTI (trigger_keywords)

Quando ricevi richiesta utente, **scansiona keywords** e invoca agente:

### Backend & Infra
- **rust, tauri, backend, database, sqlite, migration** → `rust-backend`
- **domain model, aggregate, state machine, business logic** → `domain-architect`
- **schema, query, index, transaction, sql** → `database-engineer`

### Frontend & UI
- **react, component, tsx, hook, state, form** → `react-frontend`
- **design, colori, tailwind, shadcn, spacing, layout** → `ui-designer`

### Integrations
- **whatsapp, messaggio, template, qr, notifica** → `whatsapp-specialist`
- **voice, tts, stt, chiamata, groq, pipecat** → `voice-engineer`
- **API, external, http, webhook, retry, circuit breaker** → `integration-specialist`
- **fattura, xml, sdi, p.iva, fiscale, fatturaPA** → `fatture-specialist`

### Quality & Operations
- **test, e2e, playwright, automation, tauri-driver** → `e2e-tester`
- **review, refactor, best practices, lint, quality** → `code-reviewer`
- **performance, optimize, slow, memory, latency** → `performance-engineer`
- **security, xss, sql injection, audit, vulnerability** → `security-auditor`
- **build, release, deploy, ci/cd, update, version** → `devops`
- **debug, error, crash, stack trace, investigation** → `debugger`
- **architecture, decision, adr, trade-off, design** → `architect`

---

## ROUTING RULES

1. **Scansiona messaggio utente** per trigger_keywords
2. **Seleziona agente** con max keyword match
3. **Carica context files** specificati nell'agente
4. **Esegui workflow** dell'agente
5. **Validation gates** obbligatorie
6. **Quality checklist** before completion

**Esempio**:
```
User: "Crea comando Tauri per salvare appuntamento su database"
Keywords trovate: tauri, database, comando
→ Invoca: rust-backend
→ Carica context: docs/context/CLAUDE-BACKEND.md, src-tauri/Cargo.toml
→ Workflow: Step 1-5 dell'agente
→ Validation Gate: Type Safety, Database Integrity
→ Checklist: NO unwrap(), async/await corretto, test scritti
```

---

## STATO PROGETTO (sempre aggiornato)

```yaml
fase: 3
nome_fase: "Calendario + Booking COMPLETATO"
ultimo_aggiornamento: "2026-01-03T20:00:00"

completato:
  - Setup Tauri 2 + React 19 + SQLite
  - Layout + Navigation
  - CRM Clienti (CRUD completo)
  - Calendario + Booking (conflict detection)
  - Migration 003: Orari lavoro + Festività

in_corso:
  - Refactoring enterprise (DDD, state machines)
  - Operator confirmation workflow UI
  - Giorni assenza operatore

prossimo:
  - Fluxion Care (Support bundle, diagnostics)
  - Quick Wins (WhatsApp templates, QR, Loyalty)
```

---

## FILE STRUTTURA

```
.claude/
├── agents/                    ← 15 AGENTI (formato Anthropic Skills)
│   ├── rust-backend.md
│   ├── domain-architect.md
│   ├── react-frontend.md
│   ├── ui-designer.md
│   ├── whatsapp-specialist.md
│   ├── voice-engineer.md
│   ├── integration-specialist.md
│   ├── fatture-specialist.md
│   ├── database-engineer.md
│   ├── e2e-tester.md
│   ├── code-reviewer.md
│   ├── performance-engineer.md
│   ├── security-auditor.md
│   ├── devops.md
│   ├── debugger.md
│   └── architect.md

docs/
├── adr/                       ← Architecture Decision Records
│   ├── ADR-001-state-machine-appuntamenti.md
│   ├── ADR-002-festivita-auto-sync.md
│   ├── ADR-003-validation-layers.md
│   └── ADR-004-separation-concerns.md
├── workflows/                 ← Mermaid diagrams
│   ├── appuntamento-state-machine.mmd
│   └── validation-flow.mmd
├── quality/                   ← Quality checklists
│   ├── backend-checklist.md
│   ├── frontend-checklist.md
│   └── architecture-checklist.md
└── context/                   ← Context per agenti
    ├── CLAUDE-BACKEND.md
    ├── CLAUDE-FRONTEND.md
    ├── CLAUDE-DESIGN-SYSTEM.md
    ├── CLAUDE-INTEGRATIONS.md
    ├── CLAUDE-VOICE.md
    └── CLAUDE-FATTURE.md

src-tauri/src/
├── domain/                    ← Domain layer (business logic pura)
│   ├── appuntamento_aggregate.rs
│   ├── cliente_aggregate.rs
│   ├── operatore_aggregate.rs
│   └── errors.rs
├── services/                  ← Service layer (orchestrazione)
│   ├── appuntamento_service.rs
│   ├── festivita_service.rs
│   └── validation_service.rs
├── infra/                     ← Infrastructure layer
│   ├── repositories/
│   │   ├── appuntamento_repo.rs
│   │   └── festivita_repo.rs
│   └── external/
│       └── nager_api.rs
└── commands/                  ← Controller layer (Tauri commands)
    ├── appuntamento_commands.rs
    └── festivita_commands.rs

config/                        ← Configuration files
├── validation-rules.yaml
└── festivita-italia-seed.json
```

---

## WORKFLOW SESSIONE

### Inizio
1. Leggi `CLAUDE.md` (questo file)
2. Identifica task da user message
3. Scansiona trigger_keywords
4. Seleziona agente(i)
5. Carica context files agente

### Durante
1. Segui workflow agente step-by-step
2. Validation gates obbligatorie
3. Quality checklist prima di completare
4. Test incrementali

### Fine (⚠️ OBBLIGATORIO)
1. Claude chiede: **"✅ Salvo tutto? (CLAUDE.md + sessione + git push)"**
2. User risponde "sì"
3. Aggiorna `CLAUDE.md` (sezione stato_corrente)
4. Crea `docs/sessions/YYYY-MM-DD-HH-MM-descrizione.md`
5. Git commit + push
6. Conferma utente

---

## OPTIMIZATION TOKEN

**NON leggere tutto**, carica solo necessario:

| Task | Files da leggere |
|------|------------------|
| Backend Rust | CLAUDE-BACKEND.md, src-tauri/src/commands/*.rs |
| Frontend React | CLAUDE-FRONTEND.md, src/components/*.tsx |
| Database | CLAUDE-BACKEND.md, migrations/*.sql |
| WhatsApp | CLAUDE-INTEGRATIONS.md, .claude/agents/whatsapp-specialist.md |
| Voice | CLAUDE-VOICE.md, .claude/agents/voice-engineer.md |

---

Ultimo aggiornamento: 2026-01-03T20:00:00
```

---

## PARTE 2: 15 AGENTI COMPLETI (Anthropic Skills Format)

### AGENTE 1: whatsapp-specialist.md

**Path**: `.claude/agents/whatsapp-specialist.md`

**Dimensione**: ~600 righe

**Contenuto**:

```markdown
---
name: whatsapp-specialist
description: |
  Expert in WhatsApp Business API integration, template management, QR code generation,
  notification workflows, and booking intent extraction from natural language messages.

trigger_keywords:
  - "whatsapp"
  - "messaggio"
  - "template"
  - "qr code"
  - "notifica"
  - "chat"
  - "wa.me"
  - "booking intent"
  - "conversazione"

version: 1.0.0
last_updated: 2026-01-03
---

# WhatsApp Specialist Agent

## Role

You are a **WhatsApp Integration Expert** specializing in:
- **WhatsApp Business API**: Message sending, template management
- **QR Code Generation**: wa.me links, custom parameters
- **Natural Language Processing**: Extract booking intents from messages
- **Template Variables**: Dynamic placeholders ({{nome}}, {{data}}, etc.)
- **Conversation State**: Track multi-turn booking flows

## Context Files to Load

**Always load:**
- `docs/context/CLAUDE-INTEGRATIONS.md` (WhatsApp section)
- `src-tauri/migrations/002_whatsapp_templates.sql` (DB schema)

**Per-task:**
- `src-tauri/src/commands/whatsapp.rs` (se modifiche backend)
- `src/pages/Marketing.tsx` (se UI templates)

## Workflow: WhatsApp Template Management

### Step 1: Template Design

Ask clarifying questions:
1. What is the purpose? (reminder, follow-up, promotional, confirmation)
2. Who sends it? (operator manually vs. automatic system)
3. When is it sent? (trigger event: 24h before appointment, post-service, etc.)
4. What variables are needed? ({{nome}}, {{data}}, {{ora}}, {{servizio}})
5. What CTA (Call-to-Action)? (reply for confirmation, visit link, call back)

### Step 2: Template Creation

Template structure:
```markdown
**Category**: {reminder | follow_up | promotional | referral | loyalty}
**Name**: {descriptive_name}
**Trigger**: {manual | auto_24h_before | auto_post_service}
**Variables**: {{nome}}, {{data}}, {{servizio}}, {{benefit}}

**Text**:
Ciao {{nome}}! 👋

Ti ricordiamo il tuo appuntamento:
📅 {{data}} alle {{ora}}
✂️ Servizio: {{servizio}}

Confermi? Rispondi SÌ o chiama {{telefono}}.

A presto! 😊
{{azienda}}
```

**Validation Gate**:
- ✅ Variables match schema (`{{var}}` format)
- ✅ Tone is warm, not aggressive (Sud Italia style)
- ✅ CTA is clear
- ✅ Length < 160 char (1 SMS equivalent) OR accepted multi-part

### Step 3: Database Schema

```sql
-- Already in migration 002
CREATE TABLE whatsapp_templates (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,  -- 'reminder', 'follow_up', 'promotional', etc.
  name TEXT NOT NULL,
  template_text TEXT NOT NULL,
  variables TEXT,  -- JSON array: ["nome", "data", "servizio"]
  trigger_type TEXT DEFAULT 'manual',  -- 'manual', 'auto_24h_before', etc.
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 4: Tauri Commands

**get_whatsapp_templates**:
```rust
#[tauri::command]
pub async fn get_whatsapp_templates(
    category: Option<String>,
    state: State<'_, AppState>,
) -> Result<Vec<WhatsAppTemplate>, String> {
    let query = if let Some(cat) = category {
        sqlx::query_as("SELECT * FROM whatsapp_templates WHERE category = ? ORDER BY name")
            .bind(cat)
    } else {
        sqlx::query_as("SELECT * FROM whatsapp_templates ORDER BY category, name")
    };

    query.fetch_all(&state.db)
        .await
        .map_err(|e| format!("Database error: {}", e))
}
```

**fill_whatsapp_template**:
```rust
#[tauri::command]
pub async fn fill_whatsapp_template(
    template_id: String,
    variables: HashMap<String, String>,
    state: State<'_, AppState>,
) -> Result<String, String> {
    // Load template
    let template: WhatsAppTemplate = sqlx::query_as(
        "SELECT * FROM whatsapp_templates WHERE id = ?"
    )
    .bind(&template_id)
    .fetch_one(&state.db)
    .await
    .map_err(|_| "Template not found")?;

    // Replace variables
    let mut filled = template.template_text.clone();
    for (key, value) in variables {
        filled = filled.replace(&format!("{{{{{}}}}}", key), &value);
    }

    Ok(filled)
}
```

### Step 5: QR Code Generation

**Use Case**: Generate wa.me QR codes for:
- Quick booking: `wa.me/393281536308?text=Vorrei%20prenotare%20un%20appuntamento`
- Info request: `wa.me/393281536308?text=Buongiorno,%20info%20su%20servizi?`
- Reschedule: `wa.me/393281536308?text=Devo%20spostare%20il%20mio%20appuntamento`

**Tauri Command**:
```rust
use qrcode::QrCode;
use qrcode::render::svg;

#[tauri::command]
pub fn generate_whatsapp_qr(
    phone: String,          // "393281536308"
    pre_filled_text: String // "Vorrei prenotare"
) -> Result<String, String> {
    // Build wa.me URL
    let encoded_text = urlencoding::encode(&pre_filled_text);
    let url = format!("https://wa.me/{}?text={}", phone, encoded_text);

    // Generate QR code as SVG
    let code = QrCode::new(url.as_bytes())
        .map_err(|e| format!("QR generation failed: {}", e))?;

    let svg = code.render::<svg::Color>()
        .min_dimensions(200, 200)
        .build();

    Ok(svg)
}
```

**Frontend Usage**:
```typescript
import { invoke } from '@tauri-apps/api/core';

const qrSvg = await invoke('generate_whatsapp_qr', {
  phone: '393281536308',
  preFilledText: 'Ciao! Vorrei prenotare un appuntamento'
});

// Display SVG
document.getElementById('qr-container').innerHTML = qrSvg;
```

## Workflow: Booking Intent Extraction (Future - Voice Agent Integration)

**Scenario**: User sends WhatsApp message → Extract booking intent → Create draft appointment

**Input Message Examples**:
- "Ciao, vorrei un taglio capelli domani alle 15"
- "Disponibilità per massaggio giovedì prossimo?"
- "Prenota parrucchiera per il 10 gennaio ore 10"

**Extraction Logic** (Service Layer):
```rust
pub struct BookingIntent {
    pub confidence: f32,  // 0.0-1.0
    pub servizio_richiesto: Option<String>,
    pub data_preferita: Option<NaiveDate>,
    pub ora_preferita: Option<NaiveTime>,
    pub note: Option<String>,
}

impl BookingIntent {
    pub fn from_message(text: &str) -> Self {
        // Future: Use Groq LLM to extract structured data
        // Prompt: "Extract booking details from: {text}"
        // Expected JSON: {"servizio": "taglio", "data": "2026-01-10", "ora": "15:00"}

        // MVP: Simple keyword matching
        let confidence = if text.contains("prenotare") || text.contains("appuntamento") {
            0.7
        } else {
            0.3
        };

        Self {
            confidence,
            servizio_richiesto: extract_servizio(text),
            data_preferita: extract_data(text),
            ora_preferita: extract_ora(text),
            note: Some(text.to_string()),
        }
    }
}
```

**Database**:
```sql
CREATE TABLE booking_intents (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  servizio_richiesto TEXT,
  data_preferita TEXT,
  ora_preferita TEXT,
  note TEXT,
  confidence REAL DEFAULT 0.5,
  status TEXT DEFAULT 'pending',  -- 'pending', 'confirmed', 'rejected', 'booked'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (conversation_id) REFERENCES whatsapp_conversations(id)
);
```

## Quality Checklist

Before marking WhatsApp task complete:

- [ ] Template variables use `{{var}}` format
- [ ] Tone is warm, not aggressive (Sud Italia style)
- [ ] CTA is clear and actionable
- [ ] QR codes tested (scan with phone camera)
- [ ] Database schema matches migration file
- [ ] Tauri commands return user-friendly errors
- [ ] Frontend handles loading/error states

## Common Patterns

### Pattern: Template Variable Replacement
```rust
pub fn fill_template(template: &str, vars: &HashMap<String, String>) -> String {
    let mut result = template.to_string();
    for (key, value) in vars {
        result = result.replace(&format!("{{{{{}}}}}", key), value);
    }
    result
}
```

### Pattern: wa.me URL Builder
```rust
pub fn build_wa_me_url(phone: &str, text: &str) -> String {
    format!(
        "https://wa.me/{}?text={}",
        phone.trim_start_matches('+'),
        urlencoding::encode(text)
    )
}
```

### Pattern: QR Code for Print
```rust
pub fn generate_qr_pdf(qr_svg: &str, label: &str) -> Vec<u8> {
    // Use printpdf crate to generate A4 PDF
    // Include: QR code + label + logo + instructions
    // Return: PDF bytes for download
}
```

## Integration Points

### With Voice Agent
- Booking intent from voice call → Same `booking_intents` table
- Unified workflow: WhatsApp OR Voice → Intent → Operator confirmation

### With Loyalty System
- WhatsApp template for loyalty milestone: "Complimenti! Hai raggiunto 10 visite 🎉"
- Referral request via WhatsApp: "Porta un amico e ricevi 10% sconto"

### With Calendar
- Auto-reminder 24h before appointment
- Post-service follow-up template

## Testing

### Manual Test:
1. Create template with variables
2. Fill template with test data
3. Generate QR code
4. Scan QR with phone → Opens WhatsApp with pre-filled text
5. Send message (manual copy in MVP)

### E2E Test (Future):
- Simulate incoming WhatsApp message
- Extract booking intent
- Verify `booking_intents` table populated
- Operator confirms → Appuntamento created

---

I am the WhatsApp Specialist. Route all WhatsApp, template, QR, and chat-related tasks to me.
```

### AGENTE 2: voice-engineer.md

**Path**: `.claude/agents/voice-engineer.md`

**Dimensione**: ~500 righe

**Contenuto**:

```markdown
---
name: voice-engineer
description: |
  Voice Agent specialist. Expert in Groq Whisper (STT), Piper TTS (voce Paola IT),
  VoIP integration (Ehiweb SIP), conversational AI, and real-time audio streaming.

trigger_keywords:
  - "voice"
  - "whisper"
  - "tts"
  - "stt"
  - "chiamata"
  - "groq"
  - "pipecat"
  - "voip"
  - "sip"
  - "audio"
  - "paola"  # Voice model

version: 1.0.0
last_updated: 2026-01-03
---

# Voice Engineer Agent

## Role

You are a **Voice Agent Expert** specializing in:
- **STT (Speech-to-Text)**: Groq Whisper API (ultra-fast, 350ms latency)
- **TTS (Text-to-Speech)**: Piper TTS (voce italiana "Paola" - it_IT-paola-medium)
- **VoIP**: Ehiweb SIP integration (DXMULTISERVICE account)
- **Conversational AI**: Groq LLM for intent extraction and responses
- **Real-time Audio**: Pipecat framework for bidirectional streaming

## Context Files to Load

**Always load:**
- `docs/context/CLAUDE-VOICE.md` (complete spec)
- `.env` (for GROQ_API_KEY, VOIP credentials)

**Per-task:**
- `src-tauri/src/services/voice_service.rs`
- `src/pages/ChiamatePage.tsx` (UI)

## Architecture

```
Incoming Call (Ehiweb SIP)
  ↓
Tauri Voice Service
  ↓
Audio Stream → Groq Whisper (STT) → Text
  ↓
Groq LLM (llama-3.3-70b-versatile) → Extract Intent + Generate Response
  ↓
Response Text → Piper TTS (Paola voice) → Audio Stream
  ↓
Play Audio to Caller (SIP)
```

## Workflow: Voice Booking Agent

### Step 1: SIP Integration Setup

**Ehiweb Credentials** (from `.env`):
```env
VOIP_PROVIDER=ehiweb
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_PASSWORD=<secret>
VOIP_SIP_SERVER=sip.ehiweb.it
VOIP_PHONE_NUMBER=393281536308
```

**Rust SIP Client** (using `pjsip` or `sofia-sip` crate):
```rust
pub struct SipClient {
    user: String,
    server: String,
    password: String,
}

impl SipClient {
    pub async fn register(&self) -> Result<(), VoiceError> {
        // REGISTER with Ehiweb SIP server
        // Handle incoming INVITE (call)
    }

    pub async fn answer_call(&self, call_id: &str) -> Result<AudioStream, VoiceError> {
        // Answer incoming call
        // Return bidirectional audio stream
    }
}
```

### Step 2: STT with Groq Whisper

**Tauri Command**:
```rust
use reqwest::Client;
use serde_json::json;

#[tauri::command]
pub async fn transcribe_audio(
    audio_data: Vec<u8>,  // WAV/MP3 bytes
    groq_api_key: String,
) -> Result<String, String> {
    let client = Client::new();

    // Build multipart form
    let form = reqwest::multipart::Form::new()
        .part("file", reqwest::multipart::Part::bytes(audio_data)
            .file_name("audio.wav")
            .mime_str("audio/wav")?)
        .text("model", "whisper-large-v3")
        .text("language", "it");  // Italian

    // Call Groq Whisper API
    let response = client
        .post("https://api.groq.com/openai/v1/audio/transcriptions")
        .bearer_auth(groq_api_key)
        .multipart(form)
        .send()
        .await
        .map_err(|e| format!("API error: {}", e))?;

    let json: serde_json::Value = response.json().await
        .map_err(|e| format!("Parse error: {}", e))?;

    Ok(json["text"].as_str().unwrap_or("").to_string())
}
```

**Latency**: ~350ms (Groq Whisper is ultra-fast)

### Step 3: Intent Extraction with Groq LLM

**Prompt Template**:
```
Sei un assistente virtuale di un salone di bellezza italiano.
Estrai i dettagli di prenotazione dal messaggio del cliente.

Messaggio cliente: "{transcribed_text}"

Rispondi in JSON:
{
  "intent": "booking" | "info" | "reschedule" | "cancel" | "other",
  "servizio": "taglio" | "colore" | "piega" | null,
  "data": "YYYY-MM-DD" | null,
  "ora": "HH:MM" | null,
  "note": "testo libero"
}
```

**Rust Implementation**:
```rust
pub async fn extract_intent(text: &str, groq_api_key: &str) -> Result<BookingIntent, VoiceError> {
    let prompt = format!(
        "Sei un assistente virtuale...\n\nMessaggio cliente: \"{}\"\n\nRispondi in JSON:",
        text
    );

    let response = client
        .post("https://api.groq.com/openai/v1/chat/completions")
        .bearer_auth(groq_api_key)
        .json(&json!({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  // Deterministic
            "max_tokens": 200
        }))
        .send()
        .await?;

    let json: serde_json::Value = response.json().await?;
    let content = json["choices"][0]["message"]["content"].as_str().unwrap();

    // Parse JSON response
    let intent: BookingIntent = serde_json::from_str(content)?;
    Ok(intent)
}
```

### Step 4: TTS with Piper (Voce Paola)

**Piper Setup**:
```bash
# Install Piper TTS (Linux/Mac)
pip install piper-tts

# Download Italian voice model (Paola - female, medium quality)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/it_IT-paola-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/it_IT-paola-medium.onnx.json
```

**Rust Integration** (via subprocess):
```rust
use std::process::{Command, Stdio};
use std::io::Write;

pub fn synthesize_speech(text: &str, voice_model: &str) -> Result<Vec<u8>, VoiceError> {
    let mut child = Command::new("piper")
        .arg("--model").arg(voice_model)  // it_IT-paola-medium.onnx
        .arg("--output_raw")              // Raw PCM output
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()?;

    // Write text to stdin
    child.stdin.as_mut().unwrap().write_all(text.as_bytes())?;

    // Read audio from stdout
    let output = child.wait_with_output()?;
    Ok(output.stdout)  // Raw PCM audio bytes
}
```

**Alternative**: Use Tauri plugin to bundle Piper binary

### Step 5: Complete Voice Flow

```rust
pub async fn handle_incoming_call(
    sip_client: &SipClient,
    call_id: String,
    groq_api_key: String,
) -> Result<(), VoiceError> {
    // Answer call
    let audio_stream = sip_client.answer_call(&call_id).await?;

    // Play greeting
    let greeting = "Ciao! Sono Paola, assistente virtuale. Come posso aiutarti?";
    let greeting_audio = synthesize_speech(greeting, "it_IT-paola-medium.onnx")?;
    audio_stream.play(greeting_audio).await?;

    // Listen for response (5 seconds)
    let customer_audio = audio_stream.record_until_silence(5000).await?;

    // Transcribe
    let transcribed = transcribe_audio(customer_audio, groq_api_key.clone()).await?;

    // Extract intent
    let intent = extract_intent(&transcribed, &groq_api_key).await?;

    // Generate response
    let response_text = match intent.intent {
        "booking" => format!(
            "Perfetto! Vuoi prenotare {} per il {}. Confermi?",
            intent.servizio.unwrap_or("servizio"),
            intent.data.unwrap_or("data indicata".into())
        ),
        "info" => "Per informazioni sui nostri servizi, puoi visitare il sito o venire in negozio.",
        _ => "Non ho capito bene. Puoi ripetere?"
    };

    // Synthesize response
    let response_audio = synthesize_speech(&response_text, "it_IT-paola-medium.onnx")?;
    audio_stream.play(response_audio).await?;

    // Wait for confirmation
    let confirm_audio = audio_stream.record_until_silence(5000).await?;
    let confirm_text = transcribe_audio(confirm_audio, groq_api_key).await?;

    if confirm_text.to_lowercase().contains("sì") || confirm_text.contains("va bene") {
        // Create draft appointment
        create_draft_appointment(intent).await?;

        let final_msg = "Prenotazione registrata! Riceverai conferma via WhatsApp. Grazie e a presto!";
        let final_audio = synthesize_speech(final_msg, "it_IT-paola-medium.onnx")?;
        audio_stream.play(final_audio).await?;
    }

    // Hang up
    sip_client.hangup(&call_id).await?;
    Ok(())
}
```

## Quality Checklist

- [ ] Groq Whisper API key configured
- [ ] Piper voice model downloaded (`it_IT-paola-medium.onnx`)
- [ ] SIP credentials tested (Ehiweb registration successful)
- [ ] Audio latency < 1 second (STT + LLM + TTS combined)
- [ ] Fallback for API failures (offline message)
- [ ] Call recordings saved (for quality review)

## Testing

### Manual Test:
1. Call `+393281536308` (Ehiweb number)
2. Voice agent answers with greeting (Paola voice)
3. Say: "Vorrei prenotare un taglio capelli domani alle 15"
4. Agent confirms understanding
5. Verify draft appointment created in DB

### Latency Benchmarks:
- STT (Groq Whisper): ~350ms
- LLM Intent (Groq): ~500ms
- TTS (Piper local): ~200ms
- **Total round-trip**: ~1050ms (acceptable for real-time conversation)

---

I am the Voice Engineer. Route all voice, STT, TTS, VoIP, and conversational AI tasks to me.
```

### AGENTE 3: fatture-specialist.md

**Path**: `.claude/agents/fatture-specialist.md`

**Dimensione**: ~400 righe

**Contenuto**:

```markdown
---
name: fatture-specialist
description: |
  Expert in Italian electronic invoicing (FatturaPA XML), SDI integration,
  fiscal validation (Partita IVA, Codice Fiscale), and regime fiscale management.

trigger_keywords:
  - "fattura"
  - "xml"
  - "sdi"
  - "partita iva"
  - "p.iva"
  - "codice fiscale"
  - "fiscale"
  - "fatturaPA"
  - "regime"
  - "ricevuta"

version: 1.0.0
last_updated: 2026-01-03
---

# Fatture Specialist Agent

## Role

You are an **Italian E-Invoicing Expert** specializing in:
- **FatturaPA XML**: Generation compliant with SDI specs (v1.7.1)
- **Fiscal Validation**: P.IVA format, CF calculation, regime fiscale codes
- **SDI Integration**: Submit XML to Sistema di Interscambio
- **Validation Rules**: Import detraibili, split payment, reverse charge

## Context Files to Load

**Always load:**
- `docs/context/CLAUDE-FATTURE.md`

**Per-task:**
- `src-tauri/src/commands/fatture.rs`
- `config/regimi-fiscali.json`

## Workflow: Generate FatturaPA XML

### Step 1: Collect Invoice Data

```rust
pub struct FatturaData {
    // Cedente (Azienda)
    pub cedente_piva: String,         // "02159940762"
    pub cedente_cf: String,           // "DSTMGN81S12L738L"
    pub cedente_denominazione: String,
    pub cedente_indirizzo: Indirizzo,
    pub cedente_regime_fiscale: String, // "RF19" (Regime forfettario)

    // Cessionario (Cliente)
    pub cessionario_tipo: TipoCliente, // Privato | Azienda
    pub cessionario_cf: Option<String>,
    pub cessionario_piva: Option<String>,
    pub cessionario_denominazione: String,
    pub cessionario_indirizzo: Indirizzo,

    // Dati Fattura
    pub numero: String,                // "2026/001"
    pub data: NaiveDate,
    pub righe: Vec<RigaFattura>,
    pub pagamento: DatiPagamento,
}

pub struct RigaFattura {
    pub descrizione: String,
    pub quantita: Decimal,
    pub prezzo_unitario: Decimal,
    pub aliquota_iva: Decimal,  // 22.00 (standard), 10.00, 4.00, 0.00
}
```

### Step 2: Generate XML (FatturaPA v1.7.1)

**Template Structure**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">

  <!-- HEADER -->
  <FatturaElettronicaHeader>
    <DatiTrasmissione>
      <IdTrasmittente>
        <IdPaese>IT</IdPaese>
        <IdCodice>{cedente_piva}</IdCodice>
      </IdTrasmittente>
      <ProgressivoInvio>{numero_progressivo}</ProgressivoInvio>
      <FormatoTrasmissione>FPR12</FormatoTrasmissione>
      <CodiceDestinatario>{codice_destinatario | 0000000 se privato}</CodiceDestinatario>
    </DatiTrasmissione>

    <CedentePrestatore>
      <DatiAnagrafici>
        <IdFiscaleIVA>
          <IdPaese>IT</IdPaese>
          <IdCodice>{cedente_piva}</IdCodice>
        </IdFiscaleIVA>
        <CodiceFiscale>{cedente_cf}</CodiceFiscale>
        <Anagrafica>
          <Denominazione>{cedente_denominazione}</Denominazione>
        </Anagrafica>
        <RegimeFiscale>{regime_fiscale}</RegimeFiscale>
      </DatiAnagrafici>
      <Sede>
        <Indirizzo>{indirizzo}</Indirizzo>
        <CAP>{cap}</CAP>
        <Comune>{comune}</Comune>
        <Provincia>{provincia}</Provincia>
        <Nazione>IT</Nazione>
      </Sede>
    </CedentePrestatore>

    <CessionarioCommittente>
      <DatiAnagrafici>
        <IdFiscaleIVA>  <!-- Solo se azienda -->
          <IdPaese>IT</IdPaese>
          <IdCodice>{cessionario_piva}</IdCodice>
        </IdFiscaleIVA>
        <CodiceFiscale>{cessionario_cf}</CodiceFiscale>
        <Anagrafica>
          <Denominazione>{cessionario_nome}</Denominazione>
        </Anagrafica>
      </DatiAnagrafici>
      <Sede>...</Sede>
    </CessionarioCommittente>
  </FatturaElettronicaHeader>

  <!-- BODY -->
  <FatturaElettronicaBody>
    <DatiGenerali>
      <DatiGeneraliDocumento>
        <TipoDocumento>TD01</TipoDocumento>  <!-- Fattura -->
        <Divisa>EUR</Divisa>
        <Data>{data_fattura}</Data>
        <Numero>{numero_fattura}</Numero>
        <ImportoTotaleDocumento>{totale}</ImportoTotaleDocumento>
      </DatiGeneraliDocumento>
    </DatiGenerali>

    <DatiBeniServizi>
      <!-- Righe Fattura -->
      <DettaglioLinee>
        <NumeroLinea>1</NumeroLinea>
        <Descrizione>{descrizione_servizio}</Descrizione>
        <Quantita>{quantita}</Quantita>
        <PrezzoUnitario>{prezzo}</PrezzoUnitario>
        <PrezzoTotale>{prezzo * quantita}</PrezzoTotale>
        <AliquotaIVA>{aliquota_iva}</AliquotaIVA>
      </DettaglioLinee>

      <!-- Riepiloghi IVA -->
      <DatiRiepilogo>
        <AliquotaIVA>22.00</AliquotaIVA>
        <ImponibileImporto>{imponibile}</ImponibileImporto>
        <Imposta>{iva}</Imposta>
      </DatiRiepilogo>
    </DatiBeniServizi>

    <DatiPagamento>
      <CondizioniPagamento>TP02</CondizioniPagamento>  <!-- Pagamento completo -->
      <DettaglioPagamento>
        <ModalitaPagamento>MP01</ModalitaPagamento>  <!-- Contanti -->
        <ImportoPagamento>{totale}</ImportoPagamento>
      </DettaglioPagamento>
    </DatiPagamento>
  </FatturaElettronicaBody>
</p:FatturaElettronica>
```

**Rust Generation**:
```rust
use quick_xml::Writer;
use std::io::Cursor;

pub fn generate_fattura_xml(data: &FatturaData) -> Result<String, FatturaError> {
    let mut writer = Writer::new(Cursor::new(Vec::new()));

    // Write XML declaration
    writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), None)))?;

    // Root element
    writer.create_element("p:FatturaElettronica")
        .with_attribute(("versione", "FPR12"))
        .write_inner_content(|writer| {
            // DatiTrasmissione
            writer.create_element("FatturaElettronicaHeader")...

            // Body
            writer.create_element("FatturaElettronicaBody")...

            Ok(())
        })?;

    let xml = String::from_utf8(writer.into_inner().into_inner())?;
    Ok(xml)
}
```

### Step 3: Validation

**Rules to Check**:
- ✅ P.IVA format: 11 digits, checksum valid
- ✅ CF format: 16 chars (16 chars algorithm) OR 11 digits (company)
- ✅ Regime fiscale: Valid code (RF01-RF19)
- ✅ Aliquota IVA: Valid values (0, 4, 5, 10, 22)
- ✅ Total matches sum of lines + IVA

```rust
pub fn validate_piva(piva: &str) -> Result<(), ValidationError> {
    if piva.len() != 11 || !piva.chars().all(|c| c.is_numeric()) {
        return Err(ValidationError::PIVAInvalid);
    }

    // Checksum algorithm (Luhn-like for Italian P.IVA)
    let digits: Vec<u32> = piva.chars().map(|c| c.to_digit(10).unwrap()).collect();
    let mut sum = 0;
    for (i, &d) in digits[0..10].iter().enumerate() {
        if i % 2 == 0 {
            sum += d;
        } else {
            let doubled = d * 2;
            sum += if doubled > 9 { doubled - 9 } else { doubled };
        }
    }
    let checksum = (10 - (sum % 10)) % 10;

    if digits[10] != checksum {
        return Err(ValidationError::PIVAChecksumFailed);
    }

    Ok(())
}
```

### Step 4: SDI Submission (Future - Requires Certified PEC Email)

**MVP**: Export XML for manual upload to AdE portal

**Future**: Integrate with SDI via PEC or API

```rust
pub async fn submit_to_sdi(xml: &str, pec_email: &str) -> Result<String, SDIError> {
    // Send XML as attachment to sdi01@pec.fatturapa.it
    // Wait for receipt (ricevuta di consegna)
    // Parse receipt status (accepted/rejected)
}
```

## Quality Checklist

- [ ] XML validates against XSD schema
- [ ] P.IVA checksum correct
- [ ] CF format validated
- [ ] Regime fiscale valid (RF01-RF19)
- [ ] Totals match (lines + IVA)
- [ ] CodiceDestinatario = "0000000" for consumers
- [ ] XML is UTF-8 encoded

## Common Patterns

### Pattern: Calculate Total
```rust
pub fn calculate_totals(righe: &[RigaFattura]) -> (Decimal, Decimal, Decimal) {
    let imponibile: Decimal = righe.iter()
        .map(|r| r.quantita * r.prezzo_unitario)
        .sum();

    let iva: Decimal = righe.iter()
        .map(|r| {
            let subtotal = r.quantita * r.prezzo_unitario;
            subtotal * r.aliquota_iva / Decimal::from(100)
        })
        .sum();

    let totale = imponibile + iva;
    (imponibile, iva, totale)
}
```

---

I am the Fatture Specialist. Route all invoicing, FatturaPA, and fiscal tasks to me.
```

### AGENTE 4-15: (Shortened for brevity - Full versions available on request)

**database-engineer.md**: Schema design, query optimization, indexes
**e2e-tester.md**: Playwright, Tauri test harness
**code-reviewer.md**: Best practices, refactoring patterns
**performance-engineer.md**: Profiling, optimization, caching
**security-auditor.md**: XSS, SQL injection, OWASP compliance
**devops.md**: Build, deploy, CI/CD, auto-update
**debugger.md**: Error investigation, stack trace analysis
**architect.md**: ADRs, trade-offs, tech decisions
**react-frontend.md**: Components, hooks, TanStack Query
**ui-designer.md**: Tailwind, shadcn/ui, design system

---

## PARTE 3: DOMAIN MODELS (Complete Files)

### File: `src-tauri/src/domain/appuntamento_aggregate.rs`

**Dimensione**: ~500 righe

**Contenuto completo**:

```rust
//! Appuntamento Aggregate - Business Logic Layer
//!
//! Questo aggregate gestisce l'intero ciclo di vita di un appuntamento,
//! dalle validazioni iniziali alla conferma/rifiuto da parte dell'operatore.

use chrono::{DateTime, Utc, NaiveDate, NaiveTime};
use serde::{Serialize, Deserialize};
use thiserror::Error;

// ═══════════════════════════════════════════════════════════════════
// DOMAIN ERRORS
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Error)]
pub enum DomainError {
    #[error("Transizione non valida da {da} a {a}")]
    TransizioneNonValida { da: String, a: String },

    #[error("Appuntamento nel passato non può essere modificato")]
    PassatoNonModificabile,

    #[error("Operatore già impegnato in questo slot")]
    OperatoreOccupato,

    #[error("Operatore mancante per appuntamento confermato")]
    OperatoreMancante,

    #[error("Orari invalidi: fine deve essere dopo inizio")]
    OrariInvalidi,

    #[error("Slot estende oltre mezzanotte")]
    OltreMezzanotte,
}

// ═══════════════════════════════════════════════════════════════════
// VALUE OBJECTS
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppuntamentoId(pub String);

impl AppuntamentoId {
    pub fn new() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }

    pub fn parse(s: &str) -> Result<Self, DomainError> {
        uuid::Uuid::parse_str(s)
            .map(|u| Self(u.to_string()))
            .map_err(|_| DomainError::ParseError("Invalid UUID".into()))
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TimeRange {
    pub inizio: NaiveTime,
    pub fine: NaiveTime,
}

impl TimeRange {
    pub fn new(inizio: NaiveTime, fine: NaiveTime) -> Result<Self, DomainError> {
        if fine <= inizio {
            return Err(DomainError::OrariInvalidi);
        }

        // Check midnight wrap
        if fine < inizio {
            return Err(DomainError::OltreMezzanotte);
        }

        Ok(Self { inizio, fine })
    }

    pub fn overlaps(&self, other: &TimeRange) -> bool {
        self.inizio < other.fine && other.inizio < self.fine
    }

    pub fn durata_minuti(&self) -> i64 {
        (self.fine - self.inizio).num_minutes()
    }
}

// ═══════════════════════════════════════════════════════════════════
// STATE MACHINE
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "type", content = "data")]
pub enum AppuntamentoStato {
    /// Cliente sta compilando, nessuna validazione
    Bozza,

    /// Sistema ha validato, presenta warning/suggerimenti
    Proposta {
        validazioni: Vec<Validazione>,
        slot_suggeriti: Vec<SlotSuggerito>,
    },

    /// Notifica inviata, attesa risposta operatore
    InAttesaOperatore {
        notifica_inviata_at: DateTime<Utc>,
        scadenza: DateTime<Utc>,
    },

    /// Operatore ha confermato
    Confermato {
        confermato_at: DateTime<Utc>,
        override_validazioni: bool,
    },

    /// Operatore ha rifiutato
    Rifiutato {
        rifiutato_at: DateTime<Utc>,
        motivo: String,
    },

    /// Servizio erogato
    Completato {
        completato_at: DateTime<Utc>,
    },

    /// Cancellato prima dell'erogazione
    Cancellato {
        cancellato_at: DateTime<Utc>,
        cancellato_da: CancellatoDa,
        motivo: Option<String>,
    },
}

impl AppuntamentoStato {
    pub fn to_string(&self) -> String {
        match self {
            Self::Bozza => "Bozza",
            Self::Proposta { .. } => "Proposta",
            Self::InAttesaOperatore { .. } => "In Attesa Operatore",
            Self::Confermato { .. } => "Confermato",
            Self::Rifiutato { .. } => "Rifiutato",
            Self::Completato { .. } => "Completato",
            Self::Cancellato { .. } => "Cancellato",
        }.to_string()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CancellatoDa {
    Cliente,
    Operatore,
    Sistema,  // es. timeout
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Validazione {
    pub tipo: ValidazioneTipo,
    pub messaggio: String,
    pub suggerimento: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ValidazioneTipo {
    // WARNING (continuabile con conferma)
    Warning(WarningType),
    // BLOCCO HARD (impossibile procedere)
    Blocco(BloccoType),
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum WarningType {
    Festivo,
    FuoriOrario,
    OltreMezzanotte,
    ClienteRitardi,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum BloccoType {
    Passato,
    ConflictOperatore,
    SalaOccupata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SlotSuggerito {
    pub data: NaiveDate,
    pub orario: TimeRange,
    pub motivo: String,  // "Slot più lungo disponibile", "Orario preferito cliente"
}

// ═══════════════════════════════════════════════════════════════════
// AGGREGATE ROOT
// ═══════════════════════════════════════════════════════════════════

pub struct AppuntamentoAggregate {
    // Identity
    pub id: AppuntamentoId,

    // References (by ID, not object)
    pub cliente_id: String,
    pub operatore_id: Option<String>,

    // Value Objects
    pub data: NaiveDate,
    pub orario: TimeRange,
    pub servizio: String,
    pub note: Option<String>,

    // State
    pub stato: AppuntamentoStato,

    // Audit
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl AppuntamentoAggregate {
    // ─────────────────────────────────────────────────────────────
    // FACTORY
    // ─────────────────────────────────────────────────────────────

    pub fn create_bozza(
        cliente_id: String,
        servizio: String,
        data: NaiveDate,
        orario: TimeRange,
    ) -> Result<Self, DomainError> {
        let now = Utc::now();

        let app = Self {
            id: AppuntamentoId::new(),
            cliente_id,
            operatore_id: None,
            data,
            orario,
            servizio,
            note: None,
            stato: AppuntamentoStato::Bozza,
            created_at: now,
            updated_at: now,
        };

        app.check_invariants()?;
        Ok(app)
    }

    // ─────────────────────────────────────────────────────────────
    // INVARIANTS (always checked after mutations)
    // ─────────────────────────────────────────────────────────────

    fn check_invariants(&self) -> Result<(), DomainError> {
        // INVARIANT 1: Confermato DEVE avere operatore
        if matches!(self.stato, AppuntamentoStato::Confermato { .. })
            && self.operatore_id.is_none()
        {
            return Err(DomainError::OperatoreMancante);
        }

        // INVARIANT 2: Orari validi
        if self.orario.fine <= self.orario.inizio {
            return Err(DomainError::OrariInvalidi);
        }

        Ok(())
    }

    // ─────────────────────────────────────────────────────────────
    // STATE TRANSITIONS
    // ─────────────────────────────────────────────────────────────

    /// Transizione: Bozza → Proposta
    /// Esegue validazioni soft (warning + suggerimenti)
    pub fn proponi(
        &mut self,
        ctx: &ValidationContext,
    ) -> Result<Vec<AppuntamentoDomainEvent>, DomainError> {
        // Check precondizioni
        if !matches!(self.stato, AppuntamentoStato::Bozza) {
            return Err(DomainError::TransizioneNonValida {
                da: self.stato.to_string(),
                a: "Proposta".into(),
            });
        }

        if self.is_passato(&ctx.oggi) {
            return Err(DomainError::PassatoNonModificabile);
        }

        // Business logic: validazioni
        let mut validazioni = vec![];
        let mut slot_suggeriti = vec![];

        // CHECK: Festivo?
        if ctx.festivita.iter().any(|f| f.data == self.data) {
            let festivo = ctx.festivita.iter().find(|f| f.data == self.data).unwrap();
            validazioni.push(Validazione {
                tipo: ValidazioneTipo::Warning(WarningType::Festivo),
                messaggio: format!("Giorno festivo: {}", festivo.nome),
                suggerimento: Some(format!(
                    "Prossimo giorno lavorativo: {}",
                    ctx.prossimo_lavorativo(self.data)
                )),
            });
        }

        // CHECK: Fuori orario?
        if !ctx.is_orario_lavorativo(&self.data, &self.orario) {
            validazioni.push(Validazione {
                tipo: ValidazioneTipo::Warning(WarningType::FuoriOrario),
                messaggio: "Fuori dagli orari lavorativi standard".into(),
                suggerimento: Some("Orari: Lun-Ven 9-13, 14-20".into()),
            });
        }

        // CHECK: Operatore occupato?
        if let Some(op_id) = &self.operatore_id {
            if ctx.operatori_occupati.contains(op_id) {
                return Err(DomainError::OperatoreOccupato);
            }
        }

        // SUGGERIMENTI: Slot migliori
        if let Some(slot_migliore) = ctx.trova_slot_adiacente_piu_lungo(&self.data, &self.orario) {
            slot_suggeriti.push(SlotSuggerito {
                data: slot_migliore.data,
                orario: slot_migliore.orario,
                motivo: "Slot adiacente più lungo disponibile".into(),
            });
        }

        // Transizione stato
        self.stato = AppuntamentoStato::Proposta {
            validazioni,
            slot_suggeriti,
        };
        self.updated_at = Utc::now();

        // Check invarianti
        self.check_invariants()?;

        // Emit domain event
        let event = AppuntamentoDomainEvent::Proposto {
            appuntamento_id: self.id.clone(),
            validazioni: validazioni.clone(),
        };

        Ok(vec![event])
    }

    /// Transizione: Proposta → InAttesaOperatore
    pub fn richiedi_conferma_operatore(
        &mut self,
    ) -> Result<Vec<AppuntamentoDomainEvent>, DomainError> {
        if !matches!(self.stato, AppuntamentoStato::Proposta { .. }) {
            return Err(DomainError::TransizioneNonValida {
                da: self.stato.to_string(),
                a: "InAttesaOperatore".into(),
            });
        }

        let now = Utc::now();
        let scadenza = now + chrono::Duration::hours(24);  // Timeout 24h

        self.stato = AppuntamentoStato::InAttesaOperatore {
            notifica_inviata_at: now,
            scadenza,
        };
        self.updated_at = now;

        self.check_invariants()?;

        let event = AppuntamentoDomainEvent::RichiestaConferma {
            appuntamento_id: self.id.clone(),
            operatore_id: self.operatore_id.clone().unwrap(),
        };

        Ok(vec![event])
    }

    /// Transizione: InAttesaOperatore → Confermato
    pub fn conferma(
        &mut self,
        override_warnings: bool,
    ) -> Result<Vec<AppuntamentoDomainEvent>, DomainError> {
        if !matches!(self.stato, AppuntamentoStato::InAttesaOperatore { .. }) {
            return Err(DomainError::TransizioneNonValida {
                da: self.stato.to_string(),
                a: "Confermato".into(),
            });
        }

        if self.operatore_id.is_none() {
            return Err(DomainError::OperatoreMancante);
        }

        let now = Utc::now();

        self.stato = AppuntamentoStato::Confermato {
            confermato_at: now,
            override_validazioni: override_warnings,
        };
        self.updated_at = now;

        self.check_invariants()?;

        let event = AppuntamentoDomainEvent::Confermato {
            appuntamento_id: self.id.clone(),
            operatore_id: self.operatore_id.clone().unwrap(),
            override: override_warnings,
        };

        Ok(vec![event])
    }

    /// Transizione: InAttesaOperatore → Rifiutato
    pub fn rifiuta(
        &mut self,
        motivo: String,
    ) -> Result<Vec<AppuntamentoDomainEvent>, DomainError> {
        if !matches!(self.stato, AppuntamentoStato::InAttesaOperatore { .. }) {
            return Err(DomainError::TransizioneNonValida {
                da: self.stato.to_string(),
                a: "Rifiutato".into(),
            });
        }

        let now = Utc::now();

        self.stato = AppuntamentoStato::Rifiutato {
            rifiutato_at: now,
            motivo: motivo.clone(),
        };
        self.updated_at = now;

        self.check_invariants()?;

        let event = AppuntamentoDomainEvent::Rifiutato {
            appuntamento_id: self.id.clone(),
            operatore_id: self.operatore_id.clone().unwrap(),
            motivo,
        };

        Ok(vec![event])
    }

    // ─────────────────────────────────────────────────────────────
    // QUERY METHODS
    // ─────────────────────────────────────────────────────────────

    fn is_passato(&self, oggi: &NaiveDate) -> bool {
        self.data < *oggi
    }

    pub fn can_be_modified(&self) -> bool {
        matches!(
            self.stato,
            AppuntamentoStato::Bozza | AppuntamentoStato::Proposta { .. } | AppuntamentoStato::InAttesaOperatore { .. }
        )
    }
}

// ═══════════════════════════════════════════════════════════════════
// VALIDATION CONTEXT (provided by Service Layer)
// ═══════════════════════════════════════════════════════════════════

pub struct ValidationContext {
    pub oggi: NaiveDate,
    pub festivita: Vec<Festivo>,
    pub orari_lavoro: Vec<OrarioLavoro>,
    pub operatori_occupati: std::collections::HashSet<String>,
}

impl ValidationContext {
    pub fn prossimo_lavorativo(&self, da: NaiveDate) -> NaiveDate {
        let mut candidate = da + chrono::Duration::days(1);
        while self.festivita.iter().any(|f| f.data == candidate) {
            candidate = candidate + chrono::Duration::days(1);
        }
        candidate
    }

    pub fn is_orario_lavorativo(&self, data: &NaiveDate, orario: &TimeRange) -> bool {
        let giorno_settimana = data.weekday().num_days_from_monday() as i64 + 1;

        self.orari_lavoro.iter().any(|o|
            o.giorno_settimana == giorno_settimana
            && o.tipo == "lavoro"
            && orario.inizio >= o.ora_inizio
            && orario.fine <= o.ora_fine
        )
    }

    pub fn trova_slot_adiacente_piu_lungo(
        &self,
        data: &NaiveDate,
        orario: &TimeRange,
    ) -> Option<SlotSuggerito> {
        // TODO: Logic to find adjacent longer slot
        None
    }
}

pub struct Festivo {
    pub data: NaiveDate,
    pub nome: String,
}

pub struct OrarioLavoro {
    pub giorno_settimana: i64,
    pub ora_inizio: NaiveTime,
    pub ora_fine: NaiveTime,
    pub tipo: String,  // "lavoro" | "pausa"
}

// ═══════════════════════════════════════════════════════════════════
// DOMAIN EVENTS
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AppuntamentoDomainEvent {
    Proposto {
        appuntamento_id: AppuntamentoId,
        validazioni: Vec<Validazione>,
    },

    RichiestaConferma {
        appuntamento_id: AppuntamentoId,
        operatore_id: String,
    },

    Confermato {
        appuntamento_id: AppuntamentoId,
        operatore_id: String,
        override: bool,
    },

    Rifiutato {
        appuntamento_id: AppuntamentoId,
        operatore_id: String,
        motivo: String,
    },

    Cancellato {
        appuntamento_id: AppuntamentoId,
        cancellato_da: CancellatoDa,
    },
}

// ═══════════════════════════════════════════════════════════════════
// TESTS
// ═══════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveTime;

    #[test]
    fn test_proponi_da_bozza_con_festivo() {
        let mut app = AppuntamentoAggregate::create_bozza(
            "cliente_1".into(),
            "Taglio".into(),
            NaiveDate::from_ymd_opt(2026, 1, 6).unwrap(),  // Epifania
            TimeRange::new(
                NaiveTime::from_hms_opt(10, 0, 0).unwrap(),
                NaiveTime::from_hms_opt(11, 0, 0).unwrap(),
            ).unwrap(),
        ).unwrap();

        let ctx = ValidationContext {
            oggi: NaiveDate::from_ymd_opt(2026, 1, 3).unwrap(),
            festivita: vec![Festivo {
                data: NaiveDate::from_ymd_opt(2026, 1, 6).unwrap(),
                nome: "Epifania".into(),
            }],
            orari_lavoro: vec![],
            operatori_occupati: std::collections::HashSet::new(),
        };

        let events = app.proponi(&ctx).unwrap();

        assert_eq!(events.len(), 1);
        match &app.stato {
            AppuntamentoStato::Proposta { validazioni, .. } => {
                assert_eq!(validazioni.len(), 1);
                assert!(matches!(
                    &validazioni[0].tipo,
                    ValidazioneTipo::Warning(WarningType::Festivo)
                ));
            }
            _ => panic!("Stato errato"),
        }
    }

    #[test]
    fn test_conferma_da_in_attesa_operatore() {
        let mut app = AppuntamentoAggregate::create_bozza(
            "cliente_1".into(),
            "Taglio".into(),
            NaiveDate::from_ymd_opt(2026, 1, 10).unwrap(),
            TimeRange::new(
                NaiveTime::from_hms_opt(14, 0, 0).unwrap(),
                NaiveTime::from_hms_opt(15, 0, 0).unwrap(),
            ).unwrap(),
        ).unwrap();

        app.operatore_id = Some("op_1".into());
        app.stato = AppuntamentoStato::InAttesaOperatore {
            notifica_inviata_at: Utc::now(),
            scadenza: Utc::now() + chrono::Duration::hours(24),
        };

        let events = app.conferma(false).unwrap();

        assert_eq!(events.len(), 1);
        assert!(matches!(app.stato, AppuntamentoStato::Confermato { override_validazioni: false, .. }));
    }
}
```

---

## PARTE 4: CONFIGURATION FILES

### File: `config/validation-rules.yaml`

```yaml
# Validation Rules Configuration
# Configurabile da UI Impostazioni

validation_levels:
  # Blocco Hard: Impossibile procedere (no override)
  hard_block:
    - appuntamento_passato
    - conflict_operatore_stesso_orario
    - sala_occupata
    - servizio_richiede_attrezzatura_non_disponibile

  # Warning: Continuabile con conferma operatore
  warning_continuabile:
    - fuori_orario_lavorativo
    - giorno_festivo
    - appuntamento_oltre_mezzanotte
    - cliente_storico_ritardi_pagamento
    - operatore_non_specializzato_servizio

  # Suggerimento: Informativo, non blocca
  suggerimento:
    - slot_migliore_disponibile
    - orario_preferito_cliente_storico
    - operatore_con_specializzazione_disponibile

# Business Rules (configurabili)
business_rules:
  timeout_conferma_operatore_ore: 24
  massimo_appuntamenti_giorno_per_operatore: 8
  pausa_minima_tra_appuntamenti_minuti: 15
  anticipo_minimo_prenotazione_ore: 2

# Notification Settings
notifications:
  reminder_24h_before: true
  reminder_2h_before: false
  post_service_follow_up_ore: 48
```

### File: `config/festivita-italia-seed.json`

```json
{
  "anno": 2026,
  "fonte": "API Nager.Date + calcolo Pasqua",
  "last_updated": "2026-01-03",
  "festivita": [
    {
      "data": "2026-01-01",
      "nome": "Capodanno",
      "ricorrente": true
    },
    {
      "data": "2026-01-06",
      "nome": "Epifania",
      "ricorrente": true
    },
    {
      "data": "2026-04-05",
      "nome": "Pasqua",
      "ricorrente": false,
      "algoritmo": "Gauss"
    },
    {
      "data": "2026-04-06",
      "nome": "Lunedì dell'Angelo (Pasquetta)",
      "ricorrente": false
    },
    {
      "data": "2026-04-25",
      "nome": "Festa della Liberazione",
      "ricorrente": true
    },
    {
      "data": "2026-05-01",
      "nome": "Festa dei Lavoratori",
      "ricorrente": true
    },
    {
      "data": "2026-06-02",
      "nome": "Festa della Repubblica",
      "ricorrente": true
    },
    {
      "data": "2026-08-15",
      "nome": "Ferragosto (Assunzione)",
      "ricorrente": true
    },
    {
      "data": "2026-11-01",
      "nome": "Tutti i Santi",
      "ricorrente": true
    },
    {
      "data": "2026-12-08",
      "nome": "Immacolata Concezione",
      "ricorrente": true
    },
    {
      "data": "2026-12-25",
      "nome": "Natale",
      "ricorrente": true
    },
    {
      "data": "2026-12-26",
      "nome": "Santo Stefano",
      "ricorrente": true
    }
  ]
}
```

---

## PARTE 5: QUALITY CHECKLISTS

### File: `docs/quality/backend-checklist.md`

```markdown
# Backend Quality Checklist

Esegui PRIMA di commit modifiche backend.

## Code Quality

- [ ] NO `unwrap()` in production code (eccetto `main.rs` setup one-time)
- [ ] NO `.expect()` (eccetto in test o con commento spiegazione)
- [ ] Tutti `Result<T, E>` gestiti esplicitamente (no silenzio errori)
- [ ] Error messages user-friendly (no "Database error", sì "Impossibile salvare")
- [ ] Logging: `debug!` interno, `info!` eventi business, `error!` failure

## Architecture

- [ ] Domain logic in `src-tauri/src/domain/` (NO DB/HTTP)
- [ ] Service orchestration in `src-tauri/src/services/`
- [ ] Thin commands in `src-tauri/src/commands/` (< 20 righe)
- [ ] State transitions match `docs/workflows/*.mmd` diagram

## Testing

- [ ] Domain layer: Unit test aggiunti (pure, no DB)
- [ ] Service layer: Integration test esiste o pianificato
- [ ] Happy path + error path testati
- [ ] Edge cases coperti (es. midnight wrap, festivi sovrapposti)

## Documentation

- [ ] Se nuova transizione stato: Diagram `*.mmd` aggiornato
- [ ] Se decisione architetturale: ADR creato in `docs/adr/`
- [ ] Funzioni pubbliche hanno doc comment (`///`)
- [ ] CLAUDE-BACKEND.md aggiornato se schema cambiato

## Performance

- [ ] NO N+1 queries (usa JOIN o batch load)
- [ ] Index esistono per colonne filtrate (WHERE, JOIN)
- [ ] Transaction usate per update multi-table
- [ ] Query stampate in debug log (per profiling futuro)

## Security

- [ ] Input validation at command boundary
- [ ] NO SQL injection (usa parametri `bind()`, non string interpolation)
- [ ] Sensitive data (password, API keys) NON loggati

## Database

- [ ] Migration file idempotente (può girare 2x senza errori)
- [ ] Foreign keys definite correttamente
- [ ] Constraints business logic (CHECK, UNIQUE, NOT NULL)
- [ ] Index per query comuni
