# SESSION DIRTY — chiusura senza commit auto

Sessione: `dc128c99-5c69-44da-aea3-c9bc18c9f214`  Timestamp: `2026-06-04T15:06:16Z`

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
