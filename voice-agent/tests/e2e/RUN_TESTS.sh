#!/bin/bash
# Quick runner for multi-turn conversation tests
# Usage: bash tests/e2e/RUN_TESTS.sh [--verbose] [--class TestClassName] [--remote]

set -e

VERBOSE=""
TEST_CLASS=""
REMOTE=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose)
      VERBOSE=1
      shift
      ;;
    --class)
      TEST_CLASS="::$2"
      shift 2
      ;;
    --remote)
      REMOTE=1
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

TEST_FILE="tests/e2e/test_multi_turn_conversations.py${TEST_CLASS}"

if [ $REMOTE -eq 1 ]; then
  echo "Running tests on iMac..."
  VERBOSE_ENV=""
  [ -n "$VERBOSE" ] && VERBOSE_ENV="VERBOSE=1 "
  ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && ${VERBOSE_ENV}python -m pytest ${TEST_FILE} -v --tb=short"
else
  echo "Running tests locally..."
  if [ -n "$VERBOSE" ]; then
    VERBOSE=1 python -m pytest "${TEST_FILE}" -v --tb=short
  else
    python -m pytest "${TEST_FILE}" -v --tb=short
  fi
fi
