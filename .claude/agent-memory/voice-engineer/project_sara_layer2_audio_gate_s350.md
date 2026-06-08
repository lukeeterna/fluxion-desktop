---
name: Sara Layer 2 audio gate — provider reg verde S350
description: reg_status:200 verde su VivaVox per la 1a volta da ~15 sessioni; test audio reale pendente, ipotesi anti-crash via provider da verificare
type: project
---

Sara Layer 2 (audio reale via SIP) è il gate vendita REGOLA #21 — ancora APERTO al 2026-06-08.

**Fatto strutturale nuovo (S350, output reale)**: `curl 127.0.0.1:3002/api/voice/voip/status` → `registered:true, reg_status:200` su VivaVox/EHIWEB (username 0972536918, server sip.vivavox.it, engine pjsua2). È la PRIMA registrazione verde da ~15 sessioni (S334→S349 erano 403). Trial VivaVox Free riattivato S349 (30gg/100min), credenziali allineate su iMac `voice-agent/.env`.

**Why**: la registrazione provider verde è il pre-requisito che mancava per testare l'ipotesi che una chiamata via RETE PROVIDER eviti la race del crash loopback. A S244 le chiamate provider NON crashavano; il loopback puro `127.0.0.1:5080` invece SIGABRT in `libHandleEvents` (voip_pjsua2.py:806) — bug strutturale pjsua2 group-lock owner-thread mismatch su onCallMediaState, version+config independent, NON Python-fixabile (3 cicli falsificati S336-S338).

**How to apply**: prossima sessione esegue il test audio (harness `voice-agent/scripts/sara_audio_harness.py`, NON modificarlo; WAV PCM16 8kHz mono via say+afconvert). Preferire path che passa per rete provider, non loopback. Se crasha IDENTICO anche via provider → STOP, no 4° ciclo (vincolo #1c), escala a Luke. Trial instabile: se reg_status ridiscende a 403 è BLOCKED-ON Luke→EHIWEB, NON re-diagnosticare il 403.
