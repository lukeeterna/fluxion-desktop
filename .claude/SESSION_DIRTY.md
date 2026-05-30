# SESSION DIRTY — chiusura senza commit auto

Sessione: `195f227e-f70a-4885-b387-5c22b8aede0a`  Timestamp: `2026-05-30T06:54:42Z`

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
