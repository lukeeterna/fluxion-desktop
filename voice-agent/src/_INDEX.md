# Voice Agent — File Index
> Auto-generato da `scripts/update_voice_index.py` — NON modificare manualmente.
> Aggiornato: vedi ultima riga del file.
> **Scopo**: trovare metodo/pattern → riga esatta senza leggere file interi (~7200 righe).

---

## booking_state_machine.py — 4443 righe

### Enums & Dataclasses
| Simbolo | Riga | Note |
|---------|------|------|
| `BookingState` (Enum) | 73 | 23 stati FSM |
| `BookingContext` (dataclass) | 110 | slot: nome, cognome, servizio, data, ora, operatore, telefono |
| `StateMachineResult` (dataclass) | 247 | response, next_state, has_follow_up |

### BookingState — 23 stati
| Stato | Valore |
|-------|--------|
| `IDLE` | idle |
| `WAITING_NAME` | waiting_name |
| `WAITING_SERVICE` | waiting_service |
| `WAITING_DATE` | waiting_date |
| `WAITING_TIME` | waiting_time |
| `WAITING_OPERATOR` | waiting_operator |
| `CONFIRMING` | confirming |
| `COMPLETED` / `CANCELLED` | — |
| `WAITING_SURNAME` | guided identity flow |
| `CONFIRMING_PHONE` | — |
| `PROPOSE_REGISTRATION` | new client |
| `REGISTERING_SURNAME` / `REGISTERING_PHONE` / `REGISTERING_CONFIRM` | — |
| `CHECKING_AVAILABILITY` / `SLOT_UNAVAILABLE` / `PROPOSING_WAITLIST` / `CONFIRMING_WAITLIST` / `WAITLIST_SAVED` | waitlist |
| `ASKING_CLOSE_CONFIRMATION` | chiusura |
| `DISAMBIGUATING_NAME` / `DISAMBIGUATING_BIRTH_DATE` | omonimi |

### BookingContext — metodi (riga 110)
| Metodo | Riga |
|--------|------|
| `to_json()` | 170 |
| `from_json()` | 179 |
| `to_dict()` | 187 |
| `get_summary()` | 209 |
| `is_complete()` | 226 |
| `get_missing_fields()` | 230 |

### BookingStateMachine — classe (riga 559)
| Metodo | Riga | Descrizione |
|--------|------|-------------|
| `__init__` | 570 | init con orchestrator, groq_client, verticale |
| `reset()` | 595 | reset stato FSM (full o parziale) |
| `reset_for_new_booking()` | 624 | mantiene cliente, azzera slot |
| `handle_input()` | 640 | entrypoint principale |
| `handle_input_with_confidence()` | 648 | con confidence score STT |
| `handle_api_error()` | 673 | gestisce errori API Groq |
| `complete_booking()` | 692 | finalizza prenotazione su DB |
| `process_message()` | 715 | processa messaggio con FSM routing |
| `process()` | 815 | alias di process_message (compatibilità) |
| `_check_interruption()` | 849 | comandi speciali a qualsiasi stato |
| `_update_context_from_extraction()` | 896 | aggiorna slot da ExtractionResult |
| `_update_context_from_dict()` | 957 | aggiorna slot da dict |

### FSM State Handlers (BookingStateMachine)
| Handler | Riga | Stato gestito |
|---------|------|---------------|
| `_handle_idle()` | 1002 | IDLE → raccoglie nome |
| `_handle_waiting_name()` | 1092 | WAITING_NAME → disambiguazione/registrazione |
| `_check_name_disambiguation()` | 1409 | lookup omonimi su DB |
| `_check_name_disambiguation_simulation()` | 1517 | test mode con dati mock |
| `_evaluate_candidates()` | 1562 | scoring candidati per disambiguazione |
| `_extract_surname_from_text()` | 1736 | estrai cognome da utterance |
| `_handle_waiting_surname()` | 1827 | WAITING_SURNAME |
| `_handle_waiting_service()` | 1865 | WAITING_SERVICE |
| `_handle_waiting_date()` | 1960 | WAITING_DATE |
| `_handle_waiting_time()` | 2083 | WAITING_TIME |
| `_handle_waiting_operator()` | 2154 | WAITING_OPERATOR |
| `_extract_level1_entities()` | 2192 | estrazione entità veloce L1 |
| `_detect_correction_or_rejection_signal()` | 2231 | rileva "no voglio cambiare…" |
| `_is_explicit_confirmation()` | 2247 | "sì/confermo/esatto" |
| `_format_correction_summary()` | 2258 | testo riepilogo correzioni |
| `_get_correction_patterns_for_vertical()` | 2274 | pattern correzione per verticale |
| `_build_booking_confirmation_message()` | 2285 | messaggio riepilogo prenotazione |
| `_get_state_response()` | 2310 | risposta standard per stato |
| `_normalize_service_display()` | 2328 | normalizza nome servizio |
| `_format_date_display()` | 2332 | data → "martedì 12 marzo" |
| `_format_time_display()` | 2343 | ora → "alle 15:30" |
| `handle_timeout()` | 2347 | timeout silenzio utente |
| `_get_next_required_slot()` | 2354 | prossimo slot mancante |
| `_is_slot_filled()` | 2376 | verifica slot compilato |
| `_skip_to_next_required_state()` | 2389 | salta a stato corretto |
| `_handle_confirming()` | 2405 | CONFIRMING — 3-level correction |
| `_handle_propose_registration()` | 2661 | PROPOSE_REGISTRATION |
| `_handle_registering_surname()` | 2747 | REGISTERING_SURNAME |
| `_handle_registering_phone()` | 2955 | REGISTERING_PHONE |
| `_handle_confirming_phone()` | 3091 | CONFIRMING_PHONE |
| `_handle_registering_confirm()` | 3153 | REGISTERING_CONFIRM |
| `_handle_asking_close_confirmation()` | 3195 | ASKING_CLOSE_CONFIRMATION |
| `propose_new_client_registration()` | 3244 | trigger flusso nuovo cliente |
| `start_booking_flow()` | 3263 | avvia flusso prenotazione |
| `_handle_disambiguating_name()` | 3305 | DISAMBIGUATING_NAME |
| `_handle_disambiguating_birth_date()` | 3387 | DISAMBIGUATING_BIRTH_DATE |

