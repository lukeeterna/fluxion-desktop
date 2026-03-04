# B4 Exception Handling Research — Voice Agent Sara
> CoVe 2026 FASE 1 — Research file
> Data: 2026-03-04

## Conteggio Totale

**151 occorrenze `except Exception`** in 37 file (da ripgrep).

### Distribuzione per file (solo `src/` + `main.py` + `whatsapp_callback.py`)

| File | Count | Priorita |
|------|-------|----------|
| `src/orchestrator.py` | 26 | CRITICA |
| `main.py` | 10 | ALTA |
| `src/stt.py` | 12 | ALTA |
| `src/groq_client.py` | 8 | ALTA |
| `src/whatsapp_callback.py` | 6 | MEDIA |
| `src/session_manager.py` | 7 | MEDIA |
| `src/voip.py` | 4 | BASSA |
| `src/vad_http_handler.py` | 4 | MEDIA |
| `src/audit_client.py` | 4 | BASSA |
| `src/error_recovery.py` | 4 | BASSA |
| `src/supplier_email_service.py` | 4 | BASSA |
| `src/availability_checker.py` | 2 | MEDIA |
| `src/booking_state_machine.py` | 2 | CRITICA |
| `src/faq_manager.py` | 2 | BASSA |
| `src/whatsapp.py` | 2 | BASSA |
| `src/nlu/italian_nlu.py` | 2 | BASSA |
| `src/tts.py` | 3 | BASSA |
| `src/pipeline.py` | 3 | MEDIA |
| `src/groq_nlu.py` | 1 | BASSA |
| `src/intent_classifier.py` | 1 | BASSA |
| `src/entity_extractor.py` | 1 | BASSA |
| `src/latency_optimizer.py` | 2 | BASSA |
| `src/sentiment.py` | 1 | BASSA |
| `src/sip_client.py` | 1 | BASSA |
| `src/vertical_integration.py` | 1 | BASSA |
| `guided_dialog.py` | 5 | MEDIA |

---

## Top 20 Pattern con Fix Suggerito

### PATTERN 1 — HTTP Bridge offline (aiohttp) [orchestrator.py, pipeline.py, availability_checker.py]
**Frequenza**: ~12 occorrenze
**Codice attuale**:
```python
except Exception as e:
    print(f"Client search error: {e}")
# HTTP Bridge unavailable → SQLite fallback
return self._search_client_sqlite_fallback(name)
```
**Problema**: cattura tutto — inclusi `KeyboardInterrupt`, `SystemExit`, bug logici nel fallback.
**Tipo corretto**: `aiohttp.ClientError` + `asyncio.TimeoutError`
**Fix**:
```python
except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
    logger.warning("[HTTP] Bridge offline, fallback SQLite: %s", e)
    return self._search_client_sqlite_fallback(name)
```
**Severita**: WARNING
**Azione**: log + fallback SQLite (gia implementato — solo narrowing)

---

### PATTERN 2 — Groq API call [groq_client.py, orchestrator.py]
**Frequenza**: ~5 occorrenze
**Codice attuale**:
```python
except Exception as e:
    print(f"Groq error: {e}")
    response = "Mi scusi, ho avuto un problema tecnico. Puo ripetere?"
```
**Tipo corretto**: `groq.APIError`, `groq.RateLimitError`, `groq.APITimeoutError`, `asyncio.TimeoutError`
**Fix**:
```python
except groq.RateLimitError as e:
    logger.warning("[Groq] Rate limit hit, circuit breaker attivato: %s", e)
    groq_breaker.record_failure()
    response = "Mi scusi, sono momentaneamente sovraccarica. Riprovo tra un attimo."
except (groq.APITimeoutError, asyncio.TimeoutError) as e:
    logger.warning("[Groq] Timeout: %s", e)
    response = "Mi scusi, sto impiegando troppo. Puo ripetere la domanda?"
except groq.APIError as e:
    logger.error("[Groq] API error %s: %s", e.status_code, e)
    response = "Mi scusi, ho avuto un problema tecnico. Puo ripetere?"
```
**Severita**: WARNING (LLM e optional) / CRITICAL (se unico path di risposta)
**Azione**: log differenziato per tipo + circuit breaker gia presente da sfruttare meglio

