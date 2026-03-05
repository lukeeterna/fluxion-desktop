# CoVe 2026 — Playwright UI Verification Pattern

**Created**: 2026-03-05 (sessione 21)
**Purpose**: Enable Claude to autonomously verify UI implementations via Playwright

## Summary

This pattern eliminates `checkpoint:human-verify` for basic UI checks.
Implemented during P0.5 (VoiceAgentSettings integration).

## 3-Layer Model

| Layer | Actor | Scope |
|-------|-------|-------|
| Static | Claude | type-check + grep wiring |
| Playwright | Claude | DOM, interactions, screenshot |
| Human | User | stateful/audio/real-API only |

## Files

| File | Purpose |
|------|---------|
| `e2e-tests/pages/ImpostazioniPage.ts` | Page object for /impostazioni |
| `e2e-tests/tests/impostazioni.spec.ts` | 9 tests covering VoiceAgentSettings |
| `e2e-tests/fixtures/test.fixtures.ts` | `impostazioniPage` fixture added |
| `.claude/get-shit-done/references/verification-patterns.md` | `<ui_playwright_verification>` section |

## Quick Commands

```bash
# Run impostazioni tests (Playwright auto-starts Vite if needed)
cd /Volumes/MontereyT7/FLUXION/e2e-tests
npx playwright test tests/impostazioni.spec.ts --reporter=line

# Run only smoke tests
npx playwright test --grep "@smoke" --reporter=line

# Run voice-settings tests
npx playwright test --grep "@voice-settings" --reporter=line
```

## Test Coverage — impostazioni.spec.ts

| Test | Tag | What it checks |
|------|-----|----------------|
| page loads with heading | @smoke @impostazioni | h1 "Impostazioni" visible |
| no critical console errors | @impostazioni | pageerror events = 0 |
| voice agent section visible | @voice-settings | h2 "Assistente Vocale Sara" |
| status badge present | @voice-settings | "Attivo" or "Non configurata" span |
| groq input is type=password | @voice-settings | input#groq-api-key type=password |
| Testa + Salva buttons present | @voice-settings | both buttons visible |
| screenshot evidence | @voice-settings | reports/screenshots/voice-agent-settings.png |
| empty key → error | @voice-settings | "Inserisci una chiave API" message |
| invalid format → error | @voice-settings | "Formato non valido" message |
| valid gsk_ prefix → warn/ok | @voice-settings | "Formato valido" or "raggiungibile" |
| eye toggle changes type | @voice-settings | password → text on click |

## What Stays Human-Verify

- Save key → restart app → key persists (DB state)
- Groq API real call (rate limits)
- Voice call test (audio)
