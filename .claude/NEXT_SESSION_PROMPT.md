# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-08T07:35:57Z`
**Sessione**: `07281532-9fe8-4d34-8109-5a8eb43df9d0`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `327c140 S350: pre-flight test audio Sara — reg_status:200 VERDE confermato (1a volta da ~15 sessioni), test audio reale carry. Chiusura ordinata per context budget 61%->64% (vincolo #7): stato + step ripartenza in NEXT_SESSION_PROMPT.md, memoria agent voice-engineer aggiornata con fatto strutturale (provider reg verde = pre-req per ipotesi anti-crash via rete vs loopback SIGABRT).`

## Ultimi 5 commit
```
327c140 S350: pre-flight test audio Sara — reg_status:200 VERDE confermato (1a volta da ~15 sessioni), test audio reale carry. Chiusura ordinata per context budget 61%->64% (vincolo #7): stato + step ripartenza in NEXT_SESSION_PROMPT.md, memoria agent voice-engineer aggiornata con fatto strutturale (provider reg verde = pre-req per ipotesi anti-crash via rete vs loopback SIGABRT).
fa157ce auto-close session 0153d7de-e4a0-4735-9588-2dd934e54d67 @ 2026-06-08T07:31:43Z
3e46cfc S349: 🟢 SARA LAYER 2 SBLOCCATO — EHIWEB reg_status:200 dopo ~15 sessioni di 403. Mail riattivazione VivaVox Free → root cause reale = password disallineata su iMac voice-agent/.env (main aveva controllato solo ~/.claude/.env globale). Fix: backup .env (REGOLA #1d) + allineata VOIP_SIP_PASS + restart pipeline → registered:true al primo tentativo. Carry S350 = test chiamata audio reale CTO-guidato (REGOLA #23). POI R2 (CI rotto) → R3.
c2219ca S348: R2 investigato — root-cause distribuzione = CI release-full.yml ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm), non release vuota-by-design. v1.0.1 published/0-asset. Handoff S349 con prima azione gh run view --log-failed. EHIWEB 403 invariato.
a8d97ee S347: R1 conversion attribution CHIUSO E2E — D1 sbloccato, migration 0003 applicata prod+test, deploy prod+test, smoke firmato PASS (lead_999→conversion row + licenza)
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
M	.claude/agent-memory/voice-engineer/MEMORY.md
A	.claude/agent-memory/voice-engineer/project_sara_layer2_audio_gate_s350.md
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01PZCkR3G45npYHXfyMHGkYv","type":"tool_result","content":[{"type":"text","text":"Chiusura ordinata completata. Commit `327c140`.\n\n## Report S350 (chiusura ordinata per context budget)\n\n**Esito**: pre-flight completato e VERDE, ma il test audio vero e proprio NON è stato eseguito — il mandato VOS context budget (vincolo #7, salito a 64%) ha imposto chiusura ordinata prima di iniziare il task multi-step (lettura harness → genera WAV → chiamata SIP → cattura/tras
```

## Ultimi turni assistant
```
**Nota da verificare a S351**: l'agente ha scritto `.claude/NEXT_SESSION_PROMPT.md`, ma il file canonico per REGOLA #13 è `.claude/NEXT_SESSION_PROMPT.manual.md` (quello che ho letto a inizio sessione). Da riconciliare a inizio prossima sessione.
**Prompt di ripartenza S351**: `/Volumes/MontereyT7/FLUXION/.claude/NEXT_SESSION_PROMPT.md`
**Prima azione S351 — concreta, per evitare la ricaduta di oggi**: ri-conferma `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` (se 403 → BLOCKED-ON Luke→EHIWEB, non re-diagnosticare). Se 200 → **apri sessione fresca e delega SUBITO l'intero test all'agente come PRIMA azione** (non dopo aver consumato context leggendo handoff lunghi), così l'agente ha budget pieno per: leggere harness → generare WAV → chiamare Sara via rete provider → catturare/trascrivere RTP → verdetto pertinenza. Poi R2 (CI `release-full.yml` rotto, `gh run view 25328286560 --log-failed`) → R3.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
