# FLUXION — Handoff Sessione 74 → 75 (2026-03-15)

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
Branch: master | HEAD: 02d90f6
docs(audioworklet-01): complete AudioWorklet migration plan
type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1488 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 73-74

### audioworklet-vad-fix — FASE COMPLETA ✅

**Wave 1** (S73):
- `public/audio-processor.worklet.js` creato (AudioChunkProcessor, 4096-sample buffering, `.slice()`)
- `useVADRecorder` migrato: `AudioWorkletNode`, `port.onmessage`, `port.close()` in tutti i 3 cleanup path
- `ScriptProcessorNode` + GainNode silencer rimossi
- `npm run type-check` → 0 errori ✅
- Commits: `f4db853`, `fe11f65`, `02d90f6`

**Wave 2** (S74 checkpoint):
- git push + iMac sync + Tauri build: ✅
- `audio-processor.worklet.js` embedded nel bundle: ✅
- **Phone button (open-mic) APPROVATO fisicamente su iMac** ✅
  - Audio level si muove mentre si parla ✅
  - Sara risponde dopo end_of_speech ✅
  - Loop open-mic continua ✅
  - Shutdown pulito su secondo click ✅
- Verificati: `audioworklet-02-SUMMARY.md` + `audioworklet-VERIFICATION.md` ✅
- STATE.md aggiornato: fase COMPLETA ✅

---

## PROSSIMA SESSIONE S75 — PRIORITÀ

### P1 — F-SARA-VOICE (PROSSIMA FASE)

```
/gsd:plan-phase F-SARA-VOICE
```

**Obiettivo**: FluxionTTS Adaptive — sostituire Piper con Qwen3-TTS come motore primario Sara
- Quality mode: Qwen3-TTS 0.6B CustomVoice (download ~1.2GB, streaming, ~400-800ms)
- Fast mode: Piper Italian (50MB bundled, ~50ms, fallback garantito)
- Hardware detection automatica al primo avvio
- Voice clone Sara con sara-reference-voice.wav
- Research completo: `memory/project_qwen3tts_sara.md`

**Prerequisiti soddisfatti**: AudioWorklet ✅ (Phone button funziona)
**Prerequisiti pendenti**: EHIWEB SIP non richiesto per questa fase

### P2 — F17 Distribuzione Windows (dopo F-SARA-VOICE)
```
/gsd:plan-phase F17
```
- Prerequisito: VAD Open-Mic funzionante ✅ (ora soddisfatto)
- Build Windows via GitHub Actions cross-compile
- Installer .msi / NSIS + auto-update Tauri

### P3 — F15 VoIP (bloccante su credenziali esterne)
- Quando arrivano credenziali EHIWEB: `/gsd:plan-phase F15`
- Inserire `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` in config.env iMac

---

## PROMEMORIA TECNICI
- **Fluxion.app build**: `/Volumes/MacSSD - Dati/FLUXION/src-tauri/target/release/bundle/macos/Fluxion.app`
- **MAI aprire /Applications** — usare sempre quella della build directory
- **AudioWorklet addModule path**: `/audio-processor.worklet.js` (assoluto da `public/`)
- **Pipeline iMac riavvio**: `ssh imac "kill $(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && [python] main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"`
- **Qwen3-TTS**: no GGUF disponibile (mar 2026), no MLX su Intel — usare PyTorch CPU con streaming
- **Test microfono**: sempre fisicamente su iMac (pipeline bound 127.0.0.1)
