# SESSION 2026-01-25 - Voice Agent Validation Strategy

## 🎯 DECISIONE PRESA

**Il Voice Agent è il DIFFERENZIATORE PRINCIPALE di Fluxion.**

Dopo analisi approfondita, abbiamo deciso:

### Strategia: VALIDATION-FIRST (48 ore)

Prima di investire 9 giorni di sviluppo, validare 3 assunzioni critiche:

1. **Llama 3.2 3B** → Accuracy ≥85% su intent italiani
2. **Piper TTS** → Latenza p95 <800ms su M1
3. **Whisper.cpp** → WER <12% su italiano

### Decision Matrix

```
IF (tutti pass) → GREEN: Proceed con dev sprint 9 giorni
IF (alcuni warn) → YELLOW: Modify architecture (+1-2 giorni)
IF (fail multipli) → RED: Pivot a RASA CALM o Groq cloud
```

---

## 📋 DOCUMENTI CREATI

| File | Contenuto |
|------|-----------|
| `/Users/macbook/Downloads/validation-phase-cto.md` | CTO Playbook con 3 validator script |
| `/Users/macbook/Downloads/voice-agent-complete.md` | Architettura completa (da rivedere) |
| `/Users/macbook/Downloads/FLUXION_VOICE_AGENT_COMPLETE.md` | Prima versione (problemi identificati) |

---

## ⚠️ PROBLEMI IDENTIFICATI

### edge-tts NON È OFFLINE
```python
# edge-tts usa Microsoft Azure cloud!
# Alternativa: Piper TTS (veramente offline)
```

### Architettura 4 Server Troppo Complessa
Il documento proponeva 4 server (porte 5001-5004).
Per app desktop Tauri serve **single-process**.

### Docker Irrilevante
Fluxion è app desktop, non web service.

---

## 🔧 STACK PROPOSTO (Post-Validation)

```
┌─────────────────────────────────────────────────────────┐
│ VOICE AGENT - Single Process Sidecar                    │
├─────────────────────────────────────────────────────────┤
│ STT:    Whisper.cpp (offline, italiano)                 │
│ LLM:    Llama 3.2 3B via Ollama (intent + slots)        │
│ Dialog: FSM custom JSON (8 stati)                       │
│ TTS:    Piper TTS italiano (offline)                    │
│ Bridge: HTTP localhost:3002 (già esistente)             │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 COSTI ANALIZZATI

| Soluzione | Costo/anno | Offline | GDPR |
|-----------|------------|---------|------|
| Llama locale | €0 | ✅ | ✅ |
| Groq Cloud | €0 (free tier)* | ❌ | ⚠️ |
| RASA CALM + Ollama | €0 | ✅ | ✅ |

*Free tier può cambiare, non garantito lifetime

---

## 🚀 PROSSIMI PASSI

### Domani (Validation Day)

1. **Setup su iMac** (192.168.1.9)
   - `ollama pull llama3.2:3b`
   - Setup Piper TTS italiano
   - Setup Whisper.cpp

2. **Run 3 Validator**
   - `llama_accuracy_validator.py`
   - `piper_latency_validator.py`
   - `whisper_wer_validator.py`

3. **Decision GO/NO-GO**
   - GREEN → Start 9-day dev sprint
   - YELLOW → Modify e start
   - RED → Pivot strategy

---

## 📁 FILE DA COPIARE SU IMAC

```bash
# Validator scripts (da creare da validation-phase-cto.md)
scp llama_accuracy_validator.py imac:/Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/
scp piper_latency_validator.py imac:/Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/
scp whisper_wer_validator.py imac:/Volumes/MacSSD\ -\ Dati/fluxion/voice-agent/
```

---

## 🔗 RIFERIMENTI

- [Groq Pricing](https://groq.com/pricing)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
- [tauri-local-lm](https://github.com/dillondesilva/tauri-local-lm) - Tauri + llama.cpp
- [ITALIC Dataset](https://huggingface.co/datasets/RiTA-nlp/ITALIC) - Intent italiano
- [MASSIVE Dataset](https://huggingface.co/datasets/qanastek/MASSIVE) - Multilingue
- [Piper TTS](https://github.com/rhasspy/piper) - TTS offline
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - STT offline

---

## ❌ BUG FIXATI OGGI

1. **session_manager.py** - Ricorsione infinita (fixato)
2. **Voice Pipeline** - Riavviata con nuovo PID 72955

## ❌ BUG ANCORA APERTI

1. **Entity extraction** - "Mario Rossi" → chiede cognome
2. **Database path mismatch** - HTTP Bridge legge DB sbagliato
3. **Flusso registrazione** - Propone sempre registrazione

---

*Sessione salvata: 2026-01-25 sera*
