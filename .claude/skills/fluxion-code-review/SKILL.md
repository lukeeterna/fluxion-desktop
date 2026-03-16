---
name: fluxion-code-review
description: >
  Enterprise-grade code review skill for FLUXION (Tauri + React + Rust + Python).
  Performs multi-dimensional analysis across 12 quality dimensions with letter-grade
  scoring (A-F), severity classification (CRITICAL/HIGH/MEDIUM/LOW/INFO), and
  actionable findings with file:line references and suggested fixes. Inspired by
  Uber uReview, DeepSource, and Google Critique. Outputs structured review report
  with overall grade, dimension scores, and merge verdict.
---

# FLUXION Code Review — Enterprise Grade

> Modeled after: Uber uReview (multi-stage pipeline) + DeepSource (5-dim report cards) + Google Critique (continuous improvement)
> Research: `.claude/cache/agents/code-reviewer-enterprise-research.md`

## Purpose

Perform a comprehensive, structured code review that produces an **actionable report** with:
- Overall letter grade (A-F) with numeric score (0-100)
- Per-dimension grades across 12 quality dimensions
- Severity-classified findings with file:line and suggested fixes
- Clear merge verdict: APPROVE / APPROVE_WITH_SUGGESTIONS / REQUEST_CHANGES / BLOCK

## When to Use

- Before merging any PR or feature branch
- After completing a significant implementation (>50 lines changed)
- When `/review` or `/code-review` is invoked
- When the user asks to review code, a PR, or recent changes
- As part of GSD verify-work phase

## Review Pipeline (4 Stages — Uber uReview inspired)

### Stage 1: INGESTION
1. Identify the **scope** — what changed? (git diff, specific files, or PR)
2. Read ALL changed files completely — never review without reading
3. Filter out auto-generated files, config-only changes, vendored code
4. Identify the **intent** — what is this change trying to accomplish?

### Stage 2: ANALYSIS (12 Dimensions)
Review each changed file against all applicable dimensions. Only flag issues **introduced by the change**, not pre-existing debt (diff-scoped review).

#### Dimension A: Security (Weight: 20%)
- OWASP Top 10: SQL injection, XSS, CSRF, auth bypass, SSRF
- No hardcoded secrets (API keys, passwords, tokens)
- Input validation on all user/external input
- Parameterized queries (never string interpolation in SQL)
- Proper auth/authz checks on new endpoints
- No sensitive data in logs or error messages
- Dependency CVEs (npm audit / pip audit)

**FLUXION-specific:**
- Tauri IPC: validate all invoke() parameters on Rust side
- SQLite: parameterized queries via sqlx, never format!()
- Voice agent: sanitize user transcription before processing
- No `window.open()` — use `openUrl()` from `@tauri-apps/plugin-opener`

#### Dimension B: Error Handling (Weight: 15%)
- Async errors caught (no unhandled promise rejections)
- Rust: Result<T, E> propagated, no unwrap() in production
- Python: specific exceptions caught, not bare except
- Edge cases: null/undefined, empty arrays, boundary values
- Graceful degradation when services fail
- Timeouts on all network calls
- User-friendly error messages (no stack traces in UI)

#### Dimension C: Architecture (Weight: 12%)
- SOLID principles respected
- Separation of concerns (business logic vs presentation vs infra)
- Consistent abstraction levels within functions
- No circular dependencies
- Module boundaries respected (no reaching into internals)
- Appropriate design patterns (not over-engineered)

**FLUXION-specific:**
- Tauri commands in `src-tauri/src/commands/` — not in lib.rs
- React hooks for data fetching (TanStack Query)
- Voice FSM states in booking_state_machine.py — not in orchestrator
- Italian field names in API: servizio, data, ora, cliente_id

#### Dimension D: Performance (Weight: 12%)
- No N+1 database queries (batch/join instead)
- No O(n^2) where O(n log n) or O(n) exists
- Memory leak prevention (event listener cleanup, ref cleanup)
- Missing cache opportunities
- Bundle size (unnecessary imports, tree-shaking)
- Lazy loading for large resources
- Database indexes on queried columns
- Connection pooling for DB/HTTP

**FLUXION-specific:**
- SQLite WAL mode for concurrent reads
- Voice pipeline latency budget: P95 < 800ms total
- TTS cache for common phrases
- No synchronous IPC blocking UI thread

#### Dimension E: Type Safety (Weight: 10%)
- TypeScript: zero `any`, zero `@ts-ignore`, strict mode
- Rust: proper ownership, borrowing, lifetimes
- Python: type hints on public functions
- Generics used where appropriate
- Null safety: Optional types handled explicitly
- Discriminated unions for state machines

#### Dimension F: Testing (Weight: 10%)
- Critical paths covered (not just happy path)
- Boundary conditions tested (min/max, off-by-one, empty)
- Bug fixes include regression test
- Test independence (no shared mutable state)
- Descriptive test names documenting behavior
- Integration tests for key flows

**FLUXION-specific:**
- Voice: pytest on iMac (Python 3.9)
- Frontend: type-check (tsc --noEmit)
- E2E: Playwright in e2e-tests/
- Always test audio E2E on iMac with real microphone

