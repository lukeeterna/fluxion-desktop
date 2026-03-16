# FLUXION — Handoff Sessione 80 → 81 (2026-03-16)

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
Branch: master | HEAD: 3b69af5
feat(nlu): LLM-based NLU engine replaces 2000 lines of regex (shadow mode)
type-check: 0 errori ✅
NON pushato (iMac offline a fine S80)
```

---

## COMPLETATO SESSIONE 80 (1 commit)

### `3b69af5` — LLM NLU Engine (architettura 2026) ✅
**DECISIONE ARCHITETTURALE FONDAMENTALE**: Migrazione da regex-based NLU (2000 righe) a LLM structured output.

#### Cosa è stato creato:
- `voice-agent/src/nlu/schemas.py` — NLUResult, SaraIntent, Sentiment, JSON schema
- `voice-agent/src/nlu/providers.py` — Multi-provider rotation (Groq, Cerebras, OpenRouter, SambaNova, Together)
- `voice-agent/src/nlu/llm_nlu.py` — Engine 3 livelli (profanity → LLM → template fallback)
- `voice-agent/src/nlu/template_fallback.py` — Fuzzy matching offline via rapidfuzz
- `voice-agent/tests/test_llm_nlu.py` — 34 test tutti PASS
- `voice-agent/src/orchestrator.py` — Shadow mode wired (logga LLM vs regex senza cambiare comportamento)
- 4 CoVe research files in `.claude/cache/agents/`

#### Risultati live test iMac (Groq llama-3.1-8b-instant):
| Test | Risultato | Latenza |
|------|-----------|---------|
| "mi chiamo Franco Decillis" → CORREZIONE cognome | ✅ | 264ms |
| "non voglio cancellare" → RIFIUTO | ✅ | 133ms |
| "taglio per domani alle 15" → PRENOTAZIONE | ✅ | 167ms |
| "spostare a venerdì" → SPOSTAMENTO | ✅ | 149ms |
| "cancella giovedì" → CANCELLAZIONE | ✅ | 146ms |
| "lista d'attesa" → WAITLIST | ✅ | 151ms |
| **Media** | **7/8 OK** | **168ms** |

#### Provider configurati (tutti free, OpenAI-compatible):
1. **Groq** — llama-3.1-8b-instant (GROQ_API_KEY ✅)
2. **OpenRouter** — llama-3.3-70b free (OPENROUTER_API_KEY ✅ aggiunta S80)
3. Cerebras — da configurare (CEREBRAS_API_KEY)
4. SambaNova — da configurare (SAMBANOVA_API_KEY)
5. Together — da configurare (TOGETHER_API_KEY)

---

## ⚠️ PROBLEMI APERTI

### P0: LLM NLU — Shadow → Primary (PROSSIMO STEP)
- Shadow mode attivo: logga LLM vs regex in parallelo
- **TODO S81**: Verificare log shadow su iMac → se LLM > regex → switch a primary
- **TODO S81**: Aggiungere Cerebras API key (Qwen3-32B, fondatore lo vuole)
- **TODO S81**: Dopo switch, rimuovere ~2000 righe regex (italian_regex.py, intent_classifier.py, entity_extractor.py)

### P1: TTS voce "Legacy System"
- La pipeline usa SystemTTS macOS (voce robotica, legge numeri male: "3.000.575")
- Serena/Qwen3-TTS non attiva (richiede Python 3.11 venv)
- Research TTS numeri completata (`.claude/cache/agents/` — agente TTS S80)

### P2: VAD — da testare live con microfono
- Fix silence_window deployato (2.5s→512ms) ma NON testato con microfono reale

### P3: Sara Sales FSM — non ancora wired
- Research completa, dataset pronto
- Dipende da LLM NLU come primary (lo switch semplifica enormemente il wiring)

### P4: F15 VoIP EHIWEB — non ancora wired
- voip.py esiste (1227 righe) — serve integrazione + port forward router

### P5: git push pending
- `3b69af5` non pushato — iMac era offline. Push appena possibile.

---

## AZIONE IMMEDIATA S81

### Priorità 1: Push + Deploy LLM NLU su iMac
```bash
git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
# Aggiungi API keys mancanti:
ssh imac "echo 'CEREBRAS_API_KEY=csk-emt4c8d22cy8d8x9w5f26rtcnk2rnhke3vr99n536t4meepj' >> '/Volumes/MacSSD - Dati/fluxion/voice-agent/.env'"
# Riavvia pipeline → shadow mode attivo con 3 provider (Groq + OpenRouter + Cerebras)
```

### Priorità 2: Switch LLM NLU da shadow a primary
```
# Verificare log [NLU-SHADOW] → confronto regex vs LLM
# Se LLM ≥ regex → switch: LLM NLU diventa L0-L2
# Regex diventa emergency fallback (non eliminato subito)
```

### Priorità 3: Aggiungere Cerebras + Qwen3
```
# Registrare account Cerebras (cloud.cerebras.ai) → CEREBRAS_API_KEY
# Aggiungere a .env iMac
# Modello: qwen3-32b (ottimo per italiano, fondatore lo vuole)
```

### Priorità 4: TTS numeri + Sales FSM
```
# Fix numeri italiani nel TTS (research completata)
# Wire Sara Sales FSM (ora semplificato con LLM NLU)
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 81:
1. Push 3b69af5 + deploy su iMac + restart pipeline
2. Verifica log shadow NLU → switch LLM NLU a primary
3. Aggiungi Cerebras API key (Qwen3-32B)
4. TTS fix numeri italiani
```
