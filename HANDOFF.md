# FLUXION — Handoff Sessione 121 → 122 (2026-03-30)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"Capire cosa ho → capire cosa è possibile → definire insieme cosa fare. MAI codice come secondo step."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 121

### VoIP pjsua2 — FUNZIONANTE END-TO-END
6 commit, da crash totale a conversazione bidirezionale completa:

1. **fix: MediaFormatAudio.init()** (3029889) — createPort assertion crash risolto usando `fmt.init(formatId, ...)` che inizializza type + detail_type correttamente
2. **fix: main event loop** (0ec25ed) — greeting funzionava ma process_audio crashava "Event loop is closed". Fix: `asyncio.run_coroutine_threadsafe()` sul loop principale invece di `asyncio.new_event_loop()` in thread
3. **fix: VAD audio buffer** (2dcfc9f) — speech frames venivano consumate dal VAD e perse. Fix: buffer `speech_audio` separato + anti-echo (mute RX durante TTS playback)
4. **fix: OMP libiomp5** (4351b55) — crash al 4° turno per doppio caricamento libiomp5.dylib. Fix: `KMP_DUPLICATE_LIB_OK=TRUE`
5. **fix: tx_queue size** (3664cf3) — greeting troncato a metà. Queue da 500→3000 frame (10s→60s)

### Risultato finale test chiamata reale
```
✅ SIP REGISTER 200 OK su EHIWEB
✅ Chiamata in ingresso ricevuta e risposta automaticamente
✅ Greeting Sara completo (voce Isabella EdgeTTS)
✅ STT Groq funzionante (trascrizione corretta)
✅ NLU + FSM processano e rispondono
✅ TTS risposte inviate al chiamante (audio bidirezionale)
✅ Anti-echo attivo (Sara non riprocessa la propria voce)
✅ Nessun crash durante la conversazione
```

### BUG RIMASTO: FSM perde contesto numero telefono
La **linea VoIP è perfetta**. Il problema è nella booking_state_machine:
- Sara chiede "Mi dà un numero di telefono?" → cliente dice "Sì" → Sara "Bene!" → ma poi NON aspetta il numero
- Quando cliente detta il numero ("331 49 83 901"), Sara non lo riconosce come telefono e richiede il nome
- Il flusso nuovo-cliente → raccolta telefono → booking è rotto nella FSM, non nel VoIP

---

## STATO GIT
```
Branch: master | HEAD: 3664cf3
Commits S121: 6 commit (tutti fix VoIP bridge)
type-check: 0 errori
voice pipeline: ATTIVO con VoIP
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:   Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:  Video V7             ✅ COMPLETATO (S117)
Phase 10b: Sara Features        ✅ COMPLETATO (S118)
Phase 10c: Sara VoIP EHIWEB    ✅ VoIP BRIDGE FUNZIONANTE (S121) — FSM bug rimasto
Phase 11:  Landing + Deploy     ⏳ (video YT non caricato)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/voip_pjsua2.py` — pjsua2 bridge (FUNZIONANTE)
- `voice-agent/main.py` — KMP_DUPLICATE_LIB_OK fix
- `voice-agent/src/booking_state_machine.py` — BUG: flusso nuovo cliente / numero telefono
- `voice-agent/lib/pjsua2/` — binari compilati (44 file)

---

## AMBIENTE iMac (confermato S121)
- **Homebrew**: installato, SWIG 4.4.1
- **pjproject**: `/tmp/pjproject` (compilato con PJMEDIA_HAS_SRTP=0)
- **pjsua2 bindings**: `voice-agent/lib/pjsua2/` (DYLD_LIBRARY_PATH necessario)
- **Porta SIP**: 5080 | **STUN**: `stun.voip.vivavox.it:3478`
- **Pipeline launch**: `DYLD_LIBRARY_PATH=lib/pjsua2` necessario nel comando di avvio
- **DB iMac**: warning `no such table: clienti` in NameCorrector (path DB potrebbe essere sbagliato)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 122.
PRIORITÀ: Fix booking_state_machine.py — flusso nuovo cliente rotto:
1. Quando Sara chiede "Mi dà un numero?" e cliente risponde "Sì" → deve aspettare il numero, non dire "Bene!"
2. Quando cliente detta numero telefono ("331 49 83 901") → entity_extractor deve riconoscerlo
3. Testare via VoIP: prenotazione completa, lista attesa, spostamento appuntamento
File: voice-agent/src/booking_state_machine.py + voice-agent/src/entity_extractor.py
```
