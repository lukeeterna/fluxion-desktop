# FLUXION - Session History

> **Cronologia dettagliata delle sessioni di sviluppo.**
> Per lo stato corrente, vedi `CLAUDE.md`.

---

## 2026-01-10: E2E Testing Setup

### Completato
- 33 data-testid aggiunti in 9 componenti React
- 5 WebDriverIO spec files (booking, crm, invoice, cashier, voice)
- wdio.conf.ts configurato per Tauri (tauri-driver nativo)
- tauri-plugin-automation installato (feature e2e)
- Rimossa dipendenza CrabNebula (non più necessaria)
- GitHub Actions job e2e-tests su Linux

### Limitazione Importante
**tauri-driver NON supporta macOS** (no WKWebView WebDriver)

| Piattaforma | Supporto E2E | Driver |
|-------------|--------------|--------|
| Linux       | ✅ Funziona  | WebKitGTK |
| Windows     | ✅ Funziona  | WebView2 |
| macOS       | ❌ Richiede CrabNebula ($) | WKWebView |

### Soluzione Adottata
- E2E tests eseguiti su **Linux (ubuntu-22.04)** in GitHub Actions
- xvfb per headless testing
- Zero costi, ~20-25 min per run
- Per macOS locale: usare MCP Server per test manuali

---

## 2026-01-09: Voice Pipeline Implementation

### Python Voice Agent (`voice-agent/`)
- `src/groq_client.py`: STT (Whisper) + LLM (Llama 3.3 70B)
- `src/tts.py`: Piper TTS + macOS fallback
- `src/pipeline.py`: Orchestrazione STT → LLM → TTS
- `main.py`: HTTP Server porta 3002
- Persona italiana con system prompt
- Intent detection (prenotazione, cancellazione, etc.)

### Rust Commands (`voice_pipeline.rs`)
7 Tauri commands per gestire Python server:
- start_voice_pipeline, stop_voice_pipeline
- get_voice_pipeline_status, voice_process_text
- voice_greet, voice_say, voice_reset_conversation

### Test su iMac (TUTTI PASS)
- Groq LLM: ✅ Risposte in italiano
- TTS macOS: ✅ Audio generato
- HTTP endpoints: ✅ /health, /greet, /process, /say
- CI/CD Run #137, #138: ✅ SUCCESS

### Architettura Voice
```
Tauri App ──HTTP──▶ Python Voice Server (3002)
                          │
                          ├──▶ Groq Whisper (STT)
                          ├──▶ Groq Llama 3.3 70B (LLM)
                          └──▶ Piper TTS / macOS say
```

---

## 2026-01-08: HTTP Bridge + UI Fixes

### HTTP Bridge per MCP Integration
- File: `src-tauri/src/http_bridge.rs`
- Server Axum su porta 3001
- 12 REST endpoints per collegare MCP ↔ Tauri
- Solo in debug builds (#[cfg(debug_assertions)])

### UI Bug Fixes
- Fix DatePicker: min="1900-01-01" per permettere anni come 1945
- Fix Input numerico: value=0 → stringa vuota (no leading zero "010")
- Fix Chiusura Cassa: aggiunto window.alert per feedback utente
- Fix Invalid UUID: Zod schema da .uuid() a .min(1) per mock data
- Migration 010: mock_data.sql con clienti, servizi, operatori, appuntamenti

### Architettura Servizi e Licenze
- FLUXION IA (Groq): Campo API Key SOLO nel Setup Wizard (Step 3)
- Variabile DB: `fluxion_ia_key` nella tabella `impostazioni`
- Fallback: Se non presente, legge da .env `GROQ_API_KEY`
- WhatsApp auto-start: Tauri spawn child process Node.js all'avvio

---

## 2026-01-07: RAG Locale + Fatturazione

### FAQ con Variabili Template
- File: data/faq_salone_variabili.md
- Sintassi: {{variabile}} → sostituita con dati da DB
- Variabili popolate da: tabella impostazioni, servizi, orari
- Obiettivo: 90% risposte SENZA LLM, solo template matching

### RAG Locale Leggero
- Parser file FAQ → estrae Q&A
- Template engine: sostituisce {{var}} con valori DB
- Keyword matching per trovare risposta giusta
- LLM (Groq) SOLO per domande complesse fuori FAQ

### Identificazione Cliente WhatsApp
- Priorità ricerca: nome → soprannome → data_nascita (fallback)
- Campo soprannome: aggiunto a tabella clienti
- Se ambiguo → chiede data nascita
- Lookup per numero telefono se già in rubrica

### Workflow Conversazionali
File in `data/workflows/`:
- intents.json: rilevamento intento
- identificazione.json: lookup cliente
- prenotazione.json: flow booking
- modifica.json: modifica appuntamento
- disdetta.json: cancellazione

### Implementazioni Completate
1. ✅ Salvato faq_salone_variabili.md in data/
2. ✅ Creato sistema template {{var}} → DB (migration 008 + faq_template.rs)
3. ✅ Aggiunto campo soprannome a clienti
4. ✅ Implementata identificazione cliente WhatsApp
5. ✅ Migration 009: tabella incassi + chiusure_cassa + metodi_pagamento
6. ✅ cassa.rs: 8 Tauri commands
7. ✅ CassaPage: UI completa
8. ✅ Route /cassa + voce sidebar

---

> **Nota**: Per sessioni più recenti, vedi `docs/sessions/YYYY-MM-DD-*.md`
