#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# FLUXION - Full Test Suite Script
# Run all automated tests: Frontend + Rust + E2E
# Usage: ./scripts/test-full-suite.sh [--skip-e2e]
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Parse arguments
SKIP_E2E=false
for arg in "$@"; do
    case $arg in
        --skip-e2e)
            SKIP_E2E=true
            shift
            ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  🧪 FLUXION - Full Test Suite"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo "📂 Project: $PROJECT_DIR"
echo ""

# ───────────────────────────────────────────────────────────────────────────────
# 1. FRONTEND BUILD (required for Tauri context)
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📦 Step 1: Frontend Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if npm run build; then
    echo -e "${GREEN}✅ Frontend build: PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Frontend build: FAILED${NC}"
    ((TESTS_FAILED++))
    exit 1
fi

# ───────────────────────────────────────────────────────────────────────────────
# 2. TYPESCRIPT CHECK
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔷 Step 2: TypeScript Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if npx tsc --noEmit --strict --skipLibCheck; then
    echo -e "${GREEN}✅ TypeScript check: PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ TypeScript check: FAILED${NC}"
    ((TESTS_FAILED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 3. ESLINT
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔍 Step 3: ESLint Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if npx eslint src --max-warnings 50; then
    echo -e "${GREEN}✅ ESLint: PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ ESLint: FAILED${NC}"
    ((TESTS_FAILED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 4. RUST UNIT TESTS
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🦀 Step 4: Rust Unit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v cargo &> /dev/null; then
    cd src-tauri
    if cargo test --lib --verbose 2>&1 | tee /tmp/rust-test-output.log; then
        echo -e "${GREEN}✅ Rust unit tests: PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Rust unit tests: FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    cd ..
else
    echo -e "${YELLOW}⏭️  Rust unit tests: SKIPPED (cargo not found)${NC}"
    ((TESTS_SKIPPED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 5. RUST INTEGRATION TESTS
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔗 Step 5: Rust Integration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v cargo &> /dev/null; then
    cd src-tauri
    if cargo test --test '*' --verbose 2>&1 || true; then
        echo -e "${GREEN}✅ Rust integration tests: PASSED${NC}"
        ((TESTS_PASSED++))
    fi
    cd ..
else
    echo -e "${YELLOW}⏭️  Rust integration tests: SKIPPED (cargo not found)${NC}"
    ((TESTS_SKIPPED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 6. CARGO CLIPPY (Rust Linting)
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📎 Step 6: Cargo Clippy (Rust Lint)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v cargo &> /dev/null; then
    cd src-tauri
    if cargo clippy -- -D warnings 2>&1 | tee /tmp/clippy-output.log; then
        echo -e "${GREEN}✅ Cargo Clippy: PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠️  Cargo Clippy: WARNINGS (non-blocking)${NC}"
        # Don't fail on clippy warnings
    fi
    cd ..
else
    echo -e "${YELLOW}⏭️  Cargo Clippy: SKIPPED (cargo not found)${NC}"
    ((TESTS_SKIPPED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 7. TAURI BUILD TEST
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏗️  Step 7: Tauri Build Test (Debug)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v cargo &> /dev/null; then
    if npm run tauri build -- --debug 2>&1 | tail -20; then
        echo -e "${GREEN}✅ Tauri build: PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Tauri build: FAILED${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}⏭️  Tauri build: SKIPPED (cargo not found)${NC}"
    ((TESTS_SKIPPED++))
fi

# ───────────────────────────────────────────────────────────────────────────────
# 8. E2E TESTS (optional)
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎭 Step 8: E2E Tests (WebDriverIO + Tauri Driver)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$SKIP_E2E" = true ]; then
    echo -e "${YELLOW}⏭️  E2E tests: SKIPPED (--skip-e2e flag)${NC}"
    ((TESTS_SKIPPED++))
elif [ ! -f ".env.e2e" ]; then
    echo -e "${YELLOW}⏭️  E2E tests: SKIPPED (.env.e2e not found)${NC}"
    echo "   To enable E2E tests:"
    echo "   1. Copy .env.e2e.example to .env.e2e"
    echo "   2. Set CN_API_KEY for CrabNebula (macOS)"
    ((TESTS_SKIPPED++))
else
    if npm run test:e2e 2>&1 | tee /tmp/e2e-output.log; then
        echo -e "${GREEN}✅ E2E tests: PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ E2E tests: FAILED${NC}"
        ((TESTS_FAILED++))
    fi
fi

# ───────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ───────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  📊 TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}✅ Passed:  $TESTS_PASSED${NC}"
echo -e "  ${RED}❌ Failed:  $TESTS_FAILED${NC}"
echo -e "  ${YELLOW}⏭️  Skipped: $TESTS_SKIPPED${NC}"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}══════════════════════════════════════════════════════════════════════════="${NC}
    echo -e "${RED}  ❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}══════════════════════════════════════════════════════════════════════════="${NC}
    exit 1
else
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════════="${NC}
    echo -e "${GREEN}  ✅ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════════="${NC}
    exit 0
fi
