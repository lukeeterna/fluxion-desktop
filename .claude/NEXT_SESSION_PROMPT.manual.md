# FLUXION — S334 resume — Sara live-test. Layer 1 VERDE+esteso, prossimo: SIP fix + Layer 2 audio.

> Scritto 2026-06-03 a chiusura S333. Layer 1 esteso eseguito: 50 OK / 3 WARN / 0 FAIL su 12 verticali. Commit `4f1685c`.

## CHIUSO IN S333 (NON ri-fare)
- **LAYER 1 (testo) FIX + ESTESO** — commit `4f1685c`, file `voice-agent/scripts/test_all_verticals_e2e.py` (MacBook + iMac IDENTICI, shasum verificato `f0c8072d`).
  - Risultato: **50 OK / 3 WARN / 0 FAIL** su 53 test, **12/12 verticali** (erano 9). Run: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python3 scripts/test_all_verticals_e2e.py"` (~6 min, switch+restart per verticale; stdout bufferizzato → redirigere a file e attendere fine processo).
  - I **7 falsi-WARN FLOW di S332 sono ora OK**: l'assert FLOW tollera `registering_phone` (onboarding nuovo cliente) e `disambiguating_name` (omonimo) come esiti validi.
  - +3 verticali: `wellness` (spa €90), `professionale` (consulenza), `auto` (cambio olio €40). Prezzi reali da DB.
  - +scenari: **graceful closure** (tutti → `goodbye_standalone`, OK), **waitlist** (salone/barbiere best-effort), **disambiguazione fonetica** (barbiere "Marco Rossi"~"Marco Russo").
  - **3 WARN residui (NON difetti)**: 2× waitlist non innescata (slot non forzabile da solo testo — serve audio/DB pre-popolato), 1× professionale FAQ "consulenza legale" (Sara dice "i prezzi variano" perché nel DB non ha prezzo fisso). Tutti spiegati, zero FAIL.

## STATO GATE VENDITA (REGOLA #21)
- Payment+anti-refund rail = VERIFICATO LIVE PROD (S331). Necessario, NON sufficiente.
- Sara Layer 1 (testo) = **VERDE su 12 verticali, 0 FAIL**.
- **Manca**: Layer 2 (audio reale via SIP) — il vero gate. Solo dopo "Sara soddisfa pienamente il cliente su TUTTI i verticali via voce" → "pronto a vendere" + Sales Agent WA.

## S334 — PIANO (deciso CTO, REGOLA #15 no A/B)
### Step 0 — FIX SIP registration (PREREQ Layer 2, BLOCCANTE)
A fine S333 SIP era DOWN: `curl http://127.0.0.1:3002/api/voice/voip/status` → `registered:false, reg_status:408` (timeout). In S332 era `200`. Diagnosticare (credenziali EHIWEB/vivavox scadute? server SIP irraggiungibile? re-register loop?). Log: `ssh imac "tail -50 /tmp/voice-pipeline.log"`. Target: `registered:true, reg_status:200`. Delega a `voice-engineer` (foreground, REGOLA #27).

### Step 1 — Layer 2 AUDIO (harness SIP, il vero gate)
- Harness `sara_audio_harness.py` via pjsua2: golden-path per verticale + scenari STT-sensitivi (NON tutti via audio).
- Verificare flag conversione WAV: PCM16 8kHz mono (afconvert/say) per RTP.
- **CTO guida via TTS in autonomia** (REGOLA #23), MAI chiedere a Luke di chiamare. STT è nel path pjsua2/RTP → niente endpoint HTTP audio-in→STT.
- Criterio gate (REGOLA #21): Sara "soddisfa pienamente il cliente" su tutti i verticali via voce.

### PRIMO COMANDO S334
`ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → se `registered:false` delega Step 0 a voice-engineer; appena `200`, Step 1 harness audio.

## BLOCKED-ON / RESTA (non blocca il gate Sara)
- Custom domain `fluxion-app.com`: NS su CF, nessun record A → attaccare al worker prod per go-live brandizzato. Task atomico ~10 min, per il go-live pubblico.
- Rami client-side tsc-only (offline grace/clock-rollback/banner saraEnabled): GUI iMac Keychain (REGOLA #12).
