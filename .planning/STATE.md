# Project State

## Current Position

- Phase: f03-latency-optimizer — In progress
- Last completed plan: f03-02
- Status: Plan 2 of 3 complete — GroqKeyPool + WAL mode + P50/P95/P99 analytics + latency endpoint
- Last activity: 2026-03-04 — Completed f03-02-PLAN.md (resilience + observability layer)

Progress: [██░] Plan 02 of 3 complete in f03 phase (67%)

Next: F03-03 (if exists) — check f03-03-PLAN.md or mark F03 complete

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

## Blockers / Concerns

- iMac voice pipeline restart required after f03-01 and f03-02 Python changes (port 3002)
- P95 latency target <800ms (current ~1330ms) — f03-01 saves ~10-15ms/turn, streaming LLM saves 50-100ms
- Optional: add GROQ_API_KEY_2 / GROQ_API_KEY_3 to iMac .env for key pool to be effective

## Session Continuity

Last session: 2026-03-04T18:35:45Z
Stopped at: Completed f03-02-PLAN.md (GroqKeyPool + WAL + percentiles + latency endpoint, committed in 4f7478c + 7490e4b)
Resume file: None
Next plan: F03-03 — check if plan exists, otherwise F03 complete
