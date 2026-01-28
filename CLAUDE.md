# FLUXION - Stato Progetto

> **Procedure operative:** [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md)

---

## Progetto

**FLUXION**: Gestionale desktop enterprise per PMI italiane

- **Stack**: Tauri 2.x + React 19 + TypeScript + SQLite + Tailwind CSS 3.4
- **Target**: Saloni, palestre, cliniche, ristoranti (1-15 dipendenti)
- **Modello**: Licenza LIFETIME desktop (NO SaaS, NO commissioni, NO canoni)

---

## Stato Corrente

```yaml
fase: 7.6
nome: "Voice Agent Multi-Vertical"
ultimo_update: 2026-01-28
ci_cd_run: "#158 SUCCESS"
```

### In Corso

- [ ] **Voice Agent v1.0 Sprint** - 4 settimane (vedi `_bmad-output/planning-artifacts/voice-agent-epics.md`)
  - **Week 1**: ✅ P0 fixes COMPLETATO
  - **Week 2**: P1 improvements (Date extraction, Service matching, Sentence Transformers)
  - **Week 3**: Quality (Silero VAD, Disambiguation, Corrections)
  - **Week 4**: Release (GDPR, Testing, Documentation)
- [ ] **Test SMTP Email** - Gmail App Password (già implementato, da testare)

### Completato (2026-01-28)

- [x] **Session Isolation Bug Fix** - Sessioni ora isolate correttamente
  - **Bug**: `process_handler` usava `self._current_session_id` invece di `data.get("session_id")`
  - **Effetto**: Stato booking condiviso tra sessioni diverse
  - **Fix**: `voice-agent/main.py` linea 199 - usa session_id dalla request
  - **Commit**: `162e843`

- [x] **SARA Corrections VERIFIED LIVE** - Correzioni in CONFIRMING funzionano
  - **"sì ma alle 11"** → Aggiorna ora (NON conferma), chiede riconferma ✅
  - **"niente meglio venerdì"** → Aggiorna data (NON cancella), chiede riconferma ✅
  - **Testato su iMac 192.168.1.9** via HTTP API

- [x] **CI/CD Cross-Platform** - Pipeline con Python tests e matrix macOS+Windows
  - Aggiunto Python voice-agent tests a `fast-check` e `full-suite`
  - Nuovo job `cross-platform-verify` (macOS-13 + Windows matrix)
  - Documentato in `_bmad/bmm/data/project-context.md`
  - **Commit**: `abb143d`

- [x] **BMAD Protocol Update** - Aggiunto live test iMac obbligatorio
  - `_bmad/bmm/data/project-context.md` - Fluxion project context
  - `step-03-execute.md` - Live test step aggiunto
  - **Commit**: `729561a`

- [x] **Week 1 Sprint P0 Fixes** - Voice Agent SARA completamente funzionante
  - **E7-S1**: Hybrid STT Engine (whisper.cpp + Groq fallback)
    - `voice-agent/src/stt.py` - Nuovo modulo STT con HybridSTT, WhisperOfflineSTT, GroqSTT
    - `voice-agent/src/groq_client.py` - Integrato hybrid STT engine
    - WER migliorato: 21.7% → 9-11% (quando whisper.cpp disponibile)
  - **E1-S1**: Slot availability check prima di confermare prenotazione
    - `orchestrator.py` - Aggiunto `_check_slot_availability()` method
    - Se slot non disponibile, offre alternative o waitlist
  - **E4-S1**: Cancel appointment end-to-end
    - Nuovi intent patterns per CANCELLAZIONE (15+ varianti italiane)
    - Handler completo in orchestrator per cancellazione
    - HTTP endpoint `/api/appuntamenti/cancel`
  - **E4-S2**: Reschedule appointment end-to-end
    - Nuovi intent patterns per SPOSTAMENTO (anticipare, posticipare, rimandare)
    - Handler completo in orchestrator per rescheduling
    - HTTP endpoint `/api/appuntamenti/reschedule`
    - HTTP endpoint `/api/appuntamenti/cliente/:client_id`
  - **Intent Classifier Upgrade**: Patterns robusti per italiano
    - CANCELLAZIONE: "annulla", "cancella", "disdire", "eliminare", "non posso più venire"
    - SPOSTAMENTO: "spostare", "cambiare", "modificare", "anticipare", "posticipare", "rimandare"
    - PRENOTAZIONE: Separato da nouns generici per evitare conflitti
  - **Test**: 500 passed, 22 nuovi test in `test_cancel_reschedule.py`
  - **E2E Tests**: 4 nuovi test in `voice-agent.test.ts` (cancel, reschedule, availability)
  - **Files modificati**: `stt.py`, `groq_client.py`, `orchestrator.py`, `intent_classifier.py`

- [x] **BMAD Epic Planning Voice Agent** - Pianificazione enterprise-grade completa
  - **7 Epic**: Core Booking, Registration, Disambiguation, Management, FAQ, Waitlist, Reliability
  - **17 Stories** con acceptance criteria, implementation code, effort estimates
  - **Validation Report**: 1709 righe da Perplexity con soluzioni concrete
  - **Root Cause WER**: Groq audio compression → whisper.cpp offline (9-11% WER)
  - **NLU Fix**: Sentence Transformers ONNX (no PyTorch) → 85% → 92%+
  - **VAD Fix**: Silero VAD > TEN VAD (95% vs 92% accuracy)
  - **Domain Data**: 4 verticali JSON (Salone, Palestra, Medical, Auto)
  - **GDPR**: Two-tier consent, data retention policy, DSAR handler
  - **4-Week Roadmap**: Timeline giornaliera per v1.0
  - **Files**:
    - `_bmad-output/planning-artifacts/voice-agent-epics.md` (Epic + Stories + Roadmap)
    - `docs/SARA-validation-report.md` (1709 righe technical validation)
    - `docs/SARA-lifetime-spec.md` (Business model spec)

### Completato (2026-01-27)

- [x] **SARA 3-Level Correction Logic (B1-B7)** - Integrazione completa state machine con 9 correzioni
  - **7 bug fixati**: B1 punteggiatura nomi STT, B2 follow_up_response, B3 operatore generico, B4 correzioni in CONFIRMING, B5 force_update campi, B6 slot pre-fill skip, B7 duplicazione cognome
  - **Riscritto `_handle_confirming()`** con logica entity-first: "sì ma alle 11" → aggiorna ora (non conferma), "niente meglio venerdì" → aggiorna data (non cancella)
  - **5 vertical correction patterns**: salone, palestra, medical, auto, restaurant
  - **`sanitize_name()` / `sanitize_name_pair()`** per artefatti STT ("Rossi." → "Rossi", "Gianluca Distasi" → name+surname)
  - **`extract_generic_operator()`** in entity_extractor.py ("con un'operatrice" → gender F, generic)
  - **`follow_up_response`** in StateMachineResult per messaggi split (registrazione → servizio)
  - **`force_update`** in `_update_context_from_extraction()` per sovrascrivere campi durante correzioni
  - **`_get_next_required_slot()`** per skip slot già compilati
  - **14 helper methods** aggiunti a BookingStateMachine
  - **Test**: 478 passed, 0 failed (31 nuovi in `test_booking_corrections.py`)
  - **Commit**: `bb2c61f`
  - **File**: `booking_state_machine.py` (+640 righe), `entity_extractor.py` (+66), `orchestrator.py` (+3)
  - **Riferimento**: Piano in `/Users/macbook/.claude/plans/merry-yawning-wren.md`, sorgente SARA in `/Users/macbook/Downloads/SARA-complete-system.md`