#### Dimension G: Maintainability (Weight: 8%)
- Cyclomatic complexity < 10 per function (max 15)
- Self-documenting names, consistent conventions
- DRY (no unnecessary duplication, but don't over-abstract)
- Comments explain "why" not "what"
- Functions focused (single responsibility)
- File length reasonable (< 500 lines preferred)

#### Dimension H: API Design (Weight: 5%)
- Proper HTTP methods and status codes
- Backward compatibility (no silent breaking changes)
- Consistent error response format
- Pagination for large collections
- Idempotent where needed

#### Dimension I: Database (Weight: 4%)
- No SELECT * — specify columns
- Proper JOINs, avoid subqueries where JOIN works
- Migration safety: reversible, no data loss
- Transaction boundaries correct
- Schema constraints (FK, UNIQUE, NOT NULL, CHECK)

**FLUXION-specific:**
- Custom migration runner in lib.rs — new migrations must be added explicitly
- SQLite PRAGMA journal_mode=WAL
- Parameterized queries via sqlx::query!() or query_as!()

#### Dimension J: Concurrency (Weight: 2%)
- Race conditions: shared mutable state synchronized
- Async/await: no blocking in async context
- Rust: Send + Sync where needed for Tauri State
- Python: asyncio patterns (no sync in async handler)

#### Dimension K: Accessibility (Weight: 1%)
- Semantic HTML (headings, landmarks, ARIA labels)
- Keyboard navigation for interactive elements
- Color contrast WCAG AA (4.5:1)
- Form labels associated with inputs

#### Dimension L: i18n Readiness (Weight: 1%)
- No hardcoded user-facing strings (future localization)
- Locale-aware date/number formatting
- Italian as primary, structure supports future languages

### Stage 3: SCORING

#### Per-Dimension Grade
```
A  (90-100): Excellent — no issues or only INFO-level
B  (80-89):  Good — minor issues only (LOW severity)
C  (70-79):  Acceptable — some MEDIUM issues
D  (60-69):  Below standard — HIGH issues present
F  (<60):    Failing — CRITICAL issues present
```

#### Overall Score Formula
```
overall = sum(dimension_grade * dimension_weight)

Penalty adjustments:
  Each CRITICAL finding: -20 points (capped at -60)
  Each HIGH finding:     -10 points (capped at -30)
  Each MEDIUM finding:    -3 points (no cap)
  Each LOW finding:       -1 point  (capped at -5)
```

#### Merge Verdict
| Verdict | Condition |
|---------|-----------|
| APPROVE | Overall >= A (90+), zero CRITICAL/HIGH |
| APPROVE_WITH_SUGGESTIONS | Overall >= B (80+), zero CRITICAL, max 2 HIGH |
| REQUEST_CHANGES | Overall >= C (70+) but has HIGH issues that must be fixed |
| BLOCK | Overall < C (70) OR any CRITICAL finding |

### Stage 4: OUTPUT

Use this exact template for the review report:

```markdown
## Code Review Report

**Scope**: [description of what was reviewed]
**Files**: [N files changed, +X/-Y lines]
**Overall Grade**: [LETTER] ([SCORE]/100)
**Verdict**: [APPROVE / APPROVE_WITH_SUGGESTIONS / REQUEST_CHANGES / BLOCK]

### Dimension Scores

| Dimension | Grade | Issues | Weight |
|-----------|-------|--------|--------|
| Security | [A-F] | [count by severity] | 20% |
| Error Handling | [A-F] | [count] | 15% |
| Architecture | [A-F] | [count] | 12% |
| Performance | [A-F] | [count] | 12% |
| Type Safety | [A-F] | [count] | 10% |
| Testing | [A-F] | [count] | 10% |
| Maintainability | [A-F] | [count] | 8% |
| API Design | [A-F] | [count] | 5% |
| Database | [A-F] | [count] | 4% |
| Concurrency | [A-F] | [count] | 2% |
| Accessibility | [A-F] | [count] | 1% |
| i18n | [A-F] | [count] | 1% |

### CRITICAL Issues (must fix before merge)
[numbered list with dimension tag, file:line, description, suggested fix]

### HIGH Priority Issues (should fix before merge)
[numbered list]

### MEDIUM Priority Issues (fix if possible)
[numbered list]

### LOW / Suggestions
[numbered list]

### Positive Highlights
[call out well-done code — Google Critique practice]
```

## Rules (Non-Negotiable)

1. **ALWAYS read all changed files before reviewing** — never review blind
2. **Diff-scoped only** — flag issues in changed code, not pre-existing debt
3. **Every finding must have** file:line reference + suggested fix
4. **Deduplicate** — same pattern flagged once with "N occurrences" note
5. **Educational** — briefly explain WHY each issue matters
6. **Positive highlights required** — at least 1 positive callout per review
7. **No false positives** — if unsure, mark as INFO not MEDIUM
8. **FLUXION-specific rules override general rules** when in conflict
9. **Never approve CRITICAL findings** — always BLOCK or REQUEST_CHANGES
10. **Score honestly** — don't inflate grades. B is good. C is acceptable. A is rare.

## Quick Commands

```bash
# Scope: review recent changes (unstaged + staged)
git diff HEAD

# Scope: review last commit
git diff HEAD~1..HEAD

# Scope: review branch vs master
git diff master...HEAD

# TypeScript check (part of review)
npm run type-check

# ESLint
npx eslint src/ --ext .ts,.tsx

# Python type check (if applicable)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python -m mypy src/ --ignore-missing-imports 2>&1 | tail -20"
```
