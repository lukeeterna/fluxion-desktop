# FLUXION — Handoff Sessione 83 → 84 (2026-03-17)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> **SUPPORTO POST-VENDITA = ZERO MANUALE. Sara fa tutto.**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: [da committare — cleanup S83]
Push: pendente
iMac: sincronizzato manualmente (scp) ✅
type-check: 0 errori ✅
test: 1905 PASS / 4 FAIL (pre-esistenti holiday+vad) ✅
```

---

## COMPLETATO SESSIONE 83

### Cleanup regex legacy — -3085 righe ✅
**Dead code eliminato:**
- `nlu/italian_nlu.py` (572 righe) — spaCy/UmBERTo NLU mai usato in produzione (deps non installate)
- `pipeline.py` (1287 righe) — vecchio orchestrator, mai importato
- `booking_orchestrator.py` (516 righe) — mai importato in produzione
- `test_booking_e2e_complete.py` (567 righe) — test morto, già ignorato in CI
- Rimossi `HAS_ADVANCED_NLU`, `self.advanced_nlu`, blocco L0b, param `use_advanced_nlu`

**LLM NLU wired al 100% dei code paths:**
- Cancel/reschedule (L2.5) e FAQ (L3) ora usano `_llm_nlu_result` quando disponibile
- Prima queste 2 paths ignoravano LLM NLU e usavano solo regex

**Bug fix: reset cancel/reschedule state:**
- `_pending_cancel` / `_pending_reschedule` sopravvivevano tra sessioni → risposte spurie
- Fix: `reset_handler` ora chiama `_reset_cancel_reschedule_state()`

### Test live su iMac ✅
- T1: Cortesia (Buongiorno) → saluto Sara completo ✅
- T2: Booking "taglio" → waiting_name (L2) ✅
- T3: Nome "Gianluca Di Stasi" → registering_phone ✅
- T4: Cancellazione → cancel_need_name ✅
- T5: Sales "Quanto costa?" → qualifying_vertical ✅
- T6: Reset non lascia più stato cancel stale ✅

---

## ⚠️ PROBLEMI APERTI

### P1: IP iMac — DHCP reservation da aggiornare
- iMac ora su `192.168.1.2` (MAC `a8:20:66:4e:0e:2d`)
- SSH config aggiornato a .2 ✅
- TODO: aggiornare DHCP reservation sul router per fissare .2

### P2: TTS voce "Serena" — NON WIRED
- `tts_engine.py` ESISTE con QwenTTSEngine + PiperTTSEngine + TTSEngineSelector
- `tts_download_manager.py` ESISTE per download modello
- Endpoint API `/api/tts/hardware`, `/api/tts/mode` ESISTONO in main.py
- **MA** orchestrator usa ancora vecchio `get_tts()` da `tts.py` (SystemTTS/Piper)
- Voce approvata: **Serena** (Qwen3-TTS 0.6B, approvata S76)
- Constraint: Qwen3-TTS richiede `transformers` + possibilmente torch
- **PROSSIMA SESSIONE**: deep research TTS 2026 → wire Serena nell'orchestrator

### P3: VAD — da testare live con microfono
- Fix silence_window deployato (2.5s→512ms) ma NON testato con microfono reale

### P4: F15 VoIP EHIWEB — non ancora wired
- voip.py esiste (1227 righe) — serve integrazione + port forward router

---

## AZIONE IMMEDIATA S84

### Priorità 1: Wire FluxionTTS Adaptive (Serena/Qwen3-TTS)
- Deep research CoVe 2026: stato dell'arte TTS italiano 2026 (Qwen3-TTS vs Kokoro vs F5-TTS vs XTTS-v2 vs cloud)
- Wire `tts_engine.py` nell'orchestrator (sostituire `get_tts()`)
- Test voce Serena su iMac
- Requisiti: Python 3.9 compatible, lazy load, fallback Piper

### Priorità 2: Sales → WhatsApp integration (routing inbound)
- Sales FSM funziona via API → collegare a WhatsApp inbound
- Routing: numero sconosciuto + messaggio generico → sales mode
- Numero conosciuto → booking mode (esistente)

### Priorità 3: Test VAD live con microfono su iMac

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 84:
1. Deep research TTS 2026 (Qwen3-TTS vs alternative) → wire voce Serena nell'orchestrator
2. Sales → WhatsApp integration (routing inbound)
3. Test VAD live con microfono
```
