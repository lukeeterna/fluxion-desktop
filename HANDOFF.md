# FLUXION — Handoff Sessione 60 → 61 (2026-03-12)

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
Branch: master | HEAD: 9194458
feat(voice): Sara Sprint 3 — GAP-B2/B6/A5
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1371 PASS / 0 FAIL ✅ | cargo check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 59 — F15 VoIP MVP

### P1.0 Impostazioni Redesign
**SKIP** — già completato in sessione 47. Confermato da codice + ROADMAP `✅ DONE (s47)`.
Sidebar Linear-style, badge stati, useImpostazioniStatus, QuickSetupBanner: tutti operativi.

### F15 VoIP Integration (commit `bf042cc`)

**Architettura**: `voip.py` (1227 righe SIP/RTP stdlib) era già implementato ma non integrato.
Research (Agente B gap analysis) ha identificato 7 gap critici → tutti chiusi in questa sessione.

| Gap | File | Fix | Stato |
|-----|------|-----|-------|
| GAP-1 | main.py | VoIPManager wiring con guard VOIP_SIP_USER | ✅ |
| GAP-2 | orchestrator.py | `greet()` + `process_audio()` VoIP interface | ✅ |
| GAP-3 | config.env (iMac) | `VOIP_LOCAL_IP=192.168.1.12` (da impostare) | ⏳ |
| GAP-4 | VoipSettings.tsx | UI form SIP + stato live | ✅ |
| GAP-5 | migration 032 | sip_username/password/server/port/voip_attivo | ✅ |
| GAP-6 | voice_calls.rs | VoiceAgentConfig + get_voip_status command | ✅ |
| GAP-7 | main.py | /api/voice/voip/status + /hangup endpoints | ✅ |
| GAP-8 | voip.py | WAV RIFF header strip in _send_audio() | ✅ |

**Test**: pytest 1334 PASS / 0 FAIL ✅ | cargo check: 0 errori ✅ | type-check: 0 errori ✅

### Cosa resta per F15 completamento (S60):
⚠️  **EHIWEB IN ATTESA** — email partnership inviata s55, ancora nessuna risposta (2026-03-12)
1. **Credenziali EHIWEB** — quando arrivano: sip_username=numero, sip_password, server=sip.ehiweb.it
2. **Config.env iMac** — aggiungere `VOIP_SIP_USER`, `VOIP_SIP_PASSWORD`, `VOIP_LOCAL_IP=192.168.1.12`
3. **Port forwarding router** — porta 5060 UDP → 192.168.1.12 (necessario per SIP inbound)
4. **Disable SIP ALG sul router** — se presente (corrompe pacchetti SIP)
5. **Test SIP**: `curl http://192.168.1.12:3002/api/voice/voip/status` → `{"registered": true}`
6. **Test chiamata end-to-end** — latenza P95 < 2s percepiti

---

## COMPLETATO SESSIONE 60 — Sara Enterprise Sprint 3

### GAP-B2 + GAP-B6 (entity_extractor.py — commit `9194458`)
- **GAP-B2**: `extract_date()` ora riconosce:
  - "il mese prossimo" / "mese prossimo" / "prossimo mese" → `datetime(year, month+1, 1)` (anchor primo mese)
  - "fra/tra un/N mese/mesi" → +N*30 giorni (offset semantics, distinto da anchor)
  - Estesi `fra_pattern` e `fra_word_pattern` con `mes[ei]` nel gruppo unità
- **GAP-B6**: handler weekend inserito PRIMA di DAYS_IT (intercetta "sabato o domenica"):
  - `_next_weekend_re` (prossimo weekend force_next) checkata PRIMA di `_weekend_re`
  - "fine settimana/weekend" da sabato/domenica → sabato prossimo settimana
  - Helper `_next_saturday(ref, force_next)` inline nella funzione
- 22 nuovi test in `TestDateRelativeMonthAndWeekend`

### GAP-A5 (booking_state_machine.py — commit `9194458`)
- **Fix A**: `_check_interruption()` — `PRE_IDENTIFICATION_STATES = {WAITING_NAME, WAITING_SURNAME}` → reset→IDLE invece di WAITING_SERVICE
- **Fix B**: `_handle_waiting_surname()` controlla `is_rifiuto(text)` all'INIZIO (prima di `_extract_surname_from_text`) per evitare che "no grazie" venga parsato come cognome "No"
- **Fix B (nome)**: stesso check nel fallback di `_handle_waiting_name()`
- Import `is_rifiuto` aggiunto al blocco try/except italian_regex
- 15 nuovi test in `TestCancelPreIdentification` (incl. regression guard mid-booking→WAITING_SERVICE)

**pytest iMac S60**: 1371 PASS / 0 FAIL ✅

---

## PROSSIMA SESSIONE S61

> **Skill**: `fluxion-voice-agent` (F15 se EHIWEB arrivato, poi Sprint 3 gap rimanenti)
> **NOTA**: F03 Latency e F04 Schede già ✅ in ROADMAP_REMAINING.md

### Priorità S61 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end (config.env + port forward + curl test)
2. **Sara Enterprise Sprint 3 gap rimanenti** (da CoVe audit):
   - GAP-D3: nessuna colonna `fsm_state` nei turn log analytics → impossibile analizzare dove si rompono le conversazioni
   - GAP-C1: date "13/03" non preprocessate in TTS → "tredici barra tre" (fix in tts.py)
   - GAP-H2: Groq system prompt senza orari/operatori/prezzi
3. **Telnyx fallback** (opzionale): se EHIWEB non risponde entro 2 settimane

---

## Riavvio pipeline iMac (con VoIP se configurato):
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
