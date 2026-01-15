#!/bin/bash
# FLUXION Integration Tests - Master Runner

echo "=============================================="
echo "FLUXION Integration Tests - Start"
echo "=============================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSED=0
FAILED=0

run_test() {
    local name=$1
    local cmd=$2
    echo ""
    echo "[$((PASSED + FAILED + 1))] $name..."
    echo "----------------------------------------------"
    if eval "$cmd"; then
        ((PASSED++))
        echo "Status: PASS"
    else
        ((FAILED++))
        echo "Status: FAIL"
    fi
}

# Test 1: Voice Pipeline
run_test "Voice Pipeline E2E" "python3 $SCRIPT_DIR/test-voice-pipeline.py"

# Test 2: HTTP Bridge
run_test "HTTP Bridge" "python3 $SCRIPT_DIR/test-http-bridge.py"

# Test 3: SQLite Database
run_test "SQLite Database" "python3 $SCRIPT_DIR/test-sqlite-connection.py"

# Test 4: WhatsApp Webhook (optional - requires n8n running)
if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
    run_test "WhatsApp Webhook" "bash $SCRIPT_DIR/test-whatsapp-webhook.sh"
else
    echo ""
    echo "[SKIP] WhatsApp Webhook - n8n not running"
fi

# Summary
echo ""
echo "=============================================="
echo "FLUXION Integration Tests - Summary"
echo "=============================================="
echo ""
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "Status: ALL TESTS PASSED"
    exit 0
else
    echo "Status: SOME TESTS FAILED"
    exit 1
fi
