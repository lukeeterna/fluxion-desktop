# 📊 FLUXION Test Protocol - DEPLOYMENT GUIDE (Free Plan Optimized)

> **GitHub Free Plan Compliance** + Full Enterprise Testing
> Versione finale ottimizzata per costi

---

## 🎯 VERSIONI DISPONIBILI

### ✅ **Versione Consigliata: Free Plan Optimized** (QUESTO FILE)
- Adatta al GitHub **Free tier** (2000 min/mese)
- Costi: **~$0**
- Coverage: **Unit + Integration + AI Live** (E2E solo su release)
- Monthly cost: ~1550 min (77.5% of quota)

### ⚠️ **Versione Enterprise** (test-suite.yml - ignore)
- E2E su macOS ad ogni PR
- AI Live su ogni push
- Costi: **$50-100+/mese** (over quota)
- ❌ Non consigliata per Gianluca

**Usa: `test-suite-free.yml` → rinominare a `test-suite.yml` quando deployato**

---

## 📦 DELIVERABLES FINALI (5 file)

```
docs/testing/
├── FLUXION-TEST-PROTOCOL.md       ✅ Master protocol (Tauri-specific)
├── SEVERITY-POLICY.md             ✅ Bug severity + release gates
├── TEST-MATRIX.md                 ✅ 5 critical modules
├── README-PROTOCOL.md             ✅ Setup guide
└── .github/workflows/
    └── test-suite.yml             ✅ test-suite-free.yml (use this)
```

---

## 🚀 QUICK SETUP (< 30 MIN)

### Step 1: Copy Files to Repo

```bash
# Create directories
mkdir -p docs/testing .github/workflows

# Copy documentation
cp FLUXION-TEST-PROTOCOL.md docs/testing/
cp SEVERITY-POLICY.md docs/testing/
cp TEST-MATRIX.md docs/testing/
cp README-PROTOCOL.md docs/testing/

# Copy optimized CI/CD workflow
cp test-suite-free.yml .github/workflows/test-suite.yml
```

### Step 2: Create GitHub Labels

In GitHub repo → Settings → Labels → Create:

```
bug/ci-detected          (color: 🔴 red)
severity:high            (color: 🟠 orange)
severity:critical        (color: 🔴 red)
release                  (color: 🟦 blue)
area:booking             (color: 🟨 yellow)
area:crm                 (color: 🟨 yellow)
area:invoice             (color: 🟨 yellow)
area:cashier             (color: 🟨 yellow)
area:voice               (color: 🟨 yellow)
```

### Step 3: Configure GitHub Secrets

GitHub repo → Settings → Secrets and variables → Actions → New repository secret:

```
Name: SLACK_WEBHOOK
Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 4: Update package.json Scripts

```json
{
  "scripts": {
    "test:unit:frontend": "vitest run src/**/*.test.tsx",
    "test:ai-live": "node scripts/ai-live-test.ts",
    "test:ai-live:full": "node scripts/ai-live-test.ts --full-suite",
    "build:tauri": "tauri build --release",
    "dev": "tauri dev"
  }
}
```

### Step 5: Test Locally

```bash
# Test before push
npm run test:unit:frontend
cargo test --lib
npx eslint src --max-warnings 0

# Push to develop
git push origin develop

# Watch: GitHub Actions → test-suite → fast-check
```

---

## 🎬 HOW IT WORKS

### 3 Different Pipelines Based on Event

```
┌─────────────────────────────────────────────────────────────────┐
│ PUSH develop → fast-check (5 min) ⚡                            │
│                                                                 │
│ ✅ Frontend unit tests (Vitest)                                │
│ ✅ Rust unit tests (cargo test --lib)                          │
│ ✅ Code quality (ESLint strict, TypeScript)                    │
│                                                                 │
│ Cost: 5 min quota                                              │
│ On Failure: Slack alert (quick feedback)                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PR to main → full-suite (15 min) 🧪                            │
│                                                                 │
│ ✅ Frontend unit tests + coverage (≥80%)                       │
│ ✅ Rust unit tests + coverage (≥75%)                           │
│ ✅ Integration tests (Tauri IPC)                               │
│ ✅ E2E simulation (component tests, no browser)                │
│ ✅ Code quality gates                                          │
│                                                                 │
│ Cost: 15 min quota                                             │
│ On Failure: Auto-create GitHub Issue                          │
│ Blocks merge if tests fail                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PR to main + "release" label → full-suite + release-           │
│ verification on macOS (45 min) 🚀                              │
│                                                                 │
│ ✅ All above +                                                 │
│ ✅ Real E2E tests (WebDriverIO) on macOS                       │
│ ✅ Build Tauri release binary                                  │
│ ✅ Full test suite on native platform                          │
│                                                                 │
│ Cost: 300 min quota (macOS = 10x multiplier)                   │
│ Only runs ~2x per month (on releases)                          │
│ On Success: Slack ✅ "Ready to release"                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Nightly (2 AM CET) → nightly-ai-tests (10 min) 🤖             │
│                                                                 │
│ ✅ Start Tauri app in headless mode                            │
│ ✅ Run 4 AI Live test scenarios (Booking, CRM, Data, Error)   │
│ ✅ Upload test report                                          │
│ ✅ Slack notification                                          │
│                                                                 │
│ Cost: 10 min quota per night                                   │
│ Schedule: Daily at 2 AM CET                                    │
│ Frequency: 30 nights/month = 300 min                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 COST COMPARISON

