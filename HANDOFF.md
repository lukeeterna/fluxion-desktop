# FLUXION — Handoff Sessione 135 → 136 (2026-04-08)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 135

### 1. Fix VoIP Live (7 fix)
- **Multi-service family disambiguation** (entity_extractor.py) — taglio_* family detection
- **NameCorrector DB** (orchestrator.py) — usa _find_db_path() → Tauri DB reale
- **NLU Groq-only 3.5s** (providers.py) — OpenRouter rimosso, orchestrator 4s
- **STT tiny + 5s timeout** (stt.py) — FasterWhisper tiny default, fallback limitato
- **Anti-echo 0.6s** (voip_pjsua2.py) — double drain + buffer clear
- **Guardrail vertical override** (orchestrator.py) — _vertical_explicitly_set flag
- **Max 3 services** (booking_state_machine.py) — limit on extracted services

### 2. Massive E2E Test Suite
- **101 test** in `tests/e2e/test_sara_massive.py` — 8 sezioni
- Copre: 6 verticali, 23 FSM states, 5 disambiguazione, cancel/reschedule, VAD endpoints
- Risultato finale: **85 OK / 16 WARN / 0 FAIL**

### 3. Audio E2E Test (VoIP-equivalent)
- `tests/e2e/test_voip_audio_e2e.py` — genera WAV con Edge-TTS, invia come audio_hex
- Testa full pipeline STT→NLU→FSM→TTS senza telefono
- 7 scenari audio: **7 OK / 2 WARN / 0 FAIL**

### 4. Sara Personality — L'ANIMA
- **35 template riscritti** — da burocratici a caldi, italiani, frizzanti
- **Micro-reazioni** (8 categorie, 30+ frasi): "Perfetto!", "Ci mancherebbe!", "Ottima scelta!"
- **Response variants** espansi: goodbye, slot_unavailable, ask_name, ask_date
- **System prompt Groq** completamente riscritto con personalità Sara:
  - 7 sector personality matrix (salone/auto/medical/palestra/beauty/wellness/professionale)
  - Identità: calda, frizzante, simpatica, empatica, accogliente
  - Anti-pattern eliminati: "Come posso aiutarla", "per cortesia", Lei default
  - Autenticità italiana: "Ci mancherebbe!", "Un attimino...", "Ecco fatto!"
- Deep research: Pi, Hume, Sierra, Retell, Italian cultural patterns

---

## TEST RESULTS SESSIONE 135

### Massive Suite (101 test)
| Sezione | OK | WARN | FAIL |
|---------|-----|------|------|
| Booking Flow (FSM) | 12 | 1 | 0 |
| 6 Verticals (services+FAQ+guard) | 33 | 10 | 0 |
| Disambiguation (5 types) | 3 | 2 | 0 |
| Cancel/Reschedule | 3 | 0 | 0 |
| Multi-Service + Edge | 7 | 1 | 0 |
| VAD Endpoints (9 test) | 9 | 0 | 0 |
| Error Recovery (8 test) | 8 | 0 | 0 |
| Timing | 2 | 2 | 0 |
| **TOTALE** | **85** | **16** | **0** |

### Audio Suite (9 test)
```
OK  STT: "Marco Rossi" trascritto perfettamente (2669ms)
OK  Disambiguazione taglio → chiede tipo
OK  Multi-service → accettati senza 6 varianti
OK  Booking flow 3 step (1 WARN: name disamb OK)
OK  NLU timing 2098ms
OK  TTS audio 552KB
OK  Audio/text consistency
```

---

## WARN NOTI (non bloccanti)
1. **Guardrail cross-vertical**: "Vorrei un taglio di capelli" non bloccato su auto/medical (pattern non multi-word)
2. **DB servizi salone-only**: FAQ auto/medical rispondono con prezzi salone
3. **Timing greeting**: 3-10s su prima richiesta (cold start LLM)
4. **FSM context loss**: step sequenziali nel test perdono contesto

---

## STATO GIT
```
Branch: master | HEAD: S135 — Sara personality + 7 VoIP fixes + massive tests
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10e: Sara Bug Fixes       DONE (S127, S134, S135)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — prompt pronti, clip da generare Kling free
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 136.
PROSSIMI PASSI:
1. Sprint 3 Video: generare clip Kling free (web UI manuale, 30 crediti/clip)
2. Sprint 4 Landing: embed video + hero screenshots
3. Miglioramenti Sara personalità: varianti per verticale nei template FSM
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
```