- [x] **Voice Agent UX Polish** - Waveform bars, mic pulse ring, Sara speaking glow
  - `src/hooks/use-voice-pipeline.ts` - `audioLevel` (0-1 RMS) via AnalyserNode + VAD PCM
  - `src/pages/VoiceAgent.tsx` - 5 barre animate, pulse ring mic, glow avatar Sara
  - `src/index.css` - `@keyframes mic-pulse-ring`
  - `eslint.config.js` - Aggiunti globals `AnalyserNode`, `requestAnimationFrame`, `cancelAnimationFrame`
  - **E2E**: 12/12 test passati su iMac
- [x] **Fix Antonio Bug** - Entity extraction + session isolation + DB cleanup
  - **Problema**: "Sono Antonio vorrei prenotare" → entity extractor catturava "Antonio Vorrei" come nome completo → record corrotto nel DB → ricerche successive trovavano record sporco → skip registrazione
  - **Fix 1**: `entity_extractor.py` - Espanso NAME_BLACKLIST con 30+ verbi italiani + logica "strip trailing blacklisted words" (es. "Antonio Vorrei" → "Antonio")
  - **Fix 2**: `orchestrator.py` - Reset `booking_sm` e `disambiguation` su nuova sessione e cambio sessione (bug: stato condiviso tra sessioni diverse)
  - **Fix 3**: `orchestrator.py` - Re-register session sotto il `session_id` del chiamante (fix: ogni turno resettava il SM perché session_id non trovato)
  - **Fix 4**: `booking_state_machine.py` - Skip REGISTERING_SURNAME se `client_name` ha già nome+cognome (es. "Gianluca Distasi" → split e vai a phone)
  - **Fix 5**: Eliminato record corrotto `"Antonio Vorrei" / "Calla!"` da DB
  - **Test E2E su iMac (app Tauri aperta)**: 5 turni → registrazione "Gianluca Distasi" → record creato in DB SQLite ✅
  - **Commit**: `b053fd9`, `db8a18c`
- [x] **PRD Voice Agent** - Documento requisiti completo
  - `docs/PRD-VOICE-AGENT.md` - 7 user stories, 6 flussi conversazione, 18 stati, 6 bug mappati, 5 milestone

### Completato (2026-01-26)

- [x] **Fix VAD Manual Stop Bug** - Audio ora processato correttamente
  - **Problema**: Click stop microfono non processava audio registrato
  - **Causa**: `stopListening` tornava null se VAD non aveva rilevato fine discorso
  - **Soluzione**: `allAudioRef` tiene copia di TUTTO l'audio registrato
  - **Commit**: `fe77613`
- [x] **Fix React Hooks Error** - "Should have a queue" risolto
  - **Problema**: setState dopo unmount causava crash
  - **Causa**: cleanup useEffect chiamava cancelListening che settava state
  - **Soluzione**: `isMountedRef` + cleanup diretto senza setState
  - **Commit**: `c7dc35c`
- [x] **TEN VAD Integration** - VAD professionale STANDALONE (no cloud!)
  - **Scoperta**: TEN Framework richiede Agora RTC (cloud) → NON adatto
  - **Soluzione**: Estratta libreria `ten-vad` standalone (v1.0.6.8 PyPI)
  - `voice-agent/src/vad/ten_vad_integration.py` - FluxionVAD class
  - `voice-agent/src/vad/vad_pipeline_integration.py` - VADPipelineManager
  - `voice-agent/src/vad_http_handler.py` - HTTP endpoints per VAD
  - **Features**: Start/End of speech detection, barge-in, turn management
  - **Test**: ✅ Funziona su MacBook e iMac
  - **Demo**: `voice-agent/examples/vad_microphone_demo.py`
- [x] **Frontend VAD Integration** - UI Voice Agent con VAD real-time
  - `src/hooks/use-voice-pipeline.ts` - Hook `useVADRecorder`
  - `src/pages/VoiceAgent.tsx` - UI con indicatore probabilità voce
  - **Features**:
    - Streaming audio chunks al backend (100ms)
    - Indicatore verde (parlando) / giallo (in ascolto)
    - Barra probabilità voce in tempo reale
    - Toggle VAD/manuale nelle impostazioni
  - **Server**: v2.1.0 con endpoint `/api/voice/vad/*`
- [x] **E2E Tests** - 7/7 Voice Agent tests passati

- [x] **Voice Agent Validation** - YELLOW LIGHT (proceed with modifications)
  - **Llama 3.2 3B**: 90% accuracy PASS (target 85%)
  - **Piper TTS**: 714ms p95 PASS (target 800ms)
  - **Whisper STT**: 21.7% WER YELLOW (target 12%, needs larger model)
  - **Report**: `docs/sessions/VALIDATION-REPORT-2026-01-26.md`
- [x] **Multi-Vertical Agent System** - 5 verticali configurati
  - `voice-agent/verticals/medical/config.json` - 10 intents, 8 FAQ, 6 slots
  - `voice-agent/verticals/restaurant/config.json` - 11 intents, 8 FAQ, 8 slots
  - `voice-agent/verticals/palestra/config.json` - 11 intents, 8 FAQ, 9 slots
  - `voice-agent/verticals/auto/config.json` - 11 intents, 9 FAQ, 11 slots
  - `voice-agent/verticals/salone/config.json` - 11 intents, 9 FAQ, 8 slots
  - **Totale**: 54 intents, 42 FAQ, 42 slots
- [x] **Vertical Manager** - Sistema gestione configurazioni
  - `voice-agent/verticals/vertical_manager.py` - Load, validate, render configs
  - `voice-agent/src/vertical_integration.py` - Bridge con orchestrator
  - Self-test: tutti i verticali caricano correttamente
- [x] **Reference Repos Cloned** - Pattern extraction per verticali
  - Healthcare-AI-Voice-agent (medical patterns)
  - FoodieSpot-Reservation-Management-Agent (restaurant patterns)
  - appointment-agent (generic booking patterns)
- [x] **Qwen3-TTS Analysis** - NOT viable per legacy hardware
  - iMac 2012 (512MB GPU) vs Qwen3 requirement (2-4GB VRAM)
  - Recommendation: Piper TTS + Groq fallback
- [x] **Commit** - `14ae2d4` 12 files, 4130 insertions

### Completato (2026-01-25)

- [x] **Voice Agent Strategy Analysis** - Analisi completa stack Voice Agent
  - Confronto: Llama locale vs RASA CALM vs Groq Cloud
  - Costi: Groq free tier 14,400 req/day, Whisper $0.04/ora
  - Decisione: **Validation-first** prima di investire 9 giorni dev
  - Documenti: `validation-phase-cto.md`, `voice-agent-complete.md`
- [x] **Bug Fix session_manager.py** - Ricorsione infinita fixata
  - `close_session()` chiamava `get_session()` → loop infinito
  - Fix: `self._sessions.get(session_id)` invece di `self.get_session()`
- [x] **Voice Pipeline Restart** - Nuovo PID 72955 (era 84591)
- [x] **Test LIVE Voice Agent** - Identificati 3 bug critici ancora aperti:
  - Entity extraction rotta ("Mario Rossi" → chiede cognome)
  - Database path mismatch (HTTP Bridge legge DB sbagliato)
  - Flusso sempre propone registrazione
- [x] **Commit hooks** - `246f37f` pushato

### Completato (2026-01-24)

- [x] **Claude Code Hooks** - Sistema hooks per automazione sessione
  - `session-start.sh` - Mostra stato git, verifica servizi iMac, carica contesto CLAUDE.md
  - `check-services.sh` - Verifica HTTP Bridge (3001) e Voice Pipeline (3002)
  - `restart-services.sh` - Riavvia pipeline Python su iMac
  - **Configurazione**: `.claude/settings.local.json` con hooks SessionStart e UserPromptSubmit
- [x] **Skill fluxion-service-rules** - Regole per gestione servizi
  - Regola critica: riavviare pipeline dopo modifiche Python
  - Checklist pre-test Voice Agent
  - Warning signs per debug
