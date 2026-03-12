# FLUXION — Handoff Sessione 61 → 62 (2026-03-12)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 6ff6778
feat(voice): Sara Sprint 3 — GAP-D3/C1/H2
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1385 PASS / 0 FAIL ✅ | cargo check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 61 — Sara Enterprise Sprint 3 (GAP-D3/C1/H2)

### GAP-D3 — fsm_state nei turn log analytics

**Problema**: impossibile analizzare dove si rompono le conversazioni senza sapere lo stato FSM al momento del turno.

**Fix** (commit `6ff6778`):
- `session_manager.py`: `SessionTurn.fsm_state: Optional[str] = None` + `anonymize()` preserva il campo
- `session_manager.py`: `add_turn()` accetta `fsm_state: Optional[str] = None`
- `orchestrator.py`: passa `self.booking_sm.context.state.value` ad ogni turn log

**Uso analitico**: ogni `SessionTurn.to_dict()` include ora `fsm_state` → facilita debug "dove si rompe la conversazione" su export JSON.

### GAP-C1 — date TTS "13/03" → "tredici marzo"

**Stato**: il fix era già implementato in `tts.py`:
- `preprocess_for_tts()` con `_DATE_SHORT_RE` già converte correttamente
- Tutti i path TTS passano per `TTSCache.synthesize()` che chiama il preprocessing

**Fix** (commit `6ff6778`):
- Aggiunto `test_tts_preprocessing.py` (12 test): tutti i mesi, full date, sentence context, phone coexistence, edge cases invalidi
- Confermato funzionante su MacBook

### GAP-H2 — Groq system prompt con orari/servizi/operatori

**Problema**: Sara inventava informazioni quando le si chiedeva "quanto costa il taglio?" o "siete aperti sabato?".

**Fix** (commit `6ff6778`):
- Aggiunto `_load_business_context()`: query SQLite asincrona in `start_session()`:
  - `impostazioni` → orario_apertura, orario_chiusura, giorni_lavorativi
  - `servizi WHERE attivo=1` → nome, prezzo, durata_minuti (max 15)
  - `operatori WHERE attivo=1` → nome, cognome, specializzazioni, descrizione_positiva (max 10)
- `self._business_hours`, `self._business_services`, `self._business_operators` popolati async
- `_build_llm_context()` include sezioni condizionali (solo se dati disponibili, no crash se DB vuoto)
- Regola aggiornata: "NON inventare — usa SOLO le informazioni qui sopra"

**pytest iMac S61**: 1385 PASS / 0 FAIL ✅ (+14 nuovi test)

---

## F15 VoIP — Stato Invariato

⚠️ **EHIWEB IN ATTESA** — email inviata s55, ancora nessuna risposta (2026-03-12)

Quando arrivano le credenziali:
1. `config.env iMac` → `VOIP_SIP_USER`, `VOIP_SIP_PASSWORD`, `VOIP_LOCAL_IP=192.168.1.12`
2. Port forward router: 5060 UDP → 192.168.1.12
3. Test: `curl http://192.168.1.12:3002/api/voice/voip/status` → `{"registered": true}`
4. Test chiamata end-to-end — latenza P95 < 2s

---

## PROSSIMA SESSIONE S62

> **Skill**: `fluxion-voice-agent` (F15 se EHIWEB arrivato) o `fluxion-workflow` (F07 LemonSqueezy)
> **NOTA**: Sprint 3 completato. Tutti i 6 gap (B2/B6/A5/D3/C1/H2) chiusi.

### Priorità S62 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end
2. **F07 LemonSqueezy** → webhook attivazione licenza Ed25519 + in-app upgrade
3. **Sara Sprint 4** → fare audit gap con subagenti CoVe 2026 per nuovi gap da chiudere

---

## Riavvio pipeline iMac (con VoIP se configurato):
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
