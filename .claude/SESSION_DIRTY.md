# SESSION DIRTY — chiusura senza commit auto

Sessione: `7849686e-095a-4672-aa77-554b58888ad5`  Timestamp: `2026-06-08T15:52:36Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:25: trailing whitespace.
+[{"tool_use_id":"toolu_0159xqkUNYdgF2tKueYQA69J","type":"tool_result","content":"🔍 Fluxion Pre-Commit Checks...\n⚙️  Formatting Rust...\n⚠️  cargo non disponibile, skip Rust formatting check\n📘 Type-checking TypeScript...\nnpm warn Unknown project config \"PUPPETEER_SKIP_DOWNLOAD\". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.\nnpm warn Unknown project config \"PUPPETEER_SKIP_CHROMIUM_DOWNLOAD\". This will stop working 
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
 M vos-out/decisions.jsonl
?? .claude/SESSION_DIRTY.md
?? voice-agent/docs/pjsua2-ndebug-build.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