---

### PATTERN 3 — SQLite write/read [session_manager.py, orchestrator.py, whatsapp_callback.py]
**Frequenza**: ~10 occorrenze
**Codice attuale**:
```python
except Exception as e:
    print(f"[SessionManager] SQLite persist error: {e}")
    return False
```
**Tipo corretto**: `sqlite3.Error` (superclasse di `sqlite3.OperationalError`, `sqlite3.IntegrityError`, ecc.)
**Fix**:
```python
except sqlite3.OperationalError as e:
    # Schema mismatch, locked DB — piu grave
    logger.error("[SessionManager] SQLite operational error: %s", e)
    return False
except sqlite3.IntegrityError as e:
    # Duplicate key — puo essere ignorato in certi contesti
    logger.warning("[SessionManager] SQLite integrity error (duplicate?): %s", e)
    return False
except sqlite3.Error as e:
    logger.error("[SessionManager] SQLite error: %s", e)
    return False
```
**Severita**: WARNING (sessioni) / CRITICAL (booking creation)
**Azione**: narrowing a `sqlite3.Error` al minimo, differenziare `OperationalError`

---

### PATTERN 4 — Optional component init (spaCy, UmBERTo, sentence-transformers) [orchestrator.py, nlu/]
**Frequenza**: ~6 occorrenze
**Codice attuale**:
```python
except Exception as e:
    print(f"[NLU] Advanced NLU init failed: {e}")
```
**Tipo corretto**: `ImportError` + `OSError` (model file not found) + specifico ML framework errors
**Fix**:
```python
except ImportError:
    logger.info("[NLU] spaCy non installato — NLU avanzato disabilitato")
except OSError as e:
    logger.warning("[NLU] Modello non trovato: %s — NLU avanzato disabilitato", e)
except Exception as e:
    # Qualsiasi altro errore ML (es. ONNX runtime issue)
    logger.warning("[NLU] Init fallita (%s): %s — degraded mode", type(e).__name__, e)
```
**Severita**: IGNORE (componenti optional — degraded mode atteso)
**Azione**: log chiaro del motivo di fallback

---

### PATTERN 5 — Temp file cleanup [stt.py]
**Frequenza**: 2 occorrenze
**Codice attuale**:
```python
try:
    Path(audio_path).unlink()
except Exception:
    pass
```
**Tipo corretto**: `OSError` (PermissionError, FileNotFoundError)
**Fix**:
```python
try:
    Path(audio_path).unlink(missing_ok=True)  # Python 3.8+ — elimina il try/except
except OSError:
    pass  # File in uso o gia eliminato — sicuro ignorare
```
**Severita**: IGNORE — file leak e accettabile
**Azione**: usare `missing_ok=True` per FileNotFoundError, `except OSError` per il resto

---

### PATTERN 6 — datetime.strptime su dato utente [orchestrator.py x2]
**Frequenza**: 2 occorrenze
**Codice attuale**:
```python
try:
    start = datetime.strptime(data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
    data_ora_fine = (start + timedelta(minutes=int(durata_minuti))).strftime(...)
except Exception:
    data_ora_fine = data_ora_inizio
```
**Tipo corretto**: `ValueError` (formato data invalido) + `TypeError` (None passato)
**Fix**:
```python
except (ValueError, TypeError) as e:
    logger.warning("[BOOKING] Formato data non valido '%s': %s", data_ora_inizio, e)
    data_ora_fine = data_ora_inizio
```
**Severita**: WARNING — fallback silenzioso puo mascherare dati corrotti
**Azione**: narrowing a `ValueError, TypeError` + log esplicito

---