### Helper Functions (module-level)
| Funzione | Riga | Descrizione |
|----------|------|-------------|
| `sanitize_name()` | 413 | normalizza nome/cognome |
| `sanitize_name_pair()` | 463 | normalizza coppia nome+cognome |

---

## orchestrator.py — 5127 righe

### Classi e costanti
| Simbolo | Riga | Note |
|---------|------|------|
| `ProcessingLayer` (Enum) | 191 | L0_SPECIAL / L1_EXACT / L2_SLOT / L3_FAQ / L4_GROQ |
| `_concat_wav_chunks()` | 256 | merge WAV in ordine (F03 parallel TTS) |
| `OrchestratorResult` (dataclass) | 293 | response, layer, intent, session_id, latency_ms |
| `VoiceOrchestrator` (class) | 330 | pipeline principale |
| `create_orchestrator()` | 2765 | factory function |

### Pipeline entry point
| Metodo | Riga | Descrizione |
|--------|------|-------------|
| `__init__()` | 345 | config, fsm, groq, tts, stt, layers |
| `start_session()` | 456 | inizia sessione con analytics |
| `process()` | 522 | **MAIN** — 5-layer RAG pipeline |
| `end_session()` | 1567 | chiude sessione, log analytics |

### 5-Layer Pipeline (dentro `process()` riga 522)
| Layer | Righe | Descrizione |
|-------|-------|-------------|
| **L0-PRE** Italian Regex + Guardrail + Entity Extract | 575–640 | prefilter, vertical guardrail, entity extraction |
| **L0** Special Commands | 641–660 | aiuto, operatore, annulla |
| **L0a** WhatsApp FAQ | 661–670 | evita Groq denial su domande WA |
| **L0b** Advanced NLU (spaCy/UmBERTo) | 671–694 | fallback avanzato |
| **L0c** Sentiment Analysis | 695–715 | escalation check |
| **L1** Intent Classification (Exact Match) | 716–936 | pattern matching veloce |
| **L2** Disambiguation + Booking FSM | 937–1276 | slot filling principale |
| **L2.5** Cancel/Reschedule | 1277–1364 | gestione modifica appuntamenti |
| **L3** FAQ Retrieval | 1365–1401 | risposta FAQ da DB |
| **L3.5** Guided Dialog | 1379–1414 | off-track conversations |
| **L4** Groq LLM Fallback | 1415–1477 | ultimo resort, streaming |

