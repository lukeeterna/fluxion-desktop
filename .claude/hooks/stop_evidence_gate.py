#!/usr/bin/env python3
"""
Stop hook — blocca completion senza evidence reale.
FLUXION patch — non tocca hook esistenti.
"""
import sys, json, re

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = (data.get('claude_response','') or data.get('last_message','')
            or data.get('response','') or str(data))

    FORBIDDEN = [
        r'\bproduction\s*ready\b',
        r'\bproduzione\s*pronta\b',
        r'\b(completato|implementato|deployato)\s*con\s*successo\b',
        r'\btutto\s*(funziona|ok|a\s*posto)\b',
        r'\btestato\s*e\s*(funzionante|verificato)\b',
        r'\bpronto\s*per\s*(la\s*)?produzione\b',
        r'\bdeploy\s*(riuscito|completato)\b',
        r'\bimplementation\s*complete\b',
        r'\bworks\s*(correctly|perfectly|fine)\b',
        r'\bfunziona\s*(correttamente|perfettamente)\b',
    ]
    EVIDENCE = [
        r'\bPASS\b', r'\bFAIL\b', r'Evidence:',
        r'Validation\s*Report', r'\d+/\d+\s*PASS',
        r'[|]\s*(✅|❌)', r'pytest.*passed',
        r'Tests:\s*\d+', r'cargo.*test.*ok',
        r'tauri.*build.*ok', r'npm.*test.*passed',
    ]

    has_forbidden = any(re.search(p, text, re.IGNORECASE) for p in FORBIDDEN)
    has_evidence  = any(re.search(p, text, re.IGNORECASE|re.MULTILINE) for p in EVIDENCE)

    if has_forbidden and not has_evidence:
        print(json.dumps({"decision": "block", "reason": (
            "\n⛔ STOP — EVIDENCE MANCANTE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Hai dichiarato completion senza tabella evidence.\n\n"
            "Per FLUXION il formato richiesto è:\n"
            "| # | Criteria | Comando | Output | Status |\n"
            "|---|----------|---------|--------|--------|\n"
            "| 1 | Build OK | `npm run build` | [out] | ✅ |\n"
            "| 2 | Test suite | `cargo test` | [out] | ✅ |\n\n"
            "Esegui /gsd:verify-work o /fluxion-build-verification prima di procedere."
        )}))

main()
