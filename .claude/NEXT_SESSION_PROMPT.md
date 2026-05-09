# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-09T17:02:14Z`
**Sessione**: `d96ed01b-62af-43dd-a24f-203994f44085`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `f2b0f8d auto-close S192-bis: token CF rotati + chiusura ordinata context 66%`

## Ultimi 5 commit
```
f2b0f8d auto-close S192-bis: token CF rotati + chiusura ordinata context 66%
f1ad32b docs(S192): closure session — secret removal + push origin sbloccato
404f6f8 feat(S191 D-2 recovery): IPC bench PASS 3/3 — Gate 3 D-2 chiuso
473d16e feat(S191 D-2/D-3 partial): Voice TTS bench FAIL P95 867ms + IPC bench in progress
7525442 feat(S190 D-1): SQLite EXPLAIN audit clienti 1000 — 8/8 PASS no migration
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
A	.claude/SESSION_DIRTY.md
M	HANDOFF.md
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01KLp4VdBUa88vEGBaoWs3Jo","type":"tool_result","content":"=== tts.py model resolution ===\n                    venv_bin_exe,\n                    Path(sys.executable).parent.parent / \"Scripts\" / \"piper.exe\",\n                    Path.home() / \"AppData\" / \"Local\" / \"Programs\" / \"piper\" / \"piper.exe\",\n                    Path(\"C:/Program Files/piper/piper.exe\"),\n                ]\n            else:\n                possible_paths = [\n                    ve
```

## Ultimi turni assistant
```
3. **Pattern errore noto**: latenza Piper PyInstaller è ~2-5x peggio del binary CLI standalone (Python startup overhead). Se P95 con pip-piper rimane >800ms, serve switch a binary GitHub release (Architettura promette ~50ms — verificabile solo con bench reale).
4. **Sovradimensiono?**: SI — sto pianificando rebuild sidecar (~10 min) prima di confermare bench OK. **Step 4 PRIMA di Step 5**: se bench Piper su venv corrente FAIL, niente rebuild fino a fix latency.
**Conferma scope o aggiungo deviazioni?** (es. anche P3 PRE-LAUNCH-AUDIT in stessa sessione, o solo D-3?)
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
