#!/usr/bin/env python3
"""
PreCompact — salva stato in HANDOFF.md prima di auto-compaction.
FLUXION patch — salva nel progetto corrente.
"""
import sys, json, os, datetime

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    ctx = data.get('conversation_summary','') or data.get('context','') or ''
    ts  = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    dump = f"""
## AUTO-COMPACTION DUMP — {ts}
⚠️ Context ~83% — compaction imminente.

Stato pre-compaction:
{ctx if ctx else '[ricostruire da: git diff --name-only HEAD]'}

POST-COMPACTION:
1. Leggi questo HANDOFF.md
2. Esegui: git diff --name-only HEAD
3. Riprendi dal milestone GSD in corso
"""

    # Path corretto: memory Claude Code per questo progetto
    mem_dir = os.path.expanduser(
        "~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory"
    )
    os.makedirs(mem_dir, exist_ok=True)

    for path in [os.path.join(mem_dir,'HANDOFF.md'),
                 os.path.join(mem_dir,'compaction_log.md')]:
        with open(path,'a') as f:
            f.write(dump)

    print(json.dumps({"additionalContext": (
        "⚠️ COMPACTION — stato salvato in ~/.claude/projects/.../memory/HANDOFF.md\n"
        "Leggi HANDOFF.md prima di continuare qualsiasi milestone GSD."
    )}))

main()