- [x] **Fix Voice Agent "Antonio"** - Pipeline non riconosceva nome perché non riavviata
  - **Root cause**: Pipeline Python avviata Gio 23 Gen, mai riavviata dopo fix
  - **Soluzione**: `pkill -f 'python main.py'` + riavvio
  - **Ora funziona**: "Sono Antonio" → "Non ho trovato Antonio... Vuole registrarsi?"
- [x] **Commit pushato** - `22e2a05` sincronizzato su GitHub e iMac

### Completato (2026-01-23)

- [x] **Voice Agent Full Integration Fix** - Tutti gli endpoint HTTP Bridge funzionanti
  - **VA-01**: Client search → funziona, lookup via GET /api/clienti/search?q=
  - **VA-02**: Client create → funziona, POST /api/clienti/create, record creato in DB
  - **VA-03**: Booking create → funziona, POST /api/appuntamenti/create, campo servizio→servizio
  - **VA-04**: Field mapping → fixato service→servizio, date→data, time→ora, client_id→cliente_id
  - **VA-05**: Cancel booking → NUOVO endpoint POST /api/appuntamenti/cancel
  - **VA-06**: Reschedule booking → NUOVO endpoint POST /api/appuntamenti/reschedule
  - **VA-07**: Waitlist → NUOVO handler waitlist con offerta automatica quando slot non disponibili
  - **VA-08**: Guided Dialog → 38/38 test passati, funzionante
  - **Test**: 82 Python tests passati (booking_state_machine + pipeline_e2e)
  - **Files**: `http_bridge.rs`, `orchestrator.py`, `booking_state_machine.py`, `intent_classifier.py`
- [x] **Intent SPOSTAMENTO** - Nuovo intent per rescheduling appuntamenti
  - Pattern: "sposta", "cambia", "modifica", "anticipa", "posticipa"
  - Handler in orchestrator.py che chiede data appuntamento
- [x] **Waitlist Integration** - Offerta automatica lista d'attesa
  - Quando no slots disponibili → "Vuole che la inserisca in lista d'attesa?"
  - Conferma/Rifiuto gestiti correttamente
  - Record creato in DB con lookup servizio_id e operatore_id
- [x] **Voice Agent Auto-Greet** - Auto-saluto quando pipeline già attiva
  - **Problema**: Navigando su Voice Agent con pipeline running, nessun messaggio appariva
  - **Fix**: useEffect che triggera `greet.mutateAsync()` se `isRunning && messages.length === 0`
  - **File**: `src/pages/VoiceAgent.tsx`
- [x] **Error Handling VoiceAgent** - Migliorata gestione errori in `handleVoiceResponse`
  - Check `!response.success || !response.response` prima di processare
  - Aggiunta error message alla chat quando voice response fallisce
  - Spinner si ferma correttamente anche in caso di errore
- [x] **E2E Tests** - 12/12 passed (type-check, lint, Playwright via SSH iMac)
- [x] **Commit** - `a19d2b7` pushato su origin/master

### Completato (2026-01-22)

- [x] **Fix Voice Agent UI Microphone Bug** - BUG-V5 ✅
  - **Problema**: Click su microfono avviava registrazione ma non si fermava al secondo click
  - **Root cause**: `stopRecording()` chiamava `mediaRecorder.stop()` senza verificare lo state
  - **Fix**: Check `mediaRecorder.state === 'inactive'` + cleanup immediato + debug logs
  - **File**: `src/hooks/use-voice-pipeline.ts` (stopRecording, cancelRecording)
- [x] **E2E Testing Playwright** - Setup completo per testing headless su iMac via SSH
  - `playwright.headless.config.ts` - Config Chromium headless, webServer vite
  - `tests/e2e/smoke.test.ts` - 5 test: app load, sidebar, dashboard, Tauri API, console errors
  - `tests/e2e/voice-agent.test.ts` - 7 test (3 UI, 4 pipeline-dependent skippati in browser mode)
  - `scripts/run-e2e-remote.sh` - Script esecuzione remota SSH
  - **Risultato**: 8 passed, 4 skipped (49.3s)
- [x] **HTTP Fallback Browser Mode** - Hooks voice-pipeline supportano browser mode
  - `isInTauri()` detection per Tauri vs browser
  - `httpFallback()` per chiamate HTTP a voice pipeline (porta 3002)
  - Test E2E skip automatico quando Tauri API non disponibile

### Completato (2026-01-21)

- [x] **Guided Dialog Engine** - Sistema conversazionale guidato per Voice Agent
  - `guided_dialog.py` (~1200 linee): DialogState machine, fuzzy matching italiano
  - 5 configurazioni verticali JSON: salone, palestra, medical, auto, default
  - Integrazione con `orchestrator.py`: fallback automatico
  - Test suite: 38 test cases passati (MacBook + iMac)
  - Self-test: 8 turni conversazione → SUCCESS
- [x] **Test Suite Voice Agent** - 409 test passati + 43 skipped (PyTorch)
  - pytest guided_dialog: 38/38 ✅
  - pytest voice-agent full: 409 passati
  - TypeScript type-check: ✅
  - ESLint: ✅
- [x] **Claude Code Skills** - 3 skill files creati
  - `fluxion-tauri-architecture/SKILL.md` - Pattern architetturali
  - `fluxion-voice-agent/SKILL.md` - Voice agent patterns
  - `fluxion-workflow/SKILL.md` - Epic→Story→Task workflow
- [x] **Test WhatsApp QR Scan UI** - Funzionalità verificata
  - Servizio Node.js (`whatsapp-service.cjs`): ✅ Avvio OK
  - Generazione QR code: ✅ Funziona (whatsapp-web.js)
  - Fix QR rendering: ✅ Passato da API esterna a `qrcode.react` locale
- [x] **Deploy su iMac** - git pull + test passati (Python 3.9 venv)

### Completato (2026-01-20)

- [x] **Test Voice Agent Sara** - 426 test passati + conversazione completa
  - NLU (Intent + Entity extraction): ✅ Funziona
  - FAQ Retrieval (keyword): ✅ Funziona
  - Groq LLM fallback: ✅ Funziona (714-998ms)
  - TTS: ⚠️ SystemTTS (Chatterbox richiede PyTorch, non disponibile su Python 3.13)
  - Semantic FAISS: ⚠️ Disabilitato (sentence-transformers richiede PyTorch)
- [x] **Test Prenotazione Completa con Backend** - iMac (192.168.1.9)
  - Conversazione 7 turni: servizio → data → ora → nome → telefono → email → conferma
  - Sara conferma: "Sabato 24 gennaio alle 10:00, la aspettiamo"
  - Estrazione entità corretta: data, ora, nome, telefono, email
- [x] **Verifica CI/CD Workflows** - 4 workflow configurati
  - `test-suite.yml` - Fast check (develop) + Full suite (PR to main)
  - `e2e-tests.yml` - WebDriverIO su ubuntu-latest
  - `release-full.yml` - Build + release
  - ⚠️ E2E non supportato su macOS (tauri-driver limitation)
- [x] **Modello Business documentato** - Licenze lifetime, pacchetti, assistenza a pagamento
- [x] **Decisione Email** - SMTP Gmail (pacchetto Enterprise), Resend scartato
- [x] **IP iMac aggiornato** - 192.168.1.9 (era 192.168.1.2)

### Completato (2026-01-19)

- [x] **Fix tauri.conf.json duplicato** - Rimosso file root su iMac che causava build error
- [x] **Verifica UI Impostazioni SMTP** - App avviata, UI accessibile

### Completato (2026-01-17)

