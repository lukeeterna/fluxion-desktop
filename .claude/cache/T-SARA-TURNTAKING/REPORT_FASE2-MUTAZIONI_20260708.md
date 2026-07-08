# REPORT T-SARA-TURNTAKING — FASE 2 (MUTAZIONI adapter+FSM-guard+filler)

Data: 2026-07-08 · Gate label (#1c): **GATING/BARGE-IN/FSM-HANGUP/FILLER (FASE 2 mutazioni)** · Verdetto: 🟢 FASE 2 CHIUSA (mutazioni deployate+compilate, pipeline sana) · GATE A3 test = FASE 3 (sessione fresca) · Mutazioni: 3 file

## 1. Baseline di partenza (stampata, A3)
- `engine:"pjsua2"`, `registered:true`, `reg_status:200`, `rtp_active:false`; health ok v2.1.0; latency **count=18**; PID **69142** `main.py --port 3002`, processo unico, **zero orfani** engine_darwin. Restore point = default pjsua2 (`VOICE_ENGINE` non toccato).

## 2. Mutazioni applicate (spec §4, ordine adapter → hangup-guard → filler)

### 2.1/2.2 — `voip_goengine.py` (adapter Go): 4 difetti = un sistema
Backup #1d iMac verificato: `src/voip_goengine.py.bak-PRE-TURNTAKING-20260708-190858` (md5 pre = 38cef746…, size 28715).
- **Stato-turno esplicito** `_is_sara_speaking()`: SPEAKING sse TX in coda O entro **grace `TX_GRACE_S=180ms`** dopo l'ultimo frame TX (`_tx_last_frame_ts`, marcato in `_tx_pump`). Copre i ~200ms di coda RTP residua dell'engine (txCapFrames=10) → RX non entra in STT su eco di linea.
- **Difetto 2 (load-bearing)**: `_current_tx_rms` azzerato nell'idle-branch di `_tx_pump`. Prima restava al valore dell'ultimo frame voce → `sara_speaking=True` **permanente** → parlato chiamante scartato come echo → radice della spazzatura STT GATE B (`'Vessamiteevi, buonaseraamigliorea'`).
- **Barge-in adattivo**: `echo_floor` = media mobile RMS RX durante TX (`ECHO_FLOOR_ALPHA=0.15`); trigger = `rms > max(BARGE_IN_MARGIN=500, BARGE_IN_K=2.5·echo_floor)` sostenuto **`BARGE_IN_SUSTAIN=13` frame (~260ms)**.
- **Ring-buffer pre-trigger** `RX_PRETRIGGER_FRAMES=17` (~340ms): al barge-in `clear_tx()` (svuota TX + azzera grace → LISTENING immediato) + inoltra a STT i frame del ring → le prime parole del chiamante NON si perdono.
- Costanti `ECHO_ATTENUATION`/`BARGE_IN_THRESHOLD` ora inutilizzate (lasciate: doc-replica pjsua2, edit minimo).

### 2.3 — FSM-HANGUP GUARD → applicato in `voip_goengine.py` (DISCORDANZA #3)
- **DISCORDANZA #3** | premessa spec 2.3: guardia in `booking_state_machine.py` | fatto (disco): l'hangup del motore Go nasce nell'adapter che consuma `result["should_exit"]` (voip_goengine.py); `should_exit` ha ~13 origini legittime nella FSM (booking done, goodbye, escalation…) → gate individuale = refactor (vietato "edit minimo") | **correzione (vince il disco)**: guardia al choke-point dell'adapter (che la spec stessa indica: «verificare dove nasce should_exit»). Hangup onorato SOLO se `result["intent"]` contiene `goodbye`/`chiusura` (congedo esplicito mutuo); ogni altro `should_exit` → log `HANGUP soppresso (FSM-guard)` + **Sara resta in linea**. Soddisfa done-condition B3 «Sara non riaggancia mai per prima» + orecchio «mai riagganciato lei». (`voip_pjsua2.py` NON toccato: default sicuro, fuori dal test B3.)

### 2.4 — Policy filler → `orchestrator.py` (DISCORDANZA #4)
Backup #1d iMac verificato: `src/orchestrator.py.bak-PRE-TURNTAKING-20260708-191556` (md5 pre = 09d60bf5…, size 293621).
- **DISCORDANZA #4** | premessa spec 2.4 «policy filler completa (latency-gate, cortesia)» | fatto (disco): l'adapter Go `_process_caller_audio` consuma solo `audio_response`/`should_exit`, **NON `filler_audio`** → nel path Go (sotto test B3) i filler NON vengono mai riprodotti → B3 done-condition (3) «filler solo secondo policy» **soddisfatto banalmente** nel Go. La cortesia grazie/prego è **contenuto di risposta FSM**, distinta dal banco filler (`orchestrator.py:461-466`). | **correzione (vince il disco)**: edit minimo spec-aligned = **rotazione round-robin** in `_get_filler_audio` (sostituisce `random.choice` → no ripetizioni; `_filler_idx`). Call-site invoca la funzione solo dopo end-of-turn VAD (mai in SPEAKING/silenzio; 1/turno).
- (d) VAD fine-turno: `VAD_SILENCE_TIMEOUT=50 ×20ms = 1000ms ≥ 600ms` → OK (confermato su disco, adapter riga 58).
- **Deferrato (feature-add, non turn-taking)**: wiring `filler_audio` nel Go + latency-gate predittivo + separazione FILLER/CORTESIA come layer esplicito. Non blocca GATE A3/B3.

## 3. Deploy + verifica (prova grezza)
- `py_compile` OK **locale MacBook (py3.13)** + **iMac (py3.9)** su entrambi i file.
- Sync byte-exact (md5 local==iMac): `voip_goengine.py` = `bb3b1614cf9abeeab0831e5af15d5985`; `orchestrator.py` = `049961da6079ffe866d56342698c44e4`.
- Pipeline riavviata **PID 79633** (`python3 main.py --port 3002`), health ok, `engine:"pjsua2"` (default non toccato), **`reg_status:200` in 1s**, processo unico, zero orfani engine_darwin. → deploy non regredisce il default.

## 4. ADDENDUM W (capture WAV) — stato
- **NON implementato in questa sessione** (fa parte dell'harness GATE A3, FASE 3). Nessun flag `SARA_TEST_CAPTURE` aggiunto → **nessun rischio default-ON**: la cattura verrà introdotta con l'harness e verificata OFF a fine FASE 3.

## 5. PROSSIMO — FASE 3 GATE A3 (sessione fresca, headroom pieno)
Estendere `voice-agent/tools/gospike/uac.go` con `-echo <dB>` (mix del ricevuto attenuato ~-15dB nel proprio TX) + iniezione utterance a T sopra il parlato di Sara + capture dual-stream sotto flag `SARA_TEST_CAPTURE=1` (default OFF). Scenario = GATE B in laboratorio, committato come **regressione permanente**. Done-condition A3(1-4): STT senza frammenti Sara; barge-in scatta sull'utterance vera (TX flush + log + prime parole NON perse via ring pre-trigger); filler solo secondo policy; Sara non riaggancia mai per prima. Prova = WAV+trascrizioni+contatori in `.claude/cache/T-SARA-TURNTAKING/calls/<ts>_A3/`. Rosso → UNA iterazione etichettata → ritest → STOP.
Poi CHECKPOINT context; poi FASE 4 GATE B3 (founder, una chiamata, solo su VERDE-A3).

## 6. File toccati + backup #1d
| File | Backup iMac (#1d) | md5 post (local==iMac) |
|------|-------------------|------------------------|
| `voice-agent/src/voip_goengine.py` | `.bak-PRE-TURNTAKING-20260708-190858` | `bb3b1614…` |
| `voice-agent/src/orchestrator.py` | `.bak-PRE-TURNTAKING-20260708-191556` | `049961da…` |
| `booking_state_machine.py` | NON toccato (DISCORDANZA #3: guardia in adapter) | — |