### PATTERN 7 — WhatsApp send [orchestrator.py x2, whatsapp_callback.py x2]
**Frequenza**: 4 occorrenze
**Codice attuale**:
```python
except Exception as e:
    logger.warning(f"[WA] Confirmation send error (non-critical): {e}")
```
**Tipo corretto**: `aiohttp.ClientError`, `asyncio.TimeoutError`, `httpx.HTTPError` (dipende da client)
**Fix**:
```python
except (aiohttp.ClientError, asyncio.TimeoutError) as e:
    logger.warning("[WA] Invio fallito (non critico): %s", e)
except Exception as e:
    # Errore inatteso — loggare con stack trace per debug
    logger.error("[WA] Errore inatteso invio: %s", e, exc_info=True)
```
**Severita**: WARNING — booking completato, WA e best-effort
**Azione**: narrowing HTTP errors + `exc_info=True` per unexpected

---

### PATTERN 8 — HTTP Bridge config load [orchestrator.py, main.py]
**Frequenza**: 3 occorrenze
**Codice attuale**:
```python
except Exception:
    pass
# Fallback: read directly from SQLite
```
**Tipo corretto**: `aiohttp.ClientError`, `asyncio.TimeoutError`
**Fix**:
```python
except (aiohttp.ClientError, asyncio.TimeoutError):
    pass  # Bridge offline atteso — SQLite fallback sotto
except Exception as e:
    logger.error("[CONFIG] Errore inatteso load config: %s", e, exc_info=True)
```
**Severita**: WARNING (Bridge offline e normale)
**Azione**: narrowing + log errori inattesi con stack trace

---

### PATTERN 9 — STT engine init [stt.py x3, groq_client.py]
**Frequenza**: 6 occorrenze
**Codice attuale**:
```python
except Exception as e:
    print(f"[STT] faster-whisper not available: {e}")
```
**Tipo corretto**: `ImportError` (modulo non installato) + `OSError` (model file mancante) + `RuntimeError` (init fallita)
**Fix**:
```python
except ImportError:
    logger.info("[STT] faster-whisper non installato — provo whisper.cpp")
except (OSError, RuntimeError) as e:
    logger.warning("[STT] Init engine fallita: %s — provo fallback", e)
```
**Severita**: WARNING (se esiste almeno un engine) / CRITICAL (se tutti falliscono)
**Azione**: La `raise RuntimeError("No STT engine available")` finale e corretta — solo narrowing negli step intermedi

---

### PATTERN 10 — STT transcription [stt.py, groq_client.py]
**Frequenza**: 4 occorrenze
**Codice attuale**:
```python
except Exception as e:
    return {"text": "", "confidence": 0.0, ...}
```
**Tipo corretto**: `asyncio.TimeoutError`, `groq.APIError`, `subprocess.TimeoutExpired`, `OSError`
**Fix**:
```python
except asyncio.TimeoutError:
    logger.warning("[STT] Timeout trascrizione dopo %ds", TIMEOUT_SEC)
    return {"text": "", "confidence": 0.0, "latency_ms": latency_ms}
except (groq.APIError, OSError) as e:
    logger.error("[STT] Trascrizione fallita: %s", e)
    return {"text": "", "confidence": 0.0, "latency_ms": latency_ms}
```
**Severita**: WARNING — testo vuoto porta a re-prompt
**Azione**: differenziare timeout (aspettato) da errori API (inaspettati)

---

### PATTERN 11 — Web handler catch-all [main.py, vad_http_handler.py]
**Frequenza**: 8 occorrenze
**Codice attuale**:
```python
except Exception as e:
    import traceback
    traceback.print_exc()
    return web.json_response({"success": False, "error": str(e)}, status=500)
```
**Commento**: Questo pattern e CORRETTO per il top-level handler HTTP — catturare tutto e giusto qui.
**Miglioramento**: usare `logger.exception()` invece di `traceback.print_exc()` per uniformita logging.
**Fix**:
```python
except Exception as e:
    logger.exception("[API] Errore non gestito nel handler: %s", e)
    return web.json_response({"success": False, "error": str(e)}, status=500)
```
**Severita**: N/A — questo e il safety net corretto
**Azione**: solo refactor da `traceback.print_exc()` a `logger.exception()`

