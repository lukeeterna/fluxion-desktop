#!/usr/bin/env python3
"""
PreToolUse Write — blocca credenziali hardcoded.
FLUXION patch — non tocca hook esistenti.

S296 audit fix (2026-05-26):
- Aggiunto word-boundary \b sui pattern HARDCODED (era `secret\s*=` → matchava
  `LICENSE_RECOVERY_SECRET:` causando false positive su test fixture).
- Path whitelist: tests/, __tests__/, *.test.*, *.spec.* skip controllo (unit
  test fixtures legittime).
- Valore whitelist: fixture-|test-|mock-|dummy-|deterministic- bypass
  (chiaramente non credenziali reali).
- Bypass `process.env` ora per-line (era file-level → false negative se
  process.env in funzione X e hardcoded in funzione Y senza relazione).
"""
import sys, json, re

SENSITIVE = [r'\.env$', r'credentials', r'secrets\.', r'\.pem$', r'\.key$']

# S296 fix: \b word-boundary previene match su LICENSE_RECOVERY_SECRET,
# MY_API_KEY, USER_TOKEN, etc. Match solo su keyword "pure".
HARDCODED = [
    r'\bpassword\s*[:=]\s*["\'][^"\']{4,}["\']',
    r'\bapi_key\s*[:=]\s*["\'][^"\']{4,}["\']',
    r'\btoken\s*[:=]\s*["\'][^"\']{4,}["\']',
    r'\bsecret\s*[:=]\s*["\'][^"\']{4,}["\']',
]

# S296 fix: skip enforcement su file test (fixture deterministiche sono legittime).
TEST_PATH_PATTERNS = [
    r'(^|/)tests?/',
    r'(^|/)__tests__/',
    r'\.test\.[jt]sx?$',
    r'\.spec\.[jt]sx?$',
    r'_test\.py$',
    r'(^|/)test_[^/]+\.py$',
]

# S296 fix: valore fixture chiaramente non-credenziale.
FIXTURE_VALUE_PREFIXES = ('fixture-', 'test-', 'mock-', 'dummy-', 'fake-',
                           'deterministic-', 'sample-', 'example-')

# Bypass per-line: se la riga contiene env access reader, OK.
LINE_BYPASS_TOKENS = ('std::env::var', 'os.environ', 'process.env',
                       'env::var', 'getenv(', 'ENV[', 'Deno.env')


def _is_test_path(fpath: str) -> bool:
    return any(re.search(p, fpath) for p in TEST_PATH_PATTERNS)


def _is_fixture_value(matched_text: str) -> bool:
    # Estrae il valore stringa dal match (tra "" o '')
    m = re.search(r'["\']([^"\']{4,})["\']', matched_text)
    if not m:
        return False
    val = m.group(1).lower()
    return any(val.startswith(p) for p in FIXTURE_VALUE_PREFIXES)


def _line_has_env_bypass(content: str, match_start: int) -> bool:
    # Trova inizio/fine riga contenente il match
    line_start = content.rfind('\n', 0, match_start) + 1
    line_end = content.find('\n', match_start)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    return any(tok in line for tok in LINE_BYPASS_TOKENS)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    ti      = data.get('tool_input', {})
    fpath   = ti.get('file_path','') or ti.get('path','')
    content = ti.get('content','') or ti.get('new_content','')

    for p in SENSITIVE:
        if re.search(p, fpath, re.IGNORECASE):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    f"GATE: file sensibile: {fpath}\nConferma esplicitamente."
            }}))
            return

    # S296 fix: skip enforcement su path test (fixture deterministiche legit)
    if _is_test_path(fpath):
        sys.exit(0)

    if content:
        for p in HARDCODED:
            for m in re.finditer(p, content, re.IGNORECASE):
                # Bypass valore fixture (test-only)
                if _is_fixture_value(m.group(0)):
                    continue
                # Bypass env reader sulla STESSA riga
                if _line_has_env_bypass(content, m.start()):
                    continue
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason":
                        f"GATE: credenziale hardcoded rilevata: {m.group(0)[:60]}\n"
                        "Usa std::env::var() (Rust), os.environ.get() (Python), "
                        "o process.env.* (TS/JS) sulla stessa riga.\n"
                        "Se è test fixture, sposta file in tests/ o usa prefix "
                        "'fixture-'/'test-'/'mock-'."
                }}))
                return

main()
