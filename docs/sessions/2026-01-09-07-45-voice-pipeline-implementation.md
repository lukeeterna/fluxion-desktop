# Sessione: Voice Pipeline Python + Tauri Integration

**Data**: 2026-01-09T07:45:00
**Fase**: 7 - Voice Agent
**Agente**: voice-engineer

## Obiettivo
Implementare Voice Pipeline completa con Python (Groq STT/LLM + Piper TTS) e integrazione Tauri.

## Modifiche Effettuate

### 1. Python Voice Agent (`voice-agent/`)
Creato package Python completo per voice pipeline:

| File | Descrizione |
|------|-------------|
| `requirements.txt` | Dipendenze: groq, pydantic, aiohttp, sounddevice, etc. |
| `src/__init__.py` | Package init |
| `src/groq_client.py` | STT (Whisper) + LLM (Llama 3.3 70B) |
| `src/tts.py` | Piper TTS wrapper + macOS SystemTTS fallback |
| `src/pipeline.py` | Orchestrazione STT → LLM → TTS |
| `main.py` | HTTP Server su porta 3002 |

### 2. Rust Tauri Commands (`src-tauri/src/commands/voice_pipeline.rs`)
7 Tauri commands per gestire Python voice server:

```rust
- start_voice_pipeline()    // Avvia server Python
- stop_voice_pipeline()     // Ferma server
- get_voice_pipeline_status() // Stato + health check
- voice_process_text()      // Elabora testo
- voice_greet()             // Genera saluto iniziale
- voice_say()               // TTS only
- voice_reset_conversation() // Reset conversazione
```

### 3. Architettura
```
Tauri App ──HTTP──▶ Python Voice Server (port 3002)
                          │
                          ├──▶ Groq Whisper (STT)
                          ├──▶ Groq Llama 3.3 70B (LLM)
                          └──▶ Piper TTS / macOS fallback
```

### 4. Persona Italiana "Sara"
System prompt configurato con:
- Nome: Sara
- Ruolo: Assistente vocale
- Lingua: Italiano formale (Lei)
- Capacità: Prenotazioni, info, modifiche, cancellazioni

## Test Eseguiti su iMac

| Test | Risultato | Dettagli |
|------|-----------|----------|
| Groq LLM | ✅ PASS | "Ciao! Sto bene, grazie..." |
| TTS (macOS) | ✅ PASS | 54KB audio generato |
| Pipeline completa | ✅ PASS | Greeting + Process + Intent |
| HTTP /health | ✅ PASS | {"status": "ok"} |
| HTTP /api/voice/greet | ✅ PASS | Audio 189KB |
| HTTP /api/voice/process | ✅ PASS | Intent: "prenotazione" |
| HTTP /api/voice/say | ✅ PASS | Audio 49KB |

### Sample Conversation
- **User**: "Vorrei prenotare un taglio"
- **Sara**: "Per procedere con la prenotazione, potrebbe gentilmente dirmi il suo nome?"
- **Intent**: `prenotazione` ✅

## CI/CD

| Run | Status | Commit |
|-----|--------|--------|
| #137 | ✅ SUCCESS | `de4e700` - feat(voice): implementa Voice Pipeline |
| #138 | ✅ SUCCESS | `6ab11ca` - fix(voice): Union type Python 3.9 |

## Note
- Piper TTS non installato su iMac → usa macOS `say` (voce Alice)
- GROQ_API_KEY richiesta in `.env`
- Server Python gestito come subprocess da Tauri

## Commit
- `de4e700` - feat(voice): implementa Voice Pipeline Python + Tauri commands
- `6ab11ca` - fix(voice): use Union type for Python 3.9 compatibility
