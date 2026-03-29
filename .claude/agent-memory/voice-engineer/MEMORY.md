# Voice Engineer Memory — FLUXION "Sara"
> Max 200 righe. Aggiornare dopo ogni sessione significativa.

## Architettura Audio Path
- **STT**: whisper.cpp `ggml-small` via subprocess (~30s su iMac per audio reale)
- **Timeout Python subprocess**: 30s (in `stt.py` riga ~194)
- **Timeout Rust client**: 120s (fixato da 30s — commit `7a26712`)
- Il path audio risponde in ~31s su iMac corrente (hardware lento per Whisper)

## Whisper.cpp Performance su iMac
- Modello `ggml-small` impiega ~30s per 1s di audio silenzioso
- Per audio reale con parlato atteso: ~30-40s
- Causa: CPU-only inference su iMac vecchio
- Fix futuro: passare a `ggml-tiny` per ridurre latenza (~10s), o usare Groq STT cloud

## Problemi Noti (non da fixare ora)
- `spaCy not installed` — warning costante nei log, non blocca nulla
- `table audit_log has no column named notes` — migration mancante, non critico
- `sentence-transformers not installed` — FAQ semantic retrieval degraded a keyword-only

## Riavvio Pipeline iMac
`pkill -f 'python main.py'` NON funziona (P maiuscola). Usare:
```bash
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

## Build iMac — Comando Corretto
`nohup` non disponibile su iMac (zsh). Usare:
```bash
ssh imac 'export PATH="/Users/gianlucadistasi/.cargo/bin:/usr/local/bin:$PATH" && cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri build > /tmp/fluxion-build3.log 2>&1 &'
```
Nota: usare singoli apici nell'SSH per evitare problemi con il path con spazi.

## File Chiave
- `src-tauri/src/commands/voice_pipeline.rs` — timeout Rust (riga 320)
- `voice-agent/src/stt.py` — subprocess whisper.cpp + timeout interno (riga ~194)
- `voice-agent/main.py` — entry point server porta 3002
- Log pipeline: `/tmp/voice-pipeline.log` (iMac)
- Log build: `/tmp/fluxion-build3.log` (iMac)

## B4 Exception Handling (2026-03-04) — COMPLETATO
- 105 → 87 `except Exception` in `src/` (-18 narrowati, +alcuni fallthrough corretti)
- Research: `.claude/cache/agents/b4-exception-handling-research.md`
- Pattern chiave: HTTP Bridge → `except (aiohttp.ClientError, asyncio.TimeoutError, OSError)` + `except Exception` fallthrough
- Bridge best-effort (session_manager.py): aggiungere `except Exception: pass` DOPO il narrowed per RuntimeError event loop closed
- asyncio.CancelledError: aggiunto re-raise in error_recovery.py (retry loop), voip.py (audio handler), groq_client.py (streaming generator)
- SQLite ops: narrowati a `sqlite3.Error` in session_manager.py, whatsapp_callback.py, booking_state_machine.py
- Groq error (orchestrator.py riga ~1292): differenziato TimeoutError / RuntimeError rate-limit / Exception inatteso
- Test MacBook: 1132 pass (erano 1125) — 8 failure pre-esistenti (spaCy/groq/DB iMac mancanti)

## Bug Critici Identificati (2026-03-03)
Research file: `.claude/cache/agents/voice-agent-bugs-research.md`
- **BUG-1 CRITICO**: `SentimentAnalyzer` (sentiment.py riga 103) ha "no"/"ma"/"però" in WORD_BOUNDARY_KEYWORDS con peso 1 — causa falsi positivi escalation durante booking attivo
- **BUG-2**: Sentiment check in orchestrator.py riga 575 avviene prima di L1 e NON è bypassato durante FSM booking attivo
- **BUG-3 MANCANTE**: Nessun handler per "scegli tu / prima disponibile / indifferente" → manca lookup_type="first_available"
- **BUG-4**: Escalation operatore NON fa nulla di concreto se WhatsApp non configurato
- **FIX RAPIDO #1**: orchestrator.py riga 575 — aggiungere guard `not is_booking_active`
- **FIX RAPIDO #2**: sentiment.py riga 103 — rimuovere "no", "ma", "però" da WORD_BOUNDARY_KEYWORDS
- **FIX RAPIDO #3**: orchestrator.py riga 396 — reset sentiment history in start_session()

## F02 Vertical Guardrail Research (2026-03-04) — COMPLETATO
Research files:
- `.claude/cache/agents/f02-nlu-ambiguity-research.md` — root cause analysis
- `.claude/cache/agents/f02-nlu-comprehensive-patterns.md` — FULL PATTERN LIBRARY (NEW)

Key findings for implementation:
- **BUG**: SPOSTAMENTO pattern `(cambia|cambiare|...)\s+(...)?(appuntament)?` — trailing `?` fires on "cambiare le gomme"
- **FIX 1B**: Remove `?` from object group for "cambiare/modificare" (keep for "spostare")
- **FIX GUARDRAIL**: Add verb-form patterns to all 4 verticals — noun-only patterns miss infinitive forms
- **FIX GROQ PROMPT**: Add vertical description + out-of-scope to `_build_llm_context()`
- **LATE GUARDRAIL**: Add `check_vertical_guardrail()` in orchestrator E4-S2 block (line 791) before reschedule logic
- Implementation order: italian_regex.py → intent_classifier.py → tests → orchestrator.py
- Test count needed: 40+ parametric guardrail tests per vertical + E2E suite

## CoVe 2026 Enterprise Audit Completo (2026-03-12)
Research file: `.claude/cache/agents/sara-enterprise-agente-b.md`
- **37 gap totali** (4 P0, 21 P1, 12 P2) — NESSUNO già documentato nei file precedenti
- **P0 critici**:
  - GAP-E3: `VoiceOrchestrator` ha instance vars (`_current_session`, `_pending_cancel`) condivise tra sessioni parallele — booking attribuiti alla sessione sbagliata
  - GAP-F1: PII (nome+telefono) in `print()` → `/tmp/voice-pipeline.log` non protetto (GDPR)
  - GAP-D3: Nessuna colonna `fsm_state` nei turn log analytics → impossibile sapere dove si rompono le conversazioni
  - GAP-C1: Date "13/03" non preprocessate in TTS → lette "tredici barra tre"
- **P1 chiave**: Stati SLOT_UNAVAILABLE/PROPOSING_WAITLIST/CONFIRMING_WAITLIST senza handler FSM (GAP-A2); "torna indietro" durante registrazione non gestito (GAP-A3); FCR non tracciato (GAP-D1); Groq system prompt senza orari/operatori/prezzi (GAP-H2)

## VoIP EHIWEB Bug Fixes (2026-03-28 S119) — COMPLETATO
Commit: `dc08a3e` — `voice-agent/src/voip.py`
- **Bug 1**: `answer_call()` ora usa `active_call.invite_message` (originale INVITE storato in `_handle_invite`) per costruire 200 OK corretto — RFC 3261 compliant
- **Bug 2**: `_on_call_connected` ora sync + lancia `_start_rtp_and_greet()` via `asyncio.ensure_future()` (SIPClient chiama il callback come sync)
- **Bug 3**: `_upsample_audio` / `_downsample_audio` ora usano `audioop.ratecv()` (anti-aliased) invece di linear interpolation / decimation
- **Bug 4**: `_send_audio()` legge header WAV per rilevare sample rate reale (Piper=22050Hz, Edge-TTS=16000Hz) prima di downsample a 8kHz
- **Bug 5**: `SimpleVoIPVAD` aggiunto — energy-based (audioop.rms per frame 20ms), dispatchsturn dopo 700ms silenzio + >=100ms speech; sostituisce threshold fisso 500ms
- **Config**: `SIPConfig.from_env()` ora accetta sia `VOIP_SIP_*` (main.py) che `EHIWEB_SIP_*` (legacy) env var — no più mismatch

## Bug da Conversazione Reale (2026-03-04)
Research file: `.claude/cache/agents/voice-agent-production-issues-research.md`
- **TTS-PHONE**: `booking_state_machine.py:533` template `confirm_phone_number` passa numero grezzo → SystemTTS legge "3 virgola 8 milioni". Fix: espandere cifra per cifra in `tts.py:TTSCache.synthesize()` o nel template.
- **CLIENT-ID-RESET**: `booking_sm.reset()` azzera `client_id`/`client_name` → cliente non riconosciuto nella stessa sessione. Fix: preservare client_id nel reset() soft.
- **DUPLICATE-CLIENT**: `_create_client_sqlite_fallback` fa INSERT senza controllo duplicati nome+cognome. Fix: SELECT preventivo + UPDATE se esiste.
- **WA-TRIGGER**: WA inviato solo a `should_exit=True` (fine chiamata formale). Fix: fire-and-forget subito dopo `booking_result.get("success")` (orchestrator.py:913).
- **WA-DATA-MISSING**: `_last_booking_data` non include `client_name`/`client_phone` dal context → WA inviato senza dati cliente.
- **CONTENT-FILTER-PLURAL**: `italian_regex.py:416` pattern `pompino` (singolare) non matcha `pompini` (plurale). Fix: cambiare in `pompini?`.
- **VERTICAL-GUARD-ABSENT**: Nessun filtro servizi per verticale → "cambio olio" accettato in un salone.