### ❌ Original (test-suite.yml)

```
Per day (5 commits/day):
  5 × fast-check 30min = 150 min
  1 × full-suite 15min = 15 min
  1 × nightly = 10 min
────────────────────
  Total: ~175 min/day
  Monthly: 175 × 20 = 3500 min (OVER QUOTA!)

Cost: $50-100/month (with macOS)
Status: ❌ OVER BUDGET
```

### ✅ Optimized (test-suite-free.yml)

```
Per month:
  100 fast-checks × 5 min = 500 min
  10 full-suites × 15 min = 150 min
  30 nightly AI × 10 min = 300 min
  2 releases × 300 min = 600 min
────────────────────────
  Total: ~1550 min
  Free limit: 2000 min

Usage: 77.5% of quota
Buffer: 450 min (22%)

Cost: $0 (within free tier)
Status: ✅ SAFE
```

---

## 📈 MONTHLY TIMELINE

```
Week 1-4 (repeating pattern):
├─ Mon-Fri: 5 commits/day × fast-check (5 min) = 125 min
├─ Wed: 1 PR to main × full-suite (15 min) = 15 min
├─ Nightly: 7 days × AI tests (10 min) = 70 min
└─ Weekly subtotal: ~210 min

Month total:
  4 weeks × 210 = 840 min (fast + AI)
  2 releases × 300 = 600 min (macOS E2E)
  ──────────────────
  Total: ~1440 min ✅ (within 2000 limit)
```

---

## 🔧 WHEN TO USE EACH JOB

### fast-check (Every dev push)

**Trigger:** `git push origin develop`

```bash
$ git commit -m "feat: add new booking feature"
$ git push origin develop

→ GitHub Actions: fast-check
  Duration: 5 min
  Cost: 5 min quota

Gets you instant feedback before PR
```

**When fails:**
- Slack alert to you
- Fix locally: `npm run test:unit:frontend && cargo test --lib`
- Push again

**When passes:**
- You can create a PR to main

### full-suite (Every PR to main)

**Trigger:** `git push origin + create PR to main`

```bash
$ git push origin feat/new-feature
$ GitHub: Create PR to main

→ GitHub Actions: full-suite
  Duration: 15 min
  Cost: 15 min quota

Full test suite runs
Merge blocked if fails
Auto-creates issue if failed
```

**When passes:**
- You can merge PR
- Feature goes live in next release

### release-verification (Only on releases)

**Trigger:** PR to main + add "release" label + merge

```bash
$ git push origin release/v1.2.3
$ Create PR to main
$ Add "release" label
$ GitHub Actions: release-verification

→ macOS E2E tests run
  Duration: 30+ min
  Cost: 300 min quota (but only 2x/month)

If GREEN: Slack ✅ "Ready to release"
```

### nightly-ai-tests (Every night at 2 AM CET)

**Trigger:** Cron job (automated)

```
2 AM CET every day:
→ GitHub Actions: nightly-ai-tests
  Duration: 10 min
  Cost: 10 min quota

Runs 4 AI Live scenarios
Uploads report
Posts Slack notification
```

**What it tests:**
- Scenario A: Booking workflow
- Scenario B: CRM data integrity
- Scenario C: Data consistency
- Scenario D: Error handling

---

## ✅ VERIFICATION CHECKLIST

### Before First Deployment

```
[ ] Files copied to repo:
    [ ] docs/testing/FLUXION-TEST-PROTOCOL.md
    [ ] docs/testing/SEVERITY-POLICY.md
    [ ] docs/testing/TEST-MATRIX.md
    [ ] docs/testing/README-PROTOCOL.md
    [ ] .github/workflows/test-suite.yml (from test-suite-free.yml)

[ ] GitHub configuration:
    [ ] Labels created (bug/ci-detected, severity:*, area:*, release)
    [ ] Secret SLACK_WEBHOOK added
    [ ] Branch protection enabled on main (require PR reviews)
    [ ] Status checks configured (test-suite must pass)

[ ] package.json scripts:
    [ ] test:unit:frontend ✅
    [ ] test:ai-live ✅
    [ ] test:ai-live:full ✅
    [ ] build:tauri ✅
    [ ] dev ✅

[ ] Local testing:
    [ ] npm run test:unit:frontend → GREEN
    [ ] cargo test --lib → GREEN
    [ ] npx eslint src → 0 warnings
```

