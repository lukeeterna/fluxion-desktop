#!/usr/bin/env python3
"""
F12 — Auto-update voice-agent/src/_INDEX.md
Estrae metodi e righe dai 3 file principali e aggiorna l'header con data e righe totali.
Eseguito dal pre-commit hook di Husky quando i file src/*.py sono modificati.

Usage:
    python scripts/update_voice_index.py          # aggiorna solo header/stats
    python scripts/update_voice_index.py --check  # solo verifica che l'indice sia aggiornato
"""

import re
import sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
INDEX_PATH = SRC / "_INDEX.md"

TARGET_FILES = [
    "booking_state_machine.py",
    "orchestrator.py",
    "italian_regex.py",
]


def count_lines(filepath: Path) -> int:
    try:
        return sum(1 for _ in filepath.open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def extract_public_methods(filepath: Path) -> list[tuple[int, str]]:
    """Return list of (lineno, def_signature) for public/important methods."""
    results = []
    try:
        for i, line in enumerate(filepath.open(encoding="utf-8", errors="replace"), 1):
            stripped = line.lstrip()
            # class + def + async def at module or class level
            if re.match(r"^(async\s+)?def\s+\w|^class\s+\w", stripped):
                # skip private helpers starting with __ but keep _ prefixed
                name_match = re.match(r"^(?:async\s+)?def\s+(\w+)|^class\s+(\w+)", stripped)
                if name_match:
                    name = name_match.group(1) or name_match.group(2)
                    if not name.startswith("__"):
                        results.append((i, name))
    except OSError:
        pass
    return results


def get_current_stats() -> dict[str, int]:
    return {f: count_lines(SRC / f) for f in TARGET_FILES}


def update_index_header(check_only: bool = False) -> bool:
    """
    Updates the last line of _INDEX.md with today's date and line counts.
    Returns True if file was/would-be changed, False if already up-to-date.
    """
    if not INDEX_PATH.exists():
        print(f"⚠️  _INDEX.md not found at {INDEX_PATH}")
        return False

    stats = get_current_stats()
    today = date.today().isoformat()

    # Build new last line
    line_counts = " | ".join(f"{f}: {n}" for f, n in stats.items())
    new_footer = f"_Aggiornato: {today} — {line_counts}_\n"

    content = INDEX_PATH.read_text(encoding="utf-8")

    # Replace the last _Aggiornato: line
    updated = re.sub(
        r"_Aggiornato:.*_\s*$",
        new_footer.strip(),
        content.strip(),
        flags=re.MULTILINE,
    )
    updated = updated + "\n"

    # Also update righe counts in the section headers like "3506 righe"
    for fname, nlines in stats.items():
        # e.g. "booking_state_machine.py — 3506 righe"
        updated = re.sub(
            rf"({re.escape(fname)} — )\d+ righe",
            rf"\g<1>{nlines} righe",
            updated,
        )

    if updated == content:
        if not check_only:
            print("✅ _INDEX.md già aggiornato")
        return False

    if check_only:
        print("⚠️  _INDEX.md non aggiornato — eseguire: python scripts/update_voice_index.py")
        return True

    INDEX_PATH.write_text(updated, encoding="utf-8")
    print(f"✅ _INDEX.md aggiornato ({today})")
    for fname, n in stats.items():
        print(f"   {fname}: {n} righe")
    return True


if __name__ == "__main__":
    check_mode = "--check" in sys.argv
    changed = update_index_header(check_only=check_mode)
    sys.exit(1 if (check_mode and changed) else 0)
