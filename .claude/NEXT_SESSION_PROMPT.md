# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-08T07:22:56Z`
**Sessione**: `0153d7de-e4a0-4735-9588-2dd934e54d67`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `3e46cfc S349: 🟢 SARA LAYER 2 SBLOCCATO — EHIWEB reg_status:200 dopo ~15 sessioni di 403. Mail riattivazione VivaVox Free → root cause reale = password disallineata su iMac voice-agent/.env (main aveva controllato solo ~/.claude/.env globale). Fix: backup .env (REGOLA #1d) + allineata VOIP_SIP_PASS + restart pipeline → registered:true al primo tentativo. Carry S350 = test chiamata audio reale CTO-guidato (REGOLA #23). POI R2 (CI rotto) → R3.`

## Ultimi 5 commit
```
3e46cfc S349: 🟢 SARA LAYER 2 SBLOCCATO — EHIWEB reg_status:200 dopo ~15 sessioni di 403. Mail riattivazione VivaVox Free → root cause reale = password disallineata su iMac voice-agent/.env (main aveva controllato solo ~/.claude/.env globale). Fix: backup .env (REGOLA #1d) + allineata VOIP_SIP_PASS + restart pipeline → registered:true al primo tentativo. Carry S350 = test chiamata audio reale CTO-guidato (REGOLA #23). POI R2 (CI rotto) → R3.
c2219ca S348: R2 investigato — root-cause distribuzione = CI release-full.yml ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm), non release vuota-by-design. v1.0.1 published/0-asset. Handoff S349 con prima azione gh run view --log-failed. EHIWEB 403 invariato.
a8d97ee S347: R1 conversion attribution CHIUSO E2E — D1 sbloccato, migration 0003 applicata prod+test, deploy prod+test, smoke firmato PASS (lead_999→conversion row + licenza)
f31df22 auto-close session e11bc5b2-c3ef-4df9-bdce-4484e4eb11ed @ 2026-06-08T06:53:35Z
217ff49 auto-close session e11bc5b2-c3ef-4df9-bdce-4484e4eb11ed @ 2026-06-08T06:49:48Z
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.manual.md
M	.claude/NEXT_SESSION_PROMPT.md
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01Y9NAfLsFCArFNC2mUJBcXH","type":"tool_result","content":"✖ 17 problems (0 errors, 17 warnings)\n\n✅ Pre-commit checks PASSED\n[master 3e46cfc] S349: 🟢 SARA LAYER 2 SBLOCCATO — EHIWEB reg_status:200 dopo ~15 sessioni di 403. Mail riattivazione VivaVox Free → root cause reale = password disallineata su iMac voice-agent/.env (main aveva controllato solo ~/.claude/.env globale). Fix: backup .env (REGOLA #1d) + allineata VOIP_SIP_PASS + restart pipeline → register
```

## Ultimi turni assistant
```
ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"
```
Se ancora `reg_status:200` → delega a `voice-engineer` il test chiamata reale Sara via harness `voice-agent/scripts/sara_audio_harness.py`, CTO-guidato via TTS (REGOLA #23, mai chiedere a Luke di chiamare). Questo è il **gate vendita REGOLA #21**: Sara testata LIVE via audio sui verticali. Poi R2 (CI `release-full.yml` rotto) → R3.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
