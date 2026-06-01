# S323 — Sara Voice Test su TUTTI i verticali (metodologia 2-layer)

**Generato**: 2026-06-01 (S322→S323 design, chiusura ordinata ~60% context)
**Obiettivo founder (REGOLA #21)**: Sara = pilastro. "Pronto a vendere" richiede Sara testata in modo APPROFONDITO su tutti i verticali, switch automatico Sara↔FLUXION, best practice 2026, guardrails, UX perfetta. Test guidato dal CTO via TTS/harness, MAI Luke al telefono (REGOLA #23/#14).

## STATO VERIFICATO S323 (fatti dal codice — NON re-investigare)

### Tassonomia prodotto — INTATTA (verificato src/types/setup.ts)
- **8 macro**: medico, beauty, hair, auto, wellness, professionale, pet, formazione
- **50 micro** (10+7+6+7+6+5+4+5). Struttura micro: `{ value, label, hasScheda, schedaType? }`.
- `professionale` e `formazione` → `hasScheda:false` BY DESIGN (no scheda clinica).
- **NON confondere** con `voice-agent/data/vertical_dbs/` = 12 DB SOTTOINSIEME per test VOCALE (auto, barbiere, beauty, fisioterapia, gommista, medical, odontoiatra, palestra, professionale, salone, toelettatura, wellness).

### Schede cliente — COMPLETE (verificato)
- `src/types/scheda-cliente.ts` (549 righe Zod) + `src/components/schede-cliente/` (8 .tsx).
- 9 schemi: odontoiatrica, fisioterapia, medica, estetica, parrucchiere, fitness, veicoli, carrozzeria, pet.
- **GAP NOTO (backlog, NON perdita dati)**: `SchedaPet.tsx` componente FE mancante → 4 micro pet cadono su `SchedaBase` vuota. Schema `SchedaPet` esiste, manca il componente + import in `SchedaClienteDynamic.tsx`.
- immobiliare/assicurazioni NON sono macro: esistono come micro dentro `professionale` (`agenzia`). Nessuna roadmap memoria li pianifica come verticali dedicati.

### Switch verticali — DUE meccanismi (entrambi reali, verificati live)
1. `voice-agent/scripts/switch_vertical.sh <nome>` → riscrive DB FLUXION in **3 path** (incluso app Tauri iMac) **+ kill+restart** pipeline 3002 + VoIP 5080. Tocca **SIA FLUXION SIA Sara**. ~2-15s downtime. FEDELE.
2. `POST /api/voice/set-vertical {vertical}` → runtime, ~0 downtime, tocca **solo orchestrator Sara** in-memory. Testato live OK: `{"success":true,"vertical":"salone"}`.

### Test esistenti
- `voice-agent/scripts/test_all_verticals_e2e.py`: loop 9 verticali, **SOLO TESTO** (POST /api/voice/process). Baseline noto = **21 OK / 8 WARN / 0 FAIL** (formato `TOTALE: N OK / N WARN / N FAIL`). Copre BOOKING/FAQ/TRIAGE/FLOW.
- **Nessun endpoint HTTP accetta audio reale**: `/process-audio` == alias di `/process` (testo). STT è SOLO nel path pjsua2/RTP.
- iMac: solo modulo Python `pjsua2` (no CLI pjsua/baresip/linphonec, no ffmpeg/sox). `say` + `afconvert` (builtin macOS) presenti.

## METODOLOGIA CORRETTA — TEST PYRAMID 2026 (decisione CTO)

NON testare ogni scenario × ogni verticale via audio (lento/fragile/ridondante). Due layer:

### LAYER 1 — TESTO, ampiezza (estendere l'esistente)
Copre TUTTA la logica vertical-specific a costo ~0. Task:
- Estendere `test_all_verticals_e2e.py` ai 3 DB fuori loop (**auto, professionale, wellness**) → 12 verticali.
- Aggiungere scenari avanzati: **waitlist** (slot occupato→PROPOSING_WAITLIST), **disambiguazione fonetica** (Gino vs Gigio, Levenshtein≥70%), **chiusura graceful** (ASKING_CLOSE_CONFIRMATION + WhatsApp), **escalation/triage** medico.
- Asserzioni su `fsm_state` + layer RAG (L3/L4) + keyword prezzo per verticale.
- Target: baseline pulito 12 verticali, ridurre/spiegare gli 8 WARN.

### LAYER 2 — AUDIO reale, profondità mirata (harness mancante)
Valida ciò che il testo NON può: STT su nomi/date italiani sul codec telefonico reale, naturalezza TTS, latenza E2E <800ms.
- Costruire `voice-agent/scripts/sara_audio_harness.py` con **pjsua2 Python** (NON CLI):
  - Secondo `pj::Account` SIP client → `makeCall` verso Sara (può chiamare `0972536918` liberamente, EHIWEB minuti illimitati, costo NON è vincolo).
  - `pj::AudioMediaPlayer` (WAV) → media uscita; `pj::AudioMediaRecorder` (WAV) → cattura risposta Sara.
  - `EpConfig` null audio device per girare headless via SSH.
  - WAV PCM 16-bit 8kHz mono via `say -o`/`afconvert` (verificare flag reale con `--help`, NON assumere).
- Scope audio: **golden-path per verticale** + scenari STT-sensitivi (disambiguazione fonetica). NON tutti gli scenari.
- Evidenza REALE: durata/byte WAV + trascrizione STT. NO successo senza runtime.

## TASK S323 (ordine)
0. PRE-FLIGHT 3002 (GIÀ UP fine S323-design, ma verificare): `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `registered:true, reg_status:200`. Se OFF: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python3 main.py --port 3002 > /tmp/sara.log 2>&1 &"`.
1. LAYER 1: estendere test_all_verticals_e2e.py a 12 verticali + scenari avanzati. Girare → baseline pulito.
2. LAYER 2: verificare `afconvert`/`say` flag WAV PCM16 8kHz mono. Scrivere `sara_audio_harness.py` pjsua2. Smoke 1 turno golden-path.
3. Estendere audio ai verticali chiave + disambiguazione fonetica.
4. (decisione Luke) `SchedaPet.tsx` da implementare? immobiliare/assicurazioni: micro `professionale` basta o servono macro dedicate?

## VINCOLI
- ZERO COSTI (say/Edge-TTS/Piper, EHIWEB illimitato). Verifica flag pjsua2/afconvert con doc upstream (vincolo #1).
- NON modificare codice produzione (FSM, orchestrator, voip_pjsua2.py). SOLO `scripts/`.
- Pipeline interrogabile SOLO via `ssh imac` (3002 bound 127.0.0.1).
- Context: task multi-sessione. Layer 1 prima (veloce), poi Layer 2. Chiudere a 60%.