---

### PATTERN 12 — FSM state get [main.py riga 295]
**Frequenza**: 1
**Codice attuale**:
```python
try:
    fsm_state = self.orchestrator.booking_sm.context.state.value
except Exception:
    fsm_state = "unknown"
```
**Tipo corretto**: `AttributeError` (context o state e None)
**Fix**:
```python
except AttributeError:
    fsm_state = "unknown"
```
**Severita**: IGNORE — debug info, non critico

---

### PATTERN 13 — Circuit breaker in error_recovery.py [riga 407]
**Frequenza**: 1 (in commento/esempio)
**Codice attuale**:
```python
except Exception:
    breaker.record_failure()
```
**Commento**: e in un docstring/esempio — non codice reale da fixare.
**Azione**: nessuna

---

### PATTERN 14 — Retry loop in error_recovery.py [righe 217, 272]
**Frequenza**: 2
**Codice attuale**:
```python
except Exception as e:
    last_error = e
    if error_handler:
        error_handler(e, attempt)
```
**Commento**: In un generic retry mechanism, `except Exception` e accettabile — e il punto di raccolta errori.
**Miglioramento**: aggiungere re-raise di `KeyboardInterrupt`, `SystemExit`
**Fix**:
```python
except (KeyboardInterrupt, SystemExit):
    raise  # Non intercettare segnali di sistema
except Exception as e:
    last_error = e
    if error_handler:
        error_handler(e, attempt)
```
**Severita**: MEDIA — il retry loop deve rispettare segnali di sistema
**Azione**: aggiungere re-raise per segnali di sistema

---

### PATTERN 15 — Booking state machine disambiguation [booking_state_machine.py riga 1488]
**Frequenza**: 1 (critico per il flusso)
**Codice attuale**:
```python
except Exception as e:
    logger.error(f"[DISAMBIGUATION] Error in disambiguation check: {e}")
    return self._check_name_disambiguation_simulation(input_name, input_surname)
```
**Tipo corretto**: `sqlite3.Error` (DB) + `ValueError` (input invalido)
**Fix**:
```python
except sqlite3.Error as e:
    logger.error("[DISAMBIGUATION] DB error: %s — fallback simulation", e)
    return self._check_name_disambiguation_simulation(input_name, input_surname)
except ValueError as e:
    logger.warning("[DISAMBIGUATION] Input invalido: %s", e)
    return self._check_name_disambiguation_simulation(input_name, input_surname)
```
**Severita**: WARNING — fallback simulation gia implementato
**Azione**: narrowing + mantenere fallback

---

### PATTERN 16 — spaCy NER in FSM [booking_state_machine.py riga 1311]
**Frequenza**: 1
**Codice attuale**:
```python
except Exception:
    pass  # spaCy not available, continue to fallback
```
**Tipo corretto**: `AttributeError` (model non caricato) + `ImportError`
**Fix**:
```python
except (AttributeError, RuntimeError):
    pass  # spaCy non disponibile — fallback a regex
```
**Severita**: IGNORE — degraded mode atteso
**Azione**: narrowing minimo per chiarezza

---

### PATTERN 17 — WhatsApp callback DB lookup [whatsapp_callback.py riga 329]
**Frequenza**: 1
**Codice attuale**:
```python
except Exception as e:
    logger.debug("DB lookup error for phone %s: %s", phone, e)
return None
```
**Tipo corretto**: `sqlite3.Error`
**Fix**:
```python
except sqlite3.Error as e:
    logger.debug("DB lookup phone %s: %s", phone, e)
return None
```
**Severita**: WARNING — se None, sessione non trovata = nuova sessione
**Azione**: narrowing a `sqlite3.Error`