- [x] **Test invio ordine WhatsApp** - wa.me URL funziona correttamente
- [x] **Email SMTP configurabile** - Credenziali salvate in DB, UI in Impostazioni
- [x] **Migration 017** - SMTP settings in tabella `impostazioni`
- [x] **Rust commands settings.rs** - get/save/test SMTP settings
- [x] **HTTP Bridge endpoint** - `/api/settings/smtp` per Python
- [x] **SmtpSettings.tsx** - UI configurazione email in Impostazioni
- [x] **Fix openUrl** - Usa plugin-opener invece di window.open

### Bloccante: macOS Compatibility

⚠️ **Tauri 2.9.5 NON funziona su macOS Big Sur (11.x)**
- Crash: `webView:requestMediaCapturePermissionForOrigin:` (API macOS 12+)
- **Workaround**: Sviluppo/test su iMac (macOS 12.7.4 Monterey)
- **Alternativa**: Aggiornare macOS su MacBook

⚠️ **Python 3.13 Limitazioni**
- PyTorch non disponibile → Chatterbox TTS e FAISS semantic search disabilitati
- Voice Agent funziona con SystemTTS (macOS say) e keyword search
- **Workaround**: Usare Python 3.11 per TTS avanzato

### Completato (Fase 7.5 - 2026-01-16)

- [x] **Fornitori Page UI** - Pagina completa con tabs Fornitori/Ordini
- [x] **FornitoriTable** - Lista fornitori con edit/delete, status badge
- [x] **FornitoreDialog** - Form CRUD fornitore (nome, email, telefono, P.IVA, note)
- [x] **SupplierOrdersTable** - Lista ordini con azioni Email/WhatsApp/Status
- [x] **OrderDialog** - Creazione ordine con items dinamici + importo totale
- [x] **Excel Import** - Import listino da file Excel/CSV/Word (SheetJS + mammoth.js)
- [x] **Auto-detect columns** - Mapping automatico colonne (descrizione, prezzo, qty, sku)
- [x] **SendConfirmDialog** - Dialog conferma invio con preview messaggio
- [x] **use-file-parser hook** - Parse Excel/Word con column mapping
- [x] **use-fornitori hook** - React Query mutations per tutte le operazioni
- [x] **Fix Rust type mismatch** - `CreateOrderRequest.items` da `Vec<Value>` a `String`
- [x] **Fix async state bug** - `autoDetectMapping`/`mapToProducts` con parametri diretti

### Completato (Fase 7)

- [x] Voice Agent RAG integration (Week 1-3)
- [x] HTTP Bridge endpoints (15 totali)
- [x] Waitlist con priorità VIP
- [x] Disambiguazione cliente con data_nascita + soprannome (fallback)
- [x] Registrazione nuovo cliente via conversazione
- [x] Preferenza operatore con alternative
- [x] E2E Test Suite Playwright (smoke + dashboard)
- [x] **VoIP Integration (Week 4)** - SIP/RTP per Ehiweb (voip.py, 39 tests)
- [x] **WhatsApp Integration (Week 5)** - Client Python + templates + analytics (whatsapp.py, 52 tests)
- [x] **Voice Agent UI ↔ Pipeline Integration** - STT (Whisper) + NLU + TTS nel frontend
- [x] **Disambiguazione deterministica** - data_nascita → soprannome fallback ("Mario o Marione?")
- [x] **Release Sprint 2026-01-15** - TypeScript clean, E2E smoke 8/8, Voice Agent OK
- [x] **Fix test-suite.yml** - Nightly job condition (github.event_name == 'schedule')
- [x] **E2E Playwright fallback** - Firefox per macOS Big Sur compatibility
- [x] **NLU Upgrade** - spaCy + UmBERTo 4-layer pipeline (~100ms, 100% offline)
- [x] **TTS Upgrade** - Chatterbox Italian (9/10 quality) + Piper fallback
- [x] **Voice Assistant Rebrand** - Nome voce: "Sara" (uniformato su tutto il codebase)
- [x] **Stack Analysis** - `docs/analysis/STACK_ANALYSIS.md` + `PMI_VERTICALS_ANALYSIS.md`
- [x] **FAQ Verticali System** - 96 FAQ production-ready per 5 verticali (via Perplexity)
- [x] **Vertical Loader** - `vertical_loader.py` carica FAQ per verticale con sostituzione variabili
- [x] **SQL Seed Files** - `src-tauri/migrations/seeds/` (60 servizi default per verticale)
- [x] **Deployment Guide** - `docs/DEPLOYMENT.md` (checklist, SLA, benchmarks, security)
- [x] **n8n Workflows** - `n8n-workflows/shared/whatsapp-voice-bridge.json` (copy-paste ready)
- [x] **Architecture Diagrams** - `docs/images/` (5 PNG da Perplexity: gantt, latency, architecture)
- [x] **Integration Testing Guide** - `docs/INTEGRATION_TESTING_GUIDE.md` (6 test suites)
- [x] **Test Scripts** - `scripts/tests/` (voice, http, sqlite, whatsapp, master runner)
- [x] **MCP Server Complete** - `mcp-server/src/index.ts` (8 tools, 9 resources, SQLite integration)
- [x] **n8n Additional Workflows** - booking-reminder, loyalty-update (copy-paste ready)
- [x] **data-testid Components** - E2E selectors per Sidebar, Dashboard, Clienti, Calendario
- [x] **WhatsApp QR Scan UI** - `WhatsAppQRScan.tsx` per login WhatsApp Business
- [x] **GDPR Encryption** - `encryption.rs` AES-256-GCM per dati sensibili
- [x] **Supplier Management Backend** - 14 Rust commands + migration 016 + SMTP + WhatsApp

### Prossimo (Priorità Testing → Fase 8)

**Testing Prioritario (2026-01-20):**
- [x] Test invio ordine via WhatsApp (wa.me URL) ✅
- [x] **Test Voice Agent Sara** ✅ 426 test + conversazione prenotazione OK
- [ ] **Test WhatsApp QR Scan UI** (connessione WhatsApp Business) ← PROSSIMO
- [ ] Test SMTP Email (Gmail App Password)
- [ ] n8n workflow automazione ordini

**Fase 8 - Build + Licenze:**
- [ ] Build macOS/Windows con Tauri
- [ ] Sistema licenze Keygen.sh

---

## Requisito: Configurazione Variabili all'Installazione

⚠️ **IMPORTANTE**: Tutte le variabili di ambiente devono essere configurabili al momento dell'installazione tramite Setup Wizard, NON hardcoded nel .env.

### Variabili da Configurare nel Setup Wizard

| Categoria | Variabile | Descrizione | Obbligatoria |
|-----------|-----------|-------------|--------------|
| **AI/LLM** | `GROQ_API_KEY` | API Key Groq per STT + LLM | ✅ |
| **SMTP** | `SMTP_HOST` | Server SMTP (default: smtp.gmail.com) | Per Email |
| **SMTP** | `SMTP_PORT` | Porta SMTP (default: 587) | Per Email |
| **SMTP** | `EMAIL_FROM` | Email mittente | Per Email |
| **SMTP** | `EMAIL_PASSWORD` | App Password Gmail | Per Email |
| **Azienda** | `BUSINESS_NAME` | Nome attività | ✅ |
| **Azienda** | `AZIENDA_PARTITA_IVA` | P.IVA | Per Fatture |
| **Azienda** | `AZIENDA_*` | Dati fiscali completi | Per Fatture |
| **VoIP** | `VOIP_SIP_*` | Credenziali SIP Ehiweb | Per VoIP |
| **WhatsApp** | `WHATSAPP_PHONE` | Numero WhatsApp Business | Per WA |

### Implementazione

1. **Setup Wizard (Step 1-3)**: Raccoglie tutte le variabili essenziali
2. **Impostazioni App**: Permette modifica successiva
3. **Database**: Variabili salvate in tabella `impostazioni`
4. **Fallback**: Se non configurato, legge da .env (solo dev)

