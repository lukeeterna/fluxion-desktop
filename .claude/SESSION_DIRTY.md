# SESSION DIRTY — chiusura senza commit auto

Sessione: `ebd74e24-956f-4efd-b21d-6864d3a370f3`  Timestamp: `2026-05-26T18:35:17Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:29: trailing whitespace.
+[{"tool_use_id":"toolu_01L1NiSrFrsJaZbHJ8sTribm","type":"tool_result","content":"/Volumes/MontereyT7/FLUXION/e2e-tests/tests/impostazioni.spec.ts\n  17:57  warning  'impostazioniPage' is defined but never used. Allowed unused args must match /^_/u  @typescript-eslint/no-unused-vars\n\n/Volumes/MontereyT7/FLUXION/e2e-tests/tests/mock-debug.spec.ts\n  13:30  warning  Unexpected any. Specify a different type  @typescript-eslint/no-explicit-any\n  21:39  warning  Unexpected any. Specify a different 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