### First Week

```
Day 1:
[ ] Push to develop
[ ] Verify fast-check runs and passes
[ ] Check Slack notification (or lack thereof)

Day 3:
[ ] Create PR to main
[ ] Verify full-suite runs and passes
[ ] Verify merge not blocked

Day 5:
[ ] Monitor nightly run at 2 AM
[ ] Check AI test report
[ ] Verify Slack notification received
```

---

## 🎓 PROTOCOL SUMMARY

### When You Code

1. **Before coding:** Read TEST-MATRIX.md
   - See which tests are mandatory for your module
   - Examples for Calendario, CRM, Fatturazione provided

2. **During coding:** Write tests alongside code
   - Unit tests: frontend + rust
   - Integration tests: Tauri IPC
   - E2E: only for critical flows

3. **Before push:** Run locally
   ```bash
   npm run test:unit:frontend
   cargo test --lib
   npx eslint src --max-warnings 0
   ```

4. **After push:** GitHub Actions runs fast-check
   - 5 min feedback
   - If GREEN → ready for PR
   - If RED → fix + repush

5. **Creating PR:** Describe tests added
   ```
   ## Tests Added
   - Frontend unit: 5 scenarios (availability, overbooking, pricing)
   - Rust unit: 3 scenarios (booking creation, cancellation, occupancy)
   - Integration: 2 scenarios (DB persistence, IPC commands)
   ```

6. **PR review:** full-suite runs
   - 15 min verification
   - Merge blocked if fails
   - Can merge when GREEN + approved

### When Releasing

1. **Before release:** Check SEVERITY-POLICY.md
   ```
   [ ] No BLOCKER open
   [ ] No CRITICAL open (on touched modules)
   [ ] All tests PASS (local)
   [ ] Coverage >= 75%
   ```

2. **Create release PR:** Add "release" label

3. **GitHub Actions:** release-verification runs
   - Full suite on macOS (30 min)
   - E2E tests with real browser
   - If GREEN: proceed to release

4. **Release:** Build & deploy
   - Update version
   - Create git tag
   - Build Tauri release binary
   - Announce in Slack

---

## 📞 SUPPORT

### Issue: "Fast-check failed"

```bash
# Reproduce locally
npm run test:unit:frontend
cargo test --lib
npx eslint src --max-warnings 0

# Find error, fix code, re-run tests, push
```

### Issue: "Full-suite failed on PR"

```
GitHub Issue auto-created
 → Look at "bug/ci-detected" issues
 → Review error log in Actions run
 → Fix code, push, actions re-runs automatically
```

### Issue: "Nightly AI test failed"

```
Check Slack notification from @github
 → Review test-reports/ai-live/ artifact
 → Identify which scenario failed (Booking, CRM, Data, Error)
 → Create fix branch, add test, push to develop
```

### Issue: "Over quota?"

```
Check GitHub repo → Actions → Billing
 Should show ~1550 min/month (safe)

If over:
 - Check for accidentally triggered expensive jobs
 - Review workflows for inefficiencies
 - Consider reducing nightly frequency if needed
```

---

## 🚀 NEXT STEPS

### This Week
```
1. Copy files to repo
2. Create GitHub labels
3. Add SLACK_WEBHOOK secret
4. Test with first push to develop
5. Create first PR to main
```

### Next Week
```
1. Let nightly run (2 AM)
2. Review AI test report
3. Fix any issues found
4. Prepare first release with label
5. Watch release-verification run
```

### Ongoing
```
1. Before each feature: read TEST-MATRIX.md
2. Run tests locally before push
3. Review coverage reports monthly
4. Monthly release using full checklist
5. Quarterly review of test strategy
```

---

## 📚 KEY DOCUMENTS (In Order)

1. **This file** - Deployment & cost optimization
2. **FLUXION-TEST-PROTOCOL.md** - Testing pyramid & layers
3. **TEST-MATRIX.md** - Specific modules & test examples
4. **SEVERITY-POLICY.md** - Bug levels & release gates

**Quick Reference during coding:**
- TEST-MATRIX.md: "What tests do I need for this module?"
- FLUXION-TEST-PROTOCOL.md: "How do I write each test type?"
- SEVERITY-POLICY.md: "How do I classify this bug?"

---

**Document:** FLUXION Test Protocol - Deployment Guide (Free Plan)
**Date:** 2026-01-09
**Status:** ✅ APPROVED & READY
**Cost:** $0 (GitHub Free Tier)
**Monthly Quota:** ~1550 min / 2000 min (77.5%)
**Buffer:** 450 min (22%)

**🎉 You're ready to deploy! 🚀**
