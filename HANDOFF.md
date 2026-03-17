# FLUXION — Handoff Sessione 81 → 82 (2026-03-17)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> **SUPPORTO POST-VENDITA = ZERO MANUALE. Sara fa tutto.**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: [post-commit S81]
Push S80: 350e287 pushato ✅
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 81

### Commit 1: LLM NLU shadow → primary ✅
**CAMBIO ARCHITETTURALE**: LLM NLU ora è il motore PRIMARIO di Sara.
- `orchestrator.py`: LLM NLU task async (lanciato in parallelo con L0) → awaited a L1
- Adapter `_nlu_to_intent_result()`: mappa SaraIntent → IntentCategory per backward compat
- Regex diventa fallback se LLM confidence < 0.5 o timeout 2s
- Riusato a L2 (booking SM) — zero chiamate regex duplicate
- Shadow logging rimosso → replaced con PRIMARY logging
- 34 test NLU PASS ✅

### Commit 2: TTS numeri italiani ✅
- `tts.py`: `_number_to_italian()` — conversione 0..999M in italiano parlato
- `_ITALIAN_NUMBER_RE` per "3.000", "1.500.000" (dot-separator)
- `_PLAIN_NUMBER_RE` per "3000" (plain large integers)
- Integrato in `preprocess_for_tts()` (dopo date, prima di phone)
- "3.000 euro" → "tremila euro", "1.500.000" → "un milione cinquecentomila"
- 14 nuovi test, 28 totali TTS PASS ✅

---

## ⚠️ PROBLEMI APERTI

### P0: Deploy su iMac (BLOCCATO — iMac offline)
- Push S80 fatto ✅, commit S81 da pushare
- **TODO S82**: `git push` + `git pull` su iMac + restart pipeline
- **TODO S82**: Aggiungere CEREBRAS_API_KEY su iMac .env
- **TODO S82**: Verificare log `[NLU-LLM] PRIMARY` su iMac dopo deploy

### P1: TTS voce "Legacy System"
- Numeri italiani ORA FIXATI ✅ (3.000 → tremila)
- SystemTTS macOS ancora voce robotica — Serena/Qwen3-TTS richiede Python 3.11 venv
- TODO: attivare Piper o Qwen3-TTS su iMac

### P2: VAD — da testare live con microfono
- Fix silence_window deployato (2.5s→512ms) ma NON testato con microfono reale

### P3: Sara Sales FSM — non ancora wired
- Research completa, dataset pronto
- Ora semplificato con LLM NLU come primary ✅

### P4: F15 VoIP EHIWEB — non ancora wired
- voip.py esiste (1227 righe) — serve integrazione + port forward router

### P5: Regex cleanup (post-verifica LLM primary su iMac)
- `italian_regex.py` (1350 righe), `intent_classifier.py`, `entity_extractor.py`
- Da rimuovere/ridurre DOPO verifica che LLM primary funziona in produzione

---

## AZIONE IMMEDIATA S82

### Priorità 1: Push + Deploy su iMac
```bash
git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
ssh imac "echo 'CEREBRAS_API_KEY=csk-emt4c8d22cy8d8x9w5f26rtcnk2rnhke3vr99n536t4meepj' >> '/Volumes/MacSSD - Dati/fluxion/voice-agent/.env'"
# Restart pipeline
ssh imac "kill \$(lsof -ti:3002); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Priorità 2: Verifica LLM NLU primary su iMac
```bash
# Test endpoint
curl -s -X POST http://192.168.1.2:3002/api/voice/process -H "Content-Type: application/json" -d '{"text":"Buongiorno, vorrei prenotare un taglio per domani alle 15"}'
# Check logs per [NLU-LLM] PRIMARY
ssh imac "tail -50 /tmp/voice-pipeline.log | grep NLU-LLM"
```

### Priorità 3: Sara Sales FSM wiring
- Wire dataset `sales_knowledge_base.json` nella FSM
- Semplificato ora che LLM NLU è primary

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 82:
1. Push + deploy su iMac + CEREBRAS_API_KEY + restart pipeline
2. Verifica log [NLU-LLM] PRIMARY → conferma che LLM funziona in produzione
3. Wire Sara Sales FSM (dataset pronto, LLM NLU semplifica)
4. Cleanup regex legacy (post-verifica)
```
