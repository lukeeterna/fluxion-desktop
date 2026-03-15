# FLUXION — Handoff Sessione 76 → 77 (2026-03-15)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 533c2b9
docs(handoff): S75 complete — F-SARA-NLU-PATTERNS done, S76 next: F-SARA-VOICE
type-check: 0 errori ✅ | iMac pytest: 1896 PASS / 3 pre-existing FAIL / 27 skipped ✅
```

---

## COMPLETATO SESSIONE 76

### F-SARA-VOICE — PIANIFICAZIONE COMPLETA ✅

5 piani in 3 wave — verificati dal gsd-plan-checker in 2 iterazioni (3 blockers risolti).

**Piani creati**: `.planning/phases/f-sara-voice/`
- `f-sara-voice-01-PLAN.md` — Wave 1: `tts_engine.py` (QwenTTSEngine + PiperTTSEngine + TTSEngineSelector)
- `f-sara-voice-02-PLAN.md` — Wave 1: `tts_download_manager.py` + endpoints `/api/tts/hardware` + `/api/tts/mode`
- `f-sara-voice-03-PLAN.md` — Wave 2: wiring `tts.py` → tts_engine + iMac deploy + pytest
- `f-sara-voice-04-PLAN.md` — Wave 2: SetupWizard step Sara + `VoiceSaraQuality.tsx` + `VoiceAgentSettings.tsx`
- `f-sara-voice-05-PLAN.md` — Wave 3: `test_tts_adaptive.py` + P95 benchmark + human verify + ROADMAP COMPLETE

**Research**: `.planning/phases/f-sara-voice/f-sara-voice-RESEARCH.md` (from memory/project_qwen3tts_sara.md)
**ROADMAP.md**: aggiornato con F-SARA-VOICE entry ✅
**STATE.md**: aggiornato → fase f-sara-voice PLANNED ✅

---

## AZIONE IMMEDIATA S77

```
/gsd:execute-phase f-sara-voice
```

Wave 1 in parallelo (piani 01 + 02), poi Wave 2 (03 + 04), poi Wave 3 (05 con checkpoint human-verify).

---

## ARCHITETTURA F-SARA-VOICE

### Obiettivo
FluxionTTS Adaptive: voce naturale Sara su PC capaci, fallback Piper su PC datati.
- **Quality**: Qwen3-TTS 0.6B CustomVoice (~1.2GB, streaming, 400-800ms, Apache 2.0)
- **Fast**: Piper Italian `it_IT-paola-medium.onnx` (~50MB bundled, ~50ms, sempre disponibile)
- **P95 target**: < 800ms su Intel i5 2019/8GB RAM

### File da creare/modificare
```
voice-agent/src/tts_engine.py          (nuovo) — TTSEngineSelector, QwenTTSEngine, PiperTTSEngine
voice-agent/src/tts_download_manager.py (nuovo) — download manager + mode persistence
voice-agent/src/tts.py                 (update) — factory redirected to adaptive engine
voice-agent/main.py                    (update) — 3 nuovi endpoints
src/components/setup/SetupWizard.tsx   (update) — step 9 voice quality dialog
src/components/impostazioni/VoiceSaraQuality.tsx (nuovo) — quality selector Impostazioni
src/components/impostazioni/VoiceAgentSettings.tsx (update) — render VoiceSaraQuality
voice-agent/tests/test_tts_adaptive.py (nuovo) — P95 benchmark + unit tests
```

### Constraint Python 3.9
- NO PyTorch a livello modulo (no `import torch` top-level)
- transformers[cpu] OK (usa torch internamente ma graceful fail se non installato)
- QwenTTSEngine degrada silenziosamente a PiperTTSEngine se import fallisce

### UX — Deferred Download
- Wizard step Sara → utente sceglie qualità
- `POST /api/tts/mode` salva preferenza
- Download 1.2GB avviene al **primo avvio di Sara** (non nel wizard)
- Nessuna progress bar nel wizard — chiarito in must_haves plan 04 ✅

---

## PROSSIME FASI (dopo F-SARA-VOICE)
- **EHIWEB SIP**: credenziali in arrivo → `/gsd:plan-phase F15` quando arrivano
- **F17**: Windows build — unblocked → dopo F-SARA-VOICE

---

## CONTINUA CON
```
/clear
/gsd:execute-phase f-sara-voice
```
