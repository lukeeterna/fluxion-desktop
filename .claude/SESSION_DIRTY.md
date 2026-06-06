# SESSION DIRTY — chiusura senza commit auto

Sessione: `a122c0e0-1cc6-4c28-b5d2-62e7fe4ec9c0`  Timestamp: `2026-06-06T15:48:23Z`

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