---

### PATTERN 18 — Audit client [audit_client.py riga 192, 488]
**Frequenza**: 2
**Codice attuale**:
```python
except Exception as e:
    logger.error(f"[AUDIT] Unexpected error logging operation: {e}")
    return None
```
**Commento**: Gia c'e `except sqlite3.Error` PRIMA — questo e corretto come fallthrough per errori davvero inattesi.
**Fix**: aggiungere `exc_info=True` per stack trace completo.
```python
except Exception as e:
    logger.error("[AUDIT] Errore inatteso: %s", e, exc_info=True)
    return None
```
**Severita**: BASSA — audit e non critico per il flusso
**Azione**: aggiungere `exc_info=True`

---

### PATTERN 19 — Guided Dialog Engine [guided_dialog.py riga 916]
**Frequenza**: 1 (ma nel critical path)
**Codice attuale**:
```python
except Exception as e:
    self.context.error_messages.append(str(e))
    self.context.state = DialogState.ERROR
    response = f"Scusate, c'e stato un problema tecnico. Vi passo a un collega."
```
**Tipo corretto**: `sqlite3.Error`, `ValueError`, `KeyError`
**Fix**: questo e un handler di dialogo — va bene `except Exception` qui come safety net, ma aggiungere logging.
```python
except Exception as e:
    logger.error("[GUIDED] Errore flusso dialog: %s", e, exc_info=True)
    self.context.error_messages.append(str(e))
    self.context.state = DialogState.ERROR
    response = "Scusate, c'e stato un problema tecnico. Vi passo a un collega."
```
**Severita**: WARNING — l'escalation a operatore e il recovery corretto
**Azione**: aggiungere logging

---

### PATTERN 20 — VoIP/SIP receive loop [voip.py riga 322, 908]
**Frequenza**: 2
**Codice attuale**:
```python
except Exception as e:
    logger.error(f"SIP receive error: {e}")
    await asyncio.sleep(0.1)
```
**Tipo corretto**: In un receive loop, `except Exception` e accettabile per non crashare il loop.
**Miglioramento**: re-raise `asyncio.CancelledError` (gia fatto per il primo), aggiungere counter per errori ripetuti.
**Fix**:
```python
except asyncio.CancelledError:
    raise  # sempre re-raise CancelledError
except Exception as e:
    logger.error("[VoIP] SIP receive error: %s", e)
    await asyncio.sleep(0.1)
```
**Severita**: BASSA — VoIP e feature opzionale
**Azione**: assicurarsi che `CancelledError` non venga catturato (verificare per ogni loop)

---

## Classificazione per File Critici vs Minor

### CRITICI (blocca flusso booking)

#### `src/orchestrator.py` — 26 occorrenze
- Contiene il critical path per booking, creazione cliente, disponibilita
- Pattern piu frequente: HTTP Bridge fallback — corretto, solo narrowing necessario
- Pattern pericoloso: Groq catch-all (riga 1286) — maschera RateLimitError da timeout
- Pattern corretto: WA confirmation (riga 1879) — non-critical, ok come e
- **Priorita fix**: Pattern 1 (HTTP) + Pattern 2 (Groq)

#### `src/booking_state_machine.py` — 2 occorrenze
- Entrambe in disambiguation check — hanno fallback simulation
- **Priorita fix**: Media (Pattern 15, 16)

#### `main.py` — 10 occorrenze
- Top-level HTTP handlers: `except Exception` e CORRETTO qui (safety net)
- Config load (Bridge offline): narrowing aiohttp
- FSM state get: narrowing AttributeError
- **Priorita fix**: Bassa (solo refactor logging)

### MEDI (funzionalita degradata)

#### `src/stt.py` — 12 occorrenze
- STT init chain: narrowing ImportError/OSError
- Temp file cleanup: usare `missing_ok=True`
- Transcription failure: narrowing TimeoutError vs APIError
- **Priorita fix**: Media

