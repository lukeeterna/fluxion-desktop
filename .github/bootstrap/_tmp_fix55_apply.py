#!/usr/bin/env python3
from pathlib import Path

P = Path('.github/bootstrap/fluxion-soleur-adapter.py')
text = P.read_text(encoding='utf-8')

old = '''CRITICAL RULE: In this FLUXION integration, `<promise>DONE</promise>` is forbidden
inside the engineering lane.  Only the post-publication verification lane may
report final completion.

Start with step 0b now.
'''
new = '''CRITICAL RULE: In this FLUXION integration, `<promise>DONE</promise>` is forbidden
inside the engineering lane.  Only the post-publication verification lane may
report final completion.

## FLUXION_SUBAGENT_DRAIN

This hosted one-shot execution has no later conversational resume.  Never return a
final response, pause for later, or claim that work will resume while any Soleur
review/QA subagent is still `running` or otherwise non-terminal.

If subagents are still active, remain inside this same execution and use the available
condition-wait mechanism (`Monitor` / agent-status polling) until every launched agent
reaches a terminal state.  A blocked `sleep` command is **not** permission to return
early.  Collect every review result, resolve blocking findings, finish QA/compound and
run Step 7 ship before producing any final response.

If the hosted execution cannot drain the active agents to terminal states, fail closed
without `FLUXION_SOLEUR_READY` and without `<promise>READY_FOR_SOL_000020</promise>`.
Never say "pause here", "resume later", or equivalent as a final result.

Start with step 0b now.
'''
if text.count(old) != 1:
    raise SystemExit(f'drain insertion: expected exactly one match, got {text.count(old)}')
text = text.replace(old, new, 1)

old_write = '''    one.write_text(_replace_from(one_text, "7. Use the **Skill tool**: `skill: soleur:ship`", one_overlay, "one-shot"), encoding="utf-8")

    post = root / "plugins/soleur/skills/postmerge/SKILL.md"
'''
new_write = '''    one.write_text(_replace_from(one_text, "7. Use the **Skill tool**: `skill: soleur:ship`", one_overlay, "one-shot"), encoding="utf-8")
    rendered_one = one.read_text(encoding="utf-8")
    drain_required = (
        "FLUXION_SUBAGENT_DRAIN",
        "Never return a",
        "Monitor` / agent-status polling",
        "fail closed",
        "Never say \\\"pause here\\\"",
    )
    missing_drain = [marker for marker in drain_required if marker not in rendered_one]
    if missing_drain:
        raise Blocked(f"one-shot subagent drain overlay incomplete: {missing_drain}")

    post = root / "plugins/soleur/skills/postmerge/SKILL.md"
'''
if text.count(old_write) != 1:
    raise SystemExit(f'drain assertion: expected exactly one match, got {text.count(old_write)}')
text = text.replace(old_write, new_write, 1)

P.write_text(text, encoding='utf-8')
print('FIX55_PATCH_APPLIED=PASS')
