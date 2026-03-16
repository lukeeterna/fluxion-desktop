# FLUXION — Handoff Sessione 78 → 79 (2026-03-16)

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
Branch: master | HEAD: eba6bb5
feat(f18): add Sara Sales dataset + lead generator tool
type-check: 0 errori ✅
⚠️ Sessione 78: MOLTI file Python modificati su iMac (non committati) — SCP diretto
⚠️ File TypeScript modificati su MacBook (non committati): VoiceAgent.tsx, use-voice-pipeline.ts
```

---

## COMPLETATO SESSIONE 78

### 1. Commit S77 files ✅
- `eba6bb5` — Sara Sales dataset + lead generator (sales_knowledge_base.json, support_knowledge_base.json, wa_first_contact_templates.json, lead_generator.py)

### 2. Credenziali EHIWEB VoIP MEMORIZZATE ✅
- Numero: 0972536918 | Server: sip.vivavox.it:5060 | Codec: G729.A
- Salvato in `memory/reference_ehiweb_voip.md`
- VoIP F15 NON ancora wired — serve `/gsd:plan-phase F15`

### 3. VAD BUG CRITICO FIXATO ✅
- **Silero ONNX v5 incompatibile** con onnxruntime 1.19.2 su iMac Intel
  - LSTM shape mismatch: `{1,1,1,128,3}` vs atteso `{1,-1,128}`
  - prob=0.001 SEMPRE (anche con audio reale) — VAD completamente rotto
- **Fix**: Switchato a **webrtcvad** (92% speech detection vs 0% Silero)
  - `ten_vad_integration.py` → `start()` ora preferisce webrtcvad
- **TODO S79**: Risolvere Silero ONNX per long-term (aggiornare onnxruntime o modello)

### 4. Doppio saluto FIXATO ✅
- `VoiceAgent.tsx` — `greetingFiredRef` previene doppio greet da useEffect + handleStart

### 5. Logging conversazione AGGIUNTO ✅
- `main.py` — log strutturato: `USER: '...' → SARA: '...' [intent, layer, fsm]`

### 6. 4 Bug booking FSM FIXATI ✅ (subagente, 1620 test PASS)
- **BUG 1**: Multi-servizio "barba e capelli" → ora estrae entrambi
- **BUG 2**: "Quando è possibile" → ora propone slot disponibili
- **BUG 3**: "trattamenti che ti ho chiesto" → no più false positive
- **BUG 4**: Cortesia durante booking → re-prompt dopo "Prego!"

### 7. VAD timing ottimizzato
- `silence_duration_ms`: 500 → 350ms
- `prefix_padding_ms`: 200 → 150ms
- `_webrtc_probs maxlen`: 30 → 8 (fix "sticky SPEAKING")

### 8. Research Sara Sales FSM completata ✅
- `.claude/cache/agents/sara-sales-fsm-wiring-research.md` — architettura SalesStateMachine
- `.claude/cache/agents/sales-chatbot-benchmark-research.md` — 484 righe, 5 pattern FSM, A.C.R.E. framework

---

## ⚠️ PROBLEMI APERTI S78

### P1: VAD webrtcvad "sticky" SPEAKING
- webrtcvad resta in SPEAKING troppo a lungo (40 sec di "parlato" → STT: "Grazie")
- Causa: `_webrtc_probs` deque troppo grande (30 → ridotto a 8)
- **Fix parziale deployato** — DA TESTARE in S79

### P2: Intent classification errata
- "tagliare i capelli non voglio cancellare" → interpretato come CANCELLAZIONE
- L'intent classifier prende "cancellare" e ignora "non voglio"
- **TODO S79**: Fix negazione nell'intent classifier

### P3: TTS voce "Legacy System"
- La pipeline usa SystemTTS macOS (voce robotica, legge numeri male: "3.000.575")
- Serena/Qwen3-TTS non attiva (richiede Python 3.11 venv)
- **TODO**: Attivare Serena o piper-tts come fallback

### P4: File non committati
- 6+ file Python modificati via SCP su iMac (non in git)
- 2 file TypeScript modificati su MacBook (non committati)
- **S79 PRIMO STEP**: git add + commit tutti i fix

---

## AZIONE IMMEDIATA S79

### Priorità 1: Commit + test VAD fix
```bash
# 1. Commit tutti i fix S78
git add -A  # review prima
git commit -m "fix(voice): switch to webrtcvad + fix 4 booking FSM bugs + double greeting"

# 2. Test VAD su iMac — la conversazione deve essere fluida
# - Turni < 3 secondi
# - Sara capisce "barba e capelli" come 2 servizi
# - "Quando è possibile" → propone slot

# 3. Fix intent negazione ("non voglio cancellare")
```

### Priorità 2: Wire Sara Sales FSM
```
# Research completa in .claude/cache/agents/
# Creare: sales_state_machine.py + sales_kb_loader.py
# Nuovi endpoint: /api/sales/process
```

### Priorità 3: F15 VoIP EHIWEB
```
/gsd:plan-phase F15
# Credenziali pronte — wire voip.py + port forward router
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 79:
1. Committa TUTTI i fix S78 (VAD webrtcvad, booking FSM, doppio saluto, logging)
2. Testa VAD su iMac — verifica conversazione fluida
3. Fix intent negazione ("non voglio cancellare" ≠ cancellazione)
4. Wire Sara Sales FSM (research completa, implementare)
```
