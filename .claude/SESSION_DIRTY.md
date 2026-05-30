# SESSION DIRTY — chiusura senza commit auto

Sessione: `498f3d77-1bc4-423f-9a90-d49317b1eafc`  Timestamp: `2026-05-30T20:46:40Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.manual.md
 M .claude/NEXT_SESSION_PROMPT.md
 M .claude/SESSION_DIRTY.md
 m tools/VectCutAPI
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