#### `src/groq_client.py` — 8 occorrenze
- Retry loop: corretto, aggiungere re-raise CancelledError
- Streaming fallback: ok come safety net
- **Priorita fix**: Bassa

#### `src/session_manager.py` — 7 occorrenze
- SQLite ops: narrowing a `sqlite3.Error`
- Bridge sync: `except Exception: pass` → `except (aiohttp.ClientError, asyncio.TimeoutError): pass`
- **Priorita fix**: Media

#### `src/whatsapp_callback.py` — 6 occorrenze
- DB ops: narrowing a `sqlite3.Error`
- WA send: narrowing aiohttp
- Orchestrator call: ok come safety net con fallback response
- **Priorita fix**: Bassa-Media

### MINOR (analytics, infra opzionale)

#### `src/audit_client.py` — 4 (aggiungere exc_info=True)
#### `src/vad_http_handler.py` — 4 (top-level handlers ok)
#### `src/supplier_email_service.py` — 4 (SMTP ok)
#### `src/voip.py` — 4 (VoIP opzionale)
#### Tutti gli altri — 1-3 occorrenze (bassa priorita)

---

## Cluster per Effort

### CLUSTER A — Narrowing HTTP/aiohttp (QUICK WIN)
**File**: orchestrator.py, session_manager.py, pipeline.py, availability_checker.py, whatsapp_callback.py, main.py
**Pattern**: Sostituire `except Exception` con `except (aiohttp.ClientError, asyncio.TimeoutError, OSError)`
**Occorrenze**: ~20
**Effort**: 1h — find & replace + review manuale
**Impatto**: Errori di sistema (MemoryError, KeyboardInterrupt) non piu silenziati

### CLUSTER B — SQLite narrowing
**File**: session_manager.py, whatsapp_callback.py, orchestrator.py, audit_client.py
**Pattern**: `except Exception` → `except sqlite3.Error` (o sottotipi specifici)
**Occorrenze**: ~10
**Effort**: 30min
**Impatto**: Bug logici in query SQL non mascherati

### CLUSTER C — Groq API differenziata
**File**: groq_client.py, orchestrator.py
**Pattern**: Differenziare RateLimitError / TimeoutError / APIError
**Occorrenze**: ~5
**Effort**: 2h (richiede studio Groq SDK exception hierarchy)
**Impatto**: Migliore circuit breaker, messaggi utente differenziati

### CLUSTER D — Optional component init
**File**: orchestrator.py, stt.py, nlu/italian_nlu.py, intent_classifier.py
**Pattern**: `ImportError` + `OSError` separati
**Occorrenze**: ~8
**Effort**: 30min
**Impatto**: Log piu chiari (capire se e un import mancante o un file mancante)

### CLUSTER E — Logging upgrade (exc_info=True)
**File**: tutti i file con `except Exception as e: logger.error(...)`
**Pattern**: Aggiungere `exc_info=True` o usare `logger.exception()`
**Occorrenze**: ~15
**Effort**: 30min
**Impatto**: Stack trace nei log per errori inattesi

### CLUSTER F — asyncio safety (re-raise CancelledError)
**File**: error_recovery.py, voip.py, groq_client.py
**Pattern**: Aggiungere `except (KeyboardInterrupt, SystemExit, asyncio.CancelledError): raise` sopra `except Exception`
**Occorrenze**: ~5
**Effort**: 30min
**Impatto**: CRITICO — senza questo, task asyncio non possono essere cancellati correttamente

---

## Pattern Python Raccomandati per Questo Stack

### aiohttp (HTTP Bridge)
```python
# Standard per tutte le chiamate al bridge
except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
    logger.warning("[BRIDGE] Offline, fallback SQLite: %s", e)
```

