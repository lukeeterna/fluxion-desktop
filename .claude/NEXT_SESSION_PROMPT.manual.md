# FLUXION — S333 resume — Sara live-test. Layer 1 VERDE, prossimo: fix test + Layer 2 audio.

> Scritto 2026-06-03 a chiusura S332. Layer 1 (testo) eseguito: 22 OK / 7 WARN / 0 FAIL, nessun difetto bloccante.

## CHIUSO IN S332 (NON ri-fare)
- **PRE-FLIGHT SIP VERDE**: `curl http://127.0.0.1:3002/api/voice/voip/status` → `running:true, registered:true, reg_status:200, engine:pjsua2, username:0972536918@sip.vivavox.it, rtp_active:false`. NB: i campi SIP NON sono più su `/health` (v2.1.0) → sono su `/api/voice/voip/status`.
- **LAYER 1 (testo) eseguito** via voice-engineer su iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 scripts/test_all_verticals_e2e.py"` → **22 OK / 7 WARN / 0 FAIL** su 29 test, 9/9 verticali. (S323 dichiarava 21/8/0; +1 OK è non-determinismo Groq, NON regressione.)
- **FINDING**: i 7 WARN sono **falsi negativi del test**, non difetti di Sara. Tutti lo stesso pattern FLOW: dopo "Mi chiamo Marco Rossi" (cliente non in DB) Sara va a `registering_phone` (onboarding nuovo cliente) o `disambiguating_name` (barbiere: "Marco Russo" simile → disambigua). Comportamento CORRETTO; il test è troppo rigido sull'enum di stati attesi. Zero FAIL; BOOKING/FAQ/TRIAGE solidi.
- **Path corretto del test**: `voice-agent/scripts/test_all_verticals_e2e.py` (262 righe, S151), NON in `voice-agent/` root.

## STATO GATE VENDITA (REGOLA #21)
- Payment+anti-refund rail = VERIFICATO LIVE in PROD (S331). Necessario, NON sufficiente.
- Sara Layer 1 (testo) = sostanzialmente VERDE, nessun difetto bloccante.
- **Manca**: Layer 1 completo (estensione test) + Layer 2 (audio reale via SIP). Solo dopo "Sara soddisfa pienamente il cliente su TUTTI i verticali" → "pronto a vendere" + attivare Sales Agent WA.

## S333 — PIANO (deciso CTO, REGOLA #15 no A/B)
### Step 1 — FIX + ESTENSIONE Layer 1 (`scripts/test_all_verticals_e2e.py`, ~100 righe)
Delega a `voice-engineer` (foreground, REGOLA #27). Copertura test = file scaffolding → editabile anche sopra 50% (context-budget-gate "tolerabile"). Modifiche:
1. Rendere l'assert FLOW tollerante: `registering_phone` e `disambiguating_name` sono esiti VALIDI per cliente nuovo/omonimo → trasformano 7 falsi-WARN in OK.
2. Aggiungere scenari mancanti: `waitlist` (slot occupato → PROPOSING_WAITLIST → WAITLIST_SAVED), `chiusura graceful` (ASKING_CLOSE_CONFIRMATION + WhatsApp + "arrivederci"), `disambiguazione fonetica` come scenario dedicato (Gino vs Gigio).
3. Coprire i verticali macro non ancora testati esplicitamente: wellness, professionale, formazione.
4. Re-run → target 0 FAIL, WARN solo se variante semantica accettabile.

### Step 2 — Layer 2 AUDIO (harness SIP, il vero gate)
- Harness `sara_audio_harness.py` via pjsua2: golden-path per verticale + scenari STT-sensitivi (NON tutti via audio).
- Verificare flag conversione WAV: PCM16 8kHz mono (afconvert/say) per RTP.
- **CTO guida il test via TTS in autonomia** (REGOLA #23), MAI chiedere a Luke di chiamare dal telefono. STT è nel path pjsua2/RTP → serve harness audio via SIP (no endpoint HTTP audio-in→STT).
- Criterio gate (REGOLA #21): Sara "soddisfa pienamente il cliente" su tutti i verticali.

### PRIMO COMANDO S333
`curl http://127.0.0.1:3002/api/voice/voip/status` (via ssh imac se serve) → conferma registered:true. Se down → restart via voice-engineer. Poi delega Step 1 a voice-engineer.

## BLOCKED-ON / RESTA (non blocca il gate Sara)
- Custom domain `fluxion-app.com`: NS su CF, nessun record A → attaccare al worker prod per go-live brandizzato. Task atomico ~10 min, indipendente, per il giorno del go-live pubblico.
- Rami client-side tsc-only (offline grace/clock-rollback/banner saraEnabled): GUI iMac Keychain (REGOLA #12).
