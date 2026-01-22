#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# FLUXION - Headless E2E Test Runner for macOS via SSH
# Uses Playwright + Vite (NOT tauri-driver)
# ═══════════════════════════════════════════════════════════════════

set -e

# ========== CONFIGURATION ==========
REMOTE_USER="${1:-gianlucadistasi}"
REMOTE_HOST="${2:-192.168.1.9}"
REMOTE_ADDR="$REMOTE_USER@$REMOTE_HOST"
REMOTE_PATH="/Volumes/MacSSD - Dati/fluxion"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  FLUXION E2E Tests - Headless via SSH"
echo "═══════════════════════════════════════════════════════════════════"
echo "  Target: $REMOTE_ADDR"
echo "  Path: $REMOTE_PATH"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# ========== PHASE 1: CLEANUP ==========
echo "🛑 Phase 1: Cleaning up previous processes..."
ssh "$REMOTE_ADDR" "pkill -f 'vite' 2>/dev/null || true; pkill -f 'playwright' 2>/dev/null || true; sleep 1" || true

# ========== PHASE 2: VERIFY/INSTALL PLAYWRIGHT ==========
echo ""
echo "🔍 Phase 2: Verifying Playwright installation..."

ssh "$REMOTE_ADDR" "cd '$REMOTE_PATH' && npm list @playwright/test 2>/dev/null" || {
    echo "📦 Installing Playwright..."
    ssh "$REMOTE_ADDR" "cd '$REMOTE_PATH' && npm install --save-dev @playwright/test"
    ssh "$REMOTE_ADDR" "cd '$REMOTE_PATH' && npx playwright install webkit"
}

# ========== PHASE 3: SYNC FILES ==========
echo ""
echo "📥 Phase 3: Syncing test files..."

# Sync playwright config
scp "$(dirname "$0")/../playwright.headless.config.ts" "$REMOTE_ADDR:$REMOTE_PATH/" 2>/dev/null || true

# Sync test files
scp -r "$(dirname "$0")/../tests/e2e" "$REMOTE_ADDR:$REMOTE_PATH/tests/" 2>/dev/null || true

# ========== PHASE 4: RUN TESTS ==========
echo ""
echo "🧪 Phase 4: Running Playwright tests (headless WebKit)..."
echo "───────────────────────────────────────────────────────────────────"

ssh -t "$REMOTE_ADDR" "cd '$REMOTE_PATH' && \
    export PLAYWRIGHT_HEADLESS=1 && \
    npx playwright test --config=playwright.headless.config.ts --reporter=list"

TEST_EXIT=$?

# ========== PHASE 5: COPY RESULTS ==========
echo ""
echo "───────────────────────────────────────────────────────────────────"
echo "📋 Phase 5: Copying test results..."

mkdir -p test-results 2>/dev/null || true
scp -r "$REMOTE_ADDR:$REMOTE_PATH/test-results/*" test-results/ 2>/dev/null || true

# ========== PHASE 6: REPORT ==========
echo ""
if [ -f "test-results/junit.xml" ]; then
    TOTAL=$(grep -o '<testcase' test-results/junit.xml 2>/dev/null | wc -l | tr -d ' ')
    FAILURES=$(grep -c '<failure' test-results/junit.xml 2>/dev/null || echo 0)
    PASSED=$((TOTAL - FAILURES))

    echo "═══════════════════════════════════════════════════════════════════"
    echo "  TEST RESULTS"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  Total:  $TOTAL"
    echo "  Passed: $PASSED"
    echo "  Failed: $FAILURES"
    echo ""
    echo "  Reports:"
    echo "    JUnit: test-results/junit.xml"
    echo "    HTML:  test-results/html/index.html"
    echo "═══════════════════════════════════════════════════════════════════"

    if [ "$FAILURES" -eq 0 ]; then
        echo ""
        echo "  ✅ ALL TESTS PASSED!"
        echo ""
    fi
else
    echo "⚠️  No JUnit results found"
fi

# ========== CLEANUP ==========
echo "🧹 Cleaning up..."
ssh "$REMOTE_ADDR" "pkill -f 'vite' 2>/dev/null || true" 2>/dev/null || true

exit $TEST_EXIT
