---
paths:
  - "tests/**"
  - "voice-agent/tests/**"
  - "*.test.*"
  - "*.spec.*"
---

# Testing Rules

## Pre-Commit Checklist (MANDATORY)
Run ALL relevant tests before committing:

| Modified | Commands |
|----------|----------|
| Frontend (.tsx/.ts) | `npm run type-check && npm run lint` |
| Rust (.rs) | `cd src-tauri && cargo test` |
| Python (.py) | `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && pytest tests/ -v"` |
| UI changes | `bash scripts/run-e2e-remote.sh gianlucadistasi 192.168.1.2` |

## E2E Testing
- Tool: Playwright + Chromium headless
- Run on iMac via SSH (Tauri needs macOS 12+)
- Config: `playwright.headless.config.ts`
- Tests: `tests/e2e/`

## Task Completion Criteria
A task is NOT complete until:
1. Code written and deployed
2. Tests pass (unit + integration)
3. Manual verification (conversation works, DB records created)
4. Side effects verified (SELECT confirms data)
