# 🎉 FLUXION Enterprise Test Protocol - COMPLETE & CUSTOMIZED

**Status:** ✅ **DELIVERED - Fully customized for Tauri stack**

---

## 📦 DELIVERABLES (4 files created)

```
docs/testing/
├── FLUXION-TEST-PROTOCOL.md      ✅ Master protocol (Tauri-specific)
├── SEVERITY-POLICY.md            ✅ Bug severity + release gates (GitHub Issues)
├── TEST-MATRIX.md                ✅ 5 critical modules with examples
└── test-suite.yml                ✅ Complete GitHub Actions CI/CD

Location: Copy to .github/workflows/test-suite.yml
```

---

## 🎯 CUSTOMIZATIONS MADE

### ✅ 1. Stack Adapted for Tauri

**Before:** Generic web app protocol  
**After:** Tauri desktop app + Rust backend

**Changes:**
- ✅ Split unit tests: Frontend (Vitest + RTL) + Backend (Rust #[test])
- ✅ Integration tests: Tauri IPC commands + SQLite queries
- ✅ E2E tests: WebDriverIO + @tauri-apps/webdriver (not Playwright)
- ✅ AI Live: HTTP Bridge via port 3001 (already implemented)

### ✅ 2. Real FLUXION Modules

**Before:** Generic Auth, Booking, Payment modules  
**After:** Your actual modules

```
🔴 CRITICA:
  - Calendario & Appuntamenti (booking engine)
  - CRM Clienti (customer data)
  - Fatturazione Elettronica (Italian legal requirement)

🟠 ALTA:
  - Cassa & Scontrini (daily operations)
  - Voice Agent (differentiator)

🟡 MEDIA:
  - Reporting, Sync/Export, UI
```

### ✅ 3. GitHub Issues (No Jira)

**Before:** Jira auto-integration  
**After:** GitHub Issues automation

**Features:**
- ✅ Auto-create issue on test failure (label: `bug/ci-detected`)
- ✅ Test failure includes error log + commit SHA
- ✅ Auto-close issue when fix merged
- ✅ Severity labels: `severity:blocker|critical|major|minor|trivial`
- ✅ Area labels: `area:booking|crm|invoice|cashier|voice|...`

### ✅ 4. Binding to Claude Code

Test pyramid now enforced:
- ✅ Unit tests (frontend + rust) - every commit
- ✅ Integration tests (tauri IPC) - every PR
- ✅ E2E tests (WebDriverIO) - before merge
- ✅ AI Live tests (MCP agent) - nightly + on demand
- ✅ Code quality gates (ESLint strict)

---

## 🚀 IMMEDIATE SETUP (THIS WEEK)

### Step 1: Copy Files (5 min)

```bash
# Create docs structure
mkdir -p .github/workflows

# Copy protocol files
cp FLUXION-TEST-PROTOCOL.md docs/testing/
cp SEVERITY-POLICY.md docs/testing/
cp TEST-MATRIX.md docs/testing/

# Copy CI/CD workflow
cp test-suite.yml .github/workflows/
```

### Step 2: Configure GitHub Secrets (10 min)

In GitHub repo settings → Secrets and variables → Actions:

```
SLACK_WEBHOOK = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
TAURI_PRIVATE_KEY = (existing, if using auto-updates)
TAURI_KEY_PASSWORD = (existing, if using auto-updates)
```

### Step 3: Update package.json scripts (15 min)

```json
{
  "scripts": {
    "test:unit:frontend": "vitest run src/**/*.test.tsx",
    "test:e2e": "wdio run tests/e2e/wdio.config.ts",
    "test:ai-live": "node scripts/ai-live-test.ts",
    "test:ai-live:full": "node scripts/ai-live-test.ts --full-suite",
    "build:tauri": "tauri build --release",
    "lint": "eslint src --max-warnings 0",
    "dev": "tauri dev"
  }
}
```

### Step 4: Verify CI/CD Works (10 min)

```bash
# Test locally
npm run test:unit:frontend
cargo test --lib
cargo test --test '*'

# Push to develop branch
git push origin develop

# Watch GitHub Actions run
# Navigate to: Actions tab → test-suite
```

---

## 📊 WHAT HAPPENS WHEN YOU COMMIT

### On `git push develop` (or create PR to main):

```
1. GitHub Actions triggers test-suite.yml

2. Runs in SEQUENCE:
   ├─ Frontend Unit Tests (Vitest)
   │  └─ Must have coverage >= 80%
   │
   ├─ Rust Unit Tests (cargo test --lib)
   │  └─ Must have coverage >= 75%
   │
   ├─ Integration Tests (cargo test --test '*')
   │  └─ Must all PASS
   │
   ├─ E2E Tests (WebDriverIO - only on macOS)
   │  └─ Must all PASS
   │
   ├─ AI Live Tests (MCP agent - only nightly)
   │  └─ Must all scenarios PASS
   │
   └─ Code Quality (ESLint + TypeScript)
      └─ Must have 0 warnings

3. If ANY fail:
   ├─ GitHub Actions marks build as FAILED
   ├─ Merge blocked (branch protection)
   ├─ Auto-creates GitHub Issue with label "bug/ci-detected"
   └─ Slack alert sent to #releases channel

4. If ALL pass:
   ├─ Merge is allowed
   ├─ PR can be approved + merged
   └─ Feature goes live in next release
```

---

## 📋 WORKFLOW EXAMPLES

### Example 1: You add booking feature

```
1. Create branch: git checkout -b feat/FLX-401-multi-guest

2. Implement feature + tests:
   - Write frontend unit test (Calendar.test.tsx)
   - Write Rust unit test (calendar.rs)
   - Write integration test (booking_integration.rs)
   - Write E2E test (booking.spec.ts)

3. Check test_matrix.md:
   Calendario & Appuntamenti = Unit ✅ + Integration ✅ + E2E ✅ + AI ✅ + Perf ✅

4. Run locally:
   npm run test:unit:frontend
   cargo test --lib
   cargo test --test '*'
   npm run test:e2e

5. git push origin feat/FLX-401-multi-guest

6. GitHub Actions runs full suite
   → If GREEN: can merge
   → If RED: fix and rerun

7. Merge to develop/main
```

### Example 2: AI Test finds bug (nightly run)

```
1. 2 AM CET: Nightly scheduled CI runs
   → All 4 test layers + metrics report

2. AI Live Test detects: "Booking price calculation wrong for 50+ guests"

3. Automatically:
   ├─ Creates GitHub Issue
   │  Title: "🚨 [CI] Test Failed: AI Live Tests"
   │  Labels: bug/ci-detected, severity:critical, area:booking
   │  Assign to: @gianlucadistasi
   │
   └─ Posts Slack alert to #releases
      "FLUXION Test Suite FAILED: AI Live Tests | View Details"

4. You investigate:
   git log --oneline | head -5  # Find recent changes to booking
   npm run test:ai-live  # Reproduce locally

5. Create fix branch:
   git checkout -b fix/FLX-405-booking-price-calc

6. Fix code + add test:
   npm run test:unit:frontend -- --grep "price.*50"  # verify test

7. Push: GitHub Actions runs → GREEN

8. Merge → Issue auto-closes with comment:
   "✅ Fixed in commit abc123"
```

---

## ✅ RELEASE CHECKLIST

Before releasing v1.2.3, verify:

```markdown
[ ] No BLOCKER severity issues open
[ ] No CRITICAL severity issues open (on touched modules)
[ ] All tests PASS:
    [ ] npm run test:unit:frontend -- --coverage (>=80%)
    [ ] cargo test --lib (>=75%)
    [ ] cargo test --test '*' 
    [ ] npm run test:e2e
    [ ] npm run test:ai-live:full
[ ] Code quality: npx eslint src --max-warnings 0
[ ] Performance: app startup < 3sec, booking < 1sec
[ ] CHANGELOG.md updated with:
    - Features added
    - Bugs fixed
    - Known issues (if any)
    - Test results summary
[ ] Sign-off: Gianluca approval
```

If all ✅ → Ready to release!

---

## 🔐 BINDING TO CLAUDE CODE

**Claude, you MUST now:**

1. ✅ Read FLUXION-TEST-PROTOCOL.md before ANY modification
2. ✅ Check TEST-MATRIX.md to see which tests are mandatory
3. ✅ Write required tests (unit/integration/e2e/ai based on module)
4. ✅ Run tests locally before committing:
   ```
   npm run test:unit:frontend
   cargo test --lib
   cargo test --test '*'
   ```
5. ✅ Include in commit message: "Tested: unit✅ rust✅ integration✅"
6. ✅ Do NOT commit if tests RED
7. ✅ Read SEVERITY-POLICY.md for bug levels

**If you violate protocol:**
- ❌ GitHub branch protection BLOCKS merge
- ❌ GitHub Issue auto-created (bug/ci-detected)
- ❌ Slack alert sent
- ❌ Manual override by Gianluca required (rare)

---

## 📈 EXPECTED OUTCOMES (30 days)

| Metrica | Target | Benefit |
|---------|--------|---------|
| Test Coverage | 75%+ core | Zero surprise bugs in prod |
| Bug Escape Rate | < 10% | 90% caught before release |
| Blocker SLA | < 1h | Production stability |
| Release Pass Rate | > 95% | Confidence in deploys |
| Mean Time to Release | 2-3h | Fast iteration |

---

## 🎓 RESOURCES

**Read in this order:**

1. **FLUXION-TEST-PROTOCOL.md** - Overview + testing layers
2. **TEST-MATRIX.md** - Your modules + specific test examples
3. **SEVERITY-POLICY.md** - How bugs are classified + release gates
4. **test-suite.yml** - How CI/CD executes (reference)

**Quick Reference:**

- **Before coding:** Read TEST-MATRIX.md for your module
- **During coding:** Follow testing pyramid in FLUXION-TEST-PROTOCOL.md
- **Before commit:** Run local tests, check they're GREEN
- **On failure:** Read error log, identify issue, fix + retest
- **Release time:** Use checklist in SEVERITY-POLICY.md

---

## 🚀 YOU'RE READY!

The protocol is now **LIVE and BINDING** on FLUXION.

Every modification will be tested automatically. Every bug found by tests will create a GitHub Issue. Every release will be verified against a 7-point checklist.

**Status:**
- ✅ Protocol documentation complete
- ✅ GitHub Actions CI/CD ready (copy to .github/workflows/)
- ✅ Test matrix for 5 modules with examples
- ✅ Claude Code binding instructions in place
- ✅ GitHub Issues automation specified

**Next:** Push these files to repo and configure GitHub secrets.

---

**Created by:** Gianluca di Stasi  
**Date:** 2026-01-09  
**Status:** 🟢 ACTIVE & BINDING  
**Stack:** Tauri + React + Rust + SQLite  
**Next Review:** 2026-02-09

**🎉 Buon testing su FLUXION! 🚀**