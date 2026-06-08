# CARRY S350 — TEST AUDIO REALE SARA (gate vendita REGOLA #21) — NON INIZIATO

> Chiusura ordinata per context budget 61% (vincolo #7). Pre-flight FATTO e VERDE, test audio NON ancora eseguito.

## Stato verificato a inizio S350 (2026-06-08, output reale)
- `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `{"running":true,"sip":{"registered":true,"reg_status":200,"username":"0972536918","server":"sip.vivavox.it"},"rtp_active":false,"engine":"pjsua2"}` — **registrazione VERDE confermata** (trial VivaVox riattivato S349).
- `/health` → `status:ok`, version 2.1.0, stt:GroqSTT, tts:adaptive. Pipeline UP.

## Prossimi step (ESEGUIRE in quest'ordine, NON re-investigare i fatti sopra)
1. Ri-conferma `reg_status:200` col curl. Se 403 → STOP, BLOCKED-ON Luke→EHIWEB (trial instabile, NON re-diagnosticare).
2. Leggi `voice-agent/scripts/sara_audio_harness.py` (COMMITTATO, NON modificarlo) per capire URI target + come passa WAV + dove scrive cattura RTP.
3. Genera WAV: `say -o /tmp/raw.aiff "Buongiorno, vorrei prenotare un appuntamento"` → `afconvert -f WAVE -d LEI16@8000 -c 1 /tmp/raw.aiff /tmp/sara_in.wav` → verifica con `afinfo` (`1 ch, 8000 Hz, Int16`).
4. Esegui golden-path booking via AUDIO. Preferisci path SIP che passa per la rete provider invece di puro loopback `127.0.0.1:5080` (vedi crash sotto). Cattura `/tmp/sara-pjsip-*.log` con faulthandler.
5. Se Sara risponde: cattura RTP→WAV, trascrivi (whisper.cpp/Groq), verifica risposta pertinente al booking (chiede servizio/data/nome).

## CRASH NOTO (non perdere tempo)
- LOOPBACK `sip:0972536918@127.0.0.1:5080` → `Fatal Python error: Aborted (SIGABRT)` in `libHandleEvents` (voip_pjsua2.py:806), bug STRUTTURALE pjsua2 (group-lock owner-thread mismatch su `onCallMediaState` conference port commit). Version+config independent. PARCHEGGIATO, NON Python-fixabile.
- A S244 le chiamate via PROVIDER NON crashavano (timing rete diluisce la race). Ipotesi da testare: ora che reg_status:200, una chiamata via rete EHIWEB evita la race.
- Se crasha IDENTICO anche via provider → NO 4° ciclo fix Python (vincolo #1c). Riporta firma + escala a Luke.

## DONE-CONDITION
Sara risponde PERTINENTE al golden-path booking via AUDIO REALE (WAV→STT→NLU→risposta catturata+trascritta) → chiude gate Sara Layer 2 (REGOLA #21).

---

# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-08T07:31:43Z`
**Sessione**: `0153d7de-e4a0-4735-9588-2dd934e54d67`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: committed: fa157ce
**Last commit**: `fa157ce auto-close session 0153d7de-e4a0-4735-9588-2dd934e54d67 @ 2026-06-08T07:31:43Z`

## Ultimi 5 commit
```
fa157ce auto-close session 0153d7de-e4a0-4735-9588-2dd934e54d67 @ 2026-06-08T07:31:43Z
3e46cfc S349: 🟢 SARA LAYER 2 SBLOCCATO — EHIWEB reg_status:200 dopo ~15 sessioni di 403. Mail riattivazione VivaVox Free → root cause reale = password disallineata su iMac voice-agent/.env (main aveva controllato solo ~/.claude/.env globale). Fix: backup .env (REGOLA #1d) + allineata VOIP_SIP_PASS + restart pipeline → registered:true al primo tentativo. Carry S350 = test chiamata audio reale CTO-guidato (REGOLA #23). POI R2 (CI rotto) → R3.
c2219ca S348: R2 investigato — root-cause distribuzione = CI release-full.yml ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm), non release vuota-by-design. v1.0.1 published/0-asset. Handoff S349 con prima azione gh run view --log-failed. EHIWEB 403 invariato.
a8d97ee S347: R1 conversion attribution CHIUSO E2E — D1 sbloccato, migration 0003 applicata prod+test, deploy prod+test, smoke firmato PASS (lead_999→conversion row + licenza)
f31df22 auto-close session e11bc5b2-c3ef-4df9-bdce-4484e4eb11ed @ 2026-06-08T06:53:35Z
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
```

## Ultimo prompt utente (estratto)
```
CHIUSO ORDINATAMENTE? SOLO SI O NO
```

## Ultimi turni assistant
```
```
Se ancora `reg_status:200` → delega a `voice-engineer` il test chiamata reale Sara via harness `voice-agent/scripts/sara_audio_harness.py`, CTO-guidato via TTS (REGOLA #23, mai chiedere a Luke di chiamare). Questo è il **gate vendita REGOLA #21**: Sara testata LIVE via audio sui verticali. Poi R2 (CI `release-full.yml` rotto) → R3.
SÌ.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
