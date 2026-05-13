#!/usr/bin/env bash
# Fix pjsua2 _pjsua2.so dylib lookup paths
#
# Why: stock build of _pjsua2.cpython-39-darwin.so encodes dylib references as
# "../lib/libpjsua2.dylib.2" — relative to CWD at load time, NOT to the .so
# itself. When Python imports pjsua2 from any cwd != lib/pjsua2/.. the
# dynamic loader fails:
#   ImportError: Library not loaded: '../lib/libpjsua2.dylib.2'
#
# Fix: install_name_tool -change each '../...' reference to
# '@loader_path/<basename>' which resolves relative to the .so location.
#
# Idempotent: skips refs already pointing to @loader_path.
#
# Usage: bash voice-agent/scripts/fix_pjsua2_loader_path.sh
# Reference: S209 — VoIP libpjsua2.dylib.2 missing fix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PJSUA2_DIR="$(cd "$SCRIPT_DIR/../lib/pjsua2" && pwd)"
SOFILE="$PJSUA2_DIR/_pjsua2.cpython-39-darwin.so"

if [[ ! -f "$SOFILE" ]]; then
    echo "ERROR: $SOFILE not found"
    exit 1
fi

cd "$PJSUA2_DIR"

# Detect refs starting with literal "../" (relative paths only).
# Avoid grepping for "../lib/" without -F because '.' is a regex wildcard
# and would match "/usr/lib/" etc. (bug seen in S209 first iteration).
PATCHED=0
SKIPPED=0
while read -r ref; do
    [[ -z "$ref" ]] && continue
    if [[ "$ref" == @loader_path/* ]]; then
        SKIPPED=$((SKIPPED+1))
        continue
    fi
    new="@loader_path/$(basename "$ref")"
    install_name_tool -change "$ref" "$new" "$SOFILE"
    echo "patched: $ref -> $new"
    PATCHED=$((PATCHED+1))
done < <(otool -L "$SOFILE" | awk 'NR>1 {print $1}' | grep -E '^\.\./')

echo ""
echo "Patched: $PATCHED refs"
echo "Already @loader_path: $SKIPPED refs"
echo ""
echo "Verify with: otool -L $SOFILE | head"
