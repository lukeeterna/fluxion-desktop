# FLUXION — Handoff Sessione 120 → 121 (2026-03-29)

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

## COMPLETATO SESSIONE 120

### pjsua2 compilato e funzionante su iMac
1. Homebrew installato su iMac (fondatore ha dato sudo)
2. SWIG 4.4.1 installato via brew
3. pjproject clonato e compilato da source (`/tmp/pjproject`)
4. Ricompilato con `PJMEDIA_HAS_SRTP 0` (config_site.h) per evitare SRTP self-test crash in daemon
5. Python SWIG bindings compilati con `CFLAGS='-std=c++11'`
6. Librerie copiate in `voice-agent/lib/pjsua2/` (44 file: .so + .dylib)
7. `voip_pjsua2.py` creato — drop-in replacement di `voip.py` con stessa interfaccia VoIPManager
8. `main.py` aggiornato per importare da `voip_pjsua2`

### Risultati positivi
- **SIP REGISTER 200 OK** ✅ — pjsua2 si registra correttamente su sip.vivavox.it
- **STUN funzionante** ✅ — `stun.voip.vivavox.it:3478` scopre IP pubblico
- **Re-registration automatica** ✅ — ogni ~10 minuti
- **Pipeline daemon stabile** ✅ — fino a quando arriva una chiamata
- **4 commit pushati** (b2e0730, fdc8c5a, 66dee79, 6da2dea)

### BUG BLOCCANTE: SaraAudioPort crash
**PROBLEMA**: Quando arriva una chiamata, il processo CRASHA con:
```
Assertion failed: (pia->fmt.type==PJMEDIA_TYPE_AUDIO &&
  pia->fmt.detail_type==PJMEDIA_FORMAT_DETAIL_AUDIO),
  function PJMEDIA_PIA_CCNT, file port.h, line 273.
```

**CAUSA**: `SaraAudioPort.createPort("sara_bridge", fmt)` non inizializza correttamente il `MediaFormatAudio`. Il campo `fmt.type` non viene impostato a `PJMEDIA_TYPE_AUDIO` dal costruttore Python SWIG.

**CONSEGUENZA**: Il chiamante sente "Vodafone" (irraggiungibile) o "occupato" (stale registration dopo crash).

### FIX NECESSARIO per S121
Il problema è nell'inizializzazione di `MediaFormatAudio` in `SaraAudioPort.__init__()` (voip_pjsua2.py riga ~88):
```python
fmt = pj.MediaFormatAudio()
fmt.clockRate = 8000
# MANCA: fmt.type = pj.PJMEDIA_TYPE_AUDIO
# OPPURE: usare un metodo diverso per creare il port
```

**Approcci da provare (in ordine)**:
1. Aggiungere `fmt.type = pj.PJMEDIA_TYPE_AUDIO` esplicitamente
2. Se `type` non è settabile, usare `pj.MediaFormatAudio.init()` se disponibile
3. Se nessuno funziona: NON usare `AudioMediaPort.createPort()` — usare il conference bridge direttamente con file WAV o named pipe
4. **Alternativa radicale**: usare pjsua2 solo per SIP/RTP e bridgiare l'audio via file/socket, non tramite AudioMediaPort

**Test rapido** per debug (da eseguire su iMac):
```python
import pjsua2 as pj
fmt = pj.MediaFormatAudio()
print(dir(fmt))           # lista attributi
print(hasattr(fmt, 'type'))
fmt.type = pj.PJMEDIA_TYPE_AUDIO  # prova
```

---

## STATO GIT
```
Branch: master | HEAD: 6da2dea
Commits S120: 4 commit (pjsua2 bridge + 3 fix)
type-check: 0 errori
voice pipeline: DOWN (crash assertion)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:   Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:  Video V7             ✅ COMPLETATO (S117)
Phase 10b: Sara Features        ✅ COMPLETATO (S118)
Phase 10c: Sara VoIP EHIWEB    🔄 IN PROGRESS — pjsua2 registra, audio bridge crash
Phase 11:  Landing + Deploy     ⏳ (video YT non ancora caricato)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/voip_pjsua2.py` — pjsua2 bridge (BUG: SaraAudioPort crash)
- `voice-agent/src/voip.py` — vecchio SIP client (backup, funziona ma audio broken)
- `voice-agent/lib/pjsua2/` — compilato binario pjsua2 + dylib (44 file)
- `/tmp/pjproject/` — sorgenti pjproject compilate su iMac (con config_site.h SRTP=0)
- `.claude/cache/agents/universal-voip-solution-research.md` — research 12 approcci

---

## AMBIENTE iMac (aggiornato S120)
- **Homebrew**: installato (`/usr/local/bin/brew`, PATH richiede `/usr/bin` per readlink)
- **SWIG**: 4.4.1 via brew
- **pjproject**: `/tmp/pjproject` (compilato con `PJMEDIA_HAS_SRTP 0`)
- **pjsua2 bindings**: `voice-agent/lib/pjsua2/` (DYLD_LIBRARY_PATH necessario)
- **Porta SIP**: 5080 (5060=Traccar, 5090 usato in test)
- **STUN corretto**: `stun.voip.vivavox.it:3478` (NON stun.sip.vivavox.it)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 121.
PRIORITÀ: Fix SaraAudioPort assertion crash — MediaFormatAudio.type non inizializzato.
Il pjsua2 registra OK su EHIWEB ma crasha quando arriva chiamata.
voice-agent/src/voip_pjsua2.py riga ~88 — createPort format.
```
