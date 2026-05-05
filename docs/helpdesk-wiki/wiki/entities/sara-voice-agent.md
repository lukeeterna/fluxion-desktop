---
title: "Sara Voice Agent"
type: entity
slug: sara-voice-agent
sources_consumed: []
last_ingest: 2026-05-04
status: stable
related:
  - license-key
  - pricing-tiers
  - network-firewall
  - three-pillars
  - gdpr-compliance
  - win10-installation
verticals: [all]
---

# Sara Voice Agent

> Sara è l'assistente vocale 24/7 di FLUXION (booking telefonico automatizzato). Tier **Pro €897** lifetime. 5-layer RAG, 23 stati FSM, latency target <800ms (attuale ~1330ms tech debt v1.1).

## TL;DR
- Disponibile **solo tier Pro €897** ([[pricing-tiers]]) — Base/trial hanno 30gg trial Sara poi blocco
- Pipeline locale: STT (Whisper.cpp + Groq fallback) → NLU → FSM → TTS (Edge-TTS premium / Piper offline / SystemTTS last resort)
- Porta locale **3002** (loopback only, no inbound) — vedi [[network-firewall]]
- HTTP bridge Tauri su porta **3001**
- 23 stati FSM gestiscono booking, disambiguazione fonetica nomi, waitlist, chiusura graceful

## Prerequisiti
- Tier Pro €897 attivo ([[license-key]])
- Microfono (USB / built-in) — Bluetooth NON ufficialmente supportato (gap docs)
- Connessione internet per Edge-TTS premium e Groq LLM (fallback locale Piper + template NLU se offline)
- ~520MB disco aggiuntivo (PyInstaller bundle voice-agent)

## Architettura tecnica

| Componente | Tecnologia | Note |
|-----------|-----------|------|
| STT | FluxionSTT (Whisper.cpp locale + Groq fallback) | Latency ~200-400ms |
| LLM | Groq API `llama-3.3-70b-versatile` via Proxy CF | Fallback Cerebras → template NLU offline |
| TTS | FluxionTTS 3-tier | Edge-TTS Isabella (~500ms QUALITY) / Piper paola (~50ms FAST) / SystemTTS |
| VAD | FluxionVAD (Silero ONNX) | Voice activity detection |
| FSM | 23 stati `booking_state_machine.py` | 1500+ righe, gestione completa lifecycle |
| RAG | 5-layer in `orchestrator.py` | FAQ + KB + entities + verticale + intent |
| Analytics | FluxionAnalytics (SQLite) | Turn tracking, conversion rate |

## Procedura setup

1. Verifica tier Pro attivo ([[license-key]])
2. Configurazione verticale in app: `voice-agent/docs/CONFIGURATION.md`:
   - `business_name` (es. "Salone Bellezza Roma")
   - `opening_hours` / `closing_hours`
   - `services_mapping` (per macro-verticale, vedi [[verticals-coverage]])
3. Test microfono **dall'iMac fisicamente** (pipeline bound 127.0.0.1)
4. Numero VoIP forwarding configurato (Pro tier include VoIP) — TODO docs UX guide
5. Health check: `curl http://localhost:3002/health` → `{"status":"ok"}`

## Test scenari live

1. **"Gino vs Gigio"** — disambiguazione fonetica (Levenshtein ≥70%)
2. **"Soprannome VIP"** — Gigi → Gigio (nickname canonico)
3. **"Chiusura Graceful"** — WhatsApp + "Grazie, arrivederci!" (stato `ASKING_CLOSE_CONFIRMATION`)
4. **"Flusso Perfetto"** — nuovo cliente, booking, WA, chiusura, analytics
5. **"WAITLIST"** — slot occupato → lista attesa (`PROPOSING_WAITLIST` → `WAITLIST_SAVED`)

## Errori comuni

| Sintomo | Causa | Fix |
|---------|-------|-----|
| Sara non risponde / timeout | Pipeline 3002 non attiva | `cd voice-agent && python main.py` (su iMac via SSH se architettura split MacBook/iMac) |
| Latency >2s | Groq fallback rate alto / Edge-TTS network slow | Switch tier TTS a Piper offline temporaneo. Verifica health Groq API. |
| Microfono non rilevato | Permessi OS / device USB scollegato | macOS: System Settings → Privacy → Microphone. Bluetooth pairing NON ufficialmente supportato. |
| Intent classificato male (es. "disdire" → INFO) | Pattern NLU coverage gap | Reference: `voice-agent/docs/TROUBLESHOOTING.md` § "Low Intent Accuracy". Tech debt FAQ expansion. |
| TTS voce robotica | Fallback SystemTTS attivato (Edge-TTS + Piper falliti) | Verifica internet per Edge-TTS. Piper ONNX integrità file. |
| Sara non parla italiano | Voice config errato | Reset config voice: `curl -X POST http://localhost:3002/api/voice/reset` |
| Trial Sara scaduto su tier Base | Sara è Pro-only feature, Base ha solo 30gg trial Sara | Upgrade tier Pro €897 ([[pricing-tiers]]) o accetta blocco Sara (CRM/calendario continuano). |

## Endpoint test

```bash
# Health
curl http://localhost:3002/health

# Process voice (text input simulato)
curl -X POST http://localhost:3002/api/voice/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Buongiorno, sono Marco Rossi"}'

# Reset session
curl -X POST http://localhost:3002/api/voice/reset
```

> Tutti endpoint loopback only (127.0.0.1). [[network-firewall]] per dettagli.

## Tech debt aperti (v1.1)
- **Latency Optimizer** — attuale ~1330ms vs target <800ms
- **Streaming LLM** — risposta token-by-token per percezione velocità
- **Test Live Audio** — validation completa con microfono reale
- **Bluetooth mic support** — non ufficialmente supportato, gap docs

## Cross-references
- [[license-key]] — Sara permanente solo tier Pro
- [[pricing-tiers]] — Pro €897 vs Base €497 differenze
- [[network-firewall]] — porta 3002 loopback, Groq API outbound
- [[three-pillars]] — Sara è core di pillar "Comunicazione"

## Sources
- `voice-agent/README.md` — quick start, Docker setup
- `voice-agent/docs/CONFIGURATION.md` — verticale config
- `voice-agent/docs/API.md` — HTTP endpoint spec
- `voice-agent/docs/TROUBLESHOOTING.md` — diagnosi latency/intent
- `.claude/rules/voice-agent.md`, `.claude/rules/voice-agent-details.md`
