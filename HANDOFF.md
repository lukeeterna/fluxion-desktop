# FLUXION — Handoff Sessione 70 → 71 (2026-03-14)

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
Branch: master | HEAD: 77b7b0a
feat(voice): VAD open-mic continuous listening loop (gold standard 2026)
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1488 PASS / 0 FAIL ✅ (1477+11 nuovi)
```

---

## COMPLETATO SESSIONE 70

### VAD Open-Mic Continuous Listening ✅ DONE (commit 77b7b0a)

Implementato il microfono sempre aperto dopo risposta Sara (gold standard Retell/Vapi 2026).

**Root cause**: Gap architetturale HTTP — frontend non chiamava `startListening()` dopo `playAudioFromHex()`.

#### Modifiche implementate:

| File | Modifica | Task |
|------|----------|------|
| `VoiceAgent.tsx` | Bottone Phone + `runOpenMicLoop()` async | T1 |
| `VoiceAgent.tsx` | TTS suppression via `notifyTtsSpeaking()` | T3 |
| `use-voice-pipeline.ts` | `waitForTurn()` — promise senza fermare MediaStream | T1 |
| `use-voice-pipeline.ts` | `notifyTtsSpeaking(speaking)` — POST /vad/speaking | T3 |
| `use-voice-pipeline.ts` | `UseVADRecorderReturn` interface aggiornata | — |
| `vad_http_handler.py` | `VADSession.is_tts_playing` flag | T2 |
| `vad_http_handler.py` | POST `/api/voice/vad/speaking` + `/vad/speaking` | T2 |
| `vad_http_handler.py` | Echo suppression: early return se TTS attivo | T2 |
| `vad_http_handler.py` | `vad.reset()` dopo end_of_speech | T4 |
| `tests/test_vad_openmicloop.py` | 11 nuovi test open-mic | T5 |

#### Acceptance Criteria verificati:
- ✅ Bottone Phone → loop continuo ascolta → processa → parla → ascolta
- ✅ TTS suppression: `notifyTtsSpeaking(true/false)` + backend `is_tts_playing`
- ✅ `should_exit=True` → loop termina automaticamente
- ✅ Silero hidden state resettato tra turni (vad.reset())
- ✅ 11 nuovi test open-mic: 11/11 PASS su MacBook + iMac
- ✅ 0 regression: 1488 PASS totali (1477 + 11)

---

## PENDING

### F15 VoIP (EHIWEB)
✅ Architettura implementata | ⏳ Credenziali EHIWEB SIP ancora in arrivo
- `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` → da inserire in config.env iMac

### F16 Landing Screenshot
- [ ] Catturare `fx_voice_agent.png` (Sara UI) dall'iMac fisicamente

---

## PROSSIMA SESSIONE S71

> **Priorità**: ROADMAP_REMAINING.md — prossima fase dopo open-mic

### Da fare S71:
1. `ROADMAP_REMAINING.md` → verificare prossima fase
2. Se credenziali EHIWEB arrivate → F15 test SIP end-to-end
3. F16 Landing screenshot (minor — catturare da iMac fisicamente)
4. Eventuali altri gap da ROADMAP

### Promemoria tecnici:
- **Voice pipeline** porta 3002 bound a `127.0.0.1` — accessibile solo da iMac
- **Open-mic**: testare fisicamente su iMac con microfono (bottone Phone in UI)
- **t1_live_test.py**: BASE `http://127.0.0.1:3002` (hardening F14)
- **License server** gestito da LaunchAgent (avvio automatico boot)
- **Cloudflare tunnel** gestito da LaunchAgent `com.fluxion.cloudflared`