### sqlite3
```python
# Distinguere errori di schema da errori di dati
except sqlite3.OperationalError as e:
    # Schema mismatch, DB locked, file non trovato
    logger.error("[DB] Operational error: %s", e)
except sqlite3.IntegrityError as e:
    # Duplicate key, FK violation
    logger.warning("[DB] Integrity error: %s", e)
except sqlite3.Error as e:
    # Catchall per tutti gli altri sqlite3 errors
    logger.error("[DB] SQLite error: %s", e)
```

### Groq SDK
```python
# Hierarchy da groq SDK (verificare versione installata)
import groq
except groq.RateLimitError as e:
    circuit_breaker.record_failure()
    # Backoff + retry automatico gia in groq_client.py
except groq.APITimeoutError as e:
    logger.warning("[Groq] Timeout: %s", e)
except groq.APIConnectionError as e:
    logger.error("[Groq] Connection error: %s", e)
except groq.APIStatusError as e:
    logger.error("[Groq] Status %d: %s", e.status_code, e)
```

### asyncio task loops
```python
# SEMPRE aggiungere nei loop di ricezione/polling
while running:
    try:
        await do_work()
    except asyncio.CancelledError:
        raise  # CRITICAL: non intercettare mai CancelledError
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        logger.error("[LOOP] Error: %s", e)
        await asyncio.sleep(0.1)
```

### Top-level HTTP handlers (aiohttp)
```python
# Questo pattern e CORRETTO — safety net per handler HTTP
async def handle_request(self, request):
    try:
        # ... logica ...
    except Exception as e:
        logger.exception("[API] Unhandled error: %s", e)  # logger.exception() include stack trace
        return web.json_response({"success": False, "error": str(e)}, status=500)
```

### Optional component init
```python
try:
    self.nlp = spacy.load("it_core_news_sm")
except ImportError:
    logger.info("[NLU] spaCy non installato — modalita degradata")
    self.nlp = None
except OSError:
    logger.warning("[NLU] Modello spaCy non trovato — eseguire: python -m spacy download it_core_news_sm")
    self.nlp = None
```

---

## Stima Effort Totale

| Cluster | Effort | Impatto | Priorita |
|---------|--------|---------|----------|
| F — asyncio CancelledError | 30min | CRITICO | 1 |
| A — HTTP narrowing | 1h | ALTA | 2 |
| B — SQLite narrowing | 30min | MEDIA | 3 |
| C — Groq differenziata | 2h | MEDIA | 4 |
| E — logging exc_info | 30min | BASSA | 5 |
| D — optional init | 30min | BASSA | 6 |
| **TOTALE** | **~5h** | | |

---

## Acceptance Criteria per B4

1. Nessun `except Exception` cattura `asyncio.CancelledError` o `KeyboardInterrupt` nei loop asyncio
2. Tutti i fallback HTTP Bridge usano `except (aiohttp.ClientError, asyncio.TimeoutError, OSError)`
3. Tutte le operazioni SQLite usano `except sqlite3.Error` (o sottotipi) invece di `except Exception`
4. I Groq errors nel critical path (orchestrator.py riga 1286) differenziano RateLimitError da APIError
5. `pytest tests/ -v --tb=short` rimane green (151+ test)
6. `logger.exception()` usato nei safety net invece di `traceback.print_exc()`

---

## File NON da toccare

- `src/error_recovery.py` (riga 407) — e codice in docstring, non reale
- `main.py` handler top-level (except Exception e CORRETTO li)
- `vad_http_handler.py` handler top-level (idem)
- `src/tts.py` test block in `__main__` (riga 546-558) — solo test

---

## Note su file rag_engine.py

Il file `voice-agent/src/rag_engine.py` NON ESISTE nel codebase.
La funzionalita RAG e distribuita tra:
- `src/faq_manager.py` — FAQ retrieval (2 except Exception)
- `src/faq_retriever.py` — semantic retrieval (non analizzato, 0 occorrenze)
- `src/orchestrator.py` — coordina i layer RAG

---

*Research completato. Tutte le occorrenze lette da file reali — nessuna inventata.*
