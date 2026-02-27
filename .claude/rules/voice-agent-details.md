# Voice Agent Sara — Dettagli Tecnici

## Stack Tecnologico
| Componente | Tecnologia |
|-----------|-----------|
| STT | FluxionSTT (Whisper.cpp locale + Groq fallback) |
| LLM | Groq API llama-3.3-70b-versatile |
| TTS | FluxionTTS (Piper Italian) |
| VAD | FluxionVAD (Silero ONNX) |
| FSM | 23 stati, 1500+ righe |
| Analytics | FluxionAnalytics (SQLite) |

## Test Live Scenari (da fare su iMac)
1. **"Gino vs Gigio"** — disambiguazione fonetica (Levenshtein ≥70%)
2. **"Soprannome VIP"** — Gigi → Gigio (nickname canonico)
3. **"Chiusura Graceful"** — WhatsApp + "Grazie, arrivederci!" (ASKING_CLOSE_CONFIRMATION)
4. **"Flusso Perfetto"** — nuovo cliente, booking, WA, chiusura, analytics
5. **"WAITLIST"** — slot occupato → lista attesa (PROPOSING_WAITLIST → WAITLIST_SAVED)

## Endpoint Test
```bash
curl http://192.168.1.2:3002/health
curl -X POST http://192.168.1.2:3002/api/voice/process -H "Content-Type: application/json" -d '{"text":"Buongiorno, sono Marco Rossi"}'
curl -X POST http://192.168.1.2:3002/api/voice/reset
```

## CoVe Status (2026-02-12) — tutto ✅ tranne:
- ⚠️ Latency Optimizer (TODO v1.1, attuale ~1330ms vs target <800ms)
- ⚠️ Streaming LLM (TODO v1.1)
- 🔴 **Test Live Audio** — ancora da fare

## File Chiave
```
voice-agent/main.py                         # HTTP server porta 3002
voice-agent/src/booking_state_machine.py    # 23 stati FSM
voice-agent/src/orchestrator.py             # 4-layer RAG
voice-agent/src/analytics.py               # Turn tracking
voice-agent/src/disambiguation_handler.py  # Phonetic matching
voice-agent/t1_live_test.py               # Test live T1
```
