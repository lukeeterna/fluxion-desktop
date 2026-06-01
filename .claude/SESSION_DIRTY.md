# SESSION DIRTY — chiusura senza commit auto

Sessione: `498f3d77-1bc4-423f-9a90-d49317b1eafc`  Timestamp: `2026-05-30T21:24:59Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:30: trailing whitespace.
+**Ma questo è un problema di processo, non lo giustifico.** Il workflow FLUXION (GSD) dice che PLAN.md è il documento canonico. Averlo lasciato driftare mentre lo stato vero si sparpaglia negli handoff è esattamente il pattern di drift che dovrei evitare (REGOLA #11). 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
