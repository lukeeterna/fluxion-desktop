# SESSION DIRTY — chiusura senza commit auto

Sessione: `4301b617-8362-4d72-82c5-1980d9e3fbc5`  Timestamp: `2026-06-01T17:22:42Z`

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
