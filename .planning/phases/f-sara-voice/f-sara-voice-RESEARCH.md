# F-SARA-VOICE Research — FluxionTTS Adaptive

> Source: memory/project_qwen3tts_sara.md (CTO decision S73) + CoVe 2026 analysis
> Status: COMPLETE — ready for planning

---

## Decisione CTO (S73)

Qwen3-TTS **sostituisce** Piper come motore primario Sara.
Implementazione: **dual-mode adaptive** — Quality (Qwen3-TTS) su PC capaci, Fast (Piper) su PC datati.
> "Non voglio che abbia una voce robotica a chi ha il PC giusto."

---

## Architettura FluxionTTS Adaptive

```
Sara riceve testo
        ↓
  [TTSEngineSelector] — rileva hardware al primo avvio
        ↓
┌──────────────────────┐    ┌────────────────────────┐
│ FluxionTTS-Fast      │    │ FluxionTTS-Quality     │
│ Piper Italian        │    │ Qwen3-TTS 0.6B         │
│ ~50ms · 50MB bundled │    │ streaming, 400-800ms   │
│ qualsiasi PC         │    │ download ~1.2GB        │
│ fallback garantito   │    │ PC capace ≥8GB RAM     │
└──────────────────────┘    └────────────────────────┘
```

## Criteri Selezione Automatica
- RAM ≥ 8GB disponibile → offri Quality
- CPU cores ≥ 4 + AVX2 supportato → offri Quality
- Entrambi ✅ → auto-select Quality con dialog "Vuoi scaricare la voce HD? (1.2GB)"
- Non soddisfatti → Fast silenzioso, nessun download

---

## Modelli

| Mode | Model | Size | Latency | License |
|------|-------|------|---------|---------|
| Quality | `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | ~1.2GB fp16 | 400-800ms streaming | Apache 2.0 |
| Fast | `it_IT-paola-medium.onnx` (Piper) | ~50MB bundled | ~50ms | MIT |

---

## Streaming = Chiave Latenza
- Qwen3-TTS supporta **streaming generation** (audio chunks mentre genera)
- Primo chunk audio: ~200-300ms → perceived latency < 400ms
- Resto audio sovrapposto a riproduzione → fluido
- P95 totale su PC capace: ~600-700ms (entro <800ms target) ✅

---

## Voice Clone Sara
- Generare reference audio Sara (voce femminile italiana professionale) con Voice Clone Studio (FranckyB)
- Includere ~30s WAV come `assets/sara-reference-voice.wav` nell'app
- Qwen3-TTS CustomVoice usa questo file per clonare voce Sara su qualsiasi testo

---

## UX — Setup Wizard (DECISIONE CTO S73)
La selezione TTS avviene **durante il Setup Wizard** (step Sara), NON post-install.

**PC capace (≥8GB RAM, ≥4 core):**
```
⭐ CONSIGLIATO: Alta Qualità (Qwen3-TTS)
   Voce naturale, espressiva, italiana — Download: 1.2GB
○  Veloce (Piper) — nessun download
[Scarica Alta Qualità]  [Usa Veloce]
```

**PC datato (<8GB RAM o <4 core):**
```
⚠️ RAM: 4GB (minimo consigliato: 8GB)
⭐ CONSIGLIATO: Veloce (Piper) — nessun download, <100ms
○  Alta Qualità — potrebbe essere lenta su questo computer
```

Post-install: `Impostazioni → Sara → Qualità Voce → [Auto | Alta qualità | Veloce]`

---

## File da Creare

### Backend Python (voice-agent/)
- `src/tts_engine.py` — `TTSEngineSelector`, `QwenTTSEngine`, `PiperTTSEngine`
- `src/tts_download_manager.py` — first-run download + progress tracking
- Update `main.py` — integrazione nuovi engines in TTS pipeline

### Frontend TypeScript (src/)
- Settings UI: componente `VoiceSaraQuality` in Impostazioni → Sara
- Setup Wizard step Sara: dialog hardware detection + download

### Assets
- `voice-agent/assets/sara-reference-voice.wav` — reference audio per voice clone

---

## File Chiave Esistenti
```
voice-agent/main.py                        # HTTP server porta 3002
voice-agent/src/booking_state_machine.py   # FSM 23 stati
voice-agent/src/orchestrator.py            # pipeline TTS attuale
voice-agent/src/italian_regex.py           # NLU patterns (appena aggiornato)
public/audio-processor.worklet.js          # AudioWorklet (S74)
src/components/setup/SetupWizard.tsx       # wizard step Sara (da aggiornare)
```

---

## Piano Implementazione (Step-by-Step)

1. **Research/Benchmark** — misura latenza Qwen3-TTS 0.6B su CPU Intel i5 2019
2. **Voice Design** — genera `sara-reference-voice.wav` con Voice Clone Studio
3. **Backend Python** — `tts_engine.py` con engines + selector + streaming
4. **Download Manager** — first-run dialog + progress bar + fallback automatico
5. **Settings UI** — `VoiceSaraSettings` qualità voce selector
6. **Streaming Integration** — chunk audio → play via existing TTS pipeline
7. **Test Latenza** — P95 su PC Intel i5 2019 (rappresentativo cliente PMI)
8. **iMac verify** — pytest + pipeline restart + test live audio

---

## Prerequisiti
- ✅ AudioWorklet fase (S74 — completata)
- ✅ NLU patterns (S75 — completata, 1896 PASS)
- ✅ VAD open-mic approvato fisicamente su iMac
- ⚠️ EHIWEB SIP: credenziali ancora in arrivo → non bloccante per F-SARA-VOICE

---

## Regole Non Negoziabili
1. MAI rimuovere Piper — è sempre il fallback garantito
2. Qwen3-TTS è opzionale, scaricabile, mai obbligatorio
3. Testare SEMPRE su PC low-end (Intel i5 2019, 8GB RAM) prima di rilasciare
4. Python 3.9 runtime (NO PyTorch) — usare ONNX Runtime o llamacpp per inferenza
5. Latency target P95 < 800ms — misurare con benchmark reale

---

## RESEARCH COMPLETE