**Fase 8 continua:**
- [ ] Auto-update con tauri-plugin-updater
- [ ] Code signing e notarization macOS

### Bug Aperti e Funzionalità NON Funzionanti

> ⚠️ **ATTENZIONE**: Questa lista contiene problemi REALI verificati. NON marcare come risolto senza test E2E + verifica DB!

#### CRITICI (P0) - Voice Agent NON funziona senza questi

| ID | Descrizione | Codice Esiste | Funziona | Fix In Corso |
|----|-------------|---------------|----------|--------------|
| VA-01 | **Client search non triggera** - Sara non cerca cliente nel DB | ✅ | ❌ | 🔄 2026-01-23 |
| VA-02 | **Client create non funziona** - Nuovo cliente mai creato in DB | ✅ | ❌ | 🔄 2026-01-23 |
| VA-03 | **Booking create non funziona** - Appuntamento mai creato in DB | ✅ | ❌ | 🔄 2026-01-23 |
| VA-04 | **Campo names mismatch** - Python usa `service`, Rust vuole `servizio` | ✅ | ❌ | 🔄 2026-01-23 |

#### ALTI (P1) - Funzionalità core mancanti

| ID | Descrizione | Codice Esiste | Funziona | Note |
|----|-------------|---------------|----------|------|
| VA-05 | **Cancella appuntamento** - Solo regex, no endpoint | ⚠️ Pattern | ❌ | Serve endpoint `/api/appuntamenti/cancel` |
| VA-06 | **Sposta appuntamento** - Solo intent detection | ⚠️ Intent | ❌ | Serve endpoint `/api/appuntamenti/reschedule` |
| VA-07 | **Lista d'attesa** - Endpoint esiste, mai integrato | ✅ Endpoint | ❌ | Handler in orchestrator mancante |
| VA-08 | **Guided Dialog** - File esiste, mai verificato | ✅ 1205 righe | ❓ | Da testare se utente va "fuori strada" |

#### MEDI (P2) - UX e robustezza

| ID | Descrizione | Codice Esiste | Funziona | Note |
|----|-------------|---------------|----------|------|
| VA-09 | **Operatore preferenza** - Non chiede operatore | ⚠️ | ❌ | Da verificare flusso |
| VA-10 | **Disambiguazione** - Mai testata end-to-end | ✅ | ❓ | Richiede 2+ clienti omonimi |
| VA-11 | **Disponibilità slot** - Verifica ma non propone alternative | ✅ | ⚠️ | Da migliorare UX |

#### RISOLTI

| ID | Descrizione | Priority | Data Fix |
|----|-------------|----------|----------|
| BUG-V5 | Voice UI: microfono non si ferma al click/stop | P1 | 2026-01-22 |
| BUG-V2 | Voice UI si blocca dopo prima frase | P1 | 2026-01-15 |
| BUG-V3 | Paola ripete greeting invece di chiedere nome | P1 | 2026-01-15 |
| BUG-V4 | "mai stato" interpretato come nome "Mai" | P1 | 2026-01-15 |

---

### Criterio per marcare RISOLTO

```
1. Codice scritto e deployato
2. Test manuale: conversazione completa funziona
3. Verifica DB: SELECT conferma record creati
4. Test E2E passa (se applicabile)
```

**BUG-V5 - Voice UI Microphone** (`src/hooks/use-voice-pipeline.ts`) - ✅ RISOLTO 2026-01-22:
- **Problema**: Click su microfono avvia registrazione ma non si ferma al secondo click
- **Root cause**: `stopRecording()` chiamava `mediaRecorder.stop()` senza verificare se era in `inactive` state
- **Soluzione**: Check `mediaRecorder.state === 'inactive'` prima di stop + cleanup immediato state + debug logs
- **Fix**: Linee 345-402 in `use-voice-pipeline.ts`

### Fix Recenti (2026-01-15)

**BUG-V4 - NLU Upgrade** (`voice-agent/src/nlu/italian_nlu.py`):
- **Problema**: Voice agent interpretava "Io non sono mai stato da voi" come cliente "Mai"
- **Soluzione**: 4-layer NLU pipeline con spaCy + UmBERTo (regex → NER → intent → context)
- **Test**: "mai stato", "prima volta" → NUOVO_CLIENTE ✅

**TTS Upgrade - Sara Voice** (`voice-agent/src/tts.py`):
- **Problema**: Aurora (Piper) aveva pause enfatiche randomiche, pronuncia italiana mediocre
- **Soluzione**: Multi-engine TTS con Chatterbox Italian (primario) + Piper Paola (fallback)
- **Nome voce**: Sara (unificato su tutto il codebase)
- **Qualità**: 9/10 (vs 6.5/10 Aurora), latenza 100-150ms CPU
- **File**: `docs/context/CHATTERBOX-ITALIAN-TTS.md`

**BUG-V3 - Greeting Loop Fix** (`orchestrator.py`):
- **Problema**: L1 intercettava CORTESIA ("Buongiorno") e rispondeva con altro greeting
- **Soluzione**: `is_first_turn` flag - L1 salta CORTESIA al primo turno, L2 sempre attivo
- **File**: `voice-agent/src/orchestrator.py` (linee ~340-430)

---

## Fasi Progetto

| Fase | Nome | Status |
|------|------|--------|
| 0 | Setup Iniziale | ✅ |
| 1 | Layout + Navigation | ✅ |
| 2 | CRM Clienti | ✅ |
| 3 | Calendario + Booking | ✅ |
| 4 | Fluxion Care | ✅ |
| 5 | Quick Wins Loyalty | ✅ |
| 6 | Fatturazione Elettronica | ✅ |
| 7 | Voice Agent + WhatsApp | 📋 IN CORSO |
| 8 | Build + Licenze | 📋 TODO |
| 9 | Moduli Verticali | 📋 TODO |

---

## Modello Business e Licenze

### Licenze Lifetime (3 Livelli)

| Livello | Nome | Prezzo | Target |
|---------|------|--------|--------|
| 1 | **Starter** | €XXX | Freelancer, micro-attività |
| 2 | **Professional** | €XXX | PMI 1-5 dipendenti |
| 3 | **Enterprise** | €XXX | PMI 5-15 dipendenti |

> ⚠️ **TODO**: Definire pacchetti e prezzi con **prompt Perplexity benchmark** (analisi competitor gestionali PMI italiane, pricing strategies, valore percepito per verticale)

### Funzionalità a Pacchetti

| Modulo | Starter | Professional | Enterprise |
|--------|---------|--------------|------------|
| CRM Clienti | ✅ | ✅ | ✅ |
| Calendario/Booking | ✅ | ✅ | ✅ |
| Fatturazione Base | ✅ | ✅ | ✅ |
| WhatsApp (wa.me) | ✅ | ✅ | ✅ |
| Fatturazione Elettronica SDI | ❌ | ✅ | ✅ |
| **Fluxion AI (Voice Agent Sara)** | ❌ | ❌ | ✅ |
| **Email SMTP (Gmail)** | ❌ | ❌ | ✅ |
| Fornitori + Ordini | ❌ | ❌ | ✅ |
| VoIP Integration | ❌ | ❌ | ✅ |
| Multi-sede | ❌ | ❌ | ✅ |

> **Fluxion AI** e **Email** sono funzionalità **Enterprise only** (pacchetto avanzato).

### Costi Operativi (a carico vendor)

| Servizio | Costo/mese | Note |
|----------|------------|------|
| **Groq API** | €0 | Free tier, STT + LLM |
| **Keygen.sh** | €0-50 | Gestione licenze |

> Email SMTP: il cliente usa il proprio account Gmail (App Password). Costo €0 per vendor.

### Assistenza

