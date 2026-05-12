# SESSION DIRTY — chiusura senza commit auto

Sessione: `8ee36ed2-a5c3-4698-8dbe-16bc4c91a12c`  Timestamp: `2026-05-12T16:07:58Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:25: trailing whitespace.
+  REGOLA #7: CI gate reali via self-hosted, mai offline shortcut.  
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
