# Project State

## Current Position

- Phase: f-sara-voice — IN PROGRESS (4/5 plans complete)
- Last completed plan: f-sara-voice-04 (TypeScript UI — VoiceSaraQuality + SetupWizard step 9)
- Previous phase: f-sara-nlu-patterns — COMPLETE
- Last activity: 2026-03-15 — Completed f-sara-voice-04-PLAN.md

Progress: [████░] 4 of 5 plans complete in f-sara-voice phase (80%)

Next plan: f-sara-voice-05 (checkpoint wave — final verification)

## Accumulated Decisions

| Decision | Made In | Details |
|----------|---------|---------|
| Rust build only on iMac | Global | MacBook cannot run cargo — no cargo check/build here |
| Migration 029 DEFAULT 'fattura24' | sdi-aruba-01 | Retrocompat — existing users keep Fattura24 without config change |
| COALESCE in sdi_provider_factory | sdi-aruba-01 | Null safety — handles rows where sdi_provider may be NULL |
| Fattura24Response before trait | sdi-aruba-01 | Dependency ordering — struct used by Fattura24Provider impl |
| All deps pre-existing | sdi-aruba-01 | async-trait, base64, reqwest, serde_json already in Cargo.toml — confirmed in plan 02 |
| COALESCE in update_impostazioni_fatturazione | sdi-aruba-02 | sdi_provider uses COALESCE(?, sdi_provider) — null input preserves existing value |
| Zod schema must match Rust struct | sdi-aruba-02 | ImpostazioniFatturazioneSchema fields mirror DB columns including 3 new SDI fields |
| SdiProviderSettings before FLUXION IA section | sdi-aruba-03 | Logical placement — SDI config near other integrations (WhatsApp, SMTP) |
| Explicit field mapping in useUpdateImpostazioniFatturazione | sdi-aruba-03 | All 24 fields enumerated explicitly — Tauri invoke named params, no spread |
| Multi-word-only guardrail patterns | f02-01 | No single-word blocks (e.g. 'ceretta' alone) — use context-word patterns |
| Context-word manicure/pedicure patterns | f02-01 | 'la manicure', 'fare la manicure' etc. to avoid false positives in medical |
| _dataclass_gr alias for GuardrailResult | f02-01 | Avoid collision with existing 'dataclass' import in italian_regex.py |
| HAS_VERTICAL_ENTITIES guard separate from HAS_ITALIAN_REGEX | f02-02 | If entity extractor import fails, guardrail still runs (both optional, independent) |
| entity extraction only if response is None | f02-02 | Follows existing L0 pattern — only runs when guardrail did not block |
| Adjective forms in ginecologia keywords | f02-02 | Real users say 'visita ginecologica' not 'una ginecologia' — adjective forms essential |
| F02 phase complete — 1197 PASS / 0 FAIL | f02-03 | All guardrail + entity extractor + orchestrator wiring verified on iMac |
| F03 next: streaming LLM approach | f02-03 | Groq stream=True + FSM template pre-computation to hit P95 <800ms from ~1330ms |
| cambia/modifica require booking object in SPOSTAMENTO | f02.1-01 | Generic verbs split from domain verbs — modal+cambia also requires booking obj |
| _disambiguate_hour_pm PHASE 5 only | f02.1-01 | PM convention applied only to bare digit hours — PHASE 1 (with minutes) unaffected |
| STT truncations as dict entries in DAYS_IT | f02.1-01 | marted/gioved/venerd/mercoled added alongside canonical forms — no regex needed |
| Article forms le/i/gli/dei/delle in gomme patterns | f02.1-02 | Italian masculine plural "i" missing from initial pattern — all article forms required |
| dal meccanico is multi-word | f02.1-02 | Two-word phrase satisfies multi-word-only guardrail rule — no exception needed |
| No verb-form patterns in auto vertical | f02.1-02 | Auto vertical handles these as valid in-scope services — do NOT block in auto |
| _NEGATED_CANCEL guard fires only on CANCELLAZIONE intent | f02.1-03 | Guard fires only when both intent==CANCELLAZIONE AND regex matches — no false positives |
| extra_suffix uses getattr + or {} double-safe pattern | f02.1-03 | Safe for missing attribute AND None value — zero behavior change for existing flows |
| extra_suffix appended to both Phase 4 and Phase 6 of _handle_confirming | f02.1-03 | Covers pure affirmative and Groq confermato paths — all CONFIRMING confirmation routes |
| SPOSTAMENTO semantic threshold >=0.6 without pattern match | f02.1-04 | TF-IDF alone needs 0.6+ to classify SPOSTAMENTO — prevents 'devo cambiare l'olio' false positive |
| LRU cache on classify_intent only | f03-01 | All 4 orchestrator call sites pass bare user_input (no verticale arg) — safe to normalize+cache by text |
| clear_intent_cache() in start_session() full reset only | f03-01 | Partial resets (mid-call) share same user context — only new-call full reset needs cache clear |
| streaming L4 max_tokens=150 + temperature=0.3 | f03-01 | Voice responses must be short; lower temp reduces hallucination in streaming mode |
| asyncio.gather NOT at L0 | f03-01 | extract_vertical_entities must run only after content filter passes — sequential is correct |
| GroqKeyPool _key_pool=None on init failure | f03-02 | Graceful degradation: no key or init exception → pool is None, rotation silently skipped |
| WAL mode skips :memory: DB | f03-02 | PRAGMA journal_mode=WAL only for file-based DBs — in-memory (pytest) unaffected |
| FluxionLatencyOptimizer.setup() is the init method | f03-02 | Not initialize() — verified from latency_optimizer.py source. hasattr check for forward compat |
| groq_client.py rotate() reinitializes both sync+async clients | f03-02 | Both self.client (Groq) and self.async_client (AsyncGroq) updated with new key on rotation |
| generate_response_streaming wired in L4 | f03-01 | Streaming eliminates asyncio.to_thread overhead; FALLBACK_RESPONSES for timeout resilience |
| intent_lru_cache.py 100-slot LRU | f03-01 | 4 classify_intent call sites replaced with get_cached_intent(); clear on session reset |
| GroqKeyPool in groq_client.py | f03-02 | rotate() on 429 in generate_response() retry loop; up to 3 keys from env |
| WAL mode in analytics.py _init_db() | f03-02 | Skip for :memory: DB (test safety); concurrent voice+WhatsApp writes safe |
| FluxionLatencyOptimizer.setup() (not initialize()) | f03-02 | async method name confirmed from latency_optimizer.py |
| /api/metrics/latency endpoint | f03-02 | GET returns {p50_ms, p95_ms, p99_ms, count, hours} from get_percentile_stats() |
| 4096-sample accumulation in worklet | audioworklet-01 | Matches ScriptProcessorNode buffer size for VAD backend chunk compatibility |
| .slice() for postMessage copy | audioworklet-01 | Prevents buffer neutering — no transferable used in port.postMessage |
| AudioWorkletNode no destination connection | audioworklet-01 | GainNode silencer not needed — worklet runs in dedicated thread, stays alive without destination |
| setInterval processAudioBuffer retained | audioworklet-01 | HTTP chunk dispatch unchanged — worklet replaces capture only, not the send interval |
| VERTICAL_SERVICES salone alias to hair | f-sara-nlu-patterns-01 | VERTICAL_SERVICES["salone"] = VERTICAL_SERVICES["hair"] post-dict — overrides original salone entry, 50 backward compat tests pass |
| hair guardrail includes full verb-form auto patterns | f-sara-nlu-patterns-01 | Plan listed simplified patterns; original salone verb-forms (cambiare gomme, far vedere la macchina) required for backward compat |
| sub_vertical = None default on VerticalEntities | f-sara-nlu-patterns-01 | Zero-impact on existing medical/auto extraction — only hair/beauty branches set sub_vertical |
| elif ("hair", "salone") single branch | f-sara-nlu-patterns-01 | Single extraction branch for both keys avoids code duplication |
| "medico" key added to medical check | f-sara-nlu-patterns-01 | Prep for Wave B — extract_vertical_entities() now matches both "medical" and "medico" |
| wellness guardrail includes visita medica/specialistica OOS | f-sara-nlu-patterns-02 | Legacy palestra had this pattern; alias must preserve — added explicitly to wellness |
| wellness + medico get cambiare-le-gomme verb-form pattern | f-sara-nlu-patterns-02 | Legacy palestra/medical had cambiar[ei]..gomm[ea] verb-form — required for backward compat |
| odontoiatria keywords extended with invisalign/ortodonzia | f-sara-nlu-patterns-02 | Plan test case required adjective/brand forms not in original noun-only list |
| cardiologica/cardiologico adjective forms in cardiologia | f-sara-nlu-patterns-02 | "cardiologia" NOT in "cardiologica" — adjective forms must be explicit in keyword list |
| alias new verticals must carry ALL legacy verb-form patterns | f-sara-nlu-patterns-02 | When aliasing palestra->wellness and medical->medico, original dict had verb-forms; new dict must include them |
| revisione_servizi separate from revisione key | f-sara-nlu-patterns-03 | No collision with existing 'revisione' auto key — only new sub-keys added |
| ozono abitacolo requires contiguous substring | f-sara-nlu-patterns-03 | "ozono sanificazione abitacolo" does NOT match keyword "ozono abitacolo" — substring check, non-contiguous fails |
| auto guardrail does not include sala pesi | f-sara-nlu-patterns-03 | Only personal_trainer|personal_training from wellness set in auto guardrail — tests use only covered patterns |
| DURATION_MAP uses medico key (not medical) | f-sara-nlu-patterns-03 | Canonical Wave B key; medical is legacy alias only |
| NEW_VERTICALS before LEGACY_VERTICALS in _extract_vertical_key | f-sara-nlu-patterns-04 | Priority ordering prevents 'medico_*' from matching legacy 'medical' via bare startswith |
| Separator-aware prefix match (v+'_' or v+'-') before bare startswith | f-sara-nlu-patterns-04 | Prevents 'palestra' matching 'professionale' — separator check eliminates ambiguous overlaps |
| self._faq_vertical cached attribute at all call sites | f-sara-nlu-patterns-04 | Lines 673+685 prod bug fix: normalised key used; attribute already cached in orchestrator setup |
| Standalone _extract_vertical_key_impl in integration test file | f-sara-nlu-patterns-04 | Avoids full orchestrator import chain in unit tests; fast and isolated |
| No top-level torch import in tts_engine.py | f-sara-voice-01 | transformers pipeline manages torch internally — module importable on Python 3.9 without torch pre-installed |
| QwenTTSEngine._model class-level singleton | f-sara-voice-01 | One model load per process — multiple QwenTTSEngine() instances share same transformers pipeline |
| PiperTTSEngine binary search mirrors PiperTTS.__init__ | f-sara-voice-01 | Venv bin first, then ~/.local/bin, /usr/local/bin, then shutil.which — behavioral parity with tts.py |
| capable = RAM>=8GB AND cores>=4 | f-sara-voice-01 | Hardware threshold for Qwen3-TTS AUTO mode selection — matches iMac profile (16GB, 10 cores) |
| .tts_mode plain text file | f-sara-voice-02 | Mode persisted as plain text (quality/fast/auto) — no DB, no JSON, single write_text() call |
| download_qwen_model returns bool | f-sara-voice-02 | Caller controls error UX — never raises, returns False on any failure including missing huggingface_hub |
| huggingface_hub lazy import in download | f-sara-voice-02 | Imported inside download_qwen_model() only — module importable without huggingface_hub installed |
| tts hardware handler uses lazy TTSEngineSelector import | f-sara-voice-02 | Import inside handler body — no startup cost if /api/tts/hardware endpoint never called |
| _ADAPTIVE_ENGINE_AVAILABLE flag in tts.py | f-sara-voice-03 | Clean degradation if tts_engine.py import fails — get_tts() falls back to PiperTTS |
| use_piper=False legacy -> SystemTTS preserved | f-sara-voice-03 | No-audio mode unchanged — orchestrator can still disable TTS via use_piper=False |
| SetupWizard totalSteps bumped 8->9 | f-sara-voice-04 | Step 9 positioned after Groq key step — voice quality selection at end of wizard |
| useEffect step===9 lazy hardware detection | f-sara-voice-04 | Hardware fetch only on step entry — avoids eager API call before user reaches step 9 |
| Wizard POSTs mode only — download deferred | f-sara-voice-04 | 1.2GB Qwen3-TTS downloaded at first Sara startup, not during setup wizard |
| VoiceSaraQuality.tsx committed in plan-03 bonus | f-sara-voice-04 | File present in 02e3eee — plan-04 Task 1 confirmed existing file, no re-commit needed |
| Adaptive fallback chain in get_tts() | f-sara-voice-03 | create_tts_engine() fail -> PiperTTS -> SystemTTS — same chain as tts_engine.py design |

## Blockers / Concerns

- P95 real with LLM: to be measured after production voice sessions (current 0.3ms = test-only turns)
- Optional: add GROQ_API_KEY_2 / GROQ_API_KEY_3 to iMac .env for key pool to be effective
- P0.5 Onboarding Frictionless: BLOCKER VENDITE — Groq bundled key vs setup wizard decision needed

## Session Continuity

Last session: 2026-03-15 (S77)
Stopped at: f-sara-voice-04 COMPLETE — VoiceSaraQuality + SetupWizard step 9 + VoiceAgentSettings wiring — commits f0c783b + e36f51a
Resume file: None
Next: f-sara-voice-05 (checkpoint wave — final verification)
