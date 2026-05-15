# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-15T14:05:38Z`
**Sessione**: `d84071bb-95b3-454d-8a38-73632cbf42b0`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `7e68045 fix(S238-F2): register Python callback threads with pjlib + faulthandler`

## Ultimi 5 commit
```
7e68045 fix(S238-F2): register Python callback threads with pjlib + faulthandler
9e92c68 auto-close session 70638e05-e9a0-48fa-8b39-7cd0a8b9bef5 @ 2026-05-15T08:05:14Z
5a8bf28 chore(S237): close session ORANGE — F1 success status=506784 resolved, new blocker pjmedia clock thread assertion
cf243b2 fix(S237-F1-bis): register pjlib worker thread in audio frame callbacks
685d44c fix(S237-F1): install pjsua2 null audio device to bypass Core Audio open
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
A	.claude/cache/agents/s238/pjsua2-clock-master-pattern.md
M	voice-agent/src/voip_pjsua2.py
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01Qhi8jSZougK7HzbP7NU4Mn","type":"tool_result","content":"PID=14507\n--- health ---\n{\"status\": \"ok\", \"service\": \"FLUXION Voice Agent Enterprise\", \"version\": \"2.1.0\", \"pipeline\": \"4-layer RAG\", \"features\": {\"vad\": true, \"vad_library\": \"silero-or-webrtc\", \"stt\": \"GroqSTT\", \"tts\": \"adaptive\"}}--- log tail ---\n16:05:15 [src.orchestrator] INFO: [Config] HTTP Bridge offline — using SQLite fallback (standalone mode)\n16:05:15 [src.orchestrator]
```

## Ultimi turni assistant
```
**Riassunto fix applicato (commit `7e68045`)**:
- `voice-agent/src/voip_pjsua2.py`: helper `_run_with_pjlib_registration` chiama `libRegisterThread` (idempotente) prima di invocare `on_connected`/`on_disconnected`. Hypothesis: lo spawn thread su `CONFIRMED` toccava `audio_port` via SWIG director → C-side `pj_grp_lock` release cross-thread → assertion `lock.c:279`.
- `faulthandler.enable(all_threads=True)` early: se F2 non basta, prossimo SIGABRT dumpa backtrace ogni thread → identifica thread non registrato residuo (probabili candidati: Python GC, async pool, pipeline workers).
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
