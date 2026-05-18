# SESSION DIRTY — chiusura senza commit auto

Sessione: `d65a057c-3614-4efd-aa36-ed567565edd2`  Timestamp: `2026-05-18T06:55:55Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:25: trailing whitespace.
+  --- 
.claude/NEXT_SESSION_PROMPT.md:31: trailing whitespace.
+**Coerenza ai vincoli**: v2 ora rispetta #2 (ricerca attiva audit grep), #4 (critica strutturale step 2.5 gap noto), #6 (no ARANCIONE), #7 (gate context >50%), #10 (output verificato — query SQL concrete). 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 M .claude/SESSION_DIRTY.md
 m tools/VectCutAPI
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