| Tipo | Incluso | Costo |
|------|---------|-------|
| **Documentazione + FAQ** | ✅ Sempre | €0 |
| **Aggiornamenti software** | ✅ Lifetime | €0 |
| **Assistenza remota** | ❌ | A pagamento (€/ora o pacchetto) |
| **Personalizzazioni** | ❌ | Preventivo |

### Decisioni Tecniche Correlate

- **Email SMTP**: Gmail App Password (cliente configura in Impostazioni)
- **WhatsApp**: wa.me URL (zero costi, zero config)
- **Voice**: Groq free tier (Whisper + Llama)
- **Licenze**: Keygen.sh con validazione offline

> **Nota**: Fluxion AI (Voice Agent Sara) e Email SMTP sono funzionalità del **pacchetto avanzato**.

---

## Voice Agent Roadmap

| # | Funzionalità | Endpoint/File | Status |
|---|--------------|---------------|--------|
| 1 | Cerca clienti | `/api/clienti/search` | ✅ Testato |
| 2 | Crea appuntamenti | `/api/appuntamenti/create` | ✅ Testato |
| 3 | Verifica disponibilità | `/api/appuntamenti/disponibilita` | ✅ |
| 4 | Lista d'attesa VIP | `/api/waitlist/add` | ✅ Testato |
| 5 | Disambiguazione data_nascita | `disambiguation_handler.py` | ✅ |
| 6 | Disambiguazione soprannome | `disambiguation_handler.py` | ✅ |
| 7 | Registrazione cliente | `/api/clienti/create` | ✅ Testato |
| 8 | Preferenza operatore | `/api/operatori/list` | ✅ |
| 9 | Cancella appuntamento | `/api/appuntamenti/cancel` | ✅ NUOVO |
| 10 | Sposta appuntamento | `/api/appuntamenti/reschedule` | ✅ NUOVO |
| 11 | Guided Dialog fallback | `guided_dialog.py` | ✅ Testato |

### Flusso Disambiguazione

```
1. "prenotazione per Mario Rossi"
   → "Ho trovato 2 clienti. Mi può dire la sua data di nascita?"

2. Data sbagliata (es. "10 gennaio 1980")
   → "Non ho trovato questa data. Mario o Marione?"

3. "Marione"
   → "Perfetto, Mario Rossi!" (cliente con soprannome)
```

---

## Supplier Management (Fase 7.5)

### Schema Database

| Tabella | Descrizione | Campi Chiave |
|---------|-------------|--------------|
| `suppliers` | Anagrafica fornitori | id, nome, email, telefono, partita_iva, status |
| `supplier_orders` | Ordini a fornitori | id, supplier_id, ordine_numero, importo_totale, status, items (JSON) |
| `supplier_interactions` | Log comunicazioni | id, supplier_id, order_id, tipo (email/whatsapp), messaggio |

**Migration**: `src-tauri/migrations/016_suppliers.sql`

### Rust Commands (14)

| Command | Descrizione |
|---------|-------------|
| `create_supplier` | Crea nuovo fornitore |
| `get_supplier` | Dettagli fornitore |
| `list_suppliers` | Lista fornitori (attivi) |
| `update_supplier` | Modifica fornitore |
| `delete_supplier` | Soft delete (status=inactive) |
| `search_suppliers` | Ricerca per nome/email/P.IVA |
| `create_supplier_order` | Crea ordine |
| `get_supplier_order` | Dettagli ordine |
| `get_supplier_orders` | Ordini per fornitore |
| `list_all_orders` | Tutti gli ordini (filtro status) |
| `update_order_status` | Aggiorna stato ordine |
| `log_supplier_interaction` | Log email/WA inviata |
| `get_supplier_interactions` | Storico comunicazioni |
| `get_supplier_stats` | Statistiche (totali, pending, spent) |

**File**: `src-tauri/src/commands/supplier.rs`

### Comunicazione Fornitori

| Canale | File | Status |
|--------|------|--------|
| **WhatsApp** | `scripts/whatsapp-service.cjs` | ✅ Primario |
| **Email SMTP** | `src-tauri/src/commands/settings.rs` + UI Impostazioni | ✅ Implementato |

> **Decisione 2026-01-20**: Email via SMTP Gmail (App Password). Cliente configura in Impostazioni.

**Funzioni WhatsApp:**
- `sendSupplierOrder(client, phone, orderData)` - Invia ordine
- `sendSupplierReminder(client, phone, orderNumero, giorni)` - Promemoria
- `sendConfirmationRequest(client, phone, orderNumero, name)` - Richiesta conferma

**Template Email:**
- HTML responsive con tabella articoli
- Pulsante "Conferma Ricezione"
- Variabili: `{{order_numero}}`, `{{items}}`, `{{total}}`, `{{data_consegna}}`

### Ordine Implementazione

```
1. Database Migration (016_suppliers.sql) ✅
2. Rust Commands (supplier.rs) ✅
3. Python SMTP Service ✅
4. WhatsApp Extension ✅
5. Frontend UI (TODO)
6. n8n Workflow (TODO)
```

---

## FAQ Verticali System

### File Produzione

| Verticale | File | FAQ | Generato |
|-----------|------|-----|----------|
| salone | `voice-agent/data/faq_salone.json` | 25 | Perplexity |
| wellness | `voice-agent/data/faq_wellness.json` | 24 | Perplexity |
| medical | `voice-agent/data/faq_medical.json` | 24 | Perplexity |
| auto | `voice-agent/data/faq_auto.json` | 23 | Perplexity |
| altro | `voice-agent/data/faq_altro.json` | 10 | Manuale |

### Architettura

```
1. Setup Wizard → utente sceglie categoria_attivita (salone/wellness/medical/auto/altro)
2. Orchestrator.start_session() → carica faq_{verticale}.json
3. vertical_loader.py → sostituisce {{VARIABILI}} con dati DB
4. FAQManager → keyword + semantic search (FAISS)
5. Sara risponde con dati personalizzati
```

### Roadmap Spreadsheet (TODO)

Convertire FAQ in formato spreadsheet interattivo con 2 fogli:

| Foglio | Contenuto |
|--------|-----------|
| **FAQ Database** | Tabella completa FAQ (ID, categoria, keywords, variabili) |
| **Variabili Configurazione** | Dizionario variabili (descrizione, esempio, tipo, obbligatorietà) |

**Vantaggi:**
- Gestione FAQ centralizzata
- Configurazione rapida nuove attività
- Base per automazione chatbot/CRM
- Versioning e tracking cambiamenti

**Esempio:** `FAQ Auto Officina.xlsx` (23 FAQ, ~50 variabili)

---

## Infrastruttura

```yaml
# Test Machines
iMac:
  host: imac (192.168.1.9)  # Aggiornato 2026-01-20
  path: /Volumes/MacSSD - Dati/fluxion

Windows PC:
  host: 192.168.1.17
  path: C:\Users\gianluca\fluxion

# Porte
HTTP Bridge: 3001
Voice Pipeline: 3002
MCP Server: 5000
```

---

## Riferimenti Rapidi

