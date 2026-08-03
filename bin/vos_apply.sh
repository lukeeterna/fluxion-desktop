#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
exec python3 "$REPO_ROOT/bin/vos_apply.py" "$@"
