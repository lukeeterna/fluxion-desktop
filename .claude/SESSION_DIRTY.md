# SESSION DIRTY — chiusura senza commit auto

Sessione: `bdef33c4-0a6f-4f31-82e6-e9c6b483672e`  Timestamp: `2026-06-23T20:17:10Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.manual.md
 M .claude/NEXT_SESSION_PROMPT.md
 M .claude/SESSION_DIRTY.md
 M .claude/session_state.md
 M fluxion-proxy/src/routes/stripe-webhook.ts
 m tools/VectCutAPI
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
