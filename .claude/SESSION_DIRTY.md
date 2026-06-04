# SESSION DIRTY — chiusura senza commit auto

Sessione: `c3c98f94-55ac-4ade-b90a-2b3560545abe`  Timestamp: `2026-06-04T11:37:50Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 M .claude/SESSION_DIRTY.md
 m tools/VectCutAPI
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
