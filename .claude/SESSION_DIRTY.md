# SESSION DIRTY — chiusura senza commit auto

Sessione: `06d96ad2-0b9b-41d9-8a01-7db58a4579bd`  Timestamp: `2026-06-03T19:54:14Z`

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
