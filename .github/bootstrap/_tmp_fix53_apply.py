#!/usr/bin/env python3
from pathlib import Path

ADAPTER = Path('.github/bootstrap/fluxion-soleur-adapter.py')
WORKFLOW = Path('.github/workflows/fluxion-soleur.yml')
adapter = ADAPTER.read_text(encoding='utf-8')
workflow = WORKFLOW.read_text(encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)


adapter = replace_once(
    adapter,
    'def _valid_relpath(value: str) -> bool:\n',
    '''def final_execution_result(path: Path) -> str:\n    try:\n        raw = json.loads(path.read_text(encoding="utf-8"))\n    except Exception as exc:\n        raise Blocked(f"invalid Soleur execution json: {exc}") from exc\n    if not isinstance(raw, list):\n        raise Blocked("Soleur execution root must be a list")\n    results = [item for item in raw if isinstance(item, dict) and item.get("type") == "result"]\n    if not results:\n        raise Blocked("Soleur execution has no final result record")\n    final = results[-1]\n    if final.get("subtype") != "success":\n        raise Blocked(f"final Soleur result subtype is not success: {final.get('subtype')!r}")\n    text = final.get("result")\n    if not isinstance(text, str):\n        raise Blocked("final Soleur result text missing")\n    required = (\n        "FLUXION_SOLEUR_READY",\n        "<promise>READY_FOR_SOL_000020</promise>",\n    )\n    missing = [marker for marker in required if marker not in text]\n    if missing:\n        raise Blocked(f"final Soleur result missing completion markers: {missing}")\n    return text\n\n\ndef cmd_validate_execution(a: argparse.Namespace) -> int:\n    final_execution_result(Path(a.execution))\n    print("SOLEUR_FINAL_RESULT=PASS")\n    return 0\n\n\ndef _valid_relpath(value: str) -> bool:\n''',
    'execution validator',
)

adapter = replace_once(
    adapter,
    '''    if "FLUXION_EXTERNAL_PUBLISH" not in text:\n        raise Blocked("external publisher postmerge marker absent")\n    print("WORKFLOW_STATIC=PASS")\n''',
    '''    if "FLUXION_EXTERNAL_PUBLISH" not in text:\n        raise Blocked("external publisher postmerge marker absent")\n    legacy_marker_checks = (\n        "grep -Fq 'READY_FOR_SOL_000020' \\\"$EXECUTION_FILE\\\"",\n        "grep -Fq 'FLUXION_SOLEUR_READY' \\\"$EXECUTION_FILE\\\"",\n    )\n    if any(marker in text for marker in legacy_marker_checks):\n        raise Blocked("workflow still uses broad execution-file marker grep")\n    if 'validate-execution \\\\' not in text or '--execution \\\"$EXECUTION_FILE\\\"' not in text:\n        raise Blocked("workflow final-result execution validator wiring absent")\n    print("WORKFLOW_STATIC=PASS")\n''',
    'static workflow marker contract',
)

adapter = replace_once(
    adapter,
    '''    data = b"abc"\n    assert git_blob_sha(data) == hashlib.sha1(b"blob 3\\0abc").hexdigest()\n\n    with tempfile.TemporaryDirectory() as td:\n''',
    '''    data = b"abc"\n    assert git_blob_sha(data) == hashlib.sha1(b"blob 3\\0abc").hexdigest()\n\n    with tempfile.TemporaryDirectory() as td:\n        execution = Path(td) / "execution.json"\n        early = "FLUXION_SOLEUR_READY <promise>READY_FOR_SOL_000020</promise>"\n        good = [\n            {"type": "assistant", "message": early},\n            {\n                "type": "result",\n                "subtype": "success",\n                "result": "## Ship Phase Complete — FLUXION external publisher boundary\\nFLUXION_SOLEUR_READY\\n<promise>READY_FOR_SOL_000020</promise>",\n            },\n        ]\n        execution.write_text(json.dumps(good), encoding="utf-8")\n        final_execution_result(execution)\n\n        false_green = [\n            {"type": "assistant", "message": early},\n            {"type": "result", "subtype": "success", "result": "Four review agents are still in progress."},\n        ]\n        execution.write_text(json.dumps(false_green), encoding="utf-8")\n        try:\n            final_execution_result(execution)\n        except Blocked as exc:\n            if "missing completion markers" not in str(exc):\n                raise\n        else:\n            raise Blocked("self-test accepted markers present only before final result")\n\n        failed = [\n            {"type": "result", "subtype": "error", "result": early},\n        ]\n        execution.write_text(json.dumps(failed), encoding="utf-8")\n        try:\n            final_execution_result(execution)\n        except Blocked as exc:\n            if "subtype is not success" not in str(exc):\n                raise\n        else:\n            raise Blocked("self-test accepted non-success final result")\n\n    with tempfile.TemporaryDirectory() as td:\n''',
    'execution self-tests',
)

adapter = replace_once(
    adapter,
    '''    s = sub.add_parser("static-workflow")\n    s.add_argument("--workflow", required=True)\n    s.set_defaults(fn=cmd_static_workflow)\n    s = sub.add_parser("self-test")\n''',
    '''    s = sub.add_parser("static-workflow")\n    s.add_argument("--workflow", required=True)\n    s.set_defaults(fn=cmd_static_workflow)\n    s = sub.add_parser("validate-execution")\n    s.add_argument("--execution", required=True)\n    s.set_defaults(fn=cmd_validate_execution)\n    s = sub.add_parser("self-test")\n''',
    'parser validator command',
)

workflow = replace_once(
    workflow,
    '''          test -f "$EXECUTION_FILE"\n          grep -Fq 'READY_FOR_SOL_000020' "$EXECUTION_FILE"\n          grep -Fq 'FLUXION_SOLEUR_READY' "$EXECUTION_FILE"\n''',
    '''          test -f "$EXECUTION_FILE"\n          python3 "$RUNNER_TEMP/fluxion-soleur-adapter.py" validate-execution \\\n            --execution "$EXECUTION_FILE"\n''',
    'workflow marker check',
)

ADAPTER.write_text(adapter, encoding='utf-8')
WORKFLOW.write_text(workflow, encoding='utf-8')
print('FIX53_PATCH_APPLIED=PASS')