| Risorsa | Path |
|---------|------|
| **Procedure Operative** | `docs/FLUXION-ORCHESTRATOR.md` |
| **Voice Agent RAG Enterprise** | `docs/context/VOICE-AGENT-RAG-ENTERPRISE.md` |
| **Stack Analysis** | `docs/analysis/STACK_ANALYSIS.md` |
| **PMI Verticali** | `docs/analysis/PMI_VERTICALS_ANALYSIS.md` |
| **Chatterbox TTS** | `docs/context/CHATTERBOX-ITALIAN-TTS.md` |
| **FAQ Verticali** | `voice-agent/data/faq_*.json` |
| **Vertical Loader** | `voice-agent/src/vertical_loader.py` |
| **SQL Seeds** | `src-tauri/migrations/seeds/seed_*.sql` |
| **Prompts Perplexity** | `docs/prompts/PROMPT_GENERA_*.md` |
| **Template Spreadsheet** | `docs/templates/FAQ Auto Officina.xlsx` |
| **Deployment Guide** | `docs/DEPLOYMENT.md` |
| **n8n Workflows** | `n8n-workflows/shared/*.json` |
| **Architecture Images** | `docs/images/*.png` |
| **Integration Testing** | `docs/INTEGRATION_TESTING_GUIDE.md` |
| **MCP Server Guide** | `docs/MCP_SERVER_IMPLEMENTATION.md` |
| **Test Scripts** | `scripts/tests/run-all-tests.sh` |
| **n8n Auto Workflows** | `n8n-workflows/auto/*.json` |
| **n8n Salone Workflows** | `n8n-workflows/salone/*.json` |
| Voice Agent Base | `docs/context/CLAUDE-VOICE.md` |
| Fasi Completate | `docs/context/COMPLETED-PHASES.md` |
| Cronologia Sessioni | `docs/context/SESSION-HISTORY.md` |
| Decisioni Architetturali | `docs/context/DECISIONS.md` |
| Schema DB | `docs/context/CLAUDE-BACKEND.md` |
| Design System | `docs/FLUXION-DESIGN-BIBLE.md` |

---

## Agenti (25)

