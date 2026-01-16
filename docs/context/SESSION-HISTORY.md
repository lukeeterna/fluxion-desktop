# FLUXION - Session History

> **Cronologia dettagliata delle sessioni di sviluppo.**
> Per lo stato corrente, vedi `CLAUDE.md`.

---

## 2026-01-16: Supplier Management UI + Excel Import

### Completato

**Frontend Fornitori (React):**
- `src/pages/Fornitori.tsx` - Pagina principale con tabs Fornitori/Ordini
- `src/components/fornitori/FornitoriTable.tsx` - Lista fornitori con CRUD
- `src/components/fornitori/FornitoreDialog.tsx` - Form creazione/modifica fornitore
- `src/components/fornitori/SupplierOrdersTable.tsx` - Lista ordini con azioni
- `src/components/fornitori/OrderDialog.tsx` - Form ordine con items dinamici
- `src/components/fornitori/SendConfirmDialog.tsx` - Dialog conferma invio

**Hooks React Query:**
- `src/hooks/use-fornitori.ts` - Mutations per tutte le operazioni CRUD
- `src/hooks/use-file-parser.ts` - Parse Excel/Word con auto-detect colonne

**Excel/Word Import:**
- Librerie: SheetJS (xlsx) + mammoth.js
- Auto-detect colonne: descrizione, prezzo, qty, sku
- Mapping manuale se auto-detect fallisce
- Supporto: .xlsx, .xls, .csv, .docx

### Bug Fix

| Bug | Problema | Soluzione |
|-----|----------|-----------|
| Rust type mismatch | `CreateOrderRequest.items` era `Vec<serde_json::Value>` | Cambiato a `String` |
| Hook param mismatch | `update_order_status` passava `id` | Cambiato a `orderId` |
| Select empty value | `<SelectItem value="">` crash | Usato `__none__` placeholder |
| Async state stale | `autoDetectMapping()` usava state vecchio | Parametri opzionali diretti |

### Tauri macOS Compatibility Issue

**Problema critico**: Tauri 2.9.5 con wry 0.53.5 **NON funziona** su macOS Big Sur (11.x)

```
thread 'main' panicked at:
failed overriding protocol method -[WKUIDelegate webView:requestMediaCapturePermissionForOrigin:...]
```

**Causa**: L'API WebKit `requestMediaCapturePermissionForOrigin` esiste solo da macOS 12+

**Workaround**:
- Sviluppo/test su iMac (macOS 12.7.4 Monterey) ✅
- MacBook (Big Sur) non può eseguire Tauri dev

### Da Testare (2026-01-17)

- [ ] Invio ordine via Email (mailto: con SendConfirmDialog)
- [ ] Invio ordine via WhatsApp (wa.me URL con conferma)
- [ ] Voice Agent Sara (pipeline STT + NLU + TTS)
- [ ] WhatsApp QR Scan UI (login WhatsApp Business)

### Files Creati/Modificati

| File | Azione |
|------|--------|
| `src/pages/Fornitori.tsx` | Creato (completo) |
| `src/components/fornitori/*.tsx` | Creati (6 componenti) |
| `src/hooks/use-fornitori.ts` | Creato |
| `src/hooks/use-file-parser.ts` | Creato |
| `src-tauri/src/commands/supplier.rs` | Fix tipo items |

---

## 2026-01-15: NLU + TTS Upgrades (spaCy + UmBERTo + Aurora)

### Problema (BUG-V4)
Voice agent interpretava "Io non sono mai stato da voi" come cliente "Mai" invece di riconoscere intento NUOVO_CLIENTE.

### Soluzione: 4-Layer NLU Pipeline

**Stack selezionato** (dopo ricerca Perplexity):
- **Layer 1**: Regex pattern matching (~1ms)
- **Layer 2**: spaCy NER `it_core_news_lg` (~20ms)
- **Layer 3**: UmBERTo intent classification (~80ms)
- **Layer 4**: Context management (~5ms)

**Totale**: ~100-120ms latency, 100% offline, ZERO costi ricorrenti

### Files Creati

| File | Descrizione |
|------|-------------|
| `voice-agent/src/nlu/__init__.py` | Module exports |
| `voice-agent/src/nlu/italian_nlu.py` | ItalianVoiceAgentNLU class (4-layer) |
| `voice-agent/scripts/download_models.py` | Model downloader script |

### Files Modificati

| File | Modifiche |
|------|-----------|
| `voice-agent/requirements.txt` | +spacy, +transformers, +torch, +piper-tts |
| `voice-agent/src/tts.py` | Aurora voice (8.7/10 quality) come default |
| `voice-agent/src/orchestrator.py` | Integrazione advanced NLU in Layer 0b |

### Nuove Voci TTS

| Voice | Quality | Size | Note |
|-------|---------|------|------|
| **Aurora** (default) | 8.7/10 | 63MB | Community, Dec 2024 - più calda |
| Paola (fallback) | 8.5/10 | 63MB | Official |

### Test Cases Risolti

```python
# TEST 1: False positive "Mai"
"Io non sono mai stato da voi" → NUOVO_CLIENTE ✅

# TEST 2: Intento implicito
"È la prima volta che vengo" → NUOVO_CLIENTE ✅

# TEST 3: Terza persona
"Vorrei prenotare per mia madre Maria" → cliente="Maria" ✅
```

### Setup

```bash
# Install dependencies
pip install -r voice-agent/requirements.txt

# Download models
python voice-agent/scripts/download_models.py --all

# Test NLU
python -m src.nlu.italian_nlu

# Test TTS
python -m src.tts
```

### Business Model Alignment
- spaCy: MIT License (free, offline)
- UmBERTo: Apache 2.0 (free, offline)
- Piper Aurora: CC-BY-SA (free, offline)
- **ZERO costi ricorrenti** ✅ (allineato con licenza annuale FLUXION)

---

## 2026-01-14: Voice Agent Greeting Loop Fix

### Problema
Paola ripeteva "Buonasera sono Paola..." invece di chiedere il nome del cliente dopo il greeting.

### Root Cause
L1 intent classifier intercettava CORTESIA ("Buongiorno") e rispondeva con altro greeting, impedendo a L2 (booking state machine) di essere mai invocato.

### Soluzione (`orchestrator.py`)
```python
# is_first_turn flag - skip CORTESIA su primo turno
is_first_turn = self._current_session and self._current_session.total_turns == 0

# L1: Skip greeting response on first turn
skip_greeting_cortesia = is_first_turn and intent_result.category == IntentCategory.CORTESIA

# L2: Always process booking SM on first turn
should_process_booking = (
    intent_result.category == IntentCategory.PRENOTAZIONE or
    self.booking_sm.context.state != BookingState.IDLE or
    is_first_turn
)
```

### Verifica
- Test locale MacBook: ✅
- Test iMac via SSH: ✅
- User: "Buongiorno" → Paola: "Mi può dire il suo nome per favore?" ✅

### Documento Analizzato
- `FLUXION Enterprise Agent.pdf` - conferma architettura 4-layer RAG
- Definisce KPIs, state machine states, GDPR requirements

### TODO Domani (2026-01-15)
- [ ] Test su Windows (192.168.1.17)
- [ ] Test CI/CD pipeline
- [ ] Test E2E Playwright suite

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
