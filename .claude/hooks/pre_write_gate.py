#!/usr/bin/env python3
"""
PreToolUse Write — blocca credenziali hardcoded.
FLUXION patch — non tocca hook esistenti.
"""
import sys, json, re

SENSITIVE = [r'\.env$', r'credentials', r'secrets\.', r'\.pem$', r'\.key$']
HARDCODED = [
    r'password\s*=\s*["\'][^"\']{4,}["\']',
    r'api_key\s*=\s*["\'][^"\']{4,}["\']',
    r'token\s*=\s*["\'][^"\']{4,}["\']',
    r'secret\s*=\s*["\'][^"\']{4,}["\']',
]

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

    if content:
        for p in HARDCODED:
            if re.search(p, content, re.IGNORECASE):
                if 'std::env::var' not in content and 'os.environ' not in content and 'process.env' not in content:
                    print(json.dumps({"hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason":
                            "GATE: credenziale hardcoded rilevata.\n"
                            "Usa std::env::var() (Rust) o os.environ.get() (Python)."
                    }}))
                    return

main()
