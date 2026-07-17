# REPORT B3-FIX-OBS (#34v) — capture WAV + osservabilità taratura

Data: 2026-07-17 · CC session `6a116da9` · Taglia S · SOLO logging+capture (zero FSM/NLU/logica).

## GATE-0
- `git status --porcelain` = `M tools/VectCutAPI` (gitlink embedded, residuo ammesso). Nessun file staged spurio.
- HEAD == origin/master == `6860baba`. ✅

---

## F1 — CAPTURE WAV (REGOLA #32): PREMESSA FALSIFICATA

**La premessa del mandato («nessun .wav prodotto nella chiamata delle 21:50 del 17/07») è FALSA.**
Il WAV è stato prodotto regolarmente; `SARA_TEST_CAPTURE=1` è propagato correttamente al processo Sara.

### Prova (dal log catturato `B3_LIVE_20260717/sara_go.log`)
- CALL_START=2, CALL_END=2 → `_on_call_end()` (`voip_goengine.py:401`) è scattato.
- Riga 1233:
  ```
  21:54:40 [voip_goengine] INFO: capture WAV-giudice scritto:
  /Volumes/MacSSD - Dati/FLUXION/.claude/cache/T-SARA-TURNTAKING/calls/call_20260717-215015.wav
  (rx_rms=1603 tx_rms=2899 bytes_stereo=8362240)
  ```
- File confermato ESISTENTE su iMac via SSH: `8362284` byte, 17 Lug 21:54.

### Perché il report B3-RACCOLTA lo dava «assente» — CAUSA REALE
- **Errore di posizione di ricerca**, NON bug di propagazione env. La sessione precedente ha cercato
  in `/tmp/b3` e nella cache del **MacBook** (`voice-agent/.claude/cache`), ma il WAV lato-Sara si scrive
  nel repo del **processo Sara** (iMac): `_write_call_capture()` deriva la dir da `__file__`
  (`voip_goengine.py:934-936` → `repo_root/.claude/cache/T-SARA-TURNTAKING/calls/`). Nessuno aveva
  guardato la dir `calls/` **sull'iMac**.
