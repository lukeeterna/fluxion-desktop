# S323 — Sara Audio Harness (riprende da S322)

**Generato**: 2026-06-01 (S322 chiusura ordinata a 61% context)
**Obiettivo**: BLOCKER #1 — harness audio autonomo per "parlare" a Sara via SIP senza umano al telefono.

## STATO S322 — research-first parziale (NO smoke eseguito)

### Fatti verificati a RUNTIME (non re-investigare)
- VoIP UP ORA: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` →
  `{"running":true,"sip":{"registered":true,"reg_status":200,"username":"0972536918","server":"sip.vivavox.it"},"rtp_active":false,"engine":"pjsua2"}`
- **`pjsua` / `pjsua2` CLI NON installati** sull'iMac. `baresip` NON installato. `linphonec` NON installato.
  Esiste SOLO il modulo Python `lib/pjsua2/_pjsua2.cpython-39-darwin.so` (+ codec dylib: g7221, gsm, ilbc).
  → **Il piano "pjsua CLI con --play-file/--rec-file" NON è applicabile senza installazione.**
- `say` (macOS TTS) presente. **`ffmpeg` e `sox` NON presenti** sull'iMac.
  → conversione audio: usare `say -o file.wav --data-format=LEI16@8000` (verificare flag reale, NON verificato)
    oppure `afconvert` (builtin macOS, NON ancora verificato `--help`).
- Nessuna dir `voice-agent/scripts/` con harness audio esistente (presenti solo: switch_vertical.sh, smoke_test.py, test_live_autonomous.py, test_all_verticals_e2e.py, test_cross_machine.py).

### DECISIONE TECNICA per S323 (root cause: no CLI SIP)
Dato che pjsua2 esiste SOLO come modulo Python, l'harness va costruito con **pjsua2 Python** (stesso bind usato da voip_pjsua2.py), NON con CLI esterna. Pattern:
- Secondo `pj::Account` registrato come client SIP separato che fa `makeCall` verso Sara.
- `pj::AudioMediaPlayer` (createPlayer su WAV) collegato al call media in uscita.
- `pj::AudioMediaRecorder` (createRecorder su WAV) collegato al call media in arrivo → cattura risposta Sara.
- Usare `--null-audio` equivalent: `EpConfig` con null audio device (no hardware) per girare headless via SSH.

### COSTO EHIWEB — NON È UN VINCOLO (founder-input S322)
Luke ha chiarito: **EHIWEB funziona e il costo non è un problema** (minuti illimitati da smartphone). → NIENTE step di verifica costo. L'harness può chiamare il numero `0972536918` liberamente.
- Resta comunque preferibile SIP-to-SIP interno (URI diretto) se più semplice da implementare, ma NON per ragioni di costo — solo se riduce complessità/latenza.

## TASK S323 (in ordine)
0. PRE-FLIGHT: riavviare Voice Pipeline 3002 (era NON ATTIVO a fine S322): `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara.log 2>&1 &"` poi `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → attendere `registered:true`.
1. Verificare `afconvert`/`say` per produrre WAV PCM 16-bit 8kHz mono (formato che pjsua2 player accetta).
2. (RIMOSSO — costo EHIWEB non è un vincolo, founder-input S322).
3. Scrivere `voice-agent/scripts/sara_audio_harness.py` con pjsua2 Python (player+recorder+null-audio, account secondario). Può chiamare `0972536918` liberamente.
4. SMOKE 1 turno su verticale corrente: chiamata → play WAV saluto+booking → record risposta → verify `rtp_active:true` + WAV non vuoto + (opz.) STT via /api/voice/process.
5. Riportare evidenza REALE (durata/byte WAV, trascrizione). NO successo senza runtime.

## VINCOLI
- ZERO COSTI (say/Edge-TTS/Piper OK). Verifica flag pjsua2 con doc upstream.
- NON modificare codice produzione (FSM, orchestrator, voip_pjsua2.py core). SOLO scripts/.
- Pipeline interrogabile SOLO via `ssh imac` (3002 bound su 127.0.0.1).
