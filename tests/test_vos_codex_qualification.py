from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "vos_codex_qualification", ROOT / "tools" / "vos_codex_qualification.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ParserTests(unittest.TestCase):
    def test_extract_thread_started_id(self):
        events = [
            {"type": "thread.started", "thread_id": "019d1c0a-0137-73f3-bf4a-88c90739150c"},
            {"type": "turn.completed", "usage": {"input_tokens": 1}},
        ]
        self.assertEqual(
            mod.require_single_session_id(events, "fixture"),
            "019d1c0a-0137-73f3-bf4a-88c90739150c",
        )

    def test_multiple_thread_ids_fail_closed(self):
        events = [
            {"type": "thread.started", "thread_id": "019d1c0a-0137-73f3-bf4a-88c90739150c"},
            {"type": "thread.started", "thread_id": "019d1c0a-0137-73f3-bf4a-88c90739150d"},
        ]
        with self.assertRaises(mod.QualificationError):
            mod.require_single_session_id(events, "fixture")

    def test_model_is_extracted_from_turn_context(self):
        rollout = [
            {
                "type": "turn_context",
                "payload": {"model": "gpt-5.6-sol", "model_provider": "openai"},
            }
        ]
        self.assertEqual(mod.extract_models(rollout), {"gpt-5.6-sol"})

    def test_invalid_jsonl_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.jsonl"
            path.write_text('{"type":"thread.started"}\nnot-json\n', encoding="utf-8")
            with self.assertRaises(mod.QualificationError):
                mod.parse_jsonl(path)


class QualificationFixtureTests(unittest.TestCase):
    def test_exact_resume_and_model_proof_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            codex_home = root / "codex-home"
            evidence = root / "evidence"
            workspace = root / "workspace"
            codex_home.mkdir()
            fake = root / "codex"
            fake.write_text(
                textwrap.dedent(
                    r'''#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path

sid = "019d1c0a-0137-73f3-bf4a-88c90739150c"
home = Path(os.environ["CODEX_HOME"])
state = home / "fixture-marker.txt"
args = sys.argv[1:]
if args[:2] == ["login", "status"]:
    print("Logged in using ChatGPT")
    raise SystemExit(0)
if args and args[0] == "exec" and len(args) > 1 and args[1] == "resume":
    if "--skip-git-repo-check" not in args:
        raise SystemExit(17)
    marker = state.read_text(encoding="utf-8").strip()
    print(json.dumps({"type":"thread.started","thread_id":sid}))
    print(json.dumps({"type":"turn.started"}))
    print(json.dumps({"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":marker}}))
    print(json.dumps({"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}))
    raise SystemExit(0)
if args and args[0] == "exec":
    prompt = args[-1]
    match = re.search(r"VOSQUAL-[0-9a-f-]+", prompt)
    if not match:
        raise SystemExit(9)
    state.write_text(match.group(0) + "\n", encoding="utf-8")
    session_dir = home / "sessions" / "2026" / "08" / "25"
    session_dir.mkdir(parents=True, exist_ok=True)
    rollout = session_dir / f"rollout-2026-08-25T00-00-00-{sid}.jsonl"
    rollout.write_text(
        json.dumps({"type":"session_meta","payload":{"id":sid,"model_provider":"openai"}}) + "\n" +
        json.dumps({"type":"turn_context","payload":{"model":"gpt-5.6-sol"}}) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"type":"thread.started","thread_id":sid}))
    print(json.dumps({"type":"turn.started"}))
    print(json.dumps({"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"stored"}}))
    print(json.dumps({"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}))
    raise SystemExit(0)
raise SystemExit(8)
'''
                ),
                encoding="utf-8",
            )
            fake.chmod(0o755)
            previous = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(codex_home)
            try:
                result = mod.qualify(
                    codex=str(fake),
                    codex_home=codex_home,
                    evidence=evidence,
                    model="gpt-5.6-sol",
                    workspace=workspace,
                    timeout=10,
                )
            finally:
                if previous is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["model_actual_proven"], "gpt-5.6-sol")
            self.assertEqual(result["thread_id_match"], "PASS")
            self.assertEqual(result["context_continuity"], "PASS")
            self.assertEqual(result["session_id"], "019d1c0a-0137-73f3-bf4a-88c90739150c")
            self.assertTrue(result["rollout_evidence_present"])
            self.assertTrue((evidence / "exec-first.jsonl").is_file())
            self.assertTrue((evidence / "exec-resume.jsonl").is_file())

    def test_api_key_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = root / "codex"
            fake.write_text(
                '#!/bin/sh\n[ "$1 $2" = "login status" ] && echo "Logged in using API key" && exit 0\nexit 1\n',
                encoding="utf-8",
            )
            fake.chmod(0o755)
            home = root / "home"
            home.mkdir()
            with self.assertRaisesRegex(mod.QualificationError, "API-key"):
                mod.qualify(
                    codex=str(fake),
                    codex_home=home,
                    evidence=root / "evidence",
                    model="gpt-5.6-sol",
                    workspace=root / "workspace",
                    timeout=5,
                )


if __name__ == "__main__":
    unittest.main()
