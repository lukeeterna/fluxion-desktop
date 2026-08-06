#!/usr/bin/env python3
"""Run the guarded PR #2 reviewer with the bounded CPU model profile."""
from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("fluxion_headless_reviewer_v2.py")
SPEC = importlib.util.spec_from_file_location("fluxion_guarded_reviewer", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit("cannot load guarded reviewer")

reviewer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewer)

# The 8B profile exceeds the 900-second CPU inference gate on GitHub-hosted
# runners. The 4B profile uses the identical deterministic audit, bounded
# dossier, output schema, and anti-hallucination rejection rules.
reviewer.MODEL = "qwen3:4b"

if __name__ == "__main__":
    raise SystemExit(reviewer.main())
