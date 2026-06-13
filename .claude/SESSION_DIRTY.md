# SESSION DIRTY — chiusura senza commit auto

Sessione: `c00b7ccf-2c83-42c4-b407-81f5e2ce0595`  Timestamp: `2026-06-13T11:00:05Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:31: trailing whitespace.
+**Housekeeping:** questo file è in Downloads ma dice "io sono il canonico". Se approvi le 3 correzioni, lo promuovo a `.claude/NEXT_SESSION_PROMPT.manual.md` (canonico reale) con dentro le modifiche + il catalogo Sara copiato in `.claude/`. 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
