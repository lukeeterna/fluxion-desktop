# SESSION DIRTY — chiusura senza commit auto

Sessione: `3005720a-bae1-4c07-bc9f-6e26db9d530e`  Timestamp: `2026-05-18T08:14:45Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:25: trailing whitespace.
+    chiusura ordinata. 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
