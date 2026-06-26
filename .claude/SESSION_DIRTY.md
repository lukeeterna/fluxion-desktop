# SESSION DIRTY — chiusura senza commit auto

Sessione: `c4c3019b-ea56-4fd4-aa46-97a749451aa7`  Timestamp: `2026-06-26T07:25:58Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:34: trailing whitespace.
+Confermo lo **scope**: procedo ad avviare la pipeline Sara sull'iMac e lanciare il test vocale live (delega a `voice-engineer` foreground, REGOLA #27)? 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