Routing completo in [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md#routing-matrix)

| Dominio | Agente | File Contesto |
|---------|--------|---------------|
| Backend | `@agent:rust-backend` | CLAUDE-BACKEND.md |
| Frontend | `@agent:react-frontend` | CLAUDE-FRONTEND.md |
| Voice | `@agent:voice-engineer` | CLAUDE-VOICE.md |
| **Voice RAG** | `@agent:voice-rag-specialist` | VOICE-AGENT-RAG-ENTERPRISE.md |
| Fatture | `@agent:fatture-specialist` | CLAUDE-FATTURE.md |
| Test E2E | `@agent:e2e-tester` | docs/testing/ |
| Debug | `@agent:debugger` | — |

---

## Environment

```bash
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556
GITHUB_TOKEN=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
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it
TTS_ENGINE=chatterbox           # Primary: Chatterbox Italian (9/10)
TTS_FALLBACK=piper              # Fallback: Piper paola-medium (7.5/10)
TTS_VOICE_NAME=Sara             # Unified voice assistant name
WHATSAPP_PHONE=393281536308
```

---

## Workflow Sessione

1. **Inizio**: Leggi questo file → stato corrente
2. **Come fare**: Consulta [`docs/FLUXION-ORCHESTRATOR.md`](docs/FLUXION-ORCHESTRATOR.md)
3. **Fine**: Aggiorna stato + crea sessione + commit

---

## ⛔ REGOLA CRITICA: Workflow Task Completion

> **UN TASK NON È "COMPLETATO" FINCHÉ IL CODICE NON FUNZIONA REALMENTE**

### Workflow OBBLIGATORIO per ogni task

```
1. ✅ Analizzare il problema
2. ✅ Scrivere documentazione (se necessaria)
3. ✅ FIXARE IL CODICE VERO (non solo descriverlo!)
4. ✅ TESTARE che funziona (manualmente o con test automatici)
5. ✅ VERIFICARE side-effects reali (es. record nel DB, API chiamate)
6. ✅ Solo DOPO → aggiornare CLAUDE.md con "completato"
```

### ❌ VIETATO

- Marcare come "completato" task che sono solo documentati
- Scrivere "implementato" senza aver scritto codice funzionante
- Confermare booking/azioni senza verificare che il DB sia aggiornato
- Dire "endpoint pronti" senza verificare che vengano CHIAMATI

### ✅ Definizione di DONE

| Tipo Task | Criteri di Completamento |
|-----------|--------------------------|
| Bug fix | Codice fixato + test che passa + verificato manualmente |
| Feature | Codice scritto + funziona end-to-end + DB aggiornato |
| Integration | API chiamata + response corretta + side-effect verificato |
| Voice Agent | Conversazione completa + AZIONE REALE eseguita (cliente/appuntamento in DB) |

### Esempio SBAGLIATO vs CORRETTO

**❌ SBAGLIATO (cosa ho fatto per 2 settimane):**
```
- [x] Voice Agent booking integration
  - Documentato flusso
  - Endpoint HTTP definiti
  - "Implementato" ← FALSO: il codice non chiama gli endpoint!
```

**✅ CORRETTO:**
```
- [x] Voice Agent booking integration
  - orchestrator.py chiama POST /api/appuntamenti/create
  - Testato: "Prenota taglio domani" → record ID 42 nel DB
  - Verificato con: SELECT * FROM appuntamenti WHERE id=42
```

---

## ⛔ REGOLA ASSOLUTA: Test PRIMA di Commit

> **NON FARE MAI COMMIT SENZA AVER ESEGUITO TUTTI I TEST**

### Checklist Pre-Commit (OBBLIGATORIA)

```bash
# 1. Type-check TypeScript
npm run type-check

# 2. Linter
npm run lint

# 3. Unit tests Rust (se backend modificato)
cd src-tauri && cargo test && cd ..

# 4. Unit tests Python (se voice-agent modificato)
cd voice-agent && pytest tests/ -v && cd ..

# 5. E2E Tests via SSH (SE modifiche UI/frontend) ← NUOVO
bash scripts/run-e2e-remote.sh gianlucadistasi 192.168.1.9

# 6. SOLO SE TUTTI I TEST PASSANO → Commit
git add . && git commit -m "..."
```

### Quando Eseguire Ogni Test

| Modifica | Type-check | Lint | Cargo test | Pytest | E2E (iMac) |
|----------|------------|------|------------|--------|------------|
| Frontend (.tsx, .ts) | ✅ | ✅ | ❌ | ❌ | ✅ |
| Rust backend (.rs) | ❌ | ❌ | ✅ | ❌ | ⚠️ (se UI) |
| Voice Agent (.py) | ❌ | ❌ | ❌ | ✅ | ✅ |
| Hooks/State | ✅ | ✅ | ❌ | ❌ | ✅ |
| Solo docs/config | ❌ | ❌ | ❌ | ❌ | ❌ |

> **E2E**: `bash scripts/run-e2e-remote.sh gianlucadistasi 192.168.1.9`

### Sync Manuale su iMac (se necessario debug)

```bash
# Sync singolo file per debug
scp /Volumes/MontereyT7/FLUXION/path/to/file.ts "imac:/Volumes/MacSSD\ -\ Dati/fluxion/path/to/"

# Test manuale su iMac
ssh imac "bash -l -c 'cd /Volumes/MacSSD\\ -\\ Dati/fluxion && npm run tauri dev'"
```

**Motivo**: Tauri 2.x non funziona su macOS Big Sur. Sviluppo su MacBook, test su iMac (Monterey 12.7.4).

---

## 🧪 E2E Testing Protocol (Playwright + SSH)

> **IMPORTANTE**: Per test UI/frontend automatizzati, usa E2E via SSH su iMac.
> **NON usare tauri-driver** (non funziona su macOS WKWebView).

### Setup (già completato)

- **Tool**: Playwright + Vite dev server
- **Browser**: Chromium (WebKit ha problemi su macOS 12)
- **Config**: `playwright.headless.config.ts`
- **Test dir**: `tests/e2e/`
- **iMac**: 192.168.1.9 (gianlucadistasi)

### Eseguire E2E Tests

```bash
# Opzione 1: Script automatico (da MacBook)
bash scripts/run-e2e-remote.sh gianlucadistasi 192.168.1.9

# Opzione 2: Manuale via SSH
ssh imac "bash -l -c 'cd /Volumes/MacSSD\\ -\\ Dati/fluxion && npx playwright test --config=playwright.headless.config.ts'"
```

### Quando Eseguire E2E

| Modifica | E2E Required |
|----------|--------------|
| Componenti UI (.tsx) | ✅ |
| Hooks React | ✅ |
| Pagine nuove | ✅ |
| Solo backend (.rs, .py) | ❌ |
| Solo styling (CSS) | ❌ |

### Creare Nuovi Test E2E

```typescript
// tests/e2e/my-feature.test.ts
import { test, expect } from '@playwright/test';

test.describe('My Feature', () => {
  test('should work', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // ... test logic
  });
});
```

### Debug E2E Failures

```bash
# Vedere trace di errore
npx playwright show-trace test-results/artifacts/*/trace.zip

# Run con UI (richiede display su iMac)
ssh imac "bash -l -c 'cd /Volumes/MacSSD\\ -\\ Dati/fluxion && npx playwright test --ui'"
```

### Documentazione

- **Guida completa**: `docs/testing/E2E_PLAYWRIGHT_MACOS.md`
- **Config**: `playwright.headless.config.ts`
- **Script**: `scripts/run-e2e-remote.sh`

---

## Skills Integration (Claude Code)

### Skills Fluxion (Custom)

| Skill | File | Scopo |
|-------|------|-------|
| **fluxion-tauri-architecture** | `.claude/skills/fluxion-tauri-architecture.md` | Pattern architetturali Tauri + React + Rust |
| **fluxion-voice-agent** | `.claude/skills/fluxion-voice-agent.md` | 5-layer RAG pipeline, TTS, disambiguazione |
| **fluxion-workflow** | `.claude/skills/fluxion-workflow.md` | Epic→Story→Task, RICE, quality gates |

### Skills Enterprise (External)

| Repository | Skills | Utilizzo |
|------------|--------|----------|
| **levnikolaevich/claude-code-skills** | 84 | Orchestrator pattern, audit, bootstrap |
| **alirezarezvani/claude-skills** | 42 | Domain expertise, CLI tools, regulatory |
| **anthropics/skills** | 15+ | Official reference, document skills |

### Workflow con Skills

```
1. Nuova Feature → fluxion-workflow (Epic→Story→Task)
2. Implementazione → fluxion-tauri-architecture (pattern)
3. Voice Agent → fluxion-voice-agent (pipeline)
4. Quality Check → levnikolaevich/audit-skills (9 workers)
5. Documentation → levnikolaevich/documentation-pipeline
```

### Uso Default

> **IMPORTANTE**: Claude DEVE usare le skills di default per ogni task su Fluxion.
> Non è necessario attivarle manualmente - sono sempre attive.

```yaml
default_skills:
  - fluxion-tauri-architecture  # Pattern obbligatori
  - fluxion-voice-agent         # Se voice/NLU coinvolto
  - fluxion-workflow            # Per nuove feature (Epic→Story→Task)
```

---

## MCP Server (Claude Code Integration)

### Setup

```bash
cd mcp-server
npm install
npm run build
```

### Claude Desktop Config

Aggiungi a `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxion": {
      "command": "node",
      "args": ["/Volumes/MontereyT7/FLUXION/mcp-server/dist/index.js"]
    }
  }
}
```

### Tools Disponibili (8)

| Tool | Descrizione |
|------|-------------|
| `search_clienti` | Cerca clienti per telefono/nome/email |
| `create_appuntamento` | Crea nuovo appuntamento |
| `get_disponibilita` | Slot disponibili per data |
| `get_faq` | FAQ per verticale |
| `list_servizi` | Lista servizi |
| `list_operatori` | Lista operatori |
| `get_cliente` | Dettagli cliente |
| `get_appuntamenti_cliente` | Appuntamenti cliente |

### Resources (9)

- `fluxion://clienti` - Tutti i clienti
- `fluxion://servizi` - Tutti i servizi
- `fluxion://appuntamenti/oggi` - Appuntamenti di oggi
- `fluxion://faq/{salone|wellness|medical|auto}` - FAQ per verticale
- `fluxion://stats` - Statistiche sistema

---

## Test Results Summary (2026-01-20)

### Rust Unit Tests (cargo test)

```
test result: ok. 40 passed; 0 failed; 0 ignored; finished in 0.45s
```

| Component | Tests | Status |
|-----------|-------|--------|
| RAG Commands | 3 | ✅ |
| Appuntamento Aggregate | 14 | ✅ |
| Domain Errors | 3 | ✅ |
| Encryption (AES-256-GCM) | 3 | ✅ |
| Repositories | 2 | ✅ |
| Appuntamento Service | 3 | ✅ |
| Festivita Service | 4 | ✅ |
| Validation Service | 8 | ✅ |

### Voice Agent Tests (pytest)

```
======================== 426 passed, 26 skipped ========================
```

| Component | Tests | Status |
|-----------|-------|--------|
| NLU (Intent + Entity) | 89 | ✅ |
| FAQ Retrieval | 45 | ✅ |
| Orchestrator | 78 | ✅ |
| Disambiguation | 32 | ✅ |
| VoIP (voip.py) | 39 | ✅ |
| WhatsApp (whatsapp.py) | 52 | ✅ |
| Pipeline Integration | 91 | ✅ |
| **Skipped** (PyTorch) | 26 | ⚠️ |

> **Nota**: 26 test skipped richiedono PyTorch (Chatterbox TTS, FAISS semantic).
> Python 3.13 non supporta PyTorch. Workaround: usare Python 3.11.

### E2E Test Conversation (Backend Integration)

```
[Turno 1] USER: "Buongiorno, vorrei prenotare un taglio"
[Turno 1] SARA: "Buongiorno! Per quale giorno desidera prenotare?"
[Turno 2] USER: "Sabato prossimo"
[Turno 2] SARA: "Sabato 24 gennaio. A che ora preferisce?"
[Turno 3] USER: "Alle 10"
[Turno 3] SARA: "Le 10:00 sono disponibili. Mi può dire il suo nome?"
[Turno 4] USER: "Mario Rossi"
[Turno 4] SARA: "Perfetto Mario. Mi può lasciare un numero di telefono?"
[Turno 5] USER: "3331234567"
[Turno 5] SARA: "E un'email per la conferma?"
[Turno 6] USER: "mario@example.com"
[Turno 6] SARA: "Ho prenotato: Taglio capelli, sabato 24 gennaio alle 10:00."
[Turno 7] SARA: "La aspettiamo! Arrivederci."
```

**Risultato**: ✅ Conversazione completa, estrazione entità corretta

### CI/CD Workflows

| Workflow | File | Trigger | Status |
|----------|------|---------|--------|
| Test Suite | `test-suite.yml` | push develop, PR main | ✅ |
| E2E Tests | `e2e-tests.yml` | manual, schedule | ⚠️ |
| Release | `release.yml` | tag v* | ✅ |
| Release Full | `release-full.yml` | manual | ✅ |

> **E2E Limitation**: `tauri-driver` non supporta macOS. E2E WebDriverIO funziona solo su Linux/Ubuntu.

### Known Limitations (Python 3.13)

| Feature | Status | Workaround |
|---------|--------|------------|
| Chatterbox TTS | ❌ No PyTorch | SystemTTS (macOS say) |
| FAISS Semantic | ❌ No sentence-transformers | Keyword search |
| Piper TTS | ⚠️ Parziale | Binary disponibile |

---

## Performance SLA (Target)

| Layer | Operation | Target | Status |
|-------|-----------|--------|--------|
| L0 | Regex match | <1ms | OK |
| L1 | Intent (spaCy) | <5ms | OK |
| L2 | Slot filling | <10ms | OK |
| L3 | FAISS search | <50ms | OK |
| L4 | Groq LLM | <500ms | OK |
| E2E | Voice in -> out | <2000ms | OK |

Dettagli completi: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

---

*Ultimo aggiornamento: 2026-01-20*
