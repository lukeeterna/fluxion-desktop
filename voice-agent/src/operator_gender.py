"""GAP-P1-4: Operator gender preference extraction from Italian utterances."""
import re
from typing import Optional

# Feminine indicators — only when explicitly expressed
_FEMININE_PATTERNS = [
    r"\boperatrice\b",
    r"\bun[a']?\s+donna\b",
    r"\buna\s+donna\b",
    r"\bfemmin[ae]\b",
    r"\bfemminile\b",
    r"\bpreferis[co]+\s+(?:una?\s+)?donna\b",
    r"\bvoglio\s+(?:una?\s+)?donna\b",
    r"\bcon\s+una\s+donna\b",
    r"\bcon\s+un[a']\s+operatrice\b",
]

# Masculine indicators — only when explicitly expressed
_MASCULINE_PATTERNS = [
    r"\bun\s+uomo\b",
    r"\buomo\b",
    r"\bmaschio\b",
    r"\bmascolino\b",
    r"\boperatore\s+uomo\b",
    r"\bpreferis[co]+\s+(?:un\s+)?uomo\b",
    r"\bvoglio\s+(?:un\s+)?uomo\b",
    r"\bcon\s+un\s+uomo\b",
]

_COMPILED_F = [re.compile(p, re.IGNORECASE) for p in _FEMININE_PATTERNS]
_COMPILED_M = [re.compile(p, re.IGNORECASE) for p in _MASCULINE_PATTERNS]


def extract_operator_gender_preference(text: str) -> Optional[str]:
    """Detect operator gender preference from user utterance.

    Returns 'F' (femminile), 'M' (maschile), or None (no preference expressed).
    Conservative: only returns a value when explicitly expressed.
    """
    for pat in _COMPILED_F:
        if pat.search(text):
            return "F"
    for pat in _COMPILED_M:
        if pat.search(text):
            return "M"
    return None
