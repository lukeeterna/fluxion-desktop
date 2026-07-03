# Sara — Soglie Benchmark per T-SARA-B (chiamata reale)

> Tarate sull'hardware reale: iMac 2012 (no AVX2), STT/LLM cloud (Groq), TTS EdgeTTS/Piper.
> Creato in T-SARA-A (2026-07-03). Fonte misura = analytics DB + endpoint `/api/metrics/latency` (F03, `main.py:845`), campo `latency_ms` per turno (`main.py:550`).

## 1. Latenza per turno
| Soglia | Valore | Fonte |
|--------|--------|-------|
| Target | P95 ≤ 1.5 s | `/api/metrics/latency` (p95_ms) |
| Accettabile | P95 ≤ 2.0 s | idem |
| FAIL UX | P95 > 3.0 s | idem |

Ripartizione attesa per stadio (iMac 2012 + cloud): STT Groq whisper-large-v3 ~200–400 ms · NLU/LLM Groq llama-3.3-70b ~300–600 ms · TTS EdgeTgt ~500 ms (Piper fallback ~50 ms).
**MISURABILE dai log**: totale per turno (P50/P95/P99). **NON per-stadio**: l'aggregato attuale è total-turn; la ripartizione STT/NLU/TTS è stima, non loggata per-stadio (refinement opzionale, non bloccante per T-SARA-B).

## 2. Comprensione (STT)
- Trascrizione corretta su nomi/date/orari italiani. **MISURABILE**: testo trascritto (analytics turn) vs detto (giudizio founder sul contenuto).

## 3. Completamento task
- La chiamata finisce con **appuntamento REALE scritto in agenda** (verificabile nel DB FLUXION) per i 4 verticali FSM (salone/palestra/medical/auto).
- Richiede il **Tauri HTTP Bridge :3001 UP** (Sara scrive il booking via bridge). **MISURABILE**: query DB post-chiamata.

## 4. Robustezza
- ≥2 chiamate sovrapposte senza crash né degrado.
- **Nessun SIGABRT** per l'intera durata (build NDEBUG verificata T-SARA-A, md5 match).
- Gestione interruzione (barge-in RMS, `voip_pjsua2.py:217,278`) e "non ho capito" (`vertical_integration.py:231`) senza loop. **MISURABILE**: assenza crash report `.ips` + log.

## 5. Voce/UX
- Audio intelligibile senza artefatti per tutta la chiamata. **GIUDIZIO FOUNDER** (soggettivo) + assenza errori TTS nei log.

## Onestà misurabilità
- **Misurabili dai log/DB**: latenza totale/turno (P50/95/99), trascrizione STT, appuntamento scritto in DB, assenza SIGABRT/errori TTS.
- **Richiedono giudizio umano founder**: qualità audio percepita, naturalezza intercalari, correttezza semantica della conversazione end-to-end.
