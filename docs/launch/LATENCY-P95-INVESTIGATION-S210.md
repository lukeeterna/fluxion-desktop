# Latency P95 Investigation — S210

**Source data**: release-gate-20260512-183400.json + live probe S210 (2026-05-13 11:30 CEST)

## Baseline (from release-gate run 2)

```
samples:               162
avg_ms:               2183
p50_ms:                905    <- eccellente
p95_ms:               9795    <- problematic tail
p99_ms:              11047
max_ms:              11170
slow_sample_ratio:   0.179    <- 29 sample / 162 oltre 5000ms
threshold (slow):    5000ms
gate hard fail:     12000ms   <- non superato (PASS)
gate SLO target:     2000ms   <- WARN-only
```

## Live probe per-layer (S210, 2026-05-13)

Pipeline UP, sequential calls:

| Input | Layer | Latency | Note |
|-------|-------|--------:|------|
| "Buongiorno" | L1_exact | **997ms** | ❗ alto per cached greeting path (atteso <100ms) |
| "quali sono i vostri orari" | L3_faq | 1336ms | cold cache, first FAQ lookup |
| "raccontami i vostri pacchetti benessere e cosa offrite" | L4_groq | **3183ms** | LLM fallback Groq llama-3.3-70b |
| "dimmi tutto sui trattamenti viso e corpo" | L3_faq | 185ms | warm cache hit |
| "vorrei prenotare un trattamento" | L2_slot | 875ms | FSM slot fill |

## Findings

### Finding 1 — L1_exact path NOT sub-100ms (anomalia)
**Evidence**: greeting cached "Buongiorno" → 997ms.
**Hypothesis**: L1 path include `get_cached_intent()` (LRU 100-slot, F03 fix) + entity extraction + session manager DB write + audit_client emit + TTS warm cache lookup. Pipeline overhead non-LLM è ~1s.
**Impact**: contributo al P95 marginale (L1 è < 5000ms threshold), ma riduce headroom per cumulative overhead in L3/L4.

### Finding 2 — L3 cold-cache penalty 7x
**Evidence**: prima query FAQ 1336ms vs 185ms warm.
**Hypothesis**: FAQ retriever (keyword search in `data/faq/<vertical>/*.json`) parsa file al primo accesso, poi mantiene index in-memory. Pre-warm in `main.py` startup mancante per FAQ.
**Action proposta S211**: aggiungere `await orchestrator.faq_manager.warm_index(vertical)` in startup hook (analogo a `warm_greetings`/`warm_fillers` esistenti L657-685).

### Finding 3 — L4_groq baseline 3183ms (atteso, ma vicino soglia)
**Evidence**: primo LLM fallback 3183ms.
**Hypothesis**: Groq API call media 800-2000ms (network + inference llama-3.3-70b), oltre overhead pipeline 1-1.3s (vedi Finding 1).
**Impact diretto**: L4 da solo NON spiega P95=9795ms.

### Finding 4 — P95 9795ms = stack cumulativo
**Hypothesis**: i 29 sample slow sono turn dove pipeline esegue:
1. L4_groq fallback (3-4s)
2. + LLM NLU extraction (Groq seconda call per slot extraction, 1-2s)
3. + WhatsApp service call sync (booking confirmation, 1-2s se timeout sync)
4. + TTS sintesi non-cached frase generata da L4 (Edge-TTS 500-1500ms cloud)
5. + DB writes appuntamento + audit (50-200ms)
**Stack tail probabile**: 6-10s cumulativo per turn LLM-heavy con TTS non-cache.

## Recommendation S211 (priorità ordine)

1. **TTS pre-warm L4 response patterns** (~30 min, alto impatto): identificare 10-20 frasi LLM-generated più frequenti (post-confirmation, slot-fill confirmation, error fallback) e pre-warmarle in `tts.warm_cache()` startup. Riduzione attesa 500-1500ms su tail.

2. **FAQ index warm at startup** (~15 min, medio impatto): pattern Finding 2. Riduzione cold-call FAQ ~1100ms.

3. **Streaming LLM → TTS** (~3h, alto impatto, già documentato in `latency_optimizer.py`): TODO v1.1 esistente. Atteso first-audio-byte da 3s → 800ms.

4. **L1 path profiling** (~45 min, basso impatto sul tail ma riduce P50): instrumentare `process_message` per breakdown intent/entity/session/audit. Identificare se F03 cache miss costa 200-500ms.

5. **Instrumentare release-gate report con breakdown per-layer** (~30 min): patch `R` framework (`test_sara_stress_per_verticale.py`) per salvare `events: [{level, tag, scenario, message, ms, layer}]` in JSON. Eliminerà guesswork audit.

## Decisione S210

**NON shipping-blocker** — P50 905ms eccellente, P95 9795ms sotto hard-fail catastrofico 12000ms, gate PASS. Investigation dovuta, fix deferiti S211 perché:
- Fix #1+#2 quick win ma richiedono test mirati per validazione (~1h totale)
- Fix #3 grosso (3h, modifica orchestrator) — sessione separata
- Fix #5 strumentazione → necessaria PRIMA di #4 per dati reali

Audit chiuso. Investigazione documentata. Niente patch in S210.

---
**Investigation eseguita**: S210 (2026-05-13)
**Author**: Claude (CTO autonomo)