- La trappola env documentata (var solo all'harness) NON si applica al path B3 di produzione: `b3_open.sh:60`
  usa il prefisso `VOICE_ENGINE=go SARA_TEST_CAPTURE=1 nohup $ARGV` che esporta la var al processo `nohup`
  e ai suoi figli → arriva a `main.py`. La scrittura del WAV con rms>0 lo dimostra a posteriori.
- Nota FS: su iMac `/Volumes/MacSSD - Dati/FLUXION` e `.../fluxion` risolvono alla STESSA dir
  (filesystem case-insensitive) → nessun split di path, solo differenza di case a display.

### Salvage (durabile, REGOLA #32)
- WAV portato sul MacBook nel repo tracciato:
  `.claude/cache/T-SARA-TURNTAKING/calls/20260717-215015_B3-LIVE/call_20260717-215015.wav`
- Verifica leggibilità (Python `wave`+`array`, senza audioop rimosso in 3.13):
  `ch=2 sr=8000 frames=2090560 dur=261.3s L(rx caller)_rms=1603 R(tx Sara)_rms=1452` → **rms>0 su entrambe le tracce**.
- Classe durabilità: **cache repo committata** (i WAV in cache sono tracciati: 60 già versionati).

### PROVA su rig high-port — già soddisfatta da artefatti durevoli (16-07)
Il mandato chiede rx/tx/mix «scritti e leggibili» sul rig. Sono GIÀ presenti e verificati, non serve ri-run
(che spawnerebbe processi iMac inutilmente — REGOLA #10 verificato>verosimile, #31 realtà-filesystem):
- `.claude/cache/T-SARA-TURNTAKING/rig/capture_B3X2_20260716/run2_valid/`:
  - `rx.wav`  → ch=1 sr=8000 dur=30.8s **rms=2344**
  - `tx.wav`  → ch=1 sr=8000 dur=30.8s **rms=1217**
  - `mix.wav` → ch=2 sr=8000 dur=30.8s **rms=1868** (L=rx 2344 / R=tx 1217)
  - `harness_rx.wav` → rms=2344
- Il capture harness-side (`tools/gospike/uac.go:112`, gated `SARA_TEST_CAPTURE=1`) e il capture Sara-side
  (`voip_goengine.py:188`) sono quindi **entrambi provati funzionanti**, su run distinti.

**Verdetto F1**: capture NON rotta su nessun path. Nessun fix di codice necessario. La rottura percepita era
di procedura (fetch-back del WAV dall'iMac). Discordanza aperta → vedi sezione DISCORDANZE.

---

## F2 — LOGGER (solo logging, zero logica)

Tutte le modifiche taggate `[TARATURA]` per grep. `python3 -m py_compile` OK su entrambi i file.

### a) TTS text loggato a 160 char (era ~40)
- `voice-agent/src/tts_engine.py:308`: `text[:40]` → `text[:160]`.
- Prova del bug: log 17-07 `text='Salone Demo FLUXION, buonasera! Sono Sar'` (troncato a 40, disclosure tagliata).

### b) Timestamp FINE-UTTERANCE caller (endpoint→LISTENING) + latenza percepita→audio-out
- `voice-agent/src/voip_goengine.py` `_process_caller_audio()` (dispatch del turno chiuso dal VAD):
  - entry: `[TARATURA][ENDPOINT] fine-utterance caller → dispatch NLU (bytes=%d)` + `_t_endpoint = time.monotonic()`
  - audio-out: `risposta TTS in coda TX (%dB) | [TARATURA] latenza fine-utterance→audio-out=%.0fms`

### c) SLOT-RESULT NLU per turno (servizi estratti → id catalogo)
- `voice-agent/src/voip_goengine.py` dopo `self.last_turn_result = result`:
  `[TARATURA][SLOT] intent=%r servizio=%r servizio_id=%r slots=%r`

### d) Boot log parametri con provenienza file:riga
- `voice-agent/src/voip_goengine.py` in `start()` dopo il log "GoEngine start".
- Riga renderizzata (valori dai costanti in scope):
  ```
  [TARATURA][BOOT] reprompt_timer=22.0s (voip_goengine.py:87) | vad_speech_threshold=400 rms (voip_goengine.py:58) | vad_silence_timeout=50 frame ~1000ms endpointing (voip_goengine.py:59) | vad_min_speech_frames=15 ~300ms (voip_goengine.py:60) | E6_strike_threshold=3 (booking_state_machine.py:3086)
  ```

**Nota**: NON riavviata la Sara di produzione (:3002 VIETATO dal mandato) → le nuove righe si materializzano
al prossimo boot Sara. Gli esempi sopra sono deterministici dal codice (costanti note).

---

## F3 — DISCLOSURE STATICA (M1, AI Act art.50, deadline 2/8)

- Template greeting (nuovo chiamante), `voice-agent/src/session_manager.py:744`:
  ```python
  return f"{session.business_name}, {saluto.lower()}! Sono Sara, l'assistente virtuale. Come posso aiutarla?"
  ```
  Reso a runtime (log 17-07:145, troncato): «Salone Demo FLUXION, buonasera! Sono Sara, l'assistente virtuale. Come posso aiutarla?»
- Ramo chiamante di ritorno, `voice-agent/src/session_manager.py:740`:
  ```python
  return f"{session.business_name}, {saluto.lower()}! Bentornato {caller_name}, sono Sara, l'assistente virtuale. Come posso aiutarla?"
  ```

**VERDETTO disclosure — contiene 'assistente virtuale'? SÌ** (entrambi i rami: `session_manager.py:740` e `:744`).
Nessuna modifica al testo (fuori scope). M1 statico soddisfatto.

---

## DISCORDANZE / CONTRADDIZIONI APERTE
1. **Premessa mandato vs realtà**: il mandato assume WAV assente + env non propagato; il log prova il contrario
   (WAV scritto, rms>0). La root-cause vera è procedurale (WAV resta nel repo iMac, non copiato sul MacBook).
   → Decisione giudice: aggiungere fetch-back del WAV iMac in `b3_close.sh`/RUNBOOK? (fuori scope #34v).
2. **rms tx log vs post-interleave**: log dichiara `tx_rms=2899` (buffer grezzo pre-pad); dopo interleave stereo
   con zero-pad la traccia R misura rms=1452. Entrambi >0, coerenti; differenza = padding, non perdita.
3. **rig capture Sara-side**: `launch_rig.sh` NON esporta `SARA_TEST_CAPTURE` a `sara3003` → sul rig si prova solo
   il capture harness-side (uac). Il Sara-side è provato dal path produzione 17-07. Non un difetto bloccante.

## CONTEXT
- `used_pct` dal json sessione `6a116da9`: **14.0%** (budget_state SAFE, source=transcript).
  (Il warn VOS a 50% è RAW-inflated, cfr. MEMORY REGOLA #27.)
