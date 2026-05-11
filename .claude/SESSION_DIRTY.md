# SESSION DIRTY — chiusura senza commit auto

Sessione: `0ea0b99a-7a37-42aa-9d0c-4a891e11ac63`  Timestamp: `2026-05-11T18:06:35Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md:341: trailing whitespace.
+Get-AppxPackage *WebView2* 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
M  docs/launch/PRE-LAUNCH-AUDIT.md
A  docs/launch/RUNBOOK-P1-SARA-LIVE-TEST.md
A  docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