### Metodi helper VoiceOrchestrator
| Metodo | Riga | Descrizione |
|--------|------|-------------|
| `_check_special_command()` | 1580 | comandi speciali (aiuto/operatore) |
| `_load_business_config()` | 1595 | carica config da HTTP Bridge |
| `_load_config_from_sqlite()` | 1610 | carica config da SQLite diretto |
| `_extract_vertical_key()` | 1655 | normalizza ID verticale |
| `_load_vertical_faqs()` | 1676 | carica FAQ da DB per verticale |
| `set_vertical()` | 1728 | cambia verticale a runtime |
| `_handle_back()` | 1759 | gestisce "torna indietro" |
| `_build_llm_context()` | 1783 | costruisce context per Groq |
| `_get_context_summary()` | 1808 | riepilogo sessione corrente |
| `_search_client()` | 1824 | cerca cliente via HTTP Bridge |
| `_search_client_sqlite_fallback()` | 1849 | cerca cliente via SQLite diretto |
| `_create_booking()` | 1936 | crea prenotazione via HTTP Bridge |
| `_find_db_path()` | 1985 | trova path SQLite su disco |
| `_create_booking_sqlite_fallback()` | 2001 | crea prenotazione via SQLite |
| `_send_wa_booking_confirmation()` | 2069 | invia WA conferma (Gap #4) |
| `_trigger_wa_escalation_call()` | 2120 | escalation → operatore umano |
| `_create_client()` | 2151 | crea nuovo cliente via HTTP Bridge |
| `_create_client_sqlite_fallback()` | 2190 | crea nuovo cliente via SQLite |
| `_check_slot_availability()` | 2274 | verifica disponibilità slot via HTTP |
| `_check_slot_availability_sqlite_fallback()` | 2331 | verifica disponibilità via SQLite |
| `_search_operators()` | 2439 | lista operatori disponibili |
| `_cancel_booking()` | 2453 | cancella appuntamento |
| `_reschedule_booking()` | 2482 | riprogramma appuntamento |
| `_add_to_waitlist()` | 2527 | aggiunge a lista d'attesa |
| `_get_client_appointments()` | 2553 | appuntamenti futuri cliente |
| `_get_appointment_by_id()` | 2578 | singolo appuntamento by ID |
| `_handle_cancel_flow()` | 2585 | flow completo cancellazione |
| `_handle_reschedule_flow()` | 2648 | flow completo riprogrammazione |
| `_reset_cancel_reschedule_state()` | 2751 | reset stato cancel/reschedule |

### LRU Cache (module-level, riga ~95)
| Simbolo | Riga | Descrizione |
|---------|------|-------------|
| `get_cached_intent()` | 101 | lookup LRU cache per utterance |
| `clear_intent_cache()` | 103 | reset cache (su /reset endpoint) |

---

## italian_regex.py — 1361 righe

### Gruppi di Pattern (sezioni principali)
| Gruppo | Righe | Funzione pubblica | Descrizione |
|--------|-------|-------------------|-------------|
| **Filler** | 33–77 | `strip_fillers(text)` L64 / `detect_fillers(text)` L74 | rimuove "ehm", "allora", ecc. |
| **Conferma** | 84–119 | `is_conferma(text) → (bool, float)` L107 | "sì/confermo/esatto" |
| **Rifiuto** | 126–160 | `is_rifiuto(text) → (bool, float)` L149 | "no/non voglio" |
| **Escalation** | 168–218 | `is_escalation(text) → (bool, float, str)` L195 | cliente aggressivo/frustrato |
| **Service Synonyms** | 222–297 | `get_service_synonyms(vertical)` L294 | sinonimi per verticale |
| **Multi-service** | 299–355 | `extract_multi_services(text, vertical)` L309 / `has_multi_service_intent(text)` L349 | "taglio e colore" |
| **Content Filter** | 357–479 | `check_content(text) → ContentFilterResult` L439 | mild/moderate/severe |
| **Correction Detection** | 481–572 | `detect_correction(text) → (CorrectionType, float)` L558 | "no aspetti voglio…" |
| **Ambiguous Date** | 574–597 | `is_ambiguous_date(text)` L591 | "lunedì" senza data |
| **Flexible Scheduling** | 599–640 | `is_flexible_scheduling(text)` L630 | "quando vuoi/prima disponibile" |
| **Prefilter** | 642–716 | `prefilter(text) → RegexPreFilterResult` L670 | applica tutti i filtri |
| **Vertical Guardrail** | 718–892 | `check_vertical_guardrail(text, vertical) → GuardrailResult` L859 | blocca richieste OT |

### Classi
| Classe | Riga | Descrizione |
|--------|------|-------------|
| `ContentSeverity` (Enum) | 365 | MILD / MODERATE / SEVERE |
| `ContentFilterResult` (dataclass) | 373 | severity, message, should_block |
| `CorrectionType` (Enum) | 486 | FIELD / REJECTION / CONFIRMATION |
| `RegexPreFilterResult` (dataclass) | 648 | filler_detected, escalation, content_severity |
| `GuardrailResult` (dataclass) | 730 | blocked, reason, vertical |

### Costanti chiave
| Costante | Riga | Uso |
|----------|------|-----|
| `FILLER_PATTERNS` | 33 | lista regex filler |
| `_NO_ASPETTI_PRIORITY` | 58 | "no aspetti" → override rifiuto |
| `CONFERMA_PATTERNS` | 84 | lista regex conferma |
| `RIFIUTO_PATTERNS` | 126 | lista regex rifiuto |
| `ESCALATION_PATTERNS` | 168 | lista regex escalation |
| `MULTI_SERVICE_PATTERNS` | 333 | pattern "X e Y" |
| `AMBIGUOUS_DATE_PATTERNS` | 579 | pattern data ambigua |
| `FLEXIBLE_SCHEDULING_PATTERNS` | 605 | pattern disponibilità flessibile |

---

_Aggiornato: 2026-04-10 — booking_state_machine.py: 4443 | orchestrator.py: 5127 | italian_regex.py: 1361_
